"""One role-safe selector. Inputs are trusted runner facts, never model recommendations."""
import math
import json
from .store import Blocked


def retained_candidates(store, run):
    """SQL-settled saved conversations, never caller-supplied invented sessions."""
    candidates = {}
    for row in store.db.execute("SELECT o.*,e.seq FROM wf_operations o JOIN wf_events e USING(op_id) WHERE o.run_id=? AND o.kind='sdk-turn' AND e.kind='completed' ORDER BY e.seq", (run,)):
        if row['phase'] != 'completed' or not row['result']:
            raise Blocked('retained turn is not completed')
        result = json.loads(row['result'])
        host = store.operation(result['host_op'])
        if host['phase'] != 'completed':
            raise Blocked('retained host not closed/reconciled')
        snapshot = result['after']
        candidates[snapshot['session_id']] = {**result['compatibility'], 'id':snapshot['session_id'],
            'settled':True,'poisoned':False,'settle_seq':row['seq'],'telemetry':snapshot,
            'host_op':result['host_op']}
    return list(candidates.values())


def manifest_compatibility(manifest, project, *, role, affinity, review_lineage):
    from .store import digest
    return {'role':role,'affinity':affinity,'review_lineage':review_lineage,'worktree':str(project),
            **{k:digest(manifest[k]) for k in ('profile','skills','tools','permissions','trust')},
            'settings':digest({'settings':manifest['settings'],'pressure_policy':manifest['pressure_policy'],
                               'system_prompt':manifest['system_prompt']})}


def open_manifest(manifest, candidate):
    import copy
    result = copy.deepcopy(manifest)
    snapshot = candidate['telemetry']
    result['open'] = {key:snapshot[value] for key,value in (
        ('file','session_file'),('session_id','session_id'),('leaf','leaf'),('sha256','session_file_hash'))}
    return result


COMPATIBILITY = ('affinity','profile','skills','tools','permissions','trust','settings','worktree')


def headroom(telemetry, *, now_ns, max_age_ns):
    t = telemetry or {}
    values = [t.get(k) for k in ('observed_ns','threshold','occupancy')]
    if (t.get('reliable') is not True or t.get('enabled') is not True or not t.get('provenance')
            or any(isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) or v < 0 for v in values)):
        return None
    observed, threshold, occupancy = values
    if not 0 <= now_ns-observed <= max_age_ns or threshold <= 0:
        return None
    return threshold-occupancy


def select_session(request, candidates, *, now_ns, max_age_ns,
                   min_free_tokens_before_compaction=150000):
    """Fresh is a decision, not permission to bypass unreconciled work or an original pin."""
    if not all(request.get(k) is True for k in ('authorized','ready','reconciled')):
        raise Blocked('session admission requires ready authorized reconciled work')
    if max_age_ns < 0 or min_free_tokens_before_compaction < 0:
        raise Blocked('invalid session policy')
    if len({c['id'] for c in candidates}) != len(candidates):
        raise Blocked('duplicate session identity')
    if any(not c.get('settled') or c.get('poisoned') for c in candidates):
        raise Blocked('unknown/unsettled session custody; reconcile before selection')
    role = request['role']
    family = lambda r: 'implement' if r in ('implement','repair') else r
    eligible = []
    rejected = {}
    for c in candidates:
        reason = None
        if any(c.get(k) != request.get(k) or request.get(k) is None for k in COMPATIBILITY):
            reason = 'incompatible_manifest'
        elif family(c['role']) != family(role) or c.get('review_lineage') != request.get('review_lineage'):
            reason = 'role_isolation'
        elif role == 'review' and (not request.get('review_lineage') or c.get('review_lineage') != request['review_lineage']):
            reason = 'review_lineage'
        else:
            free = headroom(c.get('telemetry'),now_ns=now_ns,max_age_ns=max_age_ns)
            if free is None or free < min_free_tokens_before_compaction:
                reason = 'unknown_or_low_headroom'
        if reason:
            rejected[c['id']] = reason
        else:
            eligible.append(c)
    pin = request.get('pin')
    if pin:
        selected = next((c for c in eligible if c['id']==pin),None)
        if request.get('fresh_only') or not selected:
            raise Blocked('original conversation pin unavailable/ineligible; owner recovery required')
        reason = 'original_question_pin'
    elif request.get('fresh_only'):
        selected,reason = None,'fresh_only'
    elif role == 'review' and not request.get('review_lineage'):
        selected,reason = None,'independent_first_review'
    else:
        eligible.sort(key=lambda c:(-c['settle_seq'],c['id']))
        selected = next((c for c in eligible if role=='repair' and c['id']==request.get('original')),None)
        reason = 'original_implementer' if selected else 'latest_settled_stable_id'
        selected = selected or next(iter(eligible),None)
        if not selected:
            reason = 'no_eligible_session'
    return {'session_id':selected['id'] if selected else None,'reason':reason,'rejected':rejected}
