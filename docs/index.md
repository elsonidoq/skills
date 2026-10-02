# Documentation Index

## Documentation Routing Guide

Use this table to find the canonical owner before reading or updating material
facts. Update the most specific owner, then its index link if discovery changes;
do not duplicate contracts or turn closeout into a repository-wide audit.

| Material change / information | Authoritative owner to read and update |
| --- | --- |
| Suite runtime prerequisites and model-class configuration requirements | [REQUIREMENTS.md](../REQUIREMENTS.md) |
| User-facing suite setup and workflow entry points | [README.md](../README.md) |
| Global repository policy and portability constraints | [AGENTS.md](../AGENTS.md) |
| A skill's operational contract | Its `skills/<name>/SKILL.md`; shared brainstorming and task semantics belong to the shared owners linked below |
| Planning depth assessment principles | [Spec-driven-development guidance](best_practices_spec_driven_development.md); planner assesses and the owner chooses |
| Pi configuration examples and attributed configuration decisions | [Pi settings sample](pi-settings-sample.md), including scope, rationale, provenance/date, verification and supersession status |
| Verified unresolved bug, risk or investigation | [Open Issues](open_issues.md), via `track-open-issue` |
| Approved requirement/design and acceptance criteria | Existing subject-specific plan and task artifacts linked below; do not create competing owners |
| Completed changes, commit history and inventories | Git history; do not duplicate these as closeout summaries |

This configuration suite has no declared project-memory adoption contract or
suite-level database/schema owner. Do not initialize either merely for closeout;
unrelated projects and the legacy port keep their own documentation boundaries.

## Project Guidance

- [Initialize Coherence](../skills/initialize-coherence/SKILL.md): Proposal-first suite adoption/memory and bounded documentation structural readiness.
- [Planner](../skills/planner/SKILL.md): Single entry point, scope assessment, user-selected depth, approvals and handoff.
- [TinySpec](../skills/tiny-spec/SKILL.md): Compact what/how source with separate tasks.
- [Task Generation](../skills/task-generation/SKILL.md): Shared dependency-aware task standards and validation.
- [Planning Brainstorming](../skills/planning-brainstorming/SKILL.md): Shared bounded owner dialogue and read-only preselection mode.
- [Approval and Recovery](../skills/planner/references/approval-and-recovery.md): Current-content approvals and legacy repair checkpoints.
- [Best Practices for Spec-Driven Development](best_practices_spec_driven_development.md): Evidence-backed specifications and qualitative depth assessment.
- [Pi Settings Sample](pi-settings-sample.md): Configuration examples and attributed, verified configuration decisions.

## Implementation Plans

- [Coherence Initialization](plans/coherence-initialization.md): Approved source and original behavior constraints for unified onboarding.
- [Coherence Initialization Tasks](plans/coherence-initialization-tasks.md): Source-first sequential implementation and acceptance contracts.
- [Coherence Planning Review](plans/reviews/coherence-planning-review.md): Digest-bound combined source/task/scope approval and execution limits.
- [Coherence Initialization Execution](plans/coherence-initialization-execution.md): Authorized bounds, per-task verification/commits and independent review status.
- [Planner Refactor](plans/planner-refactor.md): Approved architecture and source-first preservation ledger.
- [Planner Regression](plans/planner-regression.md): Deterministic and live scenario strategy, evidence and limitations.
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
