---
description: Generate an actionable, dependency-ordered tasks.md for the feature based on available design artifacts.
handoffs:
  - label: Analyze For Consistency
    agent: speckit.analyze
    prompt: Run a project analysis for consistency
    send: true
  - label: Implement Project
    agent: speckit.implement
    prompt: Implement the approved tasks in dependency order
    send: true
---

Resolve the shared `task-generation` skill and `skills/planner/references/parsimony.md`
through the authorized suite installation, not a presumed adopting-project layout.
Apply their task semantics and parsimony guidance: preserve Standard stages and approved
acceptance; distinguish source-backed requirements, necessary choices and optional hardening.

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Pre-Execution Checks

**Check for extension hooks (before tasks generation)**:
- Check if `.specify/extensions.yml` exists in the project root.
- If it exists, read it and look for entries under the `hooks.before_tasks` key
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

1. **Setup**: Run `.specify/scripts/bash/setup-tasks.sh --json` from repo root and parse FEATURE_DIR, TASKS_TEMPLATE_CONTENT, TASKS_TEMPLATE, and AVAILABLE_DOCS list. `FEATURE_DIR` and `TASKS_TEMPLATE` must be absolute paths when provided. `AVAILABLE_DOCS` is a list of document names/relative paths available under `FEATURE_DIR` (for example `research.md` or `contracts/`). For single quotes in args like "I'm Groot", use escape syntax: e.g 'I'\''m Groot' (or double-quote if possible: "I'm Groot").

2. **Load design documents**: Read from FEATURE_DIR:
   - **Required**: plan.md (tech stack, libraries, structure), spec.md (user stories with priorities)
   - **Optional**: data-model.md (entities), contracts/ (interface contracts), research.md (decisions), quickstart.md (test scenarios)
   - **IF EXISTS**: Load `.specify/memory/constitution.md` for project principles and governance constraints
   - Note: Not all projects have all documents. Generate tasks based on what's available.

3. **Execute task generation workflow**:
   - Load plan.md and extract tech stack, libraries, project structure
   - Load spec.md and extract user stories with their priorities (P1, P2, P3, etc.)
   - If data-model.md exists: Extract entities and map to user stories
   - If contracts/ exists: Map interface contracts to user stories
   - If research.md exists: Extract applicable decisions and real prerequisites
   - Generate coherent, independently verifiable outcomes covering approved scope
   - Derive task dependencies from actual producer/consumer relationships
   - Preserve one script-owned sequential implementation writer and verified producer checkpoints before dependent work
   - Validate scope coverage and task acceptance; story grouping is optional presentation, not execution machinery

4. **Generate tasks.md**: Use TASKS_TEMPLATE_CONTENT (from the JSON output above) as the structure. For compatibility with older setup scripts that omit TASKS_TEMPLATE_CONTENT, read TASKS_TEMPLATE instead. Fill with:
   - Correct feature name from plan.md
   - Coherent outcome entries with unique IDs and clear work descriptions
   - Actual dependencies, applicable acceptance and required checks, with shared constraints stated once
   - Useful paths/interfaces where known, without inventing exact paths to fill fields
   - Routine verification, documentation and teardown within the delivery outcome
   - An adjacent JSON/YAML executable task list (or object containing `tasks`) using the shared intake format
   - Optional story/MVP grouping when useful, without mandatory setup/foundation/polish phases
   - Sequential producer verification/checkpoints before consumers, with no task-count quota

## Mandatory Post-Execution Hooks

**You MUST complete this section before reporting completion to the user.**

Check if `.specify/extensions.yml` exists in the project root.
- If it does not exist, or no hooks are registered under `hooks.after_tasks`, skip to the Completion Report.
- If it exists, read it and look for entries under the `hooks.after_tasks` key.
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

Output paths to generated tasks.md and executable JSON/YAML, with a concise summary:
- Coherent outcomes and actual dependency order
- Acceptance and specified checks, distinguishing optional hardening
- Script-owned sequential execution and producer checkpoint boundary
- Shared intake validation result and any relevant scope/feasibility limits
- Story/MVP grouping only when useful

Context for task generation: $ARGUMENTS

Tasks and referenced shared context must describe the work and applicable checks clearly;
the JSON/YAML handoff is executable input and Markdown is its human presentation.

## Task Generation Rules

A task delivers an independently verifiable outcome, not a phase, layer or entity noun.
Story labels may help readers but do not determine execution order.

**Verification**: Preserve owner/source-required checks, necessary security, persistence and
integration protections, and actual manual/permission gates. Broader hardening is optional,
not an acceptance blocker; verification does not mean every imaginable test is required.

### Human presentation and executable input

A compact Markdown entry may use:

```text
- [ ] fix-title Correct the settings page title
  - Acceptance/context: [Useful outcome-specific criteria or references]
  - Check: [Relevant command and expected behavior, when specified]
```

Executable JSON/YAML contains a task list or an object containing `tasks`. Each task needs
a unique nonempty string `id` and `outcome` (or `description`); optional `depends` lists
existing task IDs without cycles. IDs need not be numbered or contiguous, and file order
is not execution order. Acceptance, paths, story labels and check commands are useful
context, not universal startup fields. Specified checks remain required after the work.
Optional `checks` accepts shell strings, argv lists or objects containing `command`/`argv`;
`check` and `required[].check` use the same command format.

### Task Organization

- **Stories and contracts**: Cover approved story outcomes and interface obligations without
  splitting automatically by models, services, endpoints or tests. Include justified interface
  checks within the delivery task. Separate a test/proof task only when it provides an
  independently necessary prerequisite.
- **Data model**: Preserve applicable field constraints in authoritative shared context and
  map them to consuming tasks/checks without repeating the same prose in every entry.
- **Setup/infrastructure**: Include only source-backed or concretely necessary work; genuine
  prerequisites block only their actual consumers, not every story by default.
- **Verification/docs**: Keep them inside the outcome unless a separately necessary
  deliverable, prerequisite, gate or resource boundary justifies separation.

### Outcome boundaries and structured handoff

Read and apply `skills/task-generation/SKILL.md` from the authorized suite installation:
the Standard adapter is create-only when managed by planner. Producers may draft, revise,
shorten and mechanically validate unsubmitted output within authorized scope without supervisor
permission for ordinary editing. This is not independent review; submitted defects follow
`overall_review` and its correction route. Never change approved upstream requirements or
silently launch implementation. Resolve paths through that installation, not a presumed
project layout. Missing shared contract/stage capability blocks; never simulate slash tools.
Produce only independently necessary work units, not one task per phase/test/entity noun.
State shared constraints once and keep the human presentation concise. Follow the shared
six-check task intake: readable JSON/YAML task list, ID/work description, unique IDs,
existing dependency references and no cycles. Derive execution order from dependencies,
not contiguous IDs, file order or story groups. Optional context and project checks remain
useful; no required approval/source/envelope/execution-intent metadata or model assessments.
Do not silently substitute the selected executor/effort in runtime configuration. Existing
optional metadata may remain without regeneration. Preserve actual permission boundaries
and required project checks; task preparation does not launch implementation.

## Done When

- [ ] Compact tasks.md and executable JSON/YAML generated with coherent outcomes and actual dependencies
- [ ] Extension hooks dispatched or skipped according to the rules in Mandatory Post-Execution Hooks above
- [ ] Shared intake validated and completion reported with applicable checks and limits

## Task checkpoint boundary

Apply `skills/memory-handling/references/task-commit-contract.md` from the authorized suite
installation: read-only analysis creates no empty commit; authorized retained artifacts
checkpoint as bounded tasks without bypassing their existing approval gates.
