"""T011/V2 synthetic per-open usage and persisted-compaction accounting."""
import unittest

from coherence_workflow.metrics import interval_record


def observation(**changes):
    value = {
        'session_id': 'session-1', 'branch': 'branch-1', 'epoch': 'epoch-1',
        'counters': {'input': 10, 'output': 5, 'cacheRead': 2, 'cacheWrite': 1},
        'costs': {'estimated_usd': 0.10},
        'compaction_entries': [{'id': 'old', 'summary_usage': {'input': 2}}],
    }
    value.update(changes)
    return value


class IntervalAccountingTests(unittest.TestCase):
    def test_two_reused_intervals_keep_categories_total_usd_and_new_entry_ids(self):
        first_before = observation()
        first_after = observation(
            counters={'input': 15, 'output': 8, 'cacheRead': 2, 'cacheWrite': 3},
            costs={'estimated_usd': 0.16},
            compaction_entries=[{'id': 'old', 'summary_usage': {'input': 2}},
                                {'id': 'compact-1', 'summary_usage': {'input': 4}}],
        )
        second_after = observation(
            counters={'input': 20, 'output': 9, 'cacheRead': 5, 'cacheWrite': 3},
            costs={'estimated_usd': 0.20},
            compaction_entries=[{'id': 'old', 'summary_usage': {'input': 2}},
                                {'id': 'compact-1', 'summary_usage': {'input': 4}},
                                {'id': 'compact-2', 'summary_usage': {'input': 3}}],
        )
        first = interval_record(first_before, first_after)
        second = interval_record(first_after, second_after)
        self.assertEqual([first['tokens'][name]['value'] for name in ('input', 'output', 'cache_read', 'cache_write')],
                         [5, 3, 0, 2])
        self.assertEqual(first['total_tokens']['value'], 10)
        self.assertEqual(first['estimated_usd']['value'], 0.06)
        self.assertEqual(first['compactions'], {'entry_ids': ['compact-1'], 'count': 1, 'unknown_reason': None})
        self.assertEqual(second['compactions']['entry_ids'], ['compact-2'])
        self.assertEqual(second['summary_overhead']['entries'][0]['entry_id'], 'compact-2')
        self.assertTrue(first['summary_overhead']['included_in_sdk_deltas'])

    def test_epoch_reset_missing_end_and_partial_counter_keep_honest_unknowns(self):
        reset = interval_record(observation(), observation(epoch='epoch-2'))
        self.assertEqual(reset['tokens']['input']['unknown_reason'], 'session_branch_or_epoch_changed')
        counter_reset = interval_record(observation(), observation(counters={'input': 1, 'output': 6, 'cacheRead': 2, 'cacheWrite': 1}))
        self.assertEqual(counter_reset['tokens']['input']['unknown_reason'], 'counter_reset')
        self.assertEqual(counter_reset['tokens']['output']['value'], 1)
        partial = interval_record(observation(), observation(counters={'input': 12, 'output': None, 'cacheRead': 2, 'cacheWrite': 1}))
        self.assertEqual(partial['tokens']['input']['value'], 2)
        self.assertEqual(partial['tokens']['output']['unknown_reason'], 'missing_or_invalid_counter')
        self.assertEqual(partial['total_tokens']['unknown_reason'], 'partial_or_unknown_token_categories')
        missing_end = interval_record(observation(), None)
        self.assertEqual(missing_end['estimated_usd']['unknown_reason'], 'missing_interval_end')

    def test_usd_and_compaction_overhead_are_unknown_without_observations(self):
        record = interval_record(observation(), observation(costs={}, compaction_entries=[{'id': 'old'}]))
        self.assertEqual(record['estimated_usd']['unknown_reason'], 'missing_or_invalid_estimated_usd')
        self.assertEqual(record['compactions']['count'], 0)
        self.assertEqual(record['summary_overhead']['unknown_reason'], None)
        unknown_entries = interval_record(observation(compaction_entries=None), observation())
        self.assertEqual(unknown_entries['compactions']['unknown_reason'], 'missing_compaction_entries')
        self.assertEqual(unknown_entries['summary_overhead']['unknown_reason'], 'missing_compaction_entries')

    def test_failed_or_aborted_start_events_do_not_count_without_persisted_entry(self):
        before = observation()
        after = observation()  # The host may have emitted start/end events, but no persisted entry exists.
        record = interval_record(before, after)
        self.assertEqual(record['compactions'], {'entry_ids': [], 'count': 0, 'unknown_reason': None})

    def test_summary_usage_projects_only_closed_safe_numeric_fields(self):
        after = observation(compaction_entries=[
            {'id': 'old', 'summary_usage': {'input': 2}},
            {'id': 'new', 'summary_usage': {'input': 3, 'reasoning': 1, 'private': 'omit',
                                             'cost': {'total': .02, 'secret': 1}}},
        ])
        record = interval_record(observation(), after)
        self.assertEqual(record['summary_overhead']['entries'][0]['usage'],
                         {'input': 3, 'reasoning': 1, 'cost': {'total': .02}})


if __name__ == '__main__':
    unittest.main()
