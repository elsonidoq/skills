#!/usr/bin/env python3
"""Safely migrate legacy epic workflow JSON to the canonical OpenCode state key."""

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

from resolve_epic import resolve


STAGES = {
    "preflight", "brainstorm_gate", "epic_brainstorm", "epic_brainstorm_fix",
    "epic_critique", "epic_fix", "spec_create", "spec_clarify", "spec_critique",
    "spec_fix", "planning_gate", "plan_create", "plan_critique", "plan_fix",
    "tasks_create", "tasks_critique", "tasks_fix", "done",
}

DEFAULTS = {
    "schema_version": 1,
    "epic_file": None,
    "epic_heading": None,
    "epic_number": None,
    "worktree_path": None,
    "spec_dir": None,
    "stage": "preflight",
    "resume_stage_after_preflight": None,
    "pending_critique": None,
    "pending_answers": None,
    "pending_handoff": None,
    "decisions": [],
    "dependencies": [],
    "deferrals": [],
    "blockers": [],
}


def _source_identity(value, repo_root):
    if value is None:
        return None
    path = Path(value)
    if repo_root is None:
        return path.as_posix().removeprefix("./")
    root = Path(repo_root).resolve()
    path = path.resolve() if path.is_absolute() else (root / path).resolve()
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def migrate_state(legacy, selected, source, repo_root=None, approve_identity_drift=False):
    if not isinstance(legacy, dict):
        raise ValueError("Legacy state must be a JSON object")
    if legacy.get("schema_version", 1) != 1:
        raise ValueError("Unsupported legacy state schema_version")
    legacy_file = _source_identity(legacy.get("epic_file"), repo_root)
    file_drift = legacy_file not in (None, selected["epic_file"])
    heading_drift = legacy.get("epic_heading") not in (None, selected["epic_heading"])
    if (file_drift or heading_drift) and not approve_identity_drift:
        raise ValueError("Legacy source identity changed; reconcile identity with the user")
    if legacy.get("epic_number") not in (None, selected["epic_number"]):
        raise ValueError("Legacy epic_number does not match the selected epic")

    old_stage = legacy.get("stage", "preflight")
    if old_stage not in STAGES:
        raise ValueError(f"Unknown legacy stage: {old_stage!r}")

    migrated = {**DEFAULTS, **legacy}
    migrated.update({
        "schema_version": 1,
        "epic_file": selected["epic_file"],
        "epic_heading": selected["epic_heading"],
        "epic_number": selected["epic_number"],
        "stage": "preflight",
        "resume_stage_after_preflight": old_stage,
        "migration_source": source,
    })
    if file_drift or heading_drift:
        migrated["reconciled_identity"] = {
            "epic_file": legacy.get("epic_file"),
            "epic_heading": legacy.get("epic_heading"),
            "epic_number": legacy.get("epic_number"),
        }
    if old_stage == "epic_brainstorm_fix" and migrated.get("pending_answers") is None:
        migrated["pending_answers"] = legacy.get("pending_brainstorm_answers")
    pending_deferrals = legacy.get("pending_deferrals") or []
    if pending_deferrals:
        migrated["deferrals"] = [*(legacy.get("deferrals") or []), *pending_deferrals]
    return migrated


def migrate_file(source, target, selected, repo_root=None, approve_identity_drift=False):
    source = Path(source).resolve()
    target = Path(target).resolve()
    legacy_bytes = source.read_bytes()
    backup = target.with_suffix(target.suffix + ".legacy.bak")
    migration_source = backup if source == target else source
    migrated = migrate_state(json.loads(legacy_bytes), selected, migration_source.as_posix(),
                             repo_root=repo_root,
                             approve_identity_drift=approve_identity_drift)
    migrated["migration_source_sha256"] = hashlib.sha256(legacy_bytes).hexdigest()
    target.parent.mkdir(parents=True, exist_ok=True)

    if source != target and target.exists():
        raise ValueError(f"Canonical state already exists; reconcile conflict: {target}")
    if source == target:
        if backup.exists() and backup.read_bytes() != legacy_bytes:
            raise ValueError(f"Migration backup already exists with different content: {backup}")
        if not backup.exists():
            backup.write_bytes(legacy_bytes)

    temporary = target.with_suffix(target.suffix + ".tmp")
    temporary.write_text(json.dumps(migrated, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, target)
    return target


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_state")
    parser.add_argument("epic_file")
    parser.add_argument("selector", nargs="?")
    parser.add_argument("--approve-identity-drift", action="store_true",
                        help="migrate a source move/title rename after explicit owner approval")
    args = parser.parse_args()
    root = next((path for path in (Path.cwd(), *Path.cwd().parents)
                 if (path / ".specify").is_dir()), None)
    if root is None:
        parser.error("Run within a repository containing .specify/")
    try:
        selected = resolve(args.epic_file, args.selector, root)
        source = Path(args.source_state)
        source = source if source.is_absolute() else root / source
        source.resolve().relative_to(root.resolve())
        target = root / ".opencode/epics-workflow" / f"{selected['state_key']}.json"
        print(migrate_file(source, target, selected, repo_root=root,
                           approve_identity_drift=args.approve_identity_drift))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
