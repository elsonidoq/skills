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
    "routing": "skills/planner/references/profile-selection.md",
}


# A7 bounded inventory: each consumer carries A1/A2 pending, A3 first-launch readiness,
# A4 independent comparison and A5/A6 exact selection through its existing dispatch guards.
ROUTING_CARRIERS = (
    ("rubric-coordinator", "coordinator", "## Prepare Approved Execution"),
    ("rubric-planner", "planner", "## Shared routing selection"),
    ("rubric-helper", "helper", "## Preflight"),
    ("rubric-brainstorm", "brainstorm", "## Capability preflight"),
)
ROUTING_SEQUENCE = (
    "independent comparative Family and Effort rationales",
    "Then report readiness/gaps under the shared rubric",
    "readiness blocks launch, not suitability",
    "retain the recommendation and ask for bounded authorization or an explicit fallback choice",
    "fallback needs its own justification, readiness and exact owner selection",
    "Reuse applicable passive proof; deeper source inspection is conditional, not a routine audit gate",
)


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



def operational_carrier(text, selector):
    """Bound an actual operational stage/adapter; summary wording cannot satisfy it."""
    if selector.startswith("stage:"):
        return stage(section(text, "### Standard path"), selector[6:])
    if selector.startswith("item:"):
        marker = selector[5:]
        text = section(text, "### TinySpec path" if marker[0].isdigit() else "## Preconditions and adapters")
        start = text.find(marker)
        if start < 0:
            return ""
        tail = text[start + len(marker):]
        end = re.search(r"\n(?:\d+\. \*\*|##|- A (?:direct|SpecKit) adapter|New TinySpec)", tail)
        return text[start:] if not end else text[start:start + len(marker) + end.start()]
    return section(text, selector)

# Focused workflow-ownership boundaries; these are textual checks, not semantic oracles.
MECHANICAL_CARRIERS = (
    ("requirements", "The explicit owner-required exception"),
    ("planner", "## Selected production and stage handoffs"),
    ("planner", "item:3. **Review"),
    ("planner", "stage:overall_review"),
    ("helper", "## Planner Standard adapter contract"),
    ("coordinator", "## Load and Verify"),
)
MECHANICAL_GUARDS = (
    "typos, formatting or broken links only",
    "actual before/after diff",
    "requirements, decisions, scope, dependencies, acceptance and approval validity",
    "Record the equivalence comparison",
    "comparable current-content evidence",
    "never silently reuse a stale digest",
    "A cosmetic label alone is insufficient",
    "Uncertain or substantive changes",
    "affected review and renewed approval",
    "independent reviewer never becomes the producer",
    "task-commit contract",
)

def check_workflow_ownership(texts):
    errors = []
    owner = section(texts["approval"], "## Bounded mechanical corrections")
    for guard in MECHANICAL_GUARDS:
        if " ".join(guard.split()) not in " ".join(owner.split()):
            errors.append("mechanical-owner: missing " + guard)
    for key, selector in MECHANICAL_CARRIERS:
        body = operational_carrier(texts[key], selector)
        label = "mechanical-" + key + "-" + selector
        if "bounded mechanical correction contract" not in body:
            errors.append(label + ": missing owner reference")
        for ban in ("Delegate all artifact corrections", "Delegate every source/task correction",
                    "Delegate mechanical task-level and upstream corrections", "never authors or repairs artifacts",
                    "no parent mechanical", "No parent artifact edits", "never artifact authoring or repair"):
            if ban.lower() in " ".join(body.split()).lower():
                errors.append(label + ": former blanket ban " + ban)
    return errors


def check_contracts(texts):
    errors = check_workflow_ownership(texts)
    def require(label, text, *phrases):
        for phrase in phrases:
            if " ".join(phrase.split()) not in " ".join(text.split()):
                errors.append(f"{label}: missing {phrase!r}")
    def reject(label, text, *phrases):
        for phrase in phrases:
            if phrase.lower() in text.lower():
                errors.append(f"{label}: contradictory {phrase!r}")

    for label, key, heading in ROUTING_CARRIERS:
        body = section(texts[key], heading)
        require(label, body, *ROUTING_SEQUENCE)
        reject(label, body, "compare only verified alternatives", "verify readiness before proposing",
               "silently substitute Sol", "always audit provider source before comparison")
    for label, key, heading in ROUTING_CARRIERS[:2]:
        require(label, section(texts[key], heading),
                "Start the first proposal with demands/oracles, inspect material evidence or state non-reliance",
                "then compare suitable family/effort options before readiness")

    p = texts["planner"]
    job_first = section(p, "## Job first; bookkeeping is subordinate")
    require("job-first", job_first,
            "Bookkeeping must always remain a small fraction of total effort",
            "Once required prerequisites are satisfied, advance the next authorized stage",
            "Reuse applicable settled evidence and decisions",
            "Keep required records terse",
            "Do not substitute repeated record polishing, duplicate evidence",
            "concrete invalidating evidence",
            "Carry this rule into every stage brief",
            "never waive required approvals, safety checks, permissions, reviews or commits",
            "exact blocker and smallest required resolution")
    pre = section(p, "## Before selection:")
    require("choice", pre, "read-only until", "no source edits", "Session history",
            "BOTH options", "TinySpec → Tasks → Implement", "Specify → Plan → Tasks",
            "call `ask_user` and STOP", "Either choice is valid", "preparation only",
            "resolved uncertainty alone does not reroute")
    require("planning-commit-authority", pre,
            "writing and committing the selected path's bounded planning artifacts",
            "Do not ask for separate\nplanning-commit authorization",
            "or defer these checkpoints until artifact approval",
            "Artifact approvals govern content and downstream progression",
            "Pass this commit authority unchanged to\nplanning delegates",
            "Genuine Git, policy, verification or ownership conflicts stop")
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
            "Explicit approved implementation scope", "executable runner alone")
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
            "do not create the plan again", "Only when no adapter is invoked delegate",
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
    routing_link = "[qualified seed rubric](references/profile-selection.md)"
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
        require("routing-" + key, carrier, "[qualified seed rubric](../planner/references/profile-selection.md)", "all six",
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
            "No universal\ntotal-bullet cap", "Every actual ordered plan stage separately",
            "Every actual task ID separately", "name the next", "immediately continue to the next authorized phase",
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
    require("intake", section(c, "## Load and Verify"), "TinySpec needs separate source/tasks",
            "Standard needs", "both current approvals", "required SpecKit stage evidence",
            "legacy source shape", "Resolve ambiguous", "conflicting planning depth",
            "Missing, stale or unverifiable approval", "approval/recovery mapping")
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
            "REQUIRED checks", "optional checks cannot compensate", "manual/permission gates block reliance",
            "smallest sufficient layer", "same original contracts")
    require("validation-timeout", section(c, "## Delegate"), "On timeout inspect the checkpoint and failed",
            "preserve completed proof", "narrow only the diagnosed remaining work", "Rotation is not retry authority")
    require("execution-checkpoints", section(c, "## Execute and Integrate"),
            "Commit each task's verified changes as one focused owned-path commit",
            "No extra evidence-only checkpoint", "failed recovery stops dispatch", "Healthy internal tasks continue")
    require("execution-sequential", section(c, "## Prepare Approved Execution"),
            "sequentially, never in parallel", "never silently reorder", "One writer verifies and commits each producer")
    require("execution-selection", section(c, "## Prepare Approved Execution"),
            "one exact profile per invocation", "Family and Effort rationales", "at assignment and dispatch",
            "supported effort", "callable binding", "Copy the owner-selected exact profile",
            "no silent settings/agent override", "binding/effort is unknown")
    require("execution-strategy", section(c, "## Prepare Approved Execution"),
            "Up to three bounded tasks", "More than three require delegation", "Completing tasks does not change that strategy",
            "current owner-selected exact profile", "observed context")
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
    # Feedback-only obligations belong at actual entry boundaries, not a footer.
    q = texts.get("coordination", "")
    if not q:
        errors.append("coordination-reference: required shared carrier missing or empty")
    entries = (("planner", "## Discovery and capability boundary", "coordination-early"),
               ("tiny", "## Inputs and preflight", "coordination-tiny"),
               ("tasks", "## Preconditions and adapters", "coordination-tasks"),
               ("helper", "## Preflight", "coordination-helper"),
               ("memory", "## Project coordination feedback", "coordination-memory"))
    for key, heading, label in entries:
        body = section(texts[key], heading)
        require(label, body, "project coordination contract", "missing", "nonblocking",
                "future-directed feedback" if key != "memory" else "future-directed feedback",
                "dirty/concurrent", "no-write")
    require("coordination-handoff", production, "both TinySpec and Standard stage briefs",
            "source observables/acceptance", "task dependencies, checkpoints, verification and coordinator handoff",
            "Memory cannot override source requirements or owner authority")
    require("coordination-guidelines", section(q, "## Read existing guidance"),
            "Missing store or STATE is nonblocking", "do not auto-initialize",
            "source criteria → task dependencies/REQUIRED checks → worker brief", "explicit relevant need",
            "read it first and open only matching records", "Missing relevant evidence retains uncertainty")
    require("coordination-feedback", section(q, "## Explicit feedback only"),
            "explicit user corrective/future-round direction", "without a routine second exact-content approval",
            "user provenance", "No feedback means no write", "Materially ambiguous", "no-write boundary",
            "symlink escapes", "dirty and concurrent content", "Concurrent drift", "secrets/sensitive payloads",
            "never history/index/run scaffolding", "one focused owned-path commit")
    require("coordination-nonpersistence", section(q, "## No routine bookkeeping"),
            "do not authorize STATE creation/edit/removal", "history/index updates", "reflection",
            "evidence-only commits", "No renamed durable snapshot")
    require("coordination-routing", section(c, "## Execute and Integrate"),
            "inspect run/invocation, partial commits and check evidence", "reruns invalidated",
            "Unknown cause blocks blind restart", "Preserve valid work and prior attempts")
    require("coordination-intake", section(c, "## Load and Verify"),
            "Missing coordination store or STATE is nonblocking", "No automatic STATE creation, editing or removal")
    require("routing-comparison", section(texts.get("routing", ""), "## Provisional family and effort choices"),
            "suitable options even with zero previous launches", "Family explains sufficient capability versus the named adequate alternative",
            "actual shortfall or select the adequate candidate without an unsupported premium", "pending readiness is not inadequacy",
            "orchestration overhead", "stateful tooling/recovery",
            "strict requirement versus a default preference")
    require("routing-tradeoff", section(c, "## Prepare Approved Execution"),
            "separate comparative Family and Effort rationales", "material profile, context, permission, owner-gate")
    dispatch = section(p, "## Selected production and stage handoffs")
    require("stage-dispatch", dispatch, "direct asynchronous single-stage dispatch",
            "selected profile unchanged", "Inspect the returned artifact/checkpoint",
            "before the next authorized stage", "Never prewire dependent source→tasks",
            "concrete branching, parallel independent work or another earned orchestration",
            "direct delegation cannot adequately serve", "single child, convenience wrapper",
            "stage sequence alone is insufficient", "parent inspection, stage authority, approvals and reviewer independence",
            "do not authorize parallel implementation batches")
    for key in ("planner", "tiny", "tasks", "helper", "memory", "coordinator", "coordination", "adoption"):
        reject("coordination-unsafe-" + key, texts.get(key, ""),
               "Automatically initialize coordination memory", "Write a run SUMMARY on completion",
               "Refresh the coordination index after every task", "Reflect at blocked pause",
               "Commit evidence separately before the next task", "Infer lessons from failed runs",
               "Automatically create STATE.md", "Update STATE after child-ID return", "Remove finished STATE items")
    reject("stage-dispatch", dispatch, "Default to a single-child workflow wrapper",
           "Prewire source→tasks without parent inspection", "Sequential convenience justifies workflows")
    # Bounded checks of changed instruction carriers, not a production audit/router.
    for label, key, heading, clauses in VERIFICATION_CARRIERS:
        require(label, section(texts.get(key, ""), heading), *clauses)
    for label, key, heading, clauses in COMPOSED_CARRIERS:
        require(label, section(texts.get(key, ""), heading), *clauses)
    for label, key, heading, clauses in RISK_CARRIERS + BOUNDARY_CARRIERS:
        require(label, section(texts.get(key, ""), heading), *clauses)
    if not texts.get("risk"):
        errors.append("risk-reference: required shared carrier missing or empty")
    for label, key, selector, clauses in DELEGATION_CARRIERS + AUTHORITY_CARRIERS:
        body = operational_carrier(texts.get(key, ""), selector)
        require(label, body, *clauses)
        reject(label, body, "parent may create artifacts", "parent may fix mechanical issues",
               "parent may fix upstream artifacts", "parent may fix tasks",
               "managed direct fallback is permitted", "inline fallback is permitted",
               "forward SDD guidance as requirements input", "reread SDD guidance for requirements",
               "approved plan is requirements truth")
    return errors


COMPOSED_CARRIERS = (
    ('composed-planner', 'planner', '## Proportionate validation', (
        'separate green components cannot establish a genuine risky boundary',
        'smallest composed check that observes the final observable, order or custody',
        'Reuse an existing focused check that already observes the boundary',
        'Use a separate proof prerequisite only when the consequential unknown and costly downstream reliance justify it',
        'block reliance only on insufficient or invalidated evidence, not on unrelated seams',
    )),
    ('composed-tasks', 'tasks', '## Task contract', (
        'separate green components cannot establish a genuine risky boundary',
        'smallest composed check that observes the final observable, order or custody',
        'Reuse an existing focused check that already observes the boundary',
        'Only an independently necessary prerequisite becomes an earlier task',
        'otherwise verify before reliance inside the same task',
    )),
    ('composed-handoff', 'planner', '## Selected production and stage handoffs', (
        'only genuinely necessary producer/consumer dependencies', 'original permission/manual gates',
        'accessible proof/pass conditions',
    )),
    ('composed-adapters', 'tasks', '## Review and handoff', (
        'applicable earlier producer dependencies', 'original permission/manual gates into the inline REQUIRED brief',
        'accessible proof/pass conditions',
    )),
)


RISK_CARRIERS = (
    ("risk-selection", "risk", "## Select for leverage",
     ("hardest core", "disproportionate technical uncertainty", "cheaply isolated",
      "meaningful executable oracle", "substantial downstream leverage", "expected value relative to effort",
      "No universal", "Easy names/types/methods resolve by inspection",
      "Genuine architecture, durability, security, migration, paid/live or expensive-downstream uncertainty",
      "independently verified prerequisite and original gates", "real-system validation", "not a forced isolated script")),
    ("risk-producer", "risk", "## Produce a minimal executable reference",
     ("Known bounded behavior normally uses permanent tests of the actual production helper",
      "verified earlier step inside its delivery task", "Do not create a separate prototype task",
      "genuine consequential", "ONE consequential", "actual dependency or boundary",
      "applicable runtime/version", "representative/adversarial", "a mock or trivial script",
      "informational", "both script code and actual reproducible execution output",
      "minimal command", "observed result and applicability", "Code without a run",
      "[PROTOTYPE]", "handoff and worker brief", "10/20/50 lines", "guidance, not a hard cap",
      "proof test suite or separate harness", "necessary validation layer")),
    ("risk-lifetime", "risk", "## Consume, validate, then clean up",
     ("do not force a separate producer/consumer task chain", "independently necessary prototype prerequisite",
      "inspect/use its code, findings and still-applicable result", "verified proof step before reliance within the same coherent task",
      "Permanent production\nacceptance tests remain necessary", "report-only link is not consumption",
      "revision, environment and scope still apply", "run a shared check once with",
      "every criterion/item mapping, pass condition, evidence binding and gate",
      "rerun only\ninvalidated proof where affected", "all applicable consumers and production validation",
      "safely discard actual disposable material", "concise command/result/limits",
      "not an artifact/report chain", "Routine teardown belongs inside its task",
      "real independently consequential resource or outcome", "no fixed global proof directory")),
    ("risk-disproof", "risk", "## Disproof and return",
     ("block downstream reliance", "Retain", "disproof and limits", "correct/replan",
      "renew affected existing producing reviews/approvals", "Never label a failed technique proven",
      "erase an", "weaken criteria post hoc", "blindly retry", "evidence gap, not technical disproof",
      "Unrun experiments also cannot release", "no automatic approval")),
    ("risk-boundary", "risk", "## Authority and scope",
     ("missing packaging stops", "missing-install report", "Direct/standalone", "Planning schedules proofs",
      "without separate execution authority", "not a new workflow, schema or approval stage")),
    ("risk-review", "risk", "## Review and handoff",
     ("Both TinySpec and Standard reviews", "justified selection/omission", "any genuinely necessary producer/consumer dependency",
      "proof reuse and retention", "production acceptance", "disproof routing", "feasibility/gates",
      "Keep a prototype informational", "separate only an independently necessary prerequisite",
      "normal tests, evidence and teardown inside coherent work", "Direct\ntasking and standalone/helper-managed planning",
      "not real-library or model-obedience proof")),
    ("risk-planner", "planner", "## Proportionate validation",
     ("[early risk reduction](references/early-risk-reduction.md)", "missing-install report",
      "known bounded behavior\nuses permanent actual-helper tests", "non-isolatable risks use real-system validation",
      "not execution without\nseparate authority", "shared risk owner defines proof applicability and lifetime",
      "challenge proposed task boundaries", "workflow or phase noun is not a reason to split",
      "Reject duplicate proof/report chains and disproportionate checks")),
    ("risk-stage-handoff", "planner", "## Selected production and stage handoffs",
     ("shared early-risk and task-boundary contracts", "selection/omission rationale",
      "only genuinely necessary producer/consumer dependencies", "proof lifetime",
      "NOT\nVERIFIED blockers", "Keep ordinary acceptance, evidence and\nteardown inside coherent delivery",
      "do not prescribe a prototype/consumer/cleanup task chain")),
    ("risk-tiny-review", "planner", "### TinySpec path",
     ("Review risk selection/omission", "actual evidence and gates", "necessary producer/consumer\ndependencies",
      "reuse/retention", "production acceptance", "task boundaries", "Source carries needs")),
    ("risk-standard-review", "planner", "### Standard path",
     ("Review risk selection/omission", "actual evidence and gates", "necessary producer/consumer\ndependencies",
      "reuse/retention", "production acceptance", "task boundaries", "direct Standard and managed/helper plans")),
    ("risk-final-handoff", "planner", "## Handoff, not execution",
     ("risk rationale", "current applicability", "consumers\nuse applicable evidence", "permanent production tests",
      "retain proof\nthrough all consumers/validation", "routine cleanup does not become a separate task")),
    ("risk-tiny", "tiny", "## Compact source contract",
     ("[early risk reduction](../planner/references/early-risk-reduction.md)", "verify it is readable or stop with a missing-install report",
      "direct/standalone", "justify proof selection/omission", "permanent actual-helper\ntests",
      "real-system validation", "genuine consequential unknown", "informational findings\nand tested limits",
      "shared risk contract owns proof scope", "task generation decides", "not a task chain")),
    ("risk-tiny-return", "tiny", "## Boundary and return",
     ("risk rationale", "genuinely necessary producer/consumer dependency", "proof\napplicability and lifetime",
      "execution gates", "failed/unrun\nreliance blockers", "affected approval renewal", "direct entry",
      "imply separate consumer/cleanup tasks")),
    ("risk-helper-preflight", "helper", "## Preflight",
     ("[early risk reduction](../planner/references/early-risk-reduction.md)", "verify it is readable or stop with a missing-install report.",
      "Standalone entry applies", "Planning schedules proofs", "separate authority")),
    ("risk-helper-adapter", "helper", "## Planner Standard adapter contract",
     ("Apply the shared early-risk contract", "task-generation boundaries", "genuinely necessary\nproducer/consumer sequencing",
      "not imply each proof is a separate task", "execute scheduled proofs")),
    ("risk-helper-plan", "helper", "## Planner Boundary",
     ("early risk reduction", "consequential unknown", "known bounded behavior uses actual-helper acceptance tests",
      "non-isolatable risks use real-system validation with actual\ngates", "necessary prototype prerequisites",
      "ordinary\ntests, evidence and teardown stay within coherent delivery", "shared risk contract owns",
      "not an embedded\ntask chain")),
    ("risk-helper-return", "helper", "## Completion",
     ("risk rationale", "genuinely necessary\ndependencies", "proof reuse/lifetime",
      "preserved production behavior", "disproof/NOT VERIFIED", "Failed/unrun proofs\ncannot release assumed reliance",
      "Routine cleanup stays with the task")),
    ("risk-tasks", "tasks", "## Task contract",
     ("[early risk reduction](../planner/references/early-risk-reduction.md)", "missing-install report",
      "Both adapters and direct entry", "Planning schedules proofs", "separate authority",
      "Known bounded behavior normally uses permanent actual-helper\ntests",
      "ONE consequential question", "script code and actual\nobserved execution evidence",
      "Both the direct and SpecKit adapters", "mark the task title **[PROTOTYPE]**",
      "Only an independently necessary\nprerequisite becomes an earlier task", "Failed or unrun evidence cannot release assumed reliance")),
    ("risk-task-review", "tasks", "## Review and handoff",
     ("Review selection/omission", "applicable dependencies", "proof lifetime",
      "Challenge redundant task splits, duplicate proofs/report chains and disproportionate checks",
      "only necessary producer/consumer\ndependencies", "For a [PROTOTYPE] task", "marker and bounded informational\nscope",
      "Reuse unchanged applicable proof once with all mappings", "routine teardown inside its task",
      "actual independently consequential resource or outcome")),
)


BOUNDARY_CARRIERS = (
    ("task-boundaries", "tasks", "## Task contract",
     ("A task delivers an independently verifiable outcome, not a phase label",
      "Separate tasks only for a concrete independently necessary deliverable, prerequisite, gate, resource boundary or material context incompatibility",
      "Test writing/running, evidence, verification, review preparation and routine teardown normally stay inside that outcome",
      "Do not split by a workflow noun or task-count quota")),
    ("planner-boundaries", "planner", "## Proportionate validation",
     ("At both TinySpec and Standard reviews", "workflow or phase noun is not a reason to split",
      "task-generation outcome rule", "Reject duplicate proof/report chains and disproportionate checks")),
    ("task-review-boundaries", "tasks", "## Review and handoff",
     ("Challenge redundant task splits", "without weakening acceptance or original gates",
      "For a [PROTOTYPE] task, preserve the marker and bounded informational\nscope in the handoff and worker brief")),
)


# Actual producer/consumer inputs, not incidental summary keywords.
DELEGATION_CARRIERS = (
    ("delegate-source", "planner", "item:1. **Source creation", ("delegate `tiny-spec`", "separate fresh", "bounded-context source producer", "unauthorized source", "delegation stops", "no parent creation/substantive correction or inline/local fallback")),
    ("delegate-tiny-tasks", "planner", "item:2. **Tasks", ("delegate a separate fresh bounded-context task", "unauthorized task delegation stops", "no parent task", "creation/substantive correction or inline/local fallback")),
    ("delegate-tiny-correction", "planner", "item:3. **Review", ("Delegate uncertain or substantive source/task corrections", "originating context or a fresh bounded correction delegate", "no parent substantive", "upstream repair", "unauthorized correction delegation stops", "inline/local fallback")),
    ("delegate-spec", "planner", "stage:spec_create", ("delegate a separate fresh bounded-context", "specification producer", "unauthorized specification delegation stops", "no parent creation/substantive correction or inline/local", "mechanical gaps are resolved by the delegate")),
    ("delegate-plan", "planner", "stage:plan_create", ("Delegate a separate fresh bounded-context plan producer", "unauthorized plan delegation stops", "no parent production/substantive repair", "inline/local fallback", "Only when no adapter is invoked delegate", "Never perform it in the parent")),
    ("delegate-standard-tasks", "planner", "stage:tasks_create", ("delegate a separate fresh bounded-context", "task producer", "unauthorized task", "delegation stops", "no parent task creation/substantive correction or inline/local fallback")),
    ("delegate-overall-correction", "planner", "stage:overall_review", ("Delegate uncertain or substantive task-level and", "originating producer", "fresh bounded correction delegate", "independent reviewer", "does not become the producer", "No parent substantive artifact edits", "unauthorized", "correction delegation stops", "no inline/local fallback")),
    ("delegate-recovery", "approval", "## Transition and invalidation table", ("Delegate uncertain or substantive artifact corrections", "originating producer context", "fresh bounded correction delegate", "No parent artifact authoring", "substantive task-level or upstream repair, including legacy recovery", "unauthorized delegation stops", "fallback or full transcript handoff")),
    ("delegate-helper", "helper", "## Planner Standard adapter contract", ("separate fresh bounded context", "manager never authors fresh artifacts or makes substantive repairs", "Delegate uncertain or substantive corrections", "originating", "fresh bounded correction delegate", "unauthorized", "delegation stops", "no managed direct/inline/local fallback")),
    ("delegate-handoff", "planner", "## Selected production and stage handoffs", ("separate fresh bounded-context producer for each artifact", "Loading", "a skill in the parent is not delegation", "never fresh artifact authoring or substantive repair", "Do not forward full", "transcripts or unrelated history", "unauthorized delegation stops", "no inline/local fallback", "Delegate uncertain or substantive artifact", "corrections, including task-level and upstream changes")),
)

AUTHORITY_CARRIERS = (
    ("quality-discovery", "planner", "## Discovery and capability boundary", ("for specification creation only, including TinySpec", "Use the SDD quality guidance to prepare source-producer briefs", "not downstream requirements", "complete relevant behavior, approach, constraints and observable", "unresolved material gaps return through existing gates")),
    ("quality-tiny-stage", "planner", "item:1. **Source creation", ("Supply SDD quality guidance for specification creation only", "complete relevant", "behavior, approach, constraints and observable acceptance in the source", "material gaps return through existing gates")),
    ("quality-spec-stage", "planner", "stage:spec_create", ("SDD reference for specification creation only", "complete relevant behavior, approach, constraints and observable acceptance", "unresolved material gaps return through existing gates")),
    ("quality-tiny-producer", "tiny", "## Compact source contract", ("Read and apply the [SDD quality guidance]", "for specification creation only, including TinySpec", "missing guidance stops", "Retain complete relevant behavior, approach, constraints", "observable acceptance in this source", "gaps return through existing gates", "governing instructions/contracts, memory and permission/safety", "separate tasks remain mandatory")),
    ("truth-plan", "planner", "stage:plan_create", ("specification is requirements", "truth; approved plan is derived sequencing only", "No SDD forwarding/rereading as direct", "requirements input", "governing instructions/contracts, memory and permission/safety")),
    ("truth-helper", "helper", "## Planner Standard adapter contract", ("specification is requirements", "truth; approved plan is derived sequencing only", "No SDD forwarding/rereading as direct", "requirements input", "Governing instructions/contracts, memory and permission/safety still apply")),
    ("truth-tiny-task-stage", "planner", "item:2. **Tasks", ("TinySpec is requirements truth", "no SDD forwarding/rereading", "direct requirements input", "Governing instructions/contracts, memory and permission/safety")),
    ("truth-standard-task-stage", "planner", "stage:tasks_create", ("Specification is requirements truth", "approved plan is derived sequencing", "No SDD forwarding/rereading as direct requirements input", "contracts, memory and permission/safety still apply")),
    ("truth-speckit-adapter", "tasks", "item:- A SpecKit adapter", ("Specification is requirements truth", "approved plan is derived", "sequencing only", "No SDD forwarding/rereading as direct requirements input", "Trace source", "criteria into task checks", "Governing instructions/contracts, memory and permission/safety", "create-only")),
    ("truth-direct-adapter", "tasks", "item:- A direct adapter", ("legacy source is requirements truth", "No SDD forwarding/rereading as direct requirements", "input", "Trace source criteria into task checks", "Governing instructions/contracts, memory", "permission/safety still apply")),
    ("brief-coverage", "approval", "## Executive brief before approval", ("concrete included scope", "Every actual ordered plan stage separately", "meaningful outcome", "Every actual task ID separately", "execution order", "Never truncate beyond six, merge IDs/stages", "catch-alls or empty headings", "TinySpec has no plan; specification-only approval", "This adds no plan approval gate", "Renewals regenerate the complete brief from current artifacts", "before calling `ask_user`")),
)


VERIFICATION_CARRIERS = (
    ("verification-practical", "tasks", "## Task contract",
     ("Use practical observables", "Both adapters", "item mappings", "no special manual gate")),
    ("verification-legacy", "tasks", "## Review and handoff",
     ("inadequate approved/legacy contracts", "producing review/renewal", "weaken acceptance post hoc")),
    ("verification-planner", "planner", "## Proportionate validation",
     ("practical observables", "generic green suite", "STOP and explicit user approval")),
    ("verification-handoff", "planner", "## Selected production and stage handoffs",
     ("item mappings unchanged", "whole task contract before", "legacy producing review/renewal")),
    ("verification-oracle", "routing", "## Assess all six factors",
     ("implementation difficulty", "oracle quality, check cost and observability", "weakest material", "practical combined verification feasibility")),
    ("verification-graph", "coordinator", "## Prepare Approved Execution",
     ("One writer verifies and commits each producer before its consumer", "approved order")),
    ("verification-audit", "coordinator", "## Execute and Integrate",
     ("actual diff", "focused commit/SHA", "REQUIRED outputs", "residual owned changes",
      "criterion relevance", "current revision/ environment", "Only satisfied REQUIRED items",
      "Representative-sample manual STOP", "inspectable sample and explicit owner approval")),
    ("verification-repair", "coordinator", "## Execute and Integrate",
     ("Targeted repair retains", "same original contracts", "Unknown cause blocks blind restart",
      "Clean retry is exceptional", "safe ownership and applicable owner gates")),
    ("verification-feedback-owner", "coordination", "## Explicit feedback only",
     ("Ordinary implementation approval, agent observations", "explanation-only questions", "No feedback means no write")),
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
    for key in ("memory", "planner", "tiny", "tasks", "coordinator", "helper"):
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
    for key, title in (("planner", "SDD reference"), ("tiny", "SDD quality guidance")):
        destinations = re.findall(r"\[" + title + r"\]\(([^)]+)\)", texts[key])
        if len(destinations) != 1 or (root / PATHS[key]).parent.joinpath(destinations[0]).resolve() != (root / PATHS["guidance"]).resolve():
            raise ValueError(f"quality-reference: {key} source guidance link wrong or missing")
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
