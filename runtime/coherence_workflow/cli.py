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
from jsonschema.exceptions import ValidationError

from .authority import AuthorityAdmission
from .engine import Engine, StrictLoader, load_workflow
from .git_effects import GitEffects, assert_safe_git_inputs
from .intake import Approvals, admit, content_hash, load_contract
from .pi_adapter import PiAdapter
from .registry import CHECKS, Handler, Registry, validate_schema
from .sessions import select_session
from .store import Authority, Blocked, canonical, digest, git, private_file, safe_path
from .tools import Gateway, ProcessTool, reconcile, snapshot
from .verification import ReviewRepair, Verification, unittest_oracle

ROOT = Path(__file__).resolve().parents[2]


def file_bytes(project, args):
    path = safe_path(project, args['path'])
    observed = path.read_text() if path.is_file() else None
    return {'collected': 1, 'exit_code': 0 if observed == args['expected'] else 1,
            'diagnosis':None if observed == args['expected'] else 'implementation',
            'output': canonical({'path': args['path'], 'expected_hash': digest(args['expected']),
                                 'observed_hash': digest(observed)})}


def registered_checks(project, gateway=None):
    result = {name: {**spec, 'execute': unittest_oracle} for name, spec in CHECKS.items()}
    for file, selector in [('test_recovery.py','EffectRecoveryTests'),('test_recovery.py','PressureRecoveryTests'),
                           ('test_projections.py','ProjectionRecoveryTests'),('test_recovery.py','VersionRecoveryTests')]:
        result['workflow.'+selector]={'version':'1','schema':{'type':'object','additionalProperties':False,
            'properties':{'test_file':{'const':'runtime/tests/'+file},'selector':{'const':selector}},
            'required':['test_file','selector']},'execute':unittest_oracle}
    def python_answer(args):
        if gateway is None:raise Blocked('contained Python oracle gateway unavailable')
        safe_path(project,args['path'])
        tool=ProcessTool('check-python-answer','1',{'type':'object','additionalProperties':False},
            lambda unused:[str(Path(sys.executable).resolve()),'-c',
                'import runpy,sys; value=runpy.run_path(sys.argv[1])["answer"](); '
                'raise SystemExit(0 if type(value) is int and value==int(sys.argv[2]) else 20)',
                str(safe_path(project,args['path'])),str(args['expected'])],(),
            {k:v for k,v in os.environ.items() if k in ('PATH','HOME','PYTHONPATH','PYTHONDONTWRITEBYTECODE','TMPDIR')})
        gateway.tools[tool.id]=tool
        op,process=gateway.launch('oracle:'+uuid.uuid4().hex,tool.id,'1',{})
        code=process.wait(timeout=15);receipt=gateway.settle(op,code)
        if not receipt.get('replacement_allowed'):raise Blocked('oracle descendants unsettled')
        valid=code in (0,20)
        return {'collected':1 if valid else 0,'exit_code':0 if code==0 else 1 if code==20 else None,
                'diagnosis':'implementation' if code==20 else None,
                'output':canonical({'operation_id':op,'raw_exit':code,'criterion':'answer() exact integer result'})}
    result['workflow.PythonAnswer']={'version':'1','schema':{'type':'object','additionalProperties':False,
        'properties':{'path':{'type':'string','minLength':1},'expected':{'type':'integer'}},'required':['path','expected']},'execute':python_answer}
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
        self.host_hash = content_hash(ROOT / 'runtime/pi-host/host.mjs')
        self.gateway = Gateway(authority, run, containment, {})
        self.git = GitEffects(authority, run, self.gateway)
        self.verification = Verification(authority, run, registered_checks(authority.project,self.gateway))
        self.store.db.executescript('''
        CREATE TABLE IF NOT EXISTS wf_tasks(
          run_id TEXT NOT NULL REFERENCES wf_runs, task_id TEXT NOT NULL, approved_order INTEGER NOT NULL,
          contract TEXT NOT NULL, state TEXT NOT NULL, baseline TEXT, evidence TEXT, checkpoint TEXT,
          PRIMARY KEY(run_id,task_id), UNIQUE(run_id,approved_order));
        CREATE TABLE IF NOT EXISTS wf_run_inputs(
          run_id TEXT PRIMARY KEY REFERENCES wf_runs, identity TEXT NOT NULL, contract TEXT NOT NULL,
          owner_catalog_hash TEXT NOT NULL);
        ''')
        self.review_repair=ReviewRepair(self)

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
                try:
                    profile=self.config['profiles'][node['profile']]
                    admission.model(profile)
                    if self.manifest['profile']!=profile:raise Blocked('exact node profile unavailable in supplied SDK manifest')
                except Blocked as exc:
                    gaps.append({'kind':'profile','id':node['id'],'impact':str(exc),'options':['provide approved exact manifest','stop']})
        checks = registered_checks(self.authority.project)
        for task in self.contract['tasks']:
            try:assert_safe_git_inputs(self.authority.project,task['owned_paths'])
            except Blocked as exc:
                gaps.append({'kind':'git_capability','id':task['id'],'impact':str(exc),'options':['provide registered contained capability','stop']})
            for item in task['required']:
                check = item['check']; spec = checks.get(check['id'])
                if not spec or spec['version'] != check['version']:
                    gaps.append({'kind':'check','id':item['id'],'impact':'registered REQUIRED oracle unavailable','options':['provide registered check','stop']})
                else:
                    from jsonschema import Draft202012Validator
                    try:
                        Draft202012Validator(spec['schema']).validate(check['args'])
                        if check['id'] in ('workflow.FileBytes','workflow.PythonAnswer'):
                            safe_path(self.authority.project,check['args']['path'])
                    except Exception:
                        gaps.append({'kind':'check','id':item['id'],'impact':'REQUIRED check arguments invalid','options':['producing contract renewal','stop']})
            try:
                self.gates_satisfied(task)
            except Blocked as exc:
                gaps.append({'kind':'gate','id':task['id'],'impact':str(exc),'options':['provide current original authority','stop']})
        rules=self.catalog.get('workflow_correction_rules',[])
        if not isinstance(rules,list):
            gaps.append({'kind':'correction_contract','id':'rules','impact':'correction authority must be a structured list','options':['producing renewal','stop']})
        else:
            for index,rule in enumerate(rules):
                try:
                    validate_schema('task.schema.json',{**self.contract,'tasks':[rule['task']]})
                except (KeyError,TypeError,ValidationError):
                    gaps.append({'kind':'correction_contract','id':str(index),'impact':'invalid correction task schema','options':['producing renewal','stop']})
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

    @staticmethod
    def admit_node_tools(node, tools):
        """Registered tool permission IDs are fixed; configuration cannot widen them."""
        expected=set(tools)
        if (set(node['tools'])!=expected or len(node['tools'])!=len(expected) or
                not expected <= set(node['permissions'])):
            raise Blocked('configured node tool/permission restrictions do not admit registered tool manifest')

    def _tools(self, task, *, review=False):
        project = self.authority.project
        readable = set(task['owned_paths']) | {s['path'] for s in self.contract['sources']} | {r['record_ref'] for r in self.contract['approval_refs']}
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

    def dispatch(self, context):
        row=self.current()
        correction=self.store.db.execute('SELECT 1 FROM wf_corrections WHERE run_id=? AND task_id=?',(self.run,row['task_id'])).fetchone()
        return {'outcome':'repair' if correction else 'implement'}

    def repair(self, context):
        row=self.current();task=json.loads(row['contract'])
        try:
            key=self.review_repair.failure_key(task)
            maximum=self.review_repair.maximum(key)
            count=self.review_repair.budget(key,maximum)
            self.gates_satisfied(task)
            if row['state']=='verifying':self.review_repair.diagnose(task,json.loads(row['evidence']))
            elif row['state']!='active':raise Blocked('repair has no inspected active task')
            with self.store.transaction() as db:db.execute("UPDATE wf_tasks SET state='active' WHERE run_id=? AND task_id=?",(self.run,task['id']))
            return self.implement(context,role='repair',attempt=count,
                                  before_prompt=lambda:self.review_repair.budget(key,maximum,consume=True))
        except Blocked as exc:
            self.record_block(str(exc),'repair budget exhausted' in str(exc))
            return {'outcome':'blocked'}

    def record_block(self, reason, exhausted=False):
        with self.store.transaction() as db:self.store.event(db,self.run,None,'workflow_blocked',{'reason':reason,'final_failure':exhausted})

    def implement(self, context, *, role='implement', attempt=0, before_prompt=None):
        if content_hash(ROOT / 'runtime/pi-host/host.mjs') != self.host_hash:
            raise Blocked('active SDK host content drift')
        row = self.current()
        if not row or row['state'] != 'active':
            raise Blocked('missing selected task')
        task = json.loads(row['contract'])
        node = context['node']
        self.gateway.tools = self._tools(task)
        self.admit_node_tools(node,self.gateway.tools)
        origin = json.loads(row['baseline']) if role=='implement' else snapshot(self.authority.project,task['owned_paths'])
        self.gateway.bind_task_origin(task['id'] + ':' + str(attempt) + ':', task['owned_paths'], origin)
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
            'role': role, 'fresh_only': node['session_policy']['mode'] == 'fresh_only'}, [], now_ns=time.time_ns(), max_age_ns=2_000_000_000)
        selection['repair_count']=attempt if role=='repair' else 0
        adapter = PiAdapter(self.gateway, manifest, node='host:' + task['id'] + ':' + str(attempt), environment=self.environment,
            session_context={'role': role, 'affinity': task['context_group'], 'review_lineage': None})
        attempt_id = task['id'] + ':' + str(attempt)
        expected = {'schema_version': 1, 'task_id': task['id'], 'attempt_id': attempt_id,
            'contract_hash': digest(task), 'kind': 'repair' if role=='repair' else 'implementation', 'outcome': 'produced',
            'changed_paths': task['owned_paths'], 'items': [], 'blocker': None}
        try:
            if before_prompt:before_prompt()
            turn = adapter.prompt(node=role+':' + task['id']+':'+str(attempt), task_id=task['id'], attempt_id=attempt_id,
                role=role, text=('Repair ONLY the diagnosed original failure; inspect current partial files and preserve the entire original contract. ' if role=='repair' else '')+'Implement ONLY this approved task using the registered tools. Never commit or access other paths. '
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
        previous=json.loads(row['evidence']) if row['evidence'] else []
        audited=self.verification.audit(task,previous)
        reusable={d['item_id'] for d in audited if d['status']!='insufficient-evidence'}
        evidence=[e for e in previous if e['item_id'] in reusable]
        affected={**task,'required':[i for i in task['required'] if i['id'] not in reusable]}
        if affected['required']:evidence += self.verification.run_checks(affected)
        dispositions = self.verification.audit(task, evidence)
        with self.store.transaction() as db:
            db.execute('UPDATE wf_tasks SET evidence=? WHERE run_id=? AND task_id=?', (canonical(evidence), self.run, task['id']))
        if any(d['status'] != 'satisfied' for d in dispositions):
            try:
                self.review_repair.diagnose(task,evidence)
                return {'outcome':'repair'}
            except Blocked as exc:
                self.record_block(str(exc));return {'outcome':'blocked'}
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
        if self.current() is not None:raise Blocked('review cannot precede checkpoints')
        with self.store.transaction() as db:
            self.store.event(db,self.run,None,'implementation_complete',{'acceptance':'blocked','reason':'independent review pending'})
        self.reconcile_effect({}, {})
        try:self.review_repair.refresh_evidence()
        except Blocked as exc:self.record_block(str(exc));return {'outcome':'blocked'}
        bundle=self.review_repair.bundle();node=context['node']
        task={'id':'final-review','owned_paths':sorted({path for t in self.contract['tasks'] for path in t['owned_paths']})}
        self.gateway.tools=self._tools(task,review=True)
        self.admit_node_tools(node,self.gateway.tools)
        manifest=copy.deepcopy(self.manifest)
        if (manifest['profile']!=self.config['profiles'][node['profile']] or len(manifest['skills'])!=1 or
                manifest['skills'][0]['sha256']!=self.config['skills'][node['skill']]['sha256'] or
                content_hash(ROOT/'runtime/pi-host/host.mjs')!=self.host_hash):
            raise Blocked('review exact profile/resource/host mismatch')
        manifest['tools']=[dict(name=t.id,version=t.version,description='Read bounded authorized current source bytes.',parameters=t.arguments,permission=t.id) for t in self.gateway.tools.values()]
        manifest['permissions']=['read_file']
        manifest['system_prompt']='You are a fresh independent read-only code reviewer. Never implement or repair. Judge the full committed range against supplied approved source/tasks/check evidence.'
        manifest['resource_hash']=digest({k:manifest[k] for k in ('skills','tools','permissions','trust','system_prompt')})
        round=self.store.db.execute('SELECT COUNT(*) FROM wf_reviews WHERE run_id=?',(self.run,)).fetchone()[0]
        selection=select_session({'authorized':True,'ready':True,'reconciled':True,'role':'review',
            'review_lineage':bundle['range_base'] if round else None,
            'fresh_only':node['session_policy']['mode']=='fresh_only'},[],now_ns=time.time_ns(),max_age_ns=2_000_000_000)
        adapter=PiAdapter(self.gateway,manifest,node='review-host:'+str(round),environment=self.environment,
            session_context={'role':'review','affinity':'final-review','review_lineage':bundle['range_base']})
        expected={'schema_version':1,'task_id':'final-review','attempt_id':'review:'+str(round),'contract_hash':digest(bundle),
            'kind':'review','outcome':'pass','range_base':bundle['range_base'],'range_head':bundle['range_head'],'findings':[],'blocker':None}
        finding={'id':'finding-1','severity':'important','criterion_ref':'ORIGINAL_ITEM_ID','location':'owned/path.py:LINE',
                 'observation':'specific observed source violation','evidence_ref':'owned/path.py','action':'bounded proposed correction','scope':'in_scope'}
        try:
            turn=adapter.prompt(node='review:'+str(round),task_id='final-review',attempt_id=expected['attempt_id'],role='review',
                text='Review independently, do not fix. Receive complete original base-to-current-head bundle below; read actual authorized files as needed. '
                'Check source requirements beyond mechanical green (including extraneous/dead code). Return ONLY JSON in the exact shape '+canonical(expected)+
                '. If actual findings exist set outcome correction and findings to objects in this exact shape '+canonical(finding)+
                '. Scope-changing findings must use scope owner_decision, not in_scope. Never invent an issue. Full bundle: '+canonical(bundle),
                skill=manifest['skills'][0]['name'],contract_hash=digest(bundle),selection=selection)
            result=json.loads(turn['output']);validate_schema('agent-result.schema.json',result)
            if any(result[k]!=expected[k] for k in ('task_id','attempt_id','contract_hash','kind')):raise Blocked('review identity mismatch')
        finally:adapter.close(force=adapter.lifecycle.poisoned)
        self.review_repair.record_review(result,adapter.host_op)
        if result['outcome']=='pass':return {'outcome':'ok'}
        if result['outcome']=='correction':return {'outcome':'correction'}
        self.record_block('review blocked or owner input unavailable');return {'outcome':'blocked'}

    def authorize_correction(self, context):
        try:self.review_repair.authorize_corrections();return {'outcome':'ok'}
        except Blocked as exc:self.record_block(str(exc),'budget exhausted' in str(exc));return {'outcome':'blocked'}

    def failure(self, context):
        raise Blocked('workflow blocked/final_failure; inspect persisted reason and original failure budget')

    def complete(self, context):
        if self.current() is not None:raise Blocked('incomplete task stream cannot accept')
        try:return self.review_repair.acceptance()
        except Blocked as exc:self.record_block(str(exc));raise

    def recover(self, authorization):
        """Explicitly reconcile known receipts; unknown/partial SDK turns never replay."""
        run=self.store.db.execute('SELECT * FROM wf_runs WHERE run_id=?',(self.run,)).fetchone()
        pending=[dict(r) for r in self.store.db.execute("SELECT * FROM wf_operations WHERE run_id=? AND phase!='completed' ORDER BY op_id",(self.run,))]
        if (authorization.get('action')!='reconcile' or authorization.get('run_id')!=self.run or
                authorization.get('config_hash')!=run['config_hash'] or
                authorization.get('operations')!=[r['op_id'] for r in pending] or
                not authorization.get('actor') or not authorization.get('provenance')):
            raise Blocked('current scoped external recovery authority required')
        with self.store.transaction() as db:
            self.store.event(db,self.run,None,'recovery_authorized',{'authority_hash':digest(authorization)})
        # Scan ALL durable worktree scopes. A live task group durably alarms; a live
        # idle host remains distinct but still prevents unapproved replacement.
        self.gateway.recover()
        self.store.assert_dispatchable(self.run)
        uncertain=[r for r in pending if r['kind']=='sdk-turn']
        if uncertain:
            raise Blocked('partial SDK invocation requires diagnosed original-session recovery; no replacement')
        checkpoints=[r for r in pending if r['kind']=='git-checkpoint']
        for op in checkpoints:
            from .git_effects import reconcile_checkpoint
            receipt=reconcile_checkpoint(self.authority,op['op_id'])
            self.store.transition(op['op_id'],'intent','completed',receipt)
            task_id=json.loads(op['intent'])['task_id']
            row=self.store.db.execute('SELECT * FROM wf_tasks WHERE run_id=? AND task_id=?',(self.run,task_id)).fetchone()
            task=json.loads(row['contract'])
            if not self.gates_satisfied(task) or any(d['status']!='satisfied' for d in self.verification.audit(task,json.loads(row['evidence']))):
                raise Blocked('recovered commit still lacks current original evidence/gates')
            with self.store.transaction() as db:
                db.execute("UPDATE wf_tasks SET state='checkpointed',checkpoint=? WHERE run_id=? AND task_id=?",(canonical(receipt),self.run,task_id))
                self.store.event(db,self.run,None,'task_checkpointed',{'task_id':task_id,**receipt})
            graph=[r for r in pending if r['kind']=='graph' and r['node_id'].split(':')[0]=='checkpoint']
            if len(graph)!=1:raise Blocked('ambiguous checkpoint graph recovery')
            self.store.transition(graph[0]['op_id'],'intent','completed',{'outcome':'ok'})
        remaining=self.store.db.execute("SELECT node_id,kind FROM wf_operations WHERE run_id=? AND phase!='completed'",(self.run,)).fetchall()
        if remaining:raise Blocked('unknown partial effects; explicit diagnosis required')
        self.reconcile_effect({}, {})

    def reconcile_effect(self, context, result):
        """Validate the committed prefix and any current owned residual, never replay it."""
        from .git_effects import entries
        expected = None
        for row in self.store.db.execute('SELECT * FROM wf_tasks WHERE run_id=? ORDER BY approved_order', (self.run,)):
            task = json.loads(row['contract'])
            assert_safe_git_inputs(self.authority.project,task['owned_paths'])
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
            ('dispatch','code','work',('implement','repair'),self.dispatch),
            ('implement','agent','work',('ok',),self.implement),
            ('repair','agent','repair',('ok','blocked'),self.repair),
            ('verify','code','verification',('ok','repair','blocked'),self.verify),
            ('checkpoint','code','checkpoint',('ok',),self.checkpoint),
            ('review','agent','review',('ok','correction','blocked'),self.review_boundary),
            ('authorize-correction','code','correction_authority',('ok','blocked'),self.authorize_correction),
            ('failure','terminal','failure',(),self.failure),
            ('complete','terminal','success',(),self.complete)]
        effects = {'intake':('read',),'authority':('read',),'custody':('read',),'select':('read',),
                   'implement':('files','process','conversation'),'verify':('read','process'),
                   'checkpoint':('git','process'),'review':('read',),'complete':('read',),
                   'dispatch':('read',),'repair':('files','process','conversation'),
                   'authorize-correction':('read',),'failure':('read',)}
        registry.handlers = {name: Handler(name,'1',kind,stage,outcomes,function,
                                          side_effects=effects[name],reconcile=self.reconcile_effect)
                             for name,kind,stage,outcomes,function in definitions}
        registry.success_terminals = {'complete'}
        return registry


def status(project, run):
    database = Path(project) / '.coherence/workflow/workflow.sqlite'
    private_file(database)
    db = sqlite3.connect(database.as_uri() + '?mode=ro', uri=True)
    db.row_factory = sqlite3.Row
    try:
        db.execute('BEGIN')
        if [r[0] for r in db.execute('SELECT version FROM wf_meta')] != [1]:
            raise Blocked('unsupported application schema; read-only status cannot interpret version')
        from .projections import state_record
        projection = state_record(db,run)
        row = db.execute('SELECT * FROM wf_runs WHERE run_id=?', (run,)).fetchone()
        if not row:
            raise Blocked('unknown run')
        from .projections import records, latest_metrics
        metrics=latest_metrics(records(db,run)[1])
        has_reviews=db.execute("SELECT 1 FROM sqlite_master WHERE name='wf_reviews'").fetchone()
        reviews=[dict(r) for r in db.execute('SELECT review_id,base_sha,head_sha,host_op,result,independent FROM wf_reviews WHERE run_id=? ORDER BY rowid',(run,))] if has_reviews else []
        findings=[dict(r) for r in db.execute('SELECT f.* FROM wf_findings f JOIN wf_reviews r USING(review_id) WHERE r.run_id=?',(run,))] if has_reviews else []
        has_budgets=db.execute("SELECT 1 FROM sqlite_master WHERE name='wf_repair_budgets'").fetchone()
        budgets=[dict(r) for r in db.execute('SELECT * FROM wf_repair_budgets WHERE run_id=?',(run,))] if has_budgets else []
        return {'run': dict(row), 'state':projection['payload']['status'],'projection':projection,
                'reviews':reviews,'findings':findings,'repair_budgets':budgets,'metrics':metrics,
                'metrics_unknown_reason':None if any(r['payload']['role'] in ('implement','repair','review') for r in metrics) else 'no agent observations recorded', 'operations': [dict(r) for r in db.execute('SELECT op_id,node_id,kind,phase FROM wf_operations WHERE run_id=?', (run,))],
                'alarms': [dict(r) for r in db.execute('SELECT * FROM wf_alarms')], 'accepted': projection['payload']['acceptance']=='accepted'}
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
        if name == 'resume': p.add_argument('--resume-authority',required=True)
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
        workflow_path=Path(args.workflow)
        if not workflow_path.is_file():raise Blocked('workflow input must be a regular file')
        with workflow_path.open('rb') as source:workflow_bytes=source.read(262145)
        if len(workflow_bytes)>262144:raise Blocked('workflow byte limit')
        try:config=yaml.load(workflow_bytes,Loader=StrictLoader)
        except (yaml.YAMLError,ValueError,RecursionError):raise Blocked('invalid bounded workflow YAML') from None
        validate_schema('workflow.schema.json',config)
        manifest = json.loads(Path(args.manifest).read_text())
        environment = {k:v for k,v in os.environ.items() if k in ('PATH','HOME','PYTHONPATH','PYTHONDONTWRITEBYTECODE','TMPDIR','PI_OFFLINE')}
        with Authority(args.project) as authority:
            # Engine reserves the run before handler operations can be persisted.
            coordinate = Coordinate(authority,args.run,contract,catalog,config,args.containment,manifest,environment)
            registry = coordinate.registry()
            load_workflow(registry, workflow_bytes, ROOT)
            maximum=max([config['defaults']['max_repair_attempts'],*[n.get('max_repair_attempts',0) for n in config['nodes']]])
            engine = Engine(authority,args.run,config,registry,ROOT,max_task_visits=len(contract['tasks'])*(maximum+1)+maximum+1,
                            input_identity={'contract':contract,'catalog_hash':digest(catalog),'manifest':manifest,'environment':environment,
                                            'host_hash':content_hash(ROOT/'runtime/pi-host/host.mjs')})
            try:
                if args.command == 'resume':
                    auth_path=Path(args.resume_authority).resolve(strict=True)
                    if auth_path.is_relative_to(authority.project):raise Blocked('resume authority must be external to agent worktree')
                    private_file(auth_path)
                    coordinate.recover(json.loads(auth_path.read_text()))
                authority.store.register_controller(args.run)
                outcome='interrupted'
                try:
                    outcome=engine.invoke()['outcome']
                    if outcome=='accepted':
                        with authority.store.transaction() as db:
                            db.execute("UPDATE wf_runs SET state='accepted',reservation=0 WHERE run_id=?",(args.run,))
                except Blocked as exc:
                    reason=str(exc)
                    previous=authority.store.db.execute("SELECT payload FROM wf_events WHERE run_id=? AND kind='workflow_blocked' ORDER BY seq DESC LIMIT 1",(args.run,)).fetchone()
                    if reason.startswith('Git prerequisite:'):reason='Git prerequisite failed; inspect scoped operation before continuation'
                    if not (previous and (json.loads(previous[0])['reason']==reason or reason.startswith('workflow blocked/final_failure;'))):
                        coordinate.record_block(reason,'budget exhausted' in reason)
                    raise
                finally:
                    authority.store.settle_controller(args.run,outcome)
                    from .projections import Publisher
                    Publisher(authority,args.run).publish()
            finally:
                engine.close()
            print(canonical(status(args.project,args.run)))
        return 0
    except (Blocked, ValueError, ValidationError) as exc:
        reason='schema-invalid input/result at '+ '/'.join(str(part) for part in exc.absolute_path) if isinstance(exc,ValidationError) else str(exc)
        print(canonical({'status':'blocked','reason':reason})); return 2


if __name__ == '__main__':
    sys.exit(main())
