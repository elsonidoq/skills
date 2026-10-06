---
name: track-open-issue
description: Use when verified unresolved work needs recording in `docs/open_issues.md`.
---

# Track Open Issue

Record the issue candidate or source artifact named in the user's request in `docs/open_issues.md`. Do not modify
product code, tests, generated assets, deployment state, or unrelated artifacts.

## Inputs and Evidence

Read every named source artifact. Extract or ask for only the minimum missing information needed to record an issue:

- a concrete unresolved problem, classified as a bug, risk, shortcut, missing capability, or investigation;
- primary evidence that verifies the problem or, for an investigation, verifies the uncertainty and names the evidence
  needed to resolve it; and
- a resumption condition: the next action, prerequisite, or observation that makes work resumable.

If the request is absent, unreadable, or insufficient, ask a concise question and do not write anything. Track only
verified unresolved work. Do not state an unverified claim as fact; record the uncertainty, its known evidence, and the
evidence required to resolve it. Exclude credentials, tokens, personal data, and sensitive payloads.

## Record in the Local Register

1. Read applicable repository instructions (`AGENTS.md`, `CLAUDE.md`, or equivalent) and the existing register when
   present. Preserve its identifiers, templates, statuses, and ownership rules.
2. Search `docs/open_issues.md` for duplicate or overlapping entries using the problem, affected area, and primary
   evidence. Inspect likely matches and their current status. Update the matching issue when appropriate; otherwise
   create one new entry. Do not duplicate a full narrative.
3. Before editing an existing register, inspect its initial dirty state and content. Do not edit a pre-existing dirty
   target without explicit owner approval. Re-read it immediately before applying a patch and stop if it changed
   concurrently.
4. When the register does not exist, initialize `docs/open_issues.md` with the `OI-N` convention, where `N` is the
   next unused positive identifier after inspecting existing entries. For a new entry, use status `open` and include
   `Status`, `Problem`, `Primary evidence`, and `Resumption condition`.
5. Do not close, reopen, reassign, or change unrelated entries.

## Validate and Report

Re-read the created or updated entry. Verify its `OI-N` reference resolves, its status, problem, primary evidence,
and resumption condition are present, and it has not duplicated an existing entry.

Report one outcome: `created`, `updated`, `deduplicated`, `deferred`, or `not recorded`. State:

- the `docs/open_issues.md` location and issue reference;
- the primary evidence, status, and resumption condition; and
- any required owner action.

## Mandatory task checkpoint

Apply the shared [task-commit contract](../memory-handling/references/task-commit-contract.md). A verified local-register update is a bounded retained deliverable; investigation without such a write creates no empty commit.
