# Requirements Manager implementation tasks

**Status: APPROVED FOR DIRECT IMPLEMENTATION (revision 4).**

## Provenance, review, and authorization

- Authoritative design: [requirements-manager.md](requirements-manager.md), including the latest owner-approved context-continuity batching criteria. Its preparation-revision hash remains historical evidence in git; current revisions and task definitions must be identified in the execution tracker before dispatch.
- Historical EPIC contract: `32e12feb382a6a0acb7e9d7f2e82559e3d397f2e:skills/epics-manager/SKILL.md`. Pre-change current protections: repository revision `fa41d5f3f5aeb7ddfa9963222eff2c0447533059`.
- [Archived critique-revised tasks](reviews/requirements-manager-tasks-revision-2.md), [DeepSeek critique/fix](reviews/requirements-manager-deepseek-critique.md), and [independent task review](reviews/requirements-manager-task-overall-review.md) preserve historical evidence. Their earlier thresholds, numbering, commit policies and hashes are not current instructions.
- Owner authorized critique/fix followed by implementation, then specified no per-task reviews, a commit for each task, local execution for up to three suitable tasks and mandatory delegation above three. The latest instructions added the batching-criteria task, requested the remaining batches, and approved them with “go ahead”: T001–T005 (Terra), T006 (Sol), T007–T011 (Terra), then T012 (fresh independent Sol reviewer).
- Owner model choices: `sonnet-class` implementation → `openai-codex/gpt-5.6-terra`; `opus-class` implementation → `openai-codex/gpt-6.1-sol`; fresh independent reviewer → `openai-codex/gpt-6.1-sol`. Final review is `opus-class`, already accepted. Concrete models are local execution choices, never hard-coded in global skills.
- Explicit owner-authorized direct bootstrap: current coordinator does not yet support these inputs/policies. Do not fabricate spec/plan artifacts, install/emulate SpecKit, or claim the future contract already exists. T005 changes shared batching criteria; T006 changes coordinator intake and local/delegated selection.
- Revision 4 inserts T005 and renumbers old T005–T011 to T006–T012. Preserve unchanged scope/evidence from revision 3; task checkboxes/evidence can change during execution, but substantive task changes remain owner gates.

## Independent review dispositions

| Finding | Disposition |
|---|---|
| R1 baseline after rewritten primitive | Valid/fixed: T001 drafts coverage before replacement-skill production, including inside a shared agent batch. |
| R2 stale commit policy/hash | Valid/fixed: separate verified task commits; previous hashes and critique policies are historical only. |
| R3 missing reorder mutation | Valid/fixed: T009 checks operational order; T010 mutates it with diagram/bodies intact. |
| R4 bootstrap ambiguity | Valid/fixed: explicit direct bootstrap above; no fake SpecKit artifacts. |
| R5 pending settled reviewer selection | Resolved by owner; no repeated choice required. |
| New owner batching direction | Added T005: amortize startup and reuse useful context; upstream plan/task organization must support coherent sequential batches. |

## Execution policy and safeguards

Eleven implementation tasks plus one independent review task: 10 `sonnet-class`, 2 `opus-class` (16.7%). Exclude standalone review tasks from strategy sizing; this candidate exceeds three and must delegate.

- Up to three bounded tasks may execute locally when selected model/class and context are suitable; more than three require shared delegated execution.
- Batch coherent consecutive same-class tasks to amortize agent startup and reuse relevant context. Internal dependencies/shared files are permitted when tasks run sequentially, producers are verified before consumers, and task commits remain separate. Phase/story headings alone do not force a new batch.
- Aim for 5–7 tasks when scope/context permit, not as a quota. Split for class changes, owner gates, observed context limits, incompatible scope or integration prerequisites not satisfiable within the batch. Never reorder prerequisites, mix model classes, run implementation batches in parallel, or pad with distant tasks.
- Plan/task producers prepare context-coherent consecutive work while preserving explicit dependencies, producer-before-consumer order, independent task evidence, and story acceptance boundaries.
- Session reuse requires model/class match, relevant context, runtime support and observed headroom; no forced one-session-per-class cap. Task count and cumulative token billing do not establish context capacity.
- Verify and commit each task before starting the next. No per-task reviews; one fresh independent final review of the complete committed diff. Only async background subagents may launch.
- Inspect failures before retry/relaunch. No silent model switches, pushes, installs, deployments, paid discovery probes, unrelated product work or scope expansion.
- Static prompt-contract tests and semantic walkthroughs do not prove runtime model obedience; report limitations and unavailable capabilities honestly.

## Tasks

### Coverage baseline

- [x] T001 [Coverage baseline] Draft the source-derived requirement matrix, historical behavior inventory, and capability/fallback inventory before reading or writing any replacement skill.
  - **Depends**: none.
  - **Outcome / write scope**: add `docs/plans/requirements-manager-coverage.md` and its `docs/index.md` entry. No skill/script edits.
  - **Sources**: owner request/design and handoff, historical EPIC, pre-change EPIC/coordinator/create-epic, REQUIREMENTS, best-practices guidance, scripts/tests. Record derivation ordering.
  - **Required content**: `ID | source citation | required behavior | carrying stage/rule | status | rationale | task IDs | check/test IDs | evidence status`; preserved/changed-deliberate/removed-deliberate/removed-unaccounted classifications, planned/verified/missing evidence.
  - **Historical inventory**: gate, optional brainstorm, exact decision application, reading/source contract, spec, plan spec-review/create/fix in one pass, create-only tasking, overall review, flagged-item categories/never-flag list/single-option mechanical resolution/owner dialogue/decision capture/same-session correction, deferrals, handoff, interruption recovery, done report, fixed classes. Current owner gates replace historical speculative material defaults.
  - **Capability inventory**: SpecKit discovery/stops, delegation policy, questions/fallback and stage stops, owner class/model selection, applicable memory, principles/constitution, independent reviewer. Record deliberate changes to mandatory delegation, batching boundaries and commit policy with pre-change citations.
  - **Not restored**: obsolete platform tools/paths, resolver/state schema, named agents/provider IDs. Flag unauthorized omissions rather than silently accepting them.
  - **Acceptance evidence**: every owner criterion/historical behavior maps to sourced row, implementing task and expected check; no rewritten-prompt-derived baseline; lint/diff checks pass.
  - **Capability needs**: local read/write, git history, shell/static lint.
  - **Model class**: sonnet-class.
  - **Rationale**: source-driven extraction, with material ambiguity reported rather than decided.
  - **Execution evidence**: `docs/plans/requirements-manager-coverage.md`; baseline lint, five validator units, task-order validation, and diff check passed before/after the documentation-only change; commit records the source-first checkpoint.

### Shared workflow foundation

- [x] T002 [Shared brainstorming] Extract one discoverable historical EPIC brainstorming primitive.
  - **Depends**: T001.
  - **Outcome / write scope**: `skills/epic-brainstorming/SKILL.md` plus focused adjacent deterministic tests.
  - **Acceptance evidence**: NO_BRAINSTORM_NEEDED/BRAINSTORM_NEEDED gate; skip bounded/mechanical ambiguity; maximum three agenda items/options; orchestrator owns material questions one at a time; exact approved decision application to bounded source; deferrals/handoff/resume/capability stops. Both managers must invoke the same behavior, not fork or substitute generic brainstorming. Valid frontmatter/references, focused tests/lint pass.
  - **Capability needs**: editing, Python/static lint; no live calls/config changes.
  - **Model class**: sonnet-class.
  - **Rationale**: bounded historical extraction governed by baseline.
  - **Execution evidence**: `skills/epic-brainstorming/SKILL.md` and `scripts/test_contract.py`; focused static contract tests and suite lint passed; manager integration is verified by T004/T007 and their operational checks.

- [x] T003 [Shared task generation] Extract common task semantics and centralize validator/tests.
  - **Depends**: T001, T002.
  - **Outcome / write scope**: `skills/task-generation/SKILL.md`; relocate EPIC task-order validator/tests; update observed callers and pointers, forwarding only for proven consumers. One validator implementation.
  - **Acceptance evidence**: shared outcomes/dependencies/files/evidence/capabilities/class+rationale; sonnet default and justified opus with 30% gate; documentation/integration/acceptance coverage; consecutive IDs from T001, earlier producers, contiguous stories/setup and manual implicit dependencies; project format discovery/Markdown fallback. Unit tests accept prior ranges/none and reject missing/duplicate/gapped IDs, absent/forward/self prerequisites and resumed stories. Direct adapter requires no plan; SpecKit adapter uses observed stage commands; lint/tests pass. T005 subsequently adds shared context-coherent task organization.
  - **Capability needs**: edits, Python 3/search/lint.
  - **Model class**: sonnet-class.
  - **Rationale**: localized contract/validator extraction.
  - **Execution evidence**: `skills/task-generation/` is the sole validator implementation; expanded units cover ranges/none, self and forward prerequisites, resumed stories, gaps/duplicates/missing fields; no non-historical in-repository caller required a forwarding wrapper.

- [x] T004 [EPIC workflow] Restore executable EPIC stages, current safety protections and SpecKit wrappers.
  - **Depends**: T001, T002, T003.
  - **Outcome / write scope**: `skills/epics-manager/SKILL.md` and necessary references/tests.
  - **Acceptance evidence**: operational chain `brainstorm_gate → [epic_brainstorm → epic_brainstorm_fix] → spec_create → plan_create → tasks_create → overall_review → done`; each stage has entry/input/steps/output/approval/resume and applicable class. Gate/fix/spec/tasks sonnet-class; plan opus-class; brainstorm orchestrator-owned; review observed/independent/owner-selected. Shared gate skip/conditional path; same-turn plan spec-review/create/review/fix; create-only tasks, overall review owns corrections. Preserve source/flagged/handoff/deferral/recovery inventory with no speculative material defaults; conditional clarification; approvals as checkpoints, spec approval renewed after changes; sizing/provenance, constitution/capability stops, docs/current-version approval/fresh-session handoff. No diagram-only stages/platform resurrection; lint/tests and inventory check pass.
  - **Capability needs**: edits/history/search/static tests; no simulated SpecKit.
  - **Model class**: sonnet-class.
  - **Rationale**: explicit approved stage and inventory contracts.
  - **Execution evidence**: operational `skills/epics-manager/SKILL.md` restores the approved chain, shared primitive references, stage ownership, current approvals/resume, SpecKit/capability stops, and independent review; `scripts/test_workflow_contract.py` covers the static contract.

- [x] T005 [Context-continuity batching] Update shared coordinator batching criteria and upstream plan/task organization to amortize startup and reuse useful context.
  - **Depends**: T003, T004.
  - **Outcome / write scope**: batching/brief/session criteria in `skills/coordinate-implementation/SKILL.md`; organization guidance in `skills/task-generation/SKILL.md` and EPIC `plan_create`/`tasks_create`; focused checks. No separate batching algorithm or unrelated intake change.
  - **Acceptance evidence**: batch consecutive coherent same-class work for startup amortization and context locality. Permit sequential internal dependencies/shared files with producer checks; headings, story transitions and overlapping files alone are not automatic split triggers. Preserve task order, story acceptance boundaries and separate commits. Aim for 5–7 only when scope/context permit; split for evidenced model/gate/context/incompatible-scope or unsatisfied external integration boundary, not arbitrary headings. Upstream plan/task producers arrange coherent consecutive work without class-based dependency reordering or distant-task padding. Brief states internal task sequence/shared context/integration checkpoints; runtime observes context and uses durable handoff for rotation. Only async background delegation; no parallel implementation batches. Record deliberate removal of old isolation-first criteria in baseline inventory. Focused scenarios keep related producer/consumer tasks across phase headings together and split genuine class/gate/context boundaries. Later T009–T010 regression/mutations reject gratuitous heading/file/dependency splits and unsafe regrouping.
  - **Capability needs**: local edits/search/history, static tests/lint.
  - **Model class**: sonnet-class.
  - **Rationale**: owner specified concrete batching recipe; bounded shared-policy and producer-guidance update.
  - **Execution evidence**: coordinator, shared task-generation, and EPIC producer guidance now preserve coherent consecutive same-class work and task commits while splitting only at evidenced boundaries; focused static batching/upstream contract checks pass.

### Origin-neutral execution

- [ ] T006 [Coordinator intake] Generalize origin-specific intake and local/delegated selection while preserving T005's batching contract.
  - **Depends**: T003, T004, T005.
  - **Outcome / write scope**: coordinator intake/execution instructions and coupled tests; do not undo context-continuity criteria or create another graph.
  - **Acceptance evidence**: EPIC still requires current spec/plan/both approvals/review/provenance; Requirements Manager requires approved durable source/tasks/review without fake plan/SpecKit prerequisite; other origins validate gates, ambiguous origin blocks. Three bounded tasks permit class/context-fit local, four require delegation; complete implementation count excludes standalone reviews, not origin/plan/remaining count, retained on resume unless recorded scope/safety revision. One common graph uses T005 criteria; owner selections/checks/integration/tracker/failure inspection remain. Context-aware matching reuse/rotation, no forced one-per-class, silent switch or unauthorized local fallback. Commit each task; no per-task review; one fresh final review of full committed range. Sequencing defects return to producer review. Capability/fallback checks explicit.
  - **Capability needs**: edits/search/static checks; future runtime capabilities checked when used.
  - **Model class**: opus-class.
  - **Rationale**: indivisible high-impact authorization/execution boundary.

### Lightweight delivery and verification

- [ ] T007 [Requirements Manager] Add plan-free orchestration using shared primitives/coordinator.
  - **Depends**: T002, T003, T005, T006.
  - **Outcome / write scope**: `skills/requirements-manager/SKILL.md` and focused tests.
  - **Acceptance evidence**: detailed prompt/source, project context/evidence/applicable memory; existing sizing guidance and owner route choice; durable requirement/criteria/exclusions/constraints/sources/decisions in existing artifact or task list, no intermediate spec/plan. Shared gate invokes historical brainstorm only when needed; direct tasks use shared standards/context-coherent ordering. Docs scope from requirement/changes; requirement-to-task review and explicit current approval, durable content evidence/stale detection. Handoff source/tasks/review/approval; coordinator alone selects execution. Capability stops/defect routing/lint/tests pass.
  - **Capability needs**: edits/search/tests; discoverable skills/questions/memory/coordinator checks.
  - **Model class**: sonnet-class.
  - **Rationale**: bounded adapter following approved shared contracts.

- [ ] T008 [Routing/docs] Align documentation, direct-task routing and discovery.
  - **Depends**: T001, T004, T005, T006, T007.
  - **Outcome / write scope**: affected README/REQUIREMENTS/index/create-epic/install-memory/initialize-documentation/probe portions; no unrelated cleanup.
  - **Acceptance evidence**: EPIC SpecKit wrappers and lightweight coordinator entry documented; preserve documentation-initialization EPIC exception. Align threshold/context-locality/task commits/class language/async-only/shared prerequisites. Dynamic installer unchanged; probe adds new skills/removes observed stale entries, no paid run. Document validation entry point/installation/discovery/handoff and /reload. Preserve index/coverage entries; links/lint/static discovery pass.
  - **Capability needs**: edits/search/shell checks.
  - **Model class**: sonnet-class.
  - **Rationale**: bounded routing/docs integration.

- [ ] T009 [Contract tests] Wire deterministic operational workflow checks into routine validation.
  - **Depends**: T004, T005, T006, T007.
  - **Outcome / write scope**: checker/tests and wiring; no unused parallel manifest.
  - **Acceptance evidence**: operational stage bodies/required elements/order/transitions, not diagrams; classes/shared invocations/gate branches/create-only/plan same-turn review-fix/approvals-renewal-staleness/source/flagged/deferrals/handoff/recovery; capability fallback/stops; direct no-plan/no-SpecKit; one graph/three-four threshold/local suitability/context reuse/rotation/per-task commits/one final review/async-only. Context-continuity grouping permits sequential dependencies/shared files/headings and distinguishes real split reasons; upstream producers support it without reorder. Frontmatter/references/no obsolete platform/state/hard-coded bindings. Ordinary validation runs checks; static limits explicit, no model calls.
  - **Capability needs**: edits/Python/shell lint.
  - **Model class**: sonnet-class.
  - **Rationale**: mechanical explicit-contract enforcement.

- [ ] T010 [Mutations] Prove omissions/contradictions fail named checks on in-memory copies.
  - **Depends**: T009.
  - **Outcome / write scope**: test fixtures/mutation helpers only; no repository source mutation during tests.
  - **Acceptance evidence**: named failures deleting operational body/class with diagram intact; reversing operational order/transitions; removing gate transitions/shared invocation/create-only/plan review-fix/owner approval-renewal-staleness/capability stops; reinstating mandatory direct plan; changing threshold/removing class-context suitability; reintroducing automatic heading/shared-file/internal-dependency batch splits or removing upstream coherence guidance; permitting dependency regrouping/parallel or non-background delegation; removing per-task commits/independent review; legacy reintroduction. Specific diagnostic, not arbitrary failure, required. Routine validation runs all; static limits stated.
  - **Capability needs**: edits/Python/shell tests.
  - **Model class**: sonnet-class.
  - **Rationale**: isolated negative regression assurance.

- [ ] T011 [Integration/evidence] Verify integration, complete source-derived coverage and prepare final packet.
  - **Depends**: T001, T008, T010.
  - **Outcome / write scope**: coverage/task evidence and demonstrated introduced wiring/docs/test defects only; no product work/install/paid probe/self-authorization/extra delegation; task commit authorized.
  - **Acceptance evidence**: actual lint/unit/task-order/workflow/mutation/diff outcomes; every baseline row verified/missing, no hidden removal. Static walkthroughs: specified/ambiguous requirement; <=3 suitable local; four delegated/resume three remaining; context-heavy task/rotation/resumption unavailable/inspected failure; coherent dependent shared-file tasks across headings batched versus real model/gate/context splits; commit conflict; sizing/EPIC exception; stale/ambiguous approvals; no SpecKit/installed direct input; forward dependencies; missing tools/classes/reviewer; >30% opus; edited resume. Distinguish PASS/FAIL/PARTIAL/NOT RUN/UNAVAILABLE and static/live. Export complete committed range, exact historical/pre-change files for T012; clean worktree is not review scope. No per-task reviews.
  - **Capability needs**: shell/Python/search/diff.
  - **Model class**: sonnet-class.
  - **Rationale**: bounded evidence/integration work in same delivery context.

### Independent final review

- [ ] T012 [Semantic review] Obtain one fresh independent review against source/history/protections/coverage.
  - **Depends**: T011.
  - **Outcome / write scope**: read-only reviewer; coordinator records findings/dispositions and returns scoped fixes for separate verified commits.
  - **Acceptance evidence**: reviewer did not produce T001–T011 or resume implementation. Inspect full committed diff, original scope/design/history/pre-change files/inventory/tests/review contract. Classify every row/stage preserved/changed/removed-deliberate/absent; report omissions/weakening/diagram-only stages/capability-approval drift/SpecKit-shared boundaries/classes/three-task/context/batching-locality/task-commit/async/no-parallel policies with severity/file:line/impact/correction. Verdict and dispositions; missing independent capability blocks. Static semantic review does not prove model obedience.
  - **Capability needs**: fresh independent binding, accessible files/diff/history, durable report.
  - **Model class**: opus-class.
  - **Rationale**: owner-selected judgment-heavy historical semantic comparison in fresh Sol session.

## Coverage, exclusions, and handoff

Baseline T001; shared primitives T002–T003; EPIC T004; batching criteria T005; coordinator intake T006; lightweight producer T007; routing T008; contract/mutations T009–T010; integration T011; final review T012. Map acceptance rows to actual artifacts/checks. No unrelated product work, duplicate origin-specific graph, parallel implementation, SpecKit replacement, sizing redesign, global state, runtime upgrades or obsolete platform restoration.

Only async background subagents. Model/commit/review choices and the three remaining implementation batches are approved by the owner. Execute them sequentially, then obtain one fresh independent final review. No skill implementation has begun; preparation commit `3817425a08fe7c9bdeefed7e6e3322e268bda02e` contains the preceding plan/task reconciliation, not this latest task revision. Report /reload after eventual skill changes.
