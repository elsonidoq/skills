"""Existing workflow CLI: six task checks, ordinary SDK execution and history."""
import argparse
import json
import os
from pathlib import Path
import sqlite3
import signal
import sys
import uuid

from .engine import Engine, usage_summary
from .intake import load_contract
from .pi_adapter import PiAdapter, parent_question, terminal_question
from .store import Authority, Blocked, Store, canonical, execution_schema


def _selected_providers(executor):
    profiles = [executor]
    if isinstance(executor.get('reviewer'), dict):
        profiles.append(executor['reviewer'])
    return sorted({profile.get('provider') for profile in profiles if isinstance(profile.get('provider'), str) and profile['provider']})


def settle_paid_scope(contract, executor, question):
    """Settle paid application/test APIs; selected models are ordinary launch authority."""
    providers = _selected_providers(executor)
    scope = contract.get('paid_scope')
    scope_apis = scope.get('apis', []) if isinstance(scope, dict) else []
    apis = contract.get('paid_apis', [])
    for values in (scope_apis, apis):
        if not isinstance(values, list) or any(not isinstance(value, str) or not value for value in values):
            raise Blocked('paid_apis and paid_scope.apis must be lists of named application/test APIs; correct the task contract')
    apis = list(dict.fromkeys(scope_apis + apis))
    if not apis or (isinstance(scope, dict) and scope.get('approved') is True
                    and set(apis).issubset(scope_apis)):
        return {'agent_providers': providers, 'apis': apis}
    answer = question('Approve paid application/test APIs: ' + ', '.join(apis) + '. [yes/no]')
    if answer.strip().lower() not in ('yes', 'y'):
        raise Blocked('paid scope was not approved; no provider launch occurred')
    return {'agent_providers': providers, 'apis': apis}

ROOT = Path(__file__).resolve().parents[2]


def _safe_history_details(value):
    """Project operation facts without private task text, prompts, answers, or output."""
    details = json.loads(value)
    return {key: details[key] for key in ('command', 'exit_code', 'baseline', 'result', 'sha', 'parent',
                                           'paths', 'artifacts', 'generated_artifacts', 'no_change', 'error')
            if key in details}


def _metric_invocation_ids(db, run):
    """Read exact dispatch identities from ordinary history, never usage tables."""
    identifiers = []
    if not db.execute("SELECT 1 FROM sqlite_master WHERE name='execution_history'").fetchone():
        return identifiers
    for kind in ('worker_invocation', 'fixer_invocation'):
        for row in db.execute("SELECT details FROM execution_history WHERE run_id=? AND kind=? ORDER BY seq", (run, kind)):
            try:
                invocation_id = json.loads(row['details']).get('invocation_id')
            except (TypeError, ValueError):
                continue
            if isinstance(invocation_id, str) and invocation_id and invocation_id not in identifiers:
                identifiers.append(invocation_id)
    if db.execute("SELECT 1 FROM sqlite_master WHERE name='execution_review_executions'").fetchone():
        for row in db.execute("SELECT execution_id FROM execution_review_executions WHERE run_id=? AND role='reviewer' ORDER BY dispatched_at, execution_id", (run,)):
            if row['execution_id'] not in identifiers:
                identifiers.append(row['execution_id'])
    return identifiers


def status(project, run):
    database = Path(project).resolve() / '.coherence/workflow/workflow.sqlite'
    db = sqlite3.connect(database.as_uri() + '?mode=ro', uri=True)
    db.row_factory = sqlite3.Row
    try:
        db.execute('BEGIN')
        if not execution_schema(db):
            raise Blocked('unsupported workflow database format; start a new run to quarantine it and create clean storage')
        else:
            row = db.execute('SELECT * FROM execution_runs WHERE run_id=?', (run,)).fetchone()
            if row:
                has_inputs = db.execute("SELECT 1 FROM sqlite_master WHERE name='execution_run_inputs'").fetchone()
                inputs = (db.execute('SELECT contract,review_base FROM execution_run_inputs WHERE run_id=?', (run,)).fetchone()
                          if has_inputs else None)
                result = {'run': dict(row), 'tasks': [
                    {key: item[key] for key in ('run_id', 'task_id', 'state', 'baseline', 'result')}
                    for item in db.execute('SELECT * FROM execution_tasks WHERE run_id=? ORDER BY rowid', (run,))]}
                if inputs:
                    contract = json.loads(inputs['contract'])
                    authority = json.loads(db.execute('SELECT authority FROM execution_run_inputs WHERE run_id=?', (run,)).fetchone()['authority'])
                    policy = authority.get('review_policy') if isinstance(authority, dict) else None
                    result['input'] = {'task_ids': [task['id'] for task in contract.get('tasks', [])],
                                       'review_base': inputs['review_base'],
                                       'review_policy': policy if policy is not None else 'historical-two-review-one-fixer'}
                    result['history'] = [
                        {'task_id': item['task_id'], 'kind': item['kind'], 'state': item['state'],
                         'details': _safe_history_details(item['details'])}
                        for item in db.execute('SELECT task_id,kind,state,details FROM execution_history WHERE run_id=? ORDER BY seq', (run,))]
                result['usage'] = usage_summary(project, run, _metric_invocation_ids(db, run))
                if db.execute("SELECT 1 FROM sqlite_master WHERE name='execution_review_executions'").fetchone():
                    # This is the safe owner result: parsed actionable findings and range/commit
                    # references, never raw reviewer payloads, prompts, or answers.
                    result['review_chain'] = Store.review_chain(type('Reader', (), {'db': db})(), run)
                if db.execute("SELECT 1 FROM sqlite_master WHERE name='execution_history'").fetchone():
                    pairs = []
                    for item in db.execute("SELECT kind,state,details FROM execution_history WHERE run_id=? AND kind IN ('review_pair_grant','review_pair_reservation') ORDER BY seq", (run,)):
                        try:
                            facts = json.loads(item['details'])
                        except (TypeError, ValueError):
                            continue
                        pairs.append({'kind': item['kind'], 'state': item['state'], **{key: facts[key] for key in
                                      ('grant_id', 'rejecting_execution_id', 'review_base', 'review_head', 'original_scope',
                                       'fixer_execution_id', 'reviewer_execution_id') if key in facts}})
                    evidence_reassessments = set()
                    for item in db.execute("SELECT details FROM execution_history WHERE run_id=? AND kind='evidence_reassessment' AND state='authorized' ORDER BY seq", (run,)):
                        try:
                            rejecting = json.loads(item['details']).get('rejecting_execution_id')
                        except (TypeError, ValueError):
                            rejecting = None
                        if isinstance(rejecting, str) and rejecting:
                            evidence_reassessments.add(rejecting)
                    chain = result.get('review_chain', {})
                    executions = chain.get('executions', [])
                    next_stage = 'initial_review'
                    if executions:
                        last = executions[-1]
                        next_stage = 'blocked'
                        if not chain.get('uncertain'):
                            if last['role'] == 'reviewer' and last['state'] == 'approved':
                                next_stage = 'complete' if row['state'] == 'complete' else 'finalize_reviewed_head'
                            elif last['role'] == 'fixer' and last['state'] == 'approved':
                                next_stage = 'assigned_fresh_reviewer'
                            elif last['role'] == 'reviewer' and last['state'] == 'rejected':
                                if not last['findings']:
                                    summary = last['references'].get('review_summary', {})
                                    next_stage = ('assigned_evidence_reassessment' if last['execution_id'] in evidence_reassessments else
                                                  'coordinator_evidence_reassessment' if
                                                  result.get('input', {}).get('review_policy') == 'owner-pair-v1' and
                                                  isinstance(summary, dict) and summary.get('coverage_gaps') else 'blocked')
                                elif last['review_ordinal'] == 1:
                                    next_stage = 'automatic_fixer'
                                elif result.get('input', {}).get('review_policy') == 'owner-pair-v1':
                                    grant = next((pair for pair in reversed(pairs)
                                                  if pair['rejecting_execution_id'] == last['execution_id']), None)
                                    next_stage = ('reserve_assigned_fixer' if grant and grant['state'] == 'authorized'
                                                  else 'assigned_fixer' if grant and grant['state'] == 'fixer_reserved'
                                                  else 'owner_authorization_required' if grant is None else 'blocked')
                            elif last['role'] == 'fixer' and last['state'] == 'dispatched' and last['fixing_round'] > 1:
                                calls = {}
                                for event in db.execute("SELECT state,details FROM execution_history WHERE run_id=? AND kind='fixer_invocation' ORDER BY seq", (run,)):
                                    facts = json.loads(event['details'])
                                    if facts.get('execution_id') == last['execution_id']:
                                        calls[facts['invocation_id']] = event['state']
                                if all(state == 'returned' for state in calls.values()):
                                    next_stage = 'reconcile_assigned_fixer' if calls else 'assigned_fixer'
                    unsupported = result.get('input', {}).get('review_policy') not in (
                        None, 'owner-pair-v1', 'historical-two-review-one-fixer')
                    if unsupported or row['state'] == 'abandoned':
                        next_stage = 'blocked'
                    if pairs or executions or unsupported:
                        result['review_authorization'] = {'events': pairs, 'next_stage': next_stage}
                    if result.get('review_chain', {}).get('executions') and result['run']['error']:
                        result['run']['error'] = 'review outcome recorded; see review_chain'
                try:
                    monitored = db.execute('SELECT recording_version FROM execution_monitor_runs WHERE run_id=?', (run,)).fetchone()
                    if monitored:
                        observations = []
                        for item in db.execute('SELECT occurrence_id,phase,kind,facts FROM execution_observations WHERE run_id=? ORDER BY seq', (run,)):
                            facts = json.loads(item['facts'])
                            value = {'occurrence_id': item['occurrence_id'], 'phase': item['phase'], 'kind': item['kind']}
                            if item['phase'] == 'review':
                                value['review_range'] = {'base': facts.get('review_base'), 'head': facts.get('review_head')}
                            observations.append(value)
                        result['monitoring'] = {'recording_version': monitored['recording_version'], 'observations': observations}
                    else:
                        result['monitoring'] = {'state': 'unknown'}
                except (sqlite3.Error, ValueError, TypeError):
                    result['monitoring'] = {'state': 'unknown'}
                return result
        raise Blocked('workflow run not found: ' + run + '; select an existing execution run ID')
    finally:
        db.close()


def attached_question(run_id):
    if any(os.environ.get('COHERENCE_PARENT_BRIDGE_' + field) for field in ('SOCKET', 'TOKEN', 'SESSION', 'RUN')):
        if os.environ.get('COHERENCE_PARENT_BRIDGE_RUN') != run_id:
            raise Blocked('parent owner bridge run mismatch; launch this run through its parent-session bridge')
        parent_question(None, ready=True)
        return parent_question
    return None


def cancel(signum, frame):
    raise KeyboardInterrupt


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest='command', required=True)
    for command in ('start', 'resume', 'intake', 'status', 'history', 'abandon', 'authorize-routine-repairs', 'refresh-review-target'):
        sub = subs.add_parser(command)
        if command != 'intake':
            sub.add_argument('--project', required=True)
        if command in ('start', 'intake'):
            sub.add_argument('--tasks', required=True)
        if command == 'start':
            sub.add_argument('--executor', help='JSON file with provider, model and effort; no manifest or binding proof')
            sub.add_argument('--run', default=None)
        if command in ('resume', 'status', 'history', 'abandon', 'authorize-routine-repairs', 'refresh-review-target'):
            sub.add_argument('--run', required=True)
        if command == 'authorize-routine-repairs':
            sub.add_argument('--scope', required=True, help='exact retained original task scope from the authorized handoff')
    args = parser.parse_args(argv)
    run_id = None
    writer_entered = False
    previous_term = signal.signal(signal.SIGTERM, cancel)
    try:
        if args.command in ('status', 'history'):
            print(canonical(status(args.project, args.run)))
            return 0
        if args.command == 'abandon':
            with Authority(args.project, wait=True) as authority:
                print(canonical(authority.store.abandon(args.run)))
            return 0
        if args.command == 'authorize-routine-repairs':
            with Authority(args.project, wait=True) as authority:
                print(canonical(authority.store.authorize_routine_review_continuation(args.run, args.scope)))
            return 0
        if args.command == 'refresh-review-target':
            with Authority(args.project, wait=True) as authority:
                saved = authority.store.input(args.run)
                if not saved or not isinstance(saved.get('authority'), dict) or not isinstance(saved['authority'].get('paid_scope'), dict):
                    raise Blocked('review target refresh needs retained run input and paid scope')
                engine = Engine(authority, args.run, saved['contract'], saved['executor'], adapter=PiAdapter,
                                paid_scope=saved['authority']['paid_scope'], resume=True)
                print(canonical(engine.refresh_review_target()))
            return 0
        contract = load_contract(args.tasks) if args.command in ('start', 'intake') else None
        if args.command == 'intake':
            print(canonical({'task_ids': [task['id'] for task in contract['tasks']],
                             'status': 'ready' if contract['tasks'] else 'no tasks'}))
            return 0
        if args.command == 'resume':
            question = attached_question(args.run)
            with Authority(args.project, wait=True) as authority:
                saved = authority.store.input(args.run)
                if not saved or not isinstance(saved.get('contract'), dict) or not isinstance(saved['contract'].get('tasks'), list):
                    raise Blocked('resume cannot continue: original contract/history is missing')
                paid_scope = saved['authority'].get('paid_scope') if isinstance(saved.get('authority'), dict) else None
                if not isinstance(paid_scope, dict):
                    raise Blocked('resume cannot continue: retained paid scope is missing')
                # Validate retained launch bindings before resume() records progress. A legacy
                # missing reviewer needs owner correction, not a stranded running run.
                engine = Engine(authority, args.run, saved['contract'], saved['executor'], adapter=PiAdapter,
                                paid_scope=paid_scope, resume=True, **({'question': question} if question else {}))
                recovered = authority.store.resume(args.run)
                writer_entered = True
                result = engine.invoke()
                print(canonical(result))
            return 0
        if not contract['tasks']:
            print(canonical({'status': 'no tasks'}))
            return 0
        if not args.executor:
            raise Blocked('supply --executor JSON with the selected provider, model and effort')
        executor = json.loads(Path(args.executor).read_text())
        if not isinstance(executor, dict) or any(not isinstance(executor.get(k), str) or not executor[k]
                                                 for k in ('provider', 'model', 'effort')):
            raise Blocked('executor needs provider, model and effort strings')
        if not isinstance(executor.get('reviewer'), dict) or any(
                not isinstance(executor['reviewer'].get(key), str) or not executor['reviewer'][key]
                for key in ('provider', 'model', 'effort')):
            raise Blocked('reviewer needs provider, model and effort strings; correct the reviewer profile in --executor JSON')
        run_id = args.run or uuid.uuid4().hex
        question = attached_question(run_id)
        paid_scope = settle_paid_scope(contract, executor, question or terminal_question)
        with Authority(args.project, wait=True, quarantine_unsupported=True) as authority:
            if authority.quarantined_database:
                print('Unsupported workflow database quarantined at ' + str(authority.quarantined_database)
                      + '; created clean execution storage', file=sys.stderr)
            writer_entered = True
            result = Engine(authority, run_id, contract, executor, adapter=PiAdapter,
                            paid_scope=paid_scope, **({'question': question} if question else {})).invoke()
            print(canonical(result))
        return 0
    except (Blocked, OSError, ValueError, sqlite3.Error) as exc:
        print(canonical({'status': 'failed', 'reason': str(exc), **({'run_id': run_id} if run_id else {})}))
        return 2
    except KeyboardInterrupt:
        reason = ('cancelled while waiting for implementation writer; no task/run started'
                  if run_id and not writer_entered else 'cancelled; partial work retained')
        print(canonical({'status': 'interrupted', 'reason': reason}))
        return 130
    finally:
        signal.signal(signal.SIGTERM, previous_term)


if __name__ == '__main__':
    sys.exit(main())
