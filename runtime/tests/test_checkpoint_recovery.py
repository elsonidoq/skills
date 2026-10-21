"""Checkpoint failures return to the same synthetic task and reconcile real commits."""
import json
import sqlite3
from unittest.mock import patch

from coherence_workflow.engine import Engine
from coherence_workflow.git_effects import FocusedGit
from coherence_workflow.intake import admit
from coherence_workflow.store import Authority, Blocked, git
from fixtures.support import ProjectTest


EXECUTOR = {'provider': 'fixture', 'model': 'offline', 'effort': 'medium'}


class CheckpointRecoveryTests(ProjectTest):
    def test_hook_failure_returns_to_worker_reruns_check_and_checkpoints(self):
        project, prompts = self.project, []
        hook = project/'.git/hooks/pre-commit'
        hook.write_text("#!/bin/sh\ngrep -q '^good$' owned.txt || { echo source-not-corrected >&2; exit 23; }\n")
        hook.chmod(0o755)

        class Worker:
            def __init__(self, *args, **kwargs): pass
            def prompt(self, prompt, **kwargs):
                if kwargs.get('read_only'):
                    return '{"approved":true,"findings":[]}'
                prompts.append(prompt)
                kwargs['claim']('owned.txt')
                project.joinpath('owned.txt').write_text('bad\n' if len(prompts) == 1 else 'good\n')
                return 'corrected'

        task = {'id': 'hook', 'description': 'Synthetic hook correction', 'owned_paths': ['owned.txt'],
                'checks': [["python3", "-B", "-c", "from pathlib import Path; assert Path('owned.txt').exists()"]]}
        with Authority(project) as owner:
            result = Engine(owner, 'hook-recovery', admit([task]), EXECUTOR, adapter=Worker).invoke()

        self.assertEqual(result['status'], 'complete')
        self.assertEqual(len(prompts), 2)
        self.assertEqual(project.joinpath('owned.txt').read_text(), 'good\n')
        db = sqlite3.connect(project/'.coherence/workflow/workflow.sqlite')
        rows = [(kind, state, json.loads(details)) for kind, state, details in db.execute(
            "SELECT kind,state,details FROM execution_history WHERE run_id='hook-recovery' ORDER BY seq")]
        db.close()
        self.assertTrue(any(kind == 'checkpoint' and state == 'failed' and 'source-not-corrected' in details['error']
                            for kind, state, details in rows))
        self.assertGreaterEqual(sum(kind == 'check' and state == 'passed' for kind, state, _ in rows), 2)
        self.assertEqual(git(project, 'show', '--name-only', '--format=', 'HEAD').decode().splitlines(), ['owned.txt'])

    def test_reported_failed_commit_is_reconciled_without_duplicate_commit(self):
        project = self.project

        class Worker:
            def __init__(self, *args, **kwargs): pass
            def prompt(self, prompt, **kwargs):
                if kwargs.get('read_only'):
                    return '{"approved":true,"findings":[]}'
                kwargs['claim']('owned.txt')
                project.joinpath('owned.txt').write_text('committed\n')
                return 'work'

        original = FocusedGit.checkpoint
        def reported_failure(focused):
            original(focused)
            raise Blocked('reported failure after actual commit')

        with Authority(project) as owner, patch.object(FocusedGit, 'checkpoint', reported_failure):
            result = Engine(owner, 'commit-reconcile', admit([{'id': 'commit', 'description': 'Synthetic commit',
                'owned_paths': ['owned.txt']}]), EXECUTOR, adapter=Worker).invoke()
            rows = [(state, json.loads(details)) for state, details in owner.store.db.execute(
                "SELECT state,details FROM execution_history WHERE run_id='commit-reconcile' AND kind='checkpoint' ORDER BY seq")]

        self.assertEqual(result['status'], 'complete')
        self.assertEqual(git(project, 'rev-list', '--count', self.base + '..HEAD'), b'1\n')
        self.assertEqual(result['checkpoints'][0]['sha'], git(project, 'rev-parse', 'HEAD').decode().strip())
        self.assertEqual(result['checkpoints'][0]['parent'], self.base)
        self.assertEqual([state for state, _ in rows], ['failed', 'passed'])
        self.assertIn('reported failure after actual commit', rows[0][1]['error'])
