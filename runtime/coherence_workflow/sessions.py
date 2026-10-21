"""Pure same-run saved-session candidate policy.

The runner supplies all facts; this module neither opens sessions nor inspects Git/files.
"""
import math


DEFAULT_MIN_FREE_TOKENS_BEFORE_COMPACTION = 150000

_COMPATIBILITY_FIELDS = (
    'role', 'worktree', 'executor', 'resources', 'instructions', 'settings', 'authority',
)


def effective_headroom(observation):
    """Return measured usable tokens, or ``None`` when the observation is unusable.

    Capacity is usable only when compaction is both enabled and applicable and all three
    token measurements are finite non-negative numbers.  Unknown capacity is deliberately
    not estimated.
    """
    if not isinstance(observation, dict):
        return None
    if observation.get('compaction_enabled') is not True or observation.get('compaction_applicable') is not True:
        return None
    values = [observation.get(name) for name in ('context_window', 'effective_reserve', 'occupancy')]
    if any(isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0
           for value in values):
        return None
    return values[0] - values[1] - values[2]


def _rejection(request, candidate, minimum):
    if not isinstance(candidate, dict):
        return 'invalid_candidate'
    if candidate.get('run_id') != request.get('run_id') or not request.get('run_id'):
        return 'different_run'
    if candidate.get('settled') is not True or candidate.get('idle') is not True:
        return 'unsettled_or_failed'
    if candidate.get('checkpoint_verified') is not True:
        return 'missing_verified_checkpoint'
    if not isinstance(candidate.get('context_group'), str) or not candidate['context_group']:
        return 'missing_context_group'
    if candidate['context_group'] != request['context_group']:
        return 'context_group_mismatch'
    for field in _COMPATIBILITY_FIELDS:
        if request.get(field) is None or candidate.get(field) != request[field]:
            return field + '_mismatch'
    headroom = effective_headroom(candidate.get('headroom'))
    if headroom is None or headroom < minimum:
        return 'unknown_or_low_headroom'
    return None


def select_session(request, candidates, *, min_free_tokens_before_compaction=DEFAULT_MIN_FREE_TOKENS_BEFORE_COMPACTION):
    """Choose an eligible saved session or an honest fresh-session decision.

    ``request`` and each candidate are runner facts.  A candidate must identify the same
    run, a successful idle settlement, a prior verified checkpoint, a nonempty matching
    context group, exact stable compatibility fields, and usable headroom.  Eligible
    candidates are ordered by latest settlement followed by stable ID.
    """
    if not isinstance(request, dict):
        request = {}
    if (isinstance(min_free_tokens_before_compaction, bool)
            or not isinstance(min_free_tokens_before_compaction, (int, float))
            or not math.isfinite(min_free_tokens_before_compaction)
            or min_free_tokens_before_compaction < 0):
        # Invalid configuration must still leave safe fresh execution available.
        return {'session_id': None, 'reason': 'invalid_headroom_policy', 'rejected': {}}
    candidates = candidates if isinstance(candidates, (list, tuple)) else ()
    rejected = {}
    if request.get('fresh_only') is True:
        return {'session_id': None, 'reason': 'fresh_only', 'rejected': rejected}
    if request.get('role') == 'reviewer':
        return {'session_id': None, 'reason': 'reviewer_fresh', 'rejected': rejected}
    if not isinstance(request.get('context_group'), str) or not request['context_group']:
        return {'session_id': None, 'reason': 'missing_context_group', 'rejected': rejected}

    eligible = []
    for index, candidate in enumerate(candidates):
        session_id = candidate.get('id') if isinstance(candidate, dict) else None
        key = session_id if isinstance(session_id, str) and session_id else 'candidate-' + str(index)
        if not isinstance(session_id, str) or not session_id:
            rejected[key] = 'invalid_session_id'
            continue
        reason = _rejection(request, candidate, min_free_tokens_before_compaction)
        if reason:
            rejected[key] = reason
            continue
        settlement = candidate.get('settled_at')
        if isinstance(settlement, bool) or not isinstance(settlement, (int, float)) or not math.isfinite(settlement):
            rejected[key] = 'invalid_settlement'
            continue
        eligible.append((settlement, session_id))
    if not eligible:
        return {'session_id': None, 'reason': 'no_eligible_session', 'rejected': rejected}
    eligible.sort(key=lambda item: (-item[0], item[1]))
    return {'session_id': eligible[0][1], 'reason': 'latest_successful_settlement', 'rejected': rejected}
