"""T003/V2: no model financial gate, scoped external actions fail closed."""
import tempfile
import unittest
from pathlib import Path

from coherence_workflow.authority import AuthorityAdmission
from coherence_workflow.store import Authority, Blocked
from fixtures.support import make_project


class AuthorityAdmissionTests(unittest.TestCase):
    def test_all_known_gaps_are_aggregated(self):
        envelope = {'profiles': [{'provider': 'p', 'model': 'm', 'effort': 'medium'}],
                    'capabilities': [{'id': 'check', 'action_scope': 'test', 'effects': ['test']},
                                     {'id': 'write', 'action_scope': 'file', 'effects': ['mutation']}]}
        gaps = AuthorityAdmission(envelope, {}, [], [], lambda ref, scope: None).gaps()
        self.assertEqual({g['kind'] for g in gaps}, {'profile', 'capability', 'permission'})
        self.assertTrue(all(g['impact'] and g['options'] for g in gaps))

    def test_ordinary_model_has_no_financial_admission(self):
        profile = {'provider': 'p', 'model': 'm', 'effort': 'medium'}
        for authority in ('denied', 'unresolved', 'owner_scoped'):
            envelope = {'profiles': [profile], 'capabilities': [], 'external_paid_authority': authority,
                        'approval_refs': [], 'limits': []}
            admission = AuthorityAdmission(envelope, {'model': profile}, [], [], lambda ref, scope: None)
            self.assertEqual(admission.gaps(), [])
            self.assertEqual(admission.model(profile), profile)
            with self.assertRaises(Blocked): admission.model(dict(profile, effort='high'))

    def test_external_gateway_denials_have_zero_sends(self):
        calls = []
        for authority in (None, 'denied', 'unresolved', 'owner_scoped'):
            envelope = {'profiles': [], 'capabilities': [
                {'id': 'api', 'action_scope': 'one-service-read', 'effects': ['paid_service'],
                 'purpose': 'check result', 'cost_impact': 'one separately charged request'}],
                'external_paid_authority': authority, 'approval_refs': [], 'limits': []}
            admission = AuthorityAdmission(envelope, {}, ['api'], ['api'], lambda ref, scope: None)
            with self.assertRaises(Blocked):
                admission.external('api', lambda: calls.append('sent'))
        self.assertEqual(calls, [])

    def test_scoped_action_authority_survives_restart_without_replay(self):
        with tempfile.TemporaryDirectory() as temp:
            project = make_project(Path(temp) / 'project')
            envelope = {'profiles': [], 'capabilities': [
                {'id': 'api', 'action_scope': 'one-read', 'effects': ['paid_service'],
                 'purpose': 'read sample', 'cost_impact': 'one separately charged read'}],
                'external_paid_authority': 'owner_scoped', 'approval_refs': [{'proof': 'external'}],
                'limits': [{'action_id': 'api', 'description': 'one read'}]}
            calls = []
            verify = lambda ref, scope: self.assertEqual(ref, {'proof': 'external'})
            with Authority(project) as owner:
                owner.store.reserve('run', 'config')
                admission = AuthorityAdmission(envelope, {}, ['api'], ['api'], verify, store=owner.store, run='run')
                self.assertEqual(admission.external('api', lambda: calls.append('sent') or {'receipt': 'one'}), {'receipt': 'one'})
            with Authority(project) as owner:
                admission = AuthorityAdmission(envelope, {}, ['api'], ['api'], verify, store=owner.store, run='run')
                with self.assertRaises(Blocked): admission.external('api', lambda: calls.append('duplicate'))
            self.assertEqual(calls, ['sent'])
