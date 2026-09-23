---
description: Compact an explicitly project-associated memory store without losing trigger-first gotchas.
---

You are compacting a project's memory index. The goal is to keep the memory store discoverable and within its
configured size limit by moving current-state knowledge to authoritative documentation and removing only stale,
duplicate, or git-owned records.

## Preconditions and Scope

1. Read repository instructions (`AGENTS.md`, `CLAUDE.md`, or equivalent) and locate a memory store explicitly
   associated with the current project. A valid association is a documented path inside the project, or project
   configuration/instructions naming the store and its index.
2. If no project memory store exists or its association cannot be verified, stop. Report `compaction unavailable:
   no verified project memory store`; do not create a memory store or modify global memory.
3. Read the project's memory/documentation distinction. If absent, use this rule: documentation describes current
   state; memory contains non-obvious, action-triggered gotchas that would surprise an agent who read the code and
   authoritative documentation.
4. Discover the configured threshold and index format. If no threshold is configured, accept `$ARGUMENTS` as a
   target only after stating that it is user-provided; otherwise ask the user for a target. Never invent a line or
   byte limit.
5. Limit all writes to the verified memory store and its existing authoritative documentation owners. Do not edit
   application code, tests, generated application assets, or unrelated documentation.

## Safety Rules

- Start with `git status --short`. Record the initial contents and dirty state of every prospective memory or
  documentation target before editing it. Do not edit an initially dirty target without explicit user approval.
  Re-read and compare immediately before each patch; stop on a concurrent change.
- Take a fresh, independent backup of the verified memory store before changing it. If it is a symlink, resolve it
  and copy its contents, not the link. Verify the backup is independent and has the same file count.
- Do not write secrets, tokens, personal data, or sensitive payloads into memory or documentation.
- Verify facts against primary artifacts before migrating them to documentation. A stale memory is dropped or
  corrected; it must not become a stale durable document.
- Never delete a genuine gotcha until its required destination is verified. When uncertain whether a fact is a
  current-state convention or a trigger-first trap, preserve the trap and put any durable convention in its
  documentation owner.

## Phase 1: Inventory and Classify

Read the complete index and every memory it references, including content beyond any context-loading cutoff.
Discover authoritative documentation owners from project instructions and existing indexes; do not assume a fixed
documentation directory or filenames.

Classify each memory exactly once:

| Class | Meaning and action |
| --- | --- |
| `KEEP` | A verified, non-obvious trigger-first gotcha. Tighten only when doing so preserves the trigger and consequence. |
| `MIGRATE` | A verified current-state fact, contract, invariant, or convention. Add it to its most specific authoritative document, then remove or reduce the redundant memory. |
| `MERGE` | Overlapping memories. Combine every distinct actionable fact into one surviving memory and repair inbound references. |
| `DROP` | Stale, resolved, superseded, duplicate, or git-owned metadata. Record why it is safe to remove. |

For each `MIGRATE`, name the target document and section. For each `DROP`, explicitly distinguish stale/wrong facts
from completed-work or other git-owned records. Search for near-duplicate claim text whenever a memory is refuted
or dropped as stale so another copy cannot retain a misleading verdict.

## Phase 2: Propose and Get Approval

Before editing, present:

1. Documentation additions grouped by target document, including source memory records.
2. Memory records to merge or delete, with a concrete reason and destination where applicable.
3. The kept-record count, any new trigger pointers, and the projected index size against the configured or
   user-provided target.
4. Backup location and verification result.

Stop and wait for explicit user approval. If the index is already within its target, ask whether the user wants a
lightweight hygiene pass rather than forcing removals.

## Phase 3: Execute the Approved Plan

1. Add approved migrations to their documentation owners first. Keep each fact in one authoritative document;
   do not create duplicate summaries.
2. Merge or delete approved memories. Repair every inbound index or intra-memory reference so no link dangles.
3. Rewrite the memory index in its existing trigger-first format. Preserve index entries' trigger and consequence;
   remove empty sections.
4. Recompute the configured target measurement. If still over, perform another approved `MIGRATE`, `MERGE`, or
   `DROP` pass rather than gutting a record until it becomes undiscoverable.
5. Validate only links and references changed by compaction.

## Phase 4: Independent Audit and Report

Ask a fresh reviewer to inspect the pre-compaction backup and current files. The reviewer checks that every
removed memory maps to an approved `MIGRATE`, `MERGE`, or `DROP`; preserved gotchas remain actionable; migrated
facts are accurate; and changed links resolve. Fix actionable findings with the same dirty-target protection, then
re-check the configured size target.

Report the verified memory location, configured target, backup path, migrations, merges, drops, kept count, final
index measurement, stale facts found, changed-link validation, audit findings and fixes, plus anything unavailable
or not verified.
