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
    "research": "skills/planner/references/dependency-research.md",
    "coordination": "skills/memory-handling/references/project-coordination.md",
}
# Deliberately updated for approved coordination-memory T003–T004: additive routing,
# factual evidence checkpoints and exact approval-controlled reflection. Original
# execution lines/order and safety mutations retain the proportionality correction.
EXECUTION_SHA256 = "89cbd7fa77bcb098d39ff9dcc9c17bc4892de2a248a45dfa25aa1d460e0b4660"


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
    validation = section(p, "## Proportionate validation")
    require("validation-focused", validation,
            "actual changed seam", "concrete failure", "lowest validation layer",
            "smallest sufficient check", "selected result or argument reaches the intended consumer",
            "Do not automatically add\nexhaustive matrices, fault injection, new test infrastructure or broad suites",
            "necessary integration layer", "expected verification effort qualitatively",
            "No universal deadlines", "not a new task schema")
    require("validation-risk", validation,
            "Genuine schema, security or durability", "migration, authorization or persistence",
            "small diffs alone never justify weakening safety evidence")
    require("validation-authority", validation,
            "Optional checks are not acceptance blockers", "gate\nis not a waiver",
            "Never drop an owner-required check or approved\nsafety criterion without explicit authority",
            "mandated independent reviews", "owner's selected planning depth")
    require("validation-reuse", validation,
            "Reuse valid unchanged evidence", "scope, revisions and environment",
            "Avoid repeated historical intake", "small causal\nsteps", "actually blocks")
    require("validation-tasks", section(t, "## Task contract"),
            "smallest sufficient check", "changed seam's concrete failure",
            "REQUIRED checks", "optional hardening/broader regression", "separately gated",
            "Optional checks do not become blockers", "owner-required criteria",
            "expected verification\neffort", "valid unchanged evidence")
    require("validation-execution", section(c, "## Execute and Integrate"),
            "REQUIRED checks remain required", "optional hardening/broader regression is not a blocker",
            "explicit permissions", "leave acceptance blocked", "renewed approval",
            "Reuse valid unchanged evidence", "lowest sufficient layer")
    require("validation-timeout", section(c, "## Select Execution Capability"),
            "checkpoint early", "After a\n  timeout, inspect", "retain valid completed\n  evidence",
            "narrow the remaining step instead of restarting the entire batch",
            "timeout alone is not retry authority")
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

    # Research obligations must occur in their operational carriers, not summaries.
    require("research-planner-link", section(p, "## Discovery and capability boundary"),
            "[dependency research contract](references/dependency-research.md)",
            "inspect repository\nguidance and dependency/version evidence first")
    require("research-preselection", pre, "no dependency docs,\nsource, plan or decisions may be persisted",
            "Carry findings in session until selection")
    reject("research-preselection", pre, "Persist dependency docs before selection")
    require("research-review", production, "persist reusable guidance during authorized production before readiness",
            "both direct/standalone consumers", "version/provenance", "proportional reuse/targeted refresh",
            "supporting spans → constraints → observable checks", "capability/permission gaps",
            "stop affected design rather than default to model recollection", "never automatically defer or fabricate evidence")
    require("research-tiny-handoff", tiny, "Supply the shared research contract", "bounded\n   canonical-owner/discovery writes before consequential approach decisions",
            "Apply the dependency evidence/permission review above before combined approval")
    require("research-spec", spec, "apply the shared research contract before consequential dependency constraints\n   are chosen",
            "carry evidence-backed constraints/checks, not invented dependency rules")
    require("research-plan", plan, "Before consequential plan decisions, complete required shared-contract research",
            "For helper invocation or the direct Standard pass", "canonical research-document and necessary discovery-link destinations",
            "observed allowed changes and prohibited operations, with explicit bounded permission\n   in addition to detected SpecKit artifacts",
            "Do not grant arbitrary documentation edits\n   or code writes", "missing required evidence/authority stops")
    require("research-standard-review", review, "direct Standard\n   pass and helper-managed/standalone contract coverage")
    t_research = section(texts["tiny"], "## Dependency evidence before approach decisions")
    require("research-tiny", t_research, "[dependency research contract](../planner/references/dependency-research.md)",
            "before consequential dependency approach decisions", "Verify the reference is readable",
            "reuse adequate applicable guidance", "Refresh only version-sensitive/stale/conflicting/missing portions",
            "Direct/standalone entry verifies equivalent TinySpec selection/preparation authority",
            "bounded canonical technical-owner/discovery-link writes", "during authorized production before readiness",
            "required insufficient evidence cannot default to recollection", "return exact gaps, affected decisions",
            "impact, allowed bounds and outstanding validation, never automatic deferral")
    source_contract = section(texts["tiny"], "## Compact source contract")
    require("research-tiny-traceability", source_contract, "Classify documented\n  recommendations, repository-derived decisions/rationale and assumptions",
            "Trace source recommendation/local evidence → compact implementation\n  constraint → observable acceptance/check")
    research_pos = texts["tiny"].find("## Dependency evidence before approach decisions")
    approach_pos = texts["tiny"].find("## Compact source contract")
    if research_pos < 0 or approach_pos < 0 or research_pos > approach_pos:
        errors.append("research-order: TinySpec research must precede compact approach production")
    h_pre = section(texts["helper"], "## Preflight")
    require("research-helper", h_pre, "[dependency research contract](../planner/references/dependency-research.md)",
            "before consequential architecture/plan decisions", "verify it is readable",
            "Standalone entry verifies equivalent Standard planning/preparation authority",
            "bounded\ncanonical-owner/discovery writes", "No recollection fallback or automatic deferral",
            "returns exact missing evidence, affected decisions and needed authority",
            "standalone local fallback cannot bypass required research",
            "Research-driven approved-specification changes require renewed approval")
    require("research-helper-adapter", section(texts["helper"], "## Planner Standard adapter contract"),
            "explicit bounded documentation permission", "absence is not implied authority")
    h_boundary = section(texts["helper"], "## Planner Boundary")
    require("research-boundary", h_boundary, "only explicit bounded\npermission permits canonical research-document and necessary discovery-link writes",
            "observed destinations with specified allowed changes and prohibited operations",
            "No arbitrary documentation edits or product code writes", "missing required authority stops",
            "supporting source spans → implementation constraints → observable checks")
    reject("research-boundary", h_boundary, "Arbitrary documentation edits are permitted")
    r = texts.get("research", "")
    if not r:
        errors.append("research-reference: required shared carrier missing or empty")
    require("research-discovery", section(r, "## Discover, trigger and reuse"),
            "Read repository instructions, dependency declarations/lockfiles", "installed/targeted dependency and version/range",
            "First repository use, insufficient guidance", "Trivial use can skip new internet\nresearch with a brief reason",
            "reuse guidance\nwith cited evidence", "version applicability", "refresh only\nthose portions",
            "A recent date alone proves neither applicability nor completeness")
    require("research-evidence", section(r, "## Obtain sufficient evidence"),
            "verify actually usable, permitted", "Tool names/configuration\nalone are not capability evidence",
            "Adequate local guidance can satisfy evidence\nwithout a new search call",
            "official documentation, official guides/\nexamples/repositories and maintainers first",
            "Label newer-version differences", "Inspect meaningful supporting sections",
            "not just\nsearch snippets or URL lists", "invent universal batching/flush rules")
    require("research-traceability", section(r, "## Classify and translate"),
            "**Documented recommendation:** inspected supporting source section/claim, primary\n  URL and applicable version",
            "**Repository-derived decision:** local evidence, resulting decision and rationale",
            "**Assumption:** uncertainty and a defined validation check",
            "Unsupported snippets, uninspected URLs, uncertain statements and generic model\nrecollection cannot satisfy required source evidence",
            "recommendation/local evidence → derived decision/implementation constraint → observable\nvalidation",
            "Material unresolved choices return to the existing owner gate")
    require("research-persistence", section(r, "## Persist within verified authority"),
            "Preselection inspection/research is read-only", "During authorized selected\nproduction, persist reusable guidance before readiness",
            "repository technical owner and its discoverability index", "verify/obtain bounded authority",
            "Re-read each target immediately before", "preserve unrelated content; stop on concurrent overlap",
            "dependency/version or range, applicable practices and\npitfalls, repository-derived decisions/rationale",
            "primary URLs tied to supporting\nclaims, research date for evolving guidance", "uncertainty/validation needs",
            "explicit bounded permission **in addition to** detected SpecKit artifacts",
            "Standalone/direct entry verifies equivalent selection/preparation and write authority")
    failure = section(r, "## Safe failure and return")
    require("research-failure", failure, "required tools, usable sources, version evidence or write authority",
            "stop affected consequential design and return the exact gap", "affected\ndecisions and evidence/authority needed",
            "No generic-knowledge fallback, fabricated\nsources, automatic deferral, installation or premature readiness",
            "explicit bounded owner deferral through existing gates", "Record impact, allowed bounds and outstanding validation",
            "not fabricate evidence or waive unrelated gates")
    reject("research-failure", failure, "Use model recollection when required research is unavailable")
    # Coordination boundaries belong in operational phases, never summary mentions.
    link = "[project coordination contract](../memory-handling/references/project-coordination.md)"
    discovery = section(p, "## Discovery and capability boundary")
    require("coordination-early", discovery, link, "during initial understanding",
            "`GUIDELINES.md` before brainstorming, scope assessment and depth choice",
            "no invented knowledge, writes or new adoption gate",
            "distinctly from required gotcha-memory stops",
            "Ordinary planning does not read", "index-first relevant-only retrieval",
            "no match retains uncertainty")
    require("coordination-handoff", production,
            "Carry exact applicable coordination guideline constraints and evidence references",
            "both TinySpec and Standard stage briefs", "source observables/acceptance",
            "task dependencies, checkpoints, verification and coordinator handoff",
            "Memory cannot override source requirements or owner authority",
            "absence requires no migration and changes no class/share/approval rule")
    require("coordination-tiny", section(texts["tiny"], "## Inputs and preflight"),
            link, "including direct/standalone entry", "not index/history by default",
            "Carry exact applicable constraints and evidence references",
            "acceptance/verification", "required gotcha-memory stops",
            "index-first relevant-only retrieval", "retains uncertainty on no match")
    require("coordination-tasks", section(t, "## Preconditions and adapters"),
            link, "including direct entry without planner", "task dependencies, delegation",
            "checkpoints and REQUIRED verification/acceptance", "source/owner authority",
            "required gotcha-memory stops remain distinct", "No default index/history intake",
            "index-first relevant-only retrieval", "does not alter classes, share or approval rules")
    require("coordination-memory", section(texts["memory"], "## Optional project coordination memory"),
            "[project coordination contract](references/project-coordination.md)",
            "Required gotcha-memory rules above remain", "never go into this gotcha index")
    require("coordination-intake", section(c, "## Load and Verify"), link,
            "exact applicable constraints/evidence references", "bounded evidence",
            "Without association/write authority", "never\nsilently initialize",
            "No default evidence-history intake")
    checkpoint = section(c, "### Coordination evidence checkpoint")
    if not (0 <= c.find("## Execute and Integrate") < c.find("### Coordination evidence checkpoint")
            < c.find("## Review and Acceptance")):
        errors.append("coordination-checkpoint: checkpoint must be inside execution before review")
        checkpoint = ""
    require("coordination-checkpoint", checkpoint,
            "At each task/attempt checkpoint", "failed, blocked or partial work and manual/user",
            "task/type, areas/tags", "approved class", "role/model/reasoning effort (or `unknown`)",
            "individual attempt/check results, reviewer findings, inspected failure cause",
            "escalation outcomes, surprises and manual findings", "Unknown is not success",
            "reuse on resume, never overwrite another run", "separate summary/task records",
            "before refreshing", "after every evidence write", "no duplicate rows",
            "reconcile interrupted record/index updates", "retaining existing runs",
            "never grants permission to mutate guidelines", "Without association/write authority")
    capability = section(c, "## Select Execution Capability")
    require("coordination-routing", capability,
            "usable owner-selected options", "Low favors a cheaper",
            "strong executable acceptance oracle", "stronger verification/review",
            "not forced opus", "reclassification or share-gate bypass",
            "Never silently\nreplace selected models, weaken approved classes",
            "inspect the child run and failed invocation first", "Preserve valid",
            "unrelated workspace changes", "architecture and authority permit",
            "verified stronger capability and owner-selection gates",
            "Unknown cause", "unestablished clean state stops", "Record both attempts")
    reflection = section(c, "## Coordination reflection and guideline approval")
    if not (0 <= c.find("## Review and Acceptance") < c.find("## Coordination reflection and guideline approval")
            < c.find("## Maintaining this contract")):
        errors.append("coordination-approval: reflection must follow review before closeout")
        reflection = ""
    require("coordination-reflection", reflection,
            "After implementation/verification and fresh independent review, or at a blocked pause",
            "nine reflection questions", "project-specific versus general",
            "reusable versus incidental", "reinforcement; contradiction",
            "guideline support versus evidence-only", "delegation lessons; manual validation",
            "surprises needing qualification/more evidence", "insufficient and conflicting",
            "index-first and\nrelevant-only", "separately from `REFLECTION.md`",
            "add/refine/supersede/remove", "supporting/contradicting pointers",
            "no update\nproposed", "not a universal ban or permanent routing rule")
    require("coordination-approval", reflection,
            "executive brief and exact candidate diff", "existing `ask_user`",
            "accept, edit, reject, or add", "approval is not guideline approval",
            "Explicit accepted/edited/added resulting content", "comparable baseline/proposed content evidence",
            "Pending, unavailable, cancelled or ambiguous answers leave guidelines unchanged",
            "Rejection leaves guideline bytes identical", "rejection disposition",
            "Immediately before applying only approved changes, re-read",
            "compare with the approved baseline: concurrent drift stops application",
            "renewed review/approval", "Re-check relevant guidance after",
            "Report implementation/feature acceptance separately")
    q = texts.get("coordination", "")
    if not q:
        errors.append("coordination-reference: required shared carrier missing or empty")
    require("coordination-association", section(q, "## Association and optional discovery"),
            "project instructions or documented project configuration", "respect declared equivalent layouts",
            "No global-store fallback or guessed association", "no new adoption",
            "declared missing/unreadable", "required-memory policy", "Discovery is read-only",
            "never a discovery", "bounded owner approval", "preserve existing content")
    require("coordination-guidelines", section(q, "## Compact guidelines"),
            "before brainstorming", "exact constraints", "scope/trigger", "qualitative",
            "Owner-supplied entries name their origin", "Preserve uncertainty and contrary",
            "`REFLECTION.md` is not planner guidance")
    require("coordination-selective", section(q, "## Selective historical retrieval"),
            "Ordinary planning reads guidelines, not", "justified only",
            "ambiguous/tentative/conflicting", "user request", "new contradictory",
            "read the compact evidence index first", "only those selected records",
            "Do not recursively", "Unrelated records\nstay unread",
            "no relevant evidence means proceed retaining uncertainty")
    require("coordination-evidence", section(q, "## Separate factual evidence"),
            "SUMMARY.md", "T001.md", "T002.md", "REFLECTION.md",
            "Reuse that ID on resume", "never\noverwrite another run",
            "append-oriented", "without erasing observations or prior runs",
            "verified write authority", "Without association/write authority",
            "otherwise `unknown`", "failed, blocked and partial", "unknown outcomes are explicitly unknown",
            "sensitive payloads", "run record before its index entry", "Every new evidence write refreshes",
            "Keep one row per run", "Reconcile an\ninterrupted record/index update on resume")
    require("coordination-synthesis", section(q, "## Conservative reflection"),
            "independent review", "evidence-only", "insufficient evidence and conflicting",
            "without numerical confidence", "One failure", "never a universal",
            "supporting\nand contradicting pointers", "no update proposed", "never automatic mutation")
    require("coordination-exact-write", section(q, "## Exact guideline approval"),
            "executive brief and exact candidate diff before", "accept, edit, reject, or add",
            "Implementation approval grants no guideline", "comparable baseline/proposed",
            "resulting content must be explicitly approved", "Pending, unavailable, cancelled or ambiguous",
            "Rejection leaves guidelines byte-identical", "re-read\n`GUIDELINES.md`",
            "compare with the approved baseline", "drift stops", "renewed review/approval",
            "Re-check", "acceptance separately")
    require("coordination-class", section(q, "## Class-compatible routing experiment"),
            "compatible with the approved class", "strong executable acceptance oracle",
            "owner-selection gates", "Inspect the failed child run and invocation",
            "unknown cause", "Record both attempts", "not provider names or permanent rules")
    for key in ("planner", "tiny", "tasks", "coordinator", "coordination"):
        reject("coordination-unsafe", texts.get(key, ""),
               "Always read the entire evidence directory", "Read coordination history on every request",
               "Automatically apply guideline proposals", "Implementation approval authorizes guideline writes",
               "Ignore concurrent guideline drift", "Automatically downgrade approved classes",
               "Retry without inspecting the failed invocation", "One failure permanently bans a model")
    return errors


def load_texts(root=ROOT):
    research_path = root / PATHS["research"]
    if not research_path.is_file():
        raise ValueError("research-reference: required shared reference unavailable")
    coordination_path = root / PATHS["coordination"]
    if not coordination_path.is_file():
        raise ValueError("coordination-reference: required shared reference unavailable")
    texts = {key: (root / path).read_text() for key, path in PATHS.items()}
    for key in ("memory", "planner", "tiny", "tasks", "coordinator"):
        destinations = re.findall(r"\[project coordination contract\]\(([^)]+)\)", texts[key])
        if len(destinations) != 1 or (root / PATHS[key]).parent.joinpath(destinations[0]).resolve() != coordination_path.resolve():
            raise ValueError(f"coordination-reference: {key} shared link missing/unresolvable or wrong owner")
    for key in ("planner", "tiny", "helper"):
        destinations = re.findall(r"\[dependency research contract\]\(([^)]+)\)", texts[key])
        if len(destinations) != 1 or (root / PATHS[key]).parent.joinpath(destinations[0]).resolve() != research_path.resolve():
            raise ValueError(f"research-reference: {key} shared link missing/unresolvable or wrong owner")
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
