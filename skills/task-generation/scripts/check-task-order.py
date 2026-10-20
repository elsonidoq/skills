#!/usr/bin/env python3
"""Lint task identity, descriptions and dependency graphs, not administrative metadata."""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / 'runtime'))
from coherence_workflow.intake import admit, load_contract
from coherence_workflow.store import Blocked

TASK = re.compile(r'^\s*-\s*\[[ xX]\]\s+(\S+)\s*(.*)$')
DEPENDS = re.compile(r'^\s*-\s*\*\*Depends\*\*:\s*(.*)$', re.I)
REFERENCE = re.compile(r'\bT\d+\b')
RANGE = re.compile(r'\bT(\d+)\s*[-–—]\s*T(\d+)\b')


def check_structured(contract):
    try:
        admit(contract)
        return []
    except Blocked as exc:
        return [str(exc)]


def check(text):
    tasks = []
    current = None
    for line in text.splitlines():
        match = TASK.match(line)
        if match:
            current = {'id': match[1], 'outcome': match[2], 'depends': []}
            tasks.append(current)
        elif (match := DEPENDS.match(line)) and current is not None:
            raw = re.split(r'\s+\*\*', match[1], 1)[0]
            raw = re.sub(r'\([^)]*\)', '', raw).split('. ', 1)[0]
            if raw.strip().lower() == 'none':
                continue
            expanded = []
            for start, end in RANGE.findall(raw):
                if int(start) > int(end):
                    return [current['id']+': descending dependency range']
                expanded.extend(f'T{number:03d}' for number in range(int(start), int(end)+1))
            rest = RANGE.sub('', raw)
            dependencies = expanded + REFERENCE.findall(rest)
            if not dependencies and raw.strip():
                dependencies = [part.strip() for part in raw.split(',')]
            current['depends'] = dependencies
    return check_structured(tasks)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('tasks', type=Path)
    args = parser.parse_args()
    try:
        if args.tasks.suffix.lower() in ('.json', '.yaml', '.yml'):
            contract = load_contract(args.tasks)
            errors = []
            empty = not contract['tasks']
        else:
            text = args.tasks.read_text(encoding='utf-8')
            errors = check(text)
            empty = not any(TASK.match(line) for line in text.splitlines())
    except (Blocked, OSError, UnicodeError) as exc:
        errors, empty = [str(exc)], False
    for error in errors:
        print(error)
    print('FAIL: task input' if errors else 'No tasks' if empty else 'PASS: task dependencies are executable')
    return 1 if errors else 0


if __name__ == '__main__':
    raise SystemExit(main())
