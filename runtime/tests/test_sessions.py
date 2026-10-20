"""T002/V2: shared deterministic all-role policy; live telemetry in BindingTests."""
import copy
import unittest
from coherence_workflow.sessions import select_session
from coherence_workflow.store import Blocked


def request(**kw):
    value = dict(role='implement', affinity='story', profile='exact', skills='sha', tools='sha',
                 permissions='sha', trust='sha', settings='sha', worktree='root',
                 authorized=True, ready=True, reconciled=True, fresh_only=False,
                 review_lineage=None, original=None, pin=None)
    value.update(kw)
    return value


def candidate(id='a', **kw):
    value = request()
    value.update(id=id, settled=True, poisoned=False, settle_seq=1, telemetry={
        'observed_ns':1000, 'reliable':True, 'enabled':True, 'threshold':483616,
        'occupancy':333616, 'provenance':'pi-0.87.1/SettingsManager/getContextUsage'})
    value.update(kw)
    return value


class SessionPolicyTests(unittest.TestCase):
    def choose(self, r=None, candidates=None):
        return select_session(r or request(), candidates if candidates is not None else [candidate()],
                              now_ns=1000, max_age_ns=100, min_free_tokens_before_compaction=150000)

    def test_unknown_metrics_do_not_veto_settled_original(self):
        c=candidate(telemetry={})
        self.assertEqual(self.choose(candidates=[c])['session_id'], 'a')

    def test_boundary_and_unknowns(self):
        self.assertEqual(self.choose()['session_id'], 'a')
        for field, value in [('occupancy',333617), ('occupancy',None), ('threshold',None),
                             ('enabled',False), ('reliable',False), ('observed_ns',899),
                             ('observed_ns',1001), ('provenance',None)]:
            c = candidate(); c['telemetry'][field] = value
            with self.subTest(field=field,value=value):
                self.assertEqual(self.choose(candidates=[c])['session_id'], 'a')

    def test_exact_compatibility_every_role(self):
        for role in ['implement','repair','review','analysis']:
            r = request(role=role, review_lineage='range' if role=='review' else None)
            c = candidate(role=role, review_lineage=r['review_lineage'])
            self.assertEqual(self.choose(r,[c])['session_id'],'a')
            for field in ['affinity','profile','skills','tools','permissions','trust','settings','worktree','role','review_lineage']:
                changed=copy.deepcopy(c); changed[field]='different'
                self.assertIsNone(self.choose(r,[changed])['session_id'])
        for changes in [dict(settled=False),dict(poisoned=True)]:
            with self.assertRaises(Blocked): self.choose(candidates=[candidate(**changes)])

    def test_repair_original_then_latest_stable_id(self):
        cs=[candidate('z',settle_seq=10),candidate('b',settle_seq=10),candidate('a',settle_seq=2)]
        self.assertEqual(self.choose(candidates=cs)['session_id'],'b')
        self.assertEqual(self.choose(request(role='repair',original='a'),cs)['session_id'],'a')
        cs[-1]['telemetry']['occupancy']=333617
        self.assertEqual(self.choose(request(role='repair',original='a'),cs)['session_id'],'b')

    def test_fresh_review_lineage_and_no_cross_role(self):
        self.assertEqual(self.choose(request(role='review'),[candidate()])['reason'],'independent_first_review')
        self.assertIsNone(self.choose(request(role='review',review_lineage='r'),[candidate()])['session_id'])
        self.assertIsNone(self.choose(request(role='repair'),[candidate(role='review')])['session_id'])
        self.assertIsNone(self.choose(request(fresh_only=True))['session_id'])
        self.assertIsNone(self.choose(request(profile='new'))['session_id'])

    def test_pin_never_substitutes_fresh(self):
        self.assertEqual(self.choose(request(pin='a'))['session_id'],'a')
        for cs in [[],[candidate('b')],[candidate(telemetry={})],[candidate(profile='new')]]:
            with self.assertRaises(Blocked): self.choose(request(pin='a'),cs)
        with self.assertRaises(Blocked): self.choose(request(pin='a',fresh_only=True))

    def test_authority_safety_and_duplicates(self):
        for field in ['authorized','ready','reconciled']:
            with self.assertRaises(Blocked): self.choose(request(**{field:False}))
        with self.assertRaises(Blocked): self.choose(candidates=[candidate(),candidate()])
