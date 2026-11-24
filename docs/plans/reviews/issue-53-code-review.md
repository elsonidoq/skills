# Issue #53 — independent code review (PR #54)

- **Range:** `git diff 057b193..894ca3f` (one commit). HEAD at review: `894ca3f`. Working tree clean.
- **Requirement:** issue #53; `docs/plans/issue53-settled-sdk-errors-tinyspec.md` (in the commit).
- **SDK examined:** `@earendil-works/pi-coding-agent` 1.4.0 `dist/core/agent-session.js` and
  `@earendil-works/pi-agent-core` `dist/agent.js`, `dist/agent-loop.js` in the same release.
- **Mode:** read-only. I did not run tests. The test results below are the supervisor's results.

## Findings

No blocking or important findings.

### Minor 1 — store classifies the failure from adapter text, and fails open if the text changes

- **Location:** `runtime/coherence_workflow/store.py:345-350`, coupled to
  `runtime/coherence_workflow/pi_adapter.py:42-44`.
- **Observed:** The store decides "sessionless" from the persisted `error` string: prefix
  `SDK operation failed: ` and absence of `effects are uncertain`. These two literals are a
  second copy of the adapter format. `graph.py:821` already uses the same marker, so this follows
  an existing pattern.
- **Impact:** If a later change rewords the adapter marker, the store treats an uncertain SDK
  error with `session: None` as sessionless (fail open). Current practical risk is low: with the
  current host and `sessionObservations: True` (`pi_adapter.py:313`), `session: None` plus an SDK
  `error` record can only come from a `createWorkflowSession` failure, before any agent run
  (see Q2). There is no current defect.
- **Smaller sturdier option (optional):** persist an explicit fact (for example
  `settled: True` on the `Blocked` and in the failure details) and test that, or share one
  marker constant between `pi_adapter.py`, `graph.py` and `store.py`.

### Minor 2 — tests do not cover the realistic settled path or the strict store side

- **Location:** `runtime/tests/test_host.mjs:395-417`; `runtime/tests/test_worker_recovery.py:151-190`.
- **Observed:**
  - The host "idle" case mocks `AgentSession.prototype.prompt` to throw before any run starts.
    The realistic path (a run ends with `stopReason: 'error'`, `promptSession` throws after
    `waitForIdle`, host marks settled) is not run through `execute()`.
  - No host test shows that a pending question keeps the error uncertain (the TinySpec states
    this limit). No test of the SIGTERM-abort path.
  - The store exemption has no direct negative test: a failed row with `session: None` and a
    non-SDK error, an error with the marker, or an `interrupted` row must still give
    "unbound fresh session". The graph test "unattested" stops earlier at `graph.py:821`, so it
    does not reach the store rule.
- **Impact:** Regression risk only. The code reasoning below shows these paths are correct today.
- **Smaller fix (optional):** one store unit test next to `test_worker_recovery.py:693`
  (reserve `None`; write `started` + `failed` rows with (a) settled SDK text → redispatch
  allowed, (b) marker text, (c) non-SDK text, (d) `interrupted` → "unbound fresh session").

## Answers to the review questions

### Q1 — Can the host attest `settled` while work is still in flight?

No, within SDK 1.4.0 semantics.

- `isIdle` is `!this._isAgentRunActive && !this.isCompacting` (agent-session.js:1072-1074).
  `isCompacting` covers auto/manual compaction and branch summary (1224-1228).
- `_isAgentRunActive` becomes false only in `_emitAgentSettled` (683-685), called from the
  `finally` of `_startRun` (1466-1472) after `agent.prompt()` and the post-run loop
  (`_handlePostAgentRun`, auto-retry, before-settle, continue) end. Auto-retry sleeps inside
  that loop (`_prepareRetry`, 3090-3124). Tool calls run inside the agent loop and are
  awaited with `Promise.all` also on abort (agent-loop.js:417-459). `agent.runWithLifecycle`
  catches loop errors and records them as an assistant error message (agent.js:343-372).
- `session.prompt()` resolves/rejects only after `_emitAgentSettled` completes, including
  deferred settled actions. `promptSession` then awaits `waitForIdle()` before it throws for
  `stopReason` error/aborted (host.mjs:36-46). An early rejection (before `_startRun`, or
  `_prepareRun` failure at 1427-1434) has no run. If a run were still active, `isIdle` is false
  and the error stays uncertain.
- **Catch vs finally:** `catch` (host.mjs:418-424) runs before `finally`. There is no `await`
  between the catch check and `process.off('SIGTERM', ...)`, so a signal cannot interleave.
  On SIGTERM, `session.abort()` sets abort flags and aborts the agent; the run drains, and
  `promptSession` reaches `waitForIdle()` before it throws "aborted". So the catch sees an
  idle session. `await aborting` in `finally` then resolves at once. `main()` emits the `error`
  record only after `execute()` returns, that is after `finally` and `session.dispose()`
  (host.mjs:484-485). Thus `settled: true` is never sent before the abort drain ends.
  Note: an externally SIGTERM-aborted run now reports settled. This agrees with the rule
  (nothing in flight); the session is bound and the existing effect/HEAD checks decide.
- **Question pause:** `pendingQuestion` is set before the abort starts (host.mjs ask_owner
  tool). Every pause failure ("did not initiate SDK abort", a rejected `pauseAbort`, "did not
  reach SDK idle", an error from `promptSession` while paused) has a non-null
  `coherencePendingQuestion()`, so the error stays uncertain.
- **`createWorkflowSession` failure** (host.mjs:385-391): no agent run started. If it fails
  after `createAgentSession`, its own catch disposes the session. Errors from the steering
  setup or the session record emit (host.mjs:395-398) are outside the try and stay uncertain.
- **Residual, outside SDK state:** detached background processes started by a tool, and
  executor-extension activity during `bindExtensions`. The TinySpec R1 records the first; the
  same risk exists for a normal successful return.

### Q2 — Is the store `sessionless` exemption safe?

Yes for the current code paths.

- Only `graph.py:434` calls `reserve_worker_dispatch`, and the graph worker always calls the
  adapter with `pause_questions=True` (graph.py:470-472). So every non-attested SDK error
  carries the marker (`pi_adapter.py:43-44`).
- `PiAdapter.prompt` always sends `sessionObservations: True` (pi_adapter.py:313). The host
  emits the `session` record immediately after `createWorkflowSession` succeeds, before any
  prompt (host.mjs:395-396). The single decode thread handles it before any later `error`
  record and sets `opened_session`; `reader.join()` precedes the raise. The graph then writes
  `session: actual` (graph.py:476-481). So a host that opened a session gives a non-null
  `session` and the exemption does not apply. `session: None` with the SDK prefix means
  `createWorkflowSession` failed.
- The exemption applies only to reservations made with `session=None` (`prior is None`), and
  only when the last invocation row is `failed`. `started` and `interrupted` rows remove it
  (store.py:345-350). A reservation without invocation rows stays blocked
  (existing test `test_worker_recovery.py:693`).
- Other failures with `session: None` (adapter-side `Blocked`, `OSError`, "SDK host exited
  without a result", invalid session record, callback errors) do not have the prefix, or
  have the marker. They stay blocked as before.
- `_safe_error` (engine.py:46-51) only replaces the parent bridge token string with
  `[excluded credential]`. It does not truncate. It cannot remove the prefix or the marker
  unless the token is a substring of them, which is not realistic.
- Data safety: the exempt case has no agent run, so a fresh worker cannot race a live
  writer. Graph recovery still checks effects, HEAD, source and index (graph.py:819-832), and
  `continue` stays blocked without a session (graph.py:836-837).

### Q3 — Are the tests sufficient and do they test real code paths?

Mostly real:

- `test_host.mjs:395`: real `execute()` and real `createWorkflowSession` with the real SDK;
  "Model not found" is the real SDK path. The idle/active cases mock `prompt` and `isIdle`
  (see Minor 2).
- `test_host.mjs:419`: real host process; checks the wire record `settled: true`.
- `test_pi_adapter.py:582`: real adapter decode with a fixture host; checks `True`, missing and
  `'true'`.
- `test_worker_recovery.py:151`: real graph, store, recovery gate and checkpoint; the fixture
  adapter uses the real `sdk_error_detail`. It proves the store change is necessary for the
  pre-session case.
- Gaps: see Minor 2.

### Q4 — Anything unnecessary?

No. The store change is necessary: without it, `fresh` recovery after a pre-session failure
always fails with "unbound fresh session". `sdk_error_detail` is a small extraction used by
the adapter and the graph test. Removal of the design HTML page leaves no dangling link
(no remaining reference in `*.md`).

## Examined and passing

- Host attestation rule and its order against SDK 1.4.0 idle, compaction, retry, abort and
  tool execution semantics.
- Question-pause failure paths stay uncertain.
- Adapter: marker removed only on `settled is True`; "host exited without a result" path
  unchanged and still uncertain.
- Store: exemption limited to fresh reservations whose last invocation row is a failed,
  session-less, attested SDK error; existing reservation/binding/allowance checks unchanged.
- Graph recovery gate (graph.py:819-840) unchanged and still applies after a settled error.
- Docs: `docs/coordinate-implementation.md` statement matches the code; plan index updated.

## Open questions

None that affect the verdict.

## Verdict

**Ready**, with optional follow-up for Minor 1 and Minor 2.

## Verification gaps

- I did not run tests (read-only review). Supervisor-reported: `test_host.mjs` 23 pass; 143
  focused Python tests OK; full suite has 1 error and `test_question_triage.mjs` 1 failure,
  both reported also on `origin/main` (not verified by me).
- No live provider run (real context overflow through the bridge).
- No direct host test for the pending-question branch or the SIGTERM path; no direct store
  negative test for the exemption.
