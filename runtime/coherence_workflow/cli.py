"""Opt-in standalone entry. Workflow edges, not this facade, schedule tasks."""
import argparse
import copy
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import time
import tempfile
import uuid

import yaml
from jsonschema.exceptions import ValidationError

from .engine import Engine, StrictLoader, load_workflow
from .git_effects import GitEffects, assert_safe_git_inputs, inventory_preflight, recovery_inventory_preflight
from .intake import admit, content_hash, load_contract
from .pi_adapter import PiAdapter, host_resource
from .registry import CHECKS, Handler, Registry, validate_schema
from .sessions import select_session, retained_candidates, manifest_compatibility, open_manifest
from .interaction import Interaction, OwnerChannel, QUESTION_SCHEMA
from .store import Authority, Blocked, canonical, digest, git, private_file, safe_path
from .tools import Gateway, ProcessTool, reconcile, snapshot, runtime_python, owned_file, clean_owned
from .verification import ReviewRepair, Verification, unittest_oracle

ROOT = Path(__file__).resolve().parents[2]


def file_bytes(project, args):
    path = safe_path(project, args['path'])
    observed = path.read_text() if path.is_file() else None
    return {'collected': 1, 'exit_code': 0 if observed == args['expected'] else 1,
            'diagnosis':None if observed == args['expected'] else 'implementation',
            'output': canonical({'path': args['path'], 'expected_hash': digest(args['expected']),
                                 'observed_hash': digest(observed)})}


def project_command_argv(args):
    """Inspect the approved executable without running project code at preflight."""
    argv=args['argv']
    executable=Path(argv[0])
    if not executable.is_absolute() or executable!=executable.resolve(strict=True) or not os.access(executable,os.X_OK):
        raise Blocked('project command executable unavailable/noncanonical; correct approved check argv')
    return argv


def registered_checks(project, gateway=None, *, admitted_host_ops=()):
    result = {name: {**spec, 'execute': unittest_oracle} for name, spec in CHECKS.items()}
    for file, selector in [('test_recovery.py','EffectRecoveryTests'),('test_recovery.py','PressureRecoveryTests'),
                           ('test_projections.py','ProjectionRecoveryTests'),('test_recovery.py','VersionRecoveryTests'),
                           ('test_interaction.py','QuestionParkTests'),('test_interaction.py','OriginalAnswerTests'),
                           ('test_controls.py','ControlDeliveryTests'),('test_interaction.py','AutonomyAdmissionTests'),
                           ('test_parent_transport.py','LeanAnswerTests')]:
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
        op,process=gateway.launch('oracle:'+uuid.uuid4().hex,tool.id,'1',{},admitted_host_ops=admitted_host_ops)
        code=process.wait(timeout=15);receipt=gateway.settle(op,code)
        if not receipt.get('replacement_allowed'):raise Blocked('oracle descendants unsettled')
        valid=code in (0,20)
        return {'collected':1 if valid else 0,'exit_code':0 if code==0 else 1 if code==20 else None,
                'diagnosis':'implementation' if code==20 else None,
                'output':canonical({'operation_id':op,'raw_exit':code,'criterion':'answer() exact integer result'})}
    result['workflow.PythonAnswer']={'version':'1','schema':{'type':'object','additionalProperties':False,
        'properties':{'path':{'type':'string','minLength':1},'expected':{'type':'integer'}},'required':['path','expected']},'execute':python_answer}
    def command(args):
        if gateway is None:raise Blocked('contained project command gateway unavailable')
        argv=project_command_argv(args)
        # Only approved task REQUIRED commands reach this runner, never worker shell input.
        # The wrapper and all command descendants share Gateway's own-child custody.
        with tempfile.TemporaryDirectory(prefix='coherence-check-') as temporary:
            output=Path(temporary)/'output'
            tool=ProcessTool('check-project-command','1',{'type':'object','additionalProperties':False},
                lambda unused:runtime_python(
                    'import subprocess; '
                    'f=open(sys.argv[1],"wb"); '
                    'p=subprocess.run(sys.argv[2:],stdout=f,stderr=subprocess.STDOUT); '
                    'f.close(); sys.exit(p.returncode)',str(output),*argv),(),
                {k:v for k,v in os.environ.items() if k in ('PATH','HOME','PYTHONPATH','PYTHONDONTWRITEBYTECODE','TMPDIR')})
            gateway.tools[tool.id]=tool
            op,process=gateway.launch('oracle:'+uuid.uuid4().hex,tool.id,'1',{},admitted_host_ops=admitted_host_ops)
            try:code=process.wait(timeout=args.get('timeout',60))
            except subprocess.TimeoutExpired:
                gateway.resolve(op)
                process.wait(timeout=5)
                return {'collected':0,'exit_code':None,'output':'project command timed out; inspect before rerun'}
            receipt=gateway.settle(op,code)
            if not receipt.get('replacement_allowed'):raise Blocked('project check descendants unsettled')
            with output.open('rb') as stream:text=stream.read(32768).decode('utf-8',errors='replace')
            return {'collected':1,'exit_code':code,'output':text,'operation_id':op,
                    'diagnosis':'implementation' if code else None}
    result['workflow.Command']={'version':'1','schema':{'type':'object','additionalProperties':False,
        'properties':{'argv':{'type':'array','minItems':1,'items':{'type':'string','pattern':'^[^\\u0000]*$'}},
                      'timeout':{'type':'integer','minimum':1}},'required':['argv']},'execute':command}
    result['workflow.FileBytes'] = {'version': '1', 'schema': {'type': 'object', 'additionalProperties': False,
        'properties': {'path': {'type': 'string', 'minLength': 1}, 'expected': {'type': 'string'}},
        'required': ['path', 'expected']}, 'execute': lambda args: file_bytes(project, args)}
    return result


class Coordinate:
    """Registered handlers compose one LangGraph task-progress cycle."""
    def __init__(self, authority, run, contract, config, containment, manifest, environment):
        self.authority, self.store, self.run = authority, authority.store, run
        self.contract, self.config, self.manifest = admit(contract), config, manifest
        self.path_limits = {task['id'] for task in self.contract['tasks'] if 'owned_paths' in task}
        for task in self.contract['tasks']:
            task.setdefault('depends', [])
            task.setdefault('owned_paths', [])
            task.setdefault('required', [])
            task.setdefault('optional', [])
            task.setdefault('context_group', task['id'])
            task.setdefault('outcome', task.get('description'))
        self.containment, self.environment = containment, environment
        self.host_hash = content_hash(host_resource())
        self.agent_node = None
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
        self.interaction=Interaction(self.store,self.run)
        self.parent_transport=None

    def publish_run_binding(self):
        value={'run_id':self.run,**{k:None for k in ('task_id','node_id','attempt_id','session_id','role','task_hash')},
               'source_hash':digest(self.contract.get('sources', [])),'approval_hash':digest(self.contract.get('approval_refs', [])),
               'config_hash':digest(self.config)}
        with self.store.transaction() as db:
            old=db.execute('SELECT binding FROM wf_run_bindings WHERE run_id=?',(self.run,)).fetchone()
            if old and old[0]!=canonical(value):raise Blocked('run control binding drift')
            db.execute('INSERT OR IGNORE INTO wf_run_bindings VALUES(?,?)',(self.run,canonical(value)))
        return value

    def current(self):
        rows = self.store.db.execute("SELECT * FROM wf_tasks WHERE run_id=? AND state NOT IN ('checkpointed','read_only_complete') ORDER BY approved_order", (self.run,)).fetchall()
        if not rows:
            return None
        return dict(rows[0])

    def intake(self, context):
        self.contract = admit(self.contract)
        with self.store.transaction() as db:
            old = db.execute('SELECT contract FROM wf_run_inputs WHERE run_id=?', (self.run,)).fetchone()
            if old:
                if old['contract'] != canonical(self.contract):
                    raise Blocked('task input changed during an active run; use a new run for changed work')
            else:
                db.execute('INSERT INTO wf_run_inputs VALUES(?,?,?,?)',
                           (self.run, digest(self.contract), canonical(self.contract), ''))
                for order, task in enumerate(self.contract['tasks']):
                    db.execute("INSERT INTO wf_tasks VALUES(?,?,?,?,'pending',NULL,NULL,NULL)",
                               (self.run, task['id'], order, canonical(task)))
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
        baseline = self.git.begin(task)
        with self.store.transaction() as db:
            db.execute("UPDATE wf_tasks SET state='active',baseline=? WHERE run_id=? AND task_id=?", (canonical(baseline), self.run, task['id']))
            self.store.event(db, self.run, None, 'task_selected', {'task_id': task['id'], 'baseline': baseline['head']})
        return {'outcome': 'work'}

    @staticmethod
    def admit_node_tools(node, tools):
        """Registered tool permission IDs are fixed; configuration cannot widen them."""
        expected=set(tools)
        if not expected <= set(node['tools']) & set(node['permissions']):
            raise Blocked('configured node tool/permission restrictions do not admit registered tool manifest')

    def claim_path(self, task, name):
        """Claim only a clean, unchanged path immediately before a tool mutation."""
        owned_file(self.authority.project, name)
        if task['id'] in self.path_limits and name not in task['owned_paths']:
            raise Blocked('path outside task owned_paths: '+name)
        if name in task['owned_paths']:
            return
        row = self.store.db.execute('SELECT baseline FROM wf_tasks WHERE run_id=? AND task_id=?',
                                    (self.run, task['id'])).fetchone()
        if not row or not row[0]:
            raise Blocked('select task before editing files')
        baseline = json.loads(row[0])
        reconcile(self.authority.project, task['owned_paths'], baseline)
        clean_owned(self.authority.project, [name])
        assert_safe_git_inputs(self.authority.project, [name])
        task['owned_paths'].append(name)
        baseline['owned'][name] = baseline['files'].get(name)
        with self.store.transaction() as db:
            db.execute('UPDATE wf_tasks SET contract=?,baseline=? WHERE run_id=? AND task_id=?',
                       (canonical(task), canonical(baseline), self.run, task['id']))

    def owned_paths(self):
        return sorted({path for row in self.store.db.execute('SELECT contract FROM wf_tasks WHERE run_id=?', (self.run,))
                       for path in json.loads(row[0]).get('owned_paths', [])})

    def _tools(self, task, *, review=False):
        project = self.authority.project
        review_bundle=self.review_repair.bundle() if review else None
        unrestricted = not review and task['id'] not in self.path_limits
        readable = set(task['owned_paths']) | {s['path'] for s in self.contract.get('sources', [])} | {r['record_ref'] for r in self.contract.get('approval_refs', [])}
        def schema(paths, write):
            properties = {'path': {'type': 'string'} if unrestricted else {'enum': sorted(paths)}}
            if write:
                properties['text'] = {'type': 'string', 'maxLength': 32768}
            else:
                properties.update({'offset': {'type': 'integer', 'minimum': 0},
                                   'limit': {'type': 'integer', 'minimum': 1, 'maximum': 32768},
                                   'query': {'type': 'string', 'minLength': 1, 'maxLength': 1024}})
            return {'type': 'object', 'additionalProperties': False, 'properties': properties,
                    'required': ['path', 'text'] if write else ['path']}
        def read_result(args, receipt):
            if review:
                from .review_documents import read_review
                return read_review(self.authority.project, review_bundle, args)
            path = owned_file(project, args['path'])
            if not path.is_file():
                raise Blocked('authorized read unavailable: select an authorized regular file')
            offset=args.get('offset',0);limit=args.get('limit',8192)
            with path.open('r', encoding='utf-8') as source:
                source.seek(offset)
                query=args.get('query')
                overlap=len(query)-1 if query else 0
                if overlap>=limit:
                    raise Blocked('search limit must exceed query length; increase limit and continue')
                text=source.read(limit-overlap)
                next_offset=source.tell()
                text+=source.read(overlap) if overlap else ''
                end_offset=source.tell()
                eof=not source.read(1)
                if eof:next_offset=end_offset
                if query:
                    text='\n'.join(line for line in text.splitlines() if query in line)
            continuation=None if eof else {'path':args['path'],'offset':next_offset,'limit':limit}
            if continuation is not None and 'query' in args:continuation['query']=args['query']
            return {'text':text,'offset':offset,'next_offset':next_offset,'eof':eof,'continuation':continuation}
        # Reads are direct scoped observations, not fake contained processes.
        read = ProcessTool('read_file', '1', schema(readable, False), None, (), self.environment, read_result)
        search_schema=schema(readable, False);search_schema['required']=['path','query']
        search = ProcessTool('search_file','1',search_schema,None,(),self.environment,read_result)
        if review:
            review_schema=schema(readable,False)
            review_schema['properties'].pop('query')
            review_schema['properties']['revision']={'enum':['working','base','head','diff']}
            return {'read_file':ProcessTool('read_file','1',review_schema,None,(),self.environment,read_result)}
        tools = {'read_file': read, 'search_file': search}
        if not review and (unrestricted or task['owned_paths']):
            def write_result(args, receipt):
                path=owned_file(project,args['path'])
                self.claim_path(task, args['path'])
                path.parent.mkdir(parents=True,exist_ok=True)
                path.write_text(args['text'],encoding='utf-8')
                return {'path':args['path'],'written':len(args['text'])}
            tools['write_file']=ProcessTool('write_file','1',schema(task['owned_paths'],True),None,
                tuple(task['owned_paths']),self.environment,write_result)
            edit_schema={'type':'object','additionalProperties':False,'properties':{
                'path':{'type':'string'} if unrestricted else {'enum':sorted(task['owned_paths'])},'old':{'type':'string','minLength':1,'maxLength':32768},
                'new':{'type':'string','maxLength':32768}},'required':['path','old','new']}
            def edit_result(args, receipt):
                path=owned_file(project,args['path'])
                text=path.read_text(encoding='utf-8')
                if text.count(args['old'])!=1:
                    raise Blocked('edit target missing or ambiguous; read/search and supply a unique exact old region')
                self.claim_path(task, args['path'])
                path.write_text(text.replace(args['old'],args['new'],1),encoding='utf-8')
                return {'path':args['path'],'replacements':1}
            tools['edit_file']=ProcessTool('edit_file','1',edit_schema,None,
                tuple(task['owned_paths']),self.environment,edit_result)
        if not review and task['required']:
            def check_result(args, receipt):
                item=next(i for i in task['required'] if i['id']==args['item_id'])
                hosts=receipt.get('admitted_host_ops',()) if receipt else ()
                verifier=Verification(self.authority,self.run,
                    registered_checks(project,self.gateway,admitted_host_ops=hosts),
                    environment=self.verification.environment)
                observed=verifier.run_checks({**task,'required':[item]},admitted_host_ops=hosts)
                row=self.current()
                evidence=json.loads(row['evidence']) if row['evidence'] else []
                evidence=[e for e in evidence if e['item_id']!=item['id']]+observed
                with self.store.transaction() as db:
                    db.execute('UPDATE wf_tasks SET evidence=? WHERE run_id=? AND task_id=?',
                        (canonical(evidence),self.run,task['id']))
                return [{**{k:r.get(k) for k in ('item_id','evidence_id','status','reason','collected','exit_code')},
                         'output':r.get('output','')[:8192],
                         'output_truncated':len(r.get('output',''))>8192} for r in observed]
            tools['run_check']=ProcessTool('run_check','1',{'type':'object','additionalProperties':False,
                'properties':{'item_id':{'enum':[i['id'] for i in task['required']]}},'required':['item_id']},
                None,(),self.environment,check_result)
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

    def controls_boundary(self, adapter=None):
        rows=self.store.db.execute("""SELECT i.*,c.action,c.binding FROM wf_owner_inputs i JOIN wf_controls c USING(input_id)
            WHERE i.run_id=? AND i.stage='received' AND i.receipt IS NULL ORDER BY i.rowid""",(self.run,)).fetchall()
        for row in rows:
            value=json.loads(row['payload'])
            target=self.store.db.execute('SELECT binding FROM wf_active_targets WHERE run_id=?',(self.run,)).fetchone()
            if value['target_scope']=='active_session' and (not adapter or not target or json.loads(target[0])!=value['binding']):
                self.interaction.control_stage(row['input_id'],'received','blocked',{'reason':'target settled/changed; never retargeted'})
                continue
            if row['action']=='inquire':
                facts={'run_state':self.store.db.execute('SELECT state FROM wf_runs WHERE run_id=?',(self.run,)).fetchone()[0],
                       'active_binding':json.loads(target[0]) if target else None,'private_reasoning':None,
                       'reason':'recorded facts only; no private thoughts or compliance claim'}
                with self.store.transaction() as db:
                    db.execute('UPDATE wf_owner_inputs SET receipt=? WHERE input_id=? AND receipt IS NULL',(canonical(facts),row['input_id']))
                    self.store.event(db,self.run,None,'control_inquiry_result',{'input_id':row['input_id'],'facts':facts})
                continue
            if row['action'] in ('steer','follow_up'):
                adapter.enqueue_control(value)
                continue
            if row['action'] in ('pause','cancel'):
                if adapter:
                    self.stop_control=value
                    return True
                self.finish_stop(value)
                raise Blocked('run '+('paused' if row['action']=='pause' else 'cancelled')+'; no worker ACK claimed')
        return False

    def finish_stop(self, value):
        self.authority.assert_held()
        if self.store.db.execute("SELECT 1 FROM wf_operations o JOIN wf_runs r USING(run_id) WHERE o.kind='process' AND o.phase!='completed' AND r.state!='ABANDONED'").fetchone():
            raise Blocked('pause/cancel custody not quiescent; no stopped claim')
        empty=[]
        for row in self.store.db.execute('SELECT p.op_id FROM wf_processes p JOIN wf_operations o USING(op_id) WHERE o.run_id=?',(self.run,)):
            record,receipt=self.gateway._record(row['op_id'])
            if self.gateway.containment.populated(receipt)!=0:raise Blocked('pause/cancel populated scope; no stopped claim')
            empty.append({'operation_id':row['op_id'],'containment_hash':digest(receipt),'populated':0})
        self.reconcile_effect({}, {})
        evidence={'scopes':empty,'partial_snapshot_hash':digest(snapshot(self.authority.project,[])),
                  'worker_acknowledged':False,'reason':'supported abort/drain plus owned kernel-empty and partial Git/files reconciliation'}
        self.interaction.control_stage(value['input_id'],'received','reconciled',evidence)
        state='paused' if value['action']=='pause' else 'cancelled'
        with self.store.transaction() as db:
            db.execute('UPDATE wf_runs SET state=? WHERE run_id=?',(state,self.run))
            db.execute('DELETE FROM wf_active_targets WHERE run_id=?',(self.run,))
            if state=='cancelled':db.execute("UPDATE wf_questions SET stage='cancelled' WHERE run_id=? AND stage IN ('parking','pending','answered','delivering')",(self.run,))
            self.store.event(db,self.run,None,'owner_'+state,{'input_id':value['input_id'],'evidence':evidence})

    def question_binding(self, task, node, attempt, role):
        return {'run_id':self.run,'task_id':task['id'],'node_id':node['id'],'attempt_id':task['id']+':'+str(attempt),
                'source_hash':digest(self.contract.get('sources', [])),'task_hash':digest(task),
                'approval_hash':digest(self.contract.get('approval_refs', [])),'config_hash':digest(self.config),'role':role}

    def session_adapter(self, manifest, node, task, role, *, pin=None, original=None):
        policy=node['session_policy']
        request={**manifest_compatibility(manifest,self.authority.project,role=role,affinity=task['context_group'],
                    review_lineage=task.get('review_lineage')),
                 'authorized':True,'ready':True,'reconciled':True,
                 'fresh_only':policy['mode']=='fresh_only','original':original}
        candidates=retained_candidates(self.store,self.run)
        context={k:request[k] for k in ('role','affinity','review_lineage')}
        if task.get('first_review') and not pin:request['review_lineage']=None
        arguments=dict(environment=self.environment,session_context=context,interaction=self.interaction,
                       question_binding=self.question_binding({k:v for k,v in task.items() if k not in ('attempt','review_lineage','first_review')},node,task.get('attempt',0),role))
        if pin:
            request['pin']=pin['snapshot']['session_id']
            request['fresh_only']=False
            candidate=next((c for c in candidates if c['id']==request['pin'] and c['host_op']==pin['host_op']),None)
            if not candidate:raise Blocked('original question conversation unavailable; owner recovery required')
            adapter=PiAdapter(self.gateway,open_manifest(manifest,candidate),node='reopen:'+uuid.uuid4().hex,
                reopen_from=candidate['host_op'],**arguments)
            try:
                choice=select_session(request,[{**candidate,'telemetry':adapter.snapshot}],now_ns=time.time_ns(),
                    max_age_ns=self.config['defaults']['telemetry_max_age_ms']*1_000_000,
                    min_free_tokens_before_compaction=policy['min_free_tokens_before_compaction'])
            except BaseException:
                adapter.close();raise
            return adapter,choice
        choice=select_session(request,candidates,now_ns=time.time_ns(),
            max_age_ns=self.config['defaults']['telemetry_max_age_ms']*1_000_000,
            min_free_tokens_before_compaction=policy['min_free_tokens_before_compaction'])
        selected=next((c for c in candidates if c['id']==choice['session_id']),None)
        adapter=PiAdapter(self.gateway,open_manifest(manifest,selected) if selected else manifest,
            node='host:'+uuid.uuid4().hex,reopen_from=selected['host_op'] if selected else None,**arguments)
        return adapter,choice

    def owner_input(self, context):
        from langgraph.types import interrupt
        pending=self.interaction.pending()
        if len(pending)!=1:raise Blocked('ambiguous/missing original question')
        gate=pending[0]
        if gate['stage']=='pending':
            interrupt({'gate_id':gate['gate_id'],'nonce':gate['nonce'],'binding':json.loads(gate['binding']),
                       'request':json.loads(gate['request'])})
            gate=self.interaction.question(gate['gate_id'])
        if gate['stage']!='answered':raise Blocked('question has no accepted original answer')
        return {'outcome':'ready'}

    def continue_original(self, context):
        pending=self.interaction.pending()
        if len(pending)!=1 or pending[0]['stage']!='answered':raise Blocked('original answer not ready')
        gate=pending[0];pin=json.loads(gate['pin']);binding=json.loads(gate['binding'])
        node=next(n for n in self.config['nodes'] if n['id']==binding['node_id'])
        declared=context['node']
        if (any(declared[key]!=node[key] for key in ('role','profile','skill','tools','permissions')) or
                declared['session_policy']['min_free_tokens_before_compaction']!=node['session_policy']['min_free_tokens_before_compaction']):
            raise Blocked('configured continuation differs from original role/resources/headroom; explicit recovery required')
        if binding['role']=='review':
            bundle=self.review_repair.bundle()
            task={'id':'final-review','context_group':'final-review','owned_paths':self.owned_paths()}
            if {**self.question_binding(task,node,0,'review'),'attempt_id':pin['attempt_id'],'session_id':binding['session_id']}!=binding or digest(bundle)!=pin['bundle_hash']:
                raise Blocked('original review source/approval/config/range drift')
            with self.store.transaction() as db:db.execute("UPDATE wf_runs SET state='running' WHERE run_id=? AND state='waiting_owner_input'",(self.run,))
            return self.review_boundary({'node':node,'operation_id':context['operation_id'],'run_id':self.run},continuation=gate)
        row=self.current()
        if not row or row['task_id']!=binding['task_id']:raise Blocked('original task changed; producing renewal required')
        task=json.loads(row['contract'])
        expected={**self.question_binding(task,node,pin['attempt'],binding['role']),'attempt_id':pin['attempt_id'],'session_id':binding['session_id']}
        if expected!=binding:raise Blocked('original source/task/approval/config drift; producing renewal required')
        with self.store.transaction() as db:
            db.execute("UPDATE wf_runs SET state='running' WHERE run_id=? AND state='waiting_owner_input'",(self.run,))
        return self.implement({'node':node,'operation_id':context['operation_id'],'run_id':self.run},
                              role=binding['role'],attempt=pin['attempt'],continuation=gate)

    def implement(self, context, *, role='implement', attempt=0, before_prompt=None, continuation=None):
        if content_hash(host_resource()) != self.host_hash:
            raise Blocked('active SDK host content drift')
        row = self.current()
        if not row or row['state'] != 'active':
            raise Blocked('missing selected task')
        task = json.loads(row['contract'])
        node = context['node']
        self.agent_node = node
        self.gateway.tools = self._tools(task)
        admitted=set(self.gateway.tools)
        if 'request_owner_input' in node['tools']:admitted.add('request_owner_input')
        self.admit_node_tools(node,admitted)
        attempt_id=task['id']+':'+str(attempt)+(':continue:'+continuation['gate_id'] if continuation else '')
        self.gateway.audit_task_boundary(task['owned_paths'], json.loads(row['baseline']))
        manifest = copy.deepcopy(self.manifest)
        if (manifest['profile'] != self.config['profiles'][node['profile']] or
                len(manifest['skills']) != 1 or manifest['skills'][0]['sha256'] != self.config['skills'][node['skill']]['sha256']):
            raise Blocked('SDK manifest differs from approved graph profile/skill')
        manifest['tools'] = [dict(name=t.id, version=t.version, description='Bounded authorized ' + t.id,
                                 parameters=t.arguments, permission=t.id) for t in self.gateway.tools.values()]
        manifest['permissions'] = list(self.gateway.tools)
        manifest['resource_hash'] = digest({k: manifest[k] for k in ('skills', 'tools', 'permissions', 'trust', 'system_prompt')})
        if 'request_owner_input' in node['tools']:
            manifest['tools'].append(dict(name='request_owner_input',version='1',description='Only necessary manager-answerable product/priority or unexpected material impact. Never routine technical work or approved tests. Use as ONLY tool in its batch.',parameters=QUESTION_SCHEMA,permission='request_owner_input'))
            manifest['permissions'].append('request_owner_input')
        manifest['resource_hash']=digest({k:manifest[k] for k in ('skills','tools','permissions','trust','system_prompt')})
        producer=self.store.db.execute('SELECT original_task_id FROM wf_corrections WHERE run_id=? AND task_id=?',(self.run,task['id'])).fetchone()
        original_task=producer[0] if producer else task['id']
        original=self.store.db.execute("SELECT result FROM wf_operations WHERE run_id=? AND node_id=? AND kind='sdk-turn' AND phase='completed'",(self.run,'implement:'+original_task+':0')).fetchone()
        original=json.loads(original[0])['after']['session_id'] if original else None
        adapter,selection=self.session_adapter(manifest,node,{**task,'attempt':attempt},role,
            pin=json.loads(continuation['pin']) if continuation else None,original=original)
        selection['repair_count']=attempt if role=='repair' else 0
        adapter.question_binding['attempt_id']=attempt_id
        expected = {'schema_version': 1, 'task_id': task['id'], 'attempt_id': attempt_id,
            'contract_hash': digest(task), 'kind': 'repair' if role=='repair' else 'implementation', 'outcome': 'produced',
            'changed_paths': task['owned_paths'], 'items': [], 'blocker': None}
        active_binding={**self.question_binding(task,node,attempt,role),'attempt_id':attempt_id,'session_id':adapter.session_id}
        with self.store.transaction() as db:
            db.execute('INSERT INTO wf_active_targets VALUES(?,?) ON CONFLICT(run_id) DO UPDATE SET binding=excluded.binding',(self.run,canonical(active_binding)))
        self.stop_control=None
        try:
            if continuation:
                value=self.interaction.delivery_intent(continuation['gate_id'])
                self.interaction.delivered(continuation['gate_id'],adapter.deliver_answer(value))
                with self.store.transaction() as db:
                    db.execute("UPDATE wf_questions SET stage='continued' WHERE gate_id=? AND stage='delivering'",(continuation['gate_id'],))
            if before_prompt:before_prompt()
            turn = adapter.prompt(node=('continue:'+continuation['gate_id']) if continuation else role+':' + task['id']+':'+str(attempt), task_id=task['id'], attempt_id=attempt_id,
                role=role, text=('Repair ONLY the diagnosed original failure; inspect current partial files and preserve the entire original contract. ' if role=='repair' else '')+'Implement ONLY this approved task using the registered tools. Never commit or access other paths. '
                'You must read relevant existing files using read_file; its output is actual authorized bytes. '
                'Whole unchanged task contract follows:\n' + canonical(task) + '\nReturn ONLY JSON matching this result shape, with actual outcome/paths. '
                'Set items to [] exactly: runner checks supply evidence, not model-invented item objects. '
                'Do not add any fields. Exact result shape: ' + canonical(expected),
                skill=manifest['skills'][0]['name'], contract_hash=digest(task), selection=selection,
                interrupt=lambda current:self.controls_boundary(current))
            result = None if turn['question_gate'] else json.loads(turn['output'])
            try:
                if result is not None:validate_schema('agent-result.schema.json', result)
            except Exception as exc:
                raise Blocked('schema-invalid implementation result; no check/commit or automatic retry') from exc
            if result is not None and (any(result[k] != expected[k] for k in ('task_id', 'attempt_id', 'contract_hash', 'kind')) or
                    result['outcome'] not in ('produced', 'read_only') or not set(result['changed_paths']) <= set(task['owned_paths'])):
                raise Blocked('invalid/blocked implementation result')
        finally:
            adapter.close(force=adapter.lifecycle.poisoned)
            with self.store.transaction() as db:db.execute('DELETE FROM wf_active_targets WHERE run_id=?',(self.run,))
            if self.stop_control:self.finish_stop(self.stop_control)
        row = self.current()
        reconcile(self.authority.project, task['owned_paths'], json.loads(row['baseline']))
        if turn['question_gate']:
            pin={'host_op':adapter.host_op,'snapshot':turn['snapshot'],'attempt':attempt,'attempt_id':attempt_id,'graph_op':context['operation_id']}
            gate=self.interaction.question(turn['question_gate'])
            self.interaction.settled(gate['gate_id'],pin=pin,
                proof={'turn_op':gate['turn_op'],'snapshot_hash':digest(turn['snapshot'])})
            return {'outcome':'owner_input_required'}
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
        receipt = self.git.checkpoint(task, json.loads(row['baseline']), dispositions)
        with self.store.transaction() as db:
            db.execute('UPDATE wf_tasks SET state=?,checkpoint=? WHERE run_id=? AND task_id=?',
                ('read_only_complete' if receipt['read_only'] else 'checkpointed', canonical(receipt), self.run, task['id']))
            self.store.event(db, self.run, None, 'task_checkpointed', {'task_id': task['id'], **receipt})
        return {'outcome': 'ok'}

    def review_boundary(self, context, *, continuation=None):
        if self.current() is not None:raise Blocked('review cannot precede checkpoints')
        with self.store.transaction() as db:
            self.store.event(db,self.run,None,'implementation_complete',{'acceptance':'blocked','reason':'independent review pending'})
        self.reconcile_effect({}, {})
        try:self.review_repair.refresh_evidence()
        except Blocked as exc:self.record_block(str(exc));return {'outcome':'blocked'}
        bundle=self.review_repair.bundle();node=context['node'];self.agent_node=node
        task={'id':'final-review','context_group':'final-review','owned_paths':self.owned_paths()}
        self.gateway.tools=self._tools(task,review=True)
        admitted=set(self.gateway.tools)
        if 'request_owner_input' in node['tools']:admitted.add('request_owner_input')
        self.admit_node_tools(node,admitted)
        manifest=copy.deepcopy(self.manifest)
        if (manifest['profile']!=self.config['profiles'][node['profile']] or len(manifest['skills'])!=1 or
                manifest['skills'][0]['sha256']!=self.config['skills'][node['skill']]['sha256'] or
                content_hash(host_resource())!=self.host_hash):
            raise Blocked('review exact profile/resource/host mismatch')
        manifest['tools']=[dict(name=t.id,version=t.version,description='Read bounded authorized current source bytes.',parameters=t.arguments,permission=t.id) for t in self.gateway.tools.values()]
        manifest['permissions']=['read_file']
        manifest['system_prompt']='You are a fresh independent read-only code reviewer. Never implement or repair. Judge the full committed range against supplied approved source/tasks/check evidence.'
        manifest['resource_hash']=digest({k:manifest[k] for k in ('skills','tools','permissions','trust','system_prompt')})
        round=self.store.db.execute('SELECT COUNT(*) FROM wf_reviews WHERE run_id=?',(self.run,)).fetchone()[0]
        if 'request_owner_input' in node['tools']:
            manifest['tools'].append(dict(name='request_owner_input',version='1',description='Necessary manager product/priority or unexpected material-impact question only, as ONLY tool in its batch. No ordinary technical/test questions.',parameters=QUESTION_SCHEMA,permission='request_owner_input'))
            manifest['permissions'].append('request_owner_input')
        manifest['resource_hash']=digest({k:manifest[k] for k in ('skills','tools','permissions','trust','system_prompt')})
        adapter,selection=self.session_adapter(manifest,node,{**task,'review_lineage':bundle['range_base'],'first_review':not round},'review',
            pin=json.loads(continuation['pin']) if continuation else None)
        if continuation and json.loads(continuation['pin'])['bundle_hash']!=digest(bundle):
            adapter.close();raise Blocked('original review bundle drift; producing renewal required')
        expected={'schema_version':1,'task_id':'final-review','attempt_id':'review:'+str(round),'contract_hash':digest(bundle),
            'kind':'review','outcome':'pass','range_base':bundle['range_base'],'range_head':bundle['range_head'],'findings':[],'blocker':None}
        finding={'id':'finding-1','severity':'important','criterion_ref':'ORIGINAL_ITEM_ID','location':'owned/path.py:LINE',
                 'observation':'specific observed source violation','evidence_ref':'owned/path.py','action':'bounded proposed correction','scope':'in_scope'}
        adapter.question_binding['attempt_id']=expected['attempt_id']
        active_binding={**self.question_binding(task,node,0,'review'),'attempt_id':expected['attempt_id'],'session_id':adapter.session_id}
        with self.store.transaction() as db:
            db.execute('INSERT INTO wf_active_targets VALUES(?,?) ON CONFLICT(run_id) DO UPDATE SET binding=excluded.binding',(self.run,canonical(active_binding)))
        self.stop_control=None
        try:
            if continuation:
                value=self.interaction.delivery_intent(continuation['gate_id'])
                self.interaction.delivered(continuation['gate_id'],adapter.deliver_answer(value))
                with self.store.transaction() as db:db.execute("UPDATE wf_questions SET stage='continued' WHERE gate_id=?",(continuation['gate_id'],))
            turn=adapter.prompt(node=('continue:'+continuation['gate_id']) if continuation else 'review:'+str(round),task_id='final-review',attempt_id=expected['attempt_id'],role='review',
                text='Review independently, do not fix. Inspect the actual full committed range and source/evidence references below. '
                'Use read_file with revision base, head or diff for committed files, or working for source documents; '
                'follow continuation offsets for large files and patches. '
                'Check source requirements beyond mechanical green (including extraneous/dead code). Return ONLY JSON in the exact shape '+canonical(expected)+
                '. If actual findings exist set outcome correction and findings to objects in this exact shape '+canonical(finding)+
                '. Scope-changing findings must use scope owner_decision, not in_scope. Never invent an issue. Full bundle: '+canonical(bundle),
                skill=manifest['skills'][0]['name'],contract_hash=digest(bundle),selection=selection,
                interrupt=lambda current:self.controls_boundary(current))
            result=None if turn['question_gate'] else json.loads(turn['output'])
            if result is not None:
                validate_schema('agent-result.schema.json',result)
                if any(result[k]!=expected[k] for k in ('task_id','attempt_id','contract_hash','kind')):raise Blocked('review identity mismatch')
        finally:
            adapter.close(force=adapter.lifecycle.poisoned)
            with self.store.transaction() as db:db.execute('DELETE FROM wf_active_targets WHERE run_id=?',(self.run,))
            if self.stop_control:self.finish_stop(self.stop_control)
        if turn['question_gate']:
            gate=self.interaction.question(turn['question_gate'])
            pin={'host_op':adapter.host_op,'snapshot':turn['snapshot'],'attempt':0,'attempt_id':expected['attempt_id'],'graph_op':context['operation_id'],'bundle_hash':digest(bundle)}
            self.interaction.settled(gate['gate_id'],pin=pin,proof={'turn_op':gate['turn_op'],'snapshot_hash':digest(turn['snapshot'])})
            return {'outcome':'owner_input_required'}
        self.review_repair.record_review(result,adapter.host_op)
        if result['outcome']=='pass':return {'outcome':'ok'}
        if result['outcome']=='correction':return {'outcome':'correction'}
        self.record_block('review blocked or owner input unavailable');return {'outcome':'blocked'}

    def schedule_correction(self, context):
        try:self.review_repair.schedule_corrections();return {'outcome':'ok'}
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
        questions=self.interaction.pending()
        if questions:
            if len(questions)!=1 or questions[0]['stage'] not in ('pending','answered'):
                raise Blocked('uncertain question/delivery; inspect original entries before recovery')
            gate=questions[0];pin=json.loads(gate['pin']);binding=json.loads(gate['binding'])
            turn=self.store.operation(gate['turn_op'])
            host=self.store.operation(pin['host_op'])
            if (turn['phase']!='completed' or host['phase']!='completed' or
                    json.loads(turn['result'])['after']!=pin['snapshot'] or
                    json.loads(gate['proof'])!={'turn_op':turn['op_id'],'snapshot_hash':digest(pin['snapshot'])}):
                raise Blocked('question recovery lacks original settled receipts')
            record,receipt=self.gateway._record(pin['host_op'])
            if self.gateway.containment.populated(receipt)!=0:raise Blocked('question original host not empty')
            self.reconcile_effect({}, {})
            graph=self.store.operation(pin['graph_op'])
            if graph['kind']!='graph' or graph['run_id']!=self.run or graph['node_id'].split(':')[0] not in (binding['node_id'],'continue-'+binding['role']):
                raise Blocked('question recovery original graph visit mismatch')
            if graph['phase']=='intent':
                self.store.transition(graph['op_id'],'intent','completed',{'outcome':'owner_input_required'})
            if any(r['op_id']!=graph['op_id'] for r in pending):
                raise Blocked('question recovery has other uncertain effects')
            if run['state']=='paused':
                with self.store.transaction() as db:db.execute("UPDATE wf_runs SET state='waiting_owner_input' WHERE run_id=?",(self.run,))
            return
        self.store.assert_dispatchable(self.run)
        uncertain=[r for r in pending if r['kind']=='sdk-turn']
        if uncertain:
            raise Blocked('partial SDK invocation cannot be replayed; inspect partial work and writers, then use abandon --project PROJECT --run RUN for a fresh run')
        checkpoints=[r for r in pending if r['kind']=='git-checkpoint']
        for op in checkpoints:
            from .git_effects import reconcile_checkpoint
            receipt=reconcile_checkpoint(self.authority,op['op_id'])
            self.store.transition(op['op_id'],'intent','completed',receipt)
            task_id=json.loads(op['intent'])['task_id']
            row=self.store.db.execute('SELECT * FROM wf_tasks WHERE run_id=? AND task_id=?',(self.run,task_id)).fetchone()
            task=json.loads(row['contract'])
            if any(d['status']!='satisfied' for d in self.verification.audit(task,json.loads(row['evidence']))):
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
            ('custody','code','custody',('ok',),self.custody),
            ('select','code','task_select',('work','done'),self.select),
            ('dispatch','code','work',('implement','repair'),self.dispatch),
            ('implement','agent','work',('ok','owner_input_required'),self.implement),
            ('repair','agent','repair',('ok','blocked','owner_input_required'),self.repair),
            ('owner-input-implement','gate','owner_input',('ready',),self.owner_input),
            ('owner-input-repair','gate','owner_input',('ready',),self.owner_input),
            ('continue-implement','agent','continue_original',('ok','owner_input_required'),self.continue_original),
            ('continue-repair','agent','continue_original',('ok','blocked','owner_input_required'),self.continue_original),
            ('verify','code','verification',('ok','repair','blocked'),self.verify),
            ('checkpoint','code','checkpoint',('ok',),self.checkpoint),
            ('review','agent','review',('ok','correction','blocked','owner_input_required'),self.review_boundary),
            ('owner-input-review','gate','owner_input',('ready',),self.owner_input),
            ('continue-review','agent','continue_original',('ok','correction','blocked','owner_input_required'),self.continue_original),
            ('schedule-correction','code','correction',('ok','blocked'),self.schedule_correction),
            ('failure','terminal','failure',(),self.failure),
            ('complete','terminal','success',(),self.complete)]
        effects = {'intake':('read',),'custody':('read',),'select':('read',),
                   'implement':('files','process','conversation'),'verify':('read','process'),
                   'checkpoint':('git','process'),'review':('read',),'complete':('read',),
                   'dispatch':('read',),'repair':('files','process','conversation'),
                   'schedule-correction':('read',),'failure':('read',)}
        effects.update({'owner-input-implement':(),'owner-input-repair':(),
                        'continue-implement':('files','process','conversation'),'continue-repair':('files','process','conversation'),
                        'owner-input-review':(),'continue-review':('read',)})
        registry.handlers = {name: Handler(name,'1',kind,stage,outcomes,function,
                                          side_effects=effects[name],reconcile=self.reconcile_effect)
                             for name,kind,stage,outcomes,function in definitions}
        registry.success_terminals = {'complete'}
        if self.parent_transport is not None:
            from .notifications.paseo import TRANSPORT
            registry.question_transports[TRANSPORT]=self.parent_transport
        return registry


class IdleControls:
    """Short-lived deterministic control consumer; no agent/task scheduling API.

    Reuse the same custody/partial-work/control implementations as the running
    controller, without reconstructing or choosing workflow inputs or a model.
    """
    def __init__(self, authority, run):
        self.authority,self.store,self.run=authority,authority.store,run
        self.interaction=Interaction(self.store,run,initialize=False)
        parents={json.loads(row[0])['parent'] for row in self.store.db.execute('SELECT p.containment FROM wf_processes p JOIN wf_operations o USING(op_id) WHERE o.run_id=? AND p.containment IS NOT NULL',(run,))}
        if len(parents)>1:raise Blocked('idle controls have ambiguous containment capability; no stop claim')
        self.gateway=Gateway(authority,run,next(iter(parents)),{}) if parents else None

    def reconcile_effect(self, context, result):
        return Coordinate.reconcile_effect(self,context,result)

    def finish_stop(self, value):
        return Coordinate.finish_stop(self,value)

    def consume(self):
        try:Coordinate.controls_boundary(self)
        except Blocked as exc:
            state=self.store.db.execute('SELECT state FROM wf_runs WHERE run_id=?',(self.run,)).fetchone()[0]
            if state not in ('paused','cancelled'):raise


def consume_idle_controls(project, run, received):
    try:
        with Authority(project) as owner:
            IdleControls(owner,run).consume()
            return dict(owner.store.db.execute('SELECT * FROM wf_owner_inputs WHERE input_id=?',(received['input_id'],)).fetchone())
    except Blocked as exc:
        if str(exc)=='worktree writer lock already held':return received
        # Acceptance remains durable, but no stopped/delivery success is invented.
        return {**received,'delivery_blocker':str(exc)}


def status(project, run):
    database = Path(project) / '.coherence/workflow/workflow.sqlite'
    private_file(database)
    db = sqlite3.connect(database.as_uri() + '?mode=ro', uri=True)
    db.row_factory = sqlite3.Row
    try:
        db.execute('BEGIN')
        if [r[0] for r in db.execute('SELECT version FROM wf_meta')] != [1]:
            raise Blocked('unsupported application schema; read-only status cannot interpret version')
        row = db.execute('SELECT * FROM wf_runs WHERE run_id=?', (run,)).fetchone()
        if not row:
            raise Blocked('unknown run')
        if row['state']=='ABANDONED':
            return {'run':dict(row),'state':'ABANDONED','accepted':False,
                    'operations':[dict(r) for r in db.execute(
                        'SELECT op_id,node_id,kind,phase FROM wf_operations WHERE run_id=?',(run,))],
                    'questions':[dict(r) for r in db.execute('SELECT * FROM wf_questions WHERE run_id=?',(run,))]
                        if db.execute("SELECT 1 FROM sqlite_master WHERE name='wf_questions'").fetchone() else [],
                    'controls':[dict(r) for r in db.execute('SELECT i.* FROM wf_owner_inputs i JOIN wf_controls c USING(input_id) WHERE i.run_id=?',(run,))]
                        if db.execute("SELECT 1 FROM sqlite_master WHERE name='wf_controls'").fetchone() else [],
                    'note':'historical rows and partial work retained; no effects replayed or completed'}
        from .projections import state_record
        projection = state_record(db,run)
        from .projections import records, latest_metrics
        metrics_reason=None
        try:
            metrics=latest_metrics(records(db,run)[1])
        except Exception as exc:
            metrics=[]  # Optional observations never replace SQL state.
            metrics_reason='metric observation unavailable: '+type(exc).__name__
        has_reviews=db.execute("SELECT 1 FROM sqlite_master WHERE name='wf_reviews'").fetchone()
        reviews=[dict(r) for r in db.execute('SELECT review_id,base_sha,head_sha,host_op,result,independent FROM wf_reviews WHERE run_id=? ORDER BY rowid',(run,))] if has_reviews else []
        findings=[dict(r) for r in db.execute('SELECT f.* FROM wf_findings f JOIN wf_reviews r USING(review_id) WHERE r.run_id=?',(run,))] if has_reviews else []
        has_budgets=db.execute("SELECT 1 FROM sqlite_master WHERE name='wf_repair_budgets'").fetchone()
        budgets=[dict(r) for r in db.execute('SELECT * FROM wf_repair_budgets WHERE run_id=?',(run,))] if has_budgets else []
        has_interaction=db.execute("SELECT 1 FROM sqlite_master WHERE name='wf_questions'").fetchone()
        questions=[dict(r) for r in db.execute("SELECT * FROM wf_questions WHERE run_id=? AND stage NOT IN ('continued','cancelled') ORDER BY rowid",(run,))] if has_interaction else []
        for question in questions:
            question['graph_parked']=bool(db.execute('SELECT 1 FROM wf_question_parks WHERE gate_id=?',(question['gate_id'],)).fetchone())
        controls=[dict(r) for r in db.execute('SELECT i.* FROM wf_owner_inputs i JOIN wf_controls c USING(input_id) WHERE i.run_id=? ORDER BY i.rowid',(run,))] if has_interaction else []
        return {'run': dict(row), 'state':projection['payload']['status'],'projection':projection,'questions':questions,'controls':controls,
                'parent_transport':{'binding':[dict(r) for r in db.execute('SELECT descriptor FROM wf_parent_bindings WHERE run_id=?',(run,))],
                    'outbox':[dict(r) for r in db.execute('SELECT o.event_id,o.stage,d.attempts,d.blocker,d.tool_receipt FROM wf_outbox o LEFT JOIN wf_parent_delivery d USING(event_id) WHERE o.run_id=?',(run,))]}
                    if db.execute("SELECT 1 FROM sqlite_master WHERE name='wf_parent_bindings'").fetchone() else None,
                'reviews':reviews,'findings':findings,'repair_budgets':budgets,'metrics':metrics,
                'metrics_unknown_reason':metrics_reason or (None if any(r['payload']['role'] in ('implement','repair','review') for r in metrics) else 'no agent observations recorded'), 'operations': [dict(r) for r in db.execute('SELECT op_id,node_id,kind,phase FROM wf_operations WHERE run_id=?', (run,))],
                'alarms': [dict(r) for r in db.execute('SELECT * FROM wf_alarms')], 'accepted': projection['payload']['acceptance']=='accepted'}
    finally:
        db.close()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest='command', required=True)
    for name in ('start','resume'):
        p = subs.add_parser(name)
        for flag in ('project','tasks'):
            p.add_argument('--' + flag, required=True)
        for flag in ('workflow','manifest','containment'):
            p.add_argument('--'+flag)
        p.add_argument('--run', required=True)
        p.add_argument('--suite-root', help='explicit approved skill/settings resource root (required for installed wheel)')
        p.add_argument('--parent-binding')
        if name == 'resume': p.add_argument('--resume-authority',required=True)
    p = subs.add_parser('preflight', help='read-only actual worktree inventory/ownership; no launch authority')
    p.add_argument('--project', required=True)
    p.add_argument('--tasks', required=True)
    p = subs.add_parser('intake')
    for flag in ('project','tasks'):
        p.add_argument('--' + flag, required=True)
    p = subs.add_parser('status'); p.add_argument('--project', required=True); p.add_argument('--run', required=True)
    p = subs.add_parser('abandon', help='explicitly release an inactive run; preserve partial work and uncertain effects')
    p.add_argument('--project', required=True); p.add_argument('--run', required=True)
    for name in ('pending','answer','control'):
        p = subs.add_parser(name); p.add_argument('--project', required=True); p.add_argument('--run', required=True)
        if name != 'pending':
            p.add_argument('--input',required=True);p.add_argument('--input-authority',required=True)
    for name in ('parent-answer',):
        p=subs.add_parser(name)
        for flag in ('project','run','nonce'):p.add_argument('--'+flag,required=True)
        p.add_argument('--event',required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == 'preflight':
            contract = load_contract(args.tasks)
            observed = inventory_preflight(args.project, contract['tasks'])
            print(canonical({'status':'ready', 'scope':'inventory/ownership only; not launch approval',
                'head':observed['head'], 'index_hash':observed['index'],
                'inventory_hash':digest(observed['files']), 'entries':len(observed['files']),
                'directories':sum(v is not None and v.get('kind')=='directory' for v in observed['files'].values()),
                'owned_paths':sorted(observed['owned'])})); return 0
        if args.command == 'parent-answer':
            from .notifications.paseo import facade
            print(canonical(facade(Path(args.project).absolute(),args.run,args.command,args.nonce,getattr(args,'event',None))));return 0
        if args.command == 'abandon':
            with Authority(args.project) as authority:
                result=authority.store.abandon(args.run)
            print(canonical({'run':result,'state':result['state'],'accepted':False}));return 0
        if args.command == 'status':
            print(canonical(status(args.project, args.run))); return 0
        if args.command == 'pending':
            result=status(args.project,args.run)
            print(canonical({'run_id':args.run,'state':result['state'],'questions':result['questions'],'controls':result['controls']}));return 0
        if args.command in ('answer','control'):
            channel=OwnerChannel(Path(args.project).resolve(strict=True),args.run)
            try:
                ledger=Interaction(channel,args.run,initialize=False)
                value=json.loads(Path(args.input).read_text())
                authority_path=Path(args.input_authority).resolve(strict=True)
                if authority_path.is_relative_to(Path(args.project).resolve()):raise Blocked('input authority must be external to worker worktree')
                private_file(authority_path)
                approval=json.loads(authority_path.read_text())
                if approval.get('input_hash')!=digest(value):raise Blocked('external input authority hash mismatch')
                if args.command=='answer' and (value.get('receipt',{}).get('source')!='cli_owner' or
                        approval.get('receipt')!=value['receipt']):raise Blocked('CLI requires genuine bound cli_owner provenance')
                if args.command=='control' and approval.get('authority_ref')!=value.get('owner_authority_ref'):
                    raise Blocked('control external authority mismatch')
                verifier=lambda incoming:{'input_hash':approval['input_hash'],'scope':approval.get('scope')}
                if args.command=='answer':
                    gate=ledger.question(value['gate_id'])
                    current=json.loads(gate['binding'])
                    if not channel.db.execute('SELECT 1 FROM wf_owner_inputs WHERE input_id=?',(value['input_id'],)).fetchone():
                        expected=channel.db.execute('SELECT binding FROM wf_run_bindings WHERE run_id=?',(args.run,)).fetchone()
                        if not expected:raise Blocked('original configuration binding unavailable')
                        stable=json.loads(expected[0])
                        for key in ('source_hash','approval_hash','config_hash'):current[key]=stable[key]
                        if current['role']!='review':
                            selected=channel.db.execute('SELECT contract FROM wf_tasks WHERE run_id=? AND task_id=?',(args.run,current['task_id'])).fetchone()
                            if not selected:raise Blocked('original task unavailable')
                            current['task_hash']=digest(json.loads(selected[0]))
                    result=ledger.answer(value,verify_owner=verifier,current_binding=current)
                else:
                    target=channel.db.execute('SELECT binding FROM wf_active_targets WHERE run_id=?',(args.run,)).fetchone()
                    if value['target_scope']=='active_session':
                        if not target:raise Blocked('no active worker target')
                        current=json.loads(target[0])
                    else:
                        saved=channel.db.execute('SELECT binding FROM wf_run_bindings WHERE run_id=?',(args.run,)).fetchone()
                        if not saved:raise Blocked('run control binding not published')
                        current=json.loads(saved[0])
                    result=ledger.control(value,verify_owner=verifier,current_binding=current)
                if args.command=='control':
                    channel.close()
                    result=consume_idle_controls(args.project,args.run,result)
                print(canonical(result));return 0
            finally:
                try:channel.close()
                except sqlite3.ProgrammingError:pass
        contract = load_contract(args.tasks)
        if args.command == 'intake':
            print(canonical({'task_ids': [task['id'] for task in contract['tasks']],
                             'status': 'ready' if contract['tasks'] else 'no tasks'})); return 0
        if not contract['tasks']:
            print(canonical({'status': 'no tasks'})); return 0
        if not args.workflow or not args.manifest or not args.containment:
            raise Blocked('remaining graph/host runtime requires --workflow, --manifest and --containment; intake itself needs only --tasks')
        workflow_path=Path(args.workflow)
        if not workflow_path.is_file():raise Blocked('workflow input must be a regular file')
        with workflow_path.open('rb') as source:workflow_bytes=source.read(262145)
        if len(workflow_bytes)>262144:raise Blocked('workflow byte limit')
        try:config=yaml.load(workflow_bytes,Loader=StrictLoader)
        except (yaml.YAMLError,ValueError,RecursionError):raise Blocked('invalid bounded workflow YAML') from None
        validate_schema('workflow.schema.json',config)
        suite_root=Path(args.suite_root).resolve(strict=True) if args.suite_root else ROOT
        if not args.suite_root and not (suite_root/'skills/coordinate-implementation/SKILL.md').is_file():
            raise Blocked('approved suite resource root unavailable; provide --suite-root, no automatic installation')
        manifest = json.loads(Path(args.manifest).read_text())
        environment = {k:v for k,v in os.environ.items() if k in ('PATH','HOME','PYTHONPATH','PYTHONDONTWRITEBYTECODE','TMPDIR','PI_OFFLINE')}
        # Observe the real inventory before Authority/storage/controller startup.
        # Resume must preserve dirty owned bytes for the ORIGINAL authorized
        # recovery/reconciliation below; structural inventory is not their approval.
        if args.command == 'resume':
            recovery_inventory_preflight(args.project, contract['tasks'])
        else:
            inventory_preflight(args.project, contract['tasks'])
        with Authority(args.project) as authority:
            # Engine reserves the run before handler operations can be persisted.
            coordinate = Coordinate(authority,args.run,contract,config,args.containment,manifest,environment)
            if config['interaction']['mode']=='interactive_parent':
                if not args.parent_binding:raise Blocked('interactive launch requires registered actual-parent binding/readiness')
                path=Path(args.parent_binding).resolve(strict=True)
                if path.is_relative_to(authority.project):raise Blocked('parent binding must be outside worker worktree')
                private_file(path)
                from .notifications.paseo import Paseo
                coordinate.parent_transport=Paseo(authority,args.run,json.loads(path.read_text()))
                coordinate.parent_transport.preflight()
            elif args.parent_binding:
                raise Blocked('standalone mode cannot silently adopt a parent transport')
            registry = coordinate.registry()
            load_workflow(registry, workflow_bytes, suite_root)
            maximum=max([config['defaults']['max_repair_attempts'],*[n.get('max_repair_attempts',0) for n in config['nodes']]])
            engine = Engine(authority,args.run,config,registry,suite_root,boundary_hook=coordinate.controls_boundary,max_task_visits=len(contract['tasks'])*(maximum+1)+maximum+1,
                            workflow_source=workflow_bytes, input_identity={'contract':contract,'manifest':manifest,'environment':environment})
            coordinate.publish_run_binding()
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
                    while outcome=='waiting_owner_input' and coordinate.parent_transport is not None:
                        coordinate.parent_transport.deliver_pending()
                        # Only bound accepted input resumes the existing LangGraph
                        # interrupt. This facade never chooses a task/model/session.
                        outcome=engine.invoke()['outcome']
                    if outcome=='accepted':
                        with authority.store.transaction() as db:
                            if db.execute("SELECT 1 FROM wf_owner_inputs i JOIN wf_controls c USING(input_id) WHERE i.run_id=? AND i.stage='received' AND c.action IN ('pause','cancel')",(args.run,)).fetchone():
                                raise Blocked('owner stop received before acceptance; reconcile before release')
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
                    from .projections import publish_observation
                    publish_observation(authority,args.run)
            finally:
                engine.close()
            print(canonical(status(args.project,args.run)))
        return 0
    except (Blocked, OSError, ValueError, ValidationError) as exc:
        reason='schema-invalid input/result at '+ '/'.join(str(part) for part in exc.absolute_path) if isinstance(exc,ValidationError) else str(exc)
        print(canonical({'status':'blocked','reason':reason})); return 2


if __name__ == '__main__':
    sys.exit(main())
