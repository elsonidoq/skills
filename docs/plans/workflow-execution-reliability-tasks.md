# Workflow execution reliability — implementation tasks

## Approval record

Authorized direct-adapter task preparation/checkpoint only. Requirements truth is the
[separate TinySpec](workflow-execution-reliability-tinyspec.md), SHA256
`c7eb4f39d3ad0480e66a2577831714d611d60f0f38e80b1bdaf787326e9aa323`.
Owner selected TinySpec and granular tasks. Fresh independent source review
`dd0be1fb-91c6-4c1a-8dc9-eef677bfe7b8` reported zero material findings;
parent verified unchanged source. This is not task approval or implementation approval.
Planner review and combined current-content owner approval remain pending. No behavior,
live-agent compliance, or implementation readiness is claimed here.

## Shared worker/reviewer brief

[Executable JSON](workflow-execution-reliability-tasks.json) owns task-local scope, owned
paths, REQUIRED pass/evidence/permission mappings and runnable check fields. This document
is its concise presentation and shared brief; do not duplicate commands into prose or
compile semantic criteria into shell. Read each task's source criteria and REQUIRED items
before work; return actual results, limits and affected blockers. Missing/failed checks
are not passes. Keep focused tests and relevant current operational docs with each outcome.

Exact selected executor path, **read by this producer before decomposition**:
`/home/dev/.paseo/worktrees/0zfm1a0e/poor-fireant/.pi/workflow-executor.json`.
It selects `openai-codex/gpt-5.6-terra`, **medium**, for implementation and
`openai-codex/gpt-6.1-sol`, **medium**, for independent review. Task production's saved
Sol/medium assignment is not the worker binding. No configuration changes or substitutions.
These tasks separate independent interfaces; none requires future unfinished work to accept.
The sequential runner serializes shared-file edits; shared paths alone introduce no fictional
producer dependencies. Final integration review uses the original complete scope plus valid
cumulative correction coverage, not just the last task's delta.

Applicable authority, consumed by the task-local checks:

- [ADR-0003](../decisions/ADR-0003-current-launch-authority-and-neutral-tasks.md),
  accepted with no recorded superseder: T001/T007 review neutral executable tasks;
  T002–T004 and T005/T006 briefs retain current scoped launch authority through initial,
  corrective and resumed work. Historical phase text is not a veto on a later authorized launch.
- [ADR-0004](../decisions/ADR-0004-shared-routine-worker-permissions.md),
  accepted with no recorded superseder: preserve the shared `_ROUTINE_AUTHORITY` mechanism,
  small isolated fixtures/databases and ordinary scoped fixes without repeated approval.
  T002–T007 REQUIRED mappings retain actual required/manual, paid application/API,
  credential/security/data, global-install, external-action, deployment/push and unrelated-byte gates.
  Authority supplies neither a missing check pass nor expensive retry consent.
- [Unified memory](../../memory/MEMORY.md), verified through [AGENTS](../../AGENTS.md),
  read whole: coordinator owns routine technical diagnosis; questions are for actual
  product/material-scope/permission decisions; correction-only review preserves unaffected
  coverage; routine repair authority is not repeatedly requested; transitions need no parent
  acknowledgment. T006/T007 apply these to recovery, not a new memory/approval service.
- Preserve [constitution](../../.specify/memory/constitution.md),
  [focused task checkpoints](../../skills/memory-handling/references/task-commit-contract.md),
  [documentation ownership](../index.md) and source binding constraints. Current owner
  removal of the Pi-version requirement governs; older REQUIREMENTS text does not restore it.
  Changed global skills/prompts require a Paseo fresh-session handoff verifying checkout,
  revision, current approval and loaded capabilities, never `/reload` or automatic restart.

Scope/exclusions are the source's **Outcome and bounds**, **Binding constraints** and
**Risk rationale, limits and gates**, unchanged: no Cerca/application changes, active task
rewrites, historical sessions/runs/experiment replay or migration, model evaluation,
installs/auth/reloads/deployments/external writes, model selection changes, wider tooling
policy, recovery framework/evidence schema/risk scoring/admission machinery, report chains,
mandatory prototypes, arbitrary quotas or automatic fresh sessions/retries. Only the owner's
initial-plus-two same-task/session dispatch allowance is added; reviewer/fixer lifecycle gets
no numeric limit. Preserve six startup linter rules, task fields and ordinary SDK lifecycle.
No live-model evaluation gate or Cerca/SSH prerequisite is introduced.

## Bounded outcomes and dependencies

- [ ] T001 Make bounded independent acceptance explicit for creators and reviewers.
  - **Depends**: none
  - Shared authoring and final-review carriers plus focused instruction/scenario fixtures.
    Accept bounded slices and legitimate wiring; challenge milestone bundles. REQUIRED T001/V1
    maps A6/A7; acceptance is contract delivery, not model obedience or a new semantic linter.

- [ ] T002 Correct the actual registered task-outcome cue.
  - **Depends**: none
  - SDK registration and shared completion text agree on continuing correctable unfinished work;
    genuine unsuccessful reporting/diagnostics and stop-before-acceptance survive. Own focused
    host/authority/outcome tests and current docs. REQUIRED T002/V1 maps A3/A7.

- [ ] T003 Enforce durable initial-plus-two dispatches per exact task-worker session.
  - **Depends**: none
  - Common pre-adapter dispatch, ordinary required history and effective explicit/held session
    identity; reopened storage, check/checkpoint corrections and duplicate-row controls.
    Own tests/docs and narrow coordinator no-quota exception. REQUIRED T003/V1 maps A4/A7.

- [ ] T004 Project compact nonrecursive continuation and diagnosis context.
  - **Depends**: T003
  - Consume durable invocation/session identity; remove embedded prior full prompts from both
    worker and coordinator diagnosis inputs while retaining actionable scope, evidence and
    authority/acceptance. Preserve original inspectable history. REQUIRED T004/V1 maps A5/A7.

- [ ] T005 Deliver retained actual check evidence to read-only independent review.
  - **Depends**: none
  - Initial and follow-up review receive applicable command/result/output, checkpoint/revision
    association and limits from existing check/history producers; private output stays private.
    This handoff accepts without the later transition. REQUIRED T005/V1 maps A2/A7.

- [ ] T006 Resume same-head evidence-only review without fixer or task replay.
  - **Depends**: T005
  - Existing explicit resume/chain/history gains only the owner-pair-v1 evidence-gap transition,
    substantive changed basis, fresh independent reassessment and retained cumulative coverage.
    Test real Git/check/reopen seams and no-dispatch controls. REQUIRED T006/V1 maps A2/A7.

- [ ] T007 Make material risk handoff actionable before coordinator reliance and recovery.
  - **Depends**: T001, T003, T004, T006
  - Review→investigation→worker brief carries material prerequisite, affected task, evidence or
    unknown and next action. Integrate supported worker/reviewer recovery and precise unavailable
    boundaries with instruction/scenario checks and current docs. REQUIRED T007/V1–V2 map A1/A6/A7.

One valid order is T001 → T002 → T003 → T004 → T005 → T006 → T007. Only named edges
are producers: T004 consumes T003's durable identity/history; T006 consumes T005's actual
private evidence handoff; T007 integrates completed atomicity, allowance/compact-context and
supported evidence-reassessment interfaces. No dependency on future live evaluation or
unfinished application work. Focused ordinary tests/docs/teardown remain in their outcome.

## Coordinator preparation, risks and evidence limits

- **Available:** inspected production `invoke_worker`, explicit/adapter-held PiAdapter session
  resolution, host opened-session reporting, Store required-write/chain logic, CLI resume and
  refresh paths, `verification.run_checks`, `ProjectTest` disposable-Git harness, review/resume/
  authority/outcome selectors and planner checker/scenario carriers. Existing intake admits
  synthetic contracts with the six linter rules; coupled fixtures need no new admission schema.
  Existing check records already contain command/exit/output; T005 consumes them unchanged.
  Existing coverage/attribution and settled-fixer recovery are delivered mechanisms to preserve,
  not work to recreate.
- **Highest mechanical risks:** T003 must associate fresh initial calls with actual session
  identity and reserve distinct invocations before dispatch even through persistence failure;
  T006 must admit only causal, same-target evidence reassessment without fake fixer/grant or
  lost checkpoints/coverage. Permanent tests at these production boundaries, including reopen
  and operation-local failures, are the earliest sufficient proofs inside those tasks. No
  consequential unknown SDK API needs a disposable prototype; do not add one. Failed/unrun
  proof blocks its affected consumer, not unrelated safe work. Changed scope/acceptance returns
  to affected existing review/approval; retain disproof and do not weaken the oracle.
- **Concrete regression adjustment:** the current unfinished-task resume fixture permits four
  calls. T003 must update that scenario to assert the new common-boundary refusal and preserve
  its unrelated-byte/checkpoint controls; it is not a legacy compatibility exception. The
  existing findings-free rejection stop remains a control until T006 supplies a genuinely
  changed diagnosis/evidence basis. `refresh-review-target` is not a same-head workaround.
- **Prepared environment:** Python 3.12.3, Node v24.21.0, Python runtime/test imports and existing
  SDK import were verified without provider calls/setup. System Python has PyYAML 6.0.1 while
  runtime metadata declares 6.0.3; imports work, but dependency pin conformance is not asserted.
  The guide's local validation-venv executable is absent; commands use the actually available
  `python3`, explicit PYTHONPATH and disabled bytecode. Planner test CLI supports the named
  existing `EarlyRiskReductionTests` selector; new scenarios stay there. No future implementation
  tests were run or reported passing during task production. If a required operation fails in
  execution, report that exact capability/dependency boundary and correction; do not install
  automatically or invent a blanket environment/version gate.
- **Behavioral unknown:** A1/A6 instruction/scenario tests establish contract sensitivity and
  handoff order, not autonomous coordinator judgment, task decomposition quality or actual
  model compliance. A3 tool/prompt tests verify real cue delivery and unsuccessful mechanics,
  not the cue's behavioral effectiveness. Synthetic adapters prove A2/A4/A5 mechanics, not
  live-provider success. Keep these limits in worker/reviewer returns; no unapproved live-model
  evaluation is required. No real target access is needed for this package's acceptance.
- **Real gates:** usable existing check runtime, ownership and focused verified checkpoints,
  fresh independent read-only final implementation review and genuine source/manual/paid/data/
  external permissions survive. Coordinator investigates routine worker and reviewer failures
  before targeted supported continuation, not blind expensive retry. Unknown effects/live or
  uncertain invocation and target drift require reconciliation. Fresh context needs applicable
  inspected necessity/owner authority; the allowance refusal never grants it.

## Planning validation and review handoff

JSON and Markdown graphs must agree. Inspect traceability A1–A7, task-local REQUIRED mappings,
actual owned production/test/doc seams and final observable, executable check shapes, link
resolution, scope and diff whitespace. The scripts prove only the six startup/graph checks;
manual inspection supplies granularity/feasibility review, not implementation acceptance.
The authorized producer checkpoints only these two artifacts and the single discovery entry;
source, configuration, historical artifacts and substantive contracts remain unchanged.
