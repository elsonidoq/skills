"""Offline prompt wiring checks; not proof that a provider follows instructions."""
from coherence_workflow.engine import Engine
from coherence_workflow.intake import admit
from coherence_workflow.store import Authority
from fixtures.support import ProjectTest


EXECUTOR = {'provider': 'fixture', 'model': 'offline', 'effort': 'medium',
            'reviewer': {'provider': 'fixture', 'model': 'offline-reviewer', 'effort': 'medium'}}


class WorkerAuthorityTests(ProjectTest):
    def assert_authority(self, prompt):
        self.assertIn('this owner-authorized workflow launch approves implementation', prompt)
        self.assertIn('wording in source/task artifacts is superseded for that scope', prompt)
        self.assertIn('A later scoped owner approval also supersedes an earlier conflicting restriction', prompt)
        self.assertIn('actual owner-imposed constraints', prompt)
        self.assertIn('task requirements, acceptance criteria, explicit manual gates', prompt)
        self.assertIn('all safety/permission boundaries', prompt)
        self.assertIn('ask the owner if a material authority conflict remains', prompt)

    def assert_test_permission(self, prompt):
        self.assertIn('Small isolated tests and local test databases are allowed for any task', prompt)
        self.assertIn("do not risk exhausting the machine's resources", prompt)
        self.assertIn('or affecting unrelated data/services', prompt)
        self.assertIn('finite execution parameters within that scope without turning them into owner-renewal gates', prompt)

    def test_every_task_gets_authority_without_rewriting_historical_task_text(self):
        prompts = []
        historical = 'Planning draft only: implementation requires separate approval.'
        contract = admit({'tasks': [
            {'id': 'one', 'description': 'First task. ' + historical},
            {'id': 'two', 'description': 'Second task. ' + historical, 'depends': ['one']},
        ]})

        class Offline:
            def __init__(self, *args, **kwargs): pass
            def prompt(self, prompt, **kwargs):
                if kwargs.get('read_only'):
                    return '{"approved":true,"findings":[]}'
                prompts.append(prompt)
                return 'Verified no-change offline fixture'

        with Authority(self.project) as owner:
            result = Engine(owner, 'authority', contract, EXECUTOR, adapter=Offline).invoke()
            self.assertEqual(owner.store.input('authority')['contract'], contract)
        self.assertEqual(result['status'], 'complete')
        self.assertEqual(len(prompts), 2)
        for prompt in prompts:
            self.assert_authority(prompt)
            self.assert_test_permission(prompt)
            self.assertIn(historical, prompt)
        self.assertEqual(result['sha'], self.base)  # No empty commits or completion redesign.

    def test_later_scoped_authority_reconciles_an_earlier_routine_parameter_gate(self):
        worker_prompts, review_prompts = [], []
        earlier_restriction = 'Earlier recovery note: ask the owner again before a 20-row fixture rerun.'

        class Offline:
            def __init__(self, *args, **kwargs): pass
            def prompt(self, prompt, **kwargs):
                if kwargs.get('read_only'):
                    review_prompts.append(prompt)
                    return '{"approved":true,"findings":[]}'
                worker_prompts.append(prompt)
                return 'Verified no-change offline fixture'

        with Authority(self.project) as owner:
            result = Engine(owner, 'later-authority', admit([{
                'id': 'one', 'description': 'Run the approved isolated fixture. ' + earlier_restriction,
            }]), EXECUTOR, adapter=Offline).invoke()
        self.assertEqual(result['status'], 'complete')
        self.assertEqual(len(worker_prompts), 1)
        self.assertEqual(len(review_prompts), 1)
        for prompt in worker_prompts + review_prompts:
            self.assert_authority(prompt)
            self.assert_test_permission(prompt)
        self.assertIn(earlier_restriction, worker_prompts[0])

    def test_same_task_correction_keeps_current_authority_and_isolated_database_permission(self):
        project, prompts = self.project, []

        class Offline:
            def __init__(self, *args, **kwargs): pass
            def prompt(self, prompt, **kwargs):
                if kwargs.get('read_only'):
                    return '{"approved":true,"findings":[]}'
                prompts.append(prompt)
                if len(prompts) > 1:
                    kwargs['claim']('owned.txt')
                    (project/'owned.txt').write_text('ready\n')
                return 'Offline scoped correction'

        # A tiny in-memory database exercises the ordinary required-check path.
        check = ['python3', '-B', '-c',
                 "import sqlite3; db=sqlite3.connect(':memory:'); "
                 "assert db.execute('select 1').fetchone() == (1,); db.close(); "
                 "assert open('owned.txt').read() == 'ready\\n'"]
        with Authority(project) as owner:
            result = Engine(owner, 'correction', admit([{
                'id': 'fix', 'description': 'Scoped fixture', 'checks': [check],
            }]), EXECUTOR, adapter=Offline).invoke()
        self.assertEqual(result['status'], 'complete')
        self.assertEqual(len(prompts), 2)
        self.assertIn('Actual failed attempt:', prompts[1])
        for prompt in prompts:
            self.assert_authority(prompt)
            self.assert_test_permission(prompt)
            self.assertTrue(prompt.startswith('Current execution authority:'))
