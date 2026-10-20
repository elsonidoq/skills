"""Actual project command behavior, not universal evidence formatting."""
from coherence_workflow.verification import run_checks
from coherence_workflow.store import Blocked
from fixtures.support import ProjectTest


class ProjectCheckTests(ProjectTest):
    def test_checks_optional_and_zero_collection_output_not_required(self):
        self.assertEqual(run_checks(self.project, {'id': 'fix'}), [])
        self.assertEqual(run_checks(self.project, {'id': 'fix', 'checks': ['true']})[0]['exit_code'], 0)

    def test_actual_argv_and_required_command_mapping(self):
        results = run_checks(self.project, {'id': 'fix', 'required': [
            {'id': 'project-check', 'check': {'argv': ['python3', '-B', '-c', 'assert 2+2 == 4']}}]})
        self.assertEqual(results[0]['exit_code'], 0)

    def test_failed_command_is_not_success(self):
        with self.assertRaisesRegex(Blocked, 'exit 19'):
            run_checks(self.project, {'id': 'fix', 'checks': ['exit 19']})

    def test_bad_command_reports_actual_operation(self):
        with self.assertRaises(FileNotFoundError):
            run_checks(self.project, {'id': 'fix', 'checks': [['/nonexistent/coherence-test']]})
        with self.assertRaisesRegex(Blocked, 'command string or argv'):
            run_checks(self.project, {'id': 'fix', 'checks': [{'id': 'removed.catalogue'}]})
