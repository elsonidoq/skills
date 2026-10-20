"""Closed, loopback-only HTTP presentation for workflow monitor snapshots."""
from __future__ import annotations

import mimetypes
from pathlib import Path
from typing import Any, Protocol

from starlette.applications import Starlette
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.routing import Route

from .mapping import normalize
from .public import minimize

_CSP = "default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; worker-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'"
_ASSET_SUFFIXES = frozenset({".css", ".gif", ".html", ".ico", ".jpeg", ".jpg", ".js", ".png", ".svg", ".webp", ".woff", ".woff2"})


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


def _assets(root: str | Path) -> dict[str, Path]:
    root = Path(root).resolve(strict=True)
    if not root.is_dir() or root.is_symlink():
        raise ValueError("assets must be a regular directory")
    files: dict[str, Path] = {}
    for candidate in root.rglob("*"):
        if not candidate.is_file():
            continue
        relative = candidate.relative_to(root)
        if (candidate.is_symlink() or candidate.suffix not in _ASSET_SUFFIXES or
                any(part.startswith(".") for part in relative.parts)):
            continue
        files["/" + relative.as_posix()] = candidate
    if "/index.html" not in files:
        raise ValueError("assets must contain index.html")
    return files


def create_app(reader: SnapshotReader, assets: str | Path, port: int) -> Starlette:
    """Create an application bound to one reader, fixed asset inventory, and port."""
    if type(port) is not int or not 1 <= port <= 65535:
        raise ValueError("port must be a valid TCP port")
    fixed_assets = _assets(assets)
    expected_host = f"127.0.0.1:{port}"

    def snapshot() -> tuple[dict[str, Any] | None, JSONResponse | None]:
        try:
            result = minimize(normalize(reader.open_snapshot()))
        except Exception:
            return None, _error("internal", 500, retryable=True)
        error = _state_response(result)
        return (result if error is None else None), error

    def run(data: dict[str, Any], reference: str) -> dict[str, Any] | None:
        return next((item for item in data["runs"] if item["ref"] == reference), None)

    async def runs(request: Request) -> Response:
        data, error = snapshot()
        if error:
            return error
        return JSONResponse({"monitor_version": 1, "runs": data["runs"], "next_cursor": None})

    async def run_snapshot(request: Request) -> Response:
        data, error = snapshot()
        if error:
            return error
        if run(data, request.path_params["run_ref"]) is None:
            return _error("not_found", 404)
        return JSONResponse(data)

    async def history(request: Request) -> Response:
        data, error = snapshot()
        if error:
            return error
        reference = request.path_params["run_ref"]
        if run(data, reference) is None:
            return _error("not_found", 404)
        records = [item for item in data["records"] if item["run_ref"] == reference]
        return JSONResponse({"monitor_version": 1, "selected_run": reference, "records": records,
                             "next_cursor": None, "inventory": data["inventory"]})

    async def record(request: Request) -> Response:
        data, error = snapshot()
        if error:
            return error
        reference = request.path_params["run_ref"]
        if run(data, reference) is None:
            return _error("not_found", 404)
        item = next((value for value in data["records"] if value["run_ref"] == reference and value["ref"] == request.path_params["record_ref"]), None)
        return JSONResponse(item) if item else _error("not_found", 404)

    async def static(request: Request) -> Response:
        name = request.path_params.get("path", "")
        path = "/index.html" if name == "" else "/" + name
        asset = fixed_assets.get(path)
        if asset is None:
            return _error("not_found", 404)
        return Response(asset.read_bytes(), media_type=mimetypes.guess_type(asset.name)[0] or "application/octet-stream")

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
        Route("/{path:path}", static, methods=["GET", "HEAD"]),
    ])
    app.add_middleware(BaseHTTPMiddleware, dispatch=protected)
    return app


__all__ = ["create_app"]
