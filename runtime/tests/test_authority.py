"""T003/V2: no model financial gate, scoped external actions fail closed."""
import tempfile
import unittest
from pathlib import Path

from coherence_workflow.authority import AuthorityAdmission
from coherence_workflow.store import Authority, Blocked
from fixtures.support import make_project


class AuthorityAdmissionTests(unittest.TestCase):
    def test_all_known_gaps_are_aggregated(self):
        envelope = {'profiles': [{'provider': 'p', 'model': 'm', 'effort': 'medium'}],
                    'capabilities': [{'id': 'check', 'action_scope': 'test', 'effects': ['test']},
                                     {'id': 'write', 'action_scope': 'file', 'effects': ['mutation']}]}
        gaps = AuthorityAdmission(envelope, {}, [], [], lambda ref, scope: None).gaps()
        self.assertEqual({g['kind'] for g in gaps}, {'profile', 'capability', 'permission'})
        self.assertTrue(all(g['impact'] and g['options'] for g in gaps))

    def test_ordinary_model_has_no_financial_admission(self):
        profile = {'provider': 'p', 'model': 'm', 'effort': 'medium'}
        for authority in ('denied', 'unresolved', 'owner_scoped'):
            envelope = {'profiles': [profile], 'capabilities': [], 'external_paid_authority': authority,
                        'approval_refs': [], 'limits': []}
            admission = AuthorityAdmission(envelope, {'model': profile}, [], [], lambda ref, scope: None)
            self.assertEqual(admission.gaps(), [])
            self.assertEqual(admission.model(profile), profile)
            with self.assertRaises(Blocked): admission.model(dict(profile, effort='high'))

    def test_external_gateway_denials_have_zero_sends(self):
        calls = []
        for authority in (None, 'denied', 'unresolved', 'owner_scoped'):
            envelope = {'profiles': [], 'capabilities': [
                {'id': 'api', 'action_scope': 'one-service-read', 'effects': ['paid_service'],
                 'purpose': 'check result', 'cost_impact': 'one separately charged request'}],
                'external_paid_authority': authority, 'approval_refs': [], 'limits': []}
            admission = AuthorityAdmission(envelope, {}, ['api'], ['api'], lambda ref, scope: None)
            with self.assertRaises(Blocked):
                admission.external('api', lambda: calls.append('sent'))
        self.assertEqual(calls, [])

    def test_scoped_action_authority_survives_restart_without_replay(self):
        with tempfile.TemporaryDirectory() as temp:
            project = make_project(Path(temp) / 'project')
            envelope = {'profiles': [], 'capabilities': [
                {'id': 'api', 'action_scope': 'one-read', 'effects': ['paid_service'],
                 'purpose': 'read sample', 'cost_impact': 'one separately charged read'}],
                'external_paid_authority': 'owner_scoped', 'approval_refs': [{'proof': 'external'}],
                'limits': [{'action_id': 'api', 'description': 'one read'}]}
            calls = []
            verify = lambda ref, scope: self.assertEqual(ref, {'proof': 'external'})
            with Authority(project) as owner:
                owner.store.reserve('run', 'config')
                admission = AuthorityAdmission(envelope, {}, ['api'], ['api'], verify, store=owner.store, run='run')
                self.assertEqual(admission.external('api', lambda: calls.append('sent') or {'receipt': 'one'}), {'receipt': 'one'})
            with Authority(project) as owner:
                admission = AuthorityAdmission(envelope, {}, ['api'], ['api'], verify, store=owner.store, run='run')
                with self.assertRaises(Blocked): admission.external('api', lambda: calls.append('duplicate'))
            self.assertEqual(calls, ['sent'])


class AuthorityCompositionTests(unittest.TestCase):
    """F001: real Coordinate/preflight and direct dispatch, never registry-as-permission."""
    def setUp(self):
        import os,yaml
        from coherence_workflow.cli import ROOT,Coordinate
        from test_intake import approved_fixture
        from test_pi_adapter import manifest,environment
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.project=make_project(Path(self.tmp.name)/'project')
        self.config=yaml.safe_load((ROOT/'runtime/coherence_workflow/workflows/coordinate.yaml').read_text())
        self.contract,self.catalog=approved_fixture(self.project,__import__('coherence_workflow.store',fromlist=['digest']).digest(self.config))
        self.contract['authorization_envelope']['profiles']=[self.config['profiles']['sol-medium']]
        self.owner=Authority(self.project);self.addCleanup(self.owner.close)
        self.owner.store.reserve('run','fixture')
        self.c=Coordinate(self.owner,'run',self.contract,self.catalog,self.config,
            os.environ['COHERENCE_TEST_CGROUP_PARENT'],manifest(self.project,tools=False),environment())

    def renew(self):
        from coherence_workflow.intake import approval_scope
        from coherence_workflow.store import digest
        for ref in self.contract['approval_refs']:
            if ref['gate_kind']=='implementation':
                ref['scope_hash']=approval_scope(self.contract,digest(self.config))
                self.catalog[ref['authority_ref']]['scope_hash']=ref['scope_hash']

    def test_empty_owner_envelope_and_omitted_workflow_check_block_preflight_and_direct_checks(self):
        self.contract['authorization_envelope']['capabilities']=[]
        self.config['permissions'].remove('workflow.FileBytes');self.renew();self.c.intake({})
        with self.assertRaisesRegex(Blocked,'known admission gaps') as caught:self.c.authority_check({})
        for name in ('read_file','write_file','request_owner_input','workflow.FileBytes','runner-git-commit'):
            self.assertIn(name,str(caught.exception))
        with self.assertRaises(Blocked):self.c.verification.run_checks(self.contract['tasks'][0])
        self.assertEqual(self.owner.store.db.execute('SELECT COUNT(*) FROM wf_checks').fetchone()[0],0)
        self.assertEqual(self.owner.store.db.execute('SELECT COUNT(*) FROM wf_processes').fetchone()[0],0)

    def test_complete_positive_and_direct_tool_check_git_mutation_revocation(self):
        from coherence_workflow.tools import snapshot
        from coherence_workflow.store import git
        self.renew();self.c.intake({});self.assertEqual(self.c.authority_check({}),{'outcome':'ok'})
        task=self.contract['tasks'][0];baseline=self.c.git.begin(task)
        self.c.agent_node=next(n for n in self.config['nodes'] if n['id']=='implement')
        self.c.gateway.tools=self.c._tools(task)
        self.assertEqual(self.c.gateway.direct('write_file',{'path':'owned.txt','text':'first\n'})['written'],6)
        evidence=self.c.verification.run_checks(task);self.assertEqual(evidence[0]['status'],'satisfied')
        before=snapshot(self.project,[])
        self.c.contract['authorization_envelope']['capabilities']=[]
        for action in (lambda:self.c.verification.run_checks(task),
                       lambda:self.c.gateway.direct('write_file',{'path':'owned.txt','text':'denied'}),
                       lambda:self.c.git.checkpoint(task,baseline,self.c.verification.audit(task,evidence),gates_satisfied=True)):
            with self.assertRaises(Blocked):action()
        self.assertEqual(before,snapshot(self.project,[]))
        self.assertEqual(self.owner.store.db.execute("SELECT COUNT(*) FROM wf_operations WHERE kind='git-checkpoint'").fetchone()[0],0)

    def test_duplicate_wrong_scope_wrong_effect_and_unknown_actions_are_known_gaps(self):
        import copy
        original=copy.deepcopy(self.contract['authorization_envelope']['capabilities'])
        mutations=[[],original+[copy.deepcopy(original[0])],
            [{**c,'action_scope':'unverified narrative'} if c['id']=='read_file' else c for c in original],
            [{**c,'effects':['network']} if c['id']=='write_file' else c for c in original],
            original+[{'id':'unknown','action_scope':'none','effects':['external']}]]
        import json
        from coherence_workflow.store import canonical
        wrong_paths=copy.deepcopy(original)
        read=next(c for c in wrong_paths if c['id']=='read_file')
        scope=json.loads(read['action_scope']);scope['readable_paths']=['not-approved.txt'];read['action_scope']=canonical(scope)
        mutations.append(wrong_paths)
        for caps in mutations:
            self.contract['authorization_envelope']['capabilities']=caps
            self.renew()
            # Admission gaps do not execute anything. The stored input remains original/immutable.
            with self.assertRaisesRegex(Blocked,'known admission gaps'):self.c.authority_check({})
        self.assertEqual(self.owner.store.db.execute('SELECT COUNT(*) FROM wf_processes').fetchone()[0],0)

    def test_python_answer_check_cannot_run_when_omitted_unpermitted_or_wrong_argument_scope(self):
        from test_intake import declare_builtin_actions
        from coherence_workflow.store import digest
        task=self.contract['tasks'][0]
        task['required'][0]['check']={'id':'workflow.PythonAnswer','version':'1','args':{'path':'owned.txt','expected':1}}
        declare_builtin_actions(self.contract)
        self.contract['authorization_envelope']['capabilities']=[c for c in self.contract['authorization_envelope']['capabilities'] if c['id']!='workflow.PythonAnswer']
        self.renew();self.c.intake({})
        sends=[];self.c.verification.checks['workflow.PythonAnswer']['execute']=lambda args:sends.append(args)
        with self.assertRaises(Blocked):self.c.verification.run_checks(task)
        self.assertEqual(sends,[])
        self.assertEqual(self.owner.store.db.execute('SELECT COUNT(*) FROM wf_processes').fetchone()[0],0)

    def test_actual_question_admission_checks_envelope_and_current_node_before_gate(self):
        from test_interaction import question
        self.contract['authorization_envelope']['capabilities']=[c for c in self.contract['authorization_envelope']['capabilities'] if c['id']!='request_owner_input']
        self.renew();self.c.intake({})
        task=self.contract['tasks'][0];node=next(n for n in self.config['nodes'] if n['id']=='implement')
        facts={**self.c.question_binding(task,node,0,'implement'),'session_id':'test-original'}
        op=self.owner.store.intent('run','fixture-turn','sdk-turn',{},
            {k:facts[k] for k in ('task_id','attempt_id','role')}|{'before':{'session_id':'test-original'}})['op_id']
        with self.assertRaisesRegex(Blocked,'owner action request_owner_input'):
            self.c.interaction.request(op,'q',facts,question(),batch=[{'call':'q','tool':'request_owner_input'}])
        self.assertEqual(self.owner.store.db.execute('SELECT COUNT(*) FROM wf_questions').fetchone()[0],0)
        self.assertEqual(self.owner.store.db.execute('SELECT COUNT(*) FROM wf_outbox').fetchone()[0],0)

    def test_direct_question_positive_and_wrong_current_node_permission(self):
        from test_interaction import question
        self.renew();self.c.intake({})
        task=self.contract['tasks'][0];node=next(n for n in self.config['nodes'] if n['id']=='implement')
        facts={**self.c.question_binding(task,node,0,'implement'),'session_id':'test-original'}
        op=self.owner.store.intent('run','fixture-turn','sdk-turn',{},
            {k:facts[k] for k in ('task_id','attempt_id','role')}|{'before':{'session_id':'test-original'}})['op_id']
        bad={**facts,'node_id':'nonexistent'}
        with self.assertRaisesRegex(Blocked,'question node'):self.c.interaction.request(op,'bad',bad,question(),batch=[{'call':'bad','tool':'request_owner_input'}])
        good=self.c.interaction.request(op,'good',facts,question(),batch=[{'call':'good','tool':'request_owner_input'}])
        self.assertTrue(good['terminate']);self.assertEqual(self.owner.store.db.execute('SELECT COUNT(*) FROM wf_questions').fetchone()[0],1)

    def test_complete_python_answer_executes_actual_contained_project_code(self):
        from test_intake import declare_builtin_actions
        task=self.contract['tasks'][0];task['owned_paths']=['answer.py']
        task['required'][0]['check']={'id':'workflow.PythonAnswer','version':'1','args':{'path':'answer.py','expected':1}}
        (self.project/'answer.py').write_text('def answer():\n    return 1\n')
        declare_builtin_actions(self.contract);self.renew();self.c.intake({})
        self.assertEqual(self.c.authority_check({}),{'outcome':'ok'})
        try:
            observed=self.c.verification.run_checks(task)
            self.assertEqual(observed[0]['status'],'satisfied');self.assertEqual(observed[0]['collected'],1)
            changed={**task,'required':[{**task['required'][0],'check':{**task['required'][0]['check'],'args':{'path':'answer.py','expected':2}}}]}
            with self.assertRaisesRegex(Blocked,'outside approved task/check stream'):self.c.verification.run_checks(changed)
        finally:
            import json
            for row in self.owner.store.db.execute('SELECT containment FROM wf_processes WHERE containment IS NOT NULL'):
                self.c.gateway.containment.remove(json.loads(row[0]))

    def test_missing_git_and_check_workflow_permissions_deny_actual_dispatch_before_effect(self):
        from coherence_workflow.tools import snapshot
        self.config['permissions'].remove('runner-git-commit');self.config['permissions'].remove('workflow.FileBytes')
        self.renew();self.c.intake({})
        with self.assertRaisesRegex(Blocked,'known admission gaps'):self.c.authority_check({})
        task=self.contract['tasks'][0];baseline=self.c.git.begin(task)
        (self.project/'owned.txt').write_text('first\n');before=snapshot(self.project,[])
        with self.assertRaisesRegex(Blocked,'unpermitted action workflow.FileBytes'):self.c.verification.run_checks(task)
        with self.assertRaisesRegex(Blocked,'unpermitted action runner-git-commit'):
            self.c.git.checkpoint(task,baseline,[{'item_id':task['required'][0]['id'],'status':'satisfied'}],gates_satisfied=True)
        self.assertEqual(before,snapshot(self.project,[]))
        self.assertEqual(self.owner.store.db.execute('SELECT COUNT(*) FROM wf_processes').fetchone()[0],0)
        self.assertEqual(self.owner.store.db.execute("SELECT COUNT(*) FROM wf_operations WHERE kind='git-checkpoint'").fetchone()[0],0)

    def test_missing_git_owner_grant_and_missing_production_callbacks_cannot_stage_or_dispatch(self):
        from coherence_workflow.tools import snapshot
        self.contract['authorization_envelope']['capabilities']=[c for c in self.contract['authorization_envelope']['capabilities'] if c['id']!='runner-git-commit']
        self.renew();self.c.intake({})
        task=self.contract['tasks'][0];baseline=self.c.git.begin(task)
        (self.project/'owned.txt').write_text('first\n');before=snapshot(self.project,[])
        with self.assertRaisesRegex(Blocked,'owner action runner-git-commit'):
            self.c.git.checkpoint(task,baseline,[{'item_id':task['required'][0]['id'],'status':'satisfied'}],gates_satisfied=True)
        self.c.git.authorize=None
        with self.assertRaisesRegex(Blocked,'Git action authority unavailable'):
            self.c.git.checkpoint(task,baseline,[{'item_id':task['required'][0]['id'],'status':'satisfied'}],gates_satisfied=True)
        self.c.gateway.tools=self.c._tools(task);self.c.gateway.authorize=None
        with self.assertRaisesRegex(Blocked,'tool action authority unavailable'):
            self.c.gateway.launch('missing-authorizer','write_file','1',{'path':'owned.txt','text':'never'})
        self.c.interaction.authorize_request=None
        with self.assertRaisesRegex(Blocked,'question action authority unavailable'):
            self.c.interaction.request('unused','unused',{}, {},batch=[])
        self.assertEqual(before,snapshot(self.project,[]))
        self.assertEqual(self.owner.store.db.execute('SELECT COUNT(*) FROM wf_processes').fetchone()[0],0)

    def test_question_node_permission_and_check_node_effect_restrictions_are_not_grants(self):
        from test_interaction import question
        node=next(n for n in self.config['nodes'] if n['id']=='implement');node['permissions'].remove('request_owner_input')
        verify=next(n for n in self.config['nodes'] if n['handler']=='verify');verify['side_effects']=[]
        self.renew();self.c.intake({})
        with self.assertRaisesRegex(Blocked,'known admission gaps') as caught:self.c.authority_check({})
        self.assertIn('node',str(caught.exception))
        task=self.contract['tasks'][0];facts={**self.c.question_binding(task,node,0,'implement'),'session_id':'test-original'}
        with self.assertRaisesRegex(Blocked,'node permission'):
            self.c.interaction.request('unused','q',facts,question(),batch=[{'call':'q','tool':'request_owner_input'}])
        with self.assertRaisesRegex(Blocked,'node effect'):self.c.verification.run_checks(task)
        self.assertEqual(self.owner.store.db.execute('SELECT COUNT(*) FROM wf_checks').fetchone()[0],0)
        self.assertEqual(self.owner.store.db.execute('SELECT COUNT(*) FROM wf_questions').fetchone()[0],0)
