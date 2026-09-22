---
name: delegating-architectural-planning
description: Use when an owner-approved architectural specification needs delegated decomposition into an implementation plan.
---

# Delegating Architectural Planning

Delegate only after the owner approves the specification and asks for a plan.
The planner owns design-to-task decomposition, not implementation or product
scope.

## Preflight

Verify and provide:

- The approved specification and evidence of approval.
- Repository instructions, governing principles, relevant contracts, and the
  intended plan location, using paths that exist.
- Existing architecture decisions and upstream/downstream dependencies.
- The planner's write scope and prohibited operations.

Inspect the runtime for an allowed delegation tool and configured planning-capable
agents. Use an owner-selected agent when available; otherwise choose from observed
capabilities and report the choice. Never invent an agent, model, command, or
configuration. If delegation is unavailable, state
`Architectural delegation: UNAVAILABLE` and offer to produce the same plan locally
with a separate review pass.

If the project uses SpecKit, detect its planning command, template, and supporting
assets before briefing the planner. Tell the planner how to use only the assets
actually found. When no planning capability is installed, use the plan contract
below as the generic fallback.

## Planner Boundary

The planner may read the supplied context and write the approved plan artifact.
Unless separately authorized, it must not:

- Implement tasks or modify product code.
- Change the approved product scope.
- Run mutating, paid, live, deployment, or release operations.
- Commit, push, or dispatch additional agents.

The plan must contain:

- Ordered tasks with outcomes and acceptance evidence.
- Exact files or interfaces when knowable; discovery steps when not.
- Dependencies, parallel-safety constraints, and integration points.
- Test-first or equivalent fail-then-pass verification for behavior changes.
- Security, privacy, migration, rollback, and authorization gates where relevant.
- A capability requirement for any task needing a specialized agent or tool.

Do not pin models or agent names in the plan. Assign work by observable capability
such as `routine implementation`, `architecture judgment`, or `security review`.
The implementation coordinator maps those requirements to agents that actually
exist at execution time.

## Owner Gates

The planner may correct an unambiguous clerical inconsistency and record it. For a
material product, architecture, privacy, permission, irreversible, or paid-operation
choice, it must stop that branch of planning and return:

```text
NEEDS_OWNER_DECISION
Question: ...
Why it blocks: ...
Affected tasks: ...
Options: ...
Recommendation: ...
```

The coordinator obtains the answer and resumes the same planning context when the
runtime supports resumption. Never invent a ruling. A future live operation is not
itself a planning blocker: represent it as an explicit authorization gate unless
the required runtime policy is undefined.

## Completion

Inspect the produced plan against the approved spec and planner boundary. Return
the plan path, task/dependency summary, capability requirements, corrections, and
open owner decisions. Stop after planning and wait for owner approval before
implementation.
