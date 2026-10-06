#!/usr/bin/env python3
"""Static task-commit contract checks; diagnostic instruction assertions, not runtime proof."""
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = (
    "brainstorming compact-memory coordinate-implementation delegating-architectural-planning "
    "finish-session finish-session-jev handoff-prompt incorporate-skill infographic initialize-coherence "
    "memory-handling planner planning-brainstorming receiving-code-review requesting-code-review "
    "scientific-method-debugging supabase-server task-generation tiny-spec track-open-issue "
    "using-git-worktrees writing-skills"
).split()


def check(root=ROOT, coordinator_text=None, prompt_text=None, architectural_text=None, contract_text=None):
    errors = []
    contract = root / "skills/memory-handling/references/task-commit-contract.md"
    if not contract.is_file():
        return ["task-commit contract: canonical owner missing"]
    contract_text = contract.read_text() if contract_text is None else contract_text
    for phrase in ("no skip/defer question", "fresh implementer", "path-limited task commit", "evidence-only checkpoint"):
        if phrase not in contract_text:
            errors.append(f"task-commit contract: missing {phrase!r}")
    coordinator = coordinator_text if coordinator_text is not None else (root / "skills/coordinate-implementation/SKILL.md").read_text()
    for phrase in (
        "no skip/defer question", "No-Git fallback", "never adopts or commits unknown work",
        "coordinator alone may recover", "failed recovery stops dispatch", "evidence-only checkpoint",
    ):
        if phrase not in coordinator:
            errors.append(f"coordinator checkpoint guard missing: {phrase!r}")
    if "ask whether to skip/defer" in coordinator or "proceed without per-task commits" in coordinator:
        errors.append("coordinator checkpoint waiver reintroduced")
    for location, text in (("contract", contract_text), ("coordinator", coordinator)):
        normalized = " ".join(text.split())
        if "without routine coordinator approval" not in normalized:
            errors.append(f"{location} batch autonomy guard missing")
        if "wait for coordinator validation before next-task writes" in normalized:
            errors.append("routine per-task coordinator barrier reintroduced")
    for skill in SKILLS:
        if "task-commit-contract.md" not in (root / "skills" / skill / "SKILL.md").read_text():
            errors.append(f"consumer link missing: {skill}")
    for prompt in (root / ".pi/prompts").glob("speckit.*.md"):
        if "task-commit-contract.md" not in prompt.read_text():
            errors.append(f"prompt link missing: {prompt.name}")
    architectural = architectural_text if architectural_text is not None else (root / "skills/delegating-architectural-planning/SKILL.md").read_text()
    for phrase in ("focused path-limited task checkpoint", "before completion or handoff", "must not push or dispatch additional agents"):
        if phrase not in architectural:
            errors.append(f"architectural planning checkpoint guard missing: {phrase!r}")
    if "Commit, push, or dispatch additional agents" in architectural:
        errors.append("architectural planning commit opt-in reintroduced")
    prompt = prompt_text if prompt_text is not None else (root / ".pi/prompts/speckit.implement.md").read_text()
    for phrase in ("hooks.before_implement", "hooks.after_implement", "MUST actually invoke the hook", "Wait for the result of the hook command"):
        if phrase not in prompt:
            errors.append(f"SpecKit hook operational guard missing: {phrase!r}")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    errors = check(args.root)
    for error in errors:
        print(error)
    print(f"task-commit contract: {'FAIL' if errors else 'PASS'} (static instructions only)")
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
