# Workflow monitor

`workflow_monitor` is a local, read-only presentation of recording-contract version 1
workflow snapshots. It imports no workflow writer, never creates or migrates a store,
and has no execution or control routes.

## Project discovery

The multi-project inventory is read-only. It validates an expanded projects root as a
readable non-symlink directory, considers only its immediate non-symlink child Git
worktree roots, then uses `git worktree list --porcelain -z` to include that repository's
registered linked worktrees (including external paths with spaces). It never recursively
scans projects or Paseo directories and never follows an arbitrary root-child symlink.

Registered worktrees are grouped by canonical Git common-directory identity. The registered
main is identified by its admin directory, not by a branch, current directory, or directory
name; canonical aliases are listed once. Each live worktree has one retained Reader and an
opaque project/recording reference. Project labels use the registered main's directory name;
source labels are `main`, `linked`, or `preserved`. Browser-facing code must use references,
never paths. An explicit project-list request (including page reload) refreshes discovery while
retaining existing Reader bindings; run polling does not rediscover projects/worktrees. Listing does not open every database snapshot or create a
store. An empty valid root is usable, while an invalid root is an actionable error. A missing
store is reported honestly and the same Reader can observe its first legitimate later store;
a Reader that has observed a replaced store reports it unavailable rather than adopting it.


New recordings use descriptor version 3. Each task retains its label, declared
prerequisites, and the complete explicit `outcome`/`description` work text when supplied;
missing work text remains unknown. The descriptor also records explicit initial independent
review intent separately from generic review phase vocabulary. It never retains task objects,
prompts, answers, credentials, or arbitrary payloads. Closed public DTOs expose only these
fields, so a missing work text or review intent is not replaced from summaries or current
files. Updating the viewer does not upgrade existing recordings: an older descriptor has no
supported planned-task projection, so its calls do not acquire task numbers or planned slots.
Use a new recording from the updated runtime to inspect those features; no history is backfilled.

Install the exact dependencies from `requirements.lock` in a prepared isolated Python
environment; starting the viewer never installs or builds anything. From the repository
root, use the prepared interpreter explicitly so neither launch nor checks accidentally
use the system Python. Build the local web assets first; this is an explicit preparation step, never viewer startup behavior:

```sh
npm --prefix workflow_monitor/web run build
workflow_monitor/.venv/bin/python -m workflow_monitor --projects-root "$HOME/projects" --assets "$PWD/workflow_monitor/web/dist" --port 8765
```

`--projects-root` defaults to the expanded `~/projects`, so it may be omitted when that
is the intended inventory root. It must already be a readable, regular directory; a
missing, unreadable, symlinked, or non-directory root stops before binding with an
actionable `--projects-root` diagnostic and is never created. An empty valid root starts
normally and reports an empty inventory. The package also declares the equivalent
`workflow-monitor` console entry point for a separately prepared local installation. It
uses the same required `--assets` argument and optional `--projects-root`; neither form
installs dependencies, builds assets, creates a workflow store, or starts the workflow
runtime. Keep `requirements.lock` with the package metadata when preparing that isolated
environment. A missing build root, missing `index.html`, symlinked root, or non-directory
asset root stops before binding with a fixed actionable diagnostic; rebuild to a regular
local `dist/` directory and retry.

Then open `http://127.0.0.1:8765/` in a local browser. One launcher uses this one loopback port for every project discovered under the selected root; it can be started from any working directory after the package and assets are prepared. The left selector and selected-run banner use readable numbered run labels; opaque references remain internal for API requests and URL routing. The graph retains one stable planned worker slot for every known task and a separately planned final independent review, then reconciles each slot only with its unique exact recorded initial call. Later plans remain visible while earlier calls run. Corrective prompts and later reviews appear only when exact recorded evidence exists; fixing rounds are not fabricated as calls. Declared prerequisites (including planned review completion) are distinct from recorded causal/input relations. Missing, ambiguous, or cyclic relations remain qualified rather than guessed. Details lead with the recorded action, outcome, blocker and findings. Missing, malformed, partial or unsupported records remain unavailable or qualified rather than repaired into a completed graph.

The browser URL identifies a run as `/projects/{project_ref}/runs/id-<percent-encoded qualified ID>`; the client decodes that component once, looks it up exactly in the selected project's inventory, and only then uses the opaque API reference. Every displayed live/preserved ID uses a fixed recording hash plus the unchanged old run ID, so collisions appearing or disappearing cannot change an existing URL. Public references, pages and freshness are recording-local; normalization resolves relations before qualifying public refs, never by rewriting internal IDs or JSON. A successful nonempty root inventory selects a project and replaces `/` with that project's newest finite-epoch run (descending, deterministic ID ties; unknown times last). Different selections push history, repeated selections do not, and Back/Forward clears obsolete graph/Details work before loading the addressed run. Unknown, removed, or unavailable IDs remain in the address bar with an honest unavailable state rather than selecting a substitute. The run-ID filter is a case-insensitive local substring filter: it neither changes the selected URL/history nor sends a server search, and it explicitly reports selected-outside-filter and no-match states. Polling remains at 60 seconds and never steals the current selection for a newer row.

A confirmed internal step that stops a recorded failed run appears as a red node with its explicit recorded support relation. A failure before any agent starts remains visible without an invented agent. Recovered checks remain in Details/history, not extra graph nodes. Edges come only from explicit recorded input, correction, review/fix and stop facts; missing, ambiguous or cyclic relations remain qualified in Details and are not rendered.

Click a task, execution, review, stop, or edge to highlight it and update the visible Details panel next to the graph (below it on narrow screens). Task Details lead with stable source-order task number, role, state, the complete retained work text, blockers, and acceptance. Supported recordings that lack full work text say that it is unknown; they never reconstruct it from labels, summaries, or current files. Execution Details keep outcome, what happened, blocker and actionable recorded findings separate from acceptance. History and expanders translate safe typed fields into ordinary language; opaque invocation, session, branch, epoch, occurrence, and run-reference values remain internal for routing and matching. Scheduled fixing rounds are notices, not invented calls. Metric Details use distinct **This call**, **Task total**, and **Overall run** scopes. This call shows recorded Input tokens, Output tokens, Cost, and other supported values only; unavailable evidence stays unavailable. Before/after **session total** context is clearly separate from spend. Summary context already included in a call is never added again. Task and run totals retain known subtotals, complete-total availability, dispatch coverage, and reviewer separation instead of substituting session totals or summing snapshots. Raw metric schema keys, enum values, provenance, artifact paths, hashes, and routing IDs are not displayed. Coverage qualifies missing intervals and uncertain attribution. A selected Reader retains artifact identity, observed length and complete-prefix digest across HTTP requests/polls: append and incomplete-tail completion are allowed, while replacement, truncation or complete-prefix rewrite yields unavailable changed evidence without adopting a successor file. Unterminated JSON records never contribute intervals. Metric evidence status is separate from the reviewed code range and cannot change execution or review acceptance. Edge Details use semantic relation metadata rather than a rendered arrow label. Expand **Recorded history** to inspect ordinary-language typed events and unavailable-record notices without raw database payloads or identity dumps. **Load more history** and **Load correction history** retrieve further pages at their snapshot watermarks. Inventory counts disclose unloaded records. Changed watermarks require refresh rather than mixing snapshots.

Snapshot occurrence `execution_summary` is derived from the full normalized snapshot
before history paging. A worker or fixing-worker `returned` is green execution success;
its own established failure is red. Checks, checkpoints, questions and review acceptance
never recolor that worker. Outstanding input is waiting, not dependency-blocked; a
start-only agent is only *recorded running* with a compatible live recorded runner,
otherwise it is unknown/incomplete. Recorded running is not process liveness.
Interrupted, abandoned, or conflicting terminal evidence stays qualified unknown.
Terminal evidence beats stale waiting/running and attempts remain distinct. A reviewer
with typed `approved` and `finding_count` returned successfully even when it rejected
the work; that reviewer is green only for the recorded-return inference while Details
still show rejected acceptance. Malformed/transport reviewer failure does not imply
success.

Each run also exposes a separate full-snapshot `acceptance_summary`: checks,
checkpoints, reviewer approval/findings/ranges, and the existing full-range acceptance
qualification. These facts are retained independently of the loaded history page;
Details explicitly display `true`/`false` for approval and no-change (or `unknown`
when absent), including when the evidence is beyond the first 50 records. The
status legend distinguishes grey planned/pending calls, blue recorded-running calls,
green execution success, red execution failure, amber evidence-backed waiting/blocked,
and neutral qualified unknown/incomplete state. A green reviewer may still reject;
worker return is **not acceptance**.

For a complete retained descriptor, each public task also has pre-page `progress`,
`reason`, and `annotation` facts. Pending means no task work or impediment; running is
qualified; completion requires a successful focused checkpoint, never a worker return.
A task-scoped failed step is failed, while an unstarted dependent is blocked with its
public prerequisite reference. Outstanding input is a separate waiting annotation,
including task-scoped manual-gate questions before any worker starts. Each question
is resolved only by its own recorded answer or delivery failure; terminal task/parent
or run evidence takes precedence over stale requests. Task waiting labels and the
waiting count use full-snapshot evidence, not the loaded history page.
An independent task never started when the run stopped remains pending with **“Not
started; run stopped”**. Incomplete evidence stays qualified, and a later final-review
rejection does not erase an earlier checkpoint. Missing or partial plans expose no task
progress; `skipped` and `cancelled` are never synthesized. Reason/annotation references
are opaque public task or occurrence refs, not task prose.

Click a plan task, planned review definition, execution, or edge to highlight it and
update the visible Details panel next to the graph (below it on narrow screens). Plan
Details distinguish plain-language progress and current blocker from execution and acceptance.
Execution Details keep outcome, what happened, blocker and actionable recorded findings separate from acceptance. Edge Details use semantic relation metadata rather than a rendered arrow label. Every Details
selection retains the full acceptance summary—checks, checkpoints, review
approval/findings/ranges and current full-range qualification—separately from paged
loaded history. The legend makes this separation explicit; `skipped` and `cancelled`
are unsupported and never inferred. **Loaded history** exposes ordinary-language typed
observations and unsupported-record notices without raw database payloads, internal
identities, or raw metric fields. DTO construction still validates types and commit hashes,
and does not expose arbitrary payload/credential fields, runner identity internals or raw errors. **Load more history** and **Load correction
history** retrieve further pages at their snapshot watermarks. Inventory counts disclose
unloaded records. Changed watermarks require refresh rather than mixing snapshots.

The graph lays out stable planned slots and actual recorded calls using their measured DOM dimensions and ELK's layered top-to-bottom direction. Declared dependencies and valid recorded relations are ELK edges; there are no task/group footprints, parent-relative children, or inferred relations. The representative production browser fixture verifies rendered bounds and connectors for branches, a join, review/fix links and an essential stop. The initial view fits the activity graph. Selection, deliberate node dragging, pan and zoom survive status-only refreshes; a topology or content-size change may relayout without arbitrarily resetting the viewport. Because the viewport is controlled, its state is synchronized on every graph move, rather than only when a pan/drag ends. The rendered node projection retains node identity across viewport-only updates so ReactFlow keeps measured dimensions and handle bounds instead of temporarily hiding nodes or removing connectors during remeasurement. The closed snapshot API is polled every **60 seconds**; this is not a claim that polling alone caused previous slowness. The owner’s same-Mac interactive acceptance remains a separate pending manual gate. Stale old-run fetch/layout results are discarded. Read freshness, last successful read and last recorded activity remain separate. Failed reads retain sanitized evidence with a warning. Recorded runner `live`/`stopped`/`unknown` qualification is not proof of progress.

Only explicitly declared local correction relations expand the selected-root graph.
For a same-run recorded review chain, the graph shows only actually emitted reviewer/fixer nodes
and explicit trigger, predecessor, fixer-check, and fixer-checkpoint relations; it never derives
those links from labels, timestamps, or correction fields. Details show the selected execution's readable role, ordinal, outcome, safe findings, and qualification without exposing identity or provenance dumps. A review issue is shown only
when it matches the inert `path:line - issue` review form; raw reviewer payloads, arbitrary
findings, prompts, answers, errors, and secrets remain private. The original rejected reviewer and subsequent reviewer remain visible by their persisted execution
identities even if optional observation rows are absent. A fixing execution is shown only as a typed
round notice in Details/history: it is not an individual model call. Individual fixing calls appear
only when retained invocation history or an exact recorded invocation ID proves them; missing
observation/dispatch evidence remains unknown rather than inferred.
A valid rejecting reviewer remains a green returned execution while its rejection stays
visible in Details and lineage acceptance. Same-run acceptance identifies the explicit terminal reviewer and its recorded range, never temporal proximity. Missing/dangling chain links remain unknown. Correction-only, unresolved and cyclic
relations do not establish current full-range acceptance. Supporting
checks/checkpoints remain available in agent Details and paginated history.

The launcher binds only `127.0.0.1`; it has no host, reload, debug, proxy, database, or
asset-building overrides. Stop it with `Ctrl-C`; this closes observation only and leaves
Git, authoritative SQLite rows, and any writer untouched. It serves only the fixed startup asset inventory (not
sourcemaps, symlinks, directories, or arbitrary files). Rebuilding the active asset directory replaces hashed JS/CSS filenames but does not refresh that startup inventory: the HTML can load while its assets return JSON 404 responses and browser MIME errors. Finish the build before starting/restarting the monitor, or serve a separate copy of the built assets for a stable preview while another process rebuilds. Restart only the monitor, not the workflow worker or Pi session.

It exposes closed GET routes. Project and recording-qualified opaque references are the
only browser/API selectors; browser values never become paths. A direct run shell uses
`/projects/{project_ref}/runs/id-<percent-encoded qualified run ID>` and validates the
raw encoded component before serving only the fixed startup `index.html`. Unknown IDs,
malformed IDs, extra segments, APIs, and assets receive closed errors rather than an HTML
fallback. Responses expose no absolute path, Git-admin identity, private recording
payload, or raw exception.

- `/api/monitor/v1/projects`
- `/api/monitor/v1/projects/{project_ref}/runs`
- `/api/monitor/v1/projects/{project_ref}/runs/{run_ref}/snapshot`
- `/api/monitor/v1/projects/{project_ref}/runs/{run_ref}/history`
- `/api/monitor/v1/projects/{project_ref}/runs/{run_ref}/records/{record_ref}?snapshot=`
- `/api/monitor/v1/projects/{project_ref}/runs/{run_ref}/followups?snapshot=&cursor=&limit=`
- `/projects/{project_ref}/runs/id-<percent-encoded qualified run ID>`

Snapshots return an opaque `snapshot_ref` and `next_cursor`. History and record lookup require that snapshot reference; stale references return closed `409` responses, and invalid cursors or other-run record references are rejected. Followups are only explicitly declared local correction references. A reference resolves only when it names a recorded reviewer occurrence; dangling, conflicting, and cyclic declarations remain unresolved. Current acceptance requires an approving findings-free review recorded from the original base through the current linked head. A correction-only range is labelled honestly, and the original rejected run remains failed history.

API requests require the exact loopback `Host`, same-origin Fetch Metadata, and the
`X-Workflow-Monitor: 1` request header. All responses use no-store, CSP, nosniff,
no-referrer, and frame-denial protections; errors use fixed closed codes/messages.

Run the focused HTTP/launcher and production-web checks with prepared local dependencies:

```sh
workflow_monitor/.venv/bin/python -B -m unittest -v workflow_monitor.tests.test_http workflow_monitor.tests.test_launch workflow_monitor.tests.test_lineage workflow_monitor.tests.test_observation
npm --prefix workflow_monitor/web run build
npm --prefix workflow_monitor/web test  # includes reviewer→fixing-agent→rereviewer browser coverage
```

The browser test uses the already-installed local Chrome executable and does not download a browser. It serves the built assets and a closed local fixture API; it is not a same-run observer acceptance. SC-006 same-run retrospective/live observation remains **NOT VERIFIED** until separately authorized operator observation of genuine later application work.

When these checks are run by `scripts/coordinate-implementation`, use this same explicit
interpreter in task check commands. Setting `COHERENCE_PYTHON` selects the runner's own
Python; it does not change which `python3` a shell check resolves. No global Python
configuration changes are needed.

## Graph layout technical guidance

Local dependency evidence checked for readability planning (2026-10-21), not a
feature-completion claim: `web/package.json` declares ReactFlow `^12.8.5` and ELK
`^0.11.1`; `web/package-lock.json` resolves 12.12.0 and 0.11.1. Read-only inspection
of matching prepared package types found `@xyflow/system`'s
`dist/esm/types/nodes.d.ts` (`NodeBase`, lines 45–61) exposes dimensions, `parentId`
for sub-flows, parent extent and expansion. ELK's `lib/elk-api.d.ts` (`ElkShape`,
`ElkNode`, `ElkExtendedEdge`, lines 26–39 and 70–74) exposes dimensions, children
and explicit source/target IDs. These are local package API evidence, not a claim
that any particular nested-routing recipe has been tested or officially recommended.
Upstream source owners: [React Flow](https://github.com/xyflow/xyflow) and
[elkjs](https://github.com/kieler/elkjs); no remote documentation was consulted.

Repository-derived constraint for future graph changes: reuse these mechanisms,
keep semantic edge selection separate from layout input, and account for rendered
label/group dimensions rather than assuming every node fits the current fixed
180×70 ELK box. Parent/child coordinate conversion, containment and secondary-edge
routing still require a representative production-view check; type availability
alone proves none of them. Preserve stable IDs, status-only layout/viewport reuse
and stale-result guards. The [readability proposal](../docs/plans/workflow-monitor-readable-graph-tinyspec.md)
owns proposed behavior/acceptance; current behavior above is not changed by this note.
Verify prepared versions before future execution; this evidence grants no setup,
installation or application-build permission.

## Stopped-source capture preparation

The later explicit preservation command uses `capture_stopped(source_worktree, private_dir)`
to prepare (not publish) one monitor-only recording. The source must be a stopped, registered
linked worktree; the helper verifies its distinct registered main, takes the ordinary source
`coherence-workflow.lock` without constructing the runtime writer, and retains that lock until
the consumer has read the prepared files and the context exits. `private_dir` is a new
command-owned directory below `main/.coherence`, so it is not discoverable as completed history.
The returned capture exposes the verified main/origin identity, private `monitor.sqlite` and
`metrics/` paths, a content fingerprint/retained-facts summary, and `verify_unchanged()`.
Readback compares all retained SQLite facts (including unsupported observations/review inputs)
and exact metric hashes, not counts or presence alone. Exact-repeat identity depends on retained
content, not inode/timestamps or unrelated native tables.

The private SQLite retains monitor descriptors, ordered observations, review executions/attempts/
input checkpoints, and only Reader-consumed worker/fixer dispatch and metric-artifact history.
It retains original internal IDs/order and copies associated JSONL metric bytes exactly, including
partial or malformed tails; absent artifacts stay absent. It excludes runtime progress, run inputs,
other history/tables, SDK sessions and prompts. An unreadable existing metric, source replacement,
or drift fails with a retain-source correction rather than claiming deletion is safe. A successful
context exit performs a final source check before unlocking. This helper never publishes, overwrites a prior capture, or provides a CLI. Owner-approved
SQLite exception: it opens the stopped source with `mode=ro`, `query_only` and a read transaction
when WAL exists, allowing only ordinary source `-shm` coordination creation/modification.
When WAL is absent it uses an immutable read to avoid creating `-wal`; before/after identity
and byte checks reject drift. Database/WAL/metric bytes stay unchanged. No full runtime DB
or WAL is copied into preparation, including on failed projection. Mixed history retains only
Reader-consumed started-dispatch fields and metric-artifact fields, never returned repair blobs.

The reader opens short SQLite `mode=ro` snapshots for exactly one canonical Git
worktree and does not import or invoke the workflow writer. It never copies a database,
checkpoints WAL, signals a process, repairs recording gaps, or falls back to legacy history.

## Preserve a stopped linked worktree

With the source writer stopped, invoke the separately prepared command from any directory:

```sh
workflow-monitor-preserve --source-worktree /canonical/stopped-linked-worktree
```

The command verifies the registered distinct main, holds the source writer lock through
capture, pre-publication drift verification, preserved-Reader readback, and its final
context-exit drift check. It privately prepares only the monitor subset and exact metric
bytes, then publishes one complete recording below main's
`.coherence/preserved-recordings/`; pending preparation is never visible to a Reader.
Success reports preserved internal workflow identities, Reader metric qualifications, and
verified readback only after the final source check succeeds.

An exact unchanged repeat reopens and verifies the existing complete recording rather than
copying it again. A changed source with the same stopped-worktree origin is a mismatch:
the command retains both the prior capture and source and says to resolve that difference;
it never performs incremental sync or versioning. Publication never overwrites a target.
Interruption, unsafe storage, uncertain completion, source drift, or failed readback returns
an operation-specific correction and leaves newly prepared/published bytes for inspection.
It never deletes/prunes the source, resumes a workflow, modifies either live database/WAL,
metrics, Git index, or existing history (only the explicit `-shm` coordination exception above), and copied historical commitment/liveness facts are not new
main commits or live-run evidence.
