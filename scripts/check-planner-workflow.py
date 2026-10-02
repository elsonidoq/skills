#!/usr/bin/env python3
"""Operational instruction checks, not model-obedience or semantic completeness proof."""
import argparse
import hashlib
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
PATHS = {
    "planner": "skills/planner/SKILL.md",
    "tiny": "skills/tiny-spec/SKILL.md",
    "brainstorm": "skills/planning-brainstorming/SKILL.md",
    "approval": "skills/planner/references/approval-and-recovery.md",
    "tasks": "skills/task-generation/SKILL.md",
    "helper": "skills/delegating-architectural-planning/SKILL.md",
    "coordinator": "skills/coordinate-implementation/SKILL.md",
    "adoption": "skills/initialize-coherence/SKILL.md",
    "docs": "skills/initialize-coherence/SKILL.md",
    "memory": "skills/memory-handling/SKILL.md",
    "guidance": "docs/best_practices_spec_driven_development.md",
    "requirements": "REQUIREMENTS.md",
}
# Captured BEFORE replacement. Intake-only refactor must not weaken execution.
EXECUTION_SHA256 = "080e25e4365a2e88e65303a7a0b95e0c0d8ff7456d55099b7c96c89367b82751"


def section(text, heading):
    start = text.find(heading)
    if start < 0:
        return ""
    level = len(heading) - len(heading.lstrip("#")) or 2
    tail_start = start + len(heading)
    end = re.search(rf"\n#{{1,{level}}}\s", text[tail_start:])
    return text[start:] if end is None else text[start:tail_start + end.start()]


def stage(text, name):
    marker = f"**`{name}`"
    start = text.find(marker)
    if start < 0:
        return ""
    next_stage = text.find("\n", start)
    # Stages are numbered top-level list entries; nested paragraphs belong to the stage.
    end = re.search(r"\n\d+\. \*\*", text[next_stage:])
    return text[start:next_stage + end.start()] if end else section(text[start:], marker)


def check_contracts(texts):
    errors = []
    def require(label, text, *phrases):
        for phrase in phrases:
            if phrase not in text:
                errors.append(f"{label}: missing {phrase!r}")
    def reject(label, text, *phrases):
        for phrase in phrases:
            if phrase.lower() in text.lower():
                errors.append(f"{label}: contradictory {phrase!r}")

    p = texts["planner"]
    pre = section(p, "## Before selection:")
    require("choice", pre, "read-only until", "no source edits", "Session history",
            "BOTH options", "TinySpec → Tasks → Implement", "Specify → Plan → Tasks",
            "call `ask_user` and STOP", "Either choice is valid", "preparation only",
            "resolved uncertainty alone does not reroute")
    continuation = section(p, "## Approval-driven continuation")
    require("continuation", continuation, "immediately start the next authorized phase",
            "Do not end the turn merely to report approval", "dispatch it",
            "explicitly requested planning-only", "older preparation-only approval")
    handoff = section(p, "## Handoff, not execution")
    require("final-continuation", handoff,
            "automatically invoke `coordinate-implementation`",
            "in the same session", "explicitly requested planning-only",
            "Do not stop at a readiness summary", "precise blocker")
    reject("final-continuation", handoff, "If execution was requested")
    require("shared-invocation", pre,
            "Invoke `planning-brainstorming` in preselection mode",
            "readiness target “informed scope assessment.”",
            "conduct required owner dialogue yourself", "one material item at a time")
    production = section(p, "## Selected production and stage handoffs")
    require("shared-application", production,
            "Apply recorded decisions through the shared mechanism inside selected bounds only.")
    require("discovery", p, "positive and negative claims", "already satisfied", "no task needed",
            "UNVERIFIED", "explicit owner deferral", "Do not invent a beneficiary",
            "separately scheduled mechanical work", "missing required memory stops".capitalize(),
            "missing-install report", "question: UNAVAILABLE", "inspect failures before",
            "Standard-only SpecKit/reviewer/constitution checks happen after Standard")
    require("handoff", p, "constraints **verbatim**", "prior-stage handoff", "Resume originating",
            "Re-present unanswered questions", "selected depth", "current content/revision evidence",
            "Explicit approved implementation scope", "Coordinator alone")
    tiny = section(p, "### TinySpec path")
    require("tiny-flow", tiny, "**Source creation — `sonnet-class`", "**Tasks — `sonnet-class`",
            "invoke `tiny-spec`", "invoke `task-generation` direct adapter",
            "Create separate tasks", "No independent planning", "**Combined approval:**",
            "BEFORE `ask_user`", "Denial returns to review", "No SpecKit prerequisite",
            "standalone\n   TinySpec approval", "Record\n   fixes",
            "brief bullet-list executive summary", "immediately proceed to handoff")
    std = section(p, "### Standard path")
    positions = [std.find(f"**`{s}`") for s in ("spec_create", "plan_create", "tasks_create", "overall_review")]
    if -1 in positions or positions != sorted(positions):
        errors.append("standard-order: missing/reordered operational stages")
    require("standard-preflight", std, "constitution", "template-only", "owner-derived",
            "verify repaired output", "Missing repair capability", "Do not reopen",
            "never install, simulate slash commands", "Required absent\ncapability stops")
    spec = stage(std, "spec_create")
    require("spec", spec, "— `sonnet-class`", "Clarify only when requested or required",
            "BEFORE\n   `ask_user`", "specification approval before `plan_create`",
            "bullet-list executive brief", "immediately continue to `plan_create`")
    plan = stage(std, "plan_create")
    require("plan", plan, "— `opus-class`", "same-session pass", "review/fix the specification",
            "create one plan", "review/fix the produced plan", "ENTIRE pass",
            "do not create the plan again", "Only when no adapter is invoked",
            "renewed specification approval", "new executive brief", "do not reorder".capitalize())
    tasks = stage(std, "tasks_create")
    require("task-stage", tasks, "— `sonnet-class`", "authorization to prepare tasks",
            "create-only", "no producer self-review/correction", "`overall_review`")
    review = stage(std, "overall_review")
    require("review", review, "independent owner-selected reviewer", "observed analysis",
            "never apply unresolved material defaults", "renew affected approvals",
            "BEFORE `ask_user`", "plan-phase implications", "Missing independent reviewer",
            "bullet-list executive", "immediately proceed to handoff")
    b = texts["brainstorm"]
    require("brainstorm", b, "NO_BRAINSTORM_NEEDED", "BRAINSTORM_NEEDED", "no more than three items",
            "one material item", "recorded owner decisions", "preselection", "read-only",
            "session history", "Only in selected-production", "owner's rationale", "sonnet-class")
    require("tiny-source", texts["tiny"], "explicit TinySpec selection/preparation authorization",
            "Context/outcome", "Scope", "Decisions/constraints", "Approach", "Acceptance/validation",
            "Risks/dependencies/notes", "Do not embed an implementation task checklist",
            "separate task file is mandatory", "No SpecKit prerequisite", "one combined approval")
    a = texts["approval"]
    require("approval", a, "EVERY artifact-approval", "before calling `ask_user`",
            "only in tool arguments", "Intended outcome", "Exclusions", "Important settled decisions",
            "Risks", "Actual review/validation", "Exact artifacts/current content",
            "withhold", "cancelled", "renew", "external", "recursive self-hashes",
            "Approved specification content changes", "Plan/tasks change after final approval",
            "4–6 short bullets", "name the next", "immediately continue to the next authorized phase",
            "same session unless the owner explicitly requested planning-only")
    require("legacy", a, "inside tasks", "approved spec awaiting plan", "earliest affected Standard",
            "Other documented producer", "Ambiguous/conflicting origin", "retired skills",
            "Missing runtime capabilities")
    t = texts["tasks"]
    require("task-contract", t, "SpecKit adapter", "direct adapter", "separate source and tasks file",
            "authorization to\n**prepare** tasks", "30%", "Number in execution order from T001",
            "explicit `Depends`", "earlier task", "implicit dependencies", "manually inspect",
            "coherent sequential work", "do not reorder dependencies or pad", "lockstep documentation")
    require("adapter", texts["helper"], "Planner Standard adapter", "`planner`", "same-session pass",
            "do not direct it to create the plan again", "standalone local\nfallback")
    c = texts["coordinator"]
    require("intake", c, "Standard depth", "both current approvals", "required SpecKit stage evidence",
            "TinySpec depth", "separate TinySpec/source and tasks", "legacy `requirements-manager`",
            "embedded in tasks", "partially planned legacy work", "For other documented origins",
            "Ambiguous origin is a blocker", "Missing/conflicting depth", "Installation alone",
            "external", "approval/recovery mapping")
    marker = "## Execution Capability Preflight"
    body = c[c.index(marker):] if marker in c else ""
    if hashlib.sha256(body.encode()).hexdigest() != EXECUTION_SHA256:
        errors.append("execution-freeze: coordinator execution differs from pre-refactor baseline")
    require("adoption", texts["adoption"], "bounded refresh", "marked", "every unrelated byte",
            "dirty", "concurrently", "Before calling `ask_user`", "memory store and index")
    require("docs", texts["docs"], "fresh read-only investigation sub-agent", "database-schema", "empty/template shells",
            "not substantive implementation authorization", "Before calling `ask_user`",
            "explicit TinySpec/Standard choice", "dirty-target/concurrent-edit")
    require("memory", texts["memory"], "Read the whole index first", "index → matching entries",
            "project-associated", "Never treat a global")
    require("guidance", texts["guidance"], "reasoning complexity and coordination cost",
            "Always present both paths", "not a routing rule")
    reject("obsolete-sizing", texts["guidance"], "all three** conditions", "At least eight expected tasks")
    all_text = "\n".join(texts.values())
    reject("material-default", all_text, "apply an unresolved material default", "recommended applied default")
    for key in ("planner", "tasks", "coordinator"):
        reject("unsafe-policy", texts[key], "parallel implementation batches are permitted",
               "foreground delegation is permitted", "batch commits replace task commits",
               "automatically split at stage headings", "automatically split shared files",
               "automatically split internal dependencies", "regroup dependencies to fill batches",
               "direct requirements must have a plan", "mandatory plan for direct requirements")
    reject("silent-routing", p, "automatically choose TinySpec", "automatically choose Standard")
    return errors


def load_texts(root=ROOT):
    texts = {key: (root / path).read_text() for key, path in PATHS.items()}
    # Check operational carriers, not incidental mentions in a combined summary.
    for key, stages in {
        "adoption": ("Preflight", "Approval", "Adoption"),
        "docs": ("Preflight", "Discovery", "Investigation", "Approval", "Documentation", "Validation"),
    }.items():
        texts[key] = "\n".join(section(texts[key], f"## {name}") for name in stages)
    return texts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    try:
        errors = check_contracts(load_texts(args.root))
    except (OSError, ValueError) as exc:
        errors = [str(exc)]
    for error in errors:
        print(error)
    print(f"planner workflow: {'FAIL' if errors else 'PASS'} (static instructions only)")
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
