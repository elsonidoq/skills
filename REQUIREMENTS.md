# Coherence — Pi Skill Suite Requirements

This repository is a pi configuration repository. It is **not runtime-portable by design**:
it binds to specific pi packages, pins their versions, and relies on the convention that a
project adopts the suite through `initialize-coherence` before the workflow skills run.

## Runtime

| Requirement | Pin | Verified how | Missing behavior |
|---|---|---|---|
| pi coding agent | 0.87.x (tested with 0.87.1) | `pi --version` | Install or update pi |
| pi-subagents | npm:`pi-subagents@0.73.1` | the `subagent` tool is registered and usable | `Delegation: UNAVAILABLE`; stop and `pi install npm:pi-subagents@0.73.1` |
| pi-ask-user | npm:`pi-ask-user@0.15.1` | the `ask_user` tool is registered | Where a stage permits prose interaction, ask in prose and end the turn; do not proceed past the owner-answer gate or infer an answer. A manager's explicit mandatory preflight may stop earlier. |
| SpecKit toolkit | installed in the **project** for planner's Standard path | detected stage commands and assets exist in the target project | Stop at the affected Standard stage with a capability report; TinySpec/direct tasking does not require it |
| jev (optional) | `~/.agents/skills/jev` | `command -v jev` or the skill loads | Manual routing in `finish-session-jev` |

All npm pins are exact: pi treats versioned npm specifications as pinned, and `pi update
--extensions` reconciles the checkout without moving the configured ref.

Keep this table in sync with the dependency statements inside the skills. The
`initialize-coherence` skill records the approved requirement list in the project's
instructions during adoption. It reports missing prerequisites without installing them;
its mandatory question/approval-contract gates stop when unavailable.

## Implementation batch selection

Implementation tasks carry objective REQUIRED task-local verification items, expected
outputs, smallest sufficient checks and manual/permission gates through
[task-generation](skills/task-generation/SKILL.md), not mandatory model classes or shares.
The coordinator uses the [qualified seed rubric](skills/coordinate-implementation/references/batch-routing.md)
plus applicable approved project guidance to assess consecutive sequential batches, normally
2–5 related tasks when feasible, never a quota. Select one exact binding and independently
justified reasoning effort per invocation through owner choice; task assignments never
silently select a different profile inside that invocation.

At assignment and dispatch verify permissions, tools, callable binding and supported effort
through the installed runtime. Registry entries, thinking flags and suffix syntax alone
are not callability/support evidence. Copy the selected exact profile into actual dispatch
arguments and check settings/agent defaults do not override it. Requested/selected is not
observed: actual binding or effort remains unknown when unobservable. The settings
[sample](docs/pi-settings-sample.md) contains no unconditional implementation-worker override.
Seed examples are provisional, not hard-coded provider defaults or a universal repair ladder.

Dispatch supplies the whole REQUIRED union and returns concrete item-mapped evidence and
per-task checkpoints. The coordinator inspects every task diff/checkpoint, outputs, scope
and manual gates before accepting/releasing dependents. Missing/contradictory/unrun proof
blocks acceptance; passing contracts need no mandatory strong per-batch reviewer. Preserve
focused per-task implementation commits, separate evidence-only checkpoints and one fresh
independent final review over the complete committed range. Diagnose failures from child
run/invocation/partial commits before authorized targeted repair; preserve valid work and
prior attempts, supply the full contract and rerun invalidated items.

Static assertions and symbolic fixtures check instructions and sample artifacts, not live
model performance or runtime obedience. Live/provider checks require separate authorization
and usable permitted binding/effort/tool support; fixture success never substitutes for them.

### Separate planning/advisory stage options

Unrelated planning and reviewer selections remain separate, verified usable and owner-selected.
Existing stage labels/options below are not implementation-task assignments or a share rule.
Skills do not hard-code provider IDs; preserve stage-specific authority and preflight gates.

| Stage label | Meaning outside implementation assignment | Existing options |
|---|---|---|
| `sonnet-class` | bounded planning/advisory work | `deepseek/deepseek-v4.1-flash` (fallback `deepseek/deepseek-v4-flash`) |
| `opus-class` | advisory work that cannot be safely decomposed | `anthropic/claude-opus-5` or `openai/gpt-sol-latest` |

## Memory contract

Successful adoption through `initialize-coherence` establishes an approved project-memory
association and index, or validates a compatible existing one. Merely invoking initialization
does not establish readiness: missing capabilities, denied approval or missing structure block
it. Owner-selected paths remain valid; bounded refresh preserves existing memory and custom
policy. Retrieval and write rules live in `memory-handling`; `compact-memory`, `finish-session`,
`planner`, `tiny-spec`, `coordinate-implementation`, and `initialize-coherence` reference it.
A missing required gotcha association routes to `initialize-coherence`, never a guessed global store.

Coordination memory is mandatory and project-local, separate from adopted gotcha memory.
Its [shared contract](skills/memory-handling/references/project-coordination.md) owns compact
`GUIDELINES.md`, separate run/task evidence with a compact index, selective history retrieval
and explicit accept/edit/reject/add guideline approval with current-content drift protection.
Every entry point automatically initializes missing files, notifies the user and commits
only those files before proceeding. The default root is `<project-root>/memory/coordination/`;
existing declared project-local layouts use the same lifecycle. No setup approval, opt-out or
handoff-only persistence path. Existing files/staged work are preserved; failures to initialize,
commit or persist evidence stop with the exact blocker. Planner reads guidelines before depth
choice and carries constraints into both routes. Empty initialization invents no knowledge;
implementation approval never grants synthesized guideline mutation.

Optional `residual_reasoning: low|medium|high` notes describe task/oracle conditions,
not assignments. Existing indexed attempts retain exact selected/observed profiles or unknown,
assessment factors, contract strength, first/final outcome, diagnosed attribution and repair
references. Environment/tooling or other non-model causes do not penalize capability; weak or
invalidated successes cannot become strong positive guidance. Approved applicable guidelines
may override the seed, never source/owner permissions; raw outcomes never mutate guidelines.
No new store, schema, ML or automatic model optimization is introduced. Runtime pins and
unrelated stage options remain unchanged.

## Project docs

`docs/open_issues.md` holds the canonical register of unresolved work
(`track-open-issue`). `initialize-coherence` preserves or establishes documentation
owners/indexes and a verified project-specific documentation-routing guide, recording them
in approved project instructions. Persistent-database projects also require an authoritative
schema owner or documented set, even without a naming convention. Initially clean projects
may initialize verified content; non-clean projects first require fresh read-only investigation
and approved shell/index bounds, with no substantive documentation writes. Missing required
structure blocks readiness; empty/stale substantive content remains planner work, not completed
by a shell. `finish-session` checks owner/index/routing/schema existence without initializing
or auditing them.
## Task commit contract

Package-managed execution uses the shared [task-commit contract](skills/memory-handling/references/task-commit-contract.md).
It requires focused per-task Git checkpoints for authorized retained repository output, while preserving
compatible signing/message conventions, unrelated dirty work, and existing approval gates. It adds no
runtime extension, adapter, provider/model binding, dependency, installation, live probe, push, deployment,
or history rewrite requirement. Missing Git/identity/permissions, failed hooks/checks, unclear ownership, or
conflicting policy stops the affected task; static checks and temporary-Git fixtures do not prove model obedience.
