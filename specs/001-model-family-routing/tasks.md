# Tasks: Model Family and Reasoning-Effort Routing

**Input**: [renewed specification](spec.md), [plan](plan.md), [benchmark research](research.md), [data model](data-model.md), [validation guide](quickstart.md), [current-content approval](spec-approval.md). This is **task preparation only**; implementation, model dispatch, runtime model-scope changes, guideline mutation and rollback are not authorized by this file. The user authorized a bounded format exception for this list: record family/effort evidence and owner selection, **not** the legacy `sonnet-class`/`opus-class` field or percentage cap.

**Routing status:** the task/reviewer table below is a **proposal, not an owner-selected assignment or execution authorization**. Present the complete table with task scope at the **single final implementation-approval gate**; the owner can ask for changes before answering. One affirmative current-content decision approves the task scope and the listed family/binding/effort/reviewer selections, recorded distinctly. No routine second approval after preflight; recheck eligibility and runtime before each dispatch, and stop for renewed owner choice on drift, unavailability or any proposed substitution. Existing Luna entries are not currently permitted by the observed subagent scope; benchmark/catalog presence does not change that. No implementation model selection is inherited from the Sol specification/planning/task-preparation bindings.

**Checks:** REQUIRED checks named below; broader hardening is optional unless a new changed-seam risk or governing policy requires it. A static PASS cannot prove real model adherence, provider effort support or benchmark applicability to this project's tasks. Do not fetch paid benchmarks, run live providers, push, or change user settings without separate authority. Commit every verified task separately; focused evidence-only checkpoint follows where mandated. Factual failure attempts use the owner-approved proposed new contract only **after its implementation is itself reviewed/approved**, never as authority to roll back work now.

## Proposed assignment snapshot for the single final approval

**Shared candidate for T001–T012:** Astra / `openai-codex/gpt-6-astra` / **medium**. [Inspected Terminal-Bench 4.0 row](research.md) reports GPT-6 Astra at **medium**, 54.24% of 330 terminal-agent tasks (Sep 3, 2026); it is a task-relevant but imperfect proxy for code/documentation/test changes made by a terminal agent, **not** a prediction for these tasks or a family ranking. Provider [model documentation](https://developers.openai.com/api/docs/models/gpt-6-astra) reports medium support; permitted subagent model scope includes this exact binding, and a read-only independent review in this planning session actually ran as Astra/medium. Writer-role tools are declared by the installed worker, but mutation behavior was **not** live-smoked: coordinator must recheck tools, binding, requested/observed effort and capacity before dispatch. Terra 5.6/max has a matching benchmark row and permitted scope but has not been shown callable here; GPT-6.1 Sol has no inspected exact-effort task-relevant result, and Luna is out of current subagent scope. Do not silently replace this proposal with any of them. Using Astra/medium throughout can be costly and leaves no automatic family escalation from an Astra initial attempt; this is a visible trade-off for owner review, not an inference that every task needs Astra.

| Task | Proposed family / binding / effort | Task-specific rationale |
| --- | --- | --- |
| T001 | Astra / `openai-codex/gpt-6-astra` / medium | Source-cited routing inventory and baseline checks across active contracts. |
| T002 | Astra / `openai-codex/gpt-6-astra` / medium | Cross-contract eligibility rules and negative fixtures must stay consistent. |
| T003 | Astra / `openai-codex/gpt-6-astra` / medium | Planning-stage changes must preserve approvals and deliberate freeze clauses. |
| T004 | Astra / `openai-codex/gpt-6-astra` / medium | Task adapter and story validator changes need cross-format regression. |
| T005 | Astra / `openai-codex/gpt-6-astra` / medium | Coordinator dispatch safety and batch ordering are high-impact. |
| T006 | Astra / `openai-codex/gpt-6-astra` / medium | Documentation must match evidence-gated implemented behavior. |
| T007 | Astra / `openai-codex/gpt-6-astra` / medium | Luna-readiness oracle and handoff fixtures must reject weak briefs. |
| T008 | Astra / `openai-codex/gpt-6-astra` / medium | Failed-commit/inverse contract requires careful Git and evidence ordering. |
| T009 | Astra / `openai-codex/gpt-6-astra` / medium | Temporary-Git recovery tests must detect unsafe inverses. |
| T010 | Astra / `openai-codex/gpt-6-astra` / medium | Indexed attempt evidence must not become unapproved project guidance. |
| T011 | Astra / `openai-codex/gpt-6-astra` / medium | Cross-suite examples and checkers need accurate final reconciliation. |
| T012 | Astra / `openai-codex/gpt-6-astra` / medium | Integration evidence must be truthful and independently reviewed. |

**Independent final implementation reviewer proposal:** fresh-context `reviewer` with Astra / `openai-codex/gpt-6-astra` / **medium**, separately scoped to review rather than writing; the same benchmark/capability evidence above applies and this role has already run read-only in planning. Owner approval of this proposal must be recorded separately from task authorization even when obtained in the same final answer. An approved assignment is frozen by task ID/reviewer role and artifact revision; changes or missing evidence require a new decision before affected execution. Until affirmative approval, every row below remains `unselected` in its execution contract.

## Phase 1: Setup — baseline and evidence boundary

**Goal:** Identify every active routing consumer and checker before changing shared contracts. **Independent test:** inventory cites each named owner/checker and distinguishes historical artifacts.

- [ ] T001 Map active model-class routing and approval/failure seams in `REQUIREMENTS.md`, `skills/planner/SKILL.md`, `skills/task-generation/SKILL.md`, `skills/coordinate-implementation/SKILL.md`, `skills/memory-handling/references/project-coordination.md`, helpers, fixtures and `scripts/check-planner-workflow.py`.
  - **Depends**: none. **Outcome:** bounded, source-cited change/negative-test inventory retained in the feature's existing tracker/evidence convention, not a new global model policy; record current coordinator SHA freeze and required approval/commit boundaries before edits.
  - **Acceptance:** compare `rg` inventory against planned seams and baseline relevant Python checker/tests and lint; report actual PASS/FAIL/NOT RUN. Distinguish active normative text from historical reviews and untracked unrelated files; verify Git/index ownership. **Capabilities:** Python 3, Git, read-only project instructions. **Routing:** unselected; benchmark and owner gate above.

## Phase 2: Foundation — one shared eligibility and evidence rule

**Goal:** All later producers and consumers share a single, source-backed version/effort gate. **Independent test:** in-memory negative mutations block missing/estimated-only/other-version benchmark rows and unsupported efforts.

- [ ] T002 Define the portable family/effort, benchmark-eligibility and owner-selection contract in `REQUIREMENTS.md` and `skills/memory-handling/references/project-coordination.md`, with focused `skills/memory-handling/scripts/test_coordination_contract.py` coverage.
  - **Depends**: T001. **Outcome:** four initial family names, separately verified exact binding/effort, task-relevant exact-version/effort measured benchmark and source provenance; retained benchmark owner/discovery distinct from project outcomes/guidelines. No provider IDs or this project's observations become universal skill policy.
  - **Acceptance:** missing result, wrong version/effort/workload, Estimated aggregate alone, catalog-only availability and unsupported runtime effort all block routing; available source spans and date remain discoverable after guideline supersession; owner selection and exact-content memory approval are distinct. Focused tests fail on removed guard then pass; review installed docs links. **Capabilities:** Python 3, relevant memory references, benchmark source inspection (reuse verified research; refresh only gaps). **Routing:** unselected; benchmark and owner gate above.

## Phase 3: User Story 1 — select an available family and effort (P1) 🎯 MVP

**Goal:** Planning/task/review stages can record eligible independent family and effort without old class tags. **Independent test:** valid selection flows through both TinySpec and Standard, while an ineligible effort or stale approval blocks.

- [ ] T003 [US1] Migrate stage selection and Standard helper constraints in `skills/planner/SKILL.md`, `skills/planning-brainstorming/SKILL.md`, `skills/delegating-architectural-planning/SKILL.md`, and their focused checkers in `scripts/check-planner-workflow.py` and `scripts/test-planner-workflow.py`.
  - **Depends**: T002. **Outcome:** no fixed old-stage class tag; each stage checks eligible family/effort, usable selected binding and approval scope; same-session spec review/one plan/review, owner questions, TinySpec depth choice and earliest-invalid-stage recovery preserved. Before final approval, planner presents every proposed task/reviewer binding and effort with task-specific evidence and accepts owner changes; one current-content answer approves both scope and listed selections. Deliberately update the coordinator SHA freeze only after comparing unchanged safety clauses.
  - **Acceptance:** static/mutation checker rejects missing stage instruction, missing benchmark/capability gate, missing or changed pre-approval assignment preview, extra routine post-approval selection question, silent model switch, stale spec approval or plan double-run; pre-existing planner regression suite passes. Do not invoke unavailable SpecKit substitutes. **Capabilities:** Python 3 and observed SpecKit contract fixtures. **Routing:** unselected; benchmark and owner gate above.

- [ ] T004 [US1] Replace implementation-task class fields, old share cap and adapter assumptions in `skills/task-generation/SKILL.md` and `skills/task-generation/scripts/check-task-order.py` (only if required by actual format), with focused direct/Standard fixture updates under `scripts/fixtures/planner/`.
  - **Depends**: T003. **Outcome:** independently verifiable tasks include evidence needs, explicit prerequisites, acceptance oracle and a complete proposed task/reviewer family/binding/effort table with its benchmark/capability evidence before the single final approval; no provider IDs embedded in *portable skill policy*, inferred effort or retroactive legacy mapping. Preserve execution numbering, story continuity, documentation coverage and source approvals.
  - **Acceptance:** validator still rejects missing/forward dependencies and story disorder; both adapters honor benchmark gate without imposing Standard prerequisites on TinySpec. Focused tests reject old class/share policy as current authority and accept safe pending selections. **Capabilities:** Python 3, detected task-stage instructions. **Routing:** unselected; benchmark and owner gate above.

- [ ] T005 [US1] Replace class-based local/batch/preflight routing in `skills/coordinate-implementation/SKILL.md` and `skills/coordinate-implementation/scripts/test_batching_contract.py` while keeping its execution safeguards.
  - **Depends**: T004. **Outcome:** graph-ordered sequential batches group only the *approved* compatible binding/effort/context, retain <=3 local task limit and mandatory delegation above it, owner selection, tool/capacity verification and independent reviewer. Immediately before dispatch, recheck current task, evidence and runtime against the approved assignment; stop for renewed owner decision on drift, never silently replace a selection. Escalation dispatch cannot skip an unbenchmarked/unavailable next family.
  - **Acceptance:** focused tests reject unverified effort, estimated-only or irrelevant benchmark, missing/changed approval snapshot, silent family change, routine second assignment-approval question, class-based reordering, missing reviewer, or weakened local/delegated threshold; observed context rather than billed tokens controls reuse. **Capabilities:** Python 3, coordinator scripts, actual async delegation capability only at live execution preflight. **Routing:** unselected; benchmark and owner gate above.

## Phase 4: User Story 2 — auditable initial benchmark guidance (P1)

**Goal:** Future agents can find initial measured evidence without mistaking it for approved project learning. **Independent test:** locate original source/limitations after a simulated guideline edit; unmeasured effort remains ineligible.

- [ ] T006 [US2] Align `README.md`, `docs/index.md`, `docs/pi-settings-sample.md`, `docs/best_practices_spec_driven_development.md` and `REQUIREMENTS.md` to the implemented T002–T005 behavior; preserve [feature-local benchmark record](research.md) with measured/estimated/secondary distinctions and index link.
  - **Depends**: T005. **Outcome:** discoverable source-backed initial *candidate* guidance, not a universal provider binding or a mutation of `memory/coordination/GUIDELINES.md`. State when to revisit source version/effort/harness and how owner approval is obtained for project-local synthesis.
  - **Acceptance:** documentation comparisons against actual skill/tests pass; invalid links, missing benchmark support or obsolete normative tags are detected; no uncontrolled source-row redistribution or fabricated complete matrix. **Capabilities:** source access and docs write authority; external refresh only for a proven gap. **Routing:** unselected; benchmark and owner gate above.

## Phase 5: User Story 3 — deterministic Luna work (P1)

**Goal:** Eligible Luna tasks are unusually clear and checked before dispatch. **Independent test:** deliberately incomplete briefs fail, complete bounded briefs pass a real wrong-result-detecting check.

- [ ] T007 [US3] Add Luna-readiness and escalation-brief gates in `skills/task-generation/SKILL.md`, `skills/coordinate-implementation/SKILL.md`, and relevant task/coordinator fixture tests.
  - **Depends**: T006. **Outcome:** objective, allowed/prohibited files/operations, prerequisites, ordered steps, expected observable outputs, capabilities and executable REQUIRED acceptance check travel unchanged from source/task through coordinator to delegate. Ambiguity returns to producing review gate, never silently substitutes another family.
  - **Acceptance:** negative fixture deletes each material brief element and observes named failure; one complete fixture has a check that fails on a wrong outcome and passes on the required one. Shared-file batching retains per-task acceptance and commits. **Capabilities:** Python 3, permitted mutation tool at actual dispatch. **Routing:** unselected; Luna is a candidate only with qualifying benchmark + supported effort + permitted binding + owner choice.

## Phase 6: User Story 4 — recover failed tasks before bounded retry (P1)

**Goal:** Record, safely checkpoint and ordinarily invert failed task-owned changes before a bounded next attempt. **Independent test:** temporary Git history shows a NOT VERIFIED failure commit then distinct inverse while unrelated changes remain intact.

- [ ] T008 [US4] Implement the owner-approved failed-attempt exception in `skills/memory-handling/references/task-commit-contract.md` and corresponding coordinator instructions in `skills/coordinate-implementation/SKILL.md`, with source/approval boundaries explicit.
  - **Depends**: T007. **Outcome:** every failed actual task execution is inspected, including final Sol/exhausted attempts; factual failure/inverse scope and authorization evidence checkpoint precedes mutation; safe wholly task-owned changes, even with failed checks, get a clearly failed-attempt commit if not already committed. Its actual SHA and failed-check status are then recorded **and checkpointed before** a separate ordinary history-preserving inverse. A previously committed task is inverted only if its commit remains wholly task-owned and no dependents consumed it. Empty, mixed, unsafe or sensitive changes stop; never reset history.
  - **Acceptance:** contract names Luna→Terra→Sol, Terra→Sol, Sol stop, <=3 total attempts and no Astra fourth attempt; owner policy preauthorizes only proven-safe pairs, not uncontrolled rollback. A failed intermediate SHA/status evidence checkpoint prevents inverse. Exhausted budget or missing next-family capability/benchmark prevents *dispatch*, not factual failure recording or safe task-owned recovery. An unknown invocation or environmental failure blocks blind escalation. Existing verified-success per-task/evidence commits remain intact. **Capabilities:** Git, existing indexed project memory, question/delegation at runtime. **Routing:** unselected; benchmark and owner gate above.

- [ ] T009 [US4] Add isolated temporary-Git and mutation scenarios in `scripts/test-task-commit-contract.py` and `skills/coordinate-implementation/scripts/test_intake_contract.py` (or the current canonical nearby test owner identified by T001).
  - **Depends**: T008. **Outcome:** executable protocol oracle rather than a string-only promise; no new engine just for tests.
  - **Acceptance:** demonstrate evidence checkpoint before mutation, failed-task SHA/failed-check-status evidence checkpoint **between** failure commit and inverse, two distinct Git SHAs, failure labelled NOT VERIFIED, restored baseline and evidence after inverse; an intermediate evidence-checkpoint failure blocks inverse. A final Sol/exhausted or missing-next-family case still records the failure and safely commits/inverts owned changes, then stops without dispatch. Reject no-change, mixed ownership, hook fail, dependent consume, changed HEAD, unknown cause, unsupported next effort/benchmark and fourth attempt without leaking unrelated staged/unstaged paths. Run existing commit-coordination fixtures and `git diff --check`; tests label simulation, not real-agent compliance. **Capabilities:** Python 3, temporary Git repositories, hook-safe commit identity. **Routing:** unselected; benchmark and owner gate above.

## Phase 7: User Story 5 — learn without silent guideline mutation (P2)

**Goal:** Keep factual attempt outcomes and source-backed provisional guidance discoverable without promoting either into unapproved policy. **Independent test:** rejection leaves guideline bytes unchanged while indexed failure records and original benchmark citations persist.

- [ ] T010 [US5] Update `skills/memory-handling/references/project-coordination.md` and `skills/memory-handling/scripts/test_coordination_contract.py` for per-attempt binding/effort/benchmark citation, failed-check commit/inverse evidence and conservative reflection.
  - **Depends**: T009. **Outcome:** separate factual task/run records, compact index, independent source-backed initial guidance owner and owner-reviewed candidate guideline diff; no record loss on rejection or retry, no permanent family rule after one failure.
  - **Acceptance:** fixture covers two failed attempts, recovery, a later manual finding, index refresh, selective retrieval, exact-content approval/rejection/concurrent drift and retained baseline after supersession. Existing mandatory initialization and gotcha-memory gates remain unchanged. **Capabilities:** project-local evidence store, Python 3, question capability for actual guideline mutation. **Routing:** unselected; benchmark and owner gate above.

## Final Phase: Integration and truthful documentation

- [ ] T011 Reconcile active suite examples and support checks in `skills/initialize-coherence/scripts/fixtures/source-contract.json`, `skills/planning-brainstorming/scripts/test_contract.py`, `skills/writing-skills/SKILL.md`, and all additional active consumers identified in T001; adjust only impacted assertions.
  - **Depends**: T010. **Outcome:** no active old class policy or quota survives in normative skills, install/setup guidance or contract oracles; historical records remain unchanged. Docs match implemented reality, not planned behavior.
  - **Acceptance:** focused `rg` inventory with reviewed active/historical classification; deliberate planner/coordinator freeze updates preserve non-routing clauses; both origin paths and legacy repair checks pass. **Capabilities:** Python 3, focused test scripts, docs ownership. **Routing:** unselected; benchmark and owner gate above.

- [ ] T012 Run integrated acceptance for `spec.md` FR-001–FR-027 and SC-001–SC-007 against current code/docs in `scripts/check-planner-workflow.py`, `scripts/test-planner-workflow.py`, coordinator/memory/task scripts and `quickstart.md`; record truthful checks in this feature's existing approval/review/coverage conventions.
  - **Depends**: T011. **Outcome:** traceable affected-seam evidence and corrected defects as separately approved task scope when needed, then fresh independent review named in the single final approval before feature acceptance. No self-certification.
  - **Acceptance:** affected unit/fixture/static suites and `bash scripts/check-skills-lint.sh` PASS, `git diff --check` PASS, source-to-tasks/docs and benchmark citations manually inspected; label real model/effort/SpecKit compliance and provider behavior NOT RUN unless separately authorized and observed. Preserve task commits and unrelated `.env`/untracked work. **Capabilities:** Python 3, Git, independent reviewer, explicit permission for live/paid operations. **Routing:** unselected; benchmark and owner gate above.

## Dependencies & Execution Order

```text
T001 -> T002 -> T003 -> T004 -> T005 -> T006 -> T007 -> T008 -> T009 -> T010 -> T011 -> T012
```

The serial graph is intentional: T002 defines eligibility before stage/adapters/coordinator consume it; T005 verifies dispatch before T006 describes it; Luna brief T007 precedes recovery T008, executable recovery fixture T009 precedes evidence integration T010, and final assurances T011–T012 follow actual behavior. Internal producer/consumer work and shared files can stay in a coherent **sequential** batch with per-task checks/commits; neither story headings nor shared files authorize parallel implementation, dependency reordering or padding. There are **no [P] task markers** or parallel implementation opportunities in this reviewed serial graph. Read-only independent benchmark refresh and final review are separate approved capabilities and never concurrent writers on the same workspace.

**User-story completion order:** US1 T003–T005 after foundation T001–T002; US2 T006 after US1 behavior; US3 T007 after US2 task/reference handoff; US4 T008–T009 after Luna readiness; US5 T010 after recovered attempt evidence; integration T011–T012 after all. Each story has an independent local acceptance oracle listed above, though final feature acceptance needs integration.

**MVP:** T001–T005 prove benchmark-gated family/effort selection through planner/task/coordinator without retry. This is a validation slice, not permission to deploy or stop early when the owner approved the full task scope. Subsequent phases add durable benchmark documentation, Luna clarity, safe recovery, learning and whole-suite assurance. No automatic stop, parallel team wave or deployment is implied.

**Task-format validation:** twelve consecutive `- [ ] T###` entries with exact file paths, source-linked outcomes, earlier prerequisites, REQUIRED acceptance, capability needs and pending owner/benchmark routing; story labels only in story phases. No old class field is active. Producing SpecKit stage is create-only; defects and material questions are handled by planner `overall_review` before final owner approval.
