# Tasks: Lean Workflow Corrections

**Input**: [Approved specification](spec.md), exact approval in [spec-approval.md](spec-approval.md). [Plan](plan.md) supplies derived sequencing, not new requirements; [research](research.md), [state model](data-model.md), [interfaces](contracts/README.md) and [validation guide](quickstart.md) supply technical context.
**Executable task input**: [tasks.json](tasks.json). Task-local `required` entries contain REQUIRED observables, smallest checks, evidence and action-specific gates; deterministic authored commands occupy `required[].check`, not merely prose. Human summaries below do not replace that executable context.

## Shared worker context

Every task description instructs its worker to read this section. Read the applicable spec story/FR/V item and linked technical evidence, then its complete JSON entry. Preserve [parsimony](../../skills/planner/references/parsimony.md), [early-risk contract](../../skills/planner/references/early-risk-reduction.md), [task semantics](../../skills/task-generation/SKILL.md) and [focused task checkpoints](../../skills/memory-handling/references/task-commit-contract.md). No separate prototype is justified: bounded known seams use permanent existing Engine/Git/flow fixtures; V3/V4 retain their supported composed demonstrations. Tests, operative documentation, actual evidence and routine teardown belong with each outcome, not proof/report/cleanup tasks.

- **Authority and accepted decisions**: Before affected work, read the whole [decision index](../../docs/decisions/index.md) and applicable accepted records in full. [ADR-0003](../../docs/decisions/ADR-0003-current-launch-authority-and-neutral-tasks.md) requires current launch authority over historical phase labels and authorization-neutral executable work. Returned transport is not acceptance; that ADR did not fix false completion. [ADR-0004](../../docs/decisions/ADR-0004-shared-routine-worker-permissions.md) requires existing shared `_ROUTINE_AUTHORITY`: ordinary scoped fixes, small isolated fixtures/databases/local servers, necessary local/in-project setup and current-task artifact lifecycle without renewed routine consent. No new permission service/schema or universal resource/spending ceilings. Unknown bytes are not adopted/deleted, except T008's specifically identified explicitly authorized transfer. Carry these applicable outcomes/source links into worker and independent review briefs, not merely an intake link.
- **Owner guidance**: [whole memory index and inline guidance](../../memory/MEMORY.md): handle routine technical decisions autonomously; ask only for product decisions/material scope creep while preserving mandatory explicit permission gates. Correction-only review assesses changed affected behavior, not already-confirmed unaffected areas. Routine transitions need no parent acknowledgment. No memory/STATE/ledger/report scaffolding writes.
- **Lean scope**: FR-013–014 and all spec exclusions apply. This is a lean first iteration, **not a cross-layer workflow redesign**. No startup/admission additions beyond the existing six intake rules; no cancellation/recovery subsystem, migration/history rewrite, registry/catalogue/receipt, permission ledger, budget/quota/timer/universal cap, broad cleanup or general framework. No extra runtime model calls for #23/#24/#27/#28; #25 scoped repair delegation and #26 separate independent reviewer remain required. No historical application repair/restart, production/deploy/index rebuild, paid application calls, auth/global changes, unapproved requirement/policy amendments or acceptance relaxation is implied.
- **Ownership and executor**: selected absolute configuration was read at `/home/dev/.paseo/worktrees/0zfm1a0e/tasty-quail/.pi/workflow-executor.json`: `openai-codex/gpt-5.6-terra` worker, medium; `openai-codex/gpt-6.1-sol` reviewer, medium. Preserve this exact path downstream; runtime config controls assignments, not the planning producer. Each outcome bounds one behavior for that worker/effort, including its tests/docs/debugging. Listed `owned_paths` are mutation limits, not mandates to edit every layer or authority to adopt pre-existing content. Inspect causal paths first; coordinate shared-file overlap. Shared-file overlap is not a producer dependency. AGENTS' owner-authorized concurrency direction supersedes older blanket sole-writer wording; preserve actual locks and coordinate overlapping paths.
- **Verification and checkpoint**: run actual task-specified commands from repository root through the existing consumer; commands in JSON are executable argv lists. Record actual command/exit/output. Required nonzero/unrun results remain unmet. Keep semantic criteria semantic; no shell compiler or universal command requirement. Additional deterministic required commands selected during delivery must also use existing executable check fields through the applicable task-contract correction gate, never prose-only handoff. Relevant focused changed-seam checks suffice; quickstart's broader candidate suites are not universally mandatory. Preserve known baseline failures separately, never weaken assertions. The runner inspects real owned diffs, checks/manual gates and focused owned-path checkpoint before subsequent mutation; workers do not stage/commit or delegate. Genuine completed no-change work creates no empty commit. Preserve unrelated dirty/staged work, hooks/signing and actual history. Final fresh independent read-only review remains required; no self-review claim.
- **Evidence and feasibility**: every V item reports tested revision/environment and actual versus simulated actors. Offline Engine/Git fixtures suffice for V1/V5/V6. V2 handoff/text coverage is not model obedience. V3/V4 mechanical fixtures cannot establish autonomous investigation or independent reviewer judgment; their required supported behavioral demonstrations remain outstanding if authority/capability is absent. Report NOT RUN/UNAVAILABLE with concrete resumption action, block affected acceptance and do not waive it. Current applicable implementation authority and usable selected tools are necessary for actual V3 delegation/continuation. Actual V4 issue mutation additionally requires scoped target/operation authority and GitHub capability; separate reviewer needs usable selected reviewer/delegation. No forced paid/live/historical exercise or routine local-fixture reapproval. Preserve actual owner/manual/paid/security/data/external gates. Evidence applies only within tested bounds; invalidate affected proof after changed behavior and return material scope/acceptance changes through existing review/approval gates.
- **Activation**: changed global skills/prompts/tools in Paseo require a fresh-session handoff verifying checkout/revision/current approval/loaded capability, never an owner `/reload` instruction or automatic restart. Use existing conversation/runtime return for evidence, not a new handoff artifact.

## Authored commands and completion — Story 1

- [ ] T001 Preserve deterministic required commands through authoring and executable handoff.
  - **Depends**: none
  - **Paths/context**: shared task-generation and only causal TinySpec/Standard adapter/template carriers; existing planner/verification/intake fixtures. See JSON mutation limits.
  - **Acceptance/context**: FR-002–003,005 / V1-handoff. An authored command crosses actual intake/consumer, records real failing exit/output and successful control. Both adapters share guidance; optional/no-command work survives. Supplies T002's composed fixture, not Engine acceptance interpretation.
  - **Check**: JSON `required[].check` runs focused verification/intake fixtures and new `AuthoredCommandHandoffTests` in the existing planner fixture. Local offline authority; no manual gate.

- [ ] T002 Prevent unsuccessful return from becoming task success; deliver composed V1.
  - **Depends**: T001
  - **Paths/context**: actual Engine completion seam, existing engine/correction/verification fixtures and operative docs; host/resume changes only for demonstrated limitation/bypass.
  - **Acceptance/context**: FR-001–003,005 / V1. Actual Engine/disposable Git/stub adapter fail-before/pass-after for blocked/failed/incomplete no-edit and partial-edit A, delivered-answer/blocked return, actual failing authored command and known worker-reported unmet required acceptance. A incomplete; B/review/fixer absent; bytes/history retained. Required-work, no-command/no-change, optional/unconfigured and corrected-error positive controls survive. Consume T001 handoff here: first point both seams are delivered.
  - **Check**: JSON executes focused Engine, check-correction and verification fixtures. Evidence includes command exits, dispatch/state and partial Git bytes. Offline sufficient; no provider/replay gate.

## Routine scoped authority — Story 2

- [ ] T003 Reconcile causal earlier agent restriction with later actual routine-test authority.
  - **Depends**: none
  - **Paths/context**: inspect shared authority/current-launch handoffs first; change only causal instructions and corresponding authority fixture/docs.
  - **Acceptance/context**: FR-004–005 / V2. Label external #24 wording **UNVERIFIED in this repository**, scenario only. Capture later scoped authority over agent-created exact-resource/rerun demand while actual owner limits survive. Initial and only affected correction/resume handoffs covered; shared defaults, no new permission system or per-layer sweep. Text delivery is not obedience/pass evidence.
  - **Check**: executable authority fixture in JSON, source conflict comparison and captured handoffs. Local routine setup permitted; paid/manual/security/data/external boundaries retained.

## Diagnosed repair and retained continuation — Story 3

- [ ] T004 Repair diagnosed out-of-worker-path blocker, verify/checkpoint, retain unfinished continuation and answer later routine question.
  - **Depends**: none
  - **Paths/context**: coordinator contract and supported CLI/bridge/retained-session mechanisms; conditional runtime edits only after concrete supported exercise limitation.
  - **Acceptance/context**: FR-005–007 / V3. One representative sequence includes inspection/lock reconciliation, explicit repair paths/current settings, actual diff/check/SHA, unfinished continuation without completed replay or routine reapproval, then another autonomous routine question. No worker delegation, blind expensive retry or historical restart. Runtime expansion is not presumed necessary.
  - **Check**: executable existing resume, question-triage and task-checkpoint fixtures in JSON support mechanical coverage. V3 behavioral demonstration remains REQUIRED separately from those stubs/text assertions. Actual delegation/continuation needs applicable authority and loaded tools; absent means NOT RUN/UNAVAILABLE and unmet affected acceptance, not a new routine consent gate.

## One investigated and independently reviewed issue entry — Story 4

- [ ] T005 Investigate before focused issue creation/readback in existing track-open-issue.
  - **Depends**: none
  - **Paths/context**: existing skill owner and focused standard-library offline fixture; no second tracker.
  - **Acceptance/context**: FR-008–010 / V4-create. Evidence-based RCA, honest uncertainty/next investigation, create/readback; preserve exact target/auth, complete open+closed duplicates, sensitive/narrow-field/concurrent-content safeguards and unknown-outcome reconciliation. Supplies actual-body/intent/evidence interface for T006. No independent review claimed yet.
  - **Check**: JSON executes focused issue fixture; simulated calls identified. Actual remote actions require scoped target/operation authority and capability; no local fallback.

- [ ] T006 Independently review actual body, evaluate/correct actionable drift and read back; deliver composed V4.
  - **Depends**: T005
  - **Paths/context**: same existing entry/fixture; affected routing/callers only where necessary.
  - **Acceptance/context**: FR-008–010 / V4. Full RCA→create/readback→separate configured read-only actual-body intent review→evaluated actionable correction→independent readback. Review ambiguity/omissions/conflicts/promoted assumptions/scope creep/overprescription. Clean review alone insufficient. Uncertain RCA/unavailable reviewer/concurrent change remain honest; ordinary narrow correction autonomous, material outcomes return to owner. No automatic multi-round loop.
  - **Check**: composed offline fixture in executable JSON, plus required representative supported behavioral use. Scripted review is not model judgment. Actual external write/reviewer permission/capability gaps remain NOT RUN/UNAVAILABLE and block affected acceptance; neither is implied by ordinary local-test authority.

## Citation compatibility — Story 5

- [ ] T007 Admit ordinary numeric citation ranges through actual rejected-review/repair flow.
  - **Depends**: none
  - **Paths/context**: existing parser/review-chain fixture and affected interface documentation only.
  - **Acceptance/context**: FR-011 / V5. Equivalent single-line and range rejection findings reach repair unchanged; malformed JSON/type/missing-location guards survive. Syntax acceptance never approves substantive findings or rewrites history.
  - **Check**: executable actual review-chain fixture in JSON; offline sufficient, no provider/historical replay.

## Exact authorized existing-file handoff — Story 6

- [ ] T008 Preserve named authorized untracked/tracked-modified recovery files through supported input, ownership, edit and focused checkpoint.
  - **Depends**: none
  - **Paths/context**: optional existing execution input to FocusedGit lifecycle, integrated existing Git/Engine/CLI fixtures and public interface docs.
  - **Acceptance/context**: FR-012–013 / V6. Exact approved targets preserve starting bytes except intended edits; actual focused Git checkpoint includes owned result. Unrelated bytes/index remain unchanged/unstaged; unapproved target under broad allowlist refused with filename/operation/supported correction. No glob/directory adoption, fake history or permission ledger; reconcile unknown/drifted target. One coherent transfer outcome must work through real input, not helper bypass.
  - **Check**: executable Git/Engine/CLI fixtures in JSON; disposable repositories suffice. Preserve hooks/signing and safe paths. Established exact-file authorization needs no repeat consent.

## Dependencies, effort and delivery boundary

Graph edges only: **T001 → T002** (authored handoff needed for composed V1), **T005 → T006** (RCA/create/readback body needed for review/correction and composed V4). Others independent; shared Engine/docs ownership requires scheduling/coordination, not false graph edges. Current intake's ready-ID order yields T001–T008; execution follows graph, not numbering. Each runner task checkpoints before subsequent mutation. Owner-authorized concurrency still coordinates overlaps/locks.

For selected Terra/medium, T001 isolates command carrier debugging from T002 completion semantics; T005 isolates investigation/create safeguards from T006 independent review/correction. T003 is a bounded causal instruction conflict; T007 a narrow parser/flow correction. T004 and T008 retain their inseparable supported sequences with tests/docs inside rather than splitting into ceremony. T002 requires most care for negative/positive completion semantics; T004/V3 and T006/V4 have behavioral capability gates, not invented effort/time quotas. No model-family hierarchy or execution eligibility metadata.

Coverage: **V1 T001 + T002 (composed T002); V2 T003; V3 T004; V4 T005 + T006 (composed T006); V5 T007; V6 T008**. FR-013–014 apply across all outcomes. Required checks are application delivery evidence, not new startup ceremonies. Missing/failed/unrun evidence cannot release affected reliance. Final independent review and existing current-content approval gates remain unchanged; this document is authorization-neutral work, not a substitute approval record.
