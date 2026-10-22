# Implementation Plan: Batch-Level Model/Effort Routing and Verification Contracts

**Branch**: `batch-level-model-effort-routing` | **Date**: 2026-10-06 | **Spec**: [spec.md](spec.md)

**Input**: Current approved specification, digest `1b4d5b90ac1e1429739e5260d0955716d125a1b4ae8430141e89b610eacd9895`; [approval](spec-approval.md). This is planning preparation, not implementation authorization.

## Summary

Replace active implementation-task class assignment with coordinator-owned, batch-level selection of one exact model binding and independently justified effort. Keep ordered sequential execution, normally 2–5 context-coherent tasks, per-task verification/commits and one final independent review. Task acceptance fields own stable verification items; the coordinator aggregates their union, inspects returned evidence and checkpoints, and blocks acceptance on missing or contradictory proof. Diagnose failures before an authorized targeted repair; persist qualified attempt feedback through existing project coordination memory without automatic guideline changes.

Use [canonical research](research.md) at checkpoint `dc62fa3`, not the older task-routing proposal. No new router service, benchmark database, runtime interceptor or external API is needed. This design extends Markdown skill contracts and their existing Python static/fixture checks.

## Technical Context

**Language/Version**: Markdown operational contracts; Python 3 for existing check/fixture scripts; Bash for installed SpecKit setup.

**Primary Dependencies**: Pi 0.87.x (research inspected 0.87.1), pi-subagents 0.73.1, pi-ask-user 0.15.1, installed project SpecKit prompt/template/scripts; pins owned by [REQUIREMENTS.md](../../REQUIREMENTS.md). No new dependency.

**Storage**: Existing project-local coordination run/task Markdown evidence and compact index; existing Git task/evidence checkpoints. No new store or schema migration.

**Testing**: Focused contract assertions and simulated routing/evidence fixtures added to existing Python unittest seams; manual source-to-dispatch and docs consistency review. See [quickstart](quickstart.md).

**Target Platform**: Pi skill suite across unrelated repositories with locally installed Standard capability; project paths and selected bindings are discovered, not hard-coded into global instructions.

**Project Type**: Instruction-managed workflow/configuration suite, not an application or public API.

**Performance Goals**: Amortize context/startup over coherent batches and avoid mandatory strong per-batch review; no invented latency, savings or model-quality target.

**Constraints**: Exact owner selections and current-content approval gates; verify binding/effort support and permissions before assignment/dispatch; actual effort unknown stays unknown. Sequential writers, smallest sufficient REQUIRED checks, no fixed escalation ladder, no new memory adoption, no paid/live probes in this stage.

**Scale/Scope**: Shared task-generation/planner/coordinator integration, small coordination compatibility changes, runtime/configuration documentation and affected existing checks. Historical approved artifacts remain unchanged.

## Constitution Check

Pre-research gate: PASS against constitution 2.1.0 and approved scope. Post-design gate: PASS for planning; implementation acceptance and independent review are still pending.

| Principle | Design constraint and gate evidence |
| --- | --- |
| I Portable assets | Seed rubric is global and qualified; guidelines/evidence remain project-local. Examples are not guaranteed callable defaults. |
| II Evidence before guidance | Research distinguishes harnesses/versions and registry evidence from authenticated launch; attempts retain uncertainty and attribution. Raw outcomes never mutate guidance. |
| III Explicit authority | Approved spec digest is unchanged. Family and effort changes require usable permitted binding and owner selection; all existing source/overall approval gates remain. |
| IV Pragmatic verification | Extend existing seams with five bounded scenarios and a small negative acceptance fixture, not exhaustive benchmark infrastructure. Static results are not runtime-obedience proof. |
| V Safe execution | Per-task focused commits and separate evidence checkpoints remain; inspect failed run/invocation before repair; preserve valid work; final independent review remains required. |
| VI Compatibility/ownership | Both planning depths and documented legacy origins retain artifact/provenance gates. Existing inadequately contracted tasks return to producing review/approval, not fabricated migration. Coordination initialization/persistence stays mandatory; gotcha adoption stays separate. |

No constitution exception or approved-spec correction is required. Current class-based instructions are the implementation targets, not authority to override this approved batch-only change. Existing planning-stage bindings are not silently changed by a future implementation-task routing policy.

## Project Structure

### Documentation (this feature)

```text
specs/002-batch-routing-contracts/
├── spec.md                 # unchanged approved source
├── spec-approval.md        # unchanged digest-bound planning authority
├── research.md             # reused canonical evidence
├── plan.md                 # this stage
├── data-model.md           # compact operational entities, not a new storage schema
└── quickstart.md            # validation guide; tasks.md belongs to the next stage
```

No `contracts/` directory: this change has no new external API, command grammar or runtime interface; existing skills are the operational contract owners.

### Affected repository seams (future implementation)

```text
REQUIREMENTS.md
README.md
docs/pi-settings-sample.md
skills/planner/SKILL.md
skills/planner/references/
skills/task-generation/SKILL.md
skills/task-generation/scripts/
skills/coordinate-implementation/SKILL.md
skills/coordinate-implementation/scripts/
skills/memory-handling/references/project-coordination.md
scripts/check-planner-workflow.py
scripts/test-planner-workflow.py
scripts/check-task-commit-contract.py
scripts/test-task-commit-contract.py
```

**Structure Decision**: Reuse existing owners; add the compact seed rubric under `skills/coordinate-implementation/references/batch-routing.md` and link it from the coordinator plus relevant producer handoffs. Do not duplicate the rubric in each skill or add a second evidence store. During implementation inspect active downstream class wording/assertions in TinySpec, planning-brainstorming, architectural helper, approval/recovery and adopted-coordination consumers; change only wording that would enforce old implementation-task classes. Preserve unrelated stage-binding rules and historical approvals. Update any active class-bearing samples/templates only where they actually feed the changed seam; do not edit historical specs or generic SpecKit assets just because they exist.

## Architecture and Operational Contracts

### Producers: planner and task-generation (FR-001, FR-005)

Planner supplies approved scope, research constraints, applicable guidelines and verification needs through both TinySpec and Standard handoffs. Task-generation stops emitting mandatory Sonnet/Opus implementation-task labels, the 30% class share rule and same-class grouping. Tasks instead carry outcome, dependencies, files/interfaces, capabilities, shared context and stable task-local REQUIRED items in existing acceptance/observable/invariant/test fields. An optional residual-reasoning note informs later batch assessment, not a task assignment.

Use references such as `T001/V1`; each item states pass criterion, expected evidence, smallest sufficient check and any manual/permission gate. Optional checks stay distinct. A missing or ambiguous contract blocks dispatch and returns to the producing review/approval gate; do not add requirements retroactively to approved legacy tasks. Preserve task ordering, story acceptance, existing depth/approval recovery and separate source/tasks owners. Leave task breakdown to the tasks stage.

### Consumer: coordinator selection and dispatch (FR-001–FR-004, FR-006)

Build consecutive sequential batches from dependency-ready work, normally 2–5 tasks where context and permissions permit. Internal producer/consumer relationships and shared files remain together when verified sequentially. Split only for materially incompatible profiles, permissions, context or external prerequisites; never reorder to meet a count, force one agent per task, or run writers in parallel. Adapt existing local-execution eligibility from class match to owner-selected exact profile/context suitability without changing the existing strategy/authorization gates.

Assess residual reasoning, agentic/tool depth, weakest material verification blind spot, scope/coupling, recovery cost and relevant approved guidelines. Record ordered task IDs, assessment, applicable evidence or explicit none, proposed/selected binding and effort, independent rationale for each dimension and conditional repair option in the existing tracker/brief. Proposed is not selected or observed. Verify permissions, tool access, supported effort and actual callable binding through the installed runtime before assignment and again at dispatch; registry entries and suffix syntax alone are insufficient.

Seed examples are provisional: Luna/medium for shallow closed-design work with strong contracts and cheap recovery; Luna/max as a justified bounded experiment, never renamed medium; Sol/low or medium for justified stronger reasoning/tool depth; Astra/Terra only when permitted, supported and justified. Deep tool use, weak oracles, unresolved architecture, high failure cost and relevant repeated negative guidance defeat optimistic Luna routing. No benchmark-only eligibility rule or universal order. Relevant approved local guidance may override the prior; empty guidance invents no success history.

Dispatch supplies the whole union of REQUIRED task items, stable mappings, internal producer checks, baseline, owned paths, gates and per-task/evidence commit convention. Shared check output can cover multiple mapped items without duplicate execution. Return actual profile (or unknown), item-mapped results/evidence, files and ordered per-task checkpoint references.

### Acceptance and repair (FR-007, FR-008)

Before accepting a batch or releasing dependents, inspect every focused task commit/diff and cheaply validate item completeness, results, observables, scope and manual gates against concrete outputs. Confidence, a clean tree or a bare completion report is not proof. Missing, failed, contradictory, unauthorized or unrun REQUIRED evidence blocks acceptance. Passing contracts need no mandatory strong per-batch reviewer; one fresh final independent review over the complete committed range remains required.

On failure inspect child run, invocation, partial commits and check evidence first. Diagnose capability versus planning/spec gap, contract gap, batching error, environment/tooling, external dependency or unknown. Preserve valid task work and prior attempt evidence; determine affected dependencies and invalidated items. A targeted repair can raise effort, change model or both, only after supported binding/owner gates. Supply original assessment/profile, passed/failed items, current state and complete contract; rerun all invalidated verification, reuse only still-valid evidence. Unknown cause is not permission for blind restart; a repair success does not prove model-only attribution.

### Feedback integration (FR-009, FR-010)

Extend only profile/feedback compatibility wording in [project coordination contract](https://github.com/elsonidoq/skills/blob/5088b25877467887dd41c9547197c6da43b3c165/skills/memory-handling/references/project-coordination.md). Existing indexed run/task records hold each attempt's exact selected and observed profile, factors, contract strength, first/final outcome, diagnosis, evidence/checkpoint references and repair. Preserve accepted, partial, escalated and blocked attempts; do not infer incapacity from unavailable environments or generalize weak/invalidated successes. Reflection remains selective/index-first, with exact owner-approved candidate content and drift checks as the only guideline-write path. No new YAML schema, score, automatic learner or raw outcome promotion.

## Research Traceability and Capability Gates

Phase 0 reuses [research.md](research.md), particularly “Inspected representative signals and limits”, “Runtime and ownership findings”, and Decisions 1–4. Its benchmark compilation, Pi 0.87.1 documentation and pi-subagents 0.73.1 reference sufficiently support this process design; no internet refresh or raw CSV archive is necessary. Historical research stays discoverable beside the new canonical research in [docs index](../../docs/index.md). Both planner direct path and architectural helper resolve the same shared research contract; implementation must keep these consumers linked, not create rival sources.

| Supporting evidence / classification | Derived constraint | Observable implementation check |
| --- | --- | --- |
| Research representative rows; supplied evidence with harness/snapshot limitations | Qualified seed, independent effort rationale; no averaged score or universal ranking | Rubric inspection and Luna/max fixture retain max and uncertainty |
| Research runtime findings; documented runtime syntax vs support/callability distinction | Exact binding, supported effort and permission gates; observed unknown remains unknown | Missing support/unknown-effort fixture cannot claim a supported profile ran; live gate remains separate |
| Research ownership findings; local task/coordinator/memory contracts | Existing task fields, union in coordinator brief, existing run/task evidence | Two-task shared-check fixture retains both item mappings and checkpoint audit |
| Research Decisions 3–4; repository-derived decisions | No fixed ladder; passing Luna batch has no strong per-batch review | Five required scenarios, plus missing/contradictory evidence rejection |
| Empty project `memory/coordination/GUIDELINES.md`; local observation | Seed usable without invented project success; no gotcha association required here | Empty-guideline fixture and applicable approved-guideline override fixture |

Assumption to validate at implementation preflight: the selected deployment supports the requested binding/effort and exposes enough actual-profile evidence. If not, stop the affected dispatch or mark actual unknown honestly; do not infer capability from catalog output. No live invocation/comparison was performed here. New version-sensitive provider support uncertainty requires targeted refresh for the actual binding, not a network research expansion of this plan.

## Sequencing and Integration

1. Establish shared seed and task-item producer contracts, then adapt both planner handoffs; verify producers before consumers. Keep nearby shared-context edits consecutive, not a prescribed model class or quota.
2. Integrate coordinator assessment, profile preflight, batch union, implementer return and cheap acceptance. Keep selection and actual-dispatch wiring inspectable together.
3. Integrate diagnosed repair and existing coordination feedback compatibility, preserving initialization, selective retrieval, exact guideline approvals and separate task/evidence checkpoints.
4. Refresh affected static assertions/fixtures and lockstep runtime/settings/README guidance; run focused scenario and preservation checks before final independent review.

These are causal design boundaries, not numbered implementation tasks. All writers stay sequential; no parallel marker can bypass dependency/ownership constraints. Task-generation must give each resulting work unit its own verification and focused checkpoint, then the existing separate evidence checkpoint. Independent review of spec → plan → tasks and separate overall implementation approval precede execution.

## Verification Strategy

REQUIRED during implementation: establish a failing check for each changed behavior at its existing seam, then make it pass; demonstrate all five FR-011 scenarios, 100% mapped REQUIRED evidence for accepted examples, exact selected effort retention, environment non-attribution and approved-guideline override. Add a bounded two-task shared-check fixture with missing/contradictory evidence rejection, plus unsupported/unknown profile handling. Do not introduce an exhaustive family/effort matrix.

Reuse `skills/coordinate-implementation/scripts/test_batching_contract.py` and `test_intake_contract.py`, task-generation contract/order checks and planner checker/fixtures. Refresh old class/count assertions only where superseded; retain ordering, stage approvals, capability stops, per-task commits and final-review assertions. Run the existing task-commit checks when revised cross-contract wording touches their assertions, to detect accidental checkpoint weakening. Expected effort is focused existing assertions plus a small fixture set, not live benchmarking or new infrastructure.

Manual REQUIRED review follows source → item production → batch brief → actual selected dispatch arguments → returned evidence → acceptance → indexed feedback → guideline approval, including direct/helper planning and documented legacy recovery. Scripted fixtures show contract behavior, not unrestricted model obedience. Optional broader lint/regression is not a substitute for these checks. Any live/provider validation requires separate owner/capability permission; if required by the eventual approved tasks but unavailable, it remains NOT RUN/UNAVAILABLE and blocks affected acceptance.

Planning-stage checks: approved digest and link resolution, no template placeholders, FR-001–FR-011 coverage, constitution recheck, scoped diff and `git diff --check`. No implementation tests or live scenarios are claimed by this artifact.

## Compatibility, Security, Migration and Rollback

No runtime pins, stored history or old approvals are rewritten. Update active class-based implementation requirements and settings examples in lockstep; do not leave an unconditional override silently selecting a different binding from the batch decision. Preserve planning-depth choice, source approval provenance, historical recovery and separate independent reviewer selection. Existing approved tasks needing better contracts return to their producer gate with renewed affected approval.

Feedback stays inside the resolved current project, contains bounded references rather than raw logs, and excludes credentials, secrets and personal payloads. Required permissions/manual gates remain blocking. No deployment, push, paid operation, guideline mutation or irreversible action is authorized here.

Rollback is a scoped, authorized correction/revert of affected workflow changes with revalidation and renewed affected approvals, never automatic discard of task work or coordination evidence. Preserve prior attempts and checkpoint provenance even after repair or rollback.

## Complexity Tracking

No constitution violations or additional framework justified. Operational data model and quickstart are proportionate; no external contracts, new database or task list is produced in this stage.
