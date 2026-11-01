#!/usr/bin/env python3
"""Retired batching carrier now guards no-orchestration and runtime ownership."""
from pathlib import Path
import unittest
from test_intake_contract import TEXT, contract_errors, section

ROOT=Path(__file__).resolve().parents[3]


class RuntimeAuthorityTests(unittest.TestCase):
    def test_interface_cannot_own_orchestration_or_persistence(self):
        introduction=TEXT.split('## Load and Verify',1)[0]
        for phrase in ('existing CLI runs sequential tasks', 'installed Pi SDK',
                       'not effect proof or execution eligibility'):
            self.assertIn(phrase,' '.join(introduction.split()))
            self.assertNotIn(phrase,' '.join(introduction.split()).replace(phrase,'REMOVED'))
        for phrase in ('never adopts or commits unknown work',
                       'the first actionable rejection gets the existing scoped repair/checkpoint'):
            self.assertIn(phrase, TEXT)
            self.assertNotIn(phrase, TEXT.replace(phrase, 'REMOVED', 1))

    def test_worker_role_cannot_recursively_launch_or_commit(self):
        worker=section(TEXT,'Runner-configured worker role')
        for phrase in ('Do NOT launch this CLI','stage/commit or manage workflow state','review read-only'):
            self.assertIn(phrase,worker)
            self.assertTrue(contract_errors(TEXT.replace(phrase,'REMOVED',1)))


if __name__=='__main__':unittest.main(verbosity=2)
