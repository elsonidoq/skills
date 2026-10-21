"""Closed, incremental JSONL metric artifacts for one workflow run.

This is deliberately a file seam only.  Callers decide when a terminal invocation
exists and treat ``MetricArtifactError`` as an optional-recording gap.
"""
from __future__ import annotations

import fcntl
import hashlib
import json
import math
import os
import stat
from pathlib import Path

from .store import Blocked, git, safe_path

VERSION = 1
_ROLES = frozenset({'worker', 'corrective_worker', 'fixing_worker', 'reviewer'})
_OUTCOMES = frozenset({'settled', 'failed', 'interrupted', 'approved', 'rejected'})
_MODES = frozenset({'fresh', 'reused_from_earlier_task', 'continued_same_task', 'unknown'})
_COUNTERS = ('input', 'output', 'cacheRead', 'cacheWrite', 'total')


class MetricArtifactError(RuntimeError):
    """The optional artifact cannot safely be appended or read."""


def _number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value) and value >= 0


def _text(value, *, nullable=False):
    return (value is None and nullable) or (isinstance(value, str) and bool(value) and '\x00' not in value)


def artifact_relative(run_id):
    if not _text(run_id):
        raise MetricArtifactError('run ID must be a nonempty string')
    digest = hashlib.sha256(run_id.encode('utf-8')).hexdigest()
    return '.coherence/metrics/run-' + digest + '.jsonl'


def artifact_path(project, run_id):
    return safe_path(project, artifact_relative(run_id))


def _clean_target(project, relative):
    try:
        status = git(project, 'status', '--porcelain=v1', '--', relative).decode('utf-8', 'replace')
    except Blocked as exc:
        raise MetricArtifactError(str(exc)) from exc
    if status:
        raise MetricArtifactError('metric artifact target is dirty or staged: ' + relative)


def _identity(info):
    # ctime closes the practical inode-reuse hole after an unlink/recreate race.
    return info.st_dev, info.st_ino, info.st_ctime_ns


def _same_file(path, identity):
    try:
        current = os.stat(path, follow_symlinks=False)
    except OSError:
        return False
    return stat.S_ISREG(current.st_mode) and _identity(current) == identity


def _field(value):
    return (isinstance(value, dict) and set(value) == {'value', 'unknown_reason', 'provenance'} and
            (value['value'] is None or _number(value['value'])) and
            (value['unknown_reason'] is None or _text(value['unknown_reason'])) and
            (value['provenance'] is None or _text(value['provenance'])))


def _interval(value):
    if not isinstance(value, dict) or set(value) != {'session_id', 'branch', 'epoch', 'outcome', 'tokens', 'total_tokens', 'estimated_usd', 'compactions', 'summary_overhead'}:
        return False
    if any(not _text(value[name], nullable=True) for name in ('session_id', 'branch', 'epoch')) or value['outcome'] not in {'settled', 'failed', 'interrupted'}:
        return False
    tokens = value['tokens']
    if not isinstance(tokens, dict) or set(tokens) != {'input', 'output', 'cache_read', 'cache_write'} or not all(_field(x) for x in tokens.values()):
        return False
    if not _field(value['total_tokens']) or not _field(value['estimated_usd']):
        return False
    compactions = value['compactions']
    if not (isinstance(compactions, dict) and set(compactions) == {'entry_ids', 'count', 'unknown_reason'} and
            isinstance(compactions['entry_ids'], list) and all(_text(x) for x in compactions['entry_ids']) and
            (compactions['count'] is None or (type(compactions['count']) is int and compactions['count'] >= 0)) and
            (compactions['unknown_reason'] is None or _text(compactions['unknown_reason']))):
        return False
    overhead = value['summary_overhead']
    if not (isinstance(overhead, dict) and set(overhead) == {'entries', 'unknown_reason', 'included_in_sdk_deltas'} and
            isinstance(overhead['entries'], list) and type(overhead['included_in_sdk_deltas']) is bool and
            (overhead['unknown_reason'] is None or _text(overhead['unknown_reason']))):
        return False
    allowed_usage = {'input', 'output', 'cacheRead', 'cacheWrite', 'totalTokens', 'cacheWrite1h', 'reasoning', 'cost'}
    for entry in overhead['entries']:
        if not (isinstance(entry, dict) and set(entry) == {'entry_id', 'usage', 'unknown_reason'} and _text(entry['entry_id']) and
                (entry['unknown_reason'] is None or _text(entry['unknown_reason']))):
            return False
        usage = entry['usage']
        if usage is not None:
            if not isinstance(usage, dict) or not set(usage) <= allowed_usage:
                return False
            for key, item in usage.items():
                if key == 'cost':
                    if not isinstance(item, dict) or not set(item) <= {'input', 'output', 'cacheRead', 'cacheWrite', 'total'} or not all(_number(x) for x in item.values()):
                        return False
                elif not _number(item):
                    return False
    return True


def _snapshot(value):
    if value is None:
        return True
    if not isinstance(value, dict) or set(value) != {'counters', 'estimated_usd', 'context', 'compaction_entry_ids'}:
        return False
    counters, context = value['counters'], value['context']
    return (isinstance(counters, dict) and set(counters) == set(_COUNTERS) and all(x is None or _number(x) for x in counters.values()) and
            (value['estimated_usd'] is None or _number(value['estimated_usd'])) and
            isinstance(context, dict) and set(context) == {'context_window', 'effective_reserve', 'occupancy', 'compaction_enabled', 'compaction_applicable'} and
            all(context[x] is None or _number(context[x]) for x in ('context_window', 'effective_reserve', 'occupancy')) and
            all(context[x] is None or type(context[x]) is bool for x in ('compaction_enabled', 'compaction_applicable')) and
            isinstance(value['compaction_entry_ids'], list) and all(_text(x) for x in value['compaction_entry_ids']))


def validate_record(record, run_id=None):
    """Return a detached closed record or raise; arbitrary payloads never pass."""
    allowed = {'version', 'run_id', 'invocation_id', 'task_id', 'role', 'outcome', 'fixing_round', 'review_ordinal',
               'interval', 'before', 'after', 'selected_session_mode', 'session_selection_reason',
               'actual_session_mode', 'actual_session_id'}
    if not isinstance(record, dict) or set(record) != allowed:
        raise MetricArtifactError('metric record has unknown or missing fields')
    if record['version'] != VERSION or not _text(record['run_id']) or (run_id is not None and record['run_id'] != run_id):
        raise MetricArtifactError('metric record has an invalid run identity')
    if not _text(record['invocation_id']) or not _text(record['task_id'], nullable=True):
        raise MetricArtifactError('metric record has an invalid invocation identity')
    if record['role'] not in _ROLES or record['outcome'] not in _OUTCOMES:
        raise MetricArtifactError('metric record has an invalid role or outcome')
    if any(value is not None and (type(value) is not int or value < 1)
           for value in (record['fixing_round'], record['review_ordinal'])):
        raise MetricArtifactError('metric record has invalid review context')
    if not _interval(record['interval']) or not _snapshot(record['before']) or not _snapshot(record['after']):
        raise MetricArtifactError('metric record has invalid metric fields')
    for key in ('selected_session_mode', 'actual_session_mode'):
        if record[key] not in _MODES:
            raise MetricArtifactError('metric record has invalid session mode')
    if not _text(record['session_selection_reason'], nullable=True) or not _text(record['actual_session_id'], nullable=True):
        raise MetricArtifactError('metric record has invalid session provenance')
    return json.loads(json.dumps(record, sort_keys=True, separators=(',', ':'), allow_nan=False))


class MetricArtifact:
    def __init__(self, project, run_id, path, identity):
        self.project, self.run_id, self.path, self.identity = Path(project), run_id, Path(path), identity

    def append(self, record):
        value = validate_record(record, self.run_id)
        if not _same_file(self.path, self.identity):
            raise MetricArtifactError('metric artifact changed before append')
        # Refuse to append behind malformed/incomplete bytes rather than repairing them.
        prior = read_artifact(self.project, self.run_id, strict=True)
        if prior['records'] and any(row['invocation_id'] == value['invocation_id'] for row in prior['records']):
            raise MetricArtifactError('metric invocation already recorded')
        encoded = (json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n').encode('utf-8')
        try:
            fd = os.open(self.path, os.O_WRONLY | os.O_APPEND | os.O_NOFOLLOW)
            try:
                fcntl.flock(fd, fcntl.LOCK_EX)
                if not _same_file(self.path, self.identity):
                    raise MetricArtifactError('metric artifact changed during append')
                offset = 0
                while offset < len(encoded):
                    wrote = os.write(fd, encoded[offset:])
                    if wrote <= 0:
                        raise MetricArtifactError('short metric artifact write')
                    offset += wrote
                # Closing the descriptor makes the complete write visible; no fsync promise.
            finally:
                os.close(fd)
        except OSError as exc:
            raise MetricArtifactError('metric artifact append failed: ' + str(exc)) from exc
        self.identity = _identity(os.stat(self.path, follow_symlinks=False))
        return value


def create_artifact(project, run_id, *, authority=None):
    """Reserve a new run artifact; preexisting files are never adopted."""
    if authority is None:
        raise MetricArtifactError('metric artifact creation requires the worktree writer authority')
    authority.assert_held()
    project = Path(project).resolve(strict=True)
    if Path(authority.project).resolve() != project:
        raise MetricArtifactError('writer authority belongs to another project')
    relative = artifact_relative(run_id)
    try:
        path = safe_path(project, relative)
    except Blocked as exc:
        raise MetricArtifactError(str(exc)) from exc
    _clean_target(project, relative)
    parent = safe_path(project, '.coherence/metrics')
    parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    if parent.is_symlink():
        raise MetricArtifactError('metric artifact directory is a symlink')
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
        os.close(fd)
    except FileExistsError as exc:
        raise MetricArtifactError('metric artifact already exists') from exc
    except OSError as exc:
        raise MetricArtifactError('cannot create metric artifact: ' + str(exc)) from exc
    info = os.stat(path, follow_symlinks=False)
    if not stat.S_ISREG(info.st_mode):
        raise MetricArtifactError('metric artifact is not a regular file')
    return MetricArtifact(project, run_id, path, _identity(info))


def read_artifact(project, run_id, *, strict=False):
    """Read one complete EOF prefix.  Bad data becomes a qualified optional gap."""
    project = Path(project).resolve(strict=True)
    path = artifact_path(project, run_id)
    result = {'records': [], 'coverage': 'complete', 'reasons': []}
    try:
        info = os.stat(path, follow_symlinks=False)
        if not stat.S_ISREG(info.st_mode):
            raise MetricArtifactError('metric artifact is not a regular file')
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
        try:
            data = b''
            while True:
                chunk = os.read(fd, 65536)
                if not chunk:
                    break
                data += chunk
            opened = os.fstat(fd)
        finally:
            os.close(fd)
        if _identity(opened) != _identity(info) or not _same_file(path, _identity(info)):
            raise MetricArtifactError('metric artifact changed during read')
    except (OSError, Blocked, MetricArtifactError) as exc:
        if strict:
            raise MetricArtifactError(str(exc)) from exc
        return {'records': [], 'coverage': 'unavailable', 'reasons': [str(exc)]}
    if data and not data.endswith(b'\n'):
        if strict:
            raise MetricArtifactError('incomplete_tail')
        result['coverage'], result['reasons'] = 'partial', ['incomplete_tail']
        data = data.rsplit(b'\n', 1)[0] + (b'\n' if b'\n' in data else b'')
    for line in data.splitlines():
        try:
            row = validate_record(json.loads(line.decode('utf-8')), run_id)
        except Exception:
            if strict:
                raise MetricArtifactError('invalid metric artifact record') from None
            result['coverage'] = 'partial'
            result['reasons'].append('invalid_record')
            continue
        result['records'].append(row)
    return result


def summarize_artifact(project, run_id, *, expected_invocation_ids=None):
    """Return deduplicated recorded totals and explicit coverage, never an invoice."""
    readback = read_artifact(project, run_id)
    unique, conflicts = {}, False
    for row in readback['records']:
        old = unique.get(row['invocation_id'])
        if old is None:
            unique[row['invocation_id']] = row
        elif old != row:
            conflicts = True
    expected = set(expected_invocation_ids or [])
    present = set(unique)
    reasons = list(readback['reasons'])
    if conflicts: reasons.append('conflicting_duplicate_invocation')
    if expected - present: reasons.append('missing_expected_invocations')
    known = {name: 0 for name in ('input', 'output', 'cache_read', 'cache_write')}
    complete = not reasons
    for row in unique.values():
        for name in known:
            field = row['interval']['tokens'][name]
            if field['value'] is None:
                complete = False
            else:
                known[name] += field['value']
    return {'invocation_count': len(unique), 'records': list(unique.values()), 'token_subtotal': known,
            'coverage': 'complete' if complete and readback['coverage'] == 'complete' else 'partial',
            'reasons': reasons or ([] if complete else ['unknown_metric_fields'])}
