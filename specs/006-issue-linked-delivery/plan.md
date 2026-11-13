# Implementation Plan: Issue-linked delivery and manual skill assessment

Apply [Parsimony and Actionable Checks](../../skills/planner/references/parsimony.md).

**Branch:** `plan-issue-44` | **Date:** 2026-11-13 | **Spec:** [spec.md](spec.md)

**Input:** Approved specification at baseline `4c1725ebded2f89dec6933b8d193bf34997c62ce`,
SHA-256 `9285a6df41070e315c167c7fd6a039070e8a5d243dd21a566843e565259c7d97`.
Issue: [github.com/elsonidoq/skills#44](https://github.com/elsonidoq/skills/issues/44).

**Status:** Derived architecture for independent review and later task generation, not
implementation approval. No substantive specification corrections were needed.
Installed `.pi/prompts/speckit.plan.md` was followed; `setup-plan.sh --json` ran once.
Its `BRANCH=006-issue-linked-delivery` is the feature identifier from the existing pointer,
not a Git branch change. Before/after hooks are absent. Phase 0 research precedes Phase 1
contracts, data model and validation guide. No tasks are generated here.

## Summary

Keep planning in skills. Associate one delivery issue, use it and the current chat for
exact-commit delivery/acceptance, and add one manual assessment skill. Replace the custom
execution controller with Python LangGraph nodes using existing Pi, check, Git, session
and history helpers. Keep sequential execution by default; permit explicitly authorized
path-disjoint worker waves and synchronize before checks/checkpoints and dependent work.
Use one metadata-only LangSmith adapter at invocation boundaries. Keep the monitor until
real replacement visibility passes its later live gate. Retire only the approved behavioral
collection and operative mandates, not meaningful runtime or security checks.

[research.md](research.md) is the single canonical dependency/seam research owner. It records
versions, inspected sources, source→constraint→check reasoning and honest evidence limits.
[data-model.md](data-model.md), [interfaces](contracts/interfaces.md), and
[quickstart.md](quickstart.md) supply compact implementation and validation contracts.

## Technical Context

- **Language/version:** Python >=3.10; current lock target Python 3.12 Linux x86_64.
  Existing Node/Pi SDK host remains JavaScript. No new agent capability version requirement.
- **Dependencies:** LangGraph 1.2.21, SQLite saver 3.1.3, LangSmith 0.14.17 and existing
  PyYAML 6.0.3. Full transitive lock/install consistency is an implementation check.
- **Storage:** Existing private `.coherence/workflow/workflow.sqlite` for original input,
  effects/checks/history; separate `.coherence/workflow/graph.sqlite` for standard saver
  tables only. Existing metric JSONL/history remains readable. Git and the delivery issue
  remain their existing evidence owners. No new trace/learning/receipt database.
- **Testing:** Existing Python unittest, Node test/SDK fixtures, temporary local Git/SQLite
  checks, focused static checks and explicitly authorized live application acceptance.
- **Platform/type:** Existing local CLI plus attached Pi parent; no daemon or hosted graph.
- **Constraints:** Exact selected executors; private state never automatically traced;
  no replay of uncertain effects; normal hooks/signing and unrelated bytes preserved.
  No invented latency, scale, resource or spending target.
- **Executor:** Reuse the already resolved
  `/home/dev/.paseo/worktrees/0zfm1a0e/boring-eel/.pi/workflow-executor.json` unchanged:
  Terra 6.1/medium implementation, explicit Sol 6.1/medium fallback and fresh Sol 6.1/medium
  reviewers. The planning assignment remains `standard-plan-helper → standard-plan →
  openai-codex/gpt-6-astra`, medium. Planning assignment is not an implementation binding.

## Constitution Check

Before research and again after design, principles I–VI remain compatible with this bounded
planning pass: portable skills, evidence/uncertainty, explicit approval, smallest sufficient
checks, retained focused commits, independent review and historical compatibility.

The current constitution's sequential custom executor and sole-writer wording cannot be
used as the implemented target. AGENTS already permits owner-directed same-checkout
concurrency. The specification explicitly requires operative amendments before reliance.
[Exact proposals below](#operative-amendments-for-later-explicit-approval) identify the
bounded changes; **they are not approved amendments in this pass**. Thus planning passes
with the implementation/cutover gate retained, not a waived constitution or an assertion
that runtime compliance already exists. No changes to the constitution or other policy
owners occur here.

Applicable accepted outcomes are carried into actual design and checks:

- [ADR-0003](../../docs/decisions/ADR-0003-current-launch-authority-and-neutral-tasks.md):
  current scoped launch authority overrides historical preparation text. Preserve its prompt
  block in initial, corrective and resumed invocations; check all three. Next task producer
  keeps executable tasks authorization-neutral, with temporary status in approval records.
- [ADR-0004](../../docs/decisions/ADR-0004-shared-routine-worker-permissions.md): keep the
  shared routine-authority block, ordinary safe repairs and small isolated tests/databases
  without repeated consent. Preserve manual/security/paid/data/external gates, hooks/signing,
  unrelated work and global-install/credential/deploy/push restrictions. Inspect failures
  before cause-specific recovery; no new permissions service or resource cap.
- Project memory index `memory/MEMORY.md`: routine progress does not wake the parent;
  questions/completion can. Routine technical choices are autonomous; capability versions
  are not eligibility requirements. No memory writes or automatic guidance from assessment.

## Project Structure

### Documentation for this feature

```text
specs/006-issue-linked-delivery/
  spec.md                    approved requirements; unchanged
  plan.md                    this derived architecture
  research.md                canonical dependency/seam findings
  data-model.md              control state and existing storage roles
  contracts/interfaces.md    CLI/Pi, delivery and assessment contracts
  quickstart.md              later validation guide
```

`tasks.md` and any executable task file belong to the next separate producer.

### Maintained source owners

- `runtime/coherence_workflow/engine.py`: replace controller with graph construction/
  invocation; extract only necessary reusable helpers into focused modules, not a generic
  orchestration abstraction. A small `graph.py` is suitable if it keeps node wiring readable.
- `store.py`, `git_effects.py`, `verification.py`: retained effects/history and focused
  check/commit boundaries; graph saver setup can live beside store setup without mixing schemas.
- `intake.py`, `sessions.py`, `processes.py`: retain six-check input and existing session/
  liveness helpers; update only actual graph/concurrency callers.
- `pi_adapter.py`, `runtime/pi-host/host.mjs`, `runtime/pi-extensions/coordinate-implementation-bridge.js`:
  durable question-pause/answer route and multiple exact steering targets.
- A small `runtime/coherence_workflow/tracing.py`: approved metadata projection and explicit
  SDK submission. Reuse `metrics.py`; retain useful `metric_artifacts.py` compatibility.
- `cli.py`, `scripts/coordinate-implementation`, package declarations/lock and runtime tests:
  same entry, graph resume, compatible status/history and dependency packaging.
- `skills/planner`, `skills/task-generation`, `skills/coordinate-implementation`,
  `skills/finish-session`, `skills/track-open-issue`: issue propagation and lifecycle owners.
  New `skills/assess-skill-improvements/SKILL.md`: manual portable entry, not a runtime service.
- `AGENTS.md`, `README.md`, `REQUIREMENTS.md`, `docs/index.md`, constitution,
  `docs/coordinate-implementation.md`, `docs/coordinate-implementation-schema.md`:
  lockstep operating/policy documentation. Relevant SpecKit task prompt/template references
  must preserve optional concurrency context without adding intake rules.
- Approved behavioral retirement paths and, after live release, monitor-only callers are
  bounded below. No historical approval rewriting or unrelated repair sweep.

## Architecture and interfaces

### Skill-owned delivery lifecycle

Planner understanding/brainstorming remains possible without an issue. Before downstream
planning handoff, resolve the declared tracker, associate the supplied issue or use existing
`track-open-issue` creation/duplicate/readback rules within authority. Missing write access
reports that operation; it is not a new universal planning stop. Carry a qualified issue URL
in existing human artifact context and optional executable top-level `delivery_issue`.
The six-check linter does not require it; generic unrelated direct coding stays valid.

After runner checks, checkpoints and fresh independent review, `finish-session` uses the
actual attributed task/repair commits to prepare the same executive text for issue and chat:
result, checks, limits, review focus and exact presented commit. Internal completion is not
owner acceptance. Link corrections by purpose (implementation/internal review, owner review,
new requirement) and refresh the presented revision. Read back tracker writes. Report a
partial publication rather than claiming delivery. If a write result is uncertain, inspect
existing issue comments before retrying it. No graph node posts/accepts/closes issues.

The owner must explicitly accept the identified revision. If acceptance names an older
revision, do not apply it to new work. Scope changes renew affected approval. Close only
with actual closure authority; preserve acceptance even if closure cannot run. A full Git
range is review context, not automatic issue attribution. Do not start RCA, skill edits or
PR creation as a side effect. Details are in the [interface contract](contracts/interfaces.md).

### One execution controller

Build one LangGraph `StateGraph`, with a task subgraph for effect boundaries. Delete the
custom `Engine.invoke` task loop, `_finish_reviews` lifecycle dispatch loop and custom
resume-stage selection once their graph replacements pass. Do not put an `Engine.invoke`
call inside a graph node. Existing parsing, prompt, evidence, Git and policy helpers can
remain ordinary functions; Store validation of facts is not a second scheduler.

Graph boundaries and data flow:

1. **Reconcile / select ready:** Load original inputs and latest framework state. Reconcile
   any interrupted invocation/checkpoint before mutation. Readiness is ordinary application
   logic over declared dependencies and accepted focused checkpoints. Choose one task in
   stable intake order, or a disjoint authorized wave; no continuous ready queue.
2. **Task prepare / gate:** Resolve task-local ownership and existing session selection.
   Declared manual gates enter a separate `owner_wait` node before the affected effect.
   Routine covered operations use existing authority, not a new question.
3. **Dispatch / Pi effect:** Retain invocation identity and saved-context reference in
   ordinary history before calling `PiAdapter`. A graph rerun reads that identity first:
   use a retained terminal result, or stop for an uncertain live/missing result. A returned
   `blocked/failed/incomplete` is not task success. A settled question result routes to wait.
4. **Owner wait / continuation:** `interrupt(payload)` holds the pending question in private
   framework state. CLI/parent obtains the actual reply and calls `Command(resume=...)` for
   the same thread/interrupt. The consumer validates the current target; a worker question
   answer is delivered to a new continuation invocation of the same saved task context, not
   a replay of the previous prompt. See the concrete transport route below.
5. **Join / project checks:** Wait for wave workers to settle. Run each task's specified
   commands and actual manual acceptance with existing `verification.py`. Retain actual
   failure output privately. A correctable check/implementation failure routes to that
   task's scoped correction, with other settled results retained. No generic retry policy.
6. **Focused checkpoint:** While no sibling can mutate, inspect task-owned bytes/diff,
   retain attempted parent/selected paths/content before Git, and use `FocusedGit` with
   normal hooks/signing. On return failure/reopen compare actual commits before retrying.
   Verify the attempted parent, exact changed-path set and selected content. If HEAD has
   since advanced, inspect the actual direct child of the attempted parent rather than
   attribute the new HEAD or a whole range to this task. Record a matching successful SHA,
   or stop an uncertain effect. Genuine no-change has no empty commit. Only accepted
   checkpoint results release dependency edges.
7. **Independent review / scoped repair:** After all tasks checkpoint, invoke a fresh
   read-only reviewer with original range, actual attributable checkpoints, required-check
   output and worker-reported returns clearly distinguished. Graph edges route actionable
   defects to scoped repair/check/checkpoint and a fresh follow-up review. Preserve existing
   cumulative coverage and evidence-only reassessment/target-refresh outcomes, and explicit
   routine repair authority; do not transplant the old dispatch loop. Material gates wait.
   Existing session allowance and fallback-stop rules remain; no new retry budgets.
8. **Finish:** Retain the actually reviewed application SHA and qualified local usage.
   Internal completion ends the graph. Skills handle executive delivery and owner acceptance.

The graph persists typed control state, result references, pending questions and coverage
references, not repeated raw task histories. Standard saver tables live separately to avoid
colliding with retained legacy tables. Stable thread identity and `durability="sync"` are
required at invocation/resume. Resume uses the latest checkpoint, not time travel. No custom
checkpoint serializer, migration service or event ledger is needed.

### Questions reach the actual consumer

Existing manual gates can directly use a wait node. In-call Pi questions need a small
transport change, because the current callback blocks while a host/provider session lives.
For graph runs, opt into `pauseQuestions` in the host request. On a question the adapter
requests a pause, not an answer. The host saves question/tool identity, reports an explicit
awaiting-decision tool disposition, aborts further generation and waits for SDK idle before
returning `waiting` plus the saved session. No actual denied/gated operation may run during
this disposition. Preserve old transport behavior for callers without the opt-in.

Persist that settled result before entering the side-effect-free wait node. Attached mode
maps its interrupt ID to the existing `coordinate_implementation_reply` or owner-only reply
request; terminal mode asks interactively. Routine triage can answer covered work from
current authority and says so. Missing input leaves the graph paused; it never fabricates
an answer. Reopen reads the same pending interrupt, reissues its question if necessary and
resumes only with the actual answer. A targeted continuation prompt includes the pending
question and actual answer, original authority and settled effects, and uses the saved Pi
session. It does not pretend to resume a dead transport callback. The new invocation has
its own identity and usage interval.

If a process dies before idle/result persistence, reconciliation inspects the saved call,
SDK session and actual live process before any continuation. Unknown effects stop only that
operation. Do not rely on a graph checkpoint as evidence the provider never ran. Test this
with the actual installed SDK fixture provider before wiring general worker questions into
graph resume. This is a production seam check, not a disposable prototype prerequisite.

### Concurrency and Git critical section

Default remains one worker. Explicit launch `--parallel` (parent `parallel: true`) records
owner-directed concurrency in retained run input; it is never inferred from independent
DAG nodes. The same controller may dispatch path-disjoint ready tasks with `Send` to the
task subgraph. Missing/uncertain path boundaries do not invalidate intake: coordinate that
wave's ownership or execute it sequentially. Use exact claimed paths plus declared
`owned_paths`/known output boundaries to detect overlap; broad directory overlap is not
safe merely because task IDs differ. Share no active Pi session between branches.

Keep the existing inherited per-worktree lock to exclude a second cooperating controller,
not to prohibit workers within the authorized controller. A small in-process mutex protects
shared claim/dispatch bookkeeping. Use thread-owned history connections/short SQLite
transactions, and the saver's own connection/lock. Do not hold a database transaction over
a provider call or owner wait. The parent bridge must route multiple exact targets rather
than overwrite its current single target; owner questions can be delivered one at a time.

After the worker wave settles, a single coordinator critical section covers the actual
check→diff→stage→commit/reconcile interval. No branch tool execution or shared generated-output
mutation overlaps it. Commit each task's explicit paths independently; do not collect all
wave changes into one commit. If checks mutate shared outputs, assign them to this serial
phase and preserve task ownership. If a correction needs wider paths, coordinate the actual
overlap before further edits. Retain successful sibling results when another fails; no
successor sees a merely returned worker as a completed prerequisite. This uses a barrier
and existing Git safety, not a new scheduler, index-per-task system or mandatory worktrees.

Uncooperative unrelated writers are not fenced by advisory locks. Recheck selected bytes,
index entries and actual parent at the operation boundary; on target drift retain work and
coordinate. Do not reset unrelated state. Post-wave integration checks and final review
observe causal cross-task interactions without claiming ownership of unrelated commits.

### Recovery and legacy compatibility

New inputs record `execution_backend: langgraph-v1` in their existing private authority
context. Missing marker identifies legacy execution, not a graph seed. New status/history
continues read-only current and historical SQLite/JSONL projection without initializing or
converting storage. Graph status adds a safe waiting/interrupt indicator, never private
question text, prompt or session path in public projections.

Pending legacy runs use the compatible pre-migration runtime at
`4c1725ebded2f89dec6933b8d193bf34997c62ce` (or a verified later pre-cutover compatible revision)
from a retained suite checkout/environment, targeting the original project and run ID.
The new CLI refuses to execute a legacy resume/recover/repair/refresh operation and gives
that exact compatible route. The owner/coordinator inspects the failed call first and
explicitly invokes that old entry; no automatic process launch, database import, replay,
reset or conversion. Keep old code in Git, not a second execution controller in the new
package. Both versions retain the same per-worktree lock so they cannot run concurrently.
Before removing a sole compatible environment/checkout, preserve its reproducible revision
and required private runtime assets through the existing retention policy. Finishing a
legacy run before switching its active runtime is the simplest operational path.

For graph runs, preserve `recover-task`, inspected `continue|fresh|escalate`, review-target
refresh and routine-repair authority as application actions feeding graph state, not new
control loops. Reuse exact transfer/ownership helpers unchanged where possible (#28/#43
remain separate). Stop after a failed authorized Sol escalation; no further dispatch without
owner direction. History and graph state may disagree after a crash: reconcile operation-local
facts, not a blanket clean-tree/HEAD admission test. Required persistence failures prevent
unsafe dependent mutations; optional metrics/telemetry failures report a gap only.

Rollback selects the retained old runtime for old runs and stops new graph launches. Never
feed graph runs into the old engine. Inspect/recover graph runs with their compatible graph
revision, or retain them stopped while repairing it. Keep both databases and partial work;
no automatic downgrade, data deletion or history conversion. Monitor removal has its own
later gate and source rollback through Git, not a service shutdown instruction.

### Tracing and monitor cutover

One small explicit LangSmith adapter consumes safe invocation observations from Pi. It
creates fixed-name run/task/invocation chain spans with opaque IDs and qualified metadata.
[Research](research.md#metadata-only-langsmith-submission) fixes the selected SDK privacy
controls, automatic-tracing suppression and final-request checks. Do not instrument raw
provider/tool calls, errors, graph state or prompts with decorators/callbacks. Do not add a
trace queue, event schema registry, new metrics mirror or per-token/tool capture.

Reuse invocation-local `metrics.interval_record`; session totals and missing statistics are
not invocation usage or zero. Keep useful local metric artifacts/readers; LangSmith is the
live visibility replacement, not a reason to convert historical records. Adapter creation,
submission and observation failures produce a safe visibility-gap notice and cannot veto
otherwise safe checks/checkpoints. Disabled/missing upload authority means no SDK network
submission, even with ambient tracing environment variables.

Monitor-specific source/dependency removal waits for: local actual-SDK privacy/fail-open
checks; explicit account/project/region/access/pricing/upload authority; and observation of
one real permitted graph/task/invocation hierarchy in the selected LangSmith UI. Inspect
usability, known/unknown usage and safe categories, not merely HTTP success. No offline
substitute releases that gate. Preserve historical monitor data, mockup/history links and
open acceptance limits (#2/#10/#13). No automatic service shutdown or issue closure.

### Manual assessment

`assess-skill-improvements` is an explicitly invoked skill. Resolve the declared tracker;
use paginated GitHub all-state issue reads and comments, excluding PRs. No assessment label
means unassessed; acceptance status is evidence, never eligibility. Default discovery
reports all unassessed matches in the explicitly selected repository; an owner may select a
bounded subset for this assessment without claiming the remainder were assessed. Do not
invent a scan cap or poll in the background.

Read intent, approved artifacts, feedback and supported correction commits. Distinguish
changed/new requirements from planning/task/implementation/review omissions and unnecessary
workflow complexity. Record uncertainty and missing evidence. Group supported causes in
one presented proposal with per-issue links and responsible existing skill owners; do not
turn each correction into a rule. Minimal labels `skill-assessment:proposed`,
`skill-assessment:addressed`, `skill-assessment:no-change` record state, with absence meaning
unassessed. Reuse equivalent labels if already available. Conflicts are inspected, not
silently overwritten. Analysis alone never means addressed. No-change may explicitly mean
insufficient evidence, not proof no defect existed. Owner-requested reassessment can include
previously assessed issues without erasing their trail.

Write labels/comments only with target/operation authority and independent readback. A
partial failure stays partial. Approved proposals enter existing planning and implementation
approval; addressed requires delivered improvement evidence. Global changes require a
portable cause/outcome, not project-specific experience promoted into global rules. No
learning ledger, autonomous edit loop or implicit PR authority.

## Ordered design stages and verification rationale

These are integration order and meaningful outcomes, **not executable task assignments**.
The next fresh producer must split independently testable seams for the selected Terra/
medium executor, with bounded owned paths, consumed interfaces and check observables.
Do not assign an entire stage below as one milestone task by default.

1. **Reconcile operative contracts and issue lifecycle.** Obtain exact amendment approval
   before affected behavior relies on it. Integrate issue association and exact-revision
   delivery at existing skill owners, with direct no-issue intake and partial tracker
   failure walkthroughs. Manual assessment can develop independently after the label/
   lifecycle contract; it does not depend on graph execution.
2. **Replace sequential control and establish durable effect boundaries.** Deliver selected
   dependencies/saver, actual graph routing and retained helpers, CLI/history compatibility,
   then question/repair/review resume at their real interfaces. Place crash-before/after
   invocation/Git checks at the first usable graph seam before downstream reliance. Remove
   the replaced custom controller, not its useful safety helpers. No throwaway prototype.
3. **Enable explicit disjoint waves.** After sequential graph/effect recovery works, add
   `Send`/keyed results, thread-safe history, multi-target parent routing and the quiescent
   check/commit barrier. A composed fork/join with one failed branch must demonstrate both
   overlap and safe serialized checkpoints. This is not permission to run workers in
   parallel during this planning pass or implementation without owner direction.
4. **Add safe invocation visibility.** Local real-SDK outbound sentinel, usage and fail-open
   checks precede any upload. After explicit live authority, observe the actual replacement
   hierarchy/metadata; only then release monitor-only source/dependency retirement. This
   stage can remain gated while unrelated local work proceeds.
5. **Finish manual assessment and bounded retirement integration.** Exercise pagination,
   open/closed/missing evidence, purpose classification, proposed/no-change/addressed
   distinctions; retire named behavioral machinery and supersede active mandates. Preserve
   meaningful checks and historical NOT RUN observations. These outcomes need not wait on
   monitor cutover; only monitor-specific retirement does.
6. **Validate composed delivery and present the exact revision.** Run the smallest actual
   CLI/Pi/Git recovery and concurrency scenarios, then the separately authorized tracker
   delivery/correction/acceptance and LangSmith observation. Fresh independent review must
   have actual task/checkpoint evidence and honest unrun gates. Publish matching issue/chat
   summary only for the reviewed delivery. Acceptance and closure are later owner actions.

The hardest risks are interrupted Pi effects, Git success before history, parallel Git
ownership and telemetry leakage. Permanent actual-helper/integration checks have more value
than a separate demo. Easy API names/labels are settled by inspection, not experiments.
Live account usability cannot be proven locally, so its real gated observation is retained.
Fail-then-pass regressions should reproduce concrete old failure paths where practical;
new graph behavior uses explicit adverse cases, not manufactured whole-feature replays.
Unrun/failed checks never release the affected dependency. [Quickstart](quickstart.md)
specifies observable scenarios and existing command families; new test selectors belong to
implementation, not fictitious commands presented as already available.

## Operative amendments for later explicit approval

The following text is the bounded proposal to approve through the existing final planning/
policy gate. Source approval does not authorize mutation of these owners. Preserve unrelated
clauses, prior version history and historical approvals. Proposed constitution version is
**4.4.0 (MINOR)**: materially expanded executor guidance, with unchanged core principles;
use the actual approval date when applying and record the owner's exact approval/rationale.

**Constitution — Project Constraints**, replace the sentence beginning “The owner-approved
Coordinate Implementation migration permits the existing sequential Python/SQLite task
executor” with:

> Coordinate Implementation uses Python LangGraph for implementation control, standard
> file-backed checkpoint persistence and the thin official Pi SDK host. Execution is
> sequential by default. Explicit owner direction can permit disjoint workers in the same
> checkout; overlap or uncertain ownership requires coordination. This permits neither a
> generalized platform, automatic installation, planning-workflow rewrite nor unrelated
> runtime extensions.

**Constitution — Development Workflow**, replace the current sole-writer/final-review
sentence with:

> The runner preserves task-owned paths and verifies each focused checkpoint. Explicitly
> authorized concurrent workers may share a checkout with distinct paths; the coordinator
> serializes shared check/Git mutation boundaries. Overlap requires coordination, not a
> mandatory worktree. Fresh independent read-only final review remains mandatory, with
> attributable task/repair checkpoints distinguished from unrelated range context.

Replace “it grants no parallel implementation writers” with “it grants no implementation
concurrency without explicit owner direction.” Keep the six linter checks, all approval/
checkpoint/recovery safeguards and skill-based planning. Clarify that the existing “no
graph ... eligibility” clause forbids extra admission protocols, not framework persistence.

**Coordinator skill, operating and schema owners**, replace sequential custom-control,
“no graph saver” and exclusive-worker descriptions with:

> LangGraph owns execution transitions, synchronized dependency waves and interrupt/resume.
> SQLite graph checkpoints hold control state; existing private operation history and actual
> Git/SDK observations support effect reconciliation, not automatic acceptance. One
> cooperating controller retains the inherited worktree lock; owner-authorized path-disjoint
> workers may overlap within it. Checks and focused commits run with sibling mutations
> quiescent. Six task-linter checks remain the entire startup linter. Historical non-graph
> runs remain readable and use their retained compatible runtime for explicit inspected
> continuation; they are never silently converted or replayed.

Retain the existing current-launch/shared-routine-authority blocks and real gates. Update
CLI/Pi schema to the [interface contract](contracts/interfaces.md); remove only replaced
stage selection, not effect validation. AGENTS suite execution wording and README/runtime
requirements follow this same bounded meaning. Correct touched operating examples to the
actual required reviewer configuration rather than preserving the current contradictory
“optional reviewer” prose; do not change historical inputs.

**Finish-session safety rule and docs routing**, replace only the summary prohibition with:

> Git owns changelogs, file-and-line inventories and plan/task completion metadata; do not
> duplicate those as routine closeout bookkeeping. For issue-linked delivery, publish the
> meaningful executive result, verification, limits, review focus, exact presented commit,
> owner feedback/correction links and acceptance trace in the delivery issue and current
> owner chat. This does not authorize routine inventories in memory/docs, automatic RCA,
> skill changes, PRs or unrelated tracker writes.

**AGENTS evaluation convention, README validation, docs/index evaluation routing and active
skill maintenance interpretations**, substitute:

> Use the smallest meaningful check of the changed behavior and report its limits. Preserve
> applicable runtime, integration, application, security and permission checks. No retained
> behavioral comparison collection, mandatory prior/candidate run, live RPC scenario or
> full historical replay is required. Static/carrier/trace sensitivity is not model-obedience
> proof; genuine live application acceptance and its authority remain required where specified.

Remove the evaluation routing link; route validation to README's maintained validation
section. In `docs/plans/planner-regression.md`, mark the old smoke/scenario and mandatory
behavioral acceptance/resumption directions superseded by this operative policy; preserve
historical observations and NOT RUN limits. Do not reclassify old evidence as a pass.

## Bounded retirement and preservation

Remove exactly `evaluations/README.md`, `evaluations/review-necessity/packet.md`,
`evaluations/review-necessity/expectations.md`, `evaluations/review-necessity/recipe.md`,
`scripts/planner-rpc-smoke.py`, its `rpc` loader and `RpcDriverTests` in
`scripts/test-planner-workflow.py`. Update the active owners above. Keep historical plan
records and Git evidence, not a new archive.

Retain meaningful `check-planner-workflow.py`, remaining planner tests, `planner-trace.py`,
planner fixtures, skill lint and runtime tests. Adjust obsolete assertions/carriers only
where maintained behavior changes; tests that merely assert the old sequential/no-saver
contract are not immutable requirements. Preserve actual permission, parser, resolver,
installer, ordering, ownership, checkpoint, recovery and privacy checks. Do not add a
synthetic replacement suite or application startup test registry.

After live release only, remove redundant `workflow_monitor` application/source/tests,
monitor launch/build-only dependencies and the now-unused recording adapter/Store monitor
writers/call sites. First inspect actual imports and packaging callers to distinguish
monitor-only code from history readers, metrics, current invocation evidence and retained
historical schemas. Preserve `workflow_monitor/README.md` as cutover/history ownership,
existing historical data and mockup evidence; reconcile active README/docs/index/setup
references. Do not remove useful historical CLI readers or optional metric helpers simply
because they once served the monitor. No service stop, data cleanup or issue-state action.

## Self-review and remaining gates

**Does the current plan induce scope creep or over complexities?** The broad required
outcomes do not justify a new platform. This design uses one graph, one standard saver,
existing operation history and one explicit trace adapter. It rejects a custom event ledger,
second execution controller, mandatory prototype chain, background assessment scanner,
retention/permission services, global admission rules and an isolated index/worktree per
parallel task. Checks stay with concrete outcomes. The host question-pause change earns
its cost because the current live callback cannot safely survive a graph interrupt;
the quiescent Git barrier earns its cost because a global index cannot isolate parallel
checks/commits. Dedicated SDK privacy options remove the need for a custom sanitizer service.

No unresolved material product choice is hidden in the design. Pending gates are explicit:
exact operative amendment approval before reliance; normal reviewed task/implementation
approval; real tracker write operations; real LangSmith account/project/region/access,
pricing and upload authority; actual live replacement visibility before monitor removal;
separate PR/push/deploy/service/data authority if ever requested. Fresh-session activation
is required for changed global capabilities in Paseo, with checkout/revision/approval and
loaded capability verification; do not ask the owner to run `/reload`.

All runtime integration, dependency installation, live provider/tracker/LangSmith and
behavioral acceptance checks are **NOT RUN** in this planning pass. Research does not
establish those outcomes. Related issues #2/#10/#13/#14/#16/#41/#42 remain separately owned;
#14 and #16 inform checks, not automatic fixes/closures. Preserve #28/#43 transfer helpers
without adding their wider repair as a prerequisite.
