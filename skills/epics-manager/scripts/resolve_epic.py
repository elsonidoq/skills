#!/usr/bin/env python3
"""Read-only epic selection and state identity; uses only the Python standard library."""

import argparse
import hashlib
import json
import re
import sys
import unicodedata
from pathlib import Path


def slug(text):
    text = unicodedata.normalize("NFKD", text.casefold())
    text = "".join(char for char in text if not unicodedata.combining(char))
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")


def epic_sections(text):
    """Return epics with 1-based inclusive bounds, ignoring fenced headings."""
    lines = text.splitlines()
    headings = []
    fence = None
    for number, line in enumerate(lines, 1):
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line)
        if marker:
            run, tail = marker.groups()
            if fence is None:
                fence = (run[0], len(run))
            elif run[0] == fence[0] and len(run) >= fence[1] and not tail.strip():
                fence = None
            continue
        if fence is not None:
            continue
        heading = re.match(r"^#\s+(.+?)\s*$", line)
        if heading:
            title = re.sub(r"\s+#+$", "", heading.group(1))
            headings.append((number, title))

    epics = []
    seen = set()
    for index, (start, title) in enumerate(headings):
        match = re.match(r"^Epic ([0-9]+)(?=$|\s|[^\w])", title)
        if not match:
            continue
        number = int(match.group(1))
        if number in seen:
            raise ValueError(f"Duplicate Epic {number} headings; resolve before proceeding")
        seen.add(number)
        end = headings[index + 1][0] - 1 if index + 1 < len(headings) else len(lines)
        epics.append({"epic_number": number, "epic_heading": "# " + title,
                      "epic_slug": slug(title), "start_line": start, "end_line": end})
    return epics


def select_epic(epics, selector):
    if selector is None:
        matches = epics if len(epics) == 1 else []
    else:
        normalized = slug(selector)
        numeric = re.fullmatch(r"(?:epic-)?([0-9]+)", normalized)
        if numeric:
            matches = [item for item in epics if item["epic_number"] == int(numeric[1])]
        elif normalized:
            matches = [item for item in epics
                       if f"-{normalized}-" in f"-{item['epic_slug']}-"]
        else:
            matches = []
    if len(matches) != 1:
        candidates = "; ".join(item["epic_heading"] for item in epics) or "none"
        raise ValueError(f"Selector {selector!r} must match exactly one epic. Candidates: {candidates}")
    return dict(matches[0])


def resolve(epic_file, selector, repo_root):
    root = Path(repo_root).resolve()
    path = Path(epic_file)
    path = (root / path).resolve() if not path.is_absolute() else path.resolve()
    try:
        relative = path.relative_to(root).as_posix()
    except ValueError as exc:
        raise ValueError("Epic file must be inside the repository") from exc
    epics = epic_sections(path.read_text(encoding="utf-8"))
    selected = select_epic(epics, selector)
    file_key = hashlib.sha256(relative.encode("utf-8")).hexdigest()[:12]
    selected.update({
        "epic_file": relative,
        "state_key": f"{slug(path.stem)}-{file_key}--{selected['epic_slug']}",
        "preamble_start_line": 1,
        "preamble_end_line": epics[0]["start_line"] - 1,
    })
    return selected


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("epic_file")
    parser.add_argument("selector", nargs="?")
    args = parser.parse_args()
    root = next((path for path in (Path.cwd(), *Path.cwd().parents)
                 if (path / ".specify").is_dir()), None)
    if root is None:
        parser.error("Run within a repository containing .specify/")
    try:
        result = resolve(args.epic_file, args.selector, root)
    except (OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
