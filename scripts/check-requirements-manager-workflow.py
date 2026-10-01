#!/usr/bin/env python3
"""Deterministic operational prompt-contract checks; not model-obedience proof."""
from pathlib import Path
import argparse
import sys

ROOT = Path(__file__).resolve().parents[1]
PATHS = {
    "epic": "skills/epics-manager/SKILL.md", "brainstorm": "skills/epic-brainstorming/SKILL.md",
    "tasks": "skills/task-generation/SKILL.md", "requirements": "skills/requirements-manager/SKILL.md",
    "coordinator": "skills/coordinate-implementation/SKILL.md", "create": "skills/create-epic/SKILL.md",
    "requirements_doc": "REQUIREMENTS.md",
}
STAGES = ("brainstorm_gate", "epic_brainstorm", "epic_brainstorm_fix", "spec_create", "plan_create", "tasks_create", "overall_review", "done")


def section(text: str, stage: str) -> str:
    marker = f"### `{stage}`"
    start = text.find(marker)
    if start < 0:
        return ""
    end = text.find("\n### ", start + len(marker))
    return text[start:] if end < 0 else text[start:end]


def numbered_section(text: str, heading: str) -> str:
    marker = f"## {heading}"
    start = text.find(marker)
    if start < 0:
        return ""
    end = text.find("\n## ", start + len(marker))
    return text[start:] if end < 0 else text[start:end]


def check_contracts(texts: dict[str, str]) -> list[str]:
    failures: list[str] = []
    def require(name: str, text: str, *phrases: str) -> None:
        for phrase in phrases:
            if phrase not in text:
                failures.append(f"{name}: missing {phrase!r}")
    def reject(name: str, text: str, *phrases: str) -> None:
        for phrase in phrases:
            if phrase.lower() in text.lower():
                failures.append(f"{name}: contradictory {phrase!r}")

    epic = texts["epic"]
    positions = [epic.find(f"### `{stage}`") for stage in STAGES]
    if -1 in positions or positions != sorted(positions):
        failures.append("epic-order: stage blocks absent or reordered")
    classes = {"brainstorm_gate": "sonnet-class", "epic_brainstorm_fix": "sonnet-class", "spec_create": "sonnet-class", "plan_create": "opus-class", "tasks_create": "sonnet-class"}
    for stage in STAGES:
        body = section(epic, stage)
        require(f"stage-{stage}", body, "**Entry/input:**", "**Steps:**", "**Output:**", "**Approval/resume:**")
        if stage != "done":
            require(f"stage-{stage}", body, "stage brief/handoff contract")
    for stage, klass in classes.items():
        require(f"stage-class-{stage}", section(epic, stage), f"— `{klass}`")
    require("gate-transition", section(epic, "brainstorm_gate"), "skip goes to `spec_create`; needed goes to `epic_brainstorm`")
    require("brainstorm-output-transition", section(epic, "epic_brainstorm"), "**Output:** durable formatted decisions for", "`epic_brainstorm_fix`")
    require("brainstorm-fix-output-transition", section(epic, "epic_brainstorm_fix"), "**Output:** updated brief plus concise handoff\ncontext for `spec_create`")
    require("brainstorm-fix-application", section(epic, "epic_brainstorm_fix"), "shared decision application", "apply exactly those decisions", "preserve structure, exclusions, and deferrals")
    require("spec-approval", section(epic, "spec_create"), "obtain and durably record explicit approval of the current", "specification before `plan_create`")
    require("plan-transition", section(epic, "plan_create"), "review the created plan", "renew specification approval")
    require("task-ownership", section(epic, "tasks_create"), "create-only", "task defects belong to `overall_review`", "authorization to\nprepare tasks")
    require("review-approval", section(epic, "overall_review"), "explicit overall-review approval", "outcome and plan-phase briefing", "never apply an unresolved")
    require("stale-recovery", epic, "Resume from the earliest missing, stale, or inconsistent", "return\nto the earliest affected stage")
    require("reading-handoff", epic, "settled and non-obvious constraints **verbatim**", "cited authorities", "prior-stage handoff", "re-present unanswered owner questions")
    require("constitution", epic, "template-only content", "owner-derived principles", "apply them through the\ndetected constitution capability", "verify the resulting detected constitution is usable", "repair/verification fails")
    require("epic-capability-stop", epic, "If a required capability is unavailable, stop at the affected stage", "missing capabilities stop with an explicit report")
    require("reference-sizing", epic, "best_practices_spec_driven_development.md", "missing-install report", "substantive scope change", "documentation-initialization exception")
    require("briefings", section(epic, "spec_create"), "specification and\nclarification summary")
    require("shared-gate", epic, "shared `epic-brainstorming`", "shared `task-generation`")

    require("brainstorm", texts["brainstorm"], "NO_BRAINSTORM_NEEDED", "BRAINSTORM_NEEDED", "no more than three items", "exactly the recorded owner decisions", "ask in prose and end the turn")
    require("direct-route", texts["requirements"], "No intermediate\nspecification or plan is created.", "It does not require a plan or SpecKit.", "authorization to **prepare** tasks", "approval order is:", "best_practices_spec_driven_development.md")
    require("requirements-operational-brainstorm", numbered_section(texts["requirements"], "2. Resolve only material uncertainty"), "Invoke the shared `epic-brainstorming` mechanism", "exact gate result", "owner-owned one-at-a-time dialogue", "decision application", "Do not fork the shared mechanism")
    require("direct-adapter", texts["tasks"], "A direct adapter derives tasks", "does not\n  require a plan or SpecKit", "Do not require final task/implementation approval", "30%")
    require("epic-exception", texts["create"], "documentation-initialization exception", "`requirements-manager`")
    require("runtime-dependency", texts["requirements_doc"], "ask in prose and end the turn", "do not proceed past the owner-answer gate")

    coordinator = texts["coordinator"]
    require("origin-intake", coordinator, "For `requirements-manager` origin", "No specification, plan, or SpecKit prerequisite is required", "Ambiguous origin is a blocker")
    require("threshold", coordinator, "Up to three bounded implementation tasks may run locally", "current owner-selected model/class matches each task", "observed context capacity is adequate", "More than three implementation tasks require delegation", "including completed tasks", "exclude standalone review tasks", "Retain the recorded strategy on resume")
    require("batching", coordinator, "Internal dependencies, shared files, and phase/story headings do not require", "evidenced model-class changes, owner gates, context limits", "never\n   run implementation batches in parallel", "only asynchronously in the background")
    require("upstream-coherence", texts["tasks"], "coherent sequential work", "do not reorder dependencies or pad")
    require("sessions", coordinator, "observed context\n  headroom is adequate", "Inspect the failed run and tool invocation before retry")
    require("epic-intake", coordinator, "require specification, plan, tasks, both current approvals", "overall review evidence", "required SpecKit stage evidence")
    require("commit-review", coordinator, "Commit each task's verified changes as one focused commit", "No per-task reviews", "fresh independent\nfinal review", "full committed revision range")
    require("async-delegation", coordinator, "only asynchronously in the background", "never\n   run implementation batches in parallel")
    require("eligibility", coordinator, "Up to three bounded implementation tasks may run locally only", "current owner-selected model/class matches each task", "scope is clear", "observed context capacity is adequate")
    require("delegation-count", coordinator, "More than three implementation tasks require delegation", "including completed tasks", "exclude standalone review tasks")
    require("upstream-epic-coherence", section(epic, "plan_create"), "coherent consecutive\nsame-class work", "do not reorder dependencies or pad distant work")

    all_text = "\n".join(texts.values())
    reject("material-default", all_text, "recommended applied default", "apply an unresolved material default")
    for carrier in (texts["requirements"], texts["tasks"], coordinator):
        reject("mandatory-direct-plan", carrier, "mandatory plan for direct requirements", "direct requirements must have a plan")
    for carrier in (texts["tasks"], epic, coordinator):
        reject("automatic-batch-split", carrier, "automatically split at stage headings", "automatically split shared files", "automatically split internal dependencies")
    reject("unsafe-execution", coordinator, "parallel implementation batches are permitted", "foreground delegation is permitted", "regroup dependencies to fill batches", "batch commits replace task commits")
    for legacy in ("OpenCode", "resolve_epic.py", "named historical agents"):
        if legacy in all_text:
            failures.append(f"legacy: forbidden {legacy!r}")
    return failures


def load_texts(root: Path = ROOT) -> dict[str, str]:
    return {key: (root / path).read_text(encoding="utf-8") for key, path in PATHS.items()}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    failures = check_contracts(load_texts(args.root))
    if failures:
        print("requirements-manager workflow contract: FAIL")
        print("\n".join(f"- {failure}" for failure in failures))
        return 1
    print("requirements-manager workflow contract: PASS (operational static checks; no model calls)")
    return 0

if __name__ == "__main__":
    sys.exit(main())
