#!/usr/bin/env python3
"""Check explicit task dependencies and story grouping in a numbered Markdown task list."""

import argparse
import re
from pathlib import Path


TASK = re.compile(r"^\s*-\s*\[[ xX]\]\s+(T(\d+))\b(.*)$")
DEPENDS = re.compile(r"^\s*-\s*\*\*Depends\*\*:\s*(.*)$", re.IGNORECASE)
REFERENCE = re.compile(r"\bT(\d+)\b")
RANGE = re.compile(r"\bT(\d+)\s*[-–—]\s*T(\d+)\b")
STORY = re.compile(r"\[([^\]]*US\d+[^\]]*)\]", re.IGNORECASE)
FIELD = re.compile(r"\s+\*\*[A-Za-z][^*]*\*\*:")


def check(text: str) -> list[str]:
    tasks: list[dict] = []
    current = None
    for line_number, line in enumerate(text.splitlines(), 1):
        match = TASK.match(line)
        if match:
            story = STORY.search(match.group(3))
            current = {
                "id": match.group(1),
                "number": int(match.group(2)),
                "line": line_number,
                "story": story.group(1).upper() if story else None,
                "depends": None,
            }
            tasks.append(current)
            continue
        match = DEPENDS.match(line)
        if match and current is not None:
            raw = FIELD.split(match.group(1), 1)[0]
            # Parenthetical annotations describe dependencies; they are not extra edges.
            raw = re.sub(r"\([^)]*\)", "", raw).split(". ", 1)[0]
            current["depends"] = raw

    if not tasks:
        return ["no numbered Markdown tasks found; inspect task format manually"]

    errors: list[str] = []
    seen: dict[int, dict] = {}
    story_blocks: set[str] = set()
    previous_story = None
    for task in tasks:
        number = task["number"]
        name = task["id"]
        line = task["line"]
        if number in seen:
            errors.append(f"line {line}: duplicate task number {name}")
        if not seen and number != 1:
            errors.append(f"line {line}: first task must be T001, not {name}")
        if seen and number != next(reversed(seen)) + 1:
            errors.append(f"line {line}: {name} is not numbered immediately after the preceding task")
        if task["depends"] is None:
            errors.append(f"line {line}: {name} has no explicit Depends field")
        else:
            raw = task["depends"]
            ranges = RANGE.findall(raw)
            expanded: list[int] = []
            for start, end in ranges:
                if int(start) > int(end):
                    errors.append(f"line {line}: {name} has a descending dependency range")
                else:
                    expanded.extend(range(int(start), int(end) + 1))
            raw = RANGE.sub("", raw)
            dependencies = expanded + [int(ref) for ref in REFERENCE.findall(raw)]
            if not dependencies and not re.match(r"\s*none\b", raw, re.IGNORECASE):
                errors.append(f"line {line}: {name} has an unrecognized Depends field")
            for dependency in dependencies:
                if dependency == number:
                    errors.append(f"line {line}: {name} depends on itself")
                elif dependency not in seen:
                    relation = "later-numbered" if dependency > number else "missing or out-of-order"
                    errors.append(f"line {line}: {name} depends on {relation} T{dependency:03d}")
        story = task["story"]
        if story != previous_story:
            if story in story_blocks:
                errors.append(f"line {line}: {story} resumes after a different story/stage")
            if story is not None:
                story_blocks.add(story)
            previous_story = story
        seen[number] = task
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tasks", type=Path, help="Path to the Markdown task list")
    args = parser.parse_args()
    try:
        text = args.tasks.read_text(encoding="utf-8")
    except OSError as error:
        parser.error(str(error))
    errors = check(text)
    for error in errors:
        print(error)
    if errors:
        print(f"FAIL: {len(errors)} task-order issue(s)")
        return 1
    print("PASS: numbered tasks have earlier prerequisites and contiguous user stories")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
