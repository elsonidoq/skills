"""Action-scoped Git checkpoints that preserve unrelated work."""
from pathlib import Path

from .store import Blocked, git, safe_path


def path_has_preexisting_changes(project, name):
    """Check only a requested mutation target, never the worktree as admission."""
    return bool(git(project, 'status', '--porcelain=v1', '-z', '--', name))


def editable_path(project, name):
    if name.split('/')[0] in ('.git', '.coherence'):
        raise Blocked('task edits cannot target Git/workflow state: ' + name)
    return safe_path(project, name)


class FocusedGit:
    def __init__(self, project, task):
        self.project, self.task = Path(project), task
        # This is history for reporting, not a continuation-admission baseline.
        self.base = git(project, 'rev-parse', 'HEAD').decode().strip()
        self.task_edited = set()
        self.known_artifacts = set()

    def command(self, phase, call):
        """Commands are never filesystem/Git admission points."""

    def _matches(self, name, paths):
        return any(name == path.rstrip('/') or name.startswith(path.rstrip('/') + '/') for path in paths)

    def claim(self, name):
        editable_path(self.project, name)
        # This is an actual write boundary, not a worktree snapshot: do not overwrite
        # bytes that were already modified when the task selected this path.
        if path_has_preexisting_changes(self.project, name):
            raise Blocked('pre-existing dirty path is not task-owned: ' + name)
        limits = self.task.get('owned_paths')
        artifact = self._matches(name, self.task.get('generated_outputs', []))
        if limits is not None and not self._matches(name, limits) and not artifact:
            raise Blocked('path outside optional owned_paths: ' + name)
        if artifact:
            self.known_artifacts.add(name)
        else:
            self.task_edited.add(name)

    def checkpoint(self):
        # Only paths explicitly selected at an edit boundary are candidates.  Do not
        # discover, adopt, or stage arbitrary command output.
        # A claimed path that ends unchanged needs no empty checkpoint.  This is a
        # per-selected-path Git query, not discovery of other worktree changes.
        owned = sorted(name for name in self.task_edited
                       if path_has_preexisting_changes(self.project, name))
        if not owned:
            return {'baseline': self.base, 'sha': self.base, 'paths': [],
                    'artifacts': sorted(self.known_artifacts), 'no_change': True}
        git(self.project, 'diff', '--check', '--', *owned)
        before_commit = git(self.project, 'rev-parse', 'HEAD').decode().strip()
        git(self.project, 'add', '-A', '--', *owned)
        git(self.project, 'commit', '--only', '-m', 'workflow: ' + self.task['id'], '--', *owned)
        sha = git(self.project, 'rev-parse', 'HEAD').decode().strip()
        if git(self.project, 'rev-list', '--parents', '-n', '1', sha).decode().split() != [sha, before_commit]:
            raise Blocked('unexpected checkpoint parent; inspect actual commit')
        actual = set(filter(None, git(self.project, 'diff-tree', '--no-commit-id', '--name-only', '-r', '-z', sha).decode().split('\0')))
        if not actual or not actual <= set(owned):
            raise Blocked('commit changed unexpected paths; inspect actual commit')
        return {'baseline': self.base, 'sha': sha, 'paths': owned,
                'artifacts': sorted(self.known_artifacts), 'no_change': False}
