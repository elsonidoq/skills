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

1. Mark completed tasks only from inspected changes and verification evidence.
2. Identify dependency-ready tasks and blocked tasks with their missing producers.
3. Group ready tasks only when they do not conflict on files, schemas, migrations,
   shared runtime state, or acceptance setup.
4. Keep contract producers before consumers and preserve explicit owner gates.
5. Prefer vertical slices that can be integrated and verified independently.

Before execution, report each batch's task IDs, scope, dependencies, integration
surface, and verification. Do not ask for routine batching approval when the owner
already approved implementation.

## Select Execution Capability

Inspect the runtime for available, permitted agents and tools. Match task capability
requirements from the plan to observed capabilities; never infer a fixed agent or
model name. Delegation is optional, not proof of completion.

- Delegate a task or safe batch only when write scope and dependencies are clear.
- Run conflicting or dependent work sequentially.
- Parallelize only independent work with isolated write surfaces and an explicit
  integration point.
- If delegation is unavailable, implement locally and perform a separate review
  pass. State `Delegation: UNAVAILABLE`.
- Resume an agent only when the runtime supports it and retained context materially
  overlaps; otherwise issue a fresh brief.

Every brief includes the exact outcome, task IDs, workspace and artifact paths,
allowed files, dependencies, acceptance criteria, baseline failures, exclusions,
authorization limits, and required return evidence. Ask for changed files, checks,
incomplete work, and non-obvious handoff context.

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
