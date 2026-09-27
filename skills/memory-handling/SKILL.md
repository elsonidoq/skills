---
name: memory-handling
description: Use when locating, retrieving, or updating the project's memory store — before planning, implementing, reviewing, or closing out work in a suite-adopting project.
---

# Memory Handling

Own the retrieval contract for the project memory store. Memory records **trigger-first
gotchas**: non-obvious, durable guidance that would surprise an agent who read the code
and authoritative documentation. Documentation describes current state; memory warns an
agent *before* an action could trigger a non-obvious problem.

## Discovering The Store

Locate the store exactly once per session and reuse the result. The store is
project-associated when repository instructions `AGENTS.md`/`CLAUDE.md` (including the
memory-store section written by the `install-memory` skill) or documented project
configuration name its path. The suite's default convention, when adopted through
`install-memory`, is a project-owned `memory/` directory with a `MEMORY.md` index and
entry files; an owner-approved different path is equally valid.

If no store or association can be verified, report that the project has not adopted the
suite (`memory adoption: missing — run install-memory`) and do not create, guess, or
modify a global store. Never treat a global agent-memory command, `~/.pi/...` store, or
similarly named index as project association without repository evidence.

## Retrieval Protocol

1. **Read the whole index first.** The index is the map: each entry states its trigger and
   consequence. It is kept small by design, so a full read is cheaper than guessing.
2. **Open entries only when relevant.** Open an entry in full when the current action
   matches its trigger, a material decision is being made (scope, architecture, schema,
   permissions, cost, irreversible behavior), or the work touches files the entry names.
3. **Cost order:** index → matching entries → nothing else. Do not open the store
   wholesale.
4. **Re-check after any memory write** (including writes made by `finish-session` or
   `compact-memory`): a changed or added trigger can change which entries apply to the
   current work.

## When To Consult

- On session start, when resuming suite work (`coordinate-implementation`,
  `epics-manager`, `create-epic`).
- Before planning, before batching implementation, and before the final integration
  review in `coordinate-implementation`.
- Before closeout, through `finish-session`.
- Ad hoc: whenever observable behavior seems surprising, a trigger matches, or a
  decision could repeat a past failure.

## Write Protocol

- Record only verified, non-obvious, trigger-first gotchas: the trigger (the future
  action), the consequence (what breaks and why), and the evidence pointer.
- Supersede an outdated entry rather than editing history silently or duplicating it;
  keep one index entry per gotcha and repair every inbound reference.
- Never write completed-work summaries, file inventories, task ledgers, or git-owned
  metadata; those belong to documentation or git.
- Never write credentials, tokens, personal data, or sensitive payloads.
- Classify surplus entries per `compact-memory`: `KEEP`, `MIGRATE` (to an authoritative
  document), `MERGE`, or `DROP` with a recorded reason.

## Report

State the verified store location, the index state, the entries consulted and why,
constraints applied from memory, and any writes or supersessions performed in this
session.