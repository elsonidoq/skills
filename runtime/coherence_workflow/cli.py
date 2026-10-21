"""Existing workflow CLI: six task checks, ordinary SDK execution and history."""
import argparse
import json
import os
from pathlib import Path
import sqlite3
import signal
import sys
import uuid

from .engine import Engine
from .intake import load_contract
from .pi_adapter import PiAdapter, parent_question, terminal_question
from .store import Authority, Blocked, canonical, read_history


def _selected_providers(executor):
    profiles = [executor]
    if isinstance(executor.get('reviewer'), dict):
        profiles.append(executor['reviewer'])
    return sorted({profile.get('provider') for profile in profiles if isinstance(profile.get('provider'), str) and profile['provider']})


def settle_paid_scope(contract, executor, question):
    """Return explicit current-run paid scope before any provider launch."""
    providers = _selected_providers(executor)
    scope = contract.get('paid_scope')
    if isinstance(scope, dict) and scope.get('approved') is True:
        approved_providers, apis = scope.get('agent_providers'), scope.get('apis')
        if (isinstance(approved_providers, list) and all(isinstance(value, str) and value for value in approved_providers)
                and sorted(set(approved_providers)) == providers and isinstance(apis, list)
                and all(isinstance(value, str) and value for value in apis)):
            return {'agent_providers': providers, 'apis': apis}
    apis = contract.get('paid_apis', [])
    if not isinstance(apis, list) or any(not isinstance(value, str) or not value for value in apis):
        raise Blocked('paid_apis must be a list of named application/test APIs when supplied')
    named_apis = ', '.join(apis) if apis else 'none declared'
    answer = question('Approve paid scope before any provider launch: selected agent-provider(s): ' +
                      ', '.join(providers) + '; application/test APIs: ' + named_apis + '. [yes/no]')
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


def status(project, run):
    database = Path(project).resolve() / '.coherence/workflow/workflow.sqlite'
    db = sqlite3.connect(database.as_uri() + '?mode=ro', uri=True)
    db.row_factory = sqlite3.Row
    try:
        db.execute('BEGIN')
        if db.execute("SELECT 1 FROM sqlite_master WHERE name='execution_runs'").fetchone():
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
                    result['input'] = {'task_ids': [task['id'] for task in contract.get('tasks', [])],
                                       'review_base': inputs['review_base']}
                    result['history'] = [
                        {'task_id': item['task_id'], 'kind': item['kind'], 'state': item['state'],
                         'details': _safe_history_details(item['details'])}
                        for item in db.execute('SELECT task_id,kind,state,details FROM execution_history WHERE run_id=? ORDER BY seq', (run,))]
                if db.execute("SELECT 1 FROM sqlite_master WHERE name='execution_review_executions'").fetchone():
                    # This is the safe owner result: parsed actionable findings and range/commit
                    # references, never raw reviewer payloads, prompts, or answers.
                    from .store import Store
                    result['review_chain'] = Store.review_chain(type('Reader', (), {'db': db})(), run)
                    if result['review_chain']['executions'] and result['run']['error']:
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
        return read_history(db, run)
    finally:
        db.close()


def cancel(signum, frame):
    raise KeyboardInterrupt


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest='command', required=True)
    for command in ('start', 'intake', 'status', 'history', 'abandon'):
        sub = subs.add_parser(command)
        if command != 'intake':
            sub.add_argument('--project', required=True)
        if command in ('start', 'intake'):
            sub.add_argument('--tasks', required=True)
        if command == 'start':
            sub.add_argument('--executor', help='JSON file with provider, model and effort; no manifest or binding proof')
            sub.add_argument('--run', default=None)
        if command in ('status', 'history', 'abandon'):
            sub.add_argument('--run', required=True)
    args = parser.parse_args(argv)
    run_id = None
    previous_term = signal.signal(signal.SIGTERM, cancel)
    try:
        if args.command in ('status', 'history'):
            print(canonical(status(args.project, args.run)))
            return 0
        if args.command == 'abandon':
            with Authority(args.project) as authority:
                print(canonical(authority.store.abandon(args.run)))
            return 0
        contract = load_contract(args.tasks)
        if args.command == 'intake':
            print(canonical({'task_ids': [task['id'] for task in contract['tasks']],
                             'status': 'ready' if contract['tasks'] else 'no tasks'}))
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
        if 'reviewer' in executor and (not isinstance(executor['reviewer'], dict) or any(
                not isinstance(executor['reviewer'].get(key), str) or not executor['reviewer'][key]
                for key in ('provider', 'model', 'effort'))):
            raise Blocked('reviewer needs provider, model and effort strings; correct the reviewer profile in --executor JSON')
        run_id = args.run or uuid.uuid4().hex
        question = None
        if any(os.environ.get('COHERENCE_PARENT_BRIDGE_' + field) for field in ('SOCKET', 'TOKEN', 'SESSION', 'RUN')):
            if os.environ.get('COHERENCE_PARENT_BRIDGE_RUN') != run_id:
                raise Blocked('parent owner bridge run mismatch; launch this run through its parent-session bridge')
            parent_question(None, ready=True)
            question = parent_question
        paid_scope = settle_paid_scope(contract, executor, question or terminal_question)
        with Authority(args.project) as authority:
            result = Engine(authority, run_id, contract, executor, adapter=PiAdapter,
                            paid_scope=paid_scope, **({'question': question} if question else {})).invoke()
            print(canonical(result))
        return 0
    except (Blocked, OSError, ValueError, sqlite3.Error) as exc:
        print(canonical({'status': 'failed', 'reason': str(exc), **({'run_id': run_id} if run_id else {})}))
        return 2
    except KeyboardInterrupt:
        print(canonical({'status': 'interrupted', 'reason': 'cancelled; partial work retained'}))
        return 130
    finally:
        signal.signal(signal.SIGTERM, previous_term)


if __name__ == '__main__':
    sys.exit(main())
