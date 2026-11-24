# Settled SDK errors allow inspected worker recovery — TinySpec

- **Qualified issue:** <https://github.com/elsonidoq/skills/issues/53>.
- **Planning depth:** TinySpec, selected by the owner. After stage 1, the owner agreed to stop
  the remaining TinySpec stages: the safety decision was settled from SDK evidence, and the
  rest was small direct work with one independent review (same as #51 and #52). This file
  records the decision and the implemented approach. There are no separate tasks.

## Outcome and scope

**Problem.** In a question-pausing run, every SDK `error` record got the text "settlement and
effects are uncertain ... do not redispatch". Graph workers always pause questions, so graph
recovery refused every `resume --recovery-action` for any worker SDK error. This included
errors where nothing could still run: provider context overflow ("Prompt is too long") and
errors before any session existed ("Model not found").

**Required behavior.**

1. The host attests an SDK error as settled only when no agent run, compaction or tool call is
   in flight and no question is pending. No session at all satisfies this.
2. The adapter removes the uncertain text only on that attestation. A missing or other value
   (older host, unknown case) stays uncertain.
3. A settled failure passes the graph recovery gate. The existing invocation, effect, HEAD,
   source, index, escalation and saved-session checks then decide the result.
4. A settled failure that opened no session can be recovered with `fresh`. `continue` stays
   blocked because no saved session exists.

**Exclusions.** Bridge compaction before overflow (#18); the "SDK host exited without a
result" path (no attestation, stays strict); historical failure rows (no backfill); matching
on provider message text.

## Decision

The host decides, because only the host observes the SDK session at error time. SDK 1.4.0
`AgentSession.isIdle` is `!_isAgentRunActive && !isCompacting`, and tool calls run inside the
agent run, so an idle session with no pending question has no tool call in flight. The
question-pause failures ("did not initiate SDK abort", "did not reach SDK idle") have a pending
question or a non-idle session, so they stay uncertain under the same rule.

## Approach (implemented)

- `runtime/pi-host/host.mjs` `execute()`: an error from `createWorkflowSession` is marked
  settled; a later error is marked settled only if `session.isIdle === true` and no question is
  pending, observed before the session is disposed. `main()` adds `settled: true` to the
  `error` record only for a marked error.
- `runtime/coherence_workflow/pi_adapter.py` `sdk_error_detail()`: adds the uncertain text
  unless `settled is True`.
- `runtime/coherence_workflow/store.py` `reserve_worker_dispatch()`: a failed invocation with
  no session and an attested SDK error (no uncertain text) is not an "unbound fresh session".
  Without this, the store blocked every redispatch after a pre-session error, because it could
  not exclude an unrecorded session. Implementation found this; the graph test shows it.
- `docs/coordinate-implementation.md`, coordinator-selected worker recovery: one statement of
  the rule.

## Acceptance

| ID | Check | Pass condition |
|----|-------|----------------|
| A1 | `runtime/tests/test_host.mjs`: settled attestation tests | Missing model and an idle prompt failure are settled; a non-idle failure is not; the real host process emits `settled: true` on its `error` record. |
| A2 | `runtime/tests/test_pi_adapter.py`: `test_only_host_attested_sdk_error_is_settled` | Only `settled: true` removes the uncertain text. |
| A3 | `runtime/tests/test_worker_recovery.py`: `test_settled_sdk_error_allows_fresh_recovery_and_unattested_error_blocks` | Pre-session and overflow errors recover with `fresh` and checkpoint; pre-session `continue` is blocked; an unattested error blocks every action. |

**Limits.** Local tests with SDK mocks. A real provider overflow through the bridge is not run.
The pending-question branch of the host rule has no direct host test; the existing question
tests and the non-idle test cover the strict side.

## Risks

- **R1 — Detached processes.** A tool can start a background process that outlives the agent
  run. A normal successful return has the same risk; the existing effect checks still apply.
- **R2 — Wrong attestation.** A wrong `settled` could let a new worker race a live writer. The
  host attests only from observed SDK state, never from text, and the default is uncertain.
