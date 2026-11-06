---
name: planner
description: Use when a structured requirement needs scope assessment, reviewed planning artifacts, or recovery of an existing planning handoff before implementation.
---

# Planner

Prepare work, never implement it. Own understanding, scope assessment, the owner's
TinySpec/Standard choice, review, approvals and the implementation handoff. Ordinary
direct coding needs no new planning artifacts; no new Epic is required.

## Job first; no coordinator bookkeeping

Produce substantive planning artifacts and approval inputs only; no coordinator bookkeeping.
Do not maintain administrative ledgers, progress records, evidence manifests or STATE.
Runtime-owned operational state stays runtime-owned. Carry this rule into every stage brief.
State each required fact once in its authoritative artifact and reference it elsewhere.
No repeated record polishing, duplicate evidence or unchanged rechecks.
Reuse applicable settled evidence and decisions; reopen only affected work on concrete
invalidating evidence: changed scope/content, stale approval, failed proof or capability/ownership drift.
Once required prerequisites are satisfied, advance the next authorized stage.
Never waive required approvals, safety checks, permissions, reviews or commits.
An unmet gate stops only the affected stage: report the exact blocker and smallest required resolution.

## Discovery and capability boundary

Read the request/selected source, repository instructions/principles, relevant existing artifacts
and affected code/tests/interfaces. Inspect workspace changes and preserve unrelated work.
Resolve ambiguous source selection through `ask_user`; do not attach a likely source or assume
artifact paths. Discover destinations after depth selection. Stop expanding discovery when
scope is supported; state remaining uncertainty rather than false precision.

Use [Memory Handling](../memory-handling/SKILL.md): read the whole verified unified index,
then relevant entries. Missing optional storage or STATE is nonblocking. Missing required memory stops,
without global-store substitution or initialization. Carry explicit owner guidance,
alongside gotchas, through source observables → dependencies or gates → task-local REQUIRED checks
→ worker/reviewer briefs. No default history intake, execution-time feedback routing, inferred
lessons or routine memory writes; retain the owner's explicit-feedback and safe-write boundaries.

Before affected planning, apply [save-adr](../save-adr/SKILL.md): read the whole discovered decision
index, relevant accepted records in full and needed supersession links; fresh/resumed contexts re-establish
applicability rather than claiming a prior read; proposed/superseded records are not
current policy; contradictory accepted authority or uncertain applicability stops only the
affected continuation for an owner decision. Carry applicable accepted outcomes and source links
into source acceptance, task checks and briefs; verify their effect, not merely their presence.

Apply the [dependency research contract](references/dependency-research.md): inspect repository
guidance and dependency/version evidence first; reuse adequate guidance and refresh proportionally
before consequential decisions. Verify permitted usable research tools only when needed.

Read the [SDD reference](../../docs/best_practices_spec_driven_development.md) for specification
creation only, including TinySpec. Use the SDD quality guidance to prepare source-producer briefs,
not downstream requirements inputs. Sources must retain complete relevant behavior, approach,
constraints and observable acceptance; unresolved material gaps return through existing gates.

Verify required skills/references and usable capabilities at the stage that needs them, not as
blanket startup ceremony. Missing packaging returns a missing-install report; do not duplicate,
install or simulate unavailable capabilities. Verify callable `ask_user` before owner gates;
if unavailable/failing, report `question: UNAVAILABLE` and stop that gate without inferred consent.
Standard-only SpecKit/constitution checks happen after Standard is selected.

Treat positive and negative claims as claims, especially “already satisfied” and “no task needed.”
Verify load-bearing claims at their source layer with paths/symbols and relevant verbatim evidence;
mark unchecked claims `UNVERIFIED`. Resolve material uncertainty empirically or obtain an explicit
owner deferral. Do not invent a beneficiary. Record exclusions and separately scheduled mechanical
work to prevent duplicate tasks. Resolve mechanical facts autonomously; material product,
architecture, privacy, permissions, cost, irreversible or settled-requirement changes need the owner.

Before declaring a blocker, identify the exact affected operation and actual enforced limit at the
consuming interface. Do not generalize a tool-operation limit into a project/artifact/workflow limit.
Distinguish owner-requested behavior, verified runtime restrictions and agent-selected design choices.
An agent inference is not an owner requirement; interpret owner agreement within the explanation
and scope actually presented. Correct a mistaken premise and affected derived constraints before reliance.

## Coherence role dispatch

In the dispatching Pi session, use the suite-owned global user agents `coherence-producer`
for artifact creation/correction and `coherence-reviewer` for independent reviews.
The suite installer links their definitions into `~/.agents/`; project activation is not
required. Verify them as described in [setup](../../README.md#coherence-role-activation):
use `subagent` action `get` to inspect each required role's user source, effective prompt
and tools. Missing roles, conflicting definitions or incompatible overrides stop only the
affected stage; report the problem and correction through setup, never substitute another
agent. Keep the saved model/effort binding unchanged in each invocation. Each review is
fresh and read-only; stage-specific brief and write bounds still apply.

## Saved planner assignments

Use [model-assignments.json](references/model-assignments.json) via the
[saved-assignment contract](references/model-assignments.md). It covers delegated decision application, TinySpec
source/tasks, Standard spec/tasks, both specification reviews, the direct/helper plan pass and overall
review/rereview. Pass the resolved binding unchanged in the invocation and bounded brief.
Parent brainstorming assessment, dialogue, inspection and approvals retain the owner-launched parent binding.
TinySpec final task review inherits `planner-parent` in a fresh reviewer session. The separate simplicity
review reuses the selected path's final-review binding in another fresh session; no new model assignment.
Gate assessment needs no delegated assignment resolution.
Verify the exact binding is permitted and callable at dispatch; configuration is not availability evidence.
A missing, malformed, unsupported, or unavailable binding stops only that operation with the resolver's
focused owner correction question: do not recommend, infer, substitute or silently default.
A correction retains its producing operation's saved assignment. Resume suitable originating context;
if its binding conflicts with a saved edit, ask for precise stage-specific resolution.
Inspect a failed expensive invocation and its call before targeted retry/resume/relaunch; inspect
failures before replacement and stop on unknown cause, never blind-retry.

## Proportionate validation

At specification and the separate final simplicity review, seek the simplest sufficient specification and delivery
approach that achieves the user's goals while preserving necessary safety and required acceptance.
Tooling, operations and verification are supporting means, not independent products. At simplicity review,
apply this to TinySpec source and tasks, or Standard specification, plan and tasks: challenge avoidable
architecture, operational subsystems, bookkeeping, task fragmentation and disproportionate checks.
Recommend removal or simplification of additions without a requirement, actual constraint or concrete
material risk as their basis; do not weaken required acceptance or silently change approved scope.

Apply [early risk reduction](references/early-risk-reduction.md); missing packaging stops with a
missing-install report. Select executable proof only for consequential uncertainty with inexpensive
leverage; known bounded behavior uses permanent actual-helper tests or an earlier verified step in
its delivery task; non-isolatable risks use real-system validation. Planning schedules proof, not
execution without separate authority; the shared risk owner defines proof applicability and lifetime.

During production and the simplicity review, challenge proposed task boundaries using the task-generation
outcome rule and [executor-sized outcome recipe](../task-generation/SKILL.md#executor-sized-outcomes).
Each task must deliver one bounded behavior or interface whose meaningful acceptance passes using
completed prerequisites and its own result, without unfinished downstream implementation. Reject
milestones that leave several independently testable interfaces unfinished together; assess
compaction/drift for the configured executor/effort, even when an advanced author could deliver
the whole milestone. Accept independently verifiable slices and ordinary established cross-system
wiring when its focused tests/docs establish the final observable.
A workflow or phase noun is not a reason to split: keep tests, evidence, review preparation and routine
teardown with the outcome unless an independent deliverable, prerequisite, gate, resource or context
boundary warrants separation. Reject duplicate proof/report chains and disproportionate checks.

At both TinySpec review and Standard overall review, return every material task-specific execution
risk or prerequisite: affected task, concrete runtime/interface/access or predecessor need,
observed evidence versus unknowns, and next investigation, mitigation, or necessary permission.
Carry this concise finding to coordinator preparation before affected worker reliance; it is not
a risk schema, score, admission checklist, or universal report. Name an unavailable
capability/access/paid/data/external operation and its corrective action; block only affected work,
leaving unrelated safe work available.

Choose checks from the actual changed seam and concrete failure: use the lowest validation layer
and smallest sufficient check, practical observables rather than a generic green suite. Carry the
rationale in existing acceptance fields, not a new task schema. Ordinary tasks need no manual ceremony;
source-required representative samples retain STOP and explicit user approval before downstream work.
For selection/query/wiring, show the selected result or argument reaches the intended consumer.
Do not automatically add exhaustive matrices, fault injection, new test infrastructure or broad suites.
When mocks cannot detect the failure, use the necessary integration layer. Genuine schema, security
or durability changes retain migration, authorization or persistence checks; small diffs alone never
justify weakening safety evidence.

When separate green components cannot establish a genuine risky boundary, use the smallest composed
check that observes the final observable, order or custody. Reuse an existing focused check that already
observes the boundary. Use a separate proof prerequisite only when the consequential unknown and costly
downstream reliance justify it; otherwise verify before reliance within the delivery task; block reliance
only on insufficient or invalidated evidence, not on unrelated seams.

Distinguish REQUIRED acceptance from optional hardening/regression. Optional checks are not acceptance
blockers. Separately gated live/provider/browser checks retain permissions; a gate is not a waiver for
REQUIRED checks. Never drop an owner-required check or approved safety criterion without explicit authority
and renewed affected approval. New concrete risk returns to scope/approval, not silent acceptance expansion.
Describe expected verification effort qualitatively; No universal deadlines. Remove unjustified setup,
not necessary criteria. Reuse valid unchanged evidence when scope, revisions and environment still apply.
Avoid repeated historical intake. Separate unrelated recovery/compatibility repairs into small causal
steps; require a prerequisite only with evidence it actually blocks the selected change. These rules
change neither the owner's selected planning depth nor mandated independent reviews or honest outcomes.

## Before selection: understand → brainstorm → assess → ask

Apply [Parsimony and Actionable Checks](references/parsimony.md). Fresh planning is read-only until
the owner selects depth: no source edits, decisions, specs, plans or tasks. Session history carries
request bounds, answers/rationale, evidence and deferrals; recover it or ask for missing answers.
Research may inform assessment, but no dependency docs, source, plan or decisions may be persisted.
Carry findings in session until selection.

Invoke `planning-brainstorming` in preselection mode directly in the parent session: assess the inspected
bounds against readiness target “informed scope assessment.” Do not delegate the gate or resolve a saved
`brainstorm-assessment` binding. With `NO_BRAINSTORM_NEEDED`, proceed directly to scope assessment and depth
choice without a child call. With `BRAINSTORM_NEEDED`, prepare the bounded agenda and conduct required owner
dialogue yourself, one material item at a time. A settled request skips extended dialogue, not parent assessment.
Use the saved `brainstorm-application` assignment only when delegating application of recorded decisions to
an authorized selected source. Generic brainstorming labels do not select depth or add an approval gate.

Present approximate scope: affected subsystems, localized/cross-cutting effects, architecture/contracts/
data, dependencies, migration, security/concurrency/deployment, verification, sequencing, uncertainty,
reversibility, likely work units and value of separate planning. Use qualitative reasoning, not line/task quotas.
Present BOTH options and recommend proportionately:
- **TinySpec → Tasks → Implement:** compact what/how source and separate tasks.
- **Standard: Specify → Plan → Tasks → Implement:** separate installed SpecKit stages.

Then call `ask_user` and STOP. Either choice is valid; denial/cancellation/ambiguity grants no authority.
Selection authorizes preparation only: writing and committing the selected path's bounded planning artifacts
and necessary factual evidence under the task-commit contract. Do not ask for separate planning-commit
authorization or defer these checkpoints until artifact approval. Artifact approvals govern content and
downstream progression. Pass this commit authority unchanged to planning delegates. Genuine Git, policy,
verification or ownership conflicts stop. Preserve selected depth on resume; resolved uncertainty alone
does not reroute. Material scope changes or explicit owner direction may reopen choice with rationale.

## Approval-driven continuation

Read the [approval/recovery contract](references/approval-and-recovery.md) before the first approval;
its executive-brief and current-content rules govern every approval/renewal. Present content-first
bullets in conversation BEFORE `ask_user`, including every actual ordered plan stage and task ID/outcome
when applicable, scope/exclusions, decisions, risks/gates, actual checks and exact content/next authority.
No total-count cap, catch-alls or invented TinySpec plan. Renewals use current artifacts.

After an affirmative choice/approval, persist its scope/current-content evidence and immediately start
the next authorized phase. Do not end the turn merely to report approval or ask “shall I continue?”
For async work, dispatch it before returning control and continue at completion. State in the brief/question
that final approval starts coordinator preflight unless explicitly requested planning-only or a separate-session
handoff. An older preparation-only approval never implies execution authority. Denied/ambiguous answers,
missing capabilities, new material gates and explicit stops still prevent continuation.

## Intended executor before decomposition

Before decomposition, resolve the current project's selected executor JSON path once with
`python3 scripts/resolve-workflow-executor.py --project PROJECT_ROOT` from the suite checkout
([resolver](../../scripts/resolve-workflow-executor.py)). Use `--executor PATH` only for an explicit
override; relative overrides are project-root-relative. Otherwise use only
`PROJECT_ROOT/.pi/workflow-executor.json`. Pass the exact absolute stdout path unchanged in both direct
TinySpec and Standard task-producer briefs and the coordinator handoff. Never search neighboring repos,
home, worktrees or historical tasks, fall back, create/copy configuration, authenticate or invoke a model
to resolve it. The producer itself must read the actual JSON before decomposing work; a
planner/parent/producer profile, remembered default or brief assertion is not a substitute.
If missing, ambiguous or unreadable, or worker model/effort is absent or invalid, stop the affected producer
and ask the owner to resolve that role, path and problem; never infer a replacement.

Apply the executor-sized outcome recipe using producer-read configuration and verified capability guidance,
not model-family hierarchy. Make interfaces/non-obvious choices explicit, record bounded scope and remaining
uncertainty; configuration alone does not establish granularity. Preserve REQUIRED acceptance and gates.
Settings stay in runtime configuration: no execution-intent, compatibility-assessment or provenance metadata.
Revise guidance only when actual changes affect it; do not regenerate historical tasks for ordinary coding.

## Selected production and stage handoffs

The following shared rules apply to EVERY stage in both paths; stage entries below supply only differences.
Persist selected source/provenance, evidence, decisions/deferrals and depth in existing project conventions.
Apply recorded decisions through the shared mechanism inside selected bounds only. No redundant brief/Epic.

Creation uses a separate fresh bounded-context producer for each artifact. Loading a skill in the parent
is not delegation: planner owns dialogue, coordination, inspection/review and its approval brief, never
fresh artifact authoring or substantive repair. Source/substantive correction stays with its producer;
the independent reviewer never becomes the producer. Delegate uncertain or substantive artifact corrections,
including task-level and upstream changes, to suitable originating context or a fresh bounded correction
delegate; Resume originating correction context when suitable. Direct mechanical repairs alone follow the
[bounded mechanical correction contract](references/approval-and-recovery.md#bounded-mechanical-corrections).
Missing, unusable or unauthorized delegation stops the affected stage; no inline/local fallback.
Do not forward full transcripts or unrelated history. Re-present unanswered questions before downstream work.

Default to direct asynchronous single-stage dispatch with the resolved saved assignment unchanged.
Inspect the returned artifact/checkpoint before the next authorized stage. Never prewire dependent source→tasks.
The two final reviews are independent parallel work: dispatch both against the same current artifact
snapshot before awaiting either report. Do not send findings between reviewers or start producer corrections
until both reports return. The parent combines its own pre-dispatch analysis with both review reports and resumes the appropriate
producer once for supported corrections, or launches a fresh bounded correction producer when the
originating context is unsuitable; resolve overlapping or contradictory findings against requirements.
A workflow needs concrete branching, parallel independent work or another earned orchestration need that
direct delegation cannot adequately serve; a single child, convenience wrapper or stage sequence alone is
insufficient. State the reason in the brief; retain parent inspection, stage authority, approvals and reviewer
independence. Earned workflows do not authorize parallel implementation batches.

The dedicated simplicity review uses only its bounded input contract below, not the production/risk
checklist in this section. For final correctness review, supply relevant facts and requirements without
forwarding simplicity-assessment instructions from production guidance.
Before every other direct or delegated TinySpec/Standard stage, provide one bounded brief containing:
- Exact saved assignment, stage authorization, allowed writes and prohibited operations.
- Bounded source, governing instructions/principles, settled/non-obvious constraints **verbatim**,
  each applicable accepted outcome constraint and source link, applicable memory and prior-stage handoff.
- Pending owner answers/flags/deferrals and required evidence. Require an updated handoff carrying those
  applicable accepted constraints and links; references do not replace constraints in a fresh delegate's brief.
- Canonical research links, local/version evidence, reuse/skip rationale, inspected supporting spans,
  capability/permission gaps and bounded canonical-owner/discovery writes; persist reusable guidance during
  authorized production before readiness. Supply the shared research contract before consequential source/plan
  decisions; carry evidence-backed constraints/checks, not invented dependency rules.
- Apply the shared early-risk and task-boundary contracts: selection/omission rationale, accessible proof/pass conditions,
  only genuinely necessary producer/consumer dependencies, proof lifetime and disproof/NOT VERIFIED blockers.
  Keep ordinary acceptance, evidence and teardown inside coherent delivery; do not prescribe a
  prototype/consumer/cleanup task chain.
- Carry stable task-local REQUIRED checks with pass criteria, evidence, original permission/manual gates and
  earlier dependencies. Carry item mappings unchanged into the whole task contract before coding for both
  adapters, including legacy producing review/renewal. Missing/weakened/unrun REQUIRED proof blocks reliance.

For source/task authority in both paths: TinySpec/specification is requirements truth; approved plan is derived
sequencing only. No SDD forwarding/rereading as direct requirements input downstream;
governing instructions/contracts, memory and permission/safety still apply.

In both TinySpec and Standard stage briefs, map guidance/accepted constraints through source
observables/acceptance → task dependencies, checkpoints, verification and coordinator handoff. Memory cannot
override source requirements or owner authority; confirm the mapping affects decisions, not just links.
Before approval, inspect shared research-link resolution (both direct/standalone consumers), canonical owner/
discovery, version/provenance, proportional reuse/targeted refresh, supporting spans → constraints → observable
checks, classified recommendations/derived decisions/assumptions and capability/permission gaps.
If required evidence is insufficient, stop affected design rather than default to model recollection. Obtain
explicit bounded owner deferral with impact, allowed bounds and outstanding validation; never automatically
defer or fabricate evidence. Research-driven content changes retain affected approval renewal.
Saved planner assignments are not implementation-task assignments and authorize no batching/runtime routing.

### Shared specification-review contract

Both paths require one fresh independent read-only specification review for fidelity to user intent,
after source creation and before downstream production. Use [the canonical review prompt](references/spec-review.md).
Give the reviewer the original user request, actual owner clarifications/decisions, relevant constraints/
accepted decisions/memory and exact current specification path/content identity with readable content.
Do not supply producer rationale, conclusions, or full unrelated transcripts.
Verify the saved exact binding is permitted and callable with async delegation, fresh context and read-only
profile. Dispatch with `async: true`, bind the report to the invocation and compare source content before
and after review. No writes, implementation, external action, or delegation. The reviewer returns ranked
findings or explicit zero; it neither edits nor approves.
Parent evaluates evidence/dispositions, including whether coverage, downstream clarity and simplicity
conclusions are supported rather than merely asserted. Inspect reported evidence limitations before
relying on zero findings; an unchanged hash is not proof of complete intake. Request targeted completion
of a material review gap through the existing reviewer context, not an automatic second review or new gate.
Parent resolves evident defects without unnecessary owner questions,
and returns corrections to the source producer under its saved producing assignment. Material decisions
go to the owner via one focused `ask_user` at a time. Parent inspects producer corrections against intent
and findings. Neither path may progress beyond specification review with unresolved material intent gaps.
A bounded owner deferral can exclude affected work but cannot release reliance on the gap. Keep findings
in existing session/report context, not a new tracker. No automatic rereview loop or additional approval gate.

### Shared final task-review contract

At the existing final review in both paths, the coordinator must follow this order:
1. Write both bounded reviewer handoff instructions: correctness and simplicity, using their respective
   input contracts and the same current artifact snapshot.
2. Before launching either reviewer, independently inspect that snapshot and explicitly answer in the
   session: **Does the current plan induce scope creep or over complexities?** State concrete findings
   and their basis, or justify why none were found. Do not defer this judgment to the reviewers.
3. Launch both fresh independent read-only reviewers with the prepared handoffs before awaiting either
   report. Keep the coordinator's analysis out of both handoffs to preserve reviewer independence.
4. After both reports return, assess all three analyses together: the coordinator's own analysis,
   correctness review and simplicity review. Route supported corrections in one bounded brief to the
   appropriate producer: resume its existing context when useful, otherwise launch a fresh correction
   subagent. Do not launch a fixer when there are no supported corrections.

Verify usable fresh read-only delegation and dispatch an independent reviewer in a new context
separate from both task producer and parent history for correctness; never fork
or resume either conversation. Use the route's resolved binding unchanged. Supply the original request,
actual owner decisions, authoritative requirements, final human and executable tasks, and necessary
verified risks and constraints. Do not supply producer conclusions, pass assurances or approval
trajectory; do not omit substantive facts. The reviewer returns supported findings or justified zero,
not approval. Parent evaluates the actual report alongside its pre-dispatch analysis and the simplicity report, routes substantive
corrections to producers and resolves material findings before approval. Missing delegation or review
evidence stops approval, not the other independent review.
This is the correctness review: assess correctness, completeness, feasibility and requirement alignment,
not whether an otherwise valid mechanism is the simplest option. Do not request a simplicity verdict or
forward parsimony/task-fragmentation assessment instructions. Preserve actual safety, permissions,
acceptance and independently executable task checks. Simplicity has its own fresh review below.

### Shared simplicity-review contract

In parallel with final correctness review, and before final owner approval, dispatch one fresh
read-only `coherence-reviewer` on the same artifact snapshot using [the simplicity prompt](references/simplicity-review.md).
Use the selected path's final-review model/effort binding unchanged. Verify the effective role prompt,
tools and fresh context through `subagent get`; use the stage-specific focus, not the correctness brief.
Normal runtime safety and inherited project instructions still apply; do not claim an empty system prompt.
Begin the brief with a concise executive bullet list describing the owner's intent: what the owner
wants, why, and the essential scope boundaries. Use as many bullets as needed to preserve that intent,
without a fixed count. Ground it only in the original request and actual owner clarifications, not the
proposed implementation. State the review goal: ensure the tasks achieve that intent in the simplest sufficient
way. The summary adds no requirements and does not replace the authoritative sources.
Alongside that summary, supply only the original request/authoritative requirements, actual owner
clarifications, current specification and human/executable tasks (plus Standard plan), applicable project
constraints, accepted decisions and relevant memory. Provide readable exact paths and relevant code access. Do not forward
producer rationale, prior verdicts, coordinator criticism, full transcripts or the broad review checklist.
Never fork or resume the parent, producer or correctness-review session for this first simplicity pass.

The reviewer returns supported findings or justified zero, not edits or approval. After both reports return,
parent checks all three analyses against original requirements, combines supported substantive corrections for the
appropriate producer under the sequence above, and explains rejected findings with evidence. Agent-added constraints remain challengeable even when labeled REQUIRED; genuine
requirements, safety and manual/permission gates remain binding. Resolve material findings before approval.
Before presenting approval, the parent summarizes the planned task specifications in one sentence and
explicitly answers: “Does the current plan induce scope creep or over complexities?” Assess the tasks
and both reports, not just their verdicts: a required outcome does not justify every proposed mechanism.
Check that simplicity comparisons use a genuinely sufficient smaller alternative, and distinguish supported
defects from optional improvements or flexibility already present. Resolve concrete review gaps through
targeted follow-up in the existing reviewer context, not another mandatory review stage.
If corrections invalidate correctness coverage, recheck only the affected changes and interactions through
the existing correction route. No automatic full-review loop, finding quota or additional owner gate.
Missing review capability/evidence stops this stage with the concrete corrective action.

### TinySpec path

1. **Source creation — saved assignment:** resolve `tinyspec-source`; delegate `tiny-spec` to a separate
   fresh bounded-context source producer and invoke `tiny-spec` with request, decisions, destination and
   preparation authority. Apply the shared stage rules, including research before consequential approach
   decisions and SDD quality guidance for specification creation only. Inspect source and blockers.
   No SpecKit prerequisite or standalone TinySpec approval before tasks; specification review is required.
2. **Specification review — independent saved reviewer assignment:** resolve `tinyspec-spec-review`;
   follow the shared specification-review contract with a fresh reviewer independent of the source producer.
   Inspect necessary producer corrections before task generation under the same saved assignment.
   Explicit zero findings proceeds directly to tasks, not a separate TinySpec approval.
   Unresolved material intent gaps stop task generation.
3. **Tasks — saved assignment:** resolve `tinyspec-tasks`; delegate a separate fresh bounded-context task
   producer and invoke `task-generation` direct adapter with TinySpec and relevant source links.
   Apply the shared stage rules and source/task authority. Create separate tasks; derive documentation
   work from inspected effects/requirements, not an absent plan. Keep coherent work consecutive without
   reordering dependencies or padding distant tasks.
4. **Review — fresh independent reviewer with planner-parent binding:** dispatch with stage 5 in parallel
   under the shared final task-review contract, inheriting `planner-parent` unchanged. Inspect source-to-task traceability, coverage, exclusions,
   decisions/deferrals, docs, integration/acceptance, verification item completeness, explicit/implicit
   dependencies and feasibility. Report contradictory or incomplete requirements and invalid instructions;
   each material finding needs the affected passage, impact and correction.
   Do not manufacture defects from stylistic preferences. Apply the shared stage rules for substantive
   corrections and the bounded mechanical correction contract for proven-equivalent repairs. Record fixes,
   validation and current content evidence. Check [authorization-neutral tasks](../task-generation/SKILL.md#authorization-neutral-tasks):
   temporary phase/approval status belongs in the approval record, not executable instructions. Review risk selection/omission, actual evidence and gates,
   necessary producer/consumer dependencies, reuse/retention, production acceptance and task boundaries.
   Check independently executable outcomes and the shared execution-risk requirements above.
   Source carries needs; tasks carry independently necessary outcomes. Apply the dependency evidence/permission
   review above before combined approval.
5. **Simplicity review:** dispatch alongside stage 4 using the shared simplicity-review contract on the
   same source and tasks. Wait for both reports before producer corrections; resolve supported findings
   before combined approval.
6. **Combined approval:** present a brief bullet-list executive summary BEFORE `ask_user`; approve current
   source, tasks and implementation scope under the continuation contract, then immediately proceed to handoff.
   Denial returns to review/correction, not execution.

### Standard path

Use observed installed SpecKit stage commands/instructions/templates; report AVAILABLE/UNAVAILABLE with
evidence. Required absent capability stops that stage; never install, simulate slash commands or substitute
ordinary Markdown. Missing/template-only constitution principles need owner-derived answers through the
observed constitution capability; verify repaired output. Missing repair capability, principles or failed
verification stops. Do not reopen valid principles.

1. **`spec_create` — saved assignment:** resolve `standard-spec-create`; delegate a separate fresh bounded-context
   specification producer using observed specification instructions and SDD reference for specification creation only.
   Apply the shared stage rules, including research before consequential dependency constraints and complete
   relevant behavior, approach, constraints and observable acceptance. Clarify only when requested or required;
   mechanical gaps are resolved by the delegate, material choices go to the owner. Finish after that ordinary
   clarification and parent inspection of the exact current specification: do not approve or plan here.
2. **`spec_review` — independent saved reviewer assignment:** resolve
   `standard-spec-review`; follow the shared specification-review contract above with a fresh independent reviewer.
   Verify the exact saved provider/model:effort is actually permitted and callable using the installed async
   delegation interface, fresh context and read-only tool/profile, plus source-producer and `ask_user` capabilities.
   Package/profile names alone are insufficient; failure stops only this review: do not substitute, route to
   another reviewer, or fall back. Dispatch exactly that saved binding unchanged with `async: true` and bind its
   report to the runtime invocation. Apply the shared reviewer inputs, no-write and source-comparison rules.

   Parent reports the total findings and meaningful areas, presents the five most important findings initially
   (all if fewer), and offers to show all findings or a grouped overview. Retain the complete returned findings
   in existing context, not a new persistent tracker. Five is a presentation batch, not a discovery or resolution
   limit; no discovery cap. Resolve fidelity defects through the source producer, not owner questions.
   For each unresolved material decision, parent asks one concrete `ask_user` question at
   a time with scenario, alternatives, and consequences; discard queued questions resolved by earlier answers.
   An unanswered or cancelled material answer stops affected planning with no inferred default.
   Send actual answers to the originating `standard-spec-create` producer under the same producing assignment.
   The producer updates relevant requirements/scenarios/acceptance and existing `Q: … → A: …` convention,
   removes contradictions, validates and checkpoints; parent
   inspects the returned change. Do not rerun ordinary clarification taxonomy or automatically rereview.
   Continue to surface the next highest-impact remaining findings; do not stop merely because five were answered.
   Before planning, every remaining material decision must be answered or explicitly deferred by the owner with
   consequences and permitted planning bounds recorded. Preserve unresolved impact; never release a material
   dependency automatically. Reviewer and parent never substantively repair the specification.

   With explicit zero findings, skip question interaction. After zero or inspected correction, present the existing
   current-specification executive brief and `ask_user` approval gate. Durably record that approval before `plan_create`,
   then immediately continue to `plan_create` without a second continuation or review approval.
3. **`plan_create` — saved assignment:** resolve `standard-plan-direct` or `standard-plan-helper` for the entire
   direct/helper pass. Delegate a separate fresh bounded-context plan producer. In one same-session pass,
   review/fix the specification, create one plan through the observed capability, then review/fix the produced plan.
   Apply the shared stage rules and source/task authority. Cover architecture/contracts, integration, migration/
   rollback, risks, docs, verification and coherent sequencing. Do not reorder dependencies or pad distant tasks.
   Before consequential plan decisions, complete required shared-contract research. For helper invocation or the
   direct Standard pass, give canonical research-document and necessary discovery-link destinations, observed
   allowed changes and prohibited operations, with explicit bounded permission in addition to detected SpecKit
   artifacts. Do not grant arbitrary documentation edits or code writes; missing required evidence/authority stops.
   When the approved adapter is needed, invoke `delegating-architectural-planning` for this entire pass; inspect
   its return, do not create the plan again. Only when no adapter is invoked delegate the whole pass directly.
   Never perform it in the parent. Approved specification changes require renewed specification approval with a
   new executive brief before leaving this stage; after renewal resume immediately. Material choices remain gates.
4. **`tasks_create` — saved assignment:** resolve `standard-tasks-create`; delegate a separate fresh bounded-context
   task producer using observed SpecKit tasks and `task-generation`. Apply the shared stage rules and source/task
   authority, with authorization to prepare tasks: final implementation approval is not a prerequisite to creation.
   This is create-only: producers may draft, revise, shorten and mechanically validate their unsubmitted work
   without supervisor permission. This is not independent review or authority to change approved requirements.
   After submission, defects follow `overall_review`; independent review and final approval remain required.
   Include docs, acceptance, shared context and producer checks without breaking dependencies or story boundaries.
5. **`overall_review` — independent saved reviewer assignment:** dispatch with stage 6 in parallel.
   Resolve `standard-overall-review` (or
   `standard-overall-rereview` for a fresh rereview); follow the shared final task-review contract and observed analysis capability and inspect source → spec → plan
   → tasks traceability, principles, exclusions, coverage, dependencies, verification item completeness, docs,
   integration and approvals. Report contradictory or incomplete requirements and invalid instructions
   across artifacts with affected passage, impact and correction. Do not silently expand acceptance. Review risk selection/omission, actual evidence and gates,
   necessary producer/consumer dependencies, reuse/retention, production acceptance and task boundaries in direct
   Standard and managed/helper plans. Check independently executable outcomes and the shared execution-risk
   requirements above.
   Check [authorization-neutral tasks](../task-generation/SKILL.md#authorization-neutral-tasks):
   temporary phase/approval status belongs in the approval record. Apply the dependency evidence/permission
   review above, including direct Standard pass and helper-managed/standalone contract coverage.
   Apply the shared stage rules for corrections and the bounded mechanical correction contract for equivalent
   repairs. The independent reviewer does not become the producer. Renew affected approvals for material upstream
   changes: renew affected approvals and preserve pending questions and correction contexts. Resolve mechanics internally; never apply unresolved
   material defaults. Missing independent reviewer/review evidence stops approval. Join both review reports
   before producer corrections, not directly to approval.
6. **`simplicity_review`:** dispatch alongside stage 5 using the shared simplicity-review contract on the
   same specification, plan and tasks. Wait for both reports before producer corrections; resolve supported
   findings before overall approval.
7. **Overall approval:** present a bullet-list executive brief
   BEFORE `ask_user`, including plan-phase implications; obtain current overall approval for source, spec, plan,
   tasks and implementation scope, then immediately proceed to handoff under the continuation contract.

## Approval, resume and legacy recovery

On interruption, drift or legacy input, read the approval/recovery contract's transition/invalidation and
legacy checkpoint mapping. Preserve original provenance, artifact shapes, task-embedded sources and valid
approvals; no forced TinySpec, invented historical choice or retired manager. Verify current content/revision
evidence, not an `approved` label or handoff assertion; return to the earliest invalid gate. Ambiguous origin
stops. Inadequate REQUIRED contracts return to the producing review/approval gate for renewed affected approval,
not fabricated historical requirements. Reconcile active/unknown children before replacement.

## Handoff, not execution

Check current source/task consistency, ordering, reviews/approvals and unresolved gates. Revalidate risk rationale
against current applicability: consumers use applicable evidence and permanent production tests; retain proof
through all consumers/validation. Failed/unrun proof cannot release reliance; routine cleanup does not become
a separate task. Supply in existing conventions, without a new state/handoff file:
- Producer `planner`, selected depth (or mapped legacy origin) and source provenance.
- Source, tasks, supporting artifacts (Standard spec/plan) and approved current content/revision evidence.
- Reviews/checks, applicable accepted outcome constraints and source links, decisions/deferrals and blockers.
  Include material task-specific execution-risk or prerequisite findings with affected task, evidence
  versus unknowns, and next investigation/mitigation/necessary permission before worker reliance.
- Combined TinySpec or both Standard approvals and Explicit approved implementation scope/authorization.

After final approval, automatically invoke `coordinate-implementation` in the same session under the
continuation contract; if explicitly requested planning-only or separate-session handoff, return the approved
handoff instead. Do not stop at a readiness summary by default. A capability/gate failure returns the precise
blocker and preserved handoff. The executable runner alone executes approved tasks, verifies REQUIRED checks/
gates and creates focused commits; planner never executes tasks or selects implementation models/batches.
Planning-only readiness is not implementation completion or feature acceptance.

## Maintaining this contract

Run `python3 scripts/check-planner-workflow.py` and `python3 scripts/test-planner-workflow.py` from the suite
checkout; unavailable Python means report UNAVAILABLE and inspect manually. These are static/fixture checks,
not model-obedience proof; see the repository's planner regression guide. In Paseo, changed global skills need
a fresh-session handoff, not automatic reload/restart or asking the owner to run `/reload`.

## Mandatory task checkpoint

Apply the shared [task-commit contract](../memory-handling/references/task-commit-contract.md) to authorized
retained artifacts/repairs. Preserve read-only preselection and approval gates; checkpoint before handoff.
