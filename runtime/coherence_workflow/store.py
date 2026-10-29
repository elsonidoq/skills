"""Worktree writer lock, ordinary progress, and read-only historical access."""
from contextlib import contextmanager
import fcntl
import hashlib
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
        CREATE TABLE IF NOT EXISTS execution_review_suggestions(
            attempt_seq INTEGER PRIMARY KEY, suggestions TEXT NOT NULL);
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

    def _worker_session(self, session, *, operation):
        if not isinstance(session, dict) or not isinstance(session.get('id'), str) or not session['id']:
            raise Blocked(operation + ' needs an exact saved task-worker session identity; inspect retained history or use an authorized fresh context')
        if not isinstance(session.get('file'), str) or not session['file']:
            raise Blocked(operation + ' needs an exact saved task-worker session file; inspect retained history or use an authorized fresh context')
        return {'id': session['id'], 'file': session['file']}

    def reserve_worker_dispatch(self, run, task, invocation_id, session):
        """Durably consume one same-task/session worker allowance before provider dispatch."""
        if not isinstance(invocation_id, str) or not invocation_id:
            raise ValueError('worker dispatch needs an invocation ID')
        selected = None if session is None else self._worker_session(session, operation='worker dispatch')
        rows = self.db.execute(
            "SELECT state,details FROM execution_history WHERE run_id=? AND task_id=? "
            "AND kind='worker_dispatch' ORDER BY seq", (run, task)).fetchall()
        reservations, bindings = {}, {}
        for row in rows:
            try:
                facts = json.loads(row['details'])
                prior_id = facts['invocation_id']
                if not isinstance(prior_id, str) or not prior_id:
                    raise ValueError
                if row['state'] == 'reserved':
                    prior = facts.get('session')
                    if prior is not None:
                        prior = self._worker_session(prior, operation='retained worker dispatch')
                    if prior_id in reservations:
                        raise ValueError
                    reservations[prior_id] = prior
                elif row['state'] == 'bound':
                    bound = self._worker_session(facts.get('session'), operation='retained worker dispatch')
                    if prior_id in bindings and bindings[prior_id] != bound:
                        raise ValueError
                    bindings[prior_id] = bound
                else:
                    raise ValueError
            except (TypeError, ValueError, KeyError, Blocked) as exc:
                raise Blocked('worker dispatch history is missing or uncertain for task ' + task +
                              '; inspect retained invocation history before continuation') from exc
        if invocation_id in reservations or invocation_id in bindings:
            raise Blocked('worker dispatch invocation is already reserved; inspect retained invocation history before continuation')
        if session is None:
            if reservations:
                raise Blocked('worker dispatch lacks an exact saved task-worker session for task ' + task +
                              '; inspect retained history before continuation')
        else:
            unresolved = [prior_id for prior_id, prior in reservations.items()
                          if prior is None and prior_id not in bindings]
            if unresolved:
                raise Blocked('worker dispatch history has an unbound fresh session for task ' + task +
                              '; inspect retained invocation ' + unresolved[-1] + ' before continuation')
            used = {prior_id for prior_id, prior in reservations.items()
                    if (bindings.get(prior_id) or prior) == selected}
            if len(used) >= 3:
                raise Blocked('worker dispatch allowance exhausted for task ' + task + ' session ' + selected['id'] +
                              ': used initial plus 2 further calls; inspect retained recovery or use an owner-authorized fresh context')
        details = canonical({'invocation_id': invocation_id, 'session': selected})
        def write():
            with self.transaction() as db:
                self._history_insert(db, run, task, 'worker_dispatch', 'reserved', details, time.time())
        def completed():
            return bool(self.db.execute(
                "SELECT 1 FROM execution_history WHERE run_id=? AND task_id=? AND kind='worker_dispatch' "
                "AND state='reserved' AND details=?", (run, task, details)).fetchone())
        self._required_write('worker dispatch reservation', write, completed)

    def bind_worker_dispatch(self, run, task, invocation_id, session):
        """Associate a pre-dispatch reservation with the session the adapter actually opened."""
        actual = self._worker_session(session, operation='worker dispatch binding')
        reservation = False
        for row in self.db.execute("SELECT details FROM execution_history WHERE run_id=? AND task_id=? "
                                   "AND kind='worker_dispatch' AND state='reserved'", (run, task)):
            try:
                if json.loads(row['details']).get('invocation_id') == invocation_id:
                    reservation = True
                    break
            except (TypeError, ValueError):
                raise Blocked('worker dispatch binding cannot inspect retained reservation; inspect invocation history before continuation') from None
        if not reservation:
            raise Blocked('worker dispatch binding lacks its retained reservation; inspect invocation history before continuation')
        details = canonical({'invocation_id': invocation_id, 'session': actual})
        def write():
            with self.transaction() as db:
                existing = db.execute("SELECT details FROM execution_history WHERE run_id=? AND task_id=? "
                                      "AND kind='worker_dispatch' AND state='bound'", (run, task)).fetchall()
                for row in existing:
                    facts = json.loads(row['details'])
                    if facts.get('invocation_id') == invocation_id:
                        if row['details'] != details:
                            raise Blocked('worker dispatch binding conflicts with retained session identity; inspect invocation history')
                        return
                self._history_insert(db, run, task, 'worker_dispatch', 'bound', details, time.time())
        def completed():
            return bool(self.db.execute(
                "SELECT 1 FROM execution_history WHERE run_id=? AND task_id=? AND kind='worker_dispatch' "
                "AND state='bound' AND details=?", (run, task, details)).fetchone())
        self._required_write('worker dispatch binding', write, completed)

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

    def review_policy(self, run):
        """Read retained policy; absent policy is deliberately historical behavior."""
        saved = self.input(run)
        if not saved:
            raise Blocked('review policy needs retained run input')
        policy = saved['authority'].get('review_policy') if isinstance(saved['authority'], dict) else None
        if policy is None:
            return 'historical-two-review-one-fixer'
        if policy != 'owner-pair-v1':
            raise Blocked('unsupported retained review policy ' + repr(policy) + '; inspect or use a compatible continuation')
        return policy

    def _actionable_rejection(self, run, execution_id, review_base, review_head):
        row = self.db.execute('SELECT role,review_base,review_head FROM execution_review_executions WHERE run_id=? AND execution_id=?',
                              (run, execution_id)).fetchone()
        if row is None or row['role'] != 'reviewer' or row['review_base'] != review_base or row['review_head'] != review_head:
            raise Blocked('pair authorization rejection/range does not match retained review execution')
        attempt = self.db.execute('SELECT state,uncertainty,findings FROM execution_review_attempts WHERE run_id=? AND execution_id=? ORDER BY seq DESC LIMIT 1',
                                  (run, execution_id)).fetchone()
        if attempt is None or attempt['state'] != 'rejected' or attempt['uncertainty']:
            raise Blocked('pair authorization needs a settled actionable rejection')
        try:
            findings = json.loads(attempt['findings'])
        except (TypeError, ValueError):
            findings = None
        if not isinstance(findings, list) or not findings:
            raise Blocked('pair authorization rejection has no actionable findings')

    def review_scope(self, run):
        saved = self.input(run)
        return hashlib.sha256(canonical(saved['contract'].get('tasks', [])).encode()).hexdigest()

    def _pair_rejection(self, run, execution_id, review_base, review_head, original_scope):
        self._actionable_rejection(run, execution_id, review_base, review_head)
        chain = self.review_chain(run, private=True)
        rejection = next(item for item in chain['executions'] if item['execution_id'] == execution_id)
        if rejection['review_ordinal'] < 2 or original_scope != self.review_scope(run):
            raise Blocked('pair grant needs a later rejection and the retained original scope; inspect original inputs')
        if chain['uncertain']:
            raise Blocked('pair grant cannot continue an uncertain stage; inspect invocation history')
        return rejection, chain

    @staticmethod
    def _pair_identity(value, name):
        if not isinstance(value, str) or not value:
            raise Blocked('pair authorization needs a concrete ' + name)
        return value

    def authorize_owner_pair(self, run, grant_id, *, rejecting_execution_id, review_base, review_head,
                             original_scope, fixer_execution_id, reviewer_execution_id):
        """Durably retain one affirmative owner pair, without a transcript or dispatch."""
        if self.review_policy(run) != 'owner-pair-v1':
            raise Blocked('retained review policy does not permit an additional owner pair')
        values = {name: self._pair_identity(value, name.replace('_', ' ')) for name, value in {
            'grant_id': grant_id, 'rejecting_execution_id': rejecting_execution_id, 'review_base': review_base,
            'review_head': review_head, 'original_scope': original_scope, 'fixer_execution_id': fixer_execution_id,
            'reviewer_execution_id': reviewer_execution_id}.items()}
        if values['fixer_execution_id'] == values['reviewer_execution_id']:
            raise Blocked('pair authorization needs distinct fixer and fresh reviewer identities')
        rejection, chain = self._pair_rejection(run, values['rejecting_execution_id'], values['review_base'],
                                               values['review_head'], values['original_scope'])
        if chain['executions'][-1]['execution_id'] != rejection['execution_id']:
            raise Blocked('pair authorization must follow the latest settled rejection; inspect retained chain')
        if any(item['execution_id'] in (fixer_execution_id, reviewer_execution_id) for item in chain['executions']):
            raise Blocked('pair identities already belong to an execution; select fresh assigned identities')
        facts = {'grant_id': values['grant_id'], 'decision': 'affirmative_actual_owner',
                 'rejecting_execution_id': values['rejecting_execution_id'], 'review_base': values['review_base'],
                 'review_head': values['review_head'], 'original_scope': values['original_scope'],
                 'fixer_execution_id': values['fixer_execution_id'], 'reviewer_execution_id': values['reviewer_execution_id']}
        encoded = canonical(facts)
        def write():
            with self.transaction() as db:
                duplicate = db.execute("SELECT 1 FROM execution_history WHERE run_id=? AND kind='review_pair_grant' AND details=?",
                                       (run, encoded)).fetchone()
                if duplicate:
                    return
                for row in db.execute("SELECT details FROM execution_history WHERE run_id=? AND kind='review_pair_grant'", (run,)):
                    try:
                        prior = json.loads(row['details'])
                    except (TypeError, ValueError):
                        continue
                    if (prior.get('grant_id') == values['grant_id'] or
                            prior.get('rejecting_execution_id') == values['rejecting_execution_id']):
                        raise Blocked('pair grant/rejection is already authorized; reuse its exact retained pair')
                self._history_insert(db, run, None, 'review_pair_grant', 'authorized', encoded, time.time())
        def completed():
            return bool(self.db.execute("SELECT 1 FROM execution_history WHERE run_id=? AND kind='review_pair_grant' AND state='authorized' AND details=?",
                                        (run, encoded)).fetchone())
        self._required_write('owner pair authorization', write, completed)
        return facts

    def authorize_routine_review_continuation(self, run, original_scope):
        """Record current owner authority for routine later review repairs in one exact run scope."""
        if self.review_policy(run) != 'owner-pair-v1':
            raise Blocked('retained review policy does not permit routine review continuation authority')
        if not isinstance(original_scope, str) or not original_scope:
            raise Blocked('routine review continuation authority needs the retained original scope')
        if original_scope != self.review_scope(run):
            raise Blocked('routine review continuation authority scope does not match retained original scope')
        facts = {'decision': 'affirmative_actual_owner', 'original_scope': original_scope}
        encoded = canonical(facts)
        def write():
            with self.transaction() as db:
                rows = db.execute("SELECT details FROM execution_history WHERE run_id=? AND kind='routine_review_authority'", (run,)).fetchall()
                for row in rows:
                    try:
                        prior = json.loads(row['details'])
                    except (TypeError, ValueError):
                        continue
                    if prior != facts:
                        raise Blocked('routine review continuation authority is already bound to another scope')
                if not any(row['details'] == encoded for row in rows):
                    self._history_insert(db, run, None, 'routine_review_authority', 'authorized', encoded, time.time())
        self._required_write('routine review continuation authority', write, lambda: bool(self.db.execute(
            "SELECT 1 FROM execution_history WHERE run_id=? AND kind='routine_review_authority' AND state='authorized' AND details=?", (run, encoded)).fetchone()))
        return facts

    def routine_review_authority(self, run, original_scope):
        """Return only current authority explicitly bound to this retained run scope."""
        if self.review_policy(run) != 'owner-pair-v1' or original_scope != self.review_scope(run):
            return None
        expected = canonical({'decision': 'affirmative_actual_owner', 'original_scope': original_scope})
        row = self.db.execute("SELECT details FROM execution_history WHERE run_id=? AND kind='routine_review_authority' AND state='authorized' AND details=? ORDER BY seq DESC LIMIT 1", (run, expected)).fetchone()
        return json.loads(row['details']) if row else None

    def reserve_owner_pair_fixer(self, run, grant_id, *, rejecting_execution_id, review_base, review_head, original_scope):
        """Atomically consume one grant for its exact fixer before any provider call."""
        if self.review_policy(run) != 'owner-pair-v1':
            raise Blocked('retained review policy does not permit an additional owner pair')
        self._pair_identity(grant_id, 'grant identity')
        rejection, chain = self._pair_rejection(run, rejecting_execution_id, review_base, review_head, original_scope)
        rows = self.db.execute("SELECT details,state FROM execution_history WHERE run_id=? AND kind IN ('review_pair_grant','review_pair_reservation') ORDER BY seq", (run,)).fetchall()
        grant = reservation = None
        for row in rows:
            try: facts = json.loads(row['details'])
            except (TypeError, ValueError): continue
            if facts.get('grant_id') == grant_id:
                if row['state'] == 'authorized': grant = facts
                elif row['state'] == 'fixer_reserved': reservation = facts
        expected = {'rejecting_execution_id': rejecting_execution_id, 'review_base': review_base,
                    'review_head': review_head, 'original_scope': original_scope}
        if grant is None or any(grant.get(key) != value for key, value in expected.items()):
            raise Blocked('pair grant does not match rejection, range, or original scope')
        last = chain['executions'][-1]
        if last['execution_id'] != rejection['execution_id']:
            if (last['execution_id'] != grant['fixer_execution_id'] or last['state'] != 'dispatched'):
                raise Blocked('pair fixer reservation cannot replace a started, failed, or completed stage; inspect retained invocation')
        if reservation is not None:
            if reservation.get('fixer_execution_id') != grant['fixer_execution_id']:
                raise Blocked('pair grant was consumed by a different fixer')
            return reservation
        facts = {**expected, 'grant_id': grant_id, 'fixer_execution_id': grant['fixer_execution_id'],
                 'reviewer_execution_id': grant['reviewer_execution_id']}
        encoded = canonical(facts)
        def write():
            with self.transaction() as db:
                existing = None
                for row in db.execute("SELECT details FROM execution_history WHERE run_id=? AND kind='review_pair_reservation'", (run,)):
                    try:
                        prior = json.loads(row['details'])
                    except (TypeError, ValueError):
                        continue
                    if prior.get('grant_id') == grant_id:
                        existing = row
                        break
                if existing:
                    if existing['details'] != encoded:
                        raise Blocked('pair grant was already consumed; inspect its retained reservation')
                    return
                self._history_insert(db, run, None, 'review_pair_reservation', 'fixer_reserved', encoded, time.time())
        def completed():
            return bool(self.db.execute("SELECT 1 FROM execution_history WHERE run_id=? AND kind='review_pair_reservation' AND state='fixer_reserved' AND details=?",
                                        (run, encoded)).fetchone())
        self._required_write('owner pair fixer reservation', write, completed)
        return facts

    def reserve_owner_pair_reviewer(self, run, grant_id, *, fixer_execution_id):
        """Reserve the grant's sole fresh reviewer only after its exact fixer succeeded."""
        if self.review_policy(run) != 'owner-pair-v1':
            raise Blocked('retained review policy does not permit an additional owner pair')
        reservation = None
        for row in self.db.execute("SELECT details FROM execution_history WHERE run_id=? AND kind='review_pair_reservation' AND state='fixer_reserved' ORDER BY seq", (run,)):
            try:
                facts = json.loads(row['details'])
            except (TypeError, ValueError):
                continue
            if facts.get('grant_id') == grant_id:
                reservation = facts
        if reservation is None:
            raise Blocked('pair reviewer needs a retained fixer reservation')
        if reservation['fixer_execution_id'] != fixer_execution_id:
            raise Blocked('pair reviewer must follow the grant-assigned successful fixer')
        fixer = self.db.execute('SELECT state,uncertainty FROM execution_review_attempts WHERE run_id=? AND execution_id=? ORDER BY seq DESC LIMIT 1',
                                (run, fixer_execution_id)).fetchone()
        if fixer is None or fixer['state'] != 'approved' or fixer['uncertainty']:
            raise Blocked('pair reviewer needs the grant-assigned successful fixer')
        chain = self.review_chain(run, private=True)
        if chain['uncertain'] or chain['executions'][-1]['execution_id'] != fixer_execution_id:
            raise Blocked('pair reviewer must immediately follow its successful fixer; inspect retained chain')
        facts = {**reservation, 'reviewer_execution_id': reservation['reviewer_execution_id']}
        encoded = canonical(facts)
        def write():
            with self.transaction() as db:
                existing = None
                for row in db.execute("SELECT details FROM execution_history WHERE run_id=? AND kind='review_pair_reservation' AND state='reviewer_reserved'", (run,)):
                    try:
                        prior = json.loads(row['details'])
                    except (TypeError, ValueError):
                        continue
                    if prior.get('grant_id') == grant_id:
                        existing = row
                        break
                if existing:
                    if existing['details'] != encoded: raise Blocked('pair reviewer reservation conflicts with retained grant')
                    return
                self._history_insert(db, run, None, 'review_pair_reservation', 'reviewer_reserved', encoded, time.time())
        self._required_write('owner pair reviewer reservation', write, lambda: bool(self.db.execute(
            "SELECT 1 FROM execution_history WHERE run_id=? AND kind='review_pair_reservation' AND state='reviewer_reserved' AND details=?", (run, encoded)).fetchone()))
        return facts

    def owner_pair_for_rejection(self, run, *, rejecting_execution_id, review_base, review_head, original_scope):
        """Return the one retained grant/reservation matching this exact rejection."""
        matched = None
        for row in self.db.execute("SELECT kind,state,details FROM execution_history WHERE run_id=? AND kind IN ('review_pair_grant','review_pair_reservation') ORDER BY seq", (run,)):
            try:
                facts = json.loads(row['details'])
            except (TypeError, ValueError):
                continue
            if all(facts.get(key) == value for key, value in {
                'rejecting_execution_id': rejecting_execution_id, 'review_base': review_base,
                'review_head': review_head, 'original_scope': original_scope}.items()):
                matched = {**facts, 'state': row['state'], 'kind': row['kind']}
        return matched

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
        # A resume is a continuation boundary: never silently reinterpret an unknown
        # retained policy, while absent policy deliberately preserves historical behavior.
        self.review_policy(run)
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

    def evidence_reassessment_for_rejection(self, run, rejecting_execution_id, *, review_base, review_head):
        """Return the one private same-head evidence reassessment authorization, if any."""
        matched = None
        for row in self.db.execute("SELECT state,details FROM execution_history WHERE run_id=? AND kind='evidence_reassessment' ORDER BY seq", (run,)):
            try:
                facts = json.loads(row['details'])
            except (TypeError, ValueError):
                continue
            if (facts.get('rejecting_execution_id') == rejecting_execution_id and
                    facts.get('review_base') == review_base and facts.get('review_head') == review_head):
                matched = {**facts, 'state': row['state']}
        return matched

    def authorize_evidence_reassessment(self, run, execution_id, *, rejecting_execution_id, review_base,
                                        review_head, diagnosis, evidence_digest):
        """Retain one coordinator basis before a same-head read-only reassessment."""
        if self.review_policy(run) != 'owner-pair-v1':
            raise Blocked('evidence reassessment needs retained owner-pair-v1 policy')
        if not all(isinstance(value, str) and value for value in
                   (execution_id, rejecting_execution_id, review_base, review_head, evidence_digest)):
            raise Blocked('evidence reassessment needs concrete execution, rejection, range, and evidence identities')
        if not isinstance(diagnosis, str):
            raise Blocked('evidence reassessment diagnosis must be text')
        chain = self.review_chain(run, private=True)
        if chain['uncertain'] or not chain['executions'] or chain['executions'][-1]['execution_id'] != rejecting_execution_id:
            raise Blocked('evidence reassessment needs the latest settled review rejection')
        rejection = chain['executions'][-1]
        summary = rejection['references'].get('review_summary')
        if (rejection['role'] != 'reviewer' or rejection['state'] != 'rejected' or rejection['findings'][-1] or
                not isinstance(summary, dict) or not summary.get('coverage_gaps') or
                rejection['references'].get('base') != review_base or rejection['references'].get('head') != review_head):
            raise Blocked('evidence reassessment needs an evidence/coverage-only settled rejection at its original range')
        prior_digest = rejection['references'].get('check_evidence_digest')
        changed_evidence = isinstance(prior_digest, str) and prior_digest != evidence_digest
        if not diagnosis.strip() and not changed_evidence:
            raise Blocked('evidence reassessment needs substantive targeted diagnosis or newly applicable retained evidence; unchanged handoff cannot dispatch review')
        existing = self.evidence_reassessment_for_rejection(run, rejecting_execution_id,
                                                            review_base=review_base, review_head=review_head)
        facts = {'execution_id': execution_id, 'rejecting_execution_id': rejecting_execution_id,
                 'review_base': review_base, 'review_head': review_head, 'diagnosis': diagnosis.strip(),
                 'evidence_digest': evidence_digest}
        encoded = canonical(facts)
        if existing is not None:
            if existing != {**facts, 'state': 'authorized'}:
                raise Blocked('evidence reassessment handoff is already retained; do not dispatch an unchanged or replacement review')
            return facts
        def write():
            with self.transaction() as db:
                self._history_insert(db, run, None, 'evidence_reassessment', 'authorized', encoded, time.time())
        self._required_write('evidence reassessment authorization', write, lambda: bool(self.db.execute(
            "SELECT 1 FROM execution_history WHERE run_id=? AND kind='evidence_reassessment' AND state='authorized' AND details=?",
            (run, encoded)).fetchone()))
        return facts

    def refresh_review_target_dispatch(self, run, execution_id, *, review_base, review_head):
        """Append one fresh read-only review after an unconsumed stale pair grant drifted."""
        if self.review_policy(run) != 'owner-pair-v1':
            raise Blocked('review target refresh needs retained owner-pair-v1 policy')
        chain = self.review_chain(run, private=True)
        last = chain['executions'][-1] if chain['executions'] else None
        if (chain['uncertain'] or last is None or last['role'] != 'reviewer' or last['state'] != 'rejected' or
                not last.get('findings') or not last['findings'][-1] or review_base != last['references'].get('base')):
            raise Blocked('review target refresh needs the latest settled actionable rejection')
        stale = self.owner_pair_for_rejection(run, rejecting_execution_id=last['execution_id'], review_base=review_base,
                                              review_head=last['references'].get('head'), original_scope=self.review_scope(run))
        if stale is None or stale['kind'] != 'review_pair_grant' or stale['state'] != 'authorized':
            raise Blocked('review target refresh needs an unreserved stale owner pair grant')
        if review_head == stale['review_head']:
            raise Blocked('review target refresh needs a changed current target')
        row = self.db.execute('SELECT state FROM execution_runs WHERE run_id=?', (run,)).fetchone()
        if row is None or row['state'] != 'failed':
            raise Blocked('review target refresh only continues a stopped failed run')
        references = canonical({'base': review_base, 'head': review_head})
        def write():
            with self.transaction() as db:
                db.execute('INSERT INTO execution_review_executions VALUES(?,?,?,?,?,?,?,?,?,?)',
                           (run, execution_id, 'reviewer', last['review_ordinal'], last['fixing_round'],
                            last['execution_id'], last['execution_id'], review_base, review_head, time.time()))
                db.execute('INSERT INTO execution_review_attempts(run_id,execution_id,state,uncertainty,findings,reference_json,recorded_at) VALUES(?,?,?,?,?,?,?)',
                           (run, execution_id, 'dispatched', 0, None, references, time.time()))
        self._required_write('refreshed review dispatch', write, lambda: bool(self.db.execute(
            'SELECT 1 FROM execution_review_executions WHERE run_id=? AND execution_id=?', (run, execution_id)).fetchone()))
        return {'review_ordinal': last['review_ordinal'], 'fixing_round': last['fixing_round'],
                'trigger_execution_id': last['execution_id']}

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
        if not isinstance(review_ordinal, int) or review_ordinal < 1 or not isinstance(fixing_round, int) or fixing_round < 0:
            raise Blocked('review execution needs positive ordinal/round values')
        if role == 'reviewer' and fixing_round != review_ordinal - 1 and not (
                fixing_round == 0 and self.review_policy(run) == 'owner-pair-v1'):
            raise Blocked('review ordinal and fixing round are inconsistent')
        if role == 'fixer' and (fixing_round < 1 or fixing_round > review_ordinal):
            raise Blocked('fixer needs a positive assigned fixing round')
        prior = self.review_chain(run, private=True)
        if prior['uncertain']:
            raise Blocked('review invocation outcome is uncertain; inspect it before any replay')
        if self.review_policy(run) == 'historical-two-review-one-fixer':
            if sum(item['role'] == 'reviewer' for item in prior['executions']) >= 2 or (role == 'fixer' and any(item['role'] == 'fixer' for item in prior['executions'])):
                raise Blocked('review chain limit already consumed; do not dispatch another review/fixing round')
        else:
            last = prior['executions'][-1] if prior['executions'] else None
            if last is None:
                if (role, review_ordinal, fixing_round, trigger_execution_id, predecessor_execution_id) != ('reviewer', 1, 0, None, None):
                    raise Blocked('review chain must start with fresh Review 1; correct the assigned stage')
            else:
                evidence = self.evidence_reassessment_for_rejection(
                    run, last['execution_id'], review_base=review_base, review_head=review_head)
                is_evidence_reassessment = (role == 'reviewer' and last['role'] == 'reviewer' and
                    last['state'] == 'rejected' and evidence is not None and evidence['execution_id'] == execution_id)
                expected_role, expected_state = ('fixer', 'rejected') if last['role'] == 'reviewer' else ('reviewer', 'approved')
                expected_ordinal = last['review_ordinal'] + (role == 'reviewer')
                expected_round = last['fixing_round'] + (role == 'fixer')
                if is_evidence_reassessment:
                    if ((last.get('findings') and last['findings'][-1]) or review_ordinal != last['review_ordinal'] + 1 or
                            fixing_round != last['fixing_round'] or trigger_execution_id != last['execution_id'] or
                            predecessor_execution_id != last['execution_id']):
                        raise Blocked('evidence reassessment has unsupported causal order; inspect retained handoff')
                elif (role != expected_role or last['state'] != expected_state or
                        review_ordinal != expected_ordinal or fixing_round != expected_round or
                        trigger_execution_id != last['execution_id'] or predecessor_execution_id != last['execution_id'] or
                        review_base != last['references'].get('base') or review_head != last['references'].get('head')):
                    raise Blocked('review dispatch has unsupported causal order/range; inspect the last settled stage')
                if role == 'fixer' and not (last.get('findings') and last['findings'][-1]):
                    raise Blocked('fixer dispatch needs an actionable settled rejection; inspect review findings')
                if fixing_round > 1:
                    rejection_id = last['execution_id'] if role == 'fixer' else last['trigger_execution_id']
                    rejection = next((item for item in prior['executions'] if item['execution_id'] == rejection_id), None)
                    grant = self.owner_pair_for_rejection(run, rejecting_execution_id=rejection_id,
                        review_base=review_base, review_head=rejection['references'].get('head') if rejection else None,
                        original_scope=self.review_scope(run))
                    reserved = 'fixer_reserved' if role == 'fixer' else 'reviewer_reserved'
                    if (grant is None or grant['state'] != reserved or
                            grant[role + '_execution_id'] != execution_id or
                            (role == 'reviewer' and grant['fixer_execution_id'] != last['execution_id'])):
                        raise Blocked('review dispatch needs its exact retained owner grant/reservation; authorize and reserve the assigned pair')
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

    def review_outcome(self, run, execution_id, state, *, findings=None, suggestions=None, uncertainty=False, references=None):
        if state not in ('approved', 'rejected', 'failed', 'interrupted'):
            raise Blocked('invalid review execution outcome')
        if not isinstance(findings, list) or any(not isinstance(item, str) for item in findings):
            raise Blocked('review findings must be a list of strings')
        if suggestions is None:
            suggestions = []
        if not isinstance(suggestions, list) or any(not isinstance(item, str) for item in suggestions):
            raise Blocked('review suggestions must be a list of strings')
        refs = canonical(references or {})
        saved_findings, saved_suggestions = canonical(findings), canonical(suggestions)
        def write():
            with self.transaction() as db:
                if not db.execute('SELECT 1 FROM execution_review_executions WHERE run_id=? AND execution_id=?',
                                  (run, execution_id)).fetchone():
                    raise Blocked('review outcome has no recorded dispatch')
                attempt = db.execute('INSERT INTO execution_review_attempts(run_id,execution_id,state,uncertainty,findings,reference_json,recorded_at) VALUES(?,?,?,?,?,?,?)',
                                     (run, execution_id, state, int(uncertainty), saved_findings, refs, time.time()))
                db.execute('INSERT INTO execution_review_suggestions(attempt_seq,suggestions) VALUES(?,?)',
                           (attempt.lastrowid, saved_suggestions))
        def completed():
            row = self.db.execute('SELECT seq FROM execution_review_attempts WHERE run_id=? AND execution_id=? AND state=? AND uncertainty=? AND findings=? AND reference_json=? ORDER BY seq DESC LIMIT 1',
                                  (run, execution_id, state, int(uncertainty), saved_findings, refs)).fetchone()
            return row is not None and bool(self.db.execute(
                'SELECT 1 FROM execution_review_suggestions WHERE attempt_seq=? AND suggestions=?',
                (row['seq'], saved_suggestions)).fetchone())
        self._required_write('review outcome history', write, completed)

    def review_chain(self, run, *, private=False):
        executions = []
        suggestions_table = bool(self.db.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name='execution_review_suggestions'").fetchone())
        for row in self.db.execute('SELECT * FROM execution_review_executions WHERE run_id=? ORDER BY dispatched_at,execution_id', (run,)):
            attempts = [dict(item) for item in self.db.execute('SELECT seq,state,uncertainty,findings,reference_json FROM execution_review_attempts WHERE run_id=? AND execution_id=? ORDER BY seq', (run, row['execution_id']))]
            for attempt in attempts:
                suggestion = (self.db.execute('SELECT suggestions FROM execution_review_suggestions WHERE attempt_seq=?',
                                              (attempt['seq'],)).fetchone() if suggestions_table else None)
                attempt['suggestions'] = suggestion['suggestions'] if suggestion is not None else '[]'
            latest = attempts[-1] if attempts else {'state': 'unknown', 'uncertainty': 1, 'findings': None, 'suggestions': '[]', 'reference_json': '{}'}
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
                item['suggestions'] = [json.loads(attempt['suggestions']) for attempt in attempts]
            else:
                item['references'].pop('saved_session', None)
                # Parsed findings/suggestions are safe owner output; raw reviewer JSON stays private.
                item['findings'] = json.loads(latest['findings']) if latest['findings'] is not None else []
                item['suggestions'] = json.loads(latest['suggestions'])
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
