"""Offline production producers -> reopened SQLite -> deterministic factual carrier."""
import json
import os
import re
from unittest.mock import patch

from coherence_workflow.engine import Engine
from coherence_workflow.intake import admit
from coherence_workflow.store import Authority
from coherence_workflow.trace_capture import (capture_questions, persist_parent_events,
                                               record_worker_question, submission_facts)
from coherence_workflow.trace_projection import project_trace, render_markdown
from fixtures.support import ProjectTest
from test_trace_submissions import EXECUTOR


class TraceProjectionTests(ProjectTest):
    def test_production_rejected_corrected_worker_fixer_checks_and_all_reviews(self):
        project, workers, reviewers = self.project, [], []
        long_body = 'meaningful ordinary explanation `code`\n' * 2200 + 'THE END\n'
        class Adapter:
            def __init__(self, *_a, **_k):
                self.saved_session = {'id': 'actual-worker', 'file': '/private/sessions/worker.jsonl'}
            def prompt(self, _prompt, **kwargs):
                if kwargs.get('read_only'):
                    reviewers.append(1)
                    return json.dumps({'approved': len(reviewers) > 1,
                        'findings': [] if len(reviewers) > 1 else ['proof.txt:1 - observed defect'],
                        'suggestions': ['ordinary suggestion'],
                        'coverage': ['actual fixture inspection'], 'coverage_gaps': []})
                workers.append(1)
                kwargs['claim']('proof.txt')
                content = ('broken' if len(workers) in (1, 3) else 'ready') + '\n' + long_body
                (project/'proof.txt').write_text(content)
                return 'report ' + str(len(workers)) + ' [proof](proof.txt) [missing](missing.txt)\n' + long_body
        task = {'id': 'one', 'description': 'offline producer', 'owned_paths': ['proof.txt', 'missing.txt'],
                'checks': [['python3', '-B', '-c', "from pathlib import Path; assert Path('proof.txt').read_text().startswith('ready'), 'actual failed validation'"]]}
        with Authority(project) as owner:
            outcome = Engine(owner, 'production', admit([task]), EXECUTOR, adapter=Adapter).invoke()
            self.assertEqual(outcome['status'], 'complete')
            original = owner.store.db.execute('SELECT * FROM execution_history').fetchall()
            snapshot = project_trace(owner.store, 'production')
            source = owner.store.trace_source('production')
            # Publication is excluded even from the high water mark and digest.
            owner.store.history('production', None, 'trace_publication', 'prepared', {'body': 'not factual content'})
            self.assertEqual(snapshot, project_trace(owner.store, 'production'))
            # Frozen source remains valid when new operational facts arrive.
            owner.store.history('production', None, 'graph_wait', 'waiting', {'invocation_id': 'later'})
            self.assertEqual(snapshot, project_trace(owner.store, 'production', source=source))
            self.assertNotEqual(snapshot['snapshot_id'], project_trace(owner.store, 'production')['snapshot_id'])
            self.assertEqual([tuple(row) for row in original],
                [tuple(row) for row in owner.store.db.execute('SELECT * FROM execution_history WHERE seq<=?', (original[-1]['seq'],))])
        with Authority(project) as owner:
            self.assertEqual(snapshot, project_trace(owner.store, 'production', source=source))
            current = project_trace(owner.store, 'production')
        self.assertEqual(len(workers), 4)
        submissions = [event['details']['submission'] for event in snapshot['events']
                       if event['kind'] in {'worker_invocation', 'fixer_invocation'} and event['state'] == 'returned']
        self.assertEqual(len(submissions), 4)
        for index, submitted in enumerate(submissions, 1):
            self.assertEqual(submitted['report'], 'report ' + str(index) + ' [proof](proof.txt) [missing](missing.txt)\n' + long_body)
            self.assertEqual(submitted['evidence'][0]['content'], ('broken' if index in (1, 3) else 'ready') + '\n' + long_body)
            self.assertTrue(submitted['gaps'])
        checks = [event for event in snapshot['events'] if event['kind'] in {'check', 'fixer_check'}]
        self.assertEqual([item['state'] for item in checks], ['failed', 'passed', 'failed', 'passed'])
        self.assertIn('actual failed validation', checks[0]['details']['output'])
        self.assertEqual([item['state'] for item in snapshot['review_attempts']],
                         ['dispatched', 'rejected', 'dispatched', 'approved', 'dispatched', 'approved'])
        self.assertEqual(snapshot['review_attempts'][1]['findings'], ['proof.txt:1 - observed defect'])
        self.assertEqual(snapshot['review_attempts'][1]['suggestions'], ['ordinary suggestion'])
        self.assertEqual([item['role'] for item in snapshot['review_executions']], ['reviewer', 'fixer', 'reviewer'])
        self.assertEqual(snapshot['counts']['implementation_invocations']['observed'], 4)
        self.assertEqual(snapshot['counts']['review_executions']['observed'], 3)
        self.assertEqual(snapshot['owner_acceptance']['state'], 'NOT VERIFIED')
        self.assertEqual(snapshot['implementation_outcome']['state'], 'complete')
        self.assertTrue(snapshot['references'])
        self.assertNotIn('/private/sessions/worker.jsonl', render_markdown(current))
        self.assertNotIn('Current execution authority:', render_markdown(current))
        markdown = render_markdown(snapshot)
        fence = re.search(r'^(`+)json$', markdown, re.M).group(1)
        self.assertEqual(json.loads(markdown.split(fence + 'json\n', 1)[1].rsplit('\n' + fence, 1)[0]), snapshot)

    def test_actual_graph_failure_inspected_escalation_and_supported_commit(self):
        from test_worker_recovery import GraphRecoveryTests, DIAGNOSIS
        # Reuse the existing complete production recovery scenario, not a made-up event schema.
        GraphRecoveryTests.exercise(self, 'escalate')
        with Authority(self.project) as owner:
            snapshot = project_trace(owner.store, 'graph-recovery')
        failed = next(item for item in snapshot['events']
                      if item['kind'] == 'worker_invocation' and item['state'] == 'failed')
        self.assertEqual(failed['details']['submission']['report'], 'inspected parser defect')
        recovery = next(item for item in snapshot['events'] if item['kind'] == 'graph_recovery')
        self.assertEqual(recovery['details']['reference']['targeted_correction'], DIAGNOSIS)
        escalations = [item for item in snapshot['events'] if item['kind'] == 'implementation_escalation']
        self.assertEqual([item['state'] for item in escalations], ['started', 'completed'])
        self.assertEqual(escalations[0]['details']['executor']['model'], 'strong')
        self.assertIn(escalations[-1]['details']['sha'], snapshot['references'])
        self.assertEqual(snapshot['counts']['implementation_invocations']['observed'], 3)

    def test_same_review_execution_failed_then_corrected_keeps_every_attempt(self):
        with Authority(self.project) as owner:
            store = owner.store
            store.start('review-retry', self.base)
            store.review_dispatch('review-retry', 'review-one', review_base=self.base, review_head=self.base)
            store.review_outcome('review-retry', 'review-one', 'failed', findings=[],
                                 references={'error': 'actual provider field limit', 'base': self.base, 'head': self.base})
            store.review_size_retry_dispatch('review-retry', 'review-one', review_base=self.base, review_head=self.base)
            store.review_outcome('review-retry', 'review-one', 'approved', findings=[],
                                 references={'base': self.base, 'head': self.base,
                                             'review_summary': {'coverage': ['examined actual range'], 'coverage_gaps': []}})
            snapshot = project_trace(store, 'review-retry')
        with Authority(self.project) as owner:
            self.assertEqual(snapshot, project_trace(owner.store, 'review-retry'))
        self.assertEqual([item['state'] for item in snapshot['review_attempts']], ['dispatched', 'failed', 'dispatched', 'approved'])
        self.assertEqual(snapshot['counts']['review_executions']['observed'], 1)
        self.assertEqual(snapshot['counts']['review_invocations']['observed'], 2)
        self.assertIn('actual provider field limit', render_markdown(snapshot))

    def test_interleaved_parent_worker_terminal_questions_exact_distinct_stages(self):
        with Authority(self.project) as owner:
            store = owner.store
            store.start('questions', self.base)
            events = [
                {'version': 1, 'id': 'p1', 'kind': 'owner_call', 'tool_call_id': 'a', 'request_id': 'parent-r',
                 'input': {'question': 'Owner wording A?', 'options': ['one', 'two']}},
                {'version': 1, 'id': 'p2', 'kind': 'owner_call', 'tool_call_id': 'b', 'input': {'question': 'Owner wording B?'}},
                {'version': 1, 'id': 'p3', 'kind': 'owner_result', 'tool_call_id': 'b',
                 'content': [{'type': 'text', 'text': 'cancelled'}], 'details': {'cancelled': True}, 'is_error': False},
                {'version': 1, 'id': 'p4', 'kind': 'owner_result', 'tool_call_id': 'a',
                 'content': [{'type': 'text', 'text': 'actual owner answer'}],
                 'details': {'response': {'selection': 'two', 'freeform': 'actual freeform', 'comment': 'ordinary comment'}}, 'is_error': False},
                {'version': 1, 'id': 'p5', 'kind': 'owner_call', 'tool_call_id': 'unanswered', 'input': {'question': 'No result?'}},
                {'version': 1, 'id': 'p6', 'kind': 'gap', 'tool_call_id': 'unanswered', 'reason': 'final result absent'},
                {'version': 1, 'id': 'p7', 'kind': 'coordinator_reply', 'request_id': 'parent-r',
                 'answer': 'coordinator answer not equal to owner', 'responder': 'coordinator', 'delivery': 'sent'}]
            persist_parent_events(store, 'questions', events)
            persist_parent_events(store, 'questions', events)
            record_worker_question(store, 'questions', 'one', 'i1', 'requested', tool_call_id='w1', question='Worker A?')
            record_worker_question(store, 'questions', 'two', 'i2', 'requested', tool_call_id='w2', question='Worker B?')
            record_worker_question(store, 'questions', 'two', 'i2', 'resolved', tool_call_id='w2', resolution='no')
            record_worker_question(store, 'questions', 'one', 'i1', 'parent_request', tool_call_id='w1', request_id='parent-r')
            record_worker_question(store, 'questions', 'one', 'i1', 'resolved', tool_call_id='w1', resolution='different technical resolution')
            record_worker_question(store, 'questions', 'one', 'i1', 'delivery_failed', tool_call_id='w1', error_type='BrokenPipeError')
            record_worker_question(store, 'questions', 'two', 'continuation', 'continuation_returned',
                                   predecessor_invocation_id='i2', tool_call_id='w2')
            from coherence_workflow.pi_adapter import terminal_question
            callback = capture_questions(terminal_question, store, 'questions')
            with patch('sys.stdin.isatty', return_value=True), patch('builtins.input', return_value='actual terminal no'):
                callback('Actual terminal question?')
            before = project_trace(store, 'questions')
        with Authority(self.project) as owner:
            self.assertEqual(before, project_trace(owner.store, 'questions'))
        self.assertEqual(before['counts']['questions']['observed'], 6)
        groups = before['questions']
        a = next(item for item in groups if item['identity'] == ['owner_tool', 'a'])
        self.assertEqual(a['stages'][0]['facts']['input']['question'], 'Owner wording A?')
        self.assertEqual(a['stages'][1]['facts']['details']['response']['freeform'], 'actual freeform')
        worker = next(item for item in groups if item['identity'] == ['worker', 'one', 'i1', 'w1'])
        self.assertEqual(worker['stages'][-2]['facts']['resolution'], 'different technical resolution')
        self.assertEqual(worker['stages'][-1]['state'], 'delivery_failed')
        self.assertIn('no synthetic answer', '\n'.join(before['gaps']))
        self.assertIn('coordinator answer not equal to owner', render_markdown(before))
        self.assertEqual(before['owner_acceptance']['state'], 'NOT VERIFIED')

    def test_missing_identity_old_capture_unknown_totals_and_privacy(self):
        with Authority(self.project) as owner:
            store = owner.store
            store.start('old', self.base)
            empty = project_trace(store, 'old')
            self.assertEqual(empty['counts']['questions'], {'observed': 0, 'total': None})
            self.assertEqual(empty['coverage']['questions']['state'], 'unavailable')
            store.history('old', 'one', 'worker_invocation', 'returned', {'summary': 'old ordinary claim',
                'session': {'id': 'logical-worker', 'file': '/private/worker'},
                'prompt': 'RAW ASSIGNMENT MUST NOT APPEAR', 'token': 'credential-sentinel',
                'error': 'failure /private/worker credential-sentinel', 'environment': {'dump': 'excluded environment'}})
            record_worker_question(store, 'old', 'one', None, 'requested', question='ordinary unpaired question')
            (self.project/'proof.txt').write_text('ordinary full evidence credential-sentinel\n```````\n')
            with patch.dict(os.environ, {'COHERENCE_PARENT_BRIDGE_TOKEN': 'credential-sentinel'}):
                facts = submission_facts(self.project, {'owned_paths': ['proof.txt']},
                                         'ordinary claim [proof](proof.txt) credential-sentinel')
            store.history('old', 'one', 'worker_invocation', 'failed', {'invocation_id': 'failed', **facts})
            store.history('old', 'one', 'worker_invocation', 'started', {'invocation_id': 'retry',
                'predecessor_invocation_id': 'failed', 'recovery_id': 'inspected'})
            store.history('old', 'one', 'graph_recovery', 'recorded', {'id': 'inspected', 'action': 'escalate',
                'reference': {'targeted_correction': 'actual inspected diagnosis'}})
            store.history('old', 'one', 'implementation_escalation', 'started', {'invocation_id': 'retry',
                'executor': {'provider': 'fixture', 'model': 'stronger'}, 'predecessor': 'failed'})
            source = store.trace_source('old')
            snapshot = project_trace(store, 'old')
            self.assertEqual(source, store.trace_source('old'))
        body = render_markdown(snapshot)
        for private in ('RAW ASSIGNMENT MUST NOT APPEAR', 'credential-sentinel', '/private/worker', 'excluded environment'):
            self.assertNotIn(private, body)
        for ordinary in ('ordinary unpaired question', 'ordinary claim', 'ordinary full evidence',
                         'actual inspected diagnosis', 'logical-worker', 'stronger', '```````'):
            self.assertIn(ordinary, body)
        self.assertEqual(snapshot['counts']['implementation_invocations']['observed'], 2)
        self.assertEqual(snapshot['counts']['questions'], {'observed': 0, 'total': None})
        self.assertTrue(any('identity unavailable' in gap for gap in snapshot['gaps']))
        self.assertTrue(any('older or absent capture' in gap for gap in snapshot['gaps']))
        self.assertEqual(snapshot['owner_acceptance']['state'], 'NOT VERIFIED')
