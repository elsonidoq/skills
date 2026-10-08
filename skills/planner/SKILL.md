---
name: planner
description: Use when a structured requirement needs scope assessment, reviewed planning artifacts, or recovery of an existing planning handoff before implementation.
---

# Planner

Prepare work, never implement it. One entry point owns understanding, proportional
brainstorming, scope assessment, the owner's TinySpec/Standard choice, review,
approvals, and the handoff to `coordinate-implementation`. Depth is the owner's
choice, not an admission threshold or a model-family choice.

## Job first; bookkeeping is subordinate

The job is to resolve the request and advance planning toward an approved, executable
handoff—not to perfect administrative records. Bookkeeping must always remain a small fraction of total effort.
Spend the bulk of effort on understanding, consequential decisions, source/task production
and substantive review. This applies to TinySpec, Standard and recovery.

Once required prerequisites are satisfied, advance the next authorized stage.
Preparation has an end: reopen only affected work on concrete invalidating evidence
such as changed scope/content, stale approval, failed proof or capability/ownership drift.
Do not substitute repeated record polishing, duplicate evidence, unchanged rechecks,
status-only updates or generic history searches for stage progress.
Reuse applicable settled evidence and decisions after checking they still apply;
refresh only invalidated portions. Keep required records terse: record each fact once
in its authoritative owner and link it elsewhere; coalesce updates within existing
checkpoint boundaries and skip unchanged writes. Carry this rule into every stage brief.

If administration starts dominating, stop optional bookkeeping, shorten remaining
records to required facts and return to substantive stage work. Do not add time trackers,
quota reports or another ceremony to enforce this rule. Efficiency is not a waiver:
never waive required approvals, safety checks, permissions, reviews or commits.
A genuine unmet gate stops the affected stage: report the exact blocker and smallest required resolution,
not an open-ended administrative cleanup programme.

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
[approval/recovery contract](references/approval-and-recovery.md) and
[dependency research contract](references/dependency-research.md). A missing required
reference stops with a missing-install report. Verify discoverable
`planning-brainstorming`, `tiny-spec`, `task-generation`, and `coordinate-implementation`
before the stage that needs each; do not duplicate an unavailable skill.

Apply the shared [project coordination contract](../memory-handling/references/project-coordination.md)
during initial understanding: ensure the mandatory project-local store exists and read
`GUIDELINES.md` before brainstorming, scope assessment and depth choice. Automatically
initialize missing files, notify the user and commit only initialization files before
proceeding, without a setup approval gate. Reuse the declared project-local root or default
`<project-root>/memory/coordination/`; preserve existing files and unrelated staged changes.
Empty guidelines mean no invented project knowledge, not a nonpersistent execution path.
Creation/commit failures stop with the exact blocker; required gotcha-memory stops remain
separate. Report applicable guidance, exact constraints and evidence references without
changing owner choice or source authority. Ordinary planning does not read the evidence
index/history. Justified clarification uses index-first relevant-only retrieval; no match
retains uncertainty.

Verify callable question capability before owner gates, and permitted usable
owner-selected exact profiles before assigning work. Apply the shared routing selection
below to planning/advisory work; verify the Standard exception at its affected stage. The suite runtime requirements
are in the global configuration repository's `REQUIREMENTS.md`; configuration names
alone are not availability evidence. `ask_user` unavailable or failing at a route or
artifact-approval gate reports `question: UNAVAILABLE` and stops. No inferred answer
or prose approval substitutes for those tool gates. Verify async delegation and its
observed budgets before delegating, and inspect failures before retry/resume/relaunch.
Never silently change selected profiles or install missing capabilities.
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

Apply the shared dependency research contract during discovery: inspect repository
guidance and dependency/version evidence first; detect consequential research needs,
proportional reuse/skip and targeted refresh before design. Verify permitted usable
research capabilities only when needed; configuration names are not usability proof.

## Shared routing selection

Use the [qualified seed rubric](../coordinate-implementation/references/batch-routing.md)
for each planning/advisory invocation, including brainstorming assessment/application,
TinySpec source/tasks/review, and Standard specification/tasks/independent review.
Assess all six applicable factors, especially the weakest verification blind spot.
Record separate Family rationale and Effort rationale, proposed versus owner-selected
exact binding plus supported effort, applicable approved guidance or none, and inspected-failure
repair conditions. Verify permissions, tools, callable binding and supported effort at
assignment and dispatch. Copy one exact selected profile unchanged into the direct call or
helper brief/dispatch; settings or agent defaults overriding selection stop dispatch.
Missing owner selection or support stops the affected invocation; never silently substitute.
Record selected versus observed separately; unknown actual model or effort stays unknown.
Implementation-only batching, task-count and REQUIRED-item rules are not planning prerequisites.

The sole fixed planning exception is Standard `plan_create`: the owner requires Sol/medium
for the complete direct/helper pass described below, not a family hierarchy or benchmark claim.
Resolve the concrete binding from permitted usable runtime options, never a provider/version
hard-coded here. This exception does not assign implementation-task profiles.

## Proportionate validation

Read and apply [early risk reduction](references/early-risk-reduction.md); verify it is
readable or stop with a missing-install report. Select a difficult isolatable core by
leverage, not ceremony; easy names/types use inspection, non-isolatable risks use
real-system validation. Planning schedules executable proofs, not execution without
separate authority. Carry minimal real-runtime proof, explicit production consumption,
production tests before cleanup and retained disproof into selected work.

During assessment and selected production/review, identify the actual changed seam
and its concrete failure before choosing checks. Choose the lowest validation layer
that can detect that failure; use the smallest sufficient check, not the broadest
available suite. Carry this rationale into source/task acceptance and the handoff
using existing artifact fields, not a new task schema. Prefer practical observables tied to the
criterion over a generic green suite. Ordinary tasks need no invented manual ceremony; source-
required representative samples retain STOP and explicit user approval before full/downstream work.

For a small selection/query or wiring change, prefer a focused check showing the
selected result or argument reaches the intended consumer. Do not automatically add
exhaustive matrices, fault injection, new test infrastructure or broad suites.
If mocks cannot detect the concrete failure (for example, real query semantics),
use the necessary integration layer instead. Genuine schema, security or durability
changes retain the checks needed to detect migration, authorization or persistence
failures; small diffs alone never justify weakening safety evidence.

Separate REQUIRED acceptance checks (from source criteria, owner direction or
repository policy) from optional hardening and broader regression. Identify separately
gated live/provider/engine/browser checks and their permissions/capabilities; a gate
is not a waiver when the check is REQUIRED. Optional checks are not acceptance blockers;
new evidence of a concrete risk returns to the affected scope/approval gate rather
than silently expanding acceptance. Never drop an owner-required check or approved
safety criterion without explicit authority and renewed affected approval.

Describe expected verification effort qualitatively: a focused existing check and
bounded setup for a local seam, or justified additional setup/checks for affected
contracts and risks. No universal deadlines. Compare this effort with the actual
change before approval; remove unjustified expansion, not necessary criteria.
Reuse valid unchanged evidence after checking its scope, revisions and environment
still apply; refresh only invalidated evidence. Avoid repeated historical intake:
carry settled evidence and decisions forward while preserving current approval checks.
Separate unrelated recovery wiring or legacy compatibility repairs into small causal
steps with their own outcomes/checks; include a prerequisite only with evidence that
it actually blocks the selected change. Preserve dependency order and scope authority.

Apply this boundary at both path reviews and in delegated briefs. It changes neither
the owner's selected planning depth nor approval provenance, explicit permissions,
mandated independent reviews or honest PASS/FAIL/NOT RUN reporting.

## Before selection: understand → brainstorm → assess → ask

Fresh planning is read-only until the owner selects depth, except the shared contract's
bounded coordination-store initialization/commit and factual evidence/index/reflection
persistence, including blocked runs before depth selection: no source edits, decision
files, TinySpec, specification, plan, or tasks. Session history carries request bounds,
evidence, answers/rationale, and deferrals. If interrupted, recover those records;
if unavailable, ask for missing answers, never invent a durable preselection artifact.
Dependency inspection/research may inform assessment read-only; no dependency docs,
source, plan or decisions may be persisted. Carry findings in session until selection.

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
Selection authorizes planning preparation only, never implementation. This includes
writing and committing the selected path's bounded planning artifacts and required
factual evidence under the shared task-commit contract. Do not ask for separate
planning-commit authorization or defer these checkpoints until artifact approval.
Artifact approvals govern content and downstream progression, not permission to
commit already-authorized preparation. Pass this commit authority unchanged to
planning delegates. Genuine Git, policy, verification or ownership conflicts stop
with the exact blocker; they do not create a routine commit-permission gate.
Preserve the selected depth on resume; resolved uncertainty alone does not reroute. Substantive
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

Apply the early risk reduction contract in stage briefs and source/task handoffs:
return justified selection/omission, executable criteria and applicability, explicit
producer → consumer → production validation → cleanup dependencies, retention through
all consumers, and disproof/NOT VERIFIED blockers with affected approval renewal.

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

Carry dependency research triggers, local/version findings, reuse/skip rationale,
inspected supporting spans, capability evidence and gaps into selected production.
Verify bounded canonical technical-owner and necessary discovery-link write scope;
persist reusable guidance during authorized production before readiness, preserving
unrelated content. No fixed project paths or arbitrary documentation permission.
Before existing approvals/readiness, review actual shared-link resolution (including
both direct/standalone consumers), canonical owner/discovery, version/provenance,
proportional reuse/targeted refresh, supporting spans → constraints → observable checks,
classified recommendations/derived decisions/assumptions, and capability/permission gaps.
Required insufficient research returns the exact gap, affected decisions and needed
evidence; stop affected design rather than default to model recollection or readiness.
Obtain the owner's explicit bounded deferral through existing gates with impact, allowed bounds
and outstanding validation; never automatically defer or fabricate evidence.

Carry exact applicable coordination guideline constraints and evidence references into
both TinySpec and Standard stage briefs: source observables/acceptance, producer/consumer
boundaries, task dependencies, checkpoints, verification and coordinator handoff. Verify
these constraints reach tasks through the shared adapter, not just a memory summary.
Memory cannot override source requirements or owner authority. Preselection stays read-only
except bounded coordination-store initialization/commit and factual evidence/index/reflection
persistence for all runs, including blocked preselection;
no default history intake or raw-outcome promotion. Optional `residual_reasoning` notes
(low/medium/high with rationale) may inform later owner-selected batch routing;
absence requires no migration and changes no approval rule.

Pass source constraints, canonical research links, applicable guidelines and stable task-local REQUIRED
verification needs through both adapters to task generation and coordinator. Each item retains
its pass criterion, smallest sufficient check, expected evidence and manual/permission gates;
optional checks stay distinct. Preserve item mappings unchanged into the whole batch union before
coding, including both adapters and legacy producing review/renewal when contracts are inadequate.
The [qualified seed rubric](../coordinate-implementation/references/batch-routing.md)
also informs planning selection under Shared routing selection; planning-stage bindings are
not implementation-task assignments. Its implementation batching rules remain coordinator-only.
Missing or ambiguous contracts, including old approved tasks, return to the producing review/approval
gate for affected review and renewed approval, never fabricated historical requirements.

### TinySpec path

1. **Source creation — shared routing selection:** invoke `tiny-spec` with verified request,
   decisions, source bounds, observed destination, and preparation authorization.
   Supply the shared research contract, findings/capability evidence and bounded
   canonical-owner/discovery writes before consequential approach decisions; inspect
   returned research traceability and persistence with the source.
   Inspect returned compact source and blockers. No SpecKit prerequisite or standalone
   TinySpec approval is required before task production.
2. **Tasks — shared routing selection:** invoke `task-generation` direct adapter with TinySpec and
   applicable source links. Create separate tasks using its full contract. Derive docs
   from inspected effects/requirement, not an absent plan. Keep context-coherent work
   consecutive without reordering dependencies or padding distant tasks.
3. **Review — planner-owned, shared routing selection:** review source-to-task traceability, in-scope coverage,
   exclusions, constraints, decisions/deferrals, documentation, integration/acceptance,
   verification item completeness, explicit and implicit dependencies, and stage feasibility. Record
   fixes, validation results and current content evidence. No independent planning
   reviewer is required for this path; implementation's independent review is unchanged.
   Apply the dependency evidence/permission review above before combined approval.
   Review early risk reduction selection/omission, real-runtime executable criteria,
   explicit consumption/dependencies, all-consumer retention, production tests before
   cleanup, disproof/renewal and feasibility; source carries needs, separate tasks carry work.
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

1. **`spec_create` — shared routing selection:** follow observed specification instructions and
   SDD reference using request/provenance and shared gate result. Supply research
   triggers/context and apply the shared research contract before consequential dependency constraints
   are chosen; carry evidence-backed constraints/checks, not invented dependency rules.
   Reflect settled
   decisions. Clarify only when requested or required by the detected workflow;
   mechanical gaps are resolved directly, material choices go to the owner. Inspect
   specification, then provide a bullet-list executive brief including clarification
   results BEFORE
   `ask_user`. Durably record current specification approval before `plan_create`, then
   immediately continue to `plan_create` without another continuation question.
2. **`plan_create` — Sol/medium:** select the Sol family with exactly **medium** supported effort
   for the ENTIRE direct/helper pass. Verify a permitted callable Sol binding and medium support
   at assignment and dispatch; record the exact selected profile and propagate it unchanged
   through the direct call or helper brief/dispatch. Unavailable Sol/medium stops with the precise
   binding/support gap; no substitution, settings/default override or standalone helper fallback
   may bypass this rule. Record observed binding/effort separately; unknown stays unknown.
   From current approved specification, in one
   same-session pass review/fix the specification, create one plan through the observed
   capability, then review/fix the produced plan. Cover contracts, architecture,
   integration, sequencing, migration/rollback, risks, docs, verification, and coherent
   consecutive context-coherent work. Do not reorder dependencies or pad distant tasks.
   Before consequential plan decisions, complete required shared-contract research and
   durable guidance. For helper invocation or the direct Standard pass, the brief must
   identify canonical research-document and necessary discovery-link destinations,
   observed allowed changes and prohibited operations, with explicit bounded permission
   in addition to detected SpecKit artifacts. Do not grant arbitrary documentation edits
   or code writes; missing required evidence/authority stops the affected branch.
   When approved work calls for `delegating-architectural-planning`, verify and invoke
   it as the planner Standard adapter for this ENTIRE pass. Inspect its returned
   evidence; do not create the plan again. Only when no adapter is invoked perform
   the pass directly through the selected permitted Sol/medium profile. Manager-governed
   Sol/medium, capability stops and approval renewal supersede helper standalone fallbacks.
   Any approved specification content change requires renewed specification approval
   with a new executive brief in short bullets before leaving this stage. After renewal,
   continue the affected stage immediately. Material choices remain gates.
3. **`tasks_create` — shared routing selection:** follow observed SpecKit tasks capability under
   `task-generation`. Supply authorization to prepare tasks and already-applicable
   approvals; final implementation approval is not a prerequisite to creation.
   This stage is create-only: no producer self-review/correction. Defects belong to
   `overall_review`. Include documentation, acceptance, shared context and producer
   checks without breaking prerequisite order or story acceptance boundaries.
4. **`overall_review` — independent owner-selected reviewer:** use shared routing selection;
   follow observed analysis
   capability; inspect source → spec → plan → tasks traceability, principles, exclusions,
   coverage, dependencies, verification item completeness, documentation, integration and approvals.
   Review early risk reduction selection/omission, real-runtime executable criteria,
   explicit consumption/dependencies, all-consumer retention, production tests before
   cleanup, disproof/renewal and feasibility in direct Standard and managed/helper plans.
   Apply the dependency evidence/permission review above, including the direct Standard
   pass and helper-managed/standalone contract coverage, before overall approval.
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

Revalidate the early risk reduction mapping and blockers against current proof applicability:
explicit consumers must inspect/run the reference and preserve behavior with production tests;
cleanup waits for all consumers. Failed/unrun proofs cannot release assumed dependents.

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

## Mandatory task checkpoint

Apply the shared [task-commit contract](../memory-handling/references/task-commit-contract.md). Retained TinySpec/Standard source and task artifacts are bounded deliverables; preserve preselection read-only and approval gates, then checkpoint authorized retained output before handoff.
