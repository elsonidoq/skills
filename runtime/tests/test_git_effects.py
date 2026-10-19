"""T003/V4 actual focused Git checkpoints and safety negatives."""
import json
import os
from pathlib import Path

from coherence_workflow.git_effects import GitEffects, reconcile_checkpoint
from coherence_workflow.store import Authority, Blocked, digest, git
from coherence_workflow.tools import Gateway, snapshot
from test_custody import IsolatedCustody


class FocusedCheckpointTests(IsolatedCustody):
    def test_actual_cli_sdk_dependency_sequence(self):
        from test_cli import live_sequence
        live_sequence(self)

    def test_symlink_and_missing_identity_block_before_mutation(self):
        from unittest.mock import patch
        with Authority(self.project) as owner:
            owner.store.reserve('run','fixture')
            effects=GitEffects(owner,'run',Gateway(owner,'run',self.parent,{}))
            (self.project/'escape').symlink_to(self.outside)
            with self.assertRaises(Blocked):effects.begin({'id':'escape','owned_paths':['escape']})
            with patch.dict(os.environ,{'GIT_AUTHOR_NAME':''}):
                with self.assertRaises(Blocked):effects.begin(self.task())
            self.assertEqual(self.outside.read_text(),'outside unchanged')

    def test_repeated_owned_writes_require_exact_kernel_empty_origin_chain(self):
        from fixtures.custody_support import process_tool
        with Authority(self.project) as owner:
            owner.store.reserve('run','fixture')
            gateway=Gateway(owner,'run',self.parent,{'fixture':process_tool(self.project)})
            baseline=snapshot(self.project,['owned.txt'])
            gateway.bind_task_origin('attempt:', ['owned.txt'], baseline)
            for visit in range(2):
                op,proc=gateway.launch('attempt:'+str(visit),'fixture','1',{'mode':'quick','exit':0})
                self.capture('released',op,owner)
                self.assertTrue(gateway.settle(op,proc.wait(timeout=10))['replacement_allowed'])
            (self.project/'owned.txt').write_text('unexplained drift')
            with self.assertRaisesRegex(Blocked,'unexplained task-origin drift'):
                gateway.launch('attempt:third','fixture','1',{'mode':'quick','exit':0})
            self.assertEqual(owner.store.db.execute('SELECT COUNT(*) FROM wf_processes').fetchone()[0],2)

    def test_actual_signing_failure_blocks_without_disabling_or_retry(self):
        git(self.project,'config','commit.gpgsign','true')
        git(self.project,'config','gpg.program','/usr/bin/false')
        with Authority(self.project) as owner:
            owner.store.reserve('run','fixture')
            baseline=snapshot(self.project,['owned.txt'])
            (self.project/'owned.txt').write_text('retained partial signing failure')
            with self.assertRaisesRegex(Blocked,'Git commit/hooks/signing failed'):
                self.checkpoint(owner,self.task(),baseline)
            self.assertEqual(git(self.project,'rev-parse','HEAD').decode().strip(),baseline['head'])
            self.assertEqual(git(self.project,'config','commit.gpgsign').decode().strip(),'true')
            self.assertEqual((self.project/'owned.txt').read_text(),'retained partial signing failure')

    def task(self):
        return {'id':'A','owned_paths':['owned.txt'],'required':[{'id':'A/V1'}]}

    def checkpoint(self, owner, task, baseline, **kwargs):
        gateway=Gateway(owner,'run',self.parent,{})
        try:
            return GitEffects(owner,'run',gateway).checkpoint(task,baseline,
                [{'item_id':'A/V1','status':'satisfied'}],gates_satisfied=True,**kwargs)
        finally:
            for row in owner.store.db.execute('SELECT containment FROM wf_processes WHERE containment IS NOT NULL'):
                receipt=json.loads(row[0])
                if receipt not in self.receipts:self.receipts.append(receipt)

    def test_actual_commit_preserves_unrelated_staged_unstaged_untracked(self):
        (self.project/'other.txt').write_text('unrelated staged');git(self.project,'add','--','other.txt')
        (self.project/'custom.md').write_text('unrelated unstaged')
        (self.project/'user-untracked').write_text('unrelated untracked')
        with Authority(self.project) as owner:
            owner.store.reserve('run','fixture')
            before=snapshot(self.project,['owned.txt'])
            (self.project/'owned.txt').write_text('implementation')
            result=self.checkpoint(owner,self.task(),before)
            self.assertEqual(result['parent'],before['head'])
            self.assertEqual(git(self.project,'diff-tree','--no-commit-id','--name-only','-r',result['sha']).decode().strip(),'owned.txt')
            self.assertEqual(git(self.project,'diff','--cached','--name-only').decode().strip(),'other.txt')
            self.assertEqual(reconcile_checkpoint(owner,result['operation_id']),result)
            for name in before['files']:
                if name!='owned.txt':self.assertEqual(before['files'][name],result['reconciliation']['files'][name])
            with self.assertRaises(Blocked):self.checkpoint(owner,self.task(),before)
            print(json.dumps(result))

    def test_read_only_no_empty_commit_and_failed_evidence_blocks(self):
        with Authority(self.project) as owner:
            owner.store.reserve('run','fixture')
            task=self.task(); baseline=snapshot(self.project,task['owned_paths'])
            effects=GitEffects(owner,'run',Gateway(owner,'run',self.parent,{}))
            with self.assertRaises(Blocked):effects.checkpoint(task,baseline,[],gates_satisfied=True)
            result=self.checkpoint(owner,task,baseline)
            self.assertTrue(result['read_only']);self.assertEqual(result['sha'],baseline['head'])
            self.assertEqual(owner.store.db.execute('SELECT COUNT(*) FROM wf_processes').fetchone()[0],0)

    def test_owned_overlap_symlink_unrelated_drift_and_hook_failure_stop(self):
        with Authority(self.project) as owner:
            owner.store.reserve('run','fixture')
            effects=GitEffects(owner,'run',Gateway(owner,'run',self.parent,{}));task=self.task()
            (self.project/'owned.txt').write_text('preexisting')
            with self.assertRaises(Blocked):effects.begin(task)
            # Each negative uses a new isolated Git baseline rather than discarding user work.
            baseline=snapshot(self.project,task['owned_paths'])
            (self.project/'custom.md').write_text('drift')
            with self.assertRaises(Blocked):self.checkpoint(owner,task,baseline)
        # Hook failure is tested in this fixture's own repository, never configured around.
        self.project=__import__('fixtures.support',fromlist=['make_project']).make_project(self.root/'hook-project')
        hook=self.project/'.git/hooks/pre-commit';hook.write_text('#!/bin/sh\nexit 1\n');hook.chmod(0o700)
        with Authority(self.project) as owner:
            owner.store.reserve('run','fixture')
            baseline=snapshot(self.project,['owned.txt']);(self.project/'owned.txt').write_text('changed')
            with self.assertRaisesRegex(Blocked,'Git commit/hooks/signing failed'):self.checkpoint(owner,self.task(),baseline)
            self.assertEqual(git(self.project,'rev-parse','HEAD').decode().strip(),baseline['head'])
            self.assertEqual((self.project/'owned.txt').read_text(),'changed')


class GitCapabilityTests(IsolatedCustody):
    def setUp(self):
        super().setUp()
        self.marker=self.root/'callback-marker'

    def effects(self,owner):
        owner.store.reserve('run',digest('git-capability-fixture'))
        return GitEffects(owner,'run',Gateway(owner,'run',self.parent,{}))

    def assert_rejected_without_effect(self,owner,effects):
        index=(self.project/'.git/index').read_bytes()
        head=git(self.project,'rev-parse','HEAD')
        with self.assertRaisesRegex(Blocked,'filter|post-index-change') as error:effects.begin(self.task())
        self.assertNotIn('DO_NOT_LOG_COMMAND_SECRET',str(error.exception))
        self.assertFalse(self.marker.exists())
        self.assertEqual((self.project/'.git/index').read_bytes(),index)
        self.assertEqual(git(self.project,'rev-parse','HEAD'),head)
        self.assertEqual(owner.store.db.execute('SELECT COUNT(*) FROM wf_operations').fetchone()[0],0)
        self.assertEqual(self.outside.read_text(),'outside unchanged')

    def task(self):return {'id':'A','owned_paths':['owned.txt'],'required':[{'id':'A/V1'}]}

    def test_applicable_clean_and_process_filters_never_execute_or_stage(self):
        import shlex
        for kind in ('clean','process'):
            project=self.project
            if kind=='process':
                from fixtures.support import make_project
                self.project=make_project(self.root/'process-project')
            (self.project/'.gitattributes').write_text('owned.txt filter=ScopedDriver\n')
            command='printf DO_NOT_LOG_COMMAND_SECRET > '+shlex.quote(str(self.marker))+'; cat'
            git(self.project,'config','filter.ScopedDriver.'+kind,command)
            with Authority(self.project) as owner:self.assert_rejected_without_effect(owner,self.effects(owner))
        self.project=project

    def test_executable_index_hook_and_custom_hook_directory_never_execute(self):
        hookdir=self.project/'configured-hooks';hookdir.mkdir()
        git(self.project,'config','core.hooksPath','configured-hooks')
        hook=hookdir/'post-index-change'
        hook.write_text('#!/bin/sh\nprintf DO_NOT_LOG_COMMAND_SECRET > '+str(self.marker)+'\n');hook.chmod(0o700)
        with Authority(self.project) as owner:self.assert_rejected_without_effect(owner,self.effects(owner))

    def test_late_hook_and_attribute_change_block_before_checkpoint_effect(self):
        import shlex
        from coherence_workflow.git_effects import assert_safe_git_inputs
        with Authority(self.project) as owner:
            effects=self.effects(owner);baseline=effects.begin(self.task())
            (self.project/'owned.txt').write_text('approved implementation')
            index=(self.project/'.git/index').read_bytes()
            git(self.project,'config','filter.late.clean','printf marker > '+shlex.quote(str(self.marker))+'; cat')
            # An unused external filter does not deny ordinary built-in operations.
            assert_safe_git_inputs(self.project,self.task()['owned_paths'])
            (self.project/'.gitattributes').write_text('owned.txt filter=late\n')
            with self.assertRaisesRegex(Blocked,'filter'):effects.checkpoint(self.task(),baseline,[{'item_id':'A/V1','status':'satisfied'}],gates_satisfied=True)
            self.assertEqual((self.project/'.git/index').read_bytes(),index);self.assertFalse(self.marker.exists())
            self.assertEqual(owner.store.db.execute('SELECT COUNT(*) FROM wf_operations').fetchone()[0],0)
        # Separate fixture: no reset/discard/configuration-around the rejected case.
        from fixtures.support import make_project
        self.project=make_project(self.root/'late-hook-project')
        with Authority(self.project) as owner:
            effects=self.effects(owner);baseline=effects.begin(self.task())
            (self.project/'owned.txt').write_text('retained partial')
            hook=self.project/'.git/hooks/post-index-change';hook.write_text('#!/bin/sh\nexit 0\n');hook.chmod(0o700)
            index=(self.project/'.git/index').read_bytes()
            with self.assertRaisesRegex(Blocked,'post-index-change'):effects.checkpoint(self.task(),baseline,[{'item_id':'A/V1','status':'satisfied'}],gates_satisfied=True)
            self.assertEqual((self.project/'.git/index').read_bytes(),index)
            self.assertEqual((self.project/'owned.txt').read_text(),'retained partial')

    def test_normal_builtin_normalization_and_contained_commit_remain_supported(self):
        (self.project/'.gitattributes').write_text('owned.txt text eol=lf\n')
        with Authority(self.project) as owner:
            effects=self.effects(owner);baseline=effects.begin(self.task())
            (self.project/'owned.txt').write_bytes(b'normalized\r\n')
            try:
                result=effects.checkpoint(self.task(),baseline,[{'item_id':'A/V1','status':'satisfied'}],gates_satisfied=True)
                self.assertEqual(git(self.project,'show',result['sha']+':owned.txt'),b'normalized\n')
                self.assertEqual((self.project/'owned.txt').read_bytes(),b'normalized\r\n')
                self.assertEqual(result['parent'],baseline['head'])
            finally:
                for row in owner.store.db.execute('SELECT containment FROM wf_processes WHERE containment IS NOT NULL'):
                    receipt=json.loads(row[0])
                    if receipt not in self.receipts:self.receipts.append(receipt)
