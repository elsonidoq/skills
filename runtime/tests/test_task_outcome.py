"""Explicit task outcomes stop actual dispatch without treating no-change as failure."""
import json
import sys
from unittest.mock import patch

from coherence_workflow.engine import Engine
from coherence_workflow.intake import admit
from coherence_workflow.pi_adapter import PiAdapter
from coherence_workflow.store import Authority, Blocked, git
from fixtures.support import ProjectTest

EXECUTOR = {'provider': 'fixture', 'model': 'offline', 'effort': 'medium',
            'reviewer': {'provider': 'fixture', 'model': 'offline-reviewer', 'effort': 'medium'}}
TASKS = [{'id': 'A', 'description': 'Required prerequisite', 'owned_paths': ['owned.txt']},
         {'id': 'B', 'description': 'Dependent', 'depends': ['A']}]


class TaskOutcomeTests(ProjectTest):
    def test_unsuccessful_outcome_preserves_work_and_stops_dependents_and_review(self):
        for status, partial in [('blocked', False), ('blocked', True), ('failed', False)]:
            with self.subTest(status=status, partial=partial):
                calls = []
                project = self.project
                class Worker:
                    def __init__(self, *args, **kwargs): pass
                    def prompt(self, prompt, **kwargs):
                        calls.append(prompt)
                        if len(calls) > 1:
                            return '{"approved":true,"findings":[]}'
                        if partial:
                            kwargs['claim']('owned.txt')
                            (project/'owned.txt').write_text('partial\n')
                        return json.dumps({'status': status, 'summary': 'required acceptance remains unmet'})
                run = status + str(partial)
                with Authority(project) as owner:
                    with self.assertRaisesRegex(Blocked, 'required acceptance remains unmet'):
                        Engine(owner, run, admit(TASKS), EXECUTOR, adapter=Worker).invoke()
                    rows = owner.store.db.execute('SELECT task_id,state FROM execution_tasks WHERE run_id=?', (run,)).fetchall()
                    self.assertEqual([tuple(row) for row in rows], [('A', 'failed')])
                    self.assertFalse(owner.store.completed_checkpoints(run))
                    invocation = owner.store.db.execute(
                        "SELECT state,details FROM execution_history WHERE run_id=? AND kind='worker_invocation' "
                        "ORDER BY seq DESC LIMIT 1", (run,)).fetchone()
                    self.assertEqual(invocation['state'], 'returned')
                    self.assertEqual(json.loads(json.loads(invocation['details'])['task_result'])['status'], status)
                self.assertEqual(len(calls), 1)
                self.assertEqual(git(project, 'rev-parse', 'HEAD').decode().strip(), self.base)
                self.assertEqual((project/'owned.txt').read_text(), 'partial\n' if partial else 'base\n')
                if partial:
                    # Restore only this fixture's known bytes for the next subcase.
                    (project/'owned.txt').write_text('base\n')

    def test_successful_no_change_with_blocked_word_in_summary_is_valid(self):
        calls = []
        class Worker:
            def __init__(self, *args, **kwargs): pass
            def prompt(self, prompt, **kwargs):
                calls.append(prompt)
                return ('{"approved":true,"findings":[]}' if kwargs.get('read_only') else
                        '{"status":"completed","summary":"Verified no change; nothing blocked"}')
        with Authority(self.project) as owner:
            result = Engine(owner, 'no-change', admit(TASKS), EXECUTOR, adapter=Worker).invoke()
        self.assertEqual(result['status'], 'complete')
        self.assertEqual(len(calls), 3)
        self.assertTrue(all(item['no_change'] for item in result['checkpoints']))
        self.assertEqual(result['sha'], self.base)

    def test_blocked_return_is_not_bypassed_by_resume(self):
        calls, questions = [], []
        class Worker:
            def __init__(self, *args, **kwargs):
                self.saved_session = {'id': 'fixture', 'file': '/private/fixture.jsonl'}
            def prompt(self, prompt, **kwargs):
                calls.append(prompt)
                if kwargs.get('read_only'):
                    return '{"approved":true,"findings":[]}'
                return ('{"status":"blocked","summary":"missing prerequisite"}' if len(calls) == 1 else
                        '{"status":"completed","summary":"prerequisite now satisfied"}')
        def question(text):
            questions.append(text)
            return '' if len(questions) == 1 else 'Inspected fixture: missing local setup is now supplied; continue same task'
        with Authority(self.project) as owner:
            with self.assertRaises(Blocked):
                Engine(owner, 'resume-block', admit(TASKS), EXECUTOR, adapter=Worker).invoke()
            owner.store.resume('resume-block')
            with self.assertRaisesRegex(Blocked, 'remains unknown'):
                Engine(owner, 'resume-block', admit(TASKS), EXECUTOR, adapter=Worker, resume=True,
                       question=question).invoke()
            self.assertEqual(len(calls), 1)
            owner.store.resume('resume-block')
            result = Engine(owner, 'resume-block', admit(TASKS), EXECUTOR, adapter=Worker, resume=True,
                            question=question).invoke()
        self.assertEqual(result['status'], 'complete')
        self.assertEqual(len(calls), 4)
        self.assertIn('missing prerequisite', questions[0])
        self.assertIn('missing local setup is now supplied', calls[1])

    def test_missing_or_malformed_outcome_cannot_certify_acceptance(self):
        for ordinal, text in enumerate(['Not implemented', '{}',
                                        '{"status":"completed","summary":""}',
                                        '{"status":"unknown","summary":"unmet"}']):
            calls = []
            class Worker:
                def __init__(self, *args, **kwargs): pass
                def prompt(self, prompt, **kwargs):
                    calls.append(prompt)
                    return text
            with self.subTest(text=text), Authority(self.project) as owner:
                with self.assertRaisesRegex(Blocked, 'task result needs'):
                    Engine(owner, 'malformed-' + str(ordinal), admit(TASKS), EXECUTOR, adapter=Worker).invoke()
            self.assertEqual(len(calls), 1)
            self.assertEqual(git(self.project, 'rev-parse', 'HEAD').decode().strip(), self.base)

    def test_blocked_required_check_correction_stops_without_checkpoint(self):
        calls = []
        project = self.project
        class Worker:
            def __init__(self, *args, **kwargs): pass
            def prompt(self, prompt, **kwargs):
                calls.append(prompt)
                if len(calls) == 1:
                    kwargs['claim']('owned.txt')
                    (project/'owned.txt').write_text('partial\n')
                    return '{"status":"completed","summary":"source work done"}'
                return '{"status":"blocked","summary":"no safe correction; required test failed"}'
        tasks = [{**TASKS[0], 'checks': ['echo required-test-failure; exit 1']}, TASKS[1]]
        with Authority(project) as owner:
            with self.assertRaisesRegex(Blocked, 'no safe correction'):
                Engine(owner, 'check-block', admit(tasks), EXECUTOR, adapter=Worker).invoke()
            rows = owner.store.db.execute("SELECT state FROM execution_history WHERE kind='check'").fetchall()
            self.assertEqual([row[0] for row in rows], ['failed'])
        self.assertEqual(len(calls), 2)
        self.assertIn('Actual failed attempt:', calls[1])
        self.assertIn('Return only JSON:', calls[1])
        self.assertEqual((project/'owned.txt').read_text(), 'partial\n')
        self.assertEqual(git(project, 'rev-parse', 'HEAD').decode().strip(), self.base)

    def test_owner_answer_through_adapter_settles_blocked_without_advancing(self):
        host = self.root/'host.py'
        host.write_text('import json\nrequest=json.loads(input())\n'
                        'print(json.dumps({"type":"question","question":"Continue?"}),flush=True)\n'
                        'answer=json.loads(input())["answer"]\n'
                        'print(json.dumps({"type":"result","text":json.dumps({"status":"blocked","summary":answer})}),flush=True)\n')
        questions = []
        def question(text):
            questions.append(text)
            return 'Stop incomplete; required acceptance unrun'
        with patch('coherence_workflow.pi_adapter.host_path', return_value=host), patch.dict(
                'os.environ', {'COHERENCE_NODE': sys.executable}), Authority(self.project) as owner:
            with self.assertRaisesRegex(Blocked, 'Stop incomplete'):
                Engine(owner, 'answer-block', admit(TASKS), EXECUTOR, adapter=PiAdapter, question=question).invoke()
            self.assertEqual(owner.store.db.execute('SELECT count(*) FROM execution_tasks').fetchone()[0], 1)
        self.assertEqual(questions, ['Continue?'])
        self.assertEqual(git(self.project, 'rev-parse', 'HEAD').decode().strip(), self.base)
