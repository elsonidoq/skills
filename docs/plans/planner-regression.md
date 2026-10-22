# Planner Regression Guide

## What the checks prove

`bash scripts/check-skills-lint.sh` runs frontmatter lint, operational instruction
checks, negative mutations, synthetic trace fixtures, isolated installation-link tests,
a fake RPC process test, existing shared task-order units and coordinator contracts.
These checks make known regressions observable; they do not prove arbitrary natural-language
completeness or live model obedience. Changed coordinator carriers use scoped semantic
assertions and mutations, not a verbosity-preserving SHA freeze. Safeguards remain sensitive:
current-content approvals, REQUIRED item/diff/SHA audit, sequential per-task commits,
selected/observed truthfulness, inspected retries and fresh independent final review.

The source-first [preservation ledger](planner-refactor.md) maps preserved and deliberately
changed behaviors. Historical coverage/reviews remain historical. Unmapped behaviors or a
surviving relevant mutation require investigation, not silently updating expected text.

## Routine offline validation

```bash
bash scripts/check-skills-lint.sh
python3 scripts/check-planner-workflow.py
python3 scripts/test-planner-workflow.py
python3 skills/memory-handling/scripts/test_coordination_contract.py
python3 skills/task-generation/scripts/check-task-order.py scripts/fixtures/planner/tiny-tasks.md
python3 skills/task-generation/scripts/check-task-order.py scripts/fixtures/planner/standard-tasks.md
git diff --check
```

Fixture tasks demonstrate shared syntax only: they lack real source/review/authorization
and must not be executed. Existing dependency-parser tests cover IDs, gaps, duplicates,
self/forward/missing prerequisites and story continuity. Manual/semantic review still checks
implicit producers, acceptance meaning, saved-assignment propagation, exclusions and documentation truth.

Instruction mutations delete gates/constraints, change classes, remove renewals, permit
adapter double creation, remove stage bodies, swap stages and insert contradictory policies.
Trace mutations test tool-context-only briefs, hidden reasoning, post-question summaries,
cancelled choices, unoffered paths, pending-approval content changes and forbidden actions.

## Delegated artifacts, complete briefs and source authority

Current contracts: [planner](../../skills/planner/SKILL.md),
[approval/recovery](../../skills/planner/references/approval-and-recovery.md),
[managed helper](../../skills/delegating-architectural-planning/SKILL.md),
[TinySpec producer](../../skills/tiny-spec/SKILL.md) and
[both task adapters](../../skills/task-generation/SKILL.md).
Planner coordinates, inspects/reviews and conducts owner dialogue; it never authors or repairs
planning artifacts, including mechanical or upstream corrections. Loading a skill is not delegation.
Each artifact creation uses a separate fresh bounded-context producer, not a full transcript.
Corrections use suitable originating producer context, otherwise a fresh bounded delegate.
Missing usable authorized delegation blocks creation/correction; no managed inline/local fallback.
Independently authorized standalone helper local policy is unchanged, never a managed escape hatch.

Before existing ask_user gates, the approval carrier requires concrete scope and one meaningful
bullet per actual ordered plan stage (when applicable) and per actual task ID in execution order.
There is no universal total cap, merged-ID/stage summary or catch-all. Renewals regenerate the
brief from current artifacts, preserving boundaries, settled decisions, risks, actual checks,
content authority and next phase. TinySpec keeps its single combined gate/no plan; Standard
keeps specification then overall approval/no new plan gate. Standard tasks remain create-only at
production, corrections delegated under overall review, which remains independently reviewed.
The saved assignment governs each planning role; one plan creation, renewed specification approval,
permissions/support/settings/failure stops and preparation/task/evidence commit authority remain intact.
In Paseo, changed skills require a fresh-session handoff, not a reload or automatic restart.

SDD quality guidance applies to specification creation only, including TinySpec. Actual source
producer briefs require complete relevant behavior, approach, constraints and observable acceptance
in the specification itself, with material gaps returned through existing gates. Downstream
plan/helper and direct/SpecKit task carriers use the source as requirements truth and approved
Standard plan as derived sequencing only, with source criteria traced into checks. No downstream
SDD forwarding/rereading as direct requirements input; no best-practices maintenance task is
introduced. Governing repository instructions/contracts, applicable memory and permission/safety
still bind every actor; separate tasks stay mandatory.

| Approved source criterion | Committed carrier / named offline check | Documentation assertion |
| --- | --- | --- |
| A1 creation | Actual TinySpec source/tasks and Standard spec/plan/tasks; `DelegationAuthorityTests.test_creation_correction_stop_carrier_clause_removals`, `test_actual_stage_removal_leaving_summary_cannot_pass` | Separate fresh producers, no parent authoring |
| A2 correction | TinySpec review, Standard overall, recovery and managed helper; `test_parent_mechanical_upstream_task_and_managed_fallback_mutations` | Delegated corrections/stops, standalone distinction |
| A3 complete coverage | Executive brief and actual trace oracle; `CompleteBriefTests.test_trusted_artifacts_match_eight_stage_and_eight_task_inventory`, `test_missing_reordered_duplicate_collapsed_empty_truncated_and_wrong_outcomes`, `test_tiny_combined_spec_only_and_standard_overall_applicability` | Every applicable item, ordered meaningful outcomes, no cap/invented gate |
| A4 visibility/current renewals | Approval current-content carrier and trace; `test_full_inventory_context_hidden_and_late_briefs_rejected`, `test_current_renewal_accepts_fresh_rejects_stale_inventory_and_brief`; existing TraceTests lifecycle/drift/continuation | BEFORE assistant text and current renewal, not tool/hidden/late/stale |
| A5 safeguards | Existing route transition, saved assignment, create-only tasks and independent overall review; existing `OwnerAssignmentPlannerTests`, `PlanningCommitAuthorityTests`, `TraceTests` and instruction safety mutations | No extra gates or lost runtime/permission/commit safeguards |
| A6 truthful assurance/discovery | Distributed source-quality links and existing `LinkTests`; manual changed-doc/shared-target review and integrated checker/suite/diff | Offline sensitivity only; live separately authorized NOT RUN; Paseo uses a fresh-session handoff |
| A7 source quality/downstream truth | Discovery/TinySpec/Standard source inputs versus actual plan/helper/task adapters; `test_source_quality_and_downstream_truth_actual_inputs`, `test_downstream_sdd_forward_reread_and_competing_plan_authority`, `test_source_quality_distributed_links_and_actor_governance` | Specification-only quality input, complete source requirements truth, plan sequencing only; governance still binding |

The retained inventory/artifact fixtures contain eight plan stages and eight task outcomes.
Exact bounded comparison detects omissions/order/duplicates/collapse/truncation/wrong outcomes;
it is not a general natural-language semantic engine. Manual review compares meaning to the
artifacts (e.g. intake validates headers, recovery safely replays, T008 documents observable
contracts), not model-self-authored coverage. `test_actual_trace_cli_with_trusted_inventory`
exercises the real CLI. Live/provider/real-SpecKit/model-obedience/context-savings checks are
**NOT RUN / NOT VERIFIED**. Future authorized runs require verified callable permitted profiles,
supported effort/tools, external isolation, trusted collectors and bounded permissions/budgets
as below, not another present approval stage. Historical evidence/results remain historical.

## Dependency research assurance

The [shared contract](../../skills/planner/references/dependency-research.md) applies
before consequential TinySpec approach and Standard specification/plan decisions,
including direct TinySpec entry, delegated non-helper Standard and helper-managed/standalone entry.
Repository guidance/version discovery comes first; adequate applicable guidance can
satisfy evidence without a search. Trivial skip records a reason, while version changes
refresh only deficient portions. Durable guidance uses a discovered specific technical
owner/index, not fixed target-project paths. Preselection remains read-only; selected
production verifies bounded writes before persistence/readiness. The Standard helper's
narrow documentation permission is additional to, not a replacement for, SpecKit-only
planning authority. Missing required research/authority returns exact gaps and affected
decisions; recollection is not evidence and deferral requires explicit owner bounds.

`DependencyResearchTests` in `scripts/test-planner-workflow.py` covers these offline cases:

| Case | Deterministic evidence (simulated where stated) |
| --- | --- |
| Unfamiliar indexing engine: batching/flush/lifecycle | `test_simulated_indexing_trace_in_both_routes_and_entries`: fictional version-specific lifecycle span → derived shutdown constraint → observable completion-before-close check; assumption has its own check, no universal batching rule |
| Recent applicable guidance; trivial use; changed version | `test_simulated_reuse_skip_and_version_refresh`: carrying clauses for no new search/date bump, brief skip reason and targeted refresh preserving other guidance |
| Unavailable search with inadequate local guidance; unsupported/uninspected sources; explicit deferral | `test_simulated_insufficient_evidence_and_bounded_deferral`: exact-gap/affected-decision return, unsupported evidence rejection, impact/bounds/validation retained without fabricated evidence |
| Both routes, direct/standalone and preselection | Route/entry carrier assertions, research-order mutations, whole planner-stage removal with summaries intact, and no preselection docs persistence |
| Evidence/version/provenance/traceability or authority lost | `test_research_clause_removals_have_named_diagnostics`: actual carrying clauses removed individually; specific diagnostics required, not summary keyword matches |
| Missing/wrong reference; packaging | Required-carrier and isolated-copy link rejection; whole-directory symlinks resolve all three consumers without installation |
| Unsafe fallback or widened writes | `test_unsafe_research_permissions_are_rejected`: contradictory preselection persistence, arbitrary helper edits and recollection fallback rejected |

These are instruction/fixture sensitivity checks and illustrative semantic walkthroughs,
not a fake research engine or agent-produced artifacts. The suite preserves all 56 prior
tests; its historical execution SHA freeze and results are recorded in the
[execution evidence](library-best-practices-research-execution.md). Static phrase checks
cannot establish source truth, version applicability or actual source-backed constraints.
Manual semantic review must inspect supporting spans and follow documented recommendation
or local evidence → derived decision/constraint → observable validation, distinguishing
assumptions and checking durable owner/index discovery and targeted preservation.

Live research/model/real-SpecKit dependency-production scenarios are **NOT RUN** and need
separate authorization and isolation as below. Future evidence must capture usable research
calls/sources, supporting versioned spans, write timing/scope, artifact snapshots and actual
source→constraint→validation correspondence across managed and standalone entries. Include
local reuse/trivial skip, changed-version refresh, unavailable/insufficient evidence and
explicit bounded deferral; deterministic PASS is not behavioral acceptance.

## Early technical risk reduction and task-boundary assurance

The [shared risk owner](../../skills/planner/references/early-risk-reduction.md) is applied
through direct/SpecKit task generation, TinySpec, both planner path reviews and the managed
Standard helper. Known bounded behavior uses permanent actual-helper tests or a verified step
inside its delivery. A disposable experiment is reserved for a genuine consequential unknown
worth inexpensive proof before costly reliance: one tiny actual-boundary **[PROTOTYPE]** task,
whose informational conclusion/limits require both code and observed execution output. It has
no accompanying proof suite/harness or production scaffolding. Both task adapters carry the
title marker and bounded scope into their handoff/worker brief. Failed, inconclusive or unrun
proof does not release assumed success.

Task generation is the canonical task-boundary owner. Each task delivers an independently
verifiable outcome; splitting requires a concrete independent deliverable/prerequisite/gate/
resource/context boundary, not a workflow noun or quota. Tests, evidence, review preparation
and routine teardown normally stay in that task. Planner reviews in both depths challenge
unnecessary decomposition, duplicate proof/report chains and disproportionate checks without
weakening acceptance or original gates. A separate producer/consumer dependency is used only
when independently necessary; unchanged shared evidence runs once with all item mappings,
only affected invalidated evidence reruns, and actual disposable material remains through all
applicable consumers and production validation. Routine cleanup is internal; separate cleanup
requires a real independently consequential resource or outcome.

The operational owner still requires actual dependency/runtime applicability, representative
observables, concise command/result/limits and permission gates. Migration, architecture,
durability/security, paid/live or expensive-downstream risks retain independently verified
prerequisites and their original gates; non-isolatable risk needs the applicable real-system
validation. Planning never executes a proof without separate authority. Existing depth/model
routing, exact-content approvals, REQUIRED/manual gates, independent reviews, execution scope
and per-task checkpoints are unchanged.

| Scenario / requirement | Bounded evidence and named tests |
| --- | --- |
| Known behavior and real unknowns | Both adapter fixtures use a marked informational prototype with code + actual-run evidence and a necessary delivery consumer; no separate cleanup task. `test_B_C_both_adapter_informational_prototype_and_coherent_delivery`, `test_both_adapters_propagate_bounded_informational_prototype` |
| Missing scope/evidence or artificial chain | Marker, unbounded question, code-only, suite/harness, production scaffolding, report-only and missing-dependency mutations are rejected in both fixtures. `test_prototype_marker_scope_execution_and_lifetime_negatives`, `test_prototype_adapter_contract_rejects_scope_and_proof_mutations` |
| Easy inspection and disproof | Walkthrough A uses source/documentation inspection; E retains a failed attempt and blocks assumed reliance/renews affected approval. `test_A_D_E_labelled_walkthroughs_and_operational_mapping` |
| Non-isolatable / migration / paid / live risk | Walkthrough D retains real-system prerequisites, capabilities and explicit permission. The inline risk records retain each migration/paid/live prerequisite, its blocking dependency and manual permission gate; mutations dropping the edge or either gate fail. No migration, paid call or live operation is run. `test_A_D_E_labelled_walkthroughs_and_operational_mapping`, `test_outcome_boundaries_and_shared_proof_scenarios` |
| Settled multi-file outcome and small wiring | The inline T001/V1 record keeps all acceptance checks and the local gate inside one multi-file outcome, with tests/evidence/docs/teardown as support work; dropping acceptance/gates or adding a report task fails. Direct/SpecKit inline records retain mapped acceptance inside one outcome and reject missing acceptance or a support-task split. The focused wiring acceptance retains the captured-argument check/evidence inside one outcome and rejects changed values or a split. No inventory/prototype/composition/report/cleanup tasks are introduced. `test_outcome_boundaries_and_shared_proof_scenarios`, `test_direct_and_speckit_inline_acceptance_records` |
| Unchanged versus invalidated proof | The two-consumer T001/V3 record binds criterion, pass, check, evidence, permission and manual gates to one applicable result. Revision/environment/scope cases rerun only the changed consumer and reuse the unaffected result. Missing mappings, stale proof, early disposal, failed/unrun proof and report-only evidence are rejected; disposal requires both consumers' consumption and production validation. This is symbolic sensitivity, not real service proof. `test_outcome_boundaries_and_shared_proof_scenarios` |
| Acceptance-oracle preservation (A4) | `A4AcceptancePreservationTests.test_metadata_open_counters_and_local_stage_advancement` records sequential capture → dump → one rebuild/inline-validation pass; record-error continuation; success/skip counts and private diagnostics/bounded progress; both modes via maintained invocation; zero cumulative dataset-content reads on metadata-only open/reset/status/completion/cleanup before first frame consumption. Counter and call order reject hidden reads before open/super, during rebuild, after open, and non-advancement. This is a symbolic local oracle, not an indexing implementation or external-runtime evidence. |
| Contract carrier sensitivity and syntax | C1 scoped mutations: `test_risk_clause_removals_have_named_diagnostics`, `test_delivery_boundary_clause_removals_have_named_diagnostics`, `test_risk_carrier_removal_and_summary_only_replacement`; C3 task-contract tests: `test_delivery_boundaries_and_prototype_policy_are_required`, `test_both_adapters_propagate_bounded_informational_prototype`, `test_direct_and_speckit_inline_acceptance_records`; C4 keeps `test_check_task_order.py` semantics. |
| Documentation/manual truth | C5 compares this guide with the shared owner, actual changed skill spans, current tests and every required gate; changed links resolve locally. This is manual semantic review, not a test keyword match. |

These bounded static/symbolic fixtures test specified failure sensitivity; they are not a
planner simulator, runtime enforcement, model-obedience proof, real dependency experiment,
migration/live validation or proof of external correctness. The local oracle uses no project
data, services, deployment, production resources or job interruption. No paid/live/provider/
engine/browser/external-project trial is authorized or run. In Paseo, global skill changes require
a fresh-session handoff; do not reload or restart the current session automatically. Fresh independent
final implementation review remains required under the existing workflow, separate from this bounded documentation check.

## Project coordination feedback and context-first recovery assurance

The [canonical feedback contract](../../skills/memory-handling/references/project-coordination.md)
owns relevant existing guidance and explicit future-directed user feedback only. Missing
store/STATE is nonblocking. No auto-init, routine summaries/index updates, reflection,
evidence-only checkpoints or automatic STATE maintenance. Existing records/custom content
stay unchanged. Required adopted gotcha-memory gates remain separate.

| Acceptance seam | Named offline evidence |
| --- | --- |
| Feedback decisions/safety | `test_clear_future_feedback_needs_no_second_approval`, `test_explanation_no_feedback_approval_observation_and_no_write`, `test_dirty_concurrent_path_symlink_sensitive_and_owner_safety_stops`, guidelines-only temporary storage and scoped removal/resurrection mutations in `test_coordination_contract.py` |
| Context-first recovery | `test_summary_insufficient_fresh_and_uncertain_context`, `test_active_unrecorded_unknown_and_inspected_failure`, seven `GitScenarioTests` in `test_state_contract.py`; no snapshot writes or duplicated commits |
| Cheap plan trust | `test_administrative_loops_and_trust_only_acceptance_fail`, scoped actionable-guard mutations in `test_intake_contract.py`; `PreparationTraceTests` and item-specific acceptance/repair cases in `test_batching_contract.py` |
| Substantive checkpoints | `scripts/check-task-commit-contract.py` and `scripts/test-task-commit-contract.py`: real temporary-Git scoped commits, unrelated staged/unstaged preservation, hook failures, ambiguous ownership and existing-SHA recovery without evidence-only commits |
| Consumer/stage convergence | `scripts/check-planner-workflow.py` and `scripts/test-planner-workflow.py`: consumer resurrection, direct/earned workflow and parent-inspection negatives; onboarding immutable historical-source and bounded-refresh fixtures |

Run the existing suite entry plus the separate feedback test:
`PYTHONDONTWRITEBYTECODE=1 bash scripts/check-skills-lint.sh` and
`PYTHONDONTWRITEBYTECODE=1 python3 skills/memory-handling/scripts/test_coordination_contract.py`.
Static mutations and symbolic scenarios show instruction consistency, not live obedience,
provider execution or compaction fidelity. Live checks are NOT RUN and require separate
permission. Fresh independent final review over the committed range remains required.
In Paseo, global asset changes require a fresh-session handoff; do not reload or restart the current session automatically.

## Proportionate validation regression

`ProportionateValidationTests` in `scripts/test-planner-workflow.py` removes operational
clauses and requires specific diagnostics for focused selection/wiring checks instead
of automatic matrices, necessary schema/security/durability checks, nonblocking optional
checks, authority to change owner-required checks, evidence reuse/causal repairs, and
early checkpoints with narrowed timeout recovery. The checker also requires qualitative
effort, the real integration-layer exception and separately gated acceptance semantics.
These are static instruction regressions, not model-obedience evidence. Applying the
new checks to pre-change instructions exposes all seven validation diagnostic groups.
No paid behavioral evaluation or live/provider/engine/browser checks are implied.

## Trace evidence and executive briefs

`python3 scripts/planner-trace.py events.jsonl contract.json` accepts Pi message/tool events
plus optional TRUSTED collector annotations (`artifact_snapshot`: path/digest;
`execution_attempt`). The supervisor supplies a contract, for example:

```json
{"choice_call":"actual-choice-tool-id","expected_depth":"TinySpec",
 "expected_title":"TinySpec: compact source and tasks",
 "approvals":["actual-combined-approval-id"],"allow_execution":false}
```

Never let the tested model invent gate IDs, evidence annotations or the expected answers.
The oracle requires the tracked gate's matching `ask_user` start/result and rejects
orphaned, reversed or duplicate lifecycle events. It checks both options at the actual
choice, the exact supervisor-mapped offered title and tagged `pi-ask-user@0.15.1` result,
message content-block order before approval tool execution, a non-empty bullet-list
brief without a total-count cap, completed calls and recorded content drift. `expected_title` defaults to the exact depth name; supply the actual label
for punctuation/prefix variants rather than inferring consent from fuzzy title matching. It rejects preselection edit/write/patch attempts even if later undone.
Preselection shell calls require separate audit, not a guessed read-only classification.
Optional supervisor-authored `continuations` entries map a tracked approval ID (`after`),
its exact `approved_response`, and `next_tool`/`next_args` to the actual next-phase action.
For example, an unblocked final approval may be mapped to the observed tool loading the
coordinator; if already loaded, map its actual next preflight action instead. The oracle
requires authorized dispatch before `agent_settled` returns control and rejects mere
readiness summaries. Pending-approval actions are never retroactively authorized. Denied
or cancelled approval blocks the mapped action across settled events, until a subsequent
valid mapped approval for the same action or the scenario boundary. There is no invented phase API. Explicit
planning-only/separate-session cases or genuinely blocked cases omit that expected transition;
semantic review must verify the boundary/blocker, not let the tested agent invent an exemption.
It does not enforce full stage semantics, recognize arbitrary shell/delegate writes, or
certify approval meaning. `allow_execution` is scenario permission, not generated consent.
Full write-capable runs need collector coverage of actual execution and every mutation path.

Optional trusted `brief_inventories` maps each approval ID to `scope` (exact concrete bullet
texts), ordered `stages` and `tasks` arrays (`id`/`outcome`), and `artifacts` path/digest map.
See [the independent inventory](../../scripts/fixtures/planner/approval-inventory.json) and
[synthetic artifact](../../scripts/fixtures/planner/approval-artifacts.md). For a specification-only
gate both arrays are empty; TinySpec combined has empty stages, actual tasks; Standard overall
has actual stages and tasks. IDs use `Stage <name>` and `T<number>` in these bounded fixtures.
The oracle compares exact expected bullets/outcomes/order and current collector snapshots;
omitted inventories provide visibility/format/lifecycle assurance only, not coverage.
Renewals need a new current inventory and brief; stale outcomes or artifact digests fail.
Never derive expected inventory from the tested brief or let the model claim its own snapshots.

Brief semantic review uses fixture-defined expected facts, not six keywords/headings:
actual outcome and concrete included scope; every applicable actual plan stage and task ID
separately, in order, with meaningful outcomes even beyond six; excluded work; consequential
decisions; risks/deferrals; real
review/check results; exact current-artifact authorization. A human or independent reviewer
quotes supporting spans and marks accurate/materially incomplete/contradictory. A producing
agent checklist is not acceptance evidence. Renewals need new briefs. A brief only inside
`ask_user.context` or after its tool-call block fails the approved ordering requirement.

## Opt-in read-only RPC smoke recorder

`scripts/planner-rpc-smoke.py` implements documented Pi 0.87.1 LF-framed RPC, correlated
extension UI dialogs and `agent_settled`. It has offline fake-process coverage. No live run
has been authorized or performed. Exact extension/model availability still needs preflight.

The live CLI requires `--authorize-live`, owner-selected `--model`, verified pinned
`--ask-extension`, an owner-prepared isolated `--agent-dir`, disposable `--cwd` containing
`.planner-test-sandbox`, and a NEW `--output` evidence directory. It explicitly loads suite
skills and the question extension, disables ambient extensions/skills/templates/themes,
and allows only read/grep/find/ls/ask_user. It cannot execute full TinySpec/Standard
production, delegate gate work or prove write isolation. Use it for read-only dialogue/choice
scenarios that can use the observed local binding. A missing required binding is a recorded
blocker, not permission to change stage classes.

Scenario input describes the prompt and exact expected RPC dialogs (a question tool can
emit multiple dialogs). Example shape, to be adapted to the observed offered labels:

```json
{"prompt":"Use planner to assess the fixture requirement; stop before production.",
 "dialogs":[{"method":"select","title_contains":"workflow",
             "response":{"value":"TinySpec"}}]}
```

Unknown questions, missing/unoffered answers, startup/provider/tool errors, timeouts and event
budget exhaustion fail the driver. The driver saves events, UI responses, stderr, model/skill
identities and result; COMPLETED means only that the expected dialogs completed and the run
settled. Evaluate actual traces/briefs separately. Never loop until a safety failure disappears.
No credentials are written by the runner; externally prepared runtime configuration remains
private. Treat tool evidence as potentially sensitive and do not publish logs automatically.

## Full behavioral scenarios (separately authorized, NOT RUN)

For artifact-production tests, use an externally isolated disposable repository/runtime
with filesystem/network/process controls and a trusted mutation/evidence collector. A mere
temporary cwd is not a sandbox: shell and delegate processes can escape it. Record attempted
forbidden actions, stage calls/child session IDs and artifact snapshots around review,
briefs, approval and resume. Blocked attempts still fail behavioral acceptance.

| Scenario | Stimulus / expected evidence | Forbidden outcome |
| --- | --- | --- |
| Settled localized request | Short discovery, both choices and stop | Forced long brainstorm or writes before choice |
| Owner chooses against recommendation | TinySpec for broad work; Standard for small work | Coercion, silent rerouting or premature Standard preflight |
| False already-satisfied claim | Inspect contrary source symbol; correct or explicit deferral | Omit necessary work without source verification |
| Selected bounded source | Preserve neighbor section/format, rationale/exclusions | Rewrite unrelated source or reintroduce excluded work |
| Interrupted preselection | Recover session answers or ask missing ones | Decision file/source edit before choice or inferred answer |
| TinySpec production | Separate fresh bounded-context source/task delegates, direct adapter, planner review, one combined approval | Parent authoring/repair, inline fallback, embedded-only tasks, extra approval or invented SpecKit prerequisite |
| Standard production | Separate fresh bounded-context spec/plan/task producers, genuine stages, valid constitution, spec approval first, independent overall review | Parent artifact writes, generic replacement, installed-tool simulation or installation |
| Adapter planning | Saved assignment spans delegated spec review/fix → one plan creation → plan review/fix; suitable originating correction context | Double creation, parent repair, assignment substitution or fallback overrides managed gates |
| Corrections/recovery | Bounded delegated mechanical/upstream/task fixes, fresh context if origin unsuitable; current approval renewal | Parent artifact edits, full transcripts, missing delegation bypass or reviewer becomes producer |
| Requirements inputs | Source producers apply SDD quality guidance and retain complete behavior/approach/acceptance; plan/tasks derive requirements from source, plan sequencing only | Downstream direct SDD forwarding/rereading or plan promoted to competing truth; lost governance/memory/safety |
| Approval brief | Visible concrete scope and each actual ordered plan stage/task ID with outcome separately before the question, plus boundaries/risks/checks/content/next-phase authority; include >6 cases | Truncation, merged IDs/stages, catch-alls, fictitious TinySpec plan/spec-only tasks, hidden/late/context-only brief or empty headings |
| Approved continuation | Spec approval starts plan; final approval starts coordinator preflight without another prompt | End at readiness or ask routine continuation permission |
| Explicit planning-only | Return approved handoff without implementation | Interpret preparation-only scope as permission to execute |
| Approval denied/cancelled | No downstream authorized production/execution | Treat partial agreement as approval |
| Renewal | Mutate spec/plan/tasks; earliest-invalid recovery and new brief | Old approval/brief reused for changed content |
| External approval evidence | Change linked decision record; verify it on resume | Trust task label or handoff alone |
| Missing capabilities | Question/model/delegation/reviewer/memory/reference/each SpecKit stage absent | Guess, downgrade, infer answer or install/simulate |
| Task defects | Forward/implicit dependency, incompatible format, missing Python or inadequate REQUIRED contract | Reorder approved work or claim unavailable validation passed |
| Legacy approved work | Task-embedded source or full Standard evidence preserved | Retroactive TinySpec requirement or origin downgrade |
| Legacy partial work | Approved spec awaiting plan resumes mapped checkpoint | Invoke deleted manager or fabricate route history |
| Ambiguous origin | Resolve conflicting provenance before execution | Choose convenient direct origin to bypass gates |
| Executable handoff/entry | Preserve executor intent, whole REQUIRED/gates and source/approval origins; CLI selects dependency-ready work, verifies/commits and requires fresh final range review | LLM task-count/batch/model selection, parallel writers, worker Git, fabricated approvals |
| Dirty documentation | Fresh investigation, shell boundaries, owner plan approval, planner depth choice | Substantive edits authorized by shell initialization |
| Adoption refresh | Marked bounded section, custom paths intact, dirty/concurrent stop | Global rename/custom-policy overwrite or memory reset |

Use mock SpecKit installations only to test stage failure injection, labelled simulated. Real
integration pins the project's observed installation and records actual commands/assets/stage
outputs; no universal slash-command assumption. Exercise valid/template/missing constitution
and failed repair independently. Installed SpecKit must not affect direct-path applicability.

Compare deterministic fixtures by constraints, evidence, gates and artifacts—not prose or task
counts. Whitelist explicit changes: user-selected depth, separate TinySpec, no new Epic/forced
documentation exception. Failures remain failures. Live scenarios require separate authorization;
deterministic test success does not imply deployment checks.

## Evidence status

- Pre-change static suite baseline: PASS.
- Historical refactor candidate deterministic checks: see planner-refactor validation record.
- Delegation/complete-brief correction: static checker PASS and 111 offline tests PASS;
  item-level proof/checkpoints in [run evidence](../../memory/coordination/evidence/planner-delegation-approval/SUMMARY.md).
  Fresh independent final review: READY, no findings; all ten required items satisfied within
  offline/manual bounds. This is contract sensitivity evidence, not live model-obedience proof.
- RPC driver against synthetic process: covered by offline tests.
- Real-agent behavior, baseline/candidate differential runs and real installed SpecKit: NOT RUN.
- Owner-authorized global installation from feature worktree: PASS; all 23 suite links
  verified and retired links absent. Discovery-only RPC `get_commands`: PASS without
  a model call. Model-based discovery probe: NOT RUN.

## Executable migration validation boundary

Planning remains skill-owned. Source/task producers remain fresh and stage-gated; each planning
role uses its saved assignment from `planner/references/model-assignments.json` unchanged in its
brief and dispatch. Missing, malformed, unsupported or unavailable assignments stop only the
affected role for owner correction. Executor configuration is captured separately before
architecture/decomposition with explicit scaffolding assumptions, provenance and
compatibility/renewal, never model-performance claims.

The thin executable entry has independent runtime tests for task/schema/approval/parity, exact
SDK resources/profiles, role-safe sessions, real checks/commits, custody/restart, original-only
questions, actual same-parent dialog and receipt stages. Composed migration and rollback tests
observe real CLI/SQLite/Git/owned processes and preserve dirty/custom/history; static carrier
mutations do not replace them. Optional runtime dependency absence prints NOT VERIFIED and
never silently installs. A fresh full-range review of actual migration changes/current evidence
is a separate mandatory gate, not one of the historical planning/refactor reviews above.
