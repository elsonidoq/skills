"""Private, stopped-worktree capture for a later preservation command.

This module deliberately prepares only the monitor subset.  It does not publish a
recording, construct the runtime writer, or modify either live database.
"""
from __future__ import annotations

from contextlib import AbstractContextManager
import fcntl
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import stat
import subprocess
from typing import Any

from .recordings import DATABASE_NAME, METRICS_DIRECTORY

_DATABASE_PARTS = (".coherence", "workflow", "workflow.sqlite")
_GIT_ENV = ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_COMMON_DIR",
            "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES")


class CaptureError(RuntimeError):
    """Stopped-source capture could not safely prepare a private recording."""


def _git(worktree: Path, argument: str) -> Path:
    if any(os.environ.get(name) for name in _GIT_ENV):
        raise CaptureError("capture cannot verify Git worktrees; unset ambient Git overrides and retry")
    result = subprocess.run(["git", "--no-optional-locks", "-C", str(worktree), "rev-parse", argument],
                            capture_output=True, check=False)
    if result.returncode:
        raise CaptureError("capture requires a readable registered Git worktree; restore it and retry")
    value = Path(result.stdout.decode("utf-8", "strict").strip())
    return (value if value.is_absolute() else worktree / value).resolve(strict=True)


def _regular(path: Path, operation: str) -> os.stat_result:
    try:
        value = path.lstat()
    except FileNotFoundError as exc:
        raise CaptureError(f"{operation}: required source file is absent; retain the source and retry") from exc
    if path.is_symlink() or not stat.S_ISREG(value.st_mode) or value.st_uid != os.geteuid() or value.st_mode & 0o022:
        raise CaptureError(f"{operation}: source file is unsafe or unreadable; restore safe ownership/permissions and retry")
    return value


def _read_bytes(path: Path, operation: str) -> bytes:
    before = _regular(path, operation)
    try:
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC)
        try:
            chunks: list[bytes] = []
            while True:
                piece = os.read(fd, 65536)
                if not piece:
                    break
                chunks.append(piece)
            opened = os.fstat(fd)
        finally:
            os.close(fd)
        after = _regular(path, operation)
    except OSError as exc:
        raise CaptureError(f"{operation}: cannot read source bytes; restore access and retry") from exc
    if (before.st_dev, before.st_ino, before.st_size, before.st_ctime_ns) != (opened.st_dev, opened.st_ino, opened.st_size, opened.st_ctime_ns) or \
       (before.st_dev, before.st_ino, before.st_size, before.st_ctime_ns) != (after.st_dev, after.st_ino, after.st_size, after.st_ctime_ns):
        raise CaptureError(f"{operation}: source changed during capture; stop its writer and retry")
    return b"".join(chunks)


def _digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _present(path: Path) -> bool:
    try:
        path.lstat()
        return True
    except FileNotFoundError:
        return False


def _safe_private_directory(main: Path, private_dir: Path) -> Path:
    proposed = private_dir.absolute()
    try:
        relative = proposed.relative_to(main)
    except ValueError as exc:
        raise CaptureError("preparation directory must be new and below verified main/.coherence; choose a private directory there") from exc
    if not relative.parts or relative.parts[0] != ".coherence" or any(part in (".", "..", "") for part in relative.parts):
        raise CaptureError("preparation directory must be new and below verified main/.coherence; choose a private directory there")
    current = main
    for part in relative.parts:
        current = current / part
        if current.exists() or current.is_symlink():
            try:
                info = current.lstat()
            except OSError as exc:
                raise CaptureError("preparation directory is unsafe; choose a new private directory") from exc
            if current.is_symlink() or not stat.S_ISDIR(info.st_mode) or info.st_uid != os.geteuid() or info.st_mode & 0o022:
                raise CaptureError("preparation directory is unsafe; choose a new private directory")
        else:
            if current != proposed:
                current.mkdir(mode=0o700)
    if proposed.exists() or proposed.is_symlink():
        raise CaptureError("preparation directory already exists; choose a new command-owned directory without overwriting it")
    try:
        proposed.mkdir(mode=0o700)
        (proposed / METRICS_DIRECTORY).mkdir(mode=0o700)
    except OSError as exc:
        raise CaptureError("cannot prepare private capture directory; restore main permissions and retry") from exc
    return proposed


def _schema(target: sqlite3.Connection) -> None:
    target.executescript("""
    CREATE TABLE execution_monitor_runs(run_id TEXT PRIMARY KEY, recording_version INTEGER NOT NULL, description TEXT NOT NULL, started_at REAL NOT NULL, runner_identity TEXT);
    CREATE TABLE execution_observations(seq INTEGER PRIMARY KEY AUTOINCREMENT, run_id TEXT NOT NULL, recording_version INTEGER NOT NULL, occurrence_id TEXT NOT NULL, phase TEXT NOT NULL, task_id TEXT, kind TEXT NOT NULL, recorded_at REAL NOT NULL, facts TEXT NOT NULL);
    CREATE TABLE execution_review_executions(run_id TEXT NOT NULL, execution_id TEXT NOT NULL, role TEXT NOT NULL, review_ordinal INTEGER, fixing_round INTEGER, trigger_execution_id TEXT, predecessor_execution_id TEXT, review_base TEXT NOT NULL, review_head TEXT NOT NULL, dispatched_at REAL NOT NULL, PRIMARY KEY(run_id, execution_id));
    CREATE TABLE execution_review_attempts(seq INTEGER PRIMARY KEY AUTOINCREMENT, run_id TEXT NOT NULL, execution_id TEXT NOT NULL, state TEXT NOT NULL, uncertainty INTEGER NOT NULL, findings TEXT, reference_json TEXT NOT NULL, recorded_at REAL NOT NULL);
    CREATE TABLE execution_review_inputs(run_id TEXT NOT NULL, execution_id TEXT NOT NULL, input_checkpoints TEXT NOT NULL, PRIMARY KEY(run_id, execution_id));
    CREATE TABLE execution_history(seq INTEGER PRIMARY KEY AUTOINCREMENT, run_id TEXT NOT NULL, task_id TEXT, kind TEXT NOT NULL, state TEXT NOT NULL, details TEXT NOT NULL, recorded_at REAL NOT NULL);
    """)


def _table_names(source: sqlite3.Connection) -> set[str]:
    return {row[0] for row in source.execute("SELECT name FROM sqlite_master WHERE type='table'")}


def _copy_monitor(source: sqlite3.Connection, target: sqlite3.Connection) -> list[str]:
    required = {"execution_monitor_runs", "execution_observations"}
    tables = _table_names(source)
    if not required <= tables:
        raise CaptureError("capture cannot find monitor recording tables; retain the source and use a compatible workflow store")
    runs = list(source.execute("SELECT run_id,recording_version,description,started_at,runner_identity FROM execution_monitor_runs ORDER BY started_at,run_id"))
    target.executemany("INSERT INTO execution_monitor_runs VALUES(?,?,?,?,?)", runs)
    run_ids = [row[0] for row in runs]
    if not run_ids:
        return run_ids
    marks = ",".join("?" for _ in run_ids)
    target.executemany("INSERT INTO execution_observations(seq,run_id,recording_version,occurrence_id,phase,task_id,kind,recorded_at,facts) VALUES(?,?,?,?,?,?,?,?,?)",
                       source.execute("SELECT seq,run_id,recording_version,occurrence_id,phase,task_id,kind,recorded_at,facts FROM execution_observations WHERE run_id IN (" + marks + ") ORDER BY seq", run_ids))
    copies = {
        "execution_review_executions": "INSERT INTO execution_review_executions VALUES(?,?,?,?,?,?,?,?,?,?)",
        "execution_review_attempts": "INSERT INTO execution_review_attempts(seq,run_id,execution_id,state,uncertainty,findings,reference_json,recorded_at) VALUES(?,?,?,?,?,?,?,?)",
        "execution_review_inputs": "INSERT INTO execution_review_inputs VALUES(?,?,?)",
    }
    selects = {
        "execution_review_executions": "SELECT run_id,execution_id,role,review_ordinal,fixing_round,trigger_execution_id,predecessor_execution_id,review_base,review_head,dispatched_at",
        "execution_review_attempts": "SELECT seq,run_id,execution_id,state,uncertainty,findings,reference_json,recorded_at",
        "execution_review_inputs": "SELECT run_id,execution_id,input_checkpoints",
    }
    for table, insert in copies.items():
        if table in tables:
            target.executemany(insert, source.execute(selects[table] + " FROM " + table + " WHERE run_id IN (" + marks + ") ORDER BY " + ("seq" if table == "execution_review_attempts" else "rowid"), run_ids))
    if "execution_history" in tables:
        for row in source.execute("SELECT seq,run_id,task_id,kind,state,details,recorded_at FROM execution_history WHERE run_id IN (" + marks + ") AND kind IN ('worker_invocation','fixer_invocation','metric_artifact') ORDER BY seq", run_ids):
            # Mixed-purpose history can contain repair blobs/session/private fields.
            # Reader consumes only started dispatch identities and artifact status.
            if row[3] != "metric_artifact" and row[4] != "started":
                continue
            try:
                detail = json.loads(row[5])
            except (ValueError, TypeError):
                detail = None
            keys = {"status", "path", "paths", "sha"} if row[3] == "metric_artifact" else {"invocation_id", "execution_id", "role"}
            safe = {key: value for key, value in detail.items() if key in keys and
                    (isinstance(value, str) or (key == "paths" and isinstance(value, list) and
                                               all(isinstance(path, str) for path in value)))} if isinstance(detail, dict) else None
            target.execute("INSERT INTO execution_history(seq,run_id,task_id,kind,state,details,recorded_at) VALUES(?,?,?,?,?,?,?)",
                           (*row[:5], json.dumps(safe, sort_keys=True, separators=(",", ":")), row[6]))
    return run_ids


class Capture(AbstractContextManager["Capture"]):
    """A private monitor-only preparation that keeps the stopped source lock held."""

    def __init__(self, source: Path, main: Path, origin_id: str, private_dir: Path, lock, fingerprint: dict[str, Any], summary: dict[str, Any]):
        self.source_worktree, self.main, self.origin_id = source, main, origin_id
        self.private_dir = private_dir
        self.database = private_dir / DATABASE_NAME
        self.metrics = private_dir / METRICS_DIRECTORY
        self.metric_paths = {name: self.metrics / name for name in fingerprint["metrics"]}
        self.fingerprint, self.summary, self._lock = fingerprint, summary, lock

    def verify_unchanged(self) -> None:
        current = _source_fingerprint(self.source_worktree, self.fingerprint["run_ids"])
        if current != self.fingerprint:
            raise CaptureError("source changed after capture; retain the source, stop its writer, and capture again before publication")

    def __exit__(self, exc_type, exc, traceback) -> bool:
        try:
            if exc_type is None:
                self.verify_unchanged()
        finally:
            self._lock.close()
        return False


def _source_fingerprint(source: Path, run_ids: list[str] | None = None) -> dict[str, Any]:
    for directory in (source / ".coherence", source / ".coherence" / "workflow", source / ".coherence" / "metrics"):
        if not _present(directory) and directory.name == "metrics":
            continue
        info = directory.lstat()
        if directory.is_symlink() or not stat.S_ISDIR(info.st_mode) or info.st_uid != os.geteuid() or info.st_mode & 0o022:
            raise CaptureError("capture source storage is unsafe; retain the source and restore owned non-symlink directories")
    database = source.joinpath(*_DATABASE_PARTS)
    values: dict[str, dict[str, Any] | None] = {}
    # ``-shm`` is SQLite reader coordination, not committed source content; opening a
    # read-only WAL snapshot may legitimately create or remove it.
    for name, path in [("database", database), ("database-wal", database.with_name(database.name + "-wal"))]:
        if _present(path):
            info = _regular(path, "capture database" if name == "database" else "capture database sidecar")
            values[name] = {"identity": (info.st_dev, info.st_ino, info.st_ctime_ns), "digest": _digest(_read_bytes(path, "capture database" if name == "database" else "capture database sidecar"))}
        else:
            values[name] = None
    metrics = source / ".coherence" / "metrics"
    metric_values: dict[str, dict[str, Any] | None] = {}
    for run_id in run_ids or []:
        name = "run-" + hashlib.sha256(run_id.encode("utf-8")).hexdigest() + ".jsonl"
        path = metrics / name
        if _present(path):
            info = _regular(path, "capture metric artifact")
            metric_values[name] = {"identity": (info.st_dev, info.st_ino, info.st_ctime_ns), "digest": _digest(_read_bytes(path, "capture metric artifact"))}
        else:
            metric_values[name] = None
    source_info = source.lstat()
    return {"source": str(source), "source_identity": (source_info.st_dev, source_info.st_ino, source_info.st_ctime_ns),
            "git": {"top": str(_git(source, "--show-toplevel")), "common": str(_git(source, "--git-common-dir")), "admin": str(_git(source, "--absolute-git-dir"))},
            "database": values, "metrics": metric_values, "run_ids": list(run_ids or [])}


def registered_main(source_worktree: str | os.PathLike[str]) -> Path:
    """Resolve the distinct main by registered Git admin identity, not directory shape."""
    try:
        source = Path(source_worktree).resolve(strict=True)
    except OSError as exc:
        raise CaptureError("capture source is unavailable; retain it and provide its registered worktree path") from exc
    if _git(source, "--show-toplevel") != source:
        raise CaptureError("capture source must be a Git worktree root; use its registered root")
    common, admin = _git(source, "--git-common-dir"), _git(source, "--absolute-git-dir")
    # Git's common dir is the admin directory of exactly one registered main worktree.
    result = subprocess.run(["git", "--no-optional-locks", "-C", str(source), "worktree", "list", "--porcelain", "-z"], capture_output=True, check=False)
    main: Path | None = None
    source_registered = False
    if result.returncode == 0:
        for field in result.stdout.decode("utf-8", "strict").split("\0"):
            if field.startswith("worktree "):
                candidate = Path(field[9:])
                try:
                    candidate = candidate.resolve(strict=True)
                    if _git(candidate, "--git-common-dir") != common:
                        continue
                    candidate_admin = _git(candidate, "--absolute-git-dir")
                    if candidate_admin == common:
                        main = candidate
                    if candidate == source and candidate_admin == admin:
                        source_registered = True
                except (OSError, CaptureError):
                    continue
    if not source_registered or main is None or main == source or admin == common:
        raise CaptureError("capture source must be a registered linked worktree distinct from its main; choose the stopped linked worktree")
    return main


def capture_stopped(source_worktree: str | os.PathLike[str], private_dir: str | os.PathLike[str]) -> Capture:
    """Prepare monitor facts below main; consumers retain this context through readback."""
    main = registered_main(source_worktree)
    source = Path(source_worktree).resolve(strict=True)
    common, admin = _git(source, "--git-common-dir"), _git(source, "--absolute-git-dir")
    _regular(admin / "HEAD", "capture Git registration")
    try:
        fd = os.open(admin / "coherence-workflow.lock", os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            lock = os.fdopen(fd, "r+")
        except BaseException:
            os.close(fd)
            raise
    except BlockingIOError as exc:
        raise CaptureError("source writer lock is busy; stop the writer and retry without signalling it") from exc
    except OSError as exc:
        raise CaptureError("cannot acquire source writer lock; restore source access and retry") from exc
    try:
        database = source.joinpath(*_DATABASE_PARTS)
        _regular(database, "capture database")
        before_database = _source_fingerprint(source)["database"]
        staged = _safe_private_directory(main, Path(private_dir))
        # Owner-approved exception: ordinary -shm coordination only. With a WAL
        # present, mode=ro reads its committed frames consistently. Without one,
        # immutable prevents SQLite from creating an empty -wal/-shm pair; the
        # before/after source checks reject a WAL appearing during that read.
        wal_present = before_database["database-wal"] is not None
        options = "?mode=ro" if wal_present else "?mode=ro&immutable=1"
        connection = sqlite3.connect(database.as_uri() + options, uri=True, isolation_level=None)
        try:
            connection.execute("PRAGMA query_only=ON")
            connection.execute("BEGIN")
            target = sqlite3.connect(staged / DATABASE_NAME)
            try:
                _schema(target)
                run_ids = _copy_monitor(connection, target)
                target.commit()
            finally:
                target.close()
            metrics = staged / METRICS_DIRECTORY
            before_metrics = _source_fingerprint(source, run_ids)["metrics"]
            for run_id in run_ids:
                name = "run-" + hashlib.sha256(run_id.encode("utf-8")).hexdigest() + ".jsonl"
                source_metric = source / ".coherence" / "metrics" / name
                if _present(source_metric):
                    (metrics / name).write_bytes(_read_bytes(source_metric, "capture metric artifact"))
            fingerprint = _source_fingerprint(source, run_ids)
            if fingerprint["metrics"] != before_metrics:
                raise CaptureError("metric changed during capture; retain the source, stop its writer and retry")
            for name, value in fingerprint["metrics"].items():
                copied = metrics / name
                if (value is None and copied.exists()) or (value is not None and
                        (not copied.exists() or _digest(_read_bytes(copied, "verify copied metric")) != value["digest"])):
                    raise CaptureError("metric changed during capture; retain the source, stop its writer and retry")
            if {key: fingerprint["database"][key] for key in ("database", "database-wal")} != before_database:
                raise CaptureError("source database changed during capture; stop its writer and retry before publication")
        finally:
            connection.close()
        origin_id = hashlib.sha256((str(common) + "\0" + str(admin)).encode()).hexdigest()[:32]
        summary = {"runs": len(run_ids), "observations": _count(staged / DATABASE_NAME, "execution_observations"),
                   "facts_sha256": retained_digest(staged / DATABASE_NAME),
                   "metrics": {name: ({"availability": "copied_unqualified", "sha256": value["digest"]} if value is not None else {"availability": "absent", "sha256": None}) for name, value in fingerprint["metrics"].items()},
                   "retained": ("monitor descriptors", "ordered observations", "review executions/attempts/input checkpoints", "typed dispatch and metric-artifact history"),
                   "excluded": ("execution_run_inputs", "runnable progress", "unrelated tables", "SDK sessions/private prompts")}
        return Capture(source, main, origin_id, staged, lock, fingerprint, summary)
    except (OSError, sqlite3.Error) as exc:
        lock.close()
        raise CaptureError("capture monitor projection failed; retain the source, restore readable compatible storage and retry") from exc
    except BaseException:
        lock.close()
        raise


def retained_digest(database: Path) -> str:
    """Compare all retained facts, including unsupported rows, without source paths."""
    tables = ("execution_monitor_runs", "execution_observations", "execution_review_executions",
              "execution_review_attempts", "execution_review_inputs", "execution_history")
    with sqlite3.connect(database.as_uri() + "?mode=ro&immutable=1", uri=True) as connection:
        facts = {table: connection.execute("SELECT * FROM " + table + " ORDER BY rowid").fetchall()
                 for table in tables}
    return _digest(json.dumps(facts, sort_keys=True, separators=(",", ":")).encode("utf-8"))


def _count(database: Path, table: str) -> int:
    with sqlite3.connect(database) as connection:
        return int(connection.execute("SELECT count(*) FROM " + table).fetchone()[0])


__all__ = ["Capture", "CaptureError", "capture_stopped"]
