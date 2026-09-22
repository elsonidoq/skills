---
name: using-git-worktrees
description: Use when starting repository work that should be isolated from the current checkout, or when an implementation workflow requires a separate workspace.
---

# Using Git Worktrees

## Purpose

Create isolation without assuming how the host manages workspaces. Prefer an existing or native isolated workspace; use Git directly only as a verified fallback.

## Workflow

1. Confirm the current directory belongs to the intended repository. If repository state cannot be inspected, do not create a worktree; explain the limitation and work in place only with user approval.
2. Determine whether the current checkout is already isolated. Use the host's workspace metadata when available; otherwise compare Git's worktree-specific and common metadata, accounting for submodules. If already isolated, reuse it.
3. Check documented instructions or an explicit user preference for isolation and location. If neither authorizes a new workspace, ask before creating one.
4. Check for a native workspace or worktree capability. If present, use it and accept the location and branch behavior it manages.
5. If no native capability exists, use Git's worktree capability only after verifying it is available.

## Git Fallback

Choose the destination in this order:

1. Explicit user or repository instructions.
2. An existing repository convention that is safe for worktrees.
3. A location proposed to and approved by the user.

Before creating a project-local worktree, verify that its destination is excluded from version control. If it is not excluded, do not silently edit ignore rules or create commits; ask whether to add the exclusion, choose an external location, or work in place.

Choose a new branch name from the task and repository conventions. If branch creation is unavailable or the host intentionally uses detached state, report that state rather than forcing a branch. If creation fails because of permissions, policy, collisions, or unsupported Git behavior, preserve the current checkout and offer the safe alternatives supported by the environment.

## Setup And Baseline

After entering the workspace:

- Use documented bootstrap instructions or a verified project task when available.
- Do not infer an install command solely from a manifest filename. If setup is undocumented, inspect available task metadata or ask; if no setup is required, continue.
- Run the documented or discoverable baseline checks relevant to the change. If none exist, report that no baseline command was found.
- If setup or baseline checks fail, report the command or capability used and the failure. Ask before proceeding when the failure makes later results ambiguous.

## Ready State

Report the workspace location, branch or detached state, setup performed, baseline result, and any fallback taken. Never claim isolation or a clean baseline without observable evidence.
