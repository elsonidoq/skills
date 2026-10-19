---
description: Execute the implementation plan by processing and executing all tasks defined in tasks.md
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Mandatory task checkpoint

Apply the shared [task-commit contract](../../skills/memory-handling/references/task-commit-contract.md). For retained repository work, use runner-owned sequential verification/commits and ownership/custody guards; each verified task has a focused commit before later task work or completion reporting. This does not bypass existing SpecKit approvals, extension hooks, or task semantics.

## Pre-Execution Checks

**Check for extension hooks (before implementation)**:
- Check if `.specify/extensions.yml` exists in the project root.
- If it exists, read it and look for entries under the `hooks.before_implement` key
- If the YAML cannot be parsed or is invalid, do not skip silently: tell the user that `.specify/extensions.yml` could not be read (include the parser error) and that no hooks were checked, including any mandatory (`optional: false`) hooks registered there, then continue normally
- Filter out hooks where `enabled` is explicitly `false`. Treat hooks without an `enabled` field as enabled by default.
- For each remaining hook, do **not** attempt to interpret or evaluate hook `condition` expressions:
  - If the hook has no `condition` field, or it is null/empty, treat the hook as executable
  - If the hook defines a non-empty `condition`, skip the hook and leave condition evaluation to the HookExecutor implementation
- For each executable hook, output the following based on its `optional` flag:
  - **Optional hook** (`optional: true`):
    ```
    ## Extension Hooks

    **Optional Pre-Hook**: {extension}
    Command: `/{command}`
    Description: {description}

    Prompt: {prompt}
    To execute: `/{command}`
    ```
  - **Mandatory hook** (`optional: false`):
    ```
    ## Extension Hooks

    **Automatic Pre-Hook**: {extension}
    Executing: `/{command}`
    EXECUTE_COMMAND: {command}

    Wait for the result of the hook command before proceeding to the Outline.
    ```
    After emitting the block above you MUST actually invoke the hook and wait for it to finish before continuing. Run it the same way you would run the command yourself in this agent/session (the invocation may differ from the literal `{command}` id shown above, e.g. a skills-mode agent runs it as `/skill:speckit-...` or `$speckit-...`). Emitting the block alone does not run the hook.
- If no hooks are registered or `.specify/extensions.yml` does not exist, skip silently

## Outline

1. Read the current approved source/tasks and actual project instructions once. Apply the
   installed `coordinate-implementation` skill as a thin executable CLI facade, not an
   implementation planner/worker. Missing current-content approval, complete structured
   contracts, required installed stage evidence or implementation scope blocks affected work.
   Standard retains specification/plan/tasks, specification approval, independent overall review
   and final approval; preserve original legacy/TinySpec gates, no forced conversion or Epic.
2. Verify the actual installed CLI/capabilities and approved exact config/executor intent.
   Missing runtime/auth/containment/question transport blocks, never silent install or substitution.
   Preserve user edits, STATE/custom/history and reconcile active/unknown legacy writers first.
3. Invoke authorized `start` or explicit diagnosed `resume` with explicit project/run/workflow/
   tasks/external-owner-catalog/manifest/containment and approved resource root. The runner alone
   selects work/sessions, checks REQUIRED/gates, audits owned diffs and makes individual focused
   commits. Do not create a competing LLM task loop, batching, model escalation or narrative state.
4. Relay genuine owner input through prescribed parent facade or standalone CLI. Interactive
   mode must actually call registered ask_user; workers use request_owner_input only. Original
   conversation answer pin, external scoped authority and changed-source renewal remain intact.
5. Read authoritative `status`/`pending`. Host exit does not imply background continuation.
   Report waiting/blocked/interrupted truthfully. Run applicable after-implementation hooks only
   after their original success/authority prerequisites; an unanswered gate is not completion.
   Implementation complete is separate from current full-range independent review/acceptance.

## Mandatory Post-Execution Hooks

**You MUST complete this section before reporting completion to the user.**

Check if `.specify/extensions.yml` exists in the project root.
- If it does not exist, or no hooks are registered under `hooks.after_implement`, skip to the Completion Report.
- If it exists, read it and look for entries under the `hooks.after_implement` key.
- If the YAML cannot be parsed or is invalid, do not skip silently: tell the user that `.specify/extensions.yml` could not be read (include the parser error) and that no hooks were checked, including any mandatory (`optional: false`) hooks registered there, then continue to the Completion Report.
- Filter out hooks where `enabled` is explicitly `false`. Treat hooks without an `enabled` field as enabled by default.
- For each remaining hook, do **not** attempt to interpret or evaluate hook `condition` expressions:
  - If the hook has no `condition` field, or it is null/empty, treat the hook as executable
  - If the hook defines a non-empty `condition`, skip the hook and leave condition evaluation to the HookExecutor implementation
- For each executable hook, output the following based on its `optional` flag:
  - **Mandatory hook** (`optional: false`) — **You MUST emit `EXECUTE_COMMAND:` for each mandatory hook**:
    ```
    ## Extension Hooks

    **Automatic Hook**: {extension}
    Executing: `/{command}`
    EXECUTE_COMMAND: {command}
    ```
    After emitting the block above you MUST actually invoke the hook and wait for it to finish before continuing. Run it the same way you would run the command yourself in this agent/session (the invocation may differ from the literal `{command}` id shown above, e.g. a skills-mode agent runs it as `/skill:speckit-...` or `$speckit-...`). Emitting the block alone does not run the hook.
  - **Optional hook** (`optional: true`):
    ```
    ## Extension Hooks

    **Optional Hook**: {extension}
    Command: `/{command}`
    Description: {description}

    Prompt: {prompt}
    To execute: `/{command}`
    ```

## Completion Report

Report final status with summary of completed work.

## Done When

- [ ] Authoritative runtime status reports task checkpoints complete; do not rewrite pinned source tasks to manufacture completion
- [ ] Implementation validated against specification, plan, and test coverage
- [ ] Each retained-writing task has a verified focused commit before subsequent task work or completion reporting
- [ ] Extension hooks dispatched or skipped according to the rules in Mandatory Post-Execution Hooks above
- [ ] Completion reported to user with summary of completed work
