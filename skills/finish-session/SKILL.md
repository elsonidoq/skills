---
name: finish-session
description: Use when closing a working session that may need documentation, unresolved-work, deployment, memory, or temporary current-execution state closeout.
---

You are closing a working session. Preserve durable knowledge without turning closeout into a repository audit.

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

## Core Invariants

1. Affected authoritative documentation describes what is built now.
2. Discovered work deliberately left unresolved has one canonical owner: `docs/open_issues.md`.
3. For a deployed project, deploy-time work pending since the last confirmed deploy has one canonical owner.
4. Memory contains only trigger-first gotchas not apparent from code and authoritative documentation.
5. The memory index remains usable.
6. A project with a persistent database has authoritative schema documentation that describes its current tables or collections, fields and types, keys and relationships, constraints, and indexes where applicable.
7. The project's temporary current-state document holds only ongoing concurrent work: active, paused, blocked or pending review/acceptance/owner gates. Update current items in place and remove verified finished items; never retain terminal dispositions, durable facts, completed-work summaries, file inventories or per-task ledgers.

## Safety Rules

- Start with `git status --short`, `git diff --name-status`, and `git diff --cached --name-status`. From those summaries, inspect full diffs and relevant untracked files only for paths attributable to this session; neither diff command includes untracked contents. Treat pre-existing or unattributable changes as out of scope and report the uncertainty.
- Record each prospective target's initial dirty state and content before editing. Do not edit a target that was already dirty unless the user explicitly approves that overlap. Re-read and compare it with the recorded content immediately before applying a patch; if it changed concurrently, stop and report the conflict.
- Do not discard, stage, commit, or rewrite unrelated work. Limit edits to closeout documentation, issue or deployment records, a verified project memory store, and the attributable current-state block in Step 6. Do not modify application code, tests, generated application assets, or completed implementation artifacts.
- Verify a durable claim against its primary artifact: code, configuration, schema, generator output, or external source explicitly configured by the repository. Never record an unverified claim as current truth.
- Do not write credentials, tokens, personal data, or sensitive payloads. Use redacted placeholders such as `$SERVICE_TOKEN`.
- Do not execute deployment procedures. Do not invent deployment commands, rollback steps, or environment state. Record an unknown or verification gap instead.
- Git owns changelogs, completed-work summaries, file-and-line inventories, and plan/task completion metadata. Do not add them to docs, issues, deployment steps, or memory.

## Step 1: Discover Existing Owners

Read repository instructions (`AGENTS.md`, `CLAUDE.md`, or equivalent) and the relevant indexes. For unresolved issues, this skill set uses the canonical local register `docs/open_issues.md` and the `track-open-issue` skill. Do not route issues to another local or external tracker or migrate unrelated records. For other information, preserve existing authoritative documentation owners and runbooks.

Do not initialize fallback artifacts during discovery. If a verified finding has
no owner, report the missing owner and ask the user to choose its location and
format, except for unresolved issues whose location is fixed as above. A missing
issue register may be initialized only for a verified candidate in Step 3 under
`track-open-issue`, after Step 0's gate is satisfied. Preserve the existing format
and identifiers when an artifact already exists.

## Step 2: Derive Candidate Findings From Attributable Work

Use the actual working tree, relevant commits made during the session when identifiable, code, configuration, schemas, and generated output. Do not rely on the session narrative alone.

Inspect only documents plausibly affected by changed behavior or data. This can include architecture docs, database-schema documents, README files, API/reference docs, configuration examples, runbooks, generated docs, and active decision records. For database-backed projects, compare schema documentation with the authoritative migrations, schema definitions, or database introspection available to the repository; update the affected schema document when tables or collections, fields, types, keys, relationships, constraints, or indexes changed. Leave accurate text unchanged. Recompute any count changed by attributable work and name its source or generating command. Mark historical records superseded in place rather than rewriting history.

If the repository declares a targeted, known-safe, bounded generator whose outputs are closeout documentation relevant to the changed area, run it and inspect its diff. Ask before running an expensive or broad generator. Do not run a generator that may modify application code, tests, or generated application assets; report its command as a verification gap instead.

## Step 3: Route Each Verified Finding

Use one canonical owner. A secondary pointer is allowed only when it provides a distinct warning or makes a dependency discoverable; never duplicate a full narrative. In particular, documentation explains current system behavior while a memory may separately warn how a future action can break it.

First apply the project's documentation-routing guide. It defines its own
material change categories and their documentation owners; treat it as
authoritative and do not limit closeout to the examples below. The examples are
non-exhaustive seed guidance for a repository that has not yet defined more
specific categories. The filenames illustrate a `docs/architecture/` layout
only. Preserve an equivalent established owner rather than creating a
competing document. If the guide identifies a missing owner, report it and
direct the user to `initialize-coherence` instead of selecting a path
during closeout.

| Changed area | Required documentation | Example owner |
| --- | --- | --- |
| New endpoint or changed API contract | Endpoints, request and response contracts, authentication and error behavior | `docs/architecture/api-conventions.md` |
| Changed server pattern | Helpers, middleware, and server conventions that other code must follow | `docs/architecture/server-conventions.md` |
| Changed frontend pattern | Hooks, state patterns, component conventions, or authentication flow | `docs/architecture/frontend-conventions.md` |
| Changed schema or migration | Current tables or collections, fields and types, keys and relationships, constraints, and indexes where applicable | `docs/architecture/db-schema.md` |
| Changed data shape or query pattern | Domain data shapes, ownership, lifecycle, and query/access patterns | `docs/architecture/data-model.md` |
| New test pattern or test-file convention | Test structure, fixtures, helpers, and required testing conventions | `docs/architecture/testing-conventions.md` |
| New import or module pattern | Module boundaries, import/export rules, and dependency-direction conventions | `docs/architecture/index-conventions.md` |

| Finding | Owner |
| --- | --- |
| Current convention, contract, invariant, module shape, API behavior, operational procedure, user-facing fact, or database schema | The most specific affected authoritative document; use the documented architecture owner when no more specific owner exists. |
| Unfixed bug, risk, shortcut, missing capability, or unresolved investigation | `docs/open_issues.md`, through `track-open-issue`. |
| Verified action required around a future deployment | The established deploy runbook, or the documented deployment-step owner when it is the local owner. |
| Non-obvious trap, counterintuitive rationale, failed approach, or user rule that would surprise an agent who read the code and docs | The project's memory store. |

If a fact cannot be verified, do not write it as fact. Report it as `unknown`; if it is actionable unresolved work, treat the verified uncertainty and its missing evidence as an investigation candidate.

For each verified issue candidate, load and follow the `track-open-issue` skill with its verified problem statement,
primary evidence, and resumption condition. Use only `docs/open_issues.md`; preserve its existing format and
identifiers and follow the skill's initialization rule when absent. Apply the base workflow's evidence,
dirty-target, concurrent-edit, and unrelated-target protections to every issue write; do not change unrelated
entries. If the skill cannot be loaded, report `issue tracking: UNAVAILABLE` and leave the candidate unwritten
with its evidence and resumption condition in the report. Do not substitute another tracker. Do not track
documentation-only facts, deployment prerequisites, memories, unverified non-actionable claims, or when no
issue candidate exists. Include the result in the closeout report.

## Step 4: Deployment Steps, Only When Relevant

Enter this step only when attributable changes have plausible deployment implications or verified evidence of a deploy may change an existing entry's status. Otherwise do not investigate deployment state or inspect its owner; report `not examined: no deployment-relevant evidence in attributable work`.

When this step applies, determine deployment state from repository evidence or user-provided session context: `deployed`, `not deployed`, or `unknown`. Do not guess.

Only inspect or reconcile the existing deployment owner when attributable changes have concrete deployment implications or verified evidence of a deploy may change an existing entry's status. Do not scan or rewrite the deployment register during an unrelated closeout.

For any deployment state with such evidence, inspect attributable changes for prerequisites such as schema/data migration, configuration or external-service setup, cache invalidation, data/content regeneration, or release ordering. Record a concrete, verified prerequisite even when deployment state is `not deployed` or `unknown`; make that state and its effect on the entry lifecycle explicit. Do not record speculative future work. Close or archive an existing entry only when confirmed deploy evidence proves it completed. Preserve useful history.

Record a verified prerequisite even when part of its procedure is unknown. Each entry states timing, applicable environment, procedure or command with provenance, verification and success condition, and rollback or irreversibility where verified; mark every missing field `unknown`, name the evidence needed, and assign an owner or action to resolve it. Never fill a gap by inference.

For `not deployed` or `unknown`, report the state and any evidence gap. Do not create hypothetical deployment work.

## Step 5: Memory and Compaction, Only When Available

Enter this step only when a verified finding routes to memory or an already-discovered project instruction requires a closeout index check. Otherwise report `not needed` without searching for a memory store.

Apply the repository's memory/documentation distinction from its instructions. If none exists, use this rule: documentation explains current state; memory warns a future agent before an action could trigger a non-obvious problem.

Discover the memory store and index before writing, following the `memory-handling` skill's discovery rule. Treat it as project-associated only when repository instructions, project configuration, or a path inside the current repository explicitly associates it with this project; a store named by the `initialize-coherence` contract section is valid association. A global memory command, `~/.pi/...` store, or similarly named index is not evidence of association. Update a related memory rather than duplicating it. If no verified project memory mechanism exists, report that capability as unavailable; do not create or modify one implicitly.

After all memory writes, check any threshold or hook explicitly configured for that verified project memory. If no
threshold is breached, report `not needed`. If one is breached, use a compactor only when its definition explicitly
targets the discovered project memory, limits writes to that memory store and its declared documentation owners, and
has been inspected for dirty-target and concurrent-edit protection. Record its prospective targets' initial content
and compare them immediately before invoking it. When no such compactor is available, report `compaction needed`
with the measured threshold breach and leave compaction to the user. Never compact with unsaved findings.

## Step 6: Reconcile Brief Current State

Use the same project-owned snapshot maintained by `coordinate-implementation`, not a closeout
tracker. Follow its [Brief Current State and Recovery](../coordinate-implementation/SKILL.md#brief-current-state-and-recovery)
contract for location, selective recovery and recovery-relevant write bounds. STATE is a
small ephemeral recovery bookmark, not a checkpoint system. Reuse a declared project-local
equivalent; otherwise root `STATE.md` is the coordinator default. When no execution snapshot exists
and no project instruction requires one, report `not needed`; closeout alone does not fabricate
implementation progress or initialize a competing file. If required state is missing, reconcile
authoritative artifacts/Git/runtime evidence first or report the exact blocker.

Keep the current block BRIEF: update ongoing items and their exact next safe action in place;
remove the verified finished item rather than replace it with a terminal disposition. This includes
a finished planner spec: remove its planning state, not its durable source/tasks/approval/evidence.
Do not fabricate implementation as its successor; retain a distinct successor only when it is
independently current and authorized. Retain paused/blocked work, active run/child IDs and pending
gates. Link authoritative artifacts only for work still current; no mandatory Git SHAs or commands/results
catalogue. Record unknowns honestly; unrun checks never pass. Reconcile any active child before
claiming completion; unresolved review/acceptance remains a gate. Unknown completion, runtime or
ownership, partial work or missing acceptance proof cannot authorize deletion.
Preserve custom headers, unrelated concurrent current-state content and durable-owner pointers.
Remove only the understood attributable finished item, never clear the whole file. An empty current
block is valid when nothing remains; preserve the file/custom structure without completed/idle-history
placeholders or a next action solely for finished work. Repeated closeout with unchanged content
requires no write or extra checkpoint. Do not erase surplus historical content outside that bounded
item or migrate it into docs/memory without separately approved scope.

Apply the base dirty-target, concurrent-edit and unrelated-target protections. Coordinate explicit
non-overlapping write responsibility with any active coordinator; never compete to write the file.
Verify an authorized update before reporting/handoff. A STATE-only edit/removal requires no
separate commit or summary/index write; leave known owned dirtiness or include it in the next safe
otherwise-required commit. Never chase its own commit. Required retained closeout documentation/
evidence commits remain unchanged. Failed writes or ambiguous ownership stop affected closeout.
Do not append history, completed-task ledgers, transcripts, full logs, file inventories or
duplicate verification evidence.

## Step 7: Validate Only What You Changed

Check that links, issue references, memory-index entries, and supersession pointers introduced or changed by this closeout resolve. Do not conduct a whole-repository link audit.

## Step 8: Report

State separately whether the session's work is implemented, verified, and deployable; each positive claim must cite evidence. List:

- local artifacts initialized and existing authoritative owners used
- documents checked and changed, including generated-document status
- unresolved items and the issue-tracking result
- deployment state and prerequisites added, or why none were added
- memories written or updated and compaction status
- the temporary execution state document updated, or why it was not
- changed-reference validation
- deliberately skipped candidates, uncertain session attribution, and unverifiable claims

## Mandatory task checkpoint

Apply the shared [task-commit contract](../memory-handling/references/task-commit-contract.md). Authorized retained closeout artifacts checkpoint as bounded tasks; reporting and read-only validation alone create no empty commit.
