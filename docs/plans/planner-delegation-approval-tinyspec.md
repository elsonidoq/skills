# Planner delegation and complete approval briefs — TinySpec

## Status, provenance and outcome

Owner-selected TinySpec; preparation authorized, content approval pending. This is the
compact authoritative source, not a task list or implementation authorization. The owner
requested: “planner must always delegate the creation of the spec, the plan, and the tasks.
It must not create them ... context gets too large.” Before specification approval the
owner wants brief concrete scope bullets; before applicable plan/tasks approval, every
ordered stage and every task must be explained (“All the tasks”). The approved correction
includes delegated artifact corrections and prohibits inline fallback.

Beneficiary: the owner reviewing planning scope, and the planner retaining a compact
coordination context rather than generating artifacts itself. Desired outcome: fresh-context
artifact production and complete, brief, owner-visible approval coverage without more gates.

## Scope and boundaries

Included: portable planner production/correction instructions, approval/recovery semantics,
managed architectural-helper alignment, focused static/synthetic regression coverage, and
truthful regression/runtime/workflow documentation where current claims conflict. Primary
implementation seams are `skills/planner/SKILL.md`,
`skills/planner/references/approval-and-recovery.md`,
`skills/delegating-architectural-planning/SKILL.md`,
`scripts/check-planner-workflow.py`, `scripts/test-planner-workflow.py`,
`scripts/planner-trace.py`, and `docs/plans/planner-regression.md`. Update linked producer
contracts or `REQUIREMENTS.md`/workflow documentation only where necessary for consistency.
Also included: specification-quality guidance and downstream authority alignment at planner
Discovery versus source-stage briefs, `skills/tiny-spec/SKILL.md` production, and
`skills/task-generation/SKILL.md` direct/SpecKit adapter boundaries. The SDD best-practices
reference is a specification-creation input only, not a downstream plan/task requirements
input. No change to that reference is needed merely to make it a task input; align operational
consumers and trace this source's criteria instead.

Excluded: runtime SDK/enforcement implementation, dependencies or settings changes,
installation, external research, live provider evaluation, product implementation,
guideline mutation, historical evidence migration, a new approval stage, a new TinySpec
plan artifact, and changes to independently authorized standalone helper policy unrelated
to managed planner execution. Later task generation is separate; this source embeds no
implementation checklist.

## Evidence and settled decisions

Repository-derived facts, inspected at baseline
`308a262d431fdc1e860637bdc48427b1704a2415`:

- [Planner production](../../skills/planner/SKILL.md#selected-production-and-stage-handoffs)
  and paths (lines 228–389) already define bounded briefs, TinySpec source/tasks and
  Standard stages. But Standard `plan_create` (line 358) says “Only when no adapter is
  invoked perform the pass directly,” conflicting with mandatory delegated production.
- [Approval contract](../../skills/planner/references/approval-and-recovery.md#executive-brief-before-approval)
  requires “4–6 short bullets” before `ask_user`, including renewals. The count cap can
  omit actual stages/tasks. Its transition table owns the gates to preserve.
- [Architectural helper](../../skills/delegating-architectural-planning/SKILL.md#planner-standard-adapter-contract)
  owns the entire managed Sol/medium specification review/fix → one plan creation →
  produced-plan review/fix pass. Its standalone local fallback must not become a managed
  planner escape hatch. [Runtime requirements](../../REQUIREMENTS.md#planningadvisory-selection)
  preserve exact selected-profile support/callability and observed-versus-selected distinctions.
- `check-planner-workflow.py` currently requires the direct fallback and bullet cap;
  `test-planner-workflow.py` mutates those clauses. `planner-trace.py` lines 142–145
  rejects briefs outside 4–6 items. There is no `scripts/check-planner-trace.py` at this
  baseline: the actual trace checker is `scripts/planner-trace.py`.
- The whole [gotcha index](../../memory/MEMORY.md) has no entries and
  [coordination guidelines](https://github.com/elsonidoq/skills/blob/5088b25877467887dd41c9547197c6da43b3c165/memory/coordination/GUIDELINES.md) have no approved
  guidance; no history was needed or loaded. No project lesson or model-success claim
  is inferred.

Owner-derived decision: production must be delegated separately for each selected-route
artifact, using fresh bounded context, not one parent authoring session or a transcript-sized
handoff. TinySpec remains a combined what/how source followed by separate tasks; Standard
retains separate specification, plan and tasks. The planner continues to own understanding,
dialogue, inspection, review, approval and coordination, including writing its own brief.

Owner clarification (verbatim): “Tasks are not meant to use that document. That document
is meant to be used for spec creation and just that the rest should. Use the spec as grand
truth, and the spec should follow the best practices, that's the name of the file to make
sure that every information required to be the good quality spec planned and done. tasks
are in the spec.” Settled interpretation: the
[SDD best-practices reference](../best_practices_spec_driven_development.md) guides
**specification creation only**, including lightweight TinySpec creation. Its specification
quality sections require explicit outcomes, scope, contracts, deterministic rules, exclusions,
constraints and observable acceptance. The specification captures complete required behavioral,
approach and acceptance information; downstream plans and separate tasks derive from it as
requirements truth. An approved Standard plan is a derived sequencing input, not a competing
requirements authority. “Tasks are in the spec” does not embed a work-unit checklist or remove
the separate task artifact. Repository instructions, memory, operational stage contracts and
permission/safety gates still govern every actor; specification authority never waives them.

Dependency research: reuse adequate local runtime/package guidance in `REQUIREMENTS.md`;
this is an instructions-only use of existing delegation, not new runtime API integration.
No version-sensitive SDK decision or external refresh is required. Capability verification
at actual future dispatch is still mandatory; configuration/selection alone is not usability
proof. No reusable dependency note or new research owner is necessary.

## Approach

Make mandatory separate fresh-context subagent production explicit in the operational
stage carriers: TinySpec via `tiny-spec`, Standard specification via detected specification
instructions, Standard plan via the installed capability and managed helper where applicable,
and each route's tasks via the existing task-generation adapter. Loading a skill in the parent
is not delegation. Neither creation nor artifact correction may be authored directly by the
parent planner, including mechanical fixes or managed review fixes. Review findings are
bounded correction instructions for the producing delegate; use suitable originating correction
context when available, otherwise a fresh delegate with a compact correction handoff. Preserve
Standard tasks' create-only producer stage: corrections occur under overall review, delegated
rather than added as producer self-review. Independent Standard review remains independent.

Missing, unusable or unauthorized delegation blocks the affected production/correction
stage with an exact gap; no local/inline fallback, silent profile change or installation.
Use references and necessary verbatim constraints plus current artifact bounds, decisions,
permissions, findings and expected evidence; do not forward full transcripts or load unrelated
history. Inspect returned artifacts/checkpoints and stop on ownership or verification conflict.
Preserve selected profile, supported effort, permissions, failure inspection/retry rules and
focused task/evidence checkpoints. Standard's entire delegated plan pass still requires the
same exact permitted Sol-family binding with medium effort, resolved from runtime options,
not a provider/version hard-coded into portable operational instructions. Review-driven
approved-specification changes still require renewed specification approval.

Make the quality-guidance boundary explicit at discovery and dispatch: planner may inspect
the SDD reference to prepare specification creation, but supplies it as guidance only to
TinySpec/Standard source producers, not as general input to every stage. Source producers
apply it and retain complete relevant behavior, approach, constraints and acceptance in the
specification itself, with unresolved material gaps returned through existing gates. Subsequent
plan/helper and task-adapter briefs use that specification as authoritative requirements input
and the approved plan only for derived sequencing. Do not forward the SDD reference as their
direct input, instruct those delegates to reread it for requirements, or require T003 to
consume/update it merely as task-generation guidance. Keep their operational instructions,
applicable memory and safety/permission constraints distinct from requirements authority.
Checks compare actual scoped source/plan/task input carriers and source-criterion traceability,
not a blanket ban on governing instructions or a new documentation-maintenance requirement.

Replace the universal total-bullet cap with content-first concise coverage. Before each
existing approval call, the planner emits assistant-text bullets with concrete included
scope. Where a plan is part of that approval, include one brief bullet for **every actual
ordered plan stage**, identifying the stage and what it does. Where tasks are part of it,
include one brief bullet for **every actual task ID in execution order**, identifying its
outcome. Never truncate, merge multiple IDs/stages into one summary bullet, use “and the
rest,” or impose a six-item maximum. Add concise necessary exclusions/boundaries, settled
decisions, risks/deferrals, actual review/check results and exact current-content/next-phase
authority supplements. Links, delegated reports, hidden reasoning or tool context alone do
not replace the owner-visible brief. Renewals regenerate it against current content.

No new plan approval is introduced: TinySpec retains one combined source/tasks/scope gate;
Standard retains specification approval then overall spec/plan/tasks/scope approval. Plan
stage coverage belongs to Standard overall approval and any already-applicable plan approval
in recovery/adoption contexts, not an invented intermediary gate. TinySpec has no fictitious
plan stages; specification-only approval does not enumerate nonexistent tasks. Existing
planning-only boundaries and immediate approved continuation remain unchanged.

## Acceptance and validation

- **A1 — Delegated creation:** both routes explicitly prohibit parent creation and require
  separate fresh-context source/specification, applicable plan and task production. Static
  mutations removing an actual stage obligation or restoring direct fallback fail even
  when summary wording survives.
- **A2 — Delegated corrections:** parent mechanical/upstream/task artifact edits are
  prohibited; correction delegation and missing-delegation stops are observable in operational
  review/recovery carriers. Focused negative cases cover direct correction and fallback,
  preserving create-only Standard task production and reviewer independence.
- **A3 — Concrete complete brief:** before existing `ask_user` gates, including renewals,
  scope is concrete; every applicable actual stage and task ID appears once in order with
  a brief meaningful outcome. Synthetic trusted expected stage/task inventories include
  **more than six** entries and accept complete coverage, rejecting omissions, reordered
  items, collapsed catch-alls and empty headings. Do not infer expected inventories from
  the tested model's own brief. Semantic review compares outcomes to the actual artifacts.
- **A4 — Visibility and timing:** synthetic traces reject tool-context-only, hidden,
  post-question and stale renewal briefs. Existing cancellation, drift and continuation
  coverage remains valid. Trace format/count acceptance alone does not prove meaning.
- **A5 — No added gates or lost safeguards:** route/gate assertions preserve TinySpec's
  combined gate and Standard spec→overall gates, no standalone plan gate, exact Sol/medium
  entire plan pass, profile/permission/failure stops, reviewer independence, preparation
  commit authority and content-bound approval renewal. Portable skill text contains no
  project destination or concrete provider/version binding.
- **A6 — Assurance truth and discovery:** documentation matches committed contracts and
  actual named tests, calls offline results static/synthetic sensitivity rather than model
  obedience, and marks live/real-SpecKit checks NOT RUN unless separately authorized.
  Shared references/discovery links resolve. Global instruction changes require `/reload`.
- **A7 — Specification-only quality guidance and downstream truth:** operational source-stage
  briefs and TinySpec/Standard producers apply the SDD best-practices reference to produce
  complete relevant behavioral/approach/acceptance information in the specification. Plan/helper
  and both task adapters derive requirements from that specification, with approved plan as
  derived sequencing only; their briefs do not use the SDD reference as a direct requirements
  input. Focused carrier assertions/mutations reject forwarding it to plan/tasks, omission of
  source-quality application or competing requirements authority. Manual review traces source
  criteria into downstream checks, preserves separate tasks and actor-governing instructions,
  memory, operational contracts and permission/safety gates, and confirms no added gate or
  T003 best-practices input/document-edit requirement.

Smallest sufficient verification for later implementation: focused instruction mutations
and synthetic traces in the existing planner suite, manual route/gate/semantic comparison,
`python3 scripts/check-planner-workflow.py`, `python3 scripts/test-planner-workflow.py`,
and `git diff --check`. Use existing suite lint/link checks for changed distribution links
when applicable; do not build a new harness or exhaustive matrix. This source itself needs
scope/criterion/link inspection and diff validation, not a claim that implementation exists.

Early risk reduction: omit an executable runtime prototype. The difficult seam here is
instruction completeness and truthful approval coverage, cheaply inspected and made sensitive
with the existing offline checks; there is no isolatable library/algorithm core requiring a
new real-runtime proof. Contract changes feed regression assertions and documentation, then
production acceptance review; retain fixtures/evidence through their consumers. Failed checks
block reliance and trigger bounded correction and affected approval renewal, never weaker criteria.

## Risks and readiness

Instructions cannot guarantee model obedience or reduced context use in every runtime.
Trusted synthetic inventories demonstrate specified completeness only; semantic review and
separately authorized live evidence remain distinct. Missing usable delegation/profile support
blocks actual production. Content approval is pending until this source and separately delegated,
reviewed tasks reach the existing combined gate. No unresolved material source decision or
owner deferral is carried; no implementation or live evaluation is authorized by this deliverable.
