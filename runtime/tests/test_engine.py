"""Offline operation fixtures exercise real task/check/Git ordering, not provider success."""
import json
from unittest.mock import patch

from coherence_workflow.engine import Engine
from coherence_workflow.intake import admit
from coherence_workflow.store import Authority, Blocked, git
from fixtures.support import ProjectTest

EXECUTOR = {'provider': 'fixture', 'model': 'offline-not-provider-success', 'effort': 'medium'}


class SequentialExecutionTests(ProjectTest):
    def execute(self, tasks, adapter, **kwargs):
        with Authority(self.project) as owner:
            return Engine(owner, 'fixture', admit(tasks), EXECUTOR, adapter=adapter, **kwargs).invoke()

    def test_dependencies_real_checks_focused_commits_and_independent_read_only_review(self):
        sessions = []
        project = self.project
        case = self
        class OfflineOperations:
            def __init__(self, project, executor, **kwargs):
                case.assertEqual(executor, EXECUTOR)
                sessions.append(self)
            def prompt(self, prompt, *, claim=None, command=None, read_only=False):
                if read_only:
                    case.assertIn('Diff:', prompt)
                    case.assertIn('consumer', prompt)
                    return '{"approved":true,"findings":[]}'
                if len(sessions) == 1:
                    claim('owned.txt')
                    (project/'owned.txt').write_text('producer\n')
                else:
                    case.assertEqual(git(project, 'show', 'HEAD:owned.txt'), b'producer\n')
                    claim('new.txt')
                    (project/'new.txt').write_text('consumer\n')
                return 'offline operation fixture'
        result = self.execute([
            {'id': 'consumer', 'description': 'Consume', 'depends': ['producer'],
             'checks': [['python3', '-B', '-c', "assert open('new.txt').read() == 'consumer\\n'"],
                        ['python3', '-B', '-c',
                         "import os; assert os.path.realpath('.git/coherence-workflow.lock') in "
                         "[os.path.realpath('/proc/self/fd/'+fd) for fd in os.listdir('/proc/self/fd')]"]]},
            {'id': 'producer', 'description': 'Produce'}], OfflineOperations)
        self.assertEqual(result['status'], 'complete')
        self.assertEqual(len(sessions), 3)
        self.assertEqual(len({id(s) for s in sessions}), 3)
        self.assertEqual(len(result['checkpoints']), 2)
        self.assertEqual(git(project, 'rev-list', '--count', self.base+'..HEAD'), b'2\n')
        import sqlite3
        db = sqlite3.connect(project/'.coherence/workflow/workflow.sqlite')
        kinds = [row[0] for row in db.execute('SELECT kind FROM execution_observations ORDER BY seq')]
        db.close()
        self.assertIn('started', kinds)
        self.assertIn('returned', kinds)
        self.assertIn('passed', kinds)

    def test_failed_check_not_passed_no_commit_or_automatic_retry(self):
        project = self.project
        calls = []
        class OfflineFailure:
            def __init__(self, *args, **kwargs): pass
            def prompt(self, prompt, **kwargs):
                calls.append(prompt)
                kwargs['claim']('owned.txt')
                (project/'owned.txt').write_text('partial\n')
                return 'worker claims done but actual command fails'
        with self.assertRaisesRegex(Blocked, 'check failed'):
            self.execute([{'id': 'fix', 'description': 'Fix', 'checks': [['python3', '-B', '-c', 'raise SystemExit(7)']]}], OfflineFailure)
        self.assertEqual(len(calls), 1)
        self.assertEqual(git(project, 'rev-parse', 'HEAD').decode().strip(), self.base)
        self.assertEqual((project/'owned.txt').read_text(), 'partial\n')
        from coherence_workflow.cli import status
        self.assertEqual(status(project, 'fixture')['run']['state'], 'failed')
        self.assertEqual(status(project, 'fixture')['tasks'][0]['state'], 'failed')

    def test_findings_honestly_reported_commits_retained_no_disposition_database(self):
        project = self.project
        class OfflineReview:
            def __init__(self, *args, **kwargs): pass
            def prompt(self, prompt, *, read_only=False, claim=None, command=None):
                if read_only:
                    return '{"approved":false,"findings":["owned.txt:1 - defect"]}'
                claim('owned.txt')
                (project/'owned.txt').write_text('changed\n')
                return 'changed'
        with self.assertRaisesRegex(Blocked, 'owned.txt:1 - defect'):
            self.execute([{'id': 'fix', 'description': 'Fix'}], OfflineReview)
        self.assertNotEqual(git(project, 'rev-parse', 'HEAD').decode().strip(), self.base)

    def test_manual_gate_uses_current_answer_without_receipt(self):
        answers = []
        def deny(question):
            answers.append(question)
            return 'no'
        class Never:
            def __init__(self, *a, **k): raise AssertionError('worker launched')
        with self.assertRaisesRegex(Blocked, 'manual gate not approved'):
            self.execute([{'id': 'fix', 'description': 'Fix', 'gates': [{'question': 'Proceed?'}]}], Never, question=deny)
        self.assertEqual(len(answers), 1)
        import sqlite3
        db = sqlite3.connect(self.project/'.coherence/workflow/workflow.sqlite')
        rows = list(db.execute('SELECT occurrence_id,phase,kind,facts FROM execution_observations ORDER BY seq'))
        db.close()
        self.assertNotIn('worker', [row[1] for row in rows])
        gate = [(row[0], row[2], json.loads(row[3])) for row in rows if row[1] == 'gate']
        self.assertIn('question_requested', [row[1] for row in gate])
        self.assertIn('answer_returned', [row[1] for row in gate])
        self.assertNotIn('answer_sent', [row[1] for row in gate])
        question = next(row for row in gate if row[1] == 'question_requested')
        self.assertTrue(question[2]['parent_occurrence_id'])

    def test_worker_question_lifecycle_uses_distinct_question_occurrence(self):
        project = self.project
        class OfflineQuestions:
            def __init__(self, project, executor, **kwargs): self.observe_question = kwargs.get('observe_question')
            def prompt(self, prompt, **kwargs):
                if kwargs.get('read_only'): return '{"approved":true,"findings":[]}'
                for state in ('requested', 'returned', 'sent'):
                    self.observe_question(state)
                return 'offline question adapter'
        self.execute([{'id': 'fix', 'description': 'Fix'}], OfflineQuestions)
        import sqlite3
        db = sqlite3.connect(project/'.coherence/workflow/workflow.sqlite')
        rows = list(db.execute("SELECT occurrence_id,kind,facts FROM execution_observations WHERE phase='worker' AND kind LIKE 'answer_%' OR phase='worker' AND kind='question_requested'"))
        db.close()
        self.assertEqual([row[1] for row in rows], ['question_requested', 'answer_returned', 'answer_sent'])
        self.assertEqual(len({row[0] for row in rows}), 1)
        self.assertTrue(json.loads(rows[0][2])['parent_occurrence_id'])

    def test_real_framed_question_send_failure_records_delivery_failed(self):
        import os, sys
        from pathlib import Path
        host, closed = self.root/'broken_answer_host.py', self.root/'stdin-closed'
        host.write_text("""import json, sys, time
from pathlib import Path
request = json.loads(input())
if request['readOnly']:
    print(json.dumps({'type':'result','text':'{\\\"approved\\\":true,\\\"findings\\\":[]}'}), flush=True)
else:
    print(json.dumps({'type':'question','question':'PRIVATE-SENTINEL'}), flush=True)
    import os
    os.close(0)
    Path(""" + repr(str(closed)) + """).write_text('closed')
    time.sleep(1)
""")
        contract = admit([{'id': 'fix', 'description': 'Fix'}])
        with patch('coherence_workflow.pi_adapter.host_path', return_value=host), patch.dict(os.environ, {'COHERENCE_NODE': sys.executable}):
            with Authority(self.project) as owner:
                with self.assertRaises((BrokenPipeError, OSError)):
                    def answer(text):
                        import time
                        deadline = time.monotonic() + 5
                        while not closed.exists() and time.monotonic() < deadline: time.sleep(.01)
                        self.assertTrue(closed.exists())
                        return 'yes'
                    Engine(owner, 'broken-send', contract, EXECUTOR, adapter=__import__('coherence_workflow.pi_adapter', fromlist=['PiAdapter']).PiAdapter, question=answer).invoke()
        import sqlite3
        db = sqlite3.connect(self.project/'.coherence/workflow/workflow.sqlite')
        rows = list(db.execute("SELECT occurrence_id,kind,facts FROM execution_observations WHERE run_id='broken-send' AND phase='worker'"))
        db.close()
        sent = [(row[0], row[1], json.loads(row[2])) for row in rows if row[1] == 'delivery_failed']
        self.assertEqual(len(sent), 1)
        self.assertTrue(sent[0][2]['parent_occurrence_id'])
        self.assertNotIn('PRIVATE-SENTINEL', str(rows))

    def test_review_base_must_be_ancestor_and_actual_prompt_uses_it(self):
        project = self.project
        prompts = []
        class Offline:
            def __init__(self, *a, **k): pass
            def prompt(self, prompt, **kwargs):
                if kwargs.get('read_only'):
                    prompts.append(prompt)
                    return '{"approved":true,"findings":[]}'
                return 'offline worker'
        contract = admit({'review_base': self.base, 'tasks': [{'id': 'fix', 'description': 'Fix'}]})
        with Authority(project) as owner:
            Engine(owner, 'range', contract, EXECUTOR, adapter=Offline).invoke()
        self.assertIn('Range: ' + self.base + '..', prompts[0])
        bad = admit({'review_base': 'not-a-commit', 'tasks': [{'id': 'again', 'description': 'Again'}]})
        with Authority(project) as owner:
            with self.assertRaisesRegex(Blocked, 'ancestor'):
                Engine(owner, 'bad-range', bad, EXECUTOR, adapter=Offline).invoke()

    def test_rejected_original_and_declared_fix_use_full_original_review_range(self):
        project, prompts = self.project, []
        class OfflineReviewCycle:
            def __init__(self, *a, **k): pass
            def prompt(self, prompt, **kwargs):
                if kwargs.get('read_only'):
                    prompts.append(prompt)
                    return '{"approved":false,"findings":["fix.txt:1 - original defect"]}' if len(prompts) == 1 else '{"approved":true,"findings":[]}'
                if 'fix' in prompt:
                    kwargs['claim']('fix.txt')
                    (project/'fix.txt').write_text('corrected\\n')
                return 'offline worker'
        original = admit({'tasks': [{'id': 'original', 'description': 'Original'}]})
        with Authority(project) as owner:
            with self.assertRaisesRegex(Blocked, 'original defect'):
                Engine(owner, 'original', original, EXECUTOR, adapter=OfflineReviewCycle).invoke()
        fixing = admit({'monitor': {'correction_of': {'run_id': 'original', 'review_execution_id': 'review-id'}}, 'review_base': self.base, 'tasks': [{'id': 'fix', 'description': 'Fix'}]})
        with Authority(project) as owner:
            Engine(owner, 'fixing', fixing, EXECUTOR, adapter=OfflineReviewCycle).invoke()
        self.assertIn('Range: ' + self.base + '..', prompts[1])
        self.assertIn('fix.txt', prompts[1])
        import sqlite3
        db = sqlite3.connect(project/'.coherence/workflow/workflow.sqlite')
        terminal = [row[0] for row in db.execute("SELECT kind FROM execution_observations WHERE run_id='original' AND phase='terminal'")]
        roles = [json.loads(row[0]).get('role') for row in db.execute("SELECT facts FROM execution_observations WHERE run_id='fixing' AND phase='worker'")]
        review_ranges = [json.loads(row[0]) for row in db.execute("SELECT facts FROM execution_observations WHERE run_id='fixing' AND phase='review'")]
        db.close()
        self.assertIn('failed', terminal)
        self.assertIn('fixing_worker', roles)
        self.assertTrue(all(row['review_base'] == self.base for row in review_ranges if 'review_base' in row))

    def test_review_transport_failure_records_selected_range(self):
        project = self.project
        class Offline:
            def __init__(self, *a, **k): pass
            def prompt(self, prompt, **kwargs):
                if kwargs.get('read_only'): raise Blocked('transport failed')
                return 'worker'
        contract = admit({'review_base': self.base, 'tasks': [{'id': 'fix', 'description': 'Fix'}]})
        with Authority(project) as owner:
            with self.assertRaisesRegex(Blocked, 'transport failed'):
                Engine(owner, 'review-failure', contract, EXECUTOR, adapter=Offline).invoke()
        import sqlite3
        db = sqlite3.connect(project/'.coherence/workflow/workflow.sqlite')
        facts = json.loads(db.execute("SELECT facts FROM execution_observations WHERE run_id='review-failure' AND phase='review' AND kind='failed'").fetchone()[0])
        db.close()
        self.assertEqual(facts['review_base'], self.base)

    def test_sdk_error_retains_partial_work_and_releases_writer_lock(self):
        project = self.project
        class OfflineSDKError:
            def __init__(self, *a, **k): pass
            def prompt(self, *a, **k):
                (project/'owned.txt').write_text('partial\n')
                raise Blocked('actual provider operation error')
        with self.assertRaisesRegex(Blocked, 'actual provider'):
            self.execute([{'id': 'fix', 'description': 'Fix'}], OfflineSDKError)
        with Authority(project): pass
        self.assertEqual((project/'owned.txt').read_text(), 'partial\n')
