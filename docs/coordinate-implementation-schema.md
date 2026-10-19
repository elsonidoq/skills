# Coordinate Implementation schema owner

This is the canonical owner for the **delivered foundation and T002 adapter**, alongside
[operating/security guidance](coordinate-implementation.md). The [design data model](../specs/003-coordinate-workflow/data-model.md)
and [reviewed contracts](../specs/003-coordinate-workflow/contracts/README.md) describe the
complete planned runtime. Tables and projections for later tasks are not implicitly installed.

## Packaged contracts

`runtime/coherence_workflow/schemas/` contains the eight reviewed draft-2020-12 JSON schemas,
byte-equivalent to the approved design copies at T001 delivery:

| File | Boundary |
| --- | --- |
| `shared.schema.json` | IDs/digests/paths, profiles, session policy, evidence and provenance definitions |
| `workflow.schema.json` | Closed version-1 declarative node/transition/profile/skill/settings/storage configuration |
| `task.schema.json` | Full normalized origin/order/ownership/REQUIRED/gates/authorization contract; intake later |
| `agent-result.schema.json` | Untrusted proposed implementation/review result; task-result admission later |
| `execution-result.schema.json` | Runner-audited outcome, REQUIRED dispositions and mandatory survivor blocking; public aggregation later |
| `host.schema.json` | Delivered SDK envelope; closed op payload/phase validation in host.mjs and pi_adapter.py |
| `interaction.schema.json` | Original question pins, owner/control/provenance/transport authority; interaction later |
| `projection.schema.json` | Derived versioned state/events/metrics; publisher later |

Schema `$id`s retain their reviewed `https://coherence.invalid/design/v1/` identifiers.
`registry.validate_schema(name,value)` resolves references from packaged resources locally,
never from the network. Schema shape is not authentication, capability readiness, task
acceptance or permission. Unknown versions/fields are rejected at their defined boundaries.
The shared definitions resource is not a standalone executable input schema.

Workflow semantic validation additionally rejects duplicate YAML keys, all explicit tags,
anchors/aliases, >256 KiB inputs, >128 nodes, unknown/unused node references, handler-version/
outcome/effect mismatch, absent capability/resources, unsafe/symlink paths, resource hash
drift, permission escalation, unsupported interaction/retries/cycles, unreachable/dead-end
nodes and paths bypassing required safety stages. Supported T001 graphs are acyclic.
Success terminals are registered trusted handlers, not an outcome inferred from prose.
Node results use the trusted handler's closed result schema; the foundation default is
`{outcome: string, value?: bounded string}`. Agent-result schemas are packaged, not a claim
that a workflow task-result/acceptance handler is present. Each registered check has closed `test_file`/`selector`
constants and version `1`: `workflow.ConfigGraphTests`, `workflow.CustodyTests`,
`workflow.LaunchCrashTests`, `workflow.LedgerCheckpointTests`.

## One application database, schema version 1

The lock and storage binding are under Git's verified per-worktree admin directory;
run roots cannot override `.coherence/workflow/workflow.sqlite`. Binding records version,
canonical project/database and admin device/inode. The lock/binding/DB must be private,
regular, single-link, same-UID files; identity is rechecked at use. Unsupported application
schema versions block before DDL; there is no automatic migration/downgrade.

`store.py` owns application DDL; LangGraph owns its own saver tables (`checkpoints`,
`writes`, etc.). Application code never modifies saver tables.

| Application table | Actual foundation columns / constraints |
| --- | --- |
| `wf_meta` | `version` PK constrained to 1 |
| `wf_runs` | `run_id` PK, immutable `config_hash`, `state`, boolean `reservation`; partial UNIQUE index allows one reserved run for the worktree |
| `wf_operations` | `op_id` PK, run FK, `node_id`, `kind`, `args_hash`, `phase`, canonical `intent`, nullable canonical `result`; UNIQUE(run,node,kind) for acyclic node visits |
| `wf_events` | global monotonically allocated `seq` PK, unique `event_id`, run/op FK, `kind`, canonical bounded/sanitized `payload`; UNIQUE(op,kind) prevents duplicate operation phase history |
| `wf_processes` | operation PK/FK, `scope_kind=host|task_tools`, unique child `name`, containment and process identity JSON, nullable exit code, empty receipt and reconciliation JSON |
| `wf_alarms` | `alarm_id` PK, process-operation FK, `kind=ORPHAN_PROCESS`, active/resolved state, original event-sequence FK, resolution JSON; one active alarm per operation |

Sequences are global for this foundation database; they are immutable history in the runner
API, not yet the planned per-run public projection sequence. Projections are not published
or read for decisions. No wf_tasks/sessions/checks/gates/outbox tables exist until their
respective delivery. Pi conversation data never becomes workflow authority.

## Transactions and replay

All application writes use one explicit `BEGIN IMMEDIATE` connection with:

- `journal_mode=WAL`
- `synchronous=FULL` (2)
- `foreign_keys=ON` (1)
- `busy_timeout=5000` ms

Startup and tests verify these settings, integrity and foreign keys. SqliteSaver has a
**separate connection/transaction** to the same file, configured WAL/FULL/foreign keys.
`Engine.invoke` uses `durability="sync"`, `thread_id=run_id`; actual LangGraph edges own
continuation. No app transaction may span a saver call, subprocess wait or handler effect.
Backups require SQLite's backup API with appropriate custody, not copying only the main
WAL file. No backup command or power-loss/device durability certification is delivered.

Graph operation ordering: unique intent/event commits → handler → validated result/event
commits → handler returns → saver checkpoints. On graph replay a completed, identical-input
operation returns its recorded schema-valid result; effect handlers require registered
applicability reconciliation. An incomplete/uncertain operation blocks, never retries an
external/Git effect. At completion the runner audits the entire actual start-to-terminal
trace, input hashes, application results and corresponding event evidence; a green cursor
without applicable app proof is corruption/incomplete evidence. SQL uniqueness/CAS and
replay reconciliation are **not exactly-once external effects** or an atomic app+saver commit.

Process operations use phases `intent → contained → prepared → released → completed`:

1. Intent holds unique operation/tool/version/argv/environment, nonce/name, explicit owned
   paths and baseline HEAD/index/file fingerprints. No raw file contents/tool output enter SQL.
2. `contained` records fresh child UID/device/inode/name+parent/boot before helper spawn.
3. `prepared` records helper PID/start/UID/parent/boot/nonce after validated membership.
4. `released` commits release intent before sending the matching nonce on the inherited gate.
   A crash in between is uncertain; neither the tool nor a Git effect is blindly replayed.
5. `completed` records actual kernel-empty receipt plus partial file/Git audit, logical exit
   (possibly unknown) and `task_accepted=false`. Exit without settlement leaves custody unresolved.

Before helper registration, restart never adopts an unknown process/group or sends release.
Invalid durable identities block before effects. Registered process identity is compared with
its prepared event and live boot/PID/start/UID; controller-death reparenting is permitted only
for that otherwise identical durable process. Cleanup targets the proven cgroup, never a PID.
A populated task-tool scope atomically records `ORPHAN_PROCESS` event/alarm and blocked run.
Survivors override exit 0/1/kill. Resolution retains alarm history, records validated empty
and actual reconciliation, and does not clear blocked run state or grant acceptance/resume.
Idle host scopes have a distinct outcome, not a task-tool alarm.

Current receipts are trusted runner-internal records, not serialized public projection/
execution-result envelopes. T002 adds SDK telemetry/null-reason segments below. Public
projections, intake/owner authority, Git commit receipts and UI integration remain later
tasks and must use the packaged contracts plus their semantic rules. No schema-valid fixture can authorize execution.

## T002 internal SDK facts and usage segments (no DDL migration)

T002 reuses `wf_operations`, `wf_processes`, and `wf_events`; it does not create session,
metric, gate, outbox or projection tables. The application schema stays version 1.
Existing task-tool intent gains `scope_kind`; default semantics and release ordering remain
unchanged. SDK host process intents use `scope_kind=host`, no owned worktree paths, and
explicit inherited pipes. Host admission/ready events pin compatibility/manifest identity and
actual initial telemetry. Host completion includes its verified `task_tool_chain`, preserving
the original baseline and each completed task-tool audit. Foundation registered hosts with
their own declared paths retain original reconciliation, but cannot mix those direct writes
with task-tool audit chains. SDK hosts never use direct worktree-write ownership.

An `sdk-turn` operation is keyed by existing UNIQUE(run,node,kind). Intent contains run/task/
node/attempt/host identity, role and compatibility, contract hash, prompt generation,
selection reason/candidates, baseline SHA, start time and before telemetry. It stores no
prompt/tool payload. A completed operation's result is the attributable segment, before/after
snapshots, stop/end/elapsed observations, requested/runtime/observed bindings, skills,
selection and retry count. Result SHA is null with `runner_checkpoint_not_yet_performed`;
checks are not invented before their later runner stage. Interrupted events preserve the
same identity/baseline/start facts, observed interruption time/elapsed, null end/final usage/
cost and explicit reasons. Incomplete SDK intent is never prompt-replay authority.

Lifecycle/request observations use immutable event kinds `sdk:<host sequence>` under that
turn operation, avoiding collision across repeated SDK event types. Only allowlisted facts
are persisted: type/generation, model/provider/wire effort/mapping/request sequence, tool names,
expansion boolean/hash and sanitized blocker/settlement flags. Full transcripts, assistant
reasoning, output text, tool arguments and provider payloads are not telemetry. Host/session
operation identity and the app event sequence retain attribution; Pi JSONL remains private
conversation persistence. This is not the later public `metrics.jsonl` revision schema.

Actual idle telemetry includes session/file/leaf/file-hash, stable branch identity, new
host counter epoch, generation/sample time, SDK version, SettingsManager provenance and
resolved model-compaction settings, effective threshold, projected occupancy/headroom,
settings/resource hashes, tools/skills/system-prompt hash, cumulative input/output/cache
read/write counters and SDK-estimated cost. Branch navigation is not exposed by this
adapter: its stable branch identity is the saved session lineage, not the changing leaf.
Reopen validates the exact durable leaf/hash and starts a new epoch; no prior process
counter baseline crosses reopen. Compaction without a post-summary assistant has null
occupancy. Disabled/unknown threshold never means infinite capacity.

`usage_segment` subtracts only same-session/branch/epoch, exclusive, settled, valid safe
monotonic counter pairs. Each token field has `{value, unknown_reason}`; observed cache zero
is retained. Missing/death, reopen/branch change, reset, nonexclusive operation or ambiguous
summary yields null with reason, never negative/double-counted usage. Cost is separately
finite/monotonic or null. Before/after occupancy is never cumulative billed tokens. Non-agent
segments have null session/context/tokens/cost and `non_agent_node`; projections must not
invent Pi identities for code/gate nodes. No financial model-token gate is added.

The host envelope stays the packaged closed v1 schema. `payload_schema=sdk-v1` selects
host-owned closed payloads; generation is inside payload, not an unreviewed envelope field.
Create/open carry the explicit manifest; prompt carries text/skill/next generation;
telemetry/abort/drain/close carry expected generation; correlated tool replies carry call ID,
generation and bounded result. Lifecycle, request observations and settled facts retain the
originating request/operation/attempt binding. Unknown op/version/identity/nonce/sequence,
duplicate request IDs, stale generations, EOF or malformed/oversized records block/poison.
Steering/owner-question commands are still unsupported, not silently approximated.

The four T002 selector contracts (`workflow.BindingTests`, `workflow.SessionPolicyTests`,
`workflow.LifecycleTests`, `workflow.UsageSegmentsTests`, version 1) have their approved
source-named test classes. Their executable check-registry integration belongs to T003;
T002 does not change the production registry or pretend task dispatch is available.

## Standalone task/checkpoint extension

T003 adds runner-only `wf_run_inputs` (run identity, canonical contract and owner-catalog
hash) and `wf_tasks` (run/task primary key, unique source order, immutable canonical task,
state, baseline, REQUIRED evidence and checkpoint receipt). `wf_checks` retains evidence ID,
run/task/item, applicability and canonical receipt; `wf_gates` retains exact manual binding,
pending/approve/deny/cancel state and truthful external answer. They share the application
connection and WAL/FULL/foreign-key policy; they do not make saver commits atomic.

Graph operations use `node:visit` logical identities only for the registered bounded
`task_select` cycle. The approved task-count bound and external input identity are in the
engine hash. A checkpoint-to-selector backedge is the only task-progress cycle admitted;
other cycles remain blocked. Registry CHECKS contains closed v1 selectors. Check receipts
contain source revision, exact check arguments, item mappings, Python/platform identity,
collected count, exit, bounded output, timestamps, applicability and disposition. Applicability
binds the whole item, owned bytes and environment. Unknown/unrun is not zero or pass.

`git-checkpoint` operations persist exact baseline/file/index and expected tree-entry maps
before launch. Their process node is `commit:OP_ID`; runner Git argv and operation trailer
must match that original intent. Results contain actual SHA, parent/tree, owned paths and
full reconciled files/index. Original process snapshots are not overwritten to admit Git.
The commit gateway has a narrowly registered exact-checkpoint reconciler; ordinary process
HEAD/index drift still blocks. Host and task-tool lifetimes remain separate.

## Controller/recovery/projection extension

`wf_controllers` binds one run to actual controller identity and active/stopped phase;
`controller_started`/`controller_stopped` events are immutable facts. Stored run state alone
is not liveness. Schema version remains the supported additive v1; unknown versions are
rejected before opening a writable saver. No untrusted saver deserialization or downgrade.

`wf_projections(run_id,seq)` is a publication convenience cursor, never a decision input.
Published state/event/metric records validate against the packaged projection schema. SQL
sequence/event IDs define logical order, including replay after append-before-cursor failure.
Metric checkpoint revisions retain original counters but set `supersedes` to the original
invocation metric ID and attach actual result SHA/check refs. Consumers select unsuperseded
records rather than summing revisions. Unknown original event timestamps are labelled
`unknown:event-timestamps-not-recorded`; SDK segment start/end nanoseconds remain actual
recorded observations. Projection files have private owner-only permissions.

Authorized post-commit recovery reconciles existing immutable intent/result/tree/index and
records the original checkpoint node's schema-valid result before saver continuation. Other
uncertain effects remain blocked. A recovery authorization digest is appended to SQL; no
model-generated result can authorize it. Controller exit never implies background progress.

## Review, original-failure budgets and acceptance

T005 adds `wf_repair_budgets(run_id,failure_key,maximum,used)` with a composite primary key;
`failure_key` remains the original task failure or `review-final` across correction IDs/restart.
`repair_dispatched` commits before each prompt; interruption never resets it. Configured zero
prevents dispatch. Transport/provider retry observations remain separate from workflow repairs.

`wf_reviews` records review ID/run, complete base/head, completed host operation, schema-valid
result and independent role proof. `wf_findings` keys every finding by review/finding ID and
retains canonical severity/location/criterion/evidence plus disposition/correction ID.
`wf_corrections` binds each separately generated task to its original task, stable failure key
and current external rule/source-approval/finding/range authority hashes. No correction ID creates
a new repair budget, changes REQUIRED criteria, or lets a reviewer produce a fix.

The registered graph now admits only bounded verification↔repair and review→correction-authority
→task-selector cycles in addition to the task-progress backedge. Each cycle still crosses actual
verification/checkpoint nodes; success must cross independent review. Graph visit bounds derive
from source task/repair limits; SQL original-failure ceilings remain the semantic dispatch gate.

Runner-only `workflow_accepted` records exact head and review reference only after full audit.
`workflow_blocked` retains reason and exhaustion/final-failure disposition. State projection derives
accepted/blocked/implementation-complete separately, and pending gates/unresolved findings override
an old accepted fact. SQL remains authority; projections never release work. Repair metrics carry
the explicit runner-selected repair count through both settled/interrupted SDK segments. Current
checkpoint metric revisions supersede original invocation records, preserving real zero and unknown
counter values without summing usage twice. Provider acknowledgement remains unknown where absent.

Checkpoint metric revision IDs include both the checkpoint event ID and the original SDK
operation ID. Multiple attempts of one task therefore retain separate attributable usage;
the same checkpoint cannot collapse their record identities. Ordering is explicit completion
sequence, not SQLite query-plan order.

SDK tool transport appends `sdk_tool_queued:<call-hash>`, `sdk_tool_launched:<call-hash>` and
`sdk_tool_cancelled:<call-hash>` to the originating SDK operation. Payloads contain stable call/
argument hashes, generation, registered tool/version and actual process-op ref on launch.
A launch-uncertain disposition never claims execution or cancellation. FIFO memory loss does
not authorize replay: unresolved SDK/graph operations and durable scope custody still block.
`sdk_failure_diagnostic` contains only an allowlisted classification/type chain, phase,
operation/host refs, validator keyword and pending process-op IDs. No raw provider payload or
unnecessary transcript is projected. A cancelled queued request has no process operation and
cannot be counted as executed work or a completed workflow attempt.

`task_evidence_refreshed` appends final-head proof for stale producer inputs without changing
their original contracts/checkpoints. Checkpoint metric evidence references are selected as of
that checkpoint event sequence; later evidence cannot rewrite immutable published history.

## T006 question/input/control extension (additive v1)

`interaction.py` owns this DDL in the same private application database; it does not alter
LangGraph saver tables. The execution controller retains the worktree mutation lock. A narrow
owner-input connection may insert/accept bound inputs while that lock is held; short SQLite
BEGIN IMMEDIATE transactions serialize inputs with controller writes. It cannot dispatch or
change graph/configuration/custody. WAL/FULL/foreign keys and bounded busy timeout remain required.

| Table | Actual columns/invariants |
| --- | --- |
| `wf_questions` | gate PK; run FK; UNIQUE turn-op FK; call ID; canonical binding; UNIQUE nonce; bounded canonical request; stage; original pin and settlement proof. UNIQUE(run,call); one unresolved parking/pending/answered/delivering gate per run |
| `wf_question_parks` | gate PK/FK, actual sync-saver checkpoint ID, interrupted gate node, original graph-op FK. A SQL pending gate without this receipt is not answer/transport eligible |
| `wf_owner_inputs` | input PK; run FK; nullable gate FK; complete input hash and safe canonical payload; stage; nullable delivery/facts/stop receipt. One answer per nonnull gate; identical duplicates return the original aggregate without redispatch |
| `wf_outbox` | stable event PK, run FK, UNIQUE gate FK, stage and nullable receipt. T006 creates recorded only; no parent sender is enabled |
| `wf_controls` | input PK/FK, immutable canonical target binding, action/scope/message. Control stages are in wf_owner_inputs and append-only events |
| `wf_run_bindings` | run PK/FK, immutable run-scoped source/approval/config binding with null task/node/attempt/session/role/task hash |
| `wf_active_targets` | run PK/FK, actual current task/node/attempt/session/role/source/task/approval/config binding; removed after host close/stop. Inputs never silently retarget |

Question stages are parking → pending → answered → delivering → continued, or cancelled.
Pending requires the completed sdk-turn snapshot, current tool-end/agent_settled and actual
closed/empty host/tool receipts. The original pin additionally records host operation, saved
snapshot, original attempt and actual invocation attempt ID, graph operation and review-bundle
hash when applicable. The application result commits before saver; after the actual sync
interrupt, `question_graph_parked` and wf_question_parks make delivery eligible. Replay can
reconcile the exact original completed graph visit; no pending tool is held for human input.
Unsupported mixed/unknown batches fail before effects; the only supported question batch is
exclusive, not arbitrary all-tools termination.

Answer input shape is the packaged owner_answer schema, accepted at delivery=accepted with
null delivery_ref. External authority binds its complete digest, genuine receipt and within-
envelope scope. Acceptance, queued_original intent, sdk_delivered entry receipt and subsequent
continuation remain separate. The entry receipt contains input/session/entry/leaf and the new
idle SDK snapshot; no answer is blindly resent after uncertain delivery. A new host has a new
counter epoch even when session/branch persist. Source/scope-changing input is blocked for
producing renewal; accepted historical input remains independently inspectable.

Controls use owner_control. received → queued → sdk_delivered → worker_acknowledged records
actual enqueue and later public user/assistant entry provenance separately. Inquiry may remain
received with a recorded-facts receipt (there is no fictional worker delivery). A safely stopped
pause/cancel becomes reconciled with owned empty-scope hashes and a partial snapshot hash,
worker_acknowledged=false. Wrong/stale/duplicate/out-of-scope controls never select a replacement
or bypass an original question. A cancelled/paused state is durable even without a live controller.
Status adds SQL-derived questions/controls; waiting_owner_input includes pending_question_ref.
These fields are facts, not optional transport notifications or projection decision inputs.

`retained_candidates` derives saved sessions from completed SDK/event receipts, latest settled
sequence and their completed host custody. Normal compatibility also hashes the system prompt
with settings/pressure policy. `Gateway.verify_closed_host` composes only exact same-run completed
tool and focused checkpoint chains to current HEAD/index/files. Original host/empty/tool receipts
are never rewritten. Unknown effects, mismatched parent/tree/operation identity or current drift
block. Reopening always checks saved file/session/leaf/hash, role/resources and actual headroom;
original-only pins cannot fall through to fresh selection.

All-role configured question/continue_original edges are bounded graph loops, not a second
scheduler. Original repair budgets remain consumed once for that repair; continuation segments
have distinct SDK operation/attempt identities. Review permits exactly configured/admitted
read_file, optionally request_owner_input, with original independent role/range lineage and
completed host-admission provenance. Mutating/undeclared tools remain rejected. T007 below adds
actual parent readiness/outbox provenance; a recorded row or authorization file alone still
cannot establish an actual ask_user invocation or answer.

## T007 registered parent transport/provenance extension

Paseo is explicit and mode-specific. `Registry.question_transports` contains only trusted runtime
capabilities; engine validation calls the selected capability's validate_config and includes its
source hash, actual ready/launch receipts, descriptor hash and observed parent identity in registry/
run identity. Config data cannot create executable capabilities or grant readiness. Default empty
registries and unpreflighted/missing capabilities fail closed; standalone performs no Paseo import.

`notifications/paseo.py` owns these additive v1 tables in the SAME private SQLite authority:

| Table | Actual columns / role |
| --- | --- |
| `wf_parent_preflight` | run_id PK, closed canonical descriptor, observed official-session identity, UNIQUE challenge nonce, challenge_recorded/ready stage, genuine launch and ready tool receipts, nullable blocker. Deliberately no run FK: readiness is established before Engine reserves a graph run |
| `wf_parent_delivery` | outbox event PK/FK, immutable generation hash, bounded send-attempt count, durable parent claim, actual question-tool receipt, nullable blocker |
| `wf_parent_attempts` | monotonic seq PK, run ID, nullable event ID, action/outcome. Includes preflight busy/unavailable/queued observations; optional status observations do not drive graph state |

A descriptor binds adapter/version, binding_id, recipient, Pi session/file/cwd, observed parent
model/effort, explicit generation and launch nonce. An observed identity binds file device/inode/
UID, header session/cwd and current active registered-tool digest. Reconnect compares those values
plus actual public inspection; it cannot silently choose another parent/generation/environment.
The original source file is owned and non-writable by group/others, but may be mode0644: no
confidentiality, cryptographic identity or malicious-same-UID protection is claimed.

Provenance reads are bounded to 32 MiB/session and 1 MiB/record, canonical non-symlink regular
single-link files, version3 header, complete LF JSON records and an unambiguous active parentId
branch. Missing/partial/rotated/stale/mismatched metadata blocks or remains pending. Only current
registry metadata and exact nonce/argument-bound bash/ask_user call/result facts are extracted.
Sanitized receipts retain tool name, call and result entry IDs, argument/result hashes and required
answer hash; they never copy the parent transcript, private reasoning or unrelated user content.
The official session file is read-only evidence, not a message channel or workflow decision store.

Launch requires a genuine registered bash call/result carrying the literal launch marker and exact
project/run/start context. A fresh public-Paseo readiness wake requires the same parent's completed
parent-ready bash result before reliance. A facade executing that command can only return ack_received;
code independently verifies completion before wf_parent_preflight becomes ready. Declared ask_user
availability alone is not a question result: actual answer acceptance additionally requires the real
registered ask_user call with exact question/context/options/flags, matching noncancelled successful
structured selection and consistent tool result text. Wrong/cancelled/error/ambiguous outcomes block.

A graph-parked question creates a stable outbox event. Stage transitions are recorded →
transport_queued → parent_received → question_tool_invoked → answered. Public queued-send receipts
and completed parent helper receipts remain distinct. If genuine parent receipt arrives before an
uncertain send is acknowledged, the required earlier queue stage is explicitly reconciled from that
receipt before later stages; an eventual send ACK cannot regress an answered row. A durable claim
is inserted before the facade may call ask_user. Duplicate callbacks cannot grant another ask;
unknown external invocation needs actual tool reconciliation or remains blocked, never exactly-once UI.

`parent-answer` does not accept caller answer text or workflow choices. It derives a deterministic
input ID from the outbox event, verifies original sources/approval records, binds the actual tool
receipt to the original gate/session/nonce/config, and submits through Interaction.answer. This is
runner-owned persistence behind a narrow facade API, not facade SQL/orchestration authority.
Material-change responses require producing renewal; input or transport success never authorizes
source/profile/task changes. Accepted inputs retain their original delivery obligations across
transport/reentry failures. Optional notifications cannot accept input or resume a graph.

Standalone status additionally exposes parent_transport preflight/outbox/blocker facts from SQL,
without loading a UI client. Required transport failure leaves durable question/pin/input data and
explicit blockers; it is not accepted completion or a manual-polling fallback. The shipped wake
adapter uses public Paseo0.9.2 inspect/send only. Test-only public package-root SDK response driving
is separate: it validates an exact current permission question/options/nonce, reconnects and responds
only to that preapproved isolated UI request. No fabricated tool/user events or historical recipients.
