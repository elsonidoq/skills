# TinySpec: Task verification contracts for batch-level model assignment

## Context and authority

**VERIFICATION PER TASK; EXECUTION PER COHERENT BATCH.** Owners and coordinators need
less expensive successful execution without losing independently observable task acceptance.
Make verification strength actionable in routing, preserve contracts through batching, and
repair diagnosed gaps rather than buying generic review or restarting valid work.

Producer: planner-selected TinySpec source, 2026-10-07. The conversation-only request and
settled scope are captured here for fresh task producers. The owner explicitly selected
TinySpec after approving scope; this authorizes **preparation only**, not approval of this
artifact, tasks, routing or implementation. An earlier “I approve” before depth choice
creates no additional execution authority. No tasks are generated here. Planner retains
source/task review and current-content combined approval; coordinator retains execution
preflight, routing approval, assignment and independent final review.

Preparation profile: owner-selected exact `openai-codex/gpt-6.1-sol:medium`, unchanged.
Planner supplied successful assignment/assessment runtime observation of `gpt-6.1-sol`
with thinking medium; this source invocation independently exposes `PI_MODEL=gpt-6.1-sol`
but no effort observation. Do not infer invocation effort from selection or earlier calls.
Assessment: `NO_BRAINSTORM_NEEDED` — settled, reversible instruction/fixture clarification,
approximately three causal work units (contracts/routing and affected fixtures; lockstep
docs; integrated acceptance/reviewer packet). Exact decomposition belongs to task generation.
No migration, runtime or dependency change is needed.

## Inspected baseline and traceability

Baseline main HEAD: `8832a4c61c3326861b3813151b3ed11eb53db979`; index/worktree clean at
source preflight. These are verified repository-derived facts, not new work requirements:

| Inspected owner / supporting span | Existing behavior → retained constraint → validation seam |
| --- | --- |
| [Task generation](../../skills/task-generation/SKILL.md), “Task contract” and “Review and handoff” | Already requires stable `Tnnn/Vn` REQUIRED pass criteria, smallest checks, evidence and manual/permission gates in existing fields; both adapters retain them. Preserve this shape and producing-gate return → focused producer assertions and representative practical contracts. |
| [Planner](../../skills/planner/SKILL.md), “Proportionate validation”, “Selected production and stage handoffs”, “TinySpec path” | Already carries stable verification needs and source authority, separate tasks and combined approval. Keep approval/legacy boundaries → source-to-task-to-brief trace, no historical retrofit. |
| [Coordinator](../../skills/coordinate-implementation/SKILL.md), “Build the Execution Graph”, “Select Execution Capability”, “Execute and Integrate”, “Review and Acceptance” | Already uses consecutive normally 2–5 coherent sequential tasks, one exact profile, whole REQUIRED union before coding, item-mapped pass/fail/not_verified return, bounded cheap acceptance, diagnosis-first original-contract repair and one final independent review. Extend these seams, not reimplement their architecture → mapped disposition/repair fixtures and preserved diff/checkpoint checks. |
| [Sole routing rubric](../../skills/coordinate-implementation/references/batch-routing.md), “Assess all six factors”, “Provisional family and effort choices”, “Selection and conditional repair gates” | Already assesses weakest contract/blind spot alongside closed design, tools, coupling, cost and approved guidance; family and effort independent, no universal ladder. Make oracle quality/cost practical in this owner → bounded routing rationale scenarios, not a score or second router. |
| [Shared coordination](../../skills/memory-handling/references/project-coordination.md), “Separate factual evidence”, “Qualified batch routing feedback”, “Exact guideline approval” | Already retains attributable attempts/profiles/diagnoses in one compact indexed run SUMMARY and requires exact owner approval of guidance. Refine factual item/disposition/escalation evidence here → inspect retained first/final attempts and unchanged guideline gates. |
| [Producer fixture](../../skills/task-generation/scripts/test_contract.py), `TaskGenerationContractTests` | Existing static contract assertions cover item/evidence/gates, adapters, continuity and checkpoints → strengthen only changed semantic carriers. |
| [Batch fixture](../../skills/coordinate-implementation/scripts/test_batching_contract.py), `sample_batch_contract`, `simulated_audit`, `SimulatedAcceptanceTests`, `simulated_repair_brief`, `SimulatedFeedbackTests` | Shared mappings and bounded repair/feedback already exist. Audit currently collapses outcomes to accepted/blocked and hardcodes “both invariants satisfied”; this cannot demonstrate task-specific proof relevance/dispositions → focused semantic fixture cases, not production enforcement or live performance claims. |

Formatting precedents, read-only: [active planning tasks](active-planning-routing-tasks.md)
and [batch-routing tasks](../../specs/002-batch-routing-contracts/tasks.md). Their existing
outcome/dependency/context/REQUIRED fields suffice; no new task schema or historical edits.

Dependency evidence: reuse inspected local owners above and [runtime requirements](../../REQUIREMENTS.md#runtime)
(pi 0.87.x, tested 0.87.1; pi-subagents 0.73.1; pi-ask-user 0.15.1). Pins unchanged;
no dependency-sensitive API/design decision, internet research, install or provider probe
is needed. Apply the [dependency research contract](../../skills/planner/references/dependency-research.md)
by local reuse, not model recollection. [Constitution](../../.specify/memory/constitution.md)
I–VI and [AGENTS.md](../../AGENTS.md) govern portability, authority and bounded evidence.
The associated [gotcha index](../../memory/MEMORY.md) has no entries;
[coordination guidelines](../../memory/coordination/GUIDELINES.md) have no approved guidance.
No historical run intake or inferred success history informs this design.

## Scope and approach

Included implementation surfaces are existing task-generation/planner handoff wording where
needed, coordinator batch formation/routing/acceptance/repair wording, the single routing
reference and shared coordination evidence contract; focused producer/batching fixtures;
active normative documentation only where changed behavior requires lockstep alignment.
Task generation must identify exact causal documentation/checker consumers before authorizing
writes. Integrated acceptance supplies the complete committed-range reviewer packet through
existing mechanisms. This is not authorization to edit those surfaces during source production.

Retain the architecture above. Producers establish practical contracts before batching;
coordinator evaluates the weakest material contract and feasibility of the combined checks,
then dispatches the whole union. Executor preserves task IDs, producer-before-consumer checks
and per-task checkpoints. Coordinator audits coverage, relevance, revision/environment,
consistency, gates and owned scope, gives each item an explicit disposition, and releases
only adequately verified dependents. A shared output can execute once and still map separately
to every covered item. Do not rereview every line or require a strong reviewer on every batch.

Routing must explicitly consider closed design **and** implementation difficulty alongside
contract quality, check cost and observability. Strong cheap reliable oracles may make a
moderately complex batch suitable for a smaller supported model. Weak oracles or hidden
coupling favor a justified stronger option when contracts remain adequate, or producing-gate
contract correction when they do not. More reasoning is not a substitute for proof or authority.
The six-factor rubric remains the sole qualitative routing owner; no formula, numeric score,
new router, fixed family ladder or automatic Luna penalty.

Dispositions are `satisfied`, `failed`, `insufficient-evidence`: map executor pass/fail/not_verified
reports through inspected proof, not confidence. `failed` requires objective evidence of
behavior violating the original criterion. Missing, irrelevant, stale, conflicting, unavailable
or unrun proof is `insufficient-evidence` unless valid observations independently demonstrate
failure; preserve both demonstrated defects and evidence limitations when they coexist.
Only satisfied REQUIRED items support acceptance. A zero exit or broad green suite alone does
not show relevance to the task criterion. Optional checks cannot replace REQUIRED evidence.

For manual contracts, an inspectable representative sample may require STOP and explicit user
approval **before** downstream/full expensive operation. Record the sample and decision against
the original gate; no LLM self-review substitutes for user acceptance. Ordinary tasks without
special/manual risk instead use specific existing practical observables, not a huge formal
specification or newly obligatory manual gate.

Failure handling continues valid work through exact-gap repair. Inspect failed run and invocation,
partial commits and evidence before resume/relaunch. Supply original tasks/contracts, current
implementation/SHA, prior item evidence, exact gaps, affected dependencies and invalidated checks.
Where diagnosed and authorized, stronger implementation capability repairs those gaps under
**the same contracts**, not generic strong-model review. Reuse only still-valid proof and rerun
invalidated items. Missing/ambiguous old approved contracts go to producing review/renewal;
never retrofit or lower acceptance post hoc. Environment, manual, permission and contract-definition
gaps do not automatically become model failures or get solved by stronger models. Unknown cause
stops blind retries. One exact owner-selected supported family/effort serves each invocation.

Clean retry is exceptional: document fundamental unsoundness, contamination, safe repository
mechanics or an applicable project rule, establish ownership and required owner gates first.
No automatic discard/reset or batch rollback; retain unrelated work, valid checkpoints and
attempt history. Existing task/evidence commits and independent final review remain mandatory.

Record factual batch/task item dispositions and selected versus observed binding/effort, contract
strength, first/final outcomes, exact escalation reasons and next selected profile or pending
selection in the existing compact run SUMMARY/index. Unknown observation stays unknown. Future
routing guidance changes only after selective synthesis and exact OWNER APPROVED content;
no parallel store/schema, automatic mutation, one-failure rule or unsupported performance claim.

## Acceptance coverage (15 source criteria)

Each criterion below must become stable task-local REQUIRED items with objective pass criteria,
smallest sufficient checks, expected evidence and applicable gates in existing task fields.
This coverage is behavior, not an implementation task list.

| ID | Observable acceptance / smallest sufficient evidence |
| --- | --- |
| A1 | Producer contracts retain task IDs and REQUIRED criterion/check/evidence/gates plus optional distinction through both adapters; focused producer assertions and a compact ordinary-task example show practical observables without invented manual ceremony. |
| A2 | Pre-assignment rationale explicitly compares closed design/implementation difficulty with weakest contract quality, cost and observability within all six factors; bounded contrasting cases show moderate complexity + strong cheap oracle can justify smaller capability, and weak oracle/hidden coupling needs justified stronger choice or producing gate. No score/new router. |
| A3 | Consecutive coherent sequential batches preserve order, task IDs and producer checks; formation explicitly considers practical combined verification and attributable failures. Shared files/headings do not force per-task dispatch; evidenced gates/context/scope differences still split safely. Inspect graph/brief and focused fixture. |
| A4 | Whole predefined REQUIRED union reaches executor before coding, unchanged, and return maps every item task-by-task with concrete proof or explicit not_verified reason; shared execution once preserves all mappings. A removed mapping blocks acceptance. |
| A5 | Cheap coordinator acceptance checks completeness, relevance to each criterion, scope, revision/environment and consistency plus existing actual task diff/ownership/SHA/checkpoints. A passing-but-irrelevant output is insufficient evidence, not success; focused positive/negative fixture demonstrates this without broad line-by-line rereview. |
| A6 | Each item has explicit satisfied/failed/insufficient-evidence disposition with reason/proof; genuine demonstrated bad behavior differs from missing, irrelevant, stale, conflicting or unrun proof. Fixture covers this distinction and confidence-only rejection. |
| A7 | Acceptance/dependent release requires all relevant REQUIRED proof and gates satisfied; optional green checks cannot compensate. Shared checks do not release a consumer before required producer evidence; bounded blocked/release case. |
| A8 | Representative-sample manual STOP prevents downstream/full expensive operation until inspectable sample and explicit user approval; pending/rejected gate blocks, approved gate permits only authorized continuation. LLM self-review is no substitute; ordinary no-special-gate path still works. |
| A9 | Inadequate or ambiguous existing approved contracts return to producing review/renewed approval before dispatch; no historical retrofit, weaker post-hoc criteria or executor-defined replacement. Inspect producer/coordinator carriers. |
| A10 | Inspected diagnosed failure can receive authorized stronger implementation repair for exact gaps with original tasks/contracts, current SHA/state, prior evidence, dependencies and invalidations; fixture proves same-contract repair, preserved valid work and rechecked invalidated items, not generic review. |
| A11 | Normal continuation preserves valid work; clean retry requires documented exceptional justification, safe ownership/repository mechanics and owner/project gates. Bounded unjustified/justified scenario rejects automatic discard/reset. |
| A12 | Failed run/invocation inspection precedes any resume/relaunch; unknown cause stops blind retry. Non-model environment/manual/permission/contract gaps remain accurately blocked and do not automatically escalate capability; focused diagnosis cases retain exact gaps. |
| A13 | One supported owner-selected exact profile propagates unchanged per invocation, family/effort independently justified; changed repair profile requires capability/owner gates, no fixed ladder or Luna penalty. Unknown actual binding/effort is never inferred. Inspect dispatch/repair carriers. |
| A14 | Existing compact SUMMARY/index retains attributable batch/task item outcomes, contract strength, selected/observed profiles, first/final attempt and exact escalation reasons/next selected profile or pending. Factual reflection cannot mutate guidance without exact owner approval; no second store/schema or one-failure rule. |
| A15 | Active documentation matches implemented contracts; integrated source→task→union→evidence→disposition→repair→feedback trace and complete committed-range packet support one fresh independent final review. Passing cheaper-model contracts need no mandatory strong per-batch reviewer. Checks report static/simulated limits and `/reload` after actual global skill changes. |

## Validation, non-goals and handoff

Reuse existing `test_contract.py` and `test_batching_contract.py` infrastructure. Focus cases
on task-specific dispositions/relevance, manual STOP/release, shared mappings, original-contract
stronger targeted repair, clean-retry justification and oracle-sensitive routing. Named scenarios
and targeted negative mutations should detect the actual changed seam; no exhaustive matrices,
new test engine, benchmark, live performance claim or paid/provider exercise. Broader checks
are justified only by concrete affected integration/policy seams. Instruction/static fixtures
cannot prove unrestricted runtime obedience. No migration/rollback mechanism is needed;
corrections remain focused verified commits, not history rewriting.

Excluded: task model classes/quotas, per-task dispatch/review, new workflow/framework/schema/store,
runtime/settings/dependency changes, migrations, automatic learning, guideline edits, speculative
legacy recovery, historical artifact rewriting, broad rereviews, installs, external operations,
push/deploy, paid probes and automatic reset/discard. Existing TinySpec/Standard/legacy authority,
source approval, task checkpoints, owned paths, manual gates and final-review independence remain.

Source-stage validation is local source traceability, local link destinations, whitespace and
allowed-path diff/ownership inspection only; it does **not** claim implementation fixtures or
future feature checks pass. Source and discovery link checkpoint precedes the separate factual
SUMMARY/index evidence checkpoint under the [task-commit contract](../../skills/memory-handling/references/task-commit-contract.md).
No STATE.md writes or implementation authorization. No unresolved product decision or explicit
owner deferral remains; live obedience/callability and fresh independent reviewer availability
are unverified future-stage capabilities, not implicit permission or source-stage acceptance.

Task-generation handoff: use this separate source and A1–A15, all settled constraints above,
verified owners/supporting spans and existing formatting. Preserve small causal sequencing,
documentation/integration coverage and task-local REQUIRED observables; do not assign execution
profiles. Planner reviews separate tasks against current source content and obtains combined
approval before coordinator preflight. Current source status: **prepared, not approved**.
