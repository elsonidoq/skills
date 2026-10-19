#!/usr/bin/env python3
"""Retired batching carrier now guards no-orchestration and runtime ownership."""
from pathlib import Path
import unittest
from test_intake_contract import TEXT, contract_errors, section

ROOT=Path(__file__).resolve().parents[3]


class RuntimeAuthorityTests(unittest.TestCase):
    def test_interface_cannot_own_orchestration_or_persistence(self):
        introduction=TEXT.split('## Load and Verify',1)[0]
        for phrase in ('Python LangGraph/SQLite','cannot select tasks, models, sessions, retries, repairs, commits or acceptance',
                       'No background LLM decides workflow transitions','Pi persistence is conversation data'):
            self.assertIn(phrase,' '.join(introduction.split()))
            self.assertNotIn(phrase,' '.join(introduction.split()).replace(phrase,'REMOVED'))
        self.assertEqual(contract_errors(TEXT),[])

    def test_planning_selection_is_separately_owned(self):
        self.assertNotIn('references/batch-routing.md',TEXT)
        planning=ROOT/'skills/planner/references/profile-selection.md'
        self.assertTrue(planning.is_file())
        body=planning.read_text()
        for phrase in ('six-factor assessment','Family rationale','Effort rationale',
                       'readiness conjunction','Sol with exactly medium supported effort'):
            self.assertIn(phrase,body)
        for consumer in ('planner','planning-brainstorming','delegating-architectural-planning'):
            self.assertIn('references/profile-selection.md',(ROOT/'skills'/consumer/'SKILL.md').read_text())

    def test_worker_role_cannot_recursively_launch_or_commit(self):
        worker=section(TEXT,'Runner-configured worker role')
        for phrase in ('Do NOT launch this CLI','stage/commit or manage workflow state','review read-only'):
            self.assertIn(phrase,worker)
            self.assertTrue(contract_errors(TEXT.replace(phrase,'REMOVED',1)))


if __name__=='__main__':unittest.main(verbosity=2)
