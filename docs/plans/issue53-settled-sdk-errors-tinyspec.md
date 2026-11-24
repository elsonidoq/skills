# Settled SDK errors allow inspected worker recovery — TinySpec

- **Qualified issue:** <https://github.com/elsonidoq/skills/issues/53> (open).
- **Planning depth:** TinySpec, selected by the owner for issue #53.
- **Status:** Stage 1 source (what, acceptance and high-level design). The detailed
  approach is pending owner design agreement on the
  [high-level design page](issue53-settled-sdk-errors-design.html). No tasks, no
  implementation and no approval exist yet.
- **Executor configuration for later tasks:** `.pi/workflow-executor.json` (path only; this
  source does not select or copy bindings).

## Outcome and scope

**Beneficiary:** the coordinator (agent or owner) that recovers a failed graph worker.

**Problem.** In a question-pausing run, every SDK `error` transport record gets the text
"settlement and effects are uncertain ... do not redispatch"
([`pi_adapter.py` L498-L502](../../runtime/coherence_workflow/pi_adapter.py)). Graph recovery
then refuses every `resume --recovery-action` value for that task
([`graph.py` L821-L822](../../runtime/coherence_workflow/graph.py)). Graph workers always use
`pause_questions=True` (`graph.py` L469), so this applies to every graph worker SDK error. It
includes errors where the session clearly ended (provider context overflow, "Prompt is too
long") and errors before any session existed ("Model not found"). The only path forward is an
owner-authorized `recover-task` of complete work; partial work has no supported continuation.

**Required behavior.**

1. IF the SDK host reports an error AND no worker session was created, THEN the host attests
   that the error is settled.
2. IF the SDK host reports an error AND the worker session is idle with no pending question
   at error time, THEN the host attests that the error is settled.
3. IF the adapter receives an `error` record with the settled attestation, THEN it reports the
   failure without the "effects are uncertain ... do not redispatch" text.
4. IF the attestation is absent or has any value other than the attested value, THEN the
   adapter keeps the existing uncertain text (old hosts and unknown cases stay strict).
5. IF a failed worker row has no uncertain text, THEN `resume --recovery-action fresh|continue`
   passes the uncertain gate and the existing invocation, HEAD, source, index, escalation and
   saved-session checks decide the result.
6. IF the error occurs while an agent run (and therefore a tool call) is active, or while a
   question is pending, THEN no attestation is given and recovery stays blocked.

**Included surfaces.** `runtime/pi-host/host.mjs` (error attestation),
`runtime/coherence_workflow/pi_adapter.py` (suffix decision for SDK `error` records), focused
tests, and one sentence in the existing recovery guide
([`docs/coordinate-implementation.md` — Coordinator-selected worker recovery](../coordinate-implementation.md#coordinator-selected-worker-recovery)).
`graph.py` keeps its gate unchanged unless the detailed approach finds a concrete need.

**Exclusions.**

- Bridge-provider compaction before context overflow (related #18).
- The "SDK host exited without a result" path (`pi_adapter.py` L537-L543): no host
  attestation exists there, so it stays strict.
- Historical failure rows: no backfill, reclassification or rewrite. They stay blocked and
  keep the `recover-task` path.
- Message-string matching of provider error text.
- Reviewer, fixer and non-graph invocations: their behavior does not change except that the
  adapter rule applies to any pause-question SDK `error` record it receives.

## Decisions and constraints

**Settled direction (parent technical decision under owner guidance "handle routine
technical decisions autonomously", [memory](../../memory/MEMORY.md#routine-technical-decisions-and-review-scope)).**

- **D1 — Host attests; adapter trusts only attestation.** The host is the only component that
  observes the SDK session state at error time. The adapter does not infer settlement from
  message text, exit codes or timing.
- **D2 — Attestation conditions.** Settled only when (a) no session was created, or (b) the
  session is idle (`session.isIdle`) and has no pending question at error time. Evidence:
  SDK 1.4.0 `AgentSession.isIdle` is `!this._isAgentRunActive && !this.isCompacting`
  (`dist/core/agent-session.js` L1072-L1073); `_startRun` sets it at L1424, clears it on a
  prepare failure (L1431) and otherwise in its `finally` through `_emitAgentSettled`
  (L1464-L1471, L683-L685); tool execution runs inside the agent run. So idle and no pending
  question implies no tool call in flight. Repository-derived, verified locally.
- **D3 — Absent attestation is strict.** Older hosts, malformed values and every other
  error stay uncertain. This keeps compatibility without a version check.
- **D4 — Existing recovery checks stay authoritative.** Graph recovery already verifies the
  exact predecessor invocation, retained `effects`, HEAD, source state and index state,
  unresolved escalation, and a saved session for `continue` (`graph.py` L823-L845). The change
  only removes a false "uncertain" label; it adds no new gate and removes no check.
- **D5 — Gate is action-independent.** The uncertain gate runs before the action is
  considered. When it passes, `escalate` also reaches its existing checks (permitted fallback,
  no unresolved escalation). This is existing behavior for any non-uncertain failure, not new
  scope.
- **D6 — Pre-session errors and `continue`.** A pre-session error has no saved session, so
  `continue` stays blocked by the existing "needs the exact saved session" check; `fresh` is
  the path. This is correct behavior, not a defect.

**Verified host facts (re-verified in this checkout).**

- `host.mjs` `main()` emits `{type: 'error', message}` only in its outer `catch`, after
  `execute()` threw (L471-L473). `execute()` calls `createWorkflowSession` first; "Model not
  found" is thrown there (L218), before `execute()` emits any `session` record. A later
  failure inside `createWorkflowSession` disposes its own session before it rethrows
  (L240-L242), so `execute()` never receives it.
- `promptSession` awaits `session.waitForIdle()` after `session.prompt` and throws
  `last.errorMessage` when the last assistant `stopReason` is `error` (L36-L50). This is how
  "Prompt is too long" surfaces: the session is idle at throw time.
- Question-pause failures ("question pause did not initiate SDK abort", "did not reach SDK
  idle") are thrown in `execute()` with a pending question or a non-idle session; they must
  stay strict (L401-L406).
- `execute()`'s `finally` awaits any host-owned abort, then disposes the session
  (L412-L420). The attestation must be decided from state observed inside `execute()`,
  because the session is disposed before `main()` emits the record.

**Constraints.**

- Parsimony (AGENTS.md): smallest working change; no new blocking machinery; preserve the real
  data-safety rule "never redispatch with a live writer".
- No specific capability-version requirement ([memory](../../memory/MEMORY.md#installed-agent-capability-versions)).
  Compatibility comes from D3, not from a version check.
- Accepted ADRs: [ADR-0003](../decisions/ADR-0003-current-launch-authority-and-neutral-tasks.md)
  applies to later tasks (authorization-neutral task text). [ADR-0004](../decisions/ADR-0004-shared-routine-worker-permissions.md)
  applies to later workers (small isolated test fixtures need no extra approval). Neither
  changes this design.
- Transport compatibility: the new field is additive on an existing record type. Old adapters
  ignore unknown fields on `error` records (they read only `message`).

**Assumption (needs validation in detailed approach).** A host-owned cancel (SIGTERM/SIGINT)
is an operator interruption, not an SDK error. Recommended: no attestation when a host-owned
cancel was requested, so that path stays strict. Validation: host test in A3.

## Approach

**Pending owner design agreement.** The high-level design is on the
[design page](issue53-settled-sdk-errors-design.html). The detailed how (exact field name and
placement, where `execute()` records the observed state, adapter validation, test fixtures and
doc sentence) is written only after the owner agrees with that design.

## Acceptance

Each criterion is pass/fail. The smallest sufficient check is named. Tests use existing
suites; no live provider call is necessary.

| ID | Criterion | Smallest check | Pass condition |
|----|-----------|----------------|----------------|
| A1 | Pre-session error is attested settled. | Host test (`runtime/tests/test_host.mjs`): an executor that names a model the runtime does not have makes `createWorkflowSession` throw "Model not found". | The emitted `error` record carries the settled attestation; no `session` record was emitted. |
| A2 | Idle post-run error is attested settled. | Host test with a session fake (or the installed SDK with mocks, as existing host tests do) where the last assistant message has `stopReason: 'error'`, `errorMessage: 'Prompt is too long'`, `isIdle` is true and no question is pending. | The emitted `error` record has message `Prompt is too long` and the settled attestation. |
| A3 | Active or paused errors stay strict. | Host tests for: error while `isIdle` is false; "question pause did not initiate SDK abort" (pending question); "question pause did not reach SDK idle"; host-owned cancel (assumption above). | No settled attestation on any of these `error` records. |
| A4 | Adapter drops the suffix only on attestation. | Adapter tests (`runtime/tests/test_pi_adapter.py`, existing fixture style) with `pause_questions=True`. | Attested record → `Blocked` text is `SDK operation failed: <message>` with no "effects are uncertain". Absent, `false`, string or other values → existing suffix kept. `pause_questions=False` unchanged. "Exited without a result" keeps its suffix (existing test `test_lost_pause_result_is_uncertain_not_permission_to_redispatch` still passes). |
| A5 | Graph recovery proceeds for a settled failure under normal checks. | Graph recovery test (`runtime/tests/test_worker_recovery.py` style) whose failed `worker_invocation` row is produced through the real adapter error path from an attested record, not handwritten text. | `fresh` records `graph_recovery` and dispatches a new invocation; `continue` with a saved session proceeds; `continue` with no saved session is blocked by the existing saved-session message; HEAD/source drift is blocked by the existing drift message. |
| A6 | Unattested failures stay blocked. | Same graph test file, row produced from an unattested `error` record. | Every action (`continue`, `fresh`, `escalate`) raises the existing "settlement and effects are uncertain" `Blocked`; no dispatch occurs. |
| A7 | Recovery guide states the rule. | Read `docs/coordinate-implementation.md` § Coordinator-selected worker recovery. | One short statement: SDK errors that the host attests as settled (no session, or idle with no pending question) are settled predecessors; other SDK errors and lost host results stay uncertain; historical rows are unchanged. |
| A8 | No regression in touched suites. | Run the existing host, adapter, graph-execution, graph-question and worker-recovery suites. | All pass; report exact commands and counts. |

**Evidence trace.** D2 → A1, A2, A3. D3 → A4, A6. D4/D6 → A5. Exclusions (exit path,
historical rows) → A4, A6. Documentation obligation → A7.

**Limits.** These are local deterministic tests with fakes or SDK mocks. They do not prove a
real provider overflow through the bridge; that live observation is NOT REQUIRED and NOT RUN.
Independent final review of the implementation stays required.

## Risks and deferrals

- **R1 — Idle is not the same as "no external process".** A tool may start a detached
  background process (for example through `bash`) that survives the agent run. This risk is
  the same for a normal successful return, and the existing effect/HEAD/source/index checks
  still apply before redispatch. Not mitigated further (no new machinery). Proposed as an
  accepted limit; owner may object at design agreement.
- **R2 — Wrong attestation is a data-safety risk.** If the host attests while a tool is still
  running, a redispatch can race a live writer. Mitigation: attest only from directly observed
  SDK state (D2), never from text; strict default (D3); A3 covers the strict cases.
- **R3 — SDK semantics may change.** `isIdle` meaning comes from SDK 1.4.0. A later SDK may
  change it. Mitigation: host tests exercise the installed SDK where the existing suite does;
  no version pin (owner guidance).
- **R4 — Pre-session side effects.** Before a session exists, the host may create the
  sessions directory and load selected executor extensions. These are not task effects; the
  existing effect checks still run before redispatch.
- **Deferred (owner direction in brief):** #18 compaction; "exited without a result" path;
  historical rows.
- **UNVERIFIED:** whether `session.prompt` can reject (non-abort) while the agent run is still
  active in SDK 1.4.0. The design does not depend on this: the attestation reads `isIdle` at
  error time, so an active run gives no attestation.
