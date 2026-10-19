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
from coherence_workflow.store import Authority, Blocked, canonical, git, safe_path
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
