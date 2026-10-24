# Owner-controlled review convergence — tasks

Requirements truth: [TinySpec](review-convergence-tinyspec.md), source commit
`6732b6fef009b382ed1d887795f626e7b19fdbfc`, SHA256
`a4b05453e3a3e1a106fdba01bb4c83374fd5886f28987785e62a8becb5e67b14`.
[Executable JSON](review-convergence-tasks.json) owns task instructions, exact owned paths,
REQUIRED pass criteria, commands, evidence and action-specific permissions. This document
presents the same five outcomes/dependencies, not a second executable contract.

## Shared implementation brief

Read the whole source and the task's executable entry. Carry this shared brief and each local
REQUIRED mapping into worker/reviewer prompts. Source A1–A8 remain mandatory; no downstream
SDD as requirements input. The producer read the actual selected
[executor](../../.pi/workflow-executor.json): `openai-codex/gpt-5.6-terra`, medium workers;
fresh `openai-codex/gpt-6.1-sol`, medium reviewers. Keep configuration unchanged; the
source-producer profile is not the implementation binding.

- [ADR-0003](../decisions/ADR-0003-current-launch-authority-and-neutral-tasks.md):
  current scoped launch supersedes historical phase wording, not requirements, acceptance,
  real manual gates or permissions. Initial, resumed and corrective repair briefs retain
  that authority. Launch is not consent for later pairs, unrelated work or blind retries.
- [ADR-0004](../decisions/ADR-0004-shared-routine-worker-permissions.md): preserve shared
  routine scoped corrections and small isolated tests/databases/local setup without repeated
  questions, bounded against machine exhaustion/unrelated data or services. Preserve global
  install, credentials, deploy/push, unrelated deletion and paid application/test API boundaries;
  authority never establishes a passed check. This work does not authorize installation or
  activation. Ordinary configured model use follows launch, not an extra paid-API question.
- [Memory index](../../memory/MEMORY.md), Parent-turn notifications: routine transitions,
  completions and steering statuses never wake the parent; actual questions and terminal
  success/error may. The existing parent bridge still triages routine technical questions;
  owner-only continuation explicitly requires registered `ask_user` and actual owner answer.
- [Task checkpoints](../../skills/memory-handling/references/task-commit-contract.md): runner
  runs actual REQUIRED/manual checks, inspects owned changes and makes a focused checkpoint
  before dependents. Workers do not stage/commit. Preserve hooks/signing, unrelated
  staged/unstaged/untracked bytes, original checkpoints, old rows and causal lineage.
  Inspect actual failure/invocation before targeted same-stage correction; unknown/live work,
  unclear scope, material permission conflicts or uncertain effects stop the affected action
  with a concrete corrective diagnostic. Never duplicate paid calls or possibly completed commits.
- Source Approach 1–4 controls: retain first automatic repair; every later actionable rejection
  needs one durable actual-owner grant before its assigned pair, consumed once atomically.
  Next acceptance is always fresh/read-only and original base→actual final repaired head.
  Suggestions do not block; real material defects remain blockers. Malformed/nonactionable/
  uncertain/failed stages are honest stops, not approval or replacement-pair permission.
  Repairs examine related adverse paths and integrated original acceptance without expanding scope.
- Retain named new policy in existing private `execution_run_inputs.authority`; absence means
  historical two-review/one-fixer, unknown means actionable unsupported-policy stop. Use existing
  append-only `execution_history` for authorization facts, never raw owner Q/A. Helper/record
  shape is necessary derived design, not an owner-prescribed schema or new ceremony. No parallel
  ledger, new engine, identity service, startup gate or automatic historical upgrade.
- Exclude application fixes, old run restart/replay/migration/backfill, approval/result rewriting,
  executor/model changes, broader planning workflow, installs/reloads, deployment/push,
  credentials, ADR/memory/STATE/review-ledger writing and live provider regression. Optional
  monitoring/metrics gaps remain nonblocking and non-authorizing; artifact SHA is not reviewed code.
  Changed bridge/skill activation uses a fresh Paseo session verifying checkout/revision/current
  approval/loaded capabilities, never owner `/reload` or automatic restart.

## Outcomes and dependency order

- [ ] T001 Deliver compatible findings/suggestions verdicts and safe persisted owner output.
  - **Depends**: none
  - REQUIRED: A3 parser/outcome/CLI cases (including contradictory/nonactionable/malformed
    stops), ADR-0003/0004 prompt preservation; A8 lockstep protocol docs and safe legacy output.
    Local engine/store/CLI fixtures establish this contract without new lifecycle selection.
- [ ] T002 Deliver an actual-owner-only continuation route distinct from routine triage.
  - **Depends**: T001
  - REQUIRED: A7 terminal/socket/bridge marker, correlated pending/reply state, `ask_user`
    capability and routine-route rejection; memory wake-up boundary, existing routine and
    paid-API behavior; A8 interface/activation documentation. No dispatch policy yet.
- [ ] T003 Deliver retained-policy and atomic single-pair grant/reservation store primitives.
  - **Depends**: T002
  - REQUIRED: A2 grant-before-dispatch, exact rejection/range/scope/pair and causal eligibility;
    A5 transaction/reopen/idempotent required-write facts; A6 historical/no-policy preservation
    and unknown-policy stop; A8 safe status/history and storage docs. Explicit fixture policy
    exercises primitives; production new-start selection waits for the composed lifecycle.
- [ ] T004 Deliver a recoverable scoped repair stage with related-failure reasoning.
  - **Depends**: T003
  - REQUIRED: A4 actual initial/corrective brief delivery, reviewer model/context/writer
    transition, adjacent correction and outside-authority stop; A5 repair/check/checkpoint/
    outcome gaps with actual Git reconciliation and no replay/recommit; A8 paths, unrelated
    bytes, checks/hooks/signing/lineage and stage documentation. Legacy first repair stays usable.
- [ ] T005 Deliver the usable owner-controlled lifecycle and composed acceptance.
  - **Depends**: T004
  - REQUIRED: **A1–A8 together at this first usable boundary**, including multiple later
    rejections/yes grants and no-answer stops, fresh original-range rereviews, actual bridge
    decision→durable grant→dispatch order, policy compatibility and every specified reopen gap.
    Integrate verified predecessors into last-eligible-stage selection and safe finalization;
    retain optional-observation gaps and synchronize skill/operating/schema owners.

This serial order protects shared files and releases only verified checkpoint interfaces.
Verdict interpretation, owner transport, durable authorization and recoverable repair are
independently testable seams; the lifecycle selector consumes all four. T005 is one composed
transition outcome, not a milestone carrying unfinished transport/storage/fixer concerns.
Tests and relevant docs stay with each outcome; no prototype, test-only, phase or report task.
Permanent production-helper/lifecycle proofs address the known authorization/durability risk
before reliance, rather than an unnecessary disposable experiment.

## Verification feasibility and limits

Observed preparation environment: Python 3.12.3, system PyYAML 6.0.1, Node 22.23.3 and Git/SQLite.
The actual CLI help confirms `intake --tasks PATH`; this command is the six-check linter,
not execution or approval. Focused baseline review/resume/authority/checkpoint modules passed
24 tests; `node --test runtime/tests/test_question_triage.mjs` passed its existing offline case.
These observations choose runnable commands, not evidence that new behavior already passes.

The canonical dependency owners are [runtime metadata](../../runtime/pyproject.toml),
[SDK package](../../runtime/pi-host/package.json) and
[setup/verification](../coordinate-implementation.md#setup-and-verification).
The repository's documented `.pi/workflow-validation/venv/bin/python`, bridge fixture's
`runtime/.venv/bin/python` and local `runtime/pi-host/node_modules` are absent in this checkout;
`/tmp/pi-workflow-prereq-venv/bin/python` has no PyYAML. System Python can run focused Python
fixtures/intake but is not the pinned PyYAML 6.0.3 prepared runtime. SDK-dependent
`test_bridge.mjs` / `test_host.mjs` acceptance is **UNAVAILABLE until separate authorized
preparation supplies those actual dependencies/paths**; do not silently skip, install, weaken
checks or claim readiness. No new dependency/API selection or internet research is needed.
An actual `node --test runtime/tests/test_host.mjs` attempt failed at module loading with
`ERR_MODULE_NOT_FOUND` for that local SDK import; no provider was invoked. This is a dependency
gap, not a behavior regression or permission to waive acceptance. T002's factory/transport
fixture and Python tests remain runnable independently of that gap.

Use the exact focused commands/pass conditions in executable REQUIRED entries, no broad suite
by default. Compare changed local links and operative prose to actual implementation; run
`git diff --check`. Report PASS/FAIL/NOT RUN/UNAVAILABLE and reuse only still-applicable proof.
Offline SDK/adapter/prompt tests prove transport, tool/session and lifecycle behavior under
fixtures, not live human participation, provider/model obedience or defect-free application code.
The separate fresh independent read-only final review covers the whole original implementation
base→final repaired head; planning-only source/task diff is not implementation-owned work.

## Approval record

- Owner selected TinySpec and owner-authorized additional-pair policy; preparation and focused
  planning checkpoint authorized. Source remains unchanged.
- Fresh independent Sol 6.1/medium read-only specification review returned **ZERO findings** for
  the source identity above (`/tmp/coherence-convergence-spec-review.md`, session-local report).
  This is specification fidelity, not implementation acceptance.
- Parent task inspection/review and **combined current-content source/task/scope approval are
  pending**. Implementation, dependency installation/global activation and live workflow proof
  are not authorized by this production operation.
- Future combined approval slot: record actual owner answer, exact current source/Markdown/JSON
  identities, reviewed task scope, genuine permission/capability limits and launch authority
  here through the existing parent approval route. No producer approval or invented receipt.
