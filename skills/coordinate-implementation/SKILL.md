---
name: coordinate-implementation
description: Use when implementing a reviewed Cerca feature in OpenCode from existing spec, plan, and tasks artifacts.
---

# Coordinate Implementation

Input: `/coordinate-implementation <spec_dir>`. Work in the current workspace.
If omitted, use an unambiguous current plan in AGENTS or feature.json; verify its
source epic before acting. If there is no identifiable feature, ask for its path.
This is a global skill (`~/.config/opencode/skills/coordinate-implementation/SKILL.md`),
available in any OpenCode project — there is no project-local wrapper command.
Invoke it directly with the `skill` tool, or by name in prose. Restart OpenCode
after skill changes.

## Non-negotiable: one subagent per task, strictly sequential

Every task in a batch gets its own delegated `task` call — never bundle two or
more task IDs into a single subagent prompt to save overhead. Tasks execute one
after another, validated before the next starts; batches execute one after
another too. Nothing in this skill runs subagents in parallel. See "Execute each
batch" for the full rule and the resume-vs-fresh-call policy.

## Load and verify

Read `AGENTS.md`, initialized `.specify/memory/constitution.md`, and the selected
`spec.md`, `plan.md`, `tasks.md`; all three feature artifacts are required.
Read research, data-model, contracts and quickstart when present. Resolve the
source epic through spec metadata or matching `.opencode/epics-workflow/` state
(if present); that state's `epic_file` field names the actual epic document to
read — there is no single hardcoded epic bundle file. Read that resolved file's
section and its own preamble (the text before its first epic heading).
Do not infer the epic solely from feature numbering: spec 001 can be Epic 0.
If provenance is ambiguous, ask before implementing. If only legacy state exists,
follow the manager's State migration rules before using it as provenance.

Follow the source/dependency and feature-context rules in the `epics-manager`
skill without starting its planning pipeline.
Bind `SPECIFY_FEATURE_DIRECTORY` to the selected absolute directory; ensure the
feature.json pin matches (preserving unrelated fields). From the repo root run:

```sh
.specify/scripts/bash/check-prerequisites.sh --json --require-tasks --include-tasks
```

Verify returned FEATURE_DIR matches the selected spec. Read
`.opencode/command/speckit.implement.md` for checklist gates, task execution
and completion rules; apply it only to the assigned batch rather than all tasks.
Supply batch IDs and verified feature context as its `$ARGUMENTS`, following the
command body directly. `/speckit.implement` is a user command, not a shell tool;
do not launch a nested CLI session or follow generated handoffs automatically.
Do not regenerate artifacts during implementation.

Validate upstream contracts, accepted ADRs and story preconditions against actual
files and evidence. A manager state of done is only artifact readiness. Missing
required producers block their consumers; a future output of this batch is not a
missing input. Read explicitly referenced cross-epic sections. Honor settled
decisions, target shapes, NOT included, acceptance criteria and approved deferrals.
If the constitution is still a template, return to the manager's constitution
preflight before implementing; do not invent principles in a batch.

## Partition

Inspect git status and record the starting commit plus existing local changes.
Establish relevant, inexpensive local test baselines from the actual plan and
available project commands. Do not assume an app/dev server exists yet or that one
will never exist. Record unavailable checks as not run.

Partition unchecked tasks into sequential story batches. Include setup with its
first consumer when practical; group shared-file work and honor task dependencies.
**A batch must be homogeneous by model class.** Every **delegated** task carries a
`[sonnet]` or `[opus]` tag; a batch may contain only tasks of one class. A
`[coordinator]` task is coordinator-owned and is never delegated — perform it
directly (like review/partition work) and exclude it from model-class batching. If a
story mixes classes, split it into consecutive batches by class, preserving
dependency order — a batch containing both a sonnet and an opus task is never
allowed. Follow the
preamble's one-story-at-a-time guidance. Show task IDs, model class, scope and
dependencies, then proceed. Do not require a fresh approval for routine batching.
Do not merge research/ADR gates with dependent implementation so tightly that the
acceptance gate disappears.

## Execute each batch: one subagent per task

**Delegation is mandatory and scoped to a single task, never a whole batch.**
Dispatch a separate `task` call for every individual task ID, even when several
tasks are small, touch the same file, or feel natural to combine. **Set
`subagent_type` from the task's model tag** — `"sonnet"` for `[sonnet]` tasks and
`"opus"` for `[opus]` tasks; never substitute `"general"` for a tagged task, and
never invent a tier. All tasks in a batch share one tag by construction (see
Partition), so every dispatch in a batch uses the same `subagent_type`. Batches
group tasks for sequencing and review, not for delegation — never fold two or more
task IDs into one subagent prompt to save overhead. Tasks execute strictly one
after another, in dependency order: wait for a task's result and validate it (see
below) before dispatching the next task's subagent. Batches also run strictly
sequentially; nothing in this skill dispatches subagents in parallel.

| Temptation | Why it's still wrong |
| --- | --- |
| "These two tasks touch the same file, may as well do them together" | Shared files justify *ordering* the two calls back to back, not merging them |
| "This task is trivial, not worth its own subagent call" | Task size doesn't change the rule; a one-line task still gets its own delegated call |
| "I'll just implement this one directly, it's faster" | Only coordinator-owned work (git status, baselines, partitioning, review) happens locally; every task is delegated |

**Resume only on substantial context overlap, otherwise spawn fresh.** Default to
a fresh `task` call per task ID. Resume a prior subagent via its returned
`task_id` instead of spawning fresh only when the new task shares substantial
context with a specific task the coordinator already delegated — the same
primary files, the same module, or direct continuation of unfinished work —
such that re-briefing a fresh agent would mostly re-explain what that agent
already has loaded. This can cross batch boundaries: a task in batch 3 may resume
the subagent from a batch 1 task if the overlap is real. Do not resume merely
because a call is recent, to avoid writing a fresh brief, or to bundle unrelated
tasks — insufficient overlap means spawn fresh. **Resume only within the same
model class**: never resume a sonnet task's subagent for an opus task, or vice
versa; a cross-class continuation gets a fresh agent of the correct class. State
the choice made (fresh, or resumed `<task_id>` and why) when reporting the task's
outcome.

The model class comes from the task's own tag via `subagent_type`; there is no
other per-call model parameter. Do not substitute a different class to save cost,
and do not silently reconfigure the user's agents or session model. Never claim a
delegation that did not happen. Without
delegation (no `task` tool available or permitted), run the same scoped work
locally, followed by a separate review pass, and say so explicitly. Subagents
share this checkout; do not assume isolated worktrees or inherited shell
bindings. Include the feature-directory binding in every brief and every script
call.

Each brief includes:

- Goal, the one assigned task ID (plus sibling task IDs in the same batch for
  sequencing awareness — the subagent still executes only its own task), story
  acceptance criteria and allowed files.
- Absolute workspace/spec paths, canonical epic heading and preamble, relevant
  accepted ADRs/contracts, constitution and AGENTS.
- Prior recomputed handoff, applicable requirements, known baseline failures.
- Required checks, upstream gates, scope exclusions, and authorized runtime work.

Ask agents to return changed files, the task ID with evidence, checks and
results, incomplete work, out-of-scope discoveries, and `Handoff context`
containing non-obvious reasoning and any docs/contracts/configuration left stale.

After every task, inspect the diff and evidence before marking that task `[X]`.
Do not equate a report or unchecked assertion with completion. Preserve other
worktree changes. Recompute the next task's brief by reading the `handoff-prompt`
skill and verifying its cited paths and baseline; the previous agent's summary
is input, not authority. Once every task
in a batch is checked off, persist completed work and the next task/gates in
`<spec_dir>/STATE.md` (create when needed); also update root `STATE.md` if it
already exists and owns project progress.

**Commit each landed batch.** Once a batch's tasks are checked off and validated,
commit exactly that batch's changes as one commit, following the repo's commit
conventions. Stage only the files that batch produced — never unrelated worktree
changes — and never commit secrets, `.env` or `.local/` evidence. If the running
agent's own instructions forbid committing without an explicit request (for example
an AGENTS.md/CLAUDE.md "do not commit autonomously" rule), do not commit and do not
silently skip: ask the user via the `question` tool how to handle commits — commit
after each batch, commit once at the end, or leave commits to the owner — and
follow that answer for the rest of the run. Historical permission from a prior
session is not continuing authorization, and a prior run's answer does not carry
over to a new run.

The coordinator handles questions using OpenCode's `question` tool with its actual
schema; the general subagent returns unresolved questions rather than asking the
user itself. If unavailable, denied or noninteractive, save progress and ask one
concise question in the final response. Persist accepted answers in feature STATE.md.
Keep material open decisions pending until answered; carry prior authorization
forward. A batch cannot reopen a settled product choice as an implementation detail.

## Review and QA

Review the accumulated task diff against the starting baseline, including interactions
between batches, frozen schemas, failure paths, and required documentation updates.
Fix in-scope defects and run the checks relevant to those fixes.

Delegate QA when available, or perform it locally. Give QA the selected spec/plan,
epic, shared preamble, initialized constitution, completed work and known limitations.
Derive QA from those artifacts: Cerca includes web and worker surfaces, messaging
consent/caps, grounded quotes and model metering where the selected epic calls for
them. Do not import another project's threat model or hardcode an absent runtime.

Use documented local commands, fixture data, provider fakes and appropriate browser
checks when available. For each acceptance scenario report PASS / FAIL / PARTIAL /
NOT RUN with the command or observation. Distinguish local correctness from empirical
spikes and pilot outcome metrics: fake-provider tests do not prove real template
approval, model accuracy or merchant response rates. Never claim live acceptance
from static inspection.

Fix in-scope failures and recheck affected scenarios. Do not start costly evals,
external messages, deployments or live infrastructure tests without the necessary
user authorization. If such evidence is required but unavailable, record the exact
remaining gate and stop dependent work; do not loop indefinitely or call it passed.

Check whether the changes stale related docs, shared contracts, config, task state
or AGENTS's plan pointer. Update affected local artifacts within scope; constitution
amendments require an explicit decision. Keep genuine deferred findings with evidence
in the feature STATE.md or an existing project issue register; use its conventions,
deduplicate, and preserve history. Do not create unrelated document indexes.

## Finish

Report what was implemented, task completion, every changed file, checks/results,
commits made or deferred, remaining acceptance gates, deferred discoveries and any
stale artifacts. State
separately whether code is complete and whether epic acceptance is verified.
Give the exact workspace and next task/gate for continuation. Never mark an epic
implemented just because every agent returned or the manager's artifacts are done.
Resume with `/coordinate-implementation <spec_dir>` in that workspace; read the
feature STATE.md and revalidate gates even in a fresh OpenCode session. A task ID,
chat session, or `todowrite` list is not durable implementation state.
