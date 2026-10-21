"""T009/V1 synthetic facts for the pure saved-session selector."""
import copy
import unittest

from coherence_workflow.sessions import effective_headroom, select_session


def request(**changes):
    value = {
        'run_id': 'run-1', 'role': 'worker', 'context_group': 'session-policy',
        'worktree': '/disposable/project', 'executor': {'provider': 'dummy', 'model': 'dummy'},
        'resources': {'tools': 'write'}, 'instructions': 'worker-v1', 'settings': 'settings-v1',
        'authority': 'authority-v1', 'fresh_only': False,
    }
    value.update(changes)
    return value


def candidate(session_id='session-a', **changes):
    value = {
        **request(), 'id': session_id, 'settled': True, 'idle': True,
        'checkpoint_verified': True, 'settled_at': 10,
        'headroom': {
            'context_window': 300000, 'effective_reserve': 50000, 'occupancy': 100000,
            'compaction_enabled': True, 'compaction_applicable': True,
        },
    }
    value.update(changes)
    return value


class SessionPolicyTests(unittest.TestCase):
    def select(self, changes=None, candidates=None):
        return select_session(request(**(changes or {})), candidates if candidates is not None else [candidate()])

    def test_effective_headroom_cutoff_is_inclusive(self):
        self.assertEqual(effective_headroom(candidate()['headroom']), 150000)
        self.assertEqual(self.select()['session_id'], 'session-a')
        low = candidate(headroom={**candidate()['headroom'], 'occupancy': 100001})
        result = self.select(candidates=[low])
        self.assertIsNone(result['session_id'])
        self.assertEqual(result['rejected'], {'session-a': 'unknown_or_low_headroom'})

    def test_unknown_invalid_disabled_or_inapplicable_measurements_choose_fresh(self):
        for observation in (
            None, {}, {'compaction_enabled': False, 'compaction_applicable': True},
            {'compaction_enabled': True, 'compaction_applicable': False},
            {**candidate()['headroom'], 'occupancy': None},
        ):
            with self.subTest(observation=observation):
                result = self.select(candidates=[candidate(headroom=observation)])
                self.assertIsNone(result['session_id'])
                self.assertEqual(result['rejected']['session-a'], 'unknown_or_low_headroom')

    def test_missing_or_different_affinity_selects_fresh(self):
        self.assertEqual(self.select({'context_group': ''})['reason'], 'missing_context_group')
        for group in (None, '', 'other'):
            with self.subTest(group=group):
                result = self.select(candidates=[candidate(context_group=group)])
                self.assertIsNone(result['session_id'])
                self.assertIn(result['rejected']['session-a'], ('missing_context_group', 'context_group_mismatch'))

    def test_each_stable_compatibility_change_rejects_candidate(self):
        for field in ('role', 'worktree', 'executor', 'resources', 'instructions', 'settings', 'authority'):
            with self.subTest(field=field):
                changed = copy.deepcopy(candidate())
                changed[field] = 'different'
                result = self.select(candidates=[changed])
                self.assertIsNone(result['session_id'])
                self.assertEqual(result['rejected'], {'session-a': field + '_mismatch'})

    def test_failed_unsettled_other_run_or_uncheckpointed_candidates_are_ineligible(self):
        cases = (
            (candidate(settled=False), 'unsettled_or_failed'),
            (candidate(idle=False), 'unsettled_or_failed'),
            (candidate(run_id='run-2'), 'different_run'),
            (candidate(checkpoint_verified=False), 'missing_verified_checkpoint'),
        )
        for item, reason in cases:
            with self.subTest(reason=reason):
                result = self.select(candidates=[item])
                self.assertIsNone(result['session_id'])
                self.assertEqual(result['rejected'], {'session-a': reason})

    def test_fresh_only_and_reviewer_are_always_fresh(self):
        self.assertEqual(self.select({'fresh_only': True})['reason'], 'fresh_only')
        self.assertEqual(self.select({'role': 'reviewer'})['reason'], 'reviewer_fresh')

    def test_latest_settlement_then_stable_id_and_rejections_are_deterministic(self):
        result = self.select(candidates=[
            candidate('z', settled_at=20), candidate('b', settled_at=20),
            candidate('failed', settled=False), candidate('low', headroom={**candidate()['headroom'], 'occupancy': 100001}),
        ])
        self.assertEqual(result['session_id'], 'b')
        self.assertEqual(result['reason'], 'latest_successful_settlement')
        self.assertEqual(result['rejected'], {
            'failed': 'unsettled_or_failed', 'low': 'unknown_or_low_headroom',
        })

    def test_task_text_or_callback_identity_do_not_affect_compatibility(self):
        reusable = candidate(task_text='old task', callback_identity='old callback')
        result = self.select({'task_text': 'new task', 'callback_identity': 'new callback'}, [reusable])
        self.assertEqual(result['session_id'], 'session-a')
