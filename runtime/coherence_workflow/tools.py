"""Runner-only registered tool gateway: durable intent, gated launch, drain and audit."""
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import selectors
import subprocess
import sys
import time
import uuid

from jsonschema import Draft202012Validator

from .containment import Cgroup, process_identity, validate_process
from .store import Blocked, canonical, digest, git, safe_path


def fingerprint(path):
    s = path.lstat()
    if path.is_symlink():
        value = os.readlink(path).encode()
    elif path.is_file():
        value = path.read_bytes()
    else:
        raise Blocked('unsupported worktree entry')
    return {'hash': hashlib.sha256(value).hexdigest(), 'mode': s.st_mode, 'uid': s.st_uid,
            'device': s.st_dev, 'inode': s.st_ino}


def snapshot(project, owned):
    for name in owned:
        p = safe_path(project, name)
        if name.startswith(('.git/', '.coherence/')) or name in ('.git', '.coherence'):
            raise Blocked('tools cannot mutate authority storage')
        if p.exists() and not p.is_file():
            raise Blocked('owned tool path must be a file')
    names = set(git(project, 'ls-files', '-z').decode().split('\0'))
    names.update(git(project, 'ls-files', '--others', '--exclude-standard', '-z').decode().split('\0'))
    # Include ignored user data as well; runtime's private subtree alone is excluded.
    names.update(git(project, 'ls-files', '--others', '--ignored', '--exclude-standard', '-z').decode().split('\0'))
    files = {}
    for name in sorted(names - {''}):
        if name.startswith('.coherence/workflow/'):
            continue
        path = Path(project) / name
        files[name] = fingerprint(path) if path.exists() or path.is_symlink() else None
    return {'head': git(project,'rev-parse','HEAD').decode().strip(),
            'index': hashlib.sha256(git(project,'ls-files','--stage','-z')).hexdigest(),
            'files': files,
            'owned': {name: files.get(name) for name in owned}}


def reconcile(project, owned, baseline):
    now = snapshot(project, owned)
    if now['head'] != baseline['head'] or now['index'] != baseline['index']:
        raise Blocked('HEAD/index drift; no automatic Git replay')
    for name in set(now['files']) | set(baseline['files']):
        if name not in owned and now['files'].get(name) != baseline['files'].get(name):
            raise Blocked('unrelated file drift: ' + name)
    return now


def clean_owned(project, owned):
    config = git(project,'config','--null','--list')
    for entry in config.split(b'\0'):
        if entry.startswith(b'core.fsmonitor\n') and entry.split(b'\n',1)[1].lower() not in (b'false',b'0',b'off'):
            raise Blocked('fsmonitor process capability unavailable for uncontained inventory')
    for name in owned:
        safe_path(project, name)
        if git(project, 'status', '--porcelain=v1', '--untracked-files=all', '--', name):
            raise Blocked('preexisting dirty owned overlap: ' + name)


@dataclass(frozen=True)
class ProcessTool:
    id: str
    version: str
    arguments: dict
    build_argv: object
    owned_paths: tuple
    environment: dict

    def argv(self, args):
        Draft202012Validator(self.arguments).validate(args)
        result = self.build_argv(args)
        if not isinstance(result, list) or not result or not all(isinstance(x,str) and '\0' not in x for x in result):
            raise Blocked('invalid registered argv')
        executable = Path(result[0])
        if not executable.is_absolute() or executable != executable.resolve(strict=True) or not os.access(executable,os.X_OK):
            raise Blocked('registered executable unavailable/noncanonical')
        return result


class Gateway:
    def __init__(self, authority, run, containment_parent, tools):
        self.authority = authority
        self.store = authority.store
        self.run = run
        self.containment = Cgroup(containment_parent)
        self.tools = dict(tools)

    def launch(self, node, tool_id, version, args, phase_hook=None):
        """phase_hook is a trusted test fault seam, never supplied by workflow data."""
        hook = phase_hook or (lambda phase, op: None)
        self.store.assert_dispatchable(self.run)
        tool = self.tools.get(tool_id)
        if not tool or tool.version != version:
            raise Blocked('unknown registered tool/version')
        argv = tool.argv(args)
        owned = list(tool.owned_paths)
        if len(set(owned)) != len(owned):
            raise Blocked('duplicate owned paths')
        clean_owned(self.authority.project, owned)
        baseline = snapshot(self.authority.project, owned)
        nonce = uuid.uuid4().hex
        name = self.containment.reserve_name()
        details = {'tool': tool_id, 'version': version, 'argv': argv, 'environment': tool.environment,
                   'owned_paths': owned, 'baseline': baseline, 'nonce': nonce, 'name': name}
        # Node identity is unique; uncertain launch cannot be regenerated under the same key.
        existing = self.store.db.execute('SELECT 1 FROM wf_operations WHERE run_id=? AND node_id=? AND kind=?',
                                         (self.run,node,'process')).fetchone()
        if existing:
            raise Blocked('process operation requires explicit reconciliation, not replay')
        op = self.store.intent(self.run,node,'process',args,details)['op_id']
        with self.store.transaction() as db:
            db.execute("INSERT INTO wf_processes(op_id,scope_kind,name) VALUES(?,'task_tools',?)", (op,name))
        hook('intent',op)
        self.containment.create(name)
        hook('child_created',op)
        receipt = self.containment.receipt(name)
        self.containment.validate(receipt)
        with self.store.transaction() as db:
            db.execute('UPDATE wf_processes SET containment=? WHERE op_id=?', (canonical(receipt),op))
        self.store.transition(op,'intent','contained',receipt)
        hook('identity_persisted',op)
        read_gate, write_gate = os.pipe()
        read_ready, write_ready = os.pipe()
        manifest = {'containment': receipt, 'nonce': nonce, 'argv': argv,
                    'cwd': str(self.authority.project), 'environment': tool.environment}
        proc = None
        gate_released = False
        try:
            proc = subprocess.Popen([sys.executable,'-m','coherence_workflow.tool_process',
                                     str(read_gate), str(write_ready), canonical(manifest)],
                                    pass_fds=(read_gate,write_ready), stdin=subprocess.DEVNULL,
                                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            os.close(read_gate); read_gate = -1
            os.close(write_ready); write_ready = -1
            hook('spawned',op)
            sel = selectors.DefaultSelector()
            try:
                sel.register(read_ready, selectors.EVENT_READ)
                data = b''
                deadline = time.monotonic()+5
                while b'\n' not in data and len(data) < 4096:
                    if not sel.select(max(0,deadline-time.monotonic())):
                        raise Blocked('helper identity deadline')
                    chunk = os.read(read_ready,4096-len(data))
                    if not chunk:
                        raise Blocked('helper EOF before identity')
                    data += chunk
                identity = json.loads(data)
            finally:
                sel.close()
            if identity.get('pid') != proc.pid or identity.get('ppid') != os.getpid():
                raise Blocked('unexpected helper PID/parent')
            self.containment.member(receipt, identity, nonce)
            hook('identity_observed',op)
            with self.store.transaction() as db:
                db.execute('UPDATE wf_processes SET identity=? WHERE op_id=?', (canonical(identity),op))
            self.store.transition(op,'contained','prepared',identity)
            hook('registered',op)
            self.authority.assert_held()
            registered, durable_receipt = self._record(op)
            if durable_receipt != receipt or json.loads(registered['identity']) != identity:
                raise Blocked('durable registration differs before release')
            self.containment.member(receipt, identity, nonce)
            if reconcile(self.authority.project,owned,baseline) != baseline:
                raise Blocked('owned path drift before release')
            self.store.transition(op,'prepared','released',{'nonce':nonce})
            hook('release_persisted',op)
            os.write(write_gate,(nonce+'\n').encode())
            gate_released = True
            hook('released',op)
            return op, proc
        finally:
            for fd in (read_gate,write_gate,read_ready,write_ready):
                if fd >= 0:
                    os.close(fd)
            if proc is not None and not gate_released:
                # EOF is cancellation; no PID-only kill fallback.
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    pass

    def _record(self, op):
        row = self.store.db.execute('SELECT * FROM wf_processes WHERE op_id=?',(op,)).fetchone()
        if not row:
            raise Blocked('missing durable process record')
        row = dict(row)
        if not row['containment']:
            raise Blocked('unidentified reserved child; no adoption or kill')
        receipt = json.loads(row['containment'])
        self.containment.validate(receipt)
        if not row['identity']:
            raise Blocked('unregistered helper identity; no adoption/replacement')
        identity = json.loads(row['identity'])
        operation = self.store.operation(op)
        details = json.loads(operation['intent'])
        if operation['run_id'] != self.run or row['name'] != details['name'] or receipt['name'] != row['name']:
            raise Blocked('operation/run/child binding mismatch')
        group_proof = self.store.db.execute("SELECT payload FROM wf_events WHERE op_id=? AND kind='contained'",(op,)).fetchone()
        if not group_proof or json.loads(group_proof[0]) != receipt:
            raise Blocked('containment differs from durable identity receipt')
        if identity.get('nonce') != details['nonce'] or identity.get('boot') != receipt['boot'] or identity.get('uid') != os.getuid():
            raise Blocked('durable process identity/nonce mismatch')
        proof = self.store.db.execute("SELECT payload FROM wf_events WHERE op_id=? AND kind='prepared'",(op,)).fetchone()
        if not proof or json.loads(proof[0]) != identity:
            raise Blocked('process identity differs from prepared receipt')
        if Path(f"/proc/{identity['pid']}").exists():
            # Controller death can reparent an otherwise identical registered process.
            current = process_identity(identity['pid'],details['nonce'])
            validate_process(dict(identity,ppid=current['ppid']),details['nonce'])
        return row, receipt

    def settle(self, op, exit_code):
        row, receipt = self._record(op)
        operation = self.store.operation(op)
        populated = self.containment.populated(receipt)
        with self.store.transaction() as db:
            db.execute('UPDATE wf_processes SET exit_code=? WHERE op_id=?',(exit_code,op))
            if populated and row['scope_kind'] == 'task_tools':
                if not db.execute("SELECT 1 FROM wf_alarms WHERE op_id=? AND state='active'",(op,)).fetchone():
                    seq = self.store.event(db,self.run,op,'ORPHAN_PROCESS',{'logical_exit':exit_code,'replacement_allowed':False})
                    db.execute("INSERT INTO wf_alarms VALUES(?,?,'ORPHAN_PROCESS','active',?,NULL)", (uuid.uuid4().hex,op,seq))
                db.execute("UPDATE wf_runs SET state='blocked' WHERE run_id=?",(self.run,))
                return {'outcome':'blocked','alarm':'ORPHAN_PROCESS','replacement_allowed':False}
        if populated:
            return {'outcome':'idle_host','replacement_allowed':False}
        return self.resolve(op, drain=False)

    def resolve(self, op, drain=True):
        """Empty AND actual partial-work/Git audit required. Does not grant task acceptance."""
        row, receipt = self._record(op)
        operation = self.store.operation(op)
        details = json.loads(operation['intent'])
        if operation['phase'] == 'completed':
            recorded = json.loads(operation['result'])
            if (self.containment.populated(receipt) != 0 or
                reconcile(self.authority.project,details['owned_paths'],details['baseline']) != recorded['reconciliation']):
                raise Blocked('completed tool receipt no longer applicable')
            return recorded
        empty = self.containment.drain(receipt) if drain else {
            'containment': receipt, 'populated': self.containment.populated(receipt), 'observed_ns':time.time_ns()}
        if empty['populated'] != 0:
            raise Blocked('task tools not quiescent')
        observed = reconcile(self.authority.project, details['owned_paths'], details['baseline'])
        result = {'logical_exit':row['exit_code'],'empty_receipt':empty,'reconciliation':observed,
                  'replacement_allowed':True, 'task_accepted':False}
        with self.store.transaction() as db:
            db.execute('UPDATE wf_processes SET empty_receipt=?,reconciliation=? WHERE op_id=?',
                       (canonical(empty),canonical(observed),op))
            db.execute("UPDATE wf_alarms SET state='resolved',resolution=? WHERE op_id=? AND state='active'", (canonical(result),op))
            cur = db.execute("UPDATE wf_operations SET phase='completed',result=? WHERE op_id=? AND phase!='completed'",(canonical(result),op))
            if cur.rowcount:
                self.store.event(db,self.run,op,'completed',result)
            # Explicit continuation/approval is a later task; alarm resolution alone never resumes.
        return result

    def recover(self):
        """Observe durable scopes; never release/replay tools or adopt unknown identities."""
        results = []
        for row in self.store.db.execute("SELECT p.* FROM wf_processes p JOIN wf_operations o USING(op_id) WHERE o.phase!='completed'").fetchall():
            results.append(self.settle(row['op_id'], row['exit_code']))
        return results
