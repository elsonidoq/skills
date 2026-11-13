# Implementation Plan: Issue-linked delivery and manual skill assessment

Apply [Parsimony and Actionable Checks](../../skills/planner/references/parsimony.md).

**Branch:** `plan-issue-44` | **Date:** 2026-11-13 | **Spec:** [spec.md](spec.md)

**Input:** [Current specification](spec.md) at `fb5d5a39246cb9ab0f7feb7c3442872721a3b48d`,
SHA-256 `952b41d0d470caa108fb4f3d1fbd17cea7333bb370f434c8d0b5c37e86338366`.
Issue: [github.com/elsonidoq/skills#44](https://github.com/elsonidoq/skills/issues/44).

**Status:** Owner-authorized downstream planning simplification for presentation, not
implementation or unseen final-task approval. Original installed SpecKit plan setup ran once;
this correction does not rerun it. Tasks remain owned by their separate producer.

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
- **Proposed storage:** Existing private `.coherence/workflow/workflow.sqlite` for original input,
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

`tasks.md` and `tasks.json` remain owned by their task producer, who aligns them after this correction.

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

### Requirements versus proposed mechanisms

The [specification](spec.md) fixes Python LangGraph control, Pi agent execution, LangSmith
visibility, skill-owned planning, one controller, durable effect reconciliation, explicit
concurrency direction, privacy and live visibility before monitor removal. These outcomes,
checks, authority and historical preservation are not optional hardening.

The node layout, `pauseQuestions` transport, saver file arrangement, backend marker,
checkpoint-intent representation and exact SDK helpers below are **derived proposals**.
Their basis is in [research](research.md); their observables are in [quickstart](quickstart.md).
Use a simpler equivalent framework/SDK mechanism when it preserves those observables and
security/history/authority outcomes. Routine equivalent mechanics need no renewed owner
choice or abstraction layer. Material changes to accepted architecture, privacy or scope
still return to the owner. Test consequential assumptions before reliance, within the
production outcome rather than a new spike chain.

### Skill-owned delivery lifecycle

Planner associates an issue after understanding, using declared tracker ownership and
existing `track-open-issue` capabilities. No issue is required for intake. Carry the URL in
artifact/context fields; issue operations do not belong in the execution graph. The
[delivery interface](contracts/interfaces.md#delivery-issue-and-acceptance) owns publication,
feedback and closure behavior. Normal coordinator/finish-session delivery after checks and
fresh independent review satisfies SC-001; no worker task stages an owner correction,
acceptance or closure exercise. Observe those branches only when they occur naturally.

Manual assessment is one portable explicitly invoked skill, using existing issue reads,
labels and approval routes, not a service or automatic acceptance hook. Its
[interface](contracts/interfaces.md#manual-assessment) owns discovery/classification/state;
[validation](quickstart.md#issue-delivery-and-manual-assessment) preserves the bounded live
assessment and local-evidence distinction.

### One execution controller

Proposed wiring: `StateGraph` with task-local effect boundaries. Remove `Engine.invoke`'s
custom task loop, `_finish_reviews` dispatch loop and custom resume-stage selection after
their replacements pass. Retain parsing, prompts, evidence, sessions, checks and Git helpers;
do not wrap the legacy engine in a single node or keep parallel old/new controllers.

| Boundary | Responsibility |
| --- | --- |
| Reconcile / ready | Read original inputs and latest state; reconcile unfinished effects; select dependency-ready work in stable order. Default one task, directed disjoint wave otherwise. |
| Prepare / gate | Establish task paths/session. Ask only an outstanding actual gate; consume already approved unchanged authority as below. |
| Pi dispatch | Retain invocation identity before calling the adapter; reuse a settled result on recovery, stop uncertainty before redispatch. Unsuccessful return is not acceptance. |
| Owner wait | Standard framework interrupt/resume connects the actual terminal/parent reply to the affected operation. No provider or Git effect is repeated because a wait node reruns. |
| Join / checks | Settle siblings, run specified checks, retain actual failures and route ordinary scoped correction to the same task. |
| Focused checkpoint | Inspect owned diff with sibling mutation quiescent; normal hooks/signing, one verified commit per task. Only checkpoints release dependents. |
| Fresh review / repair | Review actual attributable checkpoints and full integration context; retain cumulative coverage, scoped repairs and fresh follow-up review, including supported reassessment/target refresh. |
| Finish | Retain the reviewed application SHA and qualified usage; normal delivery follows outside the graph. |

Proposed persistence uses the standard SQLite saver with stable thread identity and sync
durability, separate from existing private operation history to avoid table collisions.
[Data model](data-model.md) defines ownership, not a second trace ledger. No automatic
provider-node retries or time-travel recovery. Existing session allowance and fallback-stop
rules remain; no new retry budget.

### Questions reach the actual consumer

The current Pi callback waits on a live host. A framework interrupt alone cannot preserve
that callback across process loss. Proposed adaptation: opt into `pauseQuestions`, record
an awaiting-decision disposition, stop generation and await SDK idle before returning a
saved-session `waiting` result. Then a side-effect-free graph wait receives the actual
terminal/parent answer. Continue only pending work in that saved context with a separately
identified invocation, not the old prompt. Do not await abort from inside its own tool and
create a self-deadlock. Existing callers retain their transport behavior.

This adaptation is not proven by existing abort support. Before reliance, the actual
SDK/adapter/graph check must observe settlement, reopen, targeted answer consumption and no
repeated settled effect. An equivalent supported SDK suspension/resumption route is preferable
if simpler and passes the same check. Missing idle/result facts require process/session/effect
reconciliation; they never imply safe redispatch. External reply behavior is in
[interfaces](contracts/interfaces.md#pi-question-pause-and-continuation).

### Concurrency and Git critical section

Proposed directed-wave wiring uses `Send`, keyed task results, existing inherited worktree
lock and thread-owned short SQLite transactions. The lock excludes conflicting controllers,
not authorized disjoint workers within one controller. The singleton parent steering target
needs exact task/invocation/session routing for concurrent workers; do not share an active Pi
session. Missing path boundaries require coordination or sequential work, not a new linter.

Workers may overlap only on distinct owned paths, including generated outputs. Quiesce
sibling mutation for the shared check→diff→stage→commit/reconcile boundary. Commit each task
separately; retain successful sibling results after failure. Coordinate wider corrective
edits before restarting mutation. A global Git index lock alone cannot provide this safety.
No mandatory worktrees, separate index scheme or scheduler service is needed.

For interrupted Git, retain enough operation-local facts to verify attempted parent, selected
paths/content and actual resulting commit; existing fixer/external-recovery history provides
a reuse pattern. If HEAD advanced, inspect the matching direct child rather than claim the
latest HEAD or whole range. Exact intent encoding is not prescribed. Preserve unrelated
staged/working bytes; target drift stops only the unsafe operation. Keep #28/#43 transfer
helpers and their separate ownership, not a broad recovery repair prerequisite.

### Recovery and legacy compatibility

Proposed routing records `execution_backend: langgraph-v1` in existing private run input.
Missing marker remains legacy, not seed data. New status/history reads retained SQLite/JSONL
without conversion; public projections omit prompts, questions and session paths.

For pending legacy operations, use an explicitly selected retained pre-cutover runtime at
`4c1725ebded2f89dec6933b8d193bf34997c62ce` or a verified compatible revision/environment,
targeting the original project/run after inspecting its failure. New CLI diagnostics give
that route rather than launching it automatically. Keep old code in Git, not in a second
controller; retain the shared lock and required private assets under existing retention
policy. This route is a derived compatible mechanism, not a demand for new migration tooling.

Graph recovery preserves inspected continue/fresh/escalate, external same-task completion,
routine-repair authority and review refresh as graph actions. Preserve actual checks and
fresh review. After a failed authorized Sol escalation, stop for owner direction. History/
saver disagreement requires effect reconciliation, not a blanket clean-tree admission test.
Required persistence failures block unsafe mutations; optional telemetry reports gaps only.

Rollback stops new graph launches and uses compatible runtime revisions for each run type.
Never feed a graph run to the old engine. Retain failed runs, partial work and databases;
no automatic downgrade/conversion/deletion or service stop.

### Tracing and monitor cutover

Use one small metadata-only adapter at the Pi invocation boundary, reusing qualified local
metrics. [Research](research.md#metadata-only-langsmith-submission) owns inspected SDK options
and their rationale; exact helper selection is derived, not an added owner mandate. Suppress
ambient raw graph/provider tracing. Optional telemetry failure cannot veto safe execution.

Actual SDK privacy/fail-open proof precedes upload. Actual account/project/region/access,
pricing and network authority precede live use. Usable real LangSmith UI visibility precedes
monitor-only removal; HTTP success or offline evidence is not a substitute. The
[quickstart](quickstart.md#live-replacement-and-monitor-retirement--explicit-gate) owns the
observable and evidence-reuse boundary. Preserve historical monitor data and open limits.

### Approval reuse in task handoff

Final explicit planning approval can cover the exact operative amendment text below.
For unchanged content/scope, downstream tasks inspect and consume that approval through
normal launch/brief context, rather than ask again. Changed content or an uncovered actual
operation keeps its applicable gate. No approval cache, permission protocol or runtime
schema is needed.

`verification.manual_gates` currently asks for every `gates` entry; it cannot reuse evidence.
The task producer must therefore remove duplicate policy-consent entries in T001/T003/T016,
not leave them with instructions to skip the question. Likewise, T021 already depends on
T020: inspect the applicable successful live observation, do not ask the owner to recertify
it through another “Confirm actual successful T020” gate. Missing/invalidated visibility
still prevents removal. Keep outstanding live/private/paid/tracker authority, not duplicate
questions about already satisfied prerequisites.

Remove the old T018 worker exercise. Its natural publication and conditional owner-review
trace belong to normal coordinator/finish-session delivery, not a task that manufactures
feedback or unrelated test issues. Remaining task IDs may stay stable with gaps.

## Ordered design stages and verification rationale

These stages guide dependency order, not milestone-sized worker assignments. Keep bounded
interfaces/checks for Terra/medium and split independently verifiable outcomes.

1. Align runtime and lifecycle contracts using exact final approval, consumed without repeats.
2. Replace sequential control and validate durable Pi/Git/question/review boundaries before
   consumers rely on them; retain CLI/history compatibility and remove replaced control.
3. Add directed disjoint waves, exact parent routing and safe shared check/Git serialization.
4. Add local safe tracing, then authorized real visibility; only its observed result releases
   monitor retirement. Local work need not wait on missing upload authority.
5. Deliver manual assessment and bounded behavioral retirement independently of monitor cutover.
6. Validate composed application seams and obtain fresh independent review. Normal final
   delivery publishes the exact reviewed revision, then waits for real feedback/acceptance.

Permanent actual-helper/composed checks target the consequential Pi/Git recovery, concurrency
and privacy risks; no prototype chain or historical replay. [Quickstart](quickstart.md) owns
acceptance scenarios and honest limits. Failed/unrun necessary proof cannot release reliance.

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

**Does the current plan induce scope creep or over complexities?** This revision removes
repeated consent, a staged owner-lifecycle exercise and duplicate protocol descriptions.
Derived mechanics may be simplified while preserving their tested outcomes. One graph,
standard persistence and existing effect helpers are sufficient; no new service or ledger.

Final content/implementation approval remains pending. It can include the exact amendments
above. Outstanding external/live authority and the indispensable visibility proof remain
as described in the approval-reuse and tracing sections. No runtime/live verification was
performed during planning. Related issues remain separately owned; #14/#16 inform checks,
not automatic fixes/closures. Changed global capabilities in Paseo need the normal fresh-
session handoff, not `/reload` or automatic restart.
