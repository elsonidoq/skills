# Feature Specification: Batch-Level Model/Effort Routing and Verification Contracts

**Feature Branch**: `batch-level-model-effort-routing`

**Created**: 2026-10-06

**Status**: Draft for specification approval

**Input**: Owner's “Implement Batch-Level Model/Effort Routing and Verification Contracts” request in the initiating conversation; owner selected Standard and directed use of GPT-6.1 Sol for this planning work, and removal of active Sonnet/Opus task-assignment classes after implementation.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Route a coherent implementation batch (Priority: P1)

As the coordinator, I assess a batch of related, consecutive tasks and choose one supported model family and independently justified reasoning effort before dispatch. Normally 2–5 related tasks share context; a materially different execution profile is a reason to split, never a reason to give tasks within one invocation different assignments.

**Why this priority**: Routing at task granularity contradicts the existing execution model and obscures the cost of a subagent invocation.

**Independent Test**: Inspect the batch decision and actual dispatch for bounded and difficult batches; check the exact family, binding, effort, constraints and source of guidance.

**Acceptance Scenarios**:

1. **Given** a closed-design, shallow batch with strong executable contracts and cheap recovery and no adverse local guidance, **when** routed, **then** the seed rubric proposes Luna/medium if the exact binding and effort are supported, and one profile covers the entire batch.
2. **Given** a bounded multi-file batch with moderate residual reasoning and strong contracts, **when** routed, **then** the rubric may propose Luna/max as an experiment with recorded rationale, not silently relabel it Luna/medium.
3. **Given** deep tool use, weak oracles, unresolved architecture, high failure cost or relevant repeated negative guidance, **when** routed, **then** optimistic Luna assignment is rejected in favor of a justified supported stronger option or an owner/design gate; a relevant approved project guideline overrides the seed prior.
4. **Given** no matching project guidance, **when** routed, **then** the global seed prior remains usable; the absence of local evidence is not treated as a success record.

---

### User Story 2 - Prove each task and accept a batch cheaply (Priority: P1)

As the coordinator, I receive evidence against the pre-defined verification contract for every task in the batch, and accept only when the union is covered and consistent with committed changes and scope. Shared checks can support several items without duplicate execution.

**Why this priority**: Assignment quality cannot be evaluated from an agent's confidence or a bare “done.”

**Independent Test**: Present a batch with two task contracts, shared checks, a missing item and a contradictory output; inspect accept/blocked results and task-to-evidence mapping.

**Acceptance Scenarios**:

1. **Given** task-specific required checks, observables and manual checkpoints defined in existing task acceptance fields, **when** a batch is dispatched, **then** the implementer receives their complete union with stable task/item references and reports pass/fail/not verified plus concrete evidence for each item.
2. **Given** every required item passes, observables exist, manual gates were honored, and each per-task checkpoint/diff is in scope, **when** the coordinator performs cheap validation, **then** it accepts the batch without mandatory strong-model review after every Luna batch; the existing final independent review remains required.
3. **Given** incomplete, failed or contradictory evidence, an unrun required check, or out-of-scope changes, **when** validated, **then** the coordinator cannot mark that batch accepted or release dependents.

---

### User Story 3 - Diagnose, escalate and learn without false attribution (Priority: P2)

As the coordinator, I preserve valid work, inspect failures, and propose a targeted repair or escalation that may change model, effort, or both. Factual routing feedback feeds existing project coordination memory, but only owner-approved synthesis changes project guidance.

**Why this priority**: An environment outage or a missing specification must not be mistaken for model incapacity.

**Independent Test**: Exercise capability-related Luna/max → Sol/medium repair, environment-blocked Luna/medium, and relevant approved local guidance overriding the generic seed.

**Acceptance Scenarios**:

1. **Given** a failed explicit compatibility invariant after Luna/max and a diagnosed capability error, **when** a usable Sol/medium repair is authorized, **then** the request includes the original assessment/profile, passed and failed items, implementation state, and complete re-verification; passing tasks are preserved unless implicated.
2. **Given** a required environment is unavailable, **when** checks cannot run, **then** the batch remains unverified, attribution is `environment_or_tooling`, and the profile is not penalized as inadequate.
3. **Given** complete first-attempt evidence under a meaningful contract, **when** accepted, **then** feedback records the exact model and effort and qualified positive evidence; weak verification or later invalidation prevents strong generalization.
4. **Given** repeated relevant negative evidence synthesized into an approved project guideline, **when** a similar batch is routed, **then** that guidance can recommend Sol/medium over seed Luna/max; raw feedback never directly edits the guideline.

### Edge Cases

- A family or effort is merely cataloged, not callable, unsupported by the selected binding, or actual effort is unobservable: stop or mark actual as unknown; do not claim an unsupported selection ran.
- One task has a weak contract and another a strong one: the batch assessment reflects the weakest material blind spot; split if a different execution profile is needed.
- Missing/ambiguous task acceptance or a required permission gate blocks dispatch/acceptance, not a retroactive check waiver.
- Failed invocation or partial commits: inspect the child run/invocation and task-owned state before resumption, new dispatch or escalation; preserve unrelated changes and per-task commit checkpoints.
- A successful repair does not erase the first failure or prove that the original model alone caused it.
- A prior project guideline is irrelevant, tentative or contradicted: record applicability and uncertainty rather than silently overriding source requirements.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Active planner/task-generation/coordinator routing MUST replace Sonnet/Opus implementation-task class assignments with independently selected family and reasoning effort. Neither dimension implies the other. Verify the permitted concrete binding and its supported effort at assignment and dispatch; retain owner choice and existing approval/provenance gates. Preserve independent final review and task-level commits.
- **FR-002**: The coordinator MUST preserve consecutive, sequential coherent batching, normally ~2–5 tasks when feasible, with one model+effort per invocation. Split for materially incompatible execution profiles, dependencies, permissions, or context, not a task-count quota. No one-agent-per-task default.
- **FR-003**: An inspectable global *seed* rubric MUST assess residual reasoning, agentic/tool depth, verification strength, scope/coupling, failure cost/reversibility and relevant approved project guidance. Explain hard escalation signals and the provisional Luna/medium, Luna/max, Sol/low or medium, and justified Astra/Terra options separately by model and effort. Ground the prior in the supplied benchmark compilation without equating different harnesses or deriving a universal ranking.
- **FR-004**: Before dispatch, each batch MUST have a compact recorded decision naming batch/task IDs, factor assessment, applicable local evidence (or none), exact proposed/selected model binding and effort, family/effort rationale, and conditional escalation option. Owner/model permission gates remain in force; no blind model switch.
- **FR-005**: Every new task MUST identify objective REQUIRED verification items by stable task-local reference, reusing the existing acceptance/observable/invariant/test fields. Include expected evidence, smallest sufficient checks, any manual/permission gates and optional checks separately. Existing approved tasks without adequate contracts return to their producing review/approval gate; no fabricated historical contracts.
- **FR-006**: A batch contract MUST aggregate all task REQUIRED items, allowing one valid check to cover multiple items while retaining each task mapping. The implementer MUST receive the whole contract and return actual execution/check results, evidence or explicit not-verified reason per item, changed files and per-task checkpoint references. Confidence alone cannot substitute for evidence.
- **FR-007**: The coordinator MUST inspect each checkpoint/diff and cheaply validate required evidence completeness, consistency, outputs, scope and manual gates. Passing contracts allow batch acceptance without a mandatory strong-model per-batch review. Missing, failed, contradictory or unauthorized evidence blocks acceptance and dependent work, without waiving the final independent review.
- **FR-008**: A failed batch MUST be diagnosed before targeted escalation, preserving valid work and prior attempt evidence. Escalation can raise effort, change model or both, only through verified usable permitted bindings and owner-selection gates; full batch contract is rerun where invalidated. Do not impose a universal profile ladder or blindly restart.
- **FR-009**: Factual feedback for accepted, partial, escalated and blocked batches MUST be persisted through the existing indexed project coordination evidence lifecycle, including exact model+effort per attempt, assessment, contract strength, first-attempt/final outcome, escalation and attribution (`model_capability`, `planning_or_spec_gap`, `verification_contract_gap`, `batching_error`, `environment_or_tooling`, `external_dependency`, `unknown`). Non-model causes cannot be counted as model failure; weak or invalidated successes cannot become strong positive evidence.
- **FR-010**: Existing selective reflection and exact owner approval MUST remain the only path from run evidence to project-specific routing guidelines. Relevant approved guidance may refine or override the generic prior but cannot override owner/source authority. No new memory store, automatic guideline mutation, ML, statistical router or global rule learned from one project.
- **FR-011**: The solution MUST demonstrate five bounded scenarios: Luna/medium accepted with no strong per-batch reviewer; Luna/max accepted with effort preserved; diagnosed capability failure Luna/max repaired by Sol/medium; environment-blocked Luna/medium not penalized; approved local guidance overriding seed Luna/max with Sol/medium. Static/simulated checks must be labeled as such, not claimed as live model performance.

### Key Entities

- **Task verification item**: Task-local stable identifier, required/optional or gated status, observable/pass criterion and evidence source.
- **Batch routing decision**: Ordered task IDs, assessment dimensions, relevant guidance, exact binding and effort, rationale and conditional repair profile.
- **Batch outcome/feedback**: Item-mapped results, task checkpoints, attempt profiles, diagnosis, evidence quality and disposition, recorded in existing coordination run/task evidence.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All five named scenarios produce the expected accept/escalate/blocked result in focused validation without requiring a per-batch strong reviewer on the successful Luna paths.
- **SC-002**: For every accepted sample batch, 100% of required task items have identifiable supporting evidence, and the decision and feedback retain the exact selected family/binding and effort.
- **SC-003**: In the environment-blocked example, the routing feedback labels the check unverified and makes no capability-failure inference; in the local-guideline example, the chosen profile follows the approved applicable guideline.
- **SC-004**: Active workflow documentation continues to work for projects with empty coordination guidelines, preserves task checkpoints and final independent review, and makes no claim of live runtime obedience from fixture-only tests.

## Assumptions and exclusions

- The owner's newer batch-only request supersedes the *proposed* per-task routing and fixed retry ladder in `specs/001-model-family-routing/` for this feature; the older approved specification remains historical provenance, not silently edited or treated as implementation authorization for this new scope.
- Existing project coordination memory is already implemented; only small compatibility wording for exact profile/feedback is in scope. The supplied CSV is evidence for a distilled global seed and may be archived in an appropriate research location if useful; it is not a runtime input or a project-specific approved guideline.
- No ML, statistical optimization, synthetic live benchmark, mandatory per-batch independent reviewer, project-memory redesign, deployment, push or irreversible operation is in scope.
- Provider support and invocation details must be verified from this repository's actual Pi/subagent integration when planning and before dispatch; names/examples in the request are conceptual until checked.
