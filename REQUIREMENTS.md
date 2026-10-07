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
2–5 related tasks when feasible, never a quota. Assess every batch before presenting the complete
approval table, with a one/two-sentence batch description, exact proposed binding/effort and
independent family/effort rationales. Implementation authorization is not routing approval:
explicit `ask_user` approval of boundaries/profiles is required before implementation or dispatch.
Reuse verified unchanged approval on resume; changed boundaries/profiles need affected-row approval.
There is no universal Sol/medium default and no forced model diversity. Select one exact binding
and independently justified reasoning effort per invocation through owner choice; task assignments
never silently select a different profile inside that invocation.
For one worker implementing one batch, normally use direct asynchronous delegation, even
with sequential internal tasks; workflow orchestration needs a concrete reason in the existing
brief/tracker. The [coordinator dispatch seam](skills/coordinate-implementation/SKILL.md#select-execution-capability)
owns this launch choice and the finite preparation rule: satisfied mandatory conditions and
committed intent lead to dispatch; only concrete invalidation reopens affected preparation.

At assignment and dispatch verify permissions, tools, callable binding and supported effort
through the installed runtime. Registry entries, thinking flags and suffix syntax alone
are not callability/support evidence. Copy the selected exact profile into actual dispatch
arguments and check settings/agent defaults do not override it. Requested/selected is not
observed: actual binding or effort remains unknown when unobservable. The settings
[sample](docs/pi-settings-sample.md) contains no unconditional implementation-worker override.
Seed examples are provisional, not hard-coded provider defaults or a universal repair ladder.

Verification per task; execution per coherent batch. Practical contracts preserve task/item IDs,
criterion/check/evidence/gates and optional distinction through both adapters. Compare closed
design and implementation difficulty with weakest oracle quality, check cost and observability
in the sole six-factor rubric; feasible combined verification and attributable failures inform
consecutive batching, with each producer checked before consumer work.
Dispatch supplies the whole unchanged REQUIRED union before coding and returns concrete
item-mapped evidence and per-task checkpoints; a shared check runs once with every mapping.
The coordinator cheaply audits coverage, criterion relevance, current revision/environment,
consistency, every actual task diff/checkpoint and owned scope/gates, not a full rereview.
Executor pass/fail/not_verified maps through proof to satisfied/failed/insufficient-evidence:
failed requires objectively demonstrated criterion violation; missing/irrelevant/stale/conflicting/
unrun proof is insufficient unless valid observations independently prove a defect. Retain
both proven defects and evidence limitations. Only satisfied REQUIRED items and fulfilled gates
release dependents; optional green cannot compensate. Required representative-sample manual
STOP needs inspectable sample and explicit user approval before downstream/full expensive
operation; approval permits only scoped continuation, never LLM self-review. Ordinary tasks
use practical observables without invented ceremony; inadequate approved/legacy contracts
return to producing review/renewal, not executor-defined weaker success.
Passing contracts need no mandatory strong per-batch reviewer. Preserve focused per-task
implementation commits, separate evidence-only checkpoints and one fresh independent final
review over the complete committed range. Inspect failed run/invocation/partial commits and
proof before authorized stronger implementation continuation for exact gaps under the same
original contracts, not generic strong review. Carry current SHA/state, prior proof, dependencies
and invalidations; preserve valid work/attempts and rerun invalidated items, reuse only confirmed
valid evidence. Unknown/non-model/manual/permission/contract gaps do not automatically escalate.
Clean retry is exceptional: documented justification, ownership/safe repository mechanics and
required owner/project gates first; no automatic reset/discard or batch rollback.

Static assertions and symbolic fixtures check instructions and sample artifacts, not live
model performance or runtime obedience. Live/provider checks require separate authorization
and usable permitted binding/effort/tool support; fixture success never substitutes for them.

### Planning/advisory selection

Planning/advisory invocations use the same
[qualified seed rubric](skills/coordinate-implementation/references/batch-routing.md): assess
all six applicable factors, including the weakest verification blind spot, and justify family
and supported effort independently. Obtain one exact owner-selected binding plus effort;
verify permissions, tools, callable binding and supported effort at assignment and dispatch.
Pass the selected profile unchanged through direct calls and helper briefs/dispatch. A missing
selection/support or settings/default mismatch blocks work, never silently substitutes.
Record proposed, selected and observed separately; unknown actual binding/effort stays unknown.
Implementation-only batching, task-count and REQUIRED-item rules are not planning prerequisites.

The explicit owner-required exception is Standard `plan_create`: **Sol with exactly medium
supported effort** for the complete same-session specification review/fix → one plan creation →
produced-plan review/fix, both direct and helper execution. Resolve its concrete binding from
permitted usable runtime options, not a provider/version hard-coded into skills. Unavailable
Sol/medium stops with the precise binding/support gap; no substitution, settings/default override
or standalone helper fallback may bypass this rule. It is an owner preference, not a family
hierarchy, capability ranking or benchmark claim. Independently authorized standalone helper
selection stays separate but cannot override a manager-governed Standard invocation.

Other selections—including TinySpec source/tasks, brainstorming assessment/application,
Standard specification/tasks and independent reviewer—follow the shared rubric, not fixed
stage families or replacement classes. Preserve planner-owned dialogue, stage order, approvals,
write boundaries and reviewer independence. See the operational
[planner](skills/planner/SKILL.md) and
[helper adapter](skills/delegating-architectural-planning/SKILL.md) contracts.
Settings examples are neither current owner selections nor capability proof.

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
`GUIDELINES.md`, one compact evidence file per new run with a shared index (older task files remain valid), selective history retrieval
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
references, batch/task item dispositions with proof references, reused/invalidated items,
exact escalation reason and next selected profile or pending selection. First/final selected
versus observed attempts and original unknowns remain attributable in the same SUMMARY/index.
Environment/tooling or other non-model causes do not penalize capability; weak or
invalidated successes cannot become strong positive guidance. Approved applicable guidelines
may override the seed, never source/owner permissions; raw outcomes never mutate guidelines.
No new store, schema, ML or automatic model optimization is introduced. Runtime pins and
stage workflow/approval boundaries remain unchanged.

## Brief current-state contract

Coordinator maintains BRIEF implementation-relevant current truth in project-owned root
`STATE.md`, or a declared project-local equivalent, through its
[snapshot/recovery contract](skills/coordinate-implementation/SKILL.md#brief-current-state-and-recovery).
It is not a coordinator-owned tracker or authorization record. Initialization records that
lifecycle without fabricated progress; finish-session reconciles the same snapshot. Preserve
custom content/write ownership, replace current truth rather than append history, and recover
from authoritative approval/Git/evidence/runtime state before continuation. Updates use only the
coordinator owner's exclusive write boundaries: approved start/imminent dispatch, immediate child-ID
capture with safe deferred commit, audited batch/verified local task checkpoint, genuine blocker,
final review/closeout, and materially changed recovery truth. Coalesce same-boundary changes and
skip byte-identical writes; polling, ordinary progress and healthy internal worker activity cause
no coordinator persistence. Reference worker evidence rather than duplicate its ledger. Reflection
occurs at terminal closeout or a genuine blocked pause, not routine batch transitions. Mandatory
worker task/evidence commits and local implementer duties remain unchanged.
Write/ownership/checkpoint failures stop affected work. No compaction hook, persistence framework,
runtime/settings change, dependency, automatic restart or live provider exercise is required.

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
