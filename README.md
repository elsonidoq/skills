# OpenCode Configuration

Portable global OpenCode commands and skills for developing features deliberately across unrelated repositories.

## Repository Invariants

- Documentation describes the system as it exists.
- Memory records only non-obvious, durable guidance.
- Verified unresolved work has one canonical open-issue record.
- Features are developed from approved epics and spec-driven artifacts, not improvised in code.

## Development Workflow

1. `/create-epic` turns an evidence-backed idea into a scoped epic, or a direct task list when the SpecKit pipeline is not justified.
2. `epics-manager` resolves material decisions and guides specification, approval, planning, tasks, and cross-artifact review.
3. `coordinate-implementation` implements the approved tasks in dependency order and verifies acceptance evidence.
4. `requesting-code-review` and `receiving-code-review` obtain and act on an evidence-based review.
5. `/initialize-documentation` establishes documentation owners and an `index.md` for every documentation directory; changed projects first create a documentation epic.
6. `/finish-session` maintains documentation, open-issue, deployment, and project-memory invariants.

## Use Cases

### Initialize Documentation

```
Run /initialize-documentation for this project.
```

### Deliver Recorded Session Work

```
Run /create-epic to create an epic for the documented work in [TODO list file / audio transcription].
Run epics-manager with the epic at [created epic path].
```

### Deliver Open Issues

```
Run /create-epic to create an epic that addresses open issues OI-1, ..., OI-7 in docs/open_issues.md.
Run epics-manager with the epic at [created epic path].
```

### Implement Approved Tasks

For a tasks file with 15-20 or fewer tasks:

```
Run coordinate-implementation for the approved tasks from [created epic path].
Run /finish-session.
```

For a tasks file with more than 15-20 tasks:

```
Run /finish-session.
In a separate session, run coordinate-implementation for the approved tasks from [created epic path].
Run /finish-session.
```

## Supporting Workflows

- `/track-open-issue` gives verified unresolved work a durable owner without derailing the current session.
- `/scientific-method-debugging` observes the running system before forming causal hypotheses.
- `handoff-prompt` produces concise, self-contained context for a fresh session or delegated agent.
- `using-git-worktrees` isolates work when the repository and task warrant it.
- Reusable practices borrowed from Superpowers include `brainstorming` and code-review workflows.

Global assets must not assume project paths, branches, deployment state, models, or agents. Restart OpenCode after changing this repository's configuration-time assets.
