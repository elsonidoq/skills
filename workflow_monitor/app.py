"""Closed, loopback-only HTTP presentation for workflow monitor snapshots."""
from __future__ import annotations

import copy
import hashlib
import json
import mimetypes
import os
from pathlib import Path
import stat
import time
from typing import Any, Protocol
from urllib.parse import unquote_to_bytes

from starlette.applications import Starlette
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Route

from .liveness import qualify
from .mapping import normalize
from .public import _ref, minimize, run_ref

_CSP = "default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; worker-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'"
_ASSET_SUFFIXES = frozenset({".css", ".gif", ".html", ".ico", ".jpeg", ".jpg", ".js", ".png", ".svg", ".webp", ".woff", ".woff2"})
_DEFAULT_PAGE_SIZE = 50


class SnapshotReader(Protocol):
    def open_snapshot(self, run_ref: str | None = None, cursor: int | None = None) -> dict[str, Any]: ...


def _error(code: str, status: int, retryable: bool = False) -> JSONResponse:
    messages = {
        "bad_request": "The request is not valid.", "not_found": "The requested monitor record was not found.",
        "snapshot_conflict": "Refresh the monitor snapshot and try again.", "unsupported": "The monitor data is unsupported.",
        "unavailable": "The monitor data is unavailable.", "internal": "The monitor service could not complete the request.",
    }
    return JSONResponse({"code": code, "public_message": messages[code], "retryable": retryable,
                         "observation": "unknown"}, status_code=status)


def _state_response(data: dict[str, Any]) -> JSONResponse | None:
    state = data.get("state")
    if state == "ok":
        return None
    if state == "unsupported":
        return _error("unsupported", 422)
    return _error("unavailable", 503, retryable=True)


def _assets(root: str | Path) -> tuple[int, dict[str, tuple[str, ...]]]:
    root = Path(root)
    try:
        if root.is_symlink() or (root.exists() and not root.is_dir()):
            raise ValueError("assets must be a regular directory")
        if not root.exists():
            raise ValueError("assets directory is missing or unreadable")
        root = root.resolve(strict=True)
        root_fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC)
    except OSError as exc:
        raise ValueError("assets directory is missing or unreadable") from exc
    files: dict[str, tuple[str, ...]] = {}
    for candidate in root.rglob("*"):
        if not candidate.is_file():
            continue
        relative = candidate.relative_to(root)
        if (candidate.is_symlink() or candidate.suffix not in _ASSET_SUFFIXES or
                any(part.startswith(".") for part in relative.parts)):
            continue
        files["/" + relative.as_posix()] = relative.parts
    if "/index.html" not in files:
        os.close(root_fd)
        raise ValueError("assets must contain index.html")
    return root_fd, files


def _encoded_run_id(raw_path: bytes) -> bool:
    """Accept only the one raw URL component used by the run shell route."""
    prefix = b"/runs/id-"
    if not raw_path.startswith(prefix):
        return False
    component = raw_path[len(prefix):]
    if not component or b"/" in component:
        return False
    safe = b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_.!~*'()"
    index = 0
    while index < len(component):
        byte = component[index]
        if byte in safe:
            index += 1
            continue
        if byte != ord("%") or index + 2 >= len(component) or any(
                digit not in b"0123456789abcdefABCDEF" for digit in component[index + 1:index + 3]):
            return False
        index += 3
    try:
        unquote_to_bytes(component).decode("utf-8")
    except UnicodeDecodeError:
        return False
    return True


def _read_asset(root_fd: int, parts: tuple[str, ...]) -> bytes:
    """Open an inventoried regular asset below its pinned directory descriptor."""
    directory_fd = os.dup(root_fd)
    try:
        for part in parts[:-1]:
            next_fd = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC,
                              dir_fd=directory_fd)
            os.close(directory_fd)
            directory_fd = next_fd
        asset_fd = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=directory_fd)
        try:
            size = os.fstat(asset_fd).st_size
            if not stat.S_ISREG(os.fstat(asset_fd).st_mode):
                raise OSError("asset is not regular")
            chunks: list[bytes] = []
            remaining = size
            while remaining:
                chunk = os.read(asset_fd, remaining)
                if not chunk:
                    raise OSError("asset changed while reading")
                chunks.append(chunk)
                remaining -= len(chunk)
            return b"".join(chunks)
        finally:
            os.close(asset_fd)
    finally:
        os.close(directory_fd)


def _asset_response(assets_fd: int, fixed_assets: dict[str, tuple[str, ...]], path: str) -> Response:
    asset = fixed_assets.get(path)
    if asset is None:
        return _error("not_found", 404)
    try:
        content = _read_asset(assets_fd, asset)
    except OSError:
        return _error("not_found", 404)
    return Response(content, media_type=mimetypes.guess_type(path)[0] or "application/octet-stream")


def _token(run_ref: str, records: list[dict[str, Any]], unknown: list[dict[str, Any]]) -> str:
    retained = records + unknown
    watermark = max((item.get("source_seq", -1) for item in retained if type(item.get("source_seq")) is int), default=-1)
    # Null source sequences are retained unknown records too, so include their opaque
    # identities rather than letting a stable numeric watermark conceal their arrival.
    null_refs = sorted(item["ref"] for item in retained if type(item.get("source_seq")) is not int)
    return "snapshot_" + hashlib.sha256(f"{run_ref}:{watermark}:{','.join(null_refs)}".encode()).hexdigest()[:24]


def _cursor(value: str | None) -> int | str | None:
    if value is None:
        return -1
    if value.startswith("cursor_") and value[7:].isdigit():
        return int(value[7:])
    if value.startswith("cursor_") and (value[7:].startswith("unknown_") or ".unknown_" in value[7:]):
        return value[7:]
    return None


def _page_size(value: str | None) -> int | None:
    if value is None:
        return _DEFAULT_PAGE_SIZE
    return int(value) if value.isdigit() and int(value) > 0 else None


def _page(data: dict[str, Any], reference: str, after: int | str, size: int) -> dict[str, Any]:
    records = [item for item in data["records"] if item["run_ref"] == reference]
    unknown = [item for item in data["unknown_records"] if item["run_ref"] == reference]
    retained = sorted(records + unknown, key=lambda item: (type(item.get("source_seq")) is not int,
                                                            item.get("source_seq") if type(item.get("source_seq")) is int else item["ref"]))
    if after == -1:
        start = 0
    elif isinstance(after, int):
        matches = [index for index, item in enumerate(retained) if item.get("source_seq") == after]
        if not matches:
            raise ValueError("cursor")
        start = matches[-1] + 1
    else:
        matches = [index for index, item in enumerate(retained) if item.get("source_seq") is None and item["ref"] == after]
        if not matches:
            raise ValueError("cursor")
        start = matches[0] + 1
    visible = retained[start:start + size]
    visible_records = [item for item in visible if item in records]
    visible_unknown = [item for item in visible if item in unknown]
    next_cursor = None
    if start + len(visible) < len(retained):
        last = visible[-1]
        next_cursor = "cursor_" + str(last["source_seq"]) if type(last.get("source_seq")) is int else "cursor_" + last["ref"]
    # Keep the run selector, but never return another run's graph as part of this
    # selected-root snapshot. Explicit correction expansion uses its own endpoint.
    result = dict(data)
    for key in ("phases", "tasks", "occurrences", "edges", "activities"):
        result[key] = [item for item in data.get(key, []) if item["run_ref"] == reference]
    for key in ("chain", "fixing_rounds", "review_definitions"):
        result[key] = [item for item in data.get(key, []) if item["run_ref"] == reference]
    for key in ('chain_acceptance', 'metric_coverage', 'metric_aggregates', 'metric_artifacts'):
        result[key] = {run_ref: value for run_ref, value in data.get(key, {}).items() if run_ref == reference}
    result["followups"] = [item for item in data.get("followups", [])
                           if item["run_ref"] == reference or item["source_run_ref"] == reference]
    result["records"] = visible_records
    result["unknown_records"] = visible_unknown
    inventory = dict(data["inventory"])
    inventory.update({"phase_count": len(result["phases"]), "occurrence_count": len(result["occurrences"]),
                      "observation_count": len(records), "total_count": len(retained), "loaded_count": len(visible),
                      "hidden_count": len(retained) - len(visible), "unsupported_count": len(unknown)})
    result["inventory"] = inventory
    result["snapshot_ref"] = _token(reference, records, unknown)
    result["next_cursor"] = next_cursor
    return result


def _outstanding_question(row: dict[str, Any]) -> bool:
    latest = next((item["kind"] for item in reversed(row["observations"])
                   if item["kind"] in {"question_requested", "answer_returned", "answer_sent", "delivery_failed"}), None)
    return latest == "question_requested"


def _task_progress(graph: dict[str, Any], public: dict[str, Any]) -> None:
    """Attach closed descriptor-task facts using the complete, unpaged snapshot."""
    occurrence_rows = {(row["run_id"], row["occurrence_id"]): row for row in graph.get("occurrences", [])}
    occurrences = {item["ref"]: item for item in public["occurrences"]}
    runs = {item["ref"]: item for item in public["runs"]}

    for task in public["tasks"]:
        run = runs[task["run_ref"]]
        task_rows = [row for (run_id, _), row in occurrence_rows.items()
                     if run_id == run["display_id"] and row.get("task_id") is not None]
        raw_id = task["task_id"]
        rows = [row for row in task_rows if row["task_id"] == raw_id]
        decisive = []
        for row in rows:
            outcome = next((item["kind"] for item in reversed(row["observations"])
                            if item["kind"] in {"passed", "failed", "interrupted", "abandoned"}), None)
            if row["phase"] == "checkpoint" and outcome == "passed":
                decisive.append((row["observations"][-1]["seq"], "completed", row))
            elif outcome == "failed":
                decisive.append((row["observations"][-1]["seq"], "blocked" if any(
                    item["facts"].get("error_category") == "blocked" for item in row["observations"]) else "failed", row))
        task["progress"] = {"state": "pending", "qualification": None}
        task["reason"] = None
        task["annotation"] = None
        if decisive:
            _, state, row = max(decisive, key=lambda value: value[0])
            occurrence = occurrences.get(_ref_occurrence(row["run_id"], row["occurrence_id"]))
            task["progress"] = {"state": state, "qualification": None}
            task["reason"] = {"code": "checkpoint_completed" if state == "completed" else
                               ("explicit_impediment" if state == "blocked" else "task_failure"),
                              "occurrence_ref": occurrence["ref"] if occurrence else None}
            continue
        agents = [occurrences[_ref_occurrence(row["run_id"], row["occurrence_id"])] for row in rows
                  if _ref_occurrence(row["run_id"], row["occurrence_id"]) in occurrences and
                  occurrences[_ref_occurrence(row["run_id"], row["occurrence_id"])]["role"] != "non_model"]
        # Manual-gate questions precede the worker and belong to a non-model gate.
        # Resolve each question independently using all task evidence, not agent summaries.
        terminal_kinds = {"returned", "passed", "failed", "interrupted", "abandoned"}
        run_stopped = any(run_id == run["display_id"] and row["phase"] == "terminal" and
                          any(item["kind"] in terminal_kinds for item in row["observations"])
                          for (run_id, _), row in occurrence_rows.items())
        waiting = None
        for row in reversed(rows):
            if run_stopped or not _outstanding_question(row):
                continue
            parent_ids = {item["facts"].get("parent_occurrence_id") for item in row["observations"]
                          if isinstance(item["facts"].get("parent_occurrence_id"), str)}
            parents = [occurrence_rows.get((row["run_id"], parent_id)) for parent_id in parent_ids]
            if any(parent and any(item["kind"] in terminal_kinds for item in parent["observations"]) for parent in parents):
                continue
            waiting = occurrences[_ref_occurrence(row["run_id"], row["occurrence_id"])]
            break
        active = next((item for item in reversed(agents)
                       if item.get("execution_summary", {}).get("state") == "running"), None)
        uncertain = next((item for item in reversed(agents)
                          if item.get("execution_summary", {}).get("state") == "unknown"), None)
        returned = next((item for item in reversed(agents)
                         if item.get("execution_summary", {}).get("state") == "success"), None)
        started = next((row for row in reversed(rows)
                        if any(item["kind"] == "started" for item in row["observations"])), None)
        if waiting:
            task["progress"] = {"state": "running", "qualification": "waiting_for_input"}
            task["annotation"] = {"code": "waiting_for_input", "label": "Waiting for input", "occurrence_ref": waiting["ref"]}
        elif active:
            task["progress"] = {"state": "running", "qualification": active["execution_summary"]["qualification"]}
            task["reason"] = {"code": "task_started", "occurrence_ref": active["ref"]}
        elif uncertain:
            task["progress"] = {"state": "unknown", "qualification": uncertain["execution_summary"]["qualification"]}
            task["reason"] = {"code": "incomplete_task_history", "occurrence_ref": uncertain["ref"]}
        elif returned:
            task["progress"] = {"state": "unknown", "qualification": "completion_unrecorded"}
            task["reason"] = {"code": "checkpoint_missing", "occurrence_ref": returned["ref"]}
        elif started:
            task["progress"] = {"state": "unknown", "qualification": "incomplete_history"}
            task["reason"] = {"code": "incomplete_task_history",
                              "occurrence_ref": _ref_occurrence(started["run_id"], started["occurrence_id"])}

    for task in public["tasks"]:
        if task["progress"]["state"] != "pending":
            continue
        prerequisite = next((candidate for candidate in public["tasks"]
                             if candidate["ref"] in task["prerequisite_refs"] and candidate["progress"]["state"] != "completed"), None)
        if prerequisite:
            task["progress"] = {"state": "blocked", "qualification": None}
            task["reason"] = {"code": "prerequisite_failed" if prerequisite["progress"]["state"] in {"failed", "blocked"}
                              else "prerequisite_incomplete", "task_ref": prerequisite["ref"]}
            continue
        terminal = any(row["run_id"] == run_id and row["phase"] == "terminal" and
                       any(item["kind"] in {"passed", "failed", "interrupted", "abandoned"} for item in row["observations"])
                       for (run_id, _), row in occurrence_rows.items() if run_id == runs[task["run_ref"]]["display_id"])
        if terminal:
            task["annotation"] = {"code": "not_started_run_stopped", "label": "Not started; run stopped"}


def _ref_occurrence(run_id: str, occurrence_id: str) -> str:
    return _ref("occ", run_id, occurrence_id)


def _execution_details(graph: dict[str, Any], public: dict[str, Any]) -> None:
    """Add closed execution and acceptance facts from recorded ownership, never payloads.

    Sequence means recorded order, not proven causality. A preparation failure can
    wrap a more specific check/worker failure; show only that specific stopping step.
    """
    records = {(item["run_ref"], item["source_seq"]): item for item in public["records"]}
    pairs = list(zip(graph.get("occurrences", []), public["occurrences"]))
    by_identity = {(row["run_id"], row["occurrence_id"]): item for row, item in pairs}
    for row, item in pairs:
        observations = row["observations"]
        item["phase"] = row["phase"]
        item["first_seq"] = observations[0]["seq"]
        item["last_seq"] = observations[-1]["seq"]
        parents = {by_identity[(row["run_id"], obs["facts"]["parent_occurrence_id"])]["ref"]
                   for obs in observations if isinstance(obs["facts"].get("parent_occurrence_id"), str)
                   and (row["run_id"], obs["facts"]["parent_occurrence_id"]) in by_identity}
        item["parent_ref"] = next(iter(parents)) if len(parents) == 1 else None
        item["stopping"] = False
        item["support_ref"] = None
    runner_states = {run["ref"]: run.get("runner_state", {"state": "unknown"}) for run in public["runs"]}
    for run in public["runs"]:
        scoped = [item for _, item in pairs if item["run_ref"] == run["ref"]]
        agents = [item for item in scoped if item["role"] != "non_model"]
        # Support and terminal cause are exact recorded invocation relations only.
        # Sequence, task identity, containment, and nearest-agent selection are not evidence.
        activity_by_ref = {item["ref"]: item for item in public.get("activities", []) if item["run_ref"] == run["ref"]}
        occurrence_by_ref = {item["ref"]: item for item in scoped}
        for activity in activity_by_ref.values():
            occurrence = occurrence_by_ref.get(activity.get("occurrence_ref"))
            support = activity.get("support_ref")
            if occurrence is not None and support in activity_by_ref:
                occurrence["support_ref"] = activity_by_ref[support]["occurrence_ref"]
        for terminal_activity in (item for item in scoped if item["phase"] == "terminal" and item["outcome"] in {"failed", "interrupted", "abandoned"}):
            terminal_source = next((source for source, candidate in pairs if candidate is terminal_activity), None)
            stopped_by = None
            if terminal_source:
                terminal_facts = next((source["facts"] for source in reversed(terminal_source["observations"])
                                       if source["kind"] in {"failed", "interrupted", "abandoned"}), {})
                stopped_by = terminal_facts.get("stopped_by_invocation_id")
            target = next((activity for activity in activity_by_ref.values()
                           if activity["invocation_id"] == stopped_by and activity["outcome"] in {"failed", "interrupted"}), None)
            if target and target.get("occurrence_ref") in occurrence_by_ref:
                occurrence_by_ref[target["occurrence_ref"]]["stopping"] = True
            else:
                # A terminal pre-agent/non-model failure is still an actual
                # essential stop; absence of a recorded invocation cause is
                # explicitly qualified rather than hidden.
                terminal_activity["stopping"] = True

        # Summaries deliberately use the full normalized snapshot, before HTTP paging.
        # They are execution facts, not task/check/review acceptance verdicts.
        for item in agents:
            rows = next(row["observations"] for row, candidate in pairs if candidate is item)
            kinds = [row["kind"] for row in rows]
            terminal = {kind for kind in kinds if kind in {"returned", "passed", "failed", "interrupted", "abandoned"}}
            typed_reviewer_result = item["role"] == "reviewer" and any(
                type(row["facts"].get("approved")) is bool and type(row["facts"].get("finding_count")) is int
                and row["facts"]["finding_count"] >= 0 for row in rows)
            questions = [candidate for candidate in scoped if candidate["parent_ref"] == item["ref"]]
            outstanding = any(_outstanding_question(source) for source, candidate in pairs if candidate in questions)
            if typed_reviewer_result:
                state, qualification = "success", None
            elif len(terminal & {"returned", "passed", "failed", "interrupted", "abandoned"}) > 1:
                state, qualification = "unknown", "conflicting_terminal_evidence"
            elif terminal & {"returned", "passed"}:
                state, qualification = "success", None
            elif "failed" in terminal:
                state, qualification = "failure", None
            elif terminal & {"interrupted", "abandoned"}:
                state, qualification = "unknown", "incomplete_terminal"
            elif outstanding:
                state, qualification = "waiting", "outstanding_input"
            elif "started" in kinds and runner_states[run["ref"]].get("state") == "live":
                state, qualification = "running", "recorded_running"
            else:
                state, qualification = "unknown", "incomplete_history"
            item["execution_summary"] = {"state": state, "qualification": qualification}

        checks, checkpoints, reviews = [], [], []
        for item in scoped:
            rows = next(row["observations"] for row, candidate in pairs if candidate is item)
            terminal_row = next((row for row in reversed(rows) if row["kind"] in {"passed", "failed", "interrupted", "abandoned"}), None)
            facts = records[(item["run_ref"], terminal_row["seq"])] if terminal_row else {}
            if item["phase"] == "check" and terminal_row:
                checks.append({"occurrence_ref": item["ref"], "state": terminal_row["kind"],
                               "ordinal": facts.get("ordinal"), "exit_code": facts.get("exit_code")})
            elif item["phase"] == "checkpoint" and terminal_row:
                checkpoints.append({"occurrence_ref": item["ref"], "state": terminal_row["kind"],
                                    "baseline": facts.get("baseline"), "head": facts.get("head"),
                                    "no_change": facts.get("no_change")})
            elif item["role"] == "reviewer" and terminal_row:
                reviews.append({"occurrence_ref": item["ref"], "state": terminal_row["kind"],
                                "approved": facts.get("approved"), "finding_count": facts.get("finding_count"),
                                "base": facts.get("review_base"), "head": facts.get("review_head")})
        run["acceptance_summary"] = {"checks": checks, "checkpoints": checkpoints, "reviews": reviews,
                                     "full_range": run["review_acceptance"]}


def create_app(reader: SnapshotReader, assets: str | Path, port: int, *, recording=None) -> Starlette:
    """Create an application bound to one reader, fixed asset inventory, and port."""
    if type(port) is not int or not 1 <= port <= 65535:
        raise ValueError("port must be a valid TCP port")
    assets_fd, fixed_assets = _assets(assets)
    expected_host = f"127.0.0.1:{port}"

    last_safe: dict[str, Any] | None = None
    last_success_at: float | None = None

    def observed(result: dict[str, Any], *, read_state: str, warning: str | None = None) -> dict[str, Any]:
        """Attach closed freshness facts without changing retained graph facts."""
        value = copy.deepcopy(result)
        recorded = [item.get("recorded_at") for item in value.get("records", [])
                    if type(item.get("recorded_at")) in (int, float)]
        warnings: list[str] = []
        if warning is not None:
            warnings.append(warning)
        if any(item.get("completeness") == "incomplete" for item in value.get("occurrences", [])):
            warnings.append("incomplete_history")
        if read_state == "unavailable":
            for run in value.get("runs", []):
                run["runner_state"] = {"state": "unknown", "reason": "read_unavailable"}
        value["observation"] = {"read_at": time.time(), "last_success_at": last_success_at,
                                "last_recorded_at": max(recorded) if recorded else None,
                                "read_state": read_state, "warnings": warnings}
        return value

    def snapshot() -> tuple[dict[str, Any] | None, JSONResponse | None]:
        nonlocal last_safe, last_success_at
        try:
            raw = reader.open_snapshot()
            graph = normalize(raw)
            result = minimize(graph)
            if result.get("state") != "ok":
                if last_safe is None:
                    return None, _state_response(result)
                raise RuntimeError("reader unavailable")
            # Runner identities are private input.  Only a closed local qualification
            # is associated with the corresponding public run, never the identity.
            identities = {item.get("run_id"): item.get("runner_identity") for item in raw.get("runs", [])
                          if isinstance(item, dict)}
            for item in result["runs"]:
                raw_id = next((row.get("run_id") for row in raw.get("runs", []) if isinstance(row, dict)
                               and isinstance(row.get("run_id"), str) and item["ref"] == run_ref(row["run_id"])), None)
                item["runner_state"] = qualify(identities.get(raw_id))
            _execution_details(graph, result)
            _task_progress(graph, result)
            if recording is not None:
                result = _qualify_public(result, recording)
            last_success_at = time.time()
            last_safe = observed(result, read_state="current")
            return last_safe, None
        except Exception:
            if last_safe is not None:
                return observed(last_safe, read_state="unavailable", warning="read_unavailable"), None
            return None, _error("internal", 500, retryable=True)

    def run(data: dict[str, Any], reference: str) -> dict[str, Any] | None:
        return next((item for item in data["runs"] if item["ref"] == reference), None)

    def selected(data: dict[str, Any], request: Request) -> tuple[dict[str, Any] | None, JSONResponse | None]:
        reference = request.path_params["run_ref"]
        if run(data, reference) is None:
            return None, _error("not_found", 404)
        return _page(data, reference, -1, _DEFAULT_PAGE_SIZE), None

    async def runs(request: Request) -> Response:
        data, error = snapshot()
        if error:
            return error
        return JSONResponse({"monitor_version": 1, "runs": data["runs"], "next_cursor": None})

    async def run_snapshot(request: Request) -> Response:
        data, error = snapshot()
        if error:
            return error
        try:
            result, error = selected(data, request)
        except ValueError:
            return _error("bad_request", 400)
        if result is not None and recording is not None:
            result["next_cursor"] = _scoped_cursor(result["next_cursor"], request.path_params["run_ref"])
        return error or JSONResponse(result)

    def request_cursor(request):
        value = request.query_params.get("cursor")
        if recording is not None and value is not None:
            prefix = request.path_params["run_ref"] + ":"
            if not value.startswith(prefix):
                return None
            value = value[len(prefix):]
        return _cursor(value)

    async def history(request: Request) -> Response:
        data, error = snapshot()
        if error:
            return error
        reference = request.path_params["run_ref"]
        if run(data, reference) is None:
            return _error("not_found", 404)
        cursor, size = request_cursor(request), _page_size(request.query_params.get("limit"))
        if cursor is None or size is None or request.query_params.get("snapshot") is None:
            return _error("bad_request", 400)
        records = [item for item in data["records"] if item["run_ref"] == reference]
        unknown = [item for item in data["unknown_records"] if item["run_ref"] == reference]
        if request.query_params["snapshot"] != _token(reference, records, unknown):
            return _error("snapshot_conflict", 409, retryable=True)
        try:
            page = _page(data, reference, cursor, size)
            if recording is not None:
                page["next_cursor"] = _scoped_cursor(page["next_cursor"], reference)
            return JSONResponse(page)
        except ValueError:
            return _error("bad_request", 400)

    async def followups(request: Request) -> Response:
        data, error = snapshot()
        if error:
            return error
        reference = request.path_params["run_ref"]
        if run(data, reference) is None:
            return _error("not_found", 404)
        cursor, size = request_cursor(request), _page_size(request.query_params.get("limit"))
        records = [item for item in data["records"] if item["run_ref"] == reference]
        unknown = [item for item in data["unknown_records"] if item["run_ref"] == reference]
        if not isinstance(cursor, int) or size is None or request.query_params.get("snapshot") != _token(reference, records, unknown):
            return _error("bad_request", 400) if request.query_params.get("snapshot") is None else _error("snapshot_conflict", 409, retryable=True)
        all_relations = data.get("followups", [])
        # Expand the finite explicitly declared component only; do not infer links or
        # search outside this fixed snapshot/worktree.
        related = {reference}
        while True:
            expanded = related | {item["run_ref"] for item in all_relations if item["source_run_ref"] in related} | {item["source_run_ref"] for item in all_relations if item["run_ref"] in related}
            if expanded == related:
                break
            related = expanded
        relations = [item for item in all_relations if item["run_ref"] in related or item["source_run_ref"] in related]
        if cursor >= len(relations) and cursor != -1:
            return _error("bad_request", 400)
        start = cursor + 1
        visible = relations[start:start + size]
        return JSONResponse({"monitor_version": 1, "run_ref": reference, "followups": visible,
                             "next_cursor": (_scoped_cursor("cursor_" + str(start + len(visible) - 1), reference)
                                             if recording is not None else "cursor_" + str(start + len(visible) - 1))
                                            if start + len(visible) < len(relations) else None})

    async def record(request: Request) -> Response:
        data, error = snapshot()
        if error:
            return error
        reference = request.path_params["run_ref"]
        if run(data, reference) is None:
            return _error("not_found", 404)
        records = [item for item in data["records"] if item["run_ref"] == reference]
        unknown = [item for item in data["unknown_records"] if item["run_ref"] == reference]
        if request.query_params.get("snapshot") != _token(reference, records, unknown):
            return _error("snapshot_conflict", 409, retryable=True)
        item = next((value for value in records + unknown if value["ref"] == request.path_params["record_ref"]), None)
        return JSONResponse(item) if item else _error("not_found", 404)

    def asset_response(path: str) -> Response:
        return _asset_response(assets_fd, fixed_assets, path)

    async def run_shell(request: Request) -> Response:
        raw_path = request.scope.get("raw_path")
        if not isinstance(raw_path, bytes) or not _encoded_run_id(raw_path):
            return _error("not_found", 404)
        return asset_response("/index.html")

    async def static(request: Request) -> Response:
        name = request.path_params.get("path", "")
        return asset_response("/index.html" if name == "" else "/" + name)

    def secure(response: Response) -> Response:
        response.headers.update({"Cache-Control": "no-store", "X-Content-Type-Options": "nosniff",
                                 "Referrer-Policy": "no-referrer", "X-Frame-Options": "DENY",
                                 "Content-Security-Policy": _CSP})
        return response

    async def protected(request: Request, call_next):
        host = request.headers.get("host")
        if host != expected_host or request.method not in {"GET", "HEAD"}:
            return secure(_error("bad_request", 400))
        if request.url.path.startswith("/api/"):
            origin = request.headers.get("origin")
            if origin is not None and origin != f"http://{expected_host}":
                return secure(_error("bad_request", 400))
            if request.headers.get("sec-fetch-site") != "same-origin" or request.headers.get("x-workflow-monitor") != "1":
                return secure(_error("bad_request", 400))
        try:
            return secure(await call_next(request))
        except Exception:
            return secure(_error("internal", 500, retryable=True))

    app = Starlette(routes=[
        Route("/api/monitor/v1/runs", runs, methods=["GET"]),
        Route("/api/monitor/v1/runs/{run_ref}/snapshot", run_snapshot, methods=["GET"]),
        Route("/api/monitor/v1/runs/{run_ref}/history", history, methods=["GET"]),
        Route("/api/monitor/v1/runs/{run_ref}/records/{record_ref}", record, methods=["GET"]),
        Route("/api/monitor/v1/runs/{run_ref}/followups", followups, methods=["GET"]),
        Route("/runs/{run_path:path}", run_shell, methods=["GET", "HEAD"]),
        Route("/{path:path}", static, methods=["GET", "HEAD"]),
    ])
    app.add_middleware(BaseHTTPMiddleware, dispatch=protected)
    return app


# Each recording retains the existing normalization, paging and freshness closure.
# Only closed public references are qualified, after all local relations are resolved.
from .projects import Projects, Recording


def _scoped_cursor(cursor: str | None, reference: str) -> str | None:
    return reference + ":" + cursor if cursor is not None else None


def _qualify_public(data: dict[str, Any], recording: Recording) -> dict[str, Any]:
    prefix = recording.ref + "."
    keyed = {"chain_acceptance", "metric_coverage", "metric_aggregates", "metric_artifacts"}

    def qualify(value: Any, field: str = "") -> Any:
        if isinstance(value, dict):
            return {(prefix + key if field in keyed else key): qualify(child, key)
                    for key, child in value.items()}
        if isinstance(value, list):
            return [qualify(child, field) for child in value]
        if isinstance(value, str) and (field in {"ref", "correction_chain"} or field.endswith("_ref") or field.endswith("_refs")):
            return prefix + value
        return value

    result = qualify(data)
    for run in result.get("runs", []):
        # Fixed-width full recording hash makes qualification stable and unambiguous,
        # regardless of the appearance/disappearance of another live recording.
        run["display_id"] = recording.ref.split("_", 1)[1] + "-" + run["display_id"]
        run["source"] = recording.label
    return result


def _project_app(projects: Projects, assets: str | Path, port: int) -> Starlette:
    if type(port) is not int or not 1 <= port <= 65535:
        raise ValueError("port must be a valid TCP port")
    assets_fd, fixed_assets = _assets(assets)
    expected_host = f"127.0.0.1:{port}"
    readers: dict[str, Starlette] = {}

    async def static(request: Request) -> Response:
        name = request.path_params.get("path", "")
        return _asset_response(assets_fd, fixed_assets, "/index.html" if name == "" else "/" + name)

    def secure(response: Response) -> Response:
        response.headers.update({"Cache-Control": "no-store", "X-Content-Type-Options": "nosniff",
                                 "Referrer-Policy": "no-referrer", "X-Frame-Options": "DENY",
                                 "Content-Security-Policy": _CSP})
        return response

    async def listed(request: Request) -> Response:
        # A page load explicitly refreshes discovery, retaining all existing Reader
        # bindings and their identity/fallback state. Polling runs does not rediscover.
        inventory = projects.refresh()
        return JSONResponse({"monitor_version": 1, "projects": [
            {"ref": project.ref, "label": project.label,
             "recordings": [{"ref": item.ref, "label": item.label, "state": item.state}
                            for item in project.recordings]} for project in inventory]})

    async def dispatch(request: Request, recording: Recording, path: str) -> Response:
        if recording.reader is None:
            return _error("unavailable", 503, retryable=True)
        inner = readers.get(recording.ref)
        if inner is None:
            inner = _create_single_app(recording.reader, assets, port, recording=recording)
            readers[recording.ref] = inner
        scope = dict(request.scope, path=path, raw_path=path.encode("utf-8"))
        messages: list[dict[str, Any]] = []
        async def receive() -> dict[str, Any]:
            return {"type": "http.request", "body": b"", "more_body": False}
        async def send(message: dict[str, Any]) -> None:
            messages.append(message)
        await inner(scope, receive, send)
        start = next(item for item in messages if item["type"] == "http.response.start")
        body = b"".join(item.get("body", b"") for item in messages if item["type"] == "http.response.body")
        headers = {key.decode("latin-1"): value.decode("latin-1") for key, value in start["headers"]}
        return Response(body, status_code=start["status"], headers=headers, media_type=None)

    async def proxy(request: Request) -> Response:
        project = projects.resolve_project(request.path_params["project_ref"])
        if project is None:
            return _error("not_found", 404)
        rest = request.path_params.get("rest", "")
        if not request.url.path.startswith("/api/"):
            raw = request.scope.get("raw_path", b"")
            prefix = ("/projects/" + project.ref).encode("ascii")
            shell = raw[len(prefix):] if raw.startswith(prefix) else b""
            if shell != b"/runs" and not _encoded_run_id(shell):
                return _error("not_found", 404)
            return _asset_response(assets_fd, fixed_assets, "/index.html")
        if rest == "runs":
            runs = []
            for recording in project.recordings:
                response = await dispatch(request, recording, "/api/monitor/v1/runs")
                if response.status_code == 200:
                    runs.extend(json.loads(response.body)["runs"])
            return JSONResponse({"monitor_version": 1, "runs": runs, "next_cursor": None})
        parts = rest.split("/")
        if len(parts) < 3 or parts[0] != "runs":
            return _error("not_found", 404)
        recording_ref, separator, local_ref = parts[1].partition(".")
        recording = projects.resolve_recording(project.ref, recording_ref) if separator and local_ref else None
        if recording is None:
            return _error("not_found", 404)
        return await dispatch(request, recording, "/api/monitor/v1/" + rest)

    async def protected(request: Request, call_next):
        host = request.headers.get("host")
        if host != expected_host or request.method not in {"GET", "HEAD"}:
            return secure(_error("bad_request", 400))
        if request.url.path.startswith("/api/"):
            origin = request.headers.get("origin")
            if origin is not None and origin != f"http://{expected_host}":
                return secure(_error("bad_request", 400))
            if request.headers.get("sec-fetch-site") != "same-origin" or request.headers.get("x-workflow-monitor") != "1":
                return secure(_error("bad_request", 400))
        try:
            return secure(await call_next(request))
        except Exception:
            return secure(_error("internal", 500, retryable=True))

    app = Starlette(routes=[
        Route("/api/monitor/v1/projects", listed, methods=["GET"]),
        Route("/api/monitor/v1/projects/{project_ref}/{rest:path}", proxy, methods=["GET"]),
        Route("/projects/{project_ref}/{rest:path}", proxy, methods=["GET", "HEAD"]),
        Route("/{path:path}", static, methods=["GET", "HEAD"]),
    ])
    app.add_middleware(BaseHTTPMiddleware, dispatch=protected)
    return app


_create_single_app = create_app

def create_app(reader: SnapshotReader | Projects, assets: str | Path, port: int) -> Starlette:
    """Create either the legacy single reader view or project-scoped monitor routes."""
    return _project_app(reader, assets, port) if isinstance(reader, Projects) else _create_single_app(reader, assets, port)


__all__ = ["create_app"]
