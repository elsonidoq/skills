---
name: epics-manager
description: Use when preparing or resuming a feature brief that needs specification, planning, tasking, and review before implementation.
---

# Epics Manager

Turn an owner-selected brief into reviewed implementation artifacts. This workflow
prepares work; it does not implement product code.

## Inputs and Provenance

Require a brief or source artifact and an unambiguous target within it. Resolve the
target from explicit headings, metadata, or owner input without assuming numbered
epics, a bundle filename, or a custom state directory. Record:

- Source path and selected section.
- Governing repository instructions and principles.
- Settled decisions, acceptance criteria, exclusions, dependencies, and cited
  sources.
- Existing spec, plan, tasks, and review artifacts linked to that source.

Re-read source bounds and links whenever resuming. If provenance is ambiguous,
pause for the owner instead of attaching work to a likely-looking feature.

## Detect SpecKit

Before each stage, inspect the project's command registry and files for the
corresponding SpecKit capability and its instructions, templates, and prerequisite
scripts. Conventional command names and directory layouts are hints, not contracts.
Use only commands and assets observed in the current project.

Report capability checks in this form:

```text
Capability: constitution | specification | clarification | planning | tasks | analysis | implementation
Status: AVAILABLE | UNAVAILABLE
Evidence: [command or path found]
Fallback: [generic artifact operation, or blocked behavior]
```

When a stage command is available, follow its current instructions and verify its
outputs. When unavailable, create or update the equivalent Markdown artifact using
the contracts below. Do not simulate a slash command in a shell, install tooling,
or initialize/overwrite project assets without owner authorization. Analysis that
depends on an unavailable project command must be reported as `UNAVAILABLE`; use a
manual cross-artifact review as the fallback, not as evidence that the command ran.

## Workflow

Run the earliest incomplete or invalid stage:

1. **Principles preflight:** Read the project's governing principles if present.
   If a detected SpecKit workflow requires a constitution and it is missing or
   still template text, ask the owner for the necessary project-specific principles
   and use the detected constitution capability. If that capability is unavailable,
   record the blocker; do not invent policy.
2. **Brief readiness:** Confirm the target has an outcome, users, scope, exclusions,
   acceptance criteria, dependencies, and no unresolved direction that would change
   the feature materially. Use a short owner discussion only for genuine product or
   architectural choices.
3. **Specification:** Before producing the spec, read the global configuration
   repository's [`docs/best_practices_spec_driven_development.md`](../../docs/best_practices_spec_driven_development.md).
   If it is unavailable, stop and report an incomplete global configuration
   installation. Apply **Designing AI-Friendly Specifications for Solo Builders**:
   keep goals outcome-oriented, make inputs/outputs and deterministic business rules
   explicit where relevant, include exclusions, and avoid implementation detail
   unless it is a settled constraint. Apply **Epic Sizing: When the Pipeline Earns
   Its Overhead** before continuing the pipeline.
4. **Clarification:** After specification, run the detected clarification stage.
   If unavailable, perform a generic ambiguity review against the source, acceptance
   criteria, exclusions, dependencies, and governing principles. Resolve
   mechanically answerable gaps; send material choices to the owner.
5. **Specification approval:** Present the specification and clarification results
   to the owner. Record explicit specification approval in a project-defined
   decision or progress artifact, or in the specification when none exists. Do not
   begin planning without it.
6. **Plan:** Review the spec, fix non-material defects, then produce architecture,
   contracts, sequencing, risks, and verification. Use
   `delegating-architectural-planning` when the approved work calls for delegated
   architectural decomposition.
7. **Tasks:** Derive dependency-aware, independently verifiable tasks from the plan.
   Each task identifies its outcome, prerequisites, likely files/interfaces,
   acceptance evidence, and capability needs. Do not encode fixed agent or model
   names.
8. **Overall review:** Check source -> spec -> plan -> tasks traceability,
   contradictions, omissions, dependency order, integration coverage, exclusions,
   and governing principles. Use detected SpecKit analysis when available and
   manually inspect its evidence; otherwise perform the same review directly.
9. **Overall review approval:** Present the reviewed artifact set and unresolved
   deferrals to the owner. Record explicit overall review approval in a
   project-defined decision or progress artifact, or in the reviewed artifacts when
   none exists. Do not hand off implementation without it.
10. **Handoff:** Verify both recorded approvals apply to the current artifacts,
    re-run applicable prerequisite or artifact checks, and pass the reviewed set to
    `coordinate-implementation`.

## Decisions and Corrections

Agents may resolve task organization, filenames, internal naming, and mechanically
verifiable defects. Ask the owner only when alternatives materially change product
scope, architecture, privacy, permissions, irreversible behavior, cost, or a settled
requirement. Apply no speculative answer merely to advance the workflow.

Record each owner decision and approval with its stage and affected artifact paths
in an existing project-defined decision or progress artifact when one is documented.
Otherwise keep it in the affected spec or plan. Do not create a global state schema
or require a particular progress filename.

## State and Resume

Artifacts are the default durable state. Use a project state mechanism only when
the repository documents one; validate its schema and artifact links before trusting
it. On resume:

1. Verify source and artifact paths still exist.
2. Verify recorded specification approval and overall review approval apply to the
   current artifact revisions. Missing or stale approval returns to that gate.
3. Validate stage outputs and integrations rather than trusting a `done` label.
4. Continue from the earliest stale, missing, or inconsistent artifact.

## Ready for Implementation

Report readiness only when the spec, plan, and tasks exist, provenance is clear,
dependencies are represented, specification approval and overall review approval are
recorded for the current artifacts, other owner gates are resolved or explicitly
deferred, and the overall review has evidence. List artifact paths, capability
checks, checks run, and unavailable behavior. Artifact readiness does not mean
implementation or feature acceptance is complete.
