# ADR-0004: Shared routine worker permissions without repeated approval

## Status

Accepted owner direction. Recorded 2026-10-21. This records scoped permission defaults,
not a grant for unrelated work or evidence that required checks passed.

## Decision

Use one shared default-permissions block for workers, easy to modify without editing each
task. Ordinary scoped technical fixes, isolated tests/local servers, necessary isolated or
in-project dependency setup, and current-task artifact regeneration/selective cleanup do
not need repeated owner approval. Mere file changes are not an approval trigger.

Every task may create or load small isolated test fixtures and local test databases. Keep
test data and execution bounded so they do not risk exhausting the computer's resources or
affecting unrelated data or services. These local checks must not be blocked just because
the task did not separately enumerate each test fixture or setup action.

## Context and rationale

Routine permission questions interrupt work without resolving a material owner decision.
A blanket "Do not install" also contradicted permission for necessary isolated dependency
setup. The owner explicitly requested small isolated tests/databases and easily adjustable
default permissions rather than approval for ordinary technical actions.

## Consequences and limits

- Keep defaults in the existing `_ROUTINE_AUTHORITY` block in the runner and include them
  in initial and corrective task prompts; no new permission service or per-task schema.
- Use small scoped tests, not whole-machine workloads. Do not invent universal size limits,
  spending/resource ceilings or a resource-control subsystem for this permission change.
- Preserve actual requirements/manual gates, paid-scope approval, credential protection,
  global-install exclusions, and restrictions on deployment, push and unrelated deletion.
- Product decisions, substantial complexity increases, separately scoped paid usage and
  out-of-scope actions still ask. Unknown/pre-existing bytes must not be adopted or deleted.
- Authorization does not waive required checks, turn failures into success, or justify
  blind retries of expensive failed executions.

## Provenance

Owner conversation: "all tasks are allowed to create small isolated tests or load small
isolated database to test something as long as those are small tests" and do not exhaust
the computer's resources. Follow-up: "it should be easy to add or modify permissions in
the future. So there should be default permissions for all workers."

Current defaults and exclusions: [runner](../../runtime/coherence_workflow/engine.py).
Verification: [offline prompt and tiny in-memory database checks](../../runtime/tests/test_worker_authority.py),
not a machine-resource sandbox or live-provider acceptance test.
Current procedure: [operating guide](../coordinate-implementation.md#real-execution-and-safety).
Related authority boundary: [ADR-0003](ADR-0003-current-launch-authority-and-neutral-tasks.md).

## Supersession

No preceding ADR is superseded. No superseding ADR is recorded.
