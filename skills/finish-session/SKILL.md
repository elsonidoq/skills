---
name: finish-session
description: Use when closing a working session that may need documentation, unresolved-work, deployment, memory, or explicit feedback.
---

# Finish Session

Consume ended implementation and existing evidence. Route attributable durable facts to their
owners and explain the delivery to the owner. Do not reopen implementation, audit the repository,
rerun implementation checks, launch a fresh review or adjudicate acceptance. Existing workflow
acceptance requirements remain in force; closeout neither adds nor waives them.

## Step 0: Documentation Initialization Gate

Before applying the closeout workflow, read repository instructions and existing
documentation indexes only far enough to identify the project's required
documentation owners and directories. Confirm that each required owner exists
and every discovered documentation directory has the index mechanism required
by local convention. Locate the project's documentation-routing guide: the
documented rules that identify which kinds of changes require which
documentation owners. If no such guide exists, report documentation ownership
as unavailable. If the project has a persistent database, also confirm
that an authoritative database-schema document or documented set of schema
documents exists. An existing authoritative schema document satisfies this
requirement even when no convention names it. If no local convention or
existing documentation identifies the required owners or directory-index
mechanism, report documentation ownership as unavailable. For a database-backed
project, also report ownership as unavailable when neither identifies its
database-schema owner.

This is an existence check only: do not audit documentation accuracy, create
missing files, or modify any target in this step. If documentation ownership is
unavailable or any required owner or directory index is missing, report the
missing paths or owners, instruct the user to use the `initialize-coherence`
skill, and stop. Continue with the remaining steps only after all required
documentation owners and indexes exist.

## Establish attributable findings before writing

Start with `git status --short`, `git diff --name-status` and
`git diff --cached --name-status`. Inspect full diffs, identifiable session commits and relevant
untracked contents only for attributable paths; diff summaries do not include untracked contents.
Report pre-existing or uncertain attribution rather than adopting it.

Use repository instructions, relevant indexes and the documentation-routing guide to identify
existing owners. Do not initialize fallback artifacts or migrate records. Preserve existing
runbooks and authoritative documents. For a verified finding without an owner, report the gap
and ask for its location/format; a missing documentation owner routes to `initialize-coherence`.
Preserve the existing declared local register until approved cutover. For active GitHub routing,
`track-open-issue` owns target resolution and unavailable/deferred handling; missing capability or
write authority never reactivates a historical register or creates a local fallback.

Derive candidates from primary artifacts: code, configuration, schemas, generator output or an
external source explicitly configured by the repository, not session narrative alone. Inspect
only documents plausibly affected by attributable behavior or data. Compare affected schema
text with authoritative migrations, definitions or available introspection. Recompute changed
counts and name the source or generating command. Leave accurate text unchanged; mark historical
records superseded in place. Unverified claims remain `unknown`; a concrete uncertainty with
missing evidence can be an investigation candidate.

This is the candidate-before-write insertion point for optional `finish-session-jev` triage.
It does not authorize a classifier to establish truth, choose final owners or write artifacts.

Before any write, record the target's initial content and dirty state. An initially dirty target
needs explicit approval for overlap. Re-read immediately before patching; concurrent changes stop
the affected write. Preserve unrelated staged/unstaged work and custom STATE/history/gotchas.
Limit edits to authorized closeout documents, issue/deployment records and verified project
memory. Do not edit application code, tests, generated application assets or completed
implementation artifacts. Never record credentials, tokens, personal data or sensitive payloads.
No automatic STATE maintenance, routine summaries/index refreshes, reflection, evidence-only
records, changelogs, file inventories or plan/task completion bookkeeping; Git owns those histories.

## Route findings to their owners

Apply the project's routing guide first, including categories beyond these examples. Use one
canonical owner per fact; a secondary pointer is useful only for a distinct warning or dependency,
not a duplicate narrative.

| Finding | Action and result to consume |
| --- | --- |
| Current behavior, contract or convention | Update the most specific existing document; use the documented architecture owner if no more specific owner exists. Cover affected API endpoints, request/response, authentication/errors; server helpers/middleware; frontend hooks/state/components/auth flow; data ownership/lifecycle/access; module/import direction; test fixtures/helpers/conventions; operational and user-facing facts. |
| Changed persistent schema | Update its authoritative document: current tables/collections, fields/types, keys/relationships, constraints and applicable indexes. |
| Unfixed bug, risk, shortcut, missing capability or unresolved investigation | Give `track-open-issue` the verified problem, primary evidence and resumption condition. Consume its qualified issue/result or deferred candidate with missing requirement and corrective action. Do not file documentation-only facts, deploy prerequisites, memories or non-actionable claims; no candidate means no tracker operation. |
| Verified future deployment action | Reconcile the established runbook/deployment-step owner under the conditional procedure below. |
| Verified non-obvious action-triggered trap, rationale or failed approach | Use `memory-handling` for the associated project store and gotcha evidence; consume its entry/write or unavailable result. |
| Explicit future-directed user guidance | Use `memory-handling` for provenance and bounded guidance authority, not inferred lessons. Consume its authorized entry or no-write result. |
| Explicitly approved consequential decision needing durable rationale | Use `save-adr` for canonical decision discovery/history and consume the decision record/link. Do not create routine ADRs, retrospective backfill or agent-inferred decisions. |

Load a routed skill before use. If unavailable, report the affected route and retain its candidate,
evidence and corrective action rather than substitute an owner. Documentation, schema, runbooks,
issues, memory and decisions retain their distinct jobs.

Run a declared, known-safe, bounded documentation generator only for the affected area, then
inspect its diff. Ask before an expensive or broad generator. If it can change application code,
tests or generated application assets, do not run it; report the command as a verification gap.

## Deployment, when relevant

Enter only for concrete deployment implications in attributable work or verified deploy evidence
that can change an existing entry. Otherwise report `not examined: no deployment-relevant evidence
in attributable work` without inspecting deployment state or its owner.

Determine `deployed`, `not deployed` or `unknown` from repository evidence or user-provided context.
Record verified prerequisites such as migrations, configuration/service setup, cache invalidation,
regeneration or release ordering even for `not deployed` or `unknown`; state how that affects the
entry lifecycle. Do not invent hypothetical work or execute deployment procedures. Close/archive
an entry only when confirmed deploy evidence proves completion; preserve useful history.

Each entry states timing, environment, procedure/command with provenance, verification/success
condition and verified rollback/irreversibility. Record a verified prerequisite even if its procedure
is incomplete: mark each missing field `unknown`, name needed evidence and its resolving owner/action.
Never infer commands, rollback steps or environment state.

## Memory, when needed

Enter only for a routed gotcha, explicit future-directed feedback or an already-discovered project
instruction requiring an index check; otherwise report `not needed` without searching for storage.
Use `memory-handling` to verify the one project association, read the whole index and matching
entries, reuse related entries and recheck after writes. Missing optional storage is nonblocking;
never substitute global memory or create storage implicitly. Gotchas retain trigger, consequence
and evidence; guidance retains actual user provenance and future trigger/action, not a surprise test.
Clear bounded feedback needs no routine second approval; ambiguity asks, and explanation-only,
no-feedback or explicit no-write cases write nothing. Its local-path/symlink and sensitive-data
protections apply.

After memory writes, check only thresholds/hooks configured for that verified store. No breach
means `not needed`. On a breach, use a compactor only after inspecting its definition for explicit
project targeting, bounded memory/documentation writes and dirty/concurrent protection. Record and
compare its prospective targets immediately before invocation; never compact unsaved findings.
If unavailable, report `compaction needed` with the measured breach and leave it to the user.

## Issue-linked delivery

After actual implementation, specified checks, focused checkpoints and fresh independent
review, use `track-open-issue` for the associated qualified issue and operation-scoped
tracker authority. It owns tracker mutation, reconciliation and readback; consume those
observed outcomes for the delivery report. Present the same meaningful executive text in the issue and current owner
chat: result and important changes, actual verification and limits, review focus, exact reviewed
commit, attributable task/repair links, unrelated range context and acceptance status. Distinguish
internal completion from awaiting explicit owner acceptance. Do not treat a whole commit range
as attributable without inspection.

If real feedback occurs, link corrections by purpose: approved implementation/internal-review
fix, owner-review correction, or new/changed requirement. Renew applicable approval for new
requirements; after correction and applicable checks/review, present the new exact reviewed SHA.
Acceptance of an earlier revision is not acceptance of the new revision. Retain the actual feedback,
correction links and explicit acceptance trace. Close only after explicit acceptance of the
presented revision and separate operation-scoped closure authority; read back the closure.

For every known delivery PR, use `track-open-issue` to confirm two-way traversal:
PR → qualified delivery issue and issue → qualified PR, regardless of trace host.
A PR-hosted trace also needs issue → every confirmed trace part. Reuse verified body or
comment links; append only missing link comments under actual run/target/`link_comment`
authority. Confirm full comment body, identity and destination independently; incomplete
pages, missing authority or uncertain readback mean incomplete linkage, never success.
Do not create a PR, push, edit issue/PR bodies or change state to establish links.

When a delivery PR is discovered after finish, establish only missing reciprocal links
and refer to the already confirmed trace. Do not republish the trace, rerun implementation
or reopen review. Late linkage does not change the reviewed revision, owner acceptance
or closure authority. Trace/link comments do not require problem-body quality review;
a substantive problem-body change still does. Changed global skills need the host's normal
activation procedure; in Paseo prepare a fresh-session handoff, not `/reload`.

Inspect uncertain publication or readback before retry. If only issue or chat publication
succeeded, report the partial result and retry only the missing operation after inspection.
Missing tracker capability or authority defers the affected operation with a corrective action;
it does not prevent an authorized chat report. Unobserved feedback, acceptance and closure are
NOT VERIFIED, not a reason to manufacture them. No automatic RCA, skill edit, PR or unrelated
issue change follows delivery or acceptance.

## Retention and recovery

Consume existing results, full-range/cumulative repair-review outcomes and authoritative runner
status as needed. Worker reports or `implementation_complete` alone do not prove acceptance.
Missing evidence is `unknown` or `NOT RUN`, not another closeout gate. Route unfinished findings
to the tracker, not implementation repair. Recovery uses available summary/recent context and
selective artifact/Git/check/runtime reconstruction; reconcile active/unknown children before
replacement, never guess completion or blindly retry.

Keep SQL/Pi evidence needed for active recovery or explicit retention, including paid-data and
failure-evidence requirements. Completed databases, transcripts, screenshots and temporary reports
need no automatic archive. Retain required facts in existing owners, not a session ledger. This
distinction grants no deletion permission.

At branch/worktree integration, Git merges source, not runtime state: keep workflow databases
independent and preserve legacy tracked-database precautions. Main into a worktree needs no database
transfer. For requested completed-monitor-history retention, consult the installed
[monitor cutover and history guide](../../workflow_monitor/README.md).
`workflow-monitor-preserve` and its capture helpers are historical, not current interfaces. Verify
an available compatible historical procedure and authority, or report the capability gap and retain
the required source. No silent archive, database conflict-resolution substitute, merge, migration
or deletion authority follows.

## Worktree-removal readiness, only when requested

Apply only when the owner requests worktree closeout or deletion readiness, for host-created
(including Paseo) and manual worktrees alike. An excluded worktree is `not assessed`. Use context,
Git state and targeted reads of attributable or potentially unique untracked/ignored files, not a
recursive temporary-file audit or assumptions from directory names. Check only:

1. **Source retained:** required commits must be reachable from the intended retained branch,
   not only the disposable branch. Inspect outstanding tracked and relevant untracked source;
   verify remote inclusion only when required. No unauthorized merge, push or discard.
2. **Information retained:** route still-unique required facts through the routing table and verify
   their owners survive removal (retained-branch documentation or external tracker). Reuse recorded
   facts. Temporary evidence is disposable after completion except for active recovery/explicit
   retention. A potentially unique unknown asset needs a specific ownership/retention decision,
   not silent disposal or blanket archival.
3. **Dependencies independent:** check known required processes, mounts, configurations and private
   runtime assets for worktree dependence. Use project-approved persistent storage; an ignored
   directory is neither independence nor backup. Do not relocate an independent asset merely to rename it.

Report **ready to delete**, retained branch and durable owners only when these checks support it.
Otherwise name the missing information/dependency, affected removal and corrective action. Readiness
is not permission to delete, stop services, migrate, merge or push. Ask only for consequential
retention, ownership or permission choices; no file registry, fresh test campaign or automatic archive.

## Validate and report

Validate only links, issue references, memory-index entries and supersession pointers changed by
closeout. Apply the shared [task-commit contract](../memory-handling/references/task-commit-contract.md)
to authorized retained closeout artifacts before reporting; read-only/no-change work makes no empty commit.

State implemented, verified and deployable separately, with evidence for each positive claim. Report
owners used and artifacts changed; documents checked and generator status; unresolved work and tracker
result; deployment state/prerequisites or why not examined; memory/guidance writes and compaction or
`not needed`; changed-reference checks; skipped candidates, attribution uncertainty and unverifiable
claims. STATE remains untouched. Do not imply that initialization or an inapplicable route ran.
