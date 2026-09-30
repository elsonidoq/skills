# Pi Configuration

Global pi skill suite for developing features deliberately across unrelated repositories. The suite is not runtime-portable: it binds to pinned pi packages and requires suite adoption per project.

## Prerequisites

See [REQUIREMENTS.md](REQUIREMENTS.md) for the pinned runtime and model-class mapping. Install the pinned packages once:

```bash
pi install npm:pi-subagents@0.73.1
pi install npm:pi-ask-user@0.15.1
```

Or just run the installer once — it checks pi, auto-installs the pinned
packages, symlinks every suite skill into `~/.agents/skills` (pi's standard
scanned location; the repo stays the single source of truth), backs up anything
in the way, and lint-checks the suite:

```bash
scripts/install.sh          # deterministic checks only
scripts/install.sh --probe  # ... plus one headless pi run that asserts the
                            #     suite skills appear in pi's system prompt
```

Start a new pi session (or run `/reload`) after installing.

## Jev metrics: manual default and explicit Jev-on

### Choose an installation mode

Manual mode is the default and preserves the existing workflows without requiring Jev, Jev
credentials, the metrics tracker, or SpecKit:

```bash
scripts/install.sh
```

Manual mode disables the tracker and the global Jev-on marker, so guarded seams continue with
their unchanged manual workflow and make no measured-use claim.

Choose Jev-on only when the tracked advisory path is wanted:

```bash
scripts/install.sh --jev-on
```

This is a hard, all-or-none activation. The installer requires Pi `0.87.x` (tested `0.87.1`), a
Node 22/ES2022-capable runtime, the local tracker registration harness, `jev-cli` `0.6.3`, and a
successful provider-scoped `jev auth test`. The auth check is an explicit Jev-on network
prerequisite.

The auth check is provider-scoped, and this suite defaults to the `openrouter` provider:

```bash
jev auth set --provider openrouter   # store the provider key once
scripts/install.sh --jev-on          # verifies jev auth test --provider openrouter
```

Use `--jev-provider official|vercel|openrouter|custom` (or the `JEV_AUTH_PROVIDER` environment
variable) when a different Jev provider is configured. A bare `jev auth test` defaults to the
`official` provider, so the installer's provider must match the one the key was stored for. On any
preflight failure it reports the missing or incompatible capability, the observed status without
credential material, the corrective action, and that no optimized seam was enabled. Do not use
Jev-on with credentials, logs, personal data, or sensitive candidate text as ranking input.

After successful all-four global-seam activation, the installer records the state marker at:

```text
$PI_CODING_AGENT_DIR/jev-metrics/global-seams-enabled
```

The marker is written only after all four global seams activate together. A rollback removes a
newly activated marker (or restores its pre-activation state), and returning to manual mode removes
it. This marker is an activation gate, not telemetry.

### Optional project-local SpecKit seams

To install the four SpecKit append layers with Jev-on, use the top-level all-or-none entry point:

```bash
scripts/install.sh --jev-on --speckit-project <dir>
```

It hands off to `scripts/install-jev-speckit.sh --project DIR [--uninstall]`. The project-local
helper has **no** `--jev-on` flag. Its install path requires the already-active tracker and either
installs all four layers or none; `--uninstall` is the recovery path that removes the project preset
and restores the saved original core composition. Target projects need SpecKit `1.0.12`, a live
constitution, project scripts, and Pi command artifacts. Resolver and artifact introspection must show the complete core command plus
exactly one append layer for each of `speckit.analyze`, `speckit.checklist`, `speckit.clarify`, and
`speckit.tasks`.

The preset is project-owned and append-only. It does not hand-edit, search/replace, or
checksum-patch generated `.pi/prompts/speckit.*.md` files. Resolver, reconciliation, or
introspection failure leaves all four SpecKit seams disabled and rolls back the project state.

Run `/reload` in Pi (or start a new session) after either global configuration activation or a
manual-mode deactivation so Pi reloads the changed configuration-time assets.

### Metrics, coverage, and closeout

The tracked Pi interfaces are `jev_rank`, `jev_disposition`, and `jev_metrics`; the user command is
`/jev-metrics`:

```text
/jev-metrics          # current active-branch totals and per-skill totals
/jev-metrics history  # validated cross-session closeout rows and store state
/jev-metrics help     # counters, denominators, coverage, and privacy boundary
```

`attempts` is the count of tracked invocation starts; `successes` is successful terminals;
`proposals` is the candidate-level proposals from those successes. `accepted`, `overridden`,
`not used`, and `pending` are each shown over the proposal denominator. A proposal without a
recorded disposition remains pending. Metrics are `instrumented-only`: only `jev_rank` calls are
tracked. Raw shell or MCP Jev use is explicitly untracked and must not be represented as measured
activity.

`finish-session` invokes `jev_metrics(action=closeout)` once. Closeout is complete only when it
reports `appended` or `already_exported`; `store_error` must be reported as a failed metrics
closeout. The local CSV records aggregate identifiers and counters only.

Candidate bodies, criteria, prompts, logs, raw responses, stderr, secrets, credentials, personal
data, provider endpoints, and project paths are not persisted in session telemetry, metrics output,
or the closeout CSV. If Jev-on is absent or a tracked ranking returns no proposals, the caller
retains the complete original evidence and uses the manual workflow.

This feature is not a benchmark. Do not make token, latency, performance, or quality-improvement
claims from its counters or advisory rankings.

On each project, run the `install-memory` skill first: it writes the suite contract into the project's instructions (epics, memory, state, docs) and initializes the project memory store.

## Repository Invariants

- Documentation describes the system as it exists.
- Database-backed projects maintain authoritative documentation of their current schema.
- Each project documents which material changes require which documentation owners.
- Memory records only non-obvious, durable guidance.
- Verified unresolved work has one canonical register: `docs/open_issues.md`.
- Features are developed from approved epics and spec-driven artifacts, or an owner-approved direct task list when the pipeline is not justified.

## Development Workflow

1. `create-epic` turns an evidence-backed idea into a scoped epic, or a direct task list when the SpecKit pipeline is not justified.
2. For an epic, `epics-manager` requires the project's SpecKit toolkit and guides its specification, approval, planning, tasks, and cross-artifact review stages. For a direct task list, report its path and the owner-selected next action instead.
3. In a fresh session, `coordinate-implementation` revalidates the pipeline approvals and implements the approved spec, plan, and tasks in dependency order with mandatory delegation. A direct task list alone does not enter this coordinator.
4. `requesting-code-review` and `receiving-code-review` obtain and act on an evidence-based review.
5. `initialize-documentation` establishes documentation owners and the project's directory indexes; changed projects first create a documentation epic.
6. `finish-session` maintains documentation, open-issue, deployment, project-memory, and temporary-execution-state invariants.

## Use Cases

### Initialize Documentation

```
Use the initialize-documentation skill for this project.
```

### Deliver Recorded Session Work

```
Use the create-epic skill to create an epic for the documented work in [TODO list file / audio transcription].
If an epic is created, run epics-manager with its path.
If an owner-approved direct task list is created, report its path and the owner-selected next action, then stop this delivery workflow without invoking epics-manager or coordinate-implementation.
After epics-manager completes, use the finish-session skill.
```

For an epic with an approved epics-manager handoff, in a fresh session:

```
Use the coordinate-implementation skill for the approved work.
Workflow origin: epics-manager
Specification: [specification path from epics-manager handoff]
Plan: [plan path from epics-manager handoff]
Tasks: [tasks path from epics-manager handoff]
Source brief: [source brief path from epics-manager handoff]
Specification approval: [record path and section from epics-manager handoff]
Overall review approval: [record path and section from epics-manager handoff]
Review evidence and decisions: [record paths and sections from epics-manager handoff]
Use the finish-session skill.
```

### Deliver Open Issues

```
Use the create-epic skill to create an epic that addresses the selected open issues in docs/open_issues.md.
If an epic is created, run epics-manager with its path.
If an owner-approved direct task list is created, report its path and the owner-selected next action, then stop this delivery workflow without invoking epics-manager or coordinate-implementation.
After epics-manager completes, use the finish-session skill.
```

For an epic with an approved epics-manager handoff, in a fresh session:

```
Use the coordinate-implementation skill for the approved work.
Workflow origin: epics-manager
Specification: [specification path from epics-manager handoff]
Plan: [plan path from epics-manager handoff]
Tasks: [tasks path from epics-manager handoff]
Source brief: [source brief path from epics-manager handoff]
Specification approval: [record path and section from epics-manager handoff]
Overall review approval: [record path and section from epics-manager handoff]
Review evidence and decisions: [record paths and sections from epics-manager handoff]
Use the finish-session skill.
```

## Supporting Workflows

- `track-open-issue` gives verified unresolved work a durable owner without derailing the current session.
- `scientific-method-debugging` observes the running system before forming causal hypotheses.
- `handoff-prompt` produces concise, self-contained context for a fresh session or delegated agent.
- `using-git-worktrees` isolates work when the repository and task warrant it.
- Reusable practices borrowed from Superpowers include `brainstorming` and code-review workflows.

Global assets must not assume project paths, branches, deployment state, models, or agents. Run `/reload` inside pi after changing this repository's configuration-time assets.
