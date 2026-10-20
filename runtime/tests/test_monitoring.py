"""Actual disposable Store tests for closed optional monitoring storage."""
import json
from unittest.mock import patch

from coherence_workflow.monitoring import Recorder, descriptor
from coherence_workflow.store import Authority
from fixtures.support import ProjectTest


class MonitoringStorageTests(ProjectTest):
    def test_closed_append_survives_reopen_and_ordinary_progress(self):
        contract = {'tasks': [{'id': 'one', 'depends': []}], 'monitor': {'tasks': {'one': {'label': 'Public'}}}}
        with Authority(self.project) as owner:
            owner.store.start('run', self.base)
            rec = Recorder(owner.store, 'run')
            self.assertTrue(rec.register(descriptor(contract, {'provider': 'offline', 'model': 'fixture', 'effort': 'medium'})))
            occurrence = rec.occurrence()
            rec.emit(occurrence, 'worker', 'started', task_id='one', facts={'role': 'worker'})
            rec.emit(occurrence, 'worker', 'returned', task_id='one', facts={'role': 'worker'})
            owner.store.task('run', 'one', 'complete', self.base)
            before = dict(owner.store.db.execute('SELECT * FROM execution_tasks').fetchone())
        with Authority(self.project) as owner:
            record = owner.store.monitor('run')
            self.assertEqual([row['kind'] for row in record['observations']], ['started', 'returned'])
            self.assertEqual(record['observations'][0]['occurrence_id'], occurrence)
            retained = json.loads(record['run']['description'])
            self.assertEqual(retained['tasks'][0]['label'], 'Public')
            self.assertEqual(retained['description_version'], 1)
            self.assertTrue(any(phase['pre_recording'] for phase in retained['phases']))
            self.assertTrue(any(phase['possible_branches'] for phase in retained['phases']))
            self.assertEqual(dict(owner.store.db.execute('SELECT * FROM execution_tasks').fetchone()), before)

    def test_invalid_optional_metadata_and_append_failure_do_not_veto_progress(self):
        contract = {'tasks': [{'id': 'one'}], 'monitor': {'tasks': {'one': {'label': ['private']}}}}
        self.assertEqual(descriptor(contract, {})['tasks'][0]['label'], 'Task')
        with Authority(self.project) as owner:
            owner.store.start('run', self.base)
            rec = Recorder(owner.store, 'run')
            self.assertTrue(rec.register(descriptor(contract, {})))
            self.assertIsNone(rec.emit(rec.occurrence(), 'worker', 'started', facts={'role': 'PRIVATE-SENTINEL'}))
            self.assertIsNone(rec.emit(rec.occurrence(), 'checkpoint', 'passed', facts={'baseline': self.base, 'head': self.base, 'no_change': 'false'}))
            with patch.object(owner.store, 'append_monitor_observation', side_effect=RuntimeError('private sentinel')):
                self.assertIsNone(rec.emit(rec.occurrence(), 'worker', 'started'))
            owner.store.task('run', 'one', 'complete', self.base)
            self.assertEqual(owner.store.db.execute('SELECT state FROM execution_tasks').fetchone()[0], 'complete')
