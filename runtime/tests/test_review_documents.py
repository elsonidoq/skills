"""T001 permanent bundle and same-byte delivery tests; SDK composition is V4."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from coherence_workflow.review_documents import read_bytes, read_document, settle_delivery, require_coverage
from coherence_workflow.store import Authority, Blocked, canonical, digest, git
from fixtures.support import make_project
from test_review_repair import coordinate_fixture


class DocumentCase(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.project = make_project(Path(self.temp.name) / 'project')
        self.owner = Authority(self.project)
        self.addCleanup(self.owner.__exit__, None, None, None)
        self.owner.__enter__()
        self.coordinate = coordinate_fixture(self.project, self.owner)
        self.repair = self.coordinate.review_repair
        self.db = self.owner.store.db

    def tasks(self):
        for task in self.coordinate.contract['tasks']:
            baseline = {'head': git(self.project, 'rev-parse', 'HEAD').decode().strip()}
            evidence = [{'item_id': task['required'][0]['id'], 'fixture': 'preserved evidence'}]
            self.db.execute("UPDATE wf_tasks SET state='checkpointed',baseline=?,evidence=?,checkpoint=? WHERE task_id=?",
                            (canonical(baseline), canonical(evidence), canonical({'sha': baseline['head']}), task['id']))


class ReferenceBundleTests(DocumentCase):
    def test_complete_inventory_equivalence_whole_binary_patch_and_receipts(self):
        self.tasks()
        original = copy.deepcopy(self.coordinate.contract)
        base = self.repair.range()[0]
        (self.project / 'owned.txt').write_bytes(b'new\x00binary\xff')
        git(self.project, 'add', '--', 'owned.txt'); git(self.project, 'commit', '-qm', 'binary fixture')
        bundle = self.repair.bundle()
        expected = {(s['path'], s['sha256'], s['kind'], s.get('section')) for s in original['sources']}
        expected |= {(r['record_ref'], r['record_sha256'], 'approval', r['gate_kind']) for r in original['approval_refs']}
        actual = {(r['path'], r['sha256'], r['kind'], r.get('section', r.get('role'))) for r in bundle['document_refs']}
        self.assertEqual(expected, actual)
        self.assertEqual(bundle['source_tasks_approvals'], original)
        self.assertNotIn('source_content', bundle)
        self.assertEqual(bundle['full_committed_diff'], git(self.project, 'diff', '--no-ext-diff', '--no-textconv', '--binary', base + '..HEAD').decode())
        self.assertIn('GIT binary patch', bundle['full_committed_diff'])
        for receipt, task in zip(bundle['task_receipts'], original['tasks']):
            self.assertNotIn('contract', receipt)
            self.assertEqual(receipt['contract_ref'], {'task_id': task['id'], 'sha256': digest(task)})
            self.assertEqual(receipt['state'], 'checkpointed')
            self.assertTrue(receipt['evidence']); self.assertEqual(receipt['checkpoint_sha'], base)
        print('V1 full inventory', len(actual), 'serialized bytes', len(canonical(bundle).encode()))

    def test_unequal_and_dynamic_correction_contracts_are_not_removed(self):
        self.tasks()
        changed = copy.deepcopy(self.coordinate.contract['tasks'][0]); changed['outcome'] += ' correction'
        self.db.execute('UPDATE wf_tasks SET contract=? WHERE task_id=?', (canonical(changed), changed['id']))
        dynamic = {**changed, 'id': 'dynamic', 'order': 99}
        self.db.execute("INSERT INTO wf_tasks VALUES(?,?,?,?,'pending',NULL,NULL,NULL)", ('run', 'dynamic', 99, canonical(dynamic)))
        receipts = self.repair.bundle()['task_receipts']
        self.assertEqual(receipts[0]['contract'], changed)
        self.assertEqual(receipts[-1]['contract'], dynamic)
        self.assertEqual(receipts[0]['contract']['required'], self.coordinate.contract['tasks'][0]['required'])

    def test_real_serialized_bound_rejects_without_truncation(self):
        self.tasks()
        task = copy.deepcopy(self.coordinate.contract['tasks'][0]); task['outcome'] = 'é' * 65000
        self.db.execute('UPDATE wf_tasks SET contract=? WHERE task_id=?', (canonical(task), task['id']))
        with self.assertRaisesRegex(Blocked, 'complete review bundle exceeds'):
            self.repair.bundle()
        self.assertEqual(json.loads(self.db.execute('SELECT contract FROM wf_tasks WHERE task_id=?', (task['id'],)).fetchone()[0]), task)

    def test_document_bodies_above_bundle_limit_become_complete_small_refs(self):
        names = [r['path'] for r in self.repair.bundle()['document_refs']]
        raw = b'authorized complete document\n'.ljust(32768, b'x')
        for name in names:
            (self.project / name).write_bytes(raw)
        sha = hashlib.sha256(raw).hexdigest()
        for source in self.coordinate.contract['sources']: source['sha256'] = sha
        for approval in self.coordinate.contract['approval_refs']: approval['record_sha256'] = sha
        bundle = self.repair.bundle()
        self.assertGreater(len(raw) * len(names), 120000)
        self.assertEqual({r['path'] for r in bundle['document_refs']}, set(names))
        self.assertLess(len(canonical(bundle).encode()), 120000)
        self.assertNotIn(raw.decode(), canonical(bundle))
        print('V1 document bytes', len(raw) * len(names), 'reference bundle bytes', len(canonical(bundle).encode()))

    def test_revision_only_when_exact_committed_bytes_available(self):
        bundle = self.repair.bundle()
        self.assertTrue(all('revision' not in ref for ref in bundle['document_refs']))
        names = [ref['path'] for ref in bundle['document_refs']]
        git(self.project, 'add', '--', *names); git(self.project, 'commit', '-qm', 'pin fixture documents')
        head = git(self.project, 'rev-parse', 'HEAD').decode().strip()
        self.assertTrue(all(ref['revision'] == head for ref in self.repair.bundle()['document_refs']))


class ReferenceDeliveryTests(DocumentCase):
    def fixture_delivery(self, *, delivered=True, transform=None):
        """Real settled Gateway reads; official-format branch is a fixture, NOT live SDK proof."""
        bundle = self.repair.bundle(); store = self.owner.store
        host = store.intent('run', 'review-host-fixture', 'fixture', {}, {})['op_id']
        store.transition(host, 'intent', 'completed', {})
        before = {'leaf': None, 'session_id': 'fixture-review-session'}
        details = {'host_op': host, 'role': 'review', 'contract_hash': digest(bundle), 'generation': 1,
                   'attempt_id': 'review:0', 'before': before}
        turn = store.intent('run', 'review-turn-fixture', 'sdk-turn', {}, details)['op_id']
        self.coordinate.agent_node = next(n for n in self.coordinate.config['nodes'] if n.get('role') == 'review')
        tools = self.coordinate._tools({'owned_paths': []}, review=True)
        gateway = self.coordinate.gateway; gateway.tools = tools
        entries = [{'type': 'session', 'version': 3, 'id': before['session_id']}]
        leaf = None
        for index, ref in enumerate(bundle['document_refs']):
            name = ref['path']; call = 'read-' + str(index)
            operation, process = gateway.launch(call, 'read_file', '1', {'path': name})
            receipt = gateway.settle(operation, process.wait(timeout=15))
            try:
                store.event(self.db, 'run', turn, 'sdk_tool_launched:' + digest(call),
                            {'process_operation': operation, 'generation': 1, 'tool': 'read_file', 'version': '1'})
                text = tools['read_file'].result_reader({'path': name}, receipt)
                self.assertEqual(hashlib.sha256(text.encode()).hexdigest(), ref['sha256'])
                if delivered:
                    entry = {'type': 'message', 'id': 'entry-' + str(index), 'parentId': leaf,
                             'message': {'role': 'toolResult', 'toolName': 'read_file', 'toolCallId': call,
                                         'isError': False, 'content': [{'type': 'text', 'text': canonical({'exit_code': 0, 'operation_id': operation, 'output': text})}]}}
                    entries.append(entry); leaf = entry['id']
            finally:
                group = receipt['empty_receipt']['containment']
                gateway.containment.remove(group)
        if transform: transform(entries)
        folder = self.project / '.coherence/workflow/sdk/sessions'; folder.mkdir(parents=True, exist_ok=True)
        path = folder / 'fixture.jsonl'; path.write_text(''.join(canonical(e) + '\n' for e in entries)); path.chmod(0o600)
        after = {'leaf': leaf, 'session_id': before['session_id'], 'session_file': str(path),
                 'session_file_hash': hashlib.sha256(path.read_bytes()).hexdigest()}
        segment = {**details, 'after': after}
        store.transition(turn, 'intent', 'completed', segment)
        proof = settle_delivery(self.coordinate, {'segment': segment})
        result = {'range_base': bundle['range_base'], 'range_head': bundle['range_head'],
                  'contract_hash': digest(bundle), 'attempt_id': 'review:0'}
        return result, host, turn, proof

    def test_real_gateway_same_bytes_and_complete_settled_delivery(self):
        result, host, turn, proof = self.fixture_delivery()
        self.assertTrue(require_coverage(self.coordinate, result, host))
        self.assertEqual(len(proof['reads']), len(self.repair.bundle()['document_refs']))
        self.assertEqual(self.db.execute('SELECT COUNT(*) FROM wf_reviews').fetchone()[0], 0)
        print('V2 real settled read processes', len(proof['reads']), 'fixture SDK branch; actual SDK is V4')

    def test_unread_undelivered_missing_coverage_and_wrong_host_turn_range_hash_reject(self):
        result, host, turn, proof = self.fixture_delivery()
        for field, value in [('host_op', 'wrong-host'), ('bundle_hash', 'wrong-bundle'), ('generation', 2), ('snapshot_hash', 'wrong-snapshot')]:
            with self.subTest(field=field):
                altered = copy.deepcopy(proof); altered[field] = value
                self.db.execute("UPDATE wf_events SET payload=? WHERE op_id=? AND kind='review_document_delivery'", (canonical(altered), turn))
                with self.assertRaises(Blocked): require_coverage(self.coordinate, result, host)
        for field in ['sha256', 'range_head', 'process_operation']:
            with self.subTest(read_field=field):
                altered = copy.deepcopy(proof); altered['reads'][0][field] = 'wrong'
                self.db.execute("UPDATE wf_events SET payload=? WHERE op_id=? AND kind='review_document_delivery'", (canonical(altered), turn))
                with self.assertRaises(Blocked): require_coverage(self.coordinate, result, host)
        altered = {**proof, 'reads': proof['reads'][1:]}
        self.db.execute("UPDATE wf_events SET payload=? WHERE op_id=? AND kind='review_document_delivery'", (canonical(altered), turn))
        with self.assertRaises(Blocked): require_coverage(self.coordinate, result, host)
        self.db.execute("UPDATE wf_events SET payload=? WHERE op_id=? AND kind='review_document_delivery'", (canonical(proof), turn))
        with self.assertRaises(Blocked): require_coverage(self.coordinate, result, 'other-host')
        self.assertTrue(require_coverage(self.coordinate, result, host))
        self.assertEqual(self.db.execute('SELECT COUNT(*) FROM wf_reviews').fetchone()[0], 0)
        self.assertEqual(self.db.execute('SELECT COUNT(*) FROM wf_findings').fetchone()[0], 0)

    def test_callback_without_sdk_return_is_not_delivery(self):
        result, host, turn, proof = self.fixture_delivery(delivered=False)
        self.assertEqual(proof['reads'], [])
        self.assertGreater(self.db.execute("SELECT COUNT(*) FROM wf_events WHERE kind='review_document_read'").fetchone()[0], 0)
        with self.assertRaisesRegex(Blocked, 'coverage'): require_coverage(self.coordinate, result, host)

    def test_successful_tool_result_with_wrong_returned_bytes_rejects(self):
        def corrupt(entries):
            entry = entries[-1]['message']['content'][0]
            output = json.loads(entry['text']); output['output'] = 'wrong returned bytes'
            entry['text'] = canonical(output)
        with self.assertRaisesRegex(Blocked, 'bytes mismatch'): self.fixture_delivery(transform=corrupt)
        self.assertEqual(self.db.execute('SELECT COUNT(*) FROM wf_reviews').fetchone()[0], 0)

    def test_sdk_error_result_cannot_cover_required_reference(self):
        def fail(entries): entries[-1]['message']['isError'] = True
        result, host, turn, proof = self.fixture_delivery(transform=fail)
        with self.assertRaisesRegex(Blocked, 'coverage'): require_coverage(self.coordinate, result, host)

    def test_changed_current_authority_invalidates_previously_delivered_coverage(self):
        result, host, turn, proof = self.fixture_delivery()
        self.assertTrue(require_coverage(self.coordinate, result, host))
        (self.project / proof['reads'][0]['path']).write_text('changed after delivery')
        with self.assertRaises(Blocked): require_coverage(self.coordinate, result, host)
        self.assertEqual(self.db.execute('SELECT COUNT(*) FROM wf_reviews').fetchone()[0], 0)

    def test_changed_deleted_unsafe_unauthorized_wrong_hash_and_utf8(self):
        bundle = self.repair.bundle(); ref = bundle['document_refs'][0]; path = self.project / ref['path']
        raw = path.read_bytes()
        self.assertEqual(read_bytes(self.project, ref['path'], ref['sha256'])[0].encode(), raw)
        for content in [b'changed', b'\xff']:
            path.write_bytes(content)
            with self.assertRaises(Blocked): read_bytes(self.project, ref['path'], ref['sha256'])
        path.unlink()
        with self.assertRaises(Blocked): read_bytes(self.project, ref['path'], ref['sha256'])
        outside = Path(self.temp.name) / 'outside'; outside.write_bytes(raw); path.symlink_to(outside)
        with self.assertRaises(Blocked): read_bytes(self.project, ref['path'], ref['sha256'])
        path.unlink(); path.write_bytes(raw)
        for name in ['../outside', str(outside), 'unrelated.txt']:
            with self.subTest(path=name), self.assertRaises(Blocked): read_document(self.coordinate, bundle, {'path': name}, {})
        with self.assertRaises(Blocked): read_bytes(self.project, ref['path'], '0' * 64)
        (self.project / 'utf8.txt').write_bytes(b'\xff')
        with self.assertRaises(Blocked): read_bytes(self.project, 'utf8.txt')
        (self.project / 'boundary.txt').write_bytes(b'x' * 32768)
        self.assertEqual(len(read_bytes(self.project, 'boundary.txt')[0]), 32768)
        (self.project / 'boundary.txt').write_bytes(b'x' * 32769)
        with self.assertRaises(Blocked): read_bytes(self.project, 'boundary.txt')
