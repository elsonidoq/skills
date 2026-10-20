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

from coherence_workflow.cli import Coordinate, ROOT, main
from coherence_workflow.intake import admit, load_contract
from coherence_workflow.store import Authority, Blocked, git
from test_custody import IsolatedCustody


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
        from coherence_workflow.registry import validate_schema
        for value in ([], [{'id': 'fix', 'outcome': 'Fix title'}],
                      {'tasks': [{'id': 'fix', 'description': 'Fix title', 'notes': 'optional context'}]}):
            validate_schema('task.schema.json', value)
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
                                 '--project', self.temp.name, '--tasks', str(self.path)],
                                env=dict(os.environ, COHERENCE_PYTHON=sys.executable),
                                text=True, capture_output=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stdout+result.stderr)
        self.assertEqual(json.loads(result.stdout), {'status': 'ready', 'task_ids': ['fix']})


class MinimalTaskConsumerTests(IsolatedCustody):
    def coordinate(self, owner, tasks):
        owner.store.reserve('minimal', 'fixture')
        config = yaml.safe_load((ROOT/'runtime/coherence_workflow/workflows/coordinate.yaml').read_text())
        coordinate = Coordinate(owner, 'minimal', tasks, config, self.parent, {}, {})
        coordinate.intake({})
        return coordinate

    def capture_scopes(self, owner):
        for row in owner.store.db.execute('SELECT containment FROM wf_processes WHERE containment IS NOT NULL'):
            receipt = json.loads(row[0])
            if receipt not in self.receipts:
                self.receipts.append(receipt)

    def test_minimal_real_edit_check_commit_preserves_unrelated_work(self):
        (self.project/'other.txt').write_text('staged user work')
        git(self.project, 'add', '--', 'other.txt')
        (self.project/'custom.md').write_text('unstaged user work')
        (self.project/'untracked-user').write_text('untracked user work')
        index = git(self.project, 'ls-files', '--stage', '--', 'other.txt')
        with Authority(self.project) as owner:
            c = self.coordinate(owner, [{'id': 'fix', 'outcome': 'Fix owned.txt'}])
            self.assertEqual(c.select({}), {'outcome': 'work'})
            task = json.loads(c.current()['contract'])
            c.gateway.tools = c._tools(task)
            self.assertEqual(c.gateway.direct('read_file', {'path': 'owned.txt'})['text'], 'base')
            c.gateway.direct('edit_file', {'path': 'owned.txt', 'old': 'base', 'new': 'fixed'})
            self.assertEqual(json.loads(c.current()['contract'])['owned_paths'], ['owned.txt'])
            self.assertEqual(c.verify({}), {'outcome': 'ok'})
            try:
                self.assertEqual(c.checkpoint({}), {'outcome': 'ok'})
            finally:
                self.capture_scopes(owner)
            self.assertEqual(git(self.project, 'show', 'HEAD:owned.txt'), b'fixed')
            self.assertEqual(git(self.project, 'diff-tree', '--no-commit-id', '--name-only', '-r', 'HEAD'), b'owned.txt\n')
            from coherence_workflow.review_documents import read_review
            bundle = c.review_repair.bundle()
            self.assertEqual(read_review(self.project, bundle, {'path': 'owned.txt', 'revision': 'head'})['text'], 'fixed')
            self.assertEqual(git(self.project, 'ls-files', '--stage', '--', 'other.txt'), index)
            self.assertEqual((self.project/'custom.md').read_text(), 'unstaged user work')
            self.assertEqual((self.project/'untracked-user').read_text(), 'untracked user work')

    def test_explicit_limits_and_dirty_path_refusal(self):
        (self.project/'other.txt').write_text('preexisting user edit')
        with Authority(self.project) as owner:
            c = self.coordinate(owner, [{'id': 'fix', 'outcome': 'Fix title'}])
            c.select({})
            task = json.loads(c.current()['contract'])
            c.gateway.tools = c._tools(task)
            with self.assertRaisesRegex(Blocked, 'dirty owned overlap'):
                c.gateway.direct('write_file', {'path': 'other.txt', 'text': 'overwrite'})
            with self.assertRaisesRegex(Blocked, 'authority storage'):
                c.gateway.direct('write_file', {'path': '.git/config', 'text': 'overwrite'})
            self.assertEqual(task['owned_paths'], [])
            self.assertEqual((self.project/'other.txt').read_text(), 'preexisting user edit')
        with Authority(self.project) as owner:
            owner.store.abandon('minimal')
            owner.store.reserve('limited', 'fixture')
            c = Coordinate(owner, 'limited', [{'id': 'fix', 'outcome': 'Fix', 'owned_paths': ['owned.txt']}], {}, self.parent, {}, {})
            c.intake({}); c.select({})
            c.gateway.tools = c._tools(json.loads(c.current()['contract']))
            from jsonschema.exceptions import ValidationError
            with self.assertRaises(ValidationError):
                c.gateway.direct('write_file', {'path': 'other.txt', 'text': 'overwrite'})

    def test_real_start_reaches_executor_without_administrative_task_metadata(self):
        from test_pi_adapter import manifest
        tasks = self.root/'tasks.yaml'
        tasks.write_text('- id: fix\n  outcome: Fix title\n')
        config = yaml.safe_load((ROOT/'runtime/coherence_workflow/workflows/coordinate.yaml').read_text())
        (self.project/'.coherence').mkdir(mode=0o700, exist_ok=True)
        (self.project/'.coherence/workflow').mkdir(mode=0o700, exist_ok=True)
        sdk = manifest(self.project, tools=False)
        sdk['skills'] = [{'path': str(ROOT/'skills/coordinate-implementation/SKILL.md'),
                          'sha256': config['skills']['coordinate']['sha256'], 'name': 'coordinate-implementation'}]
        sdk_path = self.root/'manifest.json'
        sdk_path.write_text(json.dumps(sdk))
        reached = []
        def executor_boundary(coordinate, manifest, node, task, role, **kwargs):
            reached.append((manifest['profile'], task['id'], role))
            raise Blocked('offline test reached executor boundary; no provider call')
        with patch.object(Coordinate, 'session_adapter', executor_boundary), contextlib.redirect_stdout(io.StringIO()) as output:
            result = main(['start', '--project', str(self.project), '--tasks', str(tasks), '--run', 'entry',
                           '--workflow', str(ROOT/'runtime/coherence_workflow/workflows/coordinate.yaml'),
                           '--manifest', str(sdk_path), '--containment', self.parent])
        self.assertEqual(result, 2, output.getvalue())
        self.assertIn('offline test reached executor boundary', output.getvalue())
        self.assertEqual(reached, [(config['profiles']['sol-medium'], 'fix', 'implement')])
        self.assertEqual((self.project/'owned.txt').read_text(), 'base')

    def test_no_effect_typo_claims_nothing_and_post_selection_drift_is_not_adopted(self):
        with Authority(self.project) as owner:
            c = self.coordinate(owner, [{'id': 'fix', 'outcome': 'Fix title'}])
            c.select({})
            task = json.loads(c.current()['contract'])
            c.gateway.tools = c._tools(task)
            with self.assertRaisesRegex(Blocked, 'edit target missing'):
                c.gateway.direct('edit_file', {'path': 'owned.txt', 'old': 'absent', 'new': 'fixed'})
            self.assertEqual(json.loads(c.current()['contract'])['owned_paths'], [])
            (self.project/'other.txt').write_text('concurrent edit')
            with self.assertRaisesRegex(Blocked, 'unrelated file drift'):
                c.gateway.direct('write_file', {'path': 'owned.txt', 'text': 'fixed'})
            self.assertEqual((self.project/'owned.txt').read_text(), 'base')

    def test_out_of_order_selection_and_optional_project_command(self):
        tasks = [{'id': 'consumer', 'outcome': 'Consume', 'depends': ['producer']},
                 {'id': 'producer', 'description': 'Read and check', 'required': [
                     {'id': 'check', 'check': {'id': 'workflow.Command', 'version': '1',
                                             'args': {'argv': [str(Path(sys.executable).resolve()), '-c', 'pass']}}}]}]
        with Authority(self.project) as owner:
            c = self.coordinate(owner, tasks)
            self.assertEqual(c.current()['task_id'], 'producer')
            c.select({})
            try:
                self.assertEqual(c.verify({}), {'outcome': 'ok'})
                self.assertEqual(c.checkpoint({}), {'outcome': 'ok'})
            finally:
                self.capture_scopes(owner)
            self.assertEqual(c.current()['task_id'], 'consumer')
            self.assertEqual(c.select({}), {'outcome': 'work'})


if __name__ == '__main__':
    unittest.main()
