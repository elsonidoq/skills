---
name: planner
description: Use when a structured requirement needs scope assessment, reviewed planning artifacts, or recovery of an existing planning handoff before implementation.
---

# Planner

Prepare work, never implement it. One entry point owns understanding, proportional
brainstorming, scope assessment, the owner's TinySpec/Standard choice, review,
approvals, and the handoff to `coordinate-implementation`. Depth is the owner's
choice, not an admission threshold or a model-class choice.

## Discovery and capability boundary

Read repository instructions, the request or explicitly selected source/section,
linked evidence, governing principles, existing planning artifacts, and workspace
changes. Preserve unrelated work. Resolve ambiguous source selection through
`ask_user`; never attach a likely source. Discover artifact conventions and ask for
missing destinations only after depth selection. Do not assume paths or a state schema.

In suite-adopting projects, verify discoverable `memory-handling` and read the whole
project memory index, then trigger-matching entries. Missing required memory stops;
do not substitute a global store. Read the distributed
[SDD reference](../../docs/best_practices_spec_driven_development.md) and
[approval/recovery contract](references/approval-and-recovery.md). A missing required
reference stops with a missing-install report. Verify discoverable
`planning-brainstorming`, `tiny-spec`, `task-generation`, and `coordinate-implementation`
before the stage that needs each; do not duplicate an unavailable skill.

Verify callable question capability before owner gates, and permitted usable
owner-selected class bindings before assigning work. The suite runtime requirements
are in the global configuration repository's `REQUIREMENTS.md`; configuration names
alone are not availability evidence. `ask_user` unavailable or failing at a route or
artifact-approval gate reports `question: UNAVAILABLE` and stops. No inferred answer
or prose approval substitutes for those tool gates. Verify async delegation and its
observed budgets before delegating, and inspect failures before retry/resume/relaunch.
Never silently change selected models, weaken classes, or install missing capabilities.
Standard-only SpecKit/reviewer/constitution checks happen after Standard is selected,
not as prerequisites for considering TinySpec.

Treat source claims as claims. Verify load-bearing positive and negative claims at
their source layer, especially “already satisfied” and “no task needed.” Cite symbols,
paths/lines and relevant verbatim evidence; retain verified results, rather than
rediscovering settled facts. Mark unchecked claims `UNVERIFIED`. Resolve those affecting
scope, acceptance, dependencies, or decisions empirically when possible, otherwise
obtain an explicit owner deferral before readiness. Do not invent a beneficiary.
Record exclusions and separately scheduled mechanical work so tasks cannot duplicate it.

Inspect affected implementations, tests, interfaces, data, integrations, and relevant
history only as needed to assess load-bearing uncertainty. Stop expanding discovery
when the scope signals are sufficiently supported; identify remaining uncertainty,
not false precision. Material product, architecture, privacy, permissions, cost,
irreversible, or settled-requirement changes are owner decisions. Resolve mechanical
facts without unnecessary dialogue or speculative material defaults.

## Before selection: understand → brainstorm → assess → ask

Fresh planning is read-only until the owner selects depth: no source edits, decision
files, TinySpec, specification, plan, or tasks. Session history carries request bounds,
evidence, answers/rationale, and deferrals. If interrupted, recover those records;
if unavailable, ask for missing answers, never invent a durable preselection artifact.

Invoke `planning-brainstorming` in preselection mode with the inspected request/bounds
and readiness target “informed scope assessment.” Preserve its exact gate result;
conduct required owner dialogue yourself, one material item at a time. A settled
request skips extended dialogue, not assessment. Generic `brainstorming` design-depth
labels do not select TinySpec/Standard or add an artifact approval before selection.

Present a concise approximate scope assessment: affected subsystems, localized versus
cross-cutting impact, architecture/contracts/data changes, dependencies, migration
and compatibility, security/concurrency/deployment concerns, tests, sequencing,
uncertainty/reversibility, likely work units, and value of a separate planning stage.
Use qualitative reasoning and coordination cost, not lines of code or a task quota.
Present BOTH options, even against your recommendation:

- **TinySpec → Tasks → Implement:** compact what/how source, separate compatible tasks.
- **Standard: Specify → Plan → Tasks → Implement:** separate SpecKit reasoning stages.

Explain why one appears proportionate, then call `ask_user` and STOP until the owner
explicitly selects TinySpec or Standard. Either choice is valid regardless of scope
recommendation. Denial/cancellation/ambiguous selection grants no production authority.
Selection authorizes planning preparation only, never implementation. Preserve the
selected depth on resume; resolved uncertainty alone does not reroute. Substantive
scope change or explicit owner direction may reopen choice, with recorded rationale.

## Approval-driven continuation

After `ask_user` returns an affirmative choice/approval, persist its scope and current
content evidence, then immediately start the next authorized phase in the same session.
Do not end the turn merely to report approval, promise the next phase, provide a prompt
for the user to run, or ask “shall I continue?” For an asynchronous phase, dispatch it
before returning control and continue at its completion notification; a routine async
wait is not an owner approval gate.

Depth choice starts selected source production. Standard specification approval starts
planning; approval renewal resumes the affected stage. TinySpec combined approval and
Standard final approval start the coordinator's implementation preflight by default.
If the owner explicitly requested planning-only or a separate-session handoff, honor
that boundary and return the approved handoff instead. State the actual next phase and
this boundary in the pre-approval bullet brief and question so approval never implies
broader authority than presented. Never reinterpret an older preparation-only approval
as execution permission. Denied/cancelled/ambiguous answers, missing capabilities,
new material owner gates and explicit stop boundaries still prevent unsafe continuation.

## Selected production and stage handoffs

After choice, persist the selected source/provenance, evidence, decisions/deferrals,
and depth using established project conventions. Preserve the original request by
reference when durable; capture necessary context when it exists only in the session.
Apply recorded decisions through the shared mechanism inside selected bounds only.
Do not create a redundant brief/Epic between request and selected planning source.

Before every delegated stage supply the bounded source, settled and non-obvious
constraints **verbatim**, cited authorities, governing instructions/principles,
applicable memory, prior-stage handoff, stage authorization, allowed writes, pending
owner flags/answers/deferrals, and required evidence. Each stage reads the brief and
returns updated handoff. Source references reduce artifact duplication; they do not
replace necessary constraints in a fresh delegate's brief. Do not delegate owner dialogue.
Resume originating correction context when supported and suitable; otherwise pass a
durable correction handoff. Re-present unanswered questions before downstream work.

### TinySpec path

1. **Source creation — `sonnet-class`:** invoke `tiny-spec` with verified request,
   decisions, source bounds, observed destination, and preparation authorization.
   Inspect returned compact source and blockers. No SpecKit prerequisite or standalone
   TinySpec approval is required before task production.
2. **Tasks — `sonnet-class`:** invoke `task-generation` direct adapter with TinySpec and
   applicable source links. Create separate tasks using its full contract. Derive docs
   from inspected effects/requirement, not an absent plan. Keep context-coherent work
   consecutive without reordering dependencies or padding distant tasks.
3. **Review — planner-owned:** review source-to-task traceability, in-scope coverage,
   exclusions, constraints, decisions/deferrals, documentation, integration/acceptance,
   class share, explicit and implicit dependencies, and stage feasibility. Record
   fixes, validation results and current content evidence. No independent planning
   reviewer is required for this path; implementation's independent review is unchanged.
4. **Combined approval:** present a brief bullet-list executive summary BEFORE `ask_user`;
   obtain explicit approval of current TinySpec/source, tasks, and implementation scope,
   stating that approval starts the coordinator next unless planning-only was requested.
   Persist that answer against current content, then immediately proceed to handoff and
   coordinator preflight under the continuation rule. Denial returns to review/correction,
   not execution.

### Standard path

Use the project's observed SpecKit stage commands, instructions, templates and
prerequisite checks; report `AVAILABLE`/`UNAVAILABLE` with evidence. Required absent
capability stops at the affected stage; never install, simulate slash commands in a
shell, or substitute generic Markdown. Verify detected constitution when required:
missing/template-only principles require owner-derived answers and the observed
constitution capability, then verify repaired output before specification work.
Missing repair capability, principles, or failed verification stops. Do not reopen
valid settled principles. Verify permitted usable owner-selected stage bindings and
an independent reviewer before assigning their work.

1. **`spec_create` — `sonnet-class`:** follow observed specification instructions and
   SDD reference using request/provenance and shared gate result. Reflect settled
   decisions. Clarify only when requested or required by the detected workflow;
   mechanical gaps are resolved directly, material choices go to the owner. Inspect
   specification, then provide a bullet-list executive brief including clarification
   results BEFORE
   `ask_user`. Durably record current specification approval before `plan_create`, then
   immediately continue to `plan_create` without another continuation question.
2. **`plan_create` — `opus-class`:** from current approved specification, in one
   same-session pass review/fix the specification, create one plan through the observed
   capability, then review/fix the produced plan. Cover contracts, architecture,
   integration, sequencing, migration/rollback, risks, docs, verification, and coherent
   consecutive same-class work. Do not reorder dependencies or pad distant tasks.
   When approved work calls for `delegating-architectural-planning`, verify and invoke
   it as the planner Standard adapter for this ENTIRE pass. Inspect its returned
   evidence; do not create the plan again. Only when no adapter is invoked perform
   the pass directly through the selected permitted binding. Manager-governed fixed
   class, capability stops and approval renewal supersede helper standalone fallbacks.
   Any approved specification content change requires renewed specification approval
   with a new executive brief in short bullets before leaving this stage. After renewal,
   continue the affected stage immediately. Material choices remain gates.
3. **`tasks_create` — `sonnet-class`:** follow observed SpecKit tasks capability under
   `task-generation`. Supply authorization to prepare tasks and already-applicable
   approvals; final implementation approval is not a prerequisite to creation.
   This stage is create-only: no producer self-review/correction. Defects belong to
   `overall_review`. Include documentation, acceptance, shared context and producer
   checks without breaking prerequisite order or story acceptance boundaries.
4. **`overall_review` — independent owner-selected reviewer:** follow observed analysis
   capability; inspect source → spec → plan → tasks traceability, principles, exclusions,
   coverage, dependencies, class share, documentation, integration and approvals.
   Fix mechanical task-level issues and record evidence. Flag only material
   friction/complexity or genuine specification deviation with alternatives and a
   recommendation; never apply unresolved material defaults. Task ordering, grouping,
   file choice, batch size, naming and single-option mechanics are internally resolved,
   not routine owner questions. Material upstream changes return to the affected gate
   and renew affected approvals. Preserve pending questions and correction contexts.
   Missing independent reviewer/review evidence stops. Present a bullet-list executive
   brief including review outcome and plan-phase implications BEFORE `ask_user`; obtain
   current overall approval for source, spec, plan, tasks and implementation scope,
   explicitly stating the next phase. After approval, immediately proceed to handoff
   and coordinator preflight under the continuation rule.

## Approval, resume and legacy recovery

Follow the linked approval/recovery contract, including denial, cancellation,
external evidence, changes, renewed approvals and earliest-invalid-stage recovery.
Fresh sessions must inspect approved current content/revision evidence; an `approved`
label, chat-only answer or handoff assertion is insufficient for implementation.

For old-manager work, use the legacy checkpoint mapping in that contract. Preserve
original artifact shapes and provenance, including source embedded in old tasks and
existing specification approvals. No forced new TinySpec, Epic creation, reclassification,
or fabricated historical depth choice. Other documented origins keep their own gates;
ambiguous origin stops. Never invoke a retired manager to repair its handoff.

## Handoff, not execution

Revalidate paths, source/task consistency, ordering, current review/approval evidence,
required upstream outputs, and unresolved material gates. Provide explicit locations
and applicable approved content/revisions for:

- Producer `planner`, selected depth `TinySpec` or `Standard` (or original legacy origin
  plus mapped planner recovery checkpoint).
- Authoritative source, tasks, and supporting artifacts; Standard spec and plan.
- Review and validation evidence, decisions/deferrals and pending blockers.
- TinySpec combined approval or Standard specification and overall approvals.
- Explicit approved implementation scope/authorization and source provenance.

Use established artifact/decision conventions; no mandatory new state/handoff file.
After final approval, supply this complete handoff and automatically invoke `coordinate-implementation`
in the same session, unless the owner explicitly requested planning-only or a separate-session
handoff. Do not stop at a readiness summary or require a second execution request. Planner
never executes tasks itself; Coordinator alone selects models/strategy/batches and verifies
its execution preflight. If a capability/gate blocks continuation, report the precise blocker
and preserve the handoff rather than silently stopping. For an explicitly bounded planning-only
request report readiness, not implementation completion or feature acceptance.

## Maintaining this contract

With Python 3 available run `python3 scripts/check-planner-workflow.py` and
`python3 scripts/test-planner-workflow.py` from the global configuration repository.
These are static/fixture checks, not model-obedience proof. If unavailable, report
scripted checks `UNAVAILABLE` and inspect manually. Behavioral tests and limitations
are documented in the repository's planner regression guide.
