"""Action-scoped Git checkpoints that preserve unrelated work."""
from pathlib import Path
import base64
import difflib
import os
import stat
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
        self.edit_only = dict(facts.get('edit_only', {}))
        self.edit_only_authority = set(self.edit_only)
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

    def authorize_edit_only(self, names):
        """Coordinator grants exact dirty paths, never whole-file transfer."""
        if not isinstance(names, list) or any(not isinstance(n, str) or not n for n in names) or len(set(names)) != len(names):
            raise Blocked('edit-only authority requires distinct exact paths; correct the continuation answer')
        for name in names:
            if name in self.handoff or name in self.resumed_handoffs:
                raise Blocked('edit-only authority conflicts with handoff for ' + name)
            limits = self.task.get('owned_paths')
            if limits is not None and not self._matches(name, limits):
                raise Blocked('edit-only path outside owned_paths: ' + name)
            if self._matches(name, self.task.get('generated_outputs', [])):
                raise Blocked('edit-only authority requires source, not generated output: ' + name)
            editable_path(self.project, name)
            if name in self.resumed_paths and name not in self.edit_only:
                raise Blocked('edit-only path already has a different claim: ' + name)
        self.edit_only_authority.update(names)

    def _index_entry(self, name):
        return git(self.project, 'ls-files', '--stage', '-z', '--', name)

    def _snapshot_edit_only(self, name):
        path = editable_path(self.project, name)
        if not path.is_file() or not path_has_preexisting_changes(self.project, name):
            raise Blocked('edit-only claim requires an exact dirty regular tracked file: ' + name)
        entry = self._index_entry(name)
        head = git(self.project, 'ls-tree', '-z', 'HEAD', '--', name)
        if not entry or not head or b'\0' in entry[:-1] or b'\0' in head[:-1]:
            raise Blocked('edit-only claim requires one tracked stage-zero file: ' + name)
        index_meta, index_name = entry[:-1].split(b'\t', 1)
        head_meta, head_name = head[:-1].split(b'\t', 1)
        mode, blob, stage = index_meta.split()
        head_mode, kind, head_blob = head_meta.split()
        if (index_name != os.fsencode(name) or head_name != index_name or stage != b'0' or kind != b'blob'
                or mode not in (b'100644', b'100755') or mode != head_mode or blob != head_blob):
            raise Blocked('edit-only claim requires index equal to HEAD for ' + name + '; preserve staged changes and inspect')
        actual_mode = stat.S_IMODE(path.stat(follow_symlinks=False).st_mode)
        if bool(actual_mode & 0o111) != (mode == b'100755'):
            raise Blocked('edit-only claim refuses inherited mode change for ' + name)
        return {'start': base64.b64encode(path.read_bytes()).decode('ascii'),
                'mode': actual_mode, 'blob': blob.decode(), 'git_mode': mode.decode()}

    def _edit_candidate(self, name):
        fact = self.edit_only[name]
        path = editable_path(self.project, name)
        if not path.is_file() or stat.S_IMODE(path.stat(follow_symlinks=False).st_mode) != fact['mode']:
            raise Blocked('edit-only checkpoint found file or mode drift for ' + name + '; preserve it and inspect')
        expected = (fact['git_mode'] + ' ' + fact['blob'] + ' 0\t' + name + '\0').encode()
        if self._index_entry(name) != expected or git(self.project, 'ls-tree', '-z', 'HEAD', '--', name) != (fact['git_mode'] + ' blob ' + fact['blob'] + '\t' + name + '\0').encode():
            raise Blocked('edit-only checkpoint found HEAD/index drift for ' + name + '; preserve it and inspect')
        try:
            start = base64.b64decode(fact['start'], validate=True)
        except (KeyError, ValueError, TypeError) as exc:
            raise Blocked('edit-only checkpoint has invalid saved baseline for ' + name) from exc
        head = git(self.project, 'cat-file', 'blob', fact['blob'])
        work = path.read_bytes()
        if any(b'\0' in data for data in (head, start, work)):
            raise Blocked('edit-only checkpoint cannot attribute binary changes in ' + name)
        h, s, w = [data.splitlines(keepends=True) for data in (head, start, work)]
        hs = difflib.SequenceMatcher(None, h, s, autojunk=False).get_opcodes()
        sw = difflib.SequenceMatcher(None, s, w, autojunk=False).get_opcodes()
        edits = []
        for tag, a, b, c, d in sw:
            if tag == 'equal':
                continue
            matches = [(i + a - x, i + b - x) for kind, i, j, x, y in hs
                       if kind == 'equal' and x <= a <= b <= y and (a != b or x < a < y)]
            # Insertion at a file boundary is safe only if that boundary is not inherited.
            if a == b and not matches:
                if a == 0 and hs and hs[0][0] == 'equal': matches = [(0, 0)]
                if a == len(s) and hs and hs[-1][0] == 'equal': matches = [(len(h), len(h))]
            if len(matches) != 1:
                raise Blocked('edit-only checkpoint has overlapping or ambiguous changes in ' + name + '; separate the edits and retry')
            left, right = matches[0]
            if a == b:
                anchors = s[max(0, a - 1):min(len(s), a + 1)]
                if not anchors or any(s.count(line) != 1 or h.count(line) != 1 for line in anchors):
                    raise Blocked('edit-only checkpoint has ambiguous insertion in ' + name + '; separate the edits and retry')
            # Repeated lines have multiple possible attributions, even if a diff picked one.
            if a != b and any(s.count(line) != 1 or h.count(line) != 1 for line in s[a:b]):
                raise Blocked('edit-only checkpoint has ambiguous repeated lines in ' + name + '; separate the edits and retry')
            edits.append((left, right, w[c:d]))
        candidate = h[:]
        for left, right, replacement in reversed(edits):
            candidate[left:right] = replacement
        result = b''.join(candidate)
        if result == head:
            raise Blocked('edit-only checkpoint has no attributable task change in ' + name + '; inspect the claim')
        return result

    def materialize_candidates(self, directory):
        """Write task-only files outside the checkout for independent checks."""
        directory = Path(directory).resolve()
        if directory == self.project.resolve() or directory.is_relative_to(self.project.resolve()):
            raise Blocked('candidate materialization needs a directory outside the checkout')
        if not directory.is_dir():
            raise Blocked('candidate materialization requires an existing external directory')
        for name in sorted(self.task_edited):
            target = safe_path(directory, name)
            source = editable_path(self.project, name)
            if name in self.edit_only:
                content, mode = self._edit_candidate(name), self.edit_only[name]['mode']
            elif source.is_file():
                content, mode = source.read_bytes(), stat.S_IMODE(source.stat().st_mode)
            elif not source.exists():
                if target.exists():
                    if not target.is_file():
                        raise Blocked('candidate materialization cannot remove non-file ' + name)
                    target.unlink()
                continue
            else:
                raise Blocked('candidate materialization requires a regular source file: ' + name)
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists():
                if not target.is_file():
                    raise Blocked('candidate materialization requires a regular target: ' + name)
                target.unlink()
            target.write_bytes(content)
            target.chmod(mode)

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
        edit_only = name in self.edit_only_authority
        if edit_only and name not in self.edit_only:
            self.edit_only[name] = self._snapshot_edit_only(name)
        if path_has_preexisting_changes(self.project, name) and not (known or handoff or edit_only):
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
                'handoff_paths': sorted(set(self.handoff) | self.resumed_handoffs),
                'edit_only': self.edit_only}

    def _checkpoint_result(self, sha, parent, owned):
        if git(self.project, 'rev-list', '--parents', '-n', '1', sha).decode().split() != [sha, parent]:
            raise Blocked('unexpected checkpoint parent; inspect actual commit')
        actual = set(filter(None, git(self.project, 'diff-tree', '--no-commit-id', '--name-only', '-r', '-z', sha).decode().split('\0')))
        if not actual or not actual <= set(owned):
            raise Blocked('commit changed unexpected paths; inspect actual commit')
        return {'baseline': self.base, 'sha': sha, 'paths': owned,
                'artifacts': sorted(self.known_artifacts), 'no_change': False}

    def _candidate_git(self, index, *args, data=None, worktree=None):
        # Validate ambient authority before setting the runner-owned temporary index.
        git(self.project, 'rev-parse', '--git-dir')
        env = os.environ.copy()
        env['GIT_INDEX_FILE'] = str(index)
        if worktree is not None:
            env['GIT_WORK_TREE'] = str(worktree)
        result = subprocess.run(['git', '--no-optional-locks', '-C', str(self.project), *args],
                                input=data, capture_output=True, env=env)
        if result.returncode:
            raise Blocked('Git operation failed: ' + result.stderr.decode(errors='replace'))
        return result.stdout

    def _advance_real_index(self):
        records = []
        for name, before in self.checkpoint_index.items():
            current = self._index_entry(name)
            entry = git(self.project, 'ls-tree', '-z', self.checkpoint_sha, '--', name)
            if entry:
                meta, actual_name = entry[:-1].split(b'\t', 1)
                mode, kind, blob = meta.split()
                if kind != b'blob' or actual_name != os.fsencode(name):
                    raise Blocked('edit-only checkpoint found unexpected committed entry for ' + name)
                after = mode + b' ' + blob + b' 0\t' + actual_name + b'\0'
            else:
                after = b''
            if current not in (before, after):
                raise Blocked('edit-only checkpoint found index drift for ' + name + '; preserve it and inspect')
            if current != after:
                records.append(after if after else b'0 ' + b'0' * len(self.checkpoint_parent) + b'\t' + os.fsencode(name) + b'\0')
        if records:
            git(self.project, 'rev-parse', '--git-dir')
            result = subprocess.run(['git', '--no-optional-locks', '-C', str(self.project), 'update-index', '-z', '--index-info'],
                                    input=b''.join(records), capture_output=True)
            if result.returncode:
                raise Blocked('edit-only checkpoint could not advance real index: ' + result.stderr.decode(errors='replace'))

    def _checkpoint_edit_only(self, owned):
        self.checkpoint_parent = git(self.project, 'rev-parse', 'HEAD').decode().strip()
        self.checkpoint_paths = owned
        self.checkpoint_index = {name: self._index_entry(name) for name in owned}
        if git(self.project, 'diff', '--cached', '--name-only', '-z', self.checkpoint_parent, '--', *owned):
            raise Blocked('edit-only checkpoint found staged changes on owned paths; preserve the index and inspect')
        candidates = {name: self._edit_candidate(name) for name in owned if name in self.edit_only}
        work = {name: (editable_path(self.project, name).read_bytes(),
                       stat.S_IMODE(editable_path(self.project, name).stat().st_mode))
                for name in owned if editable_path(self.project, name).is_file()}
        with tempfile.TemporaryDirectory(prefix='coherence-index-') as temp:
            index = Path(temp) / 'index'
            self._candidate_git(index, 'read-tree', self.checkpoint_parent)
            ordinary = [name for name in owned if name not in candidates]
            if ordinary:
                self._candidate_git(index, 'add', '-A', '--', *ordinary)
            for name, content in candidates.items():
                raw = self._candidate_git(index, 'hash-object', '-w', '--stdin', data=content).decode().strip()
                filtered = self._candidate_git(index, 'hash-object', '--path=' + name, '--stdin', data=content).decode().strip()
                if raw != filtered:
                    raise Blocked('edit-only checkpoint cannot attribute Git-filtered content for ' + name + '; inspect filters')
                self._candidate_git(index, 'update-index', '--add', '--cacheinfo', self.edit_only[name]['git_mode'], raw, name)
            self.checkpoint_tree = self._candidate_git(index, 'write-tree').decode().strip()
            parent_tree = git(self.project, 'rev-parse', self.checkpoint_parent + '^{tree}').decode().strip()
            if self.checkpoint_tree == parent_tree:
                raise Blocked('edit-only checkpoint has no task-only changes; inspect the claimed edits')
            self._candidate_git(index, 'diff', '--cached', '--check', self.checkpoint_parent, '--', *owned)
            for name in owned:
                if self._index_entry(name) != self.checkpoint_index[name]:
                    raise Blocked('edit-only checkpoint found index drift for ' + name + '; preserve it and inspect')
                path = editable_path(self.project, name)
                current = (path.read_bytes(), stat.S_IMODE(path.stat().st_mode)) if path.is_file() else None
                if current != work.get(name):
                    raise Blocked('edit-only checkpoint found worktree drift for ' + name + '; preserve it and inspect')
            if git(self.project, 'rev-parse', 'HEAD').decode().strip() != self.checkpoint_parent:
                raise Blocked('edit-only checkpoint found HEAD drift; preserve state and inspect')
            candidate_worktree = Path(temp) / 'source'
            candidate_worktree.mkdir()
            self._candidate_git(index, 'checkout-index', '--all', '--prefix=' + str(candidate_worktree) + '/')
            callback = getattr(self, 'checkpoint_intent', None)
            if callback:
                callback({'parent': self.checkpoint_parent, 'tree': self.checkpoint_tree, 'paths': owned})
            self._candidate_git(index, 'commit', '-m', 'workflow: ' + self.task['id'], worktree=candidate_worktree)
        return self._reconcile_edit_only()

    def _reconcile_edit_only(self):
        sha = git(self.project, 'rev-parse', 'HEAD').decode().strip()
        if sha == self.checkpoint_parent:
            return None
        if git(self.project, 'rev-parse', sha + '^{tree}').decode().strip() != self.checkpoint_tree:
            raise Blocked('edit-only checkpoint found unexpected commit tree; preserve state and inspect')
        result = self._checkpoint_result(sha, self.checkpoint_parent, self.checkpoint_paths)
        self.checkpoint_sha = sha
        self._advance_real_index()
        return result

    def checkpoint(self):
        # Only paths explicitly selected at an edit boundary are candidates.  Do not
        # discover, adopt, or stage arbitrary command output.
        owned = sorted(name for name in self.task_edited
                       if name in self.edit_only or path_has_preexisting_changes(self.project, name))
        completed = getattr(self, 'completed_handoff', {})
        if completed:
            self.accept_completed_handoff(completed)
        for name in (set(owned) & set(self.handoff)) - set(completed):
            if editable_path(self.project, name).read_bytes() == self.handoff[name]['bytes']:
                raise Blocked('cannot checkpoint handoff path ' + name + ': operation checkpoint found no intended edit; make the intended correction or do not claim the transfer')
        if not owned:
            return {'baseline': self.base, 'sha': self.base, 'paths': [],
                    'artifacts': sorted(self.known_artifacts), 'no_change': True}
        if set(owned) & set(self.edit_only):
            return self._checkpoint_edit_only(owned)
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
        if hasattr(self, 'checkpoint_tree'):
            return self._reconcile_edit_only()
        try:
            return self._checkpoint_result(sha, parent, owned)
        except Blocked:
            # A different incoming commit is not a continuation veto or this task's
            # checkpoint.  Leave it intact and correct the failed action instead.
            return None
