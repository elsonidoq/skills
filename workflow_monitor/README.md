# Workflow monitor

`workflow_monitor` is a local, read-only presentation of recording-contract version 1
workflow snapshots. It imports no workflow writer, never creates or migrates a store,
and has no execution or control routes.

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

Then open `http://127.0.0.1:8765/` in a local browser. The left selector chooses one
recorded run. The compact graph shows actual implementation, review, fixing and rereview
executions, not phase/task definitions or separate start/return/checkpoint events. Each
call remains distinct. Short labels use recorded roles and public task presentation;
a global review is simply **Review**. Missing public task labels remain generic, never
guessed from private task IDs.

A confirmed internal step that stops a recorded failed run appears as a red node after
its recorded parent or preceding agent in that run/task scope. A failure before any
agent starts remains visible without an invented agent. Recovered check observations
remain in Details/history, not extra stopping nodes. Sequence edges mean recorded order,
not proven causality. The status legend distinguishes green success, red failure, amber
waiting and neutral recorded/incomplete/unknown. Worker return is **not acceptance**.

Click a node or edge to highlight it and update the visible Details panel next to the
graph (below it on narrow screens). Agent Details include loaded lifecycle/check/
checkpoint evidence, source references and recorded review ranges. **Loaded history and
technical references** exposes supporting definitions, every loaded minimized observation
and unsupported record without raw payloads. **Load more history** and **Load correction
history** retrieve further pages at their snapshot watermarks. Inventory counts disclose
unloaded records. Changed watermarks require refresh rather than mixing snapshots.

The graph fits locally with ELK layout and has pan/zoom controls. The closed snapshot API
is polled every **60 seconds**; this is not a claim that polling alone caused previous
slowness. Status-only refreshes preserve selection, positions and viewport; stale old-run
fetch/layout results are discarded. Read freshness, last successful read and last recorded
activity remain separate. Failed reads retain sanitized evidence with a warning. Recorded
runner `live`/`stopped`/`unknown` qualification is not proof of progress.

Only explicitly declared local correction relations expand the selected-root graph.
The original rejected reviewer, distinct fixing calls and subsequent reviewer remain
visible; source-run refs and actual ranges are in Details rather than repeated in labels.
The original rejection stays red after a later full-range success. Correction-only,
unresolved and cyclic relations do not establish current full-range acceptance. Supporting
checks/checkpoints remain available in agent Details and paginated history.

The launcher binds only `127.0.0.1`; it has no host, reload, debug, proxy, database, or
asset-building overrides. Stopping it is the rollback: it closes observation only and leaves
Git, authoritative SQLite rows, and any writer untouched. It serves only the fixed startup asset inventory (not
sourcemaps, symlinks, directories, or arbitrary files) and exposes closed GET routes:

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

The reader opens short SQLite `mode=ro` snapshots for exactly one canonical Git
worktree and does not import or invoke the workflow writer. It never copies a database,
checkpoints WAL, signals a process, repairs recording gaps, or falls back to legacy history.
