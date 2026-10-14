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
plus applicable approved project guidance to assess consecutive sequential batches. First proposals inspect
demands/oracles, then material evidence or explicit non-reliance, then family and effort comparison before proposing;
normally
2–5 related tasks when feasible, never a quota. Assess every batch before presenting the complete
approval table, with a one/two-sentence batch description, exact proposed binding/effort and
independent family/effort rationales. Implementation authorization is not routing approval:
explicit `ask_user` approval of boundaries/profiles is required before implementation or dispatch.
Reuse verified unchanged approval on resume; changed boundaries/profiles need affected-row approval.
There is no universal Sol/medium default and no forced model diversity. Select one exact binding
and independently justified reasoning effort per invocation through owner choice; task assignments
never silently select a different profile inside that invocation. Apply **rubric first, capability
verification second**: **Prior launch success establishes availability, not superiority**. Compare
suitable family/effort options—even when an alternative has no previous launch history—and keep a
suitable proposal pending when readiness is incomplete. Catalog is distinct from authoritative
authenticated/runtime readiness and observed launch. Reuse applicable passive proof; use a
conditional source audit only for concrete uncertainty, contradiction, clamping risk, or absent
necessary support evidence. If verification is insufficient, surface the gap and ask for the
necessary authorization or an explicit fallback choice—not silently substitute Sol. An explicit
fallback needs its own rationale, readiness, and exact owner selection; model variety is not
itself a goal.
For one worker implementing one batch, normally use direct asynchronous delegation, even
with sequential internal tasks; workflow orchestration needs a concrete reason in the existing
brief. The [coordinator dispatch seam](skills/coordinate-implementation/SKILL.md#delegate)
owns this launch choice and the finite preparation rule: satisfied mandatory conditions lead
to dispatch without a state-specific intent commit; only concrete invalidation reopens affected preparation.

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
implementation commits, concrete task/runtime proof and one fresh independent final
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
and supported effort independently. Proposal precedes readiness: a suitable never-launched
option may remain pending while passive, authoritative readiness evidence is incomplete. Distinguish
catalog from authenticated/runtime readiness and observed launch; reuse current applicable proof
and audit provider/source mappings only for concrete uncertainty, contradiction, clamping risk,
or absent necessary support evidence. Missing readiness blocks dispatch, retains the proposal,
and requires bounded authorization or an explicitly selected, independently justified fallback.
Obtain one exact owner-selected binding plus effort; verify permissions, tools, callable binding
and supported effort at assignment and dispatch. Pass the selected profile unchanged through direct
calls and helper briefs/dispatch. A missing selection/support or settings/default mismatch blocks
work, never silently substitutes. Record proposed, selected and observed separately; unknown actual
binding/effort stays unknown. Implementation-only batching, task-count and REQUIRED-item rules are
not planning prerequisites.

The explicit owner-required exception is Standard `plan_create`: **Sol with exactly medium
supported effort** for the complete same-session specification review/fix → one plan creation →
produced-plan review/fix, both delegated non-helper and helper execution. Planner never
authors or repairs the artifacts: each artifact has a separate fresh bounded-context producer;
corrections use suitable originating producer context or a fresh bounded delegate. Missing,
unusable or unauthorized delegation stops with no parent inline/local fallback. Resolve its concrete binding from
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

Coordination memory is project-local explicit feedback only, separate from adopted gotchas.
The [shared contract](skills/memory-handling/references/project-coordination.md) owns relevant
existing guideline consultation and bounded user-feedback writes. Missing store/STATE is
nonblocking; no auto-init, routine summaries/index updates, evidence-only commits, reflection
or inferred lessons. Clear future corrective feedback can authorize a minimal guideline
without routine second approval; ambiguity asks, explanation-only/no feedback/no-write writes
nothing. Preserve local ownership/path/symlink, sensitive-data and dirty/concurrent safeguards.
Only a needed guidelines owner may be created, never history/index/run scaffolding.

## Context-first recovery

No automatic STATE creation/edit/removal. Preserve existing STATE/custom content. Start with
available conversation summary/recent context and selectively reconstruct uncertain approvals,
completion, Git ownership/checkpoints and actual child status under the
[recovery contract](skills/coordinate-implementation/SKILL.md#recover-context).
Unknown authority/completion blocks affected actions; active children mean inspect/wait,
unknown child status blocks replacement. Inspect failures before targeted retry; unknown
cause stops blind relaunch. No guessed completion, duplicate dispatch or repeated commits.

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
