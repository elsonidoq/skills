"""T003/V3 checks runner-owned real evidence, not worker confidence."""
import copy
import tempfile
import unittest
from pathlib import Path

from coherence_workflow.store import Authority, Blocked, digest
from coherence_workflow.verification import Verification, unittest_oracle
from fixtures.support import make_project


def oracle(args):
    # An actual deliberate oracle, not a mocked subprocess exit.
    value = Path(args['path']).read_text()
    return {'exit_code': 0 if value == 'expected' else 1, 'collected': 1,
            'output': 'expected exact file bytes: ' + repr(value)}


class RequiredEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.project = make_project(Path(self.temp.name) / 'project')
        self.owner = Authority(self.project)
        self.owner.store.reserve('run', 'config')
        self.spec = {'version': '1', 'schema': {'type': 'object', 'properties': {'path': {'const': str(self.project / 'owned.txt')}},
                     'required': ['path'], 'additionalProperties': False}, 'execute': oracle}
        item = {'id': 'T/V1', 'criterion': 'exact bytes', 'check': {'id': 'exact', 'version': '1',
                'args': {'path': str(self.project / 'owned.txt')}}, 'gates': [], 'producer_dependencies': [],
                'pass_condition': 'bytes equal expected', 'expected_evidence': 'actual file oracle'}
        self.task = {'id': 'T', 'owned_paths': ['owned.txt'], 'required': [item]}
        self.verify = Verification(self.owner, 'run', {'exact': self.spec}, {'fixture': 'v1'})

    def tearDown(self):
        self.owner.close(); self.temp.cleanup()

    def test_deliberate_failure_and_current_real_pass(self):
        evidence = self.verify.run_checks(self.task)
        self.assertEqual(self.verify.audit(self.task, evidence)[0]['status'], 'failed')
        (self.project / 'owned.txt').write_text('expected')
        evidence = self.verify.run_checks(self.task)
        self.assertEqual(self.verify.audit(self.task, evidence)[0]['status'], 'satisfied')
        self.assertEqual(evidence[0]['collected'], 1)
        self.assertEqual(len(evidence[0]['revision']), 40)

    def test_missing_stale_irrelevant_conflicting_unrun_insufficient(self):
        (self.project / 'owned.txt').write_text('expected')
        evidence = self.verify.run_checks(self.task)
        for bad in ([], evidence + evidence, [{**evidence[0], 'item_id': 'unknown'}],
                    [{**evidence[0], 'output': 'forged worker confidence'}]):
            self.assertEqual(self.verify.audit(self.task, bad)[0]['status'], 'insufficient-evidence')
        (self.project / 'owned.txt').write_text('changed')
        self.assertEqual(self.verify.audit(self.task, evidence)[0]['status'], 'insufficient-evidence')
        self.verify.checks = {}
        self.assertEqual(self.verify.run_checks(self.task)[0]['status'], 'insufficient-evidence')

    def test_command_exit_is_meaningful_without_collection_count(self):
        self.spec['execute'] = lambda args: {'exit_code': 0, 'output': ''}
        evidence = self.verify.run_checks(self.task)
        self.assertEqual(self.verify.audit(self.task, evidence)[0]['status'], 'satisfied')
        self.spec['execute'] = lambda args: {'exit_code': 1, 'output': 'actual command failure'}
        evidence = self.verify.run_checks(self.task)
        self.assertEqual(self.verify.audit(self.task, evidence)[0]['status'], 'failed')

    def test_shared_check_executes_once_and_maps_every_item(self):
        calls = []
        def execute(args):
            calls.append(args)
            return oracle(args)
        self.spec['execute'] = execute
        self.task['required'].append({**self.task['required'][0], 'id': 'T/V2'})
        evidence = self.verify.run_checks(self.task)
        self.assertEqual(len(calls), 1)
        self.assertTrue(all(e['item_ids'] == ['T/V1', 'T/V2'] for e in evidence))

    def test_unrelated_file_does_not_invalidate(self):
        evidence = self.verify.run_checks(self.task)
        (self.project / 'custom.md').write_text('unrelated')
        self.assertEqual(self.verify.audit(self.task, evidence)[0]['status'], 'failed')
        changed_environment = Verification(self.owner, 'run', {'exact': self.spec}, {'fixture': 'v2'})
        self.assertEqual(changed_environment.audit(self.task, evidence)[0]['status'], 'insufficient-evidence')

    def test_empty_selector_rejects(self):
        with self.assertRaises(Blocked): unittest_oracle({'selector': '', 'test_file': 'runtime/tests/test_verification.py'})

    def test_manual_stop_requires_current_external_binding(self):
        gate = {'id': 'sample-stop', 'kind': 'manual', 'scope': 'sample only'}
        for action in ('deny', 'cancel', 'approve'):
            request = self.verify.request_sample(self.task, gate, 'owned.txt', 'config')
            with self.assertRaises(Blocked): self.verify.require_sample(request, self.task, 'config')
            external = []
            answer = {'action': action, 'binding_hash': digest(request), 'actor': 'fixture-only'}
            self.verify.answer_sample(request, answer, verify_owner=lambda a: external.append(a))
            self.assertEqual(external, [answer])
            if action == 'approve':
                self.assertTrue(self.verify.require_sample(request, self.task, 'config'))
                with self.assertRaises(Blocked): self.verify.require_sample(request, self.task, 'different-config')
            else:
                with self.assertRaises(Blocked): self.verify.require_sample(request, self.task, 'config')
            with self.assertRaises(Blocked): self.verify.answer_sample(request, answer, verify_owner=lambda a: None)
        (self.project / 'owned.txt').write_text('hash drift')
        with self.assertRaises(Blocked): self.verify.require_sample(request, self.task, 'config')
