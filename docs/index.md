# Documentation Index

## Documentation Routing Guide

Use this table to find the canonical owner before reading or updating material
facts. Update the most specific owner, then its index link if discovery changes;
do not duplicate contracts or turn closeout into a repository-wide audit.

| Material change / information | Authoritative owner to read and update |
| --- | --- |
| Suite runtime prerequisites and model/effort routing requirements | [REQUIREMENTS.md](../REQUIREMENTS.md) |
| User-facing suite setup and workflow entry points | [README.md](../README.md) |
| Global repository policy and portability constraints | [AGENTS.md](../AGENTS.md) |
| Project development principles and constitution amendments | [Project Constitution](../.specify/memory/constitution.md) |
| A skill's operational contract | Its `skills/<name>/SKILL.md`; shared brainstorming and task semantics belong to the shared owners linked below |
| Planning depth assessment principles | [Spec-driven-development guidance](best_practices_spec_driven_development.md); planner assesses and the owner chooses |
| Pi configuration examples and attributed configuration decisions | [Pi settings sample](pi-settings-sample.md), including scope, rationale, provenance/date, verification and supersession status |
| Verified unresolved bug, risk or investigation | [Open Issues](open_issues.md), via `track-open-issue` |
| Approved requirement/design and acceptance criteria | Existing subject-specific plan and task artifacts linked below; do not create competing owners |
| Model-routing benchmark evidence and its applicability limits | [Model Family Routing Research](../specs/001-model-family-routing/research.md); keep the source record discoverable as project guidelines evolve. [Batch Routing Contracts Research](../specs/002-batch-routing-contracts/research.md) owns the newer batch-only seed evidence and runtime limitations |
| Project-local explicit feedback guidance and selective history | [Project Coordination Memory](../skills/memory-handling/references/project-coordination.md); actual guidelines/evidence stay in each project-local store; this repository uses `memory/coordination/` |
| Mandatory retained-task commit/checkpoint policy | [Task Commit Contract](../skills/memory-handling/references/task-commit-contract.md); consumer role text links this single owner |
| Context-first implementation recovery | [Coordinator recovery contract](../skills/coordinate-implementation/SKILL.md#recover-context); summary/recent context then selective artifact/Git/check/runtime reconstruction, no automatic STATE writes |
| Completed changes, commit history and inventories | Git history; do not duplicate these as closeout summaries |
| Opt-in Coordinate Implementation runtime operation, custody and supported limits | [Runtime operating guide](coordinate-implementation.md); legacy remains default |
| Delivered runtime SQLite and packaged versioned contract schemas | [Runtime schema owner](coordinate-implementation-schema.md) |

This repository's marked [Coherence adoption contract](../AGENTS.md) associates its
[gotcha-memory index](../memory/MEMORY.md) at `memory/`; it currently records no gotchas.
Coordination memory remains a separate project-local explicit-feedback store at
`memory/coordination/`; consult relevant existing guidance without auto-initialization. No
default suite-level database is created by adoption. The opt-in workflow foundation has a
[separate schema owner](coordinate-implementation-schema.md); it does not replace the legacy
entry or initialize state in unrelated projects. The legacy port retains its own boundaries.

## Project Guidance

- [Project Constitution](../.specify/memory/constitution.md): Portable global assets, feedback-only coordination memory and current-content approval and pragmatic verification.
- [Initialize Coherence](../skills/initialize-coherence/SKILL.md): Proposal-first suite adoption/memory and bounded documentation structural readiness.
- [Planner](../skills/planner/SKILL.md): Single coordination entry point, scope assessment, user-selected depth, fresh delegated artifact creation, bounded mechanical correction, complete approval briefs and handoff.
- [TinySpec](../skills/tiny-spec/SKILL.md): Compact what/how source with separate tasks.
- [Task Generation](../skills/task-generation/SKILL.md): Shared dependency-aware task standards and validation.
- [Planning Brainstorming](../skills/planning-brainstorming/SKILL.md): Shared bounded owner dialogue and read-only preselection mode.
- [Coordinator batch approval](../skills/coordinate-implementation/SKILL.md#prepare-approved-execution): Complete table with batch descriptions and exact model/effort requires explicit routing approval before implementation; unchanged verified approval is reusable, not a universal profile default.
- [Qualified routing rubric](../skills/planner/references/profile-selection.md): Canonical first-proposal and six-factor planning/advisory selection prior: demands/oracles → material evidence or explicit non-reliance → independent family/effort comparison → proposal; suitability remains separate from authenticated/runtime readiness and observed launch. Standard `plan_create` requires Sol/medium for its entire delegated non-helper/helper pass, with no unavailable-profile substitution. Implementation-only batching rules are not planning prerequisites.
- [Approval and Recovery](../skills/planner/references/approval-and-recovery.md): Current-content approvals and legacy repair checkpoints.
- [Project Coordination Memory](../skills/memory-handling/references/project-coordination.md): Relevant existing guidance, selective history and explicit future-directed user feedback; no routine persistence or inferred learning.
- [Task Commit Contract](../skills/memory-handling/references/task-commit-contract.md): Mandatory focused checkpoints for authorized retained tasks, coordinator recovery/fresh-agent boundaries, and truthful static/Git-fixture limits.
- [Early Risk Reduction](../skills/planner/references/early-risk-reduction.md): Selective early tested executable proofs, explicit production consumption, evidence lifetime and disproof replanning.
- [Dependency Research](../skills/planner/references/dependency-research.md): Shared repository-first evidence, proportional reuse/version refresh, discoverable technical ownership and bounded persistence for TinySpec and Standard, including direct/standalone entry.
- [Best Practices for Spec-Driven Development](best_practices_spec_driven_development.md): Evidence-backed specifications and qualitative depth assessment.
- [Pi Settings Sample](pi-settings-sample.md): Configuration examples and attributed, verified configuration decisions.

## Implementation Plans

- [Coordinate Implementation executable workflow — Standard specification](../specs/003-coordinate-workflow/spec.md) and [architecture plan](../specs/003-coordinate-workflow/plan.md): [canonical research](../specs/003-coordinate-workflow/research.md), [data model](../specs/003-coordinate-workflow/data-model.md), [contracts](../specs/003-coordinate-workflow/contracts/README.md) and [validation guide](../specs/003-coordinate-workflow/quickstart.md). Later owner direction authorizes scoped implementation; historical planning-only records retain their original provenance. T001 delivers only the [opt-in durable foundation](coordinate-implementation.md) and [schema owner](coordinate-implementation-schema.md); legacy remains default and SDK/task execution/policy cutover are not yet delivered.
- [Plans directory index](plans/index.md): Direct plan records and the nested review index.
- [Pragmatic planning — TinySpec](plans/pragmatic-planning-tinyspec.md): outcome-oriented decomposition, proportional proof and tagged informational prototypes; exact-content approval in [review](plans/reviews/pragmatic-planning-review.md).
- [Pragmatic planning — tasks](plans/pragmatic-planning-tasks.md): one coherent contract/regression/operative-doc delivery; A1–A6 REQUIRED evidence and gates preserved, execution-profile selection and independent final review remain required.
- [Planner delegation and complete approval briefs — TinySpec](plans/planner-delegation-approval-tinyspec.md): delegated creation/correction and complete scope/stage/task briefs; current-content owner approval and execution evidence in [run SUMMARY](../memory/coordination/evidence/planner-delegation-approval/SUMMARY.md), independent final review accepted within documented offline limits.
- [Planner delegation and complete approval briefs — tasks](plans/planner-delegation-approval-tasks.md): three approved dependency-ordered contract, regression and documentation units; checkpoints and REQUIRED dispositions in the linked source's run evidence, not historical pending labels.
- [Mandatory Task Commits — TinySpec](plans/mandatory-task-commits-tinyspec.md): Authoritative pragmatic checkpoint scope and A1–A7 acceptance; no runtime extension gate.
- [Mandatory Task Commits — Tasks](plans/mandatory-task-commits-tasks.md): Separate dependency-aware task contracts derived from the TinySpec.
- [Mandatory Task Commits — Planning Review](plans/reviews/mandatory-task-commits-planning-review.md): Exact source/task approval identities and owner authorization.
- [Mandatory Task Commits — Execution](plans/mandatory-task-commits-execution.md): Execution checkpoint and recovery evidence; final acceptance links to the independent review.
- [Mandatory Task Commits — Final Review](plans/reviews/mandatory-task-commits-final-review.md): Independent finding/disposition, RF001 correction and accepted targeted recheck; validation limits.
- [Project Coordination Memory Source](plans/project-coordination-memory.md): A1–A12 generic support and preservation bounds; approval is recorded separately.
- [Project Coordination Memory Tasks](plans/project-coordination-memory-tasks.md): Sequential contract, consumer, assurance and documentation work.
- [Project Coordination Memory Execution](plans/project-coordination-memory-execution.md): Current-content approval, per-task evidence and independent final review status.
- [Coherence Initialization](plans/coherence-initialization.md): Approved source and original behavior constraints for unified onboarding.
- [Coherence Initialization Tasks](plans/coherence-initialization-tasks.md): Source-first sequential implementation and acceptance contracts.
- [Coherence Planning Review](plans/reviews/coherence-planning-review.md): Digest-bound combined source/task/scope approval and execution limits.
- [Coherence Initialization Execution](plans/coherence-initialization-execution.md): Authorized bounds, per-task verification/commits and independent review status.
- [Planner Refactor](plans/planner-refactor.md): Approved architecture and source-first preservation ledger.
- [Planner Regression](plans/planner-regression.md): Deterministic and live scenario strategy, evidence and limitations.
- [Library Best-Practices Research](plans/library-best-practices-research.md): Approved shared dependency-evidence source (R1–R6).
- [Library Best-Practices Research Tasks](plans/library-best-practices-research-tasks.md): Sequential contract, integration, regression and documentation tasks.
- [Library Best-Practices Research Execution](plans/library-best-practices-research-execution.md): Hash-bound authority, verified task evidence and pending independent review.
- [Planner Approval UX](plans/planner-approval-ux.md): Owner-observed brief/continuation failures, approved correction and regression evidence.
- [Planner Astra Initial Review](plans/reviews/planner-astra-initial-review.md): Independent implementation findings, subsequently corrected.
- [Planner Astra Final Recheck](plans/reviews/planner-astra-final-recheck.md): Accepted targeted corrections; live-validation limits remain explicit.

The following records describe the historical pre-refactor implementation and approvals;
their manager names are not current entry points:

- [Requirements Manager](plans/requirements-manager.md): Approved shared workflow primitives, restored EPIC pipeline, origin-neutral coordination, and regression coverage.
- [Requirements Manager Tasks](plans/requirements-manager-tasks.md): Reviewed, reconciled implementation scope and authorization.
- [Requirements Manager Execution](plans/requirements-manager-execution.md): Sequential execution tracker, per-task verification, commits, and final review evidence.
- [Requirements Manager Coverage Baseline](plans/requirements-manager-coverage.md): Source-derived requirement, historical behavior, and capability/fallback inventory for implementation verification.

## Registers

- [Open Issues](open_issues.md): Canonical local register for verified unresolved bugs, risks, shortcuts, missing capabilities, and investigations.
