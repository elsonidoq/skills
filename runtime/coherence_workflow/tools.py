"""Runner-only registered tool gateway: durable intent, gated launch, drain and audit."""
from dataclasses import dataclass
import hashlib
import json
import os
import stat
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
    result_reader: object = None

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
        self.task_origin = None

    def bind_task_origin(self, prefix, owned, baseline):
        if snapshot(self.authority.project, owned) != baseline:
            raise Blocked('task origin is not current verified baseline')
        self.task_origin = (prefix, tuple(owned), baseline)

    def _owned_admission(self, owned):
        if not self.task_origin or tuple(owned) != self.task_origin[1]:
            clean_owned(self.authority.project, owned)
            return
        prefix, _, expected = self.task_origin
        rows = self.store.db.execute("""SELECT o.* FROM wf_operations o JOIN wf_events e
            ON e.op_id=o.op_id AND e.kind='intent' WHERE o.run_id=? AND o.kind='process' ORDER BY e.seq""", (self.run,)).fetchall()
        matched = False
        for row in rows:
            if not row['node_id'].startswith(prefix):
                continue
            details = json.loads(row['intent'])
            if details['scope_kind'] != 'task_tools':
                continue
            if row['phase'] != 'completed':
                raise Blocked('unsettled task-origin operation')
            process, receipt = self._record(row['op_id'])
            result = json.loads(row['result'])
            if (self.containment.populated(receipt) or not result.get('replacement_allowed') or
                    any(details['baseline'][k] != expected[k] for k in ('head','index','files'))):
                raise Blocked('task-origin audit chain gap')
            event = self.store.db.execute("SELECT payload FROM wf_events WHERE op_id=? AND kind='completed'", (row['op_id'],)).fetchone()
            if not event or event[0] != row['result'] or process['reconciliation'] != canonical(result['reconciliation']):
                raise Blocked('task-origin result/event mismatch')
            expected = result['reconciliation']
            matched = True
        now = snapshot(self.authority.project, owned)
        if any(now[k] != expected[k] for k in ('head','index','files')):
            raise Blocked('unexplained task-origin drift')
        if not matched:
            clean_owned(self.authority.project, owned)

    def launch(self, node, tool_id, version, args, phase_hook=None, *, scope_kind='task_tools',
               inherited_fds=(), admitted_host_ops=()):
        """phase_hook is a trusted test fault seam, never supplied by workflow data."""
        hook = phase_hook or (lambda phase, op: None)
        if scope_kind not in ('host','task_tools'):
            raise Blocked('invalid process scope')
        if len(set(inherited_fds)) != len(inherited_fds):
            raise Blocked('duplicate inherited descriptor')
        for fd in inherited_fds:
            # Only explicit anonymous pipes, never authority/auth files, sockets or stdio.
            try:
                valid = (type(fd) is int and fd > 2 and stat.S_ISFIFO(os.fstat(fd).st_mode)
                         and os.readlink('/proc/self/fd/'+str(fd)).startswith('pipe:['))
            except OSError:
                valid = False
            if not valid:
                raise Blocked('inherited descriptors must be controller-owned pipes')
        self.store.assert_dispatchable(self.run, admitted_host_ops=admitted_host_ops)
        tool = self.tools.get(tool_id)
        if not tool or tool.version != version:
            raise Blocked('unknown registered tool/version')
        argv = tool.argv(args)
        owned = list(tool.owned_paths)
        if len(set(owned)) != len(owned):
            raise Blocked('duplicate owned paths')
        self._owned_admission(owned)
        baseline = snapshot(self.authority.project, owned)
        nonce = uuid.uuid4().hex
        name = self.containment.reserve_name()
        details = {'tool': tool_id, 'version': version, 'argv': argv, 'environment': tool.environment,
                   'owned_paths': owned, 'baseline': baseline, 'nonce': nonce, 'name': name,
                   'scope_kind':scope_kind}
        # Node identity is unique; uncertain launch cannot be regenerated under the same key.
        existing = self.store.db.execute('SELECT 1 FROM wf_operations WHERE run_id=? AND node_id=? AND kind=?',
                                         (self.run,node,'process')).fetchone()
        if existing:
            raise Blocked('process operation requires explicit reconciliation, not replay')
        op = self.store.intent(self.run,node,'process',args,details)['op_id']
        with self.store.transaction() as db:
            db.execute("INSERT INTO wf_processes(op_id,scope_kind,name) VALUES(?,?,?)", (op,scope_kind,name))
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
                                    pass_fds=(read_gate,write_ready,*inherited_fds), stdin=subprocess.DEVNULL,
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

    def _host_reconciliation(self, operation, details):
        """Replay only durable, kernel-empty same-run tool audits since host launch.

        Host lifetime spans task writes, but owns none of them. Original snapshots
        remain immutable; unknown gaps, forged receipts or Git changes still block.
        """
        import copy
        if self.store.db.execute("SELECT 1 FROM wf_alarms WHERE state='active'").fetchone():
            raise Blocked('host reconciliation blocked by active orphan alarm')
        original = self.store.db.execute("SELECT payload FROM wf_events WHERE op_id=? AND kind='intent'",(operation['op_id'],)).fetchone()
        if not original or original[0] != operation['intent']:
            raise Blocked('host original intent/event mismatch')
        expected = copy.deepcopy(details['baseline'])
        chain = []
        start = self.store.db.execute("SELECT seq FROM wf_events WHERE op_id=? AND kind='intent'",(operation['op_id'],)).fetchone()[0]
        rows = self.store.db.execute("""SELECT o.*, e.seq FROM wf_operations o
            JOIN wf_processes p USING(op_id) JOIN wf_events e ON e.op_id=o.op_id AND e.kind='intent'
            WHERE o.run_id=? AND p.scope_kind='task_tools' AND e.seq>? ORDER BY e.seq""",(self.run,start)).fetchall()
        # Preserve registered host-owned paths supported by the foundation (its
        # lifecycle fixture has these). SDK hosts own no worktree files. Mixing
        # direct host writes with task-tool audit chains is not supported.
        if details['owned_paths']:
            if rows:
                raise Blocked('mixed direct host writes/task-tool audit unavailable')
            return reconcile(self.authority.project,details['owned_paths'],details['baseline']), []
        for row in rows:
            row = dict(row)
            process, receipt = self._record(row['op_id'])
            if row['phase'] != 'completed' or self.containment.populated(receipt) != 0:
                raise Blocked('host has unresolved task-tool effects')
            result = json.loads(row['result'])
            event = self.store.db.execute("SELECT payload FROM wf_events WHERE op_id=? AND kind='completed'",(row['op_id'],)).fetchone()
            if not event or event[0] != row['result'] or not result.get('replacement_allowed'):
                raise Blocked('task-tool completed receipt/event mismatch')
            intent = json.loads(row['intent'])
            original = self.store.db.execute("SELECT payload FROM wf_events WHERE op_id=? AND kind='intent'",(row['op_id'],)).fetchone()
            if not original or original[0] != row['intent']:
                raise Blocked('task-tool original intent/event mismatch')
            before, after = intent['baseline'], result['reconciliation']
            if any(before[k] != expected[k] for k in ('head','index','files')):
                raise Blocked('host task-tool audit chain gap')
            if after['head'] != before['head'] or after['index'] != before['index']:
                raise Blocked('host cannot reconcile runner Git changes yet')
            owned = intent['owned_paths']
            for name in set(before['files']) | set(after['files']):
                if name not in owned and before['files'].get(name) != after['files'].get(name):
                    raise Blocked('unrelated task-tool receipt drift')
            if result['empty_receipt']['containment'] != receipt or result['empty_receipt']['populated'] != 0:
                raise Blocked('task-tool empty receipt mismatch')
            if json.loads(process['reconciliation']) != after or json.loads(process['empty_receipt']) != result['empty_receipt']:
                raise Blocked('task-tool process/result mismatch')
            expected['files'] = after['files']
            chain.append(row['op_id'])
        now = snapshot(self.authority.project, details['owned_paths'])
        if any(now[k] != expected[k] for k in ('head','index','files')):
            raise Blocked('unexplained host lifetime file/Git drift')
        return now, chain

    def resolve(self, op, drain=True):
        """Empty AND actual partial-work/Git audit required. Does not grant task acceptance."""
        row, receipt = self._record(op)
        operation = self.store.operation(op)
        details = json.loads(operation['intent'])
        if operation['phase'] == 'completed':
            recorded = json.loads(operation['result'])
            if details['tool'] == 'runner-git-commit':
                from .git_effects import reconcile_commit_process
                current = reconcile_commit_process(self.authority, op)
            else:
                current = (snapshot(self.authority.project,details['owned_paths']) if row['scope_kind']=='host'
                           else reconcile(self.authority.project,details['owned_paths'],details['baseline']))
            if (self.containment.populated(receipt) != 0 or current != recorded['reconciliation']):
                raise Blocked('completed tool receipt no longer applicable')
            return recorded
        empty = self.containment.drain(receipt) if drain else {
            'containment': receipt, 'populated': self.containment.populated(receipt), 'observed_ns':time.time_ns()}
        if empty['populated'] != 0:
            raise Blocked('task tools not quiescent')
        if details['tool'] == 'runner-git-commit':
            from .git_effects import reconcile_commit_process
            observed, chain = reconcile_commit_process(self.authority, op), []
        elif row['scope_kind'] == 'host':
            observed, chain = self._host_reconciliation(operation, details)
        else:
            observed, chain = reconcile(self.authority.project, details['owned_paths'], details['baseline']), []
        result = {'logical_exit':row['exit_code'],'empty_receipt':empty,'reconciliation':observed,
                  'replacement_allowed':True, 'task_accepted':False}
        if row['scope_kind'] == 'host':
            result['task_tool_chain'] = chain
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
        results, errors = [], []
        rows = self.store.db.execute("""SELECT p.* FROM wf_processes p JOIN wf_operations o USING(op_id)
            WHERE o.phase!='completed' ORDER BY CASE p.scope_kind WHEN 'task_tools' THEN 0 ELSE 1 END,p.op_id""").fetchall()
        for row in rows:
            try:
                results.append(self.settle(row['op_id'], row['exit_code']))
            except Blocked as exc:
                errors.append(row['op_id'] + ': ' + str(exc))
        if errors:
            raise Blocked('worktree scope reconciliation blocked: ' + '; '.join(errors))
        return results
