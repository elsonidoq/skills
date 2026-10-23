#!/usr/bin/env python3
"""Operational instruction checks, not model-obedience or semantic completeness proof."""
import argparse
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
PATHS = {
    "parsimony": "skills/planner/references/parsimony.md",
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
    "specify": ".pi/prompts/speckit.specify.md",
    "clarify": ".pi/prompts/speckit.clarify.md",
    "plan_prompt": ".pi/prompts/speckit.plan.md",
    "readme": "README.md",
}


# Final unified-memory composition inspects only active carrier files. Historical plans,
# negative assertions, and inert fixture bytes are deliberately outside this boundary.
UNIFIED_MEMORY_CARRIERS = (
    ("memory", "# Memory Handling", ("One verified\nproject association and one index", "two distinct evidence kinds")),
    ("planner", "## Discovery and capability boundary", ("verified unified index", "explicit owner guidance, alongside gotchas")),
    ("tiny", "## Inputs and preflight", ("verified unified index", "explicit owner guidance, alongside gotchas")),
    ("tasks", "## Preconditions and adapters", ("verified unified", "explicit owner guidance, alongside gotchas")),
    ("helper", "## Preflight", ("verified unified index", "explicit owner guidance, alongside gotchas")),
    ("coordinator", "# Coordinate Implementation", ("Memory Handling remains the unified owner", "execution-time feedback/routing")),
    ("adoption", "## Adoption", ("One associated index carries verified technical\n  gotchas and explicit future-directed owner guidance", "Do not scaffold a separate coordination or guidelines root")),
)
SECOND_STORE_REINTRODUCTION = re.compile(
    r"\b(?:create|discover|read|maintain|propagate|use)\b.{0,100}\b(?:separate|second|independent)\b.{0,100}\b(?:guidance|coordination|feedback|memory)\b.{0,100}\b(?:store|root|index|ledger)\b",
    re.I,
)


# A5 adapter carriers: source acceptance must become a task-local gate/check/brief.
ACCEPTED_ADAPTER_CARRIERS = (
    ("accepted-tiny-source", "tiny", "## Inputs and preflight", (
        "[save-adr](../save-adr/SKILL.md)",
        "direct entry and fresh/resumed", "re-establish relevant accepted authority",
        "current supersession", "source observable must yield its task dependency or gate",
        "task-local REQUIRED check and worker brief", "not merely a link",
        "source/task conflict or uncertain current\nsupersession stops only the affected acceptance mapping",
    )),
    ("accepted-task-preflight", "tasks", "## Preconditions and adapters", (
        "[save-adr](../save-adr/SKILL.md)",
        "direct entry and fresh/resumed", "re-establish relevant accepted authority",
        "current supersession", "task's\ndependency or gate, task-local REQUIRED check and worker brief",
        "not merely a link", "source/task conflict\nor uncertain current supersession stops only the affected task mapping",
    )),
    ("accepted-speckit-adapter", "tasks", "item:- A SpecKit adapter", (
        "fresh/resumed", "source observable → dependency or gate → REQUIRED\n  check → brief mapping",
    )),
    ("accepted-direct-adapter", "tasks", "item:- A direct adapter", (
        "direct fresh/resumed", "source observable → dependency\n  or gate → REQUIRED check → brief mapping",
    )),
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
    if selector == "frontmatter":
        match = re.match(r"\A---\n.*?\n---", text, re.S)
        return match.group(0) if match else ""
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
MANAGED_ENTRY_CARRIERS = (
    ("managed-specify-handoff", "specify", "frontmatter", (
        "agent: planner", "Continue managed Standard workflow",
        "independent spec review and current-spec approval before planning",
    )),
    ("managed-specify-outline", "specify", "## Outline", (
        "Return: SUCCESS to `planner`", "distinct independent `spec_review`",
        "current-specification approval before `plan_create`",
        "outside planner's independently reviewed Standard guarantee",
    )),
    ("managed-specify-completion", "specify", "## Completion Report", (
        "return control for the distinct `spec_review`", "Raw standalone SpecKit",
    )),
    ("managed-clarify-outline", "clarify", "## Outline", (
        "Under `planner`, return after required clarification", "distinct independent `spec_review`",
        "never grants the read-only reviewer edit authority",
        "outside planner's independently reviewed Standard guarantee",
    )),
    ("managed-clarify-completion", "clarify", "## Completion Report", (
        "return control for distinct review and current-specification approval",
        "outside planner's independently reviewed Standard guarantee",
    )),
    ("managed-plan-setup", "plan_prompt", "## Outline", (
        "Under `planner`, do not run setup or create planning artifacts", "distinct independent `spec_review`",
        "current-specification approval is recorded", "Return the unmet boundary to planner",
        "outside planner's independently reviewed Standard guarantee",
    )),
    ("managed-plan-context", "plan_prompt", "## Outline", (
        "load the current approved FEATURE_SPEC only after that boundary",
        "reviewer is read-only and does not edit it",
    )),
)


MECHANICAL_CARRIERS = (
    ("planner", "## Selected production and stage handoffs"),
    ("planner", "item:3. **Review"),
    ("planner", "stage:overall_review"),
    ("helper", "## Planner Standard adapter contract"),
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

    for label, key, selector, clauses in MANAGED_ENTRY_CARRIERS:
        require(label, operational_carrier(texts[key], selector), *clauses)
    reject("managed-specify-handoff", operational_carrier(texts["specify"], "frontmatter"),
           "agent: speckit.plan")
    require("managed-readme", texts["readme"],
            "Use `planner` for the managed Standard guarantee", "independent specification review",
            "current-specification approval before planning", "Raw standalone SpecKit commands remain",
            "outside that planner guarantee", "does not add a\nwrapper command or change their installer/runtime",
            "later plan helper\n  review/fix pass is not that specification review and does not trigger it again")
    require("managed-sdd-lifecycle", section(texts["guidance"], "## SDD Role and Lifecycle"),
            "Review specification", "distinct independent `spec_review`", "reviewer reports findings only",
            "originating producer incorporates actual owner answers", "outside this independently reviewed Standard guarantee",
            "rather than a wrapper or new slash command", "reviewer reports findings only and has no edit authority")

    require("parsimony-policy", texts.get("parsimony", ""),
            "smallest working solution", "legitimate behavior prevented",
            "serious exposed security/data-loss risk", "smaller/paginated read",
            "target drift stops affected continuation", "existing gates",
            "not application startup")
    for key, heading in (("planner", "## Before selection"),
                         ("tiny", "## Compact source contract"),
                         ("brainstorm", "## 1. Gate assessment"),
                         ("helper", "## Preflight"),
                         ("helper", "## Planner Standard adapter contract"),
                         ("tasks", "## Preconditions and adapters")):
        require("parsimony-consumer", section(texts[key], heading), "parsimony.md")

    p = texts["planner"]
    job_first = section(p, "## Job first; no coordinator bookkeeping")
    require("job-first", job_first,
            "no coordinator bookkeeping",
            "Do not maintain administrative ledgers, progress records, evidence manifests",
            "Runtime-owned operational state stays runtime-owned",
            "Once required prerequisites are satisfied, advance the next authorized stage",
            "Reuse applicable settled evidence and decisions",
            "State each required fact once",
            "No repeated record polishing, duplicate evidence",
            "concrete invalidating evidence",
            "Carry this rule into every stage brief",
            "Never waive required approvals, safety checks, permissions, reviews or commits",
            "exact blocker and smallest required resolution")
    discovery = section(p, "## Discovery and capability boundary")
    require("constraint-scope", discovery,
            "exact affected operation", "actual enforced limit at the consuming interface",
            "Do not generalize a tool-operation limit",
            "owner-requested behavior, verified runtime restrictions and agent-selected design choices",
            "An agent inference is not an owner requirement",
            "interpret owner agreement within the explanation and scope actually presented",
            "Correct a mistaken premise")
    require("accepted-decision-consultation", discovery,
            "[save-adr](../save-adr/SKILL.md)",
            "whole discovered decision index", "relevant accepted records in full",
            "needed supersession links", "fresh/resumed contexts re-establish applicability",
            "rather than claiming a prior read", "proposed/superseded records are not\ncurrent policy",
            "contradictory accepted authority or uncertain applicability stops only the\naffected continuation",
            "owner decision")
    require("task-concision", texts["tasks"],
            "State shared constraints once", "concise presentation, not a prose",
            "Keep task-specific work and useful checks clear",
            "verify the exact affected operation", "A worker file-tool bound is not a task-contract loader bound",
            "An inference or agreement to a narrowly explained remedy")
    executor_intake = section(texts["tasks"], "## Executor guidance")
    require("executor-producer-intake", executor_intake,
            "Before either adapter decomposes work", "producer itself must read",
            "exact path supplied in its brief", "valid worker model and effort",
            "planner/parent/producer profile, remembered\ndefault", "present valid JSON needs no executor-selection\nquestion",
            "path is missing, ambiguous or unreadable", "worker model/effort is missing or invalid",
            "affected role, path and problem", "concrete\ninterfaces, owned paths, earlier dependencies, local checks and real permission/manual gates")
    require("executor-planner-handoff", section(p, "## Intended executor before decomposition"),
            "discover the current project's selected executor JSON path", "both direct TinySpec and Standard task-producer briefs",
            "producer itself\nmust read the actual JSON before decomposing work", "planner/parent/producer profile, remembered\ndefault",
            "missing, ambiguous or unreadable", "worker model/effort is absent\nor invalid", "affected producer", "role, path and\nproblem")
    require("executor-tiny-handoff", section(texts["tiny"], "## Intended executor before decomposition"),
            "selected executor JSON path from the planner", "direct task-producer\nbrief", "task producer itself reads that JSON before decomposition",
            "does not select or copy runtime bindings", "affected task production")
    reject("retired-routing-leftover", "\n".join((p, texts["tasks"], texts["tiny"])),
           "qualified seed rubric", "residual_reasoning", "owner-selected batch routing")
    for label, key, selector, clauses in ACCEPTED_ADAPTER_CARRIERS:
        require(label, operational_carrier(texts[key], selector), *clauses)
    require("draft-editing", section(texts["approval"], "## Bounded mechanical corrections"),
            "Ordinary drafting is not submitted-artifact correction",
            "without a supervisor decision", "Once submitted, defects follow")
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
    require("accepted-decision-handoff", handoff,
            "applicable accepted outcome constraints and source links")
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
    require("accepted-decision-stage-brief", production,
            "Before every direct or delegated TinySpec/Standard stage",
            "each applicable accepted outcome constraint\nand source link",
            "updated handoff carrying those\napplicable accepted constraints and links",
            "fresh delegate's brief")
    require("discovery", p, "positive and negative claims", "already satisfied", "no task needed",
            "UNVERIFIED", "explicit owner deferral", "Do not invent a beneficiary",
            "separately scheduled mechanical work", "missing required memory stops".capitalize(),
            "missing-install report", "question: UNAVAILABLE", "inspect failures before",
            "Standard-only SpecKit/reviewer/constitution checks happen after Standard")
    require("handoff", p, "constraints **verbatim**", "prior-stage handoff", "Resume originating",
            "Re-present unanswered questions", "selected depth", "current content/revision evidence",
            "Explicit approved implementation scope", "executable runner alone")
    tiny = section(p, "### TinySpec path")
    require("tiny-flow", tiny, "**Source creation — saved assignment", "**Tasks — saved assignment",
            "**Review — planner-owned parent binding",
            "invoke `tiny-spec`", "invoke `task-generation` direct adapter",
            "Create separate tasks", "No independent planning", "**Combined approval:**",
            "BEFORE `ask_user`", "Denial returns to review", "No SpecKit prerequisite",
            "standalone\n   TinySpec approval", "Record\n   fixes",
            "brief bullet-list executive summary", "immediately proceed to handoff")
    std = section(p, "### Standard path")
    positions = [std.find(f"**`{s}`") for s in ("spec_create", "spec_review", "plan_create", "tasks_create", "overall_review")]
    if -1 in positions or positions != sorted(positions):
        errors.append("standard-order: missing/reordered operational stages")
    require("standard-preflight", std, "constitution", "template-only", "owner-derived",
            "verify repaired output", "Missing repair capability", "Do not reopen",
            "never install, simulate slash commands", "Required absent\ncapability stops")
    spec = stage(std, "spec_create")
    require("spec", spec, "— saved assignment",  "Clarify only when requested or required",
            "ordinary clarification and parent inspection", "do not approve or plan here")
    spec_review = stage(std, "spec_review")
    require("spec-review", spec_review,
            "independent saved reviewer assignment", "standard-spec-review",
            "exact saved provider/model:effort", "actually permitted and callable",
            "installed async delegation interface", "fresh context", "read-only tool/profile",
            "source-producer and `ask_user` capabilities", "Package/profile names alone are insufficient",
            "stops only this review", "do not substitute, route to another reviewer, or fall back",
            "Dispatch exactly that saved binding unchanged", "async: true",
            "bind its report to the runtime invocation", "exact\n   current specification path/content identity",
            "Do not\n   include producer rationale, transcript, or unrelated history",
            "no writes, implementation, external action, or delegation", "before and after review",
            "reviewer and\n   parent never substantively repair", "one concrete `ask_user` question at\n   a time",
            "scenario, alternatives, and consequences", "discard queued", "unanswered or cancelled material",
            "no inferred default", "originating `standard-spec-create` producer", "same producing assignment",
            "requirements/scenarios/acceptance", "Q: … → A: …", "removes contradictions, validates and checkpoints",
            "Do not rerun ordinary clarification taxonomy", "automatically rereview", "unresolved impact",
            "never release a material dependency automatically", "explicit zero findings", "skip question interaction",
            "existing current-specification executive brief and `ask_user`\n   approval gate",
            "Durably record that approval before `plan_create`", "immediately continue to `plan_create`",
            "without a second continuation or review approval")
    plan = stage(std, "plan_create")
    require("plan", plan, "— saved assignment",  "same-session pass", "review/fix the specification",
            "create one plan", "review/fix the produced plan", "entire pass",
            "do not create the plan again", "Only when no adapter is invoked delegate",
            "renewed specification approval", "new executive brief", "do not reorder".capitalize())
    tasks = stage(std, "tasks_create")
    require("task-stage", tasks, "— saved assignment",  "authorization to prepare tasks",
            "create-only", "producers may draft, revise, shorten and mechanically",
            "without supervisor", "not independent review", "After submission",
            "independent review and final approval remain required", "`overall_review`")
    review = stage(std, "overall_review")
    require("review", review, "independent saved reviewer assignment", "standard-overall-review", "observed analysis",
            "never apply unresolved material defaults", "renew affected approvals",
            "BEFORE `ask_user`", "plan-phase implications", "Missing independent reviewer",
            "bullet-list executive", "immediately proceed to handoff")
    b = texts["brainstorm"]
    require("brainstorm", b, "NO_BRAINSTORM_NEEDED", "BRAINSTORM_NEEDED", "no more than three items",
            "one material item", "recorded owner decisions", "preselection", "read-only",
            "session history", "Only in selected-production", "owner's rationale")
    require("brainstorm-assignment", section(b, "## Capability preflight"),
            "`brainstorm-assessment` or `brainstorm-application`",
            "[shared saved-assignment contract](../planner/SKILL.md#saved-planner-assignments)",
            "shared saved `brainstorming` assignment", "exact binding\nunchanged in the bounded brief and dispatch",
            "permitted and callable only\nat dispatch",
            "focused owner-correction question and no\ncandidate recommendation, inference, substitution, or fallback",
            "The parent still\nconducts owner dialogue")
    require("brainstorm-assignment", section(b, "## 3. Apply decisions"),
            "Only in selected-production or legacy-repair mode")
    reject("brainstorm-retired-routing", b, "qualified seed rubric", "six applicable factors",
           "family/effort", "Family and Effort rationales", "shared readiness conjunction",
           "owner-selected profile")
    assignments = section(p, "## Saved planner assignments")
    require("saved-assignments", assignments, "model-assignments.json", "TinySpec source/tasks",
            "Standard spec/tasks", "direct/helper plan pass", "overall review/rereview",
            "unchanged in the invocation and bounded brief", "owner-launched parent binding",
            "missing, malformed, unsupported, or unavailable", "focused owner correction question",
            "do not recommend, infer, substitute", "A correction retains its producing operation's saved assignment",
            "precise stage-specific resolution", "Inspect a failed expensive invocation")
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
    require("spec-review-recovery", a,
            "Standard spec ready", "distinct `spec_review`", "do not approve or plan yet",
            "Standard spec review returns zero", "Skip question interaction", "existing specification approval",
            "Standard spec review has findings", "Ask one material question at a time",
            "originating producer incorporates answered decisions", "Source/spec/context drift invalidates only",
            "earliest affected boundary", "originating source/spec/context, alternatives",
            "scenario, consequences and owner rationale", "no recommendation, automatic deferral",
            "clarification-taxonomy rerun, default, or\nrereview releases it")
    require("legacy", a, "inside tasks", "approved spec awaiting plan", "earliest affected Standard",
            "Other documented producer", "Ambiguous/conflicting origin", "retired skills",
            "Missing runtime capabilities")
    require("batch-handoff", production, "stable task-local REQUIRED", "canonical research", "not implementation-task assignments")
    require("batch-tiny", tiny, "verification item completeness")
    require("batch-standard", review, "verification item completeness")
    require("batch-legacy", a, "inadequate REQUIRED contracts", "producing review/approval gate", "renewed affected approval")
    require("batch-helper", texts["helper"], "applicable guidelines")
    require("batch-source", texts["tiny"], "stable task-local REQUIRED")
    require("batch-brainstorm", texts["brainstorm"], "not implementation-task assignments")
    t = texts["tasks"]
    require("task-contract", t, "SpecKit adapter", "direct adapter", "separate source and tasks file",
            "nonempty string `id`", "Optional `depends`", "IDs must be unique",
            "references must exist", "not cycle", "File order", "Do not regenerate old tasks")
    helper_adapter = section(texts["helper"], "## Planner Standard adapter contract")
    require("adapter", helper_adapter, "Planner Standard adapter", "`planner`", "same-session pass",
            "do not direct it to create the plan again")
    require("helper-assignment", helper_adapter,
            "`standard-plan-helper` saved assignment", "exact binding unchanged",
            "ambient settings or\nobserved profile never replace it", "permitted and callable at dispatch",
            "unsupported or unavailable", "resolver's exact\nfocused owner-correction question",
            "do not substitute or run a local pass", "review/fix the approved specification",
            "once to create the plan", "review/fix the produced plan")
    reject("helper-retired-routing", helper_adapter, "Sol/medium", "Sol family",
           "standalone local fallback", "separate-review policies", "fallback may bypass")
    c = texts["coordinator"]
    require("intake", section(c, "## Load and Verify"), "exactly six linter checks",
            "An empty", "Optional context stays intact")
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
    require("validation-tasks", section(t, "## Task contract"), "smallest relevant project check",
            "optional task context", "not mandatory universal acceptance items", "real outcome")
    require("validation-execution", section(c, "## Execute and Integrate"), "Project check commands are optional",
            "no universal collection-count/receipt", "preserve pre-existing/unknown bytes; never adopt them")
    require("validation-timeout", section(c, "## Recover Context"),
            "Inspect a failed run and its invocation", "unknown cause stops blind retries",
            "Preserve partial and unrelated work")
    require("execution-checkpoints", section(c, "## Execute and Integrate"),
            "one focused verified owned-path",
            "checkpoint per implementation/repair task", "before subsequent mutation or handoff",
            "No extra evidence-only checkpoint", "Never blindly replay a Git commit")
    require("execution-sequential", section(c, "## Execute and Integrate"), "Dependencies release after",
            "real focused checkpoint", "not an approval envelope")
    require("execution-selection", section(c, "## Prepare Approved Execution"), "owner-selected executor/effort",
            "without silent substitutions", "no owner catalog")
    require("execution-strategy", section(c, "## Interface Actions"),
            "task metadata is not an approval prerequisite")
    require("execution-strategy", section(c, "## Question triage"), "never invent an answer")
    require("adoption", texts["adoption"], "bounded refresh", "marked", "every unrelated byte",
            "dirty", "concurrently", "Before calling `ask_user`", "memory store and index")
    require("docs", texts["docs"], "fresh read-only investigation sub-agent", "database-schema", "empty/template shells",
            "not substantive implementation authorization", "Before calling `ask_user`",
            "explicit TinySpec/Standard choice", "dirty-target/concurrent-edit")
    require("memory", texts["memory"], "Read the whole associated index first", "index → matching entries",
            "project-local path", "global agent memory")
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
            "bounded\ncanonical-owner/discovery writes", "No recollection-based completion or automatic deferral",
            "returns exact missing evidence, affected decisions and needed authority",
            "Standalone entry cannot bypass required research",
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
    # Unified-memory obligations belong at actual entry boundaries, not a footer.
    entries = (("planner", "## Discovery and capability boundary", "unified-memory-planner"),
               ("tiny", "## Inputs and preflight", "unified-memory-tiny"),
               ("tasks", "## Preconditions and adapters", "unified-memory-tasks"),
               ("helper", "## Preflight", "unified-memory-helper"))
    for key, heading, label in entries:
        body = section(texts[key], heading)
        require(label, body, "Memory Handling", "unified index", "nonblocking",
                "alongside gotchas, through source observables", "task-local REQUIRED checks", "worker/reviewer briefs",
                "default history intake", "execution-time feedback routing")
    require("unified-memory-owner", texts["memory"],
            "One verified", "two distinct evidence kinds", "Owner guidance",
            "Read the whole associated index first", "clear, explicit, future-directed user feedback",
            "Explanation-only questions, ordinary implementation approval", "no feedback write nothing",
            "No routine bookkeeping")
    require("unified-memory-handoff", production, "both TinySpec and Standard stage briefs",
            "source observables/acceptance", "task dependencies, checkpoints, verification and coordinator handoff",
            "Memory cannot override source requirements or owner authority")
    require("unified-memory-routing", section(c, "## Execute and Integrate"),
            "No arbitrary workflow", "Do not autonomously loop expensive failed runs")
    require("unified-memory-intake", section(c, "## Load and Verify"),
            "Missing memory or STATE is nonblocking", "no automatic summaries/indexes",
            "execution-time feedback/routing")
    require("runtime-authority", section(c, "# Coordinate Implementation"),
            "SQLite stores ordinary", "not effect proof or execution eligibility")
    dispatch = section(p, "## Selected production and stage handoffs")
    require("stage-dispatch", dispatch, "direct asynchronous single-stage dispatch",
            "resolved saved assignment unchanged", "Inspect the returned artifact/checkpoint",
            "before the next authorized stage", "Never prewire dependent source→tasks",
            "concrete branching, parallel independent work or another earned orchestration",
            "direct delegation cannot adequately serve", "single child, convenience wrapper",
            "stage sequence alone is insufficient", "parent inspection, stage authority, approvals and reviewer independence",
            "do not authorize parallel implementation batches")
    for key in ("planner", "tiny", "tasks", "helper", "memory", "coordinator", "adoption"):
        reject("unified-memory-unsafe-" + key, texts.get(key, ""),
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
        'Carry work-specific checks', 'permission boundaries', 'worker brief',
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
    ("delegate-spec-review", "planner", "stage:spec_review", ("independent saved reviewer assignment", "standard-spec-review", "Dispatch exactly that saved binding unchanged", "async: true", "fresh independent reviewer", "no writes, implementation, external action, or delegation", "reviewer and\n   parent never substantively repair", "originating `standard-spec-create` producer", "same producing assignment", "no inferred default")),
    ("delegate-plan", "planner", "stage:plan_create", ("Delegate a separate fresh bounded-context plan producer", "unauthorized plan delegation stops", "no parent production/substantive repair", "inline/local fallback", "Only when no adapter is invoked delegate", "Never perform it in the parent")),
    ("delegate-standard-tasks", "planner", "stage:tasks_create", ("delegate a separate fresh bounded-context", "task producer", "unauthorized task", "delegation stops", "no parent task creation/substantive correction or inline/local fallback")),
    ("delegate-overall-correction", "planner", "stage:overall_review", ("Delegate uncertain or substantive task-level and", "originating producer", "fresh bounded correction delegate", "independent reviewer", "does not become the producer", "No parent substantive artifact edits", "unauthorized", "correction delegation stops", "no inline/local fallback")),
    ("delegate-recovery", "approval", "## Transition and invalidation table", ("Delegate uncertain or substantive artifact corrections", "originating producer context", "fresh bounded correction delegate", "No parent artifact authoring", "substantive task-level or upstream repair, including legacy recovery", "unauthorized delegation stops", "fallback or full transcript handoff")),
    ("delegate-helper", "helper", "## Planner Standard adapter contract", ("separate fresh bounded context", "manager never authors fresh artifacts or makes substantive repairs", "Delegate uncertain or substantive corrections", "originating", "fresh bounded correction delegate", "unauthorized", "delegation stops", "`standard-plan-helper` saved assignment", "do not substitute or run a local pass")),
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
    ("verification-legacy", "tasks", "## Structured executable handoff (both adapters)",
     ("No required order", "Do not regenerate old tasks", "Useful existing `required` check mappings")),
    ("verification-planner", "planner", "## Proportionate validation",
     ("practical observables", "generic green suite", "STOP and explicit user approval")),
    ("verification-handoff", "planner", "## Selected production and stage handoffs",
     ("item mappings unchanged", "whole task contract before", "legacy producing review/renewal")),
    ("verification-graph", "coordinator", "## Execute and Integrate",
     ("one focused verified owned-path", "before subsequent mutation or handoff")),
    ("verification-audit", "coordinator", "## Execute and Integrate",
     ("actual diff", "explicit paths", "normal Git hooks/signing",
      "preserve pre-existing/unknown bytes; never adopt them", "Dependencies release after")),
    ("verification-repair", "coordinator", "## Execute and Integrate",
     ("No arbitrary workflow", "Do not autonomously loop expensive failed runs",
      "Never blindly replay a Git commit")),
    ("verification-feedback-owner", "memory", "## Authorized writes",
     ("ordinary implementation approval, agent\nobservations", "Explanation-only questions", "no feedback write nothing")),
)


def load_texts(root=ROOT):
    risk_path = root / PATHS["risk"]
    if not risk_path.is_file():
        raise ValueError("risk-reference: required shared reference unavailable")
    research_path = root / PATHS["research"]
    if not research_path.is_file():
        raise ValueError("research-reference: required shared reference unavailable")
    texts = {key: (root / path).read_text() for key, path in PATHS.items()}
    for key in ("planner", "tiny", "helper", "tasks"):
        destinations = re.findall(r"\[early risk reduction\]\(([^)]+)\)", texts[key])
        if len(destinations) != 1 or (root / PATHS[key]).parent.joinpath(destinations[0]).resolve() != risk_path.resolve():
            raise ValueError(f"risk-reference: {key} shared link missing/unresolvable or wrong owner")
    for key in ("planner", "tiny", "tasks", "helper"):
        destinations = re.findall(r"\[Memory Handling\]\(([^)]+)\)", texts[key])
        if len(destinations) != 1 or (root / PATHS[key]).parent.joinpath(destinations[0]).resolve() != (root / PATHS["memory"]).resolve():
            raise ValueError(f"unified-memory-reference: {key} shared link missing/unresolvable or wrong owner")
    for key in ("planner", "tiny", "helper"):
        destinations = re.findall(r"\[dependency research contract\]\(([^)]+)\)", texts[key])
        if len(destinations) != 1 or (root / PATHS[key]).parent.joinpath(destinations[0]).resolve() != research_path.resolve():
            raise ValueError(f"research-reference: {key} shared link missing/unresolvable or wrong owner")
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


ACTIVE_EXECUTION_CONSUMERS = (
    'skills/coordinate-implementation/SKILL.md',
    'skills/planner/SKILL.md','skills/task-generation/SKILL.md',
    'skills/planning-brainstorming/SKILL.md','skills/tiny-spec/SKILL.md',
    'skills/delegating-architectural-planning/SKILL.md',
    'skills/requesting-code-review/SKILL.md','skills/requesting-code-review/code-reviewer.md',
    'skills/receiving-code-review/SKILL.md','skills/scientific-method-debugging/SKILL.md',
    'skills/handoff-prompt/SKILL.md','skills/finish-session/SKILL.md',
    'skills/initialize-coherence/SKILL.md','README.md','REQUIREMENTS.md','AGENTS.md',
    'docs/index.md','docs/pi-settings-sample.md','docs/coordinate-implementation.md',
    '.pi/prompts/speckit.implement.md','.pi/prompts/speckit.tasks.md',
    '.specify/templates/tasks-template.md',
)


def composed_unified_memory_errors(texts):
    """Reject active second-store behavior without scanning historical/proposal bytes."""
    errors = []
    for key, heading, clauses in UNIFIED_MEMORY_CARRIERS:
        body = section(texts[key], heading)
        for clause in clauses:
            if " ".join(clause.split()) not in " ".join(body.split()):
                errors.append(f"unified-memory-composition: {key} missing {clause!r}")
        for match in SECOND_STORE_REINTRODUCTION.finditer(body):
            prefix = body[max(0, match.start() - 20):match.start()]
            if not re.search(r"(?:no|never|do not)\s*$", prefix, re.I):
                errors.append(f"unified-memory-composition: {key} restores a second-store operation")
    return errors


def repository_memory_errors(root=ROOT):
    """Check this repository's unified-memory association, not a project adoption engine."""
    errors = []
    sources = {
        "AGENTS.md": ("its single index for verified trigger-first gotchas and explicit future-directed owner\n  guidance",),
        "README.md": ("One verified association/index carries technical gotchas and explicit future-directed owner",),
        "REQUIREMENTS.md": ("one approved project-memory\nassociation and index for verified technical gotchas and explicit future-directed owner guidance",),
        "docs/index.md": ("single\n[project-memory index]", "[Memory Handling](../skills/memory-handling/SKILL.md)"),
    }
    for path, clauses in sources.items():
        text = (root / path).read_text()
        for clause in clauses:
            if clause not in text:
                errors.append(f"unified-memory-repository: {path} missing {clause!r}")
    for path in ("AGENTS.md", "README.md", "REQUIREMENTS.md"):
        if "memory/coordination/" in (root / path).read_text():
            errors.append(f"unified-memory-repository: {path} restores an operative second-store path")
    index = (root / "memory/MEMORY.md").read_text()
    guidance = ("Routine task transitions/completions and steering-status updates must not wake the parent agent or require acknowledgment. "
                "Only agent questions and terminal workflow completion, whether success or error, should trigger a parent turn.")
    for clause in ("## Owner guidance", guidance, "Explicit current owner feedback"):
        if clause not in index:
            errors.append(f"unified-memory-repository: memory/MEMORY.md missing {clause!r}")
    return errors


def active_consumer_errors(root=ROOT):
    errors=[]
    for path in ACTIVE_EXECUTION_CONSUMERS:
        text=(root/path).read_text()
        for retired in ('references/batch-routing.md','Up to three bounded tasks',
                        'More than three require delegation','Coordinator alone selects models/strategy/batches',
                        'The legacy skill remains the default','explicit batch/profile approval'):
            if retired in text:errors.append(path+': retired execution authority '+retired)
    if (root/'skills/coordinate-implementation/references/batch-routing.md').exists():
        errors.append('retired execution routing owner still active')
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--active-consumers", action="store_true")
    args = parser.parse_args()
    try:
        if args.active_consumers:
            errors=active_consumer_errors(args.root)
            for path in ACTIVE_EXECUTION_CONSUMERS:print('ActiveConsumersTests: inspected '+path)
        else:
            texts = load_texts(args.root)
            errors = (check_contracts(texts) + composed_unified_memory_errors(texts)
                      + repository_memory_errors(args.root))
    except (OSError, ValueError) as exc:
        errors = [str(exc)]
    for error in errors:
        print(error)
    print(f"planner workflow: {'FAIL' if errors else 'PASS'} (static instructions only)")
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
