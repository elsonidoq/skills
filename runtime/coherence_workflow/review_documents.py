"""Pinned review documents and minimal proof of settled SDK delivery (no bodies in SQL)."""
import hashlib
import json
import os
from pathlib import Path
import stat

from .store import Blocked, canonical, digest, git, safe_path


def references(contract, project, revision):
    refs = [dict(source) for source in contract['sources']]
    refs += [{'path': ref['record_ref'], 'sha256': ref['record_sha256'],
              'kind': 'approval', 'role': ref['gate_kind']}
             for ref in contract['approval_refs']]
    for ref in refs:
        # An authorized file need not be committed; never invent its Git revision.
        if git(project, 'ls-tree', revision, '--', ref['path']).strip():
            raw = git(project, 'show', revision + ':' + ref['path'])
            if hashlib.sha256(raw).hexdigest() == ref['sha256']:
                ref['revision'] = revision
    return refs


def read_bytes(project, name, expected=None):
    """Open once, reject identity changes, hash and decode exactly the returned bytes."""
    try:
        path = safe_path(project, name)
        before = path.lstat()
        if not stat.S_ISREG(before.st_mode):
            raise Blocked('authorized read unavailable/too large')
        with path.open('rb') as stream:
            opened = os.fstat(stream.fileno())
            raw = stream.read(32769)
            after = os.fstat(stream.fileno())
        identity = lambda info: (info.st_dev, info.st_ino, info.st_mode, info.st_size, info.st_mtime_ns, info.st_ctime_ns)
        if identity(before) != identity(opened) or identity(opened) != identity(after) or identity(path.lstat()) != identity(after) or len(raw) > 32768:
            raise Blocked('authorized read unavailable/too large or identity changed')
        sha = hashlib.sha256(raw).hexdigest()
        if expected and sha != expected:
            raise Blocked('review document pinned hash changed')
        text = raw.decode('utf-8')
    except (OSError, UnicodeError) as exc:
        raise Blocked('authorized review document unavailable/invalid UTF-8') from exc
    return text, {'path': name, 'sha256': sha, 'bytes': len(raw),
                  'identity': {'device': after.st_dev, 'inode': after.st_ino}}


def read_document(coordinate, bundle, args, receipt):
    coordinate.verify_action_origin()
    allowed = {ref['path'] for ref in bundle['document_refs']} | {path for task in coordinate.contract['tasks'] for path in task['owned_paths']}
    if args['path'] not in allowed:
        raise Blocked('unauthorized review document path')
    pins = {ref['sha256'] for ref in bundle['document_refs'] if ref['path'] == args['path']}
    if len(pins) > 1:
        raise Blocked('conflicting review document pins')
    text, proof = read_bytes(coordinate.authority.project, args['path'], next(iter(pins), None))
    if pins:
        row = coordinate.store.db.execute('SELECT op_id FROM wf_processes WHERE empty_receipt=?',
                                          (canonical(receipt['empty_receipt']),)).fetchall()
        if len(row) != 1:
            raise Blocked('review document read process identity unavailable')
        proof.update(bundle_hash=digest(bundle), range_base=bundle['range_base'], range_head=bundle['range_head'])
        with coordinate.store.transaction() as db:
            coordinate.store.event(db, coordinate.run, row[0]['op_id'], 'review_document_read', proof)
    return text


def _messages(project, before, after):
    """Inspect ONLY the settled private SDK branch, retaining no transcript copy."""
    try:
        path = Path(after['session_file'])
        root = project / '.coherence/workflow'
        if path != path.resolve(strict=True) or not path.is_relative_to(root):
            raise Blocked('unsafe review SDK delivery file')
        for parent in path.parents:
            if parent == root.parent:
                break
            if parent.is_symlink():
                raise Blocked('unsafe review SDK delivery file')
        info = path.lstat()
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or info.st_uid != os.getuid() or info.st_mode & 0o077:
            raise Blocked('unsafe review SDK delivery file')
        raw = path.read_bytes()
        current = path.lstat()
        if ((current.st_dev, current.st_ino, current.st_size, current.st_mtime_ns, current.st_ctime_ns) !=
                (info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns, info.st_ctime_ns) or
                hashlib.sha256(raw).hexdigest() != after['session_file_hash']):
            raise Blocked('review SDK delivery file changed')
        entries = [json.loads(line) for line in raw.splitlines()]
        if not entries or entries[0].get('type') != 'session' or entries[0].get('id') != after['session_id']:
            raise Blocked('wrong review SDK delivery session')
        nodes = {entry['id']: entry for entry in entries[1:] if 'id' in entry}
        branch, leaf, stop = [], after['leaf'], before['leaf']
        seen = set()
        while leaf != stop:
            if not leaf or leaf in seen or leaf not in nodes:
                raise Blocked('wrong review SDK delivery branch')
            seen.add(leaf)
            entry = nodes[leaf]
            if entry.get('type') == 'message':
                branch.append(entry)
            leaf = entry.get('parentId')
        return branch
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise Blocked('review SDK delivery evidence unavailable') from exc


def settle_delivery(coordinate, turn):
    """A callback is only a read; persisted successful SDK toolResult proves delivery."""
    store = coordinate.store
    segment = turn['segment']
    rows = store.db.execute("SELECT * FROM wf_operations WHERE run_id=? AND kind='sdk-turn' AND phase='completed'",
                            (coordinate.run,)).fetchall()
    matches = [row for row in rows if json.loads(row['result']) == segment]
    if len(matches) != 1 or segment['role'] != 'review':
        raise Blocked('missing settled independent review turn')
    operation = matches[0]
    delivered = []
    for entry in _messages(coordinate.authority.project, segment['before'], segment['after']):
        message = entry['message']
        if message.get('role') != 'toolResult' or message.get('toolName') != 'read_file' or message.get('isError') is not False:
            continue
        call_hash = digest(message['toolCallId'])
        launch = store.db.execute('SELECT payload FROM wf_events WHERE op_id=? AND kind=?',
                                  (operation['op_id'], 'sdk_tool_launched:' + call_hash)).fetchone()
        if not launch:
            raise Blocked('review delivery lacks originating tool launch')
        launch = json.loads(launch[0])
        process = launch['process_operation']
        read = store.db.execute("SELECT payload FROM wf_events WHERE op_id=? AND kind='review_document_read'", (process,)).fetchone()
        if not read:
            continue  # Owned source reads are allowed but are not mandatory document refs.
        read = json.loads(read[0])
        content = message.get('content')
        if not isinstance(content, list) or len(content) != 1 or content[0].get('type') != 'text':
            raise Blocked('review document returned content unavailable')
        output = json.loads(content[0]['text'])
        if (output.get('operation_id') != process or output.get('exit_code') != 0 or
                not isinstance(output.get('output'), str) or
                hashlib.sha256(output['output'].encode('utf-8')).hexdigest() != read['sha256'] or
                read['bundle_hash'] != segment['contract_hash'] or
                launch['generation'] != segment['generation']):
            raise Blocked('review document delivery identity/bytes mismatch')
        delivered.append({'process_operation': process, 'call_hash': call_hash, 'entry_id': entry['id'], **read})
    proof = {'host_op': segment['host_op'], 'bundle_hash': segment['contract_hash'],
             'generation': segment['generation'], 'snapshot_hash': digest(segment['after']), 'reads': delivered}
    with store.transaction() as db:
        store.event(db, coordinate.run, operation['op_id'], 'review_document_delivery', proof)
    return proof


def require_coverage(coordinate, result, host_op):
    """Reaudit current authority + exact original turn/bundle/range and settled processes."""
    coordinate.verify_action_origin()
    store = coordinate.store
    if (result['range_base'], result['range_head']) != coordinate.review_repair.range():
        raise Blocked('wrong review document delivery range')
    required = {(ref['path'], ref['sha256']) for ref in references(coordinate.contract, coordinate.authority.project, result['range_head'])}
    covered = set()
    for row in store.db.execute("SELECT * FROM wf_operations WHERE run_id=? AND kind='sdk-turn' AND phase='completed'", (coordinate.run,)):
        intent, segment = json.loads(row['intent']), json.loads(row['result'])
        if (intent.get('host_op') != host_op or intent.get('role') != 'review' or
                intent.get('contract_hash') != result['contract_hash'] or intent.get('attempt_id') != result['attempt_id']):
            continue
        event = store.db.execute("SELECT payload FROM wf_events WHERE op_id=? AND kind='review_document_delivery'", (row['op_id'],)).fetchone()
        if not event:
            continue
        proof = json.loads(event[0])
        if (any(segment.get(key) != intent.get(key) for key in ('host_op', 'role', 'contract_hash', 'generation', 'attempt_id')) or
                proof['host_op'] != host_op or proof['bundle_hash'] != result['contract_hash'] or
                proof['snapshot_hash'] != digest(segment['after']) or proof['generation'] != intent['generation']):
            raise Blocked('wrong review document delivery host/turn')
        for read in proof['reads']:
            process = store.operation(read['process_operation'])
            original = store.db.execute("SELECT payload FROM wf_events WHERE op_id=? AND kind='review_document_read'", (process['op_id'],)).fetchone()
            launch = store.db.execute('SELECT payload FROM wf_events WHERE op_id=? AND kind=?',
                                      (row['op_id'], 'sdk_tool_launched:' + read['call_hash'])).fetchone()
            if (not original or not launch or not read.get('entry_id') or
                    process['run_id'] != coordinate.run or process['args_hash'] != digest({'path': read['path']}) or
                    json.loads(process['intent']).get('tool') != 'read_file' or
                    json.loads(launch[0]).get('generation') != intent['generation'] or
                    json.loads(launch[0]).get('process_operation') != process['op_id'] or
                    any(read.get(key) != value for key, value in json.loads(original[0]).items()) or
                    process['phase'] != 'completed' or not json.loads(process['result']).get('replacement_allowed') or
                    json.loads(process['result']).get('logical_exit') != 0 or
                    read['bundle_hash'] != result['contract_hash'] or
                    (read['range_base'], read['range_head']) != (result['range_base'], result['range_head'])):
                raise Blocked('wrong/unsettled review document delivery process/range')
            covered.add((read['path'], read['sha256']))
    if not required <= covered:
        raise Blocked('missing settled review document delivery coverage')
    return True
