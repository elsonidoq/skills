"""Focused runner checkpoints with durable intent and exact Git/file reconciliation."""
import copy
import json
import os
from pathlib import Path
import shutil

from .store import Blocked, canonical, digest, git, safe_path
from .tools import ProcessTool, clean_owned, reconcile, snapshot, owned_file


def assert_safe_git_inputs(project, owned):
    """Builtin inspection only; never probe an external filter or index hook."""
    for name in owned:
        owned_file(project, name)
    try:
        raw=git(project,'config','--null','--list')
    except (Blocked,OSError):raise Blocked('Git config capability inspection unavailable') from None
    config={}
    for entry in raw.split(b'\0'):
        if entry:
            key,separator,value=entry.partition(b'\n');config[key]=value if separator else b''
    fsmonitor=config.get(b'core.fsmonitor')
    if fsmonitor is not None and fsmonitor.lower() not in (b'false',b'0',b'off'):
        raise Blocked('fsmonitor process capability unavailable for uncontained inventory')
    if not owned:return
    try:
        hook_text=git(project,'rev-parse','--path-format=absolute','--git-path','hooks').decode().removesuffix('\n')
        if not Path(hook_text).is_absolute() or '\n' in hook_text or '\r' in hook_text:
            raise Blocked('ambiguous hook path')
        hook=Path(hook_text)/'post-index-change'
        try:hook.lstat()
        except FileNotFoundError:hook=None
        if hook is not None and (hook.is_symlink() or os.access(hook,os.X_OK)):
            raise Blocked('Git post-index-change hook requires a contained staging capability')
    except (OSError,UnicodeError):raise Blocked('Git index hook applicability cannot be established safely') from None
    drivers=set()
    for key in config:
        if key[:7].lower()==b'filter.' and key.rsplit(b'.',1)[-1].lower() in (b'clean',b'process'):
            drivers.add(key[7:].rsplit(b'.',1)[0])
    if drivers:
        for options in ([],['--cached']):
            try:attributes=git(project,'check-attr','-z',*options,'filter','--',*owned).split(b'\0')
            except (Blocked,OSError):raise Blocked('Git filter applicability cannot be established safely') from None
            if attributes[-1:]!=[b''] or (len(attributes)-1)%3:
                raise Blocked('Git filter applicability record is ambiguous')
            for index in range(0,len(attributes)-1,3):
                if attributes[index+1]!=b'filter':raise Blocked('unexpected Git attribute inspection')
                if attributes[index+2] in drivers:
                    raise Blocked('Git external clean/process filter requires a contained adapter')


def inventory_inputs(project, tasks):
    """Shared safe Git/path prerequisites, without adopting any existing bytes."""
    owned = set()
    for task in tasks:
        paths = task.get('owned_paths', [])
        if len(paths) != len(set(paths)) or any(a != b and b.startswith(a + '/') for a in paths for b in paths):
            raise Blocked('overlapping owned inventory paths')
        assert_safe_git_inputs(project, paths)
        owned.update(paths)
    # Even a read-only task needs safe Git inventory (not a configured fsmonitor).
    assert_safe_git_inputs(project, [])
    git(project, 'var', 'GIT_AUTHOR_IDENT')
    git(project, 'var', 'GIT_COMMITTER_IDENT')
    return sorted(owned)


def inventory_preflight(project, tasks):
    """Fresh baseline admission; pending task selection still requires clean ownership."""
    owned = inventory_inputs(project, tasks)
    for task in tasks:
        clean_owned(project, task.get('owned_paths', []))
    return snapshot(project, owned)


def recovery_inventory_preflight(project, tasks):
    """Observe partial bytes, not approve them; original recovery must reconcile them.

    Only the resume facade uses this structural inventory before opening Authority.
    It cannot certify dirty work against the original ledger baseline or authorize
    continuation. No worker-facing bypass of fresh selection/cleanliness exists.
    """
    return snapshot(project, inventory_inputs(project, tasks))


def entries(project, *, tree=None):
    raw = git(project, 'ls-tree', '-r', '-z', tree) if tree else git(project, 'ls-files', '--stage', '-z')
    result = {}
    for record in raw.split(b'\0'):
        if not record:
            continue
        fields, path = record.split(b'\t', 1)
        mode, middle, last = fields.decode().split()
        if not tree and last != '0':
            raise Blocked('unmerged index')
        result[path.decode()] = [mode, last if tree else middle]
    return result


def expected_entries(project, baseline, owned):
    assert_safe_git_inputs(project,owned)
    result = entries(project, tree=baseline['head'])
    for name in owned:
        path = project / name
        if not path.exists():
            result.pop(name, None)
        else:
            result[name] = ['100755' if path.stat().st_mode & 0o111 else '100644',
                            git(project, 'hash-object', '--', name).decode().strip()]
    return result


class GitEffects:
    def __init__(self, authority, run, gateway, *, authorize=None, require_authorization=False):
        self.authority, self.store, self.run, self.gateway = authority, authority.store, run, gateway
        self.project = authority.project
        self.authorize = authorize
        self.require_authorization = require_authorization

    def begin(self, task):
        self.store.assert_dispatchable(self.run)
        return inventory_preflight(self.project, [task])

    def checkpoint(self, task, baseline, dispositions, *, phase_hook=None):
        assert_safe_git_inputs(self.project,task['owned_paths'])
        self.store.assert_dispatchable(self.run)
        if ({d['item_id'] for d in dispositions} != {i['id'] for i in task['required']} or
                any(d['status'] != 'satisfied' for d in dispositions)):
            raise Blocked('task checks block checkpoint')
        owned = task['owned_paths']
        now = reconcile(self.project, owned, baseline)
        if now!=baseline:
            if self.require_authorization and self.authorize is None:raise Blocked('Git action authority unavailable')
            if self.authorize is not None:self.authorize('runner-git-commit')
        before_index = entries(self.project)
        expected = expected_entries(self.project, baseline, owned)
        details = {'task_id': task['id'], 'baseline': baseline, 'owned_paths': owned,
                   'before': now, 'expected_entries': expected, 'index_entries': before_index,
                   'dispositions': dispositions}
        old = self.store.db.execute("SELECT * FROM wf_operations WHERE run_id=? AND node_id=? AND kind='git-checkpoint'",
                                    (self.run, task['id'])).fetchone()
        if old:
            raise Blocked('checkpoint already attempted; reconcile, never replay Git')
        operation = self.store.intent(self.run, task['id'], 'git-checkpoint', details, details)
        if now == baseline:
            result = {'sha': baseline['head'], 'read_only': True, 'reconciliation': now, 'parent': baseline['head']}
            self.store.transition(operation['op_id'], 'intent', 'completed', result)
            return result
        executable = str(Path(shutil.which('git')).resolve(strict=True))
        message = 'workflow: ' + task['id'] + '\n\nCoherence-Operation: ' + operation['op_id']
        # add is explicit and owned-only; commit --only preserves unrelated staging.
        assert_safe_git_inputs(self.project,owned)
        git(self.project, 'add', '-A', '--', *owned)
        tool = ProcessTool('runner-git-commit', '1', {'type': 'object', 'additionalProperties': False},
                           lambda args: [executable, '-C', str(self.project), 'commit', '--only', '-m', message, '--', *owned],
                           (), {k: v for k, v in os.environ.items() if k in ('PATH', 'HOME', 'GNUPGHOME', 'GPG_TTY', 'SSH_AUTH_SOCK')})
        self.gateway.tools[tool.id] = tool
        assert_safe_git_inputs(self.project,owned)
        op, proc = self.gateway.launch('commit:' + operation['op_id'], tool.id, '1', {})
        if phase_hook:
            phase_hook('commit_released', operation['op_id'])
        code = proc.wait(timeout=120)
        if phase_hook:
            phase_hook('commit_exit', operation['op_id'])
        if code:
            # Keep failed process and partial index intact for explicit diagnosis.
            raise Blocked('Git commit/hooks/signing failed; no configure-around or replay')
        receipt = self.gateway.settle(op, code)
        if not receipt.get('replacement_allowed'):
            raise Blocked('Git hook descendants unresolved')
        result = reconcile_checkpoint(self.authority, operation['op_id'])
        if phase_hook:
            phase_hook('commit_before_receipt', operation['op_id'])
        self.store.transition(operation['op_id'], 'intent', 'completed', result)
        return result


def reconcile_checkpoint(authority, op_id):
    operation = authority.store.operation(op_id)
    if operation['kind'] != 'git-checkpoint':
        raise Blocked('not a runner checkpoint intent')
    proof = authority.store.db.execute("SELECT payload FROM wf_events WHERE op_id=? AND kind='intent'", (op_id,)).fetchone()
    if not proof or proof[0] != operation['intent']:
        raise Blocked('checkpoint intent/event mismatch')
    details = json.loads(operation['intent'])
    project, owned = authority.project, details['owned_paths']
    assert_safe_git_inputs(project,owned)
    now = snapshot(project, owned)
    sha = now['head']
    if git(project, 'rev-list', '--parents', '-n', '1', sha).decode().strip().split() != [sha, details['baseline']['head']]:
        raise Blocked('checkpoint parent/current HEAD mismatch')
    message = git(project, 'log', '-1', '--format=%B', sha).decode()
    if message.splitlines().count('Coherence-Operation: ' + op_id) != 1:
        raise Blocked('checkpoint operation trailer mismatch')
    if entries(project, tree=sha) != details['expected_entries']:
        raise Blocked('checkpoint actual tree differs from intent')
    changed = set(git(project, 'diff-tree', '--no-commit-id', '--name-only', '-r', '-z', sha).decode().split('\0')) - {''}
    if not changed or not changed <= set(owned):
        raise Blocked('checkpoint changed paths outside ownership or empty')
    expected_index = copy.deepcopy(details['index_entries'])
    for name in owned:
        if name in details['expected_entries']:
            expected_index[name] = details['expected_entries'][name]
        else:
            expected_index.pop(name, None)
    if entries(project) != expected_index:
        raise Blocked('checkpoint residual/index drift')
    # Full file identities include unrelated staged, unstaged, ignored and custom data.
    if now['files'] != details['before']['files']:
        raise Blocked('checkpoint hook/residual file mutation')
    return {'sha': sha, 'parent': details['baseline']['head'], 'read_only': False,
            'tree': git(project, 'rev-parse', sha + '^{tree}').decode().strip(),
            'owned_paths': owned, 'reconciliation': now, 'operation_id': op_id}


def reconcile_commit_process(authority, process_op):
    operation = authority.store.operation(process_op)
    node = operation['node_id']
    if not node.startswith('commit:'):
        raise Blocked('runner commit process lacks checkpoint operation binding')
    checkpoint = authority.store.operation(node.removeprefix('commit:'))
    details = json.loads(operation['intent'])
    planned = json.loads(checkpoint['intent'])
    expected_suffix = ['commit', '--only', '-m', 'workflow: ' + planned['task_id'] +
                       '\n\nCoherence-Operation: ' + checkpoint['op_id'], '--', *planned['owned_paths']]
    if (checkpoint['run_id'] != operation['run_id'] or details['tool'] != 'runner-git-commit' or
            details['argv'][3:] != expected_suffix):
        raise Blocked('runner commit argv/custody binding mismatch')
    return reconcile_checkpoint(authority, checkpoint['op_id'])['reconciliation']
