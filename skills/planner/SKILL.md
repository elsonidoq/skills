---
name: planner
description: Use when a structured requirement needs scope assessment, reviewed planning artifacts, or recovery of an existing planning handoff before implementation.
---

# Planner

Prepare work, never implement it. One entry point owns understanding, proportional
brainstorming, scope assessment, the owner's TinySpec/Standard choice, review,
approvals, and the handoff to `coordinate-implementation`. Depth is the owner's
choice, not an admission threshold or a model-family choice.

## Job first; no coordinator bookkeeping

Resolve the request and advance toward an approved, executable handoff. Produce only
substantive planning artifacts and required approval inputs; no coordinator bookkeeping.
Do not maintain administrative ledgers, progress records, evidence manifests or repeated
readiness reports. Runtime-owned operational state stays runtime-owned. This applies to
TinySpec, Standard and recovery; it does not remove schema-required task fields.

Once required prerequisites are satisfied, advance the next authorized stage.
Reopen only affected work on concrete invalidating evidence such as changed scope/content,
stale approval, failed proof or capability/ownership drift. Reuse applicable settled evidence
and decisions; refresh only invalidated portions. State each required fact once in its
authoritative artifact or existing approval/session return and reference it elsewhere.
No repeated record polishing, duplicate evidence, unchanged rechecks or status-only writes.
Carry this rule into every stage brief; do not add trackers or ceremonies to enforce it.

Never waive required approvals, safety checks, permissions, reviews or commits.
A genuine unmet gate stops only the affected stage: report the exact blocker and smallest
required resolution, not an administrative cleanup programme.

## Discovery and capability boundary

Read repository instructions, the request or explicitly selected source/section,
linked evidence, governing principles, existing planning artifacts, and workspace
changes. Preserve unrelated work. Resolve ambiguous source selection through
`ask_user`; never attach a likely source. Discover artifact conventions and ask for
missing destinations only after depth selection. Do not assume paths or a state schema.

In suite-adopting projects, verify discoverable `memory-handling` and read the whole
project memory index, then trigger-matching entries. Missing required memory stops;
do not substitute a global store. Read the distributed
[SDD reference](../../docs/best_practices_spec_driven_development.md) for specification creation only, including TinySpec, and
[approval/recovery contract](references/approval-and-recovery.md) and
[dependency research contract](references/dependency-research.md). A missing required
reference stops with a missing-install report. Verify discoverable
`planning-brainstorming`, `tiny-spec`, `task-generation`, and `coordinate-implementation`
before the stage that needs each; do not duplicate an unavailable skill.
Use the SDD quality guidance to prepare source-producer briefs, not downstream requirements
inputs. The source must retain complete relevant behavior, approach, constraints and observable
acceptance; unresolved material gaps return through existing gates.

Use [Memory Handling](../memory-handling/SKILL.md) during initial understanding,
including standalone/direct entry: retrieve relevant guidance from the verified unified index
without auto-initialization; missing optional storage or STATE is nonblocking. Carry relevant
explicit owner guidance, alongside gotchas, through source observables → dependencies or
gates → task-local REQUIRED checks → worker/reviewer briefs; no default history intake,
execution-time feedback routing, routine persistence, reflection, inferred lessons, or STATE
maintenance. Preserve its explicit-feedback authority and path/symlink, sensitive-data, and
dirty/concurrent safeguards. Apply [save-adr](../save-adr/SKILL.md)'s consult/propagate contract before affected planning; read the
whole discovered decision index, then relevant accepted records in full and needed
supersession links; fresh/resumed contexts re-establish applicability rather than claiming a
prior read. Carry each applicable accepted outcome constraint and source link through source
observables → dependencies/REQUIRED checks → brief; proposed/superseded records are not
current policy, and contradictory accepted authority or uncertain applicability stops only the
affected continuation for an owner decision. Verify its effect on a relevant decision, never
override source/owner authority. No default history intake; explicit relevant retrieval is
index-first where useful and retains uncertainty on no match. Required gotcha-memory gates
remain separate.

Verify callable question capability before owner gates. Resolve planner-stage bindings from the
[owner planning assignments](references/model-assignments.md); parent dialogue, inspection,
TinySpec parent task review, and approvals retain the owner-launched parent model and effort.
The suite runtime requirements are in the global configuration repository's `REQUIREMENTS.md`;
configuration names alone are not availability evidence. `ask_user` unavailable or failing at a
route or artifact-approval gate reports `question: UNAVAILABLE` and stops. No inferred answer
or prose approval substitutes for those tool gates. Verify async delegation and its observed
budgets before delegating, and inspect failures before retry/resume/relaunch. Never silently
change a saved assignment or install missing capabilities.
Standard-only SpecKit/constitution checks happen after Standard is selected,
not as prerequisites for considering TinySpec.

Treat source claims as claims. Verify load-bearing positive and negative claims at
their source layer, especially “already satisfied” and “no task needed.” Cite symbols,
paths/lines and relevant verbatim evidence; retain verified results, rather than
rediscovering settled facts. Mark unchecked claims `UNVERIFIED`. Resolve those affecting
scope, acceptance, dependencies, or decisions empirically when possible, otherwise
obtain an explicit owner deferral before readiness. Do not invent a beneficiary.
Record exclusions and separately scheduled mechanical work so tasks cannot duplicate it.

Before declaring a technical blocker, identify the exact affected operation and verify its
actual enforced limit at the consuming interface. Do not generalize a tool-operation limit
into an artifact, project or workflow limit. For example, a worker's file-read bound does not
establish the task-contract loader's bound; inspect that loader before blocking task intake.
Keep owner-requested behavior, verified runtime restrictions and agent-selected design choices
explicitly distinct in existing artifacts/briefs. An agent inference is not an owner requirement;
interpret owner agreement within the explanation and scope actually presented, not as a
broader policy. Correct a mistaken premise and its affected derived constraints before reliance.

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

## Saved planner assignments

`references/model-assignments.json` is the owner-editable source for fresh planner work.
Resolve its exact model and effort for brainstorming assessment/application, TinySpec source/tasks,
Standard spec/tasks, both independent specification reviews, the whole direct/helper plan pass, and fresh overall review/rereview.
Pass the resolved binding unchanged in the invocation and bounded brief; parent-only dialogue,
inspection, TinySpec parent task review and approvals inherit the owner-launched parent binding in both
dimensions. Verify the saved binding is permitted and callable for only the affected role at
dispatch. A missing, malformed, unsupported, or unavailable exact assignment stops that role
with the resolver's focused owner correction question: do not recommend, infer, substitute, or
silently use a default.

A correction retains its producing operation's saved assignment. Resume a suitable retained
producer context when possible; otherwise launch a fresh correction with that same assignment.
If the saved assignment changed and conflicts with retained producer context, ask the owner for
a precise stage-specific resolution before correction. Inspect a failed expensive invocation and
its call before any targeted retry or resume; never blind-retry or relaunch it.

## Proportionate validation

Read and apply [early risk reduction](references/early-risk-reduction.md); verify it is
readable or stop with a missing-install report. Select proof for a consequential unknown
only when inexpensive, executable evidence can reduce costly reliance; known bounded behavior
uses permanent actual-helper tests or a verified step inside its delivery task. Easy names/types
use inspection, and non-isolatable risks use real-system validation with actual gates. Planning
schedules proofs, not execution without separate authority; the shared risk owner defines proof
applicability and lifetime.

At both TinySpec and Standard reviews, challenge proposed task boundaries using the shared
task-generation outcome rule and
[executor-sized outcome recipe](../task-generation/SKILL.md#executor-sized-outcomes): reject
milestones disguised as tasks and assess compaction/drift for the configured executor/effort,
even when an advanced author could deliver the whole milestone.
A workflow or phase noun is not a reason to split; keep tests, evidence, review preparation
and routine teardown with the supported delivery unless a concrete independent outcome,
prerequisite, gate, resource or context boundary warrants separation.
Reject duplicate proof/report chains and disproportionate checks without weakening acceptance.

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

When separate green components cannot establish a genuine risky boundary, require the
smallest composed check that observes the final observable, order or custody—not just
helper outputs. Reuse an existing focused check that already observes the boundary;
ordinary observed wiring needs no extra integration programme. Preserve necessary security
and durability checks. Use a separate proof prerequisite only when the consequential unknown
and costly downstream reliance justify it; otherwise put a verified step before reliance in
the same coherent task. Preserve real dependency order and block reliance only on insufficient
or invalidated evidence, not on unrelated seams.

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

Apply [Parsimony and Actionable Checks](references/parsimony.md). Apply during understanding and scope assessment.

Fresh planning is read-only until the owner selects depth: no source edits, decision
files, TinySpec, specification, plan, or tasks. Session history carries request bounds,
evidence, answers/rationale, and deferrals. If interrupted, recover those records;
if unavailable, ask for missing answers, never invent a durable preselection artifact.
Dependency inspection/research may inform assessment read-only; no dependency docs,
source, plan or decisions may be persisted. Carry findings in session until selection.

Invoke `planning-brainstorming` in preselection mode with `brainstorm-assessment` for its
assessment and `brainstorm-application` when applying recorded decisions; resolve and pass each
saved assignment unchanged in the fresh call and brief, with the inspected request/bounds and
readiness target “informed scope assessment.” Preserve its exact gate result;
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

## Intended executor before decomposition

Before task decomposition, resolve the current project's selected executor JSON path once with
`python3 scripts/resolve-workflow-executor.py --project PROJECT_ROOT` from the suite checkout
(the script is [here](../../scripts/resolve-workflow-executor.py)). Supply `--executor PATH` only
for an explicit override; relative overrides are project-root-relative. Otherwise the resolver uses
only `PROJECT_ROOT/.pi/workflow-executor.json`. Pass its exact absolute stdout path unchanged
in both direct TinySpec and Standard task-producer briefs and the coordinator handoff. Never search
neighboring repositories, home directories, other worktrees or historical task files; never fall
back after an override fails. Resolution reads/validates existing configuration without creating
or copying it, authenticating providers, invoking models or substituting selections. The producer itself
must read the actual JSON before decomposing work; a planner/parent/producer profile, remembered
default or brief assertion is not a substitute. A valid selected JSON supplies the worker model
and effort for bounded implementation guidance, without a redundant executor-selection question.

If the selected path is missing, ambiguous or unreadable, or its worker model/effort is absent
or invalid, stop only the affected producer and ask the owner to resolve that role, path and
problem. Do not recommend or infer a replacement. Executor settings remain in actual runtime
configuration: task handoffs follow the shared `task-generation` six-check contract, not
mandatory execution-intent, compatibility-assessment or provenance metadata.

Apply task-generation's executor-sized outcome recipe using the producer-read configuration and
verified capability guidance, not a model-family hierarchy or a substitute model. Make
interfaces and non-obvious decisions explicit where the executor needs them; configuration
alone does not establish granularity. Record bounded scope, choices left open and uncertainty.
REQUIRED acceptance, dependencies, safety and approval gates never shrink.

Preserve the selected executor and effort without silent substitution. Revise guidance when
a real change affects the work, but do not require model assessments, approval/source receipts
or regeneration of historical tasks to execute ordinary requested coding.

## Selected production and stage handoffs

Apply the shared early-risk and task-boundary contracts in stage briefs and source/task
handoffs. Return the selection/omission rationale, executable criteria and applicability,
only genuinely necessary producer/consumer dependencies, proof lifetime and disproof/NOT
VERIFIED blockers with affected approval renewal. Keep ordinary acceptance, evidence and
teardown inside coherent delivery; do not prescribe a prototype/consumer/cleanup task chain.

After choice, persist the selected source/provenance, evidence, decisions/deferrals,
and depth using established project conventions. Preserve the original request by
reference when durable; capture necessary context when it exists only in the session.
Apply recorded decisions through the shared mechanism inside selected bounds only.
Do not create a redundant brief/Epic between request and selected planning source.

Creation always uses a separate fresh bounded-context producer for each artifact. Loading
a skill in the parent is not delegation. Planner owns dialogue, coordination, inspection,
review and its own approval brief, never fresh artifact authoring or substantive repair. Direct mechanical repair is limited
to the [bounded mechanical correction contract](references/approval-and-recovery.md#bounded-mechanical-corrections). Do not forward full
transcripts or unrelated history. Missing, unusable or unauthorized delegation stops the
affected production/correction stage with the exact gap; no inline/local fallback.

Default to direct asynchronous single-stage dispatch with the resolved saved assignment unchanged.
Inspect the returned artifact/checkpoint and resolve substantive blockers before the next
authorized stage. Never prewire dependent source→tasks stages without parent inspection.
A workflow needs concrete branching, parallel independent work or another earned orchestration
need that direct delegation cannot adequately serve; a single child, convenience wrapper or
stage sequence alone is insufficient. State a terse reason in the existing brief. Earned
workflows preserve parent inspection, stage authority, approvals and reviewer independence;
they do not authorize parallel implementation batches.

Before every direct or delegated TinySpec/Standard stage, resolve the stage's saved assignment
and supply it unchanged in the bounded brief and call with the bounded source, settled and
non-obvious constraints **verbatim**, each applicable accepted outcome constraint
and source link, cited authorities, governing instructions/principles, applicable memory,
prior-stage handoff, stage authorization, allowed writes, pending owner flags/answers/deferrals,
and required evidence. Each stage reads the brief and returns an updated handoff carrying those
applicable accepted constraints and links. Source references reduce artifact duplication; they
do not replace necessary constraints in a fresh delegate's brief. Do not delegate owner dialogue.
Resume originating correction context when supported and suitable; otherwise use a
fresh bounded correction delegate with a durable correction handoff. Delegate uncertain or substantive artifact
corrections, including task-level and upstream changes; never edit those in the parent.
For proven-equivalent mechanical repairs use the bounded mechanical correction contract above. Inspect returned artifacts/checkpoints; ownership or verification conflicts stop.
Re-present unanswered questions before downstream work.

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
these constraints reach tasks through the shared adapter, not just a memory summary. Check that
approved applicable guidance changes a relevant decision (or explain existing coverage), not merely a link.
Memory cannot override source requirements or owner authority. Preselection stays read-only;
no routine coordination persistence, default history intake or raw-outcome promotion.

Pass source constraints, canonical research links, applicable guidelines and stable task-local REQUIRED
verification needs through both adapters to task generation and coordinator. Each item retains
its pass criterion, smallest sufficient check, expected evidence and manual/permission gates;
include accessible proof/pass conditions, explicit earlier producer dependencies and original
permission/manual gates in the inline REQUIRED brief for both adapters. Missing, weakened or
unrun REQUIRED proof blocks downstream reliance. Optional checks stay distinct. Preserve item mappings unchanged into the whole task contract before
coding, including both adapters and legacy producing review/renewal when contracts are inadequate.
Saved planner assignments govern only planning-stage bindings; they are not implementation-task
assignments and grant no implementation batching or runtime routing authority.
Missing or ambiguous contracts, including old approved tasks, return to the producing review/approval
gate for affected review and renewed approval, never fabricated historical requirements.

### Shared specification-review contract

Both paths require one fresh independent read-only specification review, primarily for
fidelity to user intent, after source creation and before downstream production. Use
[the canonical review prompt](references/spec-review.md). Give the reviewer the original
user request, actual owner clarifications/decisions, relevant constraints/accepted decisions/
memory, and the exact current specification path/content identity with readable content.
Do not supply producer rationale, conclusions, or full unrelated transcripts. Verify the
saved exact binding is permitted and callable with async delegation, fresh context and a
read-only reviewer profile; missing capability or binding stops only this operation for
owner correction, never substitution. Dispatch the resolved binding unchanged in brief and
call with `async: true`, bind its report to the invocation, and compare source content before
and after review. The reviewer returns ranked findings or explicit zero findings; it neither
edits nor approves. Parent evaluates evidence and dispositions, not reviewer approval.

Resolve straightforward fidelity defects without unnecessary owner questions; send substantive
corrections to the source producer under its saved producing assignment, resuming suitable
context or using a fresh bounded correction delegate. Material decisions go to the owner via
one focused `ask_user` question at a time. Parent inspects producer corrections against the
request, actual answers and findings. Neither path may progress beyond specification review
with unresolved material intent gaps. An explicit bounded owner deferral can exclude affected
work from progression but cannot release reliance on an unresolved gap. Keep findings and
dispositions in existing session/report context, not a new tracker. No automatic rereview loop
or additional approval gate; actual invalidating drift follows existing recovery rules.

### TinySpec path

1. **Source creation — saved assignment:** resolve `tinyspec-source` and delegate `tiny-spec` to a separate fresh
   bounded-context source producer; invoke `tiny-spec` with verified request,
   decisions, source bounds, observed destination, and preparation authorization.
   Supply the shared research contract, findings/capability evidence and bounded
   canonical-owner/discovery writes before consequential approach decisions; inspect
   returned research traceability and persistence with the source.
   Supply SDD quality guidance for specification creation only. Require complete relevant
   behavior, approach, constraints and observable acceptance in the source; unresolved
   material gaps return through existing gates. Missing, unusable or unauthorized source
   delegation stops; no parent creation/substantive correction or inline/local fallback.
   Inspect returned compact source and blockers. No SpecKit prerequisite or standalone
   TinySpec approval is required before task production; independent specification review is.
2. **Specification review — independent saved reviewer assignment:** resolve `tinyspec-spec-review`
   and follow the shared specification-review contract above with the compact TinySpec as the
   exact specification. Use a fresh reviewer independent of the `tinyspec-source` producer.
   Evaluate all findings and inspect necessary producer corrections before task generation.
   Return substantive corrections to `tinyspec-source` with its same saved assignment.
   Explicit zero findings skips question interaction; resolved findings proceed directly to
   tasks, not a separate TinySpec approval. Unresolved material intent gaps stop task generation.
3. **Tasks — saved assignment:** resolve `tinyspec-tasks` and delegate a separate fresh bounded-context task
   producer; invoke `task-generation` direct adapter with TinySpec and
   applicable source links. TinySpec is requirements truth; no SDD forwarding/rereading as
   direct requirements input. Governing instructions/contracts, memory and permission/safety
   still apply. Missing, unusable or unauthorized task delegation stops; no parent task
   creation/substantive correction or inline/local fallback. Create separate tasks using its full contract. Derive docs
   from inspected effects/requirement, not an absent plan. Keep context-coherent work
   consecutive without reordering dependencies or padding distant tasks.
4. **Review — planner-owned parent binding:** review source-to-task traceability, in-scope coverage,
   exclusions, constraints, decisions/deferrals, documentation, integration/acceptance,
   verification item completeness, explicit and implicit dependencies, and stage feasibility.
   Explicitly check the TinySpec and tasks, within and across artifacts, for confusing, ambiguous
   or contradictory instructions, scope creep, and unnecessary complexity/overengineering.
   Report material defects with the affected passage, concrete impact and smallest sufficient
   correction or simpler alternative; requirements coverage alone does not establish clarity
   or proportionality. Challenge additions without a requirement, actual constraint or concrete
   material risk as their basis; preserve necessary safety protections and required acceptance.
   Do not manufacture findings or treat stylistic preferences as defects. Record
   fixes, validation results and current content evidence. Apply the [bounded mechanical correction contract](references/approval-and-recovery.md#bounded-mechanical-corrections)
   to proven-equivalent mechanical repairs. Delegate uncertain or substantive source/task corrections
   to suitable originating context or a fresh bounded correction delegate; no parent substantive
   task-level or upstream repair. Missing, unusable or unauthorized correction delegation stops; no
   inline/local fallback. No additional independent task-planning reviewer is required for
   this path; the preceding independent specification review and implementation's independent
   review remain required.
   Apply the dependency evidence/permission review above before combined approval.
   Check [authorization-neutral tasks](../task-generation/SKILL.md#authorization-neutral-tasks):
   temporary phase/approval status belongs in the approval record, not executable task instructions.
   Review risk selection/omission, actual evidence and gates, necessary producer/consumer
   dependencies, reuse/retention, production acceptance, disproof/renewal and task boundaries.
   Source carries needs; separate tasks carry only independently necessary work units.
5. **Combined approval:** present a brief bullet-list executive summary BEFORE `ask_user`;
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
valid settled principles. Verify the saved exact stage binding and independent reviewer availability before assigning their work.

1. **`spec_create` — saved assignment:** resolve `standard-spec-create` and delegate a separate fresh bounded-context
   specification producer to follow observed specification instructions and
   SDD reference for specification creation only using request/provenance and shared gate result.
   Require complete relevant behavior, approach, constraints and observable acceptance in the
   specification; unresolved material gaps return through existing gates. Missing, unusable or
   unauthorized specification delegation stops; no parent creation/substantive correction or inline/local
   fallback. Supply research
   triggers/context and apply the shared research contract before consequential dependency constraints
   are chosen; carry evidence-backed constraints/checks, not invented dependency rules.
   Reflect settled
   decisions. Clarify only when requested or required by the detected workflow;
   mechanical gaps are resolved by the delegate, material choices go to the owner. Finish
   after that ordinary clarification and parent inspection of the exact current specification:
   do not approve or plan here.
2. **`spec_review` — independent saved reviewer assignment:** resolve
   `standard-spec-review`, apply the shared specification-review contract above (this is
   Standard's existing review, not an additional review), and verify the exact saved provider/model:effort is actually
   permitted and callable, with the installed async delegation interface, a fresh context,
   the reviewer’s read-only tool/profile, and source-producer and `ask_user` capabilities.
   Package/profile names alone are insufficient. A missing, unsupported, or unavailable
   exact binding stops only this review with the resolver’s focused owner correction; do
   not substitute, route to another reviewer, or fall back.

   Dispatch exactly that saved binding unchanged, with `async: true`, and bind its report
   to the runtime invocation. Give the fresh independent reviewer only the original user
   request, actual owner clarifications/decisions, exact
   current specification path/content identity, relevant context/constraints/accepted
   decisions/memory, and [the canonical review prompt](references/spec-review.md). Do not
   include producer rationale, transcript, or unrelated history or producer conclusions. Review definition of
   done for observable completion aligned with user intent, using existing acceptance
   criteria rather than requiring a new heading; include all material gaps in the same
   ranked findings and existing question/correction flow, with no discovery cap.
   Require findings only;
   no writes, implementation, external action, or delegation. Parent compares the exact
   specification before and after review and inspects the returned report; reviewer and
   parent never substantively repair the specification.

   Parent reports the total findings and meaningful areas, then surfaces the five most
   important findings initially (or all if fewer). Offer to show all findings or a grouped
   overview on request; these views summarize findings, not additional approval gates.
   Retain the complete returned findings in existing session/report context, not a new
   persistent tracker. Five is a presentation batch, not a discovery or resolution limit.
   Resolve evident fidelity defects through the shared producer-correction route, not owner
   questions. For each unresolved material decision, parent asks one concrete `ask_user` question at
   a time, retaining its scenario, alternatives, and consequences; discard queued
   questions made unnecessary by earlier answers. An unanswered or cancelled material
   answer stops affected planning with no inferred default. Send actual answers to the
   originating `standard-spec-create` producer: resume a suitable context or dispatch a
   fresh bounded correction with that same producing assignment. The producer updates
   relevant requirements/scenarios/acceptance, including definition-of-done completion
   conditions affected by the answers, and existing Clarifications/session
   `Q: … → A: …` convention, removes contradictions, validates and checkpoints; parent
   inspects the returned change. Do not rerun ordinary clarification taxonomy for answered
   questions or automatically rereview. After each presentation batch, surface the next
   highest-impact remaining findings; do not stop merely because five were answered.
   Before planning, every remaining material decision must be answered or explicitly
   deferred by the owner with consequences and permitted planning bounds recorded.
   Explicit owner stops/deferrals use existing gates with the unresolved impact; they
   never release a material dependency automatically.

   With explicit zero findings, skip question interaction. After zero or inspected producer
   incorporation, present the existing current-specification executive brief and `ask_user`
   approval gate. Durably record that approval before `plan_create`, then immediately
   continue to `plan_create` without a second continuation or review approval.
3. **`plan_create` — saved assignment:** resolve `standard-plan-direct` for a direct pass or
   `standard-plan-helper` for the helper pass. Use that resolved exact binding unchanged for the
   entire direct/helper pass and its brief/dispatch. An unavailable or unsupported saved binding
   stops only this stage with its focused owner correction question; no substitution, default, or
   helper fallback may bypass it.
   Delegate a separate fresh bounded-context plan producer. The specification is requirements
   truth; approved plan is derived sequencing only. No SDD forwarding/rereading as direct
   requirements input; governing instructions/contracts, memory and permission/safety still
   apply. Missing, unusable or unauthorized plan delegation stops; no parent production/substantive repair
   or inline/local fallback. From current approved specification, in one
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
   it as the planner Standard adapter for this entire pass. Inspect its returned
   evidence; do not create the plan again. Only when no adapter is invoked delegate
   the entire pass to the separate fresh bounded-context producer with the resolved saved
   assignment. Never perform it in the parent. Saved-assignment capability stops and approval
   renewal supersede helper standalone fallbacks.
   Any approved specification content change requires renewed specification approval
   with a new executive brief in short bullets before leaving this stage. After renewal,
   continue the affected stage immediately. Material choices remain gates.
4. **`tasks_create` — saved assignment:** resolve `standard-tasks-create` and delegate a separate fresh bounded-context
   task producer to follow observed SpecKit tasks capability under
   `task-generation`. Specification is requirements truth; approved plan is derived sequencing
   only. No SDD forwarding/rereading as direct requirements input; governing instructions/
   contracts, memory and permission/safety still apply. Missing, unusable or unauthorized task
   delegation stops; no parent task creation/substantive correction or inline/local fallback. Supply authorization to prepare tasks and already-applicable
   approvals; final implementation approval is not a prerequisite to creation.
   This stage is create-only: producers may draft, revise, shorten and mechanically
   validate their own unsubmitted output within authorized scope, without supervisor
   permission for ordinary editing. This is not independent review or permission to change
   approved upstream requirements. After submission, defects belong to `overall_review`
   and its correction route; independent review and final approval remain required.
   Include documentation, acceptance, shared context and producer checks without breaking
   prerequisite order or story acceptance boundaries.
5. **`overall_review` — independent saved reviewer assignment:** resolve
   `standard-overall-review` (or `standard-overall-rereview` for a fresh rereview), then follow observed analysis
   capability; inspect source → spec → plan → tasks traceability, principles, exclusions,
   coverage, dependencies, verification item completeness, documentation, integration and approvals.
   Explicitly check source, specification, plan and tasks, within and across artifacts, for
   confusing, ambiguous or contradictory instructions, scope creep, and unnecessary
   complexity/overengineering. Report material defects with the affected passage, concrete impact
   and smallest sufficient correction or simpler alternative; requirements coverage alone does
   not establish clarity or proportionality. Challenge additions without a requirement, actual
   constraint or concrete material risk as their basis; preserve necessary safety protections
   and required acceptance. Do not manufacture findings or treat stylistic preferences as defects.
   Review risk selection/omission, actual evidence and gates, necessary producer/consumer
   dependencies, reuse/retention, production acceptance, disproof/renewal and task boundaries
   in direct Standard and managed/helper plans.
   Check [authorization-neutral tasks](../task-generation/SKILL.md#authorization-neutral-tasks):
   temporary phase/approval status belongs in the approval record, not executable task instructions.
   Apply the dependency evidence/permission review above, including the direct Standard
   pass and helper-managed/standalone contract coverage, before overall approval.
   Apply the [bounded mechanical correction contract](references/approval-and-recovery.md#bounded-mechanical-corrections)
   to proven-equivalent mechanical repairs. Delegate uncertain or substantive task-level and
   upstream corrections to suitable originating producer
   context or a fresh bounded correction delegate; record evidence. The independent reviewer
   does not become the producer. No parent substantive artifact edits. Missing, unusable or unauthorized
   correction delegation stops; no inline/local fallback. Flag only material
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

Revalidate risk rationale and any required proof against current applicability: consumers
use applicable evidence and preserve behavior with permanent production tests; retain proof
through all consumers/validation before safely discarding disposable material. Failed/unrun
proof cannot release assumed reliance; routine cleanup does not become a separate task.

Revalidate paths, source/task consistency, ordering, current review/approval evidence,
required upstream outputs, and unresolved material gates. Provide explicit locations
and applicable approved content/revisions for:

- Producer `planner`, selected depth `TinySpec` or `Standard` (or original legacy origin
  plus mapped planner recovery checkpoint).
- Authoritative source, tasks, and supporting artifacts; Standard spec and plan.
- Review and validation evidence, applicable accepted outcome constraints and source links,
  decisions/deferrals and pending blockers.
- TinySpec combined approval or Standard specification and overall approvals.
- Explicit approved implementation scope/authorization and source provenance.

Use established artifact/decision conventions; no mandatory new state/handoff file.
After final approval, supply this complete handoff and automatically invoke `coordinate-implementation`
in the same session, unless the owner explicitly requested planning-only or a separate-session
handoff. Do not stop at a readiness summary or require a second execution request. Planner
never executes tasks itself; the executable runner alone selects dependency-ready work and
compatible role-safe sessions from approved exact configuration, verifies REQUIRED evidence
and gates, and creates focused task checkpoints. The interface cannot choose models/batches. If a capability/gate blocks continuation, report the precise blocker
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
