# Feature Specification: Model Family and Reasoning Effort Routing

**Feature Branch**: `main` (no branch hook registered; feature directory is independent)

**Created**: 2026-10-06

**Status**: Draft — owner specification approval pending; recovery decisions settled below

**Input**: User description: replace suite-wide planning and coordination model classes with independently selected model family and reasoning effort; use auditable provisional benchmark guidance, project-local experience, explicit Luna task contracts, and bounded, safely recovered retries. Standard specification creation only is authorized now.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Choose an Available Family and Effort (Priority: P1)

As the project owner, I can choose a model family and a separately justified reasoning effort for a planning stage, implementation task, or independent review, without old class tags constraining that choice or guessed runtime options being dispatched.

**Why this priority**: All downstream routing depends on a usable, explicitly authorized choice rather than a fixed class-to-provider mapping.

**Independent Test**: Present supported and unsupported family/effort combinations in a bounded workflow exercise; inspect the offered choices, recorded selection, and stop outcome without executing implementation work.

**Acceptance Scenarios**:

1. **Given** verified available bindings for Luna, Terra, Sol, and Astra with different supported efforts, **When** an owner selects a family, **Then** only that binding's verified efforts are selectable, and the selected family, concrete binding, effort, justification, and authorization are recorded separately.
2. **Given** a configured family name but no verified usable binding or supported-effort evidence, **When** a stage requires that choice, **Then** it reports the exact capability gap and stops rather than inferring provider, version, effort, or a replacement model.
3. **Given** the Standard route and an owner-selected usable Sol binding for specification creation, **When** that stage is prepared, **Then** no fixed specification-class assignment overrides the selection; specification approval still precedes planning.
4. **Given** approved tasks with routing selections, **When** coordination groups sequential work or considers local execution, **Then** it preserves task dependencies, each task's family/effort contract, observed context limits, and authorization; it does not silently switch models to simplify execution.

---

### User Story 2 - Obtain Auditable Initial Routing Guidance (Priority: P1)

As a planner, I can use credible, task-relevant benchmark findings as INITIAL provisional guidance, understand their limits, and find the original guidance again after project experience changes current guidelines.

**Why this priority**: Initial decisions must not masquerade as learned project evidence or rely on unsupported recollection about model capabilities.

**Independent Test**: Review a sample routing recommendation against its durable research record, then change the current project guideline and verify that a future agent can still locate the original recommendation, sources, applicability, and limitations.

**Acceptance Scenarios**:

1. **Given** consequential routing plan or task decisions are pending, **When** benchmark evidence is absent, insufficient, stale for the selected binding, or conflicting, **Then** targeted planning-stage research is a blocking dependency for those decisions; missing permitted research capability or write authority is reported, not replaced by invented results.
2. **Given** inspected current coding/tool-use or other task-relevant sources, **When** initial routing guidance is proposed, **Then** each recommendation identifies the tested model/version, effort if reported, test conditions, source provenance, limitations, and applicability to the proposed task; unknown details remain unknown.
3. **Given** a project later refines or supersedes a routing guideline, **When** an agent needs the initial rationale or supporting evidence, **Then** it can find the retained original guidance and relevant source record without reading the entire execution history.
4. **Given** two benchmarks use noncomparable versions, efforts, or test conditions, **When** routing is justified, **Then** the differences and uncertainty are visible; no fabricated comparison, universal ranking, or promised success rate is asserted.

---

### User Story 3 - Delegate a Deterministic Luna Task (Priority: P1)

As a coordinator, I can send eligible bounded implementation work to Luna only when its contract leaves exceptionally little unresolved implementation reasoning and provides an executable acceptance oracle.

**Why this priority**: Less expensive execution is useful only when decomposition and observable acceptance protect correctness and reduce avoidable retries.

**Independent Test**: Inspect one complete and one incomplete Luna-bound task; accept only the complete contract and demonstrate that its executable oracle distinguishes an incorrect outcome from the required one.

**Acceptance Scenarios**:

1. **Given** a candidate Luna task, **When** task readiness is checked, **Then** its objective, scope, allowed surfaces, exclusions, constraints, prerequisites, ordered steps, observable outputs, required capabilities, and executable pass/fail acceptance oracle are explicit before dispatch.
2. **Given** a task with an ambiguous outcome, missing producer, or an acceptance statement such as “looks correct” without an executable oracle, **When** Luna eligibility is assessed, **Then** dispatch is blocked until decomposition or task-contract correction resolves the defect; another family is not silently substituted.
3. **Given** several small dependent tasks, **When** they are prepared for delegation, **Then** each retains an independently verifiable outcome and checkpoint, producers precede consumers, and shared context does not turn them into one unbounded acceptance unit.

---

### User Story 4 - Recover a Failed Task Before a Bounded Retry (Priority: P1)

As the owner, I can understand a failed attempt, preserve its evidence, safely undo only its implementation commit before an authorized retry, and know that escalation will stop at the defined bound.

**Why this priority**: Retrying from contaminated task state or discarding unrelated work is unacceptable, even when a stronger family is available.

**Independent Test**: Use isolated task-state examples with a failed task commit, unrelated changes, and dependent work; inspect diagnosis, pre-mutation evidence, recovery result, attempt count, and stop outcomes. These examples do not authorize rollback in a real project.

**Acceptance Scenarios**:

1. **Given** an eligible Luna task fails with wholly task-owned changes, **When** failure inspection and pre-mutation evidence establish safe recovery, **Then** an existing task-only implementation commit is used, or a focused failed-attempt commit is created even if required checks failed; it is explicitly marked NOT VERIFIED, ordinarily reverted by a separate inverse commit, and the restored starting state is checked before an authorized Terra attempt. A failed Terra attempt can similarly reach Sol, but a failed Sol attempt stops. The task has at most three total attempts.
2. **Given** a task starts on Terra, **When** Terra fails and retry prerequisites pass, **Then** only Sol is the automatic next-family candidate; after Sol fails the task stops. **Given** a task starts on Sol, **When** it fails, **Then** it stops after that single attempt absent a new owner decision.
3. **Given** failure inspection identifies unavailable tools, permissions, runtime capability, or another environmental cause, **When** escalation is considered, **Then** that cause is distinguished from reasoning failure and must be resolved under existing authority before another attempt; a different family or higher effort is not assumed to repair the environment.
4. **Given** mixed-ownership commits, baseline drift, dependent work that would be invalidated, unavailable failure details, or an unproven task-only inverse, **When** recovery is considered, **Then** mutation and retry stop with the exact blocker; unrelated changes and recorded evidence remain intact.
5. **Given** the next family does not support the previously used effort, **When** retry is prepared, **Then** effort is selected independently from verified supported options using the task and diagnosed cause; no fixed effort ladder or unsupported request is used.
6. **Given** all allowed attempts have failed, **When** Astra is available, **Then** availability does not authorize a fourth attempt; a new owner decision is required for any further execution.

---

### User Story 5 - Learn Without Rewriting Project Policy Automatically (Priority: P2)

As the project owner, I can review factual routing outcomes separately from proposed reusable guidelines, retain useful initial evidence, and approve, edit, reject, or add guidance without weakening existing approvals or review.

**Why this priority**: Evidence should improve future coordination while preserving uncertainty, project boundaries, and owner control.

**Independent Test**: Record success, failure, and recovery in separate indexed task/run evidence; propose a guideline change and exercise rejection, exact-content approval, and concurrent drift. Verify only approved, baseline-matching guidance changes persist.

**Acceptance Scenarios**:

1. **Given** a failed and retried task, **When** its checkpoint is recorded, **Then** each attempt has its own family/binding/effort, baseline and result or unknown status, checks, diagnosis, invocation/run references, recovery evidence, and outcome; the compact project-local index points to the relevant records rather than reproducing logs.
2. **Given** one Luna failure, **When** reflection proposes guidance, **Then** it retains uncertainty and counterevidence and does not impose a permanent family/subsystem ban or silently alter synthesized guidelines.
3. **Given** rejected or pending guidance, **When** the run closes, **Then** guideline bytes remain unchanged, the disposition and evidence remain discoverable, and implementation acceptance is reported separately from guideline approval.
4. **Given** approved guideline content whose baseline has changed before application, **When** persistence is attempted, **Then** application stops for renewed owner review rather than overwriting concurrent edits.
5. **Given** existing TinySpec, Standard, or documented legacy artifacts, **When** work resumes, **Then** valid provenance and approval evidence are retained, unresolved routing is explicitly selected and verified, and no historical approval, model mapping, or planning-depth choice is fabricated.

### Edge Cases

- A verified option disappears between owner selection and dispatch: stop and seek an authorized replacement; configuration names and past successful launches alone are not current capability proof.
- A family exposes one effort or no adjustable effort: record the verified supported behavior explicitly; do not invent an effort menu or equate omitted effort with a known value.
- A failed launch has uncertain execution status: preserve the uncertainty and stop; do not infer success, a safe clean state, or a refunded attempt.
- A failed invocation is resumed, rotated, or placed in another batch: renewed task execution after failure is another attempt and must follow the same remaining family sequence; renaming or session changes never reset the budget.
- A failure produced no implementation commit: record the failure and verify task baseline, ownership, and partial changes. If wholly task-owned changes exist and are safe to checkpoint, make an explicitly failed-attempt commit followed by its ordinary inverse; if nothing changed, or safe task-only commit/revert is unavailable, stop retry without an empty or fabricated commit.
- A defect is found after dependents have consumed a committed task: stop retry/rollback, inspect dependency impact, and return unsafe recovery or changed scope to the owner; do not automatically undo downstream work.
- A recovery, evidence write, checkpoint, or required check fails: report the exact blocker and stop affected execution, leaving recoverable state and evidence intact.
- Astra may be explicitly selected for an initial stage, review, or task when verified and authorized; it is outside the automatic implementation retry sequence. An initial Astra task failure has no automatic next attempt.
- An empty project guideline store supplies no learned routing rules. No matching history supplies no invented evidence; mandatory coordination persistence still applies.
- Benchmarks omit a family or tested effort: retain the coverage gap and restrict consequential recommendations to supported claims or obtain an explicit bounded owner deferral through the existing gates.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The suite MUST replace `sonnet-class`/`opus-class` model specification throughout active planning and coordination workflows with model family and independently selected reasoning effort. This includes stage assignments, task contracts, delegation briefs, recovery rules, adapters/direct consumers, validation expectations, and normative documentation/configuration examples. Neither obsolete tags nor class-share rules may remain active routing authority under another spelling.
- **FR-002**: Initial family names MUST be Luna, Terra, Sol, and Astra. A family name MUST NOT imply a provider, concrete model version, capability, price, context size, or supported effort. The permitted runtime binding and its supported options MUST be verified when needed; not every family supports every effort.
- **FR-003**: Each stage/task/review routing selection MUST identify family, verified concrete binding, separately selected effort or explicitly verified nonadjustable behavior, supporting capability evidence, rationale, and owner authorization. Unobserved actual execution details MUST be recorded as unknown, not inferred from a requested setting.
- **FR-004**: Only permitted, usable options MUST be offered. Missing question, delegation, independent-review, mutation-tool, or other required capabilities MUST stop the affected stage with an exact capability report. Model availability checks MUST NOT install dependencies or grant external-operation authority.
- **FR-005**: Routing guidance MUST be advisory and task-specific, using task characteristics, unresolved reasoning, oracle strength, relevant local outcomes, and applicable benchmark evidence. A family MUST NOT have a permanently fixed effort, stage, or universal capability ranking; source requirements and owner-selected routing remain authoritative.
- **FR-006**: Before consequential routing plan/task decisions, planning MUST complete targeted research or validate sufficient reusable current evidence under the existing dependency-research contract. Insufficient sources, capabilities, binding/version applicability, or durable-write authority MUST block affected decisions unless the owner explicitly approves a bounded deferral with its impact and outstanding validation.
- **FR-007**: INITIAL provisional recommendations MUST be based on credible, inspected, current coding/tool-use or other task-relevant sources, preferring primary benchmark reports and reproducible methodology where available. Each supporting claim MUST retain source identity and location, inspected supporting span, research date, tested provider/model/version, effort if reported, test conditions, result as actually reported, limitations, uncertainty, and task applicability. Missing fields MUST be visible; uninspected links, invented scores, and generic recollection are not evidence.
- **FR-008**: Benchmark observations, derived provisional recommendations, owner decisions, and project execution outcomes MUST be distinguishable. Noncomparable conditions, missing coverage, and counterevidence MUST be explicit; an external score alone MUST NOT guarantee a project's task outcome.
- **FR-009**: The original benchmark-informed guidance and supporting provenance MUST remain durably discoverable for future agents whenever relevant, including after project guidelines are edited, superseded, or removed. Normal guideline maintenance MUST NOT erase that baseline or its sources. Retrieval MUST allow relevant-only access without loading all execution history; current guidance and retained initial guidance MUST be clearly distinguished.
- **FR-010**: Global assets MUST contain reusable routing process only, not any project's learned outcomes or permanent project-specific policy. Factual attempts and project-specific synthesis MUST remain in the existing project-local coordination stores and their compact index, separate from gotcha memory and durable benchmark reference material.
- **FR-011**: All implementation tasks MUST remain decomposition-friendly and independently verifiable, with explicit prerequisites and source traceability. Routing MUST NOT replace clear task boundaries, producer-before-consumer ordering, or acceptance checkpoints.
- **FR-012**: Luna-bound implementation tasks MUST have an exceptionally explicit objective, scope and allowed surfaces, exclusions, constraints, dependencies, ordered steps with observable outputs, required capabilities, and executable acceptance oracle with a deterministic pass/fail result. Missing or ambiguous elements MUST block Luna dispatch and return to task preparation/review; no informal assurance substitutes for the oracle.
- **FR-013**: Family and effort choices MUST remain separate from approval of task scope and acceptance. Effort MUST be justified per task and, on failure, per diagnosed cause, using only the selected binding's verified supported options. There MUST NOT be a fixed low-to-high effort escalation ladder or an effort inferred from family name.
- **FR-014**: Automatic implementation retry candidates MUST follow eligible Luna → Terra → Sol, starting Terra → Sol, or starting Sol → stop. The maximum is THREE total task attempts, including the initial attempt; the starting family reduces the available sequence to two or one respectively. Each automatic candidate still requires safe recovery, verified capabilities, existing owner-selected routing authority, and unchanged applicable approvals. No automatic Astra fourth attempt or skipping an unavailable next family is allowed.
- **FR-015**: An attempt MUST cover actual task execution, not approval dialogue or a read-only preflight. Every renewed task execution after failure, including resume/relaunch, MUST consume the next permitted attempt; session, batch, model-version, or effort changes MUST NOT reset or extend the count. Uncertain execution status MUST stop for inspection rather than create an assumed extra allowance. Further execution outside the sequence requires a new explicit owner decision, recorded separately from the exhausted automatic budget.
- **FR-016**: Before retry or recovery, the coordinator MUST inspect the failed run/session and failed tool invocation, review task checks and any commit/partial changes, and distinguish reasoning/implementation failure from capability/environment failure or unknown cause. The diagnosis, proposed corrective action, and why another attempt could address the cause MUST be recorded. Unknown cause or unavailable inspection evidence MUST stop; an environment failure MUST NOT automatically justify stronger reasoning.
- **FR-017**: After a failed attempt with wholly task-owned changes, the coordinator MUST identify its existing implementation commit or create one focused commit of those failed changes, even when required checks failed. Such a new commit MUST be identified as a FAILED-ATTEMPT checkpoint, never a verified task completion or release of dependents. Before retry, the failed task commit MUST be undone by a separate ordinary history-preserving inverse commit; no alternate inverse, reset, history rewrite, unrelated-work discard, evidence undo, or automatic dependent-task revert is allowed. If nothing changed or a safe commit-and-inverse pair cannot be made, record the failure and stop retry; never create empty or fabricated commits.
- **FR-018**: Before a failed-attempt commit or inverse, recovery eligibility MUST establish the failed attempt's baseline, exact owned paths/changes, existing or proposed task commit, current index/worktree and approval state, required-check results, and dependent-task impact. Mixed ownership, unsafe or sensitive content, conflicting changes, unverified baseline, invalidated dependencies, or unavailable ordinary task-only inverse MUST stop mutation and retry. A whole-project clean tree MUST NOT be obtained by erasing unrelated work.
- **FR-019**: Failure, diagnosis, existing commit identity or proposed failed-attempt commit scope, ordinary inverse scope, safety/dependency assessment, and applicable recovery authorization MUST be persisted and checkpointed in project-local evidence BEFORE either recovery commit. Record the failure commit identity and its failed-check status before the inverse; after recovery, evidence MUST record both commit identities, actual inverse result, restoration checks, and preserved unrelated state. Persistence/checkpoint failures MUST stop before the next mutation or dispatch.
- **FR-020**: Successful recovery MUST leave a verified task starting state, an auditable failed-task commit and distinct ordinary inverse commit, and separately retained failure/rollback evidence before another attempt. Approval of the current feature/task recovery policy preauthorizes only demonstrably safe task-only failed-attempt and inverse commits within its recorded bounds; no routine per-inverse owner question is needed. Unsafe, unclear, or out-of-bounds recovery stops for an explicit owner decision; ordinary implementation approval alone does not grant rollback authority before this policy is approved.
- **FR-021**: Every attempt/checkpoint MUST record task/run identity, characteristics and optional residual-reasoning rationale, selected and observed family/binding/effort, attempt number and remaining budget, baseline/result revision or explicit absence, inspection/diagnosis, required check outcomes, reviewer/manual findings, recovery, escalation, and final disposition. Failed, blocked, partial, and unknown outcomes MUST remain factual and attributable.
- **FR-022**: Growing execution evidence MUST remain separate run/task records with a compact index. Record creation/update MUST precede index refresh; interrupted updates MUST be reconciled. Ordinary planning MUST read compact project guidelines first, not all history; justified historical retrieval MUST be index-first and relevant-only. Sensitive payloads, credentials, and personal data MUST NOT be persisted.
- **FR-023**: Reflection MUST distinguish direct observations, tentative/repeated patterns, stable guidance, insufficient evidence, and contradictions. One failure MUST NOT become a permanent routing rule. Candidate add/refine/supersede/remove changes MUST be separated from factual evidence and linked to supporting and contradicting sources, including retained initial guidance where relevant.
- **FR-024**: Synthesized project guideline changes MUST require explicit owner accept/edit/reject/add review of exact resulting content, independently of implementation approval. Pending, rejected, cancelled, ambiguous, or unavailable approval MUST leave guideline bytes unchanged. Current-content drift MUST stop application and require renewed review; approved changes MUST NOT erase retained benchmark provenance.
- **FR-025**: TinySpec and Standard depth choice, current-content source/specification/final approval gates, dependency order, execution authorization, sequential coordination, per-task implementation and distinct evidence checkpoints, required acceptance checks, and fresh independent final review MUST be preserved. Family/effort changes MUST NOT weaken these boundaries or bypass a missing reviewer.
- **FR-026**: Existing and documented legacy artifacts MUST retain valid shapes, provenance, evidence, and approval history where compatible. Historical class labels MUST NOT be interpreted as current family/effort authority or converted into guessed mappings. Resumed execution requiring new routing selection or materially changed contracts MUST return to the affected owner gate; no forced recreation or fabricated approval is permitted.
- **FR-027**: Future feature verification MUST cover supported/unsupported selections, all three bounded retry starts, no automatic Astra continuation, failure-cause inspection, safe and blocked recovery, incomplete Luna contracts, evidence/index persistence, selective retrieval, rejected/approved/drifted guideline changes, retained initial guidance, and both workflow routes with legacy recovery. Static/isolated demonstrations MUST NOT be reported as live model-obedience or real benchmark proof.

### Key Entities *(include if feature involves data)*

- **Model family**: Luna, Terra, Sol, or Astra; an owner-facing routing identity, distinct from its currently verified provider/model binding and from effort.
- **Runtime capability observation**: Permitted usable binding, supported effort behavior, relevant tools/context/delegation limits, verification evidence and applicability to the imminent stage.
- **Routing selection**: Stage/task/reviewer identity, family and concrete binding, effort, task-specific rationale, source evidence, and current owner-selection authority.
- **Initial routing guidance and benchmark record**: Retained provisional recommendation and inspected supporting claims, tested versions/efforts/conditions, limitations, provenance and discovery references; distinct from evolving project guidelines.
- **Task contract and attempt**: Bounded outcome, dependencies, acceptance oracle and routing; each attributable execution attempt has its own checks, diagnosis, revision, count and disposition.
- **Recovery assessment and result**: Failed task baseline/commit/ownership, dependency impact, proposed inverse scope, approval evidence, pre-mutation checkpoint and verified post-recovery state.
- **Project coordination evidence and guidelines**: Separate indexed factual run/task records and compact mutable project guidance, connected through owner-reviewed reflection rather than automatic promotion.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Across all active planning/coordination entry points and normative routing examples, zero obsolete class-based routing instructions remain; each required selection distinguishes family and effort, offers only verified options, and retains owner control (FR-001–FR-005, FR-013, FR-025–FR-026).
- **SC-002**: Every consequential initial routing recommendation has inspectable task-relevant support or an explicit bounded owner deferral; a future agent can recover the original recommendation and provenance after a current guideline is superseded without opening unrelated run records (FR-006–FR-010).
- **SC-003**: Every Luna-bound implementation task in acceptance examples exposes all required contract elements and an executable oracle; each incomplete example is blocked before dispatch (FR-011–FR-012).
- **SC-004**: Failed-task examples starting on Luna, Terra, and Sol permit no more than three, two, and one total attempts respectively; zero automatic Astra fourth attempts occur, and missing inspection or recovery evidence blocks renewed execution (FR-014–FR-016).
- **SC-005**: In every accepted recovery example with task-owned changes, failure and commit/inverse-scope evidence predates mutation, a failed-task commit (new if needed) and distinct ordinary inverse are visible, failed checks are never reported as verified completion, history and unrelated work remain intact, task-only restoration is verified, and the next attempt has a justified supported effort. No-change and unsafe ownership/dependency/baseline examples stop without empty commits or rollback (FR-013, FR-017–FR-020).
- **SC-006**: Every attempted task, including failed/blocked/partial work, has attributable project-local evidence and an updated compact discovery entry; rejected, pending, and drifted guideline examples produce zero unapproved guideline changes and no loss of initial provenance (FR-021–FR-024).
- **SC-007**: Both TinySpec and Standard acceptance journeys, plus a documented legacy resume journey, preserve their applicable approvals, producer ordering, per-task checkpoints and independent-review boundary; no routing change is used to claim implementation authorization or live obedience from static checks (FR-025–FR-027).

## Assumptions

### Scope and Dependencies

- This is an incremental suite-wide routing change, not a new memory framework. Existing mandatory project-local coordination initialization, indexed evidence, conservative reflection, approval drift checks, and gotcha-memory separation remain authoritative except for explicitly superseded model-class routing and the unresolved failed-task recovery policy.
- Exact runtime providers, versions, effort names and availability are intentionally unspecified. Named families are the initial owner-facing vocabulary, not evidence that this specification has exercised those models.
- Targeted benchmark research is an authorized later planning-stage dependency, not work performed here. No benchmark was fetched and no result, preferred family-by-task table, or performance promise is asserted by this specification. Planning must verify canonical durable research ownership/discoverability and bounded write authority before retaining new guidance; this stage grants no such documentation writes.
- Removed class-based percentages are not automatically translated into a quota for any family. No new family-share constraint is requested; owner-selected routing, decomposition, acceptance, and capability gates remain in force.
- Immutable historical evidence and approvals remain truthful provenance, not executable policy. Compatibility does not preserve obsolete labels as current routing defaults. Active normative contracts/examples and their checks must be updated during future approved implementation.
- An explicitly selected initial Astra task has no defined automatic escalation path, so failure stops for an owner decision; Astra availability is never retry authorization.
- All scenarios describe future required behavior. This stage creates only this specification, its quality checklist, and the ignored SpecKit feature pointer, then one focused specification/checklist commit. It performs no planning, task generation, implementation, model dispatch, rollback, benchmark fetch, configuration change, guideline mutation, or coordination-evidence write.

### Settled Recovery Decisions — Subject to Specification Approval

- **Q1 — Permitted inverse method**: The owner chose an ordinary, focused, history-preserving inverse commit only. If it is unavailable or unsafe, stop; no independently constructed alternative inverse is authorized. This deliberately changes the current “separate verified correction tasks, never automatic rollback” rule for this narrowly bounded retry feature, once implemented and approved.
- **Q2 — Recovery approval**: Approval of the current feature/task recovery policy preauthorizes demonstrably safe task-only inverse commits within its recorded bounds; no per-inverse question is required. Ambiguous, unsafe, or out-of-bounds recovery and execution beyond the permitted attempt sequence still need a separate owner decision.
- **Q3 — Failure checkpoint before inverse**: The owner further directed that a task-owned failed attempt must be committed even when required checks fail, then ordinarily reverted in a second commit before retry. This failed-attempt checkpoint is auditable, explicitly NOT VERIFIED, and never a successful per-task completion. If there are no task-owned changes, or commit/revert safety cannot be established, stop without an empty commit or destructive workaround. This is a deliberate future change to the existing verified-only task-commit contract; it is not an instruction to perform live rollback now.

### Source Provenance and Decision Precedence

- **S1 — Original supplied request**: [Project-Specific Coordination Memory implementation prompt](/home/dev/.paseo/uploads/upload_72cab873-63d1-44e2-b5e6-94111228b5b1/project-coordination-memory-implementation-prompt%20%282%29.md), read in full (684 lines). Relevant spans: evidence/guidance separation and partial reads, lines 80–242; compact guidance, uncertainty and approval, 244–372; delegation and retry motivation, 374–466; persistence/retrieval, 506–571; non-goals, compatibility and validation, 610–662. Its conceptual tier/provider examples and “rather than benchmarks” experiment framing are superseded by the owner decisions below.
- **OD1 — Scope/routing, authoritative authorized handoff (2026-10-06)**: “remove sonnet-class/opus-class model specification EVERYWHERE in planning and coordination workflow, replacing with model family + independently selected reasoning effort.” Initially Luna, Terra, Sol, Astra; runtime provider/version/effort verification, not every family supports all efforts. Applies to FR-001–FR-005, FR-013, FR-025–FR-026.
- **OD2 — Initial evidence, same handoff**: benchmark-informed INITIAL provisional routing guidance from credible current coding/tool-use/task-relevant sources; version/effort/test-condition/limitations provenance; durable future access as guidelines iterate; targeted research before consequential planning/task routing decisions, not invented specification results. Applies to FR-006–FR-010.
- **OD3 — Task quality, same handoff**: “Luna-bound implementation tasks need exceptionally explicit objective, scope, constraints, dependencies, steps/observable outputs and executable acceptance oracle; tasks should be decomposition-friendly.” Applies to FR-011–FR-012.
- **OD4 — Retry and effort, same handoff**: “At most THREE total task attempts: eligible Luna -> Terra -> Sol; starting Terra -> Sol; starting Sol -> stop after its failed attempt absent owner decision; no automatic Astra fourth attempt.” Effort comes from verified supported options per task/diagnosed failure, not a fixed ladder. Applies to FR-013–FR-016.
- **OD5 — Recovery/evidence, same handoff and subsequent owner clarification**: inspect each failed run/invocation, distinguish environment/capability from reasoning failure, retain each attempt/failure in project-local evidence; before retry commit task-owned failed changes even if checks failed, label NOT VERIFIED, then revert that exact failed-task commit with a distinct ordinary inverse commit. The owner selected policy-bounded preauthorization, no alternate inverse, and stop on unsafe/empty/mixed-ownership recovery. Preserve baseline/dependency checks and checkpoint failure/rollback evidence before mutation. Applies to FR-016–FR-022 and settled Q1–Q3.
- **OD6 — Preserved safeguards, same handoff**: project-local evidence/index; owner approval for synthesized guidelines; no single-failure permanent rules; per-task commit/evidence checkpoints; owner-selected capability gates, approvals, dependency order, independent review and compatible legacy recovery. Applies to FR-010–FR-011, FR-019–FR-027.
- **OD7 — Current stage authority, same handoff**: the owner selected Standard and Sol and authorized this specification-only launch as a deliberate stage-local exception to the existing specification class tag. That selection authorizes neither downstream planning nor implementation and does not establish any permanent family/effort default.
- **S2 — Inspected repository authorities at baseline `08a16f34154f2fe45e4c99470d1e17ce35ed37a8`**: [AGENTS](../../AGENTS.md), [runtime requirements](../../REQUIREMENTS.md), [constitution](../../.specify/memory/constitution.md), [Planner](../../skills/planner/SKILL.md), [approval/recovery](../../skills/planner/references/approval-and-recovery.md), [dependency research](../../skills/planner/references/dependency-research.md), [coordination memory](../../skills/memory-handling/references/project-coordination.md), [task checkpoints](../../skills/memory-handling/references/task-commit-contract.md), [Coordinator](../../skills/coordinate-implementation/SKILL.md), [task generation](../../skills/task-generation/SKILL.md), [SDD](../../docs/best_practices_spec_driven_development.md), and the installed [specification stage](../../.pi/prompts/speckit.specify.md). The owner modifications override contradictory class/tier examples, not unrelated governing safeguards. Required governance updates belong to future approved work, not this stage.
- **S3 — Current local guidance**: [coordination guidelines](../../memory/coordination/GUIDELINES.md) states “No approved project coordination guidelines yet.” No rule is derived, seeded, or modified by this specification.

### Explicit Non-Goals

No machine learning, bandits, embeddings, automatic statistical routing optimization, complex confidence framework, cross-project learned memory, unbounded guideline growth, automatic guideline mutation, new parallel planning framework, migration of all historical artifacts, fabricated benchmark rankings, fixed provider/version bindings, fixed effort ladder, automatic fourth attempt, history rewrite, unrelated cleanup, or approval/review/checkpoint waiver.
