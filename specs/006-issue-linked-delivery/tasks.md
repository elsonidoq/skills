# Tasks: Issue-linked delivery and manual skill assessment

**Sources:** [spec.md](spec.md), [plan.md](plan.md), [research.md](research.md),
[data model](data-model.md), [interfaces](contracts/interfaces.md), [quickstart](quickstart.md).
**Executable handoff:** [tasks.json](tasks.json) holds each task's complete scope, owned paths,
acceptance and REQUIRED commands. This file is the brief human presentation of the same graph.

## Shared context

- Requirements come from the current spec. Use the actual selected `.pi/workflow-executor.json`:
  Terra/medium workers, explicit Sol/medium fallback and fresh Sol/medium reviewers. No model
  substitution or agent capability version pins. Each executable task links here because the
  current runner forwards task objects, not arbitrary top-level context.
- [ADR-0003](../../docs/decisions/ADR-0003-current-launch-authority-and-neutral-tasks.md) and
  [ADR-0004](../../docs/decisions/ADR-0004-shared-routine-worker-permissions.md) apply: preserve
  current launch/shared routine authority in initial, corrective and resumed prompts. Ordinary
  scoped fixes, isolated setup and small local tests/databases need no repeated consent.
  Retain actual product/material-scope/manual/paid/security/data/external gates, hooks/signing,
  unrelated work, inspected cause-specific recovery and the failed-Sol escalation stop.
  [Project memory](../../memory/MEMORY.md) also preserves autonomous routine technical choices
  and non-waking routine status. No memory/STATE/ledger or permission-service work.
- Final explicit planning/implementation approval may cover the exact operative proposals in
  [plan](plan.md#operative-amendments-for-later-explicit-approval). T001/T003/T016 inspect and
  reuse precise evidence for unchanged content/scope through normal launch/brief context;
  absent approval stops the affected change. Changed content or uncovered actual effects need
  their real gate. Do not repeat task-by-task consent or add an approval cache/schema/protocol.
- Fixed outcomes: Python LangGraph/Pi/LangSmith, one execution controller, standard persistence/
  interrupt/fanout/reduction, safe effect reconciliation and answer delivery, explicitly directed
  parallelism, exact ownership/checkpoints/history, metadata-only privacy and observed live
  visibility before monitor removal. [Requirements versus proposed mechanisms](plan.md#requirements-versus-proposed-mechanisms)
  distinguishes these from node layout, pauseQuestions spelling, saver arrangement, backend
  marker, intent encoding, exact SDK helpers and compatible-route mechanics. Prefer simpler
  equivalent existing mechanisms when actual checks prove the same observables and preserve
  consumers/authority/security/history. Routine equivalent mechanics are autonomous; material
  scope/privacy/accepted-architecture changes still require the owner. No new abstraction layer.
- Keep independently testable outcomes separate; tests/docs and routine teardown stay with each.
  Sequential implementation is the default for these overlapping paths. Product wave tests use
  explicit fixture concurrency authority, not implied parallel implementation permission or
  mandatory worktrees. Verify and focused-commit each producer before consumer reliance.
  Preserve #28/#43 helpers without broader repairs; related issues remain separately owned.
- Commands stay in consumed JSON `checks` fields; semantic acceptance stays prose. New
  test_graph_*.py/test_tracing.py selectors are implementation deliverables, not existing passes.
  Use permanent real saver/SDK/Git/graph checks at the first usable seam (T004–T014), then final
  local integration T017. Pure helper mocks cannot prove actual custody/answer/wire boundaries.
  No prototype chain, broad synthetic replacement or historical replay. Failed/unrun necessary
  proof blocks affected reliance; reuse unchanged applicable proof, repeat only if invalidated.
- Only T019 tracker and T020 account/project/region/access/pricing/upload questions remain in
  executable `gates`. They are real operation boundaries, not repeat policy consent. T021
  consumes applicable successful T020 visibility evidence without asking for recertification;
  absent/invalidated proof still forbids removal. Missing gates block only affected work; the
  current sequential runner does not automatically skip blocked tasks, so scope available work
  honestly. No installs/live operations are established by planning evidence.
- Retain six intake checks only: readable file, parsed list, ID/work description, unique IDs,
  existing dependencies and no cycles. No admission metadata, automatic conversion/replay,
  raw/ambient tracing, background assessment, service/data deletion, push or deployment.

Known baseline: `check-planner-workflow.py` expects lowercase `evidence-only review reassessment
uses the existing retained evidence`, but the coordinator carrier starts `Evidence-only`.
T001 aligns that maintained assertion; no skipped check, current pass claim or broader repair.

### Normal coordinator delivery — not an executable worker exercise

After actual implementation, specified checks and fresh independent final review, coordinator/
finish-session publishes the same meaningful executive summary to [issue #44](https://github.com/elsonidoq/skills/issues/44)
and current owner chat under actual tracker authority: result, verification/limits, review focus,
exact reviewed commit and attributable checkpoint links, with unrelated context distinguished.
Inspect/read back issue effects and report partial publication, not false success. Delivery
then awaits real owner review/acceptance. If actual feedback occurs, link purpose-classified
corrections and refresh the presented reviewed SHA; new requirements renew affected approval.
Close only after actual explicit acceptance of that revision plus closure authority/readback,
retaining the trace. Unobserved correction/acceptance/closure branches remain NOT VERIFIED,
not passes or blockers demanding invented work. Do not manufacture corrections, unrelated test
issues, owner acceptance or closure; no automatic RCA, skill edit or PR. This is the normal
final delivery obligation, not T017 worker publication or a renamed replacement for old T018.

## Bounded outcomes

- [ ] T001 Reconcile the runtime operative contracts
  - **Depends**: none
  - Reconcile the exact runtime/constitution amendments using precise final approval, not repeat questions. Preserve authority/checkpoint/review protections and align the known maintained-carrier case mismatch.

- [ ] T002 Carry the issue from planner understanding into task execution
  - **Depends**: T001
  - Associate after understanding, never as intake prerequisite; carry the same qualified issue into artifacts and actual initial/corrective/resumed worker/reviewer context. Preserve bare lists, existing planning approvals and actionable tracker gaps; no writes in local tests.

- [ ] T003 Define natural reviewed issue delivery
  - **Depends**: T002
  - Define natural exact-reviewed-commit issue/chat delivery through existing skills, with conditional real feedback/correction and acceptance-before-authorized-closure handling. Reuse exact final policy approval; no staged lifecycle exercise.

- [ ] T004 Provide standard file-backed graph persistence
  - **Depends**: T001
  - Resolve the compatible hashed lock and durable standard graph persistence, proving reopen/interrupt behavior and old-history preservation. Saver layout/API details are proposals, not additional owner requirements.

- [ ] T005 Reconcile focused Git success before history retry
  - **Depends**: none
  - Reconcile actual parent/path/content facts after Git success/history loss without duplicate commit. Intent encoding can vary; normal hooks/signing and unrelated bytes remain protected.

- [ ] T006 Execute dependent tasks through a sequential graph task interface
  - **Depends**: T004, T005
  - Deliver graph task execution with dependency/checkpoint readiness, reconciled provider calls, real checks and scoped correction. Proposed subgraph layout must not wrap the old engine.

- [ ] T007 Route independent review and scoped repair through graph transitions
  - **Depends**: T006
  - Replace review/repair dispatch with framework transitions while preserving fresh read-only review, evidence/coverage and scoped repair. Node layout may simplify; old controller is removed at cutover.

- [ ] T008 Settle Pi questions into a saved idle transport pause
  - **Depends**: none
  - Prove safe settled SDK question pause with retained context before reliance. pauseQuestions/abort-to-idle is proposed; a simpler supported suspension mechanism must preserve consent, settlement and existing callers.

- [ ] T009 Deliver durable graph replies to actual saved task context
  - **Depends**: T006, T008
  - Deliver the actual durable terminal/parent answer to the correct retained task context after reopen, without replay or gated action before consent. Wait-node/Command wiring may vary, not these observables.

- [ ] T010 Feed inspected recovery actions into graph continuation
  - **Depends**: T007, T009
  - Provide graph action consumers for inspected continue/fresh/escalate, transfer, routine repair and review refresh before public cutover. Preserve original scope/effects/authority and failed-Sol stop; no broader #28/#43 repair or automatic retries.

- [ ] T011 Cut the existing CLI over to one graph backend with explicit legacy routing
  - **Depends**: T010
  - Switch public CLI to one graph controller, preserving history and an explicit usable compatible legacy route without automatic conversion/replay. Backend-marker and route mechanics may use verified simpler equivalents.

- [ ] T012 Route attached-parent messages to multiple exact active targets
  - **Depends**: T008
  - Route parent messages to exact active targets, never broadcast or consume stale replies. Preserve owner-only separation and non-waking routine status; storage representation is proposed.

- [ ] T013 Complete directed disjoint waves before shared checks and Git
  - **Depends**: T011, T012
  - Complete explicitly directed disjoint waves with thread-safe state, retained successful siblings and a quiescent shared check/Git boundary. Default sequential; separate focused commits precede dependent release, no mandatory worktrees.

- [ ] T014 Submit only safe invocation metadata through the actual LangSmith SDK
  - **Depends**: T011
  - Prove actual final-SDK metadata-only requests, qualified usage, zero network without authority and fail-open execution. Exact LangSmith helpers may simplify, never privacy or real upload gates.

- [ ] T015 Provide the manual evidence-based skill assessment entry
  - **Depends**: T001
  - Add one manual portable assessment skill: all paginated open/closed issues, PR exclusion, acceptance as evidence, honest attribution and cross-issue minimal proposals. Local reader/carrier sensitivity preserves proposed/no-change versus delivered-only addressed; no scanner/ledger/self-edit.

- [ ] T016 Retire specified behavioral machinery and active mandates
  - **Depends**: T001
  - Retire only the four evaluation docs, RPC driver/loader/driver-only tests and active mandates using exact final approval. Keep meaningful runtime/static/security checks and historical limits; no replacement suite.

- [ ] T017 Verify the retained local application composition
  - **Depends**: T003, T013, T014, T015, T016
  - Integrate local application seams and causal wiring/docs fixes with retained checks. Normal fresh final review follows; this worker does not publish delivery or stage owner acceptance.

- [ ] T019 Verify real manual assessment evidence and label transitions
  - **Depends**: T017
  - Assess one owner-selected real set with complete actual discovery (all pages, open/closed, no PRs or acceptance eligibility filter). Use available linked evidence honestly for grouped minimal proposals or no-change; reuse T015 for absent categories and report limits, never manufacture cases or improvements.
  - **Live gate**: Scoped tracker reads/label/comment effects with readback. Keep proposed/no-change distinct; addressed needs actual delivered evidence or remains unobserved/NOT VERIFIED. No automatic assessment, skill edit or PR.

- [ ] T020 Observe real LangSmith replacement visibility
  - **Depends**: T017
  - After same-revision local privacy proof and explicit account/project/region/access/pricing/network authority, observe a real permitted graph/Pi invocation in LangSmith UI. Usable hierarchy and safe known/unknown metadata, not HTTP/offline success, release removal.
  - **Live gate**: Selected LangSmith account/project/region/access/pricing/upload and actual Pi-call scope; same-revision final-SDK privacy proof before upload. Usable real UI hierarchy, not HTTP/offline success.

- [ ] T021 Retire only redundant monitor source after observed replacement
  - **Depends**: T020
  - Inspect applicable successful T020 visibility evidence, then retire only redundant monitor source/callers. Missing/invalidated proof stops removal without recertification; retain history/data/readers/limitations, no service stop.

## Coverage and handoff

FR-001–002 → T002/T011 and normal coordinator delivery; FR-003–004 → T003 and normal
coordinator delivery; FR-005–008 → T001/T004–T013/T017; FR-009–010 → T014/T020;
FR-011 → T020/T021; FR-012–014 → T015/T019; FR-015 → T016/T017;
FR-016 → T001/T003/T016 using precise final approval evidence. SC-001 → T002/T003 plus
normal coordinator delivery; SC-002 → T005–T011/T017; SC-003 → T012/T013/T017;
SC-004 → T014/T020/T021; SC-005 → T015/T019; SC-006 → T016/T017;
SC-007 → applicable authority/checkpoint/review boundaries. T018 is removed; IDs need not be contiguous.

Validate both task presentations and current read-only intake. Internal graph interfaces precede
public cutover T011; concurrent composition is checked at T013, final local integration at T017.
Fresh independent final review covers actual delivered checkpoints and honest outstanding gates.
Changed global skills/extensions in Paseo require a fresh-session handoff verifying revision,
approval and loaded capabilities, never owner reload or automatic restart. Task production is
not final task approval or implementation acceptance.
