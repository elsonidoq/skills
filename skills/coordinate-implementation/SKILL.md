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
For direct execution in fresh or resumed contexts, before preparing worker or review briefs, consult
[save-adr](../save-adr/SKILL.md)'s **Consult and propagate** contract when a discovered decision
owner or supplied accepted constraints apply. Read the whole discovered decision index, relevant
accepted records and needed supersession links; carry each applicable accepted outcome, explicit
mechanism constraint and source link into both briefs. Known supplied constraints survive unavailable
contract packaging; absent decision storage alone does not block unrelated work. Contradictory
accepted authority or uncertain current supersession stops only the affected continuation.
Missing memory or STATE is nonblocking. Preserve existing STATE/custom content and history;
no automatic summaries/indexes, reflection, inferred feedback, or execution-time feedback/routing
intake. Memory Handling remains the unified owner for planning/manual feedback authority; execution
consumes only approved constraints and gotchas.

## Prepare Approved Execution

Read actual `scripts/coordinate-implementation --help` and the [operating guide](../../docs/coordinate-implementation.md).
Resolve the executor once with
`python3 scripts/resolve-workflow-executor.py --project PROJECT_ROOT` from the suite checkout
([resolver](../../scripts/resolve-workflow-executor.py)), or reuse the exact absolute path already
resolved in the approved handoff. Add `--executor PATH` only for an explicit override; relative
overrides are project-root-relative. Otherwise only `PROJECT_ROOT/.pi/workflow-executor.json`
is selected. Pass the exact absolute stdout path as `--executor CONFIG` to the CLI or as `executor`
to the parent start tool and unchanged to downstream work. Keep downstream configuration reads
and validation; do not repeat discovery. Explicit resume retains its recorded executor input.
Never search neighboring repositories, home directories, other worktrees or historical task files,
fall back after a failed override, create/copy configuration, authenticate providers or invoke a
model merely to resolve it. Supply project, task file and executor JSON containing the
owner-selected executor/effort (provider, model, effort), without silent substitutions. There is no owner catalog or binding
assessment. SDK/dependency/authentication errors report the actual failed operation. Routine scoped technical
fixes, isolated tests/servers, necessary local/in-project dependency setup, and current-task artifact
lifecycle need no owner question; prompt delivery is text-contract evidence, not proof of model obedience or passed
checks. An earlier agent-authored task,
recovery, or handoff demand for renewed exact-resource/setup/rerun consent does not override the current scoped
launch authority; actual owner limits and manual, paid, security, data, and external-operation gates still apply.
No global install, auth
refresh, credential change, deployment, push or unrelated-work deletion is authorized. Implementation
launch authorizes ordinary use of the selected worker/reviewer models without separate paid consent.
Paid application/test APIs require separate approval: declare `paid_apis` and answer the current
terminal/attached-bridge question, or supply an already approved top-level `paid_scope` with `apis`.
A denial or missing reply launches no provider. Credentials and history never authorize paid APIs.
The unchanged grant/exclusions follow worker, fixer and reviewer prompts without repetitive questions;
additional paid APIs, including those discovered during execution, require approval before use.

## Interface Actions

- `intake --tasks FILE`: six checks only; task metadata is not an approval prerequisite.
- `start --project ROOT --tasks FILE --executor CONFIG [--run ID]`: execute sequential work.
- `status` / `history --project ROOT --run ID`: read progress or historical records without
  launching an agent or repairing old intent records.
- `resume --project ROOT --run ID`: explicitly continue a retained failed/interrupted run after inspecting
  its recorded cause and operation history; retain original input/scope/baseline and never replay completed checkpoints.
- `abandon --project ROOT --run ID`: explicitly label abandoned work, never completed effects.
  The writer lock and current recorded child/controller identities protect against overlap;
  historical process scopes are inspected, never provisioned or signalled.

## Question triage

The receiving coordinator investigates and answers routine technical diagnosis, implementation
choices, ordinary corrections and focused verification within approved authority. Missing technical
evidence calls for investigation or an actionable blocker, not asking the owner to debug. Escalate
only product decisions, consequential unresolved trade-offs, material scope/complexity/verification
expansion, separately scoped spending, or actions outside authority. Autonomous answers never
impersonate owner consent or bypass manual, paid or permission gates. Before continuing a failed
expensive worker, inspect its recorded cause and invocation; never blindly retry.

Questions use current terminal owner input when needed, without external receipt files or
Paseo/session proofs. Noninteractive questions stop with the actual question and retain partial
work; never invent an answer. “No automatic resume” forbids uninspected retry, replay and background
restart; it does not forbid an explicit, inspected continuation after an authorized coordinator-scoped
repair. For that repair, settle the failed invocation and writer lock first; keep the original worker
inside its paths and separately assign only the necessary repair paths with the retained selected
executor. Inspect the repair diff, relevant checks and its focused checkpoint before explicitly using
supported `resume` on the unfinished run. Reuse a suitable saved unfinished session, skip completed
checkpoints, and triage later routine technical questions autonomously. Unknown failure cause, a live
writer, failed/unsettled repair, or missing checkpoint facts stops that continuation rather than
permitting a retry. Workers never delegate or recursively launch the CLI; this is coordinator work,
not a new cancellation/recovery API or historical restart. If another cooperating implementation writer
holds the existing worktree lock, CLI entry waits transparently and cancellation exits cleanly without
fabricating a failed task/run or replacing that writer; platforms that cannot wait report concrete busy.

## Recover Context

Start from available summary/recent context, then selectively inspect Git, partial work,
commands and progress. `resume` uses only retained original input and operation-local checkpoint/review history under the writer lock: changed files, index, HEAD and outputs are neither failure evidence nor admission. Missing history, uncertain completed effects, an uncertain review invocation, or a known live writer stops only that unsafe continuation. For an interrupted unfinished task, only its previously recorded source paths and generated-artifact facts may be reused for the next actual edit or selective cleanup; unknown bytes remain preserved and never become an admission test. In a resumed direct run, re-establish applicable accepted-decision authority
from supplied constraints or the discovered current records; retain their outcomes, explicit mechanism
constraints and source links in the resumed worker and review briefs rather than relying on a prior
read claim. Inspect a failed run and its invocation; unknown cause stops blind retries.
Preserve partial and unrelated work. A failed API/tool operation is not permanent launch poison.
Before a new task, inspect conflicting writers and actual files; do not adopt unknown work,
replay uncertain external effects, kill unrelated processes or infer liveness from old SQL rows.
Historical graph/SDK/Git intents remain untouched, not converted to successful completion.

## Execute and Integrate

The runner retains initial history for reporting but never uses HEAD, index, dirty paths or filesystem changes as continuation admission. It never adopts or commits unknown work.
One writer runs dependency-ready tasks in sequence using ordinary SDK read/search/edit/write/command tools.
Its task brief carries applicable accepted outcomes, explicit mechanism constraints and source links;
those complement rather than replace task requirements or existing execution authority. Harmless
read/argument/edit errors can be corrected in the same conversation. SDK automatic compaction
and output continuation remain normal behavior, not fatal workflow conditions. No arbitrary workflow
size caps, deadlines, lifetime quotas or repair budgets. Do not autonomously loop expensive failed runs.

Project check commands are optional; run specified checks and report their actual outcomes with
no universal collection-count/receipt format. A nonzero required command retains its exact command, exit and output as a failed attempt and returns it to the live or compatible same-task worker with its ordinary corrective tools. The worker makes a reasoned safe scoped source/setup correction or reports the actual blocker; the runner reruns affected required commands and never checkpoints before they pass. This is not cross-task reuse, a post-review round, a skip, or an unchanged-command spin. A saved worker may enter the private same-run reuse registry only after idle settlement, real required passes, and its focused checkpoint; corrective prompts remain in that same task context, and failed/unsettled sessions are never candidates for another task. A failed check is not passed. At an actual edit or destructive
cleanup, preserve pre-existing/unknown bytes; never adopt them. Optional `owned_paths` limits source edits;
explicit task edit selections determine checkpoint paths. Optional `generated_outputs` guides selective
known-artifact regeneration/cleanup only: it is not an allowlist, registration, permission prerequisite or
commit target. New, ignored, Git-visible, deleted or undeclared output never blocks commands or checks.
The SDK is an instruction-managed coding tool, not an adversarial filesystem/command sandbox.

Inspect the actual diff and preserve unrelated staged/unstaged/untracked work. The runner creates
one focused verified owned-path checkpoint per implementation/repair task before subsequent mutation or handoff.
It uses explicit paths and normal Git hooks/signing; failed hooks/signing, whitespace, source, or ownership errors return their actual cause to the same task for safe correction; ownership conflict blocks the affected checkpoint. Then rerun affected required checks and retry normally—never configure around them. After a reported-failed or interrupted commit, reconcile that operation's selected paths, attempted parent, and actual commit before retry; retain a matching SHA without recommit. An unsafe/out-of-scope action or unrecoverable signing/authority issue reports its exact blocker. No skip/defer, No-Git fallback, broad staging, reset,
cleanup or history rewrite. Read-only/no-change makes no empty commit. No extra evidence-only checkpoint.
Dependencies release after the producer's real focused checkpoint, not an approval envelope.
Never blindly replay a Git commit after interruption; inspect the actual resulting commit first.
See the canonical [task-commit contract](../memory-handling/references/task-commit-contract.md).
Planning/standalone/bootstrap writers retain their existing checkpoint duties.

## Review and Acceptance

After task checkpoints, use a fresh independent read/search-only reviewer context. A findings-free approval completes immediately. New runs retain `owner-pair-v1` before dependent work: the first actionable rejection gets the existing scoped repair/checkpoint and a fresh original-base→actual-head rereview. Every later actionable rejection asks the actual owner; only a durable affirmative grant reserves exactly one assigned fixer and its following fresh reviewer. Another rejection asks again. Denied, empty, unavailable, malformed, nonactionable, uncertain, failed, or target-drifted stages stop with retained work and never gain a replacement pair. The existing `fixer` history role records a configured-reviewer-model correction, not a task-worker agent; repair preserves original scope and never independently accepts delivery. Historical runs without policy retain the old two-review/one-fixer limit. Resume selects the last eligible persisted stage, reuses a completed exact verdict/head without another call, and never replays uncertain invocations or commits. Additional-round recovery may dispatch a provably not-started reserved fixer once or continue a returned repair's local checks/checkpoint without another fixer call. Retain matching checkpoint SHA/parent/content facts; missing or uncertain effects stop for inspection. Dispatch validates the exact causal grant/reservation, not a numeric round allowance. Findings keep compatible `path:line - defect` or `path:start-end - defect` strings with impact/basis in ordinary prose; no literal basis suffix is required.

## Runner-configured worker role

Do NOT launch this CLI recursively, delegate, stage/commit or manage workflow state.
Implement only the selected task with normal SDK tools; correct ordinary scoped technical errors in the
same conversation, including isolated test/server and necessary local setup issues. Preserve unrelated
work; use `ask_owner` only for product decisions, substantial complexity increases, separately scoped
paid usage, or actions outside authority. Authority never proves a check passed. Leave the independent
review read-only in a fresh context.

## Maintaining this contract

Operative runtime instructions supersede older graph/custody/evidence eligibility mandates.
Historical plans/specs/approvals remain historical, not a launch checklist. Keep global assets
portable and consent boundaries intact. In Paseo, changed global skills/prompts require a fresh-session
handoff verifying checkout, revision, current approval and loaded capabilities; never ask the owner to
run `/reload` or automatically reload/restart. Elsewhere follow the host's normal activation guidance.
