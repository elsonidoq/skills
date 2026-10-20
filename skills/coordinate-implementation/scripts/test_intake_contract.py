#!/usr/bin/env python3
"""Small operative skill checks, not runtime eligibility or model-obedience proof."""
from pathlib import Path
import re
import unittest

TEXT = (Path(__file__).parents[1]/'SKILL.md').read_text()


def section(text, heading):
    marker = '## ' + heading
    start = text.find(marker)
    if start < 0: return ''
    end = re.search(r'\n## ', text[start+len(marker):])
    return ' '.join((text[start:] if end is None else text[start:start+len(marker)+end.start()]).split())


GUARDS = {
    'Load and Verify': ('exactly six linter checks', 'reserves nothing', 'Optional context stays intact'),
    'Prepare Approved Execution': ('owner-selected executor/effort', 'without silent substitutions'),
    'Execute and Integrate': ('Never adopt existing dirty files', 'normal Git hooks/signing',
                              'No extra evidence-only checkpoint', 'no empty commit'),
    'Review and Acceptance': ('fresh independent reviewer context', 'only read/search tools',
                              'Concrete findings stop acceptance'),
    'Runner-configured worker role': ('Do NOT launch this CLI', 'stage/commit or manage workflow state',
                                      'review read-only'),
}


def contract_errors(text):
    return [heading + ': missing ' + clause for heading, clauses in GUARDS.items()
            for clause in clauses if clause not in section(text, heading)]


class IntakeContractTests(unittest.TestCase):
    def test_current_entry_contract(self):
        self.assertEqual(contract_errors(TEXT), [])
        self.assertIn('not effect proof or execution eligibility', TEXT)
        self.assertIn('No arbitrary workflow', TEXT)

    def test_operative_guards_not_footer_only(self):
        for heading, clauses in GUARDS.items():
            for clause in clauses:
                normalized = ' '.join(TEXT.split()).replace(' ## ', '\n## ')
                changed = normalized.replace(clause, 'REMOVED') + '\n## Footer\n' + clause
                self.assertIn(heading + ': missing ' + clause, contract_errors(changed))


if __name__ == '__main__': unittest.main(verbosity=2)
