"""T005: original-failure budgets, real independent review/correction, hard gates."""
import copy
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest

import yaml

from coherence_workflow.cli import Coordinate, ROOT, registered_checks, status
from coherence_workflow.intake import approval_scope
from coherence_workflow.store import Authority, Blocked, canonical, digest, git
from coherence_workflow.tools import Gateway, snapshot
from fixtures.support import make_project
from test_custody import IsolatedCustody
from test_intake import approved_fixture
from test_pi_adapter import manifest, environment
from test_recovery import capture


def coordinate_fixture(project, owner, *, limit=2, task_setup=None):
    config=yaml.safe_load((ROOT/'runtime/coherence_workflow/workflows/coordinate.yaml').read_text())
    for node in config['nodes']:
        if node.get('role') in ('repair','review'):node['max_repair_attempts']=limit
    config['defaults']['max_repair_attempts']=limit
    sdk=manifest(project,tools=False)
    contract,catalog=approved_fixture(project,digest(config))
    if task_setup:
        task_setup(contract)
        for ref in contract['approval_refs']:
            if ref['gate_kind']=='implementation':
                ref['scope_hash']=approval_scope(contract,digest(config));catalog[ref['authority_ref']]['scope_hash']=ref['scope_hash']
    owner.store.reserve('run',digest(config))
    coordinate=Coordinate(owner,'run',contract,catalog,config,os.environ['COHERENCE_TEST_CGROUP_PARENT'],sdk,environment())
    coordinate.intake({})
    return coordinate


class RepairBudgetTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.project=make_project(Path(self.temp.name)/'project')

    def test_actual_configured_failure_repair_original_budget_real_check_and_commit(self):
        case=IsolatedCustody()
        case.setUp()
        try:live_case(case,review_correction=False)
        finally:case.doCleanups()

    def test_zero_budget_zero_dispatch_at_actual_repair_handler(self):
        with Authority(self.project) as owner:
            coordinate=coordinate_fixture(self.project,owner,limit=0)
            sends=[];coordinate.implement=lambda *args,**kwargs:sends.append('dispatch')
            result=coordinate.repair({'node':next(n for n in coordinate.config['nodes'] if n['handler']=='repair')})
            self.assertEqual(result,{'outcome':'blocked'});self.assertEqual(sends,[])
            self.assertEqual(owner.store.db.execute('SELECT COUNT(*) FROM wf_processes').fetchone()[0],0)
            self.assertEqual(status(self.project,'run')['state'],'final_failure')

    def test_two_budget_interruption_new_ids_and_restart_cannot_reset_original(self):
        with Authority(self.project) as owner:
            coordinate=coordinate_fixture(self.project,owner)
            self.assertEqual(coordinate.review_repair.budget('original-failure',2,consume=True),1)
            # Explicit fixture interruption after durable dispatch reservation, not a fake SDK success.
            try:raise RuntimeError('fixture interrupted dispatch')
            except RuntimeError:pass
            with owner.store.transaction() as db:
                db.execute('INSERT INTO wf_corrections VALUES(?,?,?,?,?)',('run','new-correction-id','A','original-failure',canonical({'fixture':'owner preapproved isolated budget test'})))
        with Authority(self.project) as owner:
            coordinate=coordinate_fixture(self.project,owner)
            key=coordinate.review_repair.failure_key({'id':'new-correction-id'})
            self.assertEqual(key,'original-failure')
            self.assertEqual(coordinate.review_repair.budget(key,2,consume=True),2)
            with self.assertRaisesRegex(Blocked,'exhausted'):coordinate.review_repair.budget(key,2,consume=True)
            self.assertEqual(owner.store.db.execute('SELECT used FROM wf_repair_budgets WHERE failure_key=?',(key,)).fetchone()[0],2)

    def test_unknown_environment_or_contract_failure_cannot_blindly_repair(self):
        with Authority(self.project) as owner:
            coordinate=coordinate_fixture(self.project,owner)
            task=coordinate.contract['tasks'][0]
            with self.assertRaisesRegex(Blocked,'unknown/environment'):coordinate.review_repair.diagnose(task,[])
            self.assertEqual(owner.store.db.execute('SELECT COUNT(*) FROM wf_processes').fetchone()[0],0)


def live_case(case, *, review_correction):
    case.assertEqual(os.environ.get('COHERENCE_LIVE'),'1','REQUIRED actual review/repair integration NOT VERIFIED')
    project=case.project
    (project/'answer.py').write_text('def answer():\n    return -1\n')
    git(project,'add','--','answer.py');git(project,'commit','-qm','isolated answer baseline')
    (project/'other.txt').write_text('unrelated stage');git(project,'add','--','other.txt')
    (project/'custom.md').write_text('unrelated custom');(project/'untracked-user').write_text('untouched')
    (project/'.coherence/workflow').mkdir(parents=True,mode=0o700)
    config=yaml.safe_load((ROOT/'runtime/coherence_workflow/workflows/coordinate.yaml').read_text())
    sdk=manifest(project,tools=False)
    sdk['skills']=[{'path':str(ROOT/'skills/coordinate-implementation/SKILL.md'),
                   'sha256':config['skills']['coordinate']['sha256'],'name':'coordinate-implementation'}]
    sdk['resource_hash']=digest({k:sdk[k] for k in ('skills','tools','permissions','trust','system_prompt')})
    contract,catalog=approved_fixture(project,digest(config));task=contract['tasks'][0]
    task['outcome']='Implement answer.py containing only answer(), returning integer 1. Do not leave any other function, unused helper, dead code or placeholder.'
    task['owned_paths']=['answer.py'];task['required'][0]['criterion']='answer() returns integer 1; independent final source review checks the no-extra-functions requirement.'
    task['required'][0]['check']={'id':'workflow.PythonAnswer','version':'1','args':{'path':'answer.py','expected':1}}
    task['required'][0]['pass_condition']='contained real Python answer() oracle returns 1'
    contract['tasks']=[task]
    contract['authorization_envelope']['profiles']=[config['profiles']['sol-medium']]
    if review_correction:
        correction=copy.deepcopy(task)
        correction.update(id='A-correction',order=1,depends=['A'],outcome='Remove every function except answer(), preserve answer() returning integer 1. Make no other changes.')
        catalog['workflow_correction_rules']=[{'criterion_ref':'A/V1','path':'answer.py','original_task_id':'A','task':correction,
            'scope_hash':digest(correction),'actor':'current owner via mandatory-isolated-test preapproval',
            'provenance':'Actual owner preapproved all mandatory isolated tests and test-only approval scenarios; not production acceptance.'}]
    for ref in contract['approval_refs']:
        if ref['gate_kind']=='implementation':ref['scope_hash']=approval_scope(contract,digest(config));catalog[ref['authority_ref']]['scope_hash']=ref['scope_hash']
    for name,value in {'workflow.yaml':yaml.safe_dump(config),'tasks.json':canonical(contract),'catalog.json':canonical(catalog),'manifest.json':canonical(sdk)}.items():
        path=case.root/name;path.write_text(value);path.chmod(0o600)
    args=['--project',str(project),'--run','review-loop','--workflow',str(case.root/'workflow.yaml'),
          '--tasks',str(case.root/'tasks.json'),'--owner-catalog',str(case.root/'catalog.json'),
          '--manifest',str(case.root/'manifest.json'),'--containment',case.parent]
    defect='def answer():\n    return 1\n\ndef unused():\n    return 0\n' if review_correction else 'def answer():\n    return 0\n'
    driver='''
import sys
from coherence_workflow.cli import main
from coherence_workflow.engine import Engine
original=Engine.__init__
injected=False
def initialize(self,*args,**kwargs):
 def fault(phase,op):
  global injected
  operation=self.store.operation(op)
  if phase=='application_result' and operation['kind']=='graph' and operation['node_id'].startswith('implement:') and not injected:
   (self.authority.project/'answer.py').write_text(sys.argv[1])
   injected=True
 return original(self,*args,**kwargs,phase_hook=fault)
Engine.__init__=initialize
sys.exit(main(['start',*sys.argv[2:]]))
'''
    env=dict(os.environ,COHERENCE_PYTHON=sys.executable)
    before=snapshot(project,['answer.py'])
    result=subprocess.run([sys.executable,'-c',driver,defect,*args],env=env,capture_output=True,text=True,timeout=300)
    db=sqlite3.connect(project/'.coherence/workflow/workflow.sqlite');db.row_factory=sqlite3.Row
    try:
        capture(case,db)
        case.assertEqual(result.returncode,0,result.stdout+result.stderr)
        tasks=[dict(r) for r in db.execute('SELECT * FROM wf_tasks ORDER BY approved_order')]
        case.assertEqual(len(tasks),2 if review_correction else 1)
        case.assertTrue(all(t['state']=='checkpointed' for t in tasks))
        case.assertEqual(int(git(project,'rev-list','--count',before['head']+'..HEAD')),len(tasks))
        reviews=[dict(r) for r in db.execute('SELECT * FROM wf_reviews ORDER BY rowid')]
        case.assertEqual(len(reviews),2 if review_correction else 1)
        case.assertEqual(json.loads(reviews[-1]['result'])['outcome'],'pass')
        case.assertEqual(reviews[-1]['base_sha'],before['head'])
        case.assertEqual(reviews[-1]['head_sha'],git(project,'rev-parse','HEAD').decode().strip())
        for review in reviews:
            ready=json.loads(db.execute("SELECT payload FROM wf_events WHERE op_id=? AND kind='host_ready'",(review['host_op'],)).fetchone()[0])
            case.assertEqual(ready['compatibility']['role'],'review');case.assertEqual(ready['snapshot']['tools'],['read_file'])
        budgets=[dict(r) for r in db.execute('SELECT * FROM wf_repair_budgets')]
        case.assertEqual(len(budgets),1);case.assertEqual(budgets[0]['used'],1)
        case.assertEqual(budgets[0]['failure_key'],'review-final' if review_correction else 'task:A')
        if review_correction:
            findings=[dict(r) for r in db.execute('SELECT * FROM wf_findings')]
            case.assertTrue(findings);case.assertTrue(all(f['disposition']=='resolved' and f['correction_id'] for f in findings))
            one,two=[json.loads(t['checkpoint']) for t in tasks]
            case.assertEqual(two['parent'],one['sha'])
            case.assertIn('def unused',git(project,'show',one['sha']+':answer.py').decode())
            import ast
            case.assertEqual([n.name for n in ast.parse((project/'answer.py').read_text()).body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))],['answer'])
            case.assertEqual(json.loads(tasks[0]['contract'])['required'],json.loads(tasks[1]['contract'])['required'])
        else:
            checks=[json.loads(r[0]) for r in db.execute('SELECT receipt FROM wf_checks')]
            case.assertEqual([c['status'] for c in checks],['failed','satisfied'])
            case.assertEqual(json.loads(checks[0]['output'])['raw_exit'],20)
            case.assertEqual(json.loads(checks[1]['output'])['raw_exit'],0)
        observed=status(project,'review-loop');case.assertTrue(observed['accepted']);case.assertEqual(observed['state'],'accepted')
        case.assertEqual(git(project,'diff','--cached','--name-only').decode().strip(),'other.txt')
        after=snapshot(project,['answer.py'])
        for name,value in before['files'].items():
            if name!='answer.py':case.assertEqual(value,after['files'][name])
        from coherence_workflow.projections import latest_metrics
        metric_file=project/'.coherence/workflow/runs/review-loop/metrics.jsonl'
        current_metrics=latest_metrics([json.loads(line) for line in metric_file.read_text().splitlines()])
        agent_metrics=[r for r in current_metrics if r['payload']['role'] in ('implement','repair','review')]
        turns=db.execute("SELECT COUNT(*) FROM wf_operations WHERE kind='sdk-turn' AND phase='completed'").fetchone()[0]
        case.assertEqual(len(agent_metrics),turns)
        case.assertEqual([r['payload']['repair_count'] for r in agent_metrics if r['payload']['role']=='repair'],[1])
        repair_turns=[json.loads(r[0]) for r in db.execute("SELECT result FROM wf_operations WHERE kind='sdk-turn' AND phase='completed'") if json.loads(r[0]).get('role')=='repair']
        case.assertEqual(len(repair_turns),1)
        case.assertTrue(all(o['model']=='gpt-6.1-sol' and o['wire_effort']=='medium' for turn in repair_turns for o in turn['request_observed']))
        negative_audits=[]
        if review_correction:negative_audits=acceptance_negatives(case,project,contract,catalog,config,sdk)
        print(canonical({'proof':'actual-independent-review-correction' if review_correction else 'actual-failed-check-repair',
            'negative_acceptance_audits':negative_audits,
            'exit':result.returncode,'base':before['head'],'head':after['head'],'reviews':reviews,'budgets':budgets,
            'task_checkpoints':[json.loads(t['checkpoint'])['sha'] for t in tasks],
            'review_host_ops':[r['host_op'] for r in reviews],'selected_profile':'openai-codex/gpt-6.1-sol:medium'}))
    finally:db.close()


def acceptance_negatives(case,project,contract,catalog,config,sdk):
    """Negative mutations of real settled proof; never synthetic positive review evidence."""
    observed=[]
    with Authority(project) as owner:
        coordinate=Coordinate(owner,'review-loop',contract,catalog,config,case.parent,sdk,environment())
        db=owner.store.db
        review=db.execute('SELECT * FROM wf_reviews ORDER BY rowid DESC LIMIT 1').fetchone()
        db.execute('UPDATE wf_reviews SET head_sha=? WHERE review_id=?',('stale-fixture-head',review['review_id']))
        with case.assertRaisesRegex(Blocked,'current full-range'):coordinate.complete({})
        case.assertFalse(status(project,'review-loop')['accepted']);observed.append('stale-head review blocked')
        db.execute('UPDATE wf_reviews SET head_sha=? WHERE review_id=?',(review['head_sha'],review['review_id']))
        finding=db.execute('SELECT * FROM wf_findings LIMIT 1').fetchone()
        scope_case=json.loads(review['result']);scope_case['outcome']='correction'
        scope_case['findings']=[{**json.loads(finding['finding']),'scope':'owner_decision'}]
        db.execute('UPDATE wf_reviews SET result=? WHERE review_id=?',(canonical(scope_case),review['review_id']))
        task_count=db.execute('SELECT COUNT(*) FROM wf_tasks').fetchone()[0]
        with case.assertRaisesRegex(Blocked,'explicit scoped owner'):coordinate.review_repair.authorize_corrections()
        case.assertEqual(db.execute('SELECT COUNT(*) FROM wf_tasks').fetchone()[0],task_count)
        observed.append('scope-changing finding requires owner; zero correction dispatch')
        db.execute('UPDATE wf_reviews SET result=? WHERE review_id=?',(review['result'],review['review_id']))
        permission=next(r for r in coordinate.contract['approval_refs'] if r['gate_kind']=='implementation')
        permission['action']='deny'
        with case.assertRaisesRegex(Blocked,'denied/cancelled'):coordinate.complete({})
        permission['action']='approve';observed.append('denied original implementation authority blocked')
        db.execute("UPDATE wf_findings SET disposition='unresolved' WHERE review_id=? AND finding_id=?",(finding['review_id'],finding['finding_id']))
        with case.assertRaisesRegex(Blocked,'unresolved review'):coordinate.complete({})
        observed.append('real unresolved finding blocked')
        db.execute('UPDATE wf_findings SET disposition=? WHERE review_id=? AND finding_id=?',(finding['disposition'],finding['review_id'],finding['finding_id']))
        task=db.execute('SELECT * FROM wf_tasks ORDER BY approved_order DESC LIMIT 1').fetchone()
        db.execute('UPDATE wf_tasks SET evidence=? WHERE run_id=? AND task_id=?',(canonical([{'item_id':'optional-green','status':'satisfied','evidence_id':'fixture-not-required'}]),'review-loop',task['task_id']))
        with case.assertRaisesRegex(Blocked,'current REQUIRED'):coordinate.complete({})
        observed.append('optional green cannot replace missing REQUIRED')
        db.execute('UPDATE wf_tasks SET evidence=? WHERE run_id=? AND task_id=?',(task['evidence'],'review-loop',task['task_id']))
        current_task=json.loads(task['contract'])
        request=coordinate.verification.request_sample(current_task,{'id':'mandatory-test-stop','kind':'manual','scope':'isolated gate proof only'},'answer.py',digest(config))
        with case.assertRaisesRegex(Blocked,'manual STOP'):coordinate.complete({})
        case.assertFalse(status(project,'review-loop')['accepted']);observed.append('actual pending manual STOP blocked despite real passing review')
        answer={'action':'approve','binding_hash':digest(request),'actor':'current owner via standing isolated-test preapproval',
                'provenance':'Owner explicitly preapproved all mandatory isolated tests/test-only approval scenarios; no ask_user receipt claimed'}
        coordinate.verification.answer_sample(request,answer,verify_owner=lambda actual:case.assertEqual(actual,answer))
        case.assertTrue(coordinate.verification.require_sample(request,current_task,digest(config)))
        case.assertEqual(coordinate.complete({}),{'outcome':'accepted'})
        case.assertTrue(status(project,'review-loop')['accepted']);observed.append('genuine scoped standing test preapproval plus all current proof permits acceptance')
    return observed


class IndependentReviewTests(IsolatedCustody):
    def test_actual_sdk_independent_review_finding_authorized_correction_and_full_rereview(self):
        live_case(self,review_correction=True)


class AcceptanceGateTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.project=make_project(Path(self.temp.name)/'project')

    def test_missing_invalid_stale_review_cannot_accept(self):
        with Authority(self.project) as owner:
            coordinate=coordinate_fixture(self.project,owner)
            with self.assertRaisesRegex(Blocked,'review required'):coordinate.review_repair.acceptance()
            with self.assertRaises(Exception):coordinate.review_repair.record_review({'kind':'review','outcome':'pass'},'missing')
            result={'schema_version':1,'task_id':'review','attempt_id':'review:0','contract_hash':digest('fixture'),
                    'kind':'review','outcome':'pass','range_base':'stale','range_head':'stale','findings':[],'blocker':None}
            with self.assertRaisesRegex(Blocked,'stale'):coordinate.review_repair.record_review(result,'missing')
            self.assertFalse(status(self.project,'run')['accepted'])

    def test_manual_denial_cancel_and_content_drift_stay_nonreleasing(self):
        with Authority(self.project) as owner:
            coordinate=coordinate_fixture(self.project,owner);task=coordinate.contract['tasks'][0]
            gate={'id':'manual-fixture','kind':'manual','scope':'isolated mandatory gate test only'}
            for action in ('deny','cancel','approve'):
                request=coordinate.verification.request_sample(task,gate,'owned.txt',digest(coordinate.config))
                answer={'action':action,'binding_hash':digest(request),'actor':'fixture under actual owner isolated-test preapproval',
                        'provenance':'explicit current owner standing test authorization; no ask_user receipt claimed'}
                coordinate.verification.answer_sample(request,answer,verify_owner=lambda actual:self.assertEqual(actual,answer))
                if action!='approve':
                    with self.assertRaises(Blocked):coordinate.verification.require_sample(request,task,digest(coordinate.config))
                else:self.assertTrue(coordinate.verification.require_sample(request,task,digest(coordinate.config)))
            (self.project/'owned.txt').write_text('scope/content drift')
            with self.assertRaises(Blocked):coordinate.verification.require_sample(request,task,digest(coordinate.config))
            with self.assertRaises(Blocked):coordinate.review_repair.acceptance()
            self.assertFalse(status(self.project,'run')['accepted'])

    def test_later_task_overlap_refreshes_only_stale_producer_checks_without_empty_commits(self):
        def task_setup(contract):
            for task in contract['tasks']:
                task['owned_paths']=['answer.py']
                task['outcome']='Keep answer() returning integer 1.'
                task['required'][0].update(criterion='answer() retains integer result 1',
                    check={'id':'workflow.PythonAnswer','version':'1','args':{'path':'answer.py','expected':1}},
                    pass_condition='contained Python oracle exits 0',expected_evidence='actual contained process result')
        (self.project/'answer.py').write_text('def answer():\n    return -1\n')
        git(self.project,'add','--','answer.py');git(self.project,'commit','-qm','isolated overlap baseline')
        with Authority(self.project) as owner:
            coordinate=coordinate_fixture(self.project,owner,task_setup=task_setup)
            try:
                for text in ('def answer():\n    return 1\n','def answer():\n    """Preserved API."""\n    return 1\n'):
                    self.assertEqual(coordinate.select({})['outcome'],'work')
                    (self.project/'answer.py').write_text(text)  # Explicit component fixture, not a claimed SDK producer.
                    self.assertEqual(coordinate.verify({})['outcome'],'ok')
                    self.assertEqual(coordinate.checkpoint({})['outcome'],'ok')
                rows=owner.store.db.execute('SELECT * FROM wf_tasks ORDER BY approved_order').fetchall()
                first=json.loads(rows[0]['contract']);old=json.loads(rows[0]['evidence'])
                self.assertEqual(coordinate.verification.audit(first,old)[0]['status'],'insufficient-evidence')
                count=owner.store.db.execute('SELECT COUNT(*) FROM wf_checks').fetchone()[0]
                head=git(self.project,'rev-parse','HEAD')
                coordinate.review_repair.refresh_evidence()
                self.assertEqual(owner.store.db.execute('SELECT COUNT(*) FROM wf_checks').fetchone()[0],count+1)
                self.assertEqual(git(self.project,'rev-parse','HEAD'),head)
                refreshed=owner.store.db.execute('SELECT evidence FROM wf_tasks WHERE task_id=?',('A',)).fetchone()[0]
                self.assertEqual(coordinate.verification.audit(first,json.loads(refreshed))[0]['status'],'satisfied')
                self.assertEqual(owner.store.db.execute("SELECT COUNT(*) FROM wf_events WHERE kind='task_evidence_refreshed'").fetchone()[0],1)
            finally:
                for row in owner.store.db.execute('SELECT containment FROM wf_processes WHERE containment IS NOT NULL'):
                    receipt=json.loads(row[0]);coordinate.gateway.containment.drain(receipt);coordinate.gateway.containment.remove(receipt)

    def test_pure_file_evidence_invalidates_only_affected_input_and_function_inputs_are_conservative(self):
        from coherence_workflow.verification import item_identity
        with Authority(self.project) as owner:
            coordinate=coordinate_fixture(self.project,owner)
            task=copy.deepcopy(coordinate.contract['tasks'][0]);task['owned_paths']=['owned.txt','other.txt']
            task['required'][0]['check']['args']['expected']='base'
            second=copy.deepcopy(task['required'][0]);second['id']='A/V2'
            second['check']['args']={'path':'other.txt','expected':'other'};task['required'].append(second)
            evidence=coordinate.verification.run_checks(task)
            self.assertEqual([d['status'] for d in coordinate.verification.audit(task,evidence)],['satisfied','satisfied'])
            (self.project/'other.txt').write_text('changed')
            self.assertEqual([d['status'] for d in coordinate.verification.audit(task,evidence)],['satisfied','insufficient-evidence'])
            function={**task['required'][0],'check':{'id':'workflow.PythonAnswer','version':'1','args':{'path':'owned.txt','expected':1}}}
            before=item_identity(self.project,task,function,coordinate.verification.environment)
            (self.project/'other.txt').write_text('potential function dependency changed')
            self.assertNotEqual(before,item_identity(self.project,task,function,coordinate.verification.environment))

    def test_optional_green_or_worker_confidence_not_required_evidence(self):
        with Authority(self.project) as owner:
            coordinate=coordinate_fixture(self.project,owner);task=coordinate.contract['tasks'][0]
            task['optional']=[{**task['required'][0],'id':'optional-green'}]
            dispositions=coordinate.verification.audit(task,[])
            self.assertEqual(dispositions[0]['status'],'insufficient-evidence')
            with self.assertRaises(Blocked):coordinate.review_repair.acceptance()
            self.assertFalse(status(self.project,'run')['accepted'])
