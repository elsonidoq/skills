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

`--executor` is ordinary JSON containing `provider`, `model`, `effort`. The SDK resolves that
actual selected model or reports its real error. No observed-versus-requested proof, config
hash, resource pin, binding assessment or SDK/Node equality check. `package-lock.json` remains
explicit installation metadata for the tested SDK, not launch ceremony.

## Current progress tables

The project database remains `.coherence/workflow/workflow.sqlite`. New execution uses:

- `execution_runs(run_id, state, baseline, result, error)`;
- `execution_tasks(run_id, task_id, state, baseline, result, details)`.

Task details retain useful summary, actual command exit codes and changed paths. State is
ordinary running/complete/failed/interrupted/abandoned history, not proof of liveness, effect
settlement or dispatch eligibility. IDs distinguish new runs; existing runs are not replayed.
SQLite errors report the actual operation. No graph saver, attempt selection or effect ledger
is consumed to run new work. The writer lock is the ordinary per-worktree
`coherence-workflow.lock`, held by the runner and inherited by its active SDK host.

## Monitoring recording v1

New runs may additionally retain a closed `execution_monitor_runs` descriptor and ordered
`execution_observations`. These are append-only best-effort monitoring facts: registration or
append failures warn safely and never alter normal progress, checks, Git, or errors. Descriptors
retain only declared task IDs/dependencies and explicitly supplied public presentation; observations
retain closed phase/kind/fact fields, never prompts, answers, commands, output, findings, or errors.
Existing progress and historical rows are neither converted nor inferred.

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
Invalid framing/types are communication errors, not permanent launch poison. No record size
cap, pressure protocol, watchdog, telemetry prerequisite or closed host manifest.
SDK tools handle normal read/edit/write/search/command errors and output continuation.
SDK prompt completion, retries and compaction retain their standard behavior.

Independent review uses a fresh session restricted to read/search tools and an ordinary
`{approved: boolean, findings: string[]}` result. That is a small communication interface, not
provenance/evidence attestation. Findings are honestly reported; no SQL dispositions, repair
templates or budget catalogue is required. Focused Git commits are validated against actual
baseline/diff/paths with normal hooks and signing, never effect receipts.
