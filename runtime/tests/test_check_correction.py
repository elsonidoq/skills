"""Required-check correction through the production engine and disposable Git."""
import json
import sqlite3

from coherence_workflow.engine import Engine
from coherence_workflow.intake import admit
from coherence_workflow.store import Authority, git
from fixtures.support import ProjectTest


EXECUTOR = {'provider': 'fixture', 'model': 'offline', 'effort': 'medium',
            'reviewer': {'provider': 'fixture', 'model': 'offline-reviewer', 'effort': 'medium'}}


class RequiredCheckCorrectionTests(ProjectTest):
    def test_failed_required_build_returns_actual_attempt_to_same_task_worker_then_checkpoints(self):
        project, prompts = self.project, []
        (project/'other.txt').write_text('staged unrelated\n')
        git(project, 'add', '--', 'other.txt')
        (project/'sentinel.txt').write_text('dirty unrelated\n')

        class CorrectingWorker:
            def __init__(self, *args, **kwargs): pass
            def prompt(self, prompt, *, claim=None, command=None, read_only=False):
                if read_only:
                    return '{"approved":true,"findings":[]}'
                prompts.append(prompt)
                if len(prompts) == 1:
                    claim('owned.txt')
                    (project/'owned.txt').write_text('missing setup\n')
                    return '{"status":"completed","summary":"initial task work"}'
                self_case.assertIn('Actual failed attempt:', prompt)
                self_case.assertIn('missing isolated dependency', prompt)
                self_case.assertIn('"exit_code":1', prompt)
                claim('setup.txt')
                (project/'setup.txt').write_text('ready\n')
                return '{"status":"completed","summary":"scoped correction"}'

        self_case = self
        command = [
            'python3', '-B', '-c',
            "from pathlib import Path; Path('web/dist').mkdir(parents=True, exist_ok=True); "
            "Path('web/dist/build.js').write_text('output\\n'); "
            "assert Path('setup.txt').read_text() == 'ready\\n', 'missing isolated dependency'",
        ]
        task = {'id': 'build', 'description': 'Synthetic isolated build', 'owned_paths': ['owned.txt', 'setup.txt'],
                'generated_outputs': ['web/dist/'], 'required': [{'id': 'build', 'check': command}],
                'check': ['python3', '-B', '-c',
                          "from pathlib import Path; assert Path('web/dist/build.js').read_text() == 'output\\n'; Path('web/dist/build.js').unlink()"]}
        with Authority(project) as owner:
            result = Engine(owner, 'correction', admit([task]), EXECUTOR, adapter=CorrectingWorker).invoke()

        self.assertEqual(result['status'], 'complete')
        self.assertEqual(len(prompts), 2)
        self.assertEqual((project/'setup.txt').read_text(), 'ready\n')
        self.assertEqual((project/'sentinel.txt').read_text(), 'dirty unrelated\n')
        self.assertEqual(git(project, 'diff', '--cached', '--name-only').decode().splitlines(), ['other.txt'])
        self.assertEqual(git(project, 'show', '--name-only', '--format=', 'HEAD').decode().splitlines(), ['owned.txt', 'setup.txt'])
        self.assertFalse((project/'web/dist/build.js').exists())
        self.assertNotIn('web/dist/build.js', git(project, 'show', '--name-only', '--format=', 'HEAD').decode())
        db = sqlite3.connect(project/'.coherence/workflow/workflow.sqlite')
        facts = [json.loads(row[0]) for row in db.execute("SELECT facts FROM execution_observations WHERE phase='check'")]
        workers = [json.loads(row[0]) for row in db.execute(
            "SELECT facts FROM execution_observations WHERE phase='worker' AND kind='started'")]
        db.close()
        self.assertIn(1, [fact.get('exit_code') for fact in facts])
        self.assertIn(0, [fact.get('exit_code') for fact in facts])
        self.assertEqual([fact['invocation_kind'] for fact in workers], ['task_worker', 'corrective_worker'])
        self.assertEqual(workers[1]['predecessor_invocation_id'], workers[0]['invocation_id'])
        self.assertEqual(workers[1]['correction_chain'], [workers[0]['invocation_id'], workers[1]['invocation_id']])

    def test_unavailable_correction_returns_the_actual_blocker(self):
        project = self.project
        class UnavailableWorker:
            def __init__(self, *args, **kwargs): self.calls = 0
            def prompt(self, prompt, *, read_only=False, claim=None, **kwargs):
                if read_only:
                    return '{"approved":true,"findings":[]}'
                self.calls += 1
                if self.calls == 1:
                    claim('owned.txt')
                    (project/'owned.txt').write_text('partial\n')
                    return '{"status":"completed","summary":"initial"}'
                raise RuntimeError('safe correction unavailable')
        with Authority(project) as owner:
            with self.assertRaisesRegex(RuntimeError, 'safe correction unavailable'):
                Engine(owner, 'blocked-correction', admit([{'id': 'fix', 'description': 'Fix',
                       'owned_paths': ['owned.txt'], 'checks': ['exit 1']}]), EXECUTOR,
                       adapter=UnavailableWorker).invoke()
