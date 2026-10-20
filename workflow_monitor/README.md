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

Then open `http://127.0.0.1:8765/` in a local browser. The React/React Flow view has a left recorded-run selector, one selected-run graph, brief node/edge details, typed-edge legend, and pan/zoom controls. It uses local ELK layout and polls the closed snapshot API about every two seconds. Status-only polls preserve node IDs, selection, positions, and viewport; topology changes are laid out locally. Stale fetch and layout completions from an old selected run are discarded. The view displays the current read time, last successful read, and last recorded activity separately. A failed read retains the last sanitized graph with a recoverable unavailable warning; the next successful read replaces it. The selected run also reports a read-only recorded-process qualification (`live`, `stopped`, or `unknown`): process presence is not progress, and missing ends remain incomplete. The initial API snapshot is a bounded first history page. Use **Load more history** to reveal the next page at the same snapshot watermark; an expired or changed watermark refreshes instead of mixing pages. The inventory reports total, loaded, hidden, and unsupported records, while collapsed failure and waiting badges remain discoverable.

The selected-root graph expands only explicitly declared local followups. A resolved relation links the original reviewer to the distinct fixing-worker execution and its checks, checkpoint, and rereviewer; every expanded node carries its opaque source-run ref. Review detail shows its recorded base→head range. The original rejected run remains failed even when a later full-original-range review succeeds. Correction-only, unresolved, conflicting, or cyclic relations are shown as such and never display a current accepted head. Collapsed history still reports failures and inventory retains hidden/unsupported records for reveal.

The launcher binds only `127.0.0.1`; it has no host, reload, debug, proxy, database, or
asset-building overrides. It serves only the fixed startup asset inventory (not
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
