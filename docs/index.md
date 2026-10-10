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
| Required project-local coordination guidelines, selective history and reviewed feedback | [Project Coordination Memory](../skills/memory-handling/references/project-coordination.md); actual guidelines/evidence stay in each project-local store; this repository uses `memory/coordination/` |
| Mandatory retained-task commit/checkpoint policy | [Task Commit Contract](../skills/memory-handling/references/task-commit-contract.md); consumer role text links this single owner |
| Brief project-owned current state and implementation recovery | [Coordinator snapshot/recovery contract](../skills/coordinate-implementation/SKILL.md#brief-current-state-and-recovery) owns small ephemeral recovery bookmarks, material-change writes and no state-specific commit ceremony; worker checkpoints remain unchanged. This project's snapshot is root [STATE.md](../STATE.md), not a history/authorization owner |
| Completed changes, commit history and inventories | Git history; do not duplicate these as closeout summaries |

This repository's marked [Coherence adoption contract](../AGENTS.md) associates its
[gotcha-memory index](../memory/MEMORY.md) at `memory/`; it currently records no gotchas.
Coordination memory remains a separate mandatory project-local store at
`memory/coordination/`; initialize its missing files through the shared contract. No
suite-level persistent database/schema owner is declared. Unrelated projects and the
legacy port retain their own documentation and memory boundaries.

## Project Guidance

- [Project Constitution](../.specify/memory/constitution.md): Portable global assets, mandatory project-local coordination persistence, exact guideline approval and pragmatic verification.
- [Initialize Coherence](../skills/initialize-coherence/SKILL.md): Proposal-first suite adoption/memory and bounded documentation structural readiness.
- [Planner](../skills/planner/SKILL.md): Single entry point, scope assessment, user-selected depth, approvals and handoff.
- [TinySpec](../skills/tiny-spec/SKILL.md): Compact what/how source with separate tasks.
- [Task Generation](../skills/task-generation/SKILL.md): Shared dependency-aware task standards and validation.
- [Planning Brainstorming](../skills/planning-brainstorming/SKILL.md): Shared bounded owner dialogue and read-only preselection mode.
- [Coordinator batch approval](../skills/coordinate-implementation/SKILL.md#build-the-execution-graph): Complete table with batch descriptions and exact model/effort requires explicit routing approval before implementation; unchanged verified approval is reusable, not a universal profile default.
- [Qualified routing rubric](../skills/coordinate-implementation/references/batch-routing.md): Single six-factor planning/advisory and implementation selection prior; Standard `plan_create` requires Sol/medium for its entire direct/helper pass, with no unavailable-profile substitution. Implementation-only batching rules are not planning prerequisites.
- [Approval and Recovery](../skills/planner/references/approval-and-recovery.md): Current-content approvals and legacy repair checkpoints.
- [Project Coordination Memory](../skills/memory-handling/references/project-coordination.md): Mandatory project-local files automatically initialized/notified/committed before choice, separate indexed evidence, selective reads and approval-controlled learned-guideline changes.
- [Task Commit Contract](../skills/memory-handling/references/task-commit-contract.md): Mandatory focused checkpoints for authorized retained tasks, coordinator recovery/fresh-agent boundaries, and truthful static/Git-fixture limits.
- [Early Risk Reduction](../skills/planner/references/early-risk-reduction.md): Selective early tested executable proofs, explicit production consumption, evidence lifetime and disproof replanning.
- [Dependency Research](../skills/planner/references/dependency-research.md): Shared repository-first evidence, proportional reuse/version refresh, discoverable technical ownership and bounded persistence for TinySpec and Standard, including direct/standalone entry.
- [Best Practices for Spec-Driven Development](best_practices_spec_driven_development.md): Evidence-backed specifications and qualitative depth assessment.
- [Pi Settings Sample](pi-settings-sample.md): Configuration examples and attributed, verified configuration decisions.

## Implementation Plans

- [Plans directory index](plans/index.md): Direct plan records and the nested review index.
- [Planner delegation and complete approval briefs — TinySpec](plans/planner-delegation-approval-tinyspec.md): delegated creation/correction and complete scope/stage/task briefs without added gates; content approval pending.
- [Planner delegation and complete approval briefs — tasks](plans/planner-delegation-approval-tasks.md): three causal units for contracts, static/synthetic regressions and truthful documentation; planner review/combined approval pending.
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
