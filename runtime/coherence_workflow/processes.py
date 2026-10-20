"""Read actual recorded process identity for explicit historical abandon; never signal."""
import os
import json
from pathlib import Path

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


def recorded_writer_live(identity):
    """Only actual boot/PID/start/UID identity matters, not a ledger phase."""
    if not identity or identity.get('boot') != boot_id():
        return False
    pid = identity['pid']
    if not Path(f'/proc/{pid}').exists():
        return False
    try:
        observed = process_identity(pid, identity.get('nonce'))
    except Blocked:
        if not Path(f'/proc/{pid}').exists():
            return False
        raise Blocked('cannot inspect recorded PID; inspect its current identity before replacing a writer') from None
    return all(observed[k] == identity[k] for k in ('boot', 'pid', 'start', 'uid'))


def inspect_recorded_writers(db, operation):
    """Legacy process identities remain useful only to avoid a live overlap."""
    for table in ('wf_controllers', 'wf_processes'):
        if not db.execute("SELECT 1 FROM sqlite_master WHERE name=?", (table,)).fetchone():
            continue
        for row in db.execute('SELECT identity FROM ' + table):
            if row['identity'] and recorded_writer_live(json.loads(row['identity'])):
                kind = 'controller' if table == 'wf_controllers' else 'child'
                raise Blocked(operation + ' refused: live ' + kind + '; wait for its writer and inspect again')
