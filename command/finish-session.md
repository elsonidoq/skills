---
description: Close a session by preserving current documentation, unresolved work, deployment prerequisites, and trigger-first memory.
---

You are closing a working session. Preserve durable knowledge without turning closeout into a repository audit.

## Core Invariants

1. Affected authoritative documentation describes what is built now.
2. Discovered work deliberately left unresolved has one canonical owner.
3. For a deployed project, deploy-time work pending since the last confirmed deploy has one canonical owner.
4. Memory contains only trigger-first gotchas not apparent from code and authoritative documentation.
5. The memory index remains usable.

## Safety Rules

- Start with `git status --short`, `git diff --name-status`, and `git diff --cached --name-status`. From those summaries, inspect full diffs and relevant untracked files only for paths attributable to this session; neither diff command includes untracked contents. Treat pre-existing or unattributable changes as out of scope and report the uncertainty.
- Record each prospective target's initial dirty state and content before editing. Do not edit a target that was already dirty unless the user explicitly approves that overlap. Re-read and compare it with the recorded content immediately before applying a patch; if it changed concurrently, stop and report the conflict.
- Do not discard, stage, commit, or rewrite unrelated work. Limit edits to closeout documentation, issue or deployment records, and a verified project memory store. Do not modify application code, tests, generated application assets, or completed implementation artifacts.
- Verify a durable claim against its primary artifact: code, configuration, schema, generator output, or external source explicitly configured by the repository. Never record an unverified claim as current truth.
- Do not write credentials, tokens, personal data, or sensitive payloads. Use redacted placeholders such as `$SERVICE_TOKEN`.
- Do not execute deployment procedures. Do not invent deployment commands, rollback steps, or environment state. Record an unknown or verification gap instead.
- Git owns changelogs, completed-work summaries, file-and-line inventories, and plan/task completion metadata. Do not add them to docs, issues, deployment steps, or memory.

## Step 1: Discover Existing Owners

Read repository instructions (`AGENTS.md`, `CLAUDE.md`, or equivalent) and the relevant indexes. Prefer an existing authoritative destination for each kind of information. Do not replace an established external tracker or runbook.

Do not initialize fallback artifacts during discovery. Only initialize a fallback when a verified finding needs that destination and no equivalent local or accessible external owner exists:

- `docs/architecture/` — create the directory only; create a focused document later only when a new durable fact has no existing owner.
- `docs/deployment_steps.md` — initialize with a lifecycle and a short entry template for status, timing, environments, procedure, verification, and rollback/irreversibility.

Preserve the existing format and identifiers when an artifact already exists.

## Step 2: Derive Candidate Findings From Attributable Work

Use the actual working tree, relevant commits made during the session when identifiable, code, configuration, schemas, and generated output. Do not rely on the session narrative alone.

Inspect only documents plausibly affected by changed behavior or data. This can include architecture docs, README files, API/reference docs, configuration examples, runbooks, generated docs, and active decision records. Leave accurate text unchanged. Recompute any count changed by attributable work and name its source or generating command. Mark historical records superseded in place rather than rewriting history.

If the repository declares a targeted, known-safe, bounded generator whose outputs are closeout documentation relevant to the changed area, run it and inspect its diff. Ask before running an expensive or broad generator. Do not run a generator that may modify application code, tests, or generated application assets; report its command as a verification gap instead.

## Step 3: Route Each Verified Finding

Use one canonical owner. A secondary pointer is allowed only when it provides a distinct warning or makes a dependency discoverable; never duplicate a full narrative. In particular, documentation explains current system behavior while a memory may separately warn how a future action can break it.

| Finding | Owner |
| --- | --- |
| Current convention, contract, invariant, module shape, API behavior, operational procedure, or user-facing fact | The most specific affected authoritative document; use `docs/architecture/` for architecture facts with no more specific existing owner. |
| Unfixed bug, risk, shortcut, missing capability, or unresolved investigation | `/track-open-issue`, which records it in `docs/open_issues.md`. |
| Verified action required around a future deployment | The established deploy runbook, or `docs/deployment_steps.md` when it is the local owner. |
| Non-obvious trap, counterintuitive rationale, failed approach, or user rule that would surprise an agent who read the code and docs | The project's memory store. |

If a fact cannot be verified, do not write it as fact. Report it as `unknown`; if it is actionable unresolved work, treat the verified uncertainty and its missing evidence as an investigation candidate.

For each verified issue candidate, invoke `/track-open-issue` with its verified problem statement, primary evidence, and resumption condition. Do not invoke it for documentation-only facts, deployment prerequisites, memories, unverified non-actionable claims, or when no issue candidate exists. Include its result in the closeout report. If the command is unavailable, report the unavailable tracking capability.

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

Discover the memory store and index before writing. Treat it as project-associated only when repository instructions, project configuration, or a path inside the current repository explicitly associates it with this project. A global memory command or similarly named index is not evidence of association. Update a related memory rather than duplicating it. If no verified project memory mechanism exists, report that capability as unavailable; do not create or modify one implicitly.

After all memory writes, check any threshold or hook explicitly configured for that verified project memory. If no threshold is breached, report `not needed`. If one is breached, never delegate to the current global `/compact-memory`: it is nonportable and may target another project. Invoke a compactor only when its definition is project-local, explicitly targets the discovered project memory, limits writes to that memory store and its declared documentation owners, and has been inspected for dirty-target and concurrent-edit protection. Record its prospective targets' initial content and compare them immediately before invoking it. When no such compactor is available, report `compaction needed` with the measured threshold breach and leave compaction to the user. Never compact with unsaved findings.

## Step 6: Validate Only What You Changed

Check that links, issue references, memory-index entries, and supersession pointers introduced or changed by this closeout resolve. Do not conduct a whole-repository link audit.

## Step 7: Report

State separately whether the session's work is implemented, verified, and deployable; each positive claim must cite evidence. List:

- local artifacts initialized and existing authoritative owners used
- documents checked and changed, including generated-document status
- unresolved items and the result returned by `/track-open-issue`
- deployment state and prerequisites added, or why none were added
- memories written or updated and compaction status
- changed-reference validation
- deliberately skipped candidates, uncertain session attribution, and unverifiable claims
