"""T001/V2,V3: real Git/locks/gated processes and approved cgroup-v2 crash checks.

No skip/fallback: COHERENCE_TEST_CGROUP_PARENT must name an approved delegated parent.
Every killed cgroup is an exact UUID own child. An independent outside sentinel survives.
"""
import copy
from dataclasses import replace
import json
import os
from pathlib import Path
import signal
import sqlite3
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

from coherence_workflow.containment import Cgroup, process_identity, validate_process
from coherence_workflow.store import Authority, Blocked, canonical, digest, git, safe_path
from coherence_workflow.tools import Gateway, clean_owned, reconcile, snapshot
from fixtures.support import make_project
from fixtures.custody_support import process_tool


class IsolatedCustody(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.project=make_project(self.root/'project')
        self.parent=os.environ.get('COHERENCE_TEST_CGROUP_PARENT')
        self.assertTrue(self.parent,'REQUIRED process capability not supplied; NOT VERIFIED')
        self.capability=Cgroup(self.parent)
        self.receipts=[]
        self.sentinel=subprocess.Popen(['/usr/bin/sleep','120'])
        self.sentinel_identity=process_identity(self.sentinel.pid,'outside-sentinel')
        self.addCleanup(self.cleanup_scopes)
        self.outside=self.root/'outside.txt'; self.outside.write_text('outside unchanged')

    def cleanup_scopes(self):
        errors=[]
        for receipt in reversed(self.receipts):
            try:
                path=Path(receipt['parent'])/receipt['name']
                if path.exists():
                    self.capability.drain(receipt); self.capability.remove(receipt)
            except Exception as exc: errors.append(str(exc))
        self.assertIsNone(self.sentinel.poll(),'outside sentinel killed')
        validate_process(self.sentinel_identity,'outside-sentinel')
        self.sentinel.terminate(); self.sentinel.wait(timeout=5)
        self.assertEqual(self.outside.read_text(),'outside unchanged')
        if errors: self.fail('; '.join(errors))

    def gateway(self,authority):
        authority.store.reserve('run','fixture')
        return Gateway(authority,'run',self.parent,{'fixture':process_tool(self.project)})

    def capture(self,phase,op,authority):
        row=authority.store.db.execute('SELECT * FROM wf_processes WHERE op_id=?',(op,)).fetchone()
        if row['containment']:
            receipt=json.loads(row['containment'])
            if receipt not in self.receipts: self.receipts.append(receipt)

    def launch(self,authority,mode='quick',exit=0,hook=None):
        gateway=self.gateway(authority)
        def observe(phase,op):
            self.capture(phase,op,authority)
            if hook: hook(phase,op,gateway)
        op,proc=gateway.launch('tool','fixture','1',{'mode':mode,'exit':exit},observe)
        return gateway,op,proc

    def wait_partial(self):
        deadline=time.monotonic()+5
        while self.project.joinpath('owned.txt').read_text()=='base':
            if time.monotonic()>deadline: self.fail('actual tool did not write')
            time.sleep(.01)


class CustodyTests(IsolatedCustody):
    def test_real_child_controls_identity_and_kernel_empty(self):
        name=self.capability.reserve_name()
        self.capability.create(name)
        receipt=self.capability.receipt(name); self.receipts.append(receipt)
        self.capability.validate(receipt)
        self.assertEqual(self.capability.populated(receipt),0)
        empty=self.capability.drain(receipt)
        self.assertEqual(empty['populated'],0)
        print('T001/V2 own-child capability',json.dumps(empty))

    def test_two_processes_different_run_roots_one_authority_and_parked_reservation(self):
        with Authority(self.project,'runs/a') as authority:
            authority.store.reserve('original','hash')
            code='''
import sys
from coherence_workflow.store import Authority,Blocked
try:
 with Authority(sys.argv[1],'runs/b') as a: a.store.reserve('other','hash')
except Blocked: sys.exit(42)
sys.exit(0)
'''
            other=subprocess.run([sys.executable,'-c',code,str(self.project)],capture_output=True)
            self.assertEqual(other.returncode,42,other.stderr.decode())
            authority.store.park('original')
        with Authority(self.project,'runs/b') as authority:
            self.assertEqual(authority.database,self.project/'.coherence/workflow/workflow.sqlite')
            with self.assertRaisesRegex(Blocked,'reservation'): authority.store.reserve('other','hash')
            authority.store.reserve('original','hash')
            with self.assertRaises(Blocked): authority.store.assert_dispatchable('original')

    def test_authority_binding_lock_and_symlink_storage_replacement_block(self):
        with Authority(self.project) as authority:
            path=authority.lock_path
            path.rename(path.with_suffix('.old'))
            path.write_text('replacement'); path.chmod(0o600)
            with self.assertRaises(Blocked): authority.assert_held()
        with Authority(self.project) as authority:
            database=authority.database
            database.rename(database.with_suffix('.old'))
            database.symlink_to(self.outside)
            with self.assertRaises(Blocked): authority.assert_held()
        with self.assertRaises(Blocked): Authority(self.project)
        self.assertEqual(self.outside.read_text(),'outside unchanged')

    def test_containment_invalid_uid_device_inode_name_parent_boot_and_controls(self):
        name=self.capability.reserve_name(); self.capability.create(name)
        receipt=self.capability.receipt(name); self.receipts.append(receipt)
        mutations={'uid':-1,'device':-1,'inode':-1,'name':'../paseo.service','parent':'/sys/fs/cgroup',
                   'parent_identity':{},'boot':'other-boot'}
        for key,value in mutations.items():
            with self.subTest(key=key),self.assertRaises(Blocked):
                self.capability.drain(dict(receipt,**{key:value}))
        access=os.access
        with patch('coherence_workflow.containment.os.access',side_effect=lambda p,m:False if Path(p).name=='cgroup.kill' else access(p,m)):
            with self.assertRaisesRegex(Blocked,'control'): self.capability.validate(receipt)
        path=self.capability.validate(receipt)
        path.rmdir(); path.mkdir()
        # Kernel inode replacement must never authorize the old receipt.
        with self.assertRaises(Blocked): self.capability.validate(receipt)
        self.receipts.remove(receipt); self.receipts.append(self.capability.receipt(name))

    def test_process_boot_pid_start_nonce_uid_parent_identity_denials(self):
        identity=process_identity(self.sentinel.pid,'test')
        for key,value in {'boot':'wrong','pid':99999999,'start':'0','nonce':'wrong','uid':-1,'ppid':-1}.items():
            with self.subTest(key=key),self.assertRaises(Blocked): validate_process(dict(identity,**{key:value}),'test')

    def test_paths_dirty_owned_overlap_and_unrelated_drift_block(self):
        for name in ('../outside.txt','/tmp/outside','.git/config','.coherence/workflow/workflow.sqlite'):
            with self.subTest(name=name),self.assertRaises(Blocked): snapshot(self.project,[name])
        (self.project/'owned.txt').write_text('preexisting dirty')
        with Authority(self.project) as authority:
            with self.assertRaisesRegex(Blocked,'overlap'): self.launch(authority)
            self.assertEqual(authority.store.db.execute('SELECT count(*) FROM wf_operations').fetchone()[0],0)
        (self.project/'owned.txt').unlink(); (self.project/'owned.txt').symlink_to(self.outside)
        with self.assertRaises(Blocked): snapshot(self.project,['owned.txt'])
        (self.project/'owned.txt').unlink(); (self.project/'owned.txt').write_text('base')
        baseline=snapshot(self.project,['owned.txt'])
        (self.project/'custom.md').write_text('unknown drift')
        with self.assertRaisesRegex(Blocked,'unrelated'): reconcile(self.project,['owned.txt'],baseline)

    def test_eof_before_gated_release_executes_no_tool(self):
        for phase in ('spawned','identity_observed','registered','release_persisted'):
            # Each case uses a fresh worktree and durable run; no unknown-work adoption.
            if phase!='spawned': self.project=make_project(self.root/phase)
            def hook(observed,op,gateway):
                if observed==phase: raise Blocked('test closes release pipe')
            with Authority(self.project) as authority:
                with self.assertRaises(Blocked): self.launch(authority,hook=hook)
                time.sleep(.1)
                self.assertEqual((self.project/'owned.txt').read_text(),'base')
                gateway=self.gateway(authority)
                if phase in ('spawned','identity_observed'):
                    with self.assertRaisesRegex(Blocked,'unregistered'): gateway.recover()
                else:
                    gateway.recover()
                    self.assertFalse(authority.store.db.execute("SELECT 1 FROM wf_operations WHERE phase!='completed'").fetchone())

    def test_invalid_durable_registration_denies_release_without_tool_effect(self):
        for field,value in {'pid':99999999,'start':'wrong','boot':'wrong','uid':-1,'ppid':-1,'nonce':'wrong'}.items():
            self.project=make_project(self.root/('invalid-'+field))
            def hook(phase,op,gateway):
                if phase=='registered':
                    row=gateway.store.db.execute('SELECT identity FROM wf_processes WHERE op_id=?',(op,)).fetchone()
                    identity=json.loads(row[0]); identity[field]=value
                    with gateway.store.transaction() as db:
                        db.execute('UPDATE wf_processes SET identity=? WHERE op_id=?',(canonical(identity),op))
            with Authority(self.project) as authority:
                with self.assertRaises(Blocked): self.launch(authority,hook=hook)
                self.assertEqual((self.project/'owned.txt').read_text(),'base')
                self.assertEqual(authority.store.db.execute("SELECT count(*) FROM wf_events WHERE kind='released'").fetchone()[0],0)

    def test_same_bytes_inode_replacement_and_unrelated_drift_before_release_deny(self):
        for mode in ('owned-inode','unrelated'):
            self.project=make_project(self.root/mode)
            def hook(phase,op,gateway):
                if phase=='registered':
                    if mode=='owned-inode':
                        temp=self.project/'replacement'; temp.write_text('base'); temp.replace(self.project/'owned.txt')
                    else: (self.project/'custom.md').write_text('drift')
            with Authority(self.project) as authority:
                with self.assertRaises(Blocked): self.launch(authority,hook=hook)
                self.assertEqual((self.project/'owned.txt').read_text(),'base')
                self.assertEqual(authority.store.db.execute("SELECT count(*) FROM wf_events WHERE kind='released'").fetchone()[0],0)

    def test_dirty_index_untracked_state_custom_and_outside_preserved(self):
        (self.project/'other.txt').write_text('staged unrelated')
        git(self.project,'add','--','other.txt')
        (self.project/'other.txt').write_text('unstaged unrelated too')
        (self.project/'untracked.txt').write_text('user untracked')
        before=snapshot(self.project,['owned.txt'])
        with Authority(self.project) as authority:
            gateway,op,proc=self.launch(authority)
            self.assertFalse(authority.store.db.in_transaction)
            self.assertEqual(proc.wait(timeout=5),0)
            result=gateway.settle(op,0)
            self.assertTrue(result['replacement_allowed'])
            self.assertEqual(result['empty_receipt']['populated'],0)
            self.assertEqual(gateway.resolve(op),result)
            self.assertEqual(result['reconciliation'],reconcile(self.project,['owned.txt'],before))
            phases=[r[0] for r in authority.store.db.execute('SELECT kind FROM wf_events WHERE op_id=? ORDER BY seq',(op,))]
            self.assertEqual(phases,['intent','contained','prepared','released','completed'])
            for name in ('other.txt','untracked.txt','STATE.md','custom.md'):
                self.assertEqual(result['reconciliation']['files'][name],before['files'][name])
            print('T001/V2 real tool phase receipts',phases,'empty',result['empty_receipt'])


class LaunchCrashTests(IsolatedCustody):
    def test_controller_sigkill_all_distinct_launch_boundaries_and_restart(self):
        phases=('intent','child_created','identity_persisted','spawned','identity_observed','registered','release_persisted','released')
        controller=Path(__file__).with_name('fixtures')/'crash_controller.py'
        for phase in phases:
            with self.subTest(phase=phase):
                self.project=make_project(self.root/phase)
                log=self.root/(phase+'.jsonl')
                proc=subprocess.run([sys.executable,str(controller),str(self.project),self.parent,phase,str(log),'hang'],capture_output=True,timeout=15)
                self.assertEqual(proc.returncode,-signal.SIGKILL,proc.stderr.decode())
                traces=[json.loads(line) for line in log.read_text().splitlines()]
                for item in traces:
                    receipt=item['test_receipt']
                    if receipt and receipt not in self.receipts:self.receipts.append(receipt)
                with Authority(self.project,'different-run-root') as authority:
                    gateway=self.gateway(authority)
                    with self.assertRaises(Blocked): authority.store.assert_dispatchable('run')
                    if phase in ('intent','child_created','identity_persisted','spawned','identity_observed'):
                        with self.assertRaisesRegex(Blocked,'unidentified|unregistered'): gateway.recover()
                        self.assertEqual((self.project/'owned.txt').read_text(),'base')
                    else:
                        # EOF safely stops unreleased helper; a released tool may survive controller death.
                        time.sleep(.15)
                        outcomes=gateway.recover()
                        if phase=='released':
                            self.assertEqual(outcomes[0]['alarm'],'ORPHAN_PROCESS')
                            result=gateway.resolve(traces[-1]['op'])
                            self.assertEqual(result['empty_receipt']['populated'],0)
                            self.assertEqual(authority.store.db.execute('SELECT state FROM wf_alarms').fetchone()[0],'resolved')
                        else:
                            self.assertEqual((self.project/'owned.txt').read_text(),'base')
                            self.assertEqual(outcomes[0]['empty_receipt']['populated'],0)
                    print('T001/V3 SIGKILL boundary',phase,'SQL phases',[r[0] for r in authority.store.db.execute('SELECT kind FROM wf_events ORDER BY seq')], 'trace',traces[-1])

    def test_exit0_exit1_and_killed_worker_with_survivors_alarm_before_replacement(self):
        for label,exit in (('exit0',0),('exit1',1),('hostkill',0)):
            with self.subTest(label=label):
                self.project=make_project(self.root/label)
                with Authority(self.project) as authority:
                    gateway,op,proc=self.launch(authority,'survivor_hang' if label=='hostkill' else 'survivor',exit)
                    if label=='hostkill':
                        self.wait_partial()
                        row=authority.store.db.execute('SELECT identity,containment FROM wf_processes WHERE op_id=?',(op,)).fetchone()
                        identity=json.loads(row['identity']); validate_process(identity,json.loads(authority.store.operation(op)['intent'])['nonce'])
                        # Kill only the registered worker; its setsid child remains in owned containment.
                        deadline=time.monotonic()+5
                        while 'child' not in (self.project/'owned.txt').read_text():
                            if time.monotonic()>deadline: self.fail('surviving child not observed')
                            time.sleep(.01)
                        os.kill(proc.pid,signal.SIGKILL)
                        exit=proc.wait(timeout=5)
                    else:
                        self.assertEqual(proc.wait(timeout=5),exit)
                    result=gateway.settle(op,exit)
                    self.assertEqual(result,{'outcome':'blocked','alarm':'ORPHAN_PROCESS','replacement_allowed':False})
                    with self.assertRaisesRegex(Blocked,'replacement_allowed=false'): authority.store.assert_dispatchable('run')
                    with self.assertRaises(Blocked): gateway.launch('replacement','fixture','1',{'mode':'quick','exit':0})
                    alarm=dict(authority.store.db.execute('SELECT * FROM wf_alarms').fetchone())
                    self.assertEqual(alarm['state'],'active')
                    # Empty alone is insufficient: make actual unrelated drift and ensure alarm remains active.
                    gateway.containment.drain(json.loads(authority.store.db.execute('SELECT containment FROM wf_processes WHERE op_id=?',(op,)).fetchone()[0]))
                    (self.project/'custom.md').write_text('drift')
                    with self.assertRaisesRegex(Blocked,'unrelated'): gateway.resolve(op)
                    self.assertEqual(authority.store.db.execute('SELECT state FROM wf_alarms').fetchone()[0],'active')
                    (self.project/'custom.md').write_text('custom')
                    resolved=gateway.resolve(op)
                    self.assertEqual(resolved['empty_receipt']['populated'],0)
                    self.assertFalse(resolved['task_accepted'])
                    self.assertEqual(authority.store.db.execute('SELECT state FROM wf_alarms').fetchone()[0],'resolved')
                    self.assertEqual(authority.store.db.execute("SELECT count(*) FROM wf_events WHERE kind='ORPHAN_PROCESS'").fetchone()[0],1)
                    print('T001/V3 survivor',label,'alarm',alarm,'resolution',resolved['empty_receipt'])

    def test_helper_killed_before_and_after_release(self):
        for boundary in ('spawned','identity_observed','registered','release_persisted','released'):
            self.project=make_project(self.root/('helper-'+boundary))
            captured=[]
            def hook(phase,op,gateway):
                if phase==boundary:
                    row=gateway.store.db.execute('SELECT containment FROM wf_processes WHERE op_id=?',(op,)).fetchone()
                    receipt=json.loads(row[0])
                    if phase=='released': self.wait_partial()
                    if phase=='spawned':
                        deadline=time.monotonic()+5
                        while not gateway.containment.populated(receipt):
                            if time.monotonic()>deadline: self.fail('helper did not join owned child')
                            time.sleep(.005)
                    gateway.containment.drain(receipt)
                    captured.append(op)
            with Authority(self.project) as authority:
                if boundary in ('spawned','identity_observed','registered'):
                    with self.assertRaises((Blocked,ProcessLookupError,BrokenPipeError)):
                        self.launch(authority,'hang',hook=hook)
                else:
                    try:
                        gateway,op,proc=self.launch(authority,'hang',hook=hook)
                        proc.wait(timeout=5)
                    except (Blocked,BrokenPipeError): pass
                self.assertTrue(captured)
                if boundary!='released': self.assertEqual((self.project/'owned.txt').read_text(),'base')
                identity=authority.store.db.execute('SELECT identity FROM wf_processes WHERE op_id=?',(captured[0],)).fetchone()[0]
                if not identity:
                    with self.assertRaises(Blocked): self.gateway(authority).recover()
                else: self.gateway(authority).recover()
                # An already-buffered valid identity may be registered after helper death;
                # only EOF/failed release follows, and no tool can execute before registration.
                print('T001/V3 helper killed at',boundary,'zero premature tool effect',boundary!='released',
                      'registered_receipt',bool(identity))

    def test_idle_host_scope_is_not_task_tool_orphan(self):
        with Authority(self.project) as authority:
            gateway,op,proc=self.launch(authority,'hang')
            self.wait_partial()
            with authority.store.transaction() as db:
                db.execute("UPDATE wf_processes SET scope_kind='host' WHERE op_id=?",(op,))
            self.assertEqual(gateway.settle(op,None)['outcome'],'idle_host')
            self.assertEqual(authority.store.db.execute('SELECT count(*) FROM wf_alarms').fetchone()[0],0)
            gateway.resolve(op); proc.wait(timeout=5)


if __name__=='__main__': unittest.main()


class HelperPackageBindingTests(IsolatedCustody):
    def test_actual_contained_helper_ignores_local_package_and_caller_import_path(self):
        from unittest.mock import patch
        original=Path.cwd()
        for label in ('unset','conflicting'):
            self.project=make_project(self.root/label)
            shadow=self.project/'coherence_workflow';shadow.mkdir()
            marker=self.project/'SHADOW_HELPER'
            (shadow/'__init__.py').write_text('from pathlib import Path\nPath('+repr(str(marker))+').write_text("uncontained shadow")\n')
            (shadow/'tool_process.py').write_text('raise SystemExit(42)\n')
            with Authority(self.project) as owner:
                env=dict(os.environ)
                if label=='unset':env.pop('PYTHONPATH',None)
                else:env['PYTHONPATH']=str(self.project)
                try:
                    os.chdir(self.project)
                    with patch.dict(os.environ,env,clear=True):
                        gateway,op,process=self.launch(owner)
                    result=gateway.settle(op,process.wait(timeout=10))
                    self.assertTrue(result['replacement_allowed']);self.assertEqual(result['empty_receipt']['populated'],0)
                    self.assertFalse(marker.exists(),'foreign package ran before helper membership/identity')
                    self.assertEqual((self.project/'owned.txt').read_text(),'partial\n')
                    registered=json.loads(owner.store.db.execute("SELECT payload FROM wf_events WHERE op_id=? AND kind='prepared'",(op,)).fetchone()[0])
                    self.assertEqual(registered['pid'],process.pid)
                finally:os.chdir(original)


class PayloadPrivacyTests(IsolatedCustody):
    def registered_write(self,owner):
        from types import SimpleNamespace
        from coherence_workflow.cli import Coordinate
        from test_pi_adapter import environment
        c=SimpleNamespace(authority=owner,contract={'sources':[],'approval_refs':[]},environment=environment())
        tools=Coordinate._tools(c,{'owned_paths':['owned.txt']})
        return Gateway(owner,'run',self.parent,tools)

    def assert_private(self,owner,marker):
        from coherence_workflow.projections import Publisher
        for table in ('wf_operations','wf_events'):
            rows=[tuple(row) for row in owner.store.db.execute('SELECT * FROM '+table)]
            self.assertNotIn(marker,canonical(rows),table+' unnecessarily retains write payload')
        publisher=Publisher(owner,'run');publisher.publish()
        for p in publisher.root.glob('*.json*'):
            self.assertNotIn(marker,p.read_text(),str(p))

    def test_registered_write_body_absent_from_intent_event_and_projection_before_child(self):
        class StopBeforeChild(Exception):pass
        marker='R006_INNOCUOUS_FILE_BODY_NOT_SQL'
        with Authority(self.project) as owner:
            owner.store.reserve('run',digest('fixture'));gateway=self.registered_write(owner)
            def stop(phase,op):
                if phase=='intent':raise StopBeforeChild()
            with self.assertRaises(StopBeforeChild):gateway.launch('private-write','write_file','1',{'path':'owned.txt','text':marker},phase_hook=stop)
            self.assertEqual((self.project/'owned.txt').read_text(),'base')
            self.assertEqual(owner.store.db.execute('SELECT COUNT(*) FROM wf_processes WHERE containment IS NOT NULL').fetchone()[0],0)
            self.assert_private(owner,marker)
            operation=owner.store.db.execute("SELECT args_hash,intent FROM wf_operations WHERE kind='process'").fetchone()
            self.assertEqual(operation['args_hash'],digest({'path':'owned.txt','text':marker}))

    def test_actual_private_pipe_write_preserves_bytes_hashes_custody_and_git_identity(self):
        from coherence_workflow.git_effects import GitEffects,reconcile_commit_process
        from coherence_workflow.store import digest
        marker='R006_ACTUAL_INNOCUOUS_BODY'
        body=marker+'\n'+('z'*18000)+('ñ'*1000)
        with Authority(self.project) as owner:
            owner.store.reserve('run',digest('fixture'));gateway=self.registered_write(owner)
            baseline=snapshot(self.project,['owned.txt']);args={'path':'owned.txt','text':body}
            try:
                op,process=gateway.launch('private-write','write_file','1',args,
                    phase_hook=lambda phase,operation:self.capture(phase,operation,owner))
                receipt=gateway.settle(op,process.wait(timeout=10))
                self.assertTrue(receipt['replacement_allowed']);self.assertEqual(receipt['empty_receipt']['populated'],0)
                self.assertEqual((self.project/'owned.txt').read_text(),body)
                operation=owner.store.operation(op);intent=json.loads(operation['intent'])
                self.assertEqual(operation['args_hash'],digest(args));self.assertEqual(intent['argv_hash'],digest(gateway.tools['write_file'].argv(args)))
                self.assertNotIn('argv',intent)
                task={'id':'privacy-checkpoint','owned_paths':['owned.txt'],'required':[{'id':'privacy/V1'}]}
                checkpoint=GitEffects(owner,'run',gateway).checkpoint(task,baseline,[{'item_id':'privacy/V1','status':'satisfied'}],gates_satisfied=True)
                self.assertEqual(checkpoint['parent'],baseline['head'])
                git_process=owner.store.db.execute("SELECT op_id,intent FROM wf_operations WHERE kind='process' AND node_id LIKE 'commit:%'").fetchone()
                self.assertIn('argv',json.loads(git_process['intent']),'safe exact commit command identity must survive minimization')
                self.assertEqual(reconcile_commit_process(owner,git_process['op_id'])['head'],checkpoint['sha'])
                self.assert_private(owner,marker)
            finally:
                for row in owner.store.db.execute('SELECT containment FROM wf_processes WHERE containment IS NOT NULL'):
                    scope=json.loads(row[0])
                    if scope not in self.receipts:self.receipts.append(scope)

    def test_actual_intent_crash_keeps_only_identity_and_cannot_replay_lost_private_payload(self):
        marker='R006_CRASH_NON_SECRET_BODY'
        code='''import os,sys
from pathlib import Path
from types import SimpleNamespace
from coherence_workflow.store import Authority,digest
from coherence_workflow.tools import Gateway
from coherence_workflow.cli import Coordinate
with Authority(sys.argv[1]) as owner:
 owner.store.reserve('run',digest('fixture'))
 c=SimpleNamespace(authority=owner,contract={'sources':[],'approval_refs':[]},environment={'PATH':'/usr/bin:/bin'})
 gateway=Gateway(owner,'run',sys.argv[2],Coordinate._tools(c,{'owned_paths':['owned.txt']}))
 def crash(phase,op):
  if phase=='intent':os._exit(74)
 gateway.launch('crashed-write','write_file','1',{'path':'owned.txt','text':sys.argv[3]},phase_hook=crash)
'''
        result=subprocess.run([sys.executable,'-c',code,str(self.project),self.parent,marker],capture_output=True,text=True,timeout=20)
        self.assertEqual(result.returncode,74,result.stdout+result.stderr)
        with Authority(self.project) as owner:
            gateway=self.registered_write(owner);self.assert_private(owner,marker)
            self.assertEqual((self.project/'owned.txt').read_text(),'base')
            with self.assertRaisesRegex(Blocked,'unreconciled'):owner.store.assert_dispatchable('run')
            with self.assertRaises(Blocked):gateway.recover()
            self.assertEqual(owner.store.db.execute('SELECT COUNT(*) FROM wf_processes WHERE containment IS NOT NULL').fetchone()[0],0)

    def test_pipe_eof_after_spawn_before_private_payload_executes_no_tool(self):
        class ClosedController(Exception):pass
        marker='R006_PRIVATE_PAYLOAD_NOT_RELEASED'
        with Authority(self.project) as owner:
            owner.store.reserve('run',digest('fixture'));gateway=self.registered_write(owner)
            def close(phase,op):
                self.capture(phase,op,owner)
                if phase=='spawned_before_payload':raise ClosedController()
            with self.assertRaises(ClosedController):gateway.launch('no-payload','write_file','1',{'path':'owned.txt','text':marker},phase_hook=close)
            self.assertEqual((self.project/'owned.txt').read_text(),'base')
            self.assert_private(owner,marker)
            self.assertTrue(all(gateway.containment.populated(receipt)==0 for receipt in self.receipts))
            with self.assertRaises(Blocked):gateway.recover()

    def test_malformed_oversized_truncated_and_wrong_release_frames_fail_without_effect_or_echo(self):
        from coherence_workflow.tool_process import MAX_MANIFEST_BYTES
        real_write=os.write
        for mode in ('malformed','oversized','truncated','wrong-release'):
            self.project=make_project(self.root/('frame-'+mode))
            marker='R006_FRAME_BODY_NOT_EVIDENCE'
            with Authority(self.project) as owner:
                owner.store.reserve('run',digest('fixture'));gateway=self.registered_write(owner)
                writes=[]
                def write(fd,data):
                    writes.append(bytes(data))
                    if len(writes)==1 and mode!='wrong-release':
                        replacement=(b'{}\n' if mode=='malformed' else
                                     b'x'*(MAX_MANIFEST_BYTES+2)+b'\n' if mode=='oversized' else b'{"argv":')
                        real_write(fd,replacement)
                        return len(data)
                    if len(writes)==2 and mode=='wrong-release':
                        real_write(fd,b'not-the-release-nonce\n');return len(data)
                    return real_write(fd,data)
                try:
                    with patch('coherence_workflow.tools.os.write',side_effect=write):
                        if mode=='wrong-release':
                            op,process=gateway.launch('bad-frame','write_file','1',{'path':'owned.txt','text':marker},
                                phase_hook=lambda phase,operation:self.capture(phase,operation,owner))
                            self.assertEqual(process.wait(timeout=10),125)
                            self.assertFalse(gateway.settle(op,125)['task_accepted'])
                        else:
                            with self.assertRaises((Blocked,BrokenPipeError)):
                                gateway.launch('bad-frame','write_file','1',{'path':'owned.txt','text':marker},
                                    phase_hook=lambda phase,operation:self.capture(phase,operation,owner))
                    self.assertEqual((self.project/'owned.txt').read_text(),'base')
                    self.assert_private(owner,marker)
                finally:
                    for row in owner.store.db.execute('SELECT containment FROM wf_processes WHERE containment IS NOT NULL'):
                        scope=json.loads(row[0])
                        if scope not in self.receipts:self.receipts.append(scope)
