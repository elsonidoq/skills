#!/usr/bin/env python3
"""Install suite links safely; foreign/uncertain entries are never relocated."""
import argparse
import json
import os
from pathlib import Path
import time

RETIRED = ("create-epic", "epics-manager", "requirements-manager", "epic-brainstorming")


def target(link):
    """Resolve symlink text even when the old target no longer exists."""
    raw = Path(os.readlink(link))
    return (raw if raw.is_absolute() else link.parent / raw).resolve()


def backup(path, backups):
    backups.mkdir(parents=True, exist_ok=True)
    base = backups / f"{path.name}.{time.time_ns()}"
    path.rename(base)
    print(f"backed up suite-owned link: {path} -> {base}")


def install(skills, guidance, destinations, docs, backups, settings):
    skills, guidance = skills.resolve(), guidance.resolve()
    entries = [(d.name, d.resolve()) for d in sorted(skills.iterdir())
               if (d / "SKILL.md").is_file()]
    desired = [(destinations / name, src) for name, src in entries]
    desired.append((docs / guidance.name, guidance))
    # Fail before writes if a current-name conflict is not the desired link.
    for dst, src in desired:
        if dst.is_symlink() and target(dst) == src:
            continue
        if os.path.lexists(dst):
            raise ValueError(f"preserved conflicting entry: {dst}; owner must resolve it")
    # Parse settings before writes too; malformed settings must remain untouched.
    data = json.loads(settings.read_text()) if settings.exists() else None
    if data is not None and not isinstance(data, dict):
        raise ValueError("settings must be a JSON object")
    if data is not None and "skills" in data:
        if not isinstance(data["skills"], list) or not all(isinstance(s, str) for s in data["skills"]):
            raise ValueError("settings skills must be a string list")
    destinations.mkdir(parents=True, exist_ok=True)
    docs.mkdir(parents=True, exist_ok=True)
    for name in RETIRED:
        old = destinations / name
        # Exact known source in THIS checkout only. Old checkout/foreign links stay.
        if old.is_symlink() and target(old) == skills / name:
            backup(old, backups)
        elif os.path.lexists(old):
            print(f"preserved retired-name foreign/uncertain entry: {old}")
    for dst, src in desired:
        if not dst.is_symlink():
            # Recheck against races; symlink() also fails rather than overwrite.
            dst.symlink_to(src)
            print(f"linked: {dst} -> {src}")
        elif target(dst) != src:
            raise ValueError(f"destination changed concurrently: {dst}")
    if data is not None:
        registered = data.get("skills", [])
        kept = [s for s in registered if Path(os.path.expanduser(s)).resolve() != skills]
        if kept != registered:
            before = settings.read_text()
            if json.loads(before) != data:
                raise ValueError("settings changed concurrently; not replacing")
            if kept:
                data["skills"] = kept
            else:
                data.pop("skills", None)
            tmp = settings.with_name(settings.name + f".{time.time_ns()}.tmp")
            with tmp.open("x") as f:
                os.chmod(tmp, settings.stat().st_mode & 0o777)
                json.dump(data, f, indent=2); f.write("\n")
            if settings.read_text() != before:
                tmp.unlink()
                raise ValueError("settings changed concurrently; not replacing")
            tmp.replace(settings)
            print(f"removed duplicate suite registration: {settings}")
    return len(entries)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ("skills", "guidance", "destinations", "docs", "backups", "settings"):
        p.add_argument(name, type=Path)
    args = p.parse_args()
    try:
        count = install(args.skills, args.guidance, args.destinations, args.docs,
                        args.backups, args.settings)
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"installation blocked: {exc}")
        return 1
    print(f"suite links ready: {count} skills")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
