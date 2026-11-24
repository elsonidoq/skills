# Coordinate Implementation operating guide

The existing entry uses one LangGraph controller for tasks (sequential by default), checks, focused Git
checkpoints, independent review, scoped repair and durable question resume. Pi SDK tools perform
worker operations. Standard file-backed SQLite checkpoints hold graph control state; private operation
history and actual Git/SDK observations reconcile effects, not automatic acceptance. Explicitly directed
path-disjoint worker waves use standard LangGraph fanout and keyed reduction. Historical non-graph runs remain readable and use an explicitly selected
compatible runtime for inspected continuation, never silent conversion or replay. The six task-linter checks remain the entire startup linter; no extra
graph/host/custody/session/evidence admission rules. Historical approvals and rows are not rewritten.

## Optional delivery scope transport

`start --delivery-scope 'JSON'` accepts an optional launch-only carrier. The attached
`coordinate_implementation_start` tool accepts the same JSON object as `delivery_scope`.
It transports **already granted** scope; supplying it does not create approval. Example
shape (replace with the actual run, target and approval reference, not these examples):

```json
{
  "target": "https://github.com/OWNER/REPO/issues/45",
  "authority": {
    "run_id": "EXACT-RUN-ID",
    "target": "https://github.com/OWNER/REPO/issues/45",
    "operations": ["trace_comment"],
    "approval_ref": "actual owner approval reference"
  },
  "known_linked_prs": []
}
```

Use `--run EXACT-RUN-ID` at start to bind the supplied grant. Supported carrier fields
are `target`, `authority` and optional `known_linked_prs` (qualified PR URL strings).
The authority fields are `run_id`, `target`, `operations` (operation name strings) and
`approval_ref`. `trace_comment` permits only the publisher's factual trace operation;
`link_comment` remains a separate operation, not implied by trace permission. An omitted
`target` defaults to the retained delivery issue at publication; the authority must still
match that exact destination. A PR destination must be an explicitly known linked PR.
Never include credentials, bridge tokens, environment dumps or paid API approval here.

The carrier is saved unchanged in private run authority. Resume takes no new carrier
and restores the original one, like the original executor and parallel direction. Old
inputs, bare lists and tasks without an issue or delivery metadata remain valid. Missing
or drifted authority defers only publication with a concrete correction at the publisher
boundary; issue context, credentials and task fields are not grants. It does not change
routine worker permissions or paid/manual gates. `Engine.publish_delivery_trace()`
forwards the retained carrier unchanged to the existing publisher. Normal run finish
now invokes that boundary automatically as described below.

Changed installed bridge code requires a fresh Paseo session before use. The fresh agent
must verify checkout, revision, current approval and loaded bridge capabilities. Do not
reload or restart the current session automatically.

## Terminal factual trace delivery

Normal start/resume/recovery execution drains the parent bridge before the factual
snapshot, publication and local tracing teardown, even with no pending worker question.
Parent batches are persisted in the existing SQLite history before acknowledgement.
Normal attached questions also bind this observer automatically; the owner tool's actual
answer remains distinct from the coordinator's resolution. No extra agent, manual log or
provider replay is used.

A returned run result keeps its implementation `status` and adds `trace`:

- `capture`: partial/unavailable coverage, parent acknowledgement and known gaps. An
  acknowledged drain does not establish complete conversation coverage.
- `publication`: `confirmed`, `partial`, `deferred`, `failed` or `uncertain`, snapshot
  identity, confirmed part URLs and a concrete correction when needed. Confirmed
  publication can contain partial-coverage facts; it is not owner acceptance.
- `linkage`: when publication is confirmed, the separate reciprocal-link result.
  Missing/unconfirmed PR links are `incomplete`, not complete delivery. Existing links
  are independently verified; missing links require `link_comment` scope for each target.
  The launch carrier's single authority never grants writes to another target. Use the
  existing explicit finish/linkage operation with actual per-target grants for missing
  PR-side links; do not republish the trace merely to add a late PR.

On an exception or cancellation, practical failure facts and capture gaps are published
where possible; the original exception is re-raised unchanged. A separate
`coherence trace finish: {…}` record on stderr reports capture/publication outcomes.
Optional storage, callback or export failure cannot change implementation success or
mask its original failure. Waiting runs drain without finalizing parent capture or
publishing a terminal snapshot; resume remains required, not fabricated completion.

Missing target or authority defers writes only. Correct the reported target/access/scope
problem and inspect retained publication intent and remote effects before publication
recovery; never blindly resend an uncertain comment. Keep the SQLite run, snapshot and
part intents until full GitHub bodies and required links are independently confirmed.
There is no automatic database deletion, fallback issue or continuous publication.
Abrupt death can prevent drain/finish entirely and lose unpersisted parent facts; retained
facts may support later explicit publication recovery, never invented missing events.

Offline production-seam tests cover drain/persist/ack, projection and subprocess
publication, not genuine live model/owner behavior. Live acceptance additionally needs
an observed representative run and checkout-independent full-body readback, with named
issue/known-PR authority. Issue-only permission leaves PR-dependent proof unmet.
Changed global bridge/tools or skills require a fresh-session handoff before reliance:
verify checkout, exact revision, current approval and loaded capabilities in the fresh
session. Do not auto reload/restart, synthesize owner events or rerun coding to create
missing trace evidence. Phoenix remains a separate metadata-only opt-in exporter.

## Owner-selected durable assessment

On an explicit owner-selected qualified issue or PR URL, use
[Assess Skill Improvements](../skills/assess-skill-improvements/SKILL.md), not an automatic
post-run investigation. From either entry, verify the reciprocal delivery association and
read every relevant conversation/review page and trace continuation part on both sides.
Inspect accessible approved source, code at cited revisions and supported later commits/PR
fixes. No original execution checkout identity/path, SQLite or session is required.
Missing/inaccessible parts, links or code make affected conclusions partial; they do not
show zero failures. Publication recovery is needed only when selected evidence requires it
and remains a separately authorized operation, not coding replay.

Cite original intent and observed facts; separate reusable planning/skill/tool/worker
weaknesses from user/issue-specific omissions, and supported causes from hypotheses.
Attribution needs supported links and content, not author, time or a blind commit range.
Propose small changes to existing owners only. Assessment is read-only by default: no
edits, agents, PR creation, tracker transitions or implementation. Optional assessment
label/comment writes require their own target/operation scope and independent readback;
trace-comment permission alone does not grant assessment writes.

For changed skills in Paseo, prepare a fresh-session handoff with the selected URL,
current authority, known evidence gaps and pending live criteria. The fresh agent verifies
checkout, exact revision and the loaded updated assessment skill before reliance; do not
automatically reload/restart. This activation checkout is not a dependency on the old
execution worktree. Offline `python3 scripts/test-assess-skill-improvements.py` checks
actual carrier obligations and controlled evidence from both entries, including unavailable
parts/links/code and supported versus unrelated fixes. It is not model-obedience proof.
Actual explicitly selected issue AND PR assessments from GitHub without the execution
checkout remain required live proof; fixture results or issue-only reads cannot pass both.

## Publication-only recovery

From a terminal, or an attached agent's normal shell, use the same command:

```sh
scripts/coordinate-implementation recover-publication \
  --project /absolute/project --run EXACT-RUN-ID
```

Options: `--snapshot EXACT-SNAPSHOT-ID` selects a retained prepared snapshot. Without
it, recovery selects the latest prepared snapshot; only if none exists does it project
retained facts. It never invents missing parent events. `--delivery-scope 'JSON'` accepts
the same already-granted carrier described above when no launch carrier was retained;
if a launch carrier exists, any supplied carrier must match it unchanged. Neither
option grants permission. Restore missing storage/facts or obtain actual matching
run/target/operation scope as directed by the diagnostic; do not replay coding to
recover a log.

The publisher automatically recognizes the specific HTTP 422 `IssueComment` /
`unprocessable` / `data` validation, `Body is too long (maximum is N characters)`.
It completes a paginated exact-marker/full-body reconciliation before splitting a
rejected payload into lossless continuations. Each continuation includes its wire
prefix and gets independent full-body readback. No manual `LengthProof` is needed
for this response. Other validation, access, rate or malformed responses do not
trigger splitting. A retained recognized rejection is reconciled before splitting
on recovery, without resending the known rejected body; old status-only records
still use the existing complete-scan-before-targeted-attempt path.

Consumer evidence: the parent observed `maximum is 65536 characters` from the
[GitHub create-issue-comment endpoint](https://docs.github.com/rest/issues/comments#create-an-issue-comment)
for [issue #45](https://github.com/elsonidoq/skills/issues/45), run
`issue-45-final-code-sol-20261117`, prepared snapshot
`74c229ae20013724a2d8d85d8708aebedf2eebefce86127630bc20e7ef2d0d9a`.
The parent retained the raw validation response and confirmed zero created comments
by complete pagination. This is observed endpoint evidence, not an OpenAPI limit
claim or successful delivery. The publisher uses progressive splitting, not a
hard-coded character budget, truncation or a new limit registry. If even a minimal
continuation fails, it reports the safe length diagnostic and asks for correction
of endpoint/envelope validation, rather than repeating the same send.

Recovery uses the existing publisher and linkage helper under the ordinary writer lock.
It independently reads confirmed parts, completely scans uncertain destinations before
any missing write, preserves exact part bodies and supported links, and does not resend
confirmed content on repeated calls. Incomplete scans or ambiguous effects stop writes
with a correction. Missing PR-side link grants remain separate incomplete linkage.
There is no attached recovery tool or bridge route. No graph, worker, reviewer, project
check, Git commit or provider is called; read-only Git identity checks support the lock.

JSON reports `implementation.state` from retained storage with `replayed: false`,
separately from `publication` and, once confirmed, `linkage`. Recovery does not update
implementation outcome or establish owner acceptance. Exit 0 means publication and
linkage are confirmed; exit 2 reports deferred/uncertain/failed/incomplete delivery,
not failed implementation. Retain storage until independent full-body readback confirms
all effects. Live recovery proof requires the actual retained representative run and
its unchanged factual/link publication permission; offline fixtures are not live proof.

## Local Phoenix configuration

Local monitoring is opt-in. Add the following object to the task input's top level;
leave it out to disable local monitoring. A bare task list remains valid.

```json
{"local_monitoring":{"enabled":true,"endpoint":"http://127.0.0.1:6006/v1/traces"},"tasks":[]}
```

Only that exact endpoint is permitted. Other destinations disable export with a safe
configuration diagnostic; they do not stop the workflow. Ambient OTLP and LangSmith settings,
proxies, cookies and credentials are not used for monitoring. Pi/provider traffic is separate.
The isolated tracing provider sends only opaque run/task/invocation identities, fixed boundary
names, role/model, safe outcome, timing and known invocation-local usage/cost. Unknown usage is
omitted. It does not send prompts, responses, tool data, paths or errors. Completed boundary
spans export while the run is open; this does not prove when the UI displays them.

To inspect an unfinished run in Phoenix, open the project's **Spans** view and clear the
`parent_id is None` root-only filter. Open a completed invocation to inspect its task/trace
hierarchy. The root span arrives only when it ends. Reload and reopen the selected trace when
needed; automatic selected-trace updates and active-root timers are not promised. Project
navigation can restore the root-only filter. If usage/cost attributes are absent, Phoenix's
zero aggregates are not measured zero use or spend: those values remain unknown.

If Phoenix requires authorization, put the complete local `Authorization` header value in a
private file owned by the project maintainer, and explicitly set
`COHERENCE_PHOENIX_AUTHORIZATION_FILE` to its path in the runner environment. Do not put the
credential in the task input, this example, Git, a registry or logs. An unreadable or invalid
credential file disables export with a safe diagnostic, not the workflow. Keep its recovery
method with the private project operations information. Export and serialization failures are
reported as safe visibility gaps; checks and Git still run.

Before any real metadata export, run the final-wire privacy test for the same adapter and
installed dependencies:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=runtime python3 -m unittest discover -s runtime/tests -p 'test_tracing.py'
```

A pass is local intercepted/configuration proof only, not evidence of a running service,
server/browser network behavior or incremental UI visibility.

Use the official image `arizephoenix/phoenix:version-21.0.0@sha256:1f9a144a5357b4973e93a15718f050247cb7a4ee7b7c6c06ecb91b5eed3fbaad`.
Use SQLite in `/data`, the three settings in `runtime/phoenix.env.example`, and publish
only `127.0.0.1:6006:6006`. Do not use host networking, publish other ports, pass the
host environment, or configure external providers. Keep the image's authentication
default. Use only private local Phoenix credentials; never commit or log credentials.

The project maintainer owns the private persistent directory
`${XDG_DATA_HOME:-$HOME/.local/share}/coherence/PROJECT_KEY/phoenix`, with a stable
project key independent of disposable worktrees. Record its selected absolute path,
image pin, credential recovery method and restart command in project operating guidance
outside a disposable worktree. Recover using the same owned SQLite directory and private
credentials, not an empty replacement. Before setup, verify directory ownership and image-user
write access; do not adopt ambiguous data or change broad permissions. If the port, container
or data directory belongs to another service or has uncertain ownership, stop that setup and
resolve the collision without stopping or overwriting it. After those checks and the same-adapter
privacy proof, the maintainer can start the single container with the selected owned directory:

```sh
docker run --name coherence-phoenix --env-file runtime/phoenix.env.example \
  --mount "type=bind,src=$PHOENIX_DATA,dst=/data" -p 127.0.0.1:6006:6006 \
  arizephoenix/phoenix:version-21.0.0@sha256:1f9a144a5357b4973e93a15718f050247cb7a4ee7b7c6c06ecb91b5eed3fbaad
```

Set `PHOENIX_DATA` to the verified absolute directory first. Reuse the same directory and
credentials on an ordinary restart; do not create an empty replacement or stop an unrelated
container. No setup or service launch is done here. Verify the image's effective settings and
server/browser network behavior, and observe useful incremental UI progress before removing
the existing monitor.

## Legacy run retention and compatible continuation

Retain the pre-cutover suite revision `4c1725ebded2f89dec6933b8d193bf34997c62ce` and a
compatible Python/SDK environment for historical execution runs. Status and history remain
read-only in the current CLI. For an inspected legacy continuation, use an operator-selected
checkout of that revision and its compatible environment; run its original action with the
original arguments, for example:

```sh
LEGACY_SUITE/scripts/coordinate-implementation resume --project /absolute/project --run RUN
```

Substitute the actual action and arguments when appropriate. Do not feed graph runs to the
legacy engine, convert historical rows, replay uncertain effects, or automatically check out,
install, restart, or authenticate the old runtime. For rollback, retain both runtime revisions,
the original workflow database and the separate graph checkpoint database; select the runtime
that created the run. A rollback does not make graph runs compatible with the old controller.
Inspect saved calls and Git effects before any continuation.

The public CLI uses `run_graph`; `Engine.invoke` is only a compatibility facade to that same
controller, not a second lifecycle. New input authority contains `backend: langgraph-v1`. Mutation
of an unmarked legacy run stops before writer entry or provider/parent contact and prints the
compatible command with its original arguments. Status/history do not require the graph backend.

The graph exposes `graph_recovery_action` for inspected `continue`, `fresh` and
`escalate` actions, exact owner-authorized external transfer,
and stale review target refresh. It uses the retained thread, input, session and task ownership;
reconciles completed effects before continuation; and stops on unknown or live effects. A failed
implementation escalation stops and requires owner direction. The existing public commands route
these actions through the same retained graph. Ordinary resume does not authorize replay of a failed
worker. Supply the inspected action and substantive diagnosis with `--recovery-action` and
`--diagnosis`. Uncertain provider/Git effects still stop for reconciliation.

A settled worker question returns `status: waiting`, preserves its saved context and releases the
writer lock. `status` exposes only task/question identities and the resume action, not the private
question or answer. Reopen with `resume` on a terminal or attached parent to deliver the actual
reply to that precise saved invocation before the worker continues.

Local reproduction (fixture providers, not live model judgment):

```sh
umask 022
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=runtime:runtime/tests python3 -m unittest -v \
  test_cli.CliTests.test_public_cli_framed_adapter_terminal_reply_and_real_git \
  test_cli.CliTests.test_public_cli_uncertain_provider_and_git_stop_without_replay \
  test_database_compatibility.DatabaseCompatibilityTests.test_explicit_retained_revision_can_read_and_abandon_legacy_fixture
```

The first test prints actual CLI/terminal and Git output for dependency checkpoints, saved pause,
process reopen, terminal answer consumption and fresh read-only review. It injects only a local
framed provider host; the CLI, adapter transport, saver, checks and Git are real. The second injects
provider/Git uncertainty and verifies no replay. The third extracts the retained source into an isolated
fixture and exercises its CLI with the current Python environment, without conversion or installation.
These tests use temporary projects: output preserves observed Git facts, not a retained application
repository or live-model verdict. Capture this output through the existing issue #44 evidence route
and associate it with the exact tested application/review revisions; a test pass alone is not durable
functional-evidence delivery.

The approved [CLI/Pi interface target](../specs/006-issue-linked-delivery/contracts/interfaces.md#cli-and-attached-parent)
retains existing actions and adds directed parallel execution and durable targeted question resumption.
Mechanisms may vary within the approved design boundary; actual effect validation and inspected recovery remain.

## Run a minimal task

With the runtime dependencies already installed, create these ordinary inputs outside the
project's task-owned files:

```json
[{"id":"fix-title","description":"Correct the page title; run the existing relevant project test."}]
```

Executor JSON uses the actual owner selection and a required `reviewer` object for the fresh
read-only review executor, for example:

```json
{"provider":"openai-codex","model":"gpt-6.1-sol","effort":"medium","reviewer":{"provider":"openai-codex","model":"gpt-6.1-sol","effort":"medium"}}
```

A missing or malformed reviewer profile fails with a corrective diagnostic, never a
silent fallback. These are selections, not proof of provider availability or actual usage.
An optional `implementation_fallback` object uses the same provider/model/effort fields and
explicitly permits a stronger implementation worker during inspected recovery. A reviewer profile
alone grants no implementation fallback. Availability errors remain actual errors; do not install,
authenticate or silently substitute another model.

The host loads no ambient Pi extension. A provider that an extension registers, such as
`claude-bridge` from `pi-claude-bridge`, needs an optional `extensions` list of extension paths
in each profile that uses it (worker, `implementation_fallback`, `reviewer`). Relative paths
resolve from the project root. The host loads only those paths, registers their providers, and
keeps the same explicit worker/reviewer tool list; extension tools stay inactive. For example:

```json
{"provider":"claude-bridge","model":"claude-sonnet-5","effort":"medium",
 "extensions":["/home/USER/.pi/agent/npm/node_modules/pi-claude-bridge/src/index.ts"],
 "reviewer":{"provider":"claude-bridge","model":"claude-sonnet-5","effort":"medium",
  "extensions":["/home/USER/.pi/agent/npm/node_modules/pi-claude-bridge/src/index.ts"]}}
```

A path that does not load stops the session with the path and the load error.

Workers and fixers must create and change files with the `edit`/`write` tools: the focused
checkpoint includes only files changed through them, never files written by `bash`. Their
briefs state this rule. Repairs that never reach approval stop at the graph step limit with a
`Blocked` diagnosis and a `failed` run; inspect `history`, correct the cause, then abandon the
run and start a new one.
For **this repository**, every launch (including continuations/corrections) supplies
`--executor .pi/workflow-executor.json`, or that file's absolute path through the parent
bridge: Sol 6.1/medium workers, implementation fallback and reviewers. Other projects retain their own
configuration. Existing historical reviewer nodes are not changed retroactively.

The canonical project-local configuration is `<project-root>/.pi/workflow-executor.json`.
Resolve it once from the suite checkout, then pass the exact absolute path downstream:

```sh
executor=$(python3 scripts/resolve-workflow-executor.py --project /absolute/project) || exit
# Explicit override: add --executor config/custom.json (relative to the project, not cwd),
# or --executor /absolute/selected.json. See --help.
scripts/coordinate-implementation intake --tasks /tmp/tasks.json
scripts/coordinate-implementation start --project /absolute/project \
  --tasks /tmp/tasks.json --executor "$executor" --run fix-title
scripts/coordinate-implementation status --project /absolute/project --run fix-title
scripts/coordinate-implementation resume --project /absolute/project --run FAILED_OR_INTERRUPTED_RUN
# status/history include monitoring recording version, stable occurrence IDs, and safe review ranges when available
```

If an unreserved pair grant was stopped by target drift, do not rebind it. Refresh the independent review of the current committed target over the retained original range first; a rejected refresh leaves the run stopped for normal explicit resume and a new exact pair, while an approval completes it:

```sh
scripts/coordinate-implementation refresh-review-target --project /absolute/project \
  --run FAILED_OR_INTERRUPTED_RUN
```

### Watch workflow status

The global workflow install puts `coherence-status` in `~/.local/bin`. No virtual environment
activation or `jq` is needed. To run it from any directory, add the absolute path of one Git
checkout per repository to `${XDG_CONFIG_HOME:-$HOME/.config}/coherence/status-projects` (one path
per line). The command searches those repositories' Git-registered worktrees for the exact run ID.

```sh
coherence-status fix-title           # show the recorded workflow and task states once
coherence-status fix-title --watch   # check for changes every five seconds
coherence-status fix-title --project /absolute/worktree --watch
```

`--project` selects an exact worktree without reading the list. If a name matches more than one
worktree, the command lists the matches so you can use `--project`. Press Ctrl+C to stop watching;
this does not stop the workflow. Status reflects what the runner recorded, not proof that its
process is still alive. Use `coordinate-implementation status` for detailed JSON.

### Executor resolution and resume

The resolver requires only Python's standard library, prints only the absolute selected path on
success, and sends actionable failures to stderr with a nonzero exit. It reads existing JSON and
checks nonempty provider/model/effort strings, including an optional reviewer profile; it never
creates/copies configuration, searches outside the selected path, falls back after an explicit
override fails, authenticates providers or invokes a model. Downstream reads/validation still
apply; resolution does not prove runtime/provider availability. Resume uses retained executor
input rather than selecting new configuration.

The wrapper uses `runtime/.venv/bin/python` when it exists (install: `python3 -m venv runtime/.venv && runtime/.venv/bin/pip install -r runtime/requirements.lock && runtime/.venv/bin/pip install -e runtime`). Set `COHERENCE_PYTHON` only to select a different environment. Source execution
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

Dependencies determine execution order; sequential is the default and forward references are valid.
Under actual owner concurrency direction, use `start --parallel` or parent
`coordinate_implementation_start` with `parallel: true`. This is a start-only selection retained
in original run authority; resume uses it without a new flag. Feature approval alone is not
permission to launch real agents concurrently.

The controller selects a disjoint dependency-ready wave from optional `owned_paths` and
`generated_outputs`. Overlapping paths (including parent/child regions), shared outputs or
unknown ownership keep affected work sequential; they are not new intake failures. No worktree
is required. Each wave worker uses a distinct fresh saved Pi context and a thread-owned SQLite
connection with short transactions; no transaction or bookkeeping lock spans an SDK call/wait.
All siblings settle before serial checks, corrections, diff, stage and one focused commit per
task. Dependents wait for accepted producer checkpoints. A failed branch retains successful
sibling effects/checkpoints; inspected recovery continues only unfinished work. Source/index or
unexplained HEAD drift stops affected continuation, never authorizes a provider/Git replay. A linear commit
made outside the run (for example by the coordinator) is accepted for implementation-task effects when it does
not change a path that an unfinished task claimed; history records it as `external_commit`, and later checks,
checkpoints and the final review use the actual HEAD. A commit that includes such a claimed path stops with the
path and task named. Rewritten history (reset, rebase, amend), verification tasks (`owned_paths: []`) and
review/completion targets keep the strict rule.
Questions are presented serially after siblings settle.

Local-mechanism proof (real SDK fixture provider, temporary Git; not live-model judgment):
`PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=runtime python3 -m unittest discover -s runtime/tests -p 'test_graph_concurrency.py'`.
The `T013 FIXTURE-ONLY CLI/GIT EVIDENCE` output shows actual public start/history, overlapping
workers, quiescent checks/Git, focused commit IDs and accepted join. Capture that output through
normal coordinator assistance in the already selected issue evidence directory; temporary Git
repositories are disposed after the test, so their commit IDs are observations, not retained
application revisions. Associate the capture with the actual reviewed source checkpoint. Do not
claim live-model judgment, durable capture or owner acceptance from the fixture result.

Empty work reports
`no tasks` before storage, locks or SDK launch. No mandatory check, path list, approval envelope,
manifest, catalogue, graph, original session, cgroup or provenance record.

Implementation launch authorizes ordinary use of the selected worker/reviewer models; no separate
paid-consent question or `paid_scope` is needed for those calls. Paid application/test APIs still need
explicit approval. Declare them in `paid_apis` to request approval before storage or provider launch,
or supply an already approved top-level scope, for example:

```json
{"paid_scope":{"approved":true,"apis":["selected paid application/test API"]},"tasks":[{"id":"fix-title","description":"Correct the page title."}]}
```

Only application/test APIs are separately gated; changing selected model providers does not invalidate
API approval. Any declared paid APIs not covered by the approved scope trigger one current terminal or
attached-parent question. A denied or unavailable answer launches no provider. Credentials and historical
runs are not API approval. The unchanged grant and exclusions follow worker, fixing-worker and read-only
reviewer prompts. Additional paid APIs discovered during execution require approval before use. Existing
`agent_providers` fields remain compatible historical context, not a paid-consent requirement.

Optional `checks` accepts shell command strings, argv lists or objects with `command`/`argv`/`check` (in that precedence order).
A singular `check` or `required[].check` uses the same command format. Old registered catalogue
IDs are no longer executable: supply the actual project command when requesting that check. Checks
run in the project cwd with the runner's inherited environment. Each consuming project owns its
prerequisite diagnostics: make the requested check self-contained (for example,
`env PROJECT_CHECK_MODE=ready python -m unittest`) or use its command-scoped CLI launch (for
example, `project-cli exec -- python -m unittest`). Coherence does not discover arbitrary missing
variables. An attached launch inherits its already-running parent's environment; an `export` in a
worker shell cannot configure that parent, so prefer self-contained check commands there.
Commands run normally with no workflow deadline or output cap. A nonzero required command is retained with its exact command, exit and output as a failed attempt, then returned to the same-task worker for a reasoned safe scoped source/setup correction. A transport return is not task acceptance: the host carries an explicit `completed`, `blocked`, `failed`, or `incomplete` outcome to the runner. A worker finishes its assigned implementation and worker-owned semantic/manual acceptance, reports actual outcomes and remaining blockers, then returns; the runner executes/reruns configured checks, creates the focused checkpoint, and dispatches fresh independent review, without taking over all semantic/manual acceptance or the reviewer verdict. Pending runner stages alone are not unsuccessful. The shared launch prompt requires every initial, corrective and resumed worker/repair invocation to work autonomously through its assigned implementation and worker-owned acceptance. Unfinished code, unrun checks, complexity and correctable or intermittent test failures call for continued scoped work and diagnosis, not an early incomplete return; workers must not assume an unprovided time limit. Real cancellation, execution limits and safety/permission boundaries still apply. If further authorized progress is genuinely blocked, the worker identifies the concrete blocker, actual failed operation/evidence and what is needed to continue. If it must return unsuccessfully, it uses the SDK `report_task_outcome` tool and honestly reports failed/unrun acceptance. This does not permit waived checks, retries-until-green, invented diagnoses or false completion; unmet acceptance never becomes success. Offline prompt checks establish instruction delivery, not model obedience. An unsuccessful outcome, or a missing completion, stops the task before its checkpoint, session settlement, dependent dispatch, final review, or automatic fixer. The runner preserves partial bytes and actual history; when the host returns text with an unsuccessful status, that explanation is retained in the terminal diagnostic and private failure history (with a useful fallback for status-only callers). It is diagnostic evidence only, never acceptance, retry consent, or permission expansion, and safe status/monitor projections do not expose it. The same boundary applies to initial and corrective review-repair returns: an unsuccessful fixer is not checkpointed or marked approved, and no following reviewer is dispatched. On explicit resume, a retained explicit unsuccessful fixer outcome may continue only its same assigned repair after inspecting the diagnostic and reconciling the retained HEAD, exact claimed source/artifact bytes and file modes, and operation-local Git index entries, without Git clean-filter normalization. The corrective brief carries the actual failed call and partial diff, requiring diagnosis and a targeted correction before editing, never an unchanged retry or routine human-debugging question. Missing effect facts or target/source/index drift stops that continuation with staged and working bytes preserved; no replacement pair or uncertain call is replayed. A later returned corrective call takes precedence over historical failures: resume reconciles its checks/checkpoint without another provider call. Before restoring uncommitted ownership after a returned call or passed checks, it verifies retained exact source/artifact working bytes, file modes, and selected-path Git index entries; missing historical facts or drift stops that continuation without adopting bytes or replaying the provider. The continued repair still needs real checks, a focused checkpoint (or genuine no-change), and a fresh cumulative repair-review verdict. It does not scan summary prose, require a universal result format, or replace semantic work with a judging call; ordinary returned text remains compatible. The runner reruns the affected required command and only checkpoints after real passes; an unavailable safe correction or material decision reports its actual blocker. This is neither a skipped check nor cross-task reuse/post-review fixing, and it never spins an unchanged failed command. No universal test collection count, byte pin or evidence applicability receipt.
Optional `gates` contains question strings or objects with `question`/`description`; current owner
approval is needed before that task's worker starts. Other optional context is passed to the worker.

After the final reviewer call has appended its terminal metric row and all child calls have drained, the
runner makes at most one runner-only `workflow: metrics` commit for this run's exact JSONL artifact.
It validates the closed typed rows and exact path/index bytes, preserves unrelated staged and dirty work,
and inspects the actual parent/diff if Git reports an error after a possible commit. The reviewed application
SHA remains separate from the metric artifact SHA; no artifact means no empty commit and no extra review.
A collision, malformed tail, drift, hook/signing failure, or abrupt process death retains bytes and reports
an artifact gap separately without changing the task/review result or automatically recovering/replaying it.
Optional `owned_paths` limits source file/directory scope. Explicit SDK edit/write selections identify
source checkpoint paths; the runner never derives ownership by scanning a clean baseline. Around each worker
command (for example bash), the runner compares non-ignored dirty files in the task scope (`owned_paths`, or the
worktree without it) before and after the command, and claims each file the command created, changed or deleted.
A changed file that the task cannot claim (dirty before the task, outside `owned_paths`, or a generated output)
is not committed and does not stop the run; `tool_command` history records it as `uncommitted_changes`. A task may
optionally provide `handoff_paths`, a list of exact explicitly authorized pre-existing dirty regular files.
At task preparation the runner records each named file's bytes; at the actual claim it requires those
same bytes, then permits the intended edit and focused checkpoint. A resumed task retains an already
claimed exact transfer, so it checkpoints that intended edit without resnapshotting it or requiring a second edit. This is a narrow transfer, not an
`owned_paths` extension: directory/glob/broad coverage never adopts dirty content. A changed, missing,
symlinked, or unapproved target is refused with its filename, operation, and the corrective action
(restoring its authorized bytes or supplying a current exact handoff entry). Optional `generated_outputs`
names expected task artifacts for selective regeneration/cleanup guidance, not a registration, allowlist,
permission prerequisite, or automatic commit target.

## Real execution and safety

The current runtime's exclusive Git-worktree writer lock prevents overlapping cooperating runners. The SDK host
inherits that lock while active. At cutover, the lock continues to exclude competing controllers, not
explicitly authorized path-disjoint workers within one controller. A CLI entry waits transparently for that existing lock and may be
cancelled while waiting without creating a failed task/run or replacing its live writer; a platform
that cannot wait returns concrete busy. This is lock entry only, not a queue, watchdog, polling
service, or cancellation-drain claim. At an actual SDK edit/write, the runner protects unsafe/symlink,
out-of-scope, and already-modified target paths. Commands remain ordinary SDK tools, not an
adversarial sandbox: new, modified, deleted, ignored, Git-visible, or undeclared output never
stops a later command or check. The runner stages only explicitly selected source/deliverable
paths; it does not inventory, adopt, or clean arbitrary output.

Task-worker prompts state that the owner-authorized launch approves implementation of the assigned
scope, superseding historical planning-only wording without changing requirements, acceptance, real
manual gates or safety/permission boundaries. Final planning review checks authorization-neutral task
instructions; temporary approval status stays in the approval record. See [ADR-0003](decisions/ADR-0003-current-launch-authority-and-neutral-tasks.md).

Before affected worker reliance, coordinator preparation consumes final-review/handoff material risk
findings: investigate or prepare routine prerequisites within authority, then brief workers with usable
interfaces/findings, evidence limits and remaining gates. Each finding identifies affected tasks,
observed evidence versus unknowns, and next investigation, mitigation or necessary permission; later
discoveries get the same treatment while unrelated safe work continues. An unavailable capability,
access, paid, data or external boundary names the exact affected operation and corrective action and
blocks only affected work. No risk schema, scoring, admission checklist or parent acknowledgment is
introduced.

The receiving coordinator investigates and answers routine technical diagnosis, implementation
choices, ordinary corrections and focused verification within approved authority. Missing technical
evidence calls for investigation or an actionable blocker, not asking the owner to debug. Escalate
only product decisions, consequential unresolved trade-offs, material scope/complexity/verification
expansion, separately scoped spending, or actions outside authority. Autonomous answers never
impersonate owner consent or bypass manual, paid or permission gates. Routine worker or reviewer early
returns are diagnosis events, not completion or owner debugging: inspect the invocation, unfinished
scope, actual checks and retained effects, prepare a targeted correction or evidence handoff, then use
supported history/resume or evidence-only reassessment paths. Before continuing a failed expensive worker or
reviewer, inspect its recorded cause and invocation; never repeat an unchanged expensive failure.
Respect the retained initial-plus-two same-task/session allowance and compact diagnosis context;
exhaustion calls for inspected coordinator recovery, not renewed routine owner permission.
evidence-only review reassessment uses the existing retained evidence and only its supported eligibility,
never a task replay. Unknown cause or a real permission boundary stops the affected operation with its
exact capability/access/paid/data/external operation and corrective action.

Each task runs in a fresh coding conversation. Ordinary scoped technical fixes, isolated tests/servers,
necessary local/in-project dependency setup, and current-task artifact lifecycle need no owner question.
Small isolated tests and local test databases are allowed for any task, using bounded data/execution
that do not risk exhausting the machine or affecting unrelated data/services. Shared defaults live in
`_ROUTINE_AUTHORITY` in [the runner](../runtime/coherence_workflow/engine.py), included in initial,
corrective, and resumed task prompts; edit that block rather than individual tasks. See [ADR-0004](decisions/ADR-0004-shared-routine-worker-permissions.md).
Prompt delivery is text-contract evidence, not evidence of model obedience or a passed check. Worker continuations and coordinator failure diagnosis receive the actionable failure/diagnosis, targeted correction, unfinished scope, retained task/evidence/history references, and unchanged authority/acceptance constraints—not copied prior prompt bodies; original private history remains inspectable. An earlier agent-authored task, recovery, or handoff demand for
renewed exact-resource/setup/rerun consent does not override this current scoped authority; actual owner limits and
manual, paid, security, data, and external-operation gates still apply. Product decisions, substantial complexity increases,
separately scoped paid usage, and actions outside authority still ask. No global install, credential change,
deployment, push, or unrelated-work deletion is implied. It runs requested project checks and yields a real
focused commit before dependents. Normal Git configuration, hooks and signing are honored. A correctable whitespace, source, hook, or Git checkpoint failure returns to the same task worker with its actual error; affected required checks rerun before the normal checkpoint retry. A reported-failed/interrupted commit is reconciled from that operation's selected paths, attempted parent, and actual result before any retry, retaining a matching SHA without recommit. Failures retain
partial work and report the actual operation error. No empty commit for no-change work. No intent settlement
or operation trailers, hook/filter admission, hidden repair quotas, arbitrary timers or process receipts.
For an exact task-worker saved session, the initial dispatch plus at most two further calls is retained
in required history before adapter/provider dispatch. This narrow allowance includes required-check and
checkpoint corrections and survives process/storage reopen; terminal rows and duplicate observations do
not consume it again. Missing reservation history for retained invocations, or unsettled invocation history for reservations, stops continuation for inspection rather than resetting the allowance. A fourth call is refused before transport with the task/session identity and
targeted-coordinator-recovery action. The approved scope permits justified context replacement through
the explicit recovery route below; it does not erase prior attempts or cap reviewer/fixer lifecycle calls.

The final reviewer is a fresh, read-only SDK session, not the worker context. A routine reviewer early
return or evidence gap is a diagnosis/recovery event, not completion or an owner-debugging request:
inspect its invocation, retained task/check evidence, scope and effects; investigate within authority;
and use the supported targeted resume or evidence-only reassessment only when its requirements hold.
Do not repeat an unchanged expensive failed review. Unknown cause, target drift, or an actual
manual/paid/security/data/external gate stops only the affected continuation with the exact operation
and corrective action; unrelated safe work continues. It receives the
actual full committed range and diff on initial review, tasks, and the same routine-authority defaults/exclusions, with only
read/search tools for source continuation. It explicitly reports examined/passing areas and actionable defects.
Follow-up reviewers receive the prior outcome and actual delta from the prior reviewed head, checking repairs,
addressed findings, new defects and affected interactions. They carry forward unaffected passing coverage rather
than restarting the original review. Invalidated conclusions must be explained and re-examined; initial gaps
must be examined or remain explicit. A focused fix review never certifies unchecked original work. The brief separately identifies task/repair checkpoints verified from their actual Git commits, parents and changed paths; no-change means no commit changes, never that an unrelated HEAD is task work. It also gives each reviewer private retained required-command attempts (command, actual result and output) associated with completed task/repair checkpoints. Separately, initial and follow-up reviewers receive each available completed task's exact worker-reported return with its task ID and result checkpoint; missing or unusable historical returns are explicitly unavailable. These reports are not verified check passes or Git facts, and unsuccessful diagnostic returns are not completed acceptance. Reviewers evaluate that evidence semantically: retained passing execution remains valid when a read-only reviewer cannot rerun it; failed or missing required execution is an explicit gap; no live check is invented. On explicit resume, `owner-pair-v1` alone supports one same-head evidence reassessment when the latest settled review rejected for evidence/coverage only with no actionable finding: the coordinator privately retains a substantive targeted diagnosis or newly applicable retained evidence before one fresh read-only reassessment. It reviews outstanding gaps and affected conclusions only, retains the original rejection/range/checkpoints and unaffected coverage, and cannot use a fixer, task replay, empty commit, `refresh-review-target`, replacement verdict, or chain-limit reset. An unchanged handoff, uncertain stage, drift, failed/missing required check, or remaining gap stops the affected continuation. A remaining evidence gap stops that explicit resume after one reassessment; a later resume cannot repeat the preceding reassessment's diagnosis and unchanged evidence. Review ordinals advance independently of repair rounds, retaining causal grants for actual repairs before or after reassessment. Raw check output and worker returns stay out of CLI/monitor projections and review references. The existing evidence digest includes applicable completed returns as well as check evidence; when no usable return exists it retains the historical check-only digest. Historical references and rows are not backfilled. Intervening commits remain unrelated/unattributed integration context, and missing attribution stays explicit rather than guessed. Reviewers neither reject unrelated context solely for task-path scope nor certify it as delivery; causal cross-commit integration defects remain blockers, while independently unrelated defects report ownership/repair limits without expanding fixer authority. Authority does not prove checks or acceptance. The review protocol is `{approved:boolean,findings:string[],coverage:string[],coverage_gaps:string[],suggestions?:string[]}`. Coverage is the cumulative set of actual examined/passing areas, including retained valid prior coverage; gaps include unchecked or invalidated conclusions. These summaries and the prior review/delta base live in existing review-history references, with no schema migration or historical backfill. A historical outcome lacking explicit coverage is supplied as a gap to establish, not inferred passing areas; completed historical verdicts remain unchanged. Suggestions default empty, are nonblocking, and are shown separately from findings. A positive verdict with explicit passing coverage, no gaps and no blockers completes even with suggestions; blockers or gaps reject despite a positive flag. Every blocker uses `path:line - defect` and describes concrete impact and a requirement, correctness, security, or data-safety basis in ordinary prose; no literal basis suffix is required; crashes, hangs, target/credential risks, and false-unavailable observations remain blockers rather than suggestions. A well-formed actionable first rejection continues that same reviewer session for one correction round: the reviewer makes a concise plan and implements its fixes using the configured reviewer model, not the task-worker model. Malformed, interrupted, uncertain, negative-empty, or nonactionable review results stop without fixing; safe deterministic normalization may only recover the actual review result. The runner explicitly enables scoped writer tools only for the review→repair continuation, retaining the review transcript and SDK session identity. Every initial and same-stage corrective repair prompt receives the original task contracts,
unchanged authority, shared routine permissions/exclusions, paid-use boundary, explicit source/artifact
scope and the actual findings. It requires a concise correction plan, examination of directly related
adverse paths, and the integrated result against original acceptance without speculative scope expansion;
a fixer never independently accepts delivery. Its checks and focused checkpoint retain a distinct execution
identity and explicit predecessor. Correctable
check/checkpoint errors stay inside that assigned round and rerun affected checks before its
checkpoint. The existing `fixer` history role identifies this repair stage, not a separate executor-model agent. A process restart before repair reopens the privately retained reviewer session; historical outcomes without a saved session can only use a fresh reviewer-model repair session, without claiming warm-context reuse. Final chain control selects the last eligible persisted stage. New runs retain `owner-pair-v1`: routine repairs within the original scope proceed without round-based questions, including on eligible explicit resume. Each later rejection needs its own exact grant and assigned fixer/fresh reviewer; reuse existing assignments. This narrow authority never covers material scope, paid, security, data, external actions, uncertain stages, or target drift. Historical no-policy runs retain the old two-review/one-fixer limit. SDK compaction/retries follow SDK behavior; compaction/optional telemetry never creates a
workflow fatal condition. SDK tools truncate long output with their normal continuation
instructions; the transport has no size cap. A runner may reuse only a returned private saved session identity from the same run after a
successful idle settlement and preceding verified checkpoint. Reuse also requires an explicit
nonempty matching `context_group` and unchanged role, worktree, executor, resources,
instructions, settings and authority; task text or callback identity alone are not mismatches.
`fresh_only` and each independent review select fresh. Review→repair is a continuation of the selected review, not cross-task candidate reuse; it keeps all effective resources except the explicitly enabled writer tools unchanged, including disabled skill discovery through subsequent corrective prompts. Every repair prompt carries the current-launch implementation authority and shared routine permissions/exclusions.
The repair primitive accepts and forwards its caller's explicit rejecting-review, predecessor, fixer identity and
positive assigned round, subject to retained dispatch policy; legacy chain selection still supplies the first repair
assignment, so this does not itself select or authorize an additional lifecycle round. Candidates sort by latest successful settlement then
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

Material questions, including unapproved paid application/test APIs, use actual current terminal input.
Without an interactive terminal, or when terminal input reaches EOF, the run stops with a
non-sensitive operation/channel diagnostic and interactive or explicit inspected-resume guidance;
it does not fabricate an answer. Actual parent-channel connection loss or an empty reply likewise
identifies the question/readiness operation and directs reconnection through the parent-session
bridge followed by explicit inspected resume, never automatic retry. These errors preserve partial
work and do not establish recovery success. A loaded global parent-session bridge may instead
launch this same command with its private socket environment;
it wakes that parent with the exact pending question (including the paid-scope decision when needed) and returns only its correlated reply to the
waiting worker. Historical runtimes could send a marked owner-only continuation decision carrying the rejecting execution, original reviewed base/head, original scope, and one-repair/fresh-review/no-repeat effect. The bridge requires registered `ask_user`, tells the parent to call it, and accepts the actual nonempty owner answer only through `coordinate_implementation_owner_reply`; routine `coordinate_implementation_reply` cannot answer it. This is transport routing, not cryptographic proof of human identity, and neither question nor answer is retained in SQLite or public projections. Missing `ask_user`, cancellation, an empty answer, or an unavailable/uncorrelated reply stops with the concrete bridge diagnostic. A callback that cannot accept the owner-only marker/context also stops; it is never retried through routine triage. Routine technical questions remain coordinator-triaged and autonomous. Before attached execution, the runner checks the existing socket's authenticated
readiness response and active parent reply tool; incomplete/mismatched configuration stops before
storage or SDK launch, without terminal fallback. Each worker's actual SDK tool set must contain
`ask_owner` before its prompt starts. This proves current readiness, not future delivery; later
connection failures retain partial work and report the error. No model probe or heartbeat is used.
It retains neither questions nor answers in SQLite. Parent-session shutdown or the
launch tool's cancellation signal terminates only its owned runner through that runner's normal
SIGTERM path and waits for it before bridge cleanup. The bridge is optional: direct terminal
invocation remains unchanged. The source is
`runtime/pi-extensions/coordinate-implementation-bridge.js`, outside Pi's project auto-discovery.
Global activation links this source into the user's Pi extensions directory, so worktrees do not
register a second copy. The global bridge does not require project-extension trust. Other project
resources still follow Pi's normal trust rules; never change global trust defaults or trust parent
directories just to load tools. A prompt cannot load tools that startup skipped. In Paseo, use a fresh session and verify checkout, revision, current approval, loaded capabilities, and all four bridge tools
(`coordinate_implementation_start`, `coordinate_implementation_reply`, `coordinate_implementation_owner_reply`, and `coordinate_implementation_steer`) are available before launch;
do not reload or restart the current session automatically. After merging, start in the main
checkout and verify its own trust decision and tool availability: trust is path-specific, not
branch-specific. The bridge uses an executable `scripts/coordinate-implementation` in that session's checkout when present; otherwise it launches the shared `coordinate-implementation` on PATH. Permission errors on an existing local launcher are not silently bypassed. Both paths keep that session's cwd as `--project`, never an old worktree or the suite checkout.
Runner diagnostics go to stderr so they cannot corrupt the parent's RPC stdout. During an attached run, the active worker/fixer privately advertises its exact task and invocation target. The parent may call `coordinate_implementation_steer` only with that exact advertised run/task/invocation and a new direction ID; it returns `accepted` immediately, then parent notifications report `queued`, `consumed`, `failed-unavailable`, or `unknown`. Active-target and steering-status notifications remain visible but do not trigger a parent agent turn; only questions and terminal workflow success/error notifications wake the parent. `consumed` is matching SDK user-message observation, not compliance. No target exists for a reviewer, a completed invocation, or a task-ID-only successor; connection loss stays unknown and is never automatically resent or retargeted. Direction text remains in the authorized parent/worker conversation, not runner history or monitor data. After a bridge change, use a fresh Paseo session, verify checkout, revision, current approval, loaded capabilities, checkout trust, and all four bridge tools (`coordinate_implementation_start`, `coordinate_implementation_reply`, `coordinate_implementation_owner_reply`, `coordinate_implementation_steer`), and obtain separate authorization before any live-provider proof. The bridge starts an explicit same-run continuation with `{run, resume: true}`; it supplies no replacement task or executor input. There is no Paseo
version/transcript/binding/receipt gate. No automatic resume/control mailbox or daemon.
Cancellation aborts the owned SDK session and waits for its host; it never signals parent/sibling
processes or provisions/signals cgroups.

## History, explicit resume and abandon

`resume --project ROOT --run ID` is explicit only for a retained failed or interrupted run. Under the ordinary writer lock it inspects retained invocation/cause and original inputs, preserves the original contract/order, executor, paid scope, review base and attempts, skips only checkpointed tasks with matching operation history, and continues unfinished work or the exact eligible review/fix stage. It never compares the worktree, HEAD, index or outputs as admission, repeats a completed checkpoint, replaces a known live writer, resets consumed review slots, or asks again for unchanged paid scope. Missing original/checkpoint history, uncertain completed effects, or uncertain review invocation reports that precise limit. An unfinished task may continue only with its retained task-local source paths and known generated artifacts; those facts permit a selective file cleanup, never adoption or deletion of unknown output. Its exact saved worker-session dispatch history also retains the initial-plus-two allowance across reopen; missing/uncertain identity or history stops that continuation for inspection rather than resetting the allowance.

### Coordinator-selected worker recovery

Routine recovery is part of approved implementation, not an owner debugging request. Inspect the
failed invocation, useful saved context, partial work and actual checks. Prefer continuing useful
context. Select a new context or the explicitly permitted implementation fallback only when the
next action addresses the diagnosed obstacle; incomplete returns alone do not establish model incapability.

```sh
scripts/coordinate-implementation resume --project /absolute/project --run RETAINED_RUN \
  --recovery-action fresh --diagnosis 'Inspected cause; targeted correction using retained work'
# Use continue for the retained session, or escalate for its implementation_fallback profile.
```

The parent `coordinate_implementation_start` tool accepts `resume: true`, `run`, `recovery_action`
and `diagnosis`. These are coordinator decisions, not fabricated owner answers. The route keeps
original inputs, scope, source claims, completed checkpoints and attempt history. Fresh dispatch
requires a settled exact predecessor and known session effects; uncertain calls and unknown bytes
are not adopted. An SDK error is a settled predecessor only when the host attests `settled: true`
on its `error` record: no session was created, or the session was idle with no pending question,
so no tool call was in flight. A settled error that opened no session needs `fresh`, not
`continue`. Other SDK errors, a lost host result and historical failure rows stay uncertain.
Rerun affected required checks and keep independent review. Existing runs retain
their launch configuration: no fallback is inferred from a later file change or reviewer profile.

**Fresh offline verification at a repaired commit (source CLI only).** Inspect the failed call,
its effects, and the repair diff. If the call explicitly returned `failed`, the task has
`owned_paths: []` with no outputs, handoffs or retained writes, and the inspected repair is
current HEAD with the failed revision as its only parent, select it by full SHA:

```sh
scripts/coordinate-implementation resume --project /absolute/project --run RETAINED_RUN \
  --recovery-action fresh --target-head "$INSPECTED_FULL_SHA" \
  --diagnosis 'The failed local check settled without external effects. The inspected repair corrects its fixture; rerun the full offline verification.'
```

Explain the inspected cause and correction, why the attempt was offline, and why no external
effects remain. No particular wording proves those facts. This is not a transfer, an owner
receipt or a grant for paid, security, data or external actions. Git drift on delivery, repair,
owned paths or literal inputs in the verifier's `paths` list blocks this attempt. Preserve unrelated dirty work.
Inspect any other actual check inputs yourself; the runner does not trace dependencies.
The new attempt uses the original executor, manual gates and required checks. Ordinary offline commands need no repeat approval; no project edit is
authorized. Only a new result and passing checks can release dependents. The verifier's
no-change checkpoint does not claim the repair commit. Final review keeps the original range.
If interrupted after pinning, inspect the attempt and use plain `resume` to reconcile it;
do not select another target to replay a returned call. Failure finalization leaves optional
metrics uncommitted while verification is pinned, so telemetry cannot move its target. On
reopen those bytes are not adopted. If the pinned worker explicitly returns `failed`, a new
inspected direct child of that failed revision can be selected with the same explicit action.
This does not apply to a failed runner check. Plain resume never selects a new target.

If implementation escalation fails—including an unsuccessful worker return, required check or
checkpoint failure—stop and notify the owner with the diagnosis, preserved work and unmet checks.
No corrective worker, fresh replacement or further escalation follows that failure. Ordinary resume
also stops; continuation needs a new owner direction, not repeated routine authorization questions.
A subsequent successful owner-authorized `recover-task` completion for that exact task releases the
stop for normal resume and independent review. Authorization alone or a failed transfer does not.
A completed escalation task does not alter the normal worker or independent reviewer for later tasks.

### Accept an owner-authorized external same-task completion

When an inspected task session is exhausted and an explicitly owner-authorized external worker has
already completed that **same task**, use `recover-task`, then normal `resume`. Do not replay the
old session, change the retained executor, edit SQLite, create a replacement workflow, or make a fake
source edit. This action launches no model. It checkpoints only the next unfinished task, after its
dependencies, with the original required commands and manual gates. Independent full-range review
still follows normal continuation; a supplied external summary is a worker report, not acceptance proof.

First settle the failed invocation and writer, inspect its actual cause/session and the external diff
and original semantic acceptance, and obtain actual owner authority for the exact file transfer.
Prepare private JSON outside task-owned source paths:

```json
{
  "task_id": "EXACT_UNFINISHED_TASK",
  "invocation_id": "LATEST_RETAINED_TASK_INVOCATION_ID",
  "head": "FULL_CURRENT_GIT_HEAD",
  "diagnosis": "Inspected failure/cause and why the completed external correction addresses it.",
  "worker": "Actual external worker identity and provider/model/effort, as known",
  "summary": "Actual original semantic/manual acceptance outcomes and evidence references; remaining runner stages.",
  "paths": {"src/exact-file.py": {"sha256": "64_LOWERCASE_HEX_DIGITS_OF_WORKING_FILE", "mode": 420}}
}
```

`history` exposes ordinary invocation IDs, not saved private sessions. For each explicitly selected
regular dirty file, compute SHA256 from its **working bytes** and mode with Python
`hashlib.sha256(path.read_bytes()).hexdigest()` and `stat.S_IMODE(path.stat().st_mode)` (`420` is
`0644`). `head` is `git -C ROOT rev-parse HEAD`. Do not infer transfer authority from dirty state or
prior partial claims. The exact `paths` map alone transfers these already-complete bytes, subject to
the original optional `owned_paths`; other dirty/staged files remain untouched.

```sh
scripts/coordinate-implementation history --project /absolute/project --run RETAINED_RUN
# Only after the actual owner authorizes this inspected exact transfer:
scripts/coordinate-implementation recover-task --project /absolute/project --run RETAINED_RUN \
  --recovery /private/same-task-recovery.json --owner-authorized
# Only after recover-task succeeds; uses original retained executor and review base:
scripts/coordinate-implementation resume --project /absolute/project --run RETAINED_RUN
```

`--owner-authorized` asserts actual authority; it does not authenticate a conversation or authorize
new scope, paid APIs, external effects, or acceptance waivers. The action retains new private
append-only recovery facts and separate external attribution, never changes old invocation/dispatch
outcomes or resets their initial-plus-two allowance. It verifies exact source bytes/modes, selected
index entries and HEAD around checks, and uses normal focused Git hooks/signing. Changed transfer,
uncertain/live worker, failed check/manual gate or unsafe ownership stops before completion, without
a provider retry. Correct an ordinary failure within authority, inspect any partial Git effect, and
explicitly supply the current authorized transfer again. It can reconcile its own exact already-made
checkpoint after a result-write interruption without recommitting; repeating an identical transfer
for that checkpoint while the run remains stopped is idempotent. It does not accept deleted files,
unknown bytes, a different task, or a separately precommitted external change. No schema migration,
historical backfill, external-worker metric, or fabricated SDK producer is created. Optional monitor
producer links remain unknown for this external completion. The source CLI supports this action;
the parent bridge has no new recovery tool. Use the reviewed source launcher explicitly; an installed
runtime snapshot needs separately authorized updating. For changed global skill discovery in Paseo,
prepare a fresh-session handoff, not an automatic reload/restart.

For an uncertain failed initial or first repair read-only review, explicit resume can ask the coordinator for the exact completed reviewer transcript when inspection identifies a compound-location format failure. The supplied artifact must contain the independent read-only prompt, the retained task scope and original range, the exact committed diff, and a complete actionable rejection with a finding that the current parser accepts but the applicable earlier parser rejected (single-range for initial review; same-path multi-range for first repair review). For a first repair review, the retained initial rejection, successful fixer, causal order, prior-review context and repair delta must also match. It must contain no writer tool calls. The target HEAD must remain unchanged, and the original committed-range, reviewed repair-delta and task-owned paths must have no index, worktree or untracked drift. Unrelated dirty context is left untouched; its historical bytes are not certified by recovery. The runner appends the recovered rejection and preserves the failed attempt, findings, suggestions, coverage and gaps; it does not claim that a session link was historically retained. Missing, ambiguous, interrupted, incompatible or approving artifacts and target drift remain blocked. The retained failure cause must be format-related; absent or conflicting cause evidence leaves transport uncertainty blocked. New attempts retain that cause in required review history; older attempts can use an available failure observation, not a session-identity claim. A recovered actionable rejection follows the normal scoped repair and fresh cumulative review path, with an exact grant for each later pair. The coordinator supplies the artifact path through the existing technical question; this is not permission to resume any particular run.

Review prompts summarize retained checks with command, status, exit and checkpoint context, and provide private read-only file paths for complete raw outputs. The reviewer must read relevant outputs, continuing long reads as needed; the original outputs remain in workflow history. Delivery files use a private temporary directory outside the source checkout and are not source checkpoints. On explicit resume only, an exactly retained provider rejection of an oversized single input text field may continue the same failed read-only review stage with a freshly constructed compact payload. The runner verifies the original scope, causal predecessor, reviewed target and reported field limit before dispatch. It appends the new dispatch and result to the same stage; it does not replay tasks or repairs, reuse a failed verdict/session, or grant a new repair. Unknown transport errors, missing output, target drift and an uncorrected payload remain blocked.

“No automatic resume” means no blind retry, replay, daemon, or historical restart. When an inspected failure identifies an authorized repair outside the current worker's paths, the coordinator first settles that invocation and its lock, then delegates a separate repair with exact paths and the retained executor. The coordinator inspects the repair diff, runs relevant checks, and verifies its focused checkpoint before an explicit supported continuation of the retained unfinished run. The original worker never gains the repair path or launches a nested CLI. A failed or unknown repair cause is investigated rather than relaunched; a later routine technical question is coordinator-triaged without renewed routine consent. Manual, product, material-scope, spending, security and data boundaries still stop/escalate normally.

For evidence-only reassessment, explicit resume requires a retained `owner-pair-v1` findings-free coverage rejection and ordinarily the exact original reviewed HEAD. The sole exception is this run's retained successful non-no-change metrics finalizer commit directly after that head: its recorded SHA, parent and exact run artifact path must match current HEAD, the reviewed head and `artifact_relative(run)`, and Git must verify its single parent and exact changed path. Use the latest retained artifact-finalization outcome, skipping only exact `not_created` reports with no other facts: a resume without a new artifact does not erase the earlier commit evidence. Failed, malformed or conflicting finalizer facts still stop dispatch for inspection and reconciliation. Reassessment retains the original range and completion records the reviewed application SHA, not the metrics HEAD. The coordinator's diagnosis/evidence basis remains private history; safe status reports only a coordinator/assigned evidence-reassessment stage, never the diagnosis. The fresh reviewer has no repair authority and approval still requires cumulative sufficient coverage with no blockers or gaps. For additional owner-authorized repair rounds, resume distinguishes a reserved/dispatched stage with no invocation start from an uncertain started call. Only the former may invoke once. A returned repair retains explicit owned paths and head; resume can continue local checks/checkpoint work without calling the fixer again. A passed checkpoint is retained at its exact SHA/parent. A commit completed before checkpoint-result recording is reconciled against its recorded parent, selected paths and content hashes before retaining it without recommit. Missing facts, uncertain check completion, failed calls, or mismatched target effects stop for inspection. This is scoped additional-round recovery, not historical repair or a general recovery overhaul.

`status` and `history` are read-only, execution-format-only SQLite readers; there is no
legacy-reader fallback. A missing run reports its ID; an unsupported database format reports
incompatibility without changing storage. Only a new `start` quarantines an unsupported database,
under the worktree writer lock and before execution tables are created. It checkpoints committed
WAL data first (busy storage stops recovery), preserves the database and remaining sidecars in a
unique `.coherence/workflow/quarantine-*` directory, reports that path on stderr, and creates clean
execution storage. It never migrates or deletes archived history. `resume` and `abandon` do not
quarantine storage; an archived run cannot resume against the clean database.

New runs privately retain their original parsed contract/order, selected executor, settled authority, resolved initial review base, and `authority.review_policy: "owner-pair-v1"` before dependent mutation. Resume uses those retained inputs; historical absent policy remains the old two-review/one-fixer lifecycle, while an unknown retained name blocks the affected continuation with a compatible-version action. Each later routine pair has an append-only grant (grant ID, rejecting execution, exact base/head, original scope reference, assigned fixer/fresh reviewer). The grant must be retained before dispatch and is atomically consumed to reserve exactly its fixer; its reviewer becomes eligible only after that fixer succeeds. The store rejects a second grant for the same rejection and validates causal order, exact range, original-scope reference and assigned reservation at dispatch, not just in the engine. Duplicate or mismatched rejection/range/scope/order, failed fixer, and uncertain stages stop actionably without a replacement call. CLI status/history separately projects policy and grant/reservation facts with the next retained stage, without private conversations or sessions. That stage follows actual execution outcomes: completed pairs show completion, failed/uncertain invocations show blocked, and another eligible actionable rejection selects its scoped repair. Append-only operation history preserves actual invocation, check and checkpoint outcomes; a corrected check does not replace its failed command/exit/output, and checkpoint facts retain only task-local paths/artifacts and available SHA/parent. CLI output is a safe projection (task IDs, review base and operation facts), never original task text, prompts, answers or check output. This is not a resume policy or a filesystem/Git snapshot.

Ordinary task/run progress is useful history, not dispatch or completion proof. New optional usage reporting appends one JSONL row per actual terminal worker, correction, fixer, or reviewer call, keyed by its exact invocation identity; it never allocates reviewer usage to tasks or mirrors metrics in SQLite. Status derives qualified token subtotals and coverage from those rows plus ordinary exact dispatch identities. Selected session mode/reason is intent, while actual mode/identity requires the current call's opened-session observation. Missing/failed optional appends remain partial or unknown, never zero or an invoice claim, and do not replace task, check, Git, provider, or required-history outcomes. Required original-input, operation-history, progress, and review/fixer dispatch writes are made before their dependent mutation. Review-chain history retains actual execution IDs, attempts/outcomes/uncertainty, consumed review ordinal/fixing round, explicit causal IDs, private parsed findings and commit/range references. It preserves an initial rejection and completed task checkpoint identity across reopen; an uncertain invocation is never a success or replay permission. Status safely exposes parsed findings, nonblocking suggestions, and references separately, not raw reviewer JSON, prompts, saved sessions, or answers. Optional monitor observations remain non-authoritative gaps.  If one reports a SQLite failure, the runner re-reads that specific operation: a known completed write is retained without replay, otherwise it makes one safe local correction; an unreadable or unrecoverable result stops only that affected action with its actual persistence limit. It never reruns task tools or commits to repair progress or invents missing history. Optional monitoring, metrics, and telemetry persistence remains a reported gap and does not block task/check/Git/provider work. Once terminal calls have drained, the runner may make one separately reported metrics-only artifact commit; its SHA/current HEAD is not reviewed application code and does not alter the recorded review range or task checkpoints. Its failure retains the exact artifact bytes and original execution outcome. Old tables/rows in supported mixed-format databases remain in place, including incomplete intents;
unsupported databases are preserved in startup quarantine. New tasks neither reconcile nor replay old rows. Malformed optional history cannot veto new coding.
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
runtime dependencies. The SDK dependency lock is install metadata, not exact SDK/Node equality
admission. The shared `runtime/pi-host/sdk.mjs` loader uses an available local package first
(including an explicit isolated installation), then Pi's `PI_PACKAGE_DIR`, then the installed
release named by `PI_CODING_AGENT_DIR/install/current-version` or the default `~/.pi/agent`.
As a final fallback, it finds the first runnable `pi` file on `PATH`, follows its symlink,
and checks its owning package metadata for the Pi SDK name. Discovery does not execute
the CLI or scan other global installations; an unrelated runnable `pi` is not bypassed.
A new Git/Paseo worktree does not need copied `node_modules`. An invalid explicitly selected
package reports its actual error rather than silently switching SDKs.
A stale local `runtime/pi-host/node_modules` (for example, from an earlier `npm ci`) takes
precedence over the installed Pi, so its older model catalog applies, also to extension
providers such as `claude-bridge`. Remove it to follow the installed Pi release.

Package discovery uses Node's package lookup; entry and SDK-dependency loading use Node's ESM
resolver and public package exports, not constructed `dist/` paths or nested dependency paths.
The parent-aware resolver runs in a short-lived Node process with its required resolver flag;
Pi/Paseo need no extra launch flags. It executes no SDK code or workflow transport, and omits
`NODE_OPTIONS` in that resolver process so workflow preloads cannot start there. Caller
symlink-preservation and export-condition flags are forwarded separately; executable preloads
and loaders are not. Actual SDK imports retain the caller's environment and their original errors. Tests use the same loader.
Pi/Paseo updates therefore do not require a fixed installation layout; actual breaking SDK API
changes may still need adaptation. The offline compatibility checks below cover discovery,
public imports, sessions, tools and bridge discovery with the installed SDK, without paid
provider calls. Re-run them after updates; no automatic update, installation, restart or live
model probe is performed. The current runtime uses the LangGraph controller described above.
No cgroup delegation or host manifests are required.
Explicit optional setup remains `scripts/install-workflow.sh --prefix NEW_DIRECTORY --allow-network`
only with separate install/network authority. Ordinary entry never calls it.

For explicitly authorized global activation, add `--global`:

```sh
scripts/install-workflow.sh --prefix "$HOME/.local/share/coherence-workflow" --allow-network --global
```

Choose a new absolute prefix. This installs an isolated Python/SDK runtime and creates three links:

- `~/.local/bin/coordinate-implementation`
- `~/.local/bin/coherence-status`
- `${PI_CODING_AGENT_DIR:-$HOME/.pi/agent}/extensions/coordinate-implementation-bridge.js`

Existing foreign prefixes or link destinations are preserved and reported. Keep this suite checkout:
the bridge and globally linked skills refer to its current files, while the installed commands are a
snapshot. To update them, choose a new prefix and verify which command links point to the old
Coherence prefix. Remove only those verified installer-owned links before running the installer for
the new prefix; retain the old prefix and project data. Leave the bridge link in place if it already
points to the suite source shown below. Ensure `~/.local/bin` is on PATH.
The bridge source stays outside `.pi/extensions/`, so the suite checkout, new Git worktrees and
unrelated repositories load only the global entry. Do not copy it into project extension directories.
For an existing installation, inspect the global bridge link and repoint only the verified suite-owned
link to `runtime/pi-extensions/coordinate-implementation-bridge.js` in the retained suite checkout;
no runtime reinstall or download is needed for this source-path change. Foreign entries must be
preserved and resolved explicitly. Existing worktrees on older revisions still contain the old project
extension: bring this fix into those worktrees before starting a fresh session there. Merely changing
the global link does not remove their duplicate registration.
New repos need no copied launcher or bridge, but still
supply their own task file and explicit executor JSON; no model, permissions, adoption policy,
authentication or old run data is copied. Use a fresh Pi/Paseo session and verify checkout, revision, current approval, loaded capabilities, and all four bridge tools;
never automatically reload/restart the current session. Attached runs need a long-lived parent:
use interactive Pi, Paseo, or RPC with stdin kept open until the terminal workflow notification.
A one-shot print/JSON parent can settle after an intermediate notification and exit, which normally
cancels its owned runner; it is not a reliable harness for a nonempty asynchronous run. An empty-task
smoke verifies discovery/launch without creating a workflow store; use a disposable repository for
actual worker/reviewer smoke checks rather than adding runtime artifacts to an unrelated project.
To roll back global activation, remove only the verified installer-owned links listed above.
Leave the isolated runtime, status configuration, and project data intact.

Focused checks in the prepared environment:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=runtime:runtime/tests \
  .pi/workflow-validation/venv/bin/python -B -m unittest discover -v -s runtime/tests
COHERENCE_PYTHON=python3 node --test runtime/tests/test_sdk_resolution.mjs \
  runtime/tests/test_host.mjs runtime/tests/test_bridge.mjs \
  runtime/tests/test_global_bridge.mjs runtime/tests/test_saved_sessions.mjs
```

These exercise real disposable Git/project/tool operations and clearly labelled offline SDK
transport/compaction fixtures; they do not manufacture live-provider success. Independent final
review remains separate from writer validation. An optional task input `review_base` must resolve to a
Git commit that is an ancestor of the run baseline; it changes that review's actual diff/prompt and every
recorded review outcome to base→current-head. Invalid or unrelated bases fail only the affected review.
A malformed, failed, or interrupted reviewer records that actual selected range before its original error
propagates. Without it, the default
run-baseline→head range is unchanged. In Paseo, adopting changed global skills requires a fresh-session handoff; do not reload or restart the current session automatically.
