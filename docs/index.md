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
| EPIC admission/sizing principles | [Spec-driven-development guidance](best_practices_spec_driven_development.md); adapters reference it rather than copy criteria |
| Pi configuration examples and attributed configuration decisions | [Pi settings sample](pi-settings-sample.md), including scope, rationale, provenance/date, verification and supersession status |
| Verified unresolved bug, risk or investigation | [Open Issues](open_issues.md), via `track-open-issue` |
| Approved requirement/design and acceptance criteria | Existing subject-specific plan and task artifacts linked below; do not create competing owners |
| Completed changes, commit history and inventories | Git history; do not duplicate these as closeout summaries |

This configuration suite has no declared project-memory adoption contract or
suite-level database/schema owner. Do not initialize either merely for closeout;
unrelated projects and the legacy port keep their own documentation boundaries.

## Project Guidance

- [Requirements Manager](../skills/requirements-manager/SKILL.md): Plan-free, reviewed direct-requirement task production and coordinator handoff.
- [Task Generation](../skills/task-generation/SKILL.md): Shared dependency-aware task standards and validation.
- [EPIC Brainstorming](../skills/epic-brainstorming/SKILL.md): Shared bounded owner-decision gate and application mechanism.
- [Best Practices for Spec-Driven Development](best_practices_spec_driven_development.md): Guidance for writing evidence-backed specifications and deciding when an epic pipeline is warranted.
- [Pi Settings Sample](pi-settings-sample.md): Configuration examples and attributed, verified configuration decisions.

## Implementation Plans

- [Requirements Manager](plans/requirements-manager.md): Approved shared workflow primitives, restored EPIC pipeline, origin-neutral coordination, and regression coverage.
- [Requirements Manager Tasks](plans/requirements-manager-tasks.md): Reviewed, reconciled implementation scope and authorization.
- [Requirements Manager Execution](plans/requirements-manager-execution.md): Sequential execution tracker, per-task verification, commits, and final review evidence.
- [Requirements Manager Coverage Baseline](plans/requirements-manager-coverage.md): Source-derived requirement, historical behavior, and capability/fallback inventory for implementation verification.

## Registers

- [Open Issues](open_issues.md): Canonical local register for verified unresolved bugs, risks, shortcuts, missing capabilities, and investigations.
