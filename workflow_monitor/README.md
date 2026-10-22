# Workflow monitor

`workflow_monitor` is a local, read-only presentation of recording-contract version 1
workflow snapshots. It imports no workflow writer, never creates or migrates a store,
and has no execution or control routes.

New recordings use descriptor version 3. Each task retains its label, declared
prerequisites, and the complete explicit `outcome`/`description` work text when supplied;
missing work text remains unknown. The descriptor also records explicit initial independent
review intent separately from generic review phase vocabulary. It never retains task objects,
prompts, answers, credentials, or arbitrary payloads. Closed public DTOs expose only these
fields, so a missing work text or review intent is not replaced from summaries or current
files.

Install the exact dependencies from `requirements.lock` in a prepared isolated Python
environment; starting the viewer never installs or builds anything. From the repository
root, use the prepared interpreter explicitly so neither launch nor checks accidentally
use the system Python. Build the local web assets first; this is an explicit preparation step, never viewer startup behavior:

```sh
npm --prefix workflow_monitor/web run build
workflow_monitor/.venv/bin/python -m workflow_monitor --project /canonical/worktree --assets "$PWD/workflow_monitor/web/dist" --port 8765
```

The package also declares the equivalent `workflow-monitor` console entry point for a
separately prepared local installation. It uses the same required `--project` and
`--assets` arguments; neither form installs dependencies, builds assets, or starts the
workflow runtime. Keep `requirements.lock` with the package metadata when preparing
that isolated environment. A missing build root, missing `index.html`, symlinked root,
or non-directory asset root stops before binding with a fixed actionable diagnostic;
rebuild to a regular local `dist/` directory and retry.

Then open `http://127.0.0.1:8765/` in a local browser. The left selector and persistent selected-run banner show the recorded run ID as inert text, so identically labelled runs remain distinguishable during loading or a read error. Opaque references still route API requests. The graph retains one stable planned worker slot for every known task and a separately planned final independent review, then reconciles each slot only with its unique exact recorded initial call. Later plans remain visible while earlier calls run. Corrective prompts and later reviews appear only when exact recorded evidence exists; fixing rounds are not fabricated as calls. Declared prerequisites (including planned review completion) are distinct from recorded causal/input relations. Missing, ambiguous, or cyclic relations remain qualified rather than guessed. Details lead with the recorded action, outcome, blocker and findings. Missing, malformed, partial or unsupported records remain unavailable or qualified rather than repaired into a completed graph.

The browser URL identifies a run by its actual displayed ID as `/runs/id-<percent-encoded ID>`; the client decodes that component once, looks it up exactly in the inventory, and only then uses the opaque API reference. A successful nonempty root inventory replaces `/` with its newest finite-epoch run (descending, deterministic ID ties; unknown times last). Different selections push history, repeated selections do not, and Back/Forward clears obsolete graph/Details work before loading the addressed run. Unknown, removed, or unavailable IDs remain in the address bar with an honest unavailable state rather than selecting a substitute. The run-ID filter is a case-insensitive local substring filter: it neither changes the selected URL/history nor sends a server search, and it explicitly reports selected-outside-filter and no-match states. Polling remains at 60 seconds and never steals the current selection for a newer row.

A confirmed internal step that stops a recorded failed run appears as a red node with its explicit recorded support relation. A failure before any agent starts remains visible without an invented agent. Recovered checks remain in Details/history, not extra graph nodes. Edges come only from explicit recorded input, correction, review/fix and stop facts; missing, ambiguous or cyclic relations remain qualified in Details and are not rendered.

Click an execution or edge to highlight it and update the visible Details panel next to the graph (below it on narrow screens). Execution Details keep outcome, what happened, blocker and actionable recorded findings separate from acceptance. Invocation Details also show only the selected invocation's typed JSONL metric interval: selected versus confirmed session opening, token/USD fields with availability, invocation scope/provenance, before/after **session-cumulative** counters/context/headroom/compaction facts, compaction references, and any summary usage/cost subset. A summary subset marked `already_included_do_not_add` is already in the SDK interval and is never added again. Missing/partial facts remain labelled unknown; session/reviewer totals are never represented as task spend. Details separate same-task dispatched-call token/USD totals from run worker/fixer and run reviewer usage, with recorded-interval, dispatch and distinct-task counts. Known subtotals remain visible when full totals are unavailable; snapshots and already-included summary subsets are never summed into spend. Coverage compares retained dispatch history (including reviewer dispatches) with JSONL intervals and qualifies unverified dispatch evidence, missing intervals and mismatched attribution. A selected Reader retains the artifact identity, observed length and complete-prefix digest across HTTP requests/polls: append and incomplete-tail completion are allowed, while replacement, truncation or complete-prefix rewrite yields unavailable changed evidence without adopting a successor file. Unterminated JSON records never contribute intervals. Metric artifact outcome, exact run artifact path and commit SHA are shown separately from the original reviewed code range; raw artifact errors/history are not public, and artifact failure does not change execution or review acceptance. Edge Details use semantic relation metadata rather than a rendered arrow label. Expand technical references to inspect full IDs, endpoints, qualifications, source references and retained history. **Loaded history and technical references** exposes loaded typed observations and unsupported records without raw database payloads. **Load more history** and **Load correction history** retrieve further pages at their snapshot watermarks. Inventory counts disclose unloaded records. Changed watermarks require refresh rather than mixing snapshots.

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
Execution Details keep outcome, what happened, blocker and actionable recorded findings separate from acceptance. Edge Details use semantic relation metadata rather than a rendered arrow label. Expand technical references to inspect full IDs, endpoints, qualifications, source references and retained history. Every Details
selection retains the full acceptance summary—checks, checkpoints, review
approval/findings/ranges and current full-range qualification—separately from paged
loaded history. The legend makes this separation explicit; `skipped` and `cancelled`
are unsupported and never inferred. **Loaded history and technical references** exposes
supporting definitions, every loaded typed observation (including parent identities, error categories and recording gaps) and unsupported record without
raw database payloads. Recorded workflow prose and identities are intentionally visible;
this is not a privacy filter. DTO construction still validates types and commit hashes,
and does not expose arbitrary payload/credential fields, runner identity internals or raw errors. **Load more history** and **Load correction
history** retrieve further pages at their snapshot watermarks. Inventory counts disclose
unloaded records. Changed watermarks require refresh rather than mixing snapshots.

The graph lays out stable planned slots and actual recorded calls using their measured DOM dimensions and ELK's layered top-to-bottom direction. Declared dependencies and valid recorded relations are ELK edges; there are no task/group footprints, parent-relative children, or inferred relations. The representative production browser fixture verifies rendered bounds and connectors for branches, a join, review/fix links and an essential stop. The initial view fits the activity graph. Selection, deliberate node dragging, pan and zoom survive status-only refreshes; a topology or content-size change may relayout without arbitrarily resetting the viewport. Because the viewport is controlled, its state is synchronized on every graph move, rather than only when a pan/drag ends. The rendered node projection retains node identity across viewport-only updates so ReactFlow keeps measured dimensions and handle bounds instead of temporarily hiding nodes or removing connectors during remeasurement. The closed snapshot API is polled every **60 seconds**; this is not a claim that polling alone caused previous slowness. The owner’s same-Mac interactive acceptance remains a separate pending manual gate. Stale old-run fetch/layout results are discarded. Read freshness, last successful read and last recorded activity remain separate. Failed reads retain sanitized evidence with a warning. Recorded runner `live`/`stopped`/`unknown` qualification is not proof of progress.

Only explicitly declared local correction relations expand the selected-root graph.
For a same-run recorded review chain, the graph shows only actually emitted reviewer/fixer nodes
and explicit trigger, predecessor, fixer-check, and fixer-checkpoint relations; it never derives
those links from labels, timestamps, or correction fields. Details show the selected execution's
ID, ordinal/outcome/range, explicit references, and SHA references. A review issue is shown only
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
asset-building overrides. Stopping it is the rollback: it closes observation only and leaves
Git, authoritative SQLite rows, and any writer untouched. It serves only the fixed startup asset inventory (not
sourcemaps, symlinks, directories, or arbitrary files). Rebuilding the active asset directory replaces hashed JS/CSS filenames but does not refresh that startup inventory: the HTML can load while its assets return JSON 404 responses and browser MIME errors. Finish the build before starting/restarting the monitor, or serve a separate copy of the built assets for a stable preview while another process rebuilds. Restart only the monitor, not the workflow worker or Pi session.

It exposes closed GET routes. A direct run shell uses `/runs/id-<percent-encoded actual run ID>`: the server validates one raw encoded component before routing can decode a slash, then serves only the fixed startup `index.html`. Unknown IDs are resolved by the client against its inventory; malformed IDs, extra path segments, APIs, and assets receive closed errors rather than an HTML fallback.

- `/runs/id-<percent-encoded actual run ID>`
- `/api/monitor/v1/runs`
- `/api/monitor/v1/runs/{run_ref}/snapshot`
- `/api/monitor/v1/runs/{run_ref}/history`
- `/api/monitor/v1/runs/{run_ref}/records/{record_ref}?snapshot=`
- `/api/monitor/v1/runs/{run_ref}/followups?snapshot=&cursor=&limit=`

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

The reader opens short SQLite `mode=ro` snapshots for exactly one canonical Git
worktree and does not import or invoke the workflow writer. It never copies a database,
checkpoints WAL, signals a process, repairs recording gaps, or falls back to legacy history.
