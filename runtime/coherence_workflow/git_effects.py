"""Action-scoped Git checkpoints that preserve unrelated work."""
from pathlib import Path
import os
import subprocess
import tempfile

from .store import Blocked, git, safe_path


def _commit_result(project, sha, parent, path):
    if git(project, 'rev-list', '--parents', '-n', '1', sha).decode().split() != [sha, parent]:
        raise Blocked('unexpected metric artifact commit parent; inspect actual commit')
    actual = set(filter(None, git(project, 'diff-tree', '--no-commit-id', '--name-only', '-r', '-z', sha).decode().split('\0')))
    if actual != {path}:
        raise Blocked('metric artifact commit changed unexpected paths; inspect actual commit')
    return {'sha': sha, 'parent': parent, 'path': path, 'no_change': False}


class MetricArtifactFinalizer:
    """One runner-only end-of-run commit for an already-reserved metric artifact."""
    def __init__(self, project, relative, validate, *, expected_identity=None, expected_bytes=None):
        self.project, self.relative, self.validate = Path(project), relative, validate
        self.parent = None
        path = safe_path(self.project, self.relative)
        if not path.is_file():
            raise Blocked('metric artifact is not a regular file; retain bytes and inspect it')
        info = path.stat(follow_symlinks=False)
        self.expected_identity = expected_identity or (info.st_dev, info.st_ino, info.st_ctime_ns)
        self.expected_bytes = path.read_bytes() if expected_bytes is None else expected_bytes

    def _verify_reserved(self, path):
        info = path.stat(follow_symlinks=False)
        if (info.st_dev, info.st_ino, info.st_ctime_ns) != self.expected_identity or path.read_bytes() != self.expected_bytes:
            raise Blocked('metric artifact drifted from the runner-reserved bytes; retain bytes and inspect it')

    def commit(self):
        path = safe_path(self.project, self.relative)
        if not path.is_file():
            raise Blocked('metric artifact is not a regular file; retain bytes and inspect it')
        self._verify_reserved(path)
        self.validate()
        if not path.read_bytes():
            return {'sha': git(self.project, 'rev-parse', 'HEAD').decode().strip(), 'parent': None,
                    'path': self.relative, 'no_change': True}
        status = git(self.project, 'status', '--porcelain=v1', '-z', '--', self.relative).decode('utf-8', 'replace')
        if not status.startswith('?? ' + self.relative + '\0'):
            raise Blocked('metric artifact is not a new unstaged owned file; retain bytes and inspect it')
        self.parent = git(self.project, 'rev-parse', 'HEAD').decode().strip()
        git(self.project, 'diff', '--check', '--', self.relative)
        git(self.project, 'add', '--', self.relative)
        staged = set(filter(None, git(self.project, 'diff', '--cached', '--name-only', '-z', '--', self.relative).decode().split('\0')))
        if staged != {self.relative}:
            raise Blocked('metric artifact index differs from the exact owned path; retain bytes and inspect it')
        self._verify_reserved(path)
        self.validate()
        if git(self.project, 'show', ':' + self.relative) != self.expected_bytes:
            raise Blocked('metric artifact bytes changed before commit; retain bytes and inspect it')
        git(self.project, 'commit', '--only', '-m', 'workflow: metrics', '--', self.relative)
        return _commit_result(self.project, git(self.project, 'rev-parse', 'HEAD').decode().strip(), self.parent, self.relative)

    def reconcile(self):
        if not self.parent:
            return None
        sha = git(self.project, 'rev-parse', 'HEAD').decode().strip()
        if sha == self.parent:
            return None
        try:
            return _commit_result(self.project, sha, self.parent, self.relative)
        except Blocked:
            return None


def path_has_preexisting_changes(project, name):
    """Check only a requested mutation target, never the worktree as admission."""
    return bool(git(project, 'status', '--porcelain=v1', '-z', '--', ':(literal)' + name))


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
        handoff = task.get('handoff_paths', [])
        if not isinstance(handoff, list) or any(not isinstance(name, str) or not name for name in handoff):
            raise Blocked('handoff_paths must be a list of exact nonempty file paths; correct the task input')
        self.handoff = {}
        # A persisted claim is an established exact transfer.  On continuation its
        # bytes may already contain the intended edit, so taking a fresh snapshot
        # would incorrectly require a second edit before checkpointing.
        self.resumed_handoffs = self.resumed_paths & set(handoff)
        for name in handoff:
            if name in self.handoff or name in self.resumed_handoffs:
                continue
            try:
                path = editable_path(self.project, name)
            except Blocked as exc:
                raise Blocked('cannot transfer handoff path ' + name + ': operation transfer requires an exact safe regular file; correct handoff_paths') from exc
            if not path.is_file() or not path_has_preexisting_changes(self.project, name):
                raise Blocked('cannot transfer ' + name + ' for handoff: operation transfer requires an explicitly named pre-existing regular dirty file')
            info = path.stat(follow_symlinks=False)
            self.handoff[name] = {'identity': (info.st_dev, info.st_ino, info.st_ctime_ns), 'bytes': path.read_bytes()}

    def _verify_handoff(self, name):
        expected = self.handoff[name]
        try:
            path = editable_path(self.project, name)
        except Blocked as exc:
            raise Blocked('cannot claim handoff path ' + name + ': operation claim requires the authorized safe regular file; restore it and retry') from exc
        if not path.is_file():
            raise Blocked('cannot claim handoff path ' + name + ': operation claim requires the authorized regular file; restore it and retry')
        info = path.stat(follow_symlinks=False)
        if ((info.st_dev, info.st_ino, info.st_ctime_ns) != expected['identity'] or
                path.read_bytes() != expected['bytes']):
            raise Blocked('cannot claim handoff path ' + name + ': operation claim found changed pre-transfer bytes; restore the authorized bytes or supply a current exact handoff_paths entry')

    def command(self, phase, call):
        """Commands are never filesystem/Git admission points."""

    def _matches(self, name, paths):
        return any(name == path.rstrip('/') or name.startswith(path.rstrip('/') + '/') for path in paths)

    def claim(self, name):
        handoff = name in self.handoff
        try:
            editable_path(self.project, name)
        except Blocked as exc:
            if handoff:
                raise Blocked('cannot claim handoff path ' + name + ': operation claim requires the authorized safe regular file; restore it and retry') from exc
            raise
        # This is an actual write boundary, not a worktree snapshot: do not overwrite
        # bytes that were already modified when the task selected this path.
        limits = self.task.get('owned_paths')
        artifact = self._matches(name, self.task.get('generated_outputs', []))
        known = name in (self.known_artifacts if artifact else self.resumed_paths)
        if handoff:
            self._verify_handoff(name)
        if path_has_preexisting_changes(self.project, name) and not (known or handoff):
            raise Blocked('cannot claim pre-existing dirty path ' + name + ': operation claim requires an exact handoff_paths entry; broad owned_paths coverage is not transfer authority')
        if limits is not None and not self._matches(name, limits) and not artifact:
            raise Blocked('path outside optional owned_paths: ' + name)
        if artifact:
            self.known_artifacts.add(name)
        else:
            self.task_edited.add(name)

    def accept_completed_handoff(self, source_state):
        """Transfer exact owner-selected already-complete bytes, without a fake edit."""
        import hashlib
        import stat
        if not source_state or set(source_state) != set(self.handoff):
            raise Blocked('external recovery needs exact handoff paths; supply the completed file transfer')
        for name, expected in source_state.items():
            self.claim(name)
            if name not in self.task_edited:
                raise Blocked('external recovery cannot checkpoint generated artifact ' + name + '; transfer source deliverables only')
            path = editable_path(self.project, name)
            actual = {'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                      'mode': stat.S_IMODE(path.stat().st_mode)}
            if actual != expected:
                raise Blocked('external recovery bytes drifted for ' + name + '; inspect and authorize the current exact transfer')
        self.completed_handoff = source_state

    def cleanup_artifact(self, name):
        """Delete only one task-known generated file, never an output tree."""
        path = safe_path(self.project, name)
        if (name not in self.known_artifacts or not self._matches(name, self.task.get('generated_outputs', []))
                or not path.is_file()):
            raise Blocked('unsafe generated-artifact cleanup target: ' + name)
        path.unlink()

    def facts(self):
        # Report the current task's explicit transfer input.  A persisted claimed
        # path, not this report, establishes a handoff during continuation.
        return {'paths': sorted(self.task_edited), 'artifacts': sorted(self.known_artifacts),
                'handoff_paths': sorted(set(self.handoff) | self.resumed_handoffs)}

    def _checkpoint_result(self, sha, parent, owned):
        if git(self.project, 'rev-list', '--parents', '-n', '1', sha).decode().split() != [sha, parent]:
            raise Blocked('unexpected checkpoint parent; inspect actual commit')
        actual = set(filter(None, git(self.project, 'diff-tree', '--no-commit-id', '--no-renames', '--name-only', '-r', '-z', sha).decode().split('\0')))
        if not actual or not actual <= set(owned):
            raise Blocked('commit changed unexpected paths; inspect actual commit')
        return {'baseline': self.base, 'sha': sha, 'paths': owned,
                'artifacts': sorted(self.known_artifacts), 'no_change': False}

    def checkpoint(self, before_commit=None):
        self.git_commit_started = False
        for attribute in ('checkpoint_parent', 'checkpoint_paths', 'checkpoint_entries'):
            if hasattr(self, attribute):
                delattr(self, attribute)
        # Only paths explicitly selected at an edit boundary are candidates.  Do not
        # discover, adopt, or stage arbitrary command output.
        owned = sorted(name for name in self.task_edited
                       if path_has_preexisting_changes(self.project, name))
        completed = getattr(self, 'completed_handoff', {})
        if completed:
            self.accept_completed_handoff(completed)
        for name in (set(owned) & set(self.handoff)) - set(completed):
            if editable_path(self.project, name).read_bytes() == self.handoff[name]['bytes']:
                raise Blocked('cannot checkpoint handoff path ' + name + ': operation checkpoint found no intended edit; make the intended correction or do not claim the transfer')
        before_commit = before_commit or getattr(self, 'before_checkpoint', None)
        if not owned:
            head = git(self.project, 'rev-parse', 'HEAD').decode().strip()
            intent = {'baseline': self.base, 'parent': head, 'paths': [],
                      'artifacts': sorted(self.known_artifacts), 'entries': {}, 'no_change': True}
            if before_commit:
                before_commit(intent)
            return {'baseline': self.base, 'sha': head, 'paths': [],
                    'artifacts': sorted(self.known_artifacts), 'no_change': True}
        self.checkpoint_parent = git(self.project, 'rev-parse', 'HEAD').decode().strip()
        self.checkpoint_paths = owned
        specs = [':(literal)' + name for name in owned]
        git(self.project, 'diff', '--check', '--', *specs)
        # Preview only these paths in a private temporary index.  The real index is
        # untouched until the durable intent has been written.
        with tempfile.TemporaryDirectory(prefix='coherence-git-preview-') as directory:
            env = os.environ.copy()
            env['GIT_INDEX_FILE'] = str(Path(directory) / 'index')
            def preview(*args):
                result = subprocess.run(['git', '--no-optional-locks', '-C', str(self.project), *args],
                                        env=env, capture_output=True)
                if result.returncode:
                    raise Blocked('Git checkpoint preview failed: ' + result.stderr.decode(errors='replace'))
                return result.stdout
            preview('read-tree', self.checkpoint_parent)
            preview('add', '-A', '--', *specs)
            changed = sorted(filter(None, preview('diff', '--cached', '--no-renames', '--name-only', '-z',
                                                  self.checkpoint_parent, '--', *specs).decode().split('\0')))
            entries = self._index_entries(changed, preview)
        if not changed:
            intent = {'baseline': self.base, 'parent': self.checkpoint_parent, 'paths': [],
                      'artifacts': sorted(self.known_artifacts), 'entries': {}, 'no_change': True}
            if before_commit:
                before_commit(intent)
            return {'baseline': self.base, 'sha': self.checkpoint_parent, 'paths': [],
                    'artifacts': sorted(self.known_artifacts), 'no_change': True}
        self.checkpoint_paths = changed
        self.checkpoint_entries = entries
        intent = {'baseline': self.base, 'parent': self.checkpoint_parent, 'paths': changed,
                  'artifacts': sorted(self.known_artifacts), 'entries': entries}
        if before_commit:
            before_commit(intent)
        if git(self.project, 'rev-parse', 'HEAD').decode().strip() != self.checkpoint_parent:
            raise Blocked('checkpoint parent changed before commit; inspect Git effects before continuation')
        changed_specs = [':(literal)' + name for name in changed]
        git(self.project, 'add', '-A', '--', *changed_specs)
        if self._index_entries(changed, lambda *args: git(self.project, *args)) != entries:
            raise Blocked('checkpoint selected content changed before commit; preserve work and inspect it')
        attempting = getattr(self, 'before_git_commit', None)
        if attempting:
            attempting()
        if git(self.project, 'rev-parse', 'HEAD').decode().strip() != self.checkpoint_parent:
            raise Blocked('checkpoint parent changed before commit; inspect Git effects before continuation')
        self.git_commit_started = True
        git(self.project, 'commit', '--only', '-m', 'workflow: ' + self.task['id'], '--', *changed_specs)
        sha = git(self.project, 'rev-parse', 'HEAD').decode().strip()
        return self._checkpoint_result_exact(sha, intent)

    @staticmethod
    def _index_entries(paths, run):
        entries = {}
        for name in paths:
            raw = run('ls-files', '--stage', '-z', '--', ':(literal)' + name)
            records = [row for row in raw.split(b'\0') if row]
            if not records:
                entries[name] = None
            elif len(records) == 1:
                header, actual = records[0].split(b'\t', 1)
                mode, oid, stage = header.decode('ascii').split()
                if actual.decode() != name or stage != '0':
                    raise Blocked('checkpoint index is uncertain for ' + name + '; inspect selected entries')
                entries[name] = [mode, oid]
            else:
                raise Blocked('checkpoint index is unmerged for ' + name + '; resolve it before checkpoint')
        return entries

    def _checkpoint_result_exact(self, sha, intent):
        result = self._checkpoint_result(sha, intent['parent'], intent['paths'])
        actual_paths = sorted(filter(None, git(self.project, 'diff-tree', '--no-commit-id', '--no-renames',
            '--name-only', '-r', '-z', sha).decode().split('\0')))
        if actual_paths != intent['paths'] or set(intent['entries']) != set(actual_paths):
            raise Blocked('checkpoint paths differ from retained intent; inspect Git effects before continuation')
        for name, expected in intent['entries'].items():
            raw = git(self.project, 'ls-tree', '-z', sha, '--', ':(literal)' + name)
            records = [row for row in raw.split(b'\0') if row]
            actual = None
            if records:
                if len(records) != 1:
                    raise Blocked('checkpoint tree is uncertain for ' + name + '; inspect Git effects')
                header, path = records[0].split(b'\t', 1)
                mode, _kind, oid = header.decode('ascii').split()
                if path.decode() != name:
                    raise Blocked('checkpoint tree path mismatch for ' + name + '; inspect Git effects')
                actual = [mode, oid]
            if actual != expected:
                raise Blocked('checkpoint content or mode differs for ' + name + '; preserve work and inspect Git effects')
        return {**result, 'baseline': intent['baseline'], 'paths': intent['paths'],
                'artifacts': intent['artifacts'], 'parent': intent['parent']}

    def reconcile_intent(self, intent):
        """Find the unique direct child on current ancestry, or stop on uncertainty."""
        parent = intent['parent']
        head = git(self.project, 'rev-parse', 'HEAD').decode().strip()
        if head == parent:
            return None
        try:
            git(self.project, 'merge-base', '--is-ancestor', parent, head)
        except Blocked as exc:
            raise Blocked('checkpoint parent is not an ancestor of HEAD; preserve work and inspect Git effects') from exc
        lines = git(self.project, 'rev-list', '--parents', parent + '..' + head).decode().splitlines()
        children = [parts[0] for line in lines if (parts := line.split()) and parts[1:] == [parent]]
        if len(children) != 1:
            raise Blocked('checkpoint direct child is missing or ambiguous; preserve work and inspect Git effects')
        return self._checkpoint_result_exact(children[0], intent)

    def reconcile_checkpoint(self):
        """Return only this operation's completed commit after a reported failure."""
        parent = getattr(self, 'checkpoint_parent', None)
        owned = getattr(self, 'checkpoint_paths', None)
        if not parent or not owned:
            return None
        if hasattr(self, 'checkpoint_entries'):
            if not getattr(self, 'git_commit_started', False):
                return None
            return self.reconcile_intent({'baseline': self.base, 'parent': parent, 'paths': owned,
                'artifacts': sorted(self.known_artifacts), 'entries': self.checkpoint_entries})
        sha = git(self.project, 'rev-parse', 'HEAD').decode().strip()
        if sha == parent:
            return None
        try:
            return self._checkpoint_result(sha, parent, owned)
        except Blocked:
            # A different incoming commit is not a continuation veto or this task's
            # checkpoint.  Leave it intact and correct the failed action instead.
            return None
