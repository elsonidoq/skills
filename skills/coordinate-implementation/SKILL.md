---
name: coordinate-implementation
description: Use when executing requested implementation tasks through the existing workflow CLI or inspecting its history.
---

# Coordinate Implementation

The existing CLI runs sequential tasks with the installed Pi SDK, actual project commands,
focused Git commits and one fresh read-only independent final review. SQLite stores ordinary
progress, not effect proof or execution eligibility. No graph, manifest, catalogue, cgroup,
resource hashes, original-session receipts or parent-transcript protocol is required.

## Load and Verify

Read the requested tasks and project instructions. Ordinary owner-authorized coding needs no
new planning/approval cycle. Task intake has exactly six linter checks: file exists/readable;
JSON/YAML parses into a task list; each task has an ID and work description; unique IDs;
existing dependency references; acyclic dependencies. File order need not be sorted. An empty
list reports no tasks, creates no storage and reserves nothing. Optional context stays intact.

Load technical gotchas through `memory-handling`: whole index first, then matching entries.
Missing memory or STATE is nonblocking. Preserve existing STATE/custom content and history;
no automatic summaries/indexes, reflection or inferred feedback. The separate
[project coordination contract](../memory-handling/references/project-coordination.md) retains
feedback-only ownership for manual/planning work.

## Prepare Approved Execution

Read actual `scripts/coordinate-implementation --help` and the [operating guide](../../docs/coordinate-implementation.md).
Supply project, task file and executor JSON containing the owner-selected executor/effort
(provider, model, effort), without silent substitutions. There is no owner catalog or binding
assessment. SDK/dependency/authentication errors report the actual failed operation. No automatic
install, auth refresh, global settings changes, deployment or legacy restart is authorized.
Ordinary approved model tokens need no financial receipt. Obtain narrow permission for
separately chargeable or irreversible external actions outside requested coding.

## Interface Actions

- `intake --tasks FILE`: six checks only; task metadata is not an approval prerequisite.
- `start --project ROOT --tasks FILE --executor CONFIG [--run ID]`: execute sequential work.
- `status` / `history --project ROOT --run ID`: read progress or historical records without
  launching an agent or repairing old intent records.
- `abandon --project ROOT --run ID`: explicitly label abandoned work, never completed effects.
  The writer lock and current recorded child/controller identities protect against overlap;
  historical process scopes are inspected, never provisioned or signalled.

Questions use current terminal owner input when needed, without external receipt files or
Paseo/session proofs. Noninteractive questions stop with the actual question and retain partial
work; never invent an answer. No automatic resume, replay, control-mailbox or background daemon.

## Recover Context

Start from available summary/recent context, then selectively inspect Git, partial work,
commands and progress. Inspect a failed run and its invocation; unknown cause stops blind retries.
Preserve partial and unrelated work. A failed API/tool operation is not permanent launch poison.
Before a new task, inspect conflicting writers and actual files; do not adopt unknown work,
replay uncertain external effects, kill unrelated processes or infer liveness from old SQL rows.
Historical graph/SDK/Git intents remain untouched, not converted to successful completion.

## Execute and Integrate

The runner establishes baseline HEAD and index/worktree ownership. It never adopts or commits unknown work.
One writer runs dependency-ready tasks in sequence using ordinary SDK read/search/edit/write/command tools.
Harmless read/argument/edit errors can be corrected in the same conversation. SDK automatic compaction
and output continuation remain normal behavior, not fatal workflow conditions. No arbitrary workflow
size caps, deadlines, lifetime quotas or repair budgets. Do not autonomously loop expensive failed runs.

Project check commands are optional; run specified checks and report their actual outcomes with
no universal collection-count/receipt format. A failed check is not passed. Never adopt existing dirty files.
Optional `owned_paths` limits edits; otherwise ownership derives from the actual clean-baseline task edits.
The SDK is an instruction-managed coding tool, not an adversarial filesystem/command sandbox.

Inspect the actual diff and preserve unrelated staged/unstaged/untracked work. The runner creates
one focused verified owned-path checkpoint per implementation/repair task before subsequent mutation or handoff.
It uses explicit paths and normal Git hooks/signing; failed hooks/signing or ownership conflict block
that operation, never configure around them. No skip/defer, No-Git fallback, broad staging, reset,
cleanup or history rewrite. Read-only/no-change makes no empty commit. No extra evidence-only checkpoint.
Dependencies release after the producer's real focused checkpoint, not an approval envelope.
Never blindly replay a Git commit after interruption; inspect the actual resulting commit first.
See the canonical [task-commit contract](../memory-handling/references/task-commit-contract.md).
Planning/standalone/bootstrap writers retain their existing checkpoint duties.

## Review and Acceptance

After task checkpoints, use one fresh independent reviewer context with only read/search tools,
not the worker's conversation. Review the actual full committed range and relevant files with
continuation; no provenance/evidence hash or SQL disposition is required. Concrete findings stop
acceptance and are honestly reported with retained commits. Address findings in requested scope,
rerun affected checks and obtain independent review; material scope changes need owner input.
Do not relabel findings as resolved, substitute the writer as reviewer or claim unperformed checks.

## Runner-configured worker role

Do NOT launch this CLI recursively, delegate, stage/commit or manage workflow state.
Implement only the selected task with normal SDK tools; correct harmless local errors in the
same conversation. Preserve unrelated work, use `ask_owner` only for material scope/permission
questions, and leave the independent review read-only in a fresh context.

## Maintaining this contract

Operative runtime instructions supersede older graph/custody/evidence eligibility mandates.
Historical plans/specs/approvals remain historical, not a launch checklist. Keep global assets
portable and consent boundaries intact. After adopting changed global skills/prompts, run `/reload` in pi.
