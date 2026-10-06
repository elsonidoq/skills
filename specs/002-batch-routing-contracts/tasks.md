# Tasks: Batch-Level Model/Effort Routing and Verification Contracts

**Input**: [spec.md](spec.md), [plan.md](plan.md), [research.md](research.md), [data-model.md](data-model.md), [quickstart.md](quickstart.md).
**Prerequisites**: Current source approval in [spec-approval.md](spec-approval.md), spec SHA-256 `1b4d5b90ac1e1429739e5260d0955716d125a1b4ae8430141e89b610eacd9895`; plan checkpoint `c0be379`; planning evidence checkpoint `5b0e804`. Task creation is authorized; implementation requires planner overall_review and separate current-content implementation approval.
**Tests**: Focused existing Python checks and simulated fixtures are REQUIRED by FR-011 and the plan. No live model performance or runtime-obedience claim follows from them.
**Organization**: Shared contracts precede contiguous user-story increments. No task assigns an execution model/profile: approved FR-001 supersedes the current producer's Sonnet/Opus task labels and class-share rule for this feature.

## Format and execution constraints

- Checklist lines contain stable sequential IDs, story labels where applicable, and likely owned paths. Nested **Depends**, **Outcome**, **Capabilities**, **Acceptance**, and **Context** fields supply the work-unit contract.
- References `Tnnn/Vn` identify REQUIRED verification items in existing acceptance fields. Preserve these through batch union, dispatch, return and acceptance. A check may cover multiple references, but every mapping remains explicit.
- All writers execute sequentially. Before each task, establish its baseline and owned paths; within that task add/update the smallest failing check for the changed behavior, observe failure, implement, then retain a passing check. Do not checkpoint an intentionally failing test-only increment.
- Verify and commit each independently verifiable task with explicit owned paths before the next task, then separately checkpoint its factual evidence under the existing project coordination lifecycle. Never combine implementation tasks into one commit, stage broadly, or discard unrelated changes. Read-only final review creates no empty commit.
- Every item requires concrete output or an explicit NOT VERIFIED reason. Missing required capability, approval, permission or evidence blocks affected work. Optional broader regression is not a blocker or a substitute for REQUIRED checks.
- Python 3, local Git, readable repository files and installed check scripts are sufficient for the checks below. Manual checks mean bounded source/diff/artifact inspection, not a paid call. Live/provider checks require separate owner permission and verified binding/support/tool access; none is authorized or required for these static deliverables.
- Historical `specs/001-model-family-routing/`, this feature's approved source/planning artifacts, runtime pins, generic SpecKit assets, learned guidelines, external operations, deployment and push are excluded. No new router service, memory store, schema, benchmark matrix or automatic learner.
- Empty approved coordination guidelines supply no local routing evidence. Carry canonical research's cross-harness limitations, catalog-versus-callability distinction and unknown-observed-effort rule into producer and consumer contracts.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Reuse the existing owners and install the compact qualified prior; no project scaffolding or new dependency is needed.

- [ ] T001 Establish the shared qualified seed rubric in `skills/coordinate-implementation/references/batch-routing.md` and focused assertions in `skills/coordinate-implementation/scripts/test_batching_contract.py`.
  - **Depends**: None.
  - **Outcome**: One inspectable global seed assesses residual reasoning, tool depth, verification blind spots, scope/coupling, failure cost/reversibility and applicable approved guidance. Distinguish family from effort; explain provisional Luna/medium, Luna/max, Sol/low or medium and justified Astra/Terra options, hard escalation/design gates and conditional repair without a universal ladder. Cite canonical feature research rather than fabricate callable defaults or average unlike harnesses (FR-003, FR-010).
  - **Capabilities**: Local Markdown editing, Python 3 and Git; no provider capability needed for symbolic examples.
  - **Acceptance**: REQUIRED `T001/V1`: focused rubric assertions fail before the new contract and pass afterward; retain command/output from `python3 skills/coordinate-implementation/scripts/test_batching_contract.py`. REQUIRED `T001/V2`: manual comparison with research confirms all six assessment dimensions, independent effort rationale, benchmark limitations, empty-guideline behavior and approved-guideline precedence; retain bounded section references. Verification effort is one focused script plus rubric inspection; optional broader suite only.
  - **Context**: This rubric is the single owner linked by later producers/coordinator. Do not duplicate it in each skill.

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Give every later batch a usable task-item producer; no fabricated migration of historical approvals.

- [ ] T002 Replace implementation-task class assignment with stable objective acceptance items in `skills/task-generation/SKILL.md` and `skills/task-generation/scripts/test_contract.py`.
  - **Depends**: T001.
  - **Outcome**: Tasks record outcome, explicit dependencies, files/interfaces, capabilities, shared context and task-local REQUIRED item references in existing acceptance/observable/invariant/test fields. Include pass criterion, smallest sufficient check, expected evidence, manual/permission gates and optional checks separately. Optional residual reasoning informs later assessment, not assignment. Remove mandatory implementation-task class/rationale, 30% share and same-class batching; retain both adapters, preparation authorization, ordering, stage/create-only boundaries and per-task checkpoints. Existing inadequately contracted approved tasks return to the producing review/approval gate (FR-001, FR-005).
  - **Capabilities**: Local skill/Python edits, Python 3 and Git.
  - **Acceptance**: REQUIRED `T002/V1`: a producer contract assertion fails on old class allocation and passes for stable item/evidence/gate semantics; `python3 skills/task-generation/scripts/test_contract.py` passes with retained output. REQUIRED `T002/V2`: `python3 skills/task-generation/scripts/test_check_task_order.py` passes unchanged ordering cases; manually inspect adapter, checkpoint and legacy-return wording and record references. These focused producer/order checks are sufficient; no new format/schema is introduced.
  - **Context**: Producer verification precedes planner/coordinator consumption. Keep the existing task-order script unless concrete new wording requires a narrowly causal adjustment.

**Checkpoint**: Seed and task-item producer verified; consumer stories may now proceed in order.

## Phase 3: User Story 1 — Route a coherent implementation batch (Priority: P1)

**Goal**: Preserve ordered context-coherent execution while selecting one exact supported binding and independently justified effort per invocation.
**Independent Test**: Inspect both planner origins and a simulated bounded/deep batch decision through selected dispatch arguments, including unsupported/unknown profile handling.

- [ ] T003 [US1] Adapt both planning handoffs and active downstream producer consumers in `skills/planner/SKILL.md`, `skills/planner/references/approval-and-recovery.md`, `skills/tiny-spec/SKILL.md`, `skills/planning-brainstorming/SKILL.md`, `skills/delegating-architectural-planning/SKILL.md`, `scripts/check-planner-workflow.py` and `scripts/test-planner-workflow.py`.
  - **Depends**: T002.
  - **Outcome**: TinySpec and Standard pass source constraints, canonical research, applicable guidelines and stable verification needs to task generation/coordinator, without enforcing implementation-task classes/share. Preserve direct/helper shared research ownership, depth selection, source/current-content/overall approval, documented legacy recovery and unrelated planning-stage bindings. Inspect active linked samples/templates; edit only any that actually enforce superseded implementation-task allocation, recording exact additional causal paths before writing (FR-001, FR-005).
  - **Capabilities**: Local Markdown/Python edits and Git; installed SpecKit capability remains a Standard gate, not a requirement for direct origins.
  - **Acceptance**: REQUIRED `T003/V1`: updated handoff assertion fails before implementation, then `python3 scripts/check-planner-workflow.py` and `python3 scripts/test-planner-workflow.py` pass; retain output. REQUIRED `T003/V2`: manual direct/helper and TinySpec/Standard/legacy trace identifies unchanged source and overall gates, canonical research links and producing-gate return for inadequate old tasks; record section/path evidence. Bounded handoff inspection plus existing fixtures is sufficient, not a historical-artifact rewrite.
  - **Context**: These producer consumers share approval/research context. Unrelated stage selection remains unchanged, even if it still names a class.

- [ ] T004 [US1] Wire batch assessment, selection and dispatch preflight in `skills/coordinate-implementation/SKILL.md`, linking `skills/coordinate-implementation/references/batch-routing.md`, and update `skills/coordinate-implementation/scripts/test_batching_contract.py` and `skills/coordinate-implementation/scripts/test_intake_contract.py`.
  - **Depends**: T001, T003.
  - **Outcome**: Consecutive sequential batches normally contain 2–5 related tasks when feasible, not a quota or one-agent-per-task default. Split on material profile/context/permission/dependency differences, not incidental phase/shared-file boundaries. Record ordered IDs, factors, applicable approved evidence or none, proposed versus owner-selected exact binding/effort, separate rationales and conditional repair. Verify permitted callable binding, supported effort, tools and owner gates at assignment and dispatch; registry/suffix syntax alone cannot pass. Adapt local suitability from class match to selected profile/context while preserving existing strategy/authorization gates (FR-001–FR-004).
  - **Capabilities**: Local contracts, existing Python fixtures and Git. Dispatch instructions must explicitly gate live access; simulations use symbolic permitted profiles only.
  - **Acceptance**: REQUIRED `T004/V1`: focused changed-behavior assertions fail first and both coordinator scripts pass afterward with retained output. REQUIRED `T004/V2`: bounded simulation demonstrates empty-guideline Luna/medium proposal, independently justified Luna/max retaining max, deep/weak-oracle rejection of optimistic routing, unsupported binding/effort or missing permission blocking dispatch, and unobservable actual effort remaining unknown. Retain fixture case names and expected/actual decisions; do not infer actual profile from request. REQUIRED `T004/V3`: manual decision-to-dispatch trace proves one selected profile per invocation, no silent override, preserved ordering/sequential writers and strategy gates. Focused cases plus trace are sufficient; no exhaustive profile matrix.
  - **Context**: Profile preflight and actual dispatch wiring stay together. Producer/consumer tasks may share a batch only when each producer is verified before use.

**Checkpoint**: US1 routing increment verified. Acceptance and feedback stories remain necessary for feature completion.

## Phase 4: User Story 2 — Prove each task and accept a batch cheaply (Priority: P1)

**Goal**: Dispatch the whole REQUIRED union and accept only concrete consistent evidence plus inspected focused checkpoints, without a mandatory strong per-batch reviewer.
**Independent Test**: A two-task shared-check fixture accepts complete evidence and blocks missing/contradictory/unrun/unauthorized evidence and dependent release.

- [ ] T005 [US2] Integrate batch contract dispatch and implementer return mappings in `skills/coordinate-implementation/SKILL.md` and `skills/coordinate-implementation/scripts/test_batching_contract.py`.
  - **Depends**: T002, T004.
  - **Outcome**: Brief/tracker aggregates every task REQUIRED reference with gates, expected evidence, internal producer checks, baseline/owned paths and per-task plus separate evidence checkpoints. Implementer receives the whole contract and returns actual profile or unknown, item-mapped pass/fail/not-verified reasons, concrete check outputs, files and ordered baseline/result checkpoint references. Shared output may cover multiple references without losing mappings; missing/ambiguous contracts return to producing approval rather than retrofit (FR-005, FR-006).
  - **Capabilities**: Local skill/Python edits, Git and fixture execution.
  - **Acceptance**: REQUIRED `T005/V1`: focused union/return assertion fails before implementation, then the batching script passes. Two-task fixture demonstrates union completeness, shared-check mapping to both stable references and explicit not-verified reasons; retain output/case names. REQUIRED `T005/V2`: inspect sample brief/return against the producer contract and per-task commit convention; all REQUIRED references and both task checkpoints remain identifiable. Bounded fixture and artifact trace suffice; confidence-only reports cannot pass.
  - **Context**: Same coordinator seam as T004/T006; reusable selection context does not authorize merged task commits.

- [ ] T006 [US2] Enforce cheap evidence acceptance and successful Luna scenario fixtures in `skills/coordinate-implementation/SKILL.md`, `skills/coordinate-implementation/scripts/test_batching_contract.py` and `skills/coordinate-implementation/scripts/test_intake_contract.py`.
  - **Depends**: T005.
  - **Outcome**: Coordinator inspects each task checkpoint/diff and validates required item completeness, consistent concrete outputs, scope and honored manual gates before acceptance/dependent release. Passing contracts need no mandatory strong-model per-batch reviewer; final fresh independent review remains required (FR-007, FR-011; SC-001, SC-002).
  - **Capabilities**: Local editing/Python/Git; simulated commits/evidence, not a live agent run.
  - **Acceptance**: REQUIRED `T006/V1`: rejection assertions fail first, then both coordinator scripts pass. Bounded two-task fixture accepts shared evidence but blocks removed, failed, contradictory or unrun REQUIRED evidence, unauthorized scope and unmet manual gates; retain dispositions and evidence mappings. REQUIRED `T006/V2`: named simulations demonstrate Luna/medium accepted without a strong per-batch reviewer and Luna/max accepted with selected/reported max preserved; both have 100% REQUIRED evidence, inspected task checkpoints and exact symbolic bindings. REQUIRED `T006/V3`: manual inspection confirms dependent release is blocked on invalid evidence and final independent review is unchanged. Focused positive/negative fixtures suffice; label them simulated, not performance or runtime-obedience proof.
  - **Context**: Acceptance closes US2 only after dispatch/return semantics are verified. Optional checks cannot compensate for missing required evidence.

**Checkpoint**: US2 complete; passing simulated contracts can be accepted cheaply while final review remains mandatory.

## Phase 5: User Story 3 — Diagnose, escalate and learn without false attribution (Priority: P2)

**Goal**: Preserve valid work and attempt history, repair through authorized profiles, and persist qualified feedback without automatic guidance mutation.
**Independent Test**: Simulate Luna/max capability repair to Sol/medium, environment-blocked Luna/medium and approved-guideline Sol/medium override of seed Luna/max.

- [ ] T007 [US3] Integrate diagnosis-first targeted repair in `skills/coordinate-implementation/SKILL.md` and `skills/coordinate-implementation/scripts/test_batching_contract.py`.
  - **Depends**: T006.
  - **Outcome**: Inspect failed child run, invocation, partial commits and evidence before retry. Diagnose cause, preserve valid work/prior attempts, identify affected dependencies and invalidated items. A repair may change model, effort or both only after usable binding/support/owner gates; brief includes original assessment/profile, passed/failed items, current state and complete contract. Rerun invalidated checks and reuse only confirmed-valid evidence; unknown cause stops blind restart (FR-008, FR-011).
  - **Capabilities**: Local Python/Markdown/Git and simulated failure/repair evidence; no live retry authorized.
  - **Acceptance**: REQUIRED `T007/V1`: repair assertions fail before implementation, then batching script passes. Named Luna/max capability-failure → authorized Sol/medium repair fixture preserves original attempt/valid work, supports diagnosis, supplies full contract and reruns all invalidated items before acceptance. REQUIRED `T007/V2`: bounded unknown-cause and unavailable/unauthorized-repair cases stop without a fresh blind dispatch; record fixture outputs and manual cross-check of owner gates/no fixed ladder. Small repair fixtures suffice; repaired success alone cannot prove model-only attribution.
  - **Context**: Diagnose failure from artifacts, not a generic abort. Keep full contract available to repair even when some evidence remains reusable.

- [ ] T008 [US3] Add qualified attempt feedback compatibility and remaining scenario fixtures in `skills/memory-handling/references/project-coordination.md`, `skills/coordinate-implementation/SKILL.md` and `skills/coordinate-implementation/scripts/test_batching_contract.py`.
  - **Depends**: T007.
  - **Outcome**: Existing indexed run/task evidence records exact selected/observed profile or unknown, factors, contract strength, first/final outcome, diagnosis, escalation and check/checkpoint references for accepted, partial, escalated and blocked attempts. Preserve attribution values `model_capability`, `planning_or_spec_gap`, `verification_contract_gap`, `batching_error`, `environment_or_tooling`, `external_dependency`, `unknown`. Non-model causes never count as capability failure; weak/invalidated successes are not strong positive guidance. Only existing selective reflection/exact owner approval/drift checks may update guidelines; no new store/schema or global learning (FR-009–FR-011; SC-003).
  - **Capabilities**: Local contract/Python edits and Git. Fixtures do not edit real learned guidelines or perform paid operations.
  - **Acceptance**: REQUIRED `T008/V1`: feedback assertions fail first, then batching script passes. Named environment-blocked Luna/medium fixture keeps required check unverified and attributes `environment_or_tooling` without capability penalty. Named applicable approved-guideline fixture selects Sol/medium over seed Luna/max, cites applicability/approval and retains owner/source gates. REQUIRED `T008/V2`: manual comparison confirms existing project-root resolution, mandatory initialization/persistence, selective/index-first retrieval, exact candidate approval and drift checks remain; attempt history and unknown actual profile are not overwritten. REQUIRED `T008/V3`: `python3 scripts/check-task-commit-contract.py` and `python3 scripts/test-task-commit-contract.py` pass after cross-contract wording changes; narrowly update superseded assertions only if needed, preserving checkpoint behavior. Existing fixtures/contract inspection suffice; no actual guideline mutation is part of this task.
  - **Context**: Memory is the existing evidence owner, not a second router. Approved local evidence may override the seed but never permissions or source authority.

**Checkpoint**: All five required scenarios have bounded simulated demonstrations and qualified feedback.

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Synchronize active guidance and validate the integrated committed range without changing source/plan or runtime pins.

- [ ] T009 Update runtime and workflow guidance in `REQUIREMENTS.md`, `README.md` and `docs/pi-settings-sample.md` to match verified batch behavior.
  - **Depends**: T008.
  - **Outcome**: Active implementation requirements/examples describe batch-selected exact binding plus effort and task-item contracts, not mandatory per-task classes/share or an unconditional setting override. Preserve unrelated planning/reviewer selections, existing version pins, empty-guideline portability, per-task/evidence checkpoints and final independent review. Link the shared rubric and explain fixtures versus separately gated live support/callability checks (FR-001, FR-004, FR-010; SC-004).
  - **Capabilities**: Local docs/Markdown editing and Git; no runtime configuration deployment.
  - **Acceptance**: REQUIRED `T009/V1`: manual docs-to-implemented-source comparison records exact section references for task producer, selected dispatch, acceptance, repair and feedback; no active example silently replaces the selected implementation profile. REQUIRED `T009/V2`: inspect diff to confirm pins and unrelated stage bindings unchanged; `git diff --check` passes. REQUIRED `T009/V3`: run `python3 scripts/check-planner-workflow.py` and `python3 scripts/check-task-commit-contract.py` to detect docs/contract preservation conflicts; retain output. Verification is bounded lockstep comparison plus existing checkers, not new documentation infrastructure.
  - **Context**: Update only active examples that feed the changed seam; do not rewrite historical specs to make text searches pass. After global skill/configuration changes, tell the owner to run `/reload` in Pi.

- [ ] T010 Validate integrated contracts and obtain final independent review using `skills/coordinate-implementation/SKILL.md`, `skills/task-generation/SKILL.md` and the existing project coordination run/task evidence paths.
  - **Depends**: T009.
  - **Outcome**: All REQUIRED items and five scenarios are mapped to actual retained evidence/checkpoints; integrated workflow passes focused checks and a fresh final independent review of the complete implementation range. Retain the review/evidence in the resolved project-local coordination run, not a new store. A read-only check creates no empty implementation commit; retained evidence gets its own explicit-path evidence checkpoint. Defects block closeout and require separately authorized verified correction tasks, not silent source/task edits.
  - **Capabilities**: Python 3, Git, local artifact inspection and an independently authorized fresh reviewer through the existing workflow. Reviewer unavailable means NOT VERIFIED and blocks final acceptance; no live model benchmark is required.
  - **Acceptance**: REQUIRED `T010/V1`: run all eight Python commands in quickstart's focused-check section and `git diff --check`; retain outputs and task/item mappings, confirming the five named simulations plus shared-check negative and unsupported/unknown handling pass. REQUIRED `T010/V2`: manual end-to-end trace records source → producer acceptance refs → batch union → selected dispatch arguments → return → each checkpoint/diff audit → disposition → indexed feedback → separate guideline approval. Inspect both planning origins, legacy recovery, empty guidelines, exact effort retention and no silent settings override. REQUIRED `T010/V3`: fresh final independent review of the complete committed range finds no unresolved blocking defects; retain reviewer identity/capability, range and findings. Focused suite plus one complete trace/review is necessary for cross-owner integration, not a broad benchmark. Optional broader lint/regression remains separate; live results remain NOT RUN unless separately authorized.
  - **Context**: Final independent review is not a strong per-batch review. Audit every implementation/evidence checkpoint and preserve residual limitations in closeout.

## Dependencies & Execution Order

- Setup T001 → foundational T002 → US1 T003–T004 → US2 T005–T006 → US3 T007–T008 → polish/integration T009–T010.
- Explicit dependencies above are authoritative. US2 consumes US1 selection/dispatch; US3 consumes US2 evidence acceptance. Each story's test is independently observable against its completed prerequisites, not independent of its producers.
- Shared-context segments that a coordinator may consider: T001–T002 (rubric/producer), T003–T006 (handoff, dispatch and acceptance), T007–T009 (repair, feedback and lockstep guidance). These are suggestions, not invocation assignments or a quota; retain individual commits and verification boundaries. T010 is the final integration/review gate.

## Parallel Opportunities and Examples

No implementation task is marked [P]: writers are sequential and shared coordinator files/producer contracts create real dependencies.

- **US1 example**: inspect planner handoffs while reading the verified rubric, then execute T003 before T004; do not launch concurrent writers.
- **US2 example**: shared-check output may satisfy two item references after T005, but T006 acceptance is sequential; duplicate check execution is unnecessary, not a reason to parallelize task commits.
- **US3 example**: independent read-only evidence inspection may inform diagnosis; T007 repair semantics precede T008 feedback and no parallel repair/guideline writer is permitted.

## Implementation Strategy

1. Complete setup/foundation and US1 for the routing MVP; stop and validate its independent criteria. Do not claim complete feature acceptance before US2/US3.
2. Add US2 union/return/acceptance, retaining cheap successful Luna paths and final review.
3. Add US3 diagnosis/feedback and all five named simulated scenarios, preserving approvals and evidence history.
4. Synchronize docs, run focused integration checks, obtain final independent review and only then close out under the existing approval workflow. No deploy/demo, push or paid comparison is part of this task list.

## Creation-stage validation and review boundary

This artifact is created with the installed `.pi/prompts/speckit.tasks.md` stage, `.specify/scripts/bash/setup-tasks.sh --json` and resolved `.specify/templates/tasks-template.md` structure. No extension hook file is present. Creation-stage validation is limited to checklist format, stable IDs/verification references, explicit earlier prerequisites, story continuity and whitespace. It does not claim producer self-review, implementation execution or approval. Planner overall_review owns completeness, decomposition and cross-artifact defect review before implementation authorization.
