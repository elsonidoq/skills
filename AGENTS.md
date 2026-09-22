# Global Agent Instructions

## Purpose

This repository contains global OpenCode configuration, commands, and skills. Keep global assets portable across
unrelated projects. Project-specific policy belongs in that project's instructions or local skills.

## Skill Policy

Automatically use only these global process skills:

- `brainstorming`
- `using-git-worktrees`
- `requesting-code-review`
- `receiving-code-review`

Use another skill only when the user explicitly requests it or the task requires a named external capability.
Global skills may depend on a reusable capability such as SpecKit, Railway, Supabase, GitHub, or a configured
agent only after verifying it is available and stating an unavailable fallback.

## Global Assets

- Commands and skills must not assume a project name, repository layout, branch, local path, deployed state, or
  configured model or agent.
- Do not add project-specific workflow, data, or historical rationale to global assets.
- After changing global configuration, commands, or skills, tell the user to restart OpenCode.

## Expensive Subagent Failures

Never relaunch an expensive subagent, including `opus`, after a failure unless the failure cause
has been inspected and a retry directly addresses that cause. A generic tool abort, cancellation,
timeout, or missing error detail is not evidence that retrying will work.

Before any relaunch:

1. Inspect the existing task session and the failed tool invocation.
2. Determine whether the subagent can be resumed with a targeted correction.
3. Resume the existing session when it retains relevant analysis or work.
4. If the cause is unavailable or uncertain, stop and report the blocker to the owner.

Only launch a new expensive subagent after the owner explicitly requests it or the inspected
failure proves that a fresh session is necessary.
