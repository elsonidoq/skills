"""Existing workflow CLI: six task checks, ordinary SDK execution and history."""
import argparse
import json
import os
import re
from pathlib import Path
import sqlite3
import signal
import sys
import uuid

from .engine import Engine, usage_summary
from .graph import run_graph
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
                                           'paths', 'artifacts', 'generated_artifacts', 'no_change', 'error',
                                           'invocation_id', 'recovery_id', 'external_recovery_id',
                                           'sdk', 'executor_path', 'changed_fields', 'correction')
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


class RunNotFound(Blocked):
    pass


def _changed_fields(retained, current, prefix=''):
    fields = []
    for key in sorted(set(retained) | set(current)):
        old, new = retained.get(key), current.get(key)
        if isinstance(old, dict) and isinstance(new, dict):
            fields.extend(_changed_fields(old, new, prefix + key + '.'))
        elif old != new:
            fields.append(prefix + key)
    return fields


def executor_drift(db, run, retained):
    """Compare the launch executor file with the retained executor; report only."""
    row = db.execute("SELECT details FROM execution_history WHERE run_id=? AND kind='launch_environment' "
                     "ORDER BY seq DESC LIMIT 1", (run,)).fetchone()
    path = json.loads(row['details']).get('executor_path') if row else None
    if not path:
        return None
    correction = ('this run keeps its recorded executor; to use the changed file, start a new run '
                  'for the remaining tasks')
    try:
        current = json.loads(Path(path).read_text())
    except (OSError, ValueError) as exc:
        return {'executor_path': path, 'error': 'cannot read the launch executor file: ' + str(exc),
                'correction': correction}
    if not isinstance(current, dict) or not isinstance(retained, dict):
        return {'executor_path': path, 'changed_fields': ['<root>'], 'correction': correction}
    changed = _changed_fields(retained, current)
    return {'executor_path': path, 'changed_fields': changed, 'correction': correction} if changed else None


def baseline_checks(project, contract):
    """Run each distinct required check once at the current checkout; report only."""
    from .store import git
    from .verification import _run_check, commands
    distinct = {}
    for task in contract['tasks']:
        for value in commands(task):
            command = value.get('command', value.get('argv', value.get('check'))) if isinstance(value, dict) else value
            if not isinstance(command, (str, list)) or not command or (isinstance(command, list) and
                    any(not isinstance(arg, str) for arg in command)):
                raise Blocked('task ' + task['id'] + ' check needs a command string or argv list of strings')
            distinct.setdefault(canonical(command), {'command': command, 'tasks': []})['tasks'].append(task['id'])
    results = []
    for item in distinct.values():
        code, output = _run_check(Path(project).resolve(), item['command'], None, lambda state, attempt: None)
        results.append({**item, 'exit_code': code, 'output': output})
    return {'head': git(Path(project).resolve(), 'rev-parse', 'HEAD').decode().strip(),
            'failed': sum(1 for item in results if item['exit_code'] != 0), 'checks': results}


def status(project, run, *, summary_only=False):
    database = Path(project).resolve() / '.coherence/workflow/workflow.sqlite'
    if summary_only:
        try:
            database.stat()
        except FileNotFoundError as exc:
            raise RunNotFound(f'no workflow database in {project}') from exc
    db = sqlite3.connect(database.as_uri() + '?mode=ro', uri=True)
    db.row_factory = sqlite3.Row
    try:
        db.execute('BEGIN')
        if not execution_schema(db):
            raise Blocked('unsupported workflow database format; start a new run to quarantine it and create clean storage')
        else:
            row = db.execute('SELECT * FROM execution_runs WHERE run_id=?', (run,)).fetchone()
            if row:
                result = {'run': dict(row), 'tasks': [
                    {key: item[key] for key in ('run_id', 'task_id', 'state', 'baseline', 'result')}
                    for item in db.execute('SELECT * FROM execution_tasks WHERE run_id=? ORDER BY rowid', (run,))]}
                if summary_only:
                    return result
                has_inputs = db.execute("SELECT 1 FROM sqlite_master WHERE name='execution_run_inputs'").fetchone()
                inputs = (db.execute('SELECT contract,review_base FROM execution_run_inputs WHERE run_id=?', (run,)).fetchone()
                          if has_inputs else None)
                graph_backend = False
                if inputs:
                    contract = json.loads(inputs['contract'])
                    authority = json.loads(db.execute('SELECT authority FROM execution_run_inputs WHERE run_id=?', (run,)).fetchone()['authority'])
                    policy = authority.get('review_policy') if isinstance(authority, dict) else None
                    graph_backend = isinstance(authority, dict) and authority.get('backend') == 'langgraph-v1'
                    result['input'] = {'task_ids': [task['id'] for task in contract.get('tasks', [])],
                                       'review_base': inputs['review_base'],
                                       'review_policy': policy if policy is not None else 'historical-two-review-one-fixer'}
                    result['history'] = [
                        {'task_id': item['task_id'], 'kind': item['kind'], 'state': item['state'],
                         'details': _safe_history_details(item['details'])}
                        for item in db.execute('SELECT task_id,kind,state,details FROM execution_history WHERE run_id=? ORDER BY seq', (run,))]
                launch = next((item['details']['sdk'] for item in reversed(result.get('history', []))
                               if item['kind'] == 'launch_environment' and 'sdk' in item['details']), None)
                if launch is not None:
                    result['sdk'] = launch
                if row['state'] == 'interrupted' and row['error'] == 'waiting for owner answer':
                    waiting = db.execute("SELECT task_id,details FROM execution_history WHERE run_id=? AND kind='graph_wait' AND state='waiting' ORDER BY seq DESC LIMIT 1", (run,)).fetchone()
                    if waiting:
                        try:
                            identity = json.loads(waiting['details']).get('invocation_id')
                        except (TypeError, ValueError):
                            identity = None
                        if isinstance(identity, str) and identity:
                            result['waiting'] = {'task_id': waiting['task_id'], 'question_id': identity,
                                'action': 'resume interactively or through the attached parent'}
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
                                                  else 'automatic_fixer' if grant is None and graph_backend else 'blocked')
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
        raise RunNotFound('workflow run not found: ' + run + '; select an existing execution run ID')
    finally:
        db.close()


def require_graph_run(project, run, arguments):
    """Reject legacy mutation before opening the writer or contacting the parent."""
    import shlex
    database = Path(project).resolve() / '.coherence/workflow/workflow.sqlite'
    try:
        db = sqlite3.connect(database.as_uri() + '?mode=ro', uri=True)
        try:
            if not execution_schema(db):
                raise Blocked('unsupported workflow database format; inspect retained storage before mutation')
            if not db.execute('SELECT 1 FROM execution_runs WHERE run_id=?', (run,)).fetchone():
                raise Blocked('workflow run not found: ' + run + '; select an existing execution run ID')
            has_inputs = db.execute("SELECT 1 FROM sqlite_master WHERE name='execution_run_inputs'").fetchone()
            row = db.execute('SELECT authority FROM execution_run_inputs WHERE run_id=?', (run,)).fetchone() if has_inputs else None
        finally:
            db.close()
    except sqlite3.Error as exc:
        raise Blocked('cannot inspect retained run backend; inspect the existing workflow database: ' + str(exc)) from exc
    try:
        authority = json.loads(row[0]) if row else {}
    except (TypeError, ValueError) as exc:
        raise Blocked('run backend authority is unreadable; inspect retained input before mutation') from exc
    if not isinstance(authority, dict) or authority.get('backend') != 'langgraph-v1':
        command = 'LEGACY_SUITE/scripts/coordinate-implementation ' + shlex.join(arguments)
        raise Blocked('Run ' + run + ' is legacy, not a LangGraph thread. Inspect its saved call and use ' + command +
                      ' from retained pre-cutover revision 4c1725ebded2f89dec6933b8d193bf34997c62ce with compatible dependencies; do not convert or replay it.')


def attached_question(run_id):
    if any(os.environ.get('COHERENCE_PARENT_BRIDGE_' + field) for field in ('SOCKET', 'TOKEN', 'SESSION', 'RUN')):
        if os.environ.get('COHERENCE_PARENT_BRIDGE_RUN') != run_id:
            raise Blocked('parent owner bridge run mismatch; launch this run through its parent-session bridge')
        parent_question(None, ready=True)
        return parent_question
    return None


def cancel(signum, frame):
    raise KeyboardInterrupt


def _commit_id(value):
    if not re.fullmatch(r'(?:[0-9a-f]{40}|[0-9a-f]{64})', value):
        raise argparse.ArgumentTypeError('supply the full inspected commit SHA, not a ref or abbreviation')
    return value


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest='command', required=True)
    for command in ('start', 'resume', 'intake', 'baseline-checks', 'status', 'history', 'abandon', 'refresh-review-target', 'recover-task', 'recover-publication'):
        sub = subs.add_parser(command)
        if command != 'intake':
            sub.add_argument('--project', required=True)
        if command in ('start', 'intake', 'baseline-checks'):
            sub.add_argument('--tasks', required=True)
        if command == 'start':
            sub.add_argument('--executor', help='JSON file with provider, model and effort; no manifest or binding proof')
            sub.add_argument('--run', default=None)
            sub.add_argument('--delivery-scope', type=json.loads,
                             help='optional JSON carrier of already granted target/authority/known_linked_prs; retained for resume, not a grant')
            sub.add_argument('--parallel', action='store_true', help='explicitly direct disjoint dependency-ready worker waves; default sequential')
        if command in ('resume', 'status', 'history', 'abandon', 'refresh-review-target', 'recover-task', 'recover-publication'):
            sub.add_argument('--run', required=True)
        if command == 'recover-publication':
            sub.add_argument('--snapshot', help='exact retained snapshot ID; defaults to latest prepared snapshot, or retained facts if none')
            sub.add_argument('--delivery-scope', type=json.loads,
                             help='actual publication grant carrier; must match retained scope when present')
        if command == 'resume':
            sub.add_argument('--recovery-action', choices=('continue', 'fresh', 'escalate'),
                             help='coordinator-selected inspected continuation of the unfinished task')
            sub.add_argument('--target-head', type=_commit_id, metavar='COMMIT', help='full inspected direct-child commit for fresh offline verification')
            sub.add_argument('--diagnosis', help='inspected cause and targeted correction; not renewed owner consent')
        if command == 'recover-task':
            sub.add_argument('--recovery', required=True, help='JSON exact external same-task completion transfer; see operating guide')
            sub.add_argument('--owner-authorized', action='store_true', help='assert actual owner authorization for this exact transfer')
    args = parser.parse_args(argv)
    run_id = None
    writer_entered = False
    previous_term = signal.signal(signal.SIGTERM, cancel)
    try:
        if args.command in ('status', 'history'):
            print(canonical(status(args.project, args.run)))
            return 0
        if args.command == 'recover-publication':
            from .trace_publication import recover_publication
            database = Path(args.project).resolve() / '.coherence/workflow/workflow.sqlite'
            if not database.is_file():
                print(canonical({
                    'implementation': {'state': 'unavailable', 'replayed': False},
                    'publication': {'state': 'deferred', 'snapshot_id': args.snapshot,
                                    'urls': [], 'correction': 'Publication recovery needs retained workflow storage; restore the original database, not a coding replay.'}}))
                return 2
            with Authority(args.project, wait=True) as authority:
                result = recover_publication(authority.store, args.run, snapshot_id=args.snapshot,
                                             delivery_scope=args.delivery_scope)
                print(canonical(result))
            return 0 if (result['publication']['state'] == 'confirmed' and
                         result.get('linkage', {}).get('state') == 'confirmed') else 2
        if args.command == 'recover-task' and not args.owner_authorized:
            raise Blocked('external task recovery requires actual owner authorization; obtain it and supply --owner-authorized')
        if args.command == 'resume' and any(os.environ.get('COHERENCE_PARENT_BRIDGE_' + field) for field in ('SOCKET', 'TOKEN', 'SESSION', 'RUN')) and os.environ.get('COHERENCE_PARENT_BRIDGE_RUN') != args.run:
            raise Blocked('parent owner bridge run mismatch; launch this run through its parent-session bridge')
        if args.command in ('resume', 'abandon', 'refresh-review-target', 'recover-task'):
            require_graph_run(args.project, args.run, list(argv) if argv is not None else sys.argv[1:])
        if args.command == 'abandon':
            with Authority(args.project, wait=True) as authority:
                print(canonical(authority.store.abandon(args.run)))
            return 0
        if args.command == 'recover-task':
            if not args.owner_authorized:
                raise Blocked('external task recovery requires actual owner authorization; obtain it and supply --owner-authorized')
            with Authority(args.project, wait=True) as authority:
                saved = authority.store.input(args.run)
                if not saved or not isinstance(saved.get('authority'), dict) or not isinstance(saved['authority'].get('paid_scope'), dict):
                    raise Blocked('external task recovery needs retained input and paid scope; inspect run history')
                question = attached_question(args.run)
                engine = Engine(authority, args.run, saved['contract'], saved['executor'], adapter=PiAdapter,
                                paid_scope=saved['authority']['paid_scope'], resume=True,
                                **({'question': question} if question else {}))
                result = run_graph(engine, action='external', transfer=json.loads(Path(args.recovery).read_text()), owner_authorized=True)
                print(canonical(result))
            return 0
        if args.command == 'refresh-review-target':
            with Authority(args.project, wait=True) as authority:
                saved = authority.store.input(args.run)
                if not saved or not isinstance(saved.get('authority'), dict) or not isinstance(saved['authority'].get('paid_scope'), dict):
                    raise Blocked('review target refresh needs retained run input and paid scope')
                engine = Engine(authority, args.run, saved['contract'], saved['executor'], adapter=PiAdapter,
                                paid_scope=saved['authority']['paid_scope'], resume=True)
                print(canonical(run_graph(engine, action='refresh-review-target')))
            return 0
        contract = load_contract(args.tasks) if args.command in ('start', 'intake', 'baseline-checks') else None
        if args.command == 'baseline-checks':
            report = baseline_checks(args.project, contract)
            print(canonical(report))
            return 1 if report['failed'] else 0
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
                if bool(args.recovery_action) != bool(args.diagnosis):
                    raise Blocked('resume recovery needs both --recovery-action and --diagnosis')
                if args.target_head is not None and args.recovery_action != 'fresh':
                    raise Blocked('--target-head requires --recovery-action fresh and --diagnosis')
                recovery = {'action': args.recovery_action, 'diagnosis': args.diagnosis} if args.recovery_action else None
                engine = Engine(authority, args.run, saved['contract'], saved['executor'], adapter=PiAdapter,
                                paid_scope=paid_scope, resume=True, worker_recovery=recovery,
                                **({'question': question} if question else {}))
                drift = executor_drift(authority.store.db, args.run, saved['executor'])
                if drift:
                    authority.store.history(args.run, None, 'executor_drift', 'reported', drift)
                    print('Executor drift: ' + canonical(drift), file=sys.stderr, flush=True)
                authority.store.resume(args.run)
                writer_entered = True
                result = run_graph(engine, action=args.recovery_action, diagnosis=args.diagnosis, target_head=args.target_head)
                print(canonical({**result, 'executor_drift': drift} if drift and isinstance(result, dict) else result))
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
        fallback = executor.get('implementation_fallback')
        if fallback is not None and (not isinstance(fallback, dict) or any(
                not isinstance(fallback.get(key), str) or not fallback[key] for key in ('provider', 'model', 'effort'))):
            raise Blocked('implementation_fallback needs provider, model and effort strings; correct the selected executor')
        run_id = args.run or uuid.uuid4().hex
        question = attached_question(run_id)
        # Before the paid-scope question and any run state. Offline test adapters
        # have no host to resolve; the production adapter always has preflight.
        preflight = getattr(PiAdapter, 'preflight', None)
        sdk = preflight(args.project, executor) if callable(preflight) else None
        launch = {'executor_path': str(Path(args.executor).resolve()), **({'sdk': sdk} if isinstance(sdk, dict) else {})}
        if 'sdk' in launch:
            print('Pi SDK ' + str(sdk.get('version')) + ' at ' + str(sdk.get('package_dir')), file=sys.stderr, flush=True)
        paid_scope = settle_paid_scope(contract, executor, question or terminal_question)
        with Authority(args.project, wait=True, quarantine_unsupported=True) as authority:
            if authority.quarantined_database:
                print('Unsupported workflow database quarantined at ' + str(authority.quarantined_database)
                      + '; created clean execution storage', file=sys.stderr)
            writer_entered = True
            engine = Engine(authority, run_id, contract, executor, adapter=PiAdapter,
                            paid_scope=paid_scope, parallel=args.parallel, delivery_scope=args.delivery_scope,
                            launch=launch, **({'question': question} if question else {}))
            result = run_graph(engine)
            print(canonical({**result, 'sdk': launch['sdk']} if 'sdk' in launch and isinstance(result, dict) else result))
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
