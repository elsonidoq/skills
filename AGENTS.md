# Global Agent Instructions

## Purpose

This repository contains global pi configuration, commands, and skills. Keep global assets portable across
unrelated projects. Project-specific policy belongs in that project's instructions or local skills.

## Skill Policy

Automatically use only these global process skills:

- `brainstorming`
- `using-git-worktrees`
- In suite-adopting projects, load the project memory store per the `memory-handling`
  skill before planning or implementing.

Use another skill only when the user explicitly requests it or the task requires a named external capability.
Global skills may depend on a reusable capability such as SpecKit, Railway, Supabase, GitHub, or a configured
agent only after verifying it is available and stating an unavailable fallback.

## Global Assets

- Commands and skills must not assume a project name, repository layout, branch, local path, deployed state, or
  configured model or agent.
- Do not add project-specific workflow, data, or historical rationale to global assets.
- After changing global configuration, commands, or skills, tell the user to run
  `/reload` inside pi.

## Expensive Subagent Failures

Never relaunch an expensive subagent, including `opus`, after a failure unless the failure cause
has been inspected and a retry directly addresses that cause. The same rule applies to batches
delegated through the suite's `subagent` tool: inspect the failed child run before resuming or
re-dispatching, and never relaunch on an uninspected failure. A generic tool abort, cancellation,
timeout, or missing error detail is not evidence that retrying will work.

Before any relaunch:

1. Inspect the existing task session and the failed tool invocation.
2. Determine whether the subagent can be resumed with a targeted correction.
3. Resume the existing session when it retains relevant analysis or work.
4. If the cause is unavailable or uncertain, stop and report the blocker to the owner.

Only launch a new expensive subagent after the owner explicitly requests it or the inspected
failure proves that a fresh session is necessary.

## Pi Skill Suite Contract

### Requirements

- Pi coding agent: `0.87.x` (verified: `0.87.1`)
- `pi-subagents`: `0.73.1`
- `pi-ask-user`: `0.15.1`
- SpecKit: required before running pipeline stages; not installed in this project.
- `jev`: optional for `finish-session-jev` (available in this environment).

### Workflow

Use the suite workflow: brief → `create-epic` → SpecKit pipeline via
`epics-manager` → `coordinate-implementation` → `finish-session`. Do not run a
SpecKit-dependent stage until its toolkit is installed in this project.

### Memory and State

The project memory store is `memory/`, indexed by `memory/MEMORY.md`. Before
planning, implementing, reviewing, or closing work, follow the retrieval and
write contract in `memory-handling`. Keep temporary current-execution state in
`STATE.md` only when this project adopts that document; pi sessions are the
conversation record. `docs/open_issues.md` is the canonical unresolved-work
register; use `track-open-issue` for verified unresolved work.

### Documentation

Documentation owners and the documentation-routing guide have not been
initialized. Establish them with `initialize-documentation` before relying on
new documentation ownership or routing rules. Until then, retain the existing
`docs/open_issues.md` unresolved-work register.
