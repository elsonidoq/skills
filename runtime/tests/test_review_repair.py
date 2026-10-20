"""T005: original-failure budgets, real independent review/correction, hard gates."""
import copy
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

import yaml

from coherence_workflow.cli import Coordinate, ROOT, registered_checks, status
from coherence_workflow.intake import approval_scope
from coherence_workflow.store import Authority, Blocked, canonical, digest, git
from coherence_workflow.tools import Gateway, ProcessTool, snapshot
from fixtures.support import make_project
from test_intake import approved_fixture, declare_builtin_actions
from test_pi_adapter import manifest, environment


def coordinate_fixture(project, owner, *, limit=2, task_setup=None):
    config=yaml.safe_load((ROOT/'runtime/coherence_workflow/workflows/coordinate.yaml').read_text())
    for node in config['nodes']:
        if node.get('role') in ('repair','review'):node['max_repair_attempts']=limit
    config['defaults']['max_repair_attempts']=limit
    sdk=manifest(project,tools=False)
    contract,catalog=approved_fixture(project,digest(config))
    if task_setup:task_setup(contract)
    declare_builtin_actions(contract)
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


def inject_registered_fault(authority, run, parent, text, *, owned_path='answer.py'):
    """Deliberate fixture fault with real successor custody, never hidden drift."""
    gateway=Gateway(authority,run,parent,{})
    baseline=snapshot(authority.project,[owned_path])
    gateway.audit_task_boundary([owned_path],baseline)
    read=ProcessTool('fixture-fault-read','1',{'type':'object','additionalProperties':False},
                     lambda unused:[str(Path('/usr/bin/true').resolve())],(),environment())
    write=ProcessTool('fixture-fault-write','1',{'type':'object','additionalProperties':False},
        lambda unused:[str(Path(sys.executable).resolve()),'-c','import sys;from pathlib import Path;Path(sys.argv[1]).write_text(sys.argv[2])',
                       str(authority.project/owned_path),text],(owned_path,),environment())
    gateway.tools={read.id:read,write.id:write}
    results=[]
    for label,tool in (('read',read),('write',write)):
        operation,process=gateway.launch('fixture-fault:'+label,tool.id,'1',{})
        receipt=gateway.settle(operation,process.wait(timeout=15))
        if not receipt.get('replacement_allowed'):raise Blocked('registered fixture fault not quiescent')
        results.append(operation)
    return results


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
            def setup(contract):
                task=contract['tasks'][0];task['owned_paths']=['owned.txt','other.txt']
                task['required'][0]['check']['args']['expected']='base'
                second=copy.deepcopy(task['required'][0]);second['id']='A/V2'
                second['check']['args']={'path':'other.txt','expected':'other'};task['required'].append(second)
            coordinate=coordinate_fixture(self.project,owner,task_setup=setup)
            task=coordinate.contract['tasks'][0]
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


class LeanReviewTests(unittest.TestCase):
    def test_range_reads_stale_denial_and_repair_rereview(self):
        """Production review/check/repair helpers; no SDK judgment is simulated."""
        from types import SimpleNamespace
        from coherence_workflow.verification import ReviewRepair, Verification
        from coherence_workflow.review_documents import read_review
        with tempfile.TemporaryDirectory() as temporary:
            project=make_project(Path(temporary)/'project')
            with Authority(project) as owner:
                owner.store.reserve('run',digest('local-review-fixture'))
                contract,catalog=approved_fixture(project,digest('config'))
                task=copy.deepcopy(contract['tasks'][0]);task['gates']=[]
                task['owned_paths']=['owned.txt'];task['required'][0]['check']={'id':'workflow.FileBytes','version':'1','args':{'path':'owned.txt','expected':'fixed'}}
                contract['tasks']=[task]
                config=yaml.safe_load((ROOT/'runtime/coherence_workflow/workflows/coordinate.yaml').read_text())
                coordinate=SimpleNamespace(authority=owner,store=owner.store,run='run',contract=contract,config=config,
                    catalog=catalog,gates_satisfied=lambda task:True,reconcile_effect=lambda *args:None)
                coordinate.verification=Verification(owner,'run',registered_checks(project),authorize=lambda *args:None)
                review=ReviewRepair(coordinate)
                owner.store.db.executescript('''CREATE TABLE wf_tasks(run_id TEXT,task_id TEXT,approved_order INTEGER,
                    contract TEXT,state TEXT,baseline TEXT,evidence TEXT,checkpoint TEXT,PRIMARY KEY(run_id,task_id));''')
                base=git(project,'rev-parse','HEAD').decode().strip()
                owner.store.db.execute('INSERT INTO wf_tasks VALUES(?,?,?,?,?,?,?,?)',('run',task['id'],0,canonical(task),'checkpointed',canonical({'head':base}),canonical([]),canonical({'sha':base})))
                with self.assertRaisesRegex(Blocked,'current full-range'):review.acceptance()
                (project/'owned.txt').write_text('bad\n'+'x'*60000)
                git(project,'add','--','owned.txt');git(project,'commit','-qm','local defective producer')
                bundle=review.bundle()
                coordinate.review_repair=review;coordinate.environment={}
                tools=Coordinate._tools(coordinate,task,review=True)
                self.assertEqual(set(tools),{'read_file'})
                self.assertIsNone(tools['read_file'].build_argv)
                self.assertEqual(tools['read_file'].result_reader({'path':'owned.txt','revision':'head','limit':3},None)['text'],'bad')
                self.assertNotIn('full_committed_diff',bundle)
                self.assertEqual(bundle['changed_paths'],['owned.txt'])
                for revision in ('head','diff'):
                    args={'path':'owned.txt','revision':revision,'limit':32768};chunks=[]
                    while args:
                        chunk=read_review(project,bundle,args);chunks.append(chunk['text']);args=chunk['continuation']
                    self.assertGreater(len(''.join(chunks)),60000)
                self.assertEqual(read_review(project,bundle,{'path':'owned.txt','revision':'base'})['text'],'base')
                ref=bundle['document_refs'][0]
                self.assertTrue(read_review(project,bundle,{'path':ref['path']})['text'])
                with self.assertRaisesRegex(Blocked,'outside approved'):read_review(project,bundle,{'path':'unapproved'})
                def record(outcome,findings):
                    # Explicit local fixture of an already-settled read-only host,
                    # not a claim of real SDK/reviewer evaluation.
                    host=owner.store.intent('run','review-host:'+str(owner.store.db.execute('SELECT COUNT(*) FROM wf_reviews').fetchone()[0]),'fixture-host',{}, {})
                    owner.store.transition(host['op_id'],'intent','completed',{'replacement_allowed':True})
                    provenance={'snapshot':{'tools':['read_file','request_owner_input']},'compatibility':{'role':'review','review_lineage':base}}
                    with owner.store.transaction() as db:
                        owner.store.event(db,'run',host['op_id'],'host_ready',provenance)
                        owner.store.event(db,'run',host['op_id'],'host_admission',{'compatibility':provenance['compatibility']})
                    current=review.bundle()
                    result={'schema_version':1,'task_id':'final-review','attempt_id':'review:fixture','contract_hash':digest(current),
                        'kind':'review','outcome':outcome,'range_base':base,'range_head':current['range_head'],'findings':findings,'blocker':None}
                    return review.record_review(result,host['op_id']),result
                finding={'id':'bad','severity':'important','criterion_ref':task['required'][0]['id'],'location':'owned.txt:1',
                    'observation':'fixture defective content','evidence_ref':'owned.txt','action':'restore required content','scope':'in_scope'}
                correction=copy.deepcopy(task);correction.update(id='repair',order=1,depends=[task['id']])
                catalog['workflow_correction_rules']=[{'criterion_ref':finding['criterion_ref'],'path':'owned.txt','original_task_id':task['id'],
                    'task':correction,'scope_hash':digest(correction),'actor':'isolated-test owner','provenance':'explicit local wiring fixture'}]
                _,old_result=record('correction',[finding])
                plans=review.authorize_corrections();self.assertEqual(len(plans),1)
                repair=plans[0][0]
                self.assertEqual(coordinate.verification.run_checks(repair)[0]['status'],'failed')
                (project/'owned.txt').write_text('fixed')
                evidence=coordinate.verification.run_checks(repair)
                self.assertEqual(coordinate.verification.audit(repair,evidence)[0]['status'],'satisfied')
                # Focused real Git fixture commit after actual checks. Runner Git
                # custody/order is covered separately by T001, not this local test.
                git(project,'add','--','owned.txt');git(project,'commit','--only','-qm','local verified repair','--','owned.txt')
                self.assertEqual(git(project,'diff-tree','--no-commit-id','--name-only','-r','HEAD').decode().strip(),'owned.txt')
                with self.assertRaisesRegex(Blocked,'stale'):read_review(project,bundle,{'path':'owned.txt'})
                with self.assertRaisesRegex(Blocked,'stale'):tools['read_file'].result_reader({'path':'owned.txt'},None)
                with self.assertRaisesRegex(Blocked,'stale'):review.record_review(old_result,'unused')
                with self.assertRaisesRegex(Blocked,'current full-range'):review.acceptance()
                head=git(project,'rev-parse','HEAD').decode().strip()
                owner.store.db.execute("UPDATE wf_tasks SET state='checkpointed',evidence=?,checkpoint=?",(canonical(evidence),canonical({'sha':head})))
                record('pass',[])
                self.assertEqual(review.acceptance(),{'outcome':'accepted'})
                self.assertEqual(owner.store.db.execute('SELECT disposition FROM wf_findings').fetchone()[0],'resolved')
                print('V1: actual range/base/head/diff continuation; missing/stale denied; checks failed->satisfied; focused fixture repair; current-head rereview resolved finding')
