#!/usr/bin/env python3
"""Offline carrier and controlled-evidence checks, not live/model-obedience proof.

The skill is the production interface. The small oracle below documents expected
conclusions on controlled evidence; it is not an assessment engine or gh client.
"""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'skills/assess-skill-improvements/SKILL.md'

# Check operational sections, not an unrelated glossary or decorative appendix.
OBLIGATIONS = {
    'Discover and select': (
        'https://HOST/OWNER/REPO/issues/NUMBER',
        'https://HOST/OWNER/REPO/pull/NUMBER',
        'actual issue/PR identity with GET',
        'Explicit URL selection needs the selected evidence',
        'Exclude records containing `pull_request` only from this repository issue-list selection.',
        'issues?state=all&per_page=100', 'labels?per_page=100',
    ),
    'Follow durable evidence from either entry': (
        '--paginate` for every list',
        'issues/$NUMBER/comments?per_page=100',
        'pulls/$NUMBER/reviews?per_page=100',
        'pulls/$NUMBER/comments?per_page=100',
        'issues/$NUMBER/timeline?per_page=100',
        'pulls/$NUMBER/commits?per_page=100',
        'pulls/$NUMBER/files?per_page=100',
        'From an issue, follow its delivery PR',
        'From a PR, follow its qualified delivery issue',
        'Check the return link too',
        'Follow every relevant linked trace/comment page',
        'Read full bodies', 'snapshot/part identities and total parts',
        'missing, duplicate-conflicting or inaccessible part',
        'partial-coverage trace',
        'commits/$SHA', 'code at the cited revision',
        'If a files/diff response is truncated',
        'neither the original checkout identity/path, local SQLite database nor session',
        'missing evidence, not an empty result',
        'Continue independent accessible reads',
        'recovery is needed only if the selected evidence requires it',
    ),
    'Reason and present': (
        'source URLs and precise comment, part, commit or code references for each factual claim',
        'Original intent', 'completion claims versus checks/review',
        'Reusable planning/task/handoff/implementation/review weaknesses',
        'user- or issue-specific omissions',
        'Verified observations and supported causes versus hypotheses',
        'Inspect supported post-completion fixes',
        'explicit issue/trace/review links and relevant code/diff content',
        'Reject unrelated commits; author, time, or a blind Git range cannot establish attribution',
        'existing planning, skill, tool or worker-instruction owners',
        'small proposed change', 'no-change and uncertain conclusions',
        'affected conclusions as partial',
        'must not edit skills, launch agents or implementation, open a PR, transition tracker state',
    ),
    'Record only authorized results': (
        'optional, separately scoped assessment-write lifecycle',
        'skill-assessment:proposed', 'skill-assessment:no-change',
        'skill-assessment:addressed',
        'exact implementation and verification evidence',
        'explicit target- and operation-scoped tracker write authority',
        'Selection/read authority does not grant this write scope',
        'Preserve unrelated labels and content',
        'Read back each label/comment effect independently',
        'inspect actual labels/comments before any retry',
        'Without authority, present analysis without writes',
    ),
}


def normalized(text):
    return ' '.join(text.split())


def violations(text):
    sections = dict(re.findall(r'^## ([^\n]+)\n(.*?)(?=^## |\Z)', text, re.M | re.S))
    return [(section, phrase) for section, phrases in OBLIGATIONS.items()
            for phrase in phrases
            if normalized(phrase) not in normalized(sections.get(section, ''))]


def controlled_assessment(entry, resources, fixes):
    """Expected navigation/classification oracle only; no network, DB, session or Git."""
    pending, seen, gaps, facts = [entry], set(), [], []
    while pending:
        url = pending.pop(0)
        if url in seen:
            continue
        seen.add(url)
        resource = resources.get(url)
        if resource is None:
            gaps.append(url)
            continue
        facts.extend(resource.get('facts', []))
        pending.extend(resource.get('links', []))
    classified = []
    for fix in fixes:
        # Date/author/range position are deliberately not classification inputs.
        related = fix.get('source') in seen and fix.get('diff_support')
        if related:
            kind = 'reusable' if fix.get('approved_requirement') else 'issue-specific'
        else:
            kind = 'hypothesis' if fix.get('plausible') else 'unrelated'
        classified.append((fix['url'], kind))
    return {'read': seen, 'facts': facts, 'gaps': gaps,
            'partial': bool(gaps), 'fixes': classified, 'writes': []}


class CarrierTests(unittest.TestCase):
    def test_actual_skill_obligations(self):
        self.assertEqual(violations(SKILL.read_text()), [])

    def test_each_obligation_is_sensitive_in_its_operational_section(self):
        text = SKILL.read_text()
        for section, phrases in OBLIGATIONS.items():
            for phrase in phrases:
                with self.subTest(section=section, phrase=phrase):
                    # Mutate the actual carrier, even when its phrase spans lines.
                    pattern = r'\s+'.join(re.escape(word) for word in phrase.split())
                    section_pattern = r'(^## ' + re.escape(section) + r'\n)(.*?)(?=^## |\Z)'
                    match = re.search(section_pattern, text, re.M | re.S)
                    body, count = re.subn(pattern, '[removed obligation]', match[2])
                    self.assertGreaterEqual(count, 1)
                    changed = text[:match.start(2)] + body + text[match.end(2):]
                    # An appendix cannot compensate for a missing operational rule.
                    changed += '\n## Decorative appendix\n' + phrase
                    self.assertIn((section, phrase), violations(changed))

    def test_docs_route_to_contract_and_handoff(self):
        for path in ('README.md', 'docs/coordinate-implementation.md'):
            text = (ROOT / path).read_text()
            self.assertIn('assess-skill-improvements/SKILL.md', text)
            self.assertIn('issue or PR', text)
            self.assertIn('fresh-session', text)
            self.assertIn('test-assess-skill-improvements.py', text)


class ControlledEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.issue = 'https://github.example/team/repo/issues/7'
        self.pr = 'https://github.example/team/repo/pull/9'
        self.part1, self.part2 = self.pr + '#issuecomment-1', self.pr + '#issuecomment-2'
        self.code = 'https://github.example/team/repo/blob/exact-sha/worker.py'
        self.resources = {
            self.issue: {'links': [self.pr], 'facts': ['original intent', 'owner answer']},
            self.pr: {'links': [self.issue, self.part1], 'facts': ['review rejected claim']},
            self.part1: {'links': [self.part2], 'facts': ['part 1: failed check']},
            self.part2: {'links': [self.code], 'facts': ['part 2: corrected check passed']},
            self.code: {'facts': ['revision content']},
        }
        self.fixes = [
            {'url': 'fix-a', 'source': self.pr, 'diff_support': True,
             'approved_requirement': True},
            {'url': 'fix-b', 'source': self.issue, 'diff_support': True,
             'approved_requirement': False},
            {'url': 'same-author-next-day', 'author': 'same', 'time': 'later',
             'range_position': 1},
            {'url': 'possible-fix', 'source': self.pr, 'plausible': True},
        ]

    def test_issue_and_pr_reach_same_full_evidence(self):
        issue = controlled_assessment(self.issue, self.resources, self.fixes)
        pr = controlled_assessment(self.pr, self.resources, self.fixes)
        self.assertEqual(issue['read'], pr['read'])
        self.assertEqual(set(issue['facts']), set(pr['facts']))
        self.assertIn('part 2: corrected check passed', issue['facts'])
        self.assertFalse(issue['partial'])
        self.assertEqual(issue['writes'], [])
        self.assertEqual(pr['writes'], [])

    def test_inaccessible_part_association_or_code_is_partial_not_zero_failures(self):
        for entry in (self.issue, self.pr):
            for missing in (self.part2, self.code, self.pr if entry == self.issue else self.issue):
                with self.subTest(entry=entry, missing=missing):
                    resources = {url: data for url, data in self.resources.items() if url != missing}
                    result = controlled_assessment(entry, resources, self.fixes)
                    self.assertTrue(result['partial'])
                    self.assertIn(missing, result['gaps'])
                    self.assertTrue(result['facts'])  # Preserve accessible independent facts.
                    self.assertEqual(result['writes'], [])

    def test_supported_later_fix_unrelated_commit_and_omission_classification(self):
        result = controlled_assessment(self.pr, self.resources, self.fixes)
        self.assertEqual(result['fixes'], [
            ('fix-a', 'reusable'), ('fix-b', 'issue-specific'),
            ('same-author-next-day', 'unrelated'), ('possible-fix', 'hypothesis')])
        # Removing actual diff support must lose supported-cause classification.
        self.fixes[0]['diff_support'] = False
        changed = controlled_assessment(self.issue, self.resources, self.fixes)
        self.assertNotEqual(changed['fixes'][0][1], 'reusable')


if __name__ == '__main__':
    unittest.main()
