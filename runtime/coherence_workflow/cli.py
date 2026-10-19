"""Opt-in standalone entry. Workflow edges, not this facade, schedule tasks."""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import sys
import time
import uuid

import yaml

from .authority import AuthorityAdmission
from .engine import Engine, load_workflow
from .git_effects import GitEffects
from .intake import Approvals, admit, content_hash, load_contract
from .pi_adapter import PiAdapter
from .registry import CHECKS, Handler, Registry, validate_schema
from .sessions import select_session
from .store import Authority, Blocked, canonical, digest, git, private_file, safe_path
from .tools import Gateway, ProcessTool, reconcile
from .verification import Verification, unittest_oracle

ROOT = Path(__file__).resolve().parents[2]


def file_bytes(project, args):
    path = safe_path(project, args['path'])
    observed = path.read_text() if path.is_file() else None
    return {'collected': 1, 'exit_code': 0 if observed == args['expected'] else 1,
            'output': canonical({'path': args['path'], 'expected_hash': digest(args['expected']),
                                 'observed_hash': digest(observed)})}


def registered_checks(project):
    result = {name: {**spec, 'execute': unittest_oracle} for name, spec in CHECKS.items()}
    result['workflow.FileBytes'] = {'version': '1', 'schema': {'type': 'object', 'additionalProperties': False,
        'properties': {'path': {'type': 'string', 'minLength': 1}, 'expected': {'type': 'string'}},
        'required': ['path', 'expected']}, 'execute': lambda args: file_bytes(project, args)}
    return result


class Coordinate:
    """Registered handlers compose one LangGraph task-progress cycle."""
    def __init__(self, authority, run, contract, catalog, config, containment, manifest, environment):
        self.authority, self.store, self.run = authority, authority.store, run
        self.contract, self.config, self.manifest = contract, config, manifest
        self.catalog, self.containment, self.environment = catalog, containment, environment
        self.gateway = Gateway(authority, run, containment, {})
        self.git = GitEffects(authority, run, self.gateway)
        self.verification = Verification(authority, run, registered_checks(authority.project))
        self.store.db.executescript('''
        CREATE TABLE IF NOT EXISTS wf_tasks(
          run_id TEXT NOT NULL REFERENCES wf_runs, task_id TEXT NOT NULL, approved_order INTEGER NOT NULL,
          contract TEXT NOT NULL, state TEXT NOT NULL, baseline TEXT, evidence TEXT, checkpoint TEXT,
          PRIMARY KEY(run_id,task_id), UNIQUE(run_id,approved_order));
        CREATE TABLE IF NOT EXISTS wf_run_inputs(
          run_id TEXT PRIMARY KEY REFERENCES wf_runs, identity TEXT NOT NULL, contract TEXT NOT NULL,
          owner_catalog_hash TEXT NOT NULL);
        ''')

    def current(self):
        rows = self.store.db.execute("SELECT * FROM wf_tasks WHERE run_id=? AND state NOT IN ('checkpointed','read_only_complete') ORDER BY approved_order", (self.run,)).fetchall()
        if not rows:
            return None
        return dict(rows[0])

    def intake(self, context):
        self.contract, receipt = admit(self.authority.project, self.contract,
            Approvals(self.authority.project, self.catalog), digest(self.config), legacy_settled=False)
        pin = digest({'contract': self.contract, 'config': self.config, 'manifest': self.manifest,
                      'environment': self.environment, 'host_hash': content_hash(ROOT / 'runtime/pi-host/host.mjs')})
        with self.store.transaction() as db:
            old = db.execute('SELECT * FROM wf_run_inputs WHERE run_id=?', (self.run,)).fetchone()
            if old:
                if old['identity'] != pin or old['owner_catalog_hash'] != digest(self.catalog):
                    raise Blocked('active input/approval/host/environment drift')
            else:
                db.execute('INSERT INTO wf_run_inputs VALUES(?,?,?,?)', (self.run, pin, canonical(self.contract), digest(self.catalog)))
                for task in self.contract['tasks']:
                    db.execute("INSERT INTO wf_tasks VALUES(?,?,?,?,'pending',NULL,NULL,NULL)",
                               (self.run, task['id'], task['order'], canonical(task)))
                self.store.event(db, self.run, None, 'intake_admitted', receipt)
        return {'outcome': 'ok'}

    def authority_check(self, context):
        envelope = self.contract['authorization_envelope']
        capabilities = ['read_file', 'write_file', *registered_checks(self.authority.project)]
        admission = AuthorityAdmission(envelope, self.config['profiles'], capabilities, self.config['permissions'],
                                       Approvals(self.authority.project, self.catalog).verify)
        gaps = admission.gaps()
        for node in self.config['nodes']:
            if node['type'] == 'agent':
                admission.model(self.config['profiles'][node['profile']])
        checks = registered_checks(self.authority.project)
        for task in self.contract['tasks']:
            for item in task['required']:
                check = item['check']; spec = checks.get(check['id'])
                if not spec or spec['version'] != check['version']:
                    gaps.append({'kind':'check','id':item['id'],'impact':'registered REQUIRED oracle unavailable','options':['provide registered check','stop']})
                else:
                    from jsonschema import Draft202012Validator
                    try:
                        Draft202012Validator(spec['schema']).validate(check['args'])
                    except Exception:
                        gaps.append({'kind':'check','id':item['id'],'impact':'REQUIRED check arguments invalid','options':['producing contract renewal','stop']})
            try:
                self.gates_satisfied(task)
            except Blocked as exc:
                gaps.append({'kind':'gate','id':task['id'],'impact':str(exc),'options':['provide current original authority','stop']})
        if gaps:
            raise Blocked('known admission gaps: ' + canonical(gaps))
        return {'outcome': 'ok'}

    def custody(self, context):
        self.store.assert_dispatchable(self.run)
        return {'outcome': 'ok'}

    def select(self, context):
        row = self.current()
        if row is None:
            return {'outcome': 'done'}
        task = json.loads(row['contract'])
        for dependency in task['depends']:
            producer = self.store.db.execute('SELECT state,checkpoint FROM wf_tasks WHERE run_id=? AND task_id=?', (self.run, dependency)).fetchone()
            if not producer or producer['state'] not in ('checkpointed', 'read_only_complete') or not producer['checkpoint']:
                raise Blocked('producer not verified/checkpointed: ' + dependency)
        if row['state'] != 'pending':
            raise Blocked('partial task requires explicit reconciliation; no redispatch')
        # All original gates must have genuine current scoped authority before mutation.
        approvals = Approvals(self.authority.project, self.catalog)
        for gate in task['gates']:
            refs = [ref for ref in self.contract['approval_refs'] if ref['record_ref'] == gate['approval_ref']]
            if len(refs) != 1:
                raise Blocked('unmet original gate: ' + gate['id'])
            approvals.verify(refs[0], digest({'gate': {**gate, 'approval_ref': None}, 'task_id': task['id'], 'config': digest(self.config)}))
        baseline = self.git.begin(task)
        with self.store.transaction() as db:
            db.execute("UPDATE wf_tasks SET state='active',baseline=? WHERE run_id=? AND task_id=?", (canonical(baseline), self.run, task['id']))
            self.store.event(db, self.run, None, 'task_selected', {'task_id': task['id'], 'baseline': baseline['head']})
        return {'outcome': 'work'}

    def gates_satisfied(self, task):
        admit(self.authority.project,self.contract,Approvals(self.authority.project,self.catalog),digest(self.config))
        approvals = Approvals(self.authority.project, self.catalog)
        for gate in task['gates']:
            refs = [ref for ref in self.contract['approval_refs'] if ref['record_ref'] == gate['approval_ref']]
            if len(refs) != 1:
                raise Blocked('unmet original gate: ' + gate['id'])
            approvals.verify(refs[0], digest({'gate': {**gate, 'approval_ref': None}, 'task_id': task['id'], 'config': digest(self.config)}))
        return True

    def _tools(self, task, *, review=False):
        project = self.authority.project
        readable = set(task['owned_paths']) | {s['path'] for s in self.contract['sources']}
        schema = lambda paths, write: {'type': 'object', 'additionalProperties': False,
            'properties': {'path': {'enum': sorted(paths)}, **({'text': {'type': 'string', 'maxLength': 32768}} if write else {})},
            'required': ['path', 'text'] if write else ['path']}
        def read_result(args, receipt):
            path = safe_path(project, args['path'])
            if not path.is_file() or path.stat().st_size > 32768:
                raise Blocked('authorized read unavailable/too large')
            return path.read_text()
        read = ProcessTool('read_file', '1', schema(readable, False),
            lambda args: [str(Path('/usr/bin/true').resolve())], (), self.environment, read_result)
        tools = {'read_file': read}
        if not review and task['owned_paths']:
            write = ProcessTool('write_file', '1', schema(task['owned_paths'], True),
                lambda args: [str(Path(sys.executable).resolve()), '-c',
                              'import sys; from coherence_workflow.store import safe_path; '
                              'p=safe_path(sys.argv[1],sys.argv[2]); p.parent.mkdir(parents=True,exist_ok=True); '
                              'p.write_text(sys.argv[3])', str(project), args['path'], args['text']],
                tuple(task['owned_paths']), self.environment)
            tools['write_file'] = write
        return tools

    def implement(self, context):
        row = self.current()
        if not row or row['state'] != 'active':
            raise Blocked('missing selected task')
        task = json.loads(row['contract'])
        node = context['node']
        self.gateway.tools = self._tools(task)
        self.gateway.bind_task_origin(task['id'] + ':0:', task['owned_paths'], json.loads(row['baseline']))
        manifest = copy.deepcopy(self.manifest)
        if (manifest['profile'] != self.config['profiles'][node['profile']] or
                len(manifest['skills']) != 1 or manifest['skills'][0]['sha256'] != self.config['skills'][node['skill']]['sha256']):
            raise Blocked('SDK manifest differs from approved graph profile/skill')
        manifest['tools'] = [dict(name=t.id, version=t.version, description='Bounded authorized ' + t.id,
                                 parameters=t.arguments, permission=t.id) for t in self.gateway.tools.values()]
        manifest['permissions'] = list(self.gateway.tools)
        manifest['resource_hash'] = digest({k: manifest[k] for k in ('skills', 'tools', 'permissions', 'trust', 'system_prompt')})
        # Every node uses the shared selector. Fresh-only avoids carrying a live host
        # across runner commits; saved reopen remains an independently verified seam.
        selection = select_session({'authorized': True, 'ready': True, 'reconciled': True,
            'role': 'implement', 'fresh_only': node['session_policy']['mode'] == 'fresh_only'}, [], now_ns=time.time_ns(), max_age_ns=2_000_000_000)
        adapter = PiAdapter(self.gateway, manifest, node='host:' + task['id'], environment=self.environment,
            session_context={'role': 'implement', 'affinity': task['context_group'], 'review_lineage': None})
        attempt = task['id'] + ':0'
        expected = {'schema_version': 1, 'task_id': task['id'], 'attempt_id': attempt,
            'contract_hash': digest(task), 'kind': 'implementation', 'outcome': 'produced',
            'changed_paths': task['owned_paths'], 'items': [], 'blocker': None}
        try:
            turn = adapter.prompt(node='implement:' + task['id'], task_id=task['id'], attempt_id=attempt,
                role='implement', text='Implement ONLY this approved task using the registered tools. Never commit or access other paths. '
                'You must read relevant existing files using read_file; its output is actual authorized bytes. '
                'Whole unchanged task contract follows:\n' + canonical(task) + '\nReturn ONLY JSON matching this result shape, with actual outcome/paths. '
                'Set items to [] exactly: runner checks supply evidence, not model-invented item objects. '
                'Do not add any fields. Exact result shape: ' + canonical(expected),
                skill=manifest['skills'][0]['name'], contract_hash=digest(task), selection=selection)
            result = json.loads(turn['output'])
            try:
                validate_schema('agent-result.schema.json', result)
            except Exception as exc:
                raise Blocked('schema-invalid implementation result; no check/commit or automatic retry') from exc
            if (any(result[k] != expected[k] for k in ('task_id', 'attempt_id', 'contract_hash', 'kind')) or
                    result['outcome'] not in ('produced', 'read_only') or not set(result['changed_paths']) <= set(task['owned_paths'])):
                raise Blocked('invalid/blocked implementation result')
        finally:
            adapter.close(force=adapter.lifecycle.poisoned)
        reconcile(self.authority.project, task['owned_paths'], json.loads(row['baseline']))
        with self.store.transaction() as db:
            db.execute("UPDATE wf_tasks SET state='verifying' WHERE run_id=? AND task_id=?", (self.run, task['id']))
            self.store.event(db, self.run, None, 'implementation_produced', {'task_id': task['id'], 'result': result})
        return {'outcome': 'ok'}

    def verify(self, context):
        row = self.current(); task = json.loads(row['contract'])
        evidence = self.verification.run_checks(task)
        dispositions = self.verification.audit(task, evidence)
        with self.store.transaction() as db:
            db.execute('UPDATE wf_tasks SET evidence=? WHERE run_id=? AND task_id=?', (canonical(evidence), self.run, task['id']))
        if any(d['status'] != 'satisfied' for d in dispositions):
            raise Blocked('REQUIRED checks block: ' + canonical(dispositions))
        return {'outcome': 'ok'}

    def checkpoint(self, context):
        row = self.current(); task = json.loads(row['contract'])
        dispositions = self.verification.audit(task, json.loads(row['evidence']))
        receipt = self.git.checkpoint(task, json.loads(row['baseline']), dispositions, gates_satisfied=self.gates_satisfied(task))
        with self.store.transaction() as db:
            db.execute('UPDATE wf_tasks SET state=?,checkpoint=? WHERE run_id=? AND task_id=?',
                ('read_only_complete' if receipt['read_only'] else 'checkpointed', canonical(receipt), self.run, task['id']))
            self.store.event(db, self.run, None, 'task_checkpointed', {'task_id': task['id'], **receipt})
        return {'outcome': 'ok'}

    def review_boundary(self, context):
        with self.store.transaction() as db:
            self.store.event(db, self.run, None, 'implementation_complete', {'acceptance': 'blocked', 'reason': 'independent full-range review required'})
        return {'outcome': 'ok'}

    def complete(self, context):
        if self.current() is not None:
            raise Blocked('incomplete task stream cannot report implementation complete')
        return {'outcome': 'implementation_complete'}

    def reconcile_effect(self, context, result):
        """Validate the committed prefix and any current owned residual, never replay it."""
        from .git_effects import entries
        expected = None
        for row in self.store.db.execute('SELECT * FROM wf_tasks WHERE run_id=? ORDER BY approved_order', (self.run,)):
            task = json.loads(row['contract'])
            if row['state'] == 'pending':
                continue
            baseline = json.loads(row['baseline'])
            if expected is not None and any(baseline[k] != expected[k] for k in ('head','index','files')):
                raise Blocked('task checkpoint/baseline chain gap')
            if row['state'] in ('checkpointed','read_only_complete'):
                receipt = json.loads(row['checkpoint'])
                if receipt['parent'] != baseline['head']:
                    raise Blocked('task checkpoint parent mismatch')
                if not receipt['read_only']:
                    op = self.store.operation(receipt['operation_id'])
                    details = json.loads(op['intent'])
                    event = self.store.db.execute("SELECT payload FROM wf_events WHERE op_id=? AND kind='completed'", (op['op_id'],)).fetchone()
                    if (op['phase'] != 'completed' or not event or event[0] != op['result'] or json.loads(op['result']) != receipt or
                            entries(self.authority.project,tree=receipt['sha']) != details['expected_entries']):
                        raise Blocked('checkpoint operation/tree proof mismatch')
                expected = receipt['reconciliation']
            else:
                expected = reconcile(self.authority.project,task['owned_paths'],baseline)
        if expected is not None:
            from .tools import snapshot
            now = snapshot(self.authority.project,[])
            if any(now[k] != expected[k] for k in ('head','index','files')):
                raise Blocked('current task/checkpoint residual mismatch')
        return True

    def registry(self):
        registry = Registry()
        registry.profiles, registry.skills = self.config['profiles'], self.config['skills']
        registry.permissions = set(self.config['permissions'])
        registry.tools = set(self.config['tool_capabilities'])
        registry.containments = {self.config['containment_capability']} if self.config['containment_capability'] else set()
        definitions = [('intake','code','intake',('ok',),self.intake),
            ('authority','gate','authority',('ok',),self.authority_check),
            ('custody','code','custody',('ok',),self.custody),
            ('select','code','task_select',('work','done'),self.select),
            ('implement','agent','work',('ok',),self.implement),
            ('verify','code','verification',('ok',),self.verify),
            ('checkpoint','code','checkpoint',('ok',),self.checkpoint),
            ('review','agent','review',('ok',),self.review_boundary),
            ('complete','terminal','completion',(),self.complete)]
        effects = {'intake':('read',),'authority':('read',),'custody':('read',),'select':('read',),
                   'implement':('files','process','conversation'),'verify':('read','process'),
                   'checkpoint':('git','process'),'review':('read',),'complete':('read',)}
        registry.handlers = {name: Handler(name,'1',kind,stage,outcomes,function,
                                          side_effects=effects[name],reconcile=self.reconcile_effect)
                             for name,kind,stage,outcomes,function in definitions}
        registry.success_terminals = set()
        return registry


def status(project, run):
    database = Path(project) / '.coherence/workflow/workflow.sqlite'
    private_file(database)
    db = sqlite3.connect(database.as_uri() + '?mode=ro', uri=True)
    db.row_factory = sqlite3.Row
    try:
        db.execute('BEGIN')
        row = db.execute('SELECT * FROM wf_runs WHERE run_id=?', (run,)).fetchone()
        if not row:
            raise Blocked('unknown run')
        return {'run': dict(row), 'operations': [dict(r) for r in db.execute('SELECT op_id,node_id,kind,phase FROM wf_operations WHERE run_id=?', (run,))],
                'alarms': [dict(r) for r in db.execute('SELECT * FROM wf_alarms')], 'accepted': False}
    finally:
        db.close()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest='command', required=True)
    for name in ('start','resume'):
        p = subs.add_parser(name)
        for flag in ('project','workflow','tasks','owner-catalog','manifest','containment'):
            p.add_argument('--' + flag, required=True)
        p.add_argument('--run', required=True)
    p = subs.add_parser('intake')
    for flag in ('project','tasks','owner-catalog','config-hash'):
        p.add_argument('--' + flag, required=True)
    p = subs.add_parser('status'); p.add_argument('--project', required=True); p.add_argument('--run', required=True)
    for name in ('pending','answer','control'):
        p = subs.add_parser(name); p.add_argument('--project', required=True); p.add_argument('--run', required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == 'status':
            print(canonical(status(args.project, args.run))); return 0
        if args.command in ('pending','answer','control'):
            raise Blocked('interaction capability unavailable until shipped interaction adapter')
        owner_path = Path(args.owner_catalog).resolve(strict=True)
        if owner_path.is_relative_to(Path(args.project).resolve()):
            raise Blocked('owner catalog must be outside agent worktree')
        private_file(owner_path)
        catalog = json.loads(owner_path.read_text())
        contract = load_contract(args.tasks)
        if args.command == 'intake':
            _, receipt = admit(args.project,contract,Approvals(Path(args.project),catalog),args.config_hash)
            print(canonical(receipt)); return 0
        config = yaml.safe_load(Path(args.workflow).read_text())
        manifest = json.loads(Path(args.manifest).read_text())
        environment = {k:v for k,v in os.environ.items() if k in ('PATH','HOME','PYTHONPATH','PYTHONDONTWRITEBYTECODE','TMPDIR','PI_OFFLINE')}
        with Authority(args.project) as authority:
            # Engine reserves the run before handler operations can be persisted.
            coordinate = Coordinate(authority,args.run,contract,catalog,config,args.containment,manifest,environment)
            registry = coordinate.registry()
            load_workflow(registry, Path(args.workflow).read_bytes(), ROOT)
            engine = Engine(authority,args.run,config,registry,ROOT,max_task_visits=len(contract['tasks']),
                            input_identity={'contract':contract,'catalog_hash':digest(catalog),'manifest':manifest,'environment':environment})
            try:
                engine.invoke()
            finally:
                engine.close()
            print(canonical(status(args.project,args.run)))
        return 0
    except (Blocked, ValueError) as exc:
        print(canonical({'status':'blocked','reason':str(exc)})); return 2


if __name__ == '__main__':
    sys.exit(main())
