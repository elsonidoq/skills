# Pi Configuration

Global pi skills for deliberate feature delivery across unrelated repositories. The suite
binds to pinned pi packages and requires adoption per project; it is not runtime-portable.

## Setup

See [REQUIREMENTS.md](REQUIREMENTS.md). The installer verifies pi, installs missing pinned
packages, links suite skills and the SDD reference, and runs deterministic validation:

```bash
scripts/install.sh
scripts/install.sh --probe  # additionally invokes one model; authorize separately
```

Foreign entries at installation destinations are preserved and reported, not overwritten.
Retired links are backed up only when their target proves they belong to this checkout.
After installation or global skill changes, run `/reload` inside pi.

On a project, use `install-memory` to propose and approve the project association, memory
store and suite instructions. Existing adopters can approve a bounded refresh of the marked
suite section without rewriting custom policy or converting existing planning artifacts.

## Planning and Implementation

Start with one entry point:

```text
Use planner for this requirement:
<structured requirement or selected source path/section>
```

Planner inspects the requirement/codebase, brainstorms unresolved material choices, and
presents an approximate scope assessment. This phase is read-only. It always presents both
paths and stops for your explicit choice; the recommendation does not choose for you.

```text
                         ┌→ TinySpec → Tasks → Review → Combined approval ───┐
Request → Planner → Choose│                                                   ├→ coordinate-implementation
                         └→ SpecKit Specify → Spec approval → Plan → Tasks ──┤
                                                 → Analyze → Final approval ─┘
```

- **TinySpec:** compact context, scope, decisions, approach, acceptance and validation;
  mandatory separate tasks. Planner reviews both before one combined approval. No SpecKit
  or unnecessary spec/plan/research hierarchy is required.
- **Standard:** genuine installed SpecKit stages, separate what/how/task reasoning,
  specification approval before planning, independent overall review and final approval.
- **Both:** shared `task-generation` contract and durable current-content approval evidence.
  Before every artifact approval or renewal, planner presents a brief bullet-list executive
  summary in the conversation, then calls `ask_user`. You may approve, request changes or
  withhold approval. The brief states the next phase that approval will start.

After approval, planner immediately starts the next authorized phase without another
continuation prompt. Final approval automatically starts `coordinate-implementation` and
its preflight unless you explicitly requested planning-only or a separate-session handoff.
Capability failures, material owner gates and denied/ambiguous approvals still stop progress.

Choosing depth authorizes planning, not implementation. Existing legacy artifacts retain
original provenance, source shapes and applicable gates; planner owns their repair checkpoints.
No new Epic is required or produced.

After an approved handoff, in this or a fresh session:

```text
Use coordinate-implementation for the approved work.
Producer: planner
Planning depth: [TinySpec or Standard]
Source: [path/section]
Tasks: [path]
Supporting artifacts: [paths; Standard includes specification and plan]
Review and decisions/deferrals: [paths/sections]
Approval evidence: [combined approval, or specification and overall approvals]
Approved current content/revisions and implementation scope: [evidence]
```

Coordinator revalidates the handoff and preserves one shared execution graph: up to three
bounded tasks may run locally only when selected class/context fit; larger complete lists
use asynchronous sequential delegation. It verifies and commits each task separately and
requires one independent final implementation review. Planning depth does not select execution.

## Supporting Skills

- `planning-brainstorming`: shared bounded uncertainty gate and owner dialogue.
- `tiny-spec`: lightweight source producer; not an independent manager or executor.
- `task-generation`: task semantics, ordering, validation and adapter contract.
- `delegating-architectural-planning`: observed SpecKit planning adapter.
- `initialize-documentation`: owners/indexes and investigation-first bounded initialization;
  substantive documentation work goes through planner, without a forced depth exception.
- `requesting-code-review` / `receiving-code-review`: independent assessment and disposition.
- `memory-handling`, `track-open-issue`, `finish-session`: durable guidance and closeout.

## Validation and Documentation

Run `scripts/check-skills-lint.sh` for deterministic suite checks. See the
[planner regression guide](docs/plans/planner-regression.md) for trace fixtures, mutations,
read-only RPC smoke testing, full behavioral scenarios and evidence limitations. Static tests
are not proof of model obedience; live tests require separate authorization.

Use [docs/index.md](docs/index.md) to find the canonical documentation owner. Documentation
describes current behavior, memory contains only verified non-obvious gotchas, and
`docs/open_issues.md` is the canonical unresolved-work register. Global assets must not assume
project paths, branch, deployment state, named models or an invented artifact/state schema.
