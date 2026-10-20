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
from .pi_adapter import PiAdapter, parent_question
from .store import Authority, Blocked, canonical, read_history

ROOT = Path(__file__).resolve().parents[2]


def status(project, run):
    database = Path(project).resolve() / '.coherence/workflow/workflow.sqlite'
    db = sqlite3.connect(database.as_uri() + '?mode=ro', uri=True)
    db.row_factory = sqlite3.Row
    try:
        db.execute('BEGIN')
        if db.execute("SELECT 1 FROM sqlite_master WHERE name='execution_runs'").fetchone():
            row = db.execute('SELECT * FROM execution_runs WHERE run_id=?', (run,)).fetchone()
            if row:
                result = {'run': dict(row), 'tasks': [dict(r) for r in db.execute(
                    'SELECT * FROM execution_tasks WHERE run_id=? ORDER BY rowid', (run,))]}
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
        run_id = args.run or uuid.uuid4().hex
        question = parent_question if os.environ.get('COHERENCE_PARENT_BRIDGE_SOCKET') else None
        with Authority(args.project) as authority:
            result = Engine(authority, run_id, contract, executor, adapter=PiAdapter,
                            **({'question': question} if question else {})).invoke()
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
