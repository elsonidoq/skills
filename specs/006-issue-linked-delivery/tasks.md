# Tasks: Issue-linked delivery and manual skill assessment

**Sources:** [spec.md](spec.md), [plan.md](plan.md), [research.md](research.md),
[data model](data-model.md), [interfaces](contracts/interfaces.md), [quickstart](quickstart.md).
**Executable handoff:** [tasks.json](tasks.json) holds each task's complete scope, owned paths,
acceptance and REQUIRED commands. This file is the brief human presentation of the same graph.

## Shared context

- Current scoped implementation authority is recorded under [Current implementation approval](#current-implementation-approval); prior preparation-only status is historical, not a prohibition on the approved task scope.
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
- Fixed outcomes: Python LangGraph/Pi/local Phoenix, one execution controller, standard persistence/
  interrupt/fanout/reduction, safe effect reconciliation and answer delivery, explicitly directed
  parallelism, exact ownership/checkpoints/history, metadata-only local privacy and observed useful incremental UI
  visibility during an evolving run before monitor removal. [Requirements versus proposed mechanisms](plan.md#requirements-versus-proposed-mechanisms)
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
- Only T019 selected tracker operations remain in executable `gates`. Ordinary future local
  Phoenix setup/export uses scoped implementation authority, not a cloud-account/pricing/upload
  or local-confirmation ceremony. New actual external/paid/security/data effects keep their gates.
  T020 must prove useful incremental local UI visibility; T021 inspects that applicable success
  without recertification. Missing/invalidated proof still forbids removal. Missing gates block
  affected work only; the current sequential runner does not automatically skip blocked tasks.
  No installation, image pull, service launch or export is established by planning evidence.
- Monitoring is metadata-only even locally, opt-in, and only to explicit numeric-loopback Phoenix;
  disable UI analytics/external resources and ambient hosted export. Disabled monitoring makes
  zero monitoring requests; enabled loopback HTTP is expected. Existing Pi/provider traffic is
  separate, not a whole-process ban. LangSmith may remain transitive, never a hosted monitoring
  destination. T014 owns adapter/config/[wire controls](research.md#metadata-only-local-phoenix-submission) and
  [wire checks](quickstart.md#trace-privacy-before-real-metadata-export); T020 owns actual image/setup,
  server/browser incidental-network and evolving-run UI proof. No custom UI, heartbeat framework
  or new service manager. Ordinary equivalent mechanisms remain permitted with the same proof.
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

#### Issue #44 final owner skill-diff DoD gate

[FR-017](spec.md#functional-requirements)/[SC-008](spec.md#measurable-outcomes) and the
[issue-local final skill-diff contract](contracts/interfaces.md#issue-44-final-skill-diff-gate)
apply once at the existing final delivery review, after implementation, specified checks and
fresh independent technical review. Show the owner the **complete actual combined net patch**
through normal chat/host diff presentation, not just paths, links or a summary. Include every
actual task-attributed addition/deletion/modification to the eight existing and one new skill
instructions and their task-authorized coupled references/scripts/tests. Contributions are:
T001 coordinate-implementation; T002 planner/task-generation/tiny-spec; T003 finish-session/
track-open-issue; T015 new assess-skill-improvements; T016 planner/requesting-code-review/
receiving-code-review. Combine overlapping contributions, not five separate approval exercises.

Identify exact baseline, reviewed commit, attributed paths and contributing task/repair commits;
inspect attribution and exclude unrelated/concurrent work rather than claim a blind range.
Present the patch with normal delivery evidence even while approval is pending, marked
“awaiting owner skill-diff approval”. Record the actual explicit owner response and patch
identity in existing issue/chat under actual tracker authority/readback. Plan approval, green
checks and agent review never imply this owner approval. Missing approval keeps this issue's
delivery DoD/completion/acceptance and closure pending, while verified task checkpoints,
technical review and internal runtime completion may finish first; no worker failure solely
because this final gate is pending. No implementation skill diff exists yet for owner approval.

Reuse precise approval for unchanged skill content; later affected skill edits renew only
affected diff approval; unrelated commits alone do not invalidate it. Skill approval
is not overall delivery acceptance or closure authority. This is #44-only user acceptance,
not a policy to insert into global/adopting-project skills. No pre-dispatch or repeated task
questions, new task/runtime state, viewer/tool, patch ledger/receipt, required patch file or
fixture that simulates owner response. Existing natural feedback and NOT VERIFIED rules remain.

#### Issue #44 human-verifiable functional evidence

[FR-018](spec.md#functional-requirements)/[SC-009](spec.md#measurable-outcomes) and the
[canonical functional-evidence contract](contracts/interfaces.md#issue-44-functional-evidence)
require one small actual non-skill evidence package alongside the combined final skill patch;
[the four guide steps](quickstart.md#human-inspectable-functional-evidence) govern delivery.
Reuse readable actual public-CLI/Git demonstrations from T011/T013 in T017: dependency execution/
checkpoints, pause/restart/actual reply consumption, explicitly authorized parallel work/accepted
join and relevant real commits/results. Reuse actual helper checks for the other non-skill
outcomes, closing composed gaps with the smallest shared run, not separate demos or a matrix.
T019 supplies its existing bounded actual assessment results/links, not another browser scenario.

T020 requires successive actual browser-rendered local Phoenix screenshots of useful hierarchy/
progress during an evolving representative CLI run BEFORE root completion, not mockups or only
an ended trace. The coordinator verifies existing browser rendering, capture, persistence and
owner/reviewer access at that stage; a registered parent screenshot tool is not proven usable
or worker-available. Ordinary coordinator capture assistance needs no per-screenshot approval,
but missing capability is an actionable evidence gap, not browser-framework installation authority.
T021 consumes that proof, adding only changed post-removal CLI/history observations.

Resolve the project-owned durable directory once through normal coordinator setup:
`${XDG_DATA_HOME:-$HOME/.local/share}/coherence/PROJECT_KEY/evidence/issue-44/`, separate from
Phoenix data/credentials and outside disposable worktrees. The project maintainer owns access/
recovery. Retain captures/results with their generating outcome and link its actual checkpoint/
application revision, explicit persistent asset paths, actions/commands, expected/observed results,
limits and reproduction/local URL access in the existing authorized issue/chat evidence trail.
Verify assets can be opened after the session/worktree ends, not solely via /tmp or transient
attachments. Do not add outside paths to runner ownership, assume SDK UTF-8 edit claims commit
external binary screenshots, fake claims/edits or expand #28/#43. External-only capture makes no
empty/evidence-only commit; actual source/config/necessary reproduction changes retain ordinary
owned-path checkpoints. No new manifest, ledger, registry or required repository PNG copy.

Use only approved metadata; exclude sensitive paths, credentials and private prompts/responses/
errors. Disclose cropping/redaction without misrepresenting behavior; no unauthorized external
publication or shutdown/cleanup. Label SDK fixture-provider runs as local-mechanism proof, not
live model judgment; fabricate no owner reply/approval. Screenshots supplement required runtime/
privacy/security/recovery checks. Missing actual proof is NOT RUN/UNAVAILABLE/FAIL with DoD
unmet, never a pass from scheduled checks. The final owner skill-diff gate remains separate
from functional evidence, overall acceptance and closure authority. This is issue-local guidance,
not a new global skill policy; no new task, question, framework or human-response checker.

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
  - Resolve the LangGraph/saver/standard OTel compatible hashed lock without raising Python >=3.10; Phoenix server stays in its separate pinned container, needed transitive LangSmith may remain. Prove persistence reopen/interrupt/history compatibility; saver layout/API details remain proposals.

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

- [ ] T014 Deliver metadata-only local Phoenix tracing and reproducible settings
  - **Depends**: T011
  - Deliver the explicit OTel adapter with bounded runtime/phoenix.env.example and operating docs: pinned single Phoenix image/SQLite, loopback-only 6006, privacy/auth defaults and durable private data ownership/recovery. Prove final OTLP protobuf/header/destination privacy under ambient endpoints/headers/proxy and redirect, qualified usage and fail-open checks/Git; no service start. Exact controls may simplify only with equivalent proof.

- [ ] T015 Provide the manual evidence-based skill assessment entry
  - **Depends**: T001
  - Add one manual portable assessment skill: all paginated open/closed issues, PR exclusion, acceptance as evidence, honest attribution and cross-issue minimal proposals. Local reader/carrier sensitivity preserves proposed/no-change versus delivered-only addressed; no scanner/ledger/self-edit.

- [ ] T016 Retire specified behavioral machinery and active mandates
  - **Depends**: T001
  - Retire only the four evaluation docs, RPC driver/loader/driver-only tests and active mandates using exact final approval. Keep meaningful runtime/static/security checks and historical limits; no replacement suite.

- [ ] T017 Verify the retained local application composition
  - **Depends**: T003, T013, T014, T015, T016
  - Integrate local application seams, safe OTel export suppression/config checks and causal wiring/docs fixes. Actual local incremental UI visibility remains T020, not an interception-test claim. Normal fresh final review follows; no worker publication or staged owner acceptance.

- [ ] T019 Verify real manual assessment evidence and label transitions
  - **Depends**: T017
  - Assess one owner-selected real set with complete actual discovery (all pages, open/closed, no PRs or acceptance eligibility filter). Use available linked evidence honestly for grouped minimal proposals or no-change; reuse T015 for absent categories and report limits, never manufacture cases or improvements.
  - **Live gate**: Scoped tracker reads/label/comment effects with readback. Keep proposed/no-change distinct; addressed needs actual delivered evidence or remains unobserved/NOT VERIFIED. No automatic assessment, skill edit or PR.

- [ ] T020 Observe useful incremental local Phoenix replacement visibility
  - **Depends**: T017
  - After applicable final-wire proof, perform ordinary scoped single-container local setup with current collision/ownership, effective pinned-image/privacy/auth and durable storage/recovery checks. Verify actual server/browser incidental monitoring stays local. Observe useful incremental hierarchy/task/progress in an evolving actual run BEFORE root completion, recording refresh limits; no final-trace/HTTP/offline substitute.
  - **Required proof, not consent ceremony**: Retain the monitor if setup/privacy/UI visibility is inadequate; no custom UI/heartbeat framework. Reuse existing Pi-call authority; new actual external/paid/security/data effects still need their real gate. No T020 `gates` question.

- [ ] T021 Retire only redundant monitor source after observed replacement
  - **Depends**: T020
  - Inspect applicable successful T020 useful incremental local Phoenix visibility evidence from before root completion, then retire only redundant monitor source/callers. Missing/invalidated proof stops removal without recertification; retain history/data/readers/limitations, no service stop.

## Coverage and handoff

FR-001–002 → T002/T011 and normal coordinator delivery; FR-003–004 → T003 and normal
coordinator delivery; FR-005–008 → T001/T004–T013/T017; FR-009–010 → T014/T020;
FR-011 → T020/T021; FR-012–014 → T015/T019; FR-015 → T016/T017;
FR-016 → T001/T003/T016 using precise final approval evidence. SC-001 → T002/T003 plus
normal coordinator delivery; SC-002 → T005–T011/T017; SC-003 → T012/T013/T017;
SC-004 → T014/T020/T021; SC-005 → T015/T019; SC-006 → T016/T017;
SC-007 → applicable authority/checkpoint/review boundaries.
FR-017/SC-008 → T001/T002/T003/T015/T016 skill contributions plus coordinator final skill-diff
review and actual owner response, not an automatic code test.
FR-018/SC-009 → shared T011/T013/T017 CLI/Git proof, bounded T019 assessment results,
T020 coordinator-rendered evolving UI captures, T021 changed post-removal observations and
coordinator final inspection/durable access; no automatic code-test or screenshot-only claim.
T018 is removed; IDs need not be contiguous.

Validate both task presentations and current read-only intake. Internal graph interfaces precede
public cutover T011; concurrent composition is checked at T013, final local integration at T017.
Fresh independent final review covers actual delivered checkpoints and honest outstanding gates.
Changed global skills/extensions in Paseo require a fresh-session handoff verifying revision,
approval and loaded capabilities, never owner reload or automatic restart. Task production is
not final task approval or implementation acceptance.

## Current implementation approval

The owner selected **“Approve and start implementation”** through `ask_user` after the current-content executive brief. Approval covers the specification, plan, executable/human tasks and linked artifacts at `ac964e33e22e05909140c278856d40022f9e35bf`, including the exact operative amendments in `plan.md`. Reviewed identities: specification SHA-256 `d50625bc21530b004165baee4744d661476e0582a050334df351198551494652`, plan `ba547e055361a9de380c446df9e6ac1858b35027b48451bad2787d00eba1b895`, human tasks `753f9f036b8b97bd1c6f045b0dc5403a6721c7afc9e7acfc7d44b5e81293a806`, executable tasks `95958a03ee94c632bb4971ae0e7fceeec83d00578d45ece9c45a1c90d5edca9f`.

Both final correctness and simplicity reviews, including the targeted Phoenix and FR-017/FR-018 follow-ups, returned zero remaining findings. Dependency validators, read-only intake and whitespace checks passed. The known pre-existing static capitalization failure remains a required T001 correction; runtime behavior, actual captures and final skill-diff approval were not demonstrated by planning.

Authority starts sequential coordinator preflight and execution with `/home/dev/.paseo/worktrees/0zfm1a0e/boring-eel/.pi/workflow-executor.json` unchanged: Terra/medium workers, explicit Sol/medium implementation fallback and fresh Sol/medium reviewers. It includes the scoped implementation, exact operative amendments, ordinary local dependency setup and Phoenix setup/export/capture when the applicable tasks and privacy prerequisites are reached. Initial, corrective and resumed work consume this approval for unchanged scope without repeat policy questions.

The actual T019 tracker-operation gate and genuine introduced external/paid/security/data boundaries remain. No cloud monitoring, push, PR, unrelated service shutdown or retained-data deletion is authorized. Changed global capabilities require the existing fresh Paseo-session handoff before affected reliance, not automatic reload/restart. DoD remains pending until actual required functional evidence and explicit owner approval of the complete actual skill diff; that skill approval is separate from overall delivery acceptance and closure authority.

Only status, this approval record and its shared-context link were added after the approved snapshot; requirements, task outcomes, dependencies, owned paths, checks, gates and the exact operative amendments are unchanged. The executable task input remains byte-identical. This record is not approval of unseen implementation or a claim of delivered acceptance.
