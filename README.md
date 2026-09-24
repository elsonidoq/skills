# OpenCode Configuration

Portable global OpenCode skills for developing features deliberately across unrelated repositories.

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
6. `finish-session` maintains documentation, open-issue, deployment, and project-memory invariants.

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

Global assets must not assume project paths, branches, deployment state, models, or agents. Restart OpenCode after changing this repository's configuration-time assets.
