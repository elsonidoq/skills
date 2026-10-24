#!/usr/bin/env python3
"""Resolve only the supplied project's executor configuration; never launch a provider."""
import argparse
import json
from pathlib import Path
import sys


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', required=True, type=Path, help='Project root')
    parser.add_argument('--executor', type=Path,
                        help='Existing executor JSON (relative paths are project-relative); '
                             'default: <project>/.pi/workflow-executor.json')
    args = parser.parse_args(argv)
    selected = args.executor if args.executor is not None else Path('.pi/workflow-executor.json')
    path = args.project / selected
    try:
        path = path.resolve()
        executor = json.loads(path.read_text(encoding='utf-8'))
        # Match the runner's nonempty string checks without importing its SDK/runtime
        # dependencies. Reviewer configuration is optional, but never silently repaired.
        profiles = [('executor', executor)]
        if isinstance(executor, dict) and 'reviewer' in executor:
            profiles.append(('reviewer', executor['reviewer']))
        for role, profile in profiles:
            if not isinstance(profile, dict) or any(
                    not isinstance(profile.get(key), str) or not profile[key]
                    for key in ('provider', 'model', 'effort')):
                raise ValueError(f'{role} needs provider, model and effort strings')
    except (OSError, ValueError, RuntimeError) as exc:
        print(f'Cannot resolve executor configuration {path}: {exc}. '
              'Supply a readable valid JSON file with provider, model and effort strings '
              'at this path or select one with --executor PATH (relative to --project). '
              'No fallback was attempted.', file=sys.stderr)
        return 2
    print(path)
    return 0


if __name__ == '__main__':
    sys.exit(main())
