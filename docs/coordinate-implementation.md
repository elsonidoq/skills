# Coordinate Implementation operating guide

The existing entry runs ordinary requested tasks using Pi SDK tools. This operative contract
supersedes old graph/host/custody/session/evidence eligibility rules. Historical plans, schemas,
approvals and database rows are not rewritten or replayed.

## Run a minimal task

With the runtime dependencies already installed, create these ordinary inputs outside the
project's task-owned files:

```json
[{"id":"fix-title","description":"Correct the page title; run the existing relevant project test."}]
```

Executor JSON uses the actual owner selection, for example:

```json
{"provider":"openai-codex","model":"gpt-6.1-sol","effort":"medium"}
```

An optional `reviewer` object selects the fresh read-only review executor separately:

```json
{"provider":"openai-codex","model":"gpt-5.6-terra","effort":"medium","reviewer":{"provider":"openai-codex","model":"gpt-6.1-sol","effort":"medium"}}
```

Without `reviewer`, review retains the selected worker profile for compatibility.
An explicitly malformed reviewer profile fails with a corrective diagnostic, never a
silent fallback. These are selections, not proof of provider availability or actual usage.
For **this repository**, every launch (including continuations/corrections) supplies
`--executor .pi/workflow-executor.json`, or that file's absolute path through the parent
bridge: Terra/medium workers and Sol 6.1/medium reviewers. Other projects retain their own
configuration. Existing historical reviewer nodes are not changed retroactively.

```sh
scripts/coordinate-implementation intake --tasks /tmp/tasks.json
scripts/coordinate-implementation start --project /absolute/project \
  --tasks /tmp/tasks.json --executor /tmp/executor.json --run fix-title
scripts/coordinate-implementation status --project /absolute/project --run fix-title
# status/history include monitoring recording version, stable occurrence IDs, and safe review ranges when available
```

Set `COHERENCE_PYTHON` only if the dependencies are in a selected environment. Source execution
uses the suite-relative SDK host; installed execution uses its packaged host. `COHERENCE_NODE`
can select an existing Node executable. Optional `COHERENCE_AUTH_PATH` and
`COHERENCE_CATALOG_PATH` select existing SDK credential/model storage; do not print or copy secrets.
No automatic installation, credential refresh, global reconfiguration or model substitution.

## Only six task-linter checks

1. File exists and is readable.
2. JSON/YAML parses into a list, or an object containing `tasks` list.
3. Every task has an ID and work description (`description` or `outcome`).
4. IDs are unique.
5. Declared `depends` references exist.
6. Dependencies have no cycle.

Dependencies determine sequential order; forward references are valid. Empty work reports
`no tasks` before storage, locks or SDK launch. No mandatory check, path list, approval envelope,
manifest, catalogue, graph, original session, cgroup or provenance record.

Optional `checks` accepts shell command strings, argv lists or objects with `command`/`argv`.
A singular `check` or `required[].check` uses the same command format. Old registered catalogue
IDs are no longer executable: supply the actual project command when requesting that check.
Commands run normally with no workflow deadline or output cap; nonzero is failure, not success.
No universal test collection count, byte pin or evidence applicability receipt.
Optional `gates` contains question strings or objects with `question`/`description`; current owner
approval is needed before that task's worker starts. Other optional context is passed to the worker.
Optional `owned_paths` limits file/directory scope. Tasks without it derive ownership from actual
edits against the task's clean baseline, excluding all pre-existing dirty work.

## Real execution and safety

An exclusive Git-worktree writer lock prevents overlapping cooperating runners. The SDK host
inherits that lock while active. The runner inspects HEAD/index and pre-existing dirty files
before work. SDK edit/write calls reject dirty, unsafe/symlink and out-of-scope paths before
mutation. Commands remain ordinary SDK tools, not an adversarial sandbox: workers are instructed
to preserve unrelated work and not stage/commit. The runner refuses changed HEAD/index or
modified pre-existing work, and inspects actual edits before staging only explicit owned paths.
Ignored/nested data is not recursively inventoried, adopted or cleaned.

Each task runs in a fresh coding conversation, fixes ordinary no-effect tool errors in that
conversation, runs requested project checks, and yields a real focused commit before dependents.
Normal Git configuration, hooks and signing are honored. Failures retain partial work and report
the actual operation error. No empty commit for no-change work. No intent settlement or operation
trailers, hook/filter admission, hidden repair quotas, arbitrary timers or process receipts.

The final reviewer is a fresh, read-only SDK session, not the worker context. It receives the
actual full committed range and tasks, with read/search tools for source continuation. Findings
stop acceptance and are reported honestly with commits retained; there is no SQL disposition
prerequisite or automatic expensive repair/retry loop. Address actual findings within requested
scope, rerun affected checks, and obtain independent review. SDK compaction/retries follow SDK
behavior; compaction/optional telemetry never creates a workflow fatal condition. SDK tools
truncate long output with their normal continuation instructions; the transport has no size cap.

Material questions use actual current terminal input. Without an interactive terminal the run
stops with the question, preserves partial work and does not fabricate an answer. A loaded project
parent-session bridge may instead launch this same command with its private socket environment;
it wakes that parent with the exact pending question and returns only its correlated reply to the
waiting worker. Before attached execution, the runner checks the existing socket's authenticated
readiness response and active parent reply tool; incomplete/mismatched configuration stops before
storage or SDK launch, without terminal fallback. Each worker's actual SDK tool set must contain
`ask_owner` before its prompt starts. This proves current readiness, not future delivery; later
connection failures retain partial work and report the error. No model probe or heartbeat is used.
It retains neither questions nor answers in SQLite. Parent-session shutdown or the
launch tool's cancellation signal terminates only its owned runner through that runner's normal
SIGTERM path and waits for it before bridge cleanup. The bridge is optional: direct terminal
invocation remains unchanged. The project entry is
`.pi/extensions/coordinate-implementation-bridge.js`; Pi auto-discovers `.js`/`.ts`, not `.mjs`.
Noninteractive Pi (including RPC) skips project extensions without project trust. Use explicit
one-run `pi --approve` or an owner-approved saved decision for the exact checkout; never change
global trust defaults or trust parent directories just to load this bridge. A prompt cannot load
tools that startup skipped. In Paseo, use a fresh session and verify both
`coordinate_implementation_start` and `coordinate_implementation_reply` are available before launch;
do not reload or restart the current session automatically. After merging, start in the main
checkout and verify its own trust decision and tool availability: trust is path-specific, not
branch-specific. The bridge resolves the script from that session's checkout, not an old worktree.
Runner diagnostics go to stderr so they cannot corrupt the parent's RPC stdout. There is no Paseo
version/transcript/binding/receipt gate. No automatic resume/control mailbox or daemon.
Cancellation aborts the owned SDK session and waits for its host; it never signals parent/sibling
processes or provisions/signals cgroups.

## History and explicit abandon

`status` and `history` are read-only SQLite readers. Ordinary task/run progress is useful history,
not dispatch or completion proof. Old tables/rows remain in place, including incomplete intents;
new tasks neither reconcile nor replay them. Malformed optional history cannot veto new coding.
There is no automatic schema migration, drop, mass conversion or invented successful effect.

After inspecting actual writers and partial work, an operator may explicitly abandon an old run:

```sh
scripts/coordinate-implementation abandon --project /absolute/project --run OLD_RUN
```

This acquires the writer lock, checks current recorded controller/child identities and recorded
scope membership without signalling anything, labels only the run abandoned and releases its old
reservation. It never completes old effects. New failed runs can also be labelled abandoned.
A stale reservation alone is not a live writer. Do not infer safe ownership from SQL, a stale PID
or an old empty-scope observation. A live overlapping writer must not be killed or overwritten.
Inspect/reconcile actual commits before starting fresh work; never blindly replay uncertain
external operations or a possibly completed Git commit. Start a fresh run ID, not the old attempt.

## Setup and verification

Python >=3.10 with PyYAML, local Git/SQLite, and a usable Node/Pi SDK installation are actual
runtime dependencies. SDK 0.87.1 is tested; the dependency lock is install metadata, not exact
SDK/Node equality admission. No LangGraph, cgroup delegation, custom SDK tools or host manifests.
Explicit optional setup remains `scripts/install-workflow.sh --prefix NEW_DIRECTORY --allow-network`
only with separate install/network authority. Ordinary entry never calls it.

Focused checks in the prepared environment:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=runtime:runtime/tests \
  .pi/workflow-validation/venv/bin/python -B -m unittest discover -v -s runtime/tests
node --test runtime/tests/test_host.mjs
```

These exercise real disposable Git/project/tool operations and clearly labelled offline SDK
transport/compaction fixtures; they do not manufacture live-provider success. Independent final
review remains separate from writer validation. An optional task input `review_base` must resolve to a
Git commit that is an ancestor of the run baseline; it changes that review's actual diff/prompt and every
recorded review outcome to base→current-head. Invalid or unrelated bases fail only the affected review.
A malformed, failed, or interrupted reviewer records that actual selected range before its original error
propagates. Without it, the default
run-baseline→head range is unchanged. After adopting changed global skills, run `/reload`.
