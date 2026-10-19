"""T006 question boundaries. Live tests exercise shipped SDK/custody, not PoCs."""
import copy
import hashlib
import json
import os
from pathlib import Path
import time
import unittest

from coherence_workflow.interaction import Interaction, QUESTION_SCHEMA, validate_question
from coherence_workflow.pi_adapter import PiAdapter
from coherence_workflow.store import Authority, Blocked, canonical, digest
from test_custody import IsolatedCustody
from test_pi_adapter import manifest, environment


def question():
    return {'category': 'product_priority', 'question': 'Which already-approved product outcome has priority?',
            'why_owner_needed': 'The two outcomes conflict; no technical evidence establishes the owner priority.',
            'options': ['Preserve compatibility', 'Prefer new behavior'], 'recommendation': 'Preserve compatibility',
            'impact': {'scope': 'No scope increase', 'complexity': 'Either option is implementable',
                       'time': 'Similar effort', 'cost': 'No separately chargeable action'}}


def binding(session='original'):
    return dict(run_id='run', task_id='task', node_id='implement', attempt_id='task:0', session_id=session,
                role='implement', source_hash=digest('sources'), task_hash=digest('task'),
                approval_hash=digest('approval'), config_hash=digest('config'))


def question_manifest(project):
    config = manifest(project, tools=False)
    resource = Path(config['skills'][0]['path'])
    resource.write_text('---\nname: bounded-proof\ndescription: Isolated owner question integration.\n---\n'
                        'Follow the explicit test prompt. Use only request_owner_input when explicitly required. '
                        'Never ask about routine technical work or approved tests. After an answer, reply ANSWER_RECEIVED.\n')
    config['skills'][0]['sha256'] = hashlib.sha256(resource.read_bytes()).hexdigest()
    config['tools'] = [dict(name='request_owner_input', version='1', description='Only necessary owner product/priority or unexpected material-impact questions. Complete normally, then park.',
                           parameters=QUESTION_SCHEMA, permission='request_owner_input')]
    config['permissions'] = ['request_owner_input']
    config['resource_hash'] = digest({k: config[k] for k in ('skills', 'tools', 'permissions', 'trust', 'system_prompt')})
    return config


def seeded_pending(owner):
    """SQL-only fixture state, not evidence of SDK settlement or graph parking."""
    owner.store.reserve('run',digest('fixture'))
    ledger=Interaction(owner.store,'run')
    facts=binding()
    operation=owner.store.intent('run','turn','sdk-turn',{}, {k:facts[k] for k in ('task_id','attempt_id','role')} | {'before':{'session_id':'original'}})
    gate=ledger.request(operation['op_id'],'q',facts,question(),batch=[{'call':'q','tool':'request_owner_input'}])['gate_id']
    with owner.store.transaction() as db:
        db.execute("UPDATE wf_questions SET stage='pending',pin=? WHERE gate_id=?",(canonical({'snapshot':{'session_file':'original.jsonl','session_id':'original'}}),gate))
        db.execute("UPDATE wf_runs SET state='waiting_owner_input' WHERE run_id='run'")
        db.execute("INSERT INTO wf_outbox VALUES('event','run',?,'recorded',NULL)",(gate,))
        db.execute('INSERT INTO wf_question_parks VALUES(?,?,?,?)',(gate,'synthetic-checkpoint','synthetic-owner-gate',operation['op_id']))
    record=ledger.question(gate)
    value={'schema_version':1,'kind':'owner_answer','binding':facts,'input_id':'answer-id','gate_id':gate,'nonce':record['nonce'],
           'pin_policy':'original_only','answer':'Preserve compatibility','receipt':{'source':'cli_owner','actor':'standing isolated-test owner authority',
           'record_ref':'test-authority','record_sha256':digest('preapproved isolated tests'),'authority_ref':'test-owner'},
           'delivery':'accepted','original_session_ref':'original.jsonl','delivery_ref':None}
    return ledger,value


def retain_current_failure(case, result, inputs):
    """Private current-task diagnostics only; never append to historical T005 proof."""
    import sqlite3
    import uuid
    import shutil
    root=Path(__file__).resolve().parents[2]
    target=root/'.pi/workflow-validation/implementation/t006'/('failure-'+uuid.uuid4().hex)
    target.mkdir(mode=0o700)
    database=case.project/'.coherence/workflow/workflow.sqlite'
    if database.is_file():
        source=sqlite3.connect(database.as_uri()+'?mode=ro',uri=True)
        destination=sqlite3.connect(target/'workflow.sqlite')
        try:
            source.backup(destination)
            diagnostics=[{'kind':r[0],'payload':json.loads(r[1])} for r in source.execute("SELECT kind,payload FROM wf_events WHERE kind IN ('workflow_blocked','sdk_failure_diagnostic') ORDER BY seq")]
        finally:source.close();destination.close()
        (target/'workflow.sqlite').chmod(0o600)
        sessions=case.project/'.coherence/workflow/sdk/sessions'
        if sessions.is_dir():shutil.copytree(sessions,target/'conversations',symlinks=True)
        metadata={'purpose':'current test diagnostic only; conversations are private and copied bindings are NOT resumable authority',
                  'exit_code':result.returncode,'stdout_hash':digest(result.stdout),'stderr_hash':digest(result.stderr),
                  'diagnostics':diagnostics,'source_hashes':{str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest()
                       for p in (root/'runtime/coherence_workflow/cli.py',root/'runtime/coherence_workflow/engine.py',root/'runtime/coherence_workflow/pi_adapter.py',root/'runtime/pi-host/host.mjs')}}
        (target/'metadata.json').write_text(canonical(metadata))
        (target/'metadata.json').chmod(0o600)
    print(canonical({'retained_failure_database':str(target),'exit_code':result.returncode,
                     'input_hashes':{k:hashlib.sha256(Path(p).read_bytes()).hexdigest() for k,p in inputs.items()},
                     'purpose':'current isolated diagnostic only; not resumable copied authority'}))
    return target


def crash_start(argv):
    """Trusted isolated fault seam: exit after app result, before graph saver."""
    from coherence_workflow import cli
    original=cli.Engine
    holder=[]
    def stop(phase, operation):
        if phase=='application_result' and holder[0].store.operation(operation)['node_id']=='implement:0':
            os._exit(73)
    def engine(*args,**kwargs):
        result=original(*args,**kwargs,phase_hook=stop);holder.append(result);return result
    cli.Engine=engine
    raise SystemExit(cli.main(argv))


def standing_authority(value):
    return {'input_hash':digest(value),'scope':'within_envelope'}


class QuestionParkTests(IsolatedCustody):
    def test_live_normal_terminating_question_settles_before_pending(self):
        self.assertEqual(os.environ.get('COHERENCE_LIVE'), '1', 'NOT VERIFIED: actual SDK test not enabled')
        with Authority(self.project) as owner:
            gateway = self.gateway(owner)
            interaction = Interaction(owner.store, 'run')
            adapter = PiAdapter(gateway, question_manifest(self.project), node='question-host', environment=environment(),
                                session_context=dict(role='implement', affinity='story', review_lineage=None),
                                interaction=interaction, question_binding=binding())
            try:
                turn = adapter.prompt(node='question-turn', task_id='task', attempt_id='task:0', role='implement',
                    text='An isolated test-only product priority question is required. Invoke request_owner_input exactly once with this exact JSON, as the ONLY tool in its batch: '+canonical(question()),
                    skill='bounded-proof', contract_hash=digest('task'), selection={'reason':'fresh'})
                self.assertTrue(turn['question_gate'])
                self.assertEqual(interaction.question(turn['question_gate'])['stage'], 'parking')
                self.assertFalse(adapter.pending or adapter.tool_queue)
                self.assertFalse(adapter.lifecycle.active)
                self.assertTrue(adapter.lifecycle.settled)
            finally:
                adapter.close(force=adapter.lifecycle.poisoned)
                self.receipts.extend(json.loads(r[0]) for r in owner.store.db.execute('SELECT containment FROM wf_processes WHERE containment IS NOT NULL'))
            pin = {'host_op': adapter.host_op, 'snapshot': turn['snapshot']}
            proof = {'turn_op': turn['segment']['operation_id'] if 'operation_id' in turn['segment'] else interaction.question(turn['question_gate'])['turn_op'],
                     'snapshot_hash': digest(turn['snapshot'])}
            interaction.settled(turn['question_gate'], pin=pin, proof=proof)
            self.assertEqual(interaction.question(turn['question_gate'])['stage'], 'pending')
            self.assertEqual(owner.store.db.execute('SELECT COUNT(*) FROM wf_outbox').fetchone()[0], 1)
            self.assertEqual(owner.store.db.execute('SELECT state FROM wf_runs').fetchone()[0], 'waiting_owner_input')
            events=[(r['seq'],r['kind']) for r in owner.store.db.execute('SELECT seq,kind FROM wf_events ORDER BY seq')]
            print(canonical({'item':'T006/V1','scope':'actual SDK/SQL/cgroup; graph integration not covered here',
                             'events':events,'original_session':adapter.session_id,'pending':turn['question_gate']}))

    def test_host_guard_rejects_both_sides_of_mixed_batch_before_proxy(self):
        import subprocess
        root=Path(__file__).resolve().parents[2]
        source=r'''
import assert from 'node:assert/strict';
import {admitQuestionBatch} from './runtime/pi-host/host.mjs';
const mixed=[{call:'q',tool:'request_owner_input'},{call:'w',tool:'write_file'}];
for(const tool of mixed)assert.throws(()=>admitQuestionBatch(tool.tool,tool.call,mixed),/exclusive terminating batch/);
assert.throws(()=>admitQuestionBatch('request_owner_input','q',null),/exclusive/);
admitQuestionBatch('request_owner_input','q',[mixed[0]]);
admitQuestionBatch('read_file','r',[{call:'r',tool:'read_file'}]);
console.log('5 actual shipped host batch-guard assertions; no SDK/provider/proxy send');
'''
        result=subprocess.run(['node','--input-type=module','-e',source],cwd=root,capture_output=True,text=True,timeout=20)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        self.assertIn('5 actual shipped',result.stdout)

    def test_request_transaction_crash_retains_one_parking_gate_without_outbox_or_reask(self):
        import subprocess
        import sys
        source='''
import os,sys
from coherence_workflow.store import Authority,digest
from coherence_workflow.interaction import Interaction
from test_interaction import binding,question
with Authority(sys.argv[1]) as owner:
 owner.store.reserve('run',digest('crash-question'))
 ledger=Interaction(owner.store,'run');facts=binding()
 op=owner.store.intent('run','turn','sdk-turn',{}, {k:facts[k] for k in ('task_id','attempt_id','role')} | {'before':{'session_id':'original'}})
 ledger.request(op['op_id'],'crash-q',facts,question(),batch=[{'call':'crash-q','tool':'request_owner_input'}])
 os._exit(71)
'''
        result=subprocess.run([sys.executable,'-c',source,str(self.project)],capture_output=True,text=True,timeout=20)
        self.assertEqual(result.returncode,71,result.stdout+result.stderr)
        with Authority(self.project) as owner:
            ledger=Interaction(owner.store,'run')
            before=ledger.pending()
            op=owner.store.db.execute("SELECT op_id FROM wf_operations WHERE kind='sdk-turn'").fetchone()[0]
            retried=ledger.request(op,'crash-q',binding(),question(),batch=[{'call':'crash-q','tool':'request_owner_input'}])
            self.assertEqual(retried['gate_id'],before[0]['gate_id'])
            self.assertEqual(ledger.pending(),before)
            self.assertEqual(owner.store.db.execute('SELECT COUNT(*) FROM wf_outbox').fetchone()[0],0)
            self.assertEqual(owner.store.db.execute('SELECT COUNT(*) FROM wf_processes').fetchone()[0],0)
            self.assertEqual(owner.store.db.execute('PRAGMA integrity_check').fetchone()[0],'ok')

    def test_mixed_and_unknown_batch_cannot_create_a_gate(self):
        with Authority(self.project) as owner:
            self.gateway(owner)
            ledger=Interaction(owner.store,'run')
            op=owner.store.intent('run','turn','sdk-turn',{}, {})['op_id']
            for batch in (None, [], [{'call':'q','tool':'request_owner_input'},{'call':'w','tool':'write_file'}]):
                with self.assertRaisesRegex(Blocked,'exclusive'):
                    ledger.request(op,'q',binding(),question(),batch=batch)
            self.assertFalse(ledger.pending())

    def test_pending_cannot_precede_current_settlement(self):
        with Authority(self.project) as owner:
            self.gateway(owner)
            ledger=Interaction(owner.store,'run')
            facts=binding()
            op=owner.store.intent('run','turn','sdk-turn',{}, {k:facts[k] for k in ('task_id','attempt_id','role')} | {'before':{'session_id':'original'}})['op_id']
            gate=ledger.request(op,'q',binding(),question(),batch=[{'call':'q','tool':'request_owner_input'}])['gate_id']
            with self.assertRaisesRegex(Blocked,'durably settled'):
                ledger.settled(gate,pin={},proof={})
            self.assertEqual(ledger.question(gate)['stage'],'parking')
            self.assertEqual(owner.store.db.execute('SELECT COUNT(*) FROM wf_outbox').fetchone()[0],0)


class OriginalAnswerTests(IsolatedCustody):
    def test_shipped_cli_graph_park_and_new_host_original_answer_before_request(self):
        import subprocess
        import sys
        import sqlite3
        import yaml
        from coherence_workflow.cli import ROOT
        from coherence_workflow.intake import approval_scope
        from test_intake import approved_fixture
        self.assertEqual(os.environ.get('COHERENCE_LIVE'),'1','NOT VERIFIED: live CLI/SDK test not enabled')
        config=yaml.safe_load((ROOT/'runtime/coherence_workflow/workflows/coordinate.yaml').read_text())
        contract,catalog=approved_fixture(self.project,digest(config))
        contract['tasks']=contract['tasks'][:1]
        contract['tasks'][0]['outcome']=(
            'This is a mandatory isolated interaction test, not a normal cosmetic policy. BEFORE any file mutation, '
            'request_owner_input exactly once, using it as the ONLY tool in its batch, with this exact request: '+canonical(question())+
            '. Only after the bound answer is in your original conversation, read owned.txt and write exactly first\\n '
            '(the six bytes f i r s t newline). Never reask the same question after seeing bound_owner_answer. '
            'The selected test answer is Preserve compatibility; if owner instead chooses Prefer new behavior, stop blocked.')
        contract['authorization_envelope']['profiles']=[config['profiles']['sol-medium']]
        for ref in contract['approval_refs']:
            if ref['gate_kind']=='implementation':
                ref['scope_hash']=approval_scope(contract,digest(config));catalog[ref['authority_ref']]['scope_hash']=ref['scope_hash']
        (self.project/'.coherence/workflow').mkdir(parents=True,mode=0o700,exist_ok=True)
        sdk=manifest(self.project,tools=False)
        sdk['skills']=[{'path':str(ROOT/'skills/coordinate-implementation/SKILL.md'),'sha256':config['skills']['coordinate']['sha256'],'name':'coordinate-implementation'}]
        sdk['resource_hash']=digest({k:sdk[k] for k in ('skills','tools','permissions','trust','system_prompt')})
        paths={n:self.root/n for n in ('workflow.yaml','tasks.json','catalog.json','manifest.json')}
        paths['workflow.yaml'].write_text(yaml.safe_dump(config));paths['tasks.json'].write_text(canonical(contract))
        paths['catalog.json'].write_text(canonical(catalog));paths['catalog.json'].chmod(0o600)
        paths['manifest.json'].write_text(canonical(sdk))
        argv=[str(ROOT/'scripts/coordinate-implementation'),'start','--project',str(self.project),'--run','roundtrip',
              '--workflow',str(paths['workflow.yaml']),'--tasks',str(paths['tasks.json']),
              '--owner-catalog',str(paths['catalog.json']),'--manifest',str(paths['manifest.json']),'--containment',self.parent]
        env=dict(os.environ,COHERENCE_PYTHON=sys.executable)
        def receipts():
            db=sqlite3.connect(self.project/'.coherence/workflow/workflow.sqlite');db.row_factory=sqlite3.Row
            if db.execute("SELECT 1 FROM sqlite_master WHERE name='wf_processes'").fetchone():
                for r in db.execute('SELECT containment FROM wf_processes WHERE containment IS NOT NULL'):
                    receipt=json.loads(r[0])
                    if receipt not in self.receipts:self.receipts.append(receipt)
            return db
        fault_argv=[sys.executable,'-c','import json,sys; from test_interaction import crash_start; crash_start(json.loads(sys.argv[1]))',canonical(argv[1:])]
        # Match the shipped shell launcher's process-local PYTHONPATH exactly;
        # otherwise immutable environment admission correctly blocks reentry.
        fault_env={**env,'PYTHONPATH':str(ROOT/'runtime')+(':'+env['PYTHONPATH'] if env.get('PYTHONPATH') else '')}
        crashed=subprocess.run(fault_argv,env=fault_env,capture_output=True,text=True,timeout=120)
        print('actual isolated app-before-saver exit',crashed.returncode,crashed.stdout,crashed.stderr)
        db=receipts()
        try:
            self.assertEqual(crashed.returncode,73,crashed.stdout+crashed.stderr)
            self.assertEqual(db.execute('SELECT COUNT(*) FROM wf_question_parks').fetchone()[0],0)
            recovery=self.root/'resume-authority.json'
            def authorize_resume():
                recovery.write_text(canonical({'action':'reconcile','run_id':'roundtrip',
                    'config_hash':db.execute('SELECT config_hash FROM wf_runs').fetchone()[0],
                    'operations':[r[0] for r in db.execute("SELECT op_id FROM wf_operations WHERE phase!='completed' ORDER BY op_id")],
                    'actor':'current owner standing isolated-test authority','provenance':'mandatory isolated test-only crash recovery preapproved'}))
                recovery.chmod(0o600)
            authorize_resume()
            resume_argv=[argv[0],'resume',*argv[2:],'--resume-authority',str(recovery)]
            started=subprocess.run(resume_argv,env=env,capture_output=True,text=True,timeout=120)
            print('actual reconcile/park',started.returncode,started.stdout[:300],started.stderr)
            self.assertEqual(started.returncode,0,started.stdout+started.stderr)
            self.assertEqual(db.execute('SELECT COUNT(*) FROM wf_question_parks').fetchone()[0],1)
            self.assertEqual(db.execute("SELECT COUNT(*) FROM wf_operations WHERE kind='sdk-turn'").fetchone()[0],1,'crash reconciliation reasked original worker')
            parked=json.loads(started.stdout)
            self.assertEqual(parked['state'],'waiting_owner_input')
            gate=dict(db.execute('SELECT * FROM wf_questions').fetchone())
            pin=json.loads(gate['pin']);bound=json.loads(gate['binding'])
            self.assertEqual(gate['stage'],'pending')
            self.assertEqual(self.project.joinpath('owned.txt').read_text(),'base')
            self.assertEqual(db.execute("SELECT COUNT(*) FROM wf_operations WHERE kind='sdk-turn'").fetchone()[0],1)
            # Separate no-agent pending command remains portable.
            pending=subprocess.run([str(ROOT/'scripts/coordinate-implementation'),'pending','--project',str(self.project),'--run','roundtrip'],env=env,capture_output=True,text=True,timeout=20)
            self.assertEqual(pending.returncode,0,pending.stdout+pending.stderr)
            self.assertEqual(len(json.loads(pending.stdout)['questions']),1)
            value={'schema_version':1,'kind':'owner_answer','binding':bound,'input_id':'preapproved-standalone-answer',
                'gate_id':gate['gate_id'],'nonce':gate['nonce'],'pin_policy':'original_only','answer':'Preserve compatibility',
                'receipt':{'source':'cli_owner','actor':'current owner standing isolated-test authority',
                    'record_ref':'standing-test-authority','record_sha256':digest('current owner explicitly preapproved isolated tests'),
                    'authority_ref':'isolated-test-owner'},'delivery':'accepted','original_session_ref':pin['snapshot']['session_file'],'delivery_ref':None}
            answer=self.root/'answer.json';answer.write_text(canonical(value))
            auth=self.root/'answer-authority.json';auth.write_text(canonical({'input_hash':digest(value),'scope':'within_envelope','receipt':value['receipt']}));auth.chmod(0o600)
            answer_argv=[str(ROOT/'scripts/coordinate-implementation'),'answer','--project',str(self.project),'--run','roundtrip','--input',str(answer),'--input-authority',str(auth)]
            accepted=subprocess.run(answer_argv,env=env,capture_output=True,text=True,timeout=20)
            self.assertEqual(accepted.returncode,0,accepted.stdout+accepted.stderr)
            duplicate=subprocess.run(answer_argv,env=env,capture_output=True,text=True,timeout=20)
            self.assertEqual(duplicate.returncode,0,duplicate.stdout+duplicate.stderr)
            self.assertEqual(json.loads(accepted.stdout),json.loads(duplicate.stdout))
            self.assertEqual(db.execute("SELECT COUNT(*) FROM wf_operations WHERE kind='sdk-turn'").fetchone()[0],1,'answer acceptance dispatched a worker')
            authorize_resume()
            resumed=subprocess.run(resume_argv,env=env,capture_output=True,text=True,timeout=180)
            print('actual resume',resumed.returncode,resumed.stdout,resumed.stderr)
            receipts().close()
            self.assertEqual(resumed.returncode,0,resumed.stdout+resumed.stderr)
            turns=[json.loads(r[0]) for r in db.execute("SELECT result FROM wf_operations WHERE kind='sdk-turn' ORDER BY rowid")]
            self.assertEqual(turns[0]['after']['session_id'],turns[1]['before']['session_id'])
            self.assertNotEqual(turns[0]['host_op'],turns[1]['host_op'])
            self.assertEqual(turns[1]['selection']['reason'],'original_question_pin')
            original=Path(pin['snapshot']['session_file'])
            entries=[json.loads(line) for line in original.read_text().splitlines()]
            answers=[r for r in entries if r.get('type')=='message' and r['message']['role']=='user' and value['input_id'] in canonical(r['message']['content'])]
            self.assertEqual(len(answers),1)
            order=[(r['seq'],r['kind']) for r in db.execute('SELECT seq,kind FROM wf_events ORDER BY seq')]
            delivered=next(seq for seq,kind in order if kind=='original_answer_entry')
            observations=[r['seq'] for r in db.execute("SELECT seq,payload FROM wf_events WHERE kind LIKE 'sdk:%'") if json.loads(r['payload']).get('wire_effort') and r['seq']>delivered]
            self.assertTrue(observations)
            self.assertEqual(db.execute('SELECT COUNT(*) FROM wf_owner_inputs').fetchone()[0],1)
            self.assertEqual(db.execute('SELECT COUNT(*) FROM wf_questions').fetchone()[0],1,'original ask node reexecuted')
            self.assertEqual(self.project.joinpath('owned.txt').read_text(),'first\n')
            print(canonical({'items':['T006/V1','T006/V2'],'original_session':bound['session_id'],'answer_entry':answers[0]['id'],
                             'answer_before_request':delivered<min(observations),'event_order':order,
                             'isolated_crash_exit':crashed.returncode,'graph_reconcile_exit':started.returncode,'cli_answer_exit':accepted.returncode,'cli_resume_exit':resumed.returncode,
                             'provenance_limit':'standalone input uses genuine standing isolated-test authority; NOT an ask_user tool receipt'}))
        except BaseException:
            import uuid
            target=ROOT/'.pi/workflow-validation/implementation/t006'/('failure-'+uuid.uuid4().hex)
            target.mkdir(mode=0o700)
            destination=sqlite3.connect(target/'workflow.sqlite')
            try:db.backup(destination)
            finally:destination.close()
            (target/'workflow.sqlite').chmod(0o600)
            print(canonical({'retained_failure_database':str(target/'workflow.sqlite'),'purpose':'isolated diagnostic only; no copied binding/resume authority'}))
            raise
        finally:db.close()

    def test_bound_inputs_reject_wrong_identity_authority_nonce_and_conflicting_duplicate(self):
        with Authority(self.project) as owner:
            ledger,value=seeded_pending(owner)
            for field in value['binding']:
                invalid=copy.deepcopy(value)
                invalid['binding'][field]='wrong' if not field.endswith('_hash') else digest('wrong')
                if field=='role':invalid['binding'][field]='repair'
                with self.subTest(field=field),self.assertRaises(Exception):
                    ledger.answer(invalid,verify_owner=standing_authority,current_binding=value['binding'])
            for field in ('nonce','original_session_ref'):
                invalid=copy.deepcopy(value);invalid[field]='wrong'
                with self.subTest(field=field),self.assertRaises(Blocked):
                    ledger.answer(invalid,verify_owner=standing_authority,current_binding=value['binding'])
            with self.assertRaisesRegex(Blocked,'unverified'):
                ledger.answer(value,verify_owner=lambda unused:None,current_binding=value['binding'])
            old=ledger.answer(value,verify_owner=standing_authority,current_binding=value['binding'])
            self.assertEqual(old,ledger.answer(value,verify_owner=standing_authority,current_binding=value['binding']))
            invalid={**value,'answer':'conflicting answer'}
            with self.assertRaisesRegex(Blocked,'conflicting duplicate'):
                ledger.answer(invalid,verify_owner=standing_authority,current_binding=value['binding'])
            self.assertEqual(owner.store.db.execute('SELECT COUNT(*) FROM wf_owner_inputs').fetchone()[0],1)

    def test_concurrent_identical_sql_inputs_have_one_acceptance_and_no_dispatch(self):
        from concurrent.futures import ThreadPoolExecutor
        from coherence_workflow.interaction import OwnerChannel
        with Authority(self.project) as owner:
            ledger,value=seeded_pending(owner)
            def submit():
                channel=OwnerChannel(self.project,'run')
                try:return Interaction(channel,'run',initialize=False).answer(value,verify_owner=standing_authority,current_binding=value['binding'])
                finally:channel.close()
            with ThreadPoolExecutor(max_workers=2) as pool:
                results=list(pool.map(lambda unused:submit(),range(2)))
            self.assertEqual(results[0],results[1])
            self.assertEqual(owner.store.db.execute("SELECT COUNT(*) FROM wf_events WHERE kind='owner_answer_accepted'").fetchone()[0],1)
            self.assertEqual(owner.store.db.execute('SELECT COUNT(*) FROM wf_processes').fetchone()[0],0)

    def test_acceptance_and_uncertain_delivery_survive_reentry_without_blind_resend(self):
        with Authority(self.project) as owner:
            ledger,value=seeded_pending(owner)
            ledger.answer(value,verify_owner=standing_authority,current_binding=value['binding'])
        with Authority(self.project) as owner:
            ledger=Interaction(owner.store,'run')
            self.assertEqual(ledger.delivery_intent(value['gate_id']),value)
        with Authority(self.project) as owner:
            ledger=Interaction(owner.store,'run')
            with self.assertRaisesRegex(Blocked,'uncertain/already attempted'):
                ledger.delivery_intent(value['gate_id'])
            self.assertEqual(owner.store.db.execute('SELECT payload FROM wf_owner_inputs').fetchone()[0],canonical(value))
            self.assertEqual(owner.store.db.execute('SELECT COUNT(*) FROM wf_processes').fetchone()[0],0)

    def test_original_pin_low_unknown_and_missing_never_selects_fresh(self):
        from coherence_workflow.sessions import select_session
        from test_sessions import request,candidate
        now=time.time_ns()
        for telemetry in ({'reliable':True,'enabled':True,'threshold':200000,'occupancy':50001,'observed_ns':now,'provenance':'controlled-policy-test'},None):
            with self.subTest(telemetry=telemetry),self.assertRaisesRegex(Blocked,'original conversation pin'):
                select_session(request(pin='original'),[candidate(id='original',telemetry=telemetry)],now_ns=now,max_age_ns=1000000)
        with self.assertRaisesRegex(Blocked,'original conversation pin'):
            select_session(request(pin='original'),[],now_ns=now,max_age_ns=1000000)
        with Authority(self.project) as owner:
            gateway=self.gateway(owner);config=manifest(self.project,tools=False)
            config['open']={'file':str(Path(config['session_dir'])/'missing.jsonl'),'session_id':'original','leaf':'missing','sha256':digest('missing')}
            with self.assertRaisesRegex(Blocked,'original saved conversation unavailable'):
                PiAdapter(gateway,config,node='missing-host',environment=environment(),
                    session_context={'role':'implement','affinity':'story','review_lineage':None},reopen_from='missing')
            self.assertEqual(owner.store.db.execute('SELECT COUNT(*) FROM wf_processes').fetchone()[0],0)

    def test_live_normal_greedy_reopen_across_verified_checkpoint_preserves_original_receipts(self):
        import sqlite3
        from unittest.mock import patch
        import test_cli
        original=test_cli.approved_fixture
        def same_manifest_tasks(project,config_hash):
            contract,catalog=original(project,config_hash)
            for task in contract['tasks']:
                task['owned_paths']=['owned.txt']
                task['required'][0]['criterion']='The owned Python source defines answer() returning integer 1; both task results must remain valid on final bytes.'
                task['required'][0]['check']={'id':'workflow.PythonAnswer','version':'1','args':{'path':'owned.txt','expected':1}}
            contract['tasks'][0]['outcome']='Read owned.txt then replace it with Python source defining only answer(), returning integer 1. No comment yet.'
            contract['tasks'][1]['outcome']='Read owned.txt, preserve answer() returning integer 1, and add exactly the harmless source comment # second task. Do not add functions or change behavior.'
            return contract,catalog
        with patch('test_cli.approved_fixture',side_effect=same_manifest_tasks),patch('test_cli.retain_failure',side_effect=retain_current_failure):
            test_cli.live_sequence(self,expected_check_count=3)
        db=sqlite3.connect(self.project/'.coherence/workflow/workflow.sqlite');db.row_factory=sqlite3.Row
        try:
            turns=[json.loads(r[0]) for r in db.execute("SELECT result FROM wf_operations WHERE kind='sdk-turn' AND phase='completed' ORDER BY rowid")]
            self.assertEqual(turns[0]['after']['session_id'],turns[1]['before']['session_id'])
            self.assertNotEqual(turns[0]['host_op'],turns[1]['host_op'])
            self.assertEqual(turns[1]['selection']['reason'],'latest_settled_stable_id')
            old=db.execute('SELECT result FROM wf_operations WHERE op_id=?',(turns[0]['host_op'],)).fetchone()[0]
            original_event=db.execute("SELECT payload FROM wf_events WHERE op_id=? AND kind='completed'",(turns[0]['host_op'],)).fetchone()[0]
            self.assertEqual(old,original_event,'original host custody receipt was overwritten across commit')
            later=db.execute('SELECT intent FROM wf_operations WHERE op_id=?',(turns[1]['host_op'],)).fetchone()[0]
            self.assertNotEqual(json.loads(old)['reconciliation']['head'],json.loads(later)['baseline']['head'])
            print(canonical({'items':['T006/V1','T006/V2'],'policy':'normal greedy saved reuse across focused checkpoint',
                             'selection':turns[1]['selection'],'session_id':turns[1]['before']['session_id'],'original_receipt_unchanged':True}))
        finally:db.close()

    def test_unexplained_closed_host_drift_blocks_but_registered_fault_has_attributable_chain(self):
        from coherence_workflow.tools import ProcessTool,snapshot
        from coherence_workflow.store import git
        from test_review_repair import inject_registered_fault
        self.project.joinpath('other.txt').write_text('unrelated staged fixture')
        git(self.project,'add','--','other.txt')
        with Authority(self.project) as owner:
            gateway=self.gateway(owner)
            tool=ProcessTool('offline-idle-host','1',{'type':'object','additionalProperties':False},
                             lambda unused:[str(Path('/usr/bin/true').resolve())],(),environment())
            gateway.tools={tool.id:tool}
            operation,process=gateway.launch('offline-closed-host',tool.id,'1',{},
                lambda phase,op:self.capture(phase,op,owner),scope_kind='host')
            gateway.settle(operation,process.wait(timeout=10))
            original=owner.store.operation(operation)['result']
            before=snapshot(self.project,['owned.txt'])
            self.project.joinpath('owned.txt').write_text('unregistered fixture drift')
            with self.assertRaisesRegex(Blocked,'unexplained current'):
                gateway.verify_closed_host(operation)
            # Restore only these known disposable fixture bytes (not Git/history
            # or inherited user work); then exercise the approved fault carrier.
            self.project.joinpath('owned.txt').write_text('base')
            successor=inject_registered_fault(owner,'run',self.parent,'registered fault',owned_path='owned.txt')
            for row in owner.store.db.execute('SELECT containment FROM wf_processes WHERE containment IS NOT NULL'):
                receipt=json.loads(row[0])
                if receipt not in self.receipts:self.receipts.append(receipt)
            proof=gateway.verify_closed_host(operation)
            self.assertEqual(proof['successors'],successor)
            self.assertEqual(owner.store.operation(operation)['result'],original)
            after=snapshot(self.project,['owned.txt'])
            self.assertEqual(before['index'],after['index'])
            self.assertEqual(before['files']['other.txt'],after['files']['other.txt'])
            self.assertEqual(self.project.joinpath('owned.txt').read_text(),'registered fault')
            print(canonical({'proof':'registered-fault-successor-chain','host_operation':operation,'successors':successor,
                             'unregistered_drift':'blocked','original_receipt_unchanged':True,'unrelated_index_preserved':True}))

    def test_continuation_cannot_ignore_a_different_declared_profile_or_permission(self):
        from coherence_workflow.cli import Coordinate
        with Authority(self.project) as owner:
            ledger,value=seeded_pending(owner)
            ledger.answer(value,verify_owner=standing_authority,current_binding=value['binding'])
            node={'id':'implement','role':'implement','profile':'original','skill':'original','tools':['read_file'],
                  'permissions':['read_file'],'session_policy':{'min_free_tokens_before_compaction':150000}}
            coordinate=Coordinate.__new__(Coordinate);coordinate.interaction=ledger;coordinate.config={'nodes':[node]}
            for change in ({'profile':'different'},{'permissions':[]},{'session_policy':{'min_free_tokens_before_compaction':200000}}):
                with self.subTest(change=change),self.assertRaisesRegex(Blocked,'configured continuation differs'):
                    coordinate.continue_original({'node':{**node,**change}})
            self.assertEqual(owner.store.db.execute('SELECT COUNT(*) FROM wf_processes').fetchone()[0],0)

    def test_source_changing_answer_requires_producing_renewal_before_delivery(self):
        with Authority(self.project) as owner:
            ledger,value=seeded_pending(owner)
            with self.assertRaisesRegex(Blocked,'producing approval renewal'):
                ledger.answer(value,verify_owner=lambda v:{'input_hash':digest(v),'scope':'requires_approval'},current_binding=value['binding'])
            self.assertEqual(owner.store.db.execute('SELECT COUNT(*) FROM wf_owner_inputs').fetchone()[0],0)
            self.assertEqual(ledger.question(value['gate_id'])['stage'],'pending')


class AutonomyAdmissionTests(IsolatedCustody):
    def test_approved_technical_tool_is_autonomous_while_paid_action_denies_zero_send(self):
        from coherence_workflow.authority import AuthorityAdmission
        with Authority(self.project) as owner:
            gateway,operation,process=self.launch(owner)
            ledger=Interaction(owner.store,'run')
            result=gateway.settle(operation,process.wait(timeout=10))
            self.assertTrue(result['replacement_allowed'])
            self.assertFalse(ledger.pending())
            profile=manifest(self.project,tools=False)['profile']
            envelope={'profiles':[profile],'capabilities':[{'id':'separate_paid_service','effects':['paid_service'],
                'purpose':'isolated negative admission fixture only','cost_impact':'No service call is made'}],
                'external_paid_authority':'unresolved','approval_refs':[],'limits':[]}
            admission=AuthorityAdmission(envelope,{'exact':profile},['separate_paid_service'],['separate_paid_service'],lambda *unused:None,store=owner.store,run='run')
            self.assertEqual(admission.model(profile),profile,'ordinary approved model traffic received a financial gate')
            sends=[]
            with self.assertRaisesRegex(Blocked,'scoped authority'):
                admission.external('separate_paid_service',lambda:sends.append('PROHIBITED'))
            self.assertEqual(sends,[])
            gaps=admission.gaps()
            self.assertTrue(gaps and all(g['impact'] and g['options'] for g in gaps))
            self.assertFalse(ledger.pending(),'ordinary action or denied service created a routine owner question')
            print(canonical({'item':'T006/V4','technical_gateway_operation':operation,'paid_service_sends':0,
                             'ordinary_model_financial_gate':False,'known_gaps':gaps,'semantic_limit':'bounded rationale inspection, not universal classification'}))

    def test_question_tool_requires_both_declared_tool_and_permission(self):
        from coherence_workflow.cli import Coordinate
        with self.assertRaisesRegex(Blocked,'node tool/permission'):
            Coordinate.admit_node_tools({'tools':['read_file','request_owner_input'],'permissions':['read_file']},['read_file','request_owner_input'])
        with self.assertRaisesRegex(Blocked,'node tool/permission'):
            Coordinate.admit_node_tools({'tools':['read_file'],'permissions':['read_file','request_owner_input']},['read_file','request_owner_input'])
        Coordinate.admit_node_tools({'tools':['read_file','request_owner_input'],'permissions':['read_file','request_owner_input']},['read_file','request_owner_input'])

    def test_manager_rationale_shape_is_not_a_semantic_oracle(self):
        self.assertEqual(validate_question(question()), question())
        invalid=question();invalid['recommendation']='Not an offered option'
        with self.assertRaisesRegex(Blocked,'recommendation'):validate_question(invalid)
        invalid=question();invalid['category']='ordinary_debugging'
        with self.assertRaises(Exception):validate_question(invalid)


class CompletedToolQuestionTests(IsolatedCustody):
    """R002: current exclusive batch, lifetime replay IDs and durable tool quiescence."""
    def adapter(self,owner):
        from test_pi_adapter import ToolBatchTests
        adapter,cleanup=ToolBatchTests.batch_adapter(self,owner)
        facts=binding(adapter.session_id);facts['role']='review';facts['attempt_id']=adapter.current['attempt_id']
        operation=owner.store.intent('run','offline-question','sdk-turn',{},
            {'task_id':facts['task_id'],'attempt_id':facts['attempt_id'],'role':facts['role'],
             'before':{'session_id':adapter.session_id}})
        adapter.current['operation_id']=operation['op_id']
        adapter.interaction=Interaction(owner.store,'run');adapter.question_binding=facts
        adapter.manifest['tools'].append({'name':'request_owner_input','version':'1','parameters':QUESTION_SCHEMA,'permission':'request_owner_input'})
        return adapter,cleanup

    def request(self,adapter,call='question'):
        return {**adapter.binding,'command_id':adapter.current['command_id'],'operation_id':adapter.current['operation_id'],
            'attempt_id':adapter.current['attempt_id'],'session_id':adapter.session_id,
            'payload':{'call':call,'tool':'request_owner_input','version':'1','generation':adapter.lifecycle.generation,
                       'args':question(),'batch':[{'call':call,'tool':'request_owner_input'}]}}

    def read_request(self,adapter,call):
        from test_pi_adapter import ToolBatchTests
        return ToolBatchTests.request(self,adapter,call)

    def drain(self,adapter):
        deadline=time.monotonic()+10
        while adapter.pending or adapter.tool_queue:
            adapter._poll_tools()
            if time.monotonic()>deadline:self.fail('bounded real read did not settle')
            time.sleep(.01)

    def test_completed_read_then_new_exclusive_question_preserves_replay_set_and_park_order(self):
        with Authority(self.project) as owner:
            adapter,cleanup=self.adapter(owner)
            try:
                adapter._launch_tool(self.read_request(adapter,'completed-read'));self.drain(adapter)
                self.assertIn('completed-read',adapter.tool_calls_seen)
                self.assertTrue(adapter.tool_results[0]['result']['details']['quiescent'])
                adapter._launch_tool(self.request(adapter))
                self.assertEqual(adapter.tool_calls_seen,{'completed-read','question'})
                self.assertEqual(adapter.interaction.question(adapter.question_gate)['stage'],'parking')
                self.assertEqual(owner.store.db.execute('SELECT COUNT(*) FROM wf_outbox').fetchone()[0],0)
                with self.assertRaisesRegex(Blocked,'duplicate'):adapter._launch_tool(self.request(adapter))
                with self.assertRaisesRegex(Blocked,'freeze'):adapter._launch_tool(self.read_request(adapter,'after-question'))
                self.assertTrue(adapter.tool_results[-1]['result']['terminate'])
            finally:cleanup()

    def test_current_mixed_queued_pending_stale_duplicate_and_unreconciled_negatives(self):
        with Authority(self.project) as owner:
            adapter,cleanup=self.adapter(owner)
            try:
                adapter._launch_tool(self.read_request(adapter,'one'))
                with self.assertRaisesRegex(Blocked,'unsettled'):adapter._launch_tool(self.request(adapter))
                adapter._launch_tool(self.read_request(adapter,'two'))
                self.assertTrue(adapter.pending and adapter.tool_queue)
                with self.assertRaisesRegex(Blocked,'unsettled'):adapter._launch_tool(self.request(adapter))
                self.drain(adapter)
                with self.assertRaisesRegex(Blocked,'duplicate'):adapter._launch_tool(self.request(adapter,'one'))
                for field in ('command_id','session_id','attempt_id','operation_id'):
                    stale=self.request(adapter);stale[field]='stale'
                    with self.assertRaisesRegex(Blocked,'outside current'):adapter._launch_tool(stale)
                stale=self.request(adapter);stale['payload']['generation']+=1
                with self.assertRaisesRegex(Blocked,'outside current'):adapter._launch_tool(stale)
                for batch in (None,[],[{'call':'question','tool':'request_owner_input'},{'call':'other','tool':'read_fixture'}]):
                    mixed=self.request(adapter);mixed['payload']['batch']=batch
                    with self.assertRaisesRegex(Blocked,'exclusive'):adapter._launch_tool(mixed)
                # An unknown outstanding registered process cannot hide behind empty Python queues.
                op,process=adapter.gateway.launch('unreconciled-read','read_fixture','1',{'path':'owned.txt'},
                    admitted_host_ops=(adapter.host_op,))
                process.wait(timeout=10)
                with self.assertRaisesRegex(Blocked,'unreconciled'):adapter._launch_tool(self.request(adapter))
                self.assertTrue(adapter.gateway.settle(op,process.returncode)['replacement_allowed'])
                self.assertFalse(adapter.question_gate)
                self.assertEqual(owner.store.db.execute('SELECT COUNT(*) FROM wf_questions').fetchone()[0],0)
            finally:cleanup()
