---
name: memory-handling
description: Use when locating, retrieving, or updating the project's unified memory store — before planning, implementing, reviewing, or closing out work in a suite-adopting project.
---

# Memory Handling

Own the retrieval and authorized-write contract for the project memory store. One verified
project association and one index hold two distinct evidence kinds:

- **Technical gotchas:** verified, non-obvious, durable action-triggered warnings. Each
  records its trigger, consequence, and evidence pointer.
- **Owner guidance:** explicit future-directed user feedback. Each records the actual user
  provenance and a concise future trigger/action.

Documentation describes current state; memory warns or directs an agent before a relevant
future action. Guidance never overrides current owner or source authority. Do not disguise
agent-inferred coordination lessons as gotchas.

## Discovering the association

Locate the one index association exactly once per session and reuse the result. It is verified only
when repository instructions (`AGENTS.md`/`CLAUDE.md`, including an
`initialize-coherence` association) or documented project configuration names the index
and its project-local path. The adopted convention may be `memory/MEMORY.md`, but an
owner-approved custom index path is equally valid.

Read-time discovery never creates storage. Missing optional storage or STATE is nonblocking:
do not initialize it. If required project association cannot be verified, report
`memory adoption: missing — run initialize-coherence` and route through that existing
adoption process; never guess a path or use global agent memory as a fallback. Never
create, discover, read, or maintain a separate guidance store or renamed equivalent.

## Retrieval protocol

1. **Read the whole associated index first.** It maps both kinds with compact
   trigger/relevance pointers.
2. **Open only relevant entries in full:** when the action matches a trigger, a material
   decision concerns scope, architecture, schema, permissions, cost, or irreversible
   behavior, or work touches named files.
3. **Cost order:** index → matching entries → nothing else. Do not recursively or
   wholesale load history.
4. **Recheck after a memory write.** A changed trigger can make another entry relevant.

## When to consult

Consult on session start, when resuming suite work, before planning or batching
implementation, before the final integration review, and before closeout. Consult ad hoc
when behavior is surprising, a trigger matches, or a decision could repeat a past failure.
Executable runs consume applicable approved task constraints and gotchas; this does not
create an execution-time feedback or routing intake obligation.

## Authorized writes

Write a gotcha only when it is verified, non-obvious, durable, action-triggered, and has a
trigger, consequence, and evidence pointer. Supersede outdated entries rather than silently
editing history or duplicating an entry.

Write owner guidance only for clear, explicit, future-directed user feedback. Preserve its
actual user provenance and concise future trigger/action. Clear bounded feedback needs no routine
second approval. Explanation-only questions, ordinary implementation approval, agent
observations, failed runs, inferred lessons, and no feedback write nothing. Ambiguous
meaning or scope requires asking before writing; an explicit no-write boundary prevails.

Before an authorized write, establish the local owner and bounded associated paths. Refuse
outside-project paths, symlink escapes, unreadable or non-file collisions, uncertain local
ownership, dirty or concurrent content, and secrets or sensitive payloads. Preserve custom
and unrelated bytes. Re-read and compare the intended baseline immediately before applying;
concurrent drift or same-file ambiguity stops the affected write. Owner-authorized
concurrency is valid with explicit path ownership, but overlap or uncertainty stops the
affected write. An authorized new association may create only its bounded unified
index/entry structure—never separate guidance, history, run, or STATE scaffolding.

After an actual write, recheck the index and relevant entries. A retained memory change is a
substantive deliverable and follows the existing
[task-commit contract](references/task-commit-contract.md); that contract remains the sole
owner of focused checkpoint behavior.

## No routine bookkeeping

Planning, dispatch, polling, recovery, task/check/commit completion, review, pause, and
closeout do not authorize memory writes. Do not create or maintain STATE, progress ledgers,
routine summaries, index refreshes, run/evidence records, reflection, candidate synthesis,
or evidence-only commits. Leave existing custom and historical content unchanged unless an
authorized scoped write requires it. Recovery remains owned by its existing coordinator;
this skill does not copy a recovery protocol.

## Report

State the verified association/index location, entries consulted and why, applicable
constraints, and any authorized write or supersession. State when association is missing or
when a write was refused and why.

## Mandatory task checkpoint

Apply the shared [task-commit contract](references/task-commit-contract.md). Explicitly
authorized retained memory feedback is a substantive deliverable, not routine evidence
persistence.
