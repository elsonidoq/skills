#!/usr/bin/env python3
"""Static checks for shared task-generation requirements."""

from pathlib import Path
import unittest
import json
import re
import tempfile
from copy import deepcopy


TEXT = (Path(__file__).parents[1] / "SKILL.md").read_text(encoding="utf-8")


COMPOSED_RULES = (
    'separate green components cannot establish a genuine risky boundary',
    'smallest composed check that observes the final observable, order or custody',
    'Reuse an existing focused check that already observes the boundary',
    'Only an independently necessary prerequisite becomes an earlier task',
    'otherwise verify before reliance inside the same task',
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
        self.assertIn('permission boundaries into the worker brief',
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
        delivery = dict(task_id='T002', outcome='publish the verified safe write',
                        acceptance=[deepcopy(source_item)],
                        support_work=['focused tests', 'evidence', 'operative docs', 'routine teardown'],
                        separate_tasks=[])
        def sufficient(brief, result):
            item = brief['required']
            boundary = brief['delivery']
            return (all(item.get(field) for field in source_item) and item == source_item
                    and item['producer'] in brief['depends']
                    and boundary['task_id'] == 'T002' and boundary['outcome'] == delivery['outcome']
                    and boundary['acceptance'] == [item]
                    and boundary['support_work'] == ['focused tests', 'evidence', 'operative docs', 'routine teardown']
                    and boundary['separate_tasks'] == []
                    and result['status'] == 'pass' and result['observed'] == item['expected']
                    and result['proof'] == item['proof'] and result['producer_passed']
                    and result['permission'] and result['manual'])
        for adapter in ('direct', 'SpecKit'):
            brief = dict(adapter=adapter, depends=['T001'], required=deepcopy(source_item),
                         delivery=deepcopy(delivery))
            result = dict(status='pass', observed=observed, proof=source_item['proof'],
                          producer_passed=True, permission=True, manual=True)
            self.assertTrue(sufficient(brief, result))
            self.assertFalse(sufficient(dict(brief, depends=[]), result))
            split = deepcopy(brief)
            split['delivery']['separate_tasks'].append('T003: write report')
            self.assertFalse(sufficient(split, result))
            missing_acceptance = deepcopy(brief)
            missing_acceptance['delivery']['acceptance'] = []
            self.assertFalse(sufficient(missing_acceptance, result))
            phase_label = deepcopy(brief)
            phase_label['delivery']['outcome'] = 'verification phase'
            self.assertFalse(sufficient(phase_label, result))
            for field in ('ref', 'criterion', 'check', 'expected', 'proof', 'producer', 'permission', 'manual'):
                missing = deepcopy(brief)
                del missing['required'][field]
                self.assertFalse(sufficient(missing, result), (adapter, field))
            weakened = dict(source_item, criterion='sanitizer returns clean helper result')
            self.assertFalse(sufficient(dict(brief, required=weakened), result))
            for changes in (dict(status='not_verified'), dict(producer_passed=False),
                            dict(proof=None), dict(permission=False), dict(manual=False)):
                self.assertFalse(sufficient(brief, dict(result, **changes)))
        print('A2 adapters: direct/SpecKit retain mapped acceptance, coherent delivery, support work, '
              'ID/check/pass/dependency and original gates; split/missing/unrun proof blocks reliance')


class TaskGenerationContractTests(unittest.TestCase):

    def test_guidance_changes_dependency_check_and_brief_in_both_adapters(self):
        preflight = TEXT.split("## Preconditions and adapters", 1)[1].split("## Task contract", 1)[0]
        for clause in ("including direct entry without planner", "relevant decision",
                       "dependency/check and runtime brief", "not merely a link"):
            self.assertIn(clause, preflight)
            self.assertNotIn(clause, preflight.replace(clause, "REMOVED", 1))

    def test_direct_and_speckit_adapters(self):
        self.assertIn("SpecKit adapter", TEXT)
        self.assertIn("direct adapter", TEXT)
        self.assertIn("does not\n  require a plan or SpecKit", TEXT)
        self.assertIn("authorization to\n**prepare** tasks", TEXT)
        self.assertIn("Do not require final task/implementation approval", TEXT)


    def test_adapter_legacy_and_checkpoint_boundaries_remain(self):
        self.assertIn("Existing task-embedded requirements remain valid for legacy", TEXT)
        self.assertIn("Keep the stage create-only", TEXT)
        self.assertIn("separate source and tasks file", TEXT)
        self.assertIn("task-commit contract", TEXT)
        self.assertIn("checkpointing it separately", TEXT)


    def test_delivery_boundaries_and_prototype_policy_are_required(self):
        contract = TEXT.split("## Task contract", 1)[1].split("## Review and handoff", 1)[0]
        review = TEXT.split("## Review and handoff", 1)[1].split("## Mandatory", 1)[0]
        for clause in (
            "A task delivers an independently verifiable outcome, not a phase label",
            "Separate tasks only for a concrete independently necessary deliverable, prerequisite, gate, resource boundary or material context incompatibility",
            "Test writing/running, evidence, verification, review preparation and routine teardown normally stay inside that outcome",
            "Do not split by a workflow noun or task-count quota",
            "Known bounded behavior normally uses permanent actual-helper tests",
            "verified earlier step inside its delivery task", "genuinely unknown consequential",
            "ONE consequential question", "[PROTOTYPE]", "informational conclusion",
            "both script code and actual observed execution evidence", "early risk reduction",
            "Both the direct and SpecKit adapters mark the task title **[PROTOTYPE]**",
        ):
            with self.subTest(clause=clause):
                self.assertIn(" ".join(clause.split()), " ".join(contract.split()))
        for clause in (
            "Challenge redundant task splits, duplicate proofs/report chains and disproportionate checks",


        ):
            with self.subTest(clause=clause):
                self.assertIn(" ".join(clause.split()), " ".join(review.split()))

    def test_executor_sized_recipe_and_planner_review_reference(self):
        """Instruction coverage only; realistic boundary judgments need manual pressure checks."""
        recipe = TEXT.split("### Executor-sized outcomes", 1)[1].split(
            "State shared constraints once", 1)[0]
        for clause in (
            "A delivery milestone groups related capabilities",
            "one bounded outcome", "owned change paths", "scope/exclusions",
            "consumed interfaces and earlier producer dependencies",
            "multiple unfinished concerns", "context loss, compaction and drift",
            "selected executor/effort and observed capabilities",
            "not a model-family hierarchy", "without unfinished downstream work",
            "no universal task count or file/line/token/time ceiling",
            "ordinary tests, relevant docs and routine teardown",
            "Before:", "After:", "Reader acceptance does not wait for the browser",
            "Keep a simple reader fix and its regression test together",
        ):
            with self.subTest(clause=clause):
                self.assertIn(clause, " ".join(recipe.replace("**", "").split()))
        planner = (Path(__file__).parents[2] / "planner" / "SKILL.md").read_text()
        review = planner.split("## Proportionate validation", 1)[1].split(
            "## Before selection", 1)[0]
        self.assertIn("../task-generation/SKILL.md#executor-sized-outcomes", review)
        self.assertIn("milestones disguised as tasks", review)
        self.assertIn("configured executor/effort", review)

    def assert_prototype_adapter_fixture(self, source):
        tasks = re.findall(r"(?m)^- \[ \] (T\d+) (.+)$", source)
        self.assertEqual([task_id for task_id, _ in tasks], ["T001", "T002"])
        self.assertTrue(tasks[0][1].startswith("[PROTOTYPE] "))
        self.assertFalse(any("cleanup" in title.lower() for _, title in tasks))
        prototype, delivery = re.split(r"(?m)^- \[ \] T\d+", source)[1:]
        for phrase in ("ONE consequential question", "actual dependency/abstraction",
                       "informational conclusion and tested limits", "script code and actual observed execution",
                       "commands actually run", "No accompanying proof suite or separate harness",
                       "typically tens of lines"):
            self.assertIn(phrase, prototype)
        self.assertIn("**Depends**: T001", delivery)
        self.assertIn("inspect and use the applicable proof", delivery)
        self.assertIn("permanent production acceptance tests", delivery)

    def test_both_adapters_propagate_bounded_informational_prototype(self):
        root = Path(__file__).parents[3] / "scripts" / "fixtures" / "planner"
        for name in ("risk-tiny-tasks.md", "risk-standard-tasks.md"):
            with self.subTest(adapter=name):
                self.assert_prototype_adapter_fixture((root / name).read_text())

    def test_prototype_adapter_contract_rejects_scope_and_proof_mutations(self):
        root = Path(__file__).parents[3] / "scripts" / "fixtures" / "planner"
        mutations = (
            ("[PROTOTYPE] ", ""),
            ("ONE consequential question", "unbounded questions"),
            ("script code and actual observed execution", "script code only"),
            ("No accompanying proof suite or separate harness", "a separate suite and harness"),
            ("**Depends**: T001\n", "**Depends**: none\n"),
        )
        for name in ("risk-tiny-tasks.md", "risk-standard-tasks.md"):
            source = (root / name).read_text()
            for old, new in mutations:
                with self.subTest(adapter=name, negative=new):
                    self.assertIn(old, source)
                    with self.assertRaises(AssertionError):
                        self.assert_prototype_adapter_fixture(source.replace(old, new, 1))


if __name__ == "__main__":
    unittest.main()
