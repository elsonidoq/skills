"""Six task checks through the real CLI and immediate operation consumers."""
import contextlib
import copy
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import yaml

from coherence_workflow.cli import ROOT, main
from coherence_workflow.intake import admit, load_contract
from coherence_workflow.store import Authority, Blocked, git
from coherence_workflow.verification import commands


class TaskLinterTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'tasks.json'

    def test_input_exists_readable(self):
        with self.assertRaisesRegex(Blocked, 'cannot read task input'):
            load_contract(self.path)
        self.path.mkdir()
        with self.assertRaisesRegex(Blocked, 'cannot read task input'):
            load_contract(self.path)

    def test_parses_json_yaml_task_lists(self):
        for suffix, text in [('.json', '[{"id":"fix","outcome":"Fix title"}]'),
                             ('.yaml', 'tasks:\n- id: fix\n  description: Fix title\n')]:
            path = self.path.with_suffix(suffix)
            path.write_text(text)
            self.assertEqual(load_contract(path)['tasks'][0]['id'], 'fix')
            path.write_text('{ broken: [')
            with self.assertRaisesRegex(Blocked, 'cannot parse task input'):
                load_contract(path)
        for value in (None, {}, 'tasks', {'tasks': {}}):
            with self.assertRaisesRegex(Blocked, 'task list'):
                admit(value)

    def test_each_task_needs_id_and_work(self):
        for task in ({}, {'id': 'fix'}, {'id': '', 'outcome': 'Fix'},
                     {'id': 'fix', 'description': ' '}, 'fix'):
            with self.assertRaisesRegex(Blocked, 'needs|need'):
                admit([task])

    def test_packaged_task_schema_has_no_hidden_metadata_requirements(self):
        from jsonschema import validate
        schema = json.loads((ROOT/'runtime/coherence_workflow/schemas/task.schema.json').read_text())
        for value in ([], [{'id': 'fix', 'outcome': 'Fix title'}],
                      {'tasks': [{'id': 'fix', 'description': 'Fix title', 'notes': 'optional context'}]}):
            validate(value, schema)
            admit(value)

    def test_ids_unique(self):
        with self.assertRaisesRegex(Blocked, 'duplicate task id: fix'):
            admit([{'id': 'fix', 'outcome': 'A'}, {'id': 'fix', 'outcome': 'B'}])

    def test_dependency_references_exist(self):
        with self.assertRaisesRegex(Blocked, 'missing dependency: absent'):
            admit([{'id': 'fix', 'outcome': 'Fix', 'depends': ['absent']}])
        with self.assertRaisesRegex(Blocked, 'depends must be a list'):
            admit([{'id': 'fix', 'outcome': 'Fix', 'depends': 'fix'}])

    def test_dependency_cycles(self):
        for tasks in ([{'id': 'a', 'outcome': 'A', 'depends': ['a']}],
                      [{'id': 'a', 'outcome': 'A', 'depends': ['b']},
                       {'id': 'b', 'outcome': 'B', 'depends': ['a']}]):
            with self.assertRaisesRegex(Blocked, 'dependency cycle'):
                admit(tasks)

    def test_authored_required_command_is_preserved_for_the_existing_consumer(self):
        command = ['python3', '-B', '-c', "print('authored command')"]
        contract = {'tasks': [{'id': 'author', 'outcome': 'Preserve command', 'required': [
            {'id': 'required-command', 'description': 'Semantic criterion', 'check': command}]}]}
        admitted = admit(contract)
        self.assertEqual(admitted['tasks'][0]['required'][0]['check'], command)
        self.assertEqual(commands(admitted['tasks'][0]), [command])

    def test_out_of_order_and_optional_fields_preserved(self):
        value = {'origin': 'anything', 'sources': [], 'tasks': [
            {'id': 'consumer', 'outcome': 'Consume', 'depends': ['producer'],
             'order': 0, 'context_group': 'story', 'owned_paths': ['title.txt'],
             'required': [], 'notes': 'Useful context'},
            {'id': 'producer', 'description': 'Produce', 'order': 99}]}
        before = copy.deepcopy(value)
        result = admit(value)
        self.assertEqual([t['id'] for t in result['tasks']], ['producer', 'consumer'])
        self.assertEqual(result['tasks'][1], value['tasks'][0])
        self.assertEqual(value, before)

    def test_lowest_ready_id_is_reselected_after_each_task(self):
        tasks = [
            {'id': 'T008', 'outcome': 'Eight', 'depends': ['T002']},
            {'id': 'T005', 'outcome': 'Five', 'depends': ['T004']},
            {'id': 'T004', 'outcome': 'Four', 'depends': ['T002', 'T003']},
            {'id': 'T003', 'outcome': 'Three', 'depends': ['T001']},
            {'id': 'T002', 'outcome': 'Two', 'depends': ['T001']},
            {'id': 'T001', 'outcome': 'One'},
        ]
        self.assertEqual([task['id'] for task in admit(tasks)['tasks']],
                         ['T001', 'T002', 'T003', 'T004', 'T005', 'T008'])

    def test_empty_start_has_no_storage_reservation_or_worker(self):
        self.path.write_text('[]')
        project = Path(self.temp.name) / 'project'
        project.mkdir()
        with patch('coherence_workflow.cli.Authority', side_effect=AssertionError('reserved')), \
             patch('coherence_workflow.cli.PiAdapter', side_effect=AssertionError('worker')), \
             contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(main(['start', '--project', str(project), '--tasks', str(self.path), '--run', 'empty']), 0)
        self.assertEqual(json.loads(output.getvalue()), {'status': 'no tasks'})
        self.assertEqual(list(project.iterdir()), [])

    def test_actual_entry_intake_without_administrative_arguments(self):
        import subprocess
        self.path.write_text('[{"id":"fix","outcome":"Fix title"}]')
        result = subprocess.run([str(ROOT/'scripts/coordinate-implementation'), 'intake',
                                 '--tasks', str(self.path)],
                                env=dict(os.environ, COHERENCE_PYTHON=sys.executable),
                                text=True, capture_output=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stdout+result.stderr)
        self.assertEqual(json.loads(result.stdout), {'status': 'ready', 'task_ids': ['fix']})
