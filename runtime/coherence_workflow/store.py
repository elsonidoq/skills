"""Worktree writer lock, ordinary progress, and read-only historical access."""
from contextlib import contextmanager
import fcntl
import json
import os
from pathlib import Path, PurePosixPath
import sqlite3
import subprocess
import uuid
import time

class Blocked(RuntimeError):
    """An operation could not complete; partial work is retained."""

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)

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

class Authority:
    """An exclusive ordinary writer lock; old bindings are not launch eligibility."""
    def __init__(self, project):
        self.project = Path(project).resolve(strict=True)
        if Path(git(self.project, 'rev-parse', '--show-toplevel').decode().strip()).resolve() != self.project:
            raise Blocked('project must be the Git worktree root')
        admin = Path(git(self.project, 'rev-parse', '--absolute-git-dir').decode().strip())
        fd = os.open(admin / 'coherence-workflow.lock', os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
        self.lock = os.fdopen(fd, 'r+')
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            root = safe_path(self.project, '.coherence/workflow')
            root.mkdir(mode=0o700, parents=True, exist_ok=True)
            self.database = safe_path(self.project, '.coherence/workflow/workflow.sqlite')
            fd = os.open(self.database, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
            os.close(fd)
            self.store = Store(self.database, self)
        except BlockingIOError:
            self.lock.close()
            raise Blocked('worktree writer lock already held; wait for its writer') from None
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
    def start(self, run, baseline):
        from .processes import inspect_recorded_writers
        inspect_recorded_writers(self.db, 'start')
        if (self.db.execute("SELECT 1 FROM sqlite_master WHERE name='wf_runs'").fetchone() and
                self.db.execute('SELECT 1 FROM wf_runs WHERE run_id=?', (run,)).fetchone()):
            raise Blocked('historical run ID already exists; choose a fresh run ID, never replay it')
        try:
            self.db.execute("INSERT INTO execution_runs VALUES(?,'running',?,NULL,NULL)", (run,baseline))
        except sqlite3.IntegrityError:
            raise Blocked('run ID already exists; inspect its progress and choose a fresh run ID, never replay it') from None
    def register_monitor_run(self, run, description, runner_identity=None):
        """Add recording metadata without touching ordinary progress rows."""
        from .monitoring import RECORDING_VERSION
        self.authority.assert_held()
        self.db.execute('INSERT INTO execution_monitor_runs(run_id,recording_version,description,started_at,runner_identity) VALUES(?,?,?,?,?)',
                        (run, RECORDING_VERSION, canonical(description), time.time(), canonical(runner_identity) if runner_identity else None))

    def append_monitor_observation(self, run, occurrence_id, phase, task_id, kind, facts):
        """One short append; a caller treats all errors as optional warnings."""
        self.authority.assert_held()
        return self.db.execute('INSERT INTO execution_observations(run_id,recording_version,occurrence_id,phase,task_id,kind,recorded_at,facts) VALUES(?,?,?,?,?,?,?,?)',
                               (run, 1, occurrence_id, phase, task_id, kind, time.time(), canonical(facts))).lastrowid

    def monitor(self, run):
        row = self.db.execute('SELECT * FROM execution_monitor_runs WHERE run_id=?', (run,)).fetchone()
        if not row:
            return None
        return {'run': dict(row), 'observations': [dict(r) for r in self.db.execute('SELECT * FROM execution_observations WHERE run_id=? ORDER BY seq', (run,))]}

    def task(self, run, task, state, baseline, result=None, details=None):
        self.db.execute('INSERT INTO execution_tasks VALUES(?,?,?,?,?,?) ON CONFLICT(run_id,task_id) DO UPDATE SET state=excluded.state,result=excluded.result,details=excluded.details',
                        (run,task,state,baseline,result,canonical(details)))
    def finish(self, run, state, result=None, error=None):
        self.db.execute('UPDATE execution_runs SET state=?,result=?,error=? WHERE run_id=?', (state,result,error,run))
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
