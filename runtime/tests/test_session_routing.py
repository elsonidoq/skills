"""T010: synthetic two-task routing through the production engine boundary."""
import sqlite3

from coherence_workflow.engine import Engine
from coherence_workflow.intake import admit
from coherence_workflow.store import Authority
from fixtures.support import ProjectTest


EXECUTOR = {'provider': 'fixture', 'model': 'offline', 'effort': 'medium',
            'reviewer': {'provider': 'fixture', 'model': 'offline-reviewer', 'effort': 'medium'}}
HEADROOM = {'context_window': 250001, 'effective_reserve': 50000, 'occupancy': 50000,
            'compaction_enabled': True, 'compaction_applicable': True}


class SessionRoutingTests(ProjectTest):
    def test_same_affinity_reopens_only_after_corrected_check_and_checkpoint(self):
        project, workers, reviews = self.project, [], []

        class RoutedAdapter:
            def __init__(self, *_args, **_kwargs):
                self.saved_session = None
                self.last_observation = None

            def prompt(self, prompt, *, claim=None, read_only=False, saved_session=None, reuse_key=None, **_kwargs):
                if read_only:
                    reviews.append(self)
                    return '{"approved":true,"findings":[]}'
                if 'REQUIRED check' in prompt:
                    self.assert_same_worker = True
                    claim('ready')
                    project.joinpath('ready').write_text('ready\n')
                    self.saved_session = saved_session or {'id': 'persisted-worker', 'file': '/private/worker.jsonl'}
                    self.last_observation = {'after': {'headroom': HEADROOM}}
                    return 'corrected required check'
                workers.append((self, saved_session, reuse_key, prompt))
                if '"id":"first"' in prompt:
                    claim('first.txt')
                    project.joinpath('first.txt').write_text('first\n')
                else:
                    self.assertEqual(project.joinpath('first.txt').read_text(), 'first\n')
                    claim('second.txt')
                    project.joinpath('second.txt').write_text('second\n')
                self.saved_session = saved_session or {'id': 'persisted-worker', 'file': '/private/worker.jsonl'}
                self.last_observation = {'after': {'headroom': HEADROOM}}
                return 'synthetic worker'

            def assertEqual(self, left, right):
                if left != right:
                    raise AssertionError((left, right))

        tasks = admit([
            {'id': 'first', 'description': 'First synthetic task', 'context_group': 'same',
             'checks': ["test -f ready"]},
            {'id': 'second', 'description': 'Second synthetic task', 'context_group': 'same',
             'depends': ['first'], 'checks': ["test \"$(cat second.txt)\" = second"]},
        ])
        with Authority(project) as owner:
            result = Engine(owner, 'routing', tasks, EXECUTOR, adapter=RoutedAdapter).invoke()
        self.assertEqual(result['status'], 'complete')
        self.assertEqual(len(workers), 2)
        self.assertIsNone(workers[0][1])
        self.assertEqual(workers[1][1]['id'], 'persisted-worker')
        self.assertEqual(workers[0][2], workers[1][2])
        self.assertEqual(len(reviews), 1)
        self.assertIsNot(reviews[0], workers[1][0])
        self.assertEqual(len(result['checkpoints']), 2)

        db = sqlite3.connect(project/'.coherence/workflow/workflow.sqlite')
        checks = list(db.execute("SELECT state FROM execution_history WHERE run_id='routing' AND kind='check'"))
        selections = list(db.execute("SELECT details FROM execution_history WHERE run_id='routing' AND kind='session' AND state='selected' ORDER BY seq"))
        db.close()
        self.assertIn(('failed',), checks)
        self.assertIn(('passed',), checks)
        self.assertIn('"session_id":"persisted-worker"', selections[1][0])

    def test_changed_authority_selects_a_fresh_session(self):
        project, saved = self.project, []

        class RoutedAdapter:
            def __init__(self, *_args, **_kwargs):
                self.saved_session = None
                self.last_observation = None

            def prompt(self, prompt, *, claim=None, read_only=False, saved_session=None, **_kwargs):
                if read_only:
                    return '{"approved":true,"findings":[]}'
                saved.append(saved_session)
                claim('one.txt' if '"id":"one"' in prompt else 'two.txt')
                self.saved_session = {'id': 'persisted-worker', 'file': '/private/worker.jsonl'}
                self.last_observation = {'after': {'headroom': HEADROOM}}
                return 'synthetic worker'

        tasks = admit([
            {'id': 'one', 'description': 'One', 'context_group': 'same'},
            {'id': 'two', 'description': 'Two', 'context_group': 'same', 'depends': ['one'],
             'authority': 'changed'},
        ])
        with Authority(project) as owner:
            Engine(owner, 'changed-authority', tasks, EXECUTOR, adapter=RoutedAdapter).invoke()
        self.assertEqual(saved, [None, None])
