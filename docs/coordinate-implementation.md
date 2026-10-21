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

Before any selected agent-provider call, provide explicit paid authority as a top-level task-contract
field, for example:

```json
{"paid_scope":{"approved":true,"agent_providers":["openai-codex"],"apis":["selected application/test API"]},"tasks":[{"id":"fix-title","description":"Correct the page title."}]}
```

The provider list must exactly name the selected worker and reviewer providers. If this dedicated scope is
absent or does not match, the CLI asks once through the current terminal or attached parent bridge before
storage or provider launch, naming the selected providers and declared application/test APIs (`paid_apis`,
or `none declared`). A denied or unavailable answer launches no provider. Credentials, ordinary task text
and historical runs are not approval. The unchanged grant and exclusions are included in worker, fixing-worker
and read-only reviewer prompts; altered scope requires a new answer.

Optional `checks` accepts shell command strings, argv lists or objects with `command`/`argv`.
A singular `check` or `required[].check` uses the same command format. Old registered catalogue
IDs are no longer executable: supply the actual project command when requesting that check.
Commands run normally with no workflow deadline or output cap. A nonzero required command is retained with its exact command, exit and output as a failed attempt, then returned to the same-task worker for a reasoned safe scoped source/setup correction. The runner reruns the affected required command and only checkpoints after real passes; an unavailable safe correction or material decision reports its actual blocker. This is neither a skipped check nor cross-task reuse/post-review fixing, and it never spins an unchanged failed command. No universal test collection count, byte pin or evidence applicability receipt.
Optional `gates` contains question strings or objects with `question`/`description`; current owner
approval is needed before that task's worker starts. Other optional context is passed to the worker.
Optional `owned_paths` limits source file/directory scope. Explicit SDK edit/write selections identify
source checkpoint paths; the runner never derives ownership by scanning a clean baseline. Optional
`generated_outputs` names expected task artifacts for selective regeneration/cleanup guidance, not a
registration, allowlist, permission prerequisite, or automatic commit target.

## Real execution and safety

An exclusive Git-worktree writer lock prevents overlapping cooperating runners. The SDK host
inherits that lock while active. A CLI entry waits transparently for that existing lock and may be
cancelled while waiting without creating a failed task/run or replacing its live writer; a platform
that cannot wait returns concrete busy. This is lock entry only, not a queue, watchdog, polling
service, or cancellation-drain claim. At an actual SDK edit/write, the runner protects unsafe/symlink,
out-of-scope, and already-modified target paths. Commands remain ordinary SDK tools, not an
adversarial sandbox: new, modified, deleted, ignored, Git-visible, or undeclared output never
stops a later command or check. The runner stages only explicitly selected source/deliverable
paths; it does not inventory, adopt, or clean arbitrary output.

Each task runs in a fresh coding conversation. Ordinary scoped technical fixes, isolated tests/servers,
necessary local/in-project dependency setup, and current-task artifact lifecycle need no owner question;
this authority is not proof that checks passed. Product decisions, substantial complexity increases,
separately scoped paid usage, and actions outside authority still ask. No global install, credential change,
deployment, push, or unrelated-work deletion is implied. It runs requested project checks and yields a real
focused commit before dependents. Normal Git configuration, hooks and signing are honored. A correctable whitespace, source, hook, or Git checkpoint failure returns to the same task worker with its actual error; affected required checks rerun before the normal checkpoint retry. A reported-failed/interrupted commit is reconciled from that operation's selected paths, attempted parent, and actual result before any retry, retaining a matching SHA without recommit. Failures retain
partial work and report the actual operation error. No empty commit for no-change work. No intent settlement
or operation trailers, hook/filter admission, hidden repair quotas, arbitrary timers or process receipts.

The final reviewer is a fresh, read-only SDK session, not the worker context. It receives the
actual full committed range, tasks, and the same routine-authority defaults/exclusions, with only
read/search tools for source continuation. Authority does not prove checks or acceptance. Findings stop acceptance and are reported honestly with commits retained. An actionable first
rejection may use the separately bounded one-round fixer: it receives the original task contracts,
configured executor/authority, explicit source/artifact scope and the actual findings; its checks
and focused checkpoint retain a distinct execution identity and explicit predecessor. Correctable
check/checkpoint errors stay inside that assigned round and rerun affected checks before its
checkpoint. This primitive neither routes work nor starts a recursive CLI/review loop; final
chain control remains bounded to two reviews and one fixer. SDK compaction/retries follow SDK behavior; compaction/optional telemetry never creates a
workflow fatal condition. SDK tools truncate long output with their normal continuation
instructions; the transport has no size cap. A runner may reuse only a returned private saved session identity from the same run after a
successful idle settlement and preceding verified checkpoint. Reuse also requires an explicit
nonempty matching `context_group` and unchanged role, worktree, executor, resources,
instructions, settings and authority; task text or callback identity alone are not mismatches.
`fresh_only` and every reviewer select fresh. Candidates sort by latest successful settlement then
stable ID. Reuse needs measured effective headroom (context window minus effective reserve minus
occupancy) at least `min_free_tokens_before_compaction`, whose configurable default is 150000.
Unknown, invalid, disabled or inapplicable compaction/headroom facts select fresh rather than
inventing capacity or blocking safe fresh execution. There is no age expiry or file-change routing
rule. Each reopen rebuilds the current task's callbacks, tools and mutation scope. An adapter that understands the
standalone pre-invocation `session` transport record explicitly requests it with
`sessionObservations: true`; absent opt-in keeps the legacy record kinds. The host returns fresh
boundary observations and waits for SDK idle before disposal. Missing optional observations select a fresh
session at the routing layer; they do not stop ordinary SDK/tool correction. The engine keeps a
small private same-run candidate registry and records each selection/rejection reason in private
operation history. It promotes a saved identity only after that task is idle, all required checks
actually pass, and its focused checkpoint succeeds; same-task corrective prompts keep their live
context, while failed or unsettled sessions never route another task.

Material questions, including missing paid scope before provider launch, use actual current terminal input.
Without an interactive terminal the run stops with the question and does not fabricate an answer. A loaded project
parent-session bridge may instead launch this same command with its private socket environment;
it wakes that parent with the exact pending question (including the paid-scope decision when needed) and returns only its correlated reply to the
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

`status` and `history` are read-only SQLite readers. New runs privately retain their original parsed contract/order, selected executor, settled authority and resolved initial review base before dependent mutation. Append-only operation history preserves actual invocation, check and checkpoint outcomes; a corrected check does not replace its failed command/exit/output, and checkpoint facts retain only task-local paths/artifacts and available SHA/parent. CLI output is a safe projection (task IDs, review base and operation facts), never original task text, prompts, answers or check output. This is not a resume policy or a filesystem/Git snapshot.

Ordinary task/run progress is useful history, not dispatch or completion proof. Optional usage reporting records one interval per worker/reviewer occurrence and one membership per dispatched `(run_id, task_id)`, not prompts, retries, or review references. Status exposes separate worker and reviewer totals when available; missing legacy/optional data remains partial or unknown, never zero or an invoice claim. Interval storage failures are reported as coverage gaps and do not replace task, check, Git, provider, or required-history outcomes. Required original-input, operation-history, progress, and review/fixer dispatch writes are made before their dependent mutation. Review-chain history retains actual execution IDs, attempts/outcomes/uncertainty, consumed review ordinal/fixing round, explicit causal IDs, private parsed findings and commit/range references. It preserves an initial rejection and completed task checkpoint identity across reopen; an uncertain invocation is never a success or replay permission. Status safely exposes actionable findings and references, not raw reviewer JSON, prompts, or answers. Optional monitor observations remain non-authoritative gaps.  If one reports a SQLite failure, the runner re-reads that specific operation: a known completed write is retained without replay, otherwise it makes one safe local correction; an unreadable or unrecoverable result stops only that affected action with its actual persistence limit. It never reruns task tools or commits to repair progress or invents missing history. Optional monitoring, metrics, and telemetry persistence remains a reported gap and does not block task/check/Git/provider work. Old tables/rows remain in place, including incomplete intents; new tasks neither reconcile nor replay them. Malformed optional history cannot veto new coding.
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
