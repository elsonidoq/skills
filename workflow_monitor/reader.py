"""Fixed-worktree, read-only snapshots of workflow monitoring records.

This module intentionally depends only on the standard library.  It never imports the
workflow writer and opens a fresh, short-lived SQLite connection for each snapshot.
"""
from __future__ import annotations

import os
from pathlib import Path
import sqlite3
import subprocess
import threading
from typing import Any


SUPPORTED_RECORDING_VERSION = 1
_SAFE_FINDING = __import__("re").compile(r"^[A-Za-z0-9_./-]+(?::[1-9][0-9]*)? - [^\r\n]+$")
_HASH = __import__("re").compile(r"^[0-9a-f]{40,64}$")
_DATABASE_PARTS = (".coherence", "workflow", "workflow.sqlite")
_GIT_ENV = (
    "GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_COMMON_DIR",
    "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES",
)


class ReaderError(RuntimeError):
    """A fixed reader binding is no longer safe to use."""


def _git(project: Path, argument: str) -> Path:
    if any(os.environ.get(name) for name in _GIT_ENV):
        raise ReaderError("ambient Git authority override")
    result = subprocess.run(
        ["git", "--no-optional-locks", "-C", str(project), "rev-parse", argument],
        capture_output=True,
        check=False,
    )
    if result.returncode:
        raise ReaderError("project is not a readable Git worktree")
    return Path(result.stdout.decode("utf-8", "strict").strip()).resolve(strict=True)


def _owned_regular(path: Path) -> os.stat_result:
    try:
        stat = path.lstat()
    except FileNotFoundError as exc:
        raise ReaderError("no_store") from exc
    if path.is_symlink() or not path.is_file() or stat.st_uid != os.geteuid() or stat.st_mode & 0o022:
        raise ReaderError("unsafe store ownership")
    return stat


def _owned_directory(path: Path) -> None:
    try:
        stat = path.lstat()
    except FileNotFoundError as exc:
        raise ReaderError("no_store") from exc
    if path.is_symlink() or not path.is_dir() or stat.st_uid != os.geteuid() or stat.st_mode & 0o022:
        raise ReaderError("unsafe store ownership")


class Reader:
    """Read only recording-contract v1 data from one canonical worktree.

    ``open_snapshot`` returns closed reader states rather than treating an absent or
    unsupported monitor store as legacy history.  The rows are a private boundary for
    the later mapper, not browser DTOs.
    """

    def __init__(self, project: str | os.PathLike[str]):
        self.project = Path(project).resolve(strict=True)
        if _git(self.project, "--show-toplevel") != self.project:
            raise ReaderError("project must be the Git worktree root")
        self._admin = _git(self.project, "--absolute-git-dir")
        _owned_regular(self._admin / "HEAD")
        self.database = self.project.joinpath(*_DATABASE_PARTS)
        self._database_identity: tuple[int, int] | None = None
        self._thread = threading.local()
        self._bind_if_present()

    def _bind_if_present(self) -> None:
        try:
            self._database_identity = self._check_binding()
        except ReaderError as exc:
            if str(exc) != "no_store":
                raise

    def _check_binding(self) -> tuple[int, int]:
        if _git(self.project, "--show-toplevel") != self.project or _git(self.project, "--absolute-git-dir") != self._admin:
            raise ReaderError("worktree identity changed")
        current = self.project
        for part in _DATABASE_PARTS[:-1]:
            current = current / part
            _owned_directory(current)
        if self.database.is_symlink():
            raise ReaderError("store path contains symlink")
        stat = _owned_regular(self.database)
        identity = (stat.st_dev, stat.st_ino)
        if self._database_identity is not None and identity != self._database_identity:
            raise ReaderError("database identity changed")
        return identity

    @staticmethod
    def _authorizer(action: int, arg1: str | None, arg2: str | None, database: str | None, source: str | None) -> int:
        return sqlite3.SQLITE_OK if action in (sqlite3.SQLITE_SELECT, sqlite3.SQLITE_READ) else sqlite3.SQLITE_DENY

    def open_snapshot(self, run_ref: str | None = None, cursor: int | None = None) -> dict[str, Any]:
        """Read a short consistent snapshot, closing it before returning.

        ``run_ref`` and ``cursor`` are bound parameters; unsupported recording versions
        remain visible as counts/state and are never guessed into version 1 rows.
        """
        if run_ref is not None and (not isinstance(run_ref, str) or not run_ref):
            return {"state": "unavailable", "code": "invalid_run"}
        if cursor is not None and (type(cursor) is not int or cursor < 0):
            return {"state": "unavailable", "code": "invalid_cursor"}
        try:
            self._database_identity = self._check_binding()
        except ReaderError as exc:
            code = str(exc)
            return {"state": "no_store" if code == "no_store" else "unavailable", "code": code}

        connection: sqlite3.Connection | None = None
        try:
            connection = sqlite3.connect(self.database.as_uri() + "?mode=ro", uri=True, isolation_level=None)
            connection.row_factory = sqlite3.Row
            connection.execute("PRAGMA query_only=ON")
            connection.execute("BEGIN")
            connection.set_authorizer(self._authorizer)
            tables = {row["name"] for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type=? AND name IN (?, ?, ?, ?)",
                ("table", "execution_monitor_runs", "execution_observations", "execution_review_executions", "execution_review_attempts"),
            )}
            if not {"execution_monitor_runs", "execution_observations"} <= tables:
                return {"state": "unavailable", "code": "monitor_schema_missing"}
            params: list[Any] = []
            where = ""
            if run_ref is not None:
                where = " WHERE run_id=?"
                params.append(run_ref)
            run_rows = [dict(row) for row in connection.execute(
                "SELECT run_id, recording_version, description, started_at, runner_identity "
                "FROM execution_monitor_runs" + where + " ORDER BY started_at, run_id", params)]
            supported = [row for row in run_rows if row["recording_version"] == SUPPORTED_RECORDING_VERSION]
            unsupported = [row["run_id"] for row in run_rows if row["recording_version"] != SUPPORTED_RECORDING_VERSION]
            if not supported:
                return {"state": "unsupported" if unsupported else "no_monitored_runs", "runs": [],
                        "unsupported_run_ids": unsupported, "observations": []}
            placeholders = ",".join("?" for _ in supported)
            observation_params: list[Any] = [row["run_id"] for row in supported]
            observation_where = "run_id IN (" + placeholders + ") AND recording_version=?"
            observation_params.append(SUPPORTED_RECORDING_VERSION)
            if cursor is not None:
                observation_where += " AND seq>?"
                observation_params.append(cursor)
            observations = [dict(row) for row in connection.execute(
                "SELECT seq, run_id, recording_version, occurrence_id, phase, task_id, kind, recorded_at, facts "
                "FROM execution_observations WHERE " + observation_where + " ORDER BY seq", observation_params)]
            review_details: list[dict[str, Any]] = []
            if {"execution_review_executions", "execution_review_attempts"} <= tables:
                for run in supported:
                    for execution in connection.execute(
                        "SELECT execution_id, role, review_ordinal, fixing_round, trigger_execution_id, "
                        "predecessor_execution_id, review_base, review_head FROM execution_review_executions "
                        "WHERE run_id=? ORDER BY dispatched_at, execution_id", (run["run_id"],)):
                        attempt = connection.execute(
                            "SELECT state, uncertainty, findings, reference_json FROM execution_review_attempts "
                            "WHERE run_id=? AND execution_id=? ORDER BY seq DESC LIMIT 1",
                            (run["run_id"], execution["execution_id"])).fetchone()
                        if attempt is None:
                            continue
                        try:
                            findings = __import__("json").loads(attempt["findings"]) if attempt["findings"] else []
                            references = __import__("json").loads(attempt["reference_json"])
                        except (TypeError, ValueError):
                            findings, references = [], {}
                        review_details.append({
                            "run_id": run["run_id"], "execution_id": execution["execution_id"],
                            "role": execution["role"], "review_ordinal": execution["review_ordinal"],
                            "fixing_round": execution["fixing_round"], "trigger_execution_id": execution["trigger_execution_id"],
                            "predecessor_execution_id": execution["predecessor_execution_id"],
                            "review_base": execution["review_base"], "review_head": execution["review_head"],
                            "outcome": attempt["state"], "uncertain": bool(attempt["uncertainty"]),
                            "findings": [item for item in findings if isinstance(item, str) and _SAFE_FINDING.fullmatch(item)],
                            "commit_refs": {key: value for key, value in references.items()
                                            if key in {"base", "head", "commit"} and isinstance(value, str) and _HASH.fullmatch(value)},
                        })
            return {"state": "ok", "runs": supported, "unsupported_run_ids": unsupported,
                    "observations": observations, "review_details": review_details}
        except (sqlite3.Error, OSError, ValueError):
            return {"state": "unavailable", "code": "read_failed"}
        finally:
            if connection is not None:
                connection.close()


__all__ = ["Reader", "ReaderError", "SUPPORTED_RECORDING_VERSION"]
