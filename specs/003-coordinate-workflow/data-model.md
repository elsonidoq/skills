# Runtime data model — draft schema owner for implementation

Derived from [spec.md](spec.md), [plan](plan.md) and [research](research.md).
This is a proposed data model, not an installed database/migration. Production schema owner
will be `docs/coordinate-implementation-schema.md` with actual migrations/code comparison.
All table names below are runner-owned and prefixed `wf_`; never modify LangGraph tables.

## One authority, explicit ordering

One SQLite database per canonical worktree contains LangGraph saver tables plus the runner
ledger. An approved project-local storage root defaults to `.coherence/workflow/`; database
`workflow.sqlite`, run projections `runs/<run_id>/`. Resolve real paths and permissions,
exclude runtime files from Git only through authorized project setup, not implicit edits.
Storage must not be reachable by agent mutation tools. Binding is registered beside the
worktree-wide lock in Git's verified **per-worktree** administrative directory. Different
run directories cannot choose another authority DB. Moving/changing storage requires owner
migration with no active/unknown work, preserved old store and version/readability checks.

SQLite is authoritative for workflow position, facts, gates and effects; projections are
not inputs. Pi session JSONL is authorized conversation persistence only, not workflow
state. No raw transcripts, payloads, credentials or narrative STATE in the workflow store.

- LangGraph `SqliteSaver` owns its `checkpoints`/`writes` tables and continuation cursor.
- Application events, operation receipts and aggregate updates share one explicit
  application transaction on a separate connection. Foreign keys enabled; one application
  writer, bounded busy timeout; no held app transaction during saver calls/external waits.
- WAL and synchronous FULL are explicit initial SQLite settings; startup verifies them.
  This plans process-crash recovery, not physical power-loss/fsync/storage-device guarantees.
  Backup uses SQLite backup API under supported coordination, never copies only main WAL DB.
- Saver and application commits are **not one atomic transaction**. App intent commits
  before effects, app result commits before node returns; LangGraph then sync-checkpoints.
  A committed operation result with a lagging graph cursor is normal replay input. Handler
  verifies its unique key/inputs/result applicability and returns the recorded result, so
  actual graph edges still decide the next node. No second Python graph scheduler.
- If graph claims success but required app result/effect evidence is absent or conflicting,
  block as corruption/incomplete evidence. Never synthesize a receipt from a green cursor.
- SQL UNIQUE/compare-and-set phase transitions and one lock prevent duplicate logical
  operations. They do not guarantee exactly-once external filesystem/Git/provider effects.

## Entities, keys and constraints

| Table/entity | Identity, required fields and relationships | Validation / index |
| --- | --- | --- |
| `wf_meta` | schema_version, supported engine/saver versions, worktree_id, storage_binding_hash | Migrations explicit; unsupported future version read-only status or precise blocker; never automatic downgrade |
| `wf_runs` | run_id PK; worktree_id; input/config/registry/schema/host hashes; base_sha; state; acceptance_state; graph_thread_id; created/updated times; last_event_seq | One mutable run per worktree; state and acceptance distinct; thread_id=run_id; immutable identity columns |
| `wf_inputs` | (run_id,input_id) PK; kind, normalized project-relative path/section, SHA256, origin and provenance ref | Source/spec/plan/tasks/reviews/owner-answer/config/resource hashes; no secret-bearing files |
| `wf_tasks` | (run_id,task_id) PK; approved_order, contract_hash, source_refs, context_group, owned_paths, dependencies, state; original_task_id for corrections | Unique order, dependencies earlier, no cycles, required producer checkpoint/evidence before release |
| `wf_attempts` | attempt_id PK; run/task/node IDs, attempt_index, operation_id; role, profile/skill requested+observed, host/session, fresh/reused/reason; baseline/result_sha; times/outcome/budgets | UNIQUE(run,task,node,attempt_index); never overwrite failed/interrupted attempts; no fictitious Pi fields for code/gate nodes |
| `wf_sessions` | session_id PK; run/worktree association, role_family/review_lineage, profile/resource/tool/permission/settings hashes, session_ref+branch leaf, host_id, lifecycle phase, settle_seq, telemetry epoch | Exact role/affinity match; first final review fresh; never continueRecent; settled facts not in-flight estimates |
| `wf_operations` | op_id PK; run/task/attempt/node/handler version; kind, args_hash, input_revision, phase, intent/before-state refs, observed_result, error/reconciliation refs | UNIQUE(run,logical node visit,task,attempt,kind); graph replay same key; invalidated/retried attempt new key with predecessor |
| `wf_alarms` | alarm_id PK; run/op/scope identity FK, kind=ORPHAN_PROCESS, original event seq, active/resolved state, resolution evidence | Unique active alarm per operation/scope; never erase history; blocked release until cleanup+file/Git reconciliation |
| `wf_processes` | process_id PK; op_id FK; host boot ID, PID, start-time, parent/PGID, nonce, containment ID/type, launch phase, observed exit/drain evidence | PID alone not authority; known container/service/cgroup identity where required; all active/unknown processes scanned before writer replacement |
| `wf_checks` | evidence_id PK; run/task/item IDs; check_id+version, argv/args hash, revision/tree/path hashes, environment hash, times, exit/observables, output_ref+hash, verdict+limitations | Shared command once, mapping table preserves every item; revision/env/selector applicability required, missing != failed |
| `wf_gates` | gate_id PK; run/task/finding; kind; requested_scope_hash, inputs_hash, config_hash, nonce, pending/answered/denied/cancelled/stale; answer_ref/hash, actor, authority provenance | No trusted approved boolean; expected exact scoped answer and external record verified before status=answered |
| `wf_findings` | (review_id,finding_id) PK; range_base/head, criterion, location, severity, evidence, proposed action; disposition and repair task link | All findings visible; reviewer read-only; disposition justified, unresolved blocker prevents acceptance |
| `wf_events` | (run_id,seq) PK; event_id UNIQUE, schema_version, kind, timestamp, operation/attempt refs, sanitized payload, payload_hash | Seq allocated under app transaction, monotonically increasing per run; immutable; same op phase cannot append twice |
| `wf_projections` | (run_id,projection_name) PK; last published seq, generation/content hash, repair status | Cursor is convenience, not proof of file durability; reader validates actual tail and reconciles |

Structured task/profile/config/outcome definitions are in [contracts](contracts/README.md).
Large sanitized check outputs may be immutable content-addressed blobs beneath the approved
runtime root; write temp+fsync+rename **before** committing their SQL references. A crash
may leave an unreferenced blob, never an accepted missing blob. Outputs have size limits,
redaction policy and allowlisted evidence shape; no automatic sensitive full stdout capture.
If permitted storage of necessary evidence cannot be made safe, stop the affected check.

## Lifecycles and gate semantics

Run: `created → preflight → running → blocked|interrupted|implementation_complete →
reviewing → accepted|blocked|final_failure`; cancellation is terminal unless a new explicit
scoped continuation is authorized. Host exit marks interrupted/unknown, not background running.
Acceptance requires all task evidence/checkpoints plus current independent full-range review.
Empty/no-change work creates no empty commit; still evaluate applicable final acceptance gates.

Task: `pending → ready → active → verifying → checkpointed` (or `read_only_complete`);
failed/insufficient evidence stays blocked or enters diagnosed authorized bounded repair.
Only checkpointed/read-only-complete with all original gates satisfied releases dependencies.
Correction findings create separate authorized focused task IDs; they do not rewrite approved
original task contracts or merge original+repair commits. Out-of-scope changes renew approval.

Attempt: `reserved → dispatching → active → settling → settled → audited → committed` or
`failed|blocked|stopped|interrupted|orphan|unknown`. End time/counters may be null for death;
reconciliation adds facts without converting an orphan to success. Count each dispatched
repair against max_repair_attempts even if interrupted; capability failure before dispatch
records no model usage and cannot create a hidden retry. Configured bound 2, zero supported.

Operation: `intent → prepared → released → observed → reconciled|completed|blocked`.
Each phase transition appends one event and updates aggregate in one SQL transaction.
A fresh attempt after authorized remediation references old operation; no overwriting history.

## Tool/process custody before any mutation

The accepted SDK experiment observed host-kill survival of a detached bash group. Production
must not enable mutating tools until the worktree-wide lock, durable operation ledger and
controlled tool supervisor are ready. Use a small runner tool gateway, not a general service
platform. Node exposes custom tools that request registered operations; Python validates
scope and performs allowed file syscalls or supervised process launches. The host cannot
launch unregistered shell/background tasks or commit Git. Reviewer tools are read-only.

For local subprocesses, a tiny gated-start helper creates identity/containment membership
and waits on a parent pipe. Sequence:

1. App transaction reserves operation/nonce/expected executable/args/permission/input state
   and unique child-group name under approved parent. Create that group without tool work,
   validate/persist UID/device/inode/name and capability identity before spawning helper.
   Crash between mkdir and identity receipt permits no work; reconcile the reserved name
   under trusted parent before reuse, never adopt/kill an unidentified preexisting group.
2. Spawn helper **without releasing work**. Helper reports PID/start/boot/containment identity;
   EOF before release exits without executing the operation. No child work before registration.
3. App commits identity/prepared event, verifies approved containment binding and root custody,
   then releases matching nonce; helper verifies it before exec. Crash before release safely
   cancels; crash after release always has durable identity. Test both sides of every boundary.
4. Abort/drain targets only proven-owned identity/containment. Record exit, empty live group,
   tool completion and file/Git observations before permitting replacement. If unknown, stop.

PID/PGID enumeration/start-time checks are diagnostics, not the emptiness oracle. The
supported initial adapter is Linux delegated cgroup v2 for trusted local same-user tools.
Project configuration references an approved delegated parent; resolve it at runtime, do
not hardcode the evidence machine's service path. Verify child creation, writable owned
child procs/kill and readable events before use. Only exact fresh UUID-named owned children
may be killed/removed after trusted UID/device/inode/name+parent identity validation; service
root/ancestor or unknown groups are forbidden targets. Never fall back to PID-only safety.
The accepted process probe now demonstrates inherited membership across setsid, TERM
resistance, worker exit0/exit1/SIGKILL and separate-controller reentry, with outside sentinel
preserved. Earlier nonwritable-delegation discovery was resolved by owner administrative
change; no runtime service/global provisioning is authorized or presumed on other hosts.

This is local trusted-tool containment, **not malicious same-UID escape isolation**: writable
ancestor controls can permit explicit migration. Unknown capability/receipt or uncontained
external work blocks. Remote/container/different-user/adversarial effects require separate
approved lifecycle capability, not a generic sandbox or unsupported-platform promise.

**Separate scopes:** `wf_processes.scope_kind=host|task_tools`, with session_id or task/attempt
foreign key. The persistent SDK host lives in a host scope and may legitimately remain idle
for reuse; process tools are launched only through the runner gateway in per-task scopes,
not inside that long-lived host group. Tool placement before release is a supported handshake,
not an atomic-spawn claim. Durable production registration/release crash phases remain tests.

**Mandatory alarm:** after logical tool/worker/task completion, actual task group populated>0
appends `ORPHAN_PROCESS` in the same app transaction as an active alarm/current blocker,
recording original logical outcome but overriding release to `replacement_allowed=false`.
Do this for exit0 as well as failure/kill; success cannot hide a live tool. Unknown populated
or invalid ownership blocks with its precise safety reason. Keep `wf_alarms` keyed by alarm_id,
run/operation/task scope+identity, original event seq, active/resolved state and resolution
refs. `wf_runs`/state expose active alarm refs; events/results retain history. An optional
notification has no authority and cannot delay recording/blocking. Only proven owned-group
populated=0 AND actual partial files/Git reconciliation can resolve the alarm, update current
blocker and permit authorized continuation. Empty containment alone is not task acceptance.

Synchronous runner-owned file operations can be supported without arbitrary child launches;
partial writes still require receipt/file reconciliation. Registered process checks/Git/hooks
must declare their effects and containment needs; do not assume that a trusted command cannot
launch an escaping hook/child. Block when its required guarantee is unavailable. Remote/container
external effects need their own registered lifecycle/authorization/reconciliation; no promise
to track arbitrary remote effects or malicious subprocesses. A stable-file window supplements,
never replaces, proven quiescence. No daemon or automatic service provisioning is required.

## Filesystem/Git reconciliation

Intent captures exact baseline HEAD, owned paths, index entries/modes/blob IDs and unrelated
staged/unstaged/untracked fingerprints. Detect concurrent path identity/symlink changes at
use, not merely lexical prefix validation. No preexisting dirty owned overlap is adopted
without explicit bounded ownership resolution; unrelated dirt must remain unchanged.

Commit only after actual REQUIRED checks, gates, host/tool settlement and owned diff audit.
Use path-limited commit retaining hooks/signing conventions; durable intent includes unique
operation trailer plus expected baseline and tree/diff hash. After commit read actual SHA,
parent, owned paths, preserved index and hook effects. Persist receipt/result before graph
return. If killed after commit before receipt/checkpoint, search operation identity then
verify all those facts; recover matching SHA once. Subject/trailer alone never authorizes
acceptance. Unexpected HEAD, hook mutation, changed result tree, ambiguous multiple matches,
residual owned drift or missing proof blocks rather than reset, duplicate commit or discard.
Read-only/no-change results retain audited evidence but no empty commit.

## Projections and metrics

Application transaction assigns event seq and final attempt snapshot revision together with
operation result. `state.json`, `events.jsonl`, `metrics.jsonl` publish sanitized versioned
views whose envelope `seq` is their declared as-of sequence. Events and finalized metric revisions are immutable,
idempotently keyed `(run_id,seq,event_id)`; a later recovered metric fact appends a new revision
with supersedes reference, never edits old history or double-counts usage.

One runner publisher holds a projection lock (no agent), reads committed SQL events, validates
existing tail/checksums and appends missing complete LF records in order. Flush/fsync before
advancing publication cursor. Crash after append before cursor is deduplicated using actual
file tail+SQL identity; crash mid-line archives the corrupt tail then truncates only the
incomplete derived suffix under publisher lock, appending exact canonical bytes. No valid
record is rewritten; a non-tail mismatch blocks export for explicit repair/rebuild from SQL.
State uses atomic temp+fsync+rename and includes last event/checkpoint refs. Separate `status`
reads a consistent read-only SQL snapshot and reports projection lag/corruption, does not
repair files, run agents or use stale projections for decisions. A writer's explicit export
step regenerates; physical power-loss guarantees remain out of scope.

Attempt metrics require run/task/node/attempt IDs; requested/runtime-selected/request-observed
and provider-acknowledged profile/skill; Pi session/branch epoch; context_group; reuse decision;
start/end/elapsed; outcome/retry/repair counts; evidence mappings; baseline/result SHA;
input/output/cache read/write deltas; start/end context and effective threshold/headroom;
measurement/version/settings/identity provenance and per-field unknown reasons. Code/gate
nodes use null Pi/token/context fields. Model output does not populate mechanical evidence.

Counters are attributable only for identical session+branch/counter epoch, exclusive active
operation and continuous monotonic before/after readings. Cache 0 is valid. Reopen establishes
new baseline even if session counters persist; missing/reset/endless/overflow/ambiguous
summary usage yields null deltas with reason, retained known partial observations, no negative
values/double counting. Killed final usage/cost is unknown. Occupancy is the SDK estimate, not
billed token total or exact tokenizer truth. Headroom at admission is not future-task capacity.

## Versioning, security and proof obligations

Run pins all schemas/config/handlers/resources/approvals. Changes never silently apply to
active runs. Safe evolution creates reviewed transactional schema migration with backup and
old-run read compatibility; graph/profile/contract changes require affected producing/owner
renewal, settled custody and explicit new run or supported transition boundary. No narrative
STATE migration. Never deserialize untrusted checkpoint blobs; SQLite and Pi session files
are restricted trusted runtime inputs, not user-supplied execution documents.

Permanent tests must kill actual controller/host/helpers at pre/post release, post-write,
post-commit and app-result/graph-checkpoint boundaries; reconcile durable registry across
restart, separate run dirs and real tool containment. Add actual role-safe Pi reopen and
pressure/compaction/retry tests at earliest supported seam with explicit permissions. Existing
probes inform constraints, not substitute for these shipped-helper tests. Failed/NOT RUN
required proof blocks its consumers; missing containment is a capability blocker, not model
failure or permission to install/escalate.

## Owner interaction, input authority and durable delivery

This correction extends the same SQLite authority, not a parallel interaction file store.
Pi conversation files hold original worker context; worker cannot write trusted answer/
approval files. Public CLI inputs are authenticated/authorized through the selected trusted
local owner/runtime path and restricted store ownership. Hashes/nonces alone bind messages,
not arbitrary OS users. Reject secrets/sensitive payloads before first durable write; store
only bounded safe question/answer/control content or permitted sanitized evidence reference.
No narrative coordinator memory, raw reasoning or transcript export.

| Extension | Identity / authoritative fields | Invariants |
| --- | --- | --- |
| `wf_gates` owner_question | gate/input ID, kind/category, manager-readable why/options/recommendation/impact; original run/task/node/attempt/role/session+branch/file-ref; source/task/approval/config/resource hashes; nonce; parking/pending/answered/blocked/cancelled | Pending only after normal completed question result+prompt/settled/idle+tool quiescence; a pin blocks ordinary selector substitution |
| `wf_owner_inputs` | UNIQUE(run,input_id), gate or active-control target, kind, bound original/active session+role and hashes, owner/parent provenance+answer receipt, safe payload hash, accepted/delivery stage, supersedes/cancellation | Same input+hash returns old receipt without resend; conflicting duplicate rejects; stale/wrong/unauthorized binding never dispatches. Accepted answer is not transport success |
| `wf_outbox` | UNIQUE(run,event_id,parent_generation), recipient capability/version/actual-parent binding, gate/input ref, recorded/transport_queued/parent_received/question_tool_invoked/answered/blocked, attempt/deadline/error/ACK refs | App transaction with pending gate; send only committed rows. Actual parent delivery/tool call receipts required, not opaque send flag; bounded retry, no authority in notifier |
| `wf_spend_reservations` | UNIQUE(run,outbound_request_id), envelope+approval hash, requested profile/action, reserved admission units/owner-selected limits, sent/unknown/reconciled observations | Counts all attempts/hosts/allowed retries/summary requests; unknown send cannot be refunded by restart; no exactly-once external bill claim |
| `wf_inputs` authorization/launch manifest | pinned envelope/profile/capability/test/network/external/mutation scope, real approval refs, explicit selected CLI-only or interactive adapter/parent/question-tool/runtime-env manifest | Known-gap preflight aggregates before tasks. Missing/denied/unknown paid authority blocks send. Scope drift renews approval, not boolean trust |

Run gains `parking`, `waiting_owner_input`, `paused`; task gains waiting-owner/control phases;
attempt gains parked/continuing segments. Parked is not completed task and cannot release
dependents or create an implementation commit. Parked run retains the worktree reservation
in wf_runs even if its process/advisory lock exits; a new start must not bypass it.
Original attempt can continue in a new host
with separately identified invocation/telemetry segments; aggregate deltas once, preserve
idle-wait vs active-time provenance and prior failed work. Source/task/approval/config changes
invalidate affected gates/input authority; accepted content remains historical, not erased.

### Transaction/order at question park and answer

1. Runner validates request category/rationale and envelope; persists request operation/pin,
   freezes conflicting tool and outbound admission. Custom tool completes normal terminate:true
   result. Require supported exclusive/all-terminating batch; otherwise safe blocker, not a
   claim arbitrary in-flight tools are paused. Await prompt+current settled/idle+tool custody.
2. Commit gate pending+outbox, return handler result, sync LangGraph checkpoint/interrupt.
   Outbox publish requires verified parked graph/application state. A crash with request
   intent but missing gate/checkpoint reconciles actual session/tool entry IDs before action;
   do not replay ask to duplicate question. No human waits on an unfinished tool result.
3. Same launching parent is awakened through configured transport, reads authoritative gate,
   actually uses ask_user and submits genuine receipt. CLI owner may independently answer;
   distinguish receipt source. One SQL transaction verifies current binding/external authority,
   deduplicates input, stores accepted answer and original-session delivery obligation. Mere
   actor/nonce/CLI flags are not authentication; worker-created files cannot approve scope.
4. Resume is deterministic continuation of the original conversation/role, not selector
   reassignment. Revalidate stored runtime inputs, safe original leaf/profile/resources/
   permissions and normal reliable headroom policy. If unavailable/unsafe/unknown or below
   required headroom, block for explicit owner recovery; never fresh-substitute the answer.
5. Deliver a new user envelope containing accepted input ID in that saved conversation before
   next model request. Record SDK/session entry receipt. Crash after acceptance/delivery does
   not reask or resend blindly: reconcile pending input+actual saved entry/current live work.
   If delivery cannot be proved, block. Scope-changing answer requires original producing
   approval, not permission to continue merely because input was delivered.

### Outbox, parent/UI continuity and live controls

Interactive launch records actual launching-parent runtime/session/transport recipient and
permissions through supported launch integration, public inspection and bound readiness ACK;
verify underlying parent/question tool provenance, not fabricated opaque IDs. Restrict local
SQLite/IPC ownership. Selected Paseo public CLI is tested; no private supervisor file sender.
Standalone core has no UI/Paseo requirement. In interactive mode required question delivery
must preflight; no silent manual polling. Actual ask_user invocation/answer receipt is an
observable release condition; facade noncompliance leaves gate pending, not fake success.

Transport is at-least-once: outbox event IDs and parent gate receipt dedup prevent repeated
questions; an answered gate always returns its prior receipt. A crash around the actual
external ask_user call needs durable claim and actual tool receipt reconciliation; unknown
invocation blocks reasking, not an exactly-once dialog guarantee. Bounded retries while runner
alive use verified busy queue/identity; separate reentry/reconnect reloads unresolved outbox
and revalidates parent generation. UI unavailable leaves waiting_owner_input plus explicit
transport blocker. CLI pending/status/answer still works. Process exit promises no automatic
background retry, no always-on daemon or background deciding LLM. Parent reconnect/provenance/
duplicate UI races require permanent production tests, not assumed from four idle wakes.

Control inputs may arrive anytime. Run-scoped inquire/pause/cancel between tasks or during
preflight has null worker identity and uses verified run/owner binding; steer/followUp needs
an actual active session. Startup authority decisions are preflight gates, not worker
technical questions. `inquire|steer|follow_up|pause|cancel` binds active task/
attempt/session/role+hashes and owner envelope. Record received→queued→SDK-delivered→worker-
acknowledged independently; SDK queue ACK isn't worker receipt or semantic compliance.
Inquire reports observable facts/worker response, no private reasoning access. Changed scope
is blocked for approval, not injected as an accepted answer. Pending-question pin cannot be
bypassed by a steering message. Pause/cancel transitions require supported abort/drain,
validated task-tool group empty and partial-file/Git reconciliation before paused/check/
commit/reuse/replacement; surviving tools still trigger ORPHAN_PROCESS. Idle reusable host
lifetime remains distinct. Pause/cancel records reconciled quiescence evidence without
pretending the stopped worker acknowledged it. Unknown delivery/quiescence retains exact blocker and inputs.

### Upfront autonomy and budget enforcement boundary

Authorization envelope is part of approved task/run identity, not permission inferred from
fixture or planning model choice. Preflight enumerates all known missing capabilities/
permissions/spend choices before any task dispatch; no repeated routine cost/technical/test
questions inside verified scope. Unexpected necessary manager choice includes impact/options;
unknown safety/auth remains blocked. Eligibility cannot be solved universally by category enum.

If owner approves numeric limits, SQL reservations are run-wide before each supported final
outbound send, not per-process counters. Host requests runner admission via registered guard
before provider transport; versioned observer must cover retry/summary paths or disable those
paths. Admission-count bounds are distinct from provider-confirmed token/dollar enforcement;
unsupported hard cap claims block configuration. Unknown invoice/partial sent usage remains
unknown/reserved, no automatic refund. No numeric production cap is selected here. An explicit
owner-scoped allowance without numeric limit is a possible envelope decision, never default
implicit spend; missing references fail closed. Permanent tests must verify send/reservation/
input/outbox crash windows and all original manual/permission/current-content gates.
