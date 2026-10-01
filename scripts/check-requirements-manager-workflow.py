#!/usr/bin/env python3
"""Deterministic operational-contract checks for the workflow skills.

These checks examine executable stage and rule prose, not diagrams or model behavior.
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
PATHS = {
    "epic": "skills/epics-manager/SKILL.md",
    "brainstorm": "skills/epic-brainstorming/SKILL.md",
    "tasks": "skills/task-generation/SKILL.md",
    "requirements": "skills/requirements-manager/SKILL.md",
    "coordinator": "skills/coordinate-implementation/SKILL.md",
    "create": "skills/create-epic/SKILL.md",
    "requirements_doc": "REQUIREMENTS.md",
}


def check_contracts(texts: dict[str, str]) -> list[str]:
    """Return named diagnostics for missing operational requirements."""
    failures = []

    def require(check: str, key: str, *phrases: str) -> None:
        text = texts[key]
        for phrase in phrases:
            if phrase not in text:
                failures.append(f"{check}: missing {key} phrase {phrase!r}")

    require("epic-order", "epic", "### `brainstorm_gate` — `sonnet-class`",
            "### `plan_create` — `opus-class`", "### `tasks_create` — `sonnet-class`")
    sequence = ["### `brainstorm_gate`", "### `epic_brainstorm`", "### `epic_brainstorm_fix`",
                "### `spec_create`", "### `plan_create`", "### `tasks_create`",
                "### `overall_review`", "### `done`"]
    positions = [texts["epic"].find(item) for item in sequence]
    if -1 in positions or positions != sorted(positions):
        failures.append("epic-order: operational stage headings are absent or reordered")
    require("shared-gate", "epic", "shared `epic-brainstorming`", "shared `task-generation`",
            "This stage is create-only", "task defects belong to `overall_review`",
            "renew specification approval", "Resume from the earliest missing, stale, or inconsistent")
    require("brainstorm", "brainstorm", "NO_BRAINSTORM_NEEDED", "BRAINSTORM_NEEDED",
            "no more than three items", "The orchestrator, not a delegated worker",
            "exactly the recorded owner decisions", "If a required capability is unavailable, report")
    require("direct-route", "requirements", "No intermediate\nspecification or plan is created.",
            "It does not require a plan or SpecKit.", "explicit current owner approval",
            "coordinator alone selects execution", "stale or unverifiable")
    require("direct-adapter", "tasks", "A direct adapter derives tasks", "does not\n  require a plan or SpecKit", "30%")
    require("epic-exception", "create", "documentation-initialization exception", "`requirements-manager`")
    require("runtime-dependency", "requirements_doc", "direct requirements-manager tasking does not require it")
    require("origin-intake", "coordinator", "For `requirements-manager` origin",
            "No specification, plan, or SpecKit prerequisite is required", "Ambiguous origin is a blocker")
    require("threshold", "coordinator", "Up to three bounded implementation tasks may run locally",
            "current owner-selected model/class matches each task", "observed context capacity is adequate",
            "More than three implementation tasks require delegation", "including completed tasks",
            "exclude standalone review tasks", "Retain the recorded strategy on resume")
    require("context-batching", "coordinator", "Internal dependencies, shared files, and phase/story headings do not require",
            "evidenced model-class changes, owner gates, context limits", "never\n   run implementation batches in parallel",
            "only asynchronously in the background")
    require("upstream-coherence", "tasks", "coherent sequential work", "do not reorder dependencies or pad")
    require("sessions", "coordinator", "observed context\n  headroom is adequate", "Inspect the failed run and tool invocation before retry")
    require("commit-review", "coordinator", "Commit each task's verified changes as one focused commit",
            "No per-task reviews", "full committed revision range")
    for key, text in texts.items():
        for legacy in ("OpenCode", "resolve_epic.py", "named historical agents"):
            if legacy in text:
                failures.append(f"legacy: forbidden {legacy!r} in {key}")
    return failures


def load_texts(root: Path = ROOT) -> dict[str, str]:
    return {key: (root / path).read_text(encoding="utf-8") for key, path in PATHS.items()}


def main() -> int:
    failures = check_contracts(load_texts())
    if failures:
        print("requirements-manager workflow contract: FAIL")
        print("\n".join(f"- {failure}" for failure in failures))
        return 1
    print("requirements-manager workflow contract: PASS (operational static checks; no model calls)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
