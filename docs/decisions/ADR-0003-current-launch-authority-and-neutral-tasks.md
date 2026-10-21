# ADR-0003: Current launch authority and authorization-neutral tasks

## Status

Accepted owner direction. Recorded 2026-10-21. Acceptance records the decision, not
permission to launch another workflow or proof that an implementation task is complete.

## Decision

An owner-authorized implementation launch approves the assigned task scope. Historical
"planning only" or "awaiting implementation approval" wording must not independently block
that authorized work. The runner states this current authority in task-worker prompts,
including corrective and resumed task invocations.

Executable task descriptions and check permissions are authorization-neutral. Temporary
phase/approval status belongs in the approval record. Final planning review checks this in
both TinySpec and Standard; historical source/task records remain intact.

## Context and rationale

A worker received repeated historical planning-only restrictions without the owner's later
implementation authorization. It declined the task while another worker proceeded. Matching
approved artifact hashes did not establish that workers received current authority.

The owner chose a tiny runner-prompt and planning-review correction rather than a new
authorization field, bridge interface, approval protocol or worker-result format.

## Consequences and limits

- Inject current implementation authority; do not ask again merely because historical phase
  wording remains in approved artifacts.
- Preserve task requirements, acceptance criteria, real manual gates and safety/permission
  boundaries. Material unresolved authority conflicts still ask the owner.
- A launch does not authorize unrelated work, paid-scope expansion or automatic retries.
- A returned execution is not proof of task acceptance. False-completion detection was
  explicitly excluded from this fix, not declared safe or resolved.

## Provenance

Owner conversation: "Maybe doing something in the workflow runner script. That injects
into the workers the approvals, and also instructing the final plan reviewer to make sure
that. Tasks are authorization neutral. I think this fix should be tiny." The owner then
approved the two bounded tasks and instructed: "Okay, now execute those tasks."

Current behavior: [runner prompt](../../runtime/coherence_workflow/engine.py),
[task-authoring contract](../../skills/task-generation/SKILL.md#authorization-neutral-tasks)
and [planning review](../../skills/planner/SKILL.md).
[Offline prompt checks](../../runtime/tests/test_worker_authority.py) establish delivery,
not live model obedience. The [operating guide](../coordinate-implementation.md#real-execution-and-safety)
owns current operation.

## Supersession

No preceding ADR is superseded. This scopes the later implementation authorization over
historical phase restrictions without rewriting historical approvals. No superseding ADR
is recorded.
