# Documentation Index

## Documentation Routing Guide

Use this table to find the canonical owner before reading or updating material
facts. Update the most specific owner, then its index link if discovery changes;
do not duplicate contracts or turn closeout into a repository-wide audit.

| Material change / information | Authoritative owner to read and update |
| --- | --- |
| Suite runtime prerequisites and saved planning-assignment requirements | [REQUIREMENTS.md](../REQUIREMENTS.md) |
| User-facing suite setup and workflow entry points | [README.md](../README.md) |
| Global repository policy and portability constraints | [AGENTS.md](../AGENTS.md) |
| Project development principles and constitution amendments | [Project Constitution](../.specify/memory/constitution.md) |
| A skill's operational contract | Its `skills/<name>/SKILL.md`; shared brainstorming and task semantics belong to the shared owners linked below |
| Planning depth assessment principles | [Spec-driven-development guidance](best_practices_spec_driven_development.md); planner assesses and the owner chooses |
| Pi configuration examples and attributed configuration decisions | [Pi settings sample](pi-settings-sample.md), including scope, rationale, provenance/date, verification and supersession status |
| Verified unresolved bug, risk or investigation | [GitHub Issues](https://github.com/elsonidoq/skills/issues), explicit target `github.com/elsonidoq/skills`, via `track-open-issue`; [original Markdown](open_issues.md) is history only |
| Approved requirement/design and acceptance criteria | Existing subject-specific plan and task artifacts linked below; do not create competing owners |
| Consequential decision records and accepted decision constraints | [Decision index](decisions/index.md) owns this repository's ADRs; [Save ADR](../skills/save-adr/SKILL.md) preserves decision status, provenance and supersession |
| Historical model-routing research and its applicability limits | [Model Family Routing Research](../specs/001-model-family-routing/research.md) and [Batch Routing Contracts Research](../specs/002-batch-routing-contracts/research.md) remain discoverable historical records; they are not current assignment policy. |
| Project-local explicit feedback guidance and selective history | [Project Coordination Memory](../skills/memory-handling/references/project-coordination.md); actual guidelines/evidence stay in each project-local store; this repository uses `memory/coordination/` |
| Mandatory retained-task commit/checkpoint policy | [Task Commit Contract](../skills/memory-handling/references/task-commit-contract.md); consumer role text links this single owner |
| Context-first implementation recovery | [Coordinator recovery contract](../skills/coordinate-implementation/SKILL.md#recover-context); summary/recent context then selective artifact/Git/check/runtime reconstruction, no automatic STATE writes |
| Completed changes, commit history and inventories | Git history; do not duplicate these as closeout summaries |
| Coordinate Implementation executable operation and focused Git safety | [Runtime operating guide](coordinate-implementation.md); optional explicit runtime setup, thin executable interface |
| Current task progress, historical SQLite and SDK interfaces | [Runtime schema owner](coordinate-implementation-schema.md) |
| Local read-only workflow monitor package preparation, launch, rollback, correction lookup, and HTTP boundary | [Workflow monitor README](../workflow_monitor/README.md) |

This repository's marked [Coherence adoption contract](../AGENTS.md) associates its
[gotcha-memory index](../memory/MEMORY.md) at `memory/`; it currently records no gotchas.
Coordination memory remains a separate project-local explicit-feedback store at
`memory/coordination/`; consult relevant existing guidance without auto-initialization. No
default suite-level database is created by adoption. The executable workflow has a
[separate schema owner](coordinate-implementation-schema.md) and thin executable interface;
adoption never initializes execution state in unrelated projects. The legacy port retains its own boundaries.

## Project Guidance

- [Project Constitution](../.specify/memory/constitution.md): Portable global assets, feedback-only coordination memory and current-content approval and pragmatic verification.
- [Initialize Coherence](../skills/initialize-coherence/SKILL.md): Proposal-first suite adoption/memory and bounded documentation structural readiness.
- [Save ADR](../skills/save-adr/SKILL.md): Canonical discovery, save, consultation and propagation contract for consequential decisions; before affected work, read the selected project's whole decision index and relevant accepted records. This repository's owner-selected store is [docs/decisions/](decisions/index.md); other projects retain their own routing.
- [Planner](../skills/planner/SKILL.md): Single coordination entry point, scope assessment, user-selected depth, fresh delegated artifact creation, bounded mechanical correction, complete approval briefs and handoff.
- [Parsimony and Actionable Checks](../skills/planner/references/parsimony.md): Canonical planning/review policy and managed project-copy fragment; adoption/refresh belongs to initialize-coherence.
- [TinySpec](../skills/tiny-spec/SKILL.md): Compact what/how source with separate tasks.
- [Task Generation](../skills/task-generation/SKILL.md): Shared dependency-aware task standards and validation.
- [Planning Brainstorming](../skills/planning-brainstorming/SKILL.md): Shared bounded owner dialogue and read-only preselection mode.
- [Executable implementation entry](../skills/coordinate-implementation/SKILL.md): Thin CLI/interactive facade; sequential runtime uses selected executors, actual project checks/manual gates, focused commits and independent review. [Operating](coordinate-implementation.md) and [schema](coordinate-implementation-schema.md) owners cover actual interfaces/cutover/rollback.
- [Saved planning assignments](../skills/planner/references/model-assignments.json): Canonical owner-selected bindings for planning roles. Each assigned operation carries its exact saved binding unchanged in its bounded brief and dispatch; missing, malformed, unsupported or unavailable assignments stop only that operation for owner correction.
- [Approval and Recovery](../skills/planner/references/approval-and-recovery.md): Current-content approvals and legacy repair checkpoints.
- [Project Coordination Memory](../skills/memory-handling/references/project-coordination.md): Relevant existing guidance, selective history and explicit future-directed user feedback; no routine persistence or inferred learning.
- [Task Commit Contract](../skills/memory-handling/references/task-commit-contract.md): Mandatory focused checkpoints for authorized retained tasks, coordinator recovery/fresh-agent boundaries, and truthful static/Git-fixture limits.
- [Early Risk Reduction](../skills/planner/references/early-risk-reduction.md): Selective early tested executable proofs, explicit production consumption, evidence lifetime and disproof replanning.
- [Dependency Research](../skills/planner/references/dependency-research.md): Shared repository-first evidence, proportional reuse/version refresh, discoverable technical ownership and bounded persistence for TinySpec and Standard, including direct/standalone entry.
- [Best Practices for Spec-Driven Development](best_practices_spec_driven_development.md): Evidence-backed specifications and qualitative depth assessment.
- [Pi Settings Sample](pi-settings-sample.md): Configuration examples and attributed, verified configuration decisions.

## Implementation Plans

- [Read-only workflow monitor — revised proposal](../specs/004-workflow-monitor/spec.md): proposed [architecture](../specs/004-workflow-monitor/plan.md), [script/dependency evidence](../specs/004-workflow-monitor/research.md), [data model](../specs/004-workflow-monitor/data-model.md), [contracts](../specs/004-workflow-monitor/contracts/README.md), [tasks](../specs/004-workflow-monitor/tasks.md) and [operator guide](../specs/004-workflow-monitor/quickstart.md). Sixteen bounded tasks: accepted T001–T006 recording foundation before the T007–T016 application build, usable viewer at T010 before later genuine work; future Terra/medium binding remains unresolved. One graph includes reviewer/fixing-agent/rereviewer executions and same-build retrospective/live history. Artifact revision only; recording/review-range implementation, setup and launch require separate approval. Historical approvals are not renewed.
- [Coordinate Implementation executable workflow — Standard specification](../specs/003-coordinate-workflow/spec.md) and [architecture plan](../specs/003-coordinate-workflow/plan.md): [canonical research](../specs/003-coordinate-workflow/research.md), [data model](../specs/003-coordinate-workflow/data-model.md), [contracts](../specs/003-coordinate-workflow/contracts/README.md) and [validation guide](../specs/003-coordinate-workflow/quickstart.md). Later owner direction authorizes scoped implementation; historical planning-only records retain their original provenance. T001 originally delivered the durable foundation; T002–T009 add SDK/task/interaction execution, approved policy integration and the thin executable entry. [Operating](coordinate-implementation.md) and [schema](coordinate-implementation-schema.md) owners describe current delivered behavior; final migration acceptance still needs independent full-range review.
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

## Decision Records

- [Decision index](decisions/index.md): Canonical project ADR owner; maps each direct decision record and its status. Owner approved this bounded store/routing initialization through `ask_user` on 2026-10-21; existing Coherence adoption, memory and SpecKit assets are unchanged. Decision acceptance does not authorize implementation.

## Registers

- [GitHub Issues](https://github.com/elsonidoq/skills/issues): Sole canonical active unresolved-work tracker, target `github.com/elsonidoq/skills`, via `track-open-issue`; missing capability or write authority defers a candidate in the response, never to a persistent local fallback.
- [Historical Open Issues](open_issues.md): Original entries preserved verbatim, nonauthoritative for current state. Actual historical migration is **NOT RUN**; future import requires separately authorized apply, reviewed preview, OI-4/#2 mapping choice and independent full readback. No mapping or completed migration is implied by this routing switch.
- [Import Open Issues](../skills/import-open-issues/SKILL.md): Reusable default offline preview and separately gated historical import; routine active tracking belongs to `track-open-issue`.
