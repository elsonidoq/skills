"""Read and watch workflow status without starting a runner."""
import argparse
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import time

from .cli import RunNotFound, status
from .store import Blocked


def configured_worktrees():
    config_home = Path(os.environ.get('XDG_CONFIG_HOME') or Path.home() / '.config')
    config = config_home / 'coherence/status-projects'
    try:
        entries = [line.strip() for line in config.read_text().splitlines()
                   if line.strip() and not line.lstrip().startswith('#')]
    except FileNotFoundError:
        entries = []
    if not entries:
        raise Blocked(f'list one Git checkout per line in {config}, or pass --project PATH')

    worktrees = {}
    env = {key: value for key, value in os.environ.items()
           if key not in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_COMMON_DIR')}
    for entry in entries:
        checkout = Path(entry).expanduser()
        if not checkout.is_absolute():
            raise Blocked(f'use an absolute checkout path in {config}: {entry!r}')
        git = subprocess.run(['git', '-C', str(checkout), 'worktree', 'list', '--porcelain', '-z'],
                             env=env, capture_output=True)
        if git.returncode:
            raise Blocked(f'cannot list Git worktrees for {checkout}: '
                          f'{os.fsdecode(git.stderr).strip()}; correct {config} or pass --project PATH')
        for record in git.stdout.split(b'\0\0'):
            header, *fields = record.split(b'\0')
            if header.startswith(b'worktree ') and b'bare' not in fields:
                path = Path(os.fsdecode(header[len(b'worktree '):]))
                if not path.exists() and any(field.startswith(b'prunable ') for field in fields):
                    continue
                worktrees[path.resolve()] = None
    return worktrees


def read_status(project, run):
    try:
        return status(project, run, summary_only=True)
    except RunNotFound:
        raise
    except (Blocked, OSError, sqlite3.Error) as exc:
        raise Blocked(f'cannot read workflow status in {project}: {exc}; check the worktree and database access') from exc


def select_run(run, project):
    if project is not None:
        path = project.expanduser().resolve()
        return path, read_status(path, run)
    matches = {}
    for path in configured_worktrees():
        try:
            matches[path] = read_status(path, run)
        except RunNotFound:
            continue
    if not matches:
        raise RunNotFound(f'workflow {run!r} not found in configured worktrees; check the run name or pass --project PATH')
    if len(matches) > 1:
        choices = '\n'.join(f'  {path}' for path in matches)
        raise Blocked(f'workflow {run!r} matches multiple worktrees; pass --project PATH:\n{choices}')
    return next(iter(matches.items()))


def snapshot(report):
    return '\n'.join([f"{report['run']['run_id']}: {report['run']['state']}",
                      *(f"  {task['task_id']}\t{task['state']}" for task in report['tasks'])])


def main(argv=None):
    parser = argparse.ArgumentParser(description='Show the recorded state of a Coherence workflow and its tasks.')
    parser.add_argument('run', metavar='RUN_NAME', help='workflow run name (run ID)')
    parser.add_argument('--project', type=Path, metavar='PATH', help='read this exact worktree instead of searching configured projects')
    parser.add_argument('--watch', action='store_true', help='check for changes every five seconds; Ctrl+C stops watching')
    args = parser.parse_args(argv)
    try:
        project, report = select_run(args.run, args.project)
        print(f'Worktree: {project}', flush=True)
        previous = None
        while True:
            current = snapshot(report)
            if current != previous:
                print(current, flush=True)
                previous = current
            if not args.watch:
                return 0
            time.sleep(5)
            report = read_status(project, args.run)
    except KeyboardInterrupt:
        return 0
    except (Blocked, OSError, UnicodeError, RuntimeError) as exc:
        print(f'coherence-status: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
