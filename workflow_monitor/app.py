"""Closed, loopback-only HTTP presentation for workflow monitor snapshots."""
from __future__ import annotations

import copy
import hashlib
import mimetypes
import os
from pathlib import Path
import stat
import time
from typing import Any, Protocol

from starlette.applications import Starlette
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Route

from .liveness import qualify
from .mapping import normalize
from .public import minimize, run_ref

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
    if value.startswith("cursor_unknown_") and value[15:]:
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
    for key in ("phases", "tasks", "occurrences", "edges"):
        result[key] = [item for item in data[key] if item["run_ref"] == reference]
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


def _execution_details(graph: dict[str, Any], public: dict[str, Any]) -> None:
    """Add closed execution presentation facts from recorded ownership, never payloads.

    Sequence means recorded order, not proven causality. A preparation failure can
    wrap a more specific check/worker failure; show only that specific stopping step.
    """
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
    for run in public["runs"]:
        scoped = [item for _, item in pairs if item["run_ref"] == run["ref"]]
        agents = [item for item in scoped if item["role"] != "non_model"]
        for item in scoped:
            if item["role"] != "non_model":
                continue
            parent = next((agent for agent in agents if agent["ref"] == item["parent_ref"]), None)
            if parent is None:
                contained = [agent for agent in agents if item["phase"] == "prepare"
                             and agent["task_ref"] == item["task_ref"]
                             and item["first_seq"] < agent["first_seq"] <= item["last_seq"]]
                boundary = item["last_seq"] if item["phase"] == "terminal" else item["first_seq"]
                preceding = [agent for agent in agents if agent["first_seq"] < boundary
                             and (item["task_ref"] is None or agent["task_ref"] == item["task_ref"])]
                parent = min(contained, key=lambda agent: agent["first_seq"], default=None)
                if parent is None:
                    parent = max(preceding, key=lambda agent: agent["first_seq"], default=None)
            item["support_ref"] = parent["ref"] if parent else None
        terminals = [item for item in scoped if item["phase"] == "terminal" and item["outcome"] in {"failed", "interrupted", "abandoned"}]
        for terminal in terminals:
            failures = [item for item in scoped if item is not terminal and item["outcome"] in {"failed", "interrupted", "abandoned"}
                        and terminal["first_seq"] <= item["last_seq"] <= terminal["last_seq"]]
            failure = max(failures, key=lambda item: item["last_seq"], default=terminal)
            if failure["phase"] == "prepare":
                nested = [item for item in failures if item is not failure and item["task_ref"] == failure["task_ref"]
                          and failure["first_seq"] <= item["last_seq"] <= failure["last_seq"]]
                failure = max(nested, key=lambda item: item["last_seq"], default=failure)
            later_progress = [item for item in scoped if item["phase"] not in {"prepare", "terminal"}
                              and item["outcome"] == "passed" and failure["last_seq"] < item["last_seq"] < terminal["last_seq"]]
            if later_progress or any(failure["last_seq"] < agent["first_seq"] < terminal["last_seq"] for agent in agents):
                failure = terminal
            if failure["role"] == "non_model":
                failure["stopping"] = True


def create_app(reader: SnapshotReader, assets: str | Path, port: int) -> Starlette:
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
            if result.get("state") == "ok":
                _execution_details(graph, result)
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
        return error or JSONResponse(result)

    async def history(request: Request) -> Response:
        data, error = snapshot()
        if error:
            return error
        reference = request.path_params["run_ref"]
        if run(data, reference) is None:
            return _error("not_found", 404)
        cursor, size = _cursor(request.query_params.get("cursor")), _page_size(request.query_params.get("limit"))
        if cursor is None or size is None or request.query_params.get("snapshot") is None:
            return _error("bad_request", 400)
        records = [item for item in data["records"] if item["run_ref"] == reference]
        unknown = [item for item in data["unknown_records"] if item["run_ref"] == reference]
        if request.query_params["snapshot"] != _token(reference, records, unknown):
            return _error("snapshot_conflict", 409, retryable=True)
        try:
            return JSONResponse(_page(data, reference, cursor, size))
        except ValueError:
            return _error("bad_request", 400)

    async def followups(request: Request) -> Response:
        data, error = snapshot()
        if error:
            return error
        reference = request.path_params["run_ref"]
        if run(data, reference) is None:
            return _error("not_found", 404)
        cursor, size = _cursor(request.query_params.get("cursor")), _page_size(request.query_params.get("limit"))
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
                             "next_cursor": "cursor_" + str(start + len(visible) - 1) if start + len(visible) < len(relations) else None})

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

    async def static(request: Request) -> Response:
        name = request.path_params.get("path", "")
        path = "/index.html" if name == "" else "/" + name
        asset = fixed_assets.get(path)
        if asset is None:
            return _error("not_found", 404)
        try:
            content = _read_asset(assets_fd, asset)
        except OSError:
            return _error("not_found", 404)
        return Response(content, media_type=mimetypes.guess_type(path)[0] or "application/octet-stream")

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
        Route("/{path:path}", static, methods=["GET", "HEAD"]),
    ])
    app.add_middleware(BaseHTTPMiddleware, dispatch=protected)
    return app


__all__ = ["create_app"]
