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
    def __init__(self, project, task, resume_facts=None):
        self.project, self.task = Path(project), task
        # This is history for reporting, not a continuation-admission baseline.
        self.base = git(project, 'rev-parse', 'HEAD').decode().strip()
        facts = resume_facts if isinstance(resume_facts, dict) else {}
        self.resumed_paths = set(facts.get('paths', []))
        self.task_edited = set(self.resumed_paths)
        self.known_artifacts = set(facts.get('artifacts', []))

    def command(self, phase, call):
        """Commands are never filesystem/Git admission points."""

    def _matches(self, name, paths):
        return any(name == path.rstrip('/') or name.startswith(path.rstrip('/') + '/') for path in paths)

    def claim(self, name):
        editable_path(self.project, name)
        # This is an actual write boundary, not a worktree snapshot: do not overwrite
        # bytes that were already modified when the task selected this path.
        limits = self.task.get('owned_paths')
        artifact = self._matches(name, self.task.get('generated_outputs', []))
        known = name in (self.known_artifacts if artifact else self.resumed_paths)
        if path_has_preexisting_changes(self.project, name) and not known:
            raise Blocked('pre-existing dirty path is not task-owned: ' + name)
        if limits is not None and not self._matches(name, limits) and not artifact:
            raise Blocked('path outside optional owned_paths: ' + name)
        if artifact:
            self.known_artifacts.add(name)
        else:
            self.task_edited.add(name)

    def cleanup_artifact(self, name):
        """Delete only one task-known generated file, never an output tree."""
        path = safe_path(self.project, name)
        if (name not in self.known_artifacts or not self._matches(name, self.task.get('generated_outputs', []))
                or not path.is_file()):
            raise Blocked('unsafe generated-artifact cleanup target: ' + name)
        path.unlink()

    def facts(self):
        return {'paths': sorted(self.task_edited), 'artifacts': sorted(self.known_artifacts)}

    def _checkpoint_result(self, sha, parent, owned):
        if git(self.project, 'rev-list', '--parents', '-n', '1', sha).decode().split() != [sha, parent]:
            raise Blocked('unexpected checkpoint parent; inspect actual commit')
        actual = set(filter(None, git(self.project, 'diff-tree', '--no-commit-id', '--name-only', '-r', '-z', sha).decode().split('\0')))
        if not actual or not actual <= set(owned):
            raise Blocked('commit changed unexpected paths; inspect actual commit')
        return {'baseline': self.base, 'sha': sha, 'paths': owned,
                'artifacts': sorted(self.known_artifacts), 'no_change': False}

    def checkpoint(self):
        # Only paths explicitly selected at an edit boundary are candidates.  Do not
        # discover, adopt, or stage arbitrary command output.
        owned = sorted(name for name in self.task_edited
                       if path_has_preexisting_changes(self.project, name))
        if not owned:
            return {'baseline': self.base, 'sha': self.base, 'paths': [],
                    'artifacts': sorted(self.known_artifacts), 'no_change': True}
        self.checkpoint_parent = git(self.project, 'rev-parse', 'HEAD').decode().strip()
        self.checkpoint_paths = owned
        git(self.project, 'diff', '--check', '--', *owned)
        git(self.project, 'add', '-A', '--', *owned)
        git(self.project, 'commit', '--only', '-m', 'workflow: ' + self.task['id'], '--', *owned)
        sha = git(self.project, 'rev-parse', 'HEAD').decode().strip()
        return self._checkpoint_result(sha, self.checkpoint_parent, owned)

    def reconcile_checkpoint(self):
        """Return only this operation's completed commit after a reported failure."""
        parent = getattr(self, 'checkpoint_parent', None)
        owned = getattr(self, 'checkpoint_paths', None)
        if not parent or not owned:
            return None
        sha = git(self.project, 'rev-parse', 'HEAD').decode().strip()
        if sha == parent:
            return None
        try:
            return self._checkpoint_result(sha, parent, owned)
        except Blocked:
            # A different incoming commit is not a continuation veto or this task's
            # checkpoint.  Leave it intact and correct the failed action instead.
            return None
