"""T003/V1 structured-origin provenance and exact retained contracts."""
import copy
import json
from pathlib import Path
import tempfile
import unittest

from coherence_workflow.intake import Approvals, admit, approval_scope, content_hash
from coherence_workflow.store import Blocked, digest
from fixtures.support import make_project


def declare_builtin_actions(contract):
    """Explicit current mandatory-test authority only; never historical conversion."""
    from coherence_workflow.authority import action_requirement
    names={'read_file','search_file','run_check','request_owner_input'}
    if any(t['owned_paths'] for t in contract['tasks']):names.update(('write_file','edit_file','runner-git-commit'))
    names.update(i['check']['id'] for t in contract['tasks'] for i in t['required'])
    contract['authorization_envelope']['capabilities']=[{'id':name,**action_requirement(contract,name)} for name in sorted(names)]


def approved_fixture(project, config_hash, origin='TinySpec'):
    kinds = ['spec','plan','tasks','review'] if origin == 'Standard' else ['source','tasks']
    sources = []
    for kind in kinds:
        path = project / ('input-' + kind + '.json')
        path.write_text(json.dumps({'kind':kind,'scope':'isolated mandatory test only'}))
        sources.append({'path':path.name,'section':None,'sha256':content_hash(path),'kind':kind})
    def task(id, order, depends, path, text):
        return {'id':id,'order':order,'outcome':'Read '+path+' then replace its complete bytes with exactly '+repr(text),
            'depends':depends,'context_group':'story','owned_paths':[path], 'authorization_envelope_id':'isolated',
            'required':[{'id':id+'/V1','criterion':'Exact authorized file bytes','check':{'id':'workflow.FileBytes','version':'1',
                'args':{'path':path,'expected':text}},'pass_condition':'exact byte oracle exits 0','expected_evidence':'real file oracle',
                'producer_dependencies':depends,'gates':[]}], 'optional':[], 'gates':[]}
    contract = {'schema_version':1,'origin':origin,'legacy_origin':'documented-structured-v1' if origin=='legacy' else None,
        'sources':sources,'approval_refs':[], 'tasks':[task('A',0,[],'owned.txt','first\n'),task('B',1,['A'],'second.txt','second\n')],
        'execution_intent':{'model_class':'Sol','effort':'medium','resolution':'resolved',
            'assumptions':['Bounded exact-byte fixture; all acceptance and safety gates retained'],
            'provenance':'Current isolated-test authority; synthetic planning intent, not historical production approval',
            'decomposition_rationale':'Explicit file bytes and dependency order; routine editing choices remain open',
            'compatible_bindings':[{'provider':'openai-codex','model':'gpt-6.1-sol','effort':'medium',
                'assessment':'Exact owner-selected isolated implementation binding; no capability ranking inferred',
                'provenance':'Current owner preapproval for mandatory isolated tests'}]},
        'authorization_envelope':{'id':'isolated','approval_refs':[],'profiles':[],
            'capabilities':[], 'limits':[], 'external_paid_authority':'denied'}}
    catalog = {}
    for kind in {'TinySpec':['combined','implementation'],'Standard':['specification','overall','implementation'],
                 'legacy':['legacy','implementation']}[origin]:
        path = project / ('owner-' + kind + '.txt')
        path.write_text('TEST AUTHORITY: mandatory isolated fixture scope. Current owner preapproved isolated tests; not production acceptance.\n')
        scope = (next(s['sha256'] for s in sources if s['kind']=='spec') if kind=='specification' else
                 approval_scope(contract,config_hash) if kind=='implementation' else digest(sources))
        ref = {'gate_kind':kind,'record_ref':path.name,'record_sha256':content_hash(path),'scope_hash':scope,
               'actor':'fixture catalog: current owner isolated-test preapproval','authority_ref':'external-owner/'+kind,'action':'approve'}
        contract['approval_refs'].append(ref)
        catalog[ref['authority_ref']] = {k:ref[k] for k in ('actor','record_ref','record_sha256','scope_hash','gate_kind','action')}
    declare_builtin_actions(contract)
    for ref in contract['approval_refs']:
        if ref['gate_kind']=='implementation':
            ref['scope_hash']=approval_scope(contract,config_hash)
            catalog[ref['authority_ref']]['scope_hash']=ref['scope_hash']
    return contract, catalog


class OriginIntakeTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.project=make_project(Path(self.temp.name)/'project')

    def test_both_adapters_losslessly_preserve_whole_task_fields(self):
        outputs=[]
        for origin in ('TinySpec','Standard'):
            contract,catalog=approved_fixture(self.project,'config',origin)
            normalized,receipt=admit(self.project,contract,Approvals(self.project,catalog),'config')
            self.assertEqual(normalized,contract)
            self.assertEqual(receipt['task_ids'],['A','B'])
            self.assertEqual(receipt['contract_hash'],digest(contract))
            outputs.append(normalized['tasks'])
        self.assertEqual(outputs[0],outputs[1])

    def test_actual_cli_both_origin_receipts(self):
        import os
        import subprocess
        import sys
        root=Path(__file__).resolve().parents[2]
        for origin in ('TinySpec','Standard'):
            contract,catalog=approved_fixture(self.project,'config',origin)
            tasks=Path(self.temp.name)/'tasks.json';tasks.write_text(json.dumps(contract))
            catalog_path=Path(self.temp.name)/'catalog.json';catalog_path.write_text(json.dumps(catalog));catalog_path.chmod(0o600)
            result=subprocess.run([str(root/'scripts/coordinate-implementation'),'intake','--project',str(self.project),
                '--tasks',str(tasks),'--owner-catalog',str(catalog_path),'--config-hash','config'],
                env=dict(os.environ,COHERENCE_PYTHON=sys.executable),capture_output=True,text=True,timeout=20)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            receipt=json.loads(result.stdout)
            self.assertEqual(receipt['contract_hash'],digest(contract));self.assertEqual(receipt['task_ids'],['A','B'])
            print(origin,'actual CLI intake',result.returncode,result.stdout)

    def test_missing_denied_cancelled_stale_ambiguous_origin_approvals_block(self):
        for origin in ('TinySpec','Standard','legacy'):
            contract,catalog=approved_fixture(self.project,'config',origin)
            for kind in [r['gate_kind'] for r in contract['approval_refs']]:
                bad=copy.deepcopy(contract); bad['approval_refs']=[r for r in bad['approval_refs'] if r['gate_kind']!=kind]
                with self.assertRaises(Blocked): admit(self.project,bad,Approvals(self.project,catalog),'config',legacy_settled=True)
            for action in ('deny','cancel'):
                bad=copy.deepcopy(contract);bad['approval_refs'][0]['action']=action
                with self.assertRaises(Blocked):admit(self.project,bad,Approvals(self.project,catalog),'config',legacy_settled=True)
            with self.assertRaises(Blocked):admit(self.project,contract,Approvals(self.project,catalog),'changed',legacy_settled=True)
            bad=copy.deepcopy(contract);bad['approval_refs'].append(bad['approval_refs'][0])
            with self.assertRaises(Blocked):admit(self.project,bad,Approvals(self.project,catalog),'config',legacy_settled=True)

    def test_legacy_requires_settled_known_writer_and_retains_origin(self):
        contract,catalog=approved_fixture(self.project,'config','legacy')
        with self.assertRaises(Blocked):admit(self.project,contract,Approvals(self.project,catalog),'config')
        normalized,_=admit(self.project,contract,Approvals(self.project,catalog),'config',legacy_settled=True)
        self.assertEqual(normalized['legacy_origin'],'documented-structured-v1')

    def test_forward_dependency_stale_source_and_inadequate_contract_block(self):
        contract,catalog=approved_fixture(self.project,'config')
        bad=copy.deepcopy(contract);bad['tasks'][0]['depends']=['B']
        with self.assertRaises(Blocked):admit(self.project,bad,Approvals(self.project,catalog),'config')
        (self.project/contract['sources'][0]['path']).write_text('stale')
        with self.assertRaises(Blocked):admit(self.project,contract,Approvals(self.project,catalog),'config')
        bad=copy.deepcopy(contract);del bad['tasks'][0]['required'][0]['pass_condition']
        with self.assertRaises(Exception):admit(self.project,bad,Approvals(self.project,catalog),'config')


class ExecutionIntentTests(unittest.TestCase):
    setUp = OriginIntakeTests.setUp
    def test_missing_intent_returns_precise_producing_renewal(self):
        contract,catalog=approved_fixture(self.project,'config')
        contract.pop('execution_intent',None)
        with self.assertRaisesRegex(Blocked,'execution intent.*producing'):
            admit(self.project,contract,Approvals(self.project,catalog),'config')

    def test_binding_is_explicit_not_inferred_from_planner_or_reviewer(self):
        from coherence_workflow.intake import verify_execution_intent
        contract,_=approved_fixture(self.project,'config')
        profile={'provider':'openai-codex','model':'gpt-6.1-sol','effort':'medium'}
        verify_execution_intent(contract,[profile])
        for update in ({'model':'different'},{'effort':'low'}):
            with self.assertRaisesRegex(Blocked,'compatibility.*producing'):
                verify_execution_intent(contract,[{**profile,**update}])
        contract['execution_intent']['resolution']='unresolved'
        with self.assertRaisesRegex(Blocked,'unresolved.*producing'):
            verify_execution_intent(contract,[profile])

    def test_authority_consumer_checks_only_execution_roles_before_other_effects(self):
        from coherence_workflow.cli import Coordinate
        from types import SimpleNamespace
        contract,_=approved_fixture(self.project,'config')
        exact={'provider':'openai-codex','model':'gpt-6.1-sol','effort':'medium'}
        fake=SimpleNamespace(contract=contract,config={'profiles':{'coding':exact,
            'reviewer':dict(exact,model='different-reviewer')},'nodes':[
                {'type':'agent','role':'implement','profile':'coding'},
                {'type':'agent','role':'repair','profile':'coding'},
                {'type':'agent','role':'review','profile':'reviewer'}]})
        # Past intent validation the next ordinary authority dependency is deliberately absent.
        with self.assertRaises(AttributeError):Coordinate.authority_check(fake,{})
        fake.config['profiles']['coding']=dict(exact,effort='low')
        with self.assertRaisesRegex(Blocked,'compatibility.*producing'):
            Coordinate.authority_check(fake,{})
