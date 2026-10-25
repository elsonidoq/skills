"""Publish one verified stopped-worktree monitor capture without modifying live stores."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import stat
import sqlite3
import sys
import uuid
from typing import Any

from .preserve_source import Capture, CaptureError, capture_stopped, registered_main, retained_digest, _read_bytes
from .reader import Reader, ReaderError
from .recordings import (DATABASE_NAME, METADATA_NAME, PRESERVED_DIRECTORY,
                         RECORDING_VERSION, RecordingError, bind)


class PreserveError(RuntimeError):
    """A capture could not be safely published or verified."""


def _owned_directory(path: Path, operation: str) -> None:
    try:
        value = path.lstat()
    except FileNotFoundError as exc:
        raise PreserveError(f"{operation}: storage is absent; restore main/.coherence and retry") from exc
    if path.is_symlink() or not stat.S_ISDIR(value.st_mode) or value.st_uid != os.geteuid() or value.st_mode & 0o022:
        raise PreserveError(f"{operation}: storage is unsafe; restore owned non-symlink main storage and retry")


def _recording_id(capture: Capture) -> str:
    # The content identity makes an exact stopped-source repeat address the same target
    # without retaining a source path in public metadata.
    value = json.dumps({"origin": capture.origin_id, "facts": capture.summary["facts_sha256"],
                        "metrics": capture.summary["metrics"]}, sort_keys=True, separators=(",", ":"))
    return "capture-" + hashlib.sha256(value.encode("utf-8")).hexdigest()[:32]


def _root(main: Path) -> Path:
    coherence = main / ".coherence"
    _owned_directory(coherence, "preservation publication")
    root = coherence / PRESERVED_DIRECTORY
    try:
        root.mkdir(mode=0o700)
    except FileExistsError:
        pass
    except OSError as exc:
        raise PreserveError("preservation publication: cannot create recording storage; restore main permissions and retry") from exc
    _owned_directory(root, "preservation publication")
    return root


def _write_metadata(directory: Path, origin_id: str, recording_id: str) -> None:
    metadata = directory / METADATA_NAME
    try:
        fd = os.open(metadata, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as output:
            json.dump({"version": RECORDING_VERSION, "state": "complete", "recording_id": recording_id,
                       "origin_id": origin_id}, output, sort_keys=True, separators=(",", ":"))
            output.flush()
            os.fsync(output.fileno())
    except OSError as exc:
        raise PreserveError("preservation publication: cannot prepare complete metadata; retain the source and retry") from exc


def _readback(capture: Capture, recording_id: str) -> dict[str, Any]:
    try:
        reader = Reader.preserved(capture.main, recording_id)
        if reader.recording_identity != (recording_id, capture.origin_id):
            raise PreserveError("preservation readback: recording origin differs from capture; retain the source and inspect the capture")
        snapshot = reader.open_snapshot()
    except (OSError, ReaderError) as exc:
        raise PreserveError("preservation readback: cannot reopen the complete recording; retain the source and inspect the capture") from exc
    if snapshot.get("state") not in {"ok", "unsupported", "no_monitored_runs"}:
        raise PreserveError("preservation readback: completed recording is unavailable; retain the source and inspect the capture")
    directory = capture.main / ".coherence" / PRESERVED_DIRECTORY / recording_id
    try:
        if retained_digest(directory / DATABASE_NAME) != capture.summary["facts_sha256"]:
            raise PreserveError("preservation readback: retained monitor facts differ from capture; retain the source and inspect the capture")
        for name, expected_metric in capture.summary["metrics"].items():
            metric_path = directory / "metrics" / name
            if expected_metric["availability"] == "absent":
                if metric_path.exists() or metric_path.is_symlink():
                    raise PreserveError("preservation readback: absent metric was replaced; retain the source and inspect the capture")
            elif hashlib.sha256(_read_bytes(metric_path, "preservation metric readback")).hexdigest() != expected_metric["sha256"]:
                raise PreserveError("preservation readback: metric bytes differ from capture; retain the source and inspect the capture")
    except (OSError, sqlite3.Error, CaptureError) as exc:
        raise PreserveError("preservation readback: cannot verify retained facts/metric bytes; retain the source and inspect the capture") from exc
    qualifications: dict[str, str] = {}
    metrics = snapshot.get("metrics", {})
    for run_id in capture.fingerprint["run_ids"]:
        name = "run-" + hashlib.sha256(run_id.encode("utf-8")).hexdigest() + ".jsonl"
        expected = capture.summary["metrics"][name]["availability"]
        metric = metrics.get(run_id)
        if expected != "absent" and not (capture.main / ".coherence" / PRESERVED_DIRECTORY / recording_id / "metrics" / name).is_file():
            raise PreserveError("preservation readback: copied metric is absent; retain the source and inspect the capture")
        # Unsupported descriptors have no Reader metric projection, but their byte
        # presence above is still checked. Supported rows must retain the same
        # availability distinction; malformed/partial bytes remain qualified.
        if metric is not None:
            qualifications[run_id] = metric["coverage"]
            if (expected == "absent") != (metric["coverage"] == "unavailable"):
                raise PreserveError("preservation readback: metric availability differs from capture; retain the source and inspect the capture")
    return {"main_worktree": str(capture.main), "recording_id": recording_id, "origin_id": capture.origin_id,
            "runs": [row["run_id"] for row in snapshot.get("runs", [])],
            "metric_qualifications": qualifications, "readback": "verified"}


def _prior_for_origin(root: Path, origin_id: str, except_id: str) -> bool:
    try:
        entries = list(root.iterdir())
    except OSError as exc:
        raise PreserveError("preservation repeat check: cannot inspect existing captures; restore main access and retry") from exc
    for entry in entries:
        if entry.name == except_id:
            continue
        try:
            if entry.is_dir() and bind(root.parent.parent, entry.name).origin_id == origin_id:
                return True
        except (OSError, RecordingError):
            # Unknown or incomplete data is never adopted as a repeat target.
            continue
    return False


def preserve(source_worktree: str | os.PathLike[str]) -> dict[str, Any]:
    """Capture, publish once, and reopen a stopped linked worktree recording.

    The final context-exit source check happens after readback.  Therefore this function
    returns success only after the source lock has been released without drift.
    """
    source = Path(source_worktree)
    # Reuse capture's registered-main boundary; Git's admin directory need not be
    # main/.git (for example --separate-git-dir). No guessed destination is written.
    try:
        main = registered_main(source)
    except (OSError, CaptureError) as exc:
        raise PreserveError(str(exc)) from exc
    private_hint = main / ".coherence" / ("preserve-" + uuid.uuid4().hex)
    try:
        with capture_stopped(source, private_hint) as capture:
            recording_id = _recording_id(capture)
            root = _root(capture.main)
            target = root / recording_id
            if target.exists() or target.is_symlink():
                try:
                    bind(capture.main, recording_id)
                except RecordingError as exc:
                    raise PreserveError("preservation repeat check: existing target is incomplete or unsafe; retain the source and inspect it without overwriting") from exc
                capture.verify_unchanged()
                result = _readback(capture, recording_id)
                result["reused"] = True
                return result
            if _prior_for_origin(root, capture.origin_id, recording_id):
                raise PreserveError("preservation mismatch: source differs from a prior stopped capture; retain both source and prior capture while resolving the difference")
            capture.verify_unchanged()
            try:
                # mkdir is the no-overwrite reservation.  The directory is not a
                # recording until the final metadata write, so an interruption leaves
                # pending bytes invisible rather than replacing a complete capture.
                target.mkdir(mode=0o700)
            except FileExistsError as exc:
                raise PreserveError("preservation publication: target appeared during publication; retain the source and retry without overwriting") from exc
            except OSError as exc:
                raise PreserveError("preservation publication: cannot reserve recording storage; retain the source and inspect the private capture") from exc
            try:
                os.rename(capture.database, target / DATABASE_NAME)
                os.rename(capture.metrics, target / "metrics")
                _write_metadata(target, capture.origin_id, recording_id)
            except OSError as exc:
                raise PreserveError("preservation publication: cannot publish complete capture; retain the source and inspect pending bytes") from exc
            result = _readback(capture, recording_id)
            result["reused"] = False
            return result
    except CaptureError as exc:
        raise PreserveError(str(exc)) from exc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Preserve one stopped linked-worktree monitor recording under its registered main.")
    parser.add_argument("--source-worktree", required=True, metavar="PATH")
    args = parser.parse_args(argv)
    try:
        result = preserve(args.source_worktree)
    except PreserveError as exc:
        print(f"workflow-monitor-preserve: {exc}", file=sys.stderr)
        return 2
    print("preserved " + json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
