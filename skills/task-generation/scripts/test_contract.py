#!/usr/bin/env python3
"""Static checks for shared task-generation requirements."""

from pathlib import Path
import unittest
import json
import tempfile
from copy import deepcopy


TEXT = (Path(__file__).parents[1] / "SKILL.md").read_text(encoding="utf-8")


COMPOSED_RULES = (
    'separate green components cannot establish a genuine risky boundary',
    'smallest composed check that observes the final observable, order or custody',
    'Reuse an existing focused check that already observes the boundary',
    'earliest practical producer/consumer boundary',
    'not all seams before coding or a duplicate prototype',
)


def sanitize_record(record):
    return {key: value for key, value in record.items() if key != 'private'}


def composed_write(path, record, *, sanitize_first):
    """Local serialization/write seam fixture; no provider security enforcement claim."""
    if sanitize_first:
        record = sanitize_record(record)
    path.write_text(json.dumps(record))
    return sanitize_record(record)  # a clean return can conceal an unsafe first write


def composition_observations():
    record = {'id': 'chosen-7', 'private': 'fixture-only'}
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / 'record.json'
        assert sanitize_record(record) == {'id': 'chosen-7'}  # isolated sanitizer green
        path.write_text(json.dumps(record))
        assert json.loads(path.read_text()) == record  # storage helper green
        broken_result = composed_write(path, record, sanitize_first=False)
        broken_write = json.loads(path.read_text())
        corrected_result = composed_write(path, record, sanitize_first=True)
        corrected_write = json.loads(path.read_text())
    return broken_result, broken_write, corrected_result, corrected_write


class ComposedAcceptanceTests(unittest.TestCase):
    def test_task_contract_requires_unobserved_boundary_proof(self):
        body = ' '.join(TEXT.split('## Task contract', 1)[1].split('## Review and handoff', 1)[0].split())
        for rule in COMPOSED_RULES:
            with self.subTest(rule=rule):
                self.assertIn(rule, body)
                self.assertNotIn(rule, body.replace(rule, 'REMOVED', 1))
        self.assertIn('original permission/manual gates into the inline REQUIRED brief',
                      ' '.join(TEXT.split('## Review and handoff', 1)[1].split()))

    def test_isolated_green_broken_and_corrected_first_write(self):
        result, broken, corrected_result, corrected = composition_observations()
        self.assertEqual(result, corrected_result)  # isolated green is indistinguishable
        self.assertIn('private', broken)  # first durable write violates the composed criterion
        self.assertNotIn('private', corrected)
        self.assertEqual(corrected['id'], 'chosen-7')
        # Already-observed wiring needs only its existing captured-argument check.
        captured = []
        consumer = lambda selected: captured.append(selected)
        consumer('chosen-7')
        self.assertEqual(captured, ['chosen-7'])
        self.assertNotEqual(captured, ['default-1'])
        print('A2 composition: isolated helpers green; broken first write retains private field; '
              'corrected first write redacted, ID preserved; observed wiring reuses argument check')

    def test_direct_and_speckit_inline_acceptance_records(self):
        source_item = dict(ref='T002/V1', criterion='no private field at first durable write',
                           check='local composed write fixture', expected={'id': 'chosen-7'},
                           proof='accessible-first-write-output', producer='T001',
                           permission='local write', manual='original source gate')
        _, _, _, observed = composition_observations()
        def sufficient(brief, result):
            item = brief['required']
            return (all(item.get(field) for field in source_item) and item == source_item
                    and item['producer'] in brief['depends']
                    and result['status'] == 'pass' and result['observed'] == item['expected']
                    and result['proof'] == item['proof'] and result['producer_passed']
                    and result['permission'] and result['manual'])
        for adapter in ('direct', 'SpecKit'):
            brief = dict(adapter=adapter, depends=['T001'], required=deepcopy(source_item))
            result = dict(status='pass', observed=observed, proof=source_item['proof'],
                          producer_passed=True, permission=True, manual=True)
            self.assertTrue(sufficient(brief, result))
            self.assertFalse(sufficient(dict(brief, depends=[]), result))
            for field in ('ref', 'criterion', 'check', 'expected', 'proof', 'producer', 'permission', 'manual'):
                missing = deepcopy(brief)
                del missing['required'][field]
                self.assertFalse(sufficient(missing, result), (adapter, field))
            weakened = dict(source_item, criterion='sanitizer returns clean helper result')
            self.assertFalse(sufficient(dict(brief, required=weakened), result))
            for changes in (dict(status='not_verified'), dict(producer_passed=False),
                            dict(proof=None), dict(permission=False), dict(manual=False)):
                self.assertFalse(sufficient(brief, dict(result, **changes)))
        print('A2 adapters: direct/SpecKit retain ID/check/pass/access/dependency/original gates; '
              'missing/weakened/unrun proof blocks downstream reliance')


class TaskGenerationContractTests(unittest.TestCase):
    def test_practical_ordinary_contract_and_named_removals(self):
        contract = TEXT.split("## Task contract", 1)[1].split("## Review and handoff", 1)[0]
        review = TEXT.split("## Review and handoff", 1)[1].split("## Mandatory", 1)[0]
        for carrier, clause in ((contract, "Use practical observables"), (contract, "item mappings"),
                                (review, "inadequate approved/legacy contracts"),
                                (review, "producing review/renewal")):
            self.assertIn(clause, carrier)
            self.assertNotIn(clause, carrier.replace(clause, "REMOVED"))
        # Concrete ordinary wiring oracle: optional green cannot conceal changed IDs.
        ordinary = {"ref": "T001/V1", "criterion": "ID reaches consumer unchanged",
                    "expected": "chosen-7", "check": "existing argument fixture",
                    "evidence": "captured consumer ID", "manual": None, "permission": "local"}
        self.assertEqual(ordinary["expected"], "chosen-7")
        self.assertNotEqual(ordinary["expected"], "default-1")
        self.assertIsNone(ordinary["manual"])
        self.assertIn("Both adapters", contract)

    def test_guidance_changes_dependency_check_and_brief_in_both_adapters(self):
        preflight = TEXT.split("## Preconditions and adapters", 1)[1].split("## Task contract", 1)[0]
        for clause in ("including direct entry without planner", "relevant decision",
                       "dependency/check and coordinator brief", "not merely a link"):
            self.assertIn(clause, preflight)
            self.assertNotIn(clause, preflight.replace(clause, "REMOVED", 1))

    def test_direct_and_speckit_adapters(self):
        self.assertIn("SpecKit adapter", TEXT)
        self.assertIn("direct adapter", TEXT)
        self.assertIn("does not\n  require a plan or SpecKit", TEXT)
        self.assertIn("authorization to\n**prepare** tasks", TEXT)
        self.assertIn("Do not require final task/implementation approval", TEXT)

    def test_objective_items_replace_task_profile_allocation(self):
        for obsolete in ("sonnet-class", "opus-class", "30%", "same-class", "class share"):
            with self.subTest(obsolete=obsolete):
                self.assertNotIn(obsolete, TEXT)
        for required in (
            "stable task-local references", "T001/V1", "pass criterion",
            "smallest sufficient check", "expected evidence", "manual/permission gates",
            "REQUIRED", "optional checks separately", "files or interfaces",
            "required capabilities", "shared context", "not an execution assignment",
            "producing review/approval gate", "Do not fabricate historical contracts",
            "../coordinate-implementation/references/batch-routing.md",
        ):
            with self.subTest(required=required):
                self.assertIn(required, TEXT)

    def test_adapter_legacy_and_checkpoint_boundaries_remain(self):
        self.assertIn("Existing task-embedded requirements remain valid for legacy", TEXT)
        self.assertIn("Keep the stage create-only", TEXT)
        self.assertIn("separate source and tasks file", TEXT)
        self.assertIn("task-commit contract", TEXT)
        self.assertIn("checkpointing it separately", TEXT)

    def test_context_coherence_preserves_dependency_order(self):
        self.assertIn("coherent sequential work", TEXT)
        self.assertIn("do not reorder dependencies or pad a segment", TEXT)
        self.assertIn("Internal producer/consumer dependencies, shared files, and phase/story headings may", TEXT)
        self.assertIn("shared\ncontext and integration checkpoints", TEXT)


if __name__ == "__main__":
    unittest.main()
