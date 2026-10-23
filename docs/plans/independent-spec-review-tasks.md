# Independent specification review — implementation tasks

## Source and executable handoff

Requirements: [TinySpec](independent-spec-review-tinyspec.md) at
`cb892bb9add2b02a46e788e8cc13c5d54164139f`, read in full using the installed
`task-generation` direct TinySpec adapter. No Standard plan or downstream SDD
requirements input is introduced. [Executable JSON](independent-spec-review-tasks.json)
owns the exact work instructions, owned paths and task-local REQUIRED checks.

### Approval record

Owner selected TinySpec through `ask_user` and authorized task preparation. On
2026-10-23, after the parent presented the source/scope, each ordered T001–T003 outcome,
exclusions, review results and limitations, the owner answered **“Approve planning-only
handoff”** through `ask_user`. This approves the source and task scope below for handoff,
**not implementation or live feature evaluation**. The next operation is this final
planning handoff, then stop; do not launch the coordinator.

Approved content at `d36bbf060f1f6db091a6adab9ff42c415e6a2a44`:

- `independent-spec-review-tinyspec.md`: SHA256
  `0a182750336b9c295c366f02f3feb6202200a817748511179bd2de9a1a2bc769`.
- `independent-spec-review-tasks.json`: SHA256
  `fcac751add6868ee1b6af673900ca0832ee32ffce5c2dd8864d63ec700397ddc`.
- This human presentation before adding this approval record: SHA256
  `9e5b5d02593dbeb2baf28b277ba9c1aa124dfc969833145173a9cca242d4f223`.
  Only this approval section changed afterward; executable instructions, outcomes,
  dependencies and acceptance remain unchanged. Git preserves the compared bytes.

Parent review passed source A–E coverage, task boundaries/dependencies, owned-path
sequencing, accepted ADR constraints, neutral executable instructions and preservation
of existing approvals/TinySpec/late review. JSON and Markdown dependency validators,
actual runner read-only intake, local linked-file existence and `git diff --check`
passed. Feature regression/live behavioral checks were NOT RUN; historical known-gap
pair remains NOT VERIFIED. These are future implementation acceptance, not claims of
feature completion. No live feature evaluation ran during preparation.

Keep this temporary planning-only boundary in approval/handoff context, not executable
task descriptions or check permissions. Later implementation needs explicit scoped
launch authority and the selected configuration, original review/acceptance requirements
and actual capability/manual gates; this approval does not supply launch authority.

## Shared implementation context

- Producer read selected **`.pi/workflow-executor.json`** before decomposition:
  Terra/medium workers, Sol 6.1/medium fresh reviewers. Keep that selected path unchanged;
  these are runtime settings, not planner-assignment bindings or task eligibility metadata.
  The saved `tinyspec-tasks` producer assignment is separate and unchanged.
- Each worker/reviewer brief carries applicable source A–E, its local REQUIRED checks,
  exact owned paths, predecessor interfaces and shared exclusions from JSON. Three
  bounded outcomes separate prompt/routing, Standard dialogue/release/recovery and managed
  entry compatibility. Tests and lockstep documentation stay with each delivered concern.
  Shared checker/test/guide edits are sequential and preserve predecessor work.
- [ADR-0003](../decisions/ADR-0003-current-launch-authority-and-neutral-tasks.md),
  Decision/Consequences → existing runner supplies current scoped authority; executable
  tasks/check permissions stay authorization-neutral. T002 preservation checks inspect
  neutral task authoring and approval-record-only phase status; T003 preserves them.
- [ADR-0004](../decisions/ADR-0004-shared-routine-worker-permissions.md),
  Decision/Consequences → routine scoped fixes and small isolated tests/fixtures/local
  databases need no repeated approval. T002/T003 REQUIRED preservation includes bounded
  resource use, unrelated-data/services and credential protection, global-install,
  deployment/push and separately chargeable/external-action boundaries. Ordinary model
  tokens need no extra financial gate; real product answers/spec approvals remain actual
  owner gates, not simulated consent.
- Verified project association: [memory/MEMORY.md](../../memory/MEMORY.md), whole index
  read; Parent-turn notifications is the only matching entry. Carry its no-routine-parent-
  acknowledgment outcome into T002 transitions and T003 preservation. No memory/STATE writes.
- Preserve TinySpec, required ordinary clarification, later independent `overall_review`,
  both existing Standard approvals/current-content renewals and source-producer correction.
  No new framework, role, skill, hook, runtime/orchestration, default loop, extra approval,
  assignment rebinding or historical migration. Resolver/helper/installer/executor stay
  unchanged; source-proposed exact implementation owners are the JSON owned-path union.
- Known instruction wiring uses permanent focused existing checks, not a prototype.
  Main uncertainty is actual reviewer selectivity and parent/producer obedience. A–D must
  run at T002's first usable core boundary with exact usable reviewer, `ask_user` and
  producer capabilities. Static checks prove sensitivity only. Missing live evidence is
  NOT RUN/UNAVAILABLE and cannot release behavioral acceptance. Failed/inconclusive
  observations block reliance and use existing correction/review/renewal, never weakened
  acceptance or blind retries. Keep expected gaps evaluator-private; authored fixtures
  are valid, alleged historical omissions remain **NOT VERIFIED** without a verified pair.
- Changed global activation in Paseo needs a fresh-session handoff verifying checkout,
  revision, current approval and loaded capabilities; no `/reload`, automatic restart or
  real installation/symlink edits.

## Dependency-ordered outcomes

- [ ] T001 Deliver the canonical skeptical review prompt and saved operation routing contract.
  - **Depends**: none
  - Own the new `skills/planner/references/spec-review.md`, assignment JSON/reference,
    focused existing test module and regression guide. `standard-spec-review` references
    existing `standard-review`; assignment values and generic resolver are unchanged.
  - Verify prompt selectivity/independence/no-write constraints and actual generic resolution
    using extended `OwnerAssignmentConfigTests`; inspect exact config diff. No stage work.
- [ ] T002 Integrate distinct Standard review, owner questions, producer correction and existing approval/recovery; prove actual A–D.
  - **Depends**: T001
  - Own planner/recovery contracts, existing checker/test module and regression guide.
    Consume T001 prompt/operation; relocate existing specification approval after review
    and answer incorporation, preserving later stages and earliest-invalid recovery.
  - Local E checks cover operational-stage deletion/fold/order/bypass, fresh/read-only exact
    routing, correction ownership, no loops/duplicate clarification and preservation.
    Actual bounded A/B/C and D runs observe real answers, producer changes/Q&A,
    no reviewer spec mutation, approval-before-plan, zero and material-cancellation behavior.
- [ ] T003 Close managed SpecKit shortcuts and verify/document composed entry compatibility and packaging.
  - **Depends**: T002
  - Own only the three source-listed SpecKit prompts, README, active SDD lifecycle owner,
    existing checker/test module and regression guide. No helper/resolver/install changes.
  - Narrow managed returns/plan gate preserve vendor taxonomy/hooks/customization; raw
    standalone remains outside planner's independent-review guarantee. Existing isolated
    link/install fixtures prove the canonical prompt ships; composed E checks preserve all
    earlier behavior. Reuse applicable actual T002 evidence, rerun only invalidated boundary
    observations; do not accept A–D on static-only evidence.

Graph: `T001 → T002 → T003`. No implicit downstream producer is needed to finish T001;
T002's actual core boundary is usable before entry-point documentation. T003 tests the
final managed shortcuts and packaging, not a generic report stage.

## Acceptance and verification map

| Source | Earliest required observable / task | Evidence and limits |
| --- | --- | --- |
| A | T002 telemetry purpose question; owner answer changes relevant outcomes/scenarios/acceptance via producer | Actual bounded authored case, not additional metrics or static prompt matching |
| B | T002 batch per-item failure alternatives and observable consequences | Actual abort/partial-continue/retry decision question, not prescribed mechanism |
| C | T001 prompt contract; T002 actual sufficient/context-answered cases | Explicit zero or ≤5 unresolved impact-ranked concrete scenario/assumption/consequence/questions; no quotas/generic or gratuitous requirements |
| D | T002 fresh exact bounded context, no producer rationale/transcript; unchanged spec during review; one-at-time actual answers → producer spec/Q&A → inspection → existing approval → plan | Actual input/session/spec comparisons and order; zero skips question-only interaction, material cancellation prevents plan release; missing capability cannot pass |
| E | T001 routing/prompt; T002 stage/approval/correction/recovery; T003 managed entries/composed packaging | Existing checker, meaningful mutations, traces, isolated links and manual diff/behavior comparison; stage deletion fails even if summaries remain; preservation and ADR constraints are local REQUIRED checks |

JSON REQUIRED `check` values use the inspected runner's existing argv support in
`runtime/coherence_workflow/verification.py`; live/manual acceptance is in outcomes,
not invented shell commands or pre-worker approval gates. Existing `gates` run before
workers and cannot establish a post-change behavioral result, so none are invented.
The consuming `intake.load_contract` retains optional context/owned paths/REQUIRED items
and applies only its six ordinary identity/dependency checks. Task-order validation is
syntax/graph evidence, not behavioral acceptance. Each task runs `git diff --check`;
T002/T003 run `python3 scripts/check-planner-workflow.py` and
`python3 scripts/test-planner-workflow.py`. The regression guide records actual results,
limits and evidence applicability without a new harness or durable feature-review store.
