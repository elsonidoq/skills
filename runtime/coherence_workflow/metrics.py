"""Honest per-open SDK usage interval accounting.

This module only derives one interval from the fresh observations returned by the host.
It does not store, aggregate, or allocate usage to tasks.
"""
import math

_FIELDS = ('input', 'output', 'cacheRead', 'cacheWrite')


def _number(value):
    return (isinstance(value, (int, float)) and not isinstance(value, bool)
            and math.isfinite(value) and value >= 0)


def _unknown(reason):
    return {'value': None, 'unknown_reason': reason, 'provenance': None}


def _value(value, provenance):
    return {'value': value, 'unknown_reason': None, 'provenance': provenance}


def _continuity_reason(before, after, exclusive, outcome):
    if not isinstance(before, dict) or not isinstance(after, dict):
        return 'missing_interval_end'
    if exclusive is not True:
        return 'nonexclusive_interval'
    if outcome != 'settled':
        return 'ambiguous_or_unsettled_interval'
    for field in ('session_id', 'branch', 'epoch'):
        if not before.get(field) or before.get(field) != after.get(field):
            return 'session_branch_or_epoch_changed'
    return None


def _delta(before, after, field, continuity, *, source, label):
    if continuity:
        return _unknown(continuity)
    start = (before.get(source) or {}).get(field)
    end = (after.get(source) or {}).get(field)
    if not _number(start) or not _number(end):
        return _unknown('missing_or_invalid_' + label)
    if end < start:
        return _unknown(label + '_reset')
    return _value(end - start, 'sdk_cumulative_' + source + '.' + field)


def _summary_usage(value):
    """Project only the SDK summary fields that are safe metric data."""
    if not isinstance(value, dict):
        return None
    result = {}
    for name in ('input', 'output', 'cacheRead', 'cacheWrite', 'totalTokens',
                 'cacheWrite1h', 'reasoning'):
        if _number(value.get(name)):
            result[name] = value[name]
    costs = value.get('cost')
    if isinstance(costs, dict):
        safe_costs = {name: costs[name] for name in ('input', 'output', 'cacheRead', 'cacheWrite', 'total')
                      if _number(costs.get(name))}
        if safe_costs:
            result['cost'] = safe_costs
    return result or None


def _entries(observation):
    entries = observation.get('compaction_entries') if isinstance(observation, dict) else None
    if not isinstance(entries, list):
        return None
    result = {}
    for entry in entries:
        if isinstance(entry, dict) and isinstance(entry.get('id'), str) and entry['id']:
            result[entry['id']] = entry
    return result


def interval_record(before, after, *, exclusive=True, outcome='settled'):
    """Return one non-duplicating interval with field-level unknown reasons.

    Counter and estimated-USD deltas are only meaningful over one continuous exclusive
    session/branch/epoch.  Compactions are counted from newly persisted entry IDs, not
    start events, so failed or aborted attempts are absent by construction.
    """
    continuity = _continuity_reason(before, after, exclusive, outcome)
    counters = {
        'input': _delta(before or {}, after or {}, 'input', continuity, source='counters', label='counter'),
        'output': _delta(before or {}, after or {}, 'output', continuity, source='counters', label='counter'),
        'cache_read': _delta(before or {}, after or {}, 'cacheRead', continuity, source='counters', label='counter'),
        'cache_write': _delta(before or {}, after or {}, 'cacheWrite', continuity, source='counters', label='counter'),
    }
    total = (_value(sum(value['value'] for value in counters.values()), 'sum_of_sdk_counter_deltas')
             if all(value['value'] is not None for value in counters.values())
             else _unknown('partial_or_unknown_token_categories'))
    usd = _delta(before or {}, after or {}, 'estimated_usd', continuity,
                 source='costs', label='estimated_usd')

    before_entries, after_entries = _entries(before), _entries(after)
    if before_entries is None or after_entries is None:
        compactions = {'entry_ids': [], 'count': None, 'unknown_reason': 'missing_compaction_entries'}
        overhead = {'entries': [], 'unknown_reason': 'missing_compaction_entries',
                    'included_in_sdk_deltas': True}
    else:
        new_entries = [entry for entry_id, entry in after_entries.items()
                       if entry_id not in before_entries]
        entry_ids = sorted(entry['id'] for entry in new_entries)
        compactions = {'entry_ids': entry_ids, 'count': len(entry_ids), 'unknown_reason': None}
        overhead_entries = []
        for entry in sorted(new_entries, key=lambda item: item['id']):
            usage = _summary_usage(entry.get('summary_usage'))
            overhead_entries.append({
                'entry_id': entry['id'],
                'usage': usage,
                'unknown_reason': None if usage is not None else 'summary_usage_unavailable',
            })
        overhead = {'entries': overhead_entries,
                    'unknown_reason': None if all(item['unknown_reason'] is None for item in overhead_entries)
                    else 'summary_usage_unavailable',
                    # Summary usage is a labelled subset of SDK deltas, never an addend.
                    'included_in_sdk_deltas': True}
    return {
        'session_id': after.get('session_id') if isinstance(after, dict) else None,
        'branch': after.get('branch') if isinstance(after, dict) else None,
        'epoch': after.get('epoch') if isinstance(after, dict) else None,
        'outcome': outcome,
        'tokens': counters,
        'total_tokens': total,
        'estimated_usd': usd,
        'compactions': compactions,
        'summary_overhead': overhead,
    }
