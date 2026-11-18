"""Offline launch transport and real publisher boundary; no external grants/effects."""
import contextlib
import copy
import io
import json
import unittest
from unittest.mock import patch

from coherence_workflow import cli
from coherence_workflow.engine import Engine
from coherence_workflow.store import Authority, Blocked
from fixtures.support import ProjectTest
import test_trace_publication as publication

ISSUE = publication.ISSUE


class DeliveryScopeTests(ProjectTest):
    def test_cli_start_and_resume_retain_exact_scope_without_new_intake(self):
        executor = {'provider': 'fixture', 'model': 'original', 'effort': 'medium',
                    'reviewer': {'provider': 'fixture', 'model': 'review', 'effort': 'medium'}}
        scope = {'target': ISSUE, 'authority': {'run_id': 'scope-run', 'target': ISSUE,
                 'operations': ['trace_comment', 'link_comment'], 'approval_ref': 'actual owner message'},
                 'known_linked_prs': []}
        tasks, selected = self.root/'tasks.json', self.root/'executor.json'
        tasks.write_text(json.dumps([{'id': 'one', 'description': 'bare task without issue'}]))
        selected.write_text(json.dumps(executor))
        seen = []

        def stop(engine, saver, **kwargs):
            # This is after production graph input persistence/restoration, before dispatch.
            seen.append(copy.deepcopy(engine.delivery_scope))
            raise Blocked('controlled offline stop before worker')

        with patch('coherence_workflow.graph.task_graph', side_effect=stop), \
             contextlib.redirect_stdout(io.StringIO()), patch.dict('os.environ', {
                 'COHERENCE_PARENT_BRIDGE_SOCKET': '', 'COHERENCE_PARENT_BRIDGE_TOKEN': '',
                 'COHERENCE_PARENT_BRIDGE_SESSION': '', 'COHERENCE_PARENT_BRIDGE_RUN': ''}):
            self.assertEqual(cli.main(['start', '--project', str(self.project), '--tasks', str(tasks),
                             '--executor', str(selected), '--run', 'scope-run',
                             '--delivery-scope', json.dumps(scope)]), 2)
            with Authority(self.project) as authority:
                saved = authority.store.input('scope-run')
                self.assertEqual(saved['authority']['delivery_scope'], scope)
                self.assertEqual(saved['executor'], executor)
                self.assertEqual(saved['authority']['paid_scope']['apis'], [])
                self.assertTrue(saved['authority']['routine_authority'])
            self.assertEqual(cli.main(['resume', '--project', str(self.project), '--run', 'scope-run']), 2)
        self.assertEqual(seen, [scope, scope])
        # Empty legacy lists remain no-op, even with scope that cannot authorize writes.
        tasks.write_text('[]')
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(cli.main(['start', '--project', str(self.project), '--tasks', str(tasks),
                                      '--delivery-scope', '{}']), 0)


class DeliveryBoundaryTests(unittest.TestCase):
    """Reuse the production subprocess fake and its independent full-body readback."""
    setUp = publication.PublicationTests.setUp
    remote = publication.PublicationTests.remote
    update = publication.PublicationTests.update
    def engine(self, scope):
        # Retain exactly the launch carrier in the existing private input owner.
        self.store.db.execute('UPDATE execution_run_inputs SET authority=? WHERE run_id=?',
                              (json.dumps({'delivery_scope': scope}), 'run'))
        self.store.db.commit()
        engine = object.__new__(Engine)
        engine.run = 'run'
        engine.delivery_scope = copy.deepcopy(scope)
        engine.authority = type('Authority', (), {'store': self.store})()
        return engine

    def test_carrier_forwards_unchanged_and_publisher_rejects_scope_drift(self):
        scope = {'target': ISSUE, 'authority': {'run_id': 'run', 'target': ISSUE,
                 'operations': ['trace_comment'], 'approval_ref': 'owner grant'}, 'known_linked_prs': []}
        engine = self.engine(scope)
        with patch('coherence_workflow.trace_publication.publish_trace') as publish:
            engine.publish_delivery_trace(gh=self.gh)
            publish.assert_called_once_with(self.store, 'run', **scope, gh=self.gh)
        for value in (None, {}, {**scope, 'authority': {**scope['authority'], 'run_id': 'other'}},
                      {**scope, 'authority': {**scope['authority'], 'target': ISSUE+'0'}},
                      {**scope, 'authority': {**scope['authority'], 'operations': ['link_comment']}}):
            engine = self.engine(value)
            result = engine.publish_delivery_trace(gh=self.gh)
            self.assertEqual(result['state'], 'deferred')
            self.assertTrue(result['correction'])
            self.assertEqual(self.remote()['posts'], 0)
        engine = self.engine(scope)
        engine.delivery_scope['authority']['approval_ref'] = 'replacement'
        self.assertEqual(engine.publish_delivery_trace(gh=self.gh)['state'], 'deferred')
        self.assertEqual(self.remote()['posts'], 0)
        engine = self.engine(scope)
        result = engine.publish_delivery_trace(gh=self.gh)
        self.assertEqual(result['state'], 'confirmed', result)
        self.assertEqual(engine.delivery_scope, scope)
