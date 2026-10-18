# Candidate A disposable proof (not the migration)

The parent must independently accept the result. See `../../../stack-validation-report.md`.
Only run this in an authorized checkout with working Pi credentials and Git identity. Never
pass an existing or production repo as `--root`. `init` deliberately creates a toy Git repo.
No daemon, orchestration model, service, global configuration writes, or deployment is used.

## Reproduce

From repository root, with Python 3.12, Git, and Pi 0.87.1:

```sh
mkdir -p .pi/workflow-validation/reproduction/tmp
export TMPDIR="$PWD/.pi/workflow-validation/reproduction/tmp"
export PYTHONDONTWRITEBYTECODE=1
python3 -m venv .pi/workflow-validation/reproduction/venv
.pi/workflow-validation/reproduction/venv/bin/pip --no-cache-dir install -r docs/evidence/workflow-stack-validation/requirements.txt
export POC_ROOT="$PWD/.pi/workflow-validation/reproduction/run"
.pi/workflow-validation/reproduction/venv/bin/python docs/evidence/workflow-stack-validation/test_harness.py
.pi/workflow-validation/reproduction/venv/bin/python docs/evidence/workflow-stack-validation/harness.py status --root "$POC_ROOT/real" --task t2
```

The run directory must not exist. The tests intentionally SIGKILL two **synthetic-worker**
runner subprocesses, then restart the real LangGraph engine on its SQLite checkpoints.
The real worker test makes two small paid model requests, with tools restricted to read/write,
explicit toy-root instructions, disabled extension/skill/context discovery, and trusted known
local settings. These are instruction/tool constraints, **not** an OS filesystem sandbox.
Two inline instruction skills are deliberately used instead of loading production skills.

`workflow.yaml` and `schema.json` are the declarative seam. `variant.yaml` is the executed
YAML-only profile alias/skill/edge change. Both profile aliases bind to the same verified
Sol model; no different model was tested or escalated. The synthetic variant ends after
implement, instead of running check/commit. Unknown handlers fail validation, not eval/exec.

## Durable state and recovery boundary

SQLite's **LangGraph checkpointer** is authoritative for graph position and node results.
Per-task thread IDs are operation identities within a unique disposable run root. Sync
checkpoint durability is explicit. Filesystem operation receipts persist intent before
worker dispatch. For a replayed worker, only an exact expected file is reconciled;
uncertain partial content raises rather than re-dispatching. Git recovery checks the unique
task commit subject, expected file, HEAD, parent baseline and single owned changed path.
A POSIX advisory lock prevents two CLI writers in the same run directory.

`state.json` is the latest queried task snapshot (schema 1), not a full run registry.
`events.jsonl` / `metrics.jsonl` are append-only derived observations, not decision inputs.
Their `sequence` is projection append order; `projection_id` is task/index/content hash,
so repeat status is idempotent and revised metric snapshots append a distinct observation.
Within checkpoint events, sequence is task-local. Read the latest revision for a task/attempt.
An interruption can leave projections behind SQLite; querying status refreshes them.
The durable SQLite plus Git/file reconciliation is **not exactly-once external effects**.
JSONL append/fsync/power-loss hardening and multi-host locking are not demonstrated.

A runner exit stops progress; CLI `run --resume` is required. Real in-flight Pi orphan/process
recovery is not tested: do **not** blindly resume a real interrupted worker; verify it stopped
and reconcile or block first. Crash tests use no live Pi process. Real-task CLI starts and
stops Pi; the integration test retains the same RPC process across the two task threads to
exercise greedy reuse. Durable reattachment across host restarts is not claimed.

## RPC completion boundary

Pi 0.87.1 `docs/rpc.md` and `docs/json.md` distinguish low-level `agent_end` from
session-level **`agent_settled`**: retries, overflow recovery, compaction or follow-up work
can continue after agent_end. The reader independently routes responses by request ID and
tracks lifecycle under a condition lock; request waits never consume/discard lifecycle.
Prompt tracking is registered **before sending**, so settlement before the prompt response
is retained. Prompts are serialized through settlement; an active prompt must observe its
own agent_start before accepting settled, preventing an idle/prior-task settled event from
completing the next task. Prompt errors/timeouts poison the adapter rather than permit reuse
of uncertain work. This assumes the PoC's single prompt writer and disabled extensions, not
arbitrary externally queued work. Metrics include per-prompt lifecycle counts; after-task
telemetry, checks and commits only occur after the response and current agent_settled.

The synthetic `test_00_rpc_settlement_protocol` exercises fast settlement before response,
a stale prior-task settled event, low-level agent_end followed by simulated retry/compaction,
and a second agent_end that must still not finish the wait. Real retries/compactions are
not induced; the two real tasks each observed start/end/settled and distinct prompt numbers.

## Telemetry and compaction

`get_state` verifies provider/model/effort, session ID, 500000 contextWindow and enabled
compaction before dispatch. The trusted **toy-only** `.pi/settings.json` sets ordinary and
exact-model override `reserveTokens=16384`. Pi 0.87.1 installed source confirms:

- `core/settings-manager.js`, `getCompactionTokenSetting`: model override, then ordinary
  setting, then default; `getCompactionSettings` includes enabled/reserve/keepRecent.
- `core/compaction/compaction.js`, `shouldCompact`: enabled and
  `contextTokens > contextWindow - reserveTokens`.

Thus the effective threshold in this fixture is **483616**, not the advertised 500000.
This is source+controlled-settings provenance, **not an RPC threshold field**. Production
must resolve effective settings per model/version; missing reliable inputs mean fresh/block.
`get_session_stats.contextUsage.tokens` estimates current occupancy; `tokens` counters are
session-cumulative. Deltas are computed only within identical before/after session identity;
cache zeroes are measured zeroes, synthetic counters are null. The fixture admission test
selects a reused/new synthetic session ID at 150000/149999 free tokens respectively.

Reuse is an admission rule, not a guarantee that a long task will not compact. Safe policy
for future real mid-task pressure: stop dispatch, abort/drain the worker, inspect partial
files and durable identity, then explicitly reconcile/block before any fresh writer. This
PoC does not implement a pressure monitor, independent substantive final review, complete
approval/permission enforcement, durable live-process registry, or a production task contract.
They are outside demonstrations 1–8; this is not migration implementation/planning.

## Evidence

`logs/suite.log`: five executed tests after the parent settlement correction, two real task
status reads, safe telemetry records including observed settled lifecycle for each prompt.
`logs/protocol-settlement.json`: explicitly synthetic lifecycle/race regression evidence.
`logs/crash-recheck.log`: historical pre-settlement-correction focused receipt/parent-SHA/path
rerun; the current full suite also reruns these strengthened crash assertions.
`logs/*state.json`: small checkpoint-derived final snapshots; no SQLite binary or toy `.git`.
`logs/real-metrics.jsonl`: sanitized real before/after records, deltas and provenance.
`logs/cutoff.json`: explicitly synthetic admission/session fixture.
`logs/skill-observed.json`: actual assistant marker responses, not just submitted prompt text.
`logs/corrections.json`: first-draft correction history; no unexplained relaunch.
`remote-signals.json`: dated official GitHub/PyPI responses, not user/install counts.
`environment.json`: actual worker session identity and runtime versions.
