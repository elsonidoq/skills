"""Safe bindings for complete preserved monitor recordings.

A preserved recording is a monitor-only SQLite/JSONL copy published below the verified
main worktree.  This module only recognizes that narrow completed layout; it neither
creates it nor treats preparation directories as history.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import stat
from typing import Any


PRESERVED_DIRECTORY = "preserved-recordings"
METADATA_NAME = "recording.json"
DATABASE_NAME = "monitor.sqlite"
METRICS_DIRECTORY = "metrics"
RECORDING_VERSION = 1
_SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")


class RecordingError(RuntimeError):
    """A preserved recording is absent, incomplete, or unsafe to bind."""


def _owned_file(path: Path) -> os.stat_result:
    try:
        value = path.lstat()
    except FileNotFoundError as exc:
        raise RecordingError("no_store") from exc
    if path.is_symlink() or not stat.S_ISREG(value.st_mode) or value.st_uid != os.geteuid() or value.st_mode & 0o022:
        raise RecordingError("unsafe preserved storage")
    return value


def _owned_directory(path: Path) -> None:
    try:
        value = path.lstat()
    except FileNotFoundError as exc:
        raise RecordingError("no_store") from exc
    if path.is_symlink() or not stat.S_ISDIR(value.st_mode) or value.st_uid != os.geteuid() or value.st_mode & 0o022:
        raise RecordingError("unsafe preserved storage")


def _metadata(path: Path, recording_id: str) -> dict[str, str | int]:
    _owned_file(path)
    try:
        value: Any = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, ValueError) as exc:
        raise RecordingError("invalid preserved metadata") from exc
    if (not isinstance(value, dict) or set(value) != {"version", "state", "recording_id", "origin_id"} or
            value.get("version") != RECORDING_VERSION or value.get("state") != "complete" or
            value.get("recording_id") != recording_id or
            not isinstance(value.get("origin_id"), str) or not _SAFE_ID.fullmatch(value["origin_id"])):
        raise RecordingError("invalid preserved metadata")
    return value


class PreservedBinding:
    """A pinned complete recording below one verified main worktree.

    ``recording_id`` identifies this capture, while ``origin_id`` identifies the stopped
    source supplied by a later capture command.  Both are opaque stable IDs: metadata
    intentionally retains no source/admin path.  Only ``state: complete`` is public;
    any other private preparation is ineligible for Reader binding.
    """

    def __init__(self, main: Path, recording_id: str):
        if not isinstance(recording_id, str) or not _SAFE_ID.fullmatch(recording_id):
            raise RecordingError("invalid preserved recording id")
        self.main = main
        self.recording_id = recording_id
        coherence = main / ".coherence"
        root = coherence / PRESERVED_DIRECTORY
        directory = root / recording_id
        for path in (coherence, root, directory):
            _owned_directory(path)
        self.directory = directory
        self.metadata = _metadata(directory / METADATA_NAME, recording_id)
        self.database = directory / DATABASE_NAME
        self.metrics = directory / METRICS_DIRECTORY
        _owned_file(self.database)
        _owned_directory(self.metrics)
        database = _owned_file(self.database)
        metadata = _owned_file(directory / METADATA_NAME)
        directory_stat = directory.lstat()
        metrics_stat = self.metrics.lstat()
        self._identity = ((database.st_dev, database.st_ino), (metadata.st_dev, metadata.st_ino),
                          (directory_stat.st_dev, directory_stat.st_ino), (metrics_stat.st_dev, metrics_stat.st_ino))

    @property
    def origin_id(self) -> str:
        return self.metadata["origin_id"]  # validated by _metadata

    def check(self) -> None:
        """Reject replacement, incomplete metadata, and unsafe path substitution."""
        rebound = PreservedBinding(self.main, self.recording_id)
        if rebound._identity != self._identity or rebound.metadata != self.metadata:
            raise RecordingError("preserved recording identity changed")


def bind(main: Path, recording_id: str) -> PreservedBinding:
    """Bind one complete recording; callers must already have verified ``main``."""
    return PreservedBinding(main, recording_id)


__all__ = ["DATABASE_NAME", "METADATA_NAME", "METRICS_DIRECTORY", "PRESERVED_DIRECTORY",
           "PreservedBinding", "RECORDING_VERSION", "RecordingError", "bind"]
