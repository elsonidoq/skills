# Workflow monitor reader

`workflow_monitor.reader.Reader` opens short, read-only SQLite snapshots for exactly one
canonical Git worktree. It reads only recording-contract version 1 rows from
`.coherence/workflow/workflow.sqlite`; it does not import or invoke the workflow writer.

The reader uses SQLite `mode=ro`, `query_only`, a SELECT/READ authorizer, parameterized
explicit-column queries, and normal SQLite locking. It never creates a database, copies a
database, checkpoints WAL, signals a process, or falls back to legacy history.

```python
from workflow_monitor.reader import Reader

snapshot = Reader("/canonical/worktree").open_snapshot()
```

Snapshots return `ok`, `no_store`, `no_monitored_runs`, `unsupported`, or `unavailable`.
The private rows returned at this boundary are for the later mapper, not public browser DTOs.
The reader binds the selected worktree's Git admin directory and database device/inode, and
rechecks them when reopening so symlink, ownership, worktree, and substitution changes are
not read.

Run the focused check without installing dependencies:

```sh
python3 -B -m unittest -v workflow_monitor.tests.test_reader
```
