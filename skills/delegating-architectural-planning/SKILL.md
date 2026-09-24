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
  intended plan location, using paths that exist.
- Existing architecture decisions and upstream/downstream dependencies.
- The planner's write scope and prohibited operations.
- The detected SpecKit planning command or skill, its invocation instructions,
  template, prerequisite scripts, and expected output paths.

Verify that the planning capability is available to the planner in the
delegated context. If it is missing or cannot be used there, report
`SpecKit planning: UNAVAILABLE` and stop; do not write a generic plan or
claim that the planning stage ran.

Inspect the runtime for an allowed delegation tool and configured planning-capable
agents. Use an owner-selected agent when available; otherwise choose from observed
capabilities and report the choice. Never invent an agent, model, command, or
configuration. If delegation is unavailable, state
`Architectural delegation: UNAVAILABLE` and offer to run the installed SpecKit
planning stage locally with a separate review pass.

Brief the planner to follow the detected SpecKit planning instructions and
verify the generated artifacts. If the capability is exposed as
`/speckit.plan`, use that installed capability through its supported runtime
interface; do not simulate the slash command in a shell. The plan requirements
below supplement the generated artifacts and do not replace the SpecKit stage.

## Planner Boundary

The planner may read the supplied context and run the detected SpecKit planning
stage to write its specified plan artifacts.
Unless separately authorized, it must not:

- Implement tasks or modify product code.
- Change the approved product scope.
- Run paid, live, deployment, or release operations unrelated to producing
  the SpecKit planning artifacts.
- Commit, push, or dispatch additional agents.

Ensure the SpecKit plan covers:

- Architecture, contracts, and relevant files or interfaces when knowable;
  discovery steps when not.
- Sequencing, dependencies, parallel-safety constraints, and integration points.
- Verification strategy, including fail-then-pass checks for behavior changes.
- Security, privacy, migration, rollback, and authorization gates where relevant.
- Documentation scope and specialized capabilities needed for implementation.

Leave implementation task breakdown and model-class labeling to the SpecKit
tasks stage; do not use the plan as a substitute for it.

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
against the approved spec and planner boundary. Return the plan path,
architecture/dependency summary, capability requirements, corrections, and
open owner decisions. Stop after planning and wait for owner approval before
implementation.
