# Implementation Plan: Lean Workflow Corrections

Apply [Parsimony and Actionable Checks](../../skills/planner/references/parsimony.md).

**Branch**: `plan-standard-spec-flow-issues-23-28` | **Date**: 2026-10-26 | **Spec**: [spec.md](spec.md)

**Input**: Approved specification SHA-256 `56142ed66267fbbd40c29d400e87bbad9a28f041071e37d2b9877036fc811065`; [current approval](spec-approval.md). Historical draft/next-stage wording in the unchanged specification describes its production stage, not current approval. No substantive specification inconsistency was identified; no approved bytes were edited.

## Summary

Deliver six independent lean corrections: unsuccessful task completion and executable command handoff (#23/#19), routine authority precedence (#24), diagnosed coordinator repair/continuation (#25), investigated and independently reviewed issues (#26), line-range citations (#27), and exact authorized recovery-file handoff (#28). Reuse the existing runtime, command fields, shared defaults, continuation, issue tracker and Git checkpoint mechanisms.

Settled owner constraints: “This must be a lean solution. A first small iteration to remove things that can be executed from agents and place it as executable contracts among other things. It is crucial that agents do not add tons of checks that end up making the workflow don't run at all. Checks must be few and principled.” This is “not a cross-layer workflow redesign”.

[research.md](research.md) is the canonical supporting-spans → decisions → observable-checks owner. [Contracts](contracts/README.md) capture only changed public behavioral seams; [data model](data-model.md) describes existing state, not a new persistence schema; [quickstart](quickstart.md) schedules verification. Specification V1–V6 and exclusions remain authoritative.

## Technical Context

**Language/Version**: Python >=3.10; JavaScript ESM host, Node >=22; Markdown skills and Bash SpecKit tooling.

**Primary Dependencies**: existing PyYAML 6.0.3, Pi SDK 0.87.1, Git; no new framework/dependency. SpecKit 1.0.12 pi/sh used for this plan.

**Storage**: existing SQLite progress/history, runner-private Pi sessions and Git. No migration, historical rewrite or evidence registry.

**Testing**: existing Python unittest fixtures with actual Engine/Git/check subprocesses and stub adapters; existing Node bridge/session fixtures where changed; controlled supported V3/V4 exercises with truthful actual/simulated attribution.

**Target Platform / Project Type**: existing local Pi skill suite and sequential CLI runtime, not an application-service redesign.

**Constraints**: exactly six existing task-intake rules; no extra runtime model calls for #23/#24/#27/#28. #25 repair delegation and #26 separate reviewer remain required. Current selected executor is Terra/medium worker and Sol/medium reviewer, read from `.pi/workflow-executor.json`; task producer must reread it before decomposition. Saved plan assignment remains Astra/medium, not implementation routing.

**Scale/Scope**: six independently useful outcomes; #19 consolidated only into #23. No invented time/resource/task-count thresholds.

## Constitution Check

Pre-research and post-design: PASS against Constitution 4.2.0, with no policy amendment or new exception.

- Portable global assets: skill/runtime changes use project routing and selected configuration, never fixed project paths/models. This feature's artifacts may identify this worktree.
- Evidence before guidance: current source/pins underpin choices; exact external #24 wording remains UNVERIFIED. No memory/ADR writes or inferred policy.
- Explicit authority: [spec approval](spec-approval.md) permits this design stage only; source unchanged. V3/V4 future live actions retain their gates. No calls, historical replay or implementation now.
- Pragmatic verification: preserve V1–V6, put permanent checks at changed seams, omit speculative prototype/platform matrices. Static delivery proof is not model-obedience proof.
- Safe execution/recovery: actual checks and focused commits precede reliance; unsuccessful results cannot release dependents. Preserve unknown work, hooks/signing, original history and fresh final review. AGENTS' later owner-authorized concurrency direction supersedes the constitution's older blanket single-writer wording; overlapping edits still require coordination and actual lock safety.
- Compatibility: TinySpec/Standard share executable command guidance; existing neutral tasks, no-command/no-change success, correction paths, manual gates and selective recovery survive.

## Project Structure

```text
specs/005-lean-workflow-corrections/
  spec.md                  # approved requirements, unchanged
  spec-approval.md          # existing current authority, unchanged
  plan.md
  research.md              # canonical technical evidence
  data-model.md
  quickstart.md
  contracts/README.md
  # tasks are a later separately produced artifact
runtime/coherence_workflow/
  engine.py                # completion and review parser seams
  verification.py          # existing command consumer; preserve unless causal need
  git_effects.py            # exact ownership/claim/checkpoint seam
  cli.py                   # existing retained continuation/input integration
runtime/pi-host/host.mjs    # existing transport; change only if needed by demonstrated seam
runtime/tests/             # existing engine/check/authority/resume/review/Git fixtures
skills/task-generation/SKILL.md
skills/coordinate-implementation/SKILL.md
skills/track-open-issue/SKILL.md
.pi/extensions/coordinate-implementation-bridge.js  # existing continuation/question API
scripts/                   # relevant existing contract fixtures
```

**Structure decision**: localized corrections to existing owners. Do not pre-authorize edits to every listed layer; implementation owns only paths necessary for its demonstrated correction. Update operative documentation alongside each affected outcome: skill contract first; runtime behavior in `docs/coordinate-implementation.md` and interface changes in `docs/coordinate-implementation-schema.md`. Routing/README changes only if entrypoint discovery actually changes. Do not update historical plans, global settings or unrelated indexes.

## Design and meaningful sequencing

These are delivery boundaries for later decomposition, not tasks or an execution assignment. No cross-issue producer dependency is established. Shared-file overlap is scheduling/ownership coordination, not a fabricated dependency. Keep related edits consecutive when possible. The task producer should split independently testable behaviors where one assignment would carry unfinished concerns, retain tests/docs/checkpoint with each outcome, and use the actual selected executor configuration rather than a task quota.

### Completion and command handoff — FR-001–003,005 / V1

Two independently testable seams share Story 1: task-return acceptance in Engine, and task-authoring → executable command handoff. Keep these bounded in task decomposition; composed V1 belongs where both are available, without a separate report/cleanup chain.

At return, distinguish terminal unsuccessful work from invocation transport and later semantic acceptance. Stop success-path checkpoint/session settlement/completion/dependent release and final review/fixer on explicit blocked/failed/incomplete work or known unmet required acceptance; retain partial edits and actual history. Preserve safe in-task check/checkpoint correction: corrected errors are not sticky vetoes. Required failed commands may be repaired and actually rerun successfully; blocked worker returns are not permission for another expensive call. Do not change question delivery into cancellation.

Author deterministic commands directly into the existing `checks`, `check` or `required[].check` consumer field, once; retain non-command semantic criteria as prose. Verify both task adapters' shared guidance, not a new prose compiler. Optional absent checks remain absent. Do not prescribe a worker-result schema, keyword scanner or additional judging call; pin the behavioral boundary through the actual-engine V1 negative/positive cases before accepting the smallest compatible implementation. Resume changes are permitted only on a demonstrated focused bypass, not a general recovery redesign.

### Authority precedence — FR-004–005 / V2

Use current scoped authority and `_ROUTINE_AUTHORITY`, not per-task renewed resource consent. Reproduce the reported agent-authored restriction conflict in a labelled fixture and patch only a proven causal instruction/handoff. External incident wording is not established current code. Preserve genuine owner limits, explicit manual gates and paid/security/data/external boundaries. [ADR-0003](../../docs/decisions/ADR-0003-current-launch-authority-and-neutral-tasks.md) requires authorization-neutral future tasks and current authority injection; its historical fix is not completion proof. [ADR-0004](../../docs/decisions/ADR-0004-shared-routine-worker-permissions.md) requires shared ordinary scoped fix/test/database/server/dependency/artifact permissions without a permission service or universal ceilings. V2 verifies these both positively and against genuine restrictions at changed handoffs only.

### Scoped coordinator repair — FR-006–007 / V3

Coordinator inspects cause/invocation and settles/reconciles the failed worker and lock. Arrange an explicit separate repair scope for the necessary out-of-worker-path file, under the same current selected executor; do not widen original worker ownership or let it delegate. Inspect repair diff, relevant actual checks and focused checkpoint before invoking supported retained continuation. Existing CLI `resume` and parent bridge `coordinate_implementation_start` with `resume` are the starting mechanisms. Reuse suitable retained unfinished sessions and skip completed tasks; investigate later routine questions autonomously through the existing reply route.

Clarify “No automatic resume” as no blind uninspected retries or historical automatic restart, not a demand for routine renewed consent after diagnosed authorized repair. No new cancellation/steering/recovery API. Only a concrete failing supported exercise can justify runtime changes. V3 requires the repair/checkpoint/continuation/later-question sequence, not merely new instructions.

### Investigated, reviewed issue entry — FR-008–010 / V4

Replace the existing `track-open-issue` behavior in place. Evidence-based RCA precedes create/readback. Give a separate read-only reviewer original intent, evidence and actual read-back body, using selected reviewer configuration; review ambiguity, omissions, assumptions promoted to requirements, scope creep and unnecessary mechanisms/checks. Evaluate rather than blindly apply findings. Make narrow ordinary corrections under existing mutation authority, rechecking latest body and reading back independently; material outcome changes return to owner. No automatic review loop or application fix.

Preserve exact target discovery/auth/sensitive handling, complete open+closed duplicate search, existing duplicate behavior, narrow fields and concurrent-content protection. Creation success and review completion are independent. Uncertain RCA remains honest investigation; unavailable review remains incomplete. V4 must include an actionable drift correction, not only a clean reviewer response.

### Citation ranges — FR-011 / V5

Extend only the existing parser location compatibility for `path:717-723 - defect` alongside `path:717 - defect`. Preserve exact finding strings, verdict and invalid JSON/type/missing-location guards. Verify rejected-review/repair flow, not regex alone. No historical finding repair.

### Explicit existing-file handoff — FR-012–013 / V6

Provide an optional exact-file transfer through current execution input/ownership mechanisms, distinct from `owned_paths` limits and generated artifacts. Only explicitly authorized identified pre-existing files become eligible; no directory/glob adoption or inferred authority from a broad path limit. Reconcile target content at transfer/edit time; preserve pre-handoff bytes except intended edits. Reuse `FocusedGit` claim/facts/checkpoint rather than fabricate old history. Refuse unapproved/drifted targets with file, affected operation and supported corrective action. Exact optional syntax can stay local to implementation; it must be reachable through the real supported input path and tested there as well as actual Git ownership. Do not introduce a permission ledger or general dirty inventory.

## Verification, risks and delivery gates

All V1–V6 are **NOT RUN** here. [quickstart.md](quickstart.md) carries future scenario/check owners and expected evidence. V1/V5/V6 need permanent offline actual-engine/Git regressions (fail-before/pass-after where required). V2 distinguishes instruction delivery from model behavior. V3/V4 retain composed behavioral demonstrations; offline stubs alone cannot establish autonomous investigation/independent judgment. Missing future live capability/authority is a delivery evidence gap, not a planning blocker or waiver. No forced paid/live/historical exercise.

No separate prototype: existing bounded seams and fixture infrastructure suffice. The main risk is false positives/negatives at the completion boundary; positive controls and existing correction tests earn their cost. V3 may uncover a concrete continuation limitation; investigate before runtime expansion. V4's review/mutation separation must preserve concurrent content. V6 must not relax unknown-byte protection. Tested evidence is revision/environment-specific; invalidate only affected checks and return material scope/acceptance changes to producing review/approval.

[Memory guidance](../../memory/MEMORY.md#routine-technical-decisions-and-review-scope) changes the coordinator and issue-correction decisions: “Handle routine technical decisions autonomously; ask the owner only for product decisions or material scope creep. Preserve mandatory explicit permission gates rather than treating this preference as consent.” Correction-only review stays on affected behavior. It does not authorize issue writes or optional external actions.

## Migration, rollback and activation

No database migration or historical outcome rewrite. Preserve existing task input and optional fields; new exact-file transfer must be optional. Keep old single-line citations. Roll back a faulty correction with a separately authorized focused corrective commit, never reset/discard partial work or reinterpret historical acceptance. Global skill/tool changes require a Paseo fresh-session handoff and verification of checkout/revision/current approval/loaded capability, not `/reload` or automatic restart. No activation is required for these planning-only Markdown artifacts.

## Scope exclusions and next boundary

All [spec exclusions](spec.md#exclusions) apply unchanged: no cross-layer redesign, new startup/admission machinery, recovery service/matrix, cancellation/steering API, history migration, evidence receipts/registries, permission schema/service/ledger, quotas/timers, extra model calls for #23/#24/#27/#28, broad cleanup, application repair/restart/production/deploy/index rebuild, paid application API, auth/global changes or acceptance relaxation. No implementation or tasks were produced in this pass.

Next: parent inspection, separate fresh task producer reading actual selected executor, independent overall review and current overall owner approval. Specification approval does not authorize implementation. Complexity tracking: no constitution violations to justify.
