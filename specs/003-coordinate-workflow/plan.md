# Implementation Plan: Coordinate Implementation executable workflow

**Branch**: `follow-attached-workflow-migration-instructions` | **Date**: 2026-10-18 |
**Spec**: [spec.md](spec.md)

**Input**: Revised specification in this directory; historical original-digest approval in
[spec-approval.md](spec-approval.md), subsequent owner SDK direction in
[source-request.md](source-request.md#sdk-integration-owner-direction).
**Status**: Draft plan; **RENEW_SPEC_APPROVAL before tasks**. Planning only, no migration
or implementation authority. The original configurable session defaults and two repairs
were approved; the integration revision's changed bytes still require renewal.

## Summary

Replace the long-lived coordinating LLM with an actual LangGraph workflow compiled from
validated versioned YAML. Registered Python handlers own intake, task selection, checks,
owner gates, recovery and Git; configured Pi agent nodes implement, repair or review.
A small pinned official Pi SDK subprocess supplies lifecycle/resources/tools and measured
telemetry over JSONL. It has no graph, task/session-selection policy, approval or Git
responsibility. SQLite is the sole durable workflow authority; Pi session files are only
conversation persistence. CLI and conversational entry use the same engine, not two paths.

Non-negotiable constraints, carried verbatim:

- The runner alone owns persistence
- No automatic model escalation or complexity-based routing
- Never replay Git side effects blindly
- Maintain one writer per worktree
- `min_free_tokens_before_compaction: 150000` means effective automatic-compaction threshold headroom, not advertised maximum and not cumulative usage
- No background LLM wakes up to decide what to do.

Keep planning skill-based. Preserve technical gotchas, authoritative docs, existing STATE,
custom content, explicit current-content approvals, REQUIRED evidence, focused task commits,
security and manual/permission gates. No per-task review obligation is added.

## Technical Context

**Language/Version**: Python >=3.10 (3.12.3 tested), thin Node ESM host using the pinned
Pi package's supported Node engines; unsupported runtime fails preflight.
**Primary Dependencies**: LangGraph 1.2.16; langgraph-checkpoint-sqlite 3.1.2; PyYAML 6.0.3;
jsonschema 4.26.0; official `@earendil-works/pi-coding-agent` 0.87.1 with exact npm lock.
No LangChain agent abstractions. Git remains system capability, not reimplemented.
**Storage**: local single-host SQLite (saver + runner tables), derived JSON/JSONL and
restricted Pi conversation files under project-owned runtime storage.
**Testing**: existing Python unittest/static/Git fixtures; focused new runtime unit and
real-engine/SDK integration tests; separately authorized live provider proof.
**Target Platform**: Linux single-host local filesystem with approved delegated cgroup v2
for process tools. Other platforms
block mutation until locking/tool-quiescence semantics are supported and tested.
**Project Type**: portable suite CLI/library with registered workflow adapter, not server.
**Performance Goals**: no speculative throughput/latency SLA; no coordination model calls,
no polling/LLM for routine decisions, one sequential writer, short-lived status process.
**Constraints**: immutable run config/input identity, real settled lifecycle, reliable
>=150k reuse headroom, no duplicate writers/commits or inferred owner answers.
**Scale/Scope**: one required workflow, sequential task stream and optional configured
review nodes, final independent full-range review; no generalized workflow marketplace.

## Constitution Check

Before research: constitution **3.0.0** valid and read; portable assets, evidence/uncertainty,
explicit authority, pragmatic checks, safe checkpoints and legacy ownership preserved.
Owner-validated A direction is settled; generic bounded-extension preference is not a
new stack-selection gate. No operative policy is changed by this plan.

After design: design retains those principles, plus deterministic enforcement and honest
NOT RUN boundaries. Implementation cannot silently apply these proposed operative changes:

1. Explicit governance amendment/exception for a bounded executable LangGraph+SDK extension
   rather than a prompt-only coordinator, with no wider platform authorization.
2. Replace constitution Development Workflow's coordinator batch/delegation/no-wrapper
   execution descriptions with runner task-local checks, commits and session policy;
   retain the **planning-only** direct-stage/delegation restrictions.
3. Clarify principle V/shared task-commit responsibilities: runtime is verifier/committer,
   workers do not commit or adopt inherited work; planning/standalone retained artifacts
   still checkpoint under their existing writer contract. Minimal automated SQLite state
   is permitted, narrative STATE/reflection is still forbidden.

These are proposed amendment bounds/rationale, not edits or current governance. Parent
must include the exact operative amendment proposal in later review/owner approval before
implementation of conflicting contracts; version/amendment rationale follows Governance.
Current source-review and plan-authoring actions comply with current rules. No other
principle waiver or security/permission relaxation is proposed.

## Project Structure

### Documentation (this feature)

`spec.md` remains requirements truth. This installed plan pass produces `plan.md`,
[research.md](research.md), [data-model.md](data-model.md),
[contracts/README.md](contracts/README.md), declarative design schemas and
[quickstart.md](quickstart.md). `tasks.md` is deliberately absent; a separate fresh
producer owns it after specification renewal. No overall reviewer role is performed here.

### Planned source layout (not implemented)

```text
runtime/
  pyproject.toml                 # installable coherence_workflow package/CLI
  requirements.lock             # exact transitive versions/hashes, produced at implementation
  coherence_workflow/
    cli.py                      # start/status/resume, external owner answer validation
    engine.py                   # YAML→actual StateGraph, sync SqliteSaver
    registry.py                 # trusted handler/profile/skill capabilities
    intake.py                   # shared structured task/approval adapters
    authority.py                # upfront capability/spend admission from verified approvals
    interaction.py              # bound owner gate/input/control + durable outbox
    notifications/paseo.py      # explicit optional-mode public CLI UI adapter, no policy
    store.py                    # application transactions and migrations, same SQLite file
    projections.py              # state/events/metrics derived publication
    sessions.py                 # sole deterministic role-safe selector
    pi_adapter.py               # JSONL transport, lifecycle/host identity reconciliation
    tools.py                    # registered tool gateway, durable launch/drain custody
    containment.py              # own-child Linux cgroup-v2 capability/identity/empty oracle
    tool_process.py             # gated-start local process helper, not a daemon
    git_effects.py               # ownership, operation intent, focused commit/reconciliation
    verification.py             # real registered checks/evidence validity/gates
    workflows/coordinate.yaml   # one configured workflow, no engine name conditionals
    schemas/                    # delivered versions of reviewed design contracts
  pi-host/
    package.json, package-lock.json  # exact official Pi SDK dependency
    host.mjs                    # one process/session, no workflow authority
  tests/                        # focused unit + realistic integration, shared fixtures
scripts/coordinate-implementation # suite-relative CLI launcher, explicit --project
scripts/install-workflow.sh        # optional, explicit isolated runtime setup
```

Structure decision: existing repository is a skill/config suite without tracked root
Node package; root ignores manifests. A bounded `runtime/` Python package plus tiny
nested Node host is the minimum additional runtime, not a rewrite of skills or installer.
Future `.gitignore` exceptions track only nested host manifests/lock, ignore isolated venv
and runtime caches. Wheel packages YAML/schema resources. Optional installer uses a
suite-local isolated venv and local `npm ci`, never global packages. Explicit setup/network
permission remains required; ordinary adoption reports missing runtime rather than installs.
Launcher resolves its installation, accepts `--project`, never assumes this project's name,
branch, docs/memory paths or target cwd. No runtime binary/store is committed.

## Architecture and responsibilities

### Configured graph, not another orchestration engine

Compile every declared node and enumerated outcome→edge into LangGraph `StateGraph`;
compile with SQLite `SqliteSaver`, invoke with `durability="sync"`, run_id as thread_id.
Handlers return schema-validated small values; Python does not run an independent next-node
while-loop. The task-selector handler chooses the lowest approved-order dependency-ready
task; graph edges own control flow. Default graph's meaningful route is:

`intake → preflight → select_task → dispatch_implement → verify → checkpoint → select_task`;
no ready incomplete task yields precise dependency blocker. Exhausted implementation
moves to `review_final → accept` or `authorize_correction → repair → verify → checkpoint
→ review_final`. Known in-scope failed checks may enter configured repair; unknown causes
block. Code/gate nodes have no Pi session. Optional substantive review nodes use the same
finding/repair mechanism without making per-task review mandatory.

Registered handlers have version, input/output schema, legal outcomes, required capabilities,
side-effect class and role restrictions. YAML can vary supported handler/order/edges/profile/
skill without source edits, but cannot introduce arbitrary Python imports, eval, shell
snippets, code paths or new permissions. Static validation rejects unreachable/unknown
nodes, missing outcomes, dead-end nonterminals, unbounded cycles and paths bypassing mandatory
verification/checkpoint/approval/final-review invariants. Loops must be recognized task-progress
or budget-decrement loops; require terminal reachability and bounded failure paths. A configurable
graph is not permission to omit required safety nodes or reinterpret illegal results.

All config, handler/schema/engine/host versions, profile exact IDs/effort, resolved skill
content/dependency hashes, tools, permissions, trust/effective settings, task contracts and
approval provenance are pinned into the run identity. Resolve files safely beneath declared
roots, reject duplicate YAML keys/unsafe tags, bound input size, use safe_load, then schema
and semantic validation. No untrusted YAML executable commands: task checks reference trusted
registered check IDs plus schema-validated arguments. Registry additions require reviewed
code and original permissions, not runtime LLM creativity.

### Pi host and capability boundary

Python sends explicit create/open/prompt/telemetry/abort/drain/close commands with unique
request/operation IDs. A separate host process per session owns one Pi AgentSession. It
loads exact pinned SDK, explicit cwd, exact model/effort, verified resources/skills and
allowed tools/permissions; reports effective prompt/skill/tool hashes and model fallback.
It never chooses the next task, another session, profile, retry policy or owner answer.
Custom request_owner_input and bound steer/followUp/input delivery use the interaction
protocol below; workers never receive the parent ask_user tool.
No background cache-warming/unsolicited model work; configured internal provider retries
are observed and bounded, not new workflow attempts. User-supplied extensions/config cannot
silently add tools, mutate bindings, execute arbitrary startup code or bypass approvals.

Use actual `session.settingsManager.getCompactionSettings(session.model)` and current
context/stats, not a Python mirror of global/project merge. Trusted project settings are
explicit provenance, never blanket `--approve`. Compare requested/runtime-selected/outgoing
request-observed/provider-acknowledged separately. Request observations come from a host-owned
public `agent.streamFunction` wrapper: compose existing per-call payload hook (or SDK
agent hook for summary calls) **before** the final provider-payload guard; whitelist only
model/effort metadata, validate provider mapping before send. Extension exception swallowing
is not a security gate. The accepted [SDK probe](../../docs/evidence/workflow-sdk-validation/stack-integration-report.md)
proved this bounded composition with real outgoing turns and synthetic mismatch/summary-route
zero-send guards; actual compaction/retry were not induced. Permanent tests must cover the
shipped host and registered mappings (research R6–R7/R10).
Unknown observation stays null; known unsupported/mismatch/clamping/settings override blocks.
Unregistered observer mappings stop rather than guess an effort. No credential or payload
logging. Host custom tools proxy all mutations and child-process launches through the runner
registered tool gateway. Do not expose unrestricted SDK built-in bash alongside it. The
controller durably owns effect intent, launch identity and abort/drain custody before tool
execution; details are in the data model. Registered local command capabilities have explicit
argv/argument schemas, working-directory/environment/side-effect bounds and verified
containment. An owner-permitted shell can be a registered gateway capability, not unrestricted
SDK built-in bash or executable YAML; its local trusted-tool scope/permissions remain explicit.
If a task needs uncontained, adversarial or external tools, require an approved lifecycle
capability and its proof or stop with
a precise missing-tool/security blocker. Do not silently install a sandbox, assume an owner
permission is containment, or advertise path/tool instructions as OS isolation.

### Session rotor and lifecycle

One selector applies to **every agent node**, with configurable policies. A parked owner
question continuation is a higher-priority **original-conversation pin**, not a new greedy
assignment: see interaction below. Missing/unsafe/insufficient/unknown headroom blocks that
continuation for explicit owner recovery, never substitutes fresh. For ordinary assignments:

1. Require dependency-ready authorized work, no unresolved live work, matching role family,
   exact profile/model/effort, skill/resource hashes, tools, permission/trust/settings envelope,
   worktree and context affinity. Reviewer isolation is non-overridable.
2. Fresh-only creates a fresh compatible session. First final review is always fresh;
   later correction rounds may reuse only that reviewer's own eligible context/range lineage.
3. Repair prefers original eligible implementer; implementation prefers eligible same-group
   sessions (`context_group` initially story). Do not mix reviewer and implementer histories.
4. Admission uses reliable fresh telemetry: threshold=effective window−reserve while automatic
   compaction enabled; free=threshold−current estimated occupancy; eligible at >=150000, not
   149999. Missing/stale/disabled/unresolvable inputs deny reuse. Fresh is allowed only after
   old work is reconciled; otherwise precise safety blocker.
5. Remaining candidates sort by most recently **settled** monotonic settlement sequence,
   then stable session ID ascending. Persist eligibility inputs/reason and candidate choice.

No billed-token cutoff, task batches or inference-based routing. Reuse never merges task
contracts/checkpoints. Request settings remain unchanged; different profile starts fresh.
After host restart, exact saved conversation may be opened only after process/tool quiescence,
identity/branch/resource/profile verification and new telemetry; in-process PoC reuse did
not prove durable reattachment. The later accepted interactive fixture demonstrates one
original conversation reopened after orderly question park (new PID), not arbitrary recovery
or pressure-safe continuation. Unknown continuation or corrupt session blocks reuse; after
safe reconciliation an authorized resume of **ordinary non-pinned work** may use fresh
session instead. A pending owner-answer continuation remains original-only or blocked.

Subscribe before prompt; drain stdout continuously, correlate responses, serialize prompts
through current start/settled generation; stale events cannot settle current work. Accepted
prompt and agent_end are not success. Capture retry/compaction/tool activity and current
agent_settled plus idle/no-pending-tools before after-task telemetry, verification/commit/reuse.
Timeout/error/exit poisons eligibility; record attempt interrupted/stopped/orphan/unknown.

Admission does not prevent long-task compaction. While active, monitor lifecycle and fresh
telemetry at supported safe boundaries with a bounded configurable monitor interval. At
pressure/unknown telemetry/compaction, stop new dispatch, abort and drain using supported
API, establish all tracked tools/descendants quiescent, reconcile actual files/Git/operation
identity, then block for authorized resume/remediation. Never start a fresh writer merely
because host exited. Do not promise a universal hard interrupt deadline or zero compactions.

### Durable effects, locks and projections

See [data model](data-model.md) for transactions, replay and schema ownership. Use one
worktree identity/lock location resolved through Git's per-worktree administrative directory,
not each run directory; different run roots still contend. POSIX advisory lock is held for
mutation; lock file identity/custody persists across host crash as recorded unresolved work.
Kernel-lock release alone does not permit dispatch into an orphan. The same lock binds one
project-local authoritative database for all runs (no arbitrary new DB on a new run-dir).
Acquire the lock, then scan/reconcile durable run/host/tool identities across that worktree. PID+host boot+process
start+nonce/process group and actual tool state are required; never trust stale PID alone.
Separate status is read-only and launches no agent; it reports the durable run as interrupted
when runner heartbeat/process identity is not live, not as continuing in background.

Capture baseline HEAD, index entries, staged/unstaged/untracked path/hash ownership and
explicit task paths before mutation. Refuse already-dirty owned overlap unless separately
resolved/authorized, symlink/path escape, unrelated drift or unknown ownership. Preserve
unrelated staged/unstaged/untracked/custom files exactly. Worker tools cannot commit; runner
checks real REQUIRED evidence and owned diff before path-limited Git commit with unchanged
hooks/signing/identity. No empty commit for read-only/no-change outcomes. Git failure blocks;
never configure around it, disable safeguards, stage broadly, push/reset/rewrite/discard.

Persist effect intent/operation key before launch or Git; application result/events persist
before returning handler output to LangGraph. On replay first inspect receipt and actual
process/files/HEAD/index/diff; return recorded result only if still applicable. Recover an
existing exact focused commit using operation trailer/identity **plus** baseline parent,
owned diff/tree and current HEAD/residual evidence; subject alone is insufficient. Post-write
partial state does not authorize re-dispatch. Unknown results, commit hook mutations, HEAD
drift or external effects block pending diagnosis. External network/deploy/database writes
require original approval and registered reconciliation; no generic retry makes them safe.

### Containment capability and supported boundary

Use one registered **Linux delegated cgroup-v2 adapter** for supported trusted local tools;
no generic service/container orchestration platform. Project configuration identifies an
approved delegated parent via capability reference, never a hardcoded service path. Preflight
verifies actual owned child creation/placement/kill plus readable `cgroup.events`, membership
before tools spawn, and trusted receipt UID/device/inode/name. Kill only validated run/task-
owned child groups, never the service/ancestor/root or unknown group. No root privileges or
automatic service setup are assumed by runtime. Missing permission or identity blocks; no
PID/PGID-only fallback. Other platforms/capabilities need explicit owner choice/proof.

The [accepted four-case local probe](../../docs/evidence/workflow-process-validation/README.md)
cleared ordinary local lifecycle feasibility after owner administrative delegation. It covers
worker exit 0, exit 1, SIGKILL with setsid+TERM-resistant descendants, and separate-controller
reentry from a checked receipt. Kernel inherited membership and populated=0—not enumeration—
proved emptiness; the outside sentinel survived. Parent independently reran the same cases.
This supersedes earlier unavailable-delegation discovery **for this environment**, not every
installation. Production must reverify its configured capability and test durable placement/
registry crash boundaries. Do not schedule another equivalent feasibility experiment.

Supported boundary is cooperative/trusted same-user local process tools, not malicious same-
UID escape protection: writable ancestor controls may permit explicit migration. No arbitrary
remote jobs, different users, container or adversarial tracking promise. Those require their
own approved lifecycle/containment contract or BLOCKED. Direct runner-owned file syscalls and
registered command/Git/hook effects retain ownership/permission gates; tool instructions or
cgroups here are not a filesystem/security sandbox.

Long-lived Pi **session host** stays tracked in its own host scope while idle for greedy
reuse; it does not live in a per-task tool group. Runner tool gateway places each task's
process tools in its own registered group before release. At logical tool/task completion
(including success/failure), a nonempty task-tool group produces durable **ORPHAN_PROCESS**,
`replacement_allowed=false`, blocked status and ineligible reuse. Worker success cannot
suppress it. Alarm history survives cleanup; only observed owned-group empty plus partial
file/Git reconciliation yields a recorded resolved disposition, never silent success.
Notifications are optional/nonblocking; this authoritative alarm is mandatory. On runner/host
exit, resume scans both host and task scopes; an intended idle host is not mistaken for an
orphan, while unexpected live tool work always blocks. Terminating/replacing a host requires
its own validated scope drain and does not waive task-tool cleanup.

### Verification, approvals and repairs

Versioned task intake is one shared contract across direct and Standard adapters, not
narrative parsing. Preserve source IDs/order/ownership/dependencies/context_group, REQUIRED
criterion/check/pass/evidence/manual/permission fields and optional distinction. Structured
legacy subsets are admitted only when complete and provenance-verifiable; absent fields
return to producing review/renewal, never mass-convert old prose or fabricate history.

Approval status is derived from external owner-answer evidence bound to exact artifact
hashes/sections/review/scope/config and original authority, not a trusted boolean in YAML.
For CLI gates, runner emits a scoped request+nonce; explicit operator answer through resume
is bound to it and current hashes, records approver/provenance and denial/cancellation.
Conversational interface can relay that answer, not synthesize it. Permissions/manual sample
STOPs cannot be replaced by model success. Drift invalidates affected gates/evidence only.

Runner executes registered real REQUIRED checks on final owned bytes/environment, validates
nonempty selectors/oracles and maps each ID to satisfied/failed/insufficient-evidence.
Demonstrated criterion violation is failed; missing/unrun/stale/conflicting proof is insufficient.
Shared checks can map several IDs; optional green cannot release dependents. Review judgment
is separate from check exits. Schema-invalid model returns block; narrative never picks edges.

Inspect failed invocation/lifecycle/partial commits/checks before diagnosed in-scope repair.
Preserve valid work, prior attempts and original contracts; rerun invalidated items. Configured
`max_repair_attempts: 2` is the approved default, mutable only through authorized config
renewal, no escalation. Budget scope is the original failing task or review gate, retained across focused correction
IDs/rounds so a new repair ID cannot reset it. Count each dispatched repair, even interrupted
ones; retry transport
errors cannot evade the budget. Unknown/environment/permission/contract gaps block rather
than automatic repair. Known safe internal provider retries are separately bounded/observable.

Final independent reviewer receives complete base→current committed range, source/tasks/
approvals and criterion-mapped evidence with read-only tools. Every finding has schema-valid
severity/location/criterion/evidence/disposition. Accepted in-scope findings become separately
authorized focused correction task contracts and individual commits, then affected checks
and reviewer loop. Reviewer never becomes producer. Scope-changing finding returns owner gate;
no silent task invention. Final acceptance requires all dispositions resolved and independent
review of current full range; implementation completion remains a separate status.

## Interaction and maximum autonomy (owner-directed correction)

### Upfront authority and known-gap aggregation

Task intake/run config declare an authorization envelope with exact selected profiles and
paid model/service/test/network/external/mutation capability/action scopes plus verifiable
owner approval references. Production numeric budgets are **not selected** by this plan or
its PoCs; unresolved/denied/absent authority blocks affected paid dispatch. Preflight computes
all **known** missing permissions/capabilities/spend choices together before any task starts,
using manager-readable impact/options. Persist usable runtime/package/catalog/credential
references and environment manifest before launch; revalidate on separate-process answer/
resume, not depend on transient parent environment (observed missing-env failure).

Within approved scope, worker resolves technical implementation/debugging and small isolated
preapproved tests without cost/tool-trivia questions. Only necessary manager-answerable
product/priority or genuinely unexpected material scope/complexity/time/cost deviation asks,
with why blocked, options/recommendation and impact. Unknown auth/safety/permissions still
fail closed; autonomy is not permission to spend or expand scope. Category/schema checks,
existing envelope constraints and recorded rationale assist, but cannot universally judge
question relevance; the fixture's forced cosmetic title is not a policy to ask every default.

Where owner sets limits, persist run-wide reservations before outbound admission, including
all attempts/host restarts/allowed retries/summaries, and reconcile unknown spent reservations
without refund-by-guess. Disable unsupported hidden/background retries/warming. Request
admission limits are enforceable only at verified send boundaries; provider hard limits need
registered version-matched proof. Generic maxTokens was ignored by the tested Codex builder;
do not advertise token/dollar hard caps or invoice accuracy from it, per-host max5 or catalog
estimates. An approved scoped-spend envelope may have no numeric cap only by explicit owner
selection; never invent an amount or infer permission from the planning/fixture approval.

### Rare worker question: normal tool completion, durable park, original answer

Worker uses registered schema-valid **request_owner_input**, never ask_user. The tool request
is persisted as an operation tied to run/task/node/attempt/role/original session+branch,
source/task/approval/config/resource hashes and gate nonce. Enter parking, freeze new
conflicting tool/model work and drain current operations; the custom tool returns a **normal
completed result with terminate:true**, not an unfinished tool suspended for a human.
Pi0.87.1 ends automatic follow-up only when all tools in that batch terminate. Require an
exclusive question batch or verified all-tools termination; mixed/unsettled/unknown cases
block safely rather than treating the single-tool fixture as universal arbitrary-tool proof.
Await current prompt+agent_settled+idle and actual task-tool quiescence before SQL pending gate
and LangGraph park interrupt. ToolUse stop reason here is expected, not implementation success.
Persist the question/receipt before exit; crash around tool result/checkpoint requires operation
reconciliation, not blind prompt replay. Only after durable park may notification publish.
Configured agent handlers declare
owner_input_required→registered park/continue_original transitions with saved originating
node/visit; do not re-run the original ask node or add a second scheduler.

The pending gate **pins ORIGINAL persisted conversation and role**, not OS process. Parent
answer or CLI input must match pending gate/input IDs+nonce, exact original session/branch,
current source/task/approval/config hashes and verified owner provenance. Accept once in SQL
with input ID UNIQUE, invalidate stale authority, and persist answer plus delivery obligation
before dispatch. Reopen exact saved conversation after safe custody/role/profile/resources/
headroom validation, deliver answer as a new bound user envelope **before continuation**,
then require delivery receipt/current settlement. Never reask merely because transport/reentry
failed after acceptance. Unknown delivery is reconciled from persisted conversation/input ID,
not sent twice blindly. No >=150k fresh-session shortcut while answering; missing/unsafe/
insufficient or unknown original headroom is BLOCKED for explicit owner recovery/cancel or
separately approved remediation. Source/scope-changing answers renew producing approvals;
original session pin never authorizes profile/role/context mixing or bypasses permissions.

### Required interactive parent wake, portable standalone mode

Core engine+CLI has no Paseo dependency. Run selects **standalone** (pending/answer/control CLI)
or **interactive_parent** with an explicitly registered question transport and question tool.
For the tested mode use public pinned Paseo0.9.2 inspect/send --no-wait --prompt-file, fixed
argv, exact registered launching recipient; no commands/addresses from worker prose. Do not
build a generic messaging platform or simultaneously implement a native-Pi plugin. Public
pi.sendMessage(triggerTurn/followUp) extension is an unproven alternative needing explicitly
loaded approved capability and its own proof; no raw private supervisor-channel/file writes.

Production launch interface captures current actual parent runtime identity, target worktree,
selected adapter/capability/permissions and question-tool availability. Cross-check public
transport inspection plus a run-bound parent readiness challenge/ACK and actual runtime
session/tool provenance, not caller flags/nonce alone. Fixture IDs bind but do not authenticate
arbitrary users; production trusts restricted local runtime/SQLite ownership and genuine owner
input path, not worker-written approved files or fabricated opaque tool IDs. Changed recipient/
session or permissions requires explicit rebind verification before any owner-question delivery.

Runner transactionally records an outbox item for eligible parked question. Adapter wakes the
**same launching/status parent**, whose thin interface reads authoritative pending status,
actually calls its registered **ask_user**, and submits the real answer receipt through runner
answer API. Parent may explain status/relay controls, not choose tasks/profiles/sessions,
acceptance/repair or Git. This reconciles “No background LLM wakes up to decide what to do.”:
a parent wakes for prescribed tool/dialog facade work, not orchestration decisions.
Interactive launch preflight fails without selected transport+ask_user readiness; never silently
substitute manual polling. Actual tool invocation/answer provenance must be observed; prose
claims cannot release the gate. If facade does not invoke it, pending delivery is visible and
no worker resumes. Scope/approval decisions still use original owner gates.

Outbox stages `recorded → transport_queued → parent_received → question_tool_invoked →
answered` are distinct. Stable event/input IDs permit at-least-once transport, parent dedup
before asking and durable answer acknowledgement. Crash around UI invocation before receipt
must reconcile actual tool provenance; unknown state blocks reasking, not an exactly-once
external-dialog guarantee. Busy delivery must use verified supported
queue semantics or bounded retry; do not assume a send receipt means the parent woke. While
runner lives, deterministic adapter retries under bounded policy; on host exit/outage no
background progress is promised. UI loss leaves durable pending/transport blocker; independent
CLI pending/answer stays usable. Reconnect/reentry validates parent/run identity and resumes
only unresolved outbox items without reasking answered gates. No required always-on daemon/
LLM scheduler. Production parent-busy/outage/reconnect/dedup/auth/crash tests remain required;
fixture tested actual idle wakes, not those guarantees. Optional completion/block/failure
notifications remain nonblocking and never replace this required question delivery path.

### Anytime owner inquiry/steer/follow-up/pause

Accept bound owner control at any time via CLI or parent facade; persist input IDs, source/
approval/config/run/task/attempt/session/role and intended action. Receipt is not delivery.
At an idle/preflight boundary, run-scoped inquire/pause/cancel
has no fabricated worker/session identity; steer/followUp requires an actual current session.
Known upfront authority gates are startup permission decisions, not worker technical questions.
Runner validates active identity/scope/envelope, routes supported SDK steer/followUp at an
execution boundary, records **received / queued / SDK-delivered / worker-acknowledged**
separately with evidence. Wrong/stale/duplicate controls cannot dispatch/restart or silently
move to another role/session. Out-of-scope controls are blocked for producing approval; a
new approved binding/input is needed after scope changes. Pending question controls do not
unpin its original conversation or masquerade as the answer.

Inquiry returns recorded facts, or queues a worker inquiry with an observable response;
no reading private reasoning or promising that acknowledgement proves understanding or
compliance. SDK enqueue does not stop a running shell. Explicit pause/cancel uses existing
abort/drain/cgroup+partial-file/Git reconciliation before checks/commits/replacement. Orderly
question park and cooperative fixture controlled_wait are not arbitrary preemption proofs.
The user may cancel/pause even while question delivery is unavailable, subject to actual safe
quiescence; unknown tool state remains a visible blocker/orphan alarm, never false paused.

## Ordered rollout stages (architecture outcomes, not tasks)

### Stage A — Remaining integration risk bounded before reliance

Consume the **completed**, parent-accepted SDK and four-case local lifecycle probes in
canonical research; do not repeat them or stack selection. The SDK probe's real negative
result (dead host leaves detached tool writing) makes durable supervisor/tool-launch custody a prerequisite to the first production
mutation. Establish actual production worktree-wide lock + operation/process registry +
gated-start/drain helper before enabling mutating tools; also consume completed interactive
proof (R13), and establish durable input/pin/outbox/authority before enabling interactive
dispatch. No repeated interactive PoC. Test crash between launch intent,
identity persistence, release and settlement. This remaining risk reduction belongs to the
production helper delivery with permanent realistic tests, not another disposable selection
experiment. Durable reattachment and real pressure/compaction/retry remain unproven: prove
them in the shipped adapter at their earliest seam before dependent reliance, with original
permissions. Failed/NOT RUN required proof blocks only affected reliance. Retain canonical
stack/SDK/process probes through consumers; no duplicate harness/platform or separate routine cleanup stage.

### Stage B — Usable durable runner alongside legacy, opt-in only

Deliver real graph adapter/registry/schema/intake-independent engine, SQLite operation ledger,
Pi host using Stage A custody, authority admission and question/control protocol,
checks/commits/status/projections/pending/answer/control and explicit resume, with permanent
unit+integration tests of the actual helpers. Stage A evidence must apply to shipped composition.
Legacy remains default only temporarily; never both controllers mutate one worktree/run.
No entry cutover until correctness/permissions/recovery checks pass.

### Stage C — Approved task contracts and operative policy integration

Both task adapters emit the shared structured subset including explicit upfront authorization
envelope and preserve known-gap preflight/inside-envelope autonomy. Reviewer/repair/owner gates preserve
origin semantics. Review exact constitution/task-commit adaptations and obtain their required
owner approval before operative changes. Test TinySpec/Standard/legacy intake and stale/denied
manual cases, including in-progress-worker reconciliation. Planning profiles remain owner-selected;
implementation profiles move to approved config, not complexity tables. FR-040 adds [execution-profile-aware planning](execution-profile-planning.md): collect intended coding class/effort before architecture/decomposition, separate it from planner profiles, tailor task scaffolding with explicit qualitative assumptions, and preserve intent/rationale through both task adapters. T008 implements and verifies this without per-task routing or weakened acceptance. Historical approval/review does not cover this amendment. New runner may consume
only a complete approved contract, never silently reinterpret old artifacts.

### Stage D — Coordinate Implementation entry cutover

Replace execution skill with thin start/status/pending/answer/control/authorized-resume
interface to the CLI. Interactive mode must automatically wake the original interface and
actually use ask_user with verified receipts; standalone remains independent. Update
planner/handoff/adoption/review/debugging consumers to runtime ownership; preserve planning
stage order/delegation/approvals. Cut over only after real multiple-task, repair/final-review,
manual-owner, restart/dirty-tree/no-duplicate evidence passes. Explicitly stop/reconcile legacy
children first. Existing project instructions refresh only within owner-approved marked bounds.

### Stage E — Remove obsolete execution obligations and prove preservation

Remove subjective implementation batching/model-routing/escalation/local-task-count/LLM
checkpoint-memory machinery and their obsolete tests. Retain separately owned planning
selection rubric and its consumers; no global deletion of model policy or historical evidence.
Update static guards to new runtime responsibility while preserving REQUIRED/approval/checkpoint/
independence/path protections. Verify no active conflicting execution references remain.

### Stage F — Operating docs, acceptance and reversible rollout

Document actual installation/CLI/schema/config/telemetry/security/recovery/rollback behavior;
compare docs against implemented interfaces, not illustrative commands. Gate final acceptance
on permanent realistic tests and fresh independent full-range review. Report NOT RUNs and
remaining permissions, version applicability and implementation vs acceptance separately.
Retain proof/evidence; delete disposable infrastructure only after all consumers validated.
After future global skill changes tell owner to run `/reload`.

Dependencies: A→B→C→D→E→F for these meaningful outcomes, with checks/docs inside coherent
delivery where possible. Task producer owns finer causal decomposition, not one task per noun.
No parallel writers; stages do not prescribe artificial prototype/consumer/cleanup task chains.

Rollback: on failed acceptance, unsupported capability, unsafe recovery or contract drift,
stop dispatch, drain/reconcile writers and preserve SQLite/Pi evidence, focused commits and
unrelated work. Disable new entry; **do not automatically resume legacy** against partial runs.
Legacy may be explicitly selected only for a reconciled compatible current contract with still
valid owner authority and no live writer; otherwise remain blocked. No DB downgrade in place,
Git reset, deletion of STATE/history or rollback of accepted task commits. Restore entry/config
through reviewed focused changes; new runtime reads pinned old runs read-only or blocks on
unsupported versions. Host exit stops work; no required daemon.

## File-by-file impact inventory

Paths below are future adapt/remove/preserve decisions, **not edits made now**. Relevant
SKILLs and named support seams were read; large fixture suites were inspected by actionable
carriers/classes rather than treated as runtime proof. Reinspect exact bytes before adaptation.

| Existing path | Planned action / preserved contract |
| --- | --- |
| `skills/coordinate-implementation/SKILL.md` | Replace LLM control with launch/status/pending/answer/control facade; interactive original parent must wake+actually ask_user, no orchestration authority; preserve origin/independence |
| `skills/coordinate-implementation/references/batch-routing.md` | Remove implementation applicability/batching/escalation authority; retain planning six-factor selection in renamed `skills/planner/references/profile-selection.md`, update links; historical research remains |
| `skills/coordinate-implementation/scripts/test_batching_contract.py` | Remove obsolete symbolic routing/batch/escalation/feedback tests; move planning-only rubric cases to planner tests; migrate item_dispositions, readiness, invalidation and Git safety semantics to actual runtime tests, not delete them |
| `skills/coordinate-implementation/scripts/test_intake_contract.py` | Replace local<=3/batch-table obligations with thin entry/no-authority and real intake schema/approval coverage |
| `skills/coordinate-implementation/scripts/test_state_contract.py` | Preserve no STATE/custom dirt/unknown-active safeguards; replace conversational recovery walkthrough with CLI/reconciliation assertions |
| `skills/task-generation/SKILL.md` | Both adapters emit structured versioned subset, context_group, upfront authorization envelope and unchanged REQUIRED contract; remove batch-selection/handoff/profile-assessment language, keep no task-profile assignment and producing renewal |
| `skills/task-generation/scripts/check-task-order.py` | Preserve source-order/story/dependency checks; add structured contract order/ID validation without inferring contracts from prose |
| `skills/task-generation/scripts/test_check_task_order.py` | Add structured parity/negative fixtures; preserve existing earlier-prerequisite/contiguity cases |
| `skills/task-generation/scripts/test_contract.py` | Both adapters retain acceptance/dependency/manual semantics and prototype lifetime; replace batch brief expectations with task-envelope mappings |
| `skills/planner/SKILL.md` | Handoff pinned authority/runtime/interactive-launch provenance to runtime start under original planning-only exception; replace whole-batch union/implementation batching selection references, keep planning selection/delegation/Stage gates unchanged |
| `skills/planner/references/approval-and-recovery.md` | Preserve current-content/brief/mechanical/legacy approvals; add executable origin intake and external scoped gate evidence, no implied implementation |
| `skills/planner/references/dependency-research.md` | Preserve canonical spans/classification/bounded writes; update only execution-owner terminology if necessary |
| `skills/planner/references/early-risk-reduction.md` | Preserve proof scope/lifetime/producer boundaries; runtime release consumer, no extra mandatory prototype |
| `skills/planning-brainstorming/SKILL.md` | Repoint planning-only selection owner, remove implementation-batch handoff clauses; dialogue remains planner-owned |
| `skills/planning-brainstorming/scripts/test_contract.py` | Repoint routing/handoff carriers; retain preselection/read-only/owner-answer boundaries |
| `skills/tiny-spec/SKILL.md` | Update final handoff/context_group consumer, preserve compact source/direct tasks/combined approval and planning profile policy |
| `skills/delegating-architectural-planning/SKILL.md` | Keep installed one-pass Sol/medium adapter; update execution handoff/rubric links only |
| `skills/requesting-code-review/SKILL.md` | Runtime independent full-range review request integration, same role-safe question pin if review asks; generic self-review fallback cannot satisfy workflow independence |
| `skills/requesting-code-review/code-reviewer.md` | Add schema-bound findings interface while retaining evidence/location/severity/read-only/no invented base |
| `skills/receiving-code-review/SKILL.md` | Route authorized correction task+commit and owner scope gate, never direct reviewer writes |
| `skills/scientific-method-debugging/SKILL.md` | Empirical diagnosis consumes attempt/effect/input evidence, autonomously resolves approved mechanics/tests; prohibit unknown retry, preserve focused fail-then-pass fixes/permissions |
| `skills/handoff-prompt/SKILL.md` | Runtime run/config/approval/parent/question-pin/input identities, spend envelope and blockers, no invented session portability or required narrative ledger |
| `skills/finish-session/SKILL.md` | Read actual runtime acceptance/status and schema owner, no narrative persistence; preserve docs/feedback safety |
| `skills/initialize-coherence/SKILL.md` | Optional runtime and mode-specific interactive transport/question-tool capability reporting, approved marked association refresh; authoritative runtime schema docs required; no silent install/mass task conversion |
| `skills/initialize-coherence/scripts/test_contract.py` | Adjust association/runtime owners while preserving custom/dirty/approval/SpecKit capabilities |
| `skills/initialize-coherence/scripts/fixtures/workflow-ownership-outputs.json` | Add bounded runtime-owner association cases; preserve custom content |
| `skills/initialize-coherence/scripts/fixtures/source-contract.json` | Preserve immutable historical source ledger; adapt only active-consumer mapping if operative behavior changes |
| `skills/initialize-coherence/scripts/fixtures/scenarios.json` | Add runtime missing/legacy reconciliation cases without weakening existing asset/adoption gates |
| `skills/initialize-coherence/scripts/fixtures/unsafe-permissions.json` | Retain all denial/dirty/custom/asset guards; add runtime unauthorized-start rejection |
| `skills/initialize-coherence/scripts/fixtures/old-initialize-coherence.txt` | Preserve historical baseline, never rewrite to make tests pass |
| `skills/memory-handling/SKILL.md` | Remove execution batch/coordination-feedback intake obligations, keep technical gotchas and planning/closeout use |
| `skills/memory-handling/references/project-coordination.md` | Remove execution-path LLM feedback/routing paperwork; preserve explicit feedback-only owner for planning/manual use, STATE prohibition and historical content |
| `skills/memory-handling/references/task-commit-contract.md` | Add explicit runtime verifier/committer responsibility; worker no Git, replay recovery guard; preserve per-task focused mandatory checkpoints for all retained work |
| `skills/memory-handling/scripts/test_coordination_contract.py` | Keep no inferred feedback/no STATE/symlink/dirty protections; remove execution-consumer bookkeeping expectations |
| `scripts/check-planner-workflow.py` | Update coordinator-specific ROUTING/VERIFICATION carriers to runtime interface; preserve planning-profile and actual-stage guards, no footer-only substitutions |
| `scripts/test-planner-workflow.py` | Preserve stage authority/brief/research/delegation/installer safety cases; replace only implementation-batch coupling and update selection reference paths |
| `scripts/planner-trace.py` | Preserve actual owner-answer/continuation ordering; recognize runtime start only when authorized, planning-only remains no execution |
| `scripts/planner-rpc-smoke.py` | Preserve opt-in read-only Pi smoke, no implicit live run; no reuse as production runner; adjust only changed expected handoff |
| `scripts/fixtures/planner/standard-tasks.md` | Add structured illustrative subset with explicit no-approval fixture status |
| `scripts/fixtures/planner/tiny-tasks.md` | Same contract semantics as Standard, no fabricated approval |
| `scripts/fixtures/planner/risk-standard-tasks.md` | Preserve bounded informational prototype and gates in structured subset |
| `scripts/fixtures/planner/risk-tiny-tasks.md` | Preserve same prototype/genuine producer/lifetime semantics |
| `scripts/fixtures/planner/approval-inventory.json` | Update only actual handoff content expectations, preserve exhaustive ordered briefs/digests |
| `scripts/fixtures/planner/approval-artifacts.md` | Keep trusted scope/approval fixture semantics |
| `scripts/fixtures/planner/mechanical-corrections.json` | Preserve unchanged approval-equivalence and substantive-renewal cases |
| `scripts/fixtures/planner/tiny-spec.md` | Preserve source truth fixture |
| `scripts/fixtures/planner/risk-walkthroughs.md` | Update runtime consumer terms only, keep no duplicate proof chain |
| `scripts/check-skills-lint.sh` | Wire new runtime offline tests and updated contract checks; keep skill portability/frontmatter and custom-dir mode |
| `scripts/check-task-commit-contract.py` | Replace coordinator-owned recovery assertions with runner responsibility; preserve no-waiver/no duplicate evidence checks |
| `scripts/test-task-commit-contract.py` | Retain hook-failure/scoped Git/unrelated/unknown ownership fixtures; add runtime commit/replay boundary |
| `scripts/install.sh` | Optional explicit workflow setup mode/capability report, no automatic new Python/SDK install on ordinary use |
| `scripts/install-links.py` | Keep foreign-link/race protections; retain coordinate skill name, discover launcher through installation without replacing foreign binaries |
| `scripts/probe-pi-load.sh` | Keep opt-in paid discovery smoke; update expected thin entry only if actual advertisement changes |
| `.pi/prompts/speckit.implement.md` | Route approved structured handoff into runner, no competing implementation LLM; preserve applicable before/after hook and owner gates |
| `.pi/prompts/speckit.tasks.md` | Shared structured task-generation adapter, preserve installed capability and create-only stage |
| `.specify/templates/tasks-template.md` | Replace conflicting parallel-writer/sample optional-test expectations with shared versioned subset and REQUIRED semantics; retain project customization boundaries |
| `.specify/integrations/pi.manifest.json` | Reconcile only intentional changed prompt hashes/entries after review, no false upstream/pristine claims |
| `.specify/integrations/speckit.manifest.json` | Reconcile intentional template hash when adapted, preserve installation provenance |
| `.gitignore` | Narrow nested-host manifests/lock exceptions and local venv/runtime ignores, no credentials |
| `README.md` | Replace implementation batch/routing/control text with actual install/start/status/resume/limits; retain planning path/profile/approval rules |
| `REQUIREMENTS.md` | Replace implementation selection section with configured runtime/SDK/schema and optional-mode Paseo transport requirements (no core Paseo dependency); preserve planning Sol/medium/shared profile policy and installed SpecKit gates |
| `AGENTS.md` | Approved marked local association: runtime ownership/recovery/docs links; preserve portability/custom content |
| `.specify/memory/constitution.md` | Explicit owner-governed amendments above, not silent rewriting or reopening stack choice |
| `docs/index.md` | Route future runtime schema/operating owners, replace active coordinator batch/recovery links, preserve historical research discoverability |
| `docs/plans/planner-regression.md` | Update actual runtime-handoff validation scope; preserve static/live distinctions |
| `docs/pi-settings-sample.md` | Compare actual defaults with new configured profiles; remove execution override/routing contradictions only, retain attributed planning configuration |
| `stack-validation-report.md` and `docs/evidence/workflow-stack-validation/**` | Preserve immutable completed PoC evidence/limits; no repeated selection or retroactive SDK claim |
| `docs/evidence/workflow-sdk-validation/**`, `docs/evidence/workflow-process-validation/**` and `docs/evidence/workflow-interaction-validation/**` | Preserve canonical completed focused probes, real negative findings/limits; no repeat or copying toy code into production |
| `memory/**`, existing STATE/custom docs, historical plans/reviews, unrelated skills | Preserve; no execution cleanup deletes evidence or technical guidance |

New permanent documentation owners proposed with runtime delivery: `docs/coordinate-implementation.md`
(operation/security/rollout/rollback) and `docs/coordinate-implementation-schema.md` (SQLite and
published schemas). Their addition and docs/index routing belong to future authorized tasks,
not this pass. Inventory expansion beyond these known impacts requires causal evidence and
applicable scope approval, not a whole-repository rewrite.

## Verification strategy and task-intake handoff

[Quickstart](quickstart.md) gives future scenarios and permissions. These are requirements,
not executed production outcomes. Stable design check labels below are **not task IDs**;
task producer maps them to task-local REQUIRED IDs without weakening criteria.

| Check | Required observable / lowest sufficient layer | FR coverage |
| --- | --- | --- |
| V-config | Schema+semantic rejection before side effects; real StateGraph route changes through registered YAML; illegal result/version/role/edge rejected | FR-001–005, 024 |
| V-intake | Direct/Standard/legacy provenance, order, deps, ownership and REQUIRED/manual/permission parity; stale/denied/cancelled approval blocks; no narrative conversion | FR-007–010, 032 |
| V-binding | Actual pinned SDK host skill delivery/exact allowed tools/trust/settings, final outgoing model/effort observer and drift-before-send guard | FR-005–006, 013, 016 |
| V-session | Every role/fresh-only/repair preference/fresh-first reviewer, latest-settled tie; 150000 vs149999/unknown and settings override; no live-work reuse | FR-011–017 |
| V-metrics | Real two-task attribution, restart/reset/null/zero cache, start/end context vs cumulative counters; code nodes no fake Pi identity | FR-020–021 |
| V-recovery | Real engine+SQLite+SDK post-write, mid-tool pressure/orphan and post-commit kills; durable launch registry across controller restart, guarded compaction/retry, ledger/checkpoint ordering, no duplicate writers/commits/lost changes | FR-015–019, 025–027 |
| V-custody | Two run dirs contend same worktree lock; owned child-group identity/placement/empty proof, mandatory ORPHAN_PROCESS alarm before blocked replacement; idle Pi host distinct from tools; unrelated staged/unstaged/untracked/STATE/custom bytes preserved, path/symlink/tool denial/hooks honored | FR-006, 010, 024–026 |
| V-evidence | Actual REQUIRED oracle failure vs insufficient proof, affected invalidation/shared mappings, manual sample STOP, optional green cannot release | FR-022–023 |
| V-review | Real/schema review findings, diagnosed bounded repair zero/two/exhaustion and separate focused correction commits, renewed full-range independent review | FR-027–030 |
| V-status | Separate no-agent status, host-exit interrupted status, projection torn-tail/replay idempotency, authoritative ordering/schema | FR-018–021, 024 |
| V-authority | Declared paid/service/test/network/external/mutation envelope, real approval refs and all-known-gap preflight; no paid dispatch absent/denied/unknown authority, no repeated inside-envelope technical questions | FR-035 |
| V-interaction | Actual same-parent wake+ask_user, completed safe question park, original saved conversation answer-before-continuation, bound inputs/outbox/dedup; missing/unsafe/unknown-headroom original blocks, never fresh substituted | FR-036–038 |
| V-control | Active inquiry/steer/followUp receipts vs enqueue vs observed ACK; scope renewal, pause/cancel drain/cgroup; UI busy/outage/reconnect failure visible with CLI answer, no manual-polling fallback in interactive mode | FR-037–039 |
| V-migration | Stage-cutover/legacy return/rollback rehearsal, obsolete execution obligations gone, planning profile rules/gotchas/history intact, docs match CLI/schema | FR-031–034 |

Coverage review: FR-001–039 all map above; SC-001→V-intake/evidence/custody, SC-002→V-config/binding,
SC-003→V-session/binding, SC-004→V-recovery/custody, SC-005→V-metrics/status,
SC-006→V-evidence/review, SC-007→V-migration/intake, SC-008→V-interaction/control,
SC-009→V-authority/control. Original source→FR mapping remains in spec.
Known local unit checks use fixtures; actual SQLite/Git/host process seams need integration.
Live provider, external tools, installs and paid checks need explicit scoped authorization;
NOT RUN is not PASS and cannot release their consumers. No synthetic sandbox/security or
power-loss/multi-host claim. Final independent review is required, not this self-review.

Task producer must read current renewed spec first, this derived sequence and canonical
research; emit complete versioned task envelopes and human tasks with stable IDs, approved
source provenance, deps/context_group/owned paths, actual upfront authorization/spend envelope, interface mode/
required parent delivery capability and original-session pin/input contracts, REQUIRED criterion/check/pass/evidence and
original manual/permission gates. Do not put execution family classes on tasks; profiles live
in approved configuration. Identify only genuine proof producer dependencies, preserve proof
lifetime/permanent acceptance and no implementation authority. Do not run tasks now.

## Installed stage execution and producer self-review

Observed SpecKit 1.0.12/pi/sh/sequential metadata and actual plan prompt read fully.
Resolver/common/setup helpers and active template inspected. Exact setup executed **once**,
returning this feature/spec/plan; its BRANCH field is feature identifier `003-coordinate-workflow`
(from resolver fallback), **not** the Git branch, which remained unchanged. Template hash
`5ef0e4c97b36e9f91372dc6eb8e5a7e515af8958cf1a9286e43a1ebd9bd48540`.
No `.specify/extensions.yml`; pre/post hooks absent/skipped. Manager no-fanout boundary
supersedes prompt's implied research dispatch; same producer performed research. No task
handoff command, second planner/pass, implementation or helper launched.

Same-session sequence: reviewed approved original spec → escalated integration gap → owner
selected SDK host → originating bounded spec correction → one installed plan generation →
owner-authorized pauses and separate accepted SDK/local lifecycle experiments → same-session completion of
research/data/contracts/quickstart → authored-bundle self-review/correction. Historical
approval immutable; renewal required. Selected and observed producer:
`openai-codex/gpt-6.1-sol:medium`, session `01a15120-2a21-744d-b613-2c35bcf15eb4`,
actual model_change/thinking_level_change inspected. No profile substitution.

Self-review corrected potential unsafe assumptions in design: SDK extension throws are not
pre-send enforcement and onPayload alone misses summary requests; native RPC lacks actual
threshold; saver/application commits are not
one atomic transaction; kernel lock release does not prove orphan quiescence; status must
be independently read-only; Git subject matching alone is not recovery identity; per-task
tool survivors alarm durably without treating a reusable idle Pi host as orphan. The later
owner-directed interaction/autonomy correction is described above and in R13;
its proof is feasibility, not production auth/outbox/budget/pressure certification. Explicit
production spend choices remain owner gates; no amount is silently selected.

## Complexity Tracking

| Required extension | Why needed | Simpler alternative rejected |
| --- | --- | --- |
| Pinned thin Node SDK host beside Python engine | Actual effective settings and outbound metadata, stream wrapper covers summary routes without duplicating Pi internals | Pure native RPC lacks these fields; snapshot extension adds equivalence uncertainty; owner chose SDK host |
| Application operation ledger in the same SQLite store as LangGraph | Reconcile external Pi/Git effects across checkpoint lag | Saver alone cannot make external effects exactly once; toy receipts/commit subjects are inadequate |

Neither extension is a second orchestrator, a daemon, or a permission waiver. Implementation
remains gated by specification renewal, separate tasks/independent overall review/final artifact
approval and a later explicit implementation request (this request is planning-only).

### Initial producer validation result (historical d6acc13; correction rechecked below)

Full authored bundle reread and self-reviewed after both owner-directed pauses. Declarative
checks passed: seven draft-2020-12 schemas, nine positive examples and sixteen targeted
negative mutations (including orphan result/event/status cannot release/accept and non-agent
metric cannot invent Pi identity). These check design serialization, **not implemented graph,
registry, provenance/security enforcement or runtime behavior**. Host op payload and check
argument schemas must be bound to their registered capability schemas in implementation;
the reviewed envelope alone is not payload enforcement.

Feature links/anchors, original source byte-prefix preservation, immutable historical
spec-approval, 34-FR coverage and unchanged FR/SC IDs checked; only FR-002 and FR-017 normative
text changed under owner direction. No tasks or production code. Planner/checkpoint static
checks and installed plan prerequisites passed; before/after plan hooks absent. Existing
baseline planner suite previously passed 123 tests; no new live/provider/probe run here.
Constitution post-design check retains explicit amendments/approval gates above. Final
path-limited diff/whitespace/sensitive-value checks accompany the focused bundle checkpoint.
Parent inspection and renewed specification approval remain mandatory, not implied by these
checks, self-review or commit. Independent overall review belongs after separate task creation.

### Same-origin interaction correction (baseline 6534763)

Owner explicitly required the interaction/autonomy changes after d6acc13 and witnessed the
accepted integrated fixture. Same observed Sol/medium producer corrected existing artifacts,
not a new plan/setup pass. Spec FR-019 is aligned; US6, FR-035–039 and SC-008/009 are new
owner-directed requirements. R13 distinguishes actual idle-parent ask_user/steering proof
from unproven production launch/auth/outbox/pressure/budget integration. Historical approval
remains unchanged; **RENEW_SPEC_APPROVAL** is mandatory before separate fresh task generation.
No task/implementation/extra probe/extension/global changes or 123-test rerun in this correction.

Correction producer self-review/validation: eight declarative schemas, eighteen positive
fixtures, thirty-five negative schema mutations and six explicit binding/duplicate fixture
assertions pass. These demonstrate design serialization/invariants, not production receipt
authentication, temporal exactly-once, semantic question eligibility or dispatch enforcement.
Reconciled original-pin vs ordinary rotor, required dialog vs optional notifications,
run-scoped controls without fabricated idle worker, queued vs actual acknowledgement,
accepted input vs failed transport, and paid authority vs advisory/provider limits. Source
prefix/historical approval and all original FR/SC IDs remain; only existing FR-019 changes,
plus FR-035–039/US6/SC-008–009. Full correction diff/new schema/examples read and reviewed.
Constitution 3.0.0 review retains explicit owner gates, portable standalone assets, one-writer/
checkpoint safety, independent reviewer and no narrative memory; prescribed parent dialog is
not LLM orchestration. Future actual policy amendments above remain approval-gated. Final
links/coverage/secret/path/whitespace/scope checks are reported with the focused correction
checkpoint. RENEW_SPEC_APPROVAL remains the next gate, not waived by these checks or commit.
