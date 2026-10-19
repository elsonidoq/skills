# Coordinate Implementation schema owner

This is the canonical owner for the **delivered foundation**, alongside
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
| `agent-result.schema.json` | Untrusted proposed implementation/review result; host integration later |
| `execution-result.schema.json` | Runner-audited outcome, REQUIRED dispositions and mandatory survivor blocking; public aggregation later |
| `host.schema.json` | Host envelope; op-specific host payload validation later |
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
that an SDK/result adapter is present. Each registered check has closed `test_file`/`selector`
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
execution-result envelopes. Public projections, metrics/null-reason accounting, intake/owner
authority, Git commit receipts and UI/SDK adapters remain later tasks and must use the
packaged contracts plus their semantic rules. No schema-valid fixture can authorize execution.
