# Independent specification review — TinySpec

## Outcome, provenance and authority

Give Standard/Spec Kit users a skeptical second look at missing product intent before
approving a specification. A spec can be internally clear yet leave authentication,
operational telemetry, human-useful interfaces, failure behavior or concurrency outcomes
implicitly to an implementer. This stage discovers consequential missing decisions, not
implementation defects or checklist compliance.

The owner selected TinySpec through `ask_user` for **this planning change**, with
`NO_BRAINSTORM_NEEDED` assessment and planning-only authority. Owner clarification:
“It should be a new stage”; “Yes” confirmed this order:

**Specify (including detected ordinary clarification) → Spec Review → incorporate user
answers → existing specification approval → Plan → Tasks.**

`spec_review` is a distinct Standard stage, not part of `spec_create` and not a renamed
clarification pass. This source alone is being prepared; separate tasks, planner review
and combined approval remain outstanding. Even final approval of this planning request
must not launch implementation. Future executable tasks must remain authorization-neutral;
this phase restriction belongs in approval/handoff context, not permanent task instructions.

## Scope and constraints

Included: planner Standard stage/correction/recovery instructions, one maintained reviewer
prompt reference, saved-operation mapping, focused existing regression checks and necessary
workflow/entry-point documentation. Preserve TinySpec, later independent `overall_review`,
specification and final approvals, source-producer ownership and current-content renewal.

Excluded: implementation in this request; new skills unless an existing mechanism proves
insufficient; extra approval gates; automatic second taxonomy questionnaires for reviewed
questions; default repeated review loops; frameworks, database, scoring, persistent review
artifact subsystem, specialized agent roles, hooks or runtime/orchestration expansion.
No global adoption migration, actual assignment rebinding, memory or STATE updates.

Accepted constraints (neither ADR grants unrelated execution authority):

- [ADR-0003](../decisions/ADR-0003-current-launch-authority-and-neutral-tasks.md),
  Decision/Consequences: later tasks and check permissions are authorization-neutral;
  current scoped launch authority is supplied by the existing runner, with temporary phase
  status in approval records. Source/task review must check this before handoff.
- [ADR-0004](../decisions/ADR-0004-shared-routine-worker-permissions.md),
  Decision/Consequences: ordinary scoped fixes and small isolated fixtures/tests/local
  databases use shared routine permissions, without repeated approval. Preserve resource,
  unrelated-data/services, credential, global-install, deployment/push and separately
  chargeable/external-action boundaries. Validation briefs carry these bounds; local tests
  are not authorization for unrelated external actions or blind expensive retries.
- [Project memory](../../memory/MEMORY.md), Parent-turn notifications: routine transitions
  must not wake the parent for acknowledgment; only actual questions or terminal completion
  require a parent turn. Do not add per-stage acknowledgment machinery.

## Evidence and smallest approach

Repository-derived findings at baseline `76ff6a6aaf15a93a7ecf9cc095dc8b604902e4ed`:

| Inspected owner / supporting span | Consequence and observable check |
| --- | --- |
| [Planner](../../skills/planner/SKILL.md), Standard `spec_create` currently owns clarification and specification approval; `plan_create` requires approved spec | Move the existing approval transition after new `spec_review`; test explicit stage order and absence of a bypass, without an extra approval |
| [Approval/recovery](../../skills/planner/references/approval-and-recovery.md), transition table and unanswered questions | Update affected transition/recovery text; carry pending answers and inspect drift, preserving valid approvals rather than migrating old work |
| [Assignments JSON](../../skills/planner/references/model-assignments.json), `standard-review`; [assignment reference](../../skills/planner/references/model-assignments.md) | Add operation `standard-spec-review` referencing existing owner-editable `standard-review`; do not change assignment values or hardcode models in portable instructions |
| [Resolver](../../skills/planner/scripts/model_assignments.py), `resolve`/`resolve_correction` | Generic operation lookup already suffices; no resolver production-code change expected. Test the new mapping and missing/unavailable binding behavior |
| [Specify prompt](../../.pi/prompts/speckit.specify.md), frontmatter direct plan handoff, Outline 6/8 and Completion Report; [clarify](../../.pi/prompts/speckit.clarify.md), Outline 3–8 | Direct shortcuts currently suggest planning; ordinary clarification scans taxonomy, asks up to five and writes spec/Q&A. Add small compatibility instructions, not a new clarification engine |
| [Plan prompt](../../.pi/prompts/speckit.plan.md), Setup and Load context; [helper](../../skills/delegating-architectural-planning/SKILL.md), managed adapter/preflight | Keep planning behind current spec approval and respect managed `spec_review`; helper's later review/fix pass is not a substitute and must not trigger automatic repeated spec review |
| [Checker](../../scripts/check-planner-workflow.py), `standard-order`, `spec` assertions and stage-local carriers; [tests](../../scripts/test-planner-workflow.py), Standard stage and assignment inventories | Move approval assertions to their actual new carrier and extend inventory/order/mutation checks; retaining a summary while deleting stage behavior must fail |
| [Installer](../../scripts/install-links.py), whole-skill symlinks; [setup/workflow](../../README.md#planning-and-implementation); [SDD lifecycle](../best_practices_spec_driven_development.md#sdd-role-and-lifecycle) | A reference inside planner ships through existing installation. Update active lifecycle/discovery text, not installation mechanics or global policy |

**Proposed exact change owners for later implementation:**
`skills/planner/SKILL.md`, new `skills/planner/references/spec-review.md`,
`skills/planner/references/approval-and-recovery.md`,
`skills/planner/references/model-assignments.json`,
`skills/planner/references/model-assignments.md`,
`scripts/check-planner-workflow.py`, `scripts/test-planner-workflow.py`,
`docs/best_practices_spec_driven_development.md`, `README.md`,
`docs/plans/planner-regression.md`, and narrow compatibility edits in
`.pi/prompts/speckit.specify.md`, `.pi/prompts/speckit.clarify.md`,
`.pi/prompts/speckit.plan.md`. Link the new prompt from planner; no separate routing index
entry is needed. No changes expected to resolver code, helper, setup, REQUIREMENTS,
constitution, executor, agent definitions, manifests or runtime. Revisit only on concrete
contradictory evidence through existing scope/review gates.

Compatibility choice: these repository-local SpecKit prompts should state that under
planner, their direct “Build Technical Plan” suggestions do not release planning: return
control after specify/required clarification for `spec_review` and existing approval;
plan must honor that gate. Clarify's write procedure supplies integration conventions,
not reviewer edit authority. Do not rewrite vendor taxonomy or hook behavior. Standalone
raw SpecKit invocations remain available but explicitly outside planner's independently
reviewed Standard guarantee; entry guidance routes users wanting that guarantee through
planner. Do not claim a new standalone slash command or silently wrap all vendor flows.
Existing tracked customization is preserved; do not relabel local prompts pristine upstream.

### Dependency and runtime evidence

Reuse [runtime requirements](../../REQUIREMENTS.md#runtime) and actual installed local
`pi-subagents` 0.73.1 README/tool-reference (`context`, `model`, `async`, `output`, resume)
plus local package version evidence: pi 0.87.1 (`pi --version`), pi-subagents 0.73.1,
pi-ask-user 0.15.1. No new external library, internet research or research document is
needed for this known instruction-wiring change. Local installed documentation is machine
context, not a portable path to embed in global skills.

Discovery supplied by the parent: registered callable `ask_user`; model registry includes
Sol 6.1, Terra and Astra; actual Terra assessment succeeded; user `reviewer` profile tools
are `read, grep, find, ls, bash, watchdog_diff, contact_supervisor`, without edit/write.
This source production did not repeat those calls or launch a child. At the future review
boundary reverify actual profile and exact saved assignment availability; do not infer
usability from package names or substitute another model. Current checkout `standard-review`
is Sol 6.1/medium, informational only; the binding is owner-editable.

Dispatch directly with explicit fresh context, async true, resolved `provider/id:effort`,
and runtime-bound report output using the installed tool interface. The child returns
findings and the runtime can persist output; do not give it spec-write authority to save
its report. Read-only is a tool/profile **and instruction boundary**, not a security sandbox:
`bash` can mutate. Prohibit writes, implementation, external actions and further delegation;
verify the spec remains unchanged in the actual boundary check. Reuse existing output/session
facilities, not a durable per-feature review-artifact requirement.

The installed planner symlink currently resolves to `/home/dev/projects/skills/skills/planner`,
not this worktree. Inspect and later edit checkout artifacts only; do not mutate installation
now. Future activation in Paseo needs a fresh-session handoff verifying checkout, revision,
approval and loaded capabilities; never instruct `/reload` or automatically restart.

## Stage behavior and maintained prompt core

`spec_create` finishes its normal specification work and any requested/detected required
ordinary clarification. Parent inspects that exact current spec, then launches a **fresh**
read-only `spec_review` with the source request, exact current spec path/content identity,
relevant repository/product context, governing constraints and applicable decisions/memory.
Do not include the producer's justification, transcript or unrelated history. Context can
resolve a question; the reviewer must use it rather than manufacture gaps.

Maintain this prompt core in the future canonical `skills/planner/references/spec-review.md`
(the text here is planning source, not an implemented prompt):

> Act as a skeptical, independent specification reviewer. Read the current spec and relevant
> project context. Your goal is to discover important missing decisions, implicit assumptions,
> and unintended behaviors that could result in an implementation that technically satisfies
> the spec but does not match the user's actual intent.
>
> Consider product intent: the user's ultimate goal, missing or undesirable experiences and
> outcomes. Consider behavioral completeness WHERE RELEVANT: errors, failures, edge cases,
> concurrency, security/authentication/authorization, observability, data integrity and operations.
> These are perspectives, not a checklist requiring a question in each category.
>
> For each gap, consider what a reasonable implementer might assume, a different reasonable
> implementation, the consequences of the wrong assumption, and whether spec or supplied
> context already establishes the answer. Focus missing PRODUCT decisions, not implementation
> details or checklist validation. Exclude answered/context-resolved questions and generic checks.
>
> Present AT MOST FIVE highest-impact unresolved decisions, ordered by importance. For each,
> give a concrete scenario, implementer assumption/divergent behavior and consequences, and a
> specific question, preferably with meaningful alternatives. Never invent a quota or requirements.
> If zero remain, explicitly say zero; do not fabricate questions. Never modify the spec or
> implement anything. Return findings only; parent owns user dialogue.

Parent asks **one concrete question at a time** through existing `ask_user`, retaining
scenario, consequences and alternatives. Apply each answer through the existing source
producer correction route: resume suitable originating context or use a fresh bounded
correction with the same producing assignment. Neither reviewer nor parent substantively
repairs the spec. Producer updates relevant requirements, scenarios/acceptance and existing
`Clarifications`/session `Q: … → A: …` conventions, removes contradictions and performs
applicable normal validation/checkpointing. Parent inspects returned changes before release.
Preserve required ordinary clarification; do not automatically rerun its taxonomy on already
reviewed/answered questions. Later queued questions made unnecessary by earlier answers are
not asked merely to fill five slots.

Zero questions proceeds directly to the ordinary specification approval brief/gate, with
no question-only interaction. Otherwise incorporate accepted answers before that same gate.
Unanswered/cancelled material questions stop affected planning; recommendations are not inferred
defaults. Honor owner stop/deferral through existing gates, with unresolved impact explicit;
no automatic deferral permits planning around a material unresolved dependency. After current
spec approval, use unchanged `plan_create`, `tasks_create`, independent `overall_review` and
final approval. No extra review approval, automatic rereview or default review loop. Concrete
source/spec/context drift invalidates only affected work/review/approval; recover from the
earliest affected boundary without imposing retrospective review on valid historical approvals.

## Observable acceptance and validation needs

These are future production acceptance, not an implementation task list or claims of tests run.
Task generation must carry their smallest checks/pass conditions and actual gates into local
REQUIRED items and worker/reviewer briefs, preserving accepted ADR constraints above.

- **A — Product intent:** An authored telemetry-dashboard spec that lists signals but leaves
  human purpose unspecified elicits what the user must understand/accomplish, not demands for
  more metrics. A useful answer changes relevant user outcomes/scenarios/acceptance.
- **B — Failure semantics:** A batch spec leaving per-item failure unspecified elicits meaningful
  abort/continue-partially/retry alternatives and their observable consequences, not a prescribed
  implementation mechanism.
- **C — Selectivity:** Sufficiently specified behavior returns explicit zero. Context-answered
  questions are excluded; all outputs have at most five unresolved decisions ranked by impact,
  concrete scenarios/assumptions/consequences/questions. No quota, generic questionnaire or
  gratuitous security/telemetry requirements.
- **D — Actual boundary:** A bounded fresh reviewer run receives exact spec/source/context but
  no producer rationale/transcript; before/after comparison proves spec unchanged. Parent asks
  one question, actual answer goes to existing producer correction, producer changes pertinent
  requirements/scenarios/acceptance and Q&A, then ordinary current-spec approval precedes plan.
  Zero skips questions; cancellation of a material answer prevents affected plan release.
- **E — Minimal integration/preservation:** Static carrier/trace/mutation checks detect missing,
  reordered or folded `spec_review`, approval/plan bypass, nonfresh reviewer, editing authority,
  wrong assignment or silent fallback, parent/reviewer repair, automatic repeated review and
  duplicate clarification. Preserve TinySpec, independent later overall review, both existing
  Standard approvals, earliest-invalid recovery, authorization-neutral tasks and routine isolated
  test permissions with external/data/resource boundaries. Stage deletion must fail even when
  summaries remain. Entry compatibility and linked prompt packaging must be checked.

Reuse `python3 scripts/check-planner-workflow.py` and
`python3 scripts/test-planner-workflow.py`, including focused existing stage parser, operation
inventory and link checks; document actual results/limits in `docs/plans/planner-regression.md`.
Use meaningful mutations of changed instruction carriers, not a new framework or textual freeze.
Known instruction wiring merits permanent focused tests, **not a separate prototype task**.
Static checks prove sensitivity, not model obedience. A–D require bounded actual reviewer
semantics/parent-producer boundary validation before behavioral acceptance, with usable exact
profile, `ask_user`, source-producer capability and scoped live/model authority. Missing capability
or permission is NOT RUN/UNAVAILABLE and blocks claiming that acceptance, not evidence of failure
or a reason for silent fallback. No feature evaluation is executed during source preparation.

When practical add a small blinded historical pre-correction spec evaluation: evaluator selects
verified snapshots and keeps known omissions/expected gaps separate from reviewer context.
Git history exposes `specs/004-workflow-monitor/spec.md` at `0537539`, `999c05e`, `6607085`,
`062f2d2`; inspection of the first snapshot's input/User Story 1 already shows human-purpose and
readable-description requirements. This is a discoverable candidate history, **not verified proof
of the alleged historical omission**. No evaluator-private known-gap pair was verified here.
Use authored A/B/C fixtures and report this limit honestly; use blind historical evidence only
when a genuine pre-correction gap/source pair is established. Do not invent retrospective proof.

## Dependencies, risks and downstream handoff

Main uncertainty is reviewer usefulness/selectivity and faithful parent/producer behavior;
static phrase checks cannot establish either. Small real-boundary validation is necessary,
not an architecture experiment or new orchestration system. Evidence applies to inspected
revision, prompt, profile and context; refresh only invalidated observations. A failed/inconclusive
live case blocks reliance on the claimed behavior and returns correction to existing review/
approval, not weakened acceptance or blind retries. Keep evidence in normal test/session outputs;
no disposable proof subsystem or separate cleanup deliverable is needed.

No data migration or runtime rollback is involved. Existing instructions remain effective until
later approved implementation/activation; ordinary focused Git changes can be corrected through
normal reviewed work without rewriting historical approval records. Scope above is a repository-
derived minimal proposal, not an assertion that every listed file needs large edits. No material
product choice remains open in this source; future task decomposition owns independent outcome
boundaries, not a stage-per-task quota.

Pass selected executor path **`.pi/workflow-executor.json`** unchanged to the separate task
producer, which must read it before decomposition (currently Terra/medium workers and Sol
6.1/medium reviewer). Do not derive implementation bindings from planner assignments. Preserve
six actual task-linter checks: readable file, parsed list, ID/work description, unique IDs,
existing dependency references and acyclic dependencies; no extra startup ceremony.

Return this source for parent inspection only. Separate tasks and combined review/approval
remain next planning operations under the explicit planning-only boundary; implementation,
new agents, assignments and live evaluation are not authorized by this source delivery.
