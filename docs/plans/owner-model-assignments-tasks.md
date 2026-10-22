# Owner-controlled planner model assignments — implementation tasks

## Source and executable handoff

Requirements truth: [TinySpec](owner-model-assignments-tinyspec.md), committed at
`2379b47d9c9b3ce6b527ae561be2ac660b6fe7ec`. Separate executable tasks:
[owner-model-assignments-tasks.json](owner-model-assignments-tasks.json).
The JSON contains the owned paths, executable checks, scope/exclusions and task-local
**REQUIRED** pass/evidence/permission mappings; it is not a new assignment store.

## Shared implementation context

Read the whole source and applicable task before changes. Carry these constraints and
links into each actual worker brief, alongside its local REQUIRED items:

- [AGENTS](../../AGENTS.md), [constitution](../../.specify/memory/constitution.md),
  [documentation routing](../index.md), [task-generation direct adapter](../../skills/task-generation/SKILL.md)
  and [focused task-commit contract](../../skills/memory-handling/references/task-commit-contract.md)
  govern portability, source authority, bounded outcomes, dependency release, verification
  and explicit-owned-path checkpoints. Planning produces no implementation assignment.
- [ADR-0003](../decisions/ADR-0003-current-launch-authority-and-neutral-tasks.md):
  an owner-authorized implementation launch approves the assigned task scope; historical
  planning-only/awaiting-approval wording must not independently block that work. Preserve
  current authority in initial, corrective and resumed worker prompts, without rewriting
  source/approval provenance. Executable instructions and check permissions remain
  authorization-neutral; temporary phase status belongs only in the approval record.
  Preserve real requirements/manual/permission gates and current-content approval checks.
  T003 verifies prompt delivery; T004/T007 preserve the planning-to-task mappings.
- [ADR-0004](../decisions/ADR-0004-shared-routine-worker-permissions.md): retain one shared
  ordinary scoped permission block, including scoped fixes and small isolated tests/local
  databases without repeated questions. Keep test data/execution bounded so they do not
  exhaust machine resources or affect unrelated data/services. Preserve credential,
  unrelated-data, resource, paid-scope, global-install, deployment/push and external-action
  boundaries. No new permission protocol, universal size cap or resource subsystem.
  T003's existing worker-authority checks verify both initial/corrective prompts and a tiny
  database; T007 retains these outcomes through both adapters.
- The latest source assignments supersede active routing rubrics and the old fixed plan
  exception. The owner-launched parent's model **and effort** remain deliberate authority,
  never a forced parent switch. Canonical installed planning JSON owns planning choices;
  the selected project executor JSON alone owns workers/fixers and reviewers/rereviewers.
  Preserve the current runner values. No comparison, recommendation or fallback.
- Both future task producers must themselves read the project's selected actual executor
  file before decomposition. Pass/discover that path from project routing, not a reusable
  hardcoded repository layout. Valid present choices require no repeated owner question.
  This producer actually read `.pi/workflow-executor.json` before decomposition; its
  configured worker/effort guided the bounded task seams below, not the producing model.
  Exact read evidence is in the producer return, not a new ledger or duplicate JSON binding.
- Preserve fresh artifact producers, producer checks, parent inspection before dependent
  stages, TinySpec parent-owned review, independent Standard overall review/fresh rereview,
  source/spec/task approval ordering and current-content owner approvals. Do not add a
  separate plan reviewer. Corrections retain the producing-stage assignment/context;
  conflicting changed saved choices ask only the affected-stage resolution.
- Preserve dependencies, task-local REQUIRED/manual checks, focused commits, unrelated work,
  hooks/signing, old progress/history rows and existing custom/STATE content. No branches
  or worktrees, probes, installations, deployments or external actions. No paid/provider
  prompts, automatic auth refresh/reload/restart, blind expensive-run retry, benchmarks,
  prototypes, new dispatcher/model platform, administrative artifacts or history conversion.
  Inspect expensive failures and actual invocations before targeted resume/retry; unknown
  cause blocks replacement. Report ordinary safe errors without admission ceremonies.
- [Gotcha index](../../memory/MEMORY.md) has no recorded entries;
  [coordination guidelines](../../memory/coordination/GUIDELINES.md) have no approved guidance.
  They supply no routing defaults or authority for memory/ledger writes. Historical research
  and approval records remain unchanged and discoverable as historical. OpenCode is excluded.
- Latest explicit owner clarification: delete obsolete test cases, fixtures and checker rules
  enforcing retired routing/selection/eligibility contracts. This is a radical contract change,
  not a compatibility exercise: no shims, aliases, stale-heading preservation or text hacks.
  Add focused new owner-JSON/exact-dispatch/producer-read assertions. Retain meaningful current
  permission, approval-provenance, dependency, checkpoint, REQUIRED-check and reviewer-independence
  coverage. Classify stale baseline diagnostics against current guarantees: delete obsolete
  assertions, never resurrect retired eligibility language or drop real safety merely to green.

Checks may use existing isolated fixtures, not real user configuration or provider access.
The concrete early risk is SDK effort clamping/overrides and implicit reviewer inheritance:
T002/T003 use permanent actual-boundary tests. No separate prototype is warranted. SDK 0.87.1
construction verifies exposed state, **not** provider-internal execution or live availability.
Requested binding, SDK-exposed observation and unknown actual must remain distinguishable.

## Bounded outcomes and dependencies

Each task includes its own tests, relevant local documentation, diff inspection and focused
checkpoint. The JSON's exact owned paths restrict mutation. Shared paths are dependency-ordered;
the existing runner executes sequentially. No task depends on unfinished downstream acceptance.

| ID | Outcome / bounded interface | Depends | REQUIRED source mapping and observable |
| --- | --- | --- | --- |
| T001 | Canonical installed planning JSON, concise shared resolution contract; optional small actual JSON helper, not a registry | — | A1/A3: every settled planning operation and explicit parent inheritance; temporary saved edits propagate, isolated symlink discovery works, invalid entries give role-specific correction without substitution |
| T002 | Exact SDK session/prompt assignment boundary, including saved/restored state | — | A3/A4: offline **actual SDK construction** detects clamped/unsupported effort and model/effort override before prompt; correct old unsupported fixtures rather than relax guard; preserve transport/tool behavior |
| T003 | Explicit reviewer config and configured execution role propagation | T002 | A4, ADR-0003/0004: reject omitted reviewer, permit explicit shared values with independent context, preserve worker/fixer/fresh review/rereview and safe resume/failure behavior; retain authority/permissions/history/checkpoints |
| T004 | Planner dispatch, inheritance, review and correction handoffs | T001 | A1/A3/A4/A5: every planner stage consumes shared choices unchanged; changed retained producer binding asks focused resolution; fresh producers, parent inspection and all existing approvals survive |
| T005 | Brainstorming assessment and decision application consumers | T004 | A1/A3/A5: both operations consume saved choice; no selection rubric; retain read-only preselection, owner dialogue and authorized application boundaries |
| T006 | Direct/helper Standard plan pass assignment propagation | T005 | A1/A3/A4/A5: whole pass uses saved assignment, one plan creation and producer checks; no old fixed exception, family scaffold, managed fallback escape or separate plan reviewer |
| T007 | Selected executor file reaches both task producers for their own pre-decomposition reads | T006 | A2/A4, ADR-0003/0004: actual producer read order and configured guidance differ from producer/parent defaults; no redundant question or binding copies; bounded neutral outcomes and real gates remain |
| T008 | Retire obsolete active policy and align operational docs/examples/authoring | T007, T003 | A5: delete old policy after operational migration; active owners agree, historical records remain intact, Paseo activation uses fresh-session handoff, runner values unchanged |
| T009 | Migrate maintained checker/mutations to assignment semantics; composed regression at first complete boundary | T008 | A1–A5: source-required planner/lint/runtime/saved-session checks plus manual consumer/docs review; preserve unrelated safety tests and report genuine baseline gaps |

The splits follow independently testable config, SDK, engine and existing skill-consumer seams,
not milestone/phase labels or a task quota. In particular T002 cannot be replaced by static
planner traces, and T001/T004 focused checks do not require migrated downstream consumers.
Broad planner checks belong to T009, when all active contracts and docs exist. T009 delivers
maintained checker behavior, not a separate evidence/report-only deliverable.

## Verification conventions and baseline

Python 3.12.3 and the existing `.pi/workflow-validation/venv/bin/python` are present. Runtime
checks follow [the operating guide](../coordinate-implementation.md)'s existing convention:
`PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=runtime:runtime/tests` with `python -B -m unittest`.
Use the JSON check arrays and focused classes added in the existing test module; no new harness.

At source baseline `2379b47`, before task production:

- Producer ran `python3 scripts/check-planner-workflow.py`: **FAIL**, eight pre-existing
  coordinator wording diagnostics: validation-execution and verification-audit missing
  `Never adopt existing dirty files`; execution-checkpoints and verification-graph missing
  `runner establishes baseline HEAD`; execution-selection missing `No automatic`;
  execution-strategy missing `current terminal owner input`, `never invent an answer`,
  and `No automatic resume`.
- Parent separately ran `python3 scripts/test-planner-workflow.py`: **FAIL**, 146 tests /
  34 failures, reported output `/tmp/coherence-owner-model-baseline-tests.log`; the parent
  reports repeated versions of those diagnostics in the tail and will inspect failure types.
  The producer does not claim to have independently classified every failure. In the parent's
  earlier `&&` chain, the test command was NOT RUN after the failed checker.
- Producer ran existing `test_worker_authority` using the runtime convention: **PASS**, two
  tests covering initial/corrective authority and tiny isolated database permissions.

T001/T004–T007 add independently passing focused classes without requiring the broad checker
or deleting unrelated tests to green. T008 has its own focused fixture/manual review. T009
deletes obsolete routing/selection/eligibility tests, fixtures and rules and adds focused new
assignment tests. Classify pre-existing coordinator diagnostics against current guarantees:
delete obsolete assertions, or check equivalent actual current safety without text hacks,
stale headings, compatibility shims or resurrected eligibility language. A substantive unrelated gap is a reported blocker,
not permission for runtime rewrite or removal of dirty-work/owner-input safeguards.

Required evidence is actual commands/results, captured arguments/state/trace where mapped,
owned diff and checkpoint SHA in existing task/session returns. Missing checks are NOT RUN or
UNAVAILABLE, never PASS. Manual review distinguishes active policy from legitimate historical
mentions and task/product reasoning. Static fixtures cannot establish actual model obedience.
No live/paid model test or availability claim is required. A failed required check blocks only
its affected reliance; material source/scope/dependency change returns to affected existing
review/approval gates, not silent upstream repair.

## Planning review and owner approval

Owner selected TinySpec preparation. Source is committed; separate tasks are now produced.
Planner inspection and combined current-content source/task/scope approval remain pending.
Implementation is not yet authorized. Parent will inspect these tasks and obtain combined
approval before launching the coordinator with the existing selected executor file. No
separate source-approval or commit-permission question is required for this preparation.
