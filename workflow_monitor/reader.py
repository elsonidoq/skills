"""Fixed-worktree, read-only snapshots of workflow monitoring records.

This module intentionally depends only on the standard library.  It never imports the
workflow writer and opens a fresh, short-lived SQLite connection for each snapshot.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
import sqlite3
import stat
import subprocess
import threading
from typing import Any

from .recordings import PreservedBinding, RecordingError, bind


SUPPORTED_RECORDING_VERSION = 1
_SAFE_FINDING = __import__("re").compile(r"^[A-Za-z0-9_./-]+(?::[1-9][0-9]*)? - [^\r\n]+$")
_HASH = __import__("re").compile(r"^[0-9a-f]{40,64}$")
_DATABASE_PARTS = (".coherence", "workflow", "workflow.sqlite")
_METRIC_ROLES = frozenset({"worker", "corrective_worker", "fixing_worker", "reviewer"})
_METRIC_OUTCOMES = frozenset({"settled", "failed", "interrupted", "approved", "rejected"})
_METRIC_MODES = frozenset({"fresh", "reused_from_earlier_task", "continued_same_task", "unknown"})
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

    def __init__(self, project: str | os.PathLike[str], preserved_recording: str | None = None):
        self.project = Path(project).resolve(strict=True)
        if _git(self.project, "--show-toplevel") != self.project:
            raise ReaderError("project must be the Git worktree root")
        self._admin = _git(self.project, "--absolute-git-dir")
        _owned_regular(self._admin / "HEAD")
        try:
            self._preserved: PreservedBinding | None = bind(self.project, preserved_recording) if preserved_recording is not None else None
        except RecordingError as exc:
            raise ReaderError(str(exc)) from exc
        self.database = self._preserved.database if self._preserved else self.project.joinpath(*_DATABASE_PARTS)
        self._metrics = self._preserved.metrics if self._preserved else self.project / ".coherence" / "metrics"
        self._database_identity: tuple[int, int] | None = None
        self._thread = threading.local()
        self._metric_boundaries: dict[str, tuple[tuple[int, int], int, int, bytes]] = {}
        self._metric_lock = threading.Lock()
        self._bind_if_present()

    @classmethod
    def preserved(cls, main: str | os.PathLike[str], recording_id: str) -> "Reader":
        """Open one explicit complete preserved recording under verified ``main``."""
        return cls(main, preserved_recording=recording_id)

    @property
    def recording_identity(self) -> tuple[str, str] | None:
        """Opaque ``(recording_id, origin_id)`` for later recording-qualified routing."""
        if self._preserved is None:
            return None
        return self._preserved.recording_id, self._preserved.origin_id

    def _bind_if_present(self) -> None:
        try:
            self._database_identity = self._check_binding()
        except ReaderError as exc:
            if str(exc) != "no_store":
                raise

    def _check_binding(self) -> tuple[int, int]:
        if _git(self.project, "--show-toplevel") != self.project or _git(self.project, "--absolute-git-dir") != self._admin:
            raise ReaderError("worktree identity changed")
        if self._preserved is not None:
            try:
                self._preserved.check()
            except RecordingError as exc:
                raise ReaderError(str(exc)) from exc
        else:
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

    def _metric_file(self, run_id: str) -> Path:
        digest = hashlib.sha256(run_id.encode("utf-8")).hexdigest()
        return self._metrics / f"run-{digest}.jsonl"

    @staticmethod
    def _metric_record(value: object, run_id: str) -> dict[str, Any] | None:
        """Validate the T011 closed schema without admitting its arbitrary input JSON."""
        if not isinstance(value, dict) or set(value) != {"version", "run_id", "invocation_id", "task_id", "role", "outcome", "fixing_round", "review_ordinal", "interval", "before", "after", "selected_session_mode", "session_selection_reason", "actual_session_mode", "actual_session_id"}:
            return None
        if value.get("version") != 1 or value.get("run_id") != run_id or not isinstance(value.get("invocation_id"), str) or not value["invocation_id"]:
            return None
        if value.get("role") not in _METRIC_ROLES or value.get("outcome") not in _METRIC_OUTCOMES or value.get("selected_session_mode") not in _METRIC_MODES or value.get("actual_session_mode") not in _METRIC_MODES:
            return None
        if value.get("task_id") is not None and not isinstance(value["task_id"], str):
            return None
        if any(value.get(key) is not None and (type(value[key]) is not int or value[key] < 1) for key in ("fixing_round", "review_ordinal")):
            return None
        if any(value.get(key) is not None and (not isinstance(value[key], str) or not value[key]) for key in ("session_selection_reason", "actual_session_id")):
            return None
        interval = value.get("interval")
        if not isinstance(interval, dict) or set(interval) != {"session_id", "branch", "epoch", "outcome", "tokens", "total_tokens", "estimated_usd", "compactions", "summary_overhead"}:
            return None
        tokens = interval.get("tokens")
        if interval.get("outcome") not in {"settled", "failed", "interrupted"} or not isinstance(tokens, dict) or set(tokens) != {"input", "output", "cache_read", "cache_write"}:
            return None
        def field(item: object) -> bool:
            return isinstance(item, dict) and set(item) == {"value", "unknown_reason", "provenance"} and (item["value"] is None or (type(item["value"]) in (int, float) and math.isfinite(item["value"]) and item["value"] >= 0)) and (item["unknown_reason"] is None or isinstance(item["unknown_reason"], str)) and (item["provenance"] is None or isinstance(item["provenance"], str))
        if not all(field(item) for item in tokens.values()) or not field(interval.get("total_tokens")) or not field(interval.get("estimated_usd")):
            return None
        # The remaining nested fields are deliberately not projected, but their closed
        # top-level shapes must be present before this row can affect availability.
        if not isinstance(interval.get("compactions"), dict) or not isinstance(interval.get("summary_overhead"), dict):
            return None
        for snapshot in (value.get("before"), value.get("after")):
            if snapshot is not None and (not isinstance(snapshot, dict) or set(snapshot) != {"counters", "estimated_usd", "context", "compaction_entry_ids"}):
                return None
        return value

    def _read_metrics(self, run_ids: set[str], expected: dict[str, set[str]]) -> dict[str, dict[str, Any]]:
        result: dict[str, dict[str, Any]] = {}
        for run_id in run_ids:
            path = self._metric_file(run_id)
            try:
                # Keep one append-only boundary per selected Reader, across polls
                # and HTTP requests (not thread-local and not a second metric store).
                with self._metric_lock:
                    _owned_directory(path.parent.parent)
                    _owned_directory(path.parent)
                    info = path.lstat()
                    if path.is_symlink() or not stat.S_ISREG(info.st_mode):
                        raise ReaderError('unsafe metric artifact')
                    identity = (info.st_dev, info.st_ino)
                    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC)
                    try:
                        chunks = []
                        remaining = info.st_size
                        while remaining:
                            chunk = os.read(fd, min(remaining, 65536))
                            if not chunk:
                                break
                            chunks.append(chunk)
                            remaining -= len(chunk)
                        opened = os.fstat(fd)
                    finally:
                        os.close(fd)
                    current = path.lstat()
                    stamp = (info.st_dev, info.st_ino, info.st_size, info.st_ctime_ns)
                    if any(stamp != (value.st_dev, value.st_ino, value.st_size, value.st_ctime_ns) for value in (opened, current)) or remaining:
                        raise ReaderError('metric artifact changed during read')
                    data = b''.join(chunks)
                    prior = self._metric_boundaries.get(run_id)
                    if prior is not None:
                        prior_identity, observed_length, complete_length, digest = prior
                        if identity != prior_identity or len(data) < observed_length or hashlib.sha256(data[:complete_length]).digest() != digest:
                            raise ReaderError('metric_artifact_changed')
                    complete_length = data.rfind(b'\n') + 1
                    self._metric_boundaries[run_id] = (identity, len(data), complete_length, hashlib.sha256(data[:complete_length]).digest())
            except FileNotFoundError:
                result[run_id] = {"coverage": "unavailable", "reasons": ["metric_artifact_missing"], "records": []}
                continue
            except (OSError, ReaderError) as exc:
                reason = 'metric_artifact_changed' if str(exc) == 'metric_artifact_changed' else 'metric_artifact_unavailable'
                result[run_id] = {'coverage': 'unavailable', 'reasons': [reason], 'records': []}
                continue
            reasons: list[str] = []
            if data and not data.endswith(b"\n"):
                reasons.append("incomplete_tail")
                data = data[:data.rfind(b'\n') + 1]
            unique: dict[str, dict[str, Any]] = {}
            conflicted: set[str] = set()
            for line in data.splitlines():
                try:
                    record = self._metric_record(json.loads(line.decode("utf-8")), run_id)
                except (UnicodeDecodeError, ValueError):
                    record = None
                if record is None:
                    reasons.append("invalid_record")
                    continue
                invocation_id = record["invocation_id"]
                prior = unique.get(invocation_id)
                if prior is not None and prior != record:
                    reasons.append("conflicting_duplicate_invocation")
                    conflicted.add(invocation_id)
                    unique.pop(invocation_id, None)
                    continue
                if invocation_id not in conflicted:
                    unique[invocation_id] = record
            if expected.get(run_id, set()) - set(unique):
                reasons.append("missing_expected_invocations")
            result[run_id] = {"coverage": "complete" if not reasons else "partial", "reasons": sorted(set(reasons)), "records": list(unique.values())}
        return result

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
                "SELECT name FROM sqlite_master WHERE type=? AND name IN (?, ?, ?, ?, ?, ?)",
                ("table", "execution_monitor_runs", "execution_observations", "execution_review_executions", "execution_review_attempts", "execution_review_inputs", "execution_history"),
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
            if self._preserved is not None:
                # A copied identity is historical evidence, never a main-worktree runner.
                for row in run_rows:
                    row["runner_identity"] = None
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
                        for attempt in connection.execute(
                            "SELECT seq, state, uncertainty, findings, reference_json FROM execution_review_attempts "
                            "WHERE run_id=? AND execution_id=? ORDER BY seq",
                            (run["run_id"], execution["execution_id"])):
                            try:
                                findings = __import__("json").loads(attempt["findings"]) if attempt["findings"] else []
                                references = __import__("json").loads(attempt["reference_json"])
                            except (TypeError, ValueError):
                                findings, references = [], {}
                            inputs = None
                            if "execution_review_inputs" in tables:
                                row = connection.execute("SELECT input_checkpoints FROM execution_review_inputs WHERE run_id=? AND execution_id=?",
                                                         (run["run_id"], execution["execution_id"])).fetchone()
                                try:
                                    inputs = __import__("json").loads(row["input_checkpoints"]) if row else None
                                except (TypeError, ValueError):
                                    inputs = None
                            review_details.append({
                                "run_id": run["run_id"], "execution_id": execution["execution_id"], "attempt_seq": attempt["seq"],
                                "role": execution["role"], "review_ordinal": execution["review_ordinal"],
                                "fixing_round": execution["fixing_round"], "trigger_execution_id": execution["trigger_execution_id"],
                                "predecessor_execution_id": execution["predecessor_execution_id"], "input_checkpoints": inputs,
                                "review_base": execution["review_base"], "review_head": execution["review_head"],
                                "outcome": attempt["state"], "uncertain": bool(attempt["uncertainty"]),
                                "findings": [item for item in findings if isinstance(item, str) and _SAFE_FINDING.fullmatch(item)],
                                "commit_refs": {key: value for key, value in references.items()
                                                if key in {"base", "head", "commit"} and isinstance(value, str) and _HASH.fullmatch(value)},
                            })
            expected: dict[str, set[str]] = {}
            for row in observations:
                try:
                    facts = json.loads(row["facts"])
                except (TypeError, ValueError):
                    continue
                invocation_id = (facts.get('invocation_id') or (facts.get('execution_id') if facts.get('role') == 'reviewer' else None)) if isinstance(facts, dict) else None
                if isinstance(invocation_id, str) and invocation_id:
                    expected.setdefault(row["run_id"], set()).add(invocation_id)
            # Dispatch records are a separate source of exact call identity.  They
            # survive optional monitor-observation loss, but never invent an
            # individual fixer call from a fixing-round execution.
            dispatches: dict[str, dict[str, dict[str, Any]]] = {row['run_id']: {} for row in supported}
            artifacts = {}
            for run_id in dispatches:
                if 'execution_history' in tables:
                    for row in connection.execute(
                            "SELECT task_id, kind, state, details FROM execution_history WHERE run_id=? "
                            "AND kind IN ('worker_invocation','fixer_invocation','metric_artifact') ORDER BY seq", (run_id,)):
                        try:
                            detail = json.loads(row['details'])
                        except (TypeError, ValueError):
                            continue
                        if not isinstance(detail, dict):
                            continue
                        if row['kind'] == 'metric_artifact':
                            status = detail.get('status')
                            if status in {'not_created', 'failed', 'committed', 'committed_after_reported_error', 'no_content'}:
                                # History retains its original metric commitment path; the
                                # preserved physical location is deliberately not a main path.
                                expected_path = (Path('.coherence') / 'metrics' / self._metric_file(run_id).name).as_posix()
                                artifacts[run_id] = {'status': status,
                                    'path': expected_path if detail.get('path') == expected_path or detail.get('paths') == [expected_path] else None,
                                    'sha': detail.get('sha') if isinstance(detail.get('sha'), str) and _HASH.fullmatch(detail['sha']) else None}
                        elif row['state'] == 'started':
                            identity = detail.get('invocation_id')
                            if isinstance(identity, str) and identity:
                                dispatches[run_id][identity] = {'invocation_id': identity, 'task_id': row['task_id'],
                                    'role': 'fixing_worker' if row['kind'] == 'fixer_invocation' else (detail.get('role', 'worker') if detail.get('role', 'worker') in {'worker', 'fixing_worker'} else 'unknown'),
                                    'execution_id': detail.get('execution_id') if isinstance(detail.get('execution_id'), str) else None}
                if 'execution_review_executions' in tables:
                    for row in connection.execute("SELECT execution_id, review_ordinal, fixing_round, trigger_execution_id, predecessor_execution_id FROM execution_review_executions WHERE run_id=? AND role='reviewer'", (run_id,)):
                        dispatches[run_id][row['execution_id']] = {'invocation_id': row['execution_id'], 'task_id': None, 'role': 'reviewer',
                            'execution_id': row['execution_id'], 'review_ordinal': row['review_ordinal'], 'fixing_round': row['fixing_round'],
                            'trigger_execution_id': row['trigger_execution_id'], 'predecessor_execution_id': row['predecessor_execution_id']}
            observed_expected = {key: set(value) for key, value in expected.items()}
            for run_id, calls in dispatches.items():
                expected.setdefault(run_id, set()).update(calls)
            metrics = self._read_metrics({row['run_id'] for row in supported}, expected)
            for run_id, value in metrics.items():
                value['dispatches'] = list(dispatches[run_id].values())
                if not dispatches[run_id] or observed_expected.get(run_id, set()) - set(dispatches[run_id]):
                    value['reasons'] = sorted(set(value['reasons'] + ['dispatch_evidence_unverified']))
                    if value['coverage'] == 'complete':
                        value['coverage'] = 'partial'
            return {"state": "ok", "runs": supported, "unsupported_run_ids": unsupported,
                    "observations": observations, "review_details": review_details,
                    "dispatches": {run_id: list(calls.values()) for run_id, calls in dispatches.items()},
                    "metrics": metrics, "metric_artifacts": artifacts}
        except (sqlite3.Error, OSError, ValueError):
            return {"state": "unavailable", "code": "read_failed"}
        finally:
            if connection is not None:
                connection.close()


__all__ = ["Reader", "ReaderError", "SUPPORTED_RECORDING_VERSION"]
