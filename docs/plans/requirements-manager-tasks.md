# Requirements Manager implementation tasks

**Status: APPROVED FOR OWNER-AUTHORIZED DIRECT IMPLEMENTATION (revision 3).**

## Provenance, review, and authorization

- Authoritative design: [requirements-manager.md](requirements-manager.md), sha256 `57629046c7e9faeb91d809fa4fc2c01da5270b538481536da14aa6611191ac13`, git blob `6b7250acb82650895cd9ef386ed140363ce8557e` before task execution.
- Historical EPIC contract: `32e12feb382a6a0acb7e9d7f2e82559e3d397f2e:skills/epics-manager/SKILL.md`. Pre-change current protections: repository revision `fa41d5f3f5aeb7ddfa9963222eff2c0447533059`.
- [Archived critique-revised tasks](reviews/requirements-manager-tasks-revision-2.md), [DeepSeek critique/fix](reviews/requirements-manager-deepseek-critique.md), and [independent task review](reviews/requirements-manager-task-overall-review.md) preserve historical evidence. Their earlier 15-task/single-commit policies and hashes are superseded, not current instructions.
- Owner authorized: “launch a deepseek to critique and fix, then coordinate the implementation of this skill”; subsequently “don't review each task”, “do commit each one”, selected “Up to 3 local; above 3 delegate”, and confirmed “ok, continue”. This authorization applies to this revised task body: mechanical reviewer fixes plus those explicit policy changes, not unapproved scope expansion.
- Owner model choices: `sonnet-class` implementation → `openai-codex/gpt-5.6-terra`; `opus-class` implementation → `openai-codex/gpt-6.1-sol`; fresh independent reviewer → `openai-codex/gpt-6.1-sol`. T011's `opus-class` flag is resolved. These are project-local execution choices, never provider IDs embedded in global skills.
- Bootstrap uses this explicitly owner-authorized direct execution path. The current coordinator rejects direct lists and does not yet support the selected policy; do not pretend otherwise, fabricate specification/plan artifacts, or install/emulate SpecKit. T005 updates the reusable coordinator. Preserve source/task review evidence and current owner authorization.
- Approval identity: this revision's task definitions T001–T011 and the cited plan content, as committed in the preparation revision. Execution status/check evidence may change without altering approved task definitions. A fresh session compares those definitions to that committed preparation revision; substantive changes return to the owner. No recursive self-hash is required.

## Independent review dispositions

| Finding | Disposition |
|---|---|
| R1 baseline after rewritten primitive | Valid/fixed: coverage is now T001; new skill production depends on it. |
| R2 stale commits and plan hash | Valid/fixed: per-task commits, no per-task reviews; current source hash above; historical evidence archived unchanged. |
| R3 missing reorder mutation | Valid/fixed: T008 asserts canonical operational order and T009 mutates it while preserving bodies/diagram. |
| R4 bootstrap ambiguity | Valid/fixed: owner-authorized direct bootstrap is explicit above. |
| R5 pending settled reviewer choices | Already resolved by owner; recorded above without repeating selection. |

## Execution policy and safeguards

Ten implementation tasks plus one independent review task: 9 `sonnet-class`, 2 `opus-class` (18.2% of the complete list). Review-only tasks are excluded from implementation strategy sizing; this candidate still exceeds three implementation tasks and requires delegation.

- Up to three bounded implementation tasks may execute locally when the current owner-selected model/class is suitable and context is adequate. More than three require delegation using one shared dependency graph and consecutive, homogeneous, sequential story/stage batches.
- Task count is not context capacity. Reuse sessions only when model/class, relevant retained context, runtime support, and observed headroom permit it. No forced one-session-per-class limit. Smaller batches, including one task, are safe at dependencies, class/stage boundaries, conflicts, or context pressure.
- Verify and commit each task separately before starting the next. Batch grouping does not merge task commits. No per-task reviews; one fresh independent final review after implementation commits.
- Inspect failures before retry/relaunch; no blind retries, silent model switches, parallel implementation batches, pushes, installs, deployments, paid discovery probes, or product implementation.
- Material scope/architecture changes remain owner gates. Autonomous mechanical corrections remain within the approved design.
- Passing deterministic text tests proves prompt-contract conformance only, not runtime model obedience. Walkthroughs are static unless explicitly recorded as live.

## Tasks

### Coverage baseline

- [ ] T001 [Coverage baseline] Draft the source-derived requirement matrix, historical behavior inventory, and capability/fallback inventory before reading or writing any replacement skill.
  - **Depends**: none.
  - **Outcome / write scope**: add `docs/plans/requirements-manager-coverage.md`; add its index entry in `docs/index.md`. No skill/script changes.
  - **Sources**: original owner scope as preserved in design/handoff; historical EPIC commit above; pre-change EPIC/coordinator/create-epic, REQUIREMENTS, best-practices guidance, existing scripts/tests. Record derivation ordering.
  - **Required content**: columns `ID | source citation | required behavior | carrying stage/rule | status | rationale | task IDs | check/test IDs | evidence status`. Use preserved / changed-deliberate / removed-deliberate / removed-unaccounted classifications, and planned / verified / missing evidence.
  - **Historical inventory**: gate; optional brainstorm; exact decision application; reading/source contract; spec creation; plan spec-review/create/fix in one pass; create-only tasking; overall review; flagged-item categories, never-flag decisions, mechanically single-option auto-resolution, owner dialogue, decision capture, same-session correction when appropriate; deferrals; handoff context; interrupted/resume recovery; done readiness; fixed stage classes. Distinguish current safety rules replacing historical speculative material defaults.
  - **Capability inventory**: observed SpecKit commands/assets and stop conditions; delegation threshold change; question tool/fallback and applicable stage stops; class-binding owner selection; memory in suite-adopting projects; principles/constitution; independent reviewer availability. Cite pre-change lines and required unavailable behavior.
  - **Not restored**: obsolete platform paths/tools, resolver/state schema, named agents/provider IDs. Cite rationale; unaccounted behavior removal must be flagged, never silently accepted.
  - **Acceptance evidence**: each owner acceptance criterion and historical behavior maps to a sourced row, task, and expected check; inventory labels deliberate changes; no rewritten-prompt-derived coverage; lint and diff checks pass.
  - **Capability needs**: local read/write, git history, shell/static lint.
  - **Model class**: sonnet-class.
  - **Rationale**: citation-driven extraction; material ambiguity is recorded, not decided.

### Shared primitives

- [ ] T002 [Shared brainstorming] Extract one discoverable historical EPIC brainstorming primitive.
  - **Depends**: T001.
  - **Outcome / write scope**: add `skills/epic-brainstorming/SKILL.md` and focused adjacent deterministic tests. Preserve unrelated files.
  - **Acceptance evidence**: gate emits NO_BRAINSTORM_NEEDED or BRAINSTORM_NEEDED; bias toward skipping bounded/mechanical ambiguity; maximum three agenda items with concrete options; orchestrator owns one material owner question at a time; apply exactly approved decisions to bounded source; preserve deferrals, handoff, resume evidence, capabilities/stops. No independent fork or generic brainstorming substitution; valid discoverable frontmatter and resolvable references; focused contract tests and lint pass.
  - **Capability needs**: local editing, Python/test runner, static lint. No live model calls or runtime config edits.
  - **Model class**: sonnet-class.
  - **Rationale**: bounded extraction from historical source and T001 inventory.

- [ ] T003 [Shared task generation] Extract shared task semantics and centralize the task-order validator/tests.
  - **Depends**: T001, T002.
  - **Outcome / write scope**: add `skills/task-generation/SKILL.md`; relocate validator/tests from `skills/epics-manager/scripts/`; update observed callers, including EPIC validator pointer. Compatibility forwarding only for observed consumers; no duplicate validator implementation.
  - **Acceptance evidence**: common outcome/prerequisites/files/interfaces/evidence/capabilities/class+rationale contract; sonnet default, justified opus and 30% share gate; documentation/acceptance/integration coverage; consecutive IDs, earlier producers, contiguous stories/setup; manual implicit-dependency checks; project format discovery with numbered Markdown fallback. Unit tests accept prior ranges/none and reject missing/duplicate/gapped IDs, absent/forward/self prerequisites, and resumed stories. Check first ID starts at T001; correct any demonstrated gap in current validator. SpecKit and direct production adapters share semantics without making direct input require a plan. Lint and unit tests pass.
  - **Capability needs**: local editing, Python 3, repository search, static lint.
  - **Model class**: sonnet-class.
  - **Rationale**: localized contract/validator extraction with observable evidence.

### Restored producer and execution contracts

- [ ] T004 [EPIC workflow] Restore executable EPIC stages while retaining current safety protections and SpecKit wrappers.
  - **Depends**: T001, T002, T003.
  - **Outcome / write scope**: `skills/epics-manager/SKILL.md` and necessary related references/tests only.
  - **Acceptance evidence**: canonical operational order `brainstorm_gate → [epic_brainstorm → epic_brainstorm_fix] → spec_create → plan_create → tasks_create → overall_review → done`; each stage has entry, inputs, executable steps, outputs, gate/approval and resume contract, with class where delegated. Brainstorm fix/spec/tasks use sonnet-class; plan uses opus-class; gate sonnet-class; brainstorming is orchestrator-owned; overall reviewer is observed, independent, owner-selected. Gate skip and conditional fix paths invoke shared primitive. Plan reviews/corrects spec and creates/reviews/fixes plan in one turn; task creation is create-only; overall review owns task corrections. Preserve reading/flagged/handoff/deferral/resume behavior per inventory without speculative material defaults. Clarification conditional, approvals are checkpoints, specification approval renewed after changes before handoff. Preserve sizing/provenance, constitution/capability stops, documentation scope, current-version approvals, and fresh-session handoff. No diagram-only stages or obsolete platform/state conventions. Tests/lint pass; no unaccounted inventory removal.
  - **Capability needs**: local editing, history/search, static tests; no simulated SpecKit stage.
  - **Model class**: sonnet-class.
  - **Rationale**: approved sequence and inventory make this bounded prose-contract work.

- [ ] T005 [Coordinator] Generalize origin-specific intake and implement shared local/delegated selection with context-aware session reuse.
  - **Depends**: T003, T004.
  - **Outcome / write scope**: `skills/coordinate-implementation/SKILL.md` and coupled contract tests only.
  - **Acceptance evidence**: EPIC still needs current spec/plan, both approvals and required review/provenance; Requirements Manager needs durable approved source/tasks/review, no fabricated spec/plan or SpecKit prerequisite; other origins validate applicable gates, ambiguous origin blocks. Three bounded tasks permit class-suitable/context-safe local execution; four require delegation; strategy uses complete implementation-task count excluding review-only tasks, not origin/plan/remaining count; retain on resume unless recorded scope/safety changes. One graph and existing consecutive homogeneous sequential batch grouping, 5–7 only when safe, one-task batches allowed. Preserve owner class/model choice, prerequisites, integration, task checks, tracker, inspected failures, no unauthorized switch or local fallback above threshold. Resume only with observed context headroom and relevant class-matching sessions; rotate with durable handoff when necessary, no one-session-per-class cap. Commit every implementation task separately, no per-task reviews, one independent final review of complete committed diff. Route sequencing defects back to producer review, not silent reorder. Applicable checks/capability fallbacks explicit.
  - **Capability needs**: local editing/search/tests; runtime execution capabilities remain checked by future workflow.
  - **Model class**: opus-class.
  - **Rationale**: indivisible authorization/execution boundary with costly subtle failure modes.

### Lightweight producer

- [ ] T006 [Requirements Manager] Add plan-free orchestration using shared primitives and the coordinator.
  - **Depends**: T002, T003, T005.
  - **Outcome / write scope**: `skills/requirements-manager/SKILL.md` and focused tests only.
  - **Acceptance evidence**: accept detailed prompt/selected source; inspect project context/evidence/applicable memory; explicit sizing uses existing guidance and owner route decision rather than silent EPIC reroute; capture requirement/criteria/exclusions/constraints/sources/decisions durably in existing artifact or task list, not intermediate spec/plan. Shared gate decides optional historical brainstorming; direct task production uses shared standards; documentation scope comes from requirement/inspected changes. Requirement-to-task review and explicit current authorization precede handoff; durable content/revision evidence detects stale approvals. Handoff names source/tasks/review/approval; coordinator selects execution strategy itself. Capability unavailable stops and sequencing-defect return gate explicit. Lint/tests pass.
  - **Capability needs**: local editing/search/static tests; discoverable shared skills and documented questions/memory/coordinator checks.
  - **Model class**: sonnet-class.
  - **Rationale**: bounded adapter following settled contracts.

### Routing and validation

- [ ] T007 [Routing/docs] Integrate user-facing documentation, direct-task routing, and discovery checks.
  - **Depends**: T001, T004, T005, T006.
  - **Outcome / write scope**: affected portions of README, REQUIREMENTS, docs/index, create-epic/install-memory/initialize-documentation skills, discovery probe; no unrelated cleanup.
  - **Acceptance evidence**: EPIC still wraps observed SpecKit stages; lightweight path admits approved direct tasks to coordinator; create-epic no longer falsely blocks access; documentation initialization preserves its owner-approved EPIC exception. Update local/delegated threshold, per-task commits, class-vs-model language and shared prerequisites consistently. Probe required list adds new skills and reconciles observed stale use-railway entry; installer remains dynamic. Document static validation entry point, installation/discovery, handoff fields, and /reload reminder. Preserve prior index/coverage entries; links/lint/no-model checks pass. No paid probe/install.
  - **Capability needs**: local editing/search/shell checks.
  - **Model class**: sonnet-class.
  - **Rationale**: bounded docs/routing alignment after contracts exist.

- [ ] T008 [Contract tests] Add deterministic workflow checks wired into routine suite validation.
  - **Depends**: T004, T005, T006.
  - **Outcome / write scope**: workflow checker/tests and validation wiring; prose stays authoritative, no unused parallel manifest.
  - **Acceptance evidence**: resolve operational stage sections with required entry/input/output/class/steps/approval/resume, not diagram names; assert canonical operational order/transitions; fixed classes; gate skip/conditional paths; shared invocations; create-only tasking; plan same-turn review/fix; current and renewed EPIC approvals; source/flagged/deferral/handoff/recovery; required capabilities and fallback/stops; lightweight no-plan/no-SpecKit; common graph; three/four threshold excluding reviews; local suitability and delegation/context/rotation/resume; sequential homogeneous segments; per-task commits; one fresh final review. Valid frontmatter/references and absence of obsolete paths/state/hard-coded bindings. Run with ordinary validation, no live models. Label static limits.
  - **Capability needs**: local edits, Python/test runner/shell lint.
  - **Model class**: sonnet-class.
  - **Rationale**: mechanical explicit-contract enforcement.

- [ ] T009 [Mutations] Prove essential omissions/contradictions fail named contract checks.
  - **Depends**: T008.
  - **Outcome / write scope**: in-memory test fixtures/mutation helpers only; never mutate repository sources while testing.
  - **Acceptance evidence**: named failures for deleting operational body/class with diagram intact; reversing required operational order/transitions with bodies and diagram intact; deleting skip/conditional gate transitions; replacing invocation with unrelated mention; removing create-only/plan-review-fix/owner approvals/renewal/staleness/capability stops; reinstating mandatory direct-input plan; changing three-task threshold or removing local eligibility/context safety; permitting dependency regrouping/parallel implementation; removing per-task commits or independent review; reintroducing legacy platform/state/binding. No arbitrary failure accepted as proof; checker-specific diagnostic asserted. Routine validation runs all mutations; static limits stated.
  - **Capability needs**: local edits/Python/shell tests.
  - **Model class**: sonnet-class.
  - **Rationale**: isolated regression assurance with observable negative evidence.

- [ ] T010 [Integration/evidence] Verify full integration and complete coverage evidence/walkthroughs.
  - **Depends**: T001, T007, T009.
  - **Outcome / write scope**: evidence in coverage/task artifacts and demonstrated introduced wiring/docs/test defects only. No product work, installs, paid probes, self-authorization, or new delegation by this task; coordinator commits task changes.
  - **Acceptance evidence**: lint, validator units/task order, workflow tests/mutations, diff check with actual results; every baseline row has verified/missing evidence, no hidden unaccounted removal. Static walkthroughs cover well-specified/ambiguous requirements; <=3 class/context-fit local; four delegated and resumed run with three remaining; broad/context-heavy single task; rotation/resumption unavailable/inspected failure; commit-policy conflict; sizing/EPIC exception; stale/ambiguous approvals; no SpecKit and installed/direct input; forward dependency; missing questions/delegation/class/reviewer; >30% opus; changed artifacts on resume. Report PASS/FAIL/PARTIAL/NOT RUN/UNAVAILABLE honestly, separate static from live. Prepare full baseline→committed implementation diff and accessible historical/pre-change files for T011; clean worktree alone is not review scope. No per-task review.
  - **Capability needs**: shell/Python/search/diff inspection.
  - **Model class**: sonnet-class.
  - **Rationale**: bounded integration of observed defects and acceptance evidence.

### Independent final review

- [ ] T011 [Semantic review] Obtain one fresh independent review against source scope, history, current protections, and coverage.
  - **Depends**: T010.
  - **Outcome / write scope**: reviewer read-only; coordinator records findings/dispositions in coverage/task artifacts. Confirmed defects return for scoped fixes and separate verified commits.
  - **Acceptance evidence**: reviewer did not produce T001–T010 and is not a resumed implementation session. Inspect complete committed diff, original owner scope/design, exact historical EPIC, pre-change protections, matrix/inventory, test evidence and review contract. Classify every row/stage preserved/changed/removed-deliberate/absent with evidence; report omissions, weakened instructions, diagram-only stages, capability/approval drift, SpecKit/shared boundaries, model assignment, three-task/context/commit/no-parallel policies with severity/file:line/impact/correction. Verdict ready/ready-with-follow-up/not-ready, disposition each finding; missing independent capability blocks, never self-review disguised as independent. Semantic/static review does not prove runtime model obedience.
  - **Capability needs**: independent permitted fresh reviewer, accessible files/diff/history and durable report.
  - **Model class**: opus-class.
  - **Rationale**: owner accepted historical semantic-comparison review as judgment-heavy; selected fresh Sol reviewer.

## Coverage, exclusions, and handoff

The baseline is T001, shared primitives T002–T003, restored EPIC T004, shared coordinator T005, lightweight entry T006, routing T007, contract/mutation tests T008–T009, evidence T010, final independent review T011. Every acceptance row must identify carrying artifacts and real checks. No product features, duplicate origin-specific batching, parallel implementation batches, SpecKit replacement, sizing redesign, global state schema, runtime upgrades, or historical platform resurrection.

Mandatory implementation delegation for this candidate and per-task commits are authorized by the owner. Task-specific prohibitions on extra delegation/install/probes do not prohibit the coordinator's approved delegation/commits. Do not ask the owner to repeat settled model, class, commit, threshold, or review choices. Pause only for genuinely new material decisions, verified missing capabilities, or unresolvable blockers. Report /reload after skills change.
