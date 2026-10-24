"""Read-only discovery of live workflow-monitor recordings in Git worktrees.

The inventory deliberately retains one :class:`Reader` per registered worktree.  It does
not open snapshots while listing projects, so discovery neither writes storage nor walks
all databases.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import os
from pathlib import Path
import stat
import subprocess
from typing import Iterable

from .reader import Reader, ReaderError
from .recordings import PRESERVED_DIRECTORY, RecordingError

_GIT_ENV = ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_COMMON_DIR",
            "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES")


def _opaque(kind: str, value: Path) -> str:
    return kind + "_" + hashlib.sha256(os.fsencode(str(value))).hexdigest()[:24]


def _git(path: Path, *arguments: str) -> str:
    if any(os.environ.get(name) for name in _GIT_ENV):
        raise ReaderError("ambient Git authority override")
    result = subprocess.run(
        ["git", "--no-optional-locks", "-C", str(path), *arguments],
        capture_output=True, check=False,
    )
    if result.returncode:
        raise ReaderError("project is not a readable Git worktree")
    return result.stdout.decode("utf-8", "strict")


def _git_path(worktree: Path, argument: str) -> Path:
    value = Path(_git(worktree, "rev-parse", argument).strip())
    if not value.is_absolute():
        value = worktree / value
    return value.resolve(strict=True)


def _registered_worktrees(worktree: Path) -> Iterable[Path]:
    """Yield paths from Git's NUL-delimited porcelain, never by directory scanning."""
    raw = _git(worktree, "worktree", "list", "--porcelain", "-z")
    for field in raw.split("\0"):
        if field.startswith("worktree "):
            candidate = Path(field[len("worktree "):])
            try:
                yield candidate.resolve(strict=True)
            except OSError:
                # A stale registration is not a route to scan or follow elsewhere.
                continue


@dataclass(frozen=True)
class Recording:
    """An opaque live recording binding; paths stay an internal server concern."""

    ref: str
    label: str
    state: str
    reader: Reader | None
    worktree: Path


@dataclass(frozen=True)
class Project:
    ref: str
    label: str
    recordings: tuple[Recording, ...]
    common_dir: Path


class Projects:
    """Inventory immediate-child repositories and their Git-registered worktrees."""

    def __init__(self, root: str | os.PathLike[str]):
        proposed = Path(root).expanduser()
        try:
            entry = proposed.lstat()
            if stat.S_ISLNK(entry.st_mode) or not stat.S_ISDIR(entry.st_mode):
                raise OSError("not a directory")
            self.root = proposed.resolve(strict=True)
            # Test readability now, rather than turning an unreadable root into an empty one.
            with os.scandir(self.root):
                pass
        except OSError as exc:
            raise ValueError("projects root must be a readable, non-symlink directory") from exc
        self._projects: tuple[Project, ...] | None = None

    def inventory(self) -> tuple[Project, ...]:
        if self._projects is None:
            self._projects = self._discover()
        return self._projects

    def refresh(self) -> tuple[Project, ...]:
        """Re-read the inventory on an explicit page reload, without writing storage."""
        self._projects = self._discover()
        return self._projects

    def resolve_project(self, project_ref: str) -> Project | None:
        return next((project for project in self.inventory() if project.ref == project_ref), None)

    def resolve_recording(self, project_ref: str, recording_ref: str) -> Recording | None:
        project = self.resolve_project(project_ref)
        if project is None:
            return None
        return next((recording for recording in project.recordings if recording.ref == recording_ref), None)

    def main_for(self, worktree: str | os.PathLike[str]) -> Recording | None:
        """Resolve a registered source to its actual main worktree, for preservation."""
        try:
            source = Path(worktree).resolve(strict=True)
        except OSError:
            return None
        for project in self.inventory():
            if any(recording.worktree == source for recording in project.recordings):
                return next((recording for recording in project.recordings if recording.label == "main"), None)
        return None

    def _discover(self) -> tuple[Project, ...]:
        groups: dict[Path, dict[Path, tuple[Path, Path, Path]]] = {}
        try:
            children = list(self.root.iterdir())
        except OSError as exc:
            raise ValueError("projects root is not readable") from exc
        for child in children:
            try:
                info = child.lstat()
                if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
                    continue
                initial = child.resolve(strict=True)
                top = _git_path(initial, "--show-toplevel")
                # Only immediate children begin discovery.  A nested repository is not a
                # project merely because Git can find it from below its parent.
                if top != initial:
                    continue
                common = _git_path(initial, "--git-common-dir")
                for registered in _registered_worktrees(initial):
                    try:
                        registered_top = _git_path(registered, "--show-toplevel")
                        registered_common = _git_path(registered, "--git-common-dir")
                        admin = _git_path(registered, "--absolute-git-dir")
                    except (OSError, ReaderError):
                        continue
                    if registered_top != registered or registered_common != common:
                        continue
                    groups.setdefault(common, {})[registered] = (registered, admin, common)
            except (OSError, ReaderError):
                continue

        projects: list[Project] = []
        for common, members in groups.items():
            recordings: list[Recording] = []
            main_worktree: Path | None = None
            for worktree, (_, admin, _) in sorted(members.items(), key=lambda item: str(item[0])):
                label = "main" if admin == common else "linked"
                if label == "main":
                    main_worktree = worktree
                try:
                    reader: Reader | None = Reader(worktree)
                    state = "available" if reader.database.exists() else "no_store"
                except (OSError, ReaderError):
                    reader, state = None, "unavailable"
                recordings.append(Recording(_opaque("recording", admin), label, state, reader, worktree))
            # Complete captures are separate recordings.  Binding validates their fixed
            # layout; incomplete or unsafe entries remain unavailable rather than hiding
            # the healthy live recordings.
            if main_worktree is not None:
                preserved_root = main_worktree / ".coherence" / PRESERVED_DIRECTORY
                try:
                    entries = list(preserved_root.iterdir())
                except OSError:
                    entries = []
                for entry in sorted(entries, key=lambda item: item.name):
                    try:
                        reader = Reader.preserved(main_worktree, entry.name)
                    except (OSError, ReaderError, RecordingError):
                        continue
                    recordings.append(Recording(_opaque("recording", entry), "preserved", "available", reader, main_worktree))
            # Git common-directory identity, not branch/cwd/directory spelling, is the group.
            projects.append(Project(_opaque("project", common), "main", tuple(recordings), common))
        return tuple(sorted(projects, key=lambda project: project.ref))


__all__ = ["Project", "Projects", "Recording"]
