# Workflow monitor

`workflow_monitor` is a local, read-only presentation of recording-contract version 1
workflow snapshots. It imports no workflow writer, never creates or migrates a store,
and has no execution or control routes.

Install the exact dependencies from `requirements.lock` in a prepared isolated Python
environment; starting the viewer never installs or builds anything. From the repository
root, use the prepared interpreter explicitly so neither launch nor checks accidentally
use the system Python. With a fixed production asset directory containing `index.html`:

```sh
workflow_monitor/.venv/bin/python -m workflow_monitor --project /canonical/worktree --assets /path/to/production-assets --port 8765
```

The launcher binds only `127.0.0.1`; it has no host, reload, debug, proxy, database, or
asset-building overrides. It serves only the fixed startup asset inventory (not
sourcemaps, symlinks, directories, or arbitrary files) and exposes closed GET routes:

- `/api/monitor/v1/runs`
- `/api/monitor/v1/runs/{run_ref}/snapshot`
- `/api/monitor/v1/runs/{run_ref}/history`
- `/api/monitor/v1/runs/{run_ref}/records/{record_ref}`

`followups` is deliberately unavailable until its separately owned implementation.
API requests require the exact loopback `Host`, same-origin Fetch Metadata, and the
`X-Workflow-Monitor: 1` request header. All responses use no-store, CSP, nosniff,
no-referrer, and frame-denial protections; errors use fixed closed codes/messages.

Run the focused checks with the prepared environment:

```sh
workflow_monitor/.venv/bin/python -B -m unittest -v workflow_monitor.tests.test_http workflow_monitor.tests.test_launch
```

When these checks are run by `scripts/coordinate-implementation`, use this same explicit
interpreter in task check commands. Setting `COHERENCE_PYTHON` selects the runner's own
Python; it does not change which `python3` a shell check resolves. No global Python
configuration changes are needed.

The reader opens short SQLite `mode=ro` snapshots for exactly one canonical Git
worktree and does not import or invoke the workflow writer. It never copies a database,
checkpoints WAL, signals a process, or falls back to legacy history.
