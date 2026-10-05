---
name: coordinate-implementation
description: Use when implementing or resuming approved work from a reviewed task list and its authorized source artifacts.
---

# Coordinate Implementation

Implement reviewed tasks in dependency order while preserving artifact provenance,
integration safety, and evidence. Work in the selected workspace; do not regenerate
planning artifacts as a substitute for resolving implementation blockers.

## Load and Verify

Require explicit or unambiguous paths to the approved requirement/source, tasks,
applicable source/supporting artifacts, and durable authorization/review evidence.
Read repository instructions, governing principles, linked contracts, research,
decisions, and source constraints. In projects declaring the memory contract, verify
`memory-handling` is discoverable and load the project memory store, index, and
trigger-matching entries; missing required memory capability stops with a report.
Treat verified trigger-first gotchas as implementation constraints.
Apply the shared [project coordination contract](../memory-handling/references/project-coordination.md):
read associated compact guidelines and carry exact applicable constraints/evidence references
from planning into task briefs/checkpoints. Verify optional association and bounded evidence
write authority separately from required gotcha memory. Without association/write authority,
keep observations in the existing execution handoff and offer future bounded setup; never
silently initialize a store. Undeclared optional memory adds no blocker; report declared
missing/unreadable content accurately. No default evidence-history intake; justified
clarification follows index-first relevant-only retrieval. Verify:

- The source, tasks, and supporting artifacts refer to the same approved scope.
- Required upstream outputs, accepted decisions, and current authorization exist.
- Task prerequisites and integration points agree with applicable source contracts.
- Existing workspace changes are understood and preserved.

On every fresh session or resume, compare current source/task/supporting content or
revisions with durable approval evidence, including linked records outside the
artifacts. A chat-only approval or an `approved` label is not a fresh-session proof.
Missing review evidence, unresolved material owner gates, or approval that is
missing, stale, or unverifiable stops implementation at the earliest affected
producing workflow gate. Never repair provenance by inventing artifacts.

Determine workflow origin and selected planning depth from the handoff and linked artifacts.
For `planner` origin with Standard depth (or legacy `epics-manager` origin), require
specification, plan, tasks, both current approvals, source provenance, overall review
evidence, and required SpecKit stage evidence.
On every fresh session or resume:

- Read the specification-approval and overall-review-approval records, including
  records stored outside the spec, plan, or tasks, and their linked decisions.
- Verify specification approval applies to the current specification and overall
  review approval applies to the current spec, plan, and tasks. Compare their
  recorded revisions or content evidence with the current artifacts; do not trust
  an `approved` label or the handoff alone.
- Inspect the overall review evidence and unresolved owner gates. If approval is
  missing, stale, or unverifiable, or required review evidence is missing, stop
  before implementation and return to the earliest affected planner Standard checkpoint,
  including for legacy work. Do not invoke a retired producer or replace missing stages
  with generic artifacts.

For `planner` origin with TinySpec depth, require a separate TinySpec/source and tasks,
review evidence, and explicit current combined owner approval of source/tasks and
implementation scope. For legacy `requirements-manager` origin, require durable
requirement/source, tasks, review evidence and its explicit current combined approval;
its original source may be embedded in tasks and needs no retroactive TinySpec.
Verify traceability, constraints, exclusions, decisions/deferrals, and approved content
or revision evidence. No specification, plan, or SpecKit prerequisite is required;
do not fabricate placeholders. Missing/stale evidence returns to planner's applicable
combined source/task review and approval checkpoint. Preserve original provenance and
source shape for repairs, including partially planned legacy work. Follow planner's
[approval/recovery mapping](../planner/references/approval-and-recovery.md); if unavailable,
report the missing contract and stop rather than fabricate a repair gate.

For other documented origins, verify the identified producer, durable source/task
review and current owner authorization, plus applicable project gates. Do not impose
Standard's two approvals on unrelated work or waive a documented producer's safeguards.
Ambiguous origin is a blocker; resolve it before implementation, never assume
standalone origin to bypass gates. Missing/conflicting depth for planner-origin work
also blocks; never relabel legacy Standard work TinySpec to bypass evidence.
Planning depth changes intake evidence only, not execution strategy or task semantics.

Run SpecKit implementation/prerequisite instructions only when applicable to the
selected origin and artifacts. Installation alone does not make SpecKit applicable
to direct requirement/tasks. When applicable, inspect available commands and assets
and follow only instructions found in the current project. If the implementation
command is unavailable, report
`SpecKit implementation: UNAVAILABLE` and execute the reviewed tasks directly from
their contracts. If a prerequisite checker is unavailable, perform direct artifact
and path checks and label the scripted check `UNAVAILABLE`.

## Execution Capability Preflight

Before establishing completion scope or executing work, verify permitted, usable
question capability and owner-selected model/class bindings, including the current
agent for eligible local execution. Check callable bindings, not configuration names
alone. The suite declares question/delegation runtime requirements in the global
configuration repository's `REQUIREMENTS.md`; verify their availability rather than
assuming installation. Missing required question capability reports
`question: UNAVAILABLE` and stops; do not substitute inferred owner selection.
Verify async/background delegation and its runtime budgets before any delegated work,
and a usable fresh independent reviewer before implementation. Missing required
delegation or reviewer capability stops with `Delegation: UNAVAILABLE` or
`Independent review: UNAVAILABLE`. No unauthorized local fallback is permitted.

Track the execution plan throughout the task. If the host provides a native
planning or task-tracking facility, use it. Otherwise, maintain the plan as a
Markdown checklist, updating items as they move through `pending`, `in_progress`,
and `completed` states. Do not stop execution solely because a dedicated todo tool
is unavailable.

For every model class used by incomplete tasks, verify at least one usable local or
delegated agent/model option. Use the question capability to obtain the owner's
selection for each class and independent review before implementation. Retain valid
recorded selections on resume; do not re-request settled choices. Offer only observed,
permitted options; never silently switch models or downgrade task classes. If no usable
mapping exists, report `Agent/model selection: UNAVAILABLE` with the class and stop.

## Select Execution Strategy

Count the complete approved implementation task list, including completed tasks;
exclude standalone review tasks. Select by this count, not origin, plan presence, or remaining task count:

- Up to three bounded implementation tasks may run locally only when the
  current owner-selected model/class matches each task, scope is clear, and
  observed context capacity is adequate. For a different class, broader isolation,
  or excessive context, delegate the affected task or segment using the shared
  batching rules below. Do not change the current model to force local eligibility.
- More than three implementation tasks require delegation through the same
  consecutive homogeneous sequential batching machinery, including one-task batches
  where justified. The 5–7 target below is guidance, never a threshold or quota.

Record the complete count, chosen local/delegated strategy, class selections,
context evidence/limitations, and any delegated segments in the tracker before work.
Retain the recorded strategy on resume unless approved scope changes or an observed
safety/context constraint requires a recorded revision and renewed gates as applicable.
Completing tasks alone never changes delegated execution to local. If context cannot
be observed sufficiently to establish local suitability, delegate; if required
delegation is unavailable, stop rather than weakening eligibility.

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

## Build the Execution Graph

Treat task dependencies as a directed graph, not checklist order alone.
Both routes use this single execution graph, authorization preflight, verification,
integration, tracker, per-task commits, and independent final review. Local tasks
follow the same ordered task contracts; delegation uses the following shared batches.

1. Mark completed tasks only from inspected changes and verification evidence.
2. Identify dependency-ready tasks and blocked tasks with their missing producers.
3. Build batches only from consecutive task entries in the approved list and one required
   model class. Keep coherent producer/consumer work together to amortize startup and retain
   useful context. Internal dependencies, shared files, and phase/story headings do not require
   a split when one writer executes tasks sequentially, verifies each producer before its
   consumer, preserves task acceptance boundaries, and commits each task separately. Never pull
   a distant producer forward or reorder a prerequisite to fill a batch.
4. Aim for 5–7 tasks only when scope and observed context permit; it is not a quota. Split at
   evidenced model-class changes, owner gates, context limits, genuinely incompatible scope, or
   external integration prerequisites that cannot be satisfied inside the batch. A one-task batch
   is valid when justified; headings, overlapping files, or internal dependencies alone are not.
5. Keep contract producers before consumers and preserve explicit owner gates. The batch brief
   states its internal task sequence, shared context, producer checks, and integration checkpoints.
6. Execute every batch sequentially and delegate only asynchronously in the background; never
   run implementation batches in parallel. Re-evaluate the execution graph after each batch
   completes without changing approved task order.

If the approved tasks require a later-numbered task to unblock an earlier one,
stop before building the batch plan. Do not silently reorder tasks or mix stories
to make the batch run: return the sequencing defect to the producing workflow's review gate
for correction and renewed approval as required by the project's workflow.

Before execution, present the entire execution plan as a Markdown table. Include
one row per batch with its batch number, task IDs, scope, dependencies, integration
surface, verification, required model class, execution mode (local or delegated),
and initial status. Track eligible local segments as work units in this same table
and tracker, not a second execution algorithm. Do not ask for routine batching
approval when the owner already approved implementation.

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
check and obtain the selection through the question capability before proceeding.
For eligible local work, recheck current model/class and context fit at each checkpoint;
if unsafe, record the evidence and delegate the affected segment, never silently
switch models. For delegated work, an agent's report is not proof of completion.

- Delegate a task or safe batch only when write scope and dependencies are clear.
- Run conflicting or dependent work sequentially.
- Run all batches sequentially, including independent batches with isolated write
  surfaces.
- Verify and stay within observed per-run and session-wide delegation budgets;
  stop rather than exceeding them or assuming historical runtime limits.
- If required delegation is unavailable, stop before implementation and report
  `Delegation: UNAVAILABLE` to the user.
- Resume a previously used agent only when it uses the model selected for the batch, the
  runtime supports resumption, its retained context materially overlaps, and observed context
  headroom is adequate. Inspect accumulated context, compaction, tool output, and demonstrated
  scope rather than treating task count or billed tokens as capacity. When evidence is inadequate,
  record that limitation and issue a smaller fresh brief with durable handoff context.
- There is no forced one-session-per-class limit. Rotate to a fresh bounded child when
  observed capacity is inadequate, retaining selected class/model and durable evidence.
  If context metrics are unavailable, state that limitation and conservatively narrow
  the next delegation; do not force reuse or equate billed tokens with occupied context.
- Inspect the failed run and tool invocation before retry or relaunch. Resume with a
  targeted correction only when supported and the cause is understood; if evidence
  is missing or uncertain, stop and report the blocker. Rotation is not a blind retry.
- For long delegated work, checkpoint early with completed changes, check results,
  remaining work and blockers, before the observed run budget is exhausted. After a
  timeout, inspect that checkpoint and the failed invocation; retain valid completed
  evidence and narrow the remaining step instead of restarting the entire batch.
  Resume only under the inspected-cause rule above; a timeout alone is not retry authority.

Before dispatching file changes, check which mutation tool the selected agent/model
actually receives and is permitted to use. Pi's core tool set exposes `edit` and
`write`; some runtimes or models expose only a diff-based `patch` instead. Do not
infer a permission failure from a missing tool, or prohibit the agent's only viable
mutation tool in a brief or smoke test. If the tool set is uncertain, verify it with
a bounded, safe test before implementation; if no permitted mutation tool works,
stop and report the observed blocker.

For optional real-work routing experiments, apply the shared contract's class-compatible
residual-reasoning guidance using only usable owner-selected options. Low favors a cheaper
compatible selected option; medium requires a strong executable acceptance oracle plus
stronger verification/review; high favors stronger compatible reasoning, not forced opus
reclassification or share-gate bypass. Absence preserves existing routing. Never silently
replace selected models, weaken approved classes or turn one outcome into permanent policy.
On a cheap-option failure, inspect the child run and failed invocation first. Preserve valid
completed evidence and unrelated workspace changes; isolate/restore only the failed task's
clean state where existing workspace architecture and authority permit. Escalate only via
verified stronger capability and owner-selection gates. Unknown cause, unavailable permitted
capability or unestablished clean state stops with the precise blocker; no blind retry.
Record both attempts, corrections and escalation outcomes at the evidence checkpoint.

Every brief includes the exact outcome, task IDs, workspace and artifact paths,
required model class, selected model, allowed files, dependencies, acceptance
criteria, baseline failures, exclusions, authorization limits, the per-task commit
convention and whether the delegate or the coordinator performs it, the selected
agent's verified file-mutation tool when file changes are needed, and required
return evidence. Include the verified origin, source/supporting artifacts, current
approval/review locations, internal task sequence, shared context, producer checks,
and integration checkpoints. Ask for changed files, checks, incomplete work, and
non-obvious handoff context.

## Execute and Integrate

Enforce the approved task-generation acceptance boundary in each brief and checkpoint:
REQUIRED checks remain required; optional hardening/broader regression is not a blocker.
Separately gated live/provider/engine/browser checks still need explicit permissions;
if required but unavailable, report NOT RUN/UNAVAILABLE and leave acceptance blocked.
Never silently waive an owner-required check or approved safety criterion; changing
acceptance returns to the producing workflow for explicit authority and renewed approval.
Reuse valid unchanged evidence after verifying scope, revisions and environment, and
refresh only affected evidence rather than repeating historical intake or whole suites.
New unrelated compatibility failures become separate causal work with scope/dependency
gates, not an automatic expansion of the current task.

For each task, whether local or inside a delegated batch:

1. Establish the smallest meaningful failing check before behavior changes.
2. Implement only the assigned scope.
3. Inspect the actual diff; preserve unrelated changes.
4. Run required task-level checks at the lowest sufficient layer and validate reports
   against observable output; do not automatically expand to matrices or broad suites.
5. Integrate at the planned boundary and run required affected contract or cross-component
   checks before releasing dependents; justify additions by a concrete changed-seam risk
   and apply the acceptance/approval boundary above.
6. Update task completion and decisions in the project's existing artifact format.
   If none exists, update the task list; do not invent a state-file convention.
7. Update the execution tracker to reflect the batch's verified outcome and the
   next dependency-ready batch.
8. Commit each task's verified changes as one focused commit before starting the next task.
   Task commits are required checkpoints, not a reason to split a coherent batch or launch a
   new session.

Prefer a project's documented commit message and commit-workflow convention when one
exists. Before the first commit, verify the workspace is a version-control repository
and that committing is permitted. If repository instructions, governing principles,
or policy forbid or constrain committing (for example, a different message format,
branch, squash, sign-off, or a deferred-commit review gate), do not silently skip,
defer, or reshape the commit: call the runtime's `ask_user` question tool, state the
contradicting directive and the requested per-task commit, and let the owner decide.
Record the decision in the execution tracker and apply it consistently to later
batches. If the workspace has no usable version-control or commit capability, report
the observed condition and ask the owner whether to proceed without per-task
commits. Never omit a required task commit without an explicit owner decision.

Do not push, deploy, send external messages, run paid services, or perform
irreversible operations unless the owner requested that operation and repository
policy permits it.

Material product, architecture, privacy, permission, cost, or irreversible choices
remain owner gates. Save verified progress and ask one concise question when a gate
blocks dependent work. Implementation details with a mechanically verifiable answer
do not require owner escalation.

### Coordination evidence checkpoint

At each task/attempt checkpoint, including failed, blocked or partial work and manual/user
validation, record observed outcomes under the shared contract's associated write bounds.
Identify task/type, areas/tags, optional `residual_reasoning: low|medium|high` and rationale,
approved class, actual selected capability role/model/reasoning effort (or `unknown`),
individual attempt/check results, reviewer findings, inspected failure cause, retries and
escalation outcomes, surprises and manual findings. Unknown is not success. Keep bounded
evidence links, not raw logs/secrets; distinguish each attempt and preserve corrections.

Reuse a safe project run ID or retain a unique filesystem-safe date/subject ID in the
tracker; reuse on resume, never overwrite another run. Persist separate summary/task records
before refreshing that run's compact index row after every evidence write; no duplicate rows
or monolithic history. On resume reconcile interrupted record/index updates before reporting
successful persistence, retaining existing runs and all observations. Evidence recording
never grants permission to mutate guidelines. Without association/write authority, retain
these same factual observations in the existing handoff rather than creating a store.

## Review and Acceptance

No per-task reviews: after all implementation task commits, obtain one fresh independent
final review from the owner-selected usable reviewer, not an implementation session.
Provide the full committed revision range and source/task/approval evidence, not merely a clean working-tree diff.
Review against applicable source/supporting artifacts, tasks, governing principles,
failure paths, migrations, contracts, documentation, and applicable project memory
(per discoverable `memory-handling` when required). Missing independent capability
blocks final acceptance; the implementer cannot self-certify independent review.
Derive QA from the selected
artifacts and detected project capabilities; never import another project's threat
model, data, commands, or runtime assumptions.

For each acceptance scenario report `PASS`, `FAIL`, `PARTIAL`, `NOT RUN`, or
`UNAVAILABLE` with the command or observation. Distinguish local or simulated
evidence from live acceptance. Do not call unavailable external validation passed.
Record review findings/dispositions. Fix in-scope failures, re-run affected checks,
and commit verified review fixes separately; leave blocked dependents pending.
Source/task sequencing or authorization defects return to the producing workflow's
review gate, with renewed affected approval before dependents proceed.

## Maintaining this contract

With Python 3 available, run `python3 scripts/test_intake_contract.py` and
`python3 scripts/test_batching_contract.py` from this skill directory. These static
checks cover authorization/strategy and preserved batching instructions, not runtime
model obedience. If Python is unavailable, report checks `UNAVAILABLE` and inspect
the contract manually rather than claiming automated validation.

## Finish

Return completed and pending tasks, changed files, per-task commits (or the owner's
recorded decision to skip or defer them), checks and results, integration
status, unresolved owner gates, unavailable capabilities, and the next
dependency-ready action. State separately whether implementation is complete and
whether feature acceptance is verified. Agent completion and checked boxes alone
are not acceptance evidence.
