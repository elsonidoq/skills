"""Offline prompt wiring checks; not proof that a provider follows instructions."""
from coherence_workflow.engine import Engine
from coherence_workflow.pi_adapter import effective_saved_session
from coherence_workflow.intake import admit
from coherence_workflow.store import Authority, Blocked
from fixtures.support import ProjectTest


EXECUTOR = {'provider': 'fixture', 'model': 'offline', 'effort': 'medium',
            'reviewer': {'provider': 'fixture', 'model': 'offline-reviewer', 'effort': 'medium'}}


class WorkerAuthorityTests(ProjectTest):
    def assert_authority(self, prompt):
        self.assertIn('this owner-authorized workflow launch approves implementation', prompt)
        self.assertIn('wording in source/task artifacts is superseded for that scope', prompt)
        self.assertIn('Preserve task requirements, acceptance criteria, explicit manual gates', prompt)
        self.assertIn('all safety/permission boundaries', prompt)
        self.assertIn('ask the owner if a material authority conflict remains', prompt)

    def assert_test_permission(self, prompt):
        self.assertIn('Small isolated tests and local test databases are allowed for any task', prompt)
        self.assertIn("do not risk exhausting the machine's resources", prompt)
        self.assertIn('or affecting unrelated data/services', prompt)

    def assert_completion_ownership(self, prompt):
        self.assertIn('Continue unfinished authorized implementation, unrun worker-owned semantic/manual acceptance, and correctable failures', prompt)
        self.assertIn('Finish the assigned implementation and worker-owned semantic/manual acceptance', prompt)
        self.assertIn('The runner executes/reruns configured checks, creates the focused checkpoint', prompt)
        self.assertIn('dispatches fresh independent review', prompt)
        self.assertIn('it does not own all semantic/manual acceptance or the reviewer verdict', prompt)
        self.assertIn('Pending runner stages alone do not require an unsuccessful status', prompt)
        self.assertIn('genuine inability to progress, cancellation, or execution failure prevents worker-owned acceptance', prompt)
        self.assertIn('unmet acceptance never becomes success', prompt)
        self.assertIn('do not report corrected tool errors or a required check that will be rerun as unsuccessful', prompt)

    def assert_precedence_authority(self, prompt):
        self.assertIn('this current scoped authority takes precedence', prompt)
        self.assertIn('actual owner-imposed limit', prompt)
        self.assertIn('manual gate, paid application/test API boundary', prompt)
        self.assertIn('security/data restriction, or external-operation restriction', prompt)
        self.assertIn('This authority is not proof that checks succeeded.', prompt)

    def assert_precedence_scenario(self, prompt, scenario):
        self.assertIn(scenario, prompt)
        self.assert_precedence_authority(prompt)
        self.assertLess(prompt.index('this current scoped authority takes precedence'), prompt.index(scenario))

    def test_saved_session_selection_matches_adapter_explicit_precedence(self):
        held = {'id': 'held-session', 'file': '/private/held.jsonl'}
        explicit = {'id': 'explicit-session', 'file': '/private/explicit.jsonl'}
        self.assertIs(effective_saved_session(None, held), held)
        self.assertIs(effective_saved_session(explicit, held), explicit)

    def test_every_task_gets_authority_without_rewriting_historical_task_text(self):
        prompts = []
        historical = 'Planning draft only: implementation requires separate approval.'
        scenario = ('LABELLED SCENARIO ONLY: an earlier agent-authored recovery instruction requires renewed consent '
                    'for an exact 1 GiB fixture and rerunning its check.')
        contract = admit({'tasks': [
            {'id': 'one', 'description': 'First task. ' + historical + ' ' + scenario},
            {'id': 'two', 'description': 'Second task. ' + historical + ' ' + scenario, 'depends': ['one']},
        ]})

        class Offline:
            def __init__(self, *args, **kwargs): pass
            def prompt(self, prompt, **kwargs):
                if kwargs.get('read_only'):
                    return '{"approved":true,"coverage":["fixture examined"],"coverage_gaps":[],"findings":[]}'
                prompts.append(prompt)
                return 'Verified no-change offline fixture'

        with Authority(self.project) as owner:
            result = Engine(owner, 'authority', contract, EXECUTOR, adapter=Offline).invoke()
            self.assertEqual(owner.store.input('authority')['contract'], contract)
        self.assertEqual(result['status'], 'complete')
        self.assertEqual(len(prompts), 2)
        for prompt in prompts:
            self.assert_authority(prompt)
            self.assert_completion_ownership(prompt)
            self.assert_test_permission(prompt)
            self.assertIn(historical, prompt)
            self.assert_precedence_scenario(prompt, scenario)
        self.assertEqual(result['sha'], self.base)  # No empty commits or completion redesign.

    def test_same_task_correction_keeps_current_authority_and_isolated_database_permission(self):
        project, prompts = self.project, []
        scenario = ('LABELLED SCENARIO ONLY: an earlier agent-authored task instruction requires renewed consent '
                    'for exact SQLite fixture setup and rerunning its check.')
        identity = {'id': 'authority-correction-session', 'file': '/private/authority-correction.jsonl'}

        class Offline:
            def __init__(self, *args, **kwargs): self.saved_session = identity
            def prompt(self, prompt, **kwargs):
                if kwargs.get('read_only'):
                    return '{"approved":true,"coverage":["fixture examined"],"coverage_gaps":[],"findings":[]}'
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
                'id': 'fix', 'description': 'Scoped fixture. ' + scenario, 'checks': [check],
            }]), EXECUTOR, adapter=Offline).invoke()
        self.assertEqual(result['status'], 'complete')
        self.assertEqual(len(prompts), 2)
        self.assertIn('Actual failed attempt:', prompts[1])
        for ordinal, prompt in enumerate(prompts):
            self.assert_authority(prompt)
            self.assert_completion_ownership(prompt)
            self.assert_test_permission(prompt)
            if ordinal == 0:
                self.assert_precedence_scenario(prompt, scenario)
            else:
                self.assert_precedence_authority(prompt)
            self.assertTrue(prompt.startswith('Current execution authority:'))

    def test_resumed_handoff_keeps_scoped_authority_over_labelled_agent_restriction(self):
        scenario = ('LABELLED SCENARIO ONLY: an earlier agent-authored recovery instruction requires renewed consent '
                    'for an exact local fixture and rerunning its check.')
        identity, prompts = {'id': 'authority-fixture-session', 'file': '/private/fixture.jsonl'}, []

        class Interrupted:
            def __init__(self, *args, **kwargs): self.saved_session = identity
            def prompt(self, prompt, **kwargs):
                if kwargs.get('read_only'):
                    return '{"approved":true,"coverage":["fixture examined"],"coverage_gaps":[],"findings":[]}'
                raise Blocked('labelled authority fixture interruption')

        with Authority(self.project) as owner:
            with self.assertRaisesRegex(Blocked, 'labelled authority fixture interruption'):
                Engine(owner, 'authority-resume', admit([{
                    'id': 'resume', 'description': 'Scoped fixture. ' + scenario,
                }]), EXECUTOR, adapter=Interrupted).invoke()
            owner.store.resume('authority-resume')

            class Continued:
                def __init__(self, *args, **kwargs): pass
                def prompt(self, prompt, **kwargs):
                    if kwargs.get('read_only'):
                        return '{"approved":true,"coverage":["fixture examined"],"coverage_gaps":[],"findings":[]}'
                    prompts.append(prompt)
                    self_test.assertEqual(kwargs['saved_session'], identity)
                    return 'Resumed scoped fixture'

            self_test = self
            result = Engine(owner, 'authority-resume', admit([{
                'id': 'resume', 'description': 'Scoped fixture. ' + scenario,
            }]), EXECUTOR, adapter=Continued, resume=True,
                            question=lambda _question: 'diagnosed fixture interruption').invoke()
        self.assertEqual(result['status'], 'complete')
        self.assertEqual(len(prompts), 1)
        self.assertIn('Continue only the unfinished same-task work.', prompts[0])
        self.assert_completion_ownership(prompts[0])
        self.assert_precedence_scenario(prompts[0], scenario)
