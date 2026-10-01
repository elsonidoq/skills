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
scanned location) and the spec-driven-development guidance into
`~/.agents/docs`, backs up anything in the way, and lint-checks the suite:

```bash
scripts/install.sh          # deterministic checks only
scripts/install.sh --probe  # ... plus one headless pi run that asserts the
                            #     suite skills appear in pi's system prompt
```

Start a new pi session (or run `/reload`) after installing.

On each project, run the `install-memory` skill first: it writes the suite contract into the project's instructions (epics, memory, state, docs) and initializes the project memory store.

## Repository Invariants

- Documentation describes the system as it exists.
- Database-backed projects maintain authoritative documentation of their current schema.
- Each project documents which material changes require which documentation owners.
- Memory records only non-obvious, durable guidance.
- Verified unresolved work has one canonical register: `docs/open_issues.md`.
- Features are developed from approved EPIC/SpecKit artifacts or reviewed requirements-manager tasks when the pipeline is not justified.

## Development Workflow

1. `create-epic` turns an evidence-backed idea into a scoped EPIC, or records the owner's approved lightweight route when the SpecKit pipeline is not justified.
2. For an EPIC, `epics-manager` requires the project's SpecKit toolkit and guides specification, approval, planning, tasks, and cross-artifact review. For a detailed lightweight requirement, `requirements-manager` preserves the requirement, uses shared brainstorming and task-generation contracts, reviews it, and records current approval without creating a specification or plan.
3. In a fresh session, `coordinate-implementation` revalidates applicable EPIC or requirements-manager approvals and implements approved tasks in dependency order. Up to three bounded tasks may run locally only when selected class and context fit; larger lists use asynchronous, sequential, context-coherent delegation. Verify and commit every task separately, then obtain one independent final review.
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
Use create-epic to assess the documented work in [TODO list file / audio transcription].
If an EPIC is created, run epics-manager with its path.
If the owner selects the lightweight route, run requirements-manager with the durable requirement/source; then use its approved handoff with coordinate-implementation.
After the applicable producer completes, use the finish-session skill.
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

For a lightweight requirement with an approved requirements-manager handoff, in a fresh session:

```
Use the coordinate-implementation skill for the approved work.
Workflow origin: requirements-manager
Requirement/source: [durable source path and section]
Tasks: [task path]
Current owner approval: [record path and content/revision evidence]
Review evidence and decisions/deferrals: [record paths and sections]
Applicable supporting artifacts: [paths]
Use the finish-session skill.
```

### Deliver Open Issues

```
Use create-epic to assess work addressing selected open issues in docs/open_issues.md.
If an EPIC is created, run epics-manager with its path.
If the owner selects the lightweight route, run requirements-manager with the durable requirement/source; then use its approved handoff with coordinate-implementation.
After the applicable producer completes, use the finish-session skill.
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

For a lightweight requirement with an approved requirements-manager handoff, use the same requirements-manager fields above and then `finish-session`.

## Supporting Workflows

- `track-open-issue` gives verified unresolved work a durable owner without derailing the current session.
- `scientific-method-debugging` observes the running system before forming causal hypotheses.
- `handoff-prompt` produces concise, self-contained context for a fresh session or delegated agent.
- `using-git-worktrees` isolates work when the repository and task warrant it.
- Reusable practices borrowed from Superpowers include `brainstorming` and code-review workflows.

Global assets must not assume project paths, branches, deployment state, models, or agents. Run `/reload` inside pi after changing this repository's configuration-time assets.
