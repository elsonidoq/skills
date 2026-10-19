"""Approved delegated cgroup-v2 own children, not a hostile same-UID sandbox."""
import os
from pathlib import Path
import re
import time
import uuid

from .store import Blocked


def boot_id():
    return Path('/proc/sys/kernel/random/boot_id').read_text().strip()


def process_identity(pid, nonce):
    try:
        text = Path(f'/proc/{pid}/stat').read_text()
        fields = text[text.rindex(')') + 2:].split()
        return {'pid': pid, 'start': fields[19], 'boot': boot_id(), 'nonce': nonce,
                'uid': Path(f'/proc/{pid}').stat().st_uid, 'ppid': int(fields[1])}
    except (OSError, ValueError, IndexError) as exc:
        raise Blocked('process identity unavailable') from exc


def validate_process(identity, nonce):
    if not isinstance(identity, dict) or identity.get('nonce') != nonce:
        raise Blocked('process nonce mismatch')
    observed = process_identity(identity['pid'], nonce)
    if observed != identity or observed['uid'] != os.getuid():
        raise Blocked('boot/PID/start/UID/parent identity mismatch')


def stat_identity(path):
    s = path.lstat()
    if path.is_symlink() or not path.is_dir():
        raise Blocked('invalid containment directory')
    return {'uid': s.st_uid, 'device': s.st_dev, 'inode': s.st_ino}


class Cgroup:
    def __init__(self, approved_parent):
        self.parent = Path(approved_parent)
        if not self.parent.is_absolute() or self.parent != self.parent.resolve(strict=True):
            raise Blocked('containment parent must be canonical')
        self.parent_identity = stat_identity(self.parent)
        if (not self.parent.is_relative_to('/sys/fs/cgroup') or
            self.parent_identity['device'] != Path('/sys/fs/cgroup').stat().st_dev or
            self.parent_identity['uid'] != os.getuid() or not (self.parent/'cgroup.controllers').is_file()):
            raise Blocked('approved owned cgroup-v2 delegation unavailable')

    def _parent(self):
        if stat_identity(self.parent) != self.parent_identity:
            raise Blocked('containment parent identity drift')

    def reserve_name(self):
        return 'coherence-' + str(uuid.uuid4())

    def _path(self, name):
        self._parent()
        if not re.fullmatch(r'coherence-[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}', name):
            raise Blocked('not a fresh own-child scope name')
        return self.parent / name

    def create(self, name):
        path = self._path(name)
        try:
            path.mkdir()
        except OSError as exc:
            raise Blocked('own-child creation unavailable or name occupied') from exc
        return path

    def receipt(self, name):
        path = self._path(name)
        return {'name': name, 'parent': str(self.parent), 'parent_identity': self.parent_identity,
                'boot': boot_id(), **stat_identity(path)}

    def validate(self, receipt):
        if not isinstance(receipt, dict) or receipt.get('parent') != str(self.parent):
            raise Blocked('containment parent mismatch')
        name = receipt.get('name', '')
        path = self._path(name)
        try:
            observed = self.receipt(name)
            if observed != receipt or observed['uid'] != os.getuid():
                raise Blocked('containment UID/device/inode/name/boot/parent mismatch')
            for name, mode in (('cgroup.procs', os.W_OK), ('cgroup.kill', os.W_OK), ('cgroup.events', os.R_OK)):
                control = path / name
                if control.is_symlink() or not control.is_file() or not os.access(control, mode):
                    raise Blocked('missing own-child control: ' + name)
        except OSError as exc:
            raise Blocked('containment identity/controls unavailable') from exc
        return path

    def populated(self, receipt):
        path = self.validate(receipt)
        values = dict(line.split() for line in (path/'cgroup.events').read_text().splitlines())
        if values.get('populated') not in ('0','1'):
            raise Blocked('unknown populated observation')
        return int(values['populated'])

    def member(self, receipt, identity, nonce):
        validate_process(identity, nonce)
        path = self.validate(receipt)
        # Exact kernel cgroup path, not PGID enumeration or a stale procs list.
        expected = '/' + str(path.relative_to('/sys/fs/cgroup'))
        lines = Path(f"/proc/{identity['pid']}/cgroup").read_text().splitlines()
        if '0::' + expected not in lines:
            raise Blocked('helper not in registered child')

    def drain(self, receipt, timeout=5):
        path = self.validate(receipt)
        if self.populated(receipt):
            (path/'cgroup.kill').write_text('1')
        deadline = time.monotonic() + timeout
        while self.populated(receipt):
            if time.monotonic() >= deadline:
                raise Blocked('owned child did not drain')
            time.sleep(0.01)
        return {'containment': receipt, 'populated': 0, 'observed_ns': time.time_ns()}

    def remove(self, receipt):
        path = self.validate(receipt)
        if self.populated(receipt):
            raise Blocked('cannot remove populated child')
        path.rmdir()
