---
name: finish-session
description: Use when closing a working session that may need documentation, unresolved-work, deployment, memory, or explicit feedback.
---

You are closing a working session whose implementation work has already ended. Reconcile documentation
and other authorized owners with what actually happened; do not reopen implementation or turn closeout
into a repository audit, test campaign or acceptance review.

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
2. Discovered work deliberately left unresolved has one canonical owner: the project's declared unresolved-work owner, followed through `track-open-issue`.
3. For a deployed project, deploy-time work pending since the last confirmed deploy has one canonical owner.
4. The one verified project memory association/index may contain verified trigger-first gotchas and explicitly authorized future owner guidance; each retains its distinct evidence and authority.
5. The memory index remains usable.
6. A project with a persistent database has authoritative schema documentation that describes its current tables or collections, fields and types, keys and relationships, constraints, and indexes where applicable.
7. No automatic STATE maintenance, coordination summaries, routine index updates, or reflection. Only explicit future-directed user feedback may authorize guidance; never infer lessons or disguise them as gotchas.

## Safety Rules

- Start with `git status --short`, `git diff --name-status`, and `git diff --cached --name-status`. From those summaries, inspect full diffs and relevant untracked files only for paths attributable to this session; neither diff command includes untracked contents. Treat pre-existing or unattributable changes as out of scope and report the uncertainty.
- Record each prospective target's initial dirty state and content before editing. Do not edit a target that was already dirty unless the user explicitly approves that overlap. Re-read and compare it with the recorded content immediately before applying a patch; if it changed concurrently, stop and report the conflict.
- Do not discard, stage, commit, or rewrite unrelated work. Limit edits to closeout documentation, issue or deployment records, a verified project memory store, and explicit feedback under Step 6. Do not modify application code, tests, generated application assets, or completed implementation artifacts.
- Verify a durable claim against its primary artifact: code, configuration, schema, generator output, or external source explicitly configured by the repository. Never record an unverified claim as current truth.
- Do not write credentials, tokens, personal data, or sensitive payloads. Use redacted placeholders such as `$SERVICE_TOKEN`.
- Do not execute deployment procedures. Do not invent deployment commands, rollback steps, or environment state. Record an unknown or verification gap instead.
- Git owns changelogs, completed-work summaries, file-and-line inventories, and plan/task completion metadata. Do not add them to docs, issues, deployment steps, or memory.

## Step 1: Discover Existing Owners

Read repository instructions (`AGENTS.md`, `CLAUDE.md`, or equivalent) and the relevant indexes. For unresolved issues, load `track-open-issue` and follow the project's declared canonical owner. Preserve the existing declared local register until approved cutover; preparing GitHub skills or an inconclusive import proof does not switch authority. For a project already using GitHub, use only its explicitly resolved target, never create a local fallback or write to a retained historical register. Missing GitHub capability or write authority defers the candidate in the response; it does not reactivate old local ownership. Do not migrate records during closeout. For other information, preserve existing authoritative documentation owners and runbooks.

Do not initialize fallback artifacts during discovery. If a verified finding has
no owner, report the missing owner and ask the user to choose its location and
format. For unresolved issues already routed to GitHub, `track-open-issue` reports an
unavailable target, capability, authentication, or write-authority gap with candidate
evidence and a resumption condition; it never creates a local fallback.

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
| Unfixed bug, risk, shortcut, missing capability, or unresolved investigation | Project-declared unresolved-work owner, through `track-open-issue`. |
| Verified action required around a future deployment | The established deploy runbook, or the documented deployment-step owner when it is the local owner. |
| Verified non-obvious trap, counterintuitive rationale, or failed approach that would surprise an agent who read the code and docs | The project's memory store as a technical gotcha. |
| Explicit future-directed user guidance | The same project's memory association/index, only under the `memory-handling` authorized-guidance rule and with user provenance. |

If a fact cannot be verified, do not write it as fact. Report it as `unknown`; if it is actionable unresolved work, treat the verified uncertainty and its missing evidence as an investigation candidate.

For each verified issue candidate, load and follow `track-open-issue` with its verified problem statement,
primary evidence, and resumption condition. Follow its declared-local-owner branch before cutover; for an
active GitHub owner it resolves the explicit target and requires usable `gh`,
authentication, issue capability, and current scoped write authority; never infer write authority from a read or
create a local fallback. Apply the base workflow's evidence, concurrent-edit, and unrelated-target protections
to every issue write; do not change unrelated issues. If the skill cannot be loaded or its target/capability/
authority is unavailable, report `issue tracking: UNAVAILABLE` or `deferred` and leave the candidate unwritten
with its evidence, resumption condition, missing requirement, and corrective action. Do not substitute another
tracker. Do not track documentation-only facts, deployment prerequisites, memories, unverified non-actionable
claims, or when no issue candidate exists. Include the result in the closeout report.

Route an explicitly approved consequential decision that warrants durable rationale to the canonical `save-adr` skill. This is not a per-session requirement: do not create an ADR for ordinary sessions, agent-inferred implementation lessons, retrospective backfill, or acceptance/provenance that cannot be attributed. `save-adr` owns decision discovery and history; it complements rather than replaces the current-state documentation, schema, runbook, issue, memory, explicit-feedback, and validation routes in this workflow.

## Step 4: Deployment Steps, Only When Relevant

Enter this step only when attributable changes have plausible deployment implications or verified evidence of a deploy may change an existing entry's status. Otherwise do not investigate deployment state or inspect its owner; report `not examined: no deployment-relevant evidence in attributable work`.

When this step applies, determine deployment state from repository evidence or user-provided session context: `deployed`, `not deployed`, or `unknown`. Do not guess.

Only inspect or reconcile the existing deployment owner when attributable changes have concrete deployment implications or verified evidence of a deploy may change an existing entry's status. Do not scan or rewrite the deployment register during an unrelated closeout.

For any deployment state with such evidence, inspect attributable changes for prerequisites such as schema/data migration, configuration or external-service setup, cache invalidation, data/content regeneration, or release ordering. Record a concrete, verified prerequisite even when deployment state is `not deployed` or `unknown`; make that state and its effect on the entry lifecycle explicit. Do not record speculative future work. Close or archive an existing entry only when confirmed deploy evidence proves it completed. Preserve useful history.

Record a verified prerequisite even when part of its procedure is unknown. Each entry states timing, applicable environment, procedure or command with provenance, verification and success condition, and rollback or irreversibility where verified; mark every missing field `unknown`, name the evidence needed, and assign an owner or action to resolve it. Never fill a gap by inference.

For `not deployed` or `unknown`, report the state and any evidence gap. Do not create hypothetical deployment work.

## Step 5: Unified Memory and Compaction, Only When Available

Enter this step only when a verified technical-gotcha finding routes to memory, explicit future-directed user feedback may authorize guidance, or an already-discovered project instruction requires a closeout index check. Otherwise report `not needed` without searching for a memory store.

Use the same verified project association/index for both kinds. A technical gotcha remains a verified, non-obvious, action-triggered warning with trigger, consequence, and evidence; explicit owner guidance retains its actual user provenance and concise future trigger/action and need not meet the gotcha-surprise test. No feedback means no guidance write. Do not infer guidance from implementation work, observations, failed runs, explanations, or closeout reflection.

Discover the memory store and index before writing, following the `memory-handling` skill's discovery rule. Treat it as project-associated only when repository instructions, project configuration, or a path inside the current repository explicitly associates it with this project; a store named by the `initialize-coherence` contract section is valid association. A global memory command, `~/.pi/...` store, or similarly named index is not evidence of association. Read the whole index first, selectively open relevant entries, update or reuse a related entry rather than duplicating it, and recheck after an actual write. If no verified project memory mechanism exists, report that capability as unavailable; do not create or modify one implicitly.

After all memory writes, check any threshold or hook explicitly configured for that verified project memory. If no
threshold is breached, report `not needed`. If one is breached, use a compactor only when its definition explicitly
targets the discovered project memory, limits writes to that memory store and its declared documentation owners, and
has been inspected for dirty-target and concurrent-edit protection. Record its prospective targets' initial content
and compare them immediately before invoking it. When no such compactor is available, report `compaction needed`
with the measured threshold breach and leave compaction to the user. Never compact with unsaved findings.

## Step 6: Explicit Guidance Authority Only

Do not create, edit or remove STATE during closeout; leave custom/concurrent content untouched.
Do not create routine summaries, refresh indexes, reflect, or commit evidence-only records.
Apply the `memory-handling` skill's unified guidance authority: clear bounded explicit
future-directed user feedback may authorize a project-local guidance entry in the verified
association/index without a routine second gate; ambiguity asks before writing, and
explanation-only, no-feedback, or explicit no-write boundaries write nothing. Keep guidance
separate from technical-gotcha evidence even though both share the index. Keep local
path/symlink, sensitive-data and dirty/concurrent ownership protections. Missing optional
memory storage or STATE is nonblocking. Recovery starts with available summary/recent context
and selective authoritative artifact/Git/check/runtime reconstruction; reconcile active/unknown
children before replacement, never guess completion or blindly retry.

## Step 7: Validate Only What You Changed

Check that links, issue references, memory-index entries, and supersession pointers introduced or changed by this closeout resolve. Do not conduct a whole-repository link audit.

## Existing completion and validation facts

Consume existing session results and, when needed, authoritative runner status to document what
happened. Do not launch or require a fresh review, rerun implementation checks, reopen implementation,
or adjudicate final acceptance during closeout. Implementation's own acceptance requirements remain
owned by its workflow; this skill neither waives nor adds to them.

Report known completion, validation and acceptance outcomes accurately. Do not infer acceptance from
worker reports or `implementation_complete` alone. Reuse existing full-range and cumulative repair-review
outcomes without requiring another review. Missing evidence is `unknown` or `NOT RUN`, not a new closeout
gate or permission to claim success. Report known unfinished work or unresolved findings through the
existing issue route; do not repair them as part of closeout.

Preserve SQL/Pi evidence, focused commits, custom STATE/history/gotchas and unrelated dirty work;
no execution-memory closeout ledger.

## Step 8: Report

State separately whether the session's work is implemented, verified, and deployable; each positive claim must cite evidence. List:

- local artifacts initialized and existing authoritative owners used
- documents checked and changed, including generated-document status
- unresolved items and the issue-tracking result
- deployment state and prerequisites added, or why none were added
- memories written or updated and compaction status
- any explicitly authorized guidance write, or `not needed`; STATE remains untouched
- changed-reference validation
- deliberately skipped candidates, uncertain session attribution, and unverifiable claims

## Mandatory task checkpoint

Apply the shared [task-commit contract](../memory-handling/references/task-commit-contract.md). Authorized retained closeout artifacts checkpoint as bounded tasks; reporting and read-only validation alone create no empty commit.
