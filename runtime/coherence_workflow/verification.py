"""Runner checks and scoped manual STOPs; agent confidence is never evidence."""
import copy
import io
import json
import platform
import time
import unittest
import uuid

from jsonschema import Draft202012Validator

from .store import Blocked, canonical, digest, git, safe_path
from .intake import content_hash


def environment_identity():
    return {'python': platform.python_version(), 'platform': platform.platform()}


def item_identity(project, task, item, environment):
    return digest({'item': item, 'paths': {name: content_hash(safe_path(project, name))
                   if safe_path(project, name).is_file() else None for name in task['owned_paths']},
                   'environment': environment})


class Verification:
    def __init__(self, authority, run, checks, environment=None):
        self.authority, self.store, self.run = authority, authority.store, run
        self.checks = checks
        self.environment = environment or environment_identity()
        self.store.db.executescript('''
        CREATE TABLE IF NOT EXISTS wf_checks(
          evidence_id TEXT PRIMARY KEY, run_id TEXT NOT NULL REFERENCES wf_runs,
          task_id TEXT NOT NULL, item_id TEXT NOT NULL, applicability TEXT NOT NULL,
          receipt TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS wf_gates(
          gate_id TEXT PRIMARY KEY, run_id TEXT NOT NULL REFERENCES wf_runs,
          binding TEXT NOT NULL, state TEXT NOT NULL, answer TEXT);
        ''')

    def request_sample(self, task, gate, sample_path, config_hash):
        """Inspectable current bytes, nonce and scoped question precede any full work."""
        path = safe_path(self.authority.project, sample_path)
        if not path.is_file() or sample_path not in task['owned_paths']:
            raise Blocked('sample must be an existing owned artifact')
        binding = {'task_id': task['id'], 'task_hash': digest(task), 'gate': copy.deepcopy(gate),
                   'sample_path': sample_path, 'sample_hash': content_hash(path),
                   'config_hash': config_hash, 'nonce': uuid.uuid4().hex}
        id = uuid.uuid4().hex
        with self.store.transaction() as db:
            db.execute("INSERT INTO wf_gates VALUES(?,?,?,'pending',NULL)", (id, self.run, canonical(binding)))
            self.store.event(db, self.run, None, 'manual_stop_requested', {'gate_id': id, **binding})
        return {'gate_id': id, **binding}

    def answer_sample(self, request, answer, *, verify_owner):
        """verify_owner is an authenticated external input adapter, never a worker callback."""
        row = self.store.db.execute('SELECT * FROM wf_gates WHERE gate_id=? AND run_id=?',
                                    (request['gate_id'], self.run)).fetchone()
        if not row or row['binding'] != canonical({k: v for k, v in request.items() if k != 'gate_id'}):
            raise Blocked('wrong manual STOP binding')
        if row['state'] != 'pending':
            raise Blocked('manual STOP already answered; no duplicate continuation')
        if answer.get('binding_hash') != digest(request) or answer.get('action') not in ('approve', 'deny', 'cancel'):
            raise Blocked('wrong/stale manual answer')
        if content_hash(safe_path(self.authority.project, request['sample_path'])) != request['sample_hash']:
            raise Blocked('manual sample content drift')
        verify_owner(answer)
        with self.store.transaction() as db:
            cur = db.execute("UPDATE wf_gates SET state=?,answer=? WHERE gate_id=? AND state='pending'",
                             (answer['action'], canonical(answer), request['gate_id']))
            if cur.rowcount != 1:
                raise Blocked('manual answer compare-and-set failed')
            self.store.event(db, self.run, None, 'manual_stop_answered',
                             {'gate_id': request['gate_id'], 'action': answer['action'], 'binding_hash': digest(request)})
        return answer['action']

    def require_sample(self, request, task, config_hash):
        row = self.store.db.execute('SELECT * FROM wf_gates WHERE gate_id=? AND run_id=?',
                                    (request['gate_id'], self.run)).fetchone()
        if (not row or row['state'] != 'approve' or row['binding'] != canonical({k: v for k, v in request.items() if k != 'gate_id'}) or
                request['task_hash'] != digest(task) or request['config_hash'] != config_hash or
                content_hash(safe_path(self.authority.project, request['sample_path'])) != request['sample_hash']):
            raise Blocked('unmet/denied/cancelled/stale manual sample STOP')
        return True

    def run_checks(self, task):
        self.authority.assert_held()
        self.store.assert_dispatchable(self.run)
        results, shared = [], {}
        for item in task['required']:
            identity = item_identity(self.authority.project, task, item, self.environment)
            check = item['check']
            spec = self.checks.get(check['id'])
            receipt = {'item_ids': [], 'revision': git(self.authority.project, 'rev-parse', 'HEAD').decode().strip(),
                       'environment': self.environment, 'check': check, 'status': 'insufficient-evidence',
                       'reason': 'registered check unavailable', 'exit_code': None, 'collected': 0}
            if spec and spec['version'] == check['version']:
                Draft202012Validator(spec['schema']).validate(check['args'])
                key = digest(check)
                if key not in shared:
                    start = time.time_ns()
                    try:
                        observed = spec['execute'](copy.deepcopy(check['args']))
                    except Exception as exc:
                        observed = {'exit_code': None, 'collected': 0, 'output': '',
                                    'unknown_reason': 'oracle unavailable: ' + type(exc).__name__}
                    # Only registered oracles may demonstrate a violation; missing/unrun
                    # observations cannot be promoted by worker output or exit 0 alone.
                    valid = (type(observed.get('collected')) is int and observed['collected'] > 0 and
                             type(observed.get('exit_code')) is int and isinstance(observed.get('output'), str))
                    shared[key] = {**receipt, **observed, 'started_ns': start, 'ended_ns': time.time_ns(),
                                   'status': ('satisfied' if observed['exit_code'] == 0 else 'failed') if valid else 'insufficient-evidence',
                                   'reason': None if valid else 'empty/unrun/invalid oracle proof'}
                receipt = copy.deepcopy(shared[key])
            receipt['item_ids'] = [other['id'] for other in task['required'] if other['check'] == check]
            receipt['applicability'] = identity
            with self.store.transaction() as db:
                id = uuid.uuid4().hex
                db.execute('INSERT INTO wf_checks VALUES(?,?,?,?,?,?)',
                           (id, self.run, task['id'], item['id'], identity, canonical(receipt)))
                self.store.event(db, self.run, None, 'check_observed', {'evidence_id': id, 'item_id': item['id'], **receipt})
            results.append({'item_id': item['id'], 'evidence_id': id, **receipt})
        return results

    def audit(self, task, evidence):
        by_item = {}
        for receipt in evidence:
            by_item.setdefault(receipt['item_id'], []).append(receipt)
        dispositions = []
        for item in task['required']:
            receipts = by_item.get(item['id'], [])
            status, reason = 'insufficient-evidence', 'missing/conflicting/stale proof'
            if len(receipts) == 1:
                receipt = receipts[0]
                row = self.store.db.execute('SELECT * FROM wf_checks WHERE evidence_id=? AND run_id=? AND task_id=? AND item_id=?',
                    (receipt['evidence_id'], self.run, task['id'], item['id'])).fetchone()
                expected = {k: v for k, v in receipt.items() if k not in ('evidence_id', 'item_id')}
                if (row and json.loads(row['receipt']) == expected and
                        row['applicability'] == item_identity(self.authority.project, task, item, self.environment)):
                    status, reason = receipt['status'], receipt['reason']
            dispositions.append({'item_id': item['id'], 'status': status, 'reason': reason})
        return dispositions


def unittest_oracle(args):
    """Trusted registered selectors only; zero collection is not a passing oracle."""
    if not args.get('selector'):
        raise Blocked('empty test selector')
    module = args['test_file'].removesuffix('.py').replace('/', '.')
    suite = unittest.defaultTestLoader.loadTestsFromName(module + '.' + args['selector'])
    if unittest.defaultTestLoader.errors:
        unittest.defaultTestLoader.errors.clear()
        return {'exit_code': None, 'collected': 0, 'output': 'test loader unavailable'}
    stream = io.StringIO()
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
    return {'exit_code': None if result.errors or result.skipped else 0 if result.wasSuccessful() else 1,
            'collected': result.testsRun, 'output': stream.getvalue()[:32768]}
