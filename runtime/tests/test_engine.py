"""T001/V1 and V4. Real StateGraph/SqliteSaver; fixture agents are NOT SDK proof."""
from dataclasses import replace
import copy
import hashlib
from importlib.resources import files
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest

from jsonschema import Draft202012Validator, ValidationError
import yaml

from coherence_workflow.engine import Engine, load_workflow
from coherence_workflow.registry import CHECKS, Registry, schemas, validate_schema
from coherence_workflow.store import Authority, Blocked, digest
from fixtures.support import configuration, make_project, right


class ConfigGraphTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.project = make_project(Path(self.tmp.name)/'project')
        self.registry, self.config = configuration(self.project)

    def load(self, config=None):
        return load_workflow(self.registry,yaml.safe_dump(config or self.config),self.project)

    def test_packaged_workflow_fails_closed(self):
        with self.assertRaises(Blocked):
            load_workflow(Registry())

    def test_packaged_eight_reviewed_schemas_and_checks(self):
        inventory = schemas()
        self.assertEqual(len(inventory),8)
        for name,schema in inventory.items():
            Draft202012Validator.check_schema(schema)
            source = Path('specs/003-coordinate-workflow/contracts')/name
            if source.exists(): self.assertEqual(schema,json.loads(source.read_text()))
        self.assertTrue(files('coherence_workflow').joinpath('workflows/coordinate.yaml').is_file())
        self.assertTrue({'workflow.ConfigGraphTests','workflow.CustodyTests',
                         'workflow.LaunchCrashTests','workflow.LedgerCheckpointTests'} <= CHECKS.keys())
        for check in CHECKS.values():
            args={k:v['const'] for k,v in check['schema']['properties'].items()}
            Draft202012Validator(check['schema']).validate(args)
            with self.assertRaises(ValidationError):
                Draft202012Validator(check['schema']).validate(dict(args,selector='not-collected'))

    def test_reviewed_examples_and_closed_versioned_schemas(self):
        source=Path('specs/003-coordinate-workflow/contracts/examples.json')
        self.assertTrue(source.exists())
        cases=json.loads(source.read_text())['cases']
        self.assertGreater(len(cases),0)
        for case in cases:
            validate_schema(case['schema'],case['value'])
            if 'schema_version' in case['value']:
                with self.subTest(schema=case['schema']),self.assertRaises(ValidationError):
                    validate_schema(case['schema'],dict(case['value'],schema_version=999))
            with self.subTest(schema=case['schema']),self.assertRaises(ValidationError):
                validate_schema(case['schema'],dict(case['value'],unregistered_field=True))
        print('T001/V1 reviewed schema examples',len(cases))

    def test_active_config_or_registry_drift_never_adopted(self):
        with Authority(self.project) as authority:
            engine=Engine(authority,'run',self.config,self.registry,self.project)
            try:
                original=self.registry.handlers['choose']
                self.registry.handlers['choose']=replace(original,function=right)
                with self.assertRaisesRegex(Blocked,'drift'): engine.invoke()
                self.registry.handlers['choose']=original
                self.registry.version='changed'
                with self.assertRaisesRegex(Blocked,'drift'): engine.invoke()
                self.registry.version='1'
                engine.config['workflow_id']='changed'
                with self.assertRaisesRegex(Blocked,'drift'): engine.invoke()
            finally: engine.close()

    def test_actual_configured_route_handler_profile_skill_order_and_edges(self):
        hashes=[]
        routes=[]
        for index in range(3):
            config=copy.deepcopy(self.config)
            if index:
                # Supported handler selection changes the actual conditional edge.
                self.registry.handlers['choose-right']=replace(self.registry.handlers['choose'],id='choose-right',function=right)
                next(n for n in config['nodes'] if n['id']=='choose')['handler']='choose-right'
                node=next(n for n in config['nodes'] if n['id']=='work-b')
                node.update(profile='profile-b',skill='skill-b')
                config['nodes'].reverse()  # Definition order is not a second scheduler.
            if index==2:
                # Configured edge order changes actual route, safely after custody.
                next(n for n in config['nodes'] if n['id']=='choose')['transitions']={'left':'work-b','right':'work-a'}
            config=self.load(config)
            root=self.project if index==0 else make_project(Path(self.tmp.name)/('project'+str(index)))
            with Authority(root) as authority:
                engine=Engine(authority,'run',config,self.registry,self.project)
                try:
                    result=engine.invoke()
                    routes.append([v['node'] for v in result['trace']])
                    hashes.append(engine.hash)
                    selected=next(v for v in result['trace'] if v['node'].startswith('work-'))
                    if index==1:
                        self.assertEqual((selected['profile'],selected['skill']),('profile-b','skill-b'))
                    self.assertFalse(engine.graph.get_state(engine.thread).next)
                    print('T001/V1 route',json.dumps({'hash':engine.hash,'trace':result['trace']}))
                finally: engine.close()
        self.assertIn('work-a',routes[0]); self.assertIn('work-b',routes[1]); self.assertIn('work-a',routes[2])
        self.assertEqual(len(set(hashes)),3)

    def test_schema_and_semantic_negatives_before_effects(self):
        mutations=[]
        def add(label,fn):
            c=copy.deepcopy(self.config); fn(c); mutations.append((label,c))
        add('future version',lambda c:c.update(schema_version=2))
        add('unknown root',lambda c:c.update(executable='eval'))
        add('registry version',lambda c:c.update(registry_version='future'))
        add('unknown handler',lambda c:c['nodes'][0].update(handler='eval'))
        add('handler version',lambda c:c['nodes'][0].update(handler_version='2'))
        add('unknown outcome',lambda c:c['nodes'][0].update(outcomes=['invented']))
        add('unknown edge',lambda c:c['nodes'][0]['transitions'].update(ok='missing'))
        add('dead end',lambda c:c['nodes'][0].update(outcomes=[],transitions={}))
        add('cycle',lambda c:c['nodes'][0]['transitions'].update(ok='intake'))
        add('safety bypass',lambda c:c['nodes'][0]['transitions'].update(ok='accepted'))
        add('duplicate id',lambda c:c['nodes'].append(c['nodes'][0]))
        add('unavailable profile',lambda c:c['profiles']['profile-a'].update(model='unapproved'))
        add('unknown agent profile',lambda c:c['nodes'][4].update(profile='missing'))
        add('unknown skill',lambda c:c['nodes'][4].update(skill='missing'))
        add('path traversal',lambda c:c['skills']['skill-a'].update(path='../skill-a.md'))
        add('storage bypass',lambda c:c['storage'].update(checkpoint='other.sqlite'))
        add('permission escalation',lambda c:c['nodes'][4].update(permissions=['write-anything']))
        add('unregistered containment',lambda c:c.update(containment_capability='unavailable'))
        add('retry',lambda c:c['nodes'][0].update(max_retries=1))
        add('interactive unavailable',lambda c:c['interaction'].update(mode='interactive_parent',question_transport='unknown',parent_binding_ref='unknown',question_tool='ask_user'))
        for label,c in mutations:
            with self.subTest(label=label), self.assertRaises((Blocked,ValidationError)):
                self.load(c)
        self.assertFalse((self.project/'.coherence').exists())

    def test_unsafe_yaml_duplicate_alias_tag_and_size(self):
        for raw in ('schema_version: 1\nschema_version: 1\n','a: &alias [1]\nb: *alias\n',
                    '!!python/object/apply:os.system ["touch bad"]','!!map {}','x'*262145):
            with self.subTest(raw=raw[:40]), self.assertRaises((Blocked,ValidationError)):
                load_workflow(self.registry,raw,self.project)

    def test_symlink_and_resource_hash_rejected(self):
        (self.project/'skill-a.md').unlink()
        (self.project/'skill-a.md').symlink_to(self.project/'skill-b.md')
        with self.assertRaises(Blocked): self.load()
        (self.project/'skill-a.md').unlink(); (self.project/'skill-a.md').write_text('changed')
        with self.assertRaises(Blocked): self.load()

    def test_invalid_handler_result_never_becomes_green_cursor(self):
        for result in ({'outcome':'illegal'},{'outcome':'ok','unknown':True}):
            root=make_project(Path(self.tmp.name)/('invalid'+str(len(str(result)))))
            registry,config=configuration(root)
            registry.handlers['intake']=replace(registry.handlers['intake'],function=lambda context:result)
            with Authority(root) as authority:
                engine=Engine(authority,'run',config,registry,root)
                try:
                    with self.assertRaises((Blocked,ValidationError)): engine.invoke()
                    self.assertNotEqual(authority.store.db.execute('SELECT phase FROM wf_operations').fetchone()[0],'completed')
                finally: engine.close()

    def test_registered_handler_actual_input_schema_checked_before_effect(self):
        self.registry.handlers['intake']=replace(self.registry.handlers['intake'],input_schema={
            'type':'object','properties':{'run_id':{'const':'different-run'}},'required':['run_id']})
        with Authority(self.project) as authority:
            engine=Engine(authority,'run',self.config,self.registry,self.project)
            try:
                with self.assertRaises(ValidationError): engine.invoke()
                self.assertEqual(authority.store.db.execute("SELECT count(*) FROM wf_operations WHERE phase='completed'").fetchone()[0],0)
            finally: engine.close()

    def test_engine_constructor_cannot_bypass_validation(self):
        config=copy.deepcopy(self.config)
        config['nodes'][0]['transitions']['ok']='accepted'
        with Authority(self.project) as authority:
            with self.assertRaises(Blocked): Engine(authority,'run',config,self.registry,self.project)
            self.assertEqual(authority.store.db.execute('SELECT count(*) FROM wf_runs').fetchone()[0],0)


class LedgerCheckpointTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.project=make_project(Path(self.tmp.name)/'project')
        self.registry,self.config=configuration(self.project)

    def test_real_saver_restart_application_result_before_checkpoint_once(self):
        code='''
import os,sys
from pathlib import Path
from fixtures.support import configuration
from coherence_workflow.engine import Engine
from coherence_workflow.store import Authority
p=Path(sys.argv[1]); r,c=configuration(p)
def hook(phase,op): os._exit(73)
with Authority(p) as a:
 e=Engine(a,'run',c,r,p,phase_hook=hook); e.invoke()
'''
        proc=subprocess.run([sys.executable,'-c',code,str(self.project)],capture_output=True)
        self.assertEqual(proc.returncode,73,proc.stderr.decode())
        with Authority(self.project) as authority:
            self.assertEqual(authority.store.db.execute("SELECT count(*) FROM wf_operations WHERE phase='completed'").fetchone()[0],1)
            engine=Engine(authority,'run',self.config,self.registry,self.project)
            try:
                before=engine.graph.get_state(engine.thread)
                self.assertTrue(before.next)
                saved=authority.store.db.execute("SELECT * FROM wf_events WHERE kind='completed'").fetchone()
                with authority.store.transaction() as db:
                    db.execute("DELETE FROM wf_events WHERE kind='completed'")
                with self.assertRaisesRegex(Blocked,'ordered application proof'): engine.invoke()
                self.assertEqual(authority.store.db.execute('SELECT count(*) FROM wf_operations').fetchone()[0],1)
                # Restore the exact test-corrupted receipt; production has no such repair shortcut.
                with authority.store.transaction() as db:
                    db.execute('INSERT INTO wf_events VALUES(?,?,?,?,?,?)',tuple(saved))
                result=engine.invoke()
                count=authority.store.db.execute('SELECT count(*) FROM wf_operations').fetchone()[0]
                self.assertEqual(count,len(result['trace']))
                phases=[tuple(r) for r in authority.store.db.execute('SELECT op_id,kind FROM wf_events WHERE op_id IS NOT NULL ORDER BY seq')]
                for op in {r[0] for r in phases}:
                    self.assertEqual([r[1] for r in phases if r[0]==op],['intent','completed'])
                self.assertEqual(engine.invoke(),result)
                self.assertEqual(authority.store.db.execute('SELECT count(*) FROM wf_operations').fetchone()[0],count)
                print('T001/V4 cursor',before.next,'->',engine.graph.get_state(engine.thread).next,'operations',count,'events',len(phases))
            finally: engine.close()

    def test_green_checkpoint_without_application_result_blocks(self):
        with Authority(self.project) as authority:
            engine=Engine(authority,'run',self.config,self.registry,self.project)
            try:
                engine.invoke()
                with authority.store.transaction() as db:
                    db.execute("UPDATE wf_operations SET result=NULL WHERE node_id='intake'")
                with self.assertRaisesRegex(Blocked,'without applicable application proof'): engine.invoke()
            finally: engine.close()

    def test_graph_success_with_missing_route_or_event_evidence_blocks(self):
        with Authority(self.project) as authority:
            engine=Engine(authority,'run',self.config,self.registry,self.project)
            try:
                result=engine.invoke()
                with self.assertRaises(Blocked): engine.audit(dict(result,trace=result['trace'][1:]))
                op=result['trace'][0]['operation_id']
                with authority.store.transaction() as db:
                    db.execute("DELETE FROM wf_events WHERE op_id=? AND kind='completed'",(op,))
                with self.assertRaisesRegex(Blocked,'event proof'): engine.invoke()
            finally: engine.close()

    def test_unique_cas_event_order_settings_and_integrity(self):
        with Authority(self.project) as authority:
            store=authority.store
            store.reserve('run','a')
            op=store.intent('run','node','graph',{}, {})['op_id']
            self.assertEqual(store.intent('run','node','graph',{}, {})['op_id'],op)
            with self.assertRaises(Blocked): store.intent('run','node','graph',{'different':1},{})
            store.transition(op,'intent','completed',{'outcome':'ok'})
            with self.assertRaises(Blocked): store.transition(op,'intent','completed',{'outcome':'ok'})
            with self.assertRaises(sqlite3.IntegrityError), store.transaction() as db:
                db.execute("INSERT INTO wf_events(event_id,run_id,op_id,kind,payload) VALUES('bad','missing',NULL,'bad','{}')")
            self.assertEqual(store.verify_settings(),{'journal_mode':'wal','synchronous':2,'foreign_keys':1,'busy_timeout':5000})
            self.assertEqual(store.db.execute('PRAGMA integrity_check').fetchone()[0],'ok')
            self.assertEqual(store.db.execute('PRAGMA foreign_key_check').fetchall(),[])
            seq=[r[0] for r in store.db.execute('SELECT seq FROM wf_events ORDER BY seq')]
            self.assertEqual(seq,sorted(set(seq)))
            print('T001/V4 settings',store.verify_settings(),'integrity ok; sequences',seq)

    def test_no_application_transaction_during_handler_or_saver(self):
        with Authority(self.project) as authority:
            def handler(context):
                self.assertFalse(authority.store.db.in_transaction)
                connection=sqlite3.connect(authority.database,timeout=0.1)
                try:
                    connection.execute('BEGIN IMMEDIATE'); connection.rollback()
                finally: connection.close()
                return {'outcome':'ok'}
            self.registry.handlers['intake']=replace(self.registry.handlers['intake'],function=handler)
            engine=Engine(authority,'run',self.config,self.registry,self.project)
            try:
                engine.invoke()
                with authority.store.transaction(),self.assertRaises(Blocked): engine.invoke()
            finally: engine.close()


if __name__=='__main__': unittest.main()
