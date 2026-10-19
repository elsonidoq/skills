"""Lossless v1 intake. External approval evidence is supplied by the trusted operator.

Neither task prose nor an approval reference authenticates its own author. The CLI
must obtain the authority catalog through its owner input channel, never agent tools.
"""
import copy
import hashlib
import json
from pathlib import Path

from .registry import validate_schema
from .store import Blocked, digest, safe_path


def content_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def approval_scope(contract, config_hash):
    value = copy.deepcopy(contract)
    value['approval_refs'] = []
    value['authorization_envelope']['approval_refs'] = []
    for task in value['tasks']:
        for gate in task['gates']:
            gate['approval_ref'] = None
    return digest({'contract': value, 'config_hash': config_hash})


class Approvals:
    """A caller-authenticated catalog, not a catalog discovered from task files."""
    def __init__(self, project, catalog):
        self.project, self.catalog = Path(project), copy.deepcopy(catalog)

    def verify(self, ref, scope):
        if ref['scope_hash'] != scope or ref['action'] != 'approve':
            raise Blocked('denied/cancelled/stale approval')
        trusted = self.catalog.get(ref['authority_ref'])
        if not trusted or trusted != {'actor': ref['actor'], 'record_ref': ref['record_ref'],
                                     'record_sha256': ref['record_sha256'], 'scope_hash': scope,
                                     'gate_kind': ref['gate_kind'], 'action': 'approve'}:
            raise Blocked('unverified external owner authority')
        path = safe_path(self.project, ref['record_ref'])
        if not path.is_file() or content_hash(path) != ref['record_sha256']:
            raise Blocked('approval record content drift')
        return ref['record_ref']


def admit(project, contract, approvals, config_hash, *, legacy_settled=False):
    """Both adapters supply this exact object; legacy has no prose conversion."""
    validate_schema('task.schema.json', contract)
    if contract['origin'] == 'legacy' and (not contract['legacy_origin'] or not legacy_settled):
        raise Blocked('legacy origin/writer reconciliation required')
    if contract['origin'] != 'legacy' and contract['legacy_origin'] is not None:
        raise Blocked('ambiguous planning origin')
    kinds = {source['kind'] for source in contract['sources']}
    needed = {'spec', 'plan', 'tasks', 'review'} if contract['origin'] == 'Standard' else {'source', 'tasks'}
    if not needed <= kinds:
        raise Blocked('missing original source/review artifacts')
    names = set()
    for source in contract['sources']:
        key = (source['path'], source['section'])
        if key in names:
            raise Blocked('ambiguous duplicate source')
        names.add(key)
        path = safe_path(project, source['path'])
        if not path.is_file() or content_hash(path) != source['sha256']:
            raise Blocked('source content drift')
    scope = approval_scope(contract, config_hash)
    required_approvals = {'Standard': {'specification', 'overall', 'implementation'},
                          'TinySpec': {'combined', 'implementation'},
                          'legacy': {'legacy', 'implementation'}}[contract['origin']]
    refs = contract['approval_refs']
    if len({(ref['gate_kind'], ref['record_ref']) for ref in refs}) != len(refs):
        raise Blocked('ambiguous duplicate origin approval')
    if not required_approvals <= {ref['gate_kind'] for ref in refs}:
        raise Blocked('missing current origin/implementation approval')
    for kind in required_approvals:
        if len([ref for ref in refs if ref['gate_kind'] == kind]) != 1:
            raise Blocked('ambiguous origin approval')
    for ref in refs:
        matching_gates = [(task, gate) for task in contract['tasks'] for gate in task['gates']
                          if gate['approval_ref'] == ref['record_ref']]
        if matching_gates:
            if len(matching_gates) != 1:
                raise Blocked('approval cannot ambiguously release multiple gates')
            task, gate = matching_gates[0]
            expected = digest({'gate': {**gate, 'approval_ref': None}, 'task_id': task['id'], 'config': config_hash})
        elif ref['gate_kind'] == 'specification':
            specs = [source['sha256'] for source in contract['sources'] if source['kind'] == 'spec']
            if len(specs) != 1:
                raise Blocked('ambiguous specification scope')
            expected = specs[0]
        elif ref['gate_kind'] in ('overall', 'combined', 'legacy'):
            expected = digest(contract['sources'])
        else:
            expected = scope
        approvals.verify(ref, expected)
    protected = {source['path'] for source in contract['sources']} | {ref['record_ref'] for ref in refs}
    seen, items, orders, groups = set(), set(), [], []
    for task in contract['tasks']:
        if task['id'] in seen or task['order'] in orders or not set(task['depends']) <= seen:
            raise Blocked('duplicate task/order or forward prerequisite; producing review required')
        if len(set(task['depends'])) != len(task['depends']):
            raise Blocked('duplicate prerequisite')
        seen.add(task['id']); orders.append(task['order'])
        if task['context_group'] not in groups:
            groups.append(task['context_group'])
        elif groups[-1] != task['context_group']:
            raise Blocked('noncontiguous context group')
        if task['authorization_envelope_id'] != contract['authorization_envelope']['id']:
            raise Blocked('unknown authorization envelope')
        owned = task['owned_paths']
        if len(set(owned)) != len(owned):
            raise Blocked('duplicate owned path')
        for name in owned:
            if name in protected:
                raise Blocked('owned path overlaps current source/approval; producing renewal required')
            safe_path(project, name)
            if name in ('.git', '.coherence') or name.startswith(('.git/', '.coherence/')):
                raise Blocked('task cannot own authority storage')
        gates = {gate['id']: gate for gate in task['gates']}
        if len(gates) != len(task['gates']):
            raise Blocked('duplicate gate')
        for item in task['required'] + task['optional']:
            if (item['id'] in items or not set(item['gates']) <= gates.keys() or
                    not set(item['producer_dependencies']) <= set(task['depends'])):
                raise Blocked('item/gate/producer identity mismatch')
            items.add(item['id'])
    if orders != sorted(orders):
        raise Blocked('source order cannot be silently reordered')
    return copy.deepcopy(contract), {'scope_hash': scope, 'contract_hash': digest(contract),
                                    'source_hashes': copy.deepcopy(contract['sources']),
                                    'task_ids': [task['id'] for task in contract['tasks']]}


def load_contract(path):
    """Only the linked authoritative JSON subset, never narrative extraction."""
    path = Path(path)
    if path.stat().st_size > 2_000_000:
        raise Blocked('task contract byte limit')
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise Blocked('duplicate contract key')
            result[key] = value
        return result
    return json.loads(path.read_text(), object_pairs_hook=unique)
