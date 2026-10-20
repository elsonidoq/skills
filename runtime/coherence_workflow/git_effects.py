"""Focused Git checkpoints without effect intents or custom hook admission."""
import hashlib
import os
from pathlib import Path
import stat

from .store import Blocked, git, safe_path


def changed_paths(project):
    records = git(project, 'status', '--porcelain=v1', '-z', '--untracked-files=all', '--', '.',
                  ':(exclude).coherence').split(b'\0')
    result = set()
    index = 0
    while index < len(records):
        record = records[index]
        index += 1
        if not record:
            continue
        result.add(record[3:].decode())
        if b'R' in record[:2] or b'C' in record[:2]:
            result.add(records[index].decode())
            index += 1
    return result


def file_state(project, name):
    # Observe unrelated dirty entries without following symlinks or opening FIFOs.
    path = Path(project) / name
    try:
        info = path.lstat()
    except FileNotFoundError:
        return None
    if stat.S_ISLNK(info.st_mode):
        return (info.st_mode, os.readlink(path))
    if not stat.S_ISREG(info.st_mode):
        return (info.st_mode, info.st_dev, info.st_ino)
    with path.open('rb') as source:
        value = hashlib.file_digest(source, 'sha256').hexdigest() if hasattr(hashlib, 'file_digest') else _file_hash(source)
    return (info.st_mode, value)


def _file_hash(source):
    value = hashlib.sha256()
    for chunk in iter(lambda: source.read(65536), b''):
        value.update(chunk)
    return value.hexdigest()


def index_entries(raw, exclude):
    return [record for record in raw.split(b'\0') if record and record.split(b'\t', 1)[1].decode() not in exclude]


def editable_path(project, name):
    if name.split('/')[0] in ('.git', '.coherence'):
        raise Blocked('task edits cannot target Git/workflow state: ' + name)
    return safe_path(project, name)


class FocusedGit:
    def __init__(self, project, task):
        self.project, self.task = Path(project), task
        self.base = git(project, 'rev-parse', 'HEAD').decode().strip()
        self.index = git(project, 'ls-files', '--stage', '-z')
        self.dirty = {p: file_state(project, p) for p in changed_paths(project)}
        self.claimed = set()
        self.command_before = {}

    def command(self, phase, call):
        if phase == 'start':
            if not self.command_before:
                self.inspect()
            self.command_before[call] = {p: file_state(self.project, p) for p in changed_paths(self.project)}
        else:
            before = self.command_before.pop(call)
            for name in changed_paths(self.project):
                if name not in before or file_state(self.project, name) != before[name]:
                    self.claim(name)

    def claim(self, name):
        editable_path(self.project, name)
        if name in self.dirty:
            raise Blocked('pre-existing dirty path is not task-owned: ' + name)
        limits = self.task.get('owned_paths')
        if limits is not None and not any(name == p or name.startswith(p.rstrip('/') + '/') for p in limits):
            raise Blocked('path outside optional owned_paths: ' + name)
        self.claimed.add(name)

    def inspect(self):
        if git(self.project, 'rev-parse', 'HEAD').decode().strip() != self.base:
            raise Blocked('HEAD changed during task; inspect before any commit')
        if git(self.project, 'ls-files', '--stage', '-z') != self.index:
            raise Blocked('index changed during task; preserve and inspect before any commit')
        for name, before in self.dirty.items():
            if file_state(self.project, name) != before:
                raise Blocked('pre-existing work changed; preserve and inspect: ' + name)
        owned = changed_paths(self.project) - self.dirty.keys()
        if not owned <= self.claimed:
            raise Blocked('unclaimed changes appeared during task; preserve and inspect: ' + ', '.join(sorted(owned - self.claimed)))
        for name in owned:
            editable_path(self.project, name)
        return sorted(owned)

    def checkpoint(self):
        owned = self.inspect()
        if not owned:
            return {'baseline': self.base, 'sha': self.base, 'paths': [], 'no_change': True}
        git(self.project, 'diff', '--check', '--', *owned)
        git(self.project, 'add', '-A', '--', *owned)
        git(self.project, 'commit', '--only', '-m', 'workflow: ' + self.task['id'], '--', *owned)
        sha = git(self.project, 'rev-parse', 'HEAD').decode().strip()
        if git(self.project, 'rev-list', '--parents', '-n', '1', sha).decode().split() != [sha, self.base]:
            raise Blocked('unexpected checkpoint parent; inspect actual commit')
        actual = set(filter(None, git(self.project, 'diff-tree', '--no-commit-id', '--name-only', '-r', '-z', sha).decode().split('\0')))
        if not actual or not actual <= set(owned):
            raise Blocked('commit changed unexpected paths; inspect actual commit')
        if index_entries(git(self.project, 'ls-files', '--stage', '-z'), owned) != index_entries(self.index, owned):
            raise Blocked('unrelated index changed during commit; inspect hook output')
        if changed_paths(self.project) - self.dirty.keys():
            raise Blocked('task-owned changes remain after commit; inspect hook output')
        for name, before in self.dirty.items():
            if file_state(self.project, name) != before:
                raise Blocked('unrelated work changed during commit: ' + name)
        return {'baseline': self.base, 'sha': sha, 'paths': owned, 'no_change': False}
