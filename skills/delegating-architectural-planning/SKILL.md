---
name: delegating-architectural-planning
description: Use when an owner-approved specification needs delegated architectural planning through an installed SpecKit planning capability.
---

# Delegating Architectural Planning

Delegate only after the owner approves the specification and asks for a plan.
This skill requires the project's installed SpecKit planning capability. The
planner owns architectural decomposition, not implementation or product scope.

## Preflight

Verify and provide:

- The approved specification and evidence of approval.
- Repository instructions, governing principles, relevant contracts, and the
  intended plan location, using paths that exist. Load the project memory store
  per the `memory-handling` skill and include verified trigger-first gotchas as
  constraints for the planner.
- Existing architecture decisions and upstream/downstream dependencies.
- The planner's write scope and prohibited operations, including separately authorized
  canonical research-document and necessary discovery-link destinations/allowed changes
  in addition to detected SpecKit artifacts when durable guidance is required.
- Shared dependency research triggers, local/version findings, reuse/skip rationale,
  inspected supporting spans, usable permitted capability evidence and outstanding gaps.
- The detected SpecKit planning command or skill, its invocation instructions,
  template, prerequisite scripts, and expected output paths.

Read and apply the shared [dependency research contract](../planner/references/dependency-research.md)
before consequential architecture/plan decisions; verify it is readable or stop with
a missing-install report. Discover repository guidance/dependency versions first;
reuse adequate applicable evidence or refresh only deficient version-sensitive portions.
Complete required research and authorized durable guidance before readiness, tracing
documented recommendations/local evidence → plan constraints → observable verification;
label repository-derived decisions/rationale and assumptions with defined checks.

Standalone entry verifies equivalent Standard planning/preparation authority under the
approved-specification/plan-request prerequisites, research availability and bounded
canonical-owner/discovery writes; do not infer permission from invocation. Missing
required tools, usable sources, version evidence or write authority stops affected
design and returns exact missing evidence, affected decisions and needed authority to
planner (or the standalone owner). No recollection fallback or automatic deferral:
planner/owner must explicitly resolve any bounded deferral with impact, allowed bounds
and outstanding validation. The standalone local fallback cannot bypass required research.
Research-driven approved-specification changes require renewed approval through the
existing owner gate, including standalone entry; return them rather than assume approval.

Verify that the planning capability is available to the planner in the
delegated context. If it is missing or cannot be used there, report
`SpecKit planning: UNAVAILABLE` and stop; do not write a generic plan or
claim that the planning stage ran.

Inspect the runtime for an allowed delegation tool (the `subagent` tool from the
`pi-subagents` package is the suite's pinned delegation mechanism; see the global
configuration repository's `REQUIREMENTS.md`) and configured planning-capable
agents. For independently authorized standalone selection, use the
[qualified seed rubric](../coordinate-implementation/references/batch-routing.md): assess all six
applicable factors, including the weakest verification blind spot; justify family and supported
effort independently and obtain one exact owner-selected profile. Verify permissions, tools,
callable binding and supported effort at assignment and dispatch. Copy the selected binding/effort
unchanged into the invocation; missing selection/support or a settings/default override stops,
never silently substitutes. Record proposed, selected and observed separately; unknown actual
model or effort stays unknown. Implementation-only batching, task-count and REQUIRED-item rules
are not planning prerequisites. This standalone selection cannot override a manager-governed
Standard invocation's Sol/medium exception. Never invent an agent, model, command, or
configuration. If delegation is unavailable, state
`Architectural delegation: UNAVAILABLE` and offer to run the installed SpecKit
planning stage locally with a separate review pass.

Brief the planner to follow the detected SpecKit planning instructions and
verify the generated artifacts. If the capability is exposed as
`/speckit.plan`, use that installed capability through its supported runtime
interface; do not simulate the slash command in a shell. The plan requirements
below supplement the generated artifacts and do not replace the SpecKit stage.

## Planner Standard adapter contract

When `planner` invokes this helper from its Standard `plan_create` stage, it is not a standalone
fallback. Select the Sol family with exactly **medium** supported effort for the ENTIRE
Standard direct/helper pass. Use the manager's exact selected Sol/medium binding and effort
unchanged in the helper brief/dispatch, not an inferred observed profile. Verify a permitted
callable Sol binding and medium support at assignment and dispatch. Unavailable Sol/medium stops
with the precise binding/support gap; no substitution, settings/default override or standalone
helper fallback may bypass this rule. Record observed binding/effort separately;
unknown stays unknown. Preserve mandatory stops, owner gates, approval renewal, and upstream context-coherent
brief/handoff constraints. In that
one same-session pass, review/fix the approved specification, run the detected planning capability
once to create the plan, then review/fix the produced plan. Return evidence and resulting artifacts
to the manager for inspection; do not direct it to create the plan again. The standalone local
fallback and separate-review policies below do not apply to this adapter invocation.
Verify the manager's explicit bounded documentation permission against the preflight
and boundary below; absence is not implied authority. Research-driven changes to any
approved specification content return through the manager's renewed specification
approval gate before leaving the affected stage; do not invent an owner ruling.

## Planner Boundary

The planner may read the supplied context and run the detected SpecKit planning
stage to write its specified plan artifacts. In addition, only explicit bounded
permission permits canonical research-document and necessary discovery-link writes
at observed destinations with specified allowed changes and prohibited operations.
Discover the repository technical owner/index, re-read targets before targeted updates,
and preserve unrelated content. No arbitrary documentation edits or product code writes
are authorized by this narrow exception; missing required authority stops the branch.
Unless separately authorized, it must not:

- Implement tasks or modify product code.
- Change the approved product scope.
- Run paid, live, deployment, or release operations unrelated to producing
  the SpecKit planning artifacts.
- It must not push or dispatch additional agents.

For already-authorized planning outputs within the bounded write permission above, verify and
make the focused path-limited task checkpoint required by the shared contract before completion or handoff. This mandatory checkpoint needs no separate commit opt-in; it does not authorize
new writes, specification/adaptation changes, pushes, or additional delegation.

Ensure the SpecKit plan covers:

- Architecture, contracts, and relevant files or interfaces when knowable;
  discovery steps when not.
- Sequencing, dependencies, parallel-safety constraints, and integration points.
- Verification strategy, including fail-then-pass checks for behavior changes and
  supporting source spans → implementation constraints → observable checks.
- Security, privacy, migration, rollback, and authorization gates where relevant.
- Documentation scope and specialized capabilities needed for implementation.

Leave implementation task breakdown, not model-class labeling, to the SpecKit
tasks stage; do not use the plan as a substitute for it. Carry source constraints, canonical
research, applicable guidelines and observable verification needs for stable REQUIRED items
through the task-generation contract. Coordinator owns later batch profile selection;
manager-governed planning-stage bindings remain unchanged.

## Owner Gates

The planner may correct an unambiguous clerical inconsistency and record it. For a
material product, architecture, privacy, permission, irreversible, or paid-operation
choice, it must stop that branch of planning and return:

```text
NEEDS_OWNER_DECISION
Question: ...
Why it blocks: ...
Affected plan sections: ...
Options: ...
Recommendation: ...
```

The coordinator obtains the answer and resumes the same planning context when the
runtime supports resumption. Never invent a ruling. A future live operation is not
itself a planning blocker: represent it as an explicit authorization gate unless
the required runtime policy is undefined.

## Completion

Verify that the detected SpecKit planning stage ran and inspect its outputs
against the approved spec and planner boundary. Verify shared-link resolution,
version/provenance, canonical owner/discovery, targeted reuse, evidence classification,
traceability and remaining capability/permission gaps before returning. Return these
research results with the plan path, architecture/dependency summary, capability
requirements, corrections, explicit deferral bounds/validation, and
open owner decisions. Stop after planning and wait for owner approval before
implementation.

## Mandatory task checkpoint

Apply the shared [task-commit contract](../memory-handling/references/task-commit-contract.md). Only already-authorized planning/adaptation outputs may be retained; this contract never bypasses planner approval or grants broader writes.
