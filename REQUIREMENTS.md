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

## Model family and independent effort

Initial owner-facing families are Luna, Terra, Sol and Astra. A family implies no
provider, version, supported effort, price, context capacity or universal rank.
Portable skills never hard-code a provider/model ID. Verify the exact binding and
effort against provider documentation, permitted usable runtime support and the
owner's current selection before execution. Catalog-only availability is not callability;
unsupported runtime effort or missing required tools/context blocks the affected stage.
Explicitly verify nonadjustable behavior where applicable; omitted effort is not a known value.
Do not silently substitute a selected binding or infer selections from historical classes.

Use the [shared family/effort rubric](skills/memory-handling/references/project-coordination.md#family-and-effort-routing)
for each stage, task and independent reviewer. Family suitability and effort need separate
rationales after decomposition; choose the least supported effort justified as adequate
for residual reasoning. Risk strengthens safeguards, not automatic high effort or the
strongest family. Weak oracles return for decomposition and stronger observable acceptance.
No unconditional low/medium default, automatic maximum, universal family rank, fabricated
savings or mandatory per-configuration probe is introduced.

Benchmark coverage is advisory. A supported no-row pairing requires targeted research or
an explicit bounded owner uncertainty decision, not automatic exclusion or invented scores.
Neither source evidence nor an uncertainty decision waives hard capability, owner-selection,
REQUIRED checks, current-content approvals, dependencies, per-task checkpoints or review.
Present task/reviewer proposals before the single combined final implementation approval;
record approval of scope and listed routing selections distinctly. Changed or unusable
selections return for renewed affected owner decision, never a routine second selection gate.

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

Optional `residual_reasoning: low|medium|high` notes describe remaining task/oracle
conditions, not provider effort settings. Source-backed observations, derived provisional
guidance, owner preferences, factual local outcomes and synthesized guidelines remain distinct.
Retain initial source provenance even after guideline supersession; when a project retains an
archive, routine work uses compact index/research citations and matching rows on demand, never
automatic whole-dataset prompts. Exact-content guideline approval is independent of
routing/implementation approval. Runtime pins remain unchanged; no ML, dependencies, automatic
optimization or one-outcome permanent rules are introduced.

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
