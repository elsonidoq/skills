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

Then open `http://127.0.0.1:8765/` in a local browser. The React/React Flow view has a left recorded-run selector, one selected-run graph, brief node/edge details, typed-edge legend, and pan/zoom controls. It uses local ELK layout and polls the closed snapshot API about every two seconds. Status-only polls preserve node IDs, selection, positions, and viewport; topology changes are laid out locally. Stale fetch and layout completions from an old selected run are discarded. The initial API snapshot is a bounded first history page. Use **Load more history** to reveal the next page at the same snapshot watermark; an expired or changed watermark refreshes instead of mixing pages. The inventory reports total, loaded, hidden, and unsupported records, while collapsed failure and waiting badges remain discoverable.

The launcher binds only `127.0.0.1`; it has no host, reload, debug, proxy, database, or
asset-building overrides. It serves only the fixed startup asset inventory (not
sourcemaps, symlinks, directories, or arbitrary files) and exposes closed GET routes:

- `/api/monitor/v1/runs`
- `/api/monitor/v1/runs/{run_ref}/snapshot`
- `/api/monitor/v1/runs/{run_ref}/history`
- `/api/monitor/v1/runs/{run_ref}/records/{record_ref}?snapshot=`

Snapshots return an opaque `snapshot_ref` and `next_cursor`. History and record lookup require that snapshot reference; stale references return closed `409` responses, and invalid cursors or other-run record references are rejected.

`followups` is deliberately unavailable until its separately owned implementation.
API requests require the exact loopback `Host`, same-origin Fetch Metadata, and the
`X-Workflow-Monitor: 1` request header. All responses use no-store, CSP, nosniff,
no-referrer, and frame-denial protections; errors use fixed closed codes/messages.

Run the focused HTTP/launcher and production-web checks with prepared local dependencies:

```sh
workflow_monitor/.venv/bin/python -B -m unittest -v workflow_monitor.tests.test_http workflow_monitor.tests.test_launch
npm --prefix workflow_monitor/web run build
npm --prefix workflow_monitor/web test
```

The browser test uses the already-installed local Chrome executable and does not download a browser. It serves the built assets and a closed local fixture API; it is not a same-run observer acceptance. SC-006 same-run retrospective/live observation remains **NOT VERIFIED** until separately authorized operator observation of genuine later application work.

When these checks are run by `scripts/coordinate-implementation`, use this same explicit
interpreter in task check commands. Setting `COHERENCE_PYTHON` selects the runner's own
Python; it does not change which `python3` a shell check resolves. No global Python
configuration changes are needed.

The reader opens short SQLite `mode=ro` snapshots for exactly one canonical Git
worktree and does not import or invoke the workflow writer. It never copies a database,
checkpoints WAL, signals a process, or falls back to legacy history.
