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
    'separate green components cannot establish a risky boundary',
    'smallest composed check of the final observable, order or custody',
    'Reuse a focused check that already observes it',
    'first boundary with the necessary prerequisites',
    'only for an independently necessary prerequisite',
)


def body(heading):
    section = TEXT.split(heading, 1)[1]
    return ' '.join(section.split('\n## ', 1)[0].split())


def require_clauses(test, heading, clauses):
    carrier = body(heading)
    def check(text):
        for clause in clauses:
            test.assertIn(clause, text)
    check(carrier)
    for clause in clauses:
        with test.subTest(removed=clause):
            with test.assertRaises(AssertionError):
                check(carrier.replace(clause, 'REMOVED'))


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
        require_clauses(self, '## Give each task sufficient proof', COMPOSED_RULES)
        require_clauses(self, '## Return a checked task artifact', (
            'Worker briefs carry work-specific checks, exclusions and material permission boundaries',
        ))

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
        require_clauses(self, '## Draft outcomes from the source', (
            'For both routes, including direct and fresh/resumed entry',
            'Memory Handling',
            'save-adr',
            'current accepted outcomes, explicit mechanism constraints and source links',
            'task dependency or gate, task-local REQUIRED check and worker/reviewer briefs',
            'must affect that mapping',
            'source/task conflict or uncertain supersession stops only the affected mapping',
        ))

    def test_direct_and_speckit_adapters(self):
        require_clauses(self, '## Draft outcomes from the source', (
            '**direct adapter**',
            'needs neither a plan nor SpecKit',
            '**SpecKit adapter**',
            'specification as requirements truth',
            'approved plan for derived sequencing only',
            'authority to **prepare** tasks',
            'final task or implementation approval comes after production',
            "Both routes use the source's criteria, not SDD",
        ))


    def test_authorization_neutral_authoring_and_final_planning_review(self):
        require_clauses(self, '## Give each task sufficient proof', (
            'authorization-neutral work instructions',
            'approval record, not task descriptions or check permissions',
            'Preserve genuine action-specific permission boundaries and manual gates',
            'small isolated tests and local test databases without another owner question',
            'do not exhaust machine resources or affect unrelated data/services',
        ))
        require_clauses(self, '## Return a checked task artifact', ('authorization neutrality need judgment',))
        planner = (Path(__file__).parents[2] / 'planner' / 'SKILL.md').read_text()
        for start, end in (('**Review — fresh independent reviewer with planner-parent binding', '**Combined approval'),
                           ('**`overall_review`', '\n## ')):
            stage = planner.split(start, 1)[1].split(end, 1)[0]
            self.assertIn('../task-generation/SKILL.md#authorization-neutral-tasks', stage)
            self.assertIn('temporary phase/approval status belongs in the approval record', stage)

    def test_adapter_legacy_and_checkpoint_boundaries_remain(self):
        require_clauses(self, '## Draft outcomes from the source', (
            'existing task-embedded legacy requirements remain valid',
            'create-only',
            'separate source and tasks file',
            'Submitted defects return through the producing workflow',
        ))
        require_clauses(self, '## Return a checked task artifact', (
            'task-commit contract',
            'before combined artifact approval',
            'separately from source approval',
        ))


    def test_delivery_boundaries_and_prototype_policy_are_required(self):
        require_clauses(self, '## Make each outcome independently finishable', (
            'one bounded behavior or interface per task',
            'ordinary tests, evidence, relevant documentation, review preparation and routine teardown with the outcome',
            'independently necessary deliverable, prerequisite, gate, resource boundary or material context incompatibility—not a phase name',
        ))
        require_clauses(self, '## Give each task sufficient proof', (
            'early risk reduction',
            'both routes, including direct entry',
            'missing-install report',
            'selection and proof-lifetime rules',
            'ordinary actual-helper tests',
            '**[PROTOTYPE]**',
            'one consequential question',
            'informational conclusion',
            'script code and actual observed execution evidence',
            'handoff and worker brief',
            'reuse/retention limits, production acceptance and disproof/renewal rules',
            'failed or unrun proof cannot release assumed reliance',
            'not execution without authority',
        ))

    def test_producer_reads_actual_executor_json_before_both_adapter_decompositions(self):
        require_clauses(self, '## Make each outcome independently finishable', (
            'Before decomposing work in either route',
            'read the selected executor JSON yourself',
            'exact absolute path supplied',
            'valid worker model and effort',
            'not the planner, parent or producer profile or a remembered default',
            'valid selection needs no new owner question',
            'path is missing, ambiguous or unreadable',
            'worker model/effort is invalid or missing',
            'role, path and problem',
            'do not infer or substitute a binding',
            'owned paths, scope/exclusions, consumed interfaces, earlier producers',
        ))

    def test_executor_sized_recipe_and_planner_review_reference(self):
        """Instruction coverage only; realistic boundary judgments need manual pressure checks."""
        require_clauses(self, '## Make each outcome independently finishable', (
            'one bounded behavior or interface per task',
            'owned paths, scope/exclusions, consumed interfaces, earlier producers',
            'context loss, compaction and drift',
            'selected executor/effort and observed capabilities',
            'not a model-family hierarchy',
            'without unfinished downstream implementation',
            'reader acceptance must not wait for the browser',
            'small reader fix and its regression test stay together',
            'Established cross-system wiring may also stay one task',
        ))
        planner = (Path(__file__).parents[2] / "planner" / "SKILL.md").read_text()
        review = planner.split("## Proportionate validation", 1)[1].split(
            "## Before selection", 1)[0]
        self.assertIn("../task-generation/SKILL.md#executor-sized-outcomes", review)
        self.assertIn("milestones that leave several independently testable interfaces unfinished together",
                      " ".join(review.split()))
        self.assertIn("configured executor/effort", review)

    def test_ui_control_supporting_ownership_example(self):
        """Static authoring contrasts, not runtime closure or type-check validation."""
        require_clauses(self, '## Make each outcome independently finishable', (
            'acceptance selectors, coupled fixtures, admitting harness and final configuration/override owners',
            'inspect its applicable admitting/type check',
            'Include necessary in-scope support changes or name the existing producer dependency',
            'focused test and support work establish the final observable',
        ))
        # Contrast only the instruction's required task description; this is not a task validator.
        def prepared(description):
            return (description["final_observable"] and description["final_check"]
                    and description["final_config_override_owner"]
                    and description["producer_admitting_check"]
                    and (description["owned_support_paths"]
                         or description["producer_dependency"]))

        ordinary_success = dict(final_observable=True, final_check="existing focused check",
                                final_config_override_owner="ui/export_defaults.py",
                                producer_admitting_check="fixture admission check",
                                owned_support_paths=("ui/export_defaults.py",),
                                producer_dependency=None)
        self.assertTrue(prepared(ordinary_success))
        self.assertTrue(prepared(dict(ordinary_success, owned_support_paths=(),
                                      producer_dependency="T001 export-state producer")))
        for omission in (
            {"final_config_override_owner": None},
            {"producer_admitting_check": None},
            {"final_observable": False},
            {"final_check": None},
            {"owned_support_paths": (), "producer_dependency": None},
        ):
            with self.subTest(omission=omission):
                self.assertFalse(prepared(dict(ordinary_success, **omission)))

        require_clauses(self, '## Encode the tasks for their consumer', (
            '`checks`, `check`, or `required[].check` field',
            'six startup linter checks',
            'Existing `required` check mappings remain consumed',
        ))

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
