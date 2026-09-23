---
name: coordinate-implementation
description: Use when implementing an approved feature from reviewed specification, plan, and task artifacts.
---

# Coordinate Implementation

Implement reviewed tasks in dependency order while preserving artifact provenance,
integration safety, and evidence. Work in the selected workspace; do not regenerate
planning artifacts as a substitute for resolving implementation blockers.

## Load and Verify

Require explicit or unambiguous paths to the spec, plan, and tasks. Read repository
instructions, governing principles, linked contracts, research, decisions, and the
source brief when present. Verify:

- The artifacts refer to the same feature and approved scope.
- Required upstream outputs and accepted decisions exist.
- Task prerequisites and integration points agree with the plan.
- Existing workspace changes are understood and preserved.

If the project uses SpecKit, inspect the available commands and assets for its
implementation and prerequisite capabilities. Follow only instructions found in
the current project. If the implementation command is unavailable, report
`SpecKit implementation: UNAVAILABLE` and execute the reviewed tasks directly from
their contracts. If a prerequisite checker is unavailable, perform direct artifact
and path checks and label the scripted check `UNAVAILABLE`.

## Build the Execution Graph

Treat task dependencies as a directed graph, not checklist order alone.

## Establish Completion Scope

Default to implementing every incomplete batch produced by the execution graph,
including batches that become ready after a predecessor completes. Do not stop
after an intermediate batch, milestone, vertical slice, review point, or a
delegated agent return merely to report progress or await routine approval.

Only a user-defined partial implementation boundary permits ending before all
batches are complete. When the user explicitly defines such a boundary, before
starting implementation call the `question` tool to confirm whether to stop at
that boundary or implement all incomplete batches. Provide those two choices
without marking either as recommended. Record the selected scope in the
execution plan and follow it. A newly discovered material owner gate or an
unresolvable blocker may still require pausing; report it with the blocked
batch and missing decision or dependency.

1. Mark completed tasks only from inspected changes and verification evidence.
2. Identify dependency-ready tasks and blocked tasks with their missing producers.
3. Build batches of approximately 5-10 ready tasks when they do not conflict on
   files, schemas, migrations, shared runtime state, or acceptance setup, and have
   the same required model class. Do not create batches of one or two tasks unless
   a model-class boundary makes a smaller batch unavoidable, such as an
   `opus-class` task surrounded by `sonnet-class` tasks.
4. Keep contract producers before consumers and preserve explicit owner gates.
5. Prefer vertical slices that can be integrated and verified independently.
6. Execute every batch sequentially; never run implementation batches in parallel.
   Re-evaluate the execution graph after each batch completes.

Before execution, present the entire execution plan as a Markdown table. Include
one row per batch with its batch number, task IDs, scope, dependencies, integration
surface, verification, required model class, and initial status. Do not ask for
routine batching approval when the owner already approved implementation.

Create an OpenCode `todowrite` list immediately after presenting the table, with
one item per batch. Mark the first dependency-ready batch `in_progress`, later
batches `pending`, and blocked batches `pending` with the blocking producer named
in the item. Update the list after every batch: mark verified batches `completed`,
mark the next dependency-ready batch `in_progress`, and add, remove, or revise
batches only when re-evaluating the execution graph requires it. Keep exactly one
batch `in_progress` while implementation remains.

## Select Execution Capability

Inspect the runtime for available, permitted agents and tools. Before executing a
batch, use the `question` tool to ask the user to select an available model for each
model class used by incomplete tasks: `sonnet-class` and `opus-class`. Retain those
selections for the session and match each batch to the model selected for its required
class. Do not infer a model selection. Delegation is optional, not proof of
completion.

- Delegate a task or safe batch only when write scope and dependencies are clear.
- Run conflicting or dependent work sequentially.
- Run all batches sequentially, including independent batches with isolated write
  surfaces.
- If delegation is unavailable, stop before implementation and report
  `Delegation: UNAVAILABLE` to the user.
- Resume a previously used agent only when it uses the model selected for the batch,
  the runtime supports resumption, and its retained context materially overlaps;
  otherwise issue a fresh brief.

Every brief includes the exact outcome, task IDs, workspace and artifact paths,
required model class, selected model, allowed files, dependencies, acceptance
criteria, baseline failures, exclusions, authorization limits, and required return
evidence. Ask for changed files, checks, incomplete work, and non-obvious handoff
context.

## Execute and Integrate

For each task or batch:

1. Establish the smallest meaningful failing check before behavior changes.
2. Implement only the assigned scope.
3. Inspect the actual diff; preserve unrelated changes.
4. Run task-level checks and validate reports against observable output.
5. Integrate at the planned boundary and run affected contract or cross-component
   checks before releasing dependents.
6. Update task completion and decisions in the project's existing artifact format.
   If none exists, update the task list; do not invent a state-file convention.
7. Update the OpenCode `todowrite` list to reflect the batch's verified outcome and
   the next dependency-ready batch.

Do not commit, push, deploy, send external messages, run paid services, or perform
irreversible operations unless the owner requested that operation and repository
policy permits it. A commit is an optional owner-directed integration action, not a
workflow requirement.

Material product, architecture, privacy, permission, cost, or irreversible choices
remain owner gates. Save verified progress and ask one concise question when a gate
blocks dependent work. Implementation details with a mechanically verifiable answer
do not require owner escalation.

## Review and Acceptance

Review accumulated changes against the spec, plan, tasks, governing principles,
failure paths, migrations, contracts, and documentation. Derive QA from the selected
artifacts and detected project capabilities; never import another project's threat
model, data, commands, or runtime assumptions.

For each acceptance scenario report `PASS`, `FAIL`, `PARTIAL`, `NOT RUN`, or
`UNAVAILABLE` with the command or observation. Distinguish local or simulated
evidence from live acceptance. Do not call unavailable external validation passed.
Fix in-scope failures, re-run affected checks, and leave blocked dependents pending.

## Finish

Return completed and pending tasks, changed files, checks and results, integration
status, unresolved owner gates, unavailable capabilities, and the next
dependency-ready action. State separately whether implementation is complete and
whether feature acceptance is verified. Agent completion and checked boxes alone
are not acceptance evidence.
