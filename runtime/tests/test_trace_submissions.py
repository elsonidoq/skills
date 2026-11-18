"""Offline production return boundaries; submissions are claims, never acceptance."""
import json
from unittest.mock import patch

from coherence_workflow.engine import Engine
from coherence_workflow.intake import admit
from coherence_workflow.pi_adapter import TaskOutcome
from coherence_workflow.store import Authority, Blocked
from fixtures.support import ProjectTest
from test_worker_recovery import EXECUTOR, DIAGNOSIS
from coherence_workflow.graph import graph_saver, task_graph, graph_recovery_action


class SubmissionTests(ProjectTest):
    def rows(self, owner, run, kind):
        return [(r['state'], json.loads(r['details'])) for r in owner.store.db.execute(
            'SELECT state,details FROM execution_history WHERE run_id=? AND kind=? ORDER BY seq', (run, kind))]

    def test_unsuccessful_then_inspected_recovery_retains_report_and_evidence_after_reopen(self):
        project, calls = self.project, []
        class Adapter:
            def __init__(self, *_a, **_k): self.saved_session = None
            def prompt(self, _prompt, **kwargs):
                calls.append('call')
                kwargs['claim']('proof.txt')
                (project/'proof.txt').write_text('failed assertion details\n' if len(calls) == 1 else 'passing details\n')
                self.saved_session = {'id': 'worker', 'file': '/fixture/worker'}
                if len(calls) == 1:
                    return TaskOutcome('incomplete', 'Missing parser. [proof](proof.txt) [missing](missing.txt) [other](other.txt)')
                return 'Fixed parser. [proof](proof.txt)'
        contract = admit([{'id': 'one', 'description': 'parser', 'owned_paths': ['proof.txt', 'missing.txt']}])
        config = {'configurable': {'thread_id': 'submissions'}}
        (project/'other.txt').write_text('unrelated must not be harvested')
        with Authority(project) as owner:
            owner.store.start('submissions', self.base, contract=contract, executor=EXECUTOR)
            engine = Engine(owner, 'submissions', contract, EXECUTOR, adapter=Adapter, resume=True)
            with graph_saver(owner) as saver:
                with self.assertRaisesRegex(Blocked, 'incomplete'):
                    task_graph(engine, saver).invoke({}, config, durability='sync')
            self.assertNotIn('Missing parser.', engine._review_worker_evidence()[0])
            self.assertEqual(owner.store.completed_checkpoints('submissions'), {})
        with Authority(project) as owner:
            engine = Engine(owner, 'submissions', contract, EXECUTOR, adapter=Adapter, resume=True)
            with graph_saver(owner) as saver:
                graph_recovery_action(engine, task_graph(engine, saver), config, 'continue', diagnosis=DIAGNOSIS)
        with Authority(project) as owner:
            rows = self.rows(owner, 'submissions', 'worker_invocation')
            failed = next(f for s, f in rows if s == 'failed')
            returned = next(f for s, f in rows if s == 'returned')
            self.assertEqual(failed['submission']['status'], 'incomplete')
            self.assertIn('Missing parser.', failed['submission']['report'])
            self.assertEqual(failed['submission']['evidence'][0]['content'], 'failed assertion details\n')
            self.assertEqual(len(failed['submission']['gaps']), 2)
            self.assertEqual(returned['submission']['evidence'][0]['content'], 'passing details\n')
            start = [f for s, f in rows if s == 'started'][-1]
            self.assertEqual(start['predecessor_invocation_id'], failed['invocation_id'])
            recovery = self.rows(owner, 'submissions', 'graph_recovery')[-1][1]
            self.assertEqual(start['recovery_id'], recovery['id'])
            self.assertEqual(recovery['reference']['targeted_correction'], DIAGNOSIS)
            self.assertEqual(recovery['action'], 'continue')
            self.assertNotIn('unrelated must not be harvested', json.dumps(rows))
            self.assertEqual(len(calls), 2)

    def test_fixer_fail_then_pass_checks_and_rejected_review_preserve_all_reports(self):
        project, workers, reviews = self.project, [], []
        class Adapter:
            def __init__(self, *_a, **_k): self.saved_session = None
            def prompt(self, prompt, **kwargs):
                if kwargs.get('read_only'):
                    reviews.append(prompt)
                    return json.dumps({'approved': len(reviews) > 1, 'findings': [] if len(reviews) > 1 else ['proof.txt:1 - fix defect'],
                                       'coverage': ['examined fixture'], 'coverage_gaps': []})
                workers.append(prompt)
                kwargs['claim']('proof.txt')
                content = 'ready' if len(workers) != 2 else 'broken'
                (project/'proof.txt').write_text(content)
                return ('original' if len(workers) == 1 else 'fixer ' + str(len(workers))) + ' [proof](proof.txt)'
        task = {'id': 'one', 'description': 'fixture', 'owned_paths': ['proof.txt'],
                'checks': [['python3', '-B', '-c', "from pathlib import Path; assert Path('proof.txt').read_text() == 'ready', 'actual broken check'"]]}
        with Authority(project) as owner:
            result = Engine(owner, 'fix-reports', admit([task]), EXECUTOR, adapter=Adapter).invoke()
            self.assertEqual(result['status'], 'complete')
        with Authority(project) as owner:
            fixer = [f for s, f in self.rows(owner, 'fix-reports', 'fixer_invocation') if s == 'returned']
            self.assertEqual([f['submission']['evidence'][0]['content'] for f in fixer], ['broken', 'ready'])
            self.assertIn('fixer 2', fixer[0]['summary'])
            self.assertEqual(fixer[1]['predecessor_invocation_id'], fixer[0]['invocation_id'])
            start = [f for s, f in self.rows(owner, 'fix-reports', 'fixer_invocation') if s == 'started'][-1]
            decision = owner.store.db.execute('SELECT kind,state FROM execution_history WHERE seq=?',
                                             (start['decision_ref'],)).fetchone()
            self.assertEqual(tuple(decision), ('fixer_check', 'failed'))
            checks = self.rows(owner, 'fix-reports', 'fixer_check')
            self.assertEqual([s for s, _ in checks], ['failed', 'passed'])
            self.assertIn('actual broken check', json.dumps(checks[0]))
            self.assertEqual(checks[0][1]['producer_invocation_id'], fixer[0]['invocation_id'])
            self.assertEqual(checks[1][1]['producer_invocation_id'], fixer[1]['invocation_id'])
            chain = owner.store.review_chain('fix-reports', private=True)['executions']
            self.assertEqual([item['role'] for item in chain], ['reviewer', 'fixer', 'reviewer'])
            self.assertEqual(chain[0]['findings'], [['proof.txt:1 - fix defect']])
            self.assertEqual(chain[-1]['predecessor_execution_id'], chain[1]['execution_id'])
            checkpoint = self.rows(owner, 'fix-reports', 'fixer_checkpoint')[-1][1]
            self.assertEqual(checkpoint['producer_invocation_id'], fixer[-1]['invocation_id'])

    def test_unsuccessful_fixer_return_is_retained_without_acceptance_or_retry(self):
        project, calls = self.project, []
        class Adapter:
            def __init__(self, *_a, **_k): self.saved_session = None
            def prompt(self, _prompt, **kwargs):
                if kwargs.get('read_only'):
                    return json.dumps({'approved': False, 'findings': ['proof.txt:1 - fix defect'], 'coverage': ['fixture'], 'coverage_gaps': []})
                calls.append('worker')
                kwargs['claim']('proof.txt')
                (project/'proof.txt').write_text('original' if len(calls) == 1 else 'failed repair evidence')
                return 'original' if len(calls) == 1 else TaskOutcome('failed', 'repair failed [proof](proof.txt)')
        with Authority(project) as owner:
            with self.assertRaisesRegex(Blocked, 'failed'):
                Engine(owner, 'failed-fix', admit([{'id': 'one', 'description': 'fixture', 'owned_paths': ['proof.txt']}]),
                       EXECUTOR, adapter=Adapter).invoke()
        with Authority(project) as owner:
            failure = [f for s, f in self.rows(owner, 'failed-fix', 'fixer_invocation') if s == 'failed'][0]
            self.assertEqual(failure['submission']['report'], 'repair failed [proof](proof.txt)')
            self.assertEqual(failure['submission']['evidence'][0]['content'], 'failed repair evidence')
            self.assertEqual(self.rows(owner, 'failed-fix', 'fixer_checkpoint'), [])
            self.assertEqual(len(calls), 2)

    def test_capture_failure_does_not_change_actual_return_or_acceptance(self):
        class Adapter:
            def __init__(self, *_a, **_k): pass
            def prompt(self, _prompt, **kwargs):
                return ('{"approved":true,"findings":[],"coverage":["fixture"],"coverage_gaps":[]}'
                        if kwargs.get('read_only') else 'meaningful original report')
        with Authority(self.project) as owner:
            with patch('coherence_workflow.trace_capture.submission_facts', side_effect=RuntimeError('capture unavailable')):
                result = Engine(owner, 'capture-gap', admit([{'id': 'one', 'description': 'fixture'}]),
                                EXECUTOR, adapter=Adapter).invoke()
            self.assertEqual(result['status'], 'complete')
            returned = [f for s, f in self.rows(owner, 'capture-gap', 'worker_invocation') if s == 'returned'][0]
            self.assertEqual(returned['summary'], 'meaningful original report')
            self.assertEqual(returned['submission']['gaps'], ['submission report unavailable or capture failed'])

    def test_rejected_worker_check_keeps_both_submissions_and_file_contents(self):
        project, calls = self.project, []
        class Adapter:
            def __init__(self, *_a, **_k):
                self.saved_session = {'id': 'worker-check-session', 'file': '/fixture/worker-check'}
            def prompt(self, _prompt, **kwargs):
                if kwargs.get('read_only'):
                    return '{"approved":true,"findings":[],"coverage":["fixture"],"coverage_gaps":[]}'
                calls.append('worker')
                kwargs['claim']('proof.txt')
                (project/'proof.txt').write_text('failing' if len(calls) == 1 else 'passing')
                return ('first claim' if len(calls) == 1 else 'corrected claim') + ' Evidence: `proof.txt`'
        task = {'id': 'one', 'description': 'fixture', 'owned_paths': ['proof.txt'],
                'checks': [['python3', '-B', '-c',
                            "from pathlib import Path; assert Path('proof.txt').read_text() == 'passing', 'failure details'"]]}
        with Authority(project) as owner:
            self.assertEqual(Engine(owner, 'worker-check', admit([task]), EXECUTOR, adapter=Adapter).invoke()['status'], 'complete')
        with Authority(project) as owner:
            returned = [f for s, f in self.rows(owner, 'worker-check', 'worker_invocation') if s == 'returned']
            self.assertEqual([f['submission']['evidence'][0]['content'] for f in returned], ['failing', 'passing'])
            self.assertEqual([f['submission']['status'] for f in returned], ['submitted', 'submitted'])
            checks = self.rows(owner, 'worker-check', 'check')
            self.assertEqual([s for s, _ in checks], ['failed', 'passed'])
            self.assertIn('failure details', checks[0][1]['output'])
            self.assertEqual([f['producer_invocation_id'] for _, f in checks], [f['invocation_id'] for f in returned])
            self.assertEqual(self.rows(owner, 'worker-check', 'checkpoint')[-1][1]['producer_invocation_id'], returned[-1]['invocation_id'])

    def test_explicit_references_do_not_read_unsafe_or_credential_paths(self):
        from coherence_workflow.trace_capture import submission_facts
        (self.project/'proof.txt').write_text('ordinary content sentinel-token')
        (self.project/'.env').write_text('must not be retained')
        (self.project/'link.txt').symlink_to(self.project/'proof.txt')
        (self.project/'binary.txt').write_bytes(b'\xff\xfe')
        with patch.dict('os.environ', {'COHERENCE_PARENT_BRIDGE_TOKEN': 'sentinel-token'}):
            from coherence_workflow.engine import _UnsuccessfulOutcome
            self.assertNotIn('sentinel-token', str(_UnsuccessfulOutcome('failed', 'report sentinel-token')))
            facts = submission_facts(self.project, {'owned_paths': ['proof.txt', '.env', 'link.txt', 'binary.txt']},
                'report sentinel-token [proof](proof.txt) [.env](.env) [escape](../outside) [link](link.txt) [binary](binary.txt) [remote](https://example.invalid/proof)')
        self.assertNotIn('sentinel-token', json.dumps(facts))
        self.assertNotIn('must not be retained', json.dumps(facts))
        self.assertEqual(facts['submission']['evidence'][0]['content'], 'ordinary content [excluded credential]')
        self.assertEqual(len(facts['submission']['evidence']), 1)
        self.assertEqual(len(facts['submission']['gaps']), 6)
