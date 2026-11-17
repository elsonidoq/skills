---
name: planner
description: Use when a structured requirement needs scope assessment, reviewed planning artifacts, or recovery of an existing planning handoff before implementation.
---

# Planner

Turn the owner's request into reviewed, approved planning artifacts and an implementation
handoff. Own understanding, depth choice, dispatch, inspection and approval—not artifact
authoring or implementation. Ordinary direct coding needs no new planning artifacts or Epic.

## Understand the work and choose depth

Read the request or selected source, repository instructions/principles, relevant artifacts
and affected code, tests and interfaces. Inspect workspace changes and preserve unrelated
work. Ask the owner to resolve ambiguous source selection; do not assume paths or attach a
likely source. Stop discovery when the scope is supported, and state remaining uncertainty.

For fresh and resumed work, use [Memory Handling](../memory-handling/SKILL.md) to retrieve
explicit owner guidance and gotchas from the verified unified index. Apply its retrieval and
authority rules: missing optional memory or STATE is nonblocking; missing required memory
stops affected work. Consult [save-adr](../save-adr/SKILL.md#consult-and-propagate) for applicable
accepted outcomes, explicit mechanism constraints and source links. Re-establish applicability
on resume; do not rely on a prior-read claim. Consume these constraints in source acceptance,
task dependencies/gates, task-local REQUIRED checks and worker/reviewer briefs, not just links.
Conflicting authority or uncertain supersession returns to the owner for the affected decision.

Apply [Parsimony and Actionable Checks](references/parsimony.md) during assessment and production.
Verify load-bearing positive and negative claims, including “already satisfied” and “no task
needed,” at their source layer with paths/symbols and relevant verbatim evidence. Mark unchecked
claims UNVERIFIED; resolve material uncertainty empirically or obtain explicit owner deferral.
Do not invent a beneficiary. Record exclusions and separately scheduled mechanical work.
Distinguish owner requirements, verified interface limits and agent design choices; correct a
mistaken premise before relying on it. Interpret owner agreement within the scope actually
presented. Verify a claimed blocker at the affected consuming interface; do not turn a tool-operation
limit into a project or artifact limit. Resolve mechanics autonomously; material product, architecture, privacy, permission,
cost, irreversible or settled-requirement changes need the owner.

Fresh planning is read-only until explicit depth selection: no source edits, decisions, specs,
plans, tasks or dependency-document writes. Keep findings, answers/rationale and deferrals in
session history. Invoke `planning-brainstorming` directly in the parent in preselection mode,
with readiness target “informed scope assessment.” Consume its readiness result: with
`NO_BRAINSTORM_NEEDED`, assess scope without a child call; with `BRAINSTORM_NEEDED`, conduct
its bounded agenda and owner dialogue yourself, one material item at a time. Do not delegate
the gate or resolve `brainstorm-assessment`. A settled request skips extended dialogue, not assessment.

Present the affected subsystems and contracts, dependencies, data/migration, security,
concurrency/deployment, verification, sequencing, uncertainty, reversibility and likely work
units. Explain the value of separate planning without line/task quotas. Offer BOTH paths and
a proportionate recommendation:

- **TinySpec → Tasks → Implement:** compact what/how source and separate tasks.
- **Standard: Specify → Plan → Tasks → Implement:** installed SpecKit stages.

Either choice is valid. Call `ask_user` and STOP. Denial, cancellation, timeout or ambiguity grants no consent.
Selection authorizes preparation only: writing and committing bounded planning artifacts and
necessary factual evidence. Pass that authority to producers; do not ask for separate planning
commit permission or defer checkpoints until content approval. Preserve selected depth on
resume; resolved uncertainty alone does not reroute. Material scope change or explicit owner
direction may reopen the choice with reasons.

After understanding/brainstorming, use [track-open-issue](../track-open-issue/SKILL.md#establish-planner-issue-association)
to establish a supplied or matching issue against the declared tracker before planned artifact
production. Require confirmed creation or qualified exact reuse, not a proposed issue body or
an unverified URL. Consume the qualified URL in artifacts, briefs and handoff. Creation needs
specific authority, separate from planning preselection; once the actual target and issue-create
operation are authorized, proceed without a repeated routine creation question.

For no-issue entry, consume the tracker's complete open/closed overlap discovery, exact issue
body/identity/state readback and separate body-quality review when creation occurs. Reuse an
open or closed exact match without duplicate or reopen. Missing/conflicting target, capability,
authentication or required operation scope stops association and planned artifact production:
name the affected operation and concrete corrective action, never a local fallback register.
Read-only understanding, needed owner dialogue and depth assessment may continue; depth selection
alone does not release artifact production. Created/read-back but review-incomplete is not ready.
This planner boundary adds no runtime intake requirement: bare runtime tasks and execution
without a delivery issue remain valid, and an existing qualified issue is not recreated.

<a id="selected-production-and-stage-handoffs"></a>

## Arrange the next authorized stage

Use direct asynchronous single-stage dispatch. After each return, inspect the actual artifact,
checks and focused checkpoint before the next authorized stage; never prewire dependent
source → tasks. Advance without a second routine “shall I continue?” question, dispatching
async work before returning control. A workflow needs concrete branching, independent parallel
work or another need direct delegation cannot serve—not a single child or convenient stage
sequence. Explain that need in the brief and preserve parent inspection and gates. This grants
no parallel implementation authority.

Verify required skills, references and usable capabilities at the operation that needs them
under [runtime requirements](../../REQUIREMENTS.md). Missing packaging needs a missing-install
report; missing capability needs the affected operation and concrete correction, not installation,
simulation or inline substitution. Verify callable `ask_user` at owner gates; if unavailable or
failing, report `question: UNAVAILABLE` and stop that gate without inferred consent.

Use `coherence-producer` for creation/correction and `coherence-reviewer` for independent review.
Verify the required global user role with `subagent get`: inspect user source, effective prompt
and tools under [role setup](../../README.md#coherence-role-activation). Missing, conflicting or
incompatible roles stop affected dispatch; do not substitute another agent. Every new artifact
uses a separate fresh bounded-context producer. Parent dialogue, inspection and approval are
not delegation, and the parent never authors fresh artifacts or makes substantive repairs.

### Saved planner assignments

Resolve each operation through [model-assignments.json](references/model-assignments.json) and
its [saved-assignment contract](references/model-assignments.md). Pass the exact resolved binding
unchanged in invocation and brief; verify it is permitted and callable at dispatch. Configuration
alone is not availability evidence. Missing, malformed, unsupported or unavailable bindings
return the resolver's focused owner correction question, with no recommendation or substitute.
Parent assessment/dialogue retains the owner-launched binding. TinySpec final correctness review
inherits `planner-parent` in a fresh reviewer; simplicity uses the same final-review binding in
another fresh session. Planning assignments do not select implementation models or batches.

Corrections retain the producing operation's assignment. Use suitable originating context;
if a saved edit conflicts with that context, obtain precise stage-specific resolution. Inspect
a failed expensive invocation and its call before retry, resume or replacement. Unknown cause
stops; never blindly relaunch.

Only for authorized selected-source decision application, invoke `planning-brainstorming` with
`brainstorm-application` and the recorded answers; consume its bounded source update, not new decisions.

### Give producers the inputs their owners require

Supply one bounded brief with the exact source and current content, selected depth, stage
and commit authority, allowed writes, prohibited operations, exact saved assignment, governing
instructions/principles, settled/non-obvious constraints verbatim, accepted outcomes and source
links, applicable memory, prior-stage return, actual owner answers and pending deferrals/gates.
Re-present unanswered questions rather than reconstructing decisions. Do not forward full
transcripts or unrelated history. Require a return with changed paths/content evidence, checks,
checkpoint, decisions, constraints and links, verification mappings and remaining blockers.

For both paths, consume these existing owners at the relevant operation:

- Before consequential dependency decisions, apply the [dependency research contract](references/dependency-research.md).
  Consume reuse/skip/refresh rationale, capability evidence, canonical owner/discovery links,
  version/provenance and supporting spans → constraints → observable checks. Give producers
  bounded permission for required canonical research/discovery writes during selected production,
  in addition to SpecKit artifacts. Inspect the returned persistence and evidence mappings before
  readiness, including direct and helper routes. Missing required evidence or authority stops
  affected design; only explicit bounded owner deferral can permit it, with impact, allowed bounds
  and outstanding validation. Never substitute recollection or invent evidence.
- For source creation only, read the [SDD reference](../../docs/best_practices_spec_driven_development.md)
  and supply its quality guidance to the source producer. Consume complete relevant behavior,
  approach, constraints and observable acceptance. TinySpec/specification is requirements truth;
  the plan supplies derived sequencing only. Do not forward or reread SDD as downstream
  requirements input. Governing instructions, memory and permission/safety rules still apply.
- Use [early risk reduction](references/early-risk-reduction.md) for consequential uncertainty.
  Consume justified proof selection/omission, actual evidence and limits, necessary dependencies,
  applicability/lifetime, production acceptance and disproof/renewal results. Failed or unrun proof
  cannot release reliance. Planning schedules proof, not execution without separate authority.
- Before decomposition, resolve the selected executor with
  `python3 scripts/resolve-workflow-executor.py --project PROJECT_ROOT` from the suite checkout
  ([resolver](../../scripts/resolve-workflow-executor.py)). Verify Python and resolver availability;
  use `--executor PATH` only for explicit override. Pass its exact absolute stdout path unchanged
  to both direct TinySpec and Standard task-producer briefs and coordinator handoff. Do not search,
  create/copy or substitute configuration. [Task-generation](../task-generation/SKILL.md#executor-sized-outcomes)
  owns the producer's actual JSON read, invalid/missing worker model/effort correction and outcome
  sizing. Consume independently finishable outcomes sized for that executor, not the planner profile.
  Use its outcome/proof and authorization-neutral task contracts for production and final review;
  preserve whole REQUIRED check mappings and actual manual/permission gates through both adapters
  and legacy renewal. Do not add execution-intent or compatibility metadata.

<a id="proportionate-validation"></a>

Keep facts once in their authoritative artifacts. No administrative ledgers, progress records,
evidence manifests, STATE maintenance, inferred lessons or routine memory writes; runtime state
stays runtime-owned. Carry this boundary in briefs. Reuse settled evidence until changed scope,
content, revisions, environment or capability/ownership invalidates it. Use the smallest meaningful
check and report limits; static/fixture checks do not prove model obedience. Preserve required
runtime, integration, application, security and permission checks, including genuinely required
live acceptance. No mandatory prior/candidate run, live RPC scenario or full historical replay.
Optional hardening is not an acceptance blocker; changing required acceptance needs owner authority.
Inspect returned checks for the changed observable, using integration when mocks cannot detect the
failure; retain necessary migration, authorization and persistence checks. Avoid automatic exhaustive
matrices or new test infrastructure without a concrete need. Separate unrelated recovery repairs;
a prerequisite needs evidence that it blocks the selected change, not repeated historical intake.

## Produce and review the selected artifacts

For both depths, apply [interactive design agreement before detail](references/approval-and-recovery.md#interactive-design-agreement-before-detail).
Discover the project-owned HTML destination; have the authorized producer create the actual
self-contained interactive HTML high-level design, then show it and obtain explicit owner
design agreement before detailed architecture plan production or continuation. Pass shown
content identity, actual answer/scope and ordering to downstream producers/reviewers. Page
interaction, silence, denial or cancellation grants nothing. Significant design changes renew
agreement before affected planning; reuse a settled grant only for its actual shown scope.
Requirements approval, design agreement and final implementation approval remain distinct.
Routine mechanics remain autonomous; no new task schema or runtime startup gate is added.

### TinySpec path

1. Resolve `tinyspec-source`; delegate `tiny-spec` with request, decisions, observed destination
   and preparation authority. First receive its what/acceptance and HTML high-level design;
   obtain the design agreement above before resuming the producer's detailed how. Inspect its
   source and returned research/risk results. No SpecKit
   prerequisite applies.
2. Resolve `tinyspec-spec-review`; apply the shared specification-review contract below. Inspect
   source-producer corrections before tasks. Zero or resolved findings go directly to tasks;
   there is no separate TinySpec source approval.
3. Resolve `tinyspec-tasks`; delegate a separate task producer using the `task-generation` direct
   adapter and selected executor path. Consume separate human/executable tasks, source links,
   checks and execution-risk findings. Derive documentation work from inspected effects and
   requirements, not an absent plan.
4. Run the shared final task-review contract below with `planner-parent` for correctness and
   simplicity on the same source/tasks. Resolve findings before combined approval.
5. Obtain combined current source/task/implementation-scope approval under the approval contract,
   then continue to handoff. Denial returns to correction, not execution.

### Standard path

After Standard selection, inspect installed SpecKit commands, instructions and templates for
each needed stage; report AVAILABLE/UNAVAILABLE with evidence. Do not install, simulate slash
commands or substitute ordinary Markdown. Missing/template-only constitution principles need
owner-derived answers through the observed constitution capability and verified repaired output.
Missing repair capability, principles or verification stops affected work; do not reopen valid principles.

1. **`spec_create`:** resolve `standard-spec-create`; delegate a fresh specification producer using
   observed specification instructions and the source-creation guidance above. Clarify only when
   requested or required. The delegate resolves mechanics and returns material choices. Finish
   ordinary clarification and parent inspection of the exact source before review—not approval or planning.
2. **`spec_review`:** resolve `standard-spec-review`; apply the shared specification-review contract.
   Report total findings and meaningful areas, initially the five most important (all if fewer),
   and offer all findings or a grouped overview. This is a presentation batch, not a discovery or
   resolution cap. Retain all findings in existing context and continue through all material ones.
   Ask one material owner question at a time with scenario, alternatives and consequences; discard
   queued questions resolved by an answer. Send actual answers to the originating specification
   producer under its saved assignment to update requirements/scenarios/acceptance and the existing
   `Q: … → A: …` convention, remove contradictions, validate and checkpoint. Inspect corrections.
   Do not rerun ordinary clarification taxonomy. Every material decision needs an answer or explicit
   owner deferral with consequences and permitted planning bounds; cancellation releases nothing.
   With zero findings, skip questions. After zero or inspected corrections, obtain and durably record
   current-specification approval before `plan_create`, then immediately continue.
3. **`plan_create`:** first arrange the project-owned HTML high-level design under the selected
   plan-producer assignment and preparation authority, then obtain design agreement before
   setup-plan or detailed plan production/continuation. Do not dispatch an uninterrupted
   page-to-detail pass without that actual grant. After agreement, resolve `standard-plan-helper` when using `delegating-architectural-planning`,
   otherwise `standard-plan-direct`. Delegate the entire same-session pass: review/fix the
   specification, create one plan through the observed capability, then review/fix the produced plan.
   Use the helper's [planning contract](../delegating-architectural-planning/SKILL.md#planner-standard-adapter-contract)
   for either route's architecture, evidence, write bounds and return. When the helper is invoked,
   inspect its return; do not create the plan again. The parent never performs this pass. Changes
   to approved specification content require renewed specification approval with a new executive
   brief before leaving this stage, except proven equivalence under the mechanical contract below.
4. **`tasks_create`:** resolve `standard-tasks-create`; delegate a fresh producer using observed
   SpecKit tasks and `task-generation`, with the source, plan and selected executor path. Authorize
   create-only preparation: drafting, revision, shortening and mechanical validation of unsubmitted
   output need no supervisor permission, but cannot change approved requirements or replace review.
   Consume checked human/executable tasks and their mappings/risks; submitted defects go to final review.
5. **`overall_review`:** use `standard-overall-review` (or `standard-overall-rereview` for fresh
   rereview) and the observed analysis capability for the shared final task-review contract, with
   simplicity in parallel. Resolve supported corrections and renew affected upstream approvals.
6. Obtain overall approval of current source, specification, plan, tasks and implementation scope,
   including plan-phase implications, then continue to handoff.

### Shared specification-review contract

Both paths require one fresh independent read-only source review before downstream production.
The reviewer is separate from the source producer and parent history.
Use [the canonical review prompt](references/spec-review.md) for fidelity to user intent. Supply
only its bounded inputs: original request, actual owner clarifications/decisions, the current
HTML design and actual agreement evidence when available, relevant
constraints/accepted decisions/memory, exact current source path/content identity and readable
content. Exclude producer rationale, conclusions and unrelated history. Verify the saved binding,
fresh read-only async capability, source producer and question capability; dispatch `async: true`.
Bind the report to that invocation and compare source content before and after review. Reviewers
return ranked findings or justified zero, not edits, approval, implementation, external actions
or delegation.

Inspect the report's evidence for coverage, downstream clarity and simplicity, including limits;
unchanged content identity alone proves no complete intake. Request targeted completion of a
material gap in the existing reviewer context, not an automatic second review. Route evident
fidelity defects to the source producer, material decisions to the owner, and inspect corrections
against intent and findings. Unresolved material intent gaps stop downstream production; a bounded
deferral can exclude affected work but cannot release reliance on the gap. No new tracker,
automatic rereview loop or additional approval gate.

### Shared final task-review contract

1. Prepare two bounded handoffs against the same current artifact snapshot. Correctness receives
   the original request, actual owner decisions, authoritative source, final human/executable tasks,
   Standard plan when present, and verified constraints/risks—not producer conclusions, assurances
   or approval trajectory. It checks correctness, completeness, feasibility, traceability, exclusions,
   docs/integration, dependencies, principles, approvals, verification item completeness and requirement alignment.
   Findings name the affected passage, impact and correction; do not manufacture stylistic defects. Apply
   the [design and task proof review](references/spec-review.md#design-and-task-proof-review),
   task-generation's independently executable outcome and authorization-neutral contracts, the
   research evidence/permission results and early-risk review results above in both paths. Return
   each material execution risk/prerequisite with affected task, concrete need, evidence versus
   unknowns and next investigation, mitigation or permission for coordinator preparation before
   worker reliance. Do not ask correctness for a simplicity verdict or forward the simplicity checklist.
2. Before launching either reviewer, independently inspect that snapshot and answer in session:
   **Does the current plan induce scope creep or over complexities?** Give concrete findings and
   basis, or justify none. Keep this parent analysis out of both handoffs.
3. Launch both fresh independent read-only reviewers before awaiting either report. Never fork or
   resume parent, producer or the other review for these first passes. Use the selected final-review
   binding unchanged for both. Do not send findings between reviewers or begin corrections until
   both reports return. Missing review evidence stops approval, not the other independent review.
4. Assess all three analyses together. Check findings against requirements and sufficient alternatives;
   explain rejected findings with evidence. Combine supported corrections into one bounded brief
   for the appropriate producer; resume useful originating context, otherwise use a fresh correction
   producer. No fixer is needed without supported corrections. Resolve material findings before
   approval. Target review gaps through existing reviewer contexts; if corrections invalidate coverage,
   recheck affected changes and interactions, not an automatic full-review loop.

### Shared simplicity-review contract

For the parallel simplicity handoff, use [the simplicity prompt](references/simplicity-review.md),
not the correctness or broad production checklist. Start with executive bullets of what the owner
wants, why and essential scope boundaries, grounded only in the original request and actual answers.
The summary adds no requirements. Supply the authoritative sources, current specification and
human/executable tasks (plus Standard plan), applicable project constraints, accepted decisions,
memory and relevant code access. Exclude producer rationale, prior verdicts, parent criticism and
full transcripts. Consume its per-task findings and cross-task check, including evidence limits.
The aim is the simplest sufficient delivery, not fewer tasks or weaker required acceptance.
Before presenting final approval, summarize planned task specifications in one sentence and answer
“Does the current plan induce scope creep or over complexities?” using the tasks and both reports,
not just verdicts. Agent-added constraints remain challengeable; genuine requirements and safety,
manual and permission gates remain binding.

## Approve current content and hand off

Before the first approval, read the [approval/recovery contract](references/approval-and-recovery.md).
At every approval or renewal, present its content-first executive bullet brief in conversation
BEFORE `ask_user`, including every actual ordered plan stage and task ID/outcome when applicable,
not invented TinySpec plan stages. Consume the affirmative answer, exact approved current content
and next authority in existing artifact/decision conventions. Communicate that final approval
starts coordinator preflight unless explicitly planning-only or a separate-session handoff.
Older preparation-only approval never implies execution authority. Denied, cancelled, timed-out
or ambiguous answers stop affected continuation; they are not consent.

Submitted substantive or uncertain corrections, including tasks/upstream/legacy artifacts, return
to suitable originating producer context or a fresh bounded correction producer. The independent
reviewer never becomes the producer. Only direct typo, formatting or link repairs proven equivalent
under the [bounded mechanical correction contract](references/approval-and-recovery.md#bounded-mechanical-corrections)
may be made by the parent; consume its diff/equivalence and current-content evidence. Missing
usable authorized delegation stops substantive work, with no inline fallback.

On interruption, drift or legacy entry, use the approval/recovery contract's transition and legacy
mapping to recover provenance, selected depth, applicable current-content approvals, pending answers
and child/correction state. Read linked external decisions/approvals as well as artifacts; reconcile
active or unknown children before replacement. Preserve valid approvals and task-embedded sources;
return to the earliest invalid gate, not a forced TinySpec conversion or invented historical choice.
Ambiguous origin needs owner resolution. Inadequate REQUIRED contracts return to producing
review/approval for correction and renewal, not retroactive invented requirements.

Check current source/task consistency, ordering, reviews/approvals, proof applicability and unresolved
gates. Return in existing conventions, without a new state/handoff file:

- Producer `planner`, selected depth or mapped legacy origin, source provenance and qualified issue URL.
- Source, human/executable tasks, Standard plan/supporting artifacts, exact selected executor path,
  and approved current content/revision evidence.
- Checks/reviews and limits, accepted outcomes/constraints and links, decisions/deferrals, whole
  REQUIRED mappings, applicable proof/results and remaining gates. Include material task-specific
  execution risks/prerequisites and their next action before affected worker reliance.
- Combined TinySpec or both Standard approvals and explicit approved implementation scope/authority.

After final approval, automatically invoke `coordinate-implementation` in the same session. If the
owner explicitly requested planning-only or separate-session handoff, return the approved handoff
instead. Do not stop at a readiness summary by default. Missing capability or a new material gate returns the precise blocker and preserved handoff.
The executable runner alone implements, verifies required checks/gates and commits execution work;
planner does not select execution bindings/batches. Planning readiness is not feature acceptance.

Apply the shared [task-commit contract](../memory-handling/references/task-commit-contract.md) to each
authorized retained planning artifact or repair after verification, before later task writes or
handoff. Preserve unrelated work; Git, policy, verification or ownership conflicts stop the checkpoint.
Read-only work creates no empty commit.

## Maintain this skill

Run `python3 scripts/check-planner-workflow.py` and `python3 scripts/test-planner-workflow.py` from
the suite checkout. If Python is unavailable, report UNAVAILABLE and inspect manually. Static and
fixture checks are not model-obedience proof. Changed global skills in Paseo need a fresh-session
handoff, not automatic reload/restart or an owner `/reload` instruction.
