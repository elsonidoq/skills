"""Worktree writer lock, ordinary progress, and read-only historical access."""
from contextlib import contextmanager
import fcntl
import json
import os
from pathlib import Path, PurePosixPath
import sqlite3
import subprocess
import tempfile
import uuid
import time

class Blocked(RuntimeError):
    """An operation could not complete; partial work is retained."""

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)

def _review_input(value):
    if not isinstance(value, dict) or set(value) != {'checkpoint_occurrence_id', 'task_id', 'producer_invocation_id', 'correction_chain'}:
        return False
    if any(not isinstance(value[key], str) or not value[key] for key in
           ('checkpoint_occurrence_id', 'task_id', 'producer_invocation_id')):
        return False
    chain = value['correction_chain']
    return (isinstance(chain, list) and chain and all(isinstance(part, str) and part for part in chain)
            and chain[-1] == value['producer_invocation_id'])

def safe_path(root, relative):
    if not isinstance(relative, str) or not relative or "\\" in relative or "\x00" in relative:
        raise Blocked("invalid relative path")
    if PurePosixPath(relative).is_absolute() or any(p in ("..", ".") for p in relative.split("/")):
        raise Blocked("unsafe relative path: " + relative)
    root = Path(root).resolve(strict=True)
    p = root
    for part in PurePosixPath(relative).parts:
        p = p / part
        if p.is_symlink():
            raise Blocked("symlink path component: " + relative)
    if not p.resolve().is_relative_to(root):
        raise Blocked("path outside root")
    return p

def git(project, *args):
    if any(os.environ.get(k) for k in ('GIT_DIR','GIT_WORK_TREE','GIT_INDEX_FILE','GIT_COMMON_DIR','GIT_OBJECT_DIRECTORY','GIT_ALTERNATE_OBJECT_DIRECTORIES')):
        raise Blocked('ambient Git authority override; unset it before operating on this project')
    result = subprocess.run(["git", "--no-optional-locks", "-C", str(project), *args], capture_output=True)
    if result.returncode:
        raise Blocked("Git operation failed: " + result.stderr.decode(errors="replace"))
    return result.stdout

def execution_schema(db):
    """Recognize the core execution format, not optional later recording tables."""
    required = {
        'execution_runs': {'run_id', 'state', 'baseline', 'result', 'error'},
        'execution_tasks': {'run_id', 'task_id', 'state', 'baseline', 'result', 'details'},
    }
    return all(columns <= {row[1] for row in db.execute('PRAGMA table_info(' + table + ')')}
               for table, columns in required.items())


def prepare_database(path, *, quarantine=False):
    """Called under the worktree lock, before Store can add execution tables."""
    for suffix in ('', '-wal', '-shm', '-journal'):
        safe_path(path.parent, path.name + suffix)
    if not path.exists() or path.stat().st_size == 0:
        return None
    db = sqlite3.connect(path.as_uri() + '?mode=ro', uri=True)
    db.row_factory = sqlite3.Row
    try:
        if execution_schema(db):
            return None
        if not db.execute("SELECT 1 FROM sqlite_master WHERE type='table'").fetchone():
            return None  # A genuinely empty SQLite database is fresh storage.
        if not quarantine:
            raise Blocked('unsupported workflow database format; start a new run to quarantine it and create clean storage')
        from .processes import inspect_recorded_writers
        inspect_recorded_writers(db, 'quarantine')
    finally:
        db.close()
    # Fold committed WAL pages into the main file before separating any sidecars.
    # A busy checkpoint means an active SQLite reader/writer: leave storage in place.
    db = sqlite3.connect(path.as_uri() + '?mode=rw', uri=True, timeout=0)
    try:
        if db.execute('PRAGMA wal_checkpoint(TRUNCATE)').fetchone()[0]:
            raise Blocked('quarantine refused: workflow database is busy; stop its SQLite users and start again')
    finally:
        db.close()
    archive = Path(tempfile.mkdtemp(prefix='quarantine-', dir=path.parent))
    try:
        for suffix in ('-wal', '-shm', '-journal', ''):
            source = safe_path(path.parent, path.name + suffix)
            if source.exists():
                source.rename(archive / source.name)
    except OSError as exc:
        raise Blocked('quarantine incomplete at ' + str(archive) + '; inspect retained files before starting again: ' + str(exc)) from exc
    return archive


class Authority:
    """An exclusive ordinary writer lock; old bindings are not launch eligibility."""
    def __init__(self, project, *, wait=False, quarantine_unsupported=False):
        self.project = Path(project).resolve(strict=True)
        if Path(git(self.project, 'rev-parse', '--show-toplevel').decode().strip()).resolve() != self.project:
            raise Blocked('project must be the Git worktree root')
        admin = Path(git(self.project, 'rev-parse', '--absolute-git-dir').decode().strip())
        fd = os.open(admin / 'coherence-workflow.lock', os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
        self.lock = os.fdopen(fd, 'r+')
        try:
            # CLI entry waits on the kernel lock so a cooperating live writer is never
            # replaced.  Direct callers retain the old concrete-busy behavior.
            fcntl.flock(fd, fcntl.LOCK_EX if wait else fcntl.LOCK_EX | fcntl.LOCK_NB)
            root = safe_path(self.project, '.coherence/workflow')
            root.mkdir(mode=0o700, parents=True, exist_ok=True)
            self.database = safe_path(self.project, '.coherence/workflow/workflow.sqlite')
            self.quarantined_database = prepare_database(self.database, quarantine=quarantine_unsupported)
            fd = os.open(self.database, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
            os.close(fd)
            self.store = Store(self.database, self)
        except BlockingIOError:
            self.lock.close()
            raise Blocked('worktree writer lock already held; wait for its writer') from None
        except OSError as exc:
            self.lock.close()
            if wait:
                raise Blocked('worktree writer lock is busy and this platform cannot wait: ' + str(exc)) from None
            raise
        except BaseException:
            self.lock.close()
            raise
    def assert_held(self):
        if self.lock.closed:
            raise Blocked('writer lock closed')
    def close(self):
        self.store.close()
        self.lock.close()
    def __enter__(self): return self
    def __exit__(self, *exc): self.close()

class Store:
    def __init__(self, path, authority):
        self.authority = authority
        self.path = Path(path)
        self.db = sqlite3.connect(path, isolation_level=None)
        self.db.row_factory = sqlite3.Row
        # These progress tables neither deserialize nor settle legacy effects.
        self.db.executescript("""
        CREATE TABLE IF NOT EXISTS execution_runs(
            run_id TEXT PRIMARY KEY, state TEXT NOT NULL, baseline TEXT NOT NULL,
            result TEXT, error TEXT);
        CREATE TABLE IF NOT EXISTS execution_tasks(
            run_id TEXT NOT NULL, task_id TEXT NOT NULL, state TEXT NOT NULL,
            baseline TEXT NOT NULL, result TEXT, details TEXT,
            PRIMARY KEY(run_id, task_id));
        CREATE TABLE IF NOT EXISTS execution_monitor_runs(
            run_id TEXT PRIMARY KEY, recording_version INTEGER NOT NULL,
            description TEXT NOT NULL, started_at REAL NOT NULL, runner_identity TEXT);
        CREATE TABLE IF NOT EXISTS execution_run_inputs(
            run_id TEXT PRIMARY KEY, contract TEXT NOT NULL, executor TEXT NOT NULL,
            authority TEXT NOT NULL, review_base TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS execution_history(
            seq INTEGER PRIMARY KEY AUTOINCREMENT, run_id TEXT NOT NULL, task_id TEXT,
            kind TEXT NOT NULL, state TEXT NOT NULL, details TEXT NOT NULL,
            recorded_at REAL NOT NULL);
        CREATE TABLE IF NOT EXISTS execution_review_executions(
            run_id TEXT NOT NULL, execution_id TEXT NOT NULL, role TEXT NOT NULL,
            review_ordinal INTEGER, fixing_round INTEGER, trigger_execution_id TEXT,
            predecessor_execution_id TEXT, review_base TEXT NOT NULL, review_head TEXT NOT NULL,
            dispatched_at REAL NOT NULL, PRIMARY KEY(run_id, execution_id));
        CREATE TABLE IF NOT EXISTS execution_review_attempts(
            seq INTEGER PRIMARY KEY AUTOINCREMENT, run_id TEXT NOT NULL,
            execution_id TEXT NOT NULL, state TEXT NOT NULL, uncertainty INTEGER NOT NULL,
            findings TEXT, reference_json TEXT NOT NULL, recorded_at REAL NOT NULL);
        CREATE TABLE IF NOT EXISTS execution_review_inputs(
            run_id TEXT NOT NULL, execution_id TEXT NOT NULL, input_checkpoints TEXT NOT NULL,
            PRIMARY KEY(run_id, execution_id));
        CREATE TABLE IF NOT EXISTS execution_usage_memberships(
            run_id TEXT NOT NULL, task_id TEXT NOT NULL, dispatched_at REAL NOT NULL,
            PRIMARY KEY(run_id, task_id));
        CREATE TABLE IF NOT EXISTS execution_usage_intervals(
            seq INTEGER PRIMARY KEY AUTOINCREMENT, run_id TEXT NOT NULL,
            occurrence_id TEXT NOT NULL, task_id TEXT, role TEXT NOT NULL,
            outcome TEXT NOT NULL, session_id TEXT, interval TEXT, unknown_reason TEXT,
            recorded_at REAL NOT NULL, UNIQUE(run_id, occurrence_id, role));
        """)
        self.db.executescript("""
        CREATE TABLE IF NOT EXISTS execution_observations(
            seq INTEGER PRIMARY KEY AUTOINCREMENT, run_id TEXT NOT NULL,
            recording_version INTEGER NOT NULL, occurrence_id TEXT NOT NULL,
            phase TEXT NOT NULL, task_id TEXT, kind TEXT NOT NULL,
            recorded_at REAL NOT NULL, facts TEXT NOT NULL);
        """)
    @contextmanager
    def transaction(self):
        self.authority.assert_held()
        self.db.execute('BEGIN IMMEDIATE')
        try:
            yield self.db
            self.db.execute('COMMIT')
        except BaseException:
            self.db.execute('ROLLBACK')
            raise
    def event(self, db, run, op, kind, payload):
        return db.execute('INSERT INTO wf_events(event_id,run_id,op_id,kind,payload) VALUES(?,?,?,?,?)',
                          (uuid.uuid4().hex, run, op, kind, canonical(payload))).lastrowid
    def _required_write(self, operation, write, completed):
        """Correct one failed required write only after reconciling its actual result.

        Each supplied write is an atomic local operation.  A storage exception may be
        raised after SQLite accepted it, so inspect its operation-local result before
        replaying the write.  This deliberately has no timer, retry loop, or effect
        replay: a second failed write is an actionable limit for that operation.
        """
        try:
            return write()
        except sqlite3.Error as first_error:
            try:
                if completed():
                    return None
            except sqlite3.Error as reconcile_error:
                raise Blocked('required ' + operation + ' persistence is uncertain; reread failed: ' + str(reconcile_error)) from reconcile_error
            try:
                return write()
            except sqlite3.Error as retry_error:
                raise Blocked('required ' + operation + ' persistence failed after safe correction: ' + str(retry_error)) from retry_error

    def _history_insert(self, db, run, task, kind, state, details, recorded_at):
        db.execute('INSERT INTO execution_history(run_id,task_id,kind,state,details,recorded_at) VALUES(?,?,?,?,?,?)',
                   (run, task, kind, state, details, recorded_at))

    def start(self, run, baseline, *, contract=None, executor=None, authority=None, review_base=None):
        """Persist private original inputs before the run can mutate dependent work."""
        from .processes import inspect_recorded_writers
        inspect_recorded_writers(self.db, 'start')
        if (self.db.execute("SELECT 1 FROM sqlite_master WHERE name='wf_runs'").fetchone() and
                self.db.execute('SELECT 1 FROM wf_runs WHERE run_id=?', (run,)).fetchone()):
            raise Blocked('historical run ID already exists; choose a fresh run ID, never replay it')
        saved_contract = canonical(contract if contract is not None else {})
        saved_executor = canonical(executor if executor is not None else {})
        saved_authority = canonical(authority if authority is not None else {})
        saved_base = review_base or baseline
        details = canonical({'baseline': baseline, 'review_base': saved_base})
        def write():
            with self.transaction() as db:
                db.execute("INSERT INTO execution_runs VALUES(?,'running',?,NULL,NULL)", (run, baseline))
                db.execute('INSERT INTO execution_run_inputs VALUES(?,?,?,?,?)',
                           (run, saved_contract, saved_executor, saved_authority, saved_base))
                self._history_insert(db, run, None, 'invocation', 'started', details, time.time())
        def completed():
            row = self.db.execute('SELECT baseline FROM execution_runs WHERE run_id=?', (run,)).fetchone()
            saved = self.input(run)
            return row is not None and row['baseline'] == baseline and saved == {
                'contract': json.loads(saved_contract), 'executor': json.loads(saved_executor),
                'authority': json.loads(saved_authority), 'review_base': saved_base}
        try:
            self._required_write('run input', write, completed)
        except sqlite3.IntegrityError:
            raise Blocked('run ID already exists; inspect its progress and choose a fresh run ID, never replay it') from None

    def history(self, run, task, kind, state, details=None, *, db=None):
        """Append operation-local facts; never replace a prior failed attempt."""
        details = canonical(details or {})
        recorded_at = time.time()
        if db is not None:
            self._history_insert(db, run, task, kind, state, details, recorded_at)
            return
        def write():
            with self.transaction() as tx:
                self._history_insert(tx, run, task, kind, state, details, recorded_at)
        def completed():
            return bool(self.db.execute(
                'SELECT 1 FROM execution_history WHERE run_id=? AND task_id IS ? AND kind=? AND state=? AND details=? AND recorded_at=?',
                (run, task, kind, state, details, recorded_at)).fetchone())
        self._required_write('operation history', write, completed)

    def task_facts(self, run, task):
        """Return only paths/artifacts recorded before an unfinished task interruption."""
        paths, artifacts = set(), set()
        for row in self.db.execute("SELECT details FROM execution_history WHERE run_id=? AND task_id=? AND kind='mutation' AND state='claimed' ORDER BY seq", (run, task)):
            try:
                facts = json.loads(row['details'])
            except (TypeError, ValueError):
                raise Blocked('resume cannot continue task ' + task + ': saved mutation facts are unreadable') from None
            for key, target in (('paths', paths), ('artifacts', artifacts)):
                values = facts.get(key, [])
                if not isinstance(values, list) or any(not isinstance(value, str) or not value for value in values):
                    raise Blocked('resume cannot continue task ' + task + ': saved mutation facts are invalid')
                target.update(values)
        return {'paths': sorted(paths), 'artifacts': sorted(artifacts)}

    def input(self, run):
        row = self.db.execute('SELECT contract,executor,authority,review_base FROM execution_run_inputs WHERE run_id=?', (run,)).fetchone()
        if not row:
            return None
        return {key: json.loads(row[key]) if key != 'review_base' else row[key]
                for key in ('contract', 'executor', 'authority', 'review_base')}
    def resume(self, run):
        """Reopen one actually failed/interrupted run from its retained input/history."""
        from .processes import inspect_recorded_writers
        inspect_recorded_writers(self.db, 'resume')
        row = self.db.execute('SELECT state,baseline,error FROM execution_runs WHERE run_id=?', (run,)).fetchone()
        if row is None:
            raise Blocked('resume needs an existing run with retained original input/history')
        if row['state'] not in ('failed', 'interrupted'):
            raise Blocked('resume only continues genuinely failed or interrupted runs')
        saved = self.input(run)
        if not saved or not isinstance(saved.get('contract'), dict) or not isinstance(saved['contract'].get('tasks'), list):
            raise Blocked('resume cannot continue: original contract/history is missing')
        details = canonical({'previous_state': row['state'], 'previous_error': row['error']})
        def write():
            with self.transaction() as db:
                db.execute("UPDATE execution_runs SET state='running',error=NULL WHERE run_id=?", (run,))
                self._history_insert(db, run, None, 'invocation', 'resumed', details, time.time())
        def completed():
            current = self.db.execute('SELECT state,error FROM execution_runs WHERE run_id=?', (run,)).fetchone()
            recorded = self.db.execute("SELECT 1 FROM execution_history WHERE run_id=? AND task_id IS NULL AND kind='invocation' AND state='resumed' AND details=?",
                                       (run, details)).fetchone()
            return current is not None and current['state'] == 'running' and current['error'] is None and bool(recorded)
        self._required_write('resume progress', write, completed)
        return {'baseline': row['baseline'], 'input': saved, 'previous_state': row['state'], 'previous_error': row['error']}

    def completed_checkpoints(self, run):
        """Reconcile retained checkpoint results before dispatching unfinished work."""
        completed = {}
        for row in self.db.execute("SELECT task_id,state,baseline,result FROM execution_tasks WHERE run_id=?", (run,)):
            history = self.db.execute("SELECT details FROM execution_history WHERE run_id=? AND task_id=? AND kind='checkpoint' AND state='passed' ORDER BY seq DESC LIMIT 1",
                                      (run, row['task_id'])).fetchone()
            if not history and row['state'] != 'complete':
                continue
            if not history:
                raise Blocked('resume cannot skip completed task ' + row['task_id'] + ': checkpoint operation history is missing')
            details = json.loads(history['details'])
            if not isinstance(details.get('sha'), str) or (row['state'] == 'complete' and details['sha'] != row['result']):
                raise Blocked('resume cannot skip completed task ' + row['task_id'] + ': checkpoint identity is uncertain')
            # A checkpoint is durable before the current task projection is updated.
            # Inspect that exact commit, not current HEAD/worktree, and never relaunch
            # task tools merely to repair the interrupted completion write.
            git(self.authority.project, 'cat-file', '-e', details['sha'] + '^{commit}')
            if row['state'] != 'complete':
                self.task(run, row['task_id'], 'complete', row['baseline'], details['sha'],
                          {'recovered_checkpoint': details})
            completed[row['task_id']] = details
        return completed

    def register_monitor_run(self, run, description, runner_identity=None):
        """Add recording metadata without touching ordinary progress rows."""
        from .monitoring import RECORDING_VERSION
        self.authority.assert_held()
        self.db.execute('INSERT INTO execution_monitor_runs(run_id,recording_version,description,started_at,runner_identity) VALUES(?,?,?,?,?)',
                        (run, RECORDING_VERSION, canonical(description), time.time(), canonical(runner_identity) if runner_identity else None))

    def append_monitor_observation(self, run, occurrence_id, phase, task_id, kind, facts):
        """One short append; a caller treats all errors as optional warnings."""
        self.authority.assert_held()
        recorded = self.db.execute('SELECT recording_version FROM execution_monitor_runs WHERE run_id=?', (run,)).fetchone()
        if not recorded:
            raise Blocked('monitor recording is not registered')
        return self.db.execute('INSERT INTO execution_observations(run_id,recording_version,occurrence_id,phase,task_id,kind,recorded_at,facts) VALUES(?,?,?,?,?,?,?,?)',
                               (run, recorded['recording_version'], occurrence_id, phase, task_id, kind, time.time(), canonical(facts))).lastrowid

    def monitor(self, run):
        row = self.db.execute('SELECT * FROM execution_monitor_runs WHERE run_id=?', (run,)).fetchone()
        if not row:
            return None
        return {'run': dict(row), 'observations': [dict(r) for r in self.db.execute('SELECT * FROM execution_observations WHERE run_id=? ORDER BY seq', (run,))]}

    def task(self, run, task, state, baseline, result=None, details=None):
        details = details or {}
        saved_details = canonical(details)
        existing = self.db.execute('SELECT state,baseline,result FROM execution_tasks WHERE run_id=? AND task_id=?',
                                   (run, task)).fetchone()
        if existing and existing['state'] == 'complete' and (state != 'complete' or baseline != existing['baseline'] or result != existing['result']):
            raise Blocked('completed task checkpoint is immutable; retain its original task identity')
        history = canonical({'baseline': baseline, 'result': result, **details})
        def write():
            with self.transaction() as db:
                db.execute('INSERT INTO execution_tasks VALUES(?,?,?,?,?,?) ON CONFLICT(run_id,task_id) DO UPDATE SET state=excluded.state,result=excluded.result,details=excluded.details',
                           (run, task, state, baseline, result, saved_details))
                self._history_insert(db, run, task, 'task', state, history, time.time())
        def completed():
            row = self.db.execute('SELECT state,baseline,result,details FROM execution_tasks WHERE run_id=? AND task_id=?',
                                  (run, task)).fetchone()
            return row is not None and tuple(row) == (state, baseline, result, saved_details)
        self._required_write('task progress for ' + task, write, completed)

    def review_dispatch(self, run, execution_id, *, role='reviewer', review_ordinal=1,
                        fixing_round=0, trigger_execution_id=None, predecessor_execution_id=None,
                        input_checkpoints=None, review_base, review_head):
        """Persist a real review/fixing dispatch before its dependent invocation.

        Dispatch identity, rather than monitoring callbacks, consumes the bounded chain slot.
        An uncertain invocation remains a retained limit and is never silently replayed.
        """
        if role not in ('reviewer', 'fixer') or not isinstance(execution_id, str) or not execution_id:
            raise Blocked('review execution needs a concrete reviewer/fixer identity')
        if input_checkpoints is not None and (role != 'reviewer' or review_ordinal != 1 or
                                              not isinstance(input_checkpoints, list) or
                                              not all(_review_input(item) for item in input_checkpoints)):
            raise Blocked('only the first reviewer may retain explicit selected input checkpoints')
        if review_ordinal not in (1, 2) or fixing_round not in (0, 1):
            raise Blocked('review chain exceeds two reviews or one fixing round')
        if role == 'reviewer' and fixing_round != review_ordinal - 1:
            raise Blocked('review ordinal and fixing round are inconsistent')
        if role == 'fixer' and fixing_round != 1:
            raise Blocked('fixer must consume the one fixing round')
        prior = self.review_chain(run, private=True)
        if prior['uncertain']:
            raise Blocked('review invocation outcome is uncertain; inspect it before any replay')
        if sum(item['role'] == 'reviewer' for item in prior['executions']) >= 2 or (role == 'fixer' and any(item['role'] == 'fixer' for item in prior['executions'])):
            raise Blocked('review chain limit already consumed; do not dispatch another review/fixing round')
        references = canonical({'base': review_base, 'head': review_head})
        saved_inputs = canonical(input_checkpoints) if input_checkpoints is not None else None
        def write():
            with self.transaction() as db:
                db.execute('INSERT INTO execution_review_executions VALUES(?,?,?,?,?,?,?,?,?,?)',
                           (run, execution_id, role, review_ordinal, fixing_round, trigger_execution_id,
                            predecessor_execution_id, review_base, review_head, time.time()))
                if saved_inputs is not None:
                    db.execute('INSERT INTO execution_review_inputs VALUES(?,?,?)', (run, execution_id, saved_inputs))
                db.execute('INSERT INTO execution_review_attempts(run_id,execution_id,state,uncertainty,findings,reference_json,recorded_at) VALUES(?,?,?,?,?,?,?)',
                           (run, execution_id, 'dispatched', 0, None, references, time.time()))
        def completed():
            dispatched = bool(self.db.execute('SELECT 1 FROM execution_review_executions WHERE run_id=? AND execution_id=?',
                                               (run, execution_id)).fetchone())
            if saved_inputs is None:
                return dispatched
            row = self.db.execute('SELECT input_checkpoints FROM execution_review_inputs WHERE run_id=? AND execution_id=?',
                                  (run, execution_id)).fetchone()
            return dispatched and row is not None and row['input_checkpoints'] == saved_inputs
        self._required_write('review dispatch history', write, completed)

    def review_outcome(self, run, execution_id, state, *, findings=None, uncertainty=False, references=None):
        if state not in ('approved', 'rejected', 'failed', 'interrupted'):
            raise Blocked('invalid review execution outcome')
        if not isinstance(findings, list) or any(not isinstance(item, str) for item in findings):
            raise Blocked('review findings must be a list of strings')
        refs = canonical(references or {})
        saved_findings = canonical(findings)
        def write():
            with self.transaction() as db:
                if not db.execute('SELECT 1 FROM execution_review_executions WHERE run_id=? AND execution_id=?',
                                  (run, execution_id)).fetchone():
                    raise Blocked('review outcome has no recorded dispatch')
                db.execute('INSERT INTO execution_review_attempts(run_id,execution_id,state,uncertainty,findings,reference_json,recorded_at) VALUES(?,?,?,?,?,?,?)',
                           (run, execution_id, state, int(uncertainty), saved_findings, refs, time.time()))
        def completed():
            return bool(self.db.execute('SELECT 1 FROM execution_review_attempts WHERE run_id=? AND execution_id=? AND state=? AND uncertainty=? AND findings=? AND reference_json=?',
                                        (run, execution_id, state, int(uncertainty), saved_findings, refs)).fetchone())
        self._required_write('review outcome history', write, completed)

    def review_chain(self, run, *, private=False):
        executions = []
        for row in self.db.execute('SELECT * FROM execution_review_executions WHERE run_id=? ORDER BY dispatched_at,execution_id', (run,)):
            attempts = [dict(item) for item in self.db.execute('SELECT state,uncertainty,findings,reference_json FROM execution_review_attempts WHERE run_id=? AND execution_id=? ORDER BY seq', (run, row['execution_id']))]
            latest = attempts[-1] if attempts else {'state': 'unknown', 'uncertainty': 1, 'findings': None, 'reference_json': '{}'}
            item = {'execution_id': row['execution_id'], 'role': row['role'], 'review_ordinal': row['review_ordinal'],
                    'fixing_round': row['fixing_round'], 'trigger_execution_id': row['trigger_execution_id'],
                    'predecessor_execution_id': row['predecessor_execution_id'], 'state': latest['state'],
                    'uncertain': bool(latest['uncertainty']), 'references': json.loads(latest['reference_json']),
                    'attempt_count': len(attempts)}
            inputs = self.db.execute('SELECT input_checkpoints FROM execution_review_inputs WHERE run_id=? AND execution_id=?',
                                     (run, row['execution_id'])).fetchone()
            if inputs is not None:
                item['input_checkpoints'] = json.loads(inputs['input_checkpoints'])
            if private:
                item['findings'] = [json.loads(attempt['findings']) for attempt in attempts if attempt['findings'] is not None]
            else:
                item['references'].pop('saved_session', None)
                # Parsed actionable findings are safe owner output; raw reviewer JSON stays private.
                item['findings'] = json.loads(latest['findings']) if latest['findings'] is not None else []
            executions.append(item)
        return {'executions': executions, 'review_count': sum(item['role'] == 'reviewer' for item in executions),
                'fixing_round_count': sum(item['role'] == 'fixer' for item in executions),
                'uncertain': any(item['uncertain'] for item in executions)}

    def usage_membership(self, run, task):
        """Best-effort distinct task dispatch membership, never an attempt counter."""
        try:
            self.authority.assert_held()
            self.db.execute('INSERT OR IGNORE INTO execution_usage_memberships VALUES(?,?,?)',
                            (run, task, time.time()))
            return True
        except (sqlite3.Error, Blocked):
            return False

    def usage_interval(self, run, occurrence_id, *, task=None, role, outcome, interval=None):
        """Append one optional prompt interval without affecting workflow control flow."""
        try:
            self.authority.assert_held()
            if not isinstance(occurrence_id, str) or not occurrence_id or not isinstance(role, str) or not role:
                raise ValueError('usage interval needs occurrence and role')
            if interval is not None and not isinstance(interval, dict):
                raise ValueError('usage interval must be a record or unavailable')
            session_id = interval.get('session_id') if interval else None
            if not isinstance(session_id, str):
                session_id = None
            self.db.execute('INSERT OR IGNORE INTO execution_usage_intervals(run_id,occurrence_id,task_id,role,outcome,session_id,interval,unknown_reason,recorded_at) VALUES(?,?,?,?,?,?,?,?,?)',
                            (run, occurrence_id, task, role, outcome, session_id,
                             canonical(interval) if interval is not None else None,
                             None if interval is not None else 'usage_observation_unavailable', time.time()))
            return True
        except (sqlite3.Error, Blocked, ValueError):
            return False

    def usage_summary(self, run):
        """Safe optional accounting projection; legacy/missing data is unknown, never zero."""
        try:
            members = [row['task_id'] for row in self.db.execute(
                'SELECT task_id FROM execution_usage_memberships WHERE run_id=? ORDER BY task_id', (run,))]
            rows = [dict(row) for row in self.db.execute(
                'SELECT * FROM execution_usage_intervals WHERE run_id=? ORDER BY seq', (run,))]
        except sqlite3.Error:
            return {'state': 'unknown', 'reason': 'usage_storage_unavailable'}
        if not members and not rows:
            return {'state': 'unknown', 'reason': 'usage_unavailable'}
        def totals(items):
            values = {'input': 0, 'output': 0, 'cache_read': 0, 'cache_write': 0, 'total_tokens': 0, 'estimated_usd': 0}
            complete = {key: True for key in values}
            for item in items:
                record = json.loads(item['interval']) if item['interval'] else None
                for key, source in (('input', ('tokens', 'input')), ('output', ('tokens', 'output')),
                                    ('cache_read', ('tokens', 'cache_read')), ('cache_write', ('tokens', 'cache_write')),
                                    ('total_tokens', ('total_tokens',)), ('estimated_usd', ('estimated_usd',))):
                    value = record
                    for part in source:
                        value = value.get(part) if isinstance(value, dict) else None
                    value = value.get('value') if isinstance(value, dict) else None
                    if isinstance(value, (int, float)) and not isinstance(value, bool):
                        values[key] += value
                    else:
                        complete[key] = False
            return {key: values[key] if complete[key] else None for key in values}
        try:
            worker_rows = [row for row in rows if row['role'] != 'reviewer']
            reviewer_rows = [row for row in rows if row['role'] == 'reviewer']
            worker_totals, reviewer_totals = totals(worker_rows), totals(reviewer_rows)
        except (TypeError, ValueError):
            return {'state': 'unknown', 'reason': 'usage_record_unreadable'}
        known_tasks = {row['task_id'] for row in worker_rows if row['task_id'] is not None}
        return {'state': 'partial' if len(known_tasks) < len(members) or any(row['interval'] is None for row in rows) else 'available',
                'memberships': members, 'interval_count': len(rows),
                'worker_totals': worker_totals, 'reviewer_totals': reviewer_totals,
                'unknown_reason': None if len(known_tasks) == len(members) and all(row['interval'] for row in rows)
                                  else 'incomplete_optional_usage_coverage'}

    def finish(self, run, state, result=None, error=None):
        details = canonical({'result': result, 'error': error} if error else {'result': result})
        def write():
            with self.transaction() as db:
                db.execute('UPDATE execution_runs SET state=?,result=?,error=? WHERE run_id=?', (state, result, error, run))
                self._history_insert(db, run, None, 'invocation', state, details, time.time())
        def completed():
            row = self.db.execute('SELECT state,result,error FROM execution_runs WHERE run_id=?', (run,)).fetchone()
            return row is not None and tuple(row) == (state, result, error)
        self._required_write('run progress', write, completed)
    def abandon(self, run):
        """Release an explicitly abandoned run, never replay or complete its effects.

        The worktree lock excludes cooperating controllers. Inspect recorded live
        identities and scopes as well: a stopped row is not proof of an empty child.
        No process is signalled and no worktree bytes are changed.
        """
        from .processes import inspect_recorded_writers

        with self.transaction() as db:
            current = db.execute('SELECT * FROM execution_runs WHERE run_id=?', (run,)).fetchone()
            if current:
                db.execute("UPDATE execution_runs SET state='abandoned' WHERE run_id=?", (run,))
                # Monitoring is optional: an append failure must not veto explicit abandon.
                try:
                    if db.execute('SELECT 1 FROM execution_monitor_runs WHERE run_id=?', (run,)).fetchone():
                        db.execute('INSERT INTO execution_observations(run_id,recording_version,occurrence_id,phase,task_id,kind,recorded_at,facts) VALUES(?,?,?,?,?,?,?,?)',
                                   (run, 1, uuid.uuid4().hex, 'terminal', None, 'abandoned', time.time(), canonical({})))
                except sqlite3.Error:
                    pass
                return dict(db.execute('SELECT * FROM execution_runs WHERE run_id=?', (run,)).fetchone())
            if not db.execute("SELECT 1 FROM sqlite_master WHERE name='wf_runs'").fetchone():
                raise Blocked('unknown run; select the historical run to abandon')
            row=db.execute('SELECT * FROM wf_runs WHERE run_id=?',(run,)).fetchone()
            if not row:raise Blocked('unknown run; select the historical run to abandon')
            if row['state']=='ABANDONED':return dict(row)
            if not row['reservation']:
                raise Blocked('run already released; only a reserved run can be abandoned')
            inspect_recorded_writers(db, 'abandon')
            db.execute("UPDATE wf_runs SET state='ABANDONED',reservation=0 WHERE run_id=?",(run,))
            self.event(db,run,None,'abandoned',{'reason':'explicit operator abandon; partial work and incomplete effects retained'})
            return dict(db.execute('SELECT * FROM wf_runs WHERE run_id=?',(run,)).fetchone())

    def close(self): self.db.close()

# Semantic reader v1. Internal proof tables are intentionally not a consumer API.
HISTORY_FIELDS = frozenset(('task_id', 'attempt_id', 'attempt', 'runtime_revision',
    'compatibility', 'state', 'sha', 'head', 'base', 'review_id', 'gate_id', 'action',
    'evidence_id', 'item_id', 'status', 'exit_code', 'collected', 'revision',
    'outcome', 'handler', 'version', 'count', 'maximum', 'failure_key',
    'binding_hash', 'contract_hash', 'scope_hash', 'approval_hash', 'source_hash', 'baseline'))


def read_history(db, run, *, version=1):
    """Read an existing SQLite snapshot; never DDL, saver deserialization or writes.

    Caller opens mode=ro and BEGIN for a consistent WAL snapshot. Legacy v1 runs
    have no attempts/config archive: they remain historical, never executable.
    Event detail fields are explicitly allowlisted; private receipts stay SQL.
    Retained YAML/graph is private backend data, not a public projection.
    """
    if version != 1:
        raise Blocked('unsupported history reader version; use semantic reader v1')
    if [r[0] for r in db.execute('SELECT version FROM wf_meta')] != [1]:
        raise Blocked('unsupported application schema; history cannot interpret version')
    def table(name):
        return bool(db.execute('SELECT 1 FROM sqlite_master WHERE type=\'table\' AND name=?', (name,)).fetchone())
    row = db.execute('SELECT run_id,config_hash,state,reservation FROM wf_runs WHERE run_id=?', (run,)).fetchone()
    if not row:
        raise Blocked('unknown history run')
    attempts = [dict(r) for r in db.execute('SELECT run_id,attempt,runtime_revision,compatibility,workflow_yaml,graph FROM wf_attempts WHERE run_id=? ORDER BY attempt', (run,))] if table('wf_attempts') else []
    events = []
    for event in db.execute('SELECT * FROM wf_events WHERE run_id=? ORDER BY seq', (run,)):
        payload = json.loads(event['payload'])
        details = {k:v for k,v in payload.items() if k in HISTORY_FIELDS and (v is None or type(v) in (str,int,bool))}
        events.append({'seq':event['seq'], 'event_id':event['event_id'],
                       'operation_id':event['op_id'], 'kind':event['kind'], 'details':details})
    tasks = []
    if table('wf_tasks'):
        for task in db.execute('SELECT * FROM wf_tasks WHERE run_id=? ORDER BY approved_order', (run,)):
            contract = json.loads(task['contract'])
            baseline = json.loads(task['baseline']) if task['baseline'] else {}
            checkpoint = json.loads(task['checkpoint']) if task['checkpoint'] else {}
            tasks.append({'task_id':task['task_id'], 'order':task['approved_order'],
                          'depends':contract.get('depends', []), 'state':task['state'],
                          'baseline_sha':baseline.get('head'), 'result_sha':checkpoint.get('sha')})
    operations = [dict(r) for r in db.execute('SELECT op_id,node_id,kind,phase FROM wf_operations WHERE run_id=? ORDER BY rowid', (run,))]
    return {'reader_version':1, 'application_schema':1, 'run':dict(row),
            'execution_support':'historical-read-only',
            'observed_liveness':None, 'attempts':attempts, 'tasks':tasks,
            'events':events, 'operations':operations}
