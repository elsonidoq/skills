---
name: coordinate-implementation
description: Use when starting, inspecting or explicitly resuming approved implementation through the executable workflow.
---

# Coordinate Implementation

A thin interface to the installed `coordinate-implementation` CLI. Python LangGraph/SQLite
owns orchestration and durable execution authority; Pi persistence is conversation data.
The interface may launch, read status/pending, relay authorized inputs and explain recorded
blockers. It cannot select tasks, models, sessions, retries, repairs, commits or acceptance.
An explicitly owner-approved instruction-managed delivery exception uses bounded writers and
the shared checkpoint contract rather than this CLI; it is not another runtime mode.
Do not bootstrap a refactor through the runtime being changed when that route is excluded.
No background LLM decides workflow transitions. No subjective execution batches, task-count
routing, model escalation or coordination-feedback/STATE paperwork.

## Load and Verify

Read the requested task input and project instructions. Ordinary owner-authorized coding
requires no new planning or approval cycle. Intake has exactly six linter checks: input
exists/readable; JSON/YAML parses into a task list; each task has an ID and work description;
IDs are unique; dependency references exist; and dependencies have no cycles. Derive order
from dependencies, not file order. Empty lists report no tasks without reservation/launch.
No required sources/hashes, approvals, order/context groups, gates, envelopes, execution intent
or model assessments. Useful existing optional fields remain valid without regeneration.

Load technical gotchas through `memory-handling`; approved constraints already belong in the
task contract, not an LLM feedback loop. The [project coordination contract](../memory-handling/references/project-coordination.md)
retains explicit feedback-only ownership for separately authorized manual/planning work.
Missing coordination store or STATE is nonblocking. No automatic STATE creation, editing or removal.
Preserve existing STATE/custom content, technical gotchas, history and unrelated dirty work.

## Prepare Approved Execution

Resolve the CLI from the authorized suite/isolated installation. Read its actual `--help`;
[operating documentation](../../docs/coordinate-implementation.md) and
[schema owner](../../docs/coordinate-implementation-schema.md) describe the supported version.
No silent provisioning: missing Python dependencies, pinned SDK/Node, credentials/catalog,
Git authority, approved containment or mode-specific question capability is an exact blocker.
Do not install, refresh auth, change global settings/services or substitute bindings.

Supply actual project/task/run settings and preserve the owner-selected executor/effort
without silent substitutions. `intake` needs no owner catalog, binding assessment or approval
input. Full nonempty `start` still needs `--workflow`, `--manifest`, `--containment` and the
remaining graph/host/session machinery; its deletion is a separate checkpoint. Installed
wheels still use `--suite-root` for actual resources. Do not claim full six-check startup yet.
Ordinary selected-model usage needs no financial approval receipt. Require actual narrow
permission for separately chargeable/irreversible external actions at that action boundary.

Standalone mode uses portable pending/answer/control commands without Paseo. Interactive-parent
mode requires the registered transport, actual launching-parent identity/permissions and
registered ask_user capability; no silent manual-polling fallback. Use the scoped original
question and parent-answer callback, never historical recipient IDs or invented receipts.

## Interface Actions

- `start`: launch the requested work; task metadata is not an approval prerequisite.
- `status` / `pending`: read authoritative SQLite from another process, without agent launch,
  projection repair or background-continuation claims. Host exit stops execution.
- `answer`: relay genuine bound owner input through the CLI's external trusted authority path;
  a worker-created approved file, opaque ID or prose assertion cannot authenticate an answer.
- `control`: submit bound inquiry/steer/follow-up/pause/cancel. Received, queued, SDK-delivered
  and worker-acknowledged differ; enqueue is not consumption/compliance or instant preemption.
- `resume`: only after diagnosed remediation and explicit current scoped recovery authority.

For an eligible interactive question, the runner wakes the SAME launching interface. Read the
current scoped request, actually invoke registered
ask_user with exact options/context and submit parent-answer. The facade never chooses graph
outcomes. Unknown UI invocation blocks reasking; UI loss leaves durable pending, not success.
Accepted answers pin the ORIGINAL saved worker conversation and role; missing/unsafe original
or changed scope blocks for explicit recovery/producing renewal, never fresh-session substitution.
Optional headroom telemetry is recorded, not a veto. No direct ask_user in workers.

## Recover Context

Start from available conversation summary/recent context; do not assume retained tokens.
Selectively reconstruct only uncertain authorization, completion, Git HEAD/diffs/index ownership
and actual check/commit evidence from approved artifacts, SQLite/status and Git. Unknown
approval/completion blocks; never guess completion or repeat commits. Reconcile recorded and
unrecorded active children and legacy writers: a running child means inspect/wait, not duplicate
dispatch; unknown child status or missing runtime evidence stops replacement. Inspect a failed
run and its invocation before targeted recovery; unknown cause stops blind retries.
Preserve partial and unrelated work. No required new narrative ledger or snapshot.

## Execute and Integrate

The runner establishes baseline HEAD, allowed paths, index/worktree ownership and durable
effect identity; a worker never adopts or commits unknown work. It alone executes/audits real
specified project checks and actual diff, then creates one focused verified owned-path
checkpoint per implementation/repair task before subsequent mutation or handoff. No skip/defer
question, No-Git fallback, broad staging, hook/signing bypass, configure-around or history rewrite.
Read-only/no-change creates no empty commit. See the canonical [task-commit contract](../memory-handling/references/task-commit-contract.md).
Planning/standalone writers and an ongoing instruction-managed bootstrap retain their existing
checkpoint duties; do not recursively hand an ongoing migration to this entry.

Project check commands are optional. Run relevant specified checks after work and report
actual outcomes; no universal collection-count/receipt contract. `owned_paths` optionally
limits edits; absent it, claim only clean unchanged paths immediately before actual tool edits.
Never adopt existing dirty files or stage arbitrary post-run changes. Use explicit-path
commits, preserve unrelated staged/unstaged/untracked work, normal hooks and signing.
Audit actual diff, focused commit/SHA, check outputs and residual owned changes; a report or
clean tree alone is not proof. No extra evidence-only checkpoint. Dependencies release after
the producer's real focused checkpoint, not an approval envelope.

Before repair inspect run/invocation, partial commits and check evidence. Targeted repair retains
the same original contracts and reruns invalidated proof only. Unknown cause blocks blind restart;
Clean retry is exceptional, with safe ownership and applicable owner gates. Preserve valid work
and prior attempts. Runner alone reconciles matching checkpoint receipts against baseline/actual
diff/tree/current Git, never blind Git replay. Live/unknown effects, failed hooks/checks/signing or
ownership conflict block. Actual owned cgroup empty AND partial-file/Git reconciliation precede
replacement/checks/commits; no PID-only fallback. Cgroups are trusted single-host/same-UID process
custody, not a filesystem sandbox or remote/adversarial/power-loss guarantee.

## Review and Acceptance

No per-task reviews are imposed. Obtain one fresh independent final review, not an implementation
session, of the actual full committed base/head range with source/tasks/approval and criterion
evidence references. Reviewers read committed base/head/diff and source files with continuation;
no embedded binary bundle or document-byte/SDK-delivery attestation is required.
Missing reviewer blocks final acceptance. Schema findings remain read-only; authorized correction
tasks receive separate focused verified commits, affected checks and renewed current-range review.
Every finding has a disposition; changed scope returns to owner/producing gates. Distinguish
implementation complete from accepted. Return every REQUIRED item disposition, exact ordered
baseline/result SHAs, actual proof, residual state and selected versus observed profile.

## Runner-configured worker role

When this skill is explicitly loaded by a runner-configured implement/repair/review node, the
node's supplied task/role is authoritative: implement or repair ONLY its owned outcome using
allowed gateway tools, or review read-only using the result schema. Do NOT launch this CLI,
delegate, select work/profiles, stage/commit or manage workflow state. Return proposed results,
not mechanical verification/acceptance claims. Use request_owner_input only for genuinely
necessary manager-answerable unexpected decisions, never technical trivia or direct ask_user.
The runner owns all checks, Git, repair bounds and independent acceptance.

## Maintaining this contract

Run affected focused contract and runtime tests in the approved isolated environment. Historical
migration/installation/UI proof programmes are not ordinary readiness gates. Static guards
prove contract sensitivity, not universal model obedience. Changed global skills/prompts require
`/reload` in pi when adopted; never automatically activate a global installation.
