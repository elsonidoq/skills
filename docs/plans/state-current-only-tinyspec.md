# STATE current-only concurrent lifecycle — TinySpec

## Context and authority

Owner-selected TinySpec preparation; **planning only**, not implementation authorization.
Owner request (verbatim):

> the skill /skill:finish-session must use STATE to track the *CURRENT* state. It must never become a log. So every entry there reflects a CONCURRENT work being done. Usually the skill /skill:finish-session changes the state of things that are in the state. For instance, when a spec is finished from /skill:planner, finish-session should remove that sepc state from STATE.md

Outcome: a fresh agent or owner sees only work still current across concurrent activities,
not a completed-session record disguised as a snapshot. Finished planner specification
work disappears from STATE; the source, tasks, approvals and evidence remain in their
authoritative owners. Separate tasks and combined source/task review and owner approval
are still required before execution.

Governing constraints: [AGENTS](../../AGENTS.md), [constitution principles I–VI](../../.specify/memory/constitution.md),
[documentation routing](../index.md), [TinySpec](../../skills/tiny-spec/SKILL.md),
[checkpoint contract](../../skills/memory-handling/references/task-commit-contract.md),
[coordination evidence](https://github.com/elsonidoq/skills/blob/5088b25877467887dd41c9547197c6da43b3c165/skills/memory-handling/references/project-coordination.md).
Verified project gotcha store: [memory index](../../memory/MEMORY.md), no recorded gotchas.
[Coordination guidelines](https://github.com/elsonidoq/skills/blob/5088b25877467887dd41c9547197c6da43b3c165/memory/coordination/GUIDELINES.md) contain no approved guidance;
required files exist, so initialization is unnecessary. No historical evidence intake is needed.
Factual run owner: `memory/coordination/evidence/2026-10-08-state-current-only/SUMMARY.md`.

## Evidence and decisions

All lifecycle decisions below are owner-settled or repository-derived, not external-library
recommendations. Supporting spans and observable consequences:

| Inspected local evidence | Constraint derived from owner request | Observable |
| --- | --- | --- |
| [finish-session](../../skills/finish-session/SKILL.md), Core Invariant 7 and Step 6: no completed summaries, but explicitly replaces progress with “concise terminal disposition” | Remove the verified finished attributable item, not replace it with accepted/completed status | A1, A2 |
| [coordinator](../../skills/coordinate-implementation/SKILL.md#brief-current-state-and-recovery), write-boundary table, Writes and checkpoint ordering, and Finish: three terminal-disposition directions | Align producer, checkpoints and closeout with the same removal lifecycle | A1, A5 |
| [state fixture](../../skills/coordinate-implementation/scripts/test_state_contract.py), GUARDS persistence, consumer assertions, walkthrough and `test_completion_closeout_replaces_without_history` require terminal content | Replace conflicting assertions; make retention/deletion failures observable in the existing fixture | A1–A4 |
| [README Brief current state](../../README.md#brief-current-state) explicitly retains terminal disposition; [REQUIREMENTS Brief current-state contract](../../REQUIREMENTS.md#brief-current-state-contract) describes shared lifecycle | Correct the README contradiction; align other active references only when genuinely needed | A5 |
| [initialize-coherence](../../skills/initialize-coherence/SKILL.md), State adoption paragraph links current-truth lifecycle; [finish-session-jev](../../skills/finish-session-jev/SKILL.md) requires the complete base workflow | Preserve inherited lifecycle, custom content and no fabricated progress; no independent schema or Jev decision about deletion | A3, A5 |
| Root [STATE](../../STATE.md) at planning baseline records a previous independently accepted run, no active children/blockers and `/reload` next | Motivating example of completed work retained as state; not authority to clean it during planning | A2, A6 |

Baseline state fixture: `python3 -B skills/coordinate-implementation/scripts/test_state_contract.py`
passes 15 tests on the existing terminal-retention contract. This is evidence of the old
assertion, not evidence that the requested behavior is implemented.

Settled semantics:

- Current means genuinely active, paused, blocked, or pending review/acceptance/owner gate.
  A pause or session end is not completion. Change such an item's current status in place.
- Remove an item only after its completion and ownership are verified against applicable
  artifacts, Git/checkpoints and runtime evidence. Unknown status, partial work, running or
  unobserved children, missing acceptance proof or ambiguous ownership cannot imply deletion.
- Preserve every unrelated concurrent item and custom header/content. Removal is bounded to
  an understood attributable current block/item; never clear the whole file as a shortcut.
- A finished planner spec is removed when its planning work is genuinely finished; pending
  planner approval/review is still current. Implementation is not automatically created as
  its replacement. A genuinely active authorized successor is a distinct current item.
- If no current items remain, a header-only/empty-current-content snapshot is valid under the
  project's existing format. Do not add a terminal record, idle-history placeholder or next
  action solely to keep completed work visible. Do not delete the file or its custom structure.
- Durable source/task/approval, Git, coordination evidence and unresolved-work owners remain
  authoritative. Current retained items may link them briefly; finished entries do not survive
  just to retain links. No migration of arbitrary historical content is authorized.

## Scope and approach

Included production seam: finish-session invariant/Step 6 and coordinator Brief Current State
and Recovery table/checkpoint wording/Finish. Update the existing state fixture in lockstep.
Correct README's active terminal-retention wording; proportionately inspect REQUIREMENTS,
initialize-coherence, finish-session-jev, AGENTS, docs/index and shared checkpoint/coordination
references for direct lifecycle contradictions. Leave already-compatible text unchanged;
necessary consumer clarification is bounded to this lifecycle, not a policy rewrite.
Historical plans/reviews/run evidence remain historical; no broad audit or cleanup.

The smallest coherent implementation shape is coupled operational wording + focused fixture
+ necessary active documentation alignment, independently verifiable as one implementation
unit if task generation confirms that boundary. This is not an implementation task checklist
or a task quota; separate task generation owns work-unit contracts, and coordinator owns
implementation routing. No implementation profile is assigned here.

Producer → consumers → production validation: coordinator shared lifecycle is the owner;
finish-session consumes it to reconcile the same project-owned snapshot; initialization and
Jev inherit it, and README/REQUIREMENTS explain it. Inspect carrying sections together and
run the focused fixture after integration. Preserve ordered recovery, ownership/drift stops,
active child reconciliation, no duplicate dispatch, safe write boundaries, immediate child-ID
capture/deferred commit, coalescing and unchanged-status skip. Keep worker paths free of STATE
writes and preserve every existing per-task commit and distinct evidence-only checkpoint.
Terminal outcomes/reflection belong in the run evidence, not STATE; an ongoing review gate
remains current until independently resolved.

During later **authorized** execution/closeout, apply the lifecycle only to understood current
blocks with verified provenance and exclusive write ownership. Reconcile the then-current
root STATE before deciding any attributable removal; this source does not prescribe wholesale
cleanup of the previous run or migrate arbitrary history. Dirty overlap/concurrent drift,
unverified runtime or ownership stops affected writes. Use the existing format, no fixed global
schema, new tracker, persistence engine, compaction hook or runtime changes. Ordinary Git
correction with renewed approval where necessary is the rollback route; never erase unrelated
state or checkpoint history to recover.

Excluded now: skill/test/runtime/STATE implementation writes, task production, pushes,
deployment, installation, live provider/agent exercises, guideline changes and delegation.
Future implementation excludes those external/runtime/guideline operations unless separately
authorized. Future global skill changes require telling the owner to run `/reload` in pi.

## Acceptance and verification contract

These source criteria must become stable task-local **REQUIRED** references, preserving each
pass criterion, smallest sufficient check, evidence and gate below. No optional check can
replace them. An unrun/unavailable REQUIRED check is NOT VERIFIED; affected acceptance stops.

| ID | REQUIRED pass criterion | Smallest sufficient check / expected evidence | Gates |
| --- | --- | --- | --- |
| A1 | Operational producer and closeout remove verified finished items rather than retain terminal disposition; active progress still updates in place | Section-bound instruction assertions and targeted negative mutation reject missing removal rule or restored terminal-retention instruction; focused fixture PASS and bounded changed-carrier diff inspection | Approved source/tasks and owned paths before writes |
| A2 | A finished planner spec disappears, durable artifact bytes remain unchanged, and no implementation successor is fabricated | Existing state fixture gains a symbolic finished-spec closeout scenario with absent spec item, unchanged source/tasks/evidence and no synthetic successor; representative distinct active successor remains only when independently current | Planning completion/approval evidence; no live obedience claim |
| A3 | Closing one finished item preserves unrelated concurrent work/custom structure; genuinely paused, blocked and review/acceptance-pending work remains; unknown runtime/ownership cannot trigger deletion | Focused mixed-current-item scenario plus gated/unknown retention cases in the same fixture; compare preserved bytes and named stop/retain outcomes, including running child and ownership/drift protections | Runtime/ownership evidence or precise stop; no destructive guess |
| A4 | No current work yields no completed entry; repeated closeout is byte-identical and produces no extra checkpoint | Header/empty-current-content and repeat-closeout scenario in existing fixture; assert no terminal/idle-history record, no duplicated content or new commit when unchanged | Existing format/custom structure preserved |
| A5 | Active producers/consumers do not contradict removal; recovery, cadence, worker checkpoints and independent review gates remain intact | Bounded carrier/reference inventory and changed local-link/anchor check; run `python3 -B skills/coordinate-implementation/scripts/test_state_contract.py` and `python3 -B -m unittest discover -s skills/coordinate-implementation/scripts -p 'test_*_contract.py'`; PASS output and actual diff review | No broad audit, framework or live calls; final independent implementation review remains mandatory |
| A6 | Any actual STATE application is limited to verified understood current items at authorized closeout, preserving unrelated work; no historical migration or fabricated authority | Manual before/after attributable block review against Git/artifact/runtime evidence; path-limited implementation and evidence commits inspected, or explicit no-change disposition where application is not authorized/needed | Exclusive writer/dirty-overlap permission, required verification and approval; unknowns block deletion |

Fixture scenarios are symbolic walkthroughs and offline instruction/mutation checks. Existing
Git fixtures demonstrate scoped persistence and idempotence, **not live model obedience**.
No new test framework or live provider exercise is required. Broader suite checks are only
necessary if an actual changed assertion/carrier dependency demonstrates the need; avoid an
exhaustive matrix unrelated to this seam. Source/task approval, mandatory verified task/evidence
commits and final independent implementation review are unchanged, not waived by fixture PASS.

## Risk reduction, dependencies and limits

No isolated technical prototype is selected: this is a bounded instruction lifecycle, not a
hard executable dependency core. Inspection resolves local contradictions; the smallest focused
fixture detects regression at the carrying sections and representative/adversarial closeout seam.
There is no disposable proof artifact requiring production consumption/cleanup: the retained
state fixture is the production regression owner, consumed by all changed contract carriers'
integration review before closeout. Retain existing evidence and tests; no cleanup phase is needed.
Failure or disproof blocks reliance, returns to the producing contract/approval gate and renews
affected approval instead of weakening criteria or blindly retrying.

External research is skipped under the [dependency research contract](../../skills/planner/references/dependency-research.md):
local text-only change with no dependency/version decision, new API or installation. Existing
runtime requirements remain untouched; no SpecKit prerequisite for TinySpec. Both that reference
and [early risk reduction](../../skills/planner/references/early-risk-reduction.md) are readable.
The non-isolatable residual risk is model obedience: static/symbolic success cannot guarantee
real-session selective removal. That limit is explicitly retained, with no live-validation claim
or new mandatory live exercise. Material execution evidence gaps stop acceptance/deletion under
existing gates; none is silently deferred. No unresolved scope choice or separate owner deferral.

Planning profile approved for all planning stages: `openai-codex/gpt-6.1-sol:medium`.
Family rationale: consistency across coupled instruction carriers; effort rationale: bounded
inference. Six-factor assessment: low settled residual reasoning, modest tooling, shared-contract
coupling, behavioral-obedience blind spot, reversible local texts, no approved project guidance.
Selection is not observation; exact observations belong in factual run evidence.
