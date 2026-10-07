#!/usr/bin/env python3
"""Operational instruction checks, not model-obedience or semantic completeness proof."""
import argparse
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
    "risk": "skills/planner/references/early-risk-reduction.md",
    "research": "skills/planner/references/dependency-research.md",
    "coordination": "skills/memory-handling/references/project-coordination.md",
    "routing": "skills/coordinate-implementation/references/batch-routing.md",
}


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
    require("tiny-flow", tiny, "**Source creation — shared routing selection", "**Tasks — shared routing selection",
            "**Review — planner-owned, shared routing selection",
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
    require("spec", spec, "— shared routing selection",  "Clarify only when requested or required",
            "BEFORE\n   `ask_user`", "specification approval before `plan_create`",
            "bullet-list executive brief", "immediately continue to `plan_create`")
    plan = stage(std, "plan_create")
    require("plan", plan, "— Sol/medium",  "same-session pass", "review/fix the specification",
            "create one plan", "review/fix the produced plan", "ENTIRE pass",
            "do not create the plan again", "Only when no adapter is invoked",
            "renewed specification approval", "new executive brief", "do not reorder".capitalize())
    tasks = stage(std, "tasks_create")
    require("task-stage", tasks, "— shared routing selection",  "authorization to prepare tasks",
            "create-only", "no producer self-review/correction", "`overall_review`")
    review = stage(std, "overall_review")
    require("review", review, "independent owner-selected reviewer", "use shared routing selection", "observed analysis",
            "never apply unresolved material defaults", "renew affected approvals",
            "BEFORE `ask_user`", "plan-phase implications", "Missing independent reviewer",
            "bullet-list executive", "immediately proceed to handoff")
    b = texts["brainstorm"]
    require("brainstorm", b, "NO_BRAINSTORM_NEEDED", "BRAINSTORM_NEEDED", "no more than three items",
            "one material item", "recorded owner decisions", "preselection", "read-only",
            "session history", "Only in selected-production", "owner's rationale")
    # Routing obligations must reach operational consumers, not a summary keyword.
    routing_link = "[qualified seed rubric](../coordinate-implementation/references/batch-routing.md)"
    selection = section(p, "## Shared routing selection")
    require("planning-selection", selection, routing_link,
            "all six applicable factors", "weakest verification blind spot",
            "Family rationale", "Effort rationale", "proposed versus owner-selected",
            "one exact selected profile unchanged", "Missing owner selection or support stops",
            "settings or agent defaults overriding selection stop dispatch",
            "selected versus observed separately", "unknown actual model or effort stays unknown",
            "assignment and dispatch", "permissions, tools, callable binding and supported effort",
            "Implementation-only batching, task-count and REQUIRED-item rules are not planning prerequisites")
    require("planning-preflight", section(p, "## Discovery and capability boundary"),
            "owner-selected exact profiles", "Apply the shared routing selection")
    for key, heading in (("brainstorm", "## Capability preflight"), ("helper", "## Preflight")):
        carrier = section(texts[key], heading)
        require("routing-" + key, carrier, routing_link, "all six",
                "weakest verification blind spot", "effort independently", "one exact",
                "owner-selected profile", "permissions, tools", "callable binding and supported effort",
                "assignment", "dispatch", "selected binding/effort", "unchanged",
                "missing selection/support", "settings/default", "stops", "never silently substitutes",
                "proposed", "selected and observed separately", "unknown actual", "stays unknown",
                "Implementation-only batching, task-count and REQUIRED-item rules")
    require("routing-brainstorm-assessment", section(b, "## 1. Gate assessment"),
            "using the preflight's shared routing selection")
    require("routing-brainstorm-application", section(b, "## 3. Apply decisions"),
            "with the preflight's\nshared routing selection")
    adapter = section(texts["helper"], "## Planner Standard adapter contract")
    for label, carrier in (("plan-profile", plan), ("adapter-profile", adapter)):
        require(label, carrier, "Sol family with exactly **medium** supported effort", "ENTIRE",
                "direct/helper pass", "callable Sol binding and medium support",
                "assignment and dispatch", "selected", "unchanged", "brief/dispatch",
                "Unavailable Sol/medium stops", "precise", "binding/support gap",
                "no substitution, settings/default override or standalone",
                "helper fallback", "may bypass this rule", "observed binding/effort separately",
                "unknown stays unknown")
        reject(label, carrier, "fallback is permitted", "use another family", "use an agent default",
               "standalone selection supersedes", "substitute an available profile")
    require("plan-profile", plan, "for the ENTIRE direct/helper pass")
    require("adapter-profile", adapter, "for the ENTIRE\nStandard direct/helper pass", "one same-session pass", "review/fix the approved specification",
            "once to create the plan", "review/fix the produced plan", "do not direct it to create the plan again",
            "policies below do not apply to this adapter invocation")
    require("routing-helper", section(texts["helper"], "## Preflight"),
            "standalone selection cannot override a manager-governed\nStandard invocation's Sol/medium exception")
    routing = texts.get("routing", "")
    require("routing-applicability", section(routing, "## Applicability to planning/advisory invocations"),
            "same six-factor assessment", "own permissions and output verification",
            "Implementation-only batching, task-count and REQUIRED-item\nrules do not become planning prerequisites",
            "cannot bypass a manager-governed Standard rule")
    for key in ("planner", "brainstorm", "helper"):
        reject("obsolete-planning-class", texts[key], "sonnet-class", "opus-class")
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
    require("batch-handoff", production, "stable task-local REQUIRED", "qualified seed rubric", "canonical research", "not implementation-task assignments")
    require("batch-tiny", tiny, "verification item completeness")
    require("batch-standard", review, "verification item completeness")
    require("batch-legacy", a, "inadequate REQUIRED contracts", "producing review/approval gate", "renewed affected approval")
    require("batch-helper", texts["helper"], "not model-class labeling", "applicable guidelines")
    require("batch-source", texts["tiny"], "stable task-local REQUIRED")
    require("batch-brainstorm", texts["brainstorm"], "not implementation-task assignments")
    t = texts["tasks"]
    require("task-contract", t, "SpecKit adapter", "direct adapter", "separate source and tasks file",
            "authorization to\n**prepare** tasks", "stable task-local references", "Number in execution order from T001",
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
    require("execution-checkpoints", section(c, "## Execute and Integrate"),
            "Commit each task's verified changes as one focused commit", "separate evidence-only checkpoint",
            "failed recovery stops dispatch", "coordinator independently", "no routine coordinator pause")
    require("execution-sequential", section(c, "## Build the Execution Graph"),
            "only asynchronously in the background", "never\n   run implementation batches in parallel",
            "Never pull\n   a distant producer forward or reorder a prerequisite", "commits each task separately")
    require("execution-selection", section(c, "## Select Execution Capability"),
            "one exact profile", "proposed versus owner-selected", "Family rationale", "Effort rationale",
            "at assignment and again at dispatch", "supported effort", "callable binding",
            "Copy the owner-selected binding and effort unchanged", "no silent settings/agent override",
            "actual model or effort remains unknown")
    require("execution-strategy", section(c, "## Select Execution Strategy"),
            "Up to three bounded implementation tasks", "More than three implementation tasks require delegation",
            "Retain the recorded strategy on resume", "current owner-selected exact profile fits")
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
            "ensure the mandatory project-local store exists",
            "initialize missing files, notify the user and commit only initialization files",
            "without a setup approval gate", "Creation/commit failures stop",
            "required gotcha-memory stops remain", "no invented project knowledge",
            "Ordinary planning does not read", "index-first relevant-only retrieval",
            "retains uncertainty")
    require("coordination-handoff", production,
            "Carry exact applicable coordination guideline constraints and evidence references",
            "both TinySpec and Standard stage briefs", "source observables/acceptance",
            "task dependencies, checkpoints, verification and coordinator handoff",
            "Memory cannot override source requirements or owner authority",
            "absence requires no migration and changes no approval rule")
    require("coordination-tiny", section(texts["tiny"], "## Inputs and preflight"),
            link, "including direct/standalone entry", "not index/history by default",
            "ensure the mandatory project-local store", "initialize missing files, notify the user",
            "commit only initialization", "without a setup approval gate",
            "Carry exact applicable constraints and evidence references",
            "acceptance/verification", "required gotcha-memory stops",
            "index-first relevant-only retrieval", "retains uncertainty on no match")
    require("coordination-tasks", section(t, "## Preconditions and adapters"),
            link, "including direct entry without planner", "dependencies, delegation briefs",
            "ensure the mandatory project-local", "initialize missing files, notify the user",
            "initialization files before proceeding", "without a setup approval gate",
            "checkpoints and REQUIRED verification/acceptance", "source/owner authority",
            "required gotcha-memory stops remain distinct", "No default index/history intake",
            "index-first relevant-only", "does not alter approval rules")
    require("coordination-memory", section(texts["memory"], "## Required project coordination memory"),
            "[project coordination contract](references/project-coordination.md)",
            "Required gotcha-memory rules above remain", "never go into this gotcha index",
            "initialize missing files, notify the user", "commit only initialization files",
            "no separate setup approval or handoff-only alternative")
    require("coordination-intake", section(c, "## Load and Verify"), link,
            "applicable constraints/evidence references", "mandatory project-local store exists",
            "initialize missing files, notify the user and commit only initialization files",
            "without a setup approval gate", "never a handoff-only alternative",
            "No default evidence-history intake")
    checkpoint = section(c, "### Coordination evidence checkpoint")
    if not (0 <= c.find("## Execute and Integrate") < c.find("### Coordination evidence checkpoint")
            < c.find("## Review and Acceptance")):
        errors.append("coordination-checkpoint: checkpoint must be inside execution before review")
        checkpoint = ""
    require("coordination-checkpoint", checkpoint,
            "At each task/attempt checkpoint", "failed, blocked or partial work and manual/user",
            "task/type, areas/tags", "exact selected and observed profile", "binding plus effort or unknown",
            "contract strength, first/final outcome", "diagnosis, repair/escalation",
            "item check/checkpoint references", "individual check results, reviewer findings",
            "accepted, partial, escalated", "`model_capability`", "`planning_or_spec_gap`",
            "`verification_contract_gap`", "`batching_error`", "`environment_or_tooling`",
            "`external_dependency`", "`unknown`", "Non-model causes never count as capability failure",
            "weak or invalidated successes", "An unknown observation is never overwritten by selection",
            "Unknown is not success",
            "reuse on resume, never overwrite another run", "sole evidence file for each new run",
            "before refreshing its index row after every evidence", "no duplicate rows",
            "reconcile interrupted summary/index updates", "retaining prior attempts",
            "never grants permission to mutate guidelines", "initialized project-local store",
            "Evidence-write failures stop", "never a no-write fallback")
    capability = section(c, "## Select Execution Capability")
    require("coordination-routing", capability,
            "usable owner-selected", "independent family/effort rationales",
            "Strong contracts and cheap recovery", "missing requirements or permissions",
            "Never silently replace selected models",
            "Inspect the failed child run, invocation, partial commits and check evidence", "Preserve valid",
            "unrelated\nchanges and prior attempt evidence", "affected dependencies and invalidated REQUIRED items",
            "raise effort, change model or both", "no fixed profile ladder",
            "permitted callable binding, supported effort, tools and owner-selection gates",
            "safe task-owned state stops", "unknown cause stops blind restart",
            "original assessment and selected/observed profile", "complete batch contract",
            "rerun every invalidated item", "reuse only confirmed-valid evidence",
            "Retain both attempts", "Repair success alone does not prove")
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
            "index-first and\nrelevant-only", "same run `SUMMARY.md`",
            "Older runs with `REFLECTION.md` remain", "add/refine/supersede/remove",
            "supporting/contradicting pointers", "no update proposed",
            "not a universal ban or permanent routing rule")
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
    require("coordination-initialization", section(q, "## Project-local initialization"),
            "one mandatory lifecycle in every entry point", "no opt-out or handoff-only",
            "current project root", "never the global", "explicitly declared",
            "<project-root>/memory/coordination/", "no adoption or association ceremony",
            "inside\nthe current project", "automatically\ncreate only missing",
            "No approved project coordination guidelines yet", "Preserve every existing file byte-for-byte",
            "partial stores get only their missing files", "Repeated entry is idempotent",
            "Tell the user", "commit only those new files", "path-limited commit",
            "Preserve unrelated working-tree and staged", "No separate setup approval is required",
            "report the exact blocker and stop", "finish its missing commit",
            "preselection read-only rule permits only bounded coordination-store",
            "initialization/commit and factual evidence/index/reflection persistence",
            "blocked before depth selection", "unavailable question capability",
            "no source, planning-artifact/decision-file or",
            "unapproved learned-guideline write authority")
    require("coordination-preselection", pre,
            "factual evidence/index/reflection", "including blocked runs before depth selection",
            "no source edits, decision")
    require("coordination-preselection", production,
            "factual evidence/index/reflection", "including blocked preselection")
    require("coordination-guidelines", section(q, "## Compact guidelines"),
            "before brainstorming", "exact constraints", "scope/trigger", "qualitative",
            "Owner-supplied entries name their origin", "Preserve uncertainty and contrary",
            "run evidence and reflection are not planner guidance")
    require("coordination-selective", section(q, "## Selective historical retrieval"),
            "Ordinary planning reads guidelines, not", "justified only",
            "ambiguous/tentative/conflicting", "user request", "new contradictory",
            "read the compact evidence index first", "only those selected records",
            "Do not recursively", "Unrelated records\nstay unread",
            "no relevant evidence means proceed retaining uncertainty")
    require("coordination-evidence", section(q, "## Separate factual evidence"),
            "one compact evidence file per run", "SUMMARY.md", "Do not create separate task",
            "short attributable checkpoint/attempt ledger", "Older runs with separate task",
            "Reuse that ID on resume", "never\noverwrite another run",
            "Evidence is factual and append-oriented:", "without erasing observations or prior runs",
            "initialized\nproject-local store", "never replace it", "If an evidence write\nfails",
            "exact selected and observed profile", "unknown observation is never overwritten",
            "contract strength, first/final outcome", "item check/checkpoint references",
            "accepted, partial, escalated and blocked", "failed, blocked and partial",
            "unknown outcomes are explicitly unknown",
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
    require("coordination-profile", section(q, "## Qualified batch routing feedback"),
            "Family and effort have independent", "one exact permitted owner-selected profile",
            "Relevant approved guidance may override the seed", "owner/source authority",
            "contract strength, first/final outcome", "`model_capability`", "`planning_or_spec_gap`",
            "`verification_contract_gap`", "`batching_error`", "`environment_or_tooling`",
            "`external_dependency`", "`unknown`", "Non-model causes never count as capability failure",
            "weak or\ninvalidated successes are not strong positive guidance",
            "Unknown actual model/effort stays unknown", "Inspect failed child run, invocation, partial commits",
            "permitted binding/support and owner gates", "unknown cause or unavailable/unauthorized repair stops",
            "full contract", "rerunning all invalidated checks", "selective/index-first retrieval",
            "exact owner approval", "baseline drift checks", "never automatically become guidance")
    for key in ("planner", "tiny", "tasks", "coordinator", "coordination"):
        reject("coordination-unsafe", texts.get(key, ""),
               "Always read the entire evidence directory", "Read coordination history on every request",
               "Automatically apply guideline proposals", "Implementation approval authorizes guideline writes",
               "Ignore concurrent guideline drift", "Automatically downgrade approved classes",
               "Retry without inspecting the failed invocation", "One failure permanently bans a model",
               "Without association/write authority", "offer future bounded setup",
               "Undeclared optional memory preserves existing behavior")
    # Bounded checks of changed instruction carriers, not a production audit/router.
    for label, key, heading, clauses in VERIFICATION_CARRIERS:
        require(label, section(texts.get(key, ""), heading), *clauses)
    for label, key, heading, clauses in RISK_CARRIERS:
        require(label, section(texts.get(key, ""), heading), *clauses)
    if not texts.get("risk"):
        errors.append("risk-reference: required shared carrier missing or empty")
    return errors


RISK_CARRIERS = (
    ("risk-selection", "risk", "## Select for leverage",
     ("hardest core", "disproportionate technical uncertainty", "cheaply isolated",
      "meaningful executable oracle", "substantial downstream leverage", "expected value relative to effort",
      "No universal", "Easy names/types/methods resolve by inspection", "Non-isolatable uncertainty needs",
      "real-system validation", "actual prerequisites", "not a forced isolated script")),
    ("risk-producer", "risk", "## Produce a minimal executable reference",
     ("before plumbing/integration", "smallest disposable", "not production-quality abstractions",
      "real dependency/runtime", "applicable version", "a mock or trivial script",
      "representative/adversarial assertions", "objective success/failure criteria", "reproducible commands",
      "capability/permission gates", "actually run", "observed findings", "applicability and limitations",
      "NOT VERIFIED and cannot release dependents", "tested bounds only")),
    ("risk-lifetime", "risk", "## Consume, validate, then clean up",
     ("Retain executable artifact, commands and findings", "all applicable production consumers",
      "explicit earlier producer dependency", "inspect and run", "implementation reference",
      "preserve proven behavior", "production tests", "Merely linking a report is not consumption",
      "remaining", "integration-risk checks", "changes invalidate affected evidence",
      "cleanup only after all applicable consumers and production validation pass",
      "preserve reproducible evidence", "no fixed global proof directory")),
    ("risk-disproof", "risk", "## Disproof and return",
     ("block downstream reliance", "Retain", "disproof and limits", "correct/replan",
      "renew affected existing producing reviews/approvals", "Never label a failed technique proven",
      "erase an", "weaken criteria post hoc", "blindly retry", "evidence gap, not technical disproof",
      "Unrun experiments also cannot release", "no automatic approval")),
    ("risk-boundary", "risk", "## Authority and scope",
     ("missing packaging stops", "missing-install report", "Direct/standalone", "Planning schedules proofs",
      "without separate execution authority", "not a new workflow, schema or approval stage")),
    ("risk-review", "risk", "## Review and handoff",
     ("Both TinySpec and Standard", "selection/omission", "explicit production consumption/dependencies",
      "retention through", "production tests before cleanup", "disproof routing", "feasibility/gates",
      "without embedding a task checklist", "without replacing installed task production",
      "Direct TinySpec/tasking", "standalone/helper-managed", "not real-library or model-obedience proof")),
    ("risk-planner", "planner", "## Proportionate validation",
     ("[early risk reduction](references/early-risk-reduction.md)", "missing-install report",
      "leverage, not ceremony", "easy names/types use inspection", "real-system validation",
      "Planning schedules executable proofs", "separate authority", "explicit production consumption",
      "production tests before cleanup", "retained disproof")),
    ("risk-stage-handoff", "planner", "## Selected production and stage handoffs",
     ("Apply the early risk reduction contract in stage briefs", "return justified selection/omission", "executable criteria and applicability",
      "producer → consumer → production validation → cleanup", "all consumers", "NOT VERIFIED",
      "affected approval renewal")),
    ("risk-tiny-review", "planner", "### TinySpec path",
     ("Review early risk reduction selection/omission", "real-runtime executable criteria",
      "explicit consumption/dependencies", "all-consumer retention", "production tests before",
      "cleanup, disproof/renewal and feasibility")),
    ("risk-standard-review", "planner", "### Standard path",
     ("Review early risk reduction selection/omission", "explicit consumption/dependencies",
      "all-consumer retention", "production tests before", "cleanup, disproof/renewal and feasibility",
      "direct Standard and managed/helper plans")),
    ("risk-final-handoff", "planner", "## Handoff, not execution",
     ("early risk reduction", "current proof applicability", "inspect/run", "production tests",
      "cleanup waits for all consumers", "Failed/unrun proofs cannot release assumed dependents")),
    ("risk-tiny", "tiny", "## Compact source contract",
     ("[early risk reduction](../planner/references/early-risk-reduction.md)", "missing-install report",
      "direct/standalone", "selection/omission", "minimal real-runtime executable proof",
      "easy names/types", "real-system validation", "representative/adversarial", "applicability",
      "production tests before", "all-consumer retention", "disproof/renewal",
      "Planning schedules proofs", "separate authority")),
    ("risk-tiny-return", "tiny", "## Boundary and return",
     ("early risk reduction", "explicit dependencies and inspect/run consumption",
      "commands/findings/applicability", "all-consumer retention", "failed/unrun reliance blockers",
      "affected existing approval renewal", "direct entry")),
    ("risk-helper-preflight", "helper", "## Preflight",
     ("[early risk reduction](../planner/references/early-risk-reduction.md)", "verify it is readable or stop with a missing-install report.",
      "Standalone entry applies", "Planning schedules proofs", "separate authority")),
    ("risk-helper-adapter", "helper", "## Planner Standard adapter contract",
     ("early risk reduction", "managed pass", "review/handoff", "selection/omission",
      "producer/consumer sequencing", "do not execute scheduled proofs")),
    ("risk-helper-plan", "helper", "## Planner Boundary",
     ("early risk reduction", "selection/omission", "substantial leverage", "easy names/types use inspection",
      "non-isolatable risks", "real-system validation", "minimal", "real-runtime executable proof",
      "representative/adversarial", "explicit production", "consumption/dependencies",
      "all-consumer retention", "production tests before cleanup", "disproof/renewal")),
    ("risk-helper-return", "helper", "## Completion",
     ("early risk reduction", "executable criteria/applicability", "inspect/run",
      "preserved behavior", "all-consumer retention", "disproof/NOT VERIFIED", "standalone entry",
      "Failed/unrun proofs cannot", "release assumed dependents")),
    ("risk-tasks", "tasks", "## Task contract",
     ("[early risk reduction](../planner/references/early-risk-reduction.md)", "missing-install report",
      "Both adapters and direct entry", "Planning schedules proofs", "separate authority",
      "selection/omission", "easy names/types use inspection", "real-system", "actual prerequisites/gates",
      "minimal real-runtime", "representative/adversarial", "commands/artifact/findings",
      "applicability", "explicitly depend on the earlier", "inspect/run/use",
      "preserving proven", "production tests", "not a report-only link", "all consumers",
      "cleanup last", "Failed/unrun proofs cannot release", "retain disproof/limits", "correct/replan",
      "renew affected existing approvals")),
    ("risk-task-review", "tasks", "## Review and handoff",
     ("early risk reduction selection/omission", "explicit consumption/dependencies",
      "all-consumer retention", "production tests before cleanup", "disproof/renewal",
      "both adapters/direct entry", "applicability", "blocked reliance",
      "syntax/order validation alone cannot prove consumption")),
)


VERIFICATION_CARRIERS = (
    ("verification-practical", "tasks", "## Task contract",
     ("Use practical observables", "Both adapters", "item mappings", "no special manual gate")),
    ("verification-legacy", "tasks", "## Review and handoff",
     ("inadequate approved/legacy contracts", "producing review/renewal", "weaken acceptance post hoc")),
    ("verification-planner", "planner", "## Proportionate validation",
     ("practical observables", "generic green suite", "STOP and explicit user approval")),
    ("verification-handoff", "planner", "## Selected production and stage handoffs",
     ("item mappings unchanged", "whole batch union before", "legacy producing review/renewal")),
    ("verification-oracle", "routing", "## Assess all six factors",
     ("implementation difficulty", "oracle quality, check cost and observability", "weakest material", "practical combined verification feasibility")),
    ("verification-graph", "coordinator", "## Build the Execution Graph",
     ("practical combined verification feasibility", "attributable failures", "producer-before-consumer checks")),
    ("verification-audit", "coordinator", "## Execute and Integrate",
     ("`satisfied`, `failed` or `insufficient-evidence`", "relevance to the original criterion",
      "current revision/environment", "objectively demonstrated criterion violation",
      "both proven defects and evidence limitations", "representative-sample manual STOP",
      "inspectable sample and explicit user approval", "Ordinary no-special-gate")),
    ("verification-repair", "coordinator", "## Select Execution Capability",
     ("Inspect the failed child run, invocation, partial commits and check evidence",
      "Where diagnosed and authorized, stronger-capability repair is implementation continuation",
      "Same-profile targeted repair remains appropriate when sufficient",
      "current implementation SHA/state", "same original contracts", "Clean retry is exceptional",
      "safe repository", "ownership and required owner/project gates")),
    ("verification-feedback", "coordinator", "### Coordination evidence checkpoint",
     ("batch/task item dispositions and proof references", "exact escalation reason", "next selected")),
    ("verification-feedback-owner", "coordination", "## Separate factual evidence",
     ("batch/task item dispositions and proof references", "exact escalation", "next selected profile or pending selection")),
)


def load_texts(root=ROOT):
    risk_path = root / PATHS["risk"]
    if not risk_path.is_file():
        raise ValueError("risk-reference: required shared reference unavailable")
    research_path = root / PATHS["research"]
    if not research_path.is_file():
        raise ValueError("research-reference: required shared reference unavailable")
    coordination_path = root / PATHS["coordination"]
    if not coordination_path.is_file():
        raise ValueError("coordination-reference: required shared reference unavailable")
    texts = {key: (root / path).read_text() for key, path in PATHS.items()}
    for key in ("planner", "tiny", "helper", "tasks"):
        destinations = re.findall(r"\[early risk reduction\]\(([^)]+)\)", texts[key])
        if len(destinations) != 1 or (root / PATHS[key]).parent.joinpath(destinations[0]).resolve() != risk_path.resolve():
            raise ValueError(f"risk-reference: {key} shared link missing/unresolvable or wrong owner")
    for key in ("memory", "planner", "tiny", "tasks", "coordinator"):
        destinations = re.findall(r"\[project coordination contract\]\(([^)]+)\)", texts[key])
        if len(destinations) != 1 or (root / PATHS[key]).parent.joinpath(destinations[0]).resolve() != coordination_path.resolve():
            raise ValueError(f"coordination-reference: {key} shared link missing/unresolvable or wrong owner")
    for key in ("planner", "tiny", "helper"):
        destinations = re.findall(r"\[dependency research contract\]\(([^)]+)\)", texts[key])
        if len(destinations) != 1 or (root / PATHS[key]).parent.joinpath(destinations[0]).resolve() != research_path.resolve():
            raise ValueError(f"research-reference: {key} shared link missing/unresolvable or wrong owner")
    routing_path = root / PATHS["routing"]
    for key in ("planner", "brainstorm", "helper"):
        destinations = re.findall(r"\[qualified seed rubric\]\(([^)]+)\)", texts[key])
        if not destinations or any((root / PATHS[key]).parent.joinpath(dest).resolve() != routing_path.resolve()
                                   for dest in destinations):
            raise ValueError(f"routing-reference: {key} shared link missing/unresolvable or wrong owner")
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
