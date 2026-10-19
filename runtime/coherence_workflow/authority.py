"""Upfront capability admission and separately chargeable action authority.

Ordinary permitted model traffic deliberately has no financial admission path.
"""
import copy

from .store import Blocked, digest, canonical


BUILTIN_EFFECTS={'read_file':['external'],'write_file':['mutation'],
                 'request_owner_input':['external'],'runner-git-commit':['mutation']}


def action_requirement(contract, name):
    """Builtin v1 scope: concrete approved stream, never prose or a self-referential hash."""
    tasks=contract['tasks']
    scope={'version':1,'action':name,'tasks':[{'id':t['id'],'owned_paths':t['owned_paths']} for t in tasks]}
    if name=='read_file':
        scope['readable_paths']=sorted({s['path'] for s in contract.get('sources',[])} |
            {r['record_ref'] for r in contract.get('approval_refs',[])} |
            {p for t in tasks for p in t['owned_paths']})
    if name not in BUILTIN_EFFECTS:
        checks=[{'task_id':t['id'],'version':i['check']['version'],'args_hash':digest(i['check']['args'])}
                for t in tasks for i in t['required'] if i['check']['id']==name]
        if not checks:raise Blocked('unknown action scope; producing renewal required')
        scope['checks']=checks
        if name=='workflow.PythonAnswer':scope['execution']='trusted-project-python'
    return {'action_scope':canonical(scope),'effects':BUILTIN_EFFECTS.get(name,['test'])}


def required_actions(contract, config):
    actions=set()
    for node in config['nodes']:
        if node['type']!='agent':continue
        actions.add('read_file')
        if node['role']!='review' and any(t['owned_paths'] for t in contract['tasks']):actions.add('write_file')
        if 'request_owner_input' in node['tools']:actions.add('request_owner_input')
    actions.update(i['check']['id'] for t in contract['tasks'] for i in t['required'])
    if any(t['owned_paths'] for t in contract['tasks']):actions.add('runner-git-commit')
    return {name:action_requirement(contract,name) for name in sorted(actions)}


class AuthorityAdmission:
    def __init__(self, envelope, profiles, capabilities, permissions, verify, *, store=None, run=None):
        self.envelope = copy.deepcopy(envelope)
        self.profiles = copy.deepcopy(profiles)
        self.capabilities, self.permissions = set(capabilities), set(permissions)
        self.verify, self.store, self.run = verify, store, run

    def gaps(self, required=None):
        gaps = []
        def add(kind, name, impact):
            gaps.append({'kind': kind, 'id': name, 'impact': impact,
                         'options': ['provide scoped authority/capability', 'stop affected work']})
        for profile in self.envelope['profiles']:
            if profile not in self.profiles.values():
                add('profile', digest(profile), 'exact profile unavailable; no substitution')
        for capability in self.envelope['capabilities']:
            name = capability['id']
            if name not in self.capabilities:
                add('capability', name, 'registered action unavailable')
            if name not in self.permissions:
                add('permission', name, 'action not authorized')
            if 'paid_service' in capability['effects']:
                try:
                    self._external_authority(name)
                except Blocked as exc:
                    add('external_paid_authority', name, str(exc))
        names=[c['id'] for c in self.envelope['capabilities']]
        for name in sorted(set(names)):
            if names.count(name)!=1:add('owner_action',name,'duplicate/ambiguous action declaration; producing renewal required')
        for name,requirement in (required or {}).items():
            try:self.require(name,requirement)
            except Blocked as exc:add('owner_action',name,str(exc))
        return gaps

    def require(self, name, requirement):
        matches=[c for c in self.envelope['capabilities'] if c['id']==name]
        if len(matches)!=1:
            raise Blocked('missing/ambiguous owner action '+name+'; producing renewal required')
        if name not in self.capabilities or name not in self.permissions:
            raise Blocked('unavailable/unpermitted action '+name+'; producing renewal required')
        value=matches[0]
        if (value['action_scope']!=requirement['action_scope'] or
                sorted(value['effects'])!=sorted(requirement['effects']) or
                len(value['effects'])!=len(set(value['effects']))):
            raise Blocked('incompatible action scope/effects '+name+'; producing renewal required')
        return True

    def model(self, profile):
        if profile not in self.envelope['profiles'] or profile not in self.profiles.values():
            raise Blocked('exact approved model profile unavailable')
        return copy.deepcopy(profile)

    def _external_authority(self, name):
        matches = [c for c in self.envelope['capabilities'] if c['id'] == name]
        if len(matches) != 1:
            raise Blocked('unknown/ambiguous external action')
        capability = matches[0]
        if (name not in self.capabilities or name not in self.permissions or
                'paid_service' not in capability['effects'] or
                self.envelope.get('external_paid_authority') != 'owner_scoped' or
                not capability.get('purpose') or not capability.get('cost_impact')):
            raise Blocked('separately chargeable action lacks purpose/cost-impact/scoped authority')
        scope = digest({'capability': capability, 'limits': [limit for limit in self.envelope.get('limits', [])
                                                          if limit['action_id'] == name]})
        refs = self.envelope.get('approval_refs', [])
        if not refs:
            raise Blocked('missing separately chargeable action approval')
        for ref in refs:
            self.verify(ref, scope)
        return scope

    def external(self, name, send):
        """Persist intent before sending. Restart cannot blindly repeat an external effect."""
        scope = self._external_authority(name)
        if self.store is None or self.run is None:
            raise Blocked('external action requires durable operation custody')
        node = 'external:' + name
        if self.store.db.execute('SELECT 1 FROM wf_operations WHERE run_id=? AND node_id=? AND kind=?',
                                 (self.run, node, 'external-action')).fetchone():
            raise Blocked('external effect already attempted; explicit reconciliation required')
        operation = self.store.intent(self.run, node, 'external-action', {'scope': scope},
                                      {'scope': scope, 'authority_hash': digest(self.envelope['approval_refs'])})
        result = send()
        self.store.transition(operation['op_id'], 'intent', 'completed', result)
        return result
