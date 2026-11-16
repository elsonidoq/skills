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
    'Reuse an existing focused check',
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
        body = ' '.join(TEXT.split('## Choose evidence before reliance', 1)[1].split('## Write the deliverables', 1)[0].split())
        for rule in COMPOSED_RULES:
            with self.subTest(rule=rule):
                self.assertIn(rule, body)
                self.assertNotIn(rule, body.replace(rule, 'REMOVED', 1))
        self.assertIn('permission boundaries in briefs',
                      ' '.join(TEXT.split('## Check and return', 1)[1].split()))

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

    def assert_clauses(self, heading, clauses):
        body = TEXT if heading is None else TEXT.split(heading, 1)[1].split("\n## ", 1)[0]
        body = " ".join(body.split())
        for clause in clauses:
            with self.subTest(clause=clause):
                self.assertIn(clause, body)


    def test_required_owner_links_resolve(self):
        skill = Path(__file__).parents[1] / 'SKILL.md'
        for target in re.findall(r'\]\(([^)]+)\)', TEXT):
            with self.subTest(target=target):
                self.assertTrue((skill.parent / target.split('#')[0]).is_file())

    def test_binding_and_constraints_precede_decomposition(self):
        inputs = TEXT.index('## Establish the inputs')
        binding = TEXT.index('## Read the execution binding')
        sizing = TEXT.index('## Find work that can finish')
        self.assertLess(inputs, binding)
        self.assertLess(binding, sizing)
        self.assertLess(TEXT.index('task dependency or gate, task-local REQUIRED check'), sizing)
        self.assertLess(TEXT.index('producer itself must read'), sizing)

    def test_guidance_changes_dependency_check_and_brief_in_both_adapters(self):
        self.assert_clauses('## Establish the inputs', (
            'direct, standalone, fresh and resumed',
            '[Memory Handling](../memory-handling/SKILL.md)',
            '[save-adr](../save-adr/SKILL.md)',
            'current accepted decisions and supersession',
            'task dependency or gate, task-local REQUIRED check and worker/reviewer brief',
            'not merely appear as a link',
            'stops only the affected mapping',
        ))

    def test_direct_and_speckit_adapters(self):
        self.assert_clauses('## Establish the inputs', (
            'authorization to **prepare** tasks',
            'approval comes after production',
            '**Direct:**',
            'No plan or SpecKit is required',
            '**SpecKit:**',
            'specification as requirements truth',
            'approved plan only as derived sequencing',
            'unavailable required stage stops production',
            'Do not forward or reread SDD guidance',
        ))


    def test_authorization_neutral_authoring_and_final_planning_review(self):
        self.assert_clauses('## Write the deliverables', (
            'authorization-neutral work instructions',
            'belongs in the approval record',
            'action-specific permission boundaries and manual gates',
            'Small isolated tests and local test databases need no extra owner question',
            'avoid exhausting resources or affecting unrelated data/services',
            'Ordinary scoped fixes',
            'does not authorize global installs',
        ))
        self.assertIn('review source coverage, exclusions, authorization neutrality', TEXT)
        planner = (Path(__file__).parents[2] / 'planner' / 'SKILL.md').read_text()
        self.assertEqual(planner.count('../task-generation/SKILL.md#authorization-neutral-tasks'), 2)

    def test_adapter_legacy_and_checkpoint_boundaries_remain(self):
        self.assert_clauses(None, (
            'legacy task-embedded requirements remain valid',
            'create-only',
            'separate source and tasks file',
            'task-commit contract',
            'checkpoint this deliverable before combined artifact approval',
            'separately from its source',
            'independent review and approval route',
        ))


    def test_delivery_boundaries_and_prototype_policy_are_required(self):
        self.assert_clauses('## Choose evidence before reliance', (
            'early risk reduction',
            'both routes',
            'direct/standalone entry',
            'selection, evidence, applicability/lifetime, consumption, teardown and disproof rules',
            'without separate authority',
            'permanent actual-helper tests',
            'one genuinely unknown consequential question',
            '**[PROTOTYPE]**',
            'marker and bounded informational scope in the handoff and worker brief',
            'script code and actual observed execution evidence',
            'Only an independently necessary prerequisite becomes an earlier task',
            'otherwise verify before reliance inside the same task',
            'Failed or unrun evidence cannot release assumed reliance',
            'renew affected existing approvals',
        ))

    def test_producer_reads_actual_executor_json_before_both_adapter_decompositions(self):
        self.assert_clauses('## Read the execution binding', (
            'Before either route decomposes work',
            'producer itself must read',
            'exact absolute path supplied',
            'valid worker model and effort',
            'planner/parent/producer profile or a remembered default',
            'Valid configuration needs no executor-selection question',
            'path is missing, ambiguous or unreadable',
            'worker model/effort is missing or invalid',
            'role, path and problem',
            'Do not substitute assignments',
            'On standalone entry without a resolved path',
            '--executor PATH',
            'fall back after a failed override',
        ))

    def test_executor_sized_recipe_and_planner_review_reference(self):
        self.assert_clauses('## Find work that can finish', (
            'one bounded behavior or interface',
            'completed predecessors and its own result',
            'without unfinished downstream implementation',
            'owned change paths, scope/exclusions, consumed interfaces',
            'context loss, compaction and drift',
            'selected executor/effort and observed capability',
            'model-family hierarchy',
            'task-count, file, line, token or time ceilings',
            'Reader acceptance must not wait for that browser',
            'ordinary cross-system wiring',
            'focused wiring test, docs and support work',
            'not a workflow noun or quota',
        ))
        planner = (Path(__file__).parents[2] / 'planner' / 'SKILL.md').read_text()
        self.assertIn('../task-generation/SKILL.md#executor-sized-outcomes', planner)
        for anchor in ('executor-sized-outcomes', 'authorization-neutral-tasks',
                       'structured-executable-handoff-both-adapters'):
            self.assertIn(f'<a id="{anchor}"></a>', TEXT)

    def test_ui_control_supporting_ownership_example(self):
        """Static authoring contrasts, not runtime closure or type-check validation."""
        self.assert_clauses('## Find work that can finish', (
            'acceptance selectors, coupled fixtures, admitting harness and final configuration/override owners',
            'inspect its applicable admitting/type check',
            'necessary in-scope tests, fixtures, configuration, harness changes and relevant documentation',
            'name the real predecessor that supplies them',
            'Do not assign a product file alone',
            'work description or existing optional fields, not a new schema',
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

        self.assert_clauses('## Write the deliverables', (
            'existing `checks`, `check`, or `required[].check` field',
            'startup linter has six checks', 'Empty lists mean no work',
            'existing `required` check mappings must be consumed',
            'Without owned paths the runner claims only clean, unchanged paths',
            'optional top-level `delivery_issue`',
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
