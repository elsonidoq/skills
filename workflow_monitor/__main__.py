"""Safe local launcher for the read-only workflow monitor."""
from __future__ import annotations

import argparse
from pathlib import Path

import uvicorn

from .app import create_app
from .reader import Reader, ReaderError


def _port(value: str) -> int:
    try:
        port = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("port must be numeric") from exc
    if not 1 <= port <= 65535:
        raise argparse.ArgumentTypeError("port must be between 1 and 65535")
    return port


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Serve read-only workflow monitor snapshots on numeric loopback.")
    parser.add_argument("--project", required=True, metavar="CANONICAL_WORKTREE")
    parser.add_argument("--assets", required=True, metavar="BUILD_ROOT")
    parser.add_argument("--port", type=_port, default=8765)
    args = parser.parse_args(argv)
    try:
        app = create_app(Reader(Path(args.project)), Path(args.assets), args.port)
    except (OSError, ValueError, ReaderError) as exc:
        parser.error(str(exc))
    uvicorn.run(app, host="127.0.0.1", port=args.port, reload=False, access_log=False,
                proxy_headers=False, server_header=False, date_header=False, log_level="warning")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
