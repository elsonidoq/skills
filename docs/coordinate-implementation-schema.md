# Coordinate Implementation schema and storage owner

See the [operating guide](coordinate-implementation.md) for actual invocation and safety.
This operative contract supersedes the old executable graph/effect/host/projection schemas.
Historical [design contracts](../specs/003-coordinate-workflow/contracts/README.md) remain
unchanged historical documents, not byte-equality or execution-eligibility mandates.

## Task input

`runtime/coherence_workflow/intake.py` owns the six task-linter checks. The packaged
`schemas/task.schema.json` describes ID/work and optional dependencies/context; it is not a
second launch validator. A bare task list or `tasks` object is accepted. No mandatory
approvals, evidence, order, execution intent, check catalogue, path list or envelope.

A task-contract object may also contain dedicated paid-use fields outside individual task text:
`paid_scope` is an explicit object with `approved: true`, exact `agent_providers` for the selected
worker/reviewer providers, and an `apis` string list; alternatively `paid_apis` is the named application/test
API list used in the one owner question. Missing, denied or mismatched scope stops before storage or any
provider launch. Credentials, task descriptions and historical rows are never approval. The accepted unchanged
scope/exclusions are prompt context for all roles, not a receipt, budget service or persistent permission store.

`--executor` is ordinary JSON containing worker `provider`, `model`, `effort`, with a
required `reviewer` object containing its own `provider`, `model`, `effort`. The engine
passes the worker assignment to implementation sessions and the reviewer assignment to
fresh read-only review/rereview sessions. Actionable first-review findings continue in that
reviewer's saved session with scoped writer tools, a correction plan and implementation;
the recorded `fixer` stage uses the reviewer model, not a separate worker-model agent. Missing or malformed reviewer configuration
is an actionable error, never implicit worker-assignment inheritance. Explicitly identical
worker and reviewer values are allowed; reviewer contexts remain independent.
The SDK resolves the exact selected model or reports its real error. Before prompting, the
host checks that SDK-exposed provider, model and effort match the requested assignment; it rejects
clamping, omission or substitution. Opted-in opened-session and result `before`/`after`
observations separately expose `requested_assignment` and `sdk_observed_assignment`, each with
`provider`, `model` and `effort`; unavailable SDK fields are `null` (unknown). SDK-exposed state
is not provider-internal execution proof; unknown actual execution remains unknown. No config hash, resource pin, binding assessment or
SDK/Node equality check is required.
`package-lock.json` remains explicit installation metadata for the tested SDK, not launch
ceremony. Project-specific selection is in the [operating guide](coordinate-implementation.md).
The monitoring descriptor's `requested_executor` still describes the worker profile; it
does not establish the reviewer's actual model or retrofit historical reviewer records.

## Current progress tables

The project database remains `.coherence/workflow/workflow.sqlite`. New execution uses:

- `execution_runs(run_id, state, baseline, result, error)`;
- `execution_tasks(run_id, task_id, state, baseline, result, details)`;
- private `execution_run_inputs(run_id, contract, executor, authority, review_base)` captured before task mutation; and
- append-only private `execution_history(run_id, task_id, kind, state, details, recorded_at)`; and
- required chain rows: `execution_review_executions` (actual reviewer/fixer ID, ordinal/round, explicit trigger/predecessor and range), append-only `execution_review_attempts` (dispatch/outcome/uncertainty, private parsed findings and references), and `execution_review_suggestions` keyed to the attempt (optional parsed nonblocking suggestions).

Legacy `execution_usage_memberships` and `execution_usage_intervals` remain untouched when present; new runs do not write or read them.

Inputs preserve the parsed original contract/order, selected executor, settled authority and resolved initial review base. Explicit same-run resume is limited to failed/interrupted rows: it records its inspected prior invocation/cause, reuses those retained inputs without a new paid-scope question, and skips only completed task rows with matching checkpoint history/SHA. Missing retained input/history or uncertain effects remains an action-specific limit, never a filesystem admission test. History retains actual invocation/task/check/checkpoint outcomes, so a failed required command/exit/output remains after correction. Before a task mutation, append its explicit claimed source paths and known generated artifacts; an interrupted same-run task may reuse only those task-local facts for its next edit or selective file cleanup. Checkpoint facts retain explicit task-edited paths, known generated artifacts, SHA and available actual parent. Latest task rows are a current projection only; they cannot erase failure/interruption history. The safe CLI projection exposes task IDs, review base and operation facts, never original task text, prompts, answers or check output. These are operation-local facts, not global HEAD/index/dirty/file snapshots, unchanged-tree proof, custody ledger, custom trailers, legacy backfill or resume policy.

A failed required-check attempt is returned only to the same task's corrective worker context; a later real pass is required before checkpointing, while an unavailable safe correction retains its actual blocker. A whitespace, source, hook, or Git checkpoint failure likewise retains its actual error, returns to that same task for safe correction, reruns affected required checks, and retries with normal hooks/signing intact. If a commit reports failure/interruption, the runner first reconciles that operation's selected paths, attempted parent, and actual HEAD; a matching completed checkpoint retains its SHA without recommit, while another or unrecoverable result reports the exact blocker. Required original-input, history, and progress writes are atomic operation-local boundaries: after a SQLite failure the store re-reads that operation, retains a known completed result without replay, or makes one safe write correction before the dependent mutation. An unrecoverable or unreadable result reports the affected persistence operation and never launches/replays task tools, commits, or invented history. Optional monitoring, metrics, and telemetry writes remain nonblocking reported gaps and never use this required-data boundary. New terminal-call metrics are JSONL-only: no prompts, answers, transcripts, session paths, or SQLite metric mirror. Status/history derives its qualified JSONL subtotal and coverage from exact ordinary dispatch identities; missing or failed optional appends remain partial rather than zero or an invoice claim. State is ordinary running/complete/failed/interrupted/abandoned history,
not proof of liveness, effect settlement or dispatch eligibility. IDs distinguish new runs; existing runs are not replayed.
SQLite errors report the actual operation. New starts retain `execution_run_inputs.authority.review_policy: "owner-pair-v1"` before dependent execution; resume consumes that retained policy, inputs, executor and base. Absent policy remains the historical two-review/one-fixer lifecycle, and an unknown retained name stops only the affected continuation with a compatible-version diagnostic. For `owner-pair-v1`, append-only `execution_history` retains only an affirmative actual-owner pair grant identity, rejecting execution, exact base/head, original-scope reference, and assigned fixer/fresh-reviewer identities—never owner Q/A or sessions. The store validates the latest settled actionable rejection and original-scope digest at authorization/reservation, rejects multiple grants for that rejection, then atomically records single fixer consumption/reservation under the writer transaction. Dispatch itself validates causal role/order/round/range and the exact assigned reservation for additional pairs; a caller cannot bypass the grant by supplying a larger ordinal. The paired reviewer can be reserved only after that exact fixer has a successful settled outcome. Wrong grant/rejection/range/scope/order, failed fixer, or uncertainty stops without dispatch; required-write reconciliation retains a known write without duplicating facts. A review/fixer dispatch is persisted before its dependent invocation; reopen retains the original rejection, attempts, positive ordinals/rounds, grants/reservations, and immutable completed task checkpoints. A positive first verdict with no findings completes even when optional suggestions are present; findings reject despite a positive flag. Blockers require a `path:line - defect` location, concrete impact, and requirement/correctness/security/data-safety basis in ordinary prose (no mandatory literal suffix), while suggestions are nonblocking and separately retained. A well-formed actionable first rejection dispatches the automatic fixer and fresh reviewer. Each later actionable rejection requires a new exact durable owner grant before its assigned one pair; completed review finalization reuses its exact verdict/head. Safe normalization preserves only an actual result; malformed types/results, interrupted, uncertain, negative-empty, nonactionable, unrecoverable fixer/checkpoint, or target drift stops without another dispatch. Old finding strings and attempt rows remain historical and are never reclassified. The repair primitive accepts and forwards explicit rejecting-review/predecessor, fixer identity, and positive assigned review/fixing rounds from its caller, subject to retained dispatch policy; legacy chain selection still assigns only the first repair, so this parameterization neither selects nor authorizes a later lifecycle round. The scoped fixer retains its own execution ID, explicit review predecessor, check attempts, interval and focused checkpoint/parent rather than changing original task membership or checkpoint identity. Initial and same-stage corrective repair prompts retain original contracts/owned paths, paid exclusions, current-launch and routine authority, and require a concise correction plan, directly related adverse-path examination, and integrated original-acceptance reasoning without scope expansion; a fixer never independently accepts delivery. Correctable fixer check/checkpoint failures return to that same fixing context and require affected real passes before its checkpoint. An uncertain invocation is not success or replay permission. Optional monitor facts never provide this authority. Review outcomes privately retain the returned SDK session identity for reopening before repair; repair keeps skill discovery disabled as in the initial review. Safe CLI owner history exposes parsed actionable findings, separately projected suggestions, and range/commit references, never saved SDK identities, raw reviewer payloads, prompts, or answers. No graph saver, attempt selection or effect ledger
is consumed to run new work. The writer lock is the ordinary per-worktree
`coherence-workflow.lock`, held by the runner and inherited by its active SDK host.

Additional owner-authorized repairs use existing private history for recovery: `fixer_invocation` starts precede calls; returned facts retain explicit paths/artifacts, baseline and head, not raw repair answers. `fixer_checks` records local-check start/pass, and `fixer_checkpoint` start retains the attempted parent, selected paths and expected blob hashes before Git. Reopen may dispatch a provably not-started reserved stage once, or continue returned local work without repeating its provider call. It retains a matching passed checkpoint or reconciles a completed commit against that intent before writing its missing result. Missing/uncertain facts, unsettled checks, failed invocations and mismatched SHA/parent/content stop the affected continuation. This does not upgrade historical gaps or reset consumed grants. Safe CLI `review_authorization.next_stage` follows the last execution outcome as well as reservation facts, distinguishing completion, blocked calls, pending owner decisions and eligible local reconciliation; it is a projection, never dispatch authority.

## Metric artifact JSONL v1

`metric_artifacts.py` owns the independently callable, optional file contract for future
per-terminal-invocation metrics. It creates only
`.coherence/metrics/run-<sha256(UTF-8 run ID)>.jsonl` below the selected project root;
the digest is filename encoding while every closed UTF-8 newline-framed object retains the
exact run and invocation IDs. `version: 1` rows contain only run/invocation/task identity,
closed worker/corrective/fixer/reviewer role and terminal outcome, optional positive
fixing/review ordinals, `metrics.interval_record`'s typed token/USD/compaction/summary
subset, typed before/after cumulative/context snapshots, and selected/actual session mode,
safe selection reason and actual session ID. Modes are `fresh`,
`reused_from_earlier_task`, `continued_same_task`, or `unknown`; selected mode never
confirms actual opening. Prompts, errors, paths, credentials, raw SDK dictionaries and
arbitrary nested payloads are rejected.

The helper reserves a previously absent clean target under the existing writer authority,
uses safe-path/no-symlink checks, serializes complete short-write-aware appends and closes
before reporting success. Existing, staged/dirty, symlinked, replaced or incomplete-tail
files are preserved and reported as optional gaps: no truncation, cleanup, fsync guarantee,
per-append commit or workflow veto. Its read/summary API reads one complete-line prefix,
deduplicates exact invocation IDs and reports missing expected dispatch IDs, conflicting
records, invalid rows and unknown fields as partial/unavailable rather than zero or complete.
Engine terminal-call boundaries attribute each actual worker/corrective/fixer/reviewer call to this helper's JSONL rows. They reset adapter observations before every prompt, retain before-only failures honestly, and derive CLI/runtime summaries from exact ordinary dispatch IDs plus JSONL records. Selection reason/mode is intent; only the current host's explicit opened-session observation confirms actual mode/identity. After every child call drains, the runner-only finalizer validates the exact artifact, stages and commits only that path once with normal hooks/signing, and verifies its actual parent/diff. The reviewed code SHA/range and task checkpoints remain unchanged; a separate artifact SHA/current HEAD is explicitly not application-review evidence. Empty/missing content has no commit. Collision, invalid tail, symlink/drift, staging/path mismatch, hook/signing error, or an abrupt process death leaves bytes for inspection and reports a separate optional artifact failure; it never retries blindly, replays work, or creates an extra review. The artifact is not projected to the monitor (T012).

## Monitoring recording v1

New runs may additionally retain a closed `execution_monitor_runs` descriptor and ordered
`execution_observations`. These are append-only best-effort monitoring facts: registration or
append failures warn safely and never alter normal progress, checks, Git, or errors. Descriptors
retain declared task IDs/dependencies, safe optional labels, and complete explicit task
`outcome`/`description` work text; missing work text remains unknown, not reconstructed from
summaries or current files. Descriptor version 3 also retains explicit `initial_review: {planned: true}`
intent, separately from generic phase vocabulary. It never retains arbitrary task objects or prompts.
The viewer's planned task/review projection accepts version 3 only; older descriptors expose no
plan, so their calls cannot receive task numbers from that projection. Stored history is not
migrated or backfilled.
Observations retain closed phase/kind/fact fields, never prompts, answers, commands, output,
findings, or errors. Recorded facts include actual review execution IDs/ordinals, explicit trigger
and predecessor execution IDs, fixer-owned check/checkpoint IDs, review range/outcome/count,
and existing checkpoint hashes.
A question's parent occurrence is callback lineage, not execution causality. The descriptor declares
only the closed vocabulary; it does not assert any stage ran. Missing legacy links stay unknown: no
backfill or inference from descriptor, role name, timestamp, or `correction_of` is permitted.
Existing progress and historical rows are neither converted nor inferred. The retained closed descriptor has a
distinct description version, phase labels with possible branches and pre-recording markers, task IDs and
safe optional presentation, requested executor, revision-or-unknown, declared correction, and private
runner identity in its dedicated column. Descriptor/identity collection and warning output are best effort. If a later append recovers after a
recording failure, the recorder appends a closed `gap` marker; it never reconstructs missing events.
Engine emissions include
per-command check start/outcome and checkpoint start/outcome; command text and output remain private.

Task-worker recording has a closed, future-run-only invocation vocabulary. Each actual prompt call emits one
run-scoped `invocation_id` at its real start and terminal return/failure, with `invocation_kind` of
`task_worker` or `corrective_worker`. A corrective call names its exact selected predecessor and retains its
ordered `correction_chain`. At task dispatch, `selected_input_checkpoints` records only the completed declared
prerequisite checkpoints selected by the sequential runner: each value contains its checkpoint occurrence ID,
task ID, producing invocation ID, and that producer's correction chain. A passed task checkpoint records the
final producing invocation and chain, so a later task consumes an exact producer rather than a viewer-selected
latest attempt. Failed/interrupted worker calls and the enclosing terminal boundary may name the explicit
`stopped_by_invocation_id`; `support_invocation_id` is reserved for separately recorded explicit support, never
inferred from timing, dependency declarations, or a shared session. These typed relations are producer facts
for later consumers, not model-reading/obedience or concurrency proof. The actual first reviewer additionally
records its exact selected completed task outputs using the same checkpoint shape and its reviewed range; an
unrecordable output leaves membership unknown rather than substituting every plan task or commit in that range.
Each actual fixer prompt has its own invocation ID and correction chain while retaining its fixing-round and
review trigger/predecessor identities. Re-review has no first-review membership claim. Invalid or unavailable
optional facts are rejected or become recorder gaps without changing ordinary execution. No prompts, errors,
summaries, output, paths, or arbitrary payload fields enter monitoring facts.
The read-only monitor may correlate an actually recorded execution ID with its required chain row: it exposes only explicit reviewer/fixer predecessor relations, typed outcome/range, SHA references, and findings matching the review protocol's inert `path:line - issue` form. Raw reviewer payloads, arbitrary findings, prompts, answers, errors, and secrets remain private; absent/dangling IDs remain unknown and are never inferred from order, labels, timestamps, or `correction_of`.
A no-change checkpoint is recorded explicitly, while an uncertain Git exception is only a failed boundary.
Facts are validated by phase and milestone before append: Git fields are hashes, roles and error categories
are closed enums, and counters/exit codes/booleans retain their actual types. Allowlisted names do not admit
arbitrary scalar data. Question observations retain only requested, terminal-returned, host-sent, or delivery-failed state and a
parent occurrence ID. They never retain question or answer text; a send is not a consumption claim.
Recorder callbacks are independently best effort at requested, returned, sent and delivery-failed points;
their failures cannot prevent a terminal answer or replace a transport error.
Read-only status/history exposes recording version, stable occurrence IDs and review base/head ranges when
present; the monitor's public chain DTO retains known dispatched review executions even without
matching observations. Exact same-run execution/invocation identity reconciles their activities
and call metrics; a fixing-round dispatch alone does not prove an individual prompt occurred.
Acceptance attaches only to its explicit terminal reviewer ID and recorded range. Absent or corrupt
monitoring is reported unknown. Explicit abandon preserves prior progress/error
history and appends an `abandoned` observation when the run was registered.

## Historical records

All historical `wf_*` and LangGraph tables/rows remain readable in place. No automatic rewrite,
drop, migration or reconciliation occurs; incomplete SDK/tool/graph/Git intents remain incomplete.
The semantic historical reader v1 remains read-only for existing history. `status` / `history`
open SQLite with `mode=ro`; display errors do not veto execution. Historical schema/projection
contracts do not impose equality with current product files.

Explicit `abandon` retains the historical identity/scope inspection needed not to replace a live
writer. It only marks the selected old run `ABANDONED`, sets its reservation to zero and appends
an honest abandonment event. It does not manufacture completion, delete alarms/operations,
release cgroups, signal processes or discard partial files. Current runs can be labelled
abandoned without rewriting their error/task history. No legacy execution stack is retained.

## SDK transport

Private `worker_invocation` history records each dispatched call's prompt, stable reuse key,
saved-session identity and terminal outcome/cause. Explicit resume supplies that prior context,
not an unchanged original assignment. A missing terminal outcome or legacy invocation data
cannot authorize replay. A terminal expensive failure requires inspection of the saved call/session
and an explicit diagnosed, targeted correction through current owner input before continuation;
unknown cause or absent saved identity stops that launch. Genuine interrupted unfinished work
may continue with the retained context and compatible saved identity when available.
Worker-only `cleanup_artifact` transports one path to the runner's selective known-file cleanup;
errors return to the SDK tool, and reviewer tools remain read/search-only. Boundary headroom uses
the SDK's effective model-specific reserve, context occupancy/window and compaction enabled/applicable
facts; unavailable observations select fresh. Each check's combined stdout/stderr and actual
exit/interruption outcome is retained before the next command, including earlier passes in failed lists.

`pi_adapter.py` and `pi-host/host.mjs` exchange newline-delimited JSON for a prompt, local
edit/write path checks, current owner questions, optional event observations and final text/error.
A caller that explicitly supplies an initial worker/fixer `steering` target (`run_id`,
`task_id`, `invocation_id`, and closed worker/fixer `role`) selects the multiplexed host protocol: the host privately advertises the
created session identity in an active target record; callback replies are `reply` records
correlated to host callback IDs; and `steer` control records carry an exact target, request ID
and inert owner-direction text. The Python adapter is the sole initial-request opt-in: it has one
stdout decoder, serializes stdin writes, exposes the active target only for that host invocation,
and sends controls through its `steer` hook. For an attached parent bridge it privately publishes
only that runner-created exact target and forwards controls matching it; target/session tokens and
direction text are never monitoring/SQLite/public data. It continues decoding target/status records while a
callback waits; a callback reply remains correlated and cannot be supplied by a control record.
The host reports accepted, queued, consumed, failed-unavailable or unknown separately. It
validates consumption only from the matching SDK user `message_start`; queue insertion/removal
is not consumption. Same request IDs are idempotent, new IDs remain distinct, and settlement,
cancellation, EOF or disposal closes the target without retargeting. Without this explicit opt-in,
the original uncorrelated callback/reply vocabulary remains the only transport vocabulary;
`sessionObservations` alone does not select steering. When explicitly launched by the project parent-session bridge, the adapter uses one private
Unix-socket request/reply connection with a token, parent session, run and request identity; EOF,
unavailable endpoints and uncorrelated replies stop with the actual bridge error. An owner-only continuation request additionally carries a marker and decision context (rejecting execution, original reviewed base/head, original scope, and exactly one repair/fresh-review pair with no repeat grant). The bridge keeps that marker through its in-memory pending/reply correlation, requires registered `ask_user`, rejects the routine reply route, and accepts only a nonempty answer relayed through its dedicated owner-reply route. This does not attest human identity or persist a transcript: the bridge keeps
its pending request only in memory and never stores question or answer text in monitoring SQLite or public projections. Missing owner capability, cancellation, empty answer, or invalid correlation stops actionably; routine technical questions retain their ordinary coordinator route.
Invalid framing/types are communication errors, not permanent launch poison. No record size
cap, pressure protocol, watchdog, telemetry prerequisite or closed host manifest.
SDK tools handle normal read/edit/write/search/command errors and output continuation.
SDK prompt completion, retries and compaction retain their standard behavior.

For runner-owned saved-session reuse, the adapter may pass back only the host result's private
`session` identity (`id`, private file, and effective resource compatibility) on a later prompt.
The runner supplies a stable `reuseKey` when instructions/settings/authority need to be part of
that compatibility; a changed key rejects reuse. The host creates or opens that exact `SessionManager` file under
`.coherence/workflow/sessions`, rebuilds the current resource loader and task callbacks/tools on
every open, and rejects an identity/resource mismatch rather than adopting an ambient session.
A result retains text plus fresh before/after observations (requested assignment, SDK-observed
assignment, session/branch/epoch/entry, available counters, and context fields). An adapter explicitly sends `sessionObservations: true` before the
host emits the optional standalone opened-identity record; without that opt-in, the host emits only
legacy record kinds. On opted-in calls, the opened identity precedes invocation, so a terminal
transport failure retains its existing session and actual cause for inspected targeted resumption;
it never authorizes a blind relaunch. Unknown optional observations remain unknown; they are not a
transport failure or evidence that reuse is safe. The host waits for both prompt completion and
SDK idle before returning or disposing. `compaction_start`/`compaction_end` are forwarded when
emitted by the SDK; old auto-compaction event spelling remains observable for compatibility.

Per-open usage observations may derive one private interval record: fieldwise cumulative
`input`, `output`, `cacheRead`, and `cacheWrite` deltas; their defined total; and available
estimated USD. Each value carries SDK provenance or an unknown reason. Deltas require a monotone,
continuous exclusive session/branch/epoch; missing ends, resets and ambiguous intervals remain
unknown while independently valid fields remain available. Context occupancy is never spend.
Compaction count is the set of newly persisted compaction entry IDs, so starts that do not persist
an entry do not count. Any available per-entry summary overhead is labelled as a subset already
included in SDK deltas, never added again; unavailable overhead is unknown. These records are not
membership, storage, CLI, or invoice data.

Independent review uses a fresh session restricted to read/search tools and an ordinary
`{approved: boolean, findings: string[], suggestions?: string[]}` result. Suggestions default to
empty and are nonblocking; blocker findings retain location, impact, and accepted basis. That is a
small communication interface, not provenance/evidence attestation. No SQL dispositions, repair
templates or budget catalogue is required. Focused Git commits select only explicit task-edited source/deliverable paths and retain their actual
parent/history with normal hooks and signing, never effect receipts. Filesystem, index, HEAD and undeclared-output
changes are not execution admission or checkpoint-selection evidence.
