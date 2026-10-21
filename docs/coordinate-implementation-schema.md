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

`--executor` is ordinary JSON containing worker `provider`, `model`, `effort`, with an
optional `reviewer` object containing its own `provider`, `model`, `effort`. The engine
passes the worker profile to implementation sessions and the reviewer profile to the
separate fresh read-only review session. Omission preserves worker-profile review for
compatibility; an explicitly malformed reviewer profile is an error, not a fallback.
The SDK resolves each actual selected model or reports its real error. No observed-versus-requested
proof, config hash, resource pin, binding assessment or SDK/Node equality check.
`package-lock.json` remains explicit installation metadata for the tested SDK, not launch
ceremony. Project-specific selection is in the [operating guide](coordinate-implementation.md).
The monitoring descriptor's `requested_executor` still describes the worker profile; it
does not establish the reviewer's actual model or retrofit historical reviewer records.

## Current progress tables

The project database remains `.coherence/workflow/workflow.sqlite`. New execution uses:

- `execution_runs(run_id, state, baseline, result, error)`;
- `execution_tasks(run_id, task_id, state, baseline, result, details)`.

Task details retain useful summary, actual command exit codes, explicit task-edited checkpoint paths,
and known generated-artifact facts. State is ordinary running/complete/failed/interrupted/abandoned history,
not proof of liveness, effect settlement or dispatch eligibility. IDs distinguish new runs; existing runs are not replayed.
SQLite errors report the actual operation. No graph saver, attempt selection or effect ledger
is consumed to run new work. The writer lock is the ordinary per-worktree
`coherence-workflow.lock`, held by the runner and inherited by its active SDK host.

## Monitoring recording v1

New runs may additionally retain a closed `execution_monitor_runs` descriptor and ordered
`execution_observations`. These are append-only best-effort monitoring facts: registration or
append failures warn safely and never alter normal progress, checks, Git, or errors. Descriptors
retain only declared task IDs/dependencies and explicitly supplied public presentation; observations
retain closed phase/kind/fact fields, never prompts, answers, commands, output, findings, or errors.
Existing progress and historical rows are neither converted nor inferred. The retained closed descriptor has a
distinct description version, phase labels with possible branches and pre-recording markers, task IDs and
safe optional presentation, requested executor, revision-or-unknown, declared correction, and private
runner identity in its dedicated column. Descriptor/identity collection and warning output are best effort. If a later append recovers after a
recording failure, the recorder appends a closed `gap` marker; it never reconstructs missing events.
Engine emissions include
per-command check start/outcome and checkpoint start/outcome; command text and output remain private.
A no-change checkpoint is recorded explicitly, while an uncertain Git exception is only a failed boundary.
Facts are validated by phase and milestone before append: Git fields are hashes, roles and error categories
are closed enums, and counters/exit codes/booleans retain their actual types. Allowlisted names do not admit
arbitrary scalar data. Question observations retain only requested, terminal-returned, host-sent, or delivery-failed state and a
parent occurrence ID. They never retain question or answer text; a send is not a consumption claim.
Recorder callbacks are independently best effort at requested, returned, sent and delivery-failed points;
their failures cannot prevent a terminal answer or replace a transport error.
Read-only status/history exposes recording version, stable occurrence IDs and review base/head ranges when
present; absent or corrupt monitoring is reported unknown. Explicit abandon preserves prior progress/error
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

`pi_adapter.py` and `pi-host/host.mjs` exchange newline-delimited JSON for a prompt, local
edit/write path checks, current owner questions, optional event observations and final text/error.
When explicitly launched by the project parent-session bridge, the adapter uses one private
Unix-socket request/reply connection with a token, parent session, run and request identity; EOF,
unavailable endpoints and uncorrelated replies stop with the actual bridge error. The bridge keeps
its pending request only in memory and never stores question or answer text in monitoring SQLite.
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
A result retains text plus fresh before/after observations (session/branch/epoch/entry, available
counters, and context fields). An adapter explicitly sends `sessionObservations: true` before the
host emits the optional standalone opened-identity record; without that opt-in, the host emits only
legacy record kinds. On opted-in calls, the opened identity precedes invocation, so a terminal
transport failure retains its existing session and actual cause for inspected targeted resumption;
it never authorizes a blind relaunch. Unknown optional observations remain unknown; they are not a
transport failure or evidence that reuse is safe. The host waits for both prompt completion and
SDK idle before returning or disposing. `compaction_start`/`compaction_end` are forwarded when
emitted by the SDK; old auto-compaction event spelling remains observable for compatibility.

Independent review uses a fresh session restricted to read/search tools and an ordinary
`{approved: boolean, findings: string[]}` result. That is a small communication interface, not
provenance/evidence attestation. Findings are honestly reported; no SQL dispositions, repair
templates or budget catalogue is required. Focused Git commits select only explicit task-edited source/deliverable paths and retain their actual
parent/history with normal hooks and signing, never effect receipts. Filesystem, index, HEAD and undeclared-output
changes are not execution admission or checkpoint-selection evidence.
