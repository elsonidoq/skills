"""T007 controlled adapter subprocess/SQL/provenance fixtures.

Synthetic official-format parent records are validation fixtures, NOT genuine UI
or launch evidence. ParentRoundtripTests separately exercises the actual parent.
"""
import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import yaml

from coherence_workflow.engine import load_workflow
from coherence_workflow.notifications.paseo import Paseo, ParentEvidence, TRANSPORT, facade
from coherence_workflow.store import Authority, Blocked, canonical, digest
from test_custody import IsolatedCustody
from test_interaction import question
from test_review_repair import coordinate_fixture


def append_entry(path, message):
    lines=[json.loads(line) for line in path.read_text().splitlines()]
    entry={'type':'message','id':'entry-'+str(len(lines)),'parentId':lines[-1].get('id') if len(lines)>1 else None,
           'timestamp':'fixture','message':message}
    with path.open('a') as stream:stream.write(canonical(entry)+'\n')
    return entry['id']


def append_call(path, name, arguments, id):
    return append_entry(path,{'role':'assistant','content':[{'type':'toolCall','id':id,'name':name,'arguments':arguments}]})


def append_result(path, name, id, body, details=None, *, error=False):
    return append_entry(path,{'role':'toolResult','toolCallId':id,'toolName':name,'isError':error,
                             'content':[{'type':'text','text':body}],'details':details})


MOCK_CLI=r'''
import json,sys
from pathlib import Path
state=Path(sys.argv[1]);v=json.loads(state.read_text());args=sys.argv[2:]
def save():state.write_text(json.dumps(v))
def append(message):
 p=Path(v['descriptor']['session_file']);rows=[json.loads(line) for line in p.read_text().splitlines()]
 with p.open('a') as f:f.write(json.dumps({'type':'message','id':'entry-'+str(len(rows)),'parentId':rows[-1].get('id') if len(rows)>1 else None,'message':message})+'\n')
if args==['--version']:print('0.9.2');sys.exit(0)
if args[0]=='inspect':
 if v.get('outages',0):v['outages']-=1;save();sys.exit(75)
 status='running' if v.get('busy',0)>0 else 'idle'
 if v.get('busy',0):v['busy']-=1
 save();d=v['descriptor'];print(json.dumps({'Id':d['recipient_id'],'Provider':'pi','Archived':False,'Cwd':d['parent_cwd'],'Model':d['parent_model'],'Thinking':d['parent_effort'],'Status':status}));sys.exit(0)
if args[0]=='send':
 p=Path(args[args.index('--prompt-file')+1]);payload=json.loads(p.read_text().splitlines()[1]);v['sends']=v.get('sends',0)+1;v['last']=payload;save()
 if payload['kind']=='ready':
  id='ready-'+payload['nonce'];marker='COHERENCE_PARENT_READY:'+payload['nonce']
  append({'role':'assistant','content':[{'type':'toolCall','name':'bash','id':id,'arguments':{'command':payload['command']}}]})
  append({'role':'toolResult','toolName':'bash','toolCallId':id,'isError':False,'content':[{'type':'text','text':marker}]})
 print(json.dumps({'agentId':v['descriptor']['recipient_id'],'status':'sent'}));sys.exit(0)
raise SystemExit(2)
'''


class TransportFixture(IsolatedCustody):
    def setup_parent(self, owner):
        self.coordinate=coordinate_fixture(self.project,owner)
        self.coordinate.publish_run_binding();self.coordinate.select({})
        self.parent_file=self.root/'synthetic-parent.jsonl'
        self.descriptor={'adapter':TRANSPORT,'version':'0.9.2','binding_id':'test-parent','recipient_id':'fixture-parent-agent',
            'runtime_session_id':'fixture-parent-session','session_file':str(self.parent_file),'parent_cwd':str(self.root),
            'parent_model':'fixture-model','parent_effort':'medium','generation':1,'launch_nonce':'fixture-launch-nonce'}
        self.parent_file.write_text(canonical({'type':'session','version':3,'id':'fixture-parent-session','cwd':str(self.root)})+'\n')
        append_entry(self.parent_file,{'role':'system','content':'','toolsAdded':[{'name':'bash'},{'name':'ask_user'}]})
        marker='COHERENCE_LAUNCH_RECEIPT:'+self.descriptor['launch_nonce']
        append_call(self.parent_file,'bash',{'command':'coordinate-implementation start --project '+str(self.project)+' --run run; echo '+marker},'launch')
        append_result(self.parent_file,'bash','launch',marker)
        self.state=self.root/'transport-state.json';self.state.write_text(canonical({'descriptor':self.descriptor,'sends':0}))
        self.script=self.root/'public-cli-fixture.py';self.script.write_text(MOCK_CLI)
        self.driven=False;self.drive_mode='answer'
        self.capability=Paseo(owner,'run',self.descriptor,command=self.command,sleep=self.drive)
        task=self.coordinate.contract['tasks'][0];node=next(n for n in self.coordinate.config['nodes'] if n['id']=='implement')
        facts={**self.coordinate.question_binding(task,node,0,'implement'),'session_id':'original'}
        turn=owner.store.intent('run','fixture-question-turn','sdk-turn',{},
            {k:facts[k] for k in ('task_id','attempt_id','role')} | {'before':{'session_id':'original'}})
        gate=self.coordinate.interaction.request(turn['op_id'],'fixture-question',facts,question(),
            batch=[{'call':'fixture-question','tool':'request_owner_input'}])['gate_id']
        with owner.store.transaction() as db:
            db.execute("UPDATE wf_questions SET stage='pending',pin=? WHERE gate_id=?",(canonical({'snapshot':{'session_file':'original.jsonl'}}),gate))
            db.execute('INSERT INTO wf_question_parks VALUES(?,?,?,?)',(gate,'synthetic-checkpoint','owner-input-implement',turn['op_id']))
            db.execute("INSERT INTO wf_outbox VALUES('fixture-event','run',?,'recorded',NULL)",(gate,))
            db.execute("UPDATE wf_runs SET state='waiting_owner_input' WHERE run_id='run'")
        self.gate=gate
        return self.capability

    def command(self, argv, **kwargs):
        return subprocess.run([sys.executable,str(self.script),str(self.state),*argv[1:]],**kwargs)

    def drive(self, delay):
        state=json.loads(self.state.read_text())
        payload=state.get('last',{})
        if payload.get('kind')!='question' or self.driven:return
        self.driven=True
        event=payload['event_id'];nonce=payload['nonce']
        append_call(self.parent_file,'bash',{'command':payload['received_command']},'received-call')
        receipt=facade(self.project,'run','parent-received',nonce,event,command=self.command)
        append_result(self.parent_file,'bash','received-call',canonical(receipt))
        self.assertTrue(receipt['ask_allowed'])
        args={key:payload[key] for key in ('question','context','options','allowMultiple','allowFreeform','allowComment')}
        append_call(self.parent_file,'ask_user',args,'question-call')
        if self.drive_mode=='invoked_only':return
        answer=payload['options'][0]['title']
        details={'question':payload['question'],'options':payload['options'],'cancelled':False,
                 'response':{'kind':'selection','selections':[answer]}}
        append_result(self.parent_file,'ask_user','question-call','User answered: '+answer,details)
        append_call(self.parent_file,'bash',{'command':payload['answer_command']},'answer-call')
        accepted=facade(self.project,'run','parent-answer',nonce,event,command=self.command)
        append_result(self.parent_file,'bash','answer-call',canonical(accepted))
        self.assertEqual(accepted['stage'],'accepted')


class ParentTransportTests(TransportFixture):
    def test_actual_adapter_subprocess_busy_outage_reconnect_and_ordered_answer_dedup(self):
        with Authority(self.project) as owner:
            capability=self.setup_parent(owner)
            state=json.loads(self.state.read_text());state.update(outages=1,busy=4);self.state.write_text(canonical(state))
            with self.assertRaisesRegex(Blocked,'unavailable'):capability.preflight(timeout=2)
            capability.preflight(timeout=5)
            self.assertTrue(capability.deliver_pending(timeout=5))
            rows=[dict(r) for r in owner.store.db.execute("SELECT seq,kind,payload FROM wf_events WHERE kind IN ('parent_transport_queued','parent_received','parent_question_tool_invoked','owner_answer_accepted') ORDER BY seq")]
            self.assertEqual([r['kind'] for r in rows],['parent_transport_queued','parent_received','parent_question_tool_invoked','owner_answer_accepted'])
            sends=json.loads(self.state.read_text())['sends']
            self.assertTrue(capability.deliver_pending(timeout=.1))
            self.assertEqual(json.loads(self.state.read_text())['sends'],sends)
            self.assertEqual(owner.store.db.execute('SELECT COUNT(*) FROM wf_owner_inputs').fetchone()[0],1)
            outcomes=[r[0] for r in owner.store.db.execute('SELECT outcome FROM wf_parent_attempts')]
            self.assertIn('busy',outcomes)
            self.assertEqual(owner.store.db.execute('SELECT COUNT(*) FROM wf_processes').fetchone()[0],0)
            print(canonical({'item':'T007/V2','proof':'controlled actual adapter subprocess/SQL; synthetic parent records, NOT genuine UI',
                             'stages':rows,'outcomes':outcomes,'duplicate_sends':0}))

    def test_parent_answer_before_send_receipt_reconciles_stages_without_regression(self):
        with Authority(self.project) as owner:
            capability=self.setup_parent(owner);capability.preflight(timeout=5)
            original=self.command
            def response_before_ack(argv,**kwargs):
                result=original(argv,**kwargs)
                if len(argv)>1 and argv[1]=='send':self.drive(0)
                return result
            capability.command=response_before_ack
            self.assertTrue(capability.deliver_pending(timeout=5))
            events=[dict(r) for r in owner.store.db.execute("SELECT kind,payload FROM wf_events WHERE kind IN ('parent_transport_queued','parent_received','parent_question_tool_invoked','owner_answer_accepted') ORDER BY seq")]
            self.assertEqual([e['kind'] for e in events],['parent_transport_queued','parent_received','parent_question_tool_invoked','owner_answer_accepted'])
            self.assertIn('reconciled_from_actual_parent_received',json.loads(events[0]['payload'])['receipt'])
            self.assertEqual(owner.store.db.execute('SELECT stage FROM wf_outbox').fetchone()[0],'answered')
            self.assertEqual(owner.store.db.execute('SELECT COUNT(*) FROM wf_owner_inputs').fetchone()[0],1)

    def test_invocation_crash_claim_blocks_blind_reask_and_stale_nonce(self):
        with Authority(self.project) as owner:
            capability=self.setup_parent(owner);capability.preflight(timeout=5)
            self.drive_mode='invoked_only'
            with self.assertRaisesRegex(Blocked,'no blind reask'):capability.deliver_pending(timeout=.2)
            row=owner.store.db.execute('SELECT nonce FROM wf_questions').fetchone()
            duplicate=facade(self.project,'run','parent-received',row[0],'fixture-event',command=self.command)
            self.assertFalse(duplicate['ask_allowed'])
            with self.assertRaisesRegex(Blocked,'wrong/stale'):facade(self.project,'run','parent-received','stale','fixture-event',command=self.command)
            self.assertEqual(owner.store.db.execute('SELECT COUNT(*) FROM wf_owner_inputs').fetchone()[0],0)
            observed=ParentEvidence(self.descriptor).calls('ask_user',lambda unused:True)
            self.assertIsNotNone(observed)
            self.assertIsNone(observed['result'])
            self.assertEqual(owner.store.db.execute('SELECT stage FROM wf_outbox').fetchone()[0],'question_tool_invoked')
            sends=json.loads(self.state.read_text())['sends']
            with self.assertRaisesRegex(Blocked,'no blind reask'):capability.deliver_pending(timeout=.1)
            self.assertEqual(json.loads(self.state.read_text())['sends'],sends)

    def test_forged_wrong_parent_generation_worker_file_partial_tail_and_missing_tool_block(self):
        with Authority(self.project) as owner:
            capability=self.setup_parent(owner)
            invalid={**self.descriptor,'session_file':str(self.project/'worker-written.jsonl')}
            self.project.joinpath('worker-written.jsonl').write_text(self.parent_file.read_text())
            with self.assertRaisesRegex(Blocked,'worker-written'):Paseo(owner,'run',invalid,command=self.command)
            invalid={**self.descriptor,'approved':True}
            with self.assertRaisesRegex(Blocked,'closed registered'):Paseo(owner,'run',invalid,command=self.command)
            invalid={**self.descriptor,'runtime_session_id':'wrong'}
            with self.assertRaisesRegex(Blocked,'session/header'):ParentEvidence(invalid)
            before=self.parent_file.read_text()
            with self.parent_file.open('a') as f:f.write('{"partial":')
            with self.assertRaisesRegex(Blocked,'partial tail'):ParentEvidence(self.descriptor)
            self.parent_file.write_text(before)
            append_entry(self.parent_file,{'role':'system','content':'','toolsRemoved':[{'name':'ask_user'}]})
            with self.assertRaisesRegex(Blocked,'capability unavailable'):ParentEvidence(self.descriptor)
            self.parent_file.write_text(before)
            capability.preflight(timeout=5)
            changed=Paseo(owner,'run',{**self.descriptor,'generation':2},command=self.command)
            with self.assertRaisesRegex(Blocked,'descriptor/provenance drift'):changed.preflight(timeout=5)


class FacadeAuthorityTests(TransportFixture):
    def test_worker_question_cannot_select_recipient_store_approval_or_ask_user(self):
        from coherence_workflow.interaction import validate_question
        for field in ('recipient_id','store','approval','ask_user'):
            value={**question(),field:'worker-selected'}
            with self.subTest(field=field),self.assertRaises(Exception):validate_question(value)

    def test_unavailable_unpreflighted_and_valid_registered_interactive_capability(self):
        with Authority(self.project) as owner:
            capability=self.setup_parent(owner)
            config=copy.deepcopy(self.coordinate.config)
            config['interaction']={'mode':'interactive_parent','question_transport':TRANSPORT,'parent_binding_ref':'test-parent','question_tool':'ask_user'}
            registry=self.coordinate.registry()
            with self.assertRaisesRegex(Blocked,'interactive capability unavailable'):load_workflow(registry,yaml.safe_dump(config),Path(__file__).resolve().parents[2])
            registry.question_transports[TRANSPORT]=capability
            with self.assertRaisesRegex(Blocked,'actually preflighted'):load_workflow(registry,yaml.safe_dump(config),Path(__file__).resolve().parents[2])
            capability.preflight(timeout=5)
            load_workflow(registry,yaml.safe_dump(config),Path(__file__).resolve().parents[2])
            self.assertEqual(owner.store.db.execute('SELECT COUNT(*) FROM wf_processes').fetchone()[0],0)

    def test_optional_notification_failure_cannot_release_gate_or_change_graph_and_status_needs_no_paseo(self):
        with Authority(self.project) as owner:
            capability=self.setup_parent(owner);capability.preflight(timeout=5)
            state=json.loads(self.state.read_text());state['outages']=10;self.state.write_text(canonical(state))
            before=dict(owner.store.db.execute('SELECT * FROM wf_runs').fetchone())
            self.assertFalse(capability.optional_status({'status':'waiting_owner_input'}))
            self.assertEqual(dict(owner.store.db.execute('SELECT * FROM wf_runs').fetchone()),before)
            self.assertEqual(owner.store.db.execute('SELECT stage FROM wf_questions').fetchone()[0],'pending')
        env={**os.environ,'PATH':'/unavailable','PYTHONDONTWRITEBYTECODE':'1'}
        result=subprocess.run([sys.executable,'-m','coherence_workflow.cli','status','--project',str(self.project),'--run','run'],env=env,capture_output=True,text=True,timeout=20)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        self.assertFalse(json.loads(result.stdout)['accepted'])
        self.assertTrue(json.loads(result.stdout)['questions'])


class FacadeResourceTests(unittest.TestCase):
    """R003 callbacks bind actual interpreter/package, not parent cwd/PYTHONPATH."""
    def exercise(self, command, root):
        import shlex
        project=root/'foreign-project';project.mkdir()
        conflict=root/'caller-path';conflict.mkdir()
        marker=root/'shadow-executed'
        for directory in (project,conflict):
            package=directory/'coherence_workflow';package.mkdir()
            (package/'__init__.py').write_text('from pathlib import Path\nPath('+repr(str(marker))+').write_text("shadow")\nraise RuntimeError("SHADOW_RUNTIME")\n')
        for value in (None,str(conflict)):
            env=dict(os.environ);env.pop('PYTHONPATH',None)
            if value:env['PYTHONPATH']=value
            result=subprocess.run(shlex.split(command.split(' # ')[0]),cwd=project,env=env,
                capture_output=True,text=True,timeout=20)
            self.assertEqual(result.returncode,2,result.stdout+result.stderr)
            self.assertEqual(json.loads(result.stdout),{'status':'blocked','reason':'parent channel project must be canonical'})
            self.assertNotIn('ModuleNotFoundError',result.stderr)
            self.assertNotIn('SHADOW_RUNTIME',result.stdout+result.stderr)
            self.assertFalse(marker.exists(),'foreign cwd/environment shadowed approved runtime')
        print('actual facade isolated interpreter/package; unset/conflicting PYTHONPATH and local shadow rejected')

    def test_source_callback_does_not_depend_on_parent_import_environment(self):
        from types import SimpleNamespace
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);target=root/'project-target';target.mkdir()
            project=root/'unregistered-project';project.symlink_to(target,target_is_directory=True)
            capability=SimpleNamespace(authority=SimpleNamespace(project=project),run='unregistered')
            command=Paseo.facade_command(capability,'parent-ready','no-gate')
            self.exercise(command,root)

    def test_wheel_callback_binds_its_actual_installed_package_and_interpreter(self):
        from test_installation import PortableInstallationTests
        PortableInstallationTests.setUpClass()
        try:
            fixture=PortableInstallationTests
            target=fixture.root/'project-target';target.mkdir()
            project=fixture.root/'unregistered-project';project.symlink_to(target,target_is_directory=True)
            code='''from types import SimpleNamespace
from pathlib import Path
from coherence_workflow.notifications.paseo import Paseo
capability=SimpleNamespace(authority=SimpleNamespace(project=Path(__import__('sys').argv[1])),run='unregistered')
print(Paseo.facade_command(capability,'parent-ready','no-gate'))
'''
            generated=subprocess.run([sys.executable,'-c',code,str(project)],env=fixture.env,cwd=fixture.foreign,
                capture_output=True,text=True,timeout=20)
            self.assertEqual(generated.returncode,0,generated.stdout+generated.stderr)
            self.assertIn(str(fixture.installed),generated.stdout,'callback did not bind wheel package root')
            self.exercise(generated.stdout.strip(),fixture.root)
        finally:PortableInstallationTests.doClassCleanups()
