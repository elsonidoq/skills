"""Composed cutover/rollback proof uses real CLI, SDK, SQLite, Git and scoped custody."""
import copy
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest

import yaml
from coherence_workflow.containment import Cgroup, process_identity
from coherence_workflow.intake import approval_scope
from coherence_workflow.store import canonical, digest, git
from coherence_workflow.tools import snapshot
from fixtures.support import make_project
from test_custody import IsolatedCustody
from test_intake import approved_fixture, declare_builtin_actions
from test_interaction import question
from test_pi_adapter import manifest

ROOT=Path(__file__).resolve().parents[2]


class EntryCutoverTests(IsolatedCustody):
    def setUp(self):
        self.assertEqual(os.environ.get('COHERENCE_LIVE'),'1','mandatory composed cutover NOT VERIFIED')
        retained=ROOT/'.pi/workflow-validation/implementation/t009'
        self.root=Path(tempfile.mkdtemp(prefix='composed-',dir=retained))
        self.project=make_project(self.root/'unrelated-adopted-project')
        self.parent=os.environ['COHERENCE_TEST_CGROUP_PARENT'];self.capability=Cgroup(self.parent)
        self.receipts=[]
        self.sentinel=subprocess.Popen(['/usr/bin/sleep','600'])
        self.sentinel_identity=process_identity(self.sentinel.pid,'outside-sentinel')
        self.outside=self.root/'outside.txt';self.outside.write_text('outside unchanged')
        self.addCleanup(self.cleanup_scopes)
        self.addCleanup(self.capture_scopes)

    def capture_scopes(self):
        database=self.project/'.coherence/workflow/workflow.sqlite'
        if not database.is_file():return
        with sqlite3.connect(database) as db:
            if not db.execute("SELECT 1 FROM sqlite_master WHERE name='wf_processes'").fetchone():return
            for row in db.execute('SELECT containment FROM wf_processes WHERE containment IS NOT NULL'):
                receipt=json.loads(row[0])
                if receipt not in self.receipts:self.receipts.append(receipt)


    def test_actual_multiple_task_review_correction_owner_restart_dirty_composition(self):
        project=self.project
        (project/'answer.py').write_text('def answer():\n    return -1\n')
        (project/'second.txt').write_text('initial second')
        git(project,'add','--','answer.py','second.txt');git(project,'commit','-qm','isolated composed baseline')
        (project/'other.txt').write_text('unrelated staged');git(project,'add','--','other.txt')
        (project/'custom.md').write_text('unrelated custom');(project/'untracked-user').write_text('unrelated')
        (project/'STATE.md').write_text('owner dirty custom STATE; preserve exactly')
        (project/'.coherence/workflow').mkdir(parents=True,mode=0o700)
        config=yaml.safe_load((ROOT/'runtime/coherence_workflow/workflows/coordinate.yaml').read_text())
        sdk=manifest(project,tools=False)
        skill=ROOT/'skills/coordinate-implementation/SKILL.md'
        self.assertEqual(hashlib.sha256(skill.read_bytes()).hexdigest(),config['skills']['coordinate']['sha256'])
        sdk['skills']=[{'path':str(skill),'sha256':config['skills']['coordinate']['sha256'],'name':'coordinate-implementation'}]
        sdk['resource_hash']=digest({k:sdk[k] for k in ('skills','tools','permissions','trust','system_prompt')})
        contract,catalog=approved_fixture(project,digest(config));task=contract['tasks'][0]
        task['outcome']=('Mandatory isolated cutover test. First invoke read_file on answer.py exactly once. AFTER that read completes, invoke request_owner_input exactly once in a NEW observed batch as its ONLY tool, with this exact JSON: '+canonical(question())+
            '. After the bound owner answer Preserve compatibility, implement answer.py containing ONLY answer() returning integer 1. Do not reask or launch the CLI. No unused functions, dead code or placeholders.')
        task['owned_paths']=['answer.py']
        task['required'][0]['criterion']='answer() returns integer 1; independent source review also requires no extra functions/dead code.'
        task['required'][0]['check']={'id':'workflow.PythonAnswer','version':'1','args':{'path':'answer.py','expected':1}}
        task['required'][0]['pass_condition']='contained actual Python answer() oracle returns integer 1'
        contract['authorization_envelope']['profiles']=[config['profiles']['sol-medium']]
        correction=copy.deepcopy(task);correction.update(id='A-correction',order=2,depends=['A'],
            outcome='Remove every function except answer(), retain answer() returning integer 1. No other changes or questions.')
        catalog['workflow_correction_rules']=[{'criterion_ref':'A/V1','path':'answer.py','original_task_id':'A','task':correction,
            'scope_hash':digest(correction),'actor':'current owner standing mandatory isolated-test preapproval',
            'provenance':'Actual owner preapproved mandatory isolated tests and exact test-only answer/correction scenarios; not production approval.'}]
        declare_builtin_actions(contract)
        for ref in contract['approval_refs']:
            if ref['gate_kind']=='implementation':ref['scope_hash']=approval_scope(contract,digest(config));catalog[ref['authority_ref']]['scope_hash']=ref['scope_hash']
        for name,value in {'workflow.yaml':yaml.safe_dump(config),'tasks.json':canonical(contract),'catalog.json':canonical(catalog),'manifest.json':canonical(sdk)}.items():
            p=self.root/name;p.write_text(value);p.chmod(0o600)
        run='composed-cutover'
        args=['--project',str(project),'--run',run,'--workflow',str(self.root/'workflow.yaml'),'--tasks',str(self.root/'tasks.json'),
            '--owner-catalog',str(self.root/'catalog.json'),'--manifest',str(self.root/'manifest.json'),'--containment',self.parent]
        launcher=str(ROOT/'scripts/coordinate-implementation')
        env=dict(os.environ,COHERENCE_PYTHON=sys.executable)
        driver_env={**env,'PYTHONPATH':str(ROOT/'runtime')+':'+env['PYTHONPATH']}
        before=snapshot(project,['answer.py','second.txt'])
        def invoke(argv,label,*,driver=False,timeout=240):
            result=subprocess.run(argv,env=driver_env if driver else env,cwd=project,capture_output=True,text=True,timeout=timeout)
            (self.root/(label+'.log')).write_text(result.stdout+result.stderr)
            return result
        crashed=invoke([sys.executable,'-c','import json,sys;from test_interaction import crash_start;crash_start(json.loads(sys.argv[1]))',canonical(['start',*args])],'crash',driver=True)
        self.assertEqual(crashed.returncode,73,crashed.stdout+crashed.stderr)
        db=sqlite3.connect(project/'.coherence/workflow/workflow.sqlite');db.row_factory=sqlite3.Row
        self.addCleanup(db.close)
        def capture():
            for row in db.execute('SELECT containment FROM wf_processes WHERE containment IS NOT NULL'):
                receipt=json.loads(row[0])
                if receipt not in self.receipts:self.receipts.append(receipt)
        self.addCleanup(capture)
        def authorize():
            value={'action':'reconcile','run_id':run,'config_hash':db.execute('SELECT config_hash FROM wf_runs').fetchone()[0],
                'operations':[r[0] for r in db.execute("SELECT op_id FROM wf_operations WHERE phase!='completed' ORDER BY op_id")],
                'actor':'current owner standing mandatory isolated-test authority','provenance':'Actual mandatory test-only crash recovery preapproval'}
            p=self.root/'resume.json';p.write_text(canonical(value));p.chmod(0o600);return str(p)
        parked=invoke([launcher,'resume',*args,'--resume-authority',authorize()],'park')
        self.assertEqual(parked.returncode,0,parked.stdout+parked.stderr)
        self.assertEqual(json.loads(parked.stdout)['state'],'waiting_owner_input')
        gate=dict(db.execute('SELECT * FROM wf_questions').fetchone());pin=json.loads(gate['pin'])
        self.assertEqual(db.execute("SELECT COUNT(*) FROM wf_operations WHERE kind='sdk-turn'").fetchone()[0],1)
        value={'schema_version':1,'kind':'owner_answer','binding':json.loads(gate['binding']),'input_id':'standing-composed-answer',
            'gate_id':gate['gate_id'],'nonce':gate['nonce'],'pin_policy':'original_only','answer':'Preserve compatibility',
            'receipt':{'source':'cli_owner','actor':'current owner standing isolated-test authority','record_ref':'standing-mandatory-test-authority',
                'record_sha256':digest('actual current owner mandatory isolated-test preapproval'),'authority_ref':'isolated-test-owner'},
            'delivery':'accepted','original_session_ref':pin['snapshot']['session_file'],'delivery_ref':None}
        answer=self.root/'answer.json';answer.write_text(canonical(value))
        authority=self.root/'answer-authority.json';authority.write_text(canonical({'input_hash':digest(value),'scope':'within_envelope','receipt':value['receipt']}));authority.chmod(0o600)
        accepted=invoke([launcher,'answer','--project',str(project),'--run',run,'--input',str(answer),'--input-authority',str(authority)],'answer')
        self.assertEqual(accepted.returncode,0,accepted.stdout+accepted.stderr)
        defect='def answer():\n    return 1\n\ndef unused():\n    return 0\n'
        driver='''import os,sys
from coherence_workflow.cli import main
from coherence_workflow.engine import Engine
from test_review_repair import inject_registered_fault
original=Engine.__init__
injected=False
def initialize(self,*args,**kwargs):
 def fault(phase,op):
  global injected
  operation=self.store.operation(op)
  if phase=='application_result' and operation['node_id'].startswith('continue-implement:') and not injected:
   inject_registered_fault(self.authority,self.run_id,os.environ['COHERENCE_TEST_CGROUP_PARENT'],sys.argv[1])
   injected=True
 return original(self,*args,**kwargs,phase_hook=fault)
Engine.__init__=initialize
sys.exit(main(['resume',*sys.argv[2:]]))
'''
        result=invoke([sys.executable,'-c',driver,defect,*args,'--resume-authority',authorize()],'complete',driver=True,timeout=360)
        capture()
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        self.assertTrue(json.loads(result.stdout)['accepted'])
        tasks=[dict(r) for r in db.execute('SELECT * FROM wf_tasks ORDER BY approved_order')]
        self.assertEqual(len(tasks),3);self.assertTrue(all(t['state']=='checkpointed' for t in tasks))
        commits=[json.loads(t['checkpoint']) for t in tasks]
        self.assertEqual([c['parent'] for c in commits],[before['head'],commits[0]['sha'],commits[1]['sha']])
        self.assertEqual(int(git(project,'rev-list','--count',before['head']+'..HEAD')),3)
        reviews=[dict(r) for r in db.execute('SELECT * FROM wf_reviews ORDER BY rowid')]
        self.assertEqual([json.loads(r['result'])['outcome'] for r in reviews],['correction','pass'])
        self.assertEqual(reviews[-1]['base_sha'],before['head']);self.assertEqual(reviews[-1]['head_sha'],commits[-1]['sha'])
        self.assertTrue(all(r['disposition']=='resolved' for r in db.execute('SELECT * FROM wf_findings')))
        self.assertEqual(db.execute('SELECT COUNT(*) FROM wf_owner_inputs').fetchone()[0],1)
        self.assertEqual(db.execute('SELECT COUNT(*) FROM wf_questions').fetchone()[0],1)
        turns=[json.loads(r[0]) for r in db.execute("SELECT result FROM wf_operations WHERE kind='sdk-turn' ORDER BY rowid")]
        calls=[]
        for line in Path(pin['snapshot']['session_file']).read_text().splitlines():
            entry=json.loads(line)
            if entry.get('type')=='message' and isinstance(entry['message'].get('content'),list):
                calls += [part['name'] for part in entry['message']['content'] if part.get('type')=='toolCall']
        self.assertEqual(calls[:2],['read_file','request_owner_input'],'actual read-before-question not exercised')
        self.assertEqual(turns[0]['after']['session_id'],turns[1]['before']['session_id'])
        self.assertNotEqual(turns[0]['host_op'],turns[1]['host_op'])
        observations=[o for t in turns for o in t.get('request_observed',[])]
        self.assertTrue(observations);self.assertTrue(all(o['model']=='gpt-6.1-sol' and o['wire_effort']=='medium' for o in observations))
        checks=[json.loads(r[0]) for r in db.execute('SELECT receipt FROM wf_checks')]
        self.assertTrue(checks);self.assertTrue(all(c['status']=='satisfied' and c['collected']>0 for c in checks))
        after=snapshot(project,['answer.py','second.txt'])
        for path,value in before['files'].items():
            if path not in ('answer.py','second.txt'):self.assertEqual(value,after['files'][path],path)
        self.assertEqual(git(project,'diff','--cached','--name-only').decode().strip(),'other.txt')
        self.assertEqual(db.execute('PRAGMA integrity_check').fetchone()[0],'ok')
        process_rows=list(db.execute('SELECT empty_receipt FROM wf_processes'))
        self.assertTrue(process_rows)
        self.assertTrue(all(r[0] and json.loads(r[0])['populated']==0 for r in process_rows))
        proof={'fixture':str(self.root),'base':before['head'],'commits':[c['sha'] for c in commits],
            'new_skill_sha256':hashlib.sha256(skill.read_bytes()).hexdigest(),'selected':'openai-codex/gpt-6.1-sol:medium',
            'observed_requests':len(observations),'reviews':len(reviews),'checks':len(checks),
            'owner_answer':'Actual CLI acceptance under standing test-only authority; NOT ask_user or human-click evidence',
            'before':before,'after':after,'exit_codes':[crashed.returncode,parked.returncode,accepted.returncode,result.returncode]}
        (self.root/'proof.json').write_text(canonical(proof));print(canonical(proof))

    def test_legacy_active_unknown_origin_is_denied_before_dispatch(self):
        contract,catalog=approved_fixture(self.project,'config','legacy')
        for name,value in [('tasks.json',contract),('catalog.json',catalog)]:
            p=self.root/name;p.write_text(canonical(value));p.chmod(0o600)
        before=snapshot(self.project,[])
        result=subprocess.run([str(ROOT/'scripts/coordinate-implementation'),'intake','--project',str(self.project),
            '--tasks',str(self.root/'tasks.json'),'--owner-catalog',str(self.root/'catalog.json'),'--config-hash','config'],
            env=dict(os.environ,COHERENCE_PYTHON=sys.executable),capture_output=True,text=True,timeout=20)
        self.assertEqual(result.returncode,2,result.stdout+result.stderr)
        self.assertIn('legacy origin/writer reconciliation required',result.stdout)
        self.assertEqual(before,snapshot(self.project,[]))
        self.assertFalse((self.project/'.coherence/workflow/workflow.sqlite').exists())
        print('actual legacy-active/unknown CLI denial exit2, no database/dispatch/files/index mutation')


class ActiveConsumersTests(unittest.TestCase):
    def test_bounded_inventory_and_retired_execution_mutations(self):
        import importlib.util
        spec=importlib.util.spec_from_file_location('active_checker',ROOT/'scripts/check-planner-workflow.py')
        checker=importlib.util.module_from_spec(spec);spec.loader.exec_module(checker)
        self.assertEqual(checker.active_consumer_errors(),[])
        result=subprocess.run([str(ROOT/'scripts/check-skills-lint.sh'),'--active-consumers'],
            env=dict(os.environ,COHERENCE_PYTHON=sys.executable),capture_output=True,text=True,timeout=20)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        self.assertEqual(result.stdout.count('ActiveConsumersTests: inspected '),len(checker.ACTIVE_EXECUTION_CONSUMERS))
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            for path in checker.ACTIVE_EXECUTION_CONSUMERS:
                p=root/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((ROOT/path).read_bytes())
            path=root/'skills/coordinate-implementation/SKILL.md';original=path.read_text()
            for retired in ('Up to three bounded tasks','references/batch-routing.md','explicit batch/profile approval'):
                path.write_text(original+'\n'+retired)
                self.assertTrue(checker.active_consumer_errors(root))
        print(result.stdout)


class RollbackTests(IsolatedCustody):
    """Actual bound control, owned descendant drain, preserved accepted history, disabled entry."""
    def setUp(self):
        self.assertTrue(os.environ.get('COHERENCE_ROLLBACK_FIXTURE'),'explicit current composed fixture required; NOT VERIFIED')
        retained=Path(os.environ['COHERENCE_ROLLBACK_FIXTURE']).resolve(strict=True)
        self.assertTrue(retained.is_relative_to(ROOT/'.pi/workflow-validation/implementation/t009'))
        self.root=Path(tempfile.mkdtemp(prefix='rollback-',dir=ROOT/'.pi/workflow-validation/implementation/t010'))
        self.project=retained/'unrelated-adopted-project'
        self.parent=os.environ['COHERENCE_TEST_CGROUP_PARENT'];self.capability=Cgroup(self.parent);self.receipts=[]
        self.sentinel=subprocess.Popen(['/usr/bin/sleep','120'])
        self.sentinel_identity=process_identity(self.sentinel.pid,'outside-sentinel')
        self.outside=self.root/'outside.txt';self.outside.write_text('outside unchanged')
        self.addCleanup(self.cleanup_scopes)

    def test_failed_acceptance_safe_drain_preserves_sql_pi_commits_index_and_partial_work(self):
        import time,uuid
        from coherence_workflow.cli import Coordinate
        from coherence_workflow.store import Authority,Blocked
        from test_controls import control_value
        from test_pi_adapter import environment
        from fixtures.custody_support import process_tool
        project=self.project
        accepted_head=git(project,'rev-parse','HEAD').decode().strip()
        before=snapshot(project,['owned.txt'])
        pi_files={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in (project/'.coherence/workflow/sdk/sessions').glob('*.jsonl')}
        self.assertTrue(pi_files,'must preserve real original Pi conversations, not placeholders')
        run='rollback-'+uuid.uuid4().hex
        import shlex
        selected_entry=self.root/'coordinate-entry'
        initial_entry='#!/bin/sh\nexec '+shlex.quote(str(ROOT/'scripts/coordinate-implementation'))+' "$@"\n'
        selected_entry.write_text(initial_entry);selected_entry.chmod(0o700)
        # The original selected entry is ACTUALLY invoked before its scoped disable change.
        initial=subprocess.run([str(selected_entry),'status','--project',str(project),'--run','composed-cutover'],
            env=dict(os.environ,COHERENCE_PYTHON=sys.executable),capture_output=True,text=True,timeout=20)
        self.assertEqual(initial.returncode,0,initial.stdout+initial.stderr);self.assertTrue(json.loads(initial.stdout)['accepted'])
        with Authority(project) as owner:
            original={table:[tuple(r) for r in owner.store.db.execute('SELECT * FROM '+table+" WHERE run_id='composed-cutover' ORDER BY rowid")]
                for table in ('wf_runs','wf_operations','wf_events','wf_tasks','wf_checks','wf_reviews')}
            backup=sqlite3.connect(self.root/'before.sqlite');owner.store.db.backup(backup);backup.close()
            config=yaml.safe_load((ROOT/'runtime/coherence_workflow/workflows/coordinate.yaml').read_text())
            contract,catalog=approved_fixture(project,digest(config))
            owner.store.reserve(run,digest(config))
            c=Coordinate(owner,run,contract,catalog,config,self.parent,manifest(project,tools=False),environment())
            c.intake({});binding=c.publish_run_binding();c.select({})
            from coherence_workflow.tools import Gateway
            # Explicit trusted rollback custody probe, not a configured agent-tool grant.
            c.gateway=Gateway(owner,run,self.parent,{'fixture':process_tool(project)})
            op,process=c.gateway.launch('rollback-active','fixture','1',{'mode':'survivor_hang','exit':0})
            self.receipts.append(json.loads(owner.store.db.execute('SELECT containment FROM wf_processes WHERE op_id=?',(op,)).fetchone()[0]))
            deadline=time.monotonic()+10
            while 'child' not in (project/'owned.txt').read_text():
                if time.monotonic()>deadline:self.fail('actual scoped descendant did not write')
                time.sleep(.01)
            with self.assertRaisesRegex(Blocked,'current full-range independent review required'):
                c.review_repair.acceptance()
            value=control_value(binding,'pause','rollback-pause-'+uuid.uuid4().hex,active=False)
            incoming=self.root/'pause.json';incoming.write_text(canonical(value))
            authority=self.root/'pause-authority.json';authority.write_text(canonical({'input_hash':digest(value),'scope':'within_envelope','authority_ref':value['owner_authority_ref']}));authority.chmod(0o600)
            control=subprocess.run([str(selected_entry),'control','--project',str(project),'--run',run,
                '--input',str(incoming),'--input-authority',str(authority)],
                env=dict(os.environ,COHERENCE_PYTHON=sys.executable),capture_output=True,text=True,timeout=20)
            self.assertEqual(control.returncode,0,control.stdout+control.stderr)
            self.assertEqual(json.loads(control.stdout)['stage'],'received','no false pause before actual drain')
            with self.assertRaisesRegex(Blocked,'custody not quiescent'):c.controls_boundary()
            with self.assertRaisesRegex(Blocked,'unreconciled process'):owner.store.assert_dispatchable(run)
            drained=c.gateway.resolve(op);process.wait(timeout=10)
            self.assertTrue(drained['replacement_allowed']);self.assertEqual(drained['empty_receipt']['populated'],0)
            partial=(project/'owned.txt').read_bytes();self.assertIn(b'child',partial)
            with self.assertRaisesRegex(Blocked,'paused; no worker ACK'):c.controls_boundary()
            row=owner.store.db.execute('SELECT stage,receipt FROM wf_owner_inputs WHERE input_id=?',(value['input_id'],)).fetchone()
            self.assertEqual(row['stage'],'reconciled');self.assertFalse(json.loads(row['receipt'])['worker_acknowledged'])
            self.assertEqual(owner.store.db.execute('SELECT state FROM wf_runs WHERE run_id=?',(run,)).fetchone()[0],'paused')
            self.assertEqual(owner.store.db.execute("SELECT COUNT(*) FROM wf_operations WHERE run_id=? AND kind='git-checkpoint'",(run,)).fetchone()[0],0)
            for table,rows in original.items():
                self.assertEqual(rows,[tuple(r) for r in owner.store.db.execute('SELECT * FROM '+table+" WHERE run_id='composed-cutover' ORDER BY rowid")],table)
            backup=sqlite3.connect(self.root/'after.sqlite');owner.store.db.backup(backup);backup.close()
            self.assertEqual(owner.store.db.execute('PRAGMA integrity_check').fetchone()[0],'ok')
        # Actual entry refuses an unsupported capability before dispatch, keeping prior SQL/commits.
        for name,payload in {'workflow.yaml':yaml.safe_dump(config),'tasks.json':canonical(contract),
                             'catalog.json':canonical(catalog),'manifest.json':canonical(c.manifest)}.items():
            p=self.root/name;p.write_text(payload);p.chmod(0o600)
        capability_denial=subprocess.run([str(selected_entry),'start','--project',str(project),'--run','unsupported-'+run,
            '--workflow',str(self.root/'workflow.yaml'),'--tasks',str(self.root/'tasks.json'),
            '--owner-catalog',str(self.root/'catalog.json'),'--manifest',str(self.root/'manifest.json'),
            '--containment',str(self.root)],env=dict(os.environ,COHERENCE_PYTHON=sys.executable),
            capture_output=True,text=True,timeout=20)
        self.assertEqual(capability_denial.returncode,2,capability_denial.stdout+capability_denial.stderr)
        self.assertIn('approved owned cgroup-v2 delegation unavailable',capability_denial.stdout)
        # Disable only this exact owned selected-entry wrapper; preserve its shipped target.
        old=selected_entry.lstat();target=ROOT/'scripts/coordinate-implementation'
        delta={'scope':'standing owner preapproved isolated rollback test; full migration review still required',
               'before_target':str(target),'before_sha256':hashlib.sha256(initial_entry.encode()).hexdigest(),'before_device':old.st_dev,'before_inode':old.st_ino,
               'after':'blocking shim, no legacy fallback'}
        (self.root/'entry-disable-scope.json').write_text(canonical(delta))
        self.assertFalse(selected_entry.is_symlink());self.assertEqual(selected_entry.lstat(),old)
        self.assertEqual(selected_entry.read_text(),initial_entry)
        selected_entry.write_text('#!/bin/sh\nprintf "%s\\n" "workflow entry disabled: explicit compatible authority/reconciliation required; legacy remains off" >&2\nexit 2\n');selected_entry.chmod(0o700)
        disabled=subprocess.run([str(selected_entry),'start'],capture_output=True,text=True,timeout=10)
        self.assertEqual(disabled.returncode,2);self.assertIn('legacy remains off',disabled.stderr)
        self.assertEqual((project/'owned.txt').read_bytes(),partial)
        self.assertEqual(git(project,'rev-parse','HEAD').decode().strip(),accepted_head)
        after=snapshot(project,['owned.txt'])
        self.assertEqual(before['index'],after['index'])
        for path,value in before['files'].items():
            if path!='owned.txt':self.assertEqual(value,after['files'][path],path)
        self.assertEqual(pi_files,{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in (project/'.coherence/workflow/sdk/sessions').glob('*.jsonl')})
        proof={'root':str(self.root),'project':str(project),'run':run,'prior_accepted_run':'composed-cutover',
            'prior_head_preserved':accepted_head,'index_hash_preserved':before['index'],
            'before':before,'after':after,'real_pi_hashes_preserved':pi_files,
            'database_backups':{name:hashlib.sha256((self.root/name).read_bytes()).hexdigest() for name in ('before.sqlite','after.sqlite')},
            'prior_SQL_rows_unchanged':True,'actual_empty':drained['empty_receipt'],'partial_hash':hashlib.sha256(partial).hexdigest(),
            'entry_scope':delta,'trigger':'actual current full-range acceptance rejection and actual unsupported-containment CLI denial',
            'unsupported_capability_exit':capability_denial.returncode,'control_exit':control.returncode,'disabled_exit':disabled.returncode,
            'residual':'Known paused test run/reservation and partial owned.txt intentionally retained; no SDK/model calls or legacy restart, no reset/downgrade/history deletion.'}
        (self.root/'proof.json').write_text(canonical(proof));print(canonical(proof))
