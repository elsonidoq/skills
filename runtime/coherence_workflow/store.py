"""Single-worktree authority and application ledger (separate from saver transactions)."""
from contextlib import contextmanager
import fcntl
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import sqlite3
import stat
import subprocess
import uuid


class Blocked(RuntimeError):
    """An unmet custody, capability or evidence condition; never logical success."""


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def safe_path(root, relative):
    if not isinstance(relative, str) or not relative or "\\" in relative or "\x00" in relative:
        raise Blocked("invalid relative path")
    parts = PurePosixPath(relative).parts
    if PurePosixPath(relative).is_absolute() or any(p in ("..", ".") for p in relative.split("/")):
        raise Blocked("unsafe relative path")
    root = Path(root).resolve(strict=True)
    p = root
    for part in parts:
        p = p / part
        if p.is_symlink():
            raise Blocked("symlink path component")
    if not p.resolve().is_relative_to(root):
        raise Blocked("path outside root")
    return p


def git(project, *args):
    if any(os.environ.get(k) for k in ('GIT_DIR','GIT_WORK_TREE','GIT_INDEX_FILE','GIT_COMMON_DIR','GIT_OBJECT_DIRECTORY','GIT_ALTERNATE_OBJECT_DIRECTORIES')):
        raise Blocked('ambient Git authority override')
    result = subprocess.run(["git", "--no-optional-locks", "-C", str(project), *args], capture_output=True, check=False)
    if result.returncode:
        raise Blocked("Git prerequisite: " + result.stderr.decode(errors="replace")[:400])
    return result.stdout


def private_file(path):
    s = path.lstat()
    if not stat.S_ISREG(s.st_mode) or s.st_uid != os.getuid() or s.st_mode & 0o077 or s.st_nlink != 1:
        raise Blocked("untrusted authority file: " + str(path))
    return (s.st_dev, s.st_ino)


class Authority:
    """Lock/binding live in Git's per-worktree admin dir; run roots cannot choose a DB."""
    def __init__(self, project, run_root=None):
        given = Path(project).absolute()
        if given != given.resolve():
            raise Blocked("project path must be canonical without symlinks")
        self.project = given.resolve(strict=True)
        if Path(git(self.project, "rev-parse", "--show-toplevel").decode().strip()).resolve() != self.project:
            raise Blocked("project must be worktree root")
        self.admin = Path(git(self.project, "rev-parse", "--absolute-git-dir").decode().strip()).resolve(strict=True)
        self.lock_path = self.admin / "coherence-workflow.lock"
        fd = os.open(self.lock_path, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
        self.lock = os.fdopen(fd, "r+")
        try:
            private_file(self.lock_path)
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError as exc:
                raise Blocked('worktree writer lock already held') from exc
            self.lock_identity = private_file(self.lock_path)
            self.root = safe_path(self.project, ".coherence/workflow")
            self.root.mkdir(mode=0o700, parents=True, exist_ok=True)
            if self.root.stat().st_uid != os.getuid() or self.root.stat().st_mode & 0o077:
                raise Blocked("storage must be private and owned")
            self.database = safe_path(self.project, ".coherence/workflow/workflow.sqlite")
            self.binding_path = self.admin / "coherence-workflow.binding"
            binding = {"version": 1, "project": str(self.project), "database": str(self.database),
                       "admin_device": self.admin.stat().st_dev, "admin_inode": self.admin.stat().st_ino}
            if self.binding_path.exists() or self.binding_path.is_symlink():
                private_file(self.binding_path)
                if json.loads(self.binding_path.read_text()) != binding:
                    raise Blocked("authority binding drift; explicit migration required")
            else:
                with os.fdopen(os.open(self.binding_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600), "w") as f:
                    f.write(canonical(binding)); f.flush(); os.fsync(f.fileno())
                self._sync_admin()
            self.binding_identity = private_file(self.binding_path)
            if not self.database.exists():
                os.close(os.open(self.database, os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_WRONLY, 0o600))
            self.db_identity = private_file(self.database)
            if run_root is not None:
                safe_path(self.project, run_root)
            self.store = Store(self.database, self)
        except BaseException:
            self.lock.close()
            raise

    def _sync_admin(self):
        fd = os.open(self.admin, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)

    def assert_held(self):
        if self.lock.closed or private_file(self.lock_path) != self.lock_identity:
            raise Blocked("writer lock identity lost")
        if private_file(self.binding_path) != self.binding_identity or private_file(self.database) != self.db_identity:
            raise Blocked("authority file identity changed")
        safe_path(self.project, ".coherence/workflow/workflow.sqlite")

    def close(self):
        if hasattr(self, "store"):
            self.store.close()
        self.lock.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()


class Store:
    def __init__(self, path, authority):
        self.authority = authority
        self.path = Path(path)
        self.db = sqlite3.connect(path, isolation_level=None, timeout=5)
        self.db.row_factory = sqlite3.Row
        if self.db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='wf_meta'").fetchone():
            if [r[0] for r in self.db.execute('SELECT version FROM wf_meta')] != [1]:
                self.db.close()
                raise Blocked('unsupported application schema; no automatic migration')
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("PRAGMA synchronous=FULL")
        self.db.execute("PRAGMA foreign_keys=ON")
        self.db.execute("PRAGMA busy_timeout=5000")
        self.db.executescript('''
        CREATE TABLE IF NOT EXISTS wf_meta(version INTEGER PRIMARY KEY CHECK(version=1));
        INSERT OR IGNORE INTO wf_meta VALUES(1);
        CREATE TABLE IF NOT EXISTS wf_runs(
          run_id TEXT PRIMARY KEY, config_hash TEXT NOT NULL, state TEXT NOT NULL,
          reservation INTEGER NOT NULL CHECK(reservation IN(0,1)));
        CREATE UNIQUE INDEX IF NOT EXISTS wf_one_reservation ON wf_runs(reservation) WHERE reservation=1;
        CREATE TABLE IF NOT EXISTS wf_operations(
          op_id TEXT PRIMARY KEY, run_id TEXT NOT NULL REFERENCES wf_runs,
          node_id TEXT NOT NULL, kind TEXT NOT NULL, args_hash TEXT NOT NULL,
          phase TEXT NOT NULL, intent TEXT NOT NULL, result TEXT,
          UNIQUE(run_id,node_id,kind));
        CREATE TABLE IF NOT EXISTS wf_events(
          seq INTEGER PRIMARY KEY AUTOINCREMENT, event_id TEXT NOT NULL UNIQUE,
          run_id TEXT NOT NULL REFERENCES wf_runs, op_id TEXT REFERENCES wf_operations,
          kind TEXT NOT NULL, payload TEXT NOT NULL, UNIQUE(op_id,kind));
        CREATE TABLE IF NOT EXISTS wf_processes(
          op_id TEXT PRIMARY KEY REFERENCES wf_operations, scope_kind TEXT NOT NULL
            CHECK(scope_kind IN('host','task_tools')), name TEXT NOT NULL UNIQUE,
          containment TEXT, identity TEXT, exit_code INTEGER, empty_receipt TEXT, reconciliation TEXT);
        CREATE TABLE IF NOT EXISTS wf_controllers(
          run_id TEXT PRIMARY KEY REFERENCES wf_runs, identity TEXT NOT NULL, phase TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS wf_alarms(
          alarm_id TEXT PRIMARY KEY, op_id TEXT NOT NULL REFERENCES wf_processes,
          kind TEXT NOT NULL CHECK(kind='ORPHAN_PROCESS'), state TEXT NOT NULL,
          original_seq INTEGER NOT NULL REFERENCES wf_events(seq), resolution TEXT);
        CREATE UNIQUE INDEX IF NOT EXISTS wf_active_alarm ON wf_alarms(op_id) WHERE state='active';
        ''')
        if [r[0] for r in self.db.execute("SELECT version FROM wf_meta")] != [1]:
            raise Blocked("unsupported application schema")
        self.verify_settings()

    def verify_settings(self):
        expected = {"journal_mode": "wal", "synchronous": 2, "foreign_keys": 1, "busy_timeout": 5000}
        for key, value in expected.items():
            if self.db.execute("PRAGMA " + key).fetchone()[0] != value:
                raise Blocked("SQLite setting mismatch: " + key)
        return expected

    @contextmanager
    def transaction(self):
        self.authority.assert_held()
        if self.db.in_transaction:
            raise Blocked("nested or externally held application transaction")
        self.db.execute("BEGIN IMMEDIATE")
        try:
            yield self.db
            self.db.execute("COMMIT")
        except BaseException:
            self.db.execute("ROLLBACK")
            raise

    def event(self, db, run, op, kind, payload):
        cur = db.execute("INSERT INTO wf_events(event_id,run_id,op_id,kind,payload) VALUES(?,?,?,?,?)",
                         (uuid.uuid4().hex, run, op, kind, canonical(payload)))
        return cur.lastrowid

    def reserve(self, run, config_hash):
        with self.transaction() as db:
            row = db.execute("SELECT * FROM wf_runs WHERE reservation=1").fetchone()
            if row and (row['run_id'] != run or row['config_hash'] != config_hash):
                raise Blocked("durable worktree reservation; reconcile original run")
            old = db.execute("SELECT * FROM wf_runs WHERE run_id=?", (run,)).fetchone()
            if old and (old['config_hash'] != config_hash or not old['reservation']):
                raise Blocked("run configuration/reservation mismatch; reconcile original run")
            if not old:
                db.execute("INSERT INTO wf_runs VALUES(?,?,'running',1)", (run, config_hash))
                self.event(db, run, None, 'reserved', {})

    def reserve_attempt(self, run, compatibility, revision, config, workflow_yaml):
        """Only settled compatible boundaries can adopt a different runtime revision."""
        with self.transaction() as db:
            old = db.execute('SELECT * FROM wf_runs WHERE run_id=?', (run,)).fetchone()
            exists = db.execute("SELECT 1 FROM sqlite_master WHERE name='wf_attempts'").fetchone()
            previous = db.execute('SELECT * FROM wf_attempts WHERE run_id=? ORDER BY attempt DESC LIMIT 1',
                                  (run,)).fetchone() if exists else None
            if old and not previous:
                raise Blocked('historical run is read-only; use explicit abandon after inspecting writers and partial work, then start a new run')
            if old and old['config_hash'] != compatibility:
                raise Blocked('attempt configuration/schema/authority incompatible; renew affected inputs explicitly')
            if previous and previous['runtime_revision'] != revision:
                if (db.execute("SELECT 1 FROM wf_operations WHERE run_id=? AND phase!='completed'", (run,)).fetchone() or
                        db.execute("SELECT 1 FROM wf_alarms a JOIN wf_operations o USING(op_id) JOIN wf_runs r USING(run_id) WHERE a.state='active' AND r.state!='ABANDONED'").fetchone()):
                    raise Blocked('incomplete effects block new runtime attempt; reconcile original SDK/tool/Git operations')
                if db.execute("SELECT 1 FROM sqlite_master WHERE name='wf_questions'").fetchone() and db.execute(
                        "SELECT 1 FROM wf_questions WHERE run_id=? AND stage NOT IN ('continued','cancelled')", (run,)).fetchone():
                    raise Blocked('pending original question blocks runtime attempt; settle original continuation')
            reserved = db.execute('SELECT * FROM wf_runs WHERE reservation=1').fetchone()
            if reserved and reserved['run_id'] != run:
                raise Blocked('durable worktree reservation; reconcile original run')
            if old and not old['reservation']:
                raise Blocked('completed run is read-only; start separately approved work')
            if not old:
                db.execute("INSERT INTO wf_runs VALUES(?,?,'running',1)", (run, compatibility))
                self.event(db, run, None, 'reserved', {})
            db.execute("""CREATE TABLE IF NOT EXISTS wf_attempts(
                run_id TEXT NOT NULL REFERENCES wf_runs, attempt INTEGER NOT NULL,
                runtime_revision TEXT, compatibility TEXT NOT NULL,
                workflow_yaml TEXT NOT NULL, graph TEXT NOT NULL,
                PRIMARY KEY(run_id,attempt))""")
            if not previous or previous['runtime_revision'] != revision:
                attempt = previous['attempt'] + 1 if previous else 0
                db.execute('INSERT INTO wf_attempts VALUES(?,?,?,?,?,?)',
                           (run, attempt, revision, compatibility, workflow_yaml, canonical(config)))
                self.event(db, run, None, 'attempt_started', {'attempt':attempt,
                           'runtime_revision':revision,'compatibility':compatibility})

    def abandon(self, run):
        """Release an explicitly abandoned run, never replay or complete its effects.

        The worktree lock excludes cooperating controllers. Inspect recorded live
        identities and scopes as well: a stopped row is not proof of an empty child.
        No process is signalled and no worktree bytes are changed.
        """
        from .containment import boot_id, process_identity

        def live(identity):
            if not identity or identity.get('boot') != boot_id():
                return False
            pid=identity['pid']
            if not Path(f'/proc/{pid}').exists():
                return False
            try:
                observed=process_identity(pid,identity['nonce'])
            except Blocked:
                if not Path(f'/proc/{pid}').exists():return False
                raise Blocked('abandon cannot inspect recorded PID; inspect its current identity before release') from None
            # Reparenting does not make a still-live child safe to replace.
            return all(observed[k]==identity[k] for k in ('boot','pid','start','uid'))

        with self.transaction() as db:
            row=db.execute('SELECT * FROM wf_runs WHERE run_id=?',(run,)).fetchone()
            if not row:raise Blocked('unknown run; select the historical run to abandon')
            if row['state']=='ABANDONED':return dict(row)
            if not row['reservation']:
                raise Blocked('run already released; only a reserved run can be abandoned')
            for controller in db.execute('SELECT identity FROM wf_controllers'):
                if live(json.loads(controller['identity'])):
                    raise Blocked('abandon refused: live controller; wait for that writer to stop and inspect again')
            for process in db.execute('SELECT identity,containment FROM wf_processes'):
                if process['identity'] and live(json.loads(process['identity'])):
                    raise Blocked('abandon refused: live child; inspect and stop its owning operation before release')
                if not process['containment']:continue
                receipt=json.loads(process['containment'])
                parent=Path(receipt['parent']);path=parent/receipt['name']
                if (parent != parent.resolve() or not parent.is_relative_to('/sys/fs/cgroup') or
                        path.parent != parent or path != path.resolve()):
                    raise Blocked('abandon cannot inspect recorded scope path; inspect custody before release')
                if not path.exists():continue
                # Even a replaced scope with live members is a conflict; stale
                # identity metadata alone, or a removed empty scope, is not.
                try:
                    events=dict(line.split() for line in (path/'cgroup.events').read_text().splitlines())
                    members=(path/'cgroup.procs').read_text().strip()
                except OSError:
                    raise Blocked('abandon cannot read recorded scope; inspect its membership before release') from None
                if events.get('populated') not in ('0','1'):
                    raise Blocked('abandon cannot determine scope membership; inspect before release')
                if events['populated']=='1' or members:
                    raise Blocked('abandon refused: populated child scope; wait for its writer to stop and inspect again')
            db.execute("UPDATE wf_runs SET state='ABANDONED',reservation=0 WHERE run_id=?",(run,))
            self.event(db,run,None,'abandoned',{'reason':'explicit operator abandon; partial work and incomplete effects retained'})
            return dict(db.execute('SELECT * FROM wf_runs WHERE run_id=?',(run,)).fetchone())

    def park(self, run):
        with self.transaction() as db:
            db.execute("UPDATE wf_runs SET state='parked' WHERE run_id=? AND reservation=1", (run,))
            self.event(db, run, None, 'parked', {})

    def intent(self, run, node, kind, args, details):
        args_hash = digest(args)
        with self.transaction() as db:
            row = db.execute("SELECT * FROM wf_operations WHERE run_id=? AND node_id=? AND kind=?", (run,node,kind)).fetchone()
            if row:
                if row['args_hash'] != args_hash or row['intent'] != canonical(details):
                    raise Blocked("operation input drift")
                return dict(row)
            op = uuid.uuid4().hex
            db.execute("INSERT INTO wf_operations VALUES(?,?,?,?,?,'intent',?,NULL)",
                       (op,run,node,kind,args_hash,canonical(details)))
            self.event(db,run,op,'intent',details)
            return dict(db.execute("SELECT * FROM wf_operations WHERE op_id=?", (op,)).fetchone())

    def operation(self, op):
        row = self.db.execute("SELECT * FROM wf_operations WHERE op_id=?", (op,)).fetchone()
        if not row:
            raise Blocked("unknown operation")
        return dict(row)

    def transition(self, op, before, after, result=None):
        with self.transaction() as db:
            row = self.operation(op)
            cur = db.execute("UPDATE wf_operations SET phase=?,result=? WHERE op_id=? AND phase=?",
                             (after, canonical(result) if result is not None else row['result'], op,before))
            if cur.rowcount != 1:
                raise Blocked("operation phase compare-and-set failed")
            self.event(db,row['run_id'],op,after,result or {})

    def assert_dispatchable(self, run, *, admitted_host_ops=()):
        self.authority.assert_held()
        row = self.db.execute("SELECT * FROM wf_runs WHERE run_id=? AND reservation=1", (run,)).fetchone()
        if self.db.execute("SELECT 1 FROM wf_alarms a JOIN wf_operations o USING(op_id) JOIN wf_runs r USING(run_id) WHERE a.state='active' AND r.state!='ABANDONED'").fetchone():
            raise Blocked("ORPHAN_PROCESS: replacement_allowed=false")
        if not row or row['state'] != 'running':
            raise Blocked("run does not hold running reservation")
        # Trusted adapter may admit its exact live host for a current tool request or
        # proven idle boundary. This is not a blanket exemption for host rows.
        from .tools import Gateway
        allowed = set(admitted_host_ops)
        if len(allowed) != len(admitted_host_ops):
            raise Blocked('duplicate host admission')
        active = self.db.execute("SELECT o.* FROM wf_operations o JOIN wf_runs r USING(run_id) WHERE o.kind='process' AND o.phase!='completed' AND r.state!='ABANDONED'").fetchall()
        found = set()
        for operation in active:
            if operation['op_id'] not in allowed:
                raise Blocked("unreconciled process operation; replacement_allowed=false")
            if operation['run_id'] != run or operation['phase'] != 'released':
                raise Blocked('host admission run/phase mismatch')
            details = json.loads(operation['intent'])
            process = self.db.execute('SELECT containment FROM wf_processes WHERE op_id=?',(operation['op_id'],)).fetchone()
            if not process or not process['containment']:
                raise Blocked('host containment unavailable')
            gateway = Gateway(self.authority, run, json.loads(process['containment'])['parent'], {})
            record, receipt = gateway._record(operation['op_id'])
            if record['scope_kind'] != 'host' or details.get('scope_kind') != 'host':
                raise Blocked('only host scopes may be explicitly admitted')
            identity = json.loads(record['identity'])
            gateway.containment.member(receipt, identity, details['nonce'])
            found.add(operation['op_id'])
        if found != allowed:
            raise Blocked('unknown/completed host admission')

    def register_controller(self, run):
        from .containment import process_identity
        identity = process_identity(os.getpid(), uuid.uuid4().hex)
        with self.transaction() as db:
            db.execute('INSERT INTO wf_controllers VALUES(?,?,?) ON CONFLICT(run_id) DO UPDATE SET identity=excluded.identity,phase=excluded.phase',
                       (run, canonical(identity), 'active'))
            self.event(db,run,None,'controller_started',{'identity':identity})
        return identity

    def settle_controller(self, run, state):
        with self.transaction() as db:
            db.execute("UPDATE wf_controllers SET phase='stopped' WHERE run_id=?",(run,))
            self.event(db,run,None,'controller_stopped',{'state':state})

    def backup(self, destination, *, authorization):
        if authorization != {'action':'sqlite-backup','database':str(self.path)}:
            raise Blocked('explicit settled backup authority required')
        self.authority.assert_held()
        if (self.db.execute("SELECT 1 FROM wf_operations WHERE phase!='completed'").fetchone() or
                self.db.execute("SELECT 1 FROM wf_alarms WHERE state='active'").fetchone()):
            raise Blocked('backup/migration requires settled operations')
        destination = Path(destination)
        if destination.exists() or destination.is_symlink() or destination.parent != destination.parent.resolve(strict=True):
            raise Blocked('backup destination must be fresh and canonical')
        fd = os.open(destination,os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_WRONLY,0o600); os.close(fd)
        target = sqlite3.connect(destination)
        try:
            self.db.backup(target)
            if target.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
                raise Blocked('SQLite backup integrity failed')
        finally:
            target.close()
        return {'path':str(destination),'sha256':hashlib.sha256(destination.read_bytes()).hexdigest(),'integrity':'ok'}

    def close(self):
        self.db.close()


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
                          'depends':contract['depends'], 'state':task['state'],
                          'baseline_sha':baseline.get('head'), 'result_sha':checkpoint.get('sha')})
    operations = [dict(r) for r in db.execute('SELECT op_id,node_id,kind,phase FROM wf_operations WHERE run_id=? ORDER BY rowid', (run,))]
    return {'reader_version':1, 'application_schema':1, 'run':dict(row),
            'execution_support':'attempt-v2' if attempts else 'historical-read-only',
            'observed_liveness':None, 'attempts':attempts, 'tasks':tasks,
            'events':events, 'operations':operations}
