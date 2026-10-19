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
                raise Blocked("run identity is immutable")
            if not old:
                db.execute("INSERT INTO wf_runs VALUES(?,?,'running',1)", (run, config_hash))
                self.event(db, run, None, 'reserved', {})

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
        if self.db.execute("SELECT 1 FROM wf_alarms WHERE state='active'").fetchone():
            raise Blocked("ORPHAN_PROCESS: replacement_allowed=false")
        if not row or row['state'] != 'running':
            raise Blocked("run does not hold running reservation")
        # Trusted adapter may admit its exact live host for a current tool request or
        # proven idle boundary. This is not a blanket exemption for host rows.
        from .tools import Gateway
        allowed = set(admitted_host_ops)
        if len(allowed) != len(admitted_host_ops):
            raise Blocked('duplicate host admission')
        active = self.db.execute("SELECT * FROM wf_operations WHERE kind='process' AND phase!='completed'").fetchall()
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

    def close(self):
        self.db.close()
