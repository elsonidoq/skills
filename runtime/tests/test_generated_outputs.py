"""Synthetic generated-output lifecycle tests at parser, worker, check and Git boundaries."""
from coherence_workflow.engine import Engine
from coherence_workflow.intake import admit
from coherence_workflow.store import Authority, git
from fixtures.support import ProjectTest


EXECUTOR = {'provider': 'fixture', 'model': 'offline', 'effort': 'medium'}


class GeneratedActionScopeTests(ProjectTest):
    def test_generated_outputs_are_optional_parser_guidance(self):
        task = admit([{'id': 'build', 'description': 'Build',
                       'generated_outputs': ['web/dist/']}])['tasks'][0]
        self.assertEqual(task['generated_outputs'], ['web/dist/'])

    def test_task_intake(self):
        self.test_generated_outputs_are_optional_parser_guidance()

    def test_git_effects(self):
        project = self.project
        calls = []

        class SyntheticWorker:
            def __init__(self, *args, **kwargs): pass
            def prompt(self, prompt, *, claim=None, command=None, read_only=False):
                if read_only:
                    return '{"approved":true,"findings":[]}'
                claim('owned.txt')
                (project/'owned.txt').write_text('source\n')
                command('start', 'synthetic-build')
                (project/'web/dist').mkdir(parents=True)
                claim('web/dist/known.js')
                (project/'web/dist/known.js').write_text('known\n')
                # Git-visible and ignored/undeclared output are not command admission.
                (project/'undeclared.out').write_text('undeclared\n')
                (project/'ignored.tmp').write_text('ignored\n')
                command('end', 'synthetic-build')
                calls.append('continued')
                return 'synthetic build complete'

        task = {'id': 'build', 'description': 'Synthetic build', 'owned_paths': ['owned.txt'],
                'generated_outputs': ['web/dist/'],
                'checks': [['python3', '-B', '-c',
                            "assert open('web/dist/known.js').read() == 'known\\n'"]]}
        with Authority(project) as owner:
            result = Engine(owner, 'generated', admit([task]), EXECUTOR, adapter=SyntheticWorker).invoke()
        self.assertEqual(calls, ['continued'])
        self.assertEqual(result['checkpoints'][0]['paths'], ['owned.txt'])
        self.assertEqual(result['checkpoints'][0]['artifacts'], ['web/dist/known.js'])
        self.assertEqual((project/'undeclared.out').read_text(), 'undeclared\n')
        self.assertEqual((project/'ignored.tmp').read_text(), 'ignored\n')
        self.assertNotIn('web/dist/known.js', git(project, 'show', '--name-only', '--format=', 'HEAD').decode())
