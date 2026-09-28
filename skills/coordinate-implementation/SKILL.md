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
source brief when present. Load the project memory store per the `memory-handling`
skill and read the index plus any entries whose triggers match the planned work;
treat verified trigger-first gotchas as implementation constraints. Verify:

- The artifacts refer to the same feature and approved scope.
- Required upstream outputs and accepted decisions exist.
- Task prerequisites and integration points agree with the plan.
- Existing workspace changes are understood and preserved.

Determine workflow origin from the handoff and linked artifacts. For work produced
by `epics-manager`, on every fresh session or resume:

- Read the specification-approval and overall-review-approval records, including
  records stored outside the spec, plan, or tasks, and their linked decisions.
- Verify specification approval applies to the current specification and overall
  review approval applies to the current spec, plan, and tasks. Compare their
  recorded revisions or content evidence with the current artifacts; do not trust
  an `approved` label or the handoff alone.
- Inspect the overall review evidence and unresolved owner gates. If approval is
  missing, stale, or unverifiable, or required review evidence is missing, stop
  before implementation and return to the earliest affected `epics-manager` gate.
  Do not replace missing pipeline stages with generic artifacts.

If origin or approval provenance is ambiguous, resolve it before implementation;
do not assume standalone origin to bypass these gates. For unrelated standalone
work, verify current owner authorization and applicable project gates without
imposing the manager's two-gate process or requiring SpecKit-generated artifacts.
This skill still requires a spec, plan, and tasks; a direct task list alone belongs
to a separate owner-selected execution path.

If the project uses SpecKit, inspect the available commands and assets for its
implementation and prerequisite capabilities. Follow only instructions found in
the current project. If the implementation command is unavailable, report
`SpecKit implementation: UNAVAILABLE` and execute the reviewed tasks directly from
their contracts. If a prerequisite checker is unavailable, perform direct artifact
and path checks and label the scripted check `UNAVAILABLE`.

## Execution Capability Preflight

Before establishing completion scope or executing work, verify that the runtime
exposes permitted, usable question and delegation tools. The suite pins these to the
`ask_user` question tool (package `pi-ask-user`) and the `subagent` delegation tool
(package `pi-subagents`); see the global configuration repository's `REQUIREMENTS.md`.
Delegation is mandatory for implementation. Check configured agents and their callable
model bindings (the suite's `subagents.agentOverrides` mapping), not configuration
names alone. If either required capability is unavailable, stop before
implementation and report `question: UNAVAILABLE` or `Delegation: UNAVAILABLE` with
the missing requirement. Do not substitute prose selection or local implementation.

Track the execution plan throughout the task. If the host provides a native
planning or task-tracking facility, use it. Otherwise, maintain the plan as a
Markdown checklist, updating items as they move through `pending`, `in_progress`,
and `completed` states. Do not stop execution solely because a dedicated todo tool
is unavailable.

For every model class used by incomplete tasks, verify there is at least one usable
agent/model option. Use the runtime's `ask_user` question tool to obtain the owner's selection for each class
before implementation and retain the selected agent/model mapping for the session.
Offer only observed, permitted options; never infer a selection or silently switch
models. If no usable mapping exists, report `Agent/model selection: UNAVAILABLE`
with the affected class and stop before implementation.

## Build the Execution Graph

Treat task dependencies as a directed graph, not checklist order alone.

## Establish Completion Scope

Default to implementing every incomplete batch produced by the execution graph,
including batches that become ready after a predecessor completes. Do not stop
after an intermediate batch, milestone, vertical slice, review point, or a
delegated agent return merely to report progress or await routine approval.

Only a user-defined partial implementation boundary permits ending before all
batches are complete. When the user explicitly defines such a boundary, before
starting implementation call the runtime's `ask_user` question tool to confirm whether to stop at
that boundary or implement all incomplete batches. Provide those two choices
without marking either as recommended. Record the selected scope in the
execution plan and follow it. A newly discovered material owner gate or an
unresolvable blocker may still require pausing; report it with the blocked
batch and missing decision or dependency.

1. Mark completed tasks only from inspected changes and verification evidence.
2. Identify dependency-ready tasks and blocked tasks with their missing producers.
3. Build batches only from consecutive task entries in the approved list, within
   one user story (or one shared setup/stage segment when tasks have no story).
   Never pull a distant producer forward into a batch: execute intervening
   prerequisite batches first. Aim for 5-7 tasks only when the
   consecutive tasks do not conflict on files, schemas, migrations, shared
   runtime state, or acceptance setup, and have the same required model class.
   Smaller batches, including one task, are fine at story/stage boundaries,
   dependency bottlenecks, owner gates, model-class boundaries, or conflicting
   write surfaces; record the reason rather than filling a batch with distant work.
4. Keep contract producers before consumers and preserve explicit owner gates.
5. Prefer vertical slices that can be integrated and verified independently.
6. Execute every batch sequentially; never run implementation batches in parallel.
   Re-evaluate the execution graph after each batch completes.

If the approved tasks require a later-numbered task to unblock an earlier one,
stop before building the batch plan. Do not silently reorder tasks or mix stories
to make the batch run: return the sequencing defect to the plan/tasks review gate
for correction and renewed approval as required by the project's workflow.

Before execution, present the entire execution plan as a Markdown table. Include
one row per batch with its batch number, task IDs, scope, dependencies, integration
surface, verification, required model class, and initial status. Do not ask for
routine batching approval when the owner already approved implementation.

Immediately after presenting the table, initialize the execution tracker with one
item per batch. Mark the first dependency-ready batch `in_progress`, later batches
`pending`, and blocked batches `pending` with the blocking producer named in the
item. Update it after every batch: mark verified batches `completed`, mark the next
dependency-ready batch `in_progress`, and add, remove, or revise batches only when
re-evaluating the execution graph requires it. Keep exactly one batch `in_progress`
while implementation remains.

## Select Execution Capability

Use the agent/model mappings obtained in preflight for `sonnet-class` and
`opus-class`, as applicable. Before each batch, confirm its selected mapping remains
usable. If a new class or replacement mapping is needed, repeat the capability
check and obtain the selection through the runtime's `ask_user` question tool before proceeding. Delegation
is mandatory, but an agent's report is not proof of completion.

- Delegate a task or safe batch only when write scope and dependencies are clear.
- Run conflicting or dependent work sequentially.
- Run all batches sequentially, including independent batches with isolated write
  surfaces.
- Stay within the delegation runtime's documented spawn budgets: a large epic of
  many tens of tasks delegates on the order of 20 batches, which is within the
  pinned runtime's defaults, but verify the per-run and session-wide budgets
  before starting and stop rather than exceeding them.
- If delegation is unavailable, stop before implementation and report
  `Delegation: UNAVAILABLE` to the user.
- Resume a previously used agent only when it uses the model selected for the batch,
  the runtime supports resumption, and its retained context materially overlaps;
  otherwise issue a fresh brief.

Before dispatching file changes, check which mutation tool the selected agent/model
actually receives and is permitted to use. Pi's core tool set exposes `edit` and
`write`; some runtimes or models expose only a diff-based `patch` instead. Do not
infer a permission failure from a missing tool, or prohibit the agent's only viable
mutation tool in a brief or smoke test. If the tool set is uncertain, verify it with
a bounded, safe test before implementation; if no permitted mutation tool works,
stop and report the observed blocker.

Every brief includes the exact outcome, task IDs, workspace and artifact paths,
required model class, selected model, allowed files, dependencies, acceptance
criteria, baseline failures, exclusions, authorization limits, the batch commit
convention and whether the delegate or the coordinator performs it, the selected
agent's verified file-mutation tool when file changes are needed, and required
return evidence. Ask for changed files, checks, incomplete work, and non-obvious
handoff context.

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
7. Update the execution tracker to reflect the batch's verified outcome and the
   next dependency-ready batch.
8. Commit the batch's verified changes as one focused commit before starting the
   next batch. A per-batch commit is a required workflow step, not an optional
   integration action.

Prefer a project's documented commit message and commit-workflow convention when one
exists. Before the first commit, verify the workspace is a version-control repository
and that committing is permitted. If repository instructions, governing principles,
or policy forbid or constrain committing (for example, a different message format,
branch, squash, sign-off, or a deferred-commit review gate), do not silently skip,
defer, or reshape the commit: call the runtime's `ask_user` question tool, state the
contradicting directive and the requested per-batch commit, and let the owner decide.
Record the decision in the execution tracker and apply it consistently to later
batches. If the workspace has no usable version-control or commit capability, report
the observed condition and ask the owner whether to proceed without per-batch
commits. Never omit a batch commit without an explicit owner decision.

Do not push, deploy, send external messages, run paid services, or perform
irreversible operations unless the owner requested that operation and repository
policy permits it.

Material product, architecture, privacy, permission, cost, or irreversible choices
remain owner gates. Save verified progress and ask one concise question when a gate
blocks dependent work. Implementation details with a mechanically verifiable answer
do not require owner escalation.

## Review and Acceptance

Review accumulated changes against the spec, plan, tasks, governing principles,
failure paths, migrations, contracts, documentation, and the project memory store
(per the `memory-handling` skill). Derive QA from the selected
artifacts and detected project capabilities; never import another project's threat
model, data, commands, or runtime assumptions.

For each acceptance scenario report `PASS`, `FAIL`, `PARTIAL`, `NOT RUN`, or
`UNAVAILABLE` with the command or observation. Distinguish local or simulated
evidence from live acceptance. Do not call unavailable external validation passed.
Fix in-scope failures, re-run affected checks, and leave blocked dependents pending.

## Finish

Return completed and pending tasks, changed files, per-batch commits (or the owner's
recorded decision to skip or defer them), checks and results, integration
status, unresolved owner gates, unavailable capabilities, and the next
dependency-ready action. State separately whether implementation is complete and
whether feature acceptance is verified. Agent completion and checked boxes alone
are not acceptance evidence.
