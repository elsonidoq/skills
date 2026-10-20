"""T004 required real crash/reentry, pressure and immutable-version checks."""
import copy
import json
import os
from pathlib import Path
import signal
import sqlite3
import subprocess
import sys
import tempfile
import unittest

import yaml

from coherence_workflow.engine import Engine
from coherence_workflow.intake import approval_scope
from coherence_workflow.store import Authority, Blocked, canonical, digest, git
from coherence_workflow.tools import Gateway, snapshot
from fixtures.support import configuration, make_project
from test_custody import IsolatedCustody
from test_intake import approved_fixture, declare_builtin_actions
from test_pi_adapter import manifest, environment

ROOT=Path(__file__).resolve().parents[2]


def cli_inputs(case):
    case.assertEqual(os.environ.get('COHERENCE_LIVE'),'1','REQUIRED live SDK integration NOT VERIFIED')
    project=case.project
    (project/'second.txt').write_text('initial second');git(project,'add','--','second.txt');git(project,'commit','-qm','isolated second baseline')
    (project/'other.txt').write_text('unrelated staging');git(project,'add','--','other.txt')
    (project/'custom.md').write_text('unrelated custom');(project/'untracked-user').write_text('unrelated')
    (project/'.coherence/workflow').mkdir(parents=True,mode=0o700)
    config=yaml.safe_load((ROOT/'runtime/coherence_workflow/workflows/coordinate.yaml').read_text())
    sdk=manifest(project,tools=False)
    sdk['skills']=[{'path':str(ROOT/'skills/coordinate-implementation/SKILL.md'),'sha256':config['skills']['coordinate']['sha256'],'name':'coordinate-implementation'}]
    sdk['resource_hash']=digest({k:sdk[k] for k in ('skills','tools','permissions','trust','system_prompt')})
    contract,catalog=approved_fixture(project,digest(config))
    contract['authorization_envelope']['profiles']=[config['profiles']['sol-medium']]
    declare_builtin_actions(contract)
    for ref in contract['approval_refs']:
        if ref['gate_kind']=='implementation':ref['scope_hash']=approval_scope(contract,digest(config));catalog[ref['authority_ref']]['scope_hash']=ref['scope_hash']
    values={'workflow.yaml':yaml.safe_dump(config),'tasks.json':canonical(contract),'catalog.json':canonical(catalog),'manifest.json':canonical(sdk)}
    for name,value in values.items():
        path=case.root/name;path.write_text(value);path.chmod(0o600)
    return ['--project',str(project),'--run','sequence','--workflow',str(case.root/'workflow.yaml'),
            '--tasks',str(case.root/'tasks.json'),'--owner-catalog',str(case.root/'catalog.json'),
            '--manifest',str(case.root/'manifest.json'),'--containment',case.parent]


def capture(case,db):
    for row in db.execute('SELECT containment FROM wf_processes WHERE containment IS NOT NULL'):
        receipt=json.loads(row[0])
        if receipt not in case.receipts:case.receipts.append(receipt)


CRASH_GATEWAY=None


def crash_work(context):
    import time
    gateway=CRASH_GATEWAY
    op,process=gateway.launch('crash-tool','fixture','1',{'mode':'survivor_hang','exit':0})
    deadline=time.monotonic()+10
    path=gateway.authority.project/'owned.txt'
    while path.read_text()=='base':
        if time.monotonic()>deadline:raise RuntimeError('fixture tool never wrote')
        time.sleep(.01)
    os.kill(os.getpid(),signal.SIGKILL)


def unreconciled_handler(context,result):
    return False  # An interrupted mutation is deliberately never certified.


class EffectRecoveryTests(IsolatedCustody):
    def test_actual_engine_controller_death_during_write_reentry_alarms_before_replacement(self):
        driver='''
import sys
import test_recovery as fixture
from coherence_workflow.registry import Handler
from fixtures.custody_support import process_tool
with fixture.Authority(sys.argv[1]) as owner:
 registry,config=fixture.configuration(owner.project)
 fixture.CRASH_GATEWAY=fixture.Gateway(owner,'run',sys.argv[2],{'fixture':process_tool(owner.project)})
 registry.handlers['work-a']=Handler('work-a','1','agent','work',('ok',),fixture.crash_work,side_effects=('process',),reconcile=fixture.unreconciled_handler)
 next(n for n in config['nodes'] if n['id']=='work-a')['side_effects']=['process']
 engine=fixture.Engine(owner,'run',config,registry,owner.project)
 engine.invoke()
'''
        process=subprocess.run([sys.executable,'-c',driver,str(self.project),self.parent],capture_output=True,text=True,timeout=30)
        self.assertEqual(process.returncode,-signal.SIGKILL,process.stdout+process.stderr)
        with Authority(self.project) as owner:
            gateway=Gateway(owner,'run',self.parent,{})
            capture(self,owner.store.db)
            count=owner.store.db.execute('SELECT COUNT(*) FROM wf_operations').fetchone()[0]
            results=gateway.recover()
            self.assertTrue(any(r.get('alarm')=='ORPHAN_PROCESS' for r in results))
            with self.assertRaisesRegex(Blocked,'ORPHAN_PROCESS'):owner.store.assert_dispatchable('run')
            self.assertEqual(count,owner.store.db.execute('SELECT COUNT(*) FROM wf_operations').fetchone()[0])
            op=owner.store.db.execute('SELECT op_id FROM wf_processes').fetchone()[0]
            receipt=gateway.resolve(op)
            self.assertEqual(receipt['empty_receipt']['populated'],0)
            partial=(self.project/'owned.txt').read_bytes()
            import time
            time.sleep(.1);self.assertEqual(partial,(self.project/'owned.txt').read_bytes())
            with self.assertRaises(Blocked):owner.store.assert_dispatchable('run')
            print(canonical({'proof':'actual-engine-controller-death-postwrite','exit':process.returncode,'empty':receipt['empty_receipt'],
                             'replacement_allowed':False,'partial_hash':digest(partial.hex())}))
    def test_actual_cli_sdk_post_commit_before_receipt_kill_and_exact_recovery(self):
        args=cli_inputs(self);before=snapshot(self.project,['owned.txt','second.txt'])
        driver='''
import os, signal, sys
from coherence_workflow.git_effects import GitEffects
from coherence_workflow.cli import main, ROOT
# Match the suite launcher's effective loader environment on both sides of death.
os.environ['PYTHONPATH']=str(ROOT/'runtime')+':'+os.environ.get('PYTHONPATH','')
original=GitEffects.checkpoint
def checkpoint(self,*args,**kwargs):
 def fault(phase,op):
  if phase=='commit_before_receipt':os.kill(os.getpid(),signal.SIGKILL)
 return original(self,*args,**kwargs,phase_hook=fault)
GitEffects.checkpoint=checkpoint
sys.exit(main(['start',*sys.argv[1:]]))
'''
        env=dict(os.environ,COHERENCE_PYTHON=sys.executable)
        process=subprocess.run([sys.executable,'-c',driver,*args],env=env,capture_output=True,text=True,timeout=180)
        self.assertEqual(process.returncode,-signal.SIGKILL,process.stdout+process.stderr)
        database=self.project/'.coherence/workflow/workflow.sqlite'
        db=sqlite3.connect(database);db.row_factory=sqlite3.Row
        try:
            capture(self,db)
            partial=git(self.project,'rev-parse','HEAD').decode().strip();self.assertNotEqual(partial,before['head'])
            pending=[r['op_id'] for r in db.execute("SELECT * FROM wf_operations WHERE phase!='completed' ORDER BY op_id")]
            self.assertEqual(len(pending),2)
            self.assertEqual(db.execute("SELECT COUNT(*) FROM wf_events WHERE kind='task_selected'").fetchone()[0],1)
            authority={'action':'reconcile','run_id':'sequence','config_hash':db.execute('SELECT config_hash FROM wf_runs').fetchone()[0],
                'operations':pending,'actor':'current owner via mandatory-isolated-test preapproval',
                'provenance':'owner explicitly preapproved mandatory isolated tests; not production acceptance'}
            path=self.root/'resume-authority.json';path.write_text(canonical(authority));path.chmod(0o600)
            result=subprocess.run([str(ROOT/'scripts/coordinate-implementation'),'resume',*args,'--resume-authority',str(path)],
                                  env=env,capture_output=True,text=True,timeout=180)
            capture(self,db)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            rows=db.execute('SELECT * FROM wf_tasks ORDER BY approved_order').fetchall()
            one,two=[json.loads(row['checkpoint']) for row in rows]
            self.assertEqual(one['sha'],partial);self.assertEqual(two['parent'],partial)
            self.assertEqual(git(self.project,'rev-list','--count',before['head']+'..HEAD').decode().strip(),'2')
            self.assertEqual(db.execute('PRAGMA integrity_check').fetchone()[0],'ok')
            self.assertEqual(db.execute("SELECT COUNT(*) FROM wf_operations WHERE phase!='completed'").fetchone()[0],0)
            for name,value in before['files'].items():
                if name not in ('owned.txt','second.txt'):self.assertEqual(value,snapshot(self.project,[])['files'][name])
            print(canonical({'proof':'actual-cli-sdk-postcommit-reentry','killed_exit':process.returncode,'resume_exit':result.returncode,
                             'before':before['head'],'recovered':one['sha'],'head':two['sha'],'pending_before':pending,'authority':authority}))
        finally:db.close()

    def test_actual_hook_mutation_prevents_receipt_and_recovery(self):
        from coherence_workflow.git_effects import GitEffects, reconcile_checkpoint
        hook=self.project/'.git/hooks/pre-commit';hook.write_text('#!/bin/sh\nprintf hook-mutation > owned.txt\n');hook.chmod(0o700)
        with Authority(self.project) as owner:
            owner.store.reserve('run',digest('fixture'))
            gateway=Gateway(owner,'run',self.parent,{})
            baseline=snapshot(self.project,['owned.txt'])
            (self.project/'owned.txt').write_text('approved bytes')
            task={'id':'A','owned_paths':['owned.txt'],'required':[{'id':'A/V1'}]}
            try:
                with self.assertRaises(Blocked):GitEffects(owner,'run',gateway).checkpoint(task,baseline,[{'item_id':'A/V1','status':'satisfied'}],gates_satisfied=True)
                op=owner.store.db.execute("SELECT op_id FROM wf_operations WHERE kind='git-checkpoint'").fetchone()[0]
                with self.assertRaises(Blocked):reconcile_checkpoint(owner,op)
                self.assertEqual((self.project/'owned.txt').read_text(),'hook-mutation')
            finally:capture(self,owner.store.db)

    def test_actual_engine_application_result_before_saver_once(self):
        from test_engine import LedgerCheckpointTests
        case=LedgerCheckpointTests('test_real_saver_restart_application_result_before_checkpoint_once')
        result=unittest.TestResult();case.run(result)
        self.assertEqual(result.testsRun,1);self.assertTrue(result.wasSuccessful(),result.errors+result.failures)


class PressureRecoveryTests(IsolatedCustody):
    def test_actual_host_death_and_abort_drain_paths_remain_closed(self):
        from test_pi_adapter import LifecycleTests
        for name in ('test_live_abort_drain_current_prompt_tool_and_host_death',
                     'test_live_host_death_survivor_alarm_then_gateway_drain'):
            case=LifecycleTests(name);result=unittest.TestResult();case.run(result)
            self.assertTrue(result.wasSuccessful(),result.errors+result.failures)
            self.assertFalse(result.skipped)

    def test_actual_sdk_compaction_summary_retry_guard(self):
        from test_pi_adapter import BindingTests
        case=BindingTests('test_live_actual_shipped_compaction_and_retry');result=unittest.TestResult();case.run(result)
        self.assertEqual(result.testsRun,1);self.assertTrue(result.wasSuccessful(),result.errors+result.failures);self.assertFalse(result.skipped)

    def test_saved_role_safe_conversation_actual_new_host_reopen(self):
        from test_pi_adapter import BindingTests
        case=BindingTests('test_live_exact_skill_tools_two_turns_and_saved_conversation_open');result=unittest.TestResult();case.run(result)
        self.assertEqual(result.testsRun,1);self.assertTrue(result.wasSuccessful(),result.errors+result.failures);self.assertFalse(result.skipped)


class VersionRecoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.project=make_project(self.root/'project')

    def test_real_sqlite_backup_wal_snapshot_and_pending_boundary(self):
        with Authority(self.project) as owner:
            owner.store.reserve('run',digest('config'))
            op=owner.store.intent('run','one','test',{},{});
            auth={'action':'sqlite-backup','database':str(owner.database)}
            with self.assertRaises(Blocked):owner.store.backup(self.root/'not-settled.sqlite',authorization=auth)
            owner.store.transition(op['op_id'],'intent','completed',{'actual':'WAL fact'})
            backup=owner.store.backup(self.root/'backup.sqlite',authorization=auth)
            target=sqlite3.connect(backup['path'])
            self.assertEqual(target.execute('PRAGMA integrity_check').fetchone()[0],'ok')
            self.assertEqual(target.execute('SELECT COUNT(*) FROM wf_events').fetchone()[0],3);target.close()
            print('SQLite backup',canonical(backup))

    def test_changed_resource_and_authority_refused_at_attempt_admission(self):
        registry,config=configuration(self.project)
        with Authority(self.project) as owner:
            engine=Engine(owner,'run',config,registry,self.project,input_identity={'contract':'original'})
            engine.invoke();engine.close()
            with self.assertRaisesRegex(Blocked,'incompatible'):
                Engine(owner,'run',config,registry,self.project,input_identity={'contract':'changed'})
            (self.project/'skill-a.md').write_text('changed resource')
            with self.assertRaisesRegex(Blocked,'drift'):
                Engine(owner,'run',config,registry,self.project,input_identity={'contract':'original'})

    def test_future_schema_rejected_without_downgrade_or_deserialization(self):
        root=self.project/'.coherence/workflow';root.mkdir(parents=True,mode=0o700)
        path=root/'workflow.sqlite';db=sqlite3.connect(path);db.execute('CREATE TABLE wf_meta(version INTEGER)');db.execute('INSERT INTO wf_meta VALUES(99)');db.commit();db.close();path.chmod(0o600)
        before=path.read_bytes()
        with self.assertRaisesRegex(Blocked,'unsupported application schema'):Authority(self.project)
        self.assertEqual(before,path.read_bytes())
