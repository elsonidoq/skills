# Workflow monitor

`workflow_monitor` is a local, read-only presentation of recording-contract version 1
workflow snapshots. It imports no workflow writer, never creates or migrates a store,
and has no execution or control routes.

## Visual reference and UI change rule

The [workflow monitor mockup](../docs/workflow-monitor-mockup.html) is the durable,
authoritative **visual reference** for monitor UI changes. Its current design is
**proposed, not owner-approved**. It is not the current application, an implementation
specification, or evidence of recorded work. All displayed projects, run identifiers,
worktree names, tasks, relations and results are synthetic. Current application
behavior is documented below.

Owner direction for **all future monitor UI changes**: **modify this mockup first,
obtain explicit owner approval, then modify the monitor UI**. Copy the approved
markup structure and styling mechanically; do not independently reinterpret the
approved design in application code. Approval of a visual reference does not itself
authorize recording, API, privacy or runtime changes. This rule is monitor-specific;
it adds no global workflow policy. Provenance: the owner's minimal-change monitor
mockup request, including the explicit mockup-first approval and copy requirement.

Open `docs/workflow-monitor-mockup.html` directly in a local browser (`file://`); no
build, server, installation or monitor connection is needed. The initial view shows
eight sample nodes, branches and a join with all four colors. Select a task for its
short work description; Task 7 demonstrates unavailable retained text. Select an edge
for its relation meaning. Select **review-convergence-20261023 · curvy-skunk**,
**Run 1**, for a returned reviewer that requested changes, an interrupted corrective
call and a stopping step. The older preserved sample keeps its generated original
run identifier, with **Worktree name unavailable** and an unavailable plan. Select
**sample-docs** for an empty project. Filter, project/run
selection, drag-to-pan, node dragging, zoom, Fit, disclosures and Close work locally;
they do not call APIs. The graph uses the same ReactFlow engine as the monitor, bundled
in the HTML for offline viewing.

### Proposed visual changes and copy boundaries

- Keep the current system font, pale page, white panels, rounded nodes and top-to-bottom
  graph. Reduce the run rail from 17rem to 14rem. Replace repeated run metadata with
  one compact heading. The graph gets the full viewer width until a selection opens
  the 18rem Details panel; Close returns that space. Below 1000px Details stays below
  the graph; below 700px navigation stacks as in the current UI.
- Show **original run identifier + final worktree folder name**, for example the
  synthetic **review-convergence-20261024 · curvy-skunk**. The owner's later explicit
  **Show existing identifier + folder** answer resolves the earlier name ambiguity:
  use retained raw `run_id`, including generated IDs, not a separate human name or
  the recording-qualified routing ID. Do not show full absolute paths, including in
  disclosures or tooltips. Keep readable start context and existing compact qualifiers
  secondary; qualifier stability must not depend on filtering, paging or list position.
  The sample qualifiers are not a production numbering algorithm. Wrap identifiers,
  never clip or replace a retained generated ID with unavailable-name text. The heading
  uses `min-width: 0` and `overflow-wrap: anywhere` to retain long IDs on narrow screens;
  the rail already uses wrapping. Missing
  source basenames say **Worktree name unavailable**, including preserved recordings
  or a reader without a verified live binding. No naming subsystem or new persisted
  data is proposed.
- Use exactly four node color categories: **Not started**, **Running**, **Failed**,
  **Completed**. Waiting, blocked, interrupted, unknown and other exceptional states
  use the **same Failed color**, with their actual status stated in node text. Waiting
  never becomes Running. Green returned calls remain distinct from task checkpoint
  completion and successful acceptance. The rejected reviewer sample stays green
  with **Returned · changes requested**; neither its color nor worker return asserts
  acceptance. Preserve existing semantic evidence and its qualifications.
- Use one solid edge style for all relations. Keep every meaningful node, attempt,
  stop and relation; keep edge meaning in selected Details. This is a display change,
  not permission to prune topology or change recorded relation semantics.
- Keep the title/short retained task description, state, blocker and acceptance
  qualification visible in selection Details. Put metrics, checks and history in
  existing-style disclosures. Keep read errors, stale/unavailable warnings and
  material acceptance qualifications visible when applicable; the sample's neutral
  read metadata is collapsed, not an instruction to hide warnings.

The mockup's `style#monitor-visual-styles` is the proposed style source for
`web/src/style.css`; the marked copy boundary covers the shell, navigation, legend,
nodes, single edge style and Details. Use its HTML class structure in `web/src/main.tsx`.
Map the same four classes from existing semantic states in `web/src/graph.ts`; do not
replace semantic values with color names. Replace conflicting old node/edge styles
rather than layering a second palette over them. The same edge stroke also applies
to selected edges; selection Details carry their meaning.

Do **not** copy `style#mockup-only-styles`, synthetic fixtures, initial fixture
coordinates or local navigation handlers into production. Retain measured DOM
sizes, ELK layout, stable identities, viewport preservation, selection/fetch guards,
history paging and opaque routing. The 208px node width is a presentation starting
width, not a fixed clipping box. Production layout still measures content. The
proposal banner is reference-only, not application chrome.

**Preserved interaction boundary:** the readable
[mockup source](../docs/workflow-monitor-mockup.jsx) uses the actual ReactFlow engine,
not a pointer/scrollbar imitation. Its `SampleGraph` copies the current monitor's
controlled `viewport`, `onMove` updates, `onNodeDragStop` position retention, node/edge
selection, `minZoom={.15}`, `Background` and `Controls`. Keep those interactions in
future UI changes: dragging empty graph space pans; dragging a node moves that node
and its attached edges, with the engine's normal edge-of-viewport auto-pan preserved.
Selection/Close does not refit the graph or reset moved nodes. Opening Details can
narrow the visible canvas; use drag-to-pan or explicit Fit to see off-canvas nodes.
Initial fitting and the explicit Fit control remain available.

Inspection of the prepared locked ReactFlow defaults confirms `panOnDrag=true`,
`nodesDraggable=true`, scroll/pinch/double-click zoom enabled, and `panOnScroll=false`.
The application does not override them. The mockup retains these defaults, including
the existing Controls interaction toggle; do not remove graph or node dragging based
on this reference. The old scrollbar-only mockup behavior is replaced, not approved
as a production alternative. Fixture positions replace only the data/layout input;
this mockup does not exercise production ELK layout, polling or status-refresh logic.

### Rebuild the offline reference

The HTML contains generated ReactFlow CSS/JavaScript and bundled dependency license
notices. Edit its marked visual CSS/HTML and the readable
[`workflow-monitor-mockup.jsx`](../docs/workflow-monitor-mockup.jsx), then regenerate
with the small documentation-only
[`workflow-monitor-mockup-build.mjs`](../docs/workflow-monitor-mockup-build.mjs):

```sh
node docs/workflow-monitor-mockup-build.mjs
# Or use an already-prepared monitor dependency directory; no installation:
node docs/workflow-monitor-mockup-build.mjs /path/to/prepared/monitor/node_modules
```

The default uses `workflow_monitor/web/node_modules`. The builder uses esbuild from
the existing monitor toolchain and checks bundled package versions against
`workflow_monitor/web/package-lock.json`; it adds no dependency manifest or application
build step. Missing/mismatched prepared dependencies require a prepared matching
location, not automatic installation. Commit the regenerated HTML with source changes.
No external directory, server or network is needed to view the resulting HTML. Do not
edit the generated engine blocks by hand or copy them into the production application;
production continues to import its existing packages. Source maps and private build
paths are not retained. This does not grant owner approval of the design.

### Existing data and later implementation boundaries

- Current `Run`/`Recording` DTOs expose `main`/`linked`/`preserved`, opaque refs and
  the generic `Recorded run` label (`public.py:minimize`). The owner-selected display
  source is the existing original raw `run_id`, whether meaningful or generated.
  `runtime/coherence_workflow/cli.py:main` accepts `--run` or generates `uuid.uuid4().hex`.
  The proposed alignment uses that raw ID as the existing public `label`, before
  `app.py:_qualify_public` adds the recording hash to the separate `display_id`.
  Keep opaque refs and qualified routing IDs unchanged; do not parse them to invent
  labels. Descriptor version 3 has no separate run-name field and needs none for this
  choice. An old plan can lack task descriptions while its run ID remains available.
  This resolves the display-source question without new persistence; application
  mapping is still unimplemented by this mockup.
- Live `projects.py:Recording.worktree` already holds the registered worktree path
  internally, from which only its final folder name is needed for display. The current
  DTO does not expose that basename. Preserved recordings bind `worktree` to the main
  storage worktree; their `recording.json` retains opaque `recording_id`/`origin_id`,
  not the original worktree name (`recordings.py:PreservedBinding`). Do not label the
  storage folder as the original source worktree. Use **Worktree name unavailable**
  for preserved recordings or a reader without a verified live binding. Keep the
  no-absolute-path HTTP boundary and opaque API selectors unchanged;
  no absolute-path exception is needed or proposed.
- Supported descriptor version 3 retains `label` and explicit `outcome`/`description`
  as `work_description`. Generic/ID-only labels currently become `Recorded task` in
  `graph.ts:taskTitle`; the helper does not use `work_description`. Later work can
  display a short faithful excerpt of retained text with full text in Details. No
  model summary or new detail system is needed. Missing text must remain unavailable;
  never fetch current task files to invent historical text. Older descriptors may
  lack the whole supported plan, not just a title.
- Green in the current graph means a returned call, not accepted work. Keep task
  progress/checkpoints, reviewer verdict and full-range acceptance separate when
  mapping the four display colors. Do not infer new success from the simplified legend.

The [accepted decision index](../docs/decisions/index.md) was consulted. Applicable
[ADR-0003](../docs/decisions/ADR-0003-current-launch-authority-and-neutral-tasks.md)
keeps current scoped authority separate from historical approvals;
[ADR-0004](../docs/decisions/ADR-0004-shared-routine-worker-permissions.md) permits
bounded local checks without expanding product scope. Neither approves this design.
Older readability proposals retain their history; they do not authorize a redesign
or override the owner's current four-color, single-edge-style mockup direction.
Owner visual approval and later scoped planning/implementation approval remain pending.

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

## Merge source without merging runtime databases

Git merges source and committed metric artifacts, not live workflow databases. Keep
`.coherence/workflow/` and `.coherence/preserved-recordings/` ignored; ignore rules do not untrack
existing files. Do not resolve a runtime database conflict with Git's ours/theirs or a SQLite merge.

- **Linked worktree into main:** merge the source normally. If the owner wants completed monitor
  history retained, use the preservation command below while the stopped source worktree still
  exists. Verify its `readback: verified` result before relying on the recording. This is separate
  from source integration and does not import resumable execution state into main.
- **Main into a linked worktree:** merge source only. Leave both runtime databases independent;
  there is no reverse history transfer. Main's preserved recordings remain in main.

When a legacy branch tracks the database, removing it from tracking requires an authorized migration:
stop writers, preserve the local database and any SQLite sidecars outside merge-affected paths,
remove only Git tracking, then verify local bytes unchanged. Before an older branch receives that
removal commit, preserve its own stopped database/sidecars first: Git may delete a clean tracked
file during merge even when the new ignore rule covers it. After resolving source integration,
restore that branch's own bytes to the now-ignored location and verify them before restarting.
Do not copy main's database over the branch's database. Uncertain/live state stops this migration,
not authorization to kill a writer or discard data. Existing tracked historical session files are
not automatically removed by adding ignore rules.

Preservation is optional unless explicitly required. These instructions authorize neither merges,
shutdowns, database migration nor worktree deletion. Active workflow relocation is not supported by
this command. Worktree-removal readiness remains owned by `finish-session`.

## Preserve a stopped linked worktree

With the source writer stopped, invoke the separately prepared command from any directory:

```sh
workflow-monitor-preserve --source-worktree /canonical/stopped-linked-worktree
```

If the console entry point is not installed, the same command is available from a verified
Coherence checkout without installing packages. Set `COHERENCE_ROOT` to that checkout; it must
contain `workflow_monitor/` and `runtime/`. With a compatible Python interpreter:

```sh
PYTHONPATH="$COHERENCE_ROOT:$COHERENCE_ROOT/runtime" python3 -B -m workflow_monitor.preserve --help
PYTHONPATH="$COHERENCE_ROOT:$COHERENCE_ROOT/runtime" python3 -B -m workflow_monitor.preserve \
  --source-worktree /canonical/stopped-linked-worktree
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
