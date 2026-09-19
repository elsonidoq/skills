---
name: delegating-architectural-planning
description: Use when an approved architectural spec needs an opus planning agent to create a task-by-task implementation plan with explicit sonnet or opus assignments.
---

# Delegating Architectural Planning

Use only after the owner explicitly approves a spec and requests a planning exception. The planner owns design-to-task decomposition, not implementation.

## Required Context

Before dispatching, give the planner the spec path, `AGENTS.md`, `STATE.md`, constitution, `BUILD.md`, relevant package guidance, and the target plan path. State that the owner requested `writing-plans` despite any superseded-plan warning in project workflow.

## Planner Contract

The planner MUST load `writing-plans` before planning. It may read and write only the approved spec and the new plan artifact. It must not implement, run mutating commands, commit, push, deploy, make external calls, or dispatch agents.

The plan must contain ordered tasks with: purpose, exact files/interfaces, dependencies, RED/GREEN verification, safety boundaries, and assigned model.

## Model Assignment

The dispatch provides ordered `Allowed models`. The first is the default for bounded execution; every task assignment must be one of those models. If omitted, use `sonnet, opus` in that order.

Use the highest-capability allowed model only for unresolved cross-cutting architecture, non-obvious security/privacy reasoning, or a material design choice. Split an otherwise large high-capability task into a small design task plus independent default-model implementation tasks whenever possible. Every non-default assignment needs a one-line justification.

## Spec Corrections And Decisions

The planner may correct an unambiguous inconsistency in the approved spec and record the correction in the plan. For a material product, privacy, permission, irreversible, paid-operation, or architectural choice, it must stop and return:

```
NEEDS_OWNER_DECISION
- Question: ...
- Why it blocks: ...
- Affected tasks: ...
- Recommended option: ...
```

The coordinator resumes the same planner with the owner's answer. Never invent a ruling.

An absent authorization for a future paid test or live run is not a planning blocker: plan the test as an explicit owner-authorization gate and do not execute it. Stop only when the product's runtime policy itself is undefined.

## Completion

Return the plan path, task/model table, any spec corrections, and unresolved decisions. Stop after planning and wait for owner approval; never start implementation.

## Common Mistakes

| Mistake | Required behavior |
| --- | --- |
| One difficult `opus` task | Split it; use `sonnet` for bounded execution. |
| Defaulting to `sonnet` despite owner options | Assign only listed models; use the first listed model by default. |
| Asking the owner interactively | Emit the resumable decision block. |
| Live call needed to plan | Describe the authorization gate; do not call it. |
| Treating future call authorization as a spec blocker | Plan it as an owner-authorization gate; do not execute it. |
| Starting code after a plan | Stop and await explicit approval. |
