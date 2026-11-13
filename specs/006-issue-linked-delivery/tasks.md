# Tasks: Issue-linked delivery and manual skill assessment

**Input**: [Approved spec](spec.md), [derived plan](plan.md) and linked contracts.
**Executable task input**: [tasks.json](tasks.json). Same IDs/outcomes/dependencies; full bounded instructions, owned paths, acceptance and consumed checks/gates are task-local.

## Shared context

[spec.md](spec.md) is requirements truth; [plan.md](plan.md) is derived and challengeable.
Read affected [research](research.md), [data model](data-model.md), [interfaces](contracts/interfaces.md)
and [quickstart](quickstart.md). Issue: [#44](https://github.com/elsonidoq/skills/issues/44).
No task implies tracker write authority. No SDD quality document is a direct task input.

- Use exact existing `.pi/workflow-executor.json`: Terra/medium workers, explicit Sol/medium
  fallback, fresh Sol/medium reviewers. Do not edit bindings, use producer assignment for
  implementation, or require specific agent capability versions.
- [ADR-0003](../../docs/decisions/ADR-0003-current-launch-authority-and-neutral-tasks.md):
  current scoped launch overrides historical preparation labels. Preserve it in initial,
  corrective and resumed prompts. T002/T006/T007/T009/T010 check actual consumers.
  Executable instructions are authorization-neutral; phase status belongs in approval records.
- [ADR-0004](../../docs/decisions/ADR-0004-shared-routine-worker-permissions.md) and verified
  [memory index](../../memory/MEMORY.md): retain shared routine authority, autonomous routine
  technical choices, ordinary scoped repairs/isolated setup/small local tests and databases
  without repeated consent. Preserve genuine material/product/manual/paid/security/data/external
  gates, normal hooks/signing, unrelated bytes, failure inspection and stop after failed Sol
  escalation. No permission service/cap/memory write/default history intake/ledger. Routine
  progress must not wake the parent; questions and terminal completion can.
- Own only declared paths and coupled support. This task list uses sequential implementation;
  shared-path overlap needs coordination, not mandatory worktrees. Product concurrency tests
  use explicitly directed isolated fixtures, not implied concurrent implementation permission.
  Each producer is validated and focused-committed before consumer reliance. Preserve #28/#43
  helpers; related issues remain separately owned, not automatic closure/repair prerequisites.
- REQUIRED acceptance is each task's semantic acceptance plus `checks` and actual `gates`.
  Deterministic commands occur once in existing executable fields in [tasks.json](tasks.json).
  The current runner forwards the whole task object, including this task-local context link;
  it does not forward arbitrary top-level context. `gates` uses existing manual_gates string
  questions before dispatch, not a new schema. Genuine later operation/feedback/acceptance
  gates still apply; a generic affirmative question is not exact-revision acceptance.
- Exact policy approval gates belong to T001/T003/T016; current final approval can provide
  evidence, not fabricated consent or repeated routine-setup questions. Tracker delivery T018/assessment T019,
  account/project/region/access/pricing/upload T020 and observed visibility T021 remain real.
  Missing authority blocks only affected operations/reliance. Complete unrelated local work
  first; coordinator schedules available authorized scopes rather than falsely completing a
  gated task. This does not promise current sequential runner automatically skips blocked work.
- Preserve one final graph controller, saver/interrupt/Send/reducers, useful Pi/Git/check/session/
  history helpers and six linter checks only. No automatic conversion/replay, raw/ambient
  tracing, historical feature reconstruction, background assessment, automatic RCA/skill edit/PR,
  STATE/manifests, new test platform, service-stop/data deletion/push/deployment.
- `test_graph_*.py` and `test_tracing.py` are explicit implementation-produced selectors, not
  currently available passing checks. Other command families/files exist now. Run checks in
  selected implementation environment; establish lock/import consistency before graph reliance.
  Runtime/live/model behavior is NOT VERIFIED by task production. Unrun/failed required proof
  blocks affected reliance. Local necessary setup is ordinary authority, not global install.

## Proof selection and limits

Use permanent actual-helper tests at earliest useful seams: saver reopen T004, Git/history
window T005, provider reconciliation T006, installed SDK pause T008, actual answer consumption
T009, composed public sequential entry T011, directed wave completion T013 and FINAL-SDK privacy
T014. No separate prototype/scaffold/report/cleanup chain earns its cost. T017 checks final
local composition after integration, not a new comparison programme. Mock-only helpers cannot
replace actual saver/SDK/Git proofs where effects/order matter. Reuse unchanged applicable proof;
changed code/dependency/environment or failed/inconclusive results require affected correction/
replanning before reliance. Live tracker T018/T019 and LangSmith T020 are REQUIRED real-system
outcomes, not optional hardening; only T020 observed visibility releases T021 removal.

Known baseline: check-planner-workflow.py fails risk-coordinator-triage: expected lowercase
`evidence-only review reassessment uses the existing retained evidence`, coordinator carrier
starts `Evidence-only`. T001 aligns the touched maintained assertion. Do not skip the check,
claim it passes now, or turn this into unrelated repair.


## Independently verifiable outcomes

- [ ] T001 Reconcile the runtime operative contracts
  - **Depends**: none
  - **Paths/context**: `.specify/memory/constitution.md`, `AGENTS.md`, `README.md`; complete owned paths/support in `T001.owned_paths`.
  - **Acceptance/context**: Apply the exact runtime/constitution amendments only after explicit approval. Align affected maintained assertions (including the known case mismatch), keeping six-check intake, actual permissions, checkpoints and independent review; no runtime-success claim.
  - **Check**: REQUIRED commands appear only in `T001.checks` in tasks.json; run after this outcome and report actual results.
  - **Manual gate**: Exact runtime/constitution amendment approval. Full consumed question in tasks.json.

- [ ] T002 Carry the issue from planner understanding into task execution
  - **Depends**: T001
  - **Paths/context**: `skills/planner/SKILL.md`, `skills/task-generation/SKILL.md`, `skills/tiny-spec/SKILL.md`; complete owned paths/support in `T002.owned_paths`.
  - **Acceptance/context**: Associate after understanding, never as intake prerequisite; carry the same qualified issue into artifacts and actual initial/corrective/resumed worker/reviewer context. Preserve bare lists, existing planning approvals and actionable tracker gaps; no writes in local tests.
  - **Check**: REQUIRED commands appear only in `T002.checks` in tasks.json; run after this outcome and report actual results.

- [ ] T003 Deliver and accept an exact reviewed issue revision
  - **Depends**: T002
  - **Paths/context**: `skills/finish-session/SKILL.md`, `skills/track-open-issue/SKILL.md`, `docs/index.md`; complete owned paths/support in `T003.owned_paths`.
  - **Acceptance/context**: Permit the reviewed exact-SHA executive summary in issue and chat through existing skills. Preserve purpose-linked corrections, partial publication recovery, explicit revision-specific acceptance and separately authorized closure; no automatic RCA/skill/PR.
  - **Check**: REQUIRED commands appear only in `T003.checks` in tasks.json; run after this outcome and report actual results.
  - **Manual gate**: Exact executive-summary policy amendment approval. Full consumed question in tasks.json.

- [ ] T004 Provide standard file-backed graph persistence
  - **Depends**: T001
  - **Paths/context**: `runtime/pyproject.toml`, `runtime/requirements.lock`, `runtime/coherence_workflow/graph.py`; complete owned paths/support in `T004.owned_paths`.
  - **Acceptance/context**: Resolve compatible hashed dependencies and deliver actual stable-thread/sync SQLite saver reopen and interrupt primitives in separate graph storage. Preserve Python minimum/history; align existing package fixture, report unavailable platform proof, no scheduler or upload.
  - **Check**: REQUIRED commands appear only in `T004.checks` in tasks.json; run after this outcome and report actual results.

- [ ] T005 Reconcile focused Git success before history retry
  - **Depends**: none
  - **Paths/context**: `runtime/coherence_workflow/git_effects.py`, `runtime/coherence_workflow/store.py`, `runtime/coherence_workflow/engine.py`; complete owned paths/support in `T005.owned_paths`.
  - **Acceptance/context**: Persist attempted parent/path/content before Git and reconcile actual matching direct child before retry, including advanced HEAD. Recover the original SHA without recommit; retain hooks, unrelated bytes and stop uncertain effects.
  - **Check**: REQUIRED commands appear only in `T005.checks` in tasks.json; run after this outcome and report actual results.

- [ ] T006 Execute dependent tasks through a sequential graph task interface
  - **Depends**: T004, T005
  - **Paths/context**: `runtime/coherence_workflow/graph.py`, `runtime/coherence_workflow/engine.py`, `runtime/coherence_workflow/store.py`; complete owned paths/support in `T006.owned_paths`.
  - **Acceptance/context**: Deliver independently testable graph task execution: dependency readiness, durable provider results, real checks/correction and accepted focused checkpoints. Prove uncertain-call stop before redispatch and authority in all prompt modes; internal until public cutover, no wrapper engine.
  - **Check**: REQUIRED commands appear only in `T006.checks` in tasks.json; run after this outcome and report actual results.

- [ ] T007 Route independent review and scoped repair through graph transitions
  - **Depends**: T006
  - **Paths/context**: `runtime/coherence_workflow/graph.py`, `runtime/coherence_workflow/engine.py`, `runtime/coherence_workflow/store.py`; complete owned paths/support in `T007.owned_paths`.
  - **Acceptance/context**: Deliver graph review/repair/re-review transitions against completed task checkpoints and actual check evidence. Preserve fresh read-only contexts, coverage/gaps, reassessment and failure inspection; old public controller is deleted together at cutover, not embedded in nodes.
  - **Check**: REQUIRED commands appear only in `T007.checks` in tasks.json; run after this outcome and report actual results.

- [ ] T008 Settle Pi questions into a saved idle transport pause
  - **Depends**: none
  - **Paths/context**: `runtime/pi-host/host.mjs`, `runtime/coherence_workflow/pi_adapter.py`, `runtime/tests/test_host.mjs`; complete owned paths/support in `T008.owned_paths`.
  - **Acceptance/context**: Add opt-in question pause to idle saved Pi session while non-opt-in callbacks keep working. Actual SDK fixture verifies no gated effect before consent and uncertain settlement is not safe redispatch; update coupled fixture assumptions.
  - **Check**: REQUIRED commands appear only in `T008.checks` in tasks.json; run after this outcome and report actual results.

- [ ] T009 Deliver durable graph replies to actual saved task context
  - **Depends**: T006, T008
  - **Paths/context**: `runtime/coherence_workflow/graph.py`, `runtime/coherence_workflow/engine.py`, `runtime/coherence_workflow/pi_adapter.py`; complete owned paths/support in `T009.owned_paths`.
  - **Acceptance/context**: Persist settled pause, then interrupt separately; actual terminal/parent answer reaches a new invocation in the same saved task context. Composed SDK/Git reopen test rejects stale reply, retains no-answer pause, denial and no replay.
  - **Check**: REQUIRED commands appear only in `T009.checks` in tasks.json; run after this outcome and report actual results.

- [ ] T010 Feed inspected recovery actions into graph continuation
  - **Depends**: T007, T009
  - **Paths/context**: `runtime/coherence_workflow/cli.py`, `runtime/coherence_workflow/graph.py`, `runtime/coherence_workflow/engine.py`; complete owned paths/support in `T010.owned_paths`.
  - **Acceptance/context**: Provide graph action consumers for inspected continue/fresh/escalate, transfer, routine repair and review refresh before public cutover. Preserve original scope/effects/authority and failed-Sol stop; no broader #28/#43 repair or automatic retries.
  - **Check**: REQUIRED commands appear only in `T010.checks` in tasks.json; run after this outcome and report actual results.

- [ ] T011 Cut the existing CLI over to one graph backend with explicit legacy routing
  - **Depends**: T010
  - **Paths/context**: `runtime/coherence_workflow/cli.py`, `runtime/coherence_workflow/engine.py`, `runtime/coherence_workflow/graph.py`; complete owned paths/support in `T011.owned_paths`.
  - **Acceptance/context**: Switch existing CLI start/resume to completed graph and remove custom task/review/resume loops. Verify full actual sequential CLI/SDK/Git/review/question composition; retain read-only old history and concrete compatible legacy-runtime route, no conversion or second engine.
  - **Check**: REQUIRED commands appear only in `T011.checks` in tasks.json; run after this outcome and report actual results.

- [ ] T012 Route attached-parent messages to multiple exact active targets
  - **Depends**: T008
  - **Paths/context**: `runtime/pi-extensions/coordinate-implementation-bridge.js`, `runtime/coherence_workflow/pi_adapter.py`, `runtime/tests/test_bridge.mjs`; complete owned paths/support in `T012.owned_paths`.
  - **Acceptance/context**: Replace singleton parent target with exact run/task/invocation/session/role routing. Two actual SDK fixture targets prove no broadcast/stale consumption, serialized owner-only questions and non-waking routine updates; no scheduling.
  - **Check**: REQUIRED commands appear only in `T012.checks` in tasks.json; run after this outcome and report actual results.

- [ ] T013 Complete directed disjoint waves before shared checks and Git
  - **Depends**: T011, T012
  - **Paths/context**: `runtime/coherence_workflow/graph.py`, `runtime/coherence_workflow/engine.py`, `runtime/coherence_workflow/store.py`; complete owned paths/support in `T013.owned_paths`.
  - **Acceptance/context**: Support explicit disjoint Send waves, thread-owned history and retained mode, sequential by default. Actual overlap/failure/reopen joins preserve sibling results; quiescent shared checks/Git yield separate task commits before dependent release, no mandatory worktree.
  - **Check**: REQUIRED commands appear only in `T013.checks` in tasks.json; run after this outcome and report actual results.

- [ ] T014 Submit only safe invocation metadata through the actual LangSmith SDK
  - **Depends**: T011
  - **Paths/context**: `runtime/coherence_workflow/tracing.py`, `runtime/coherence_workflow/graph.py`, `runtime/coherence_workflow/engine.py`; complete owned paths/support in `T014.owned_paths`.
  - **Acceptance/context**: Add one explicit metadata-only SDK adapter with opaque IDs and qualified local usage. Final real-SDK requests must exclude all private sentinels/ambient metadata; no-authority gives zero network, telemetry failure still permits safe graph checks/commit.
  - **Check**: REQUIRED commands appear only in `T014.checks` in tasks.json; run after this outcome and report actual results.

- [ ] T015 Provide the manual evidence-based skill assessment entry
  - **Depends**: T001
  - **Paths/context**: `skills/assess-skill-improvements/SKILL.md`, `README.md`, `docs/index.md`; complete owned paths/support in `T015.owned_paths`.
  - **Acceptance/context**: Add one manual portable assessment skill: all paginated open/closed issues, PR exclusion, acceptance as evidence, honest attribution and cross-issue minimal proposals. Local reader/carrier sensitivity preserves proposed/no-change versus delivered-only addressed; no scanner/ledger/self-edit.
  - **Check**: REQUIRED commands appear only in `T015.checks` in tasks.json; run after this outcome and report actual results.

- [ ] T016 Retire specified behavioral machinery and active mandates
  - **Depends**: T001
  - **Paths/context**: `evaluations/README.md`, `evaluations/review-necessity/packet.md`, `evaluations/review-necessity/expectations.md`; complete owned paths/support in `T016.owned_paths`.
  - **Acceptance/context**: After exact amendment approval, remove only four evaluation documents, RPC driver/loader/driver-only tests and active mandatory run directions. Keep historical NOT RUN evidence and useful static/runtime/security checks; no synthetic replacement or monitor deletion.
  - **Check**: REQUIRED commands appear only in `T016.checks` in tasks.json; run after this outcome and report actual results.
  - **Manual gate**: Exact behavioral-retirement amendment approval. Full consumed question in tasks.json.

- [ ] T017 Verify the retained local application composition
  - **Depends**: T003, T013, T014, T015, T016
  - **Paths/context**: `runtime/tests/test_graph_execution.py`, `runtime/tests/test_graph_questions.py`, `runtime/tests/test_graph_concurrency.py`; complete owned paths/support in `T017.owned_paths`.
  - **Acceptance/context**: Integrate the completed local application and fix only causal cross-seam wiring/docs defects. Full retained checks observe reply/recovery/wave/privacy composition; preserve actual checkpoint review and fresh-session Paseo activation handoff, not live/model claims.
  - **Check**: REQUIRED commands appear only in `T017.checks` in tasks.json; run after this outcome and report actual results.

- [ ] T018 Verify real issue delivery and exact-revision acceptance
  - **Depends**: T017
  - **Paths/context**: No repository mutation; selected issue/chat/live observation only.
  - **Acceptance/context**: Use an authorized selected issue and independently reviewed revision for actual dual publication, real correction, refreshed SHA, actual acceptance and authorized closure/readback. No implied #44 closure or acceptance of unfinished work; missing authority blocks this live outcome only.
  - **Check**: No deterministic shell command is configured; the real manual observation above is REQUIRED.
  - **Manual gate**: Selected tracker operations plus actual owner feedback/acceptance. Full consumed question in tasks.json.

- [ ] T019 Verify real manual assessment evidence and label transitions
  - **Depends**: T017
  - **Paths/context**: No repository mutation; selected issue/chat/live observation only.
  - **Acceptance/context**: Manually assess a representative selected paginated issue set with real authorized label/comment readback. Observe grouped proposals, evidence gaps and delivered-only addressed; approval of a proposal is not delivery, incomplete effects remain partial.
  - **Check**: No deterministic shell command is configured; the real manual observation above is REQUIRED.
  - **Manual gate**: Selected assessment reads/label/comment operations; actual delivery evidence before addressed. Full consumed question in tasks.json.

- [ ] T020 Observe real LangSmith replacement visibility
  - **Depends**: T017
  - **Paths/context**: No repository mutation; selected issue/chat/live observation only.
  - **Acceptance/context**: After same-revision local privacy proof and explicit account/project/region/access/pricing/network authority, observe a real permitted graph/Pi invocation in LangSmith UI. Usable hierarchy and safe known/unknown metadata, not HTTP/offline success, release removal.
  - **Check**: No deterministic shell command is configured; the real manual observation above is REQUIRED.
  - **Manual gate**: Selected LangSmith account/project/region/access/pricing/upload authority and actual Pi-call scope. Full consumed question in tasks.json.

- [ ] T021 Retire only redundant monitor source after observed replacement
  - **Depends**: T020
  - **Paths/context**: `workflow_monitor`, `runtime/coherence_workflow/monitoring.py`, `runtime/coherence_workflow/store.py`; complete owned paths/support in `T021.owned_paths`.
  - **Acceptance/context**: Only after observed replacement, remove redundant monitor source/recorders/dependencies and inspect actual callers. Preserve monitor README/history/mockups, old data/tables, useful metrics/readers and unresolved limitations; no service-stop/data deletion/migration.
  - **Check**: REQUIRED commands appear only in `T021.checks` in tasks.json; run after this outcome and report actual results.
  - **Manual gate**: Observed same-revision usable live replacement, not an offline substitute. Full consumed question in tasks.json.

## Minimal executable intake

JSON uses current tasks/id/outcome/depends plus optional owned_paths/context/acceptance/checks/gates/delivery_issue. Startup checks only readable input, parsed list, ID/work description, uniqueness, existing references and acyclic dependencies. File order/numbering is not authority. No new launch/schema prerequisite.

## Verification and review

Validate both presentations with installed task-order script and JSON with current CLI read-only intake. Inspect source coverage, real producer dependencies, owned paths, links and executable check/gate consumption. Implementation runs actual task checks plus semantic/manual acceptance. No optional hardening matrix or universal startup protocol.

Coverage: FR-001–002 → T002/T011/T018; FR-003–004 → T003/T018; FR-005–008 → T001/T004–T013/T017; FR-009–010 → T014/T020; FR-011 → T020/T021; FR-012–014 → T015/T019; FR-015 → T016/T017; FR-016 → T001/T003/T016 approval gates. SC-001 → T002/T003/T018; SC-002 → T005–T011/T017; SC-003 → T012/T013/T017; SC-004 → T014/T020/T021; SC-005 → T015/T019; SC-006 → T016/T017; SC-007 → applicable authority/checkpoint/review boundaries T001–T017.

T017 is final local integration, not a waiver for gated live criteria. Normal fresh independent full-range review covers actual delivered checkpoints and honest outstanding gates before executive presentation. Changed global skills/extensions in Paseo require a fresh-session handoff verifying checkout/revision/current approval/loaded capability; never owner reload or automatic restart. Task preparation does not launch implementation. Independent review and final owner approval remain outside production.
