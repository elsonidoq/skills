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
             'checks': [['python3', '-B', '-c', "assert open('new.txt').read() == 'consumer\\n'"]]},
            {'id': 'producer', 'description': 'Produce'}], OfflineOperations)
        self.assertEqual(result['status'], 'complete')
        self.assertEqual(len(sessions), 3)
        self.assertEqual(len({id(s) for s in sessions}), 3)
        self.assertEqual(len(result['checkpoints']), 2)
        self.assertEqual(git(project, 'rev-list', '--count', self.base+'..HEAD'), b'2\n')

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
