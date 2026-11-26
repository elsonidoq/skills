#!/usr/bin/env python3
"""Operational instruction checks, not model-obedience or semantic completeness proof."""
import argparse
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
PATHS = {
    "parsimony": "skills/planner/references/parsimony.md",
    "planner": "skills/planner/SKILL.md",
    "spec_review_prompt": "skills/planner/references/spec-review.md",
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
    "tasks_prompt": ".pi/prompts/speckit.tasks.md",
    "tasks_template": ".specify/templates/tasks-template.md",
    "plan_template": ".specify/templates/plan-template.md",
    "readme": "README.md",
    "finish": "skills/finish-session/SKILL.md",
    "tracker": "skills/track-open-issue/SKILL.md",
}


# Final unified-memory composition inspects only active carrier files. Historical plans,
# negative assertions, and inert fixture bytes are deliberately outside this boundary.
UNIFIED_MEMORY_CARRIERS = (
    ("planner", "## Understand the work and choose depth", ("verified unified index", "explicit owner guidance and gotchas")),
    ("memory", "# Memory Handling", ("One verified\nproject association and one index", "two distinct evidence kinds")),
    ("tiny", '## Establish the source to write', ("verified unified index", "explicit owner guidance and gotchas")),
    ("tasks", '## Draft outcomes from the source', ("verified unified index", "explicit owner guidance and gotchas")),
    ("helper", '## Arrange the bounded planning pass', ("verified unified index", "explicit owner guidance and gotchas")),
    ("coordinator", "# Coordinate Implementation", ("Memory Handling remains the unified owner", "execution-time feedback/routing")),
    ("adoption", "## Adoption", ("One associated index carries verified technical\n  gotchas and explicit future-directed owner guidance", "Do not scaffold a separate coordination or guidelines root")),
)
SECOND_STORE_REINTRODUCTION = re.compile(
    r"\b(?:create|discover|read|maintain|propagate|use)\b.{0,100}\b(?:separate|second|independent)\b.{0,100}\b(?:guidance|coordination|feedback|memory)\b.{0,100}\b(?:store|root|index|ledger)\b",
    re.I,
)


# A5 adapter carriers: source acceptance must become a task-local gate/check/brief.
ACCEPTED_ADAPTER_CARRIERS = (
    ('accepted-tiny-source', 'tiny', '## Establish the source to write', (
        '[save-adr](../save-adr/SKILL.md#consult-and-propagate)',
        'fresh or resumed production',
        'current accepted outcomes, explicit mechanism constraints and source links',
        'source observables and acceptance, not just citations',
        'dependency or gate and check needs',
        'task-local REQUIRED checks and worker/reviewer briefs',
        'source/task conflict or uncertain supersession stops only the affected mapping',
    )),
    ('accepted-task-preflight', 'tasks', '## Draft outcomes from the source', (
        '[save-adr](../save-adr/SKILL.md#consult-and-propagate)',
        'direct and fresh/resumed entry',
        'current accepted outcomes, explicit mechanism constraints and source links',
        'task dependency or gate, task-local REQUIRED check and worker/reviewer briefs',
        'must affect that mapping',
        'source/task conflict or uncertain supersession stops only the affected mapping',
    )),
    ('accepted-speckit-adapter', 'tasks', '## Draft outcomes from the source', (
        '**SpecKit adapter**',
        'For both routes',
        'task dependency or gate, task-local REQUIRED check',
        'worker/reviewer briefs',
    )),
    ('accepted-direct-adapter', 'tasks', '## Draft outcomes from the source', (
        '**direct adapter**',
        'For both routes',
        'direct and fresh/resumed entry',
        'task dependency or gate, task-local REQUIRED check',
        'worker/reviewer briefs',
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
    ("planner", "## Approve current content and hand off"),
    ("helper", '## Arrange the bounded planning pass'),
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


# Check coordinator operations and consumed owner results, not a duplicate specialist recipe.
PLANNER_CARRIERS = (
    ('discovery', '## Understand the work and choose depth', (
        'request or selected source', 'preserve unrelated work', 'ambiguous source selection',
        'positive and negative claims', 'UNVERIFIED', 'explicit owner deferral',
        'Do not invent a beneficiary', 'exclusions and separately scheduled mechanical work',
        'owner requirements, verified interface limits and agent design choices',
        'affected consuming interface', 'scope actually presented',
    )),
    ('unified-memory-planner', '## Understand the work and choose depth', (
        '[Memory Handling](../memory-handling/SKILL.md)', 'verified unified index',
        'explicit owner guidance and gotchas', 'retrieval and authority rules',
        'missing optional memory or STATE is nonblocking', 'missing required memory',
        'task-local REQUIRED checks and worker/reviewer briefs',
    )),
    ('accepted-decision-consultation', '## Understand the work and choose depth', (
        '[save-adr](../save-adr/SKILL.md#consult-and-propagate)', 'fresh and resumed work',
        'accepted outcomes, explicit mechanism constraints and source links',
        'Re-establish applicability on resume', 'not just links',
        'Conflicting authority or uncertain supersession returns to the owner',
    )),
    ('choice', '## Understand the work and choose depth', (
        'read-only until explicit depth selection', 'no source edits', 'dependency-document writes',
        'session history', 'BOTH paths', 'TinySpec → Tasks → Implement',
        'Standard: Specify → Plan → Tasks → Implement', 'Either choice is valid',
        'Call `ask_user` and STOP', 'Denial, cancellation, timeout or ambiguity grants no consent',
        'preparation only', 'resolved uncertainty alone does not reroute',
    )),
    ('planning-commit-authority', '## Understand the work and choose depth', (
        'writing and committing bounded planning artifacts', 'Pass that authority to producers',
        'do not ask for separate planning commit permission or defer checkpoints until content approval',
    )),
    ('shared-invocation', '## Understand the work and choose depth', (
        'Invoke `planning-brainstorming` directly in the parent in preselection mode',
        'readiness target “informed scope assessment.”', 'NO_BRAINSTORM_NEEDED',
        'without a child call', 'BRAINSTORM_NEEDED', 'owner dialogue yourself',
        'one material item at a time', 'Do not delegate the gate or resolve `brainstorm-assessment`',
    )),
    ('issue-association', '## Understand the work and choose depth', (
        'After understanding/brainstorming', '[track-open-issue]', 'declared tracker',
        'specific authority, separate from planning preselection', 'qualified URL',
        'before planned artifact production', 'confirmed creation or qualified exact reuse',
        'complete open/closed overlap discovery', 'exact issue body/identity/state readback',
        'separate body-quality review when creation occurs',
        'without a repeated routine creation question',
        'open or closed exact match without duplicate or reopen',
        'stops association and planned artifact production', 'concrete corrective action',
        'never a local fallback register', 'depth selection alone does not release artifact production',
        'Created/read-back but review-incomplete is not ready', 'bare runtime tasks',
    )),
    ('stage-dispatch', '## Arrange the next authorized stage', (
        'direct asynchronous single-stage dispatch', 'inspect the actual artifact, checks and focused checkpoint',
        'before the next authorized stage', 'never prewire dependent source → tasks',
        'dispatching async work before returning control', 'another need direct delegation cannot serve',
        'not a single child or convenient stage sequence', 'no parallel implementation authority',
    )),
    ('capabilities', '## Arrange the next authorized stage', (
        '[runtime requirements]', 'at the operation that needs them', 'missing-install report',
        'concrete correction', 'not installation, simulation or inline substitution',
        'question: UNAVAILABLE', 'without inferred consent', 'coherence-producer', 'coherence-reviewer',
        'subagent get', 'user source, effective prompt and tools', 'do not substitute another agent',
        'separate fresh bounded-context producer', 'never authors fresh artifacts or makes substantive repairs',
    )),
    ('saved-assignments', '### Saved planner assignments', (
        '[model-assignments.json](references/model-assignments.json)', 'saved-assignment contract', 'unchanged in invocation and brief',
        'permitted and callable at dispatch', 'not availability evidence',
        'Missing, malformed, unsupported or unavailable', 'focused owner correction question',
        'no recommendation or substitute', 'owner-launched binding', 'inherits `planner-parent`',
        'another fresh session', 'do not select implementation models or batches',
        'Corrections retain the producing operation', 'precise stage-specific resolution',
        'failed expensive invocation and its call before retry', 'Unknown cause stops',
        '`brainstorm-application` and the recorded answers',
    )),
    ('brief', '### Give producers the inputs their owners require', (
        'exact source and current content', 'stage and commit authority', 'allowed writes, prohibited operations',
        'constraints verbatim', 'accepted outcomes and source links', 'prior-stage return',
        'actual owner answers and pending deferrals/gates', 'Re-present unanswered questions',
        'Do not forward full transcripts or unrelated history', 'changed paths/content evidence',
        'checkpoint, decisions, constraints and links, verification mappings and remaining blockers',
    )),
    ('research-review', '### Give producers the inputs their owners require', (
        'Before consequential dependency decisions', '[dependency research contract](references/dependency-research.md)',
        'reuse/skip/refresh rationale', 'capability evidence, canonical owner/discovery links',
        'version/provenance and supporting spans → constraints → observable checks',
        'bounded permission', 'during selected production, in addition to SpecKit artifacts',
        'Inspect the returned persistence and evidence mappings before readiness, including direct and helper routes',
        'only explicit bounded owner deferral', 'impact, allowed bounds and outstanding validation',
        'Never substitute recollection or invent evidence',
    )),
    ('source-authority', '### Give producers the inputs their owners require', (
        'For source creation only', '[SDD reference]', 'complete relevant behavior, approach, constraints and observable acceptance',
        'TinySpec/specification is requirements truth', 'plan supplies derived sequencing only',
        'Do not forward or reread SDD as downstream requirements input',
        'Governing instructions, memory and permission/safety rules still apply',
    )),
    ('risk-planner', '### Give producers the inputs their owners require', (
        '[early risk reduction](references/early-risk-reduction.md)', 'justified proof selection/omission',
        'actual evidence and limits, necessary dependencies', 'applicability/lifetime',
        'production acceptance and disproof/renewal results', 'Failed or unrun proof cannot release reliance',
        'not execution without separate authority',
    )),
    ('executor-planner-handoff', '### Give producers the inputs their owners require', (
        'Before decomposition', 'scripts/resolve-workflow-executor.py --project PROJECT_ROOT',
        'Verify Python and resolver availability', '`--executor PATH` only for explicit override',
        'exact absolute stdout path unchanged', 'both direct TinySpec and Standard task-producer briefs',
        'coordinator handoff', 'Do not search, create/copy or substitute configuration',
        'producer\'s actual JSON read', 'invalid/missing worker model/effort correction',
        'independently finishable outcomes sized for that executor', 'not the planner profile',
        'outcome/proof and authorization-neutral task contracts', 'production and final review',
        'whole REQUIRED check mappings', 'actual manual/permission gates through both adapters and legacy renewal',
        'Do not add execution-intent or compatibility metadata',
    )),
    ('job-first', '### Give producers the inputs their owners require', (
        'Keep facts once in their authoritative artifacts', 'No administrative ledgers, progress records, evidence manifests',
        'STATE maintenance, inferred lessons or routine memory writes', 'runtime state stays runtime-owned',
        'Carry this boundary in briefs', 'Reuse settled evidence until changed scope',
        'smallest meaningful check and report limits', 'static/fixture checks do not prove model obedience',
        'Preserve required runtime, integration, application, security and permission checks',
        'genuinely required live acceptance', 'No mandatory prior/candidate run',
        'Optional hardening is not an acceptance blocker', 'changing required acceptance needs owner authority',
        'changed observable', 'integration when mocks cannot detect the failure',
        'migration, authorization and persistence checks', 'Avoid automatic exhaustive matrices or new test infrastructure',
        'Separate unrelated recovery repairs', 'evidence that it blocks the selected change', 'not repeated historical intake',
    )),
    ('tiny-flow', '### TinySpec path', (
        '`tinyspec-source`; delegate `tiny-spec`', 'observed destination and preparation authority',
        'Inspect its source and returned research/risk results', 'No SpecKit prerequisite',
        '`tinyspec-spec-review`; apply the shared specification-review contract',
        'Inspect source-producer corrections before tasks', 'Zero or resolved findings go directly to tasks',
        'no separate TinySpec source approval', '`tinyspec-tasks`', '`task-generation` direct adapter',
        'selected executor path', 'separate human/executable tasks', 'documentation work from inspected effects',
        'shared final task-review contract', '`planner-parent` for correctness and simplicity on the same source/tasks',
        'combined current source/task/implementation-scope approval', 'continue to handoff',
        'Denial returns to correction, not execution',
    )),
    ('standard-preflight', '### Standard path', (
        'After Standard selection', 'installed SpecKit commands, instructions and templates',
        'AVAILABLE/UNAVAILABLE with evidence', 'Do not install, simulate slash commands or substitute ordinary Markdown',
        'template-only constitution principles', 'owner-derived answers', 'verified repaired output',
        'Missing repair capability, principles or verification stops', 'do not reopen valid principles',
    )),
    ('spec', 'stage:spec_create', (
        '`standard-spec-create`', 'delegate a fresh specification producer', 'observed specification instructions',
        'source-creation guidance above', 'Clarify only when requested or required',
        'ordinary clarification and parent inspection', 'before review—not approval or planning',
    )),
    ('spec-review', 'stage:spec_review', (
        '`standard-spec-review`', 'shared specification-review contract', 'Report total findings and meaningful areas',
        'five most important (all if fewer)', 'offer all findings or a grouped overview',
        'not a discovery or resolution cap', 'Retain all findings', 'continue through all material ones',
        'Ask one material owner question at a time', 'scenario, alternatives and consequences',
        'discard queued questions resolved by an answer', 'Send actual answers to the originating specification producer',
        'under its saved assignment', 'requirements/scenarios/acceptance', '`Q: … → A: …`',
        'remove contradictions, validate and checkpoint', 'Inspect corrections',
        'Do not rerun ordinary clarification taxonomy', 'Every material decision needs an answer or explicit owner deferral',
        'consequences and permitted planning bounds', 'cancellation releases nothing', 'With zero findings, skip questions',
        'current-specification approval before `plan_create`, then immediately continue',
    )),
    ('plan', 'stage:plan_create', (
        '`standard-plan-helper`', '`standard-plan-direct`', 'Delegate the entire same-session pass',
        'review/fix the specification, create one plan', 'review/fix the produced plan',
        '[planning contract]', 'either route\'s architecture, evidence, write bounds and return',
        'inspect its return; do not create the plan again', 'parent never performs this pass',
        'renewed specification approval with a new executive brief before leaving this stage',
        'proven equivalence under the mechanical contract',
    )),
    ('task-stage', 'stage:tasks_create', (
        '`standard-tasks-create`', 'delegate a fresh producer', 'observed SpecKit tasks and `task-generation`',
        'source, plan and selected executor path', 'create-only preparation',
        'drafting, revision, shortening and mechanical validation of unsubmitted output need no supervisor permission',
        'cannot change approved requirements or replace review', 'checked human/executable tasks and their mappings/risks',
        'submitted defects go to final review',
    )),
    ('review', 'stage:overall_review', (
        '`standard-overall-review`', '`standard-overall-rereview`', 'observed analysis capability',
        'shared final task-review contract', 'simplicity in parallel', 'renew affected upstream approvals',
    )),
    ('intent-review', '### Shared specification-review contract', (
        'one fresh independent read-only source review before downstream production',
        'separate from the source producer and parent history', '[the canonical review prompt]',
        'original request, actual owner clarifications/decisions', 'exact current source path/content identity and readable content',
        'Exclude producer rationale, conclusions and unrelated history', 'Verify the saved binding',
        'fresh read-only async capability, source producer and question capability', '`async: true`',
        'Bind the report to that invocation', 'compare source content before and after review',
        'not edits, approval, implementation, external actions or delegation',
        'coverage, downstream clarity and simplicity', 'including limits', 'targeted completion',
        'existing reviewer context', 'not an automatic second review', 'fidelity defects to the source producer',
        'material decisions to the owner', 'inspect corrections against intent and findings',
        'Unresolved material intent gaps stop downstream production', 'cannot release reliance on the gap',
        'No new tracker, automatic rereview loop or additional approval gate',
    )),
    ('final-task-review', '### Shared final task-review contract', (
        'two bounded handoffs against the same current artifact snapshot', 'original request, actual owner decisions',
        'final human/executable tasks', 'not producer conclusions, assurances or approval trajectory',
        'correctness, completeness, feasibility, traceability', 'verification item completeness',
        'independently executable outcome and authorization-neutral contracts',
        'research evidence/permission results and early-risk review results', 'in both paths',
        'each material execution risk/prerequisite with affected task', 'evidence versus unknowns',
        'next investigation, mitigation or permission', 'before worker reliance',
        'Do not ask correctness for a simplicity verdict',
    )),
    ('coordinator-review-sequence', '### Shared final task-review contract', (
        '1. Prepare two bounded handoffs', '2. Before launching either reviewer',
        'independently inspect that snapshot', 'Does this plan achieve the requested outcome with the least necessary work?',
        'Justify your conclusion with specific examples from the plan.',
        'identify the potentially costly choices you examined', 'Do not give an unsupported yes/no answer.',
        'Keep this parent analysis out of both handoffs', '3. Launch both fresh independent read-only reviewers before awaiting either report',
        'Never fork or resume parent, producer or the other review', 'selected final-review binding unchanged for both',
        'Do not send findings between reviewers or begin corrections until both reports return',
        'Missing review evidence stops approval, not the other independent review',
        '4. Assess all three analyses together', 'explain rejected findings with evidence',
        'one bounded brief for the appropriate producer', 'resume useful originating context',
        'fresh correction producer', 'No fixer is needed without supported corrections',
        'Resolve material findings before approval', 'recheck affected changes and interactions',
        'not an automatic full-review loop',
    )),
    ('simplicity-review', '### Shared simplicity-review contract', (
        '[the simplicity prompt](references/simplicity-review.md)', 'not the correctness or broad production checklist',
        'executive bullets of what the owner wants, why and essential scope boundaries',
        'original request and actual answers', 'summary adds no requirements',
        'human/executable tasks (plus Standard plan)', 'accepted decisions, memory and relevant code access',
        'Exclude producer rationale, prior verdicts, parent criticism and full transcripts',
        'per-task findings and cross-task check, including evidence limits', 'simplest sufficient delivery',
        'not fewer tasks or weaker required acceptance', 'summarize planned task specifications in one sentence',
        'least-necessary-work question from step 2 above', 'same evidence and justification requirements',
        'tasks and both reports, not just verdicts',
        'Agent-added constraints remain challengeable', 'manual and permission gates remain binding',
    )),
    ('approval-handoff', '## Approve current content and hand off', (
        '[approval/recovery contract]', 'At every approval or renewal', 'executive bullet brief in conversation BEFORE `ask_user`',
        'every actual ordered plan stage and task ID/outcome', 'not invented TinySpec plan stages',
        'exact approved current content and next authority', 'final approval starts coordinator preflight',
        'Older preparation-only approval never implies execution authority',
        'Denied, cancelled, timed-out or ambiguous answers stop affected continuation',
        'independent reviewer never becomes the producer', '[bounded mechanical correction contract]',
        'diff/equivalence and current-content evidence', 'no inline fallback',
        'transition and legacy mapping', 'pending answers and child/correction state',
        'Read linked external decisions/approvals', 'reconcile active or unknown children before replacement',
        'Preserve valid approvals and task-embedded sources', 'earliest invalid gate',
        'Ambiguous origin needs owner resolution', 'Inadequate REQUIRED contracts return to producing review/approval',
        'source/task consistency, ordering, reviews/approvals, proof applicability',
        'without a new state/handoff file', 'approved current content/revision evidence', 'explicit approved implementation scope/authority',
        'automatically invoke `coordinate-implementation` in the same session',
        'explicitly requested planning-only or separate-session handoff', 'precise blocker and preserved handoff',
        'executable runner alone implements', '[task-commit contract]', 'after verification, before later task writes or handoff',
        'Git, policy, verification or ownership conflicts stop', 'Read-only work creates no empty commit',
    )),
)


def check_planner(text):
    errors = []
    for label, selector, clauses in PLANNER_CARRIERS:
        body = ' '.join(operational_carrier(text, selector).split())
        for clause in clauses:
            if clause not in body:
                errors.append(f'{label}: missing {clause!r}')
    for label, selector, markers in (
        ('standard-order', '### Standard path', ('**`spec_create`', '**`spec_review`', '**`plan_create`', '**`tasks_create`', '**`overall_review`', '6. Obtain overall approval')),
        ('tiny-review-order', '### TinySpec path', ('`tinyspec-source`', '`tinyspec-spec-review`', '`tinyspec-tasks`', '4. Run the shared final task-review', '5. Obtain combined')),
        ('coordinator-review-order', '### Shared final task-review contract', ('1. Prepare', '2. Before', '3. Launch', '4. Assess')),
        ('spec-review-order', 'stage:spec_review', ('Ask one material', 'Send actual answers', 'Inspect corrections', 'With zero findings', 'current-specification approval')),
    ):
        body = operational_carrier(text, selector)
        positions = [body.find(marker) for marker in markers]
        if -1 in positions or positions != sorted(positions):
            errors.append(label + ': missing/reordered operations')
    pre = section(text, '## Understand the work and choose depth')
    if 'persist dependency docs before selection' in pre.lower():
        errors.append('research-preselection: unauthorized write before depth choice')
    dispatch = section(text, '## Arrange the next authorized stage')
    for unsafe in ('Default to a single-child workflow wrapper', 'Prewire source→tasks without parent inspection',
                   'Sequential convenience justifies workflows'):
        if unsafe in dispatch:
            errors.append('stage-dispatch: contradictory ' + unsafe)
    return errors


# Check actual stage carriers, not a repository-wide mention of the design gate.
DESIGN_CARRIERS = (
    ('planner', '## Produce and review the selected artifacts', (
        'explicit owner design agreement before detailed architecture plan production or continuation',
        'Significant design changes renew', 'Requirements approval, design agreement and final implementation approval remain distinct',
        'reuse a settled grant', 'project-owned HTML destination')),
    ('tiny', '## Write the what and how', (
        'self-contained interactive HTML high-level design', 'interfaces, dependencies and material risks',
        'explicit owner design agreement before producing or continuing the detailed how',
        'Page creation/interaction, silence, denial or cancellation is not consent',
        'Significant design changes renew agreement', 'Routine mechanics remain autonomous')),
    ('helper', '## Produce and inspect the plan', (
        'Before setup-plan or detailed architecture plan production or continuation',
        'self-contained interactive HTML high-level design', 'explicit owner design agreement',
        'shown content identity, actual answer/scope and ordering', 'Significant design changes renew agreement')),
    ('plan_prompt', '## Design agreement before setup or detail', (
        'including standalone and resumed entry', 'project-owned page destination',
        'explicit owner design agreement before setup-plan or detailed architecture plan production or continuation',
        'Page creation/interaction, silence, denial or cancellation is not consent',
        'Significant design changes renew agreement', 'reuse a settled grant')),
    ('brainstorm', '## Apply and return the decisions', (
        'Readiness is not design consent', 'self-contained interactive HTML high-level design',
        'explicit owner design agreement before detailed architecture plan production or continuation',
        'Preselection remains read-only', 'Significant design changes', 'Routine mechanics remain autonomous')),
    ('approval', '## Interactive design agreement before detail', (
        'project-owned self-contained interactive HTML high-level design',
        'before detailed architecture plan production or continuation',
        'approach, interfaces, dependencies and material risks',
        'purpose, inputs/outputs, boundaries and significant choices',
        'Executive bullets below the schematic', 'supported properties, tradeoffs/limits and necessary context',
        'without unverified capability or performance claims',
        'workflow approvals from data flow', 'proposed/unimplemented behavior from implemented behavior',
        'pointer and keyboard activation, readable mobile layout, Close and Escape dismissal and focus return',
        'Page creation, opening/clicking, silence, no answer, denial or cancellation is not consent',
        'Significant design changes update the page and renew agreement before affected planning resumes',
        'requirements approval, design agreement and final implementation approval distinct',
        'without repeating the same question', 'Routine mechanics remain autonomous',
        'No renderer, generator or framework is required', 'fresh session', 'NOT RUN')),
    ('tasks', '## Draft outcomes from the source', (
        'explicit owner design agreement', 'shown content identity, actual answer/scope and ordering',
        'Significant design changes renew agreement', 'current launch authority or shared routine permissions')),
    ('tasks_prompt', '## User Input', (
        'explicit design agreement before detailed architecture plan production or continuation',
        'Significant design changes renew agreement', 'reuse a settled grant', 'shared routine permissions')),
    ('plan_template', '## Design agreement provenance', (
        'project-owned self-contained interactive HTML high-level design',
        'explicit design agreement before setup-plan and detailed architecture plan production or continuation',
        'Page interaction, silence, denial or cancellation is not consent', 'Significant design changes')),
    ('tasks_template', '## Verification and review', (
        'explicit owner design agreement before detailed architecture plan production or continuation',
        'Significant design changes renew agreement', 'meaningful submitted completion evidence',
        'Preserve whole REQUIRED mappings', 'no startup eligibility')),
    ('spec_review_prompt', '## Design and task proof review', (
        'explicit owner design agreement before detailed architecture plan production or continuation',
        'Page interaction, silence, denial or cancellation is not consent',
        'significant design changes renew agreement', 'Static inspection is not real-browser proof',
        'whole REQUIRED mappings', 'actual evidence limits')),
)


def check_design_contracts(texts):
    errors = []
    for key, heading, clauses in DESIGN_CARRIERS:
        body = ' '.join(section(texts[key], heading).split())
        for clause in clauses:
            if ' '.join(clause.split()) not in body:
                errors.append(f'design-{key}: {heading} missing {clause!r}; restore the design gate before affected planning')
    # The gate must precede mutation-capable planning hooks and setup, not just final handoff.
    prompt = texts['plan_prompt']
    gate = prompt.find('## Design agreement before setup or detail')
    hooks = prompt.find('## Pre-Execution Checks')
    setup = prompt.find('run `.specify/scripts/bash/setup-plan.sh')
    if not 0 <= gate < hooks < setup:
        errors.append('design-order: Standard gate must precede planning hooks and setup-plan; move it before those operations')
    tiny = section(texts['tiny'], '## Write the what and how')
    if not 0 <= tiny.find('explicit owner design agreement') < tiny.find('Include only relevant detail'):
        errors.append('design-order: TinySpec agreement must precede detailed how; restore the page-first return')
    return errors


ISSUE_ASSOCIATION_CARRIERS = (
    ('tracker', '## Establish planner issue association', (
        'first understand the request and conduct needed owner brainstorming',
        'Before planned artifact production', 'complete open/closed overlap procedure',
        'Compare intent, problem, scope and primary evidence, not just titles',
        'Independently GET any exact match', 'qualified identity/URL, body and state',
        'open or closed exact match without duplicate or reopen',
        'actual target- and issue-create operation-scoped authority',
        'actually create the requested issue, independently read it back',
        'complete the separate problem-body quality review',
        'Do not ask a repeated routine creation question',
        'incomplete discovery or ambiguous effects cannot authorize another create',
        'review is unavailable, retain that issue identity', 'resume its review, never create another issue',
        'blocks association and planned artifact production', 'concrete corrective action',
        'never invent a fallback register', 'bare runtime tasks')),
    ('brainstorm', '## Apply and return the decisions', (
        'Readiness is not issue association or artifact-production authority',
        'before planned artifact production', 'confirmed creation with body-quality review',
        'qualified exact open/closed reuse without duplicate/reopen',
        'Missing prerequisites leave association pending', 'concrete corrective action',
        'not a fallback register', 'Needed dialogue remains available')),
)


def check_issue_association(texts):
    errors = []
    for key, heading, clauses in ISSUE_ASSOCIATION_CARRIERS:
        body = ' '.join(section(texts[key], heading).split())
        for clause in clauses:
            if clause not in body:
                errors.append(f'issue-{key}: missing {clause!r}; restore association before artifacts')
    return errors


ACCEPTANCE_TASK_CARRIERS = (
    ('tasks', '## Give each task sufficient proof', (
        'add one last task that depends on every other task',
        'No acceptance task: <reason>',
        'git diff --quiet HEAD -- <scenario paths> && <command>',
        'live, production-write, paid or destructive effect')),
    ('tasks', '## Encode the tasks for their consumer', (
        'never `[]` and never omitted',)),
    ('planner', '### Give producers the inputs their owners require', (
        'Require the source to state its acceptance intent',)),
    ('approval', '## Executive brief before approval', (
        'Acceptance task: ON (command ...) or OFF (reason ...)',)),
    ('spec_review_prompt', '## Definition of done and intent alignment', (
        'Check that the source states the acceptance intent',)),
    ('spec_review_prompt', '## Design and task proof review', (
        'check that the acceptance task is present and follows the task-generation template',)),
)


def check_acceptance_task(texts):
    errors = []
    for key, heading, clauses in ACCEPTANCE_TASK_CARRIERS:
        body = ' '.join(section(texts[key], heading).split())
        for clause in clauses:
            if clause not in body:
                errors.append(f'acceptance-{key}: {heading} missing {clause!r}; restore it in that section of the source')
    return errors


def check_contracts(texts):
    errors = (check_workflow_ownership(texts) + check_planner(texts["planner"])
              + check_design_contracts(texts) + check_issue_association(texts)
              + check_acceptance_task(texts))
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
    for key, heading in (("planner", "## Understand the work and choose depth"),
                         ("tiny", '## Write the what and how'),
                         ("brainstorm", "## Judge readiness"),
                         ("helper", '## Resolve architectural choices from evidence'),
                         ("tasks", '## Give each task sufficient proof')):
        require("parsimony-consumer", section(texts[key], heading), "parsimony.md")

    p = texts["planner"]
    require("task-concision", texts["tasks"],
            "State shared constraints once", "outcome-specific work and checks",
            "verify the affected operation's enforced limit at its consumer",
            "do not generalize a tool limit", "narrow remedy into a broader owner requirement")
    executor_intake = section(texts["tasks"], "## Make each outcome independently finishable")
    require("executor-producer-intake", executor_intake,
            "Before decomposing work in either route", "read the selected executor JSON yourself",
            "exact absolute path supplied", "valid worker model and effort",
            "not the planner, parent or producer profile or a remembered default",
            "valid selection needs no new owner question", "path is missing, ambiguous or unreadable",
            "worker model/effort is invalid or missing", "role, path and problem",
            "do not infer or substitute a binding", "owned paths, scope/exclusions, consumed interfaces, earlier producers")
    require("executor-tiny-handoff", section(texts["tiny"], '## Return for review and separate tasks'),
            "planner's selected executor JSON path unchanged to the task producer",
            "Task-generation owns reading it", "missing-path/assignment correction",
            "does not select or copy runtime bindings")
    reject("retired-routing-leftover", "\n".join((p, texts["tasks"], texts["tiny"])),
           "qualified seed rubric", "residual_reasoning", "owner-selected batch routing")
    for label, key, selector, clauses in ACCEPTED_ADAPTER_CARRIERS:
        require(label, operational_carrier(texts[key], selector), *clauses)
    require("draft-editing", section(texts["approval"], "## Bounded mechanical corrections"),
            "Ordinary drafting is not submitted-artifact correction",
            "without a supervisor decision", "Once submitted, defects follow")
    prompt = texts["spec_review_prompt"]
    require("intent-review-prompt", prompt,
            "TinySpec\nor Standard", "primary focus is fidelity",
            "relevant user-intent evidence", "affected specification section", "concrete consequence",
            "correction or\nowner question", "actual problem, intended beneficiary, desired behavior, boundaries, explicit\nexclusions, and observable completion",
            "omitted requirements, distorted meaning", "invented scope, unnecessary restrictions",
            "technical solutions that fail to deliver", "explicit user requirements",
            "necessary derived choices", "revisitable assumptions", "**zero findings**",
            "no numerical discovery cap", "original user request and actual owner clarifications/decisions",
            "Exclude producer conclusions", "not approval", "no writes, implementation changes")
    require("review-consequences", prompt,
            "simplest specification that achieves the user's goals", "supporting\nmeans, not independent products",
            "removal or simplification", "actual consumers, including coexistence and rollback",
            "retrieve the missing relevant content with smaller reads", "not complete intake",
            "state what is unreviewed", "evidence supporting coverage, downstream clarity and simplicity",
            "without a separate matrix", "preserve justified zero findings")
    b = texts["brainstorm"]
    require("brainstorm", b, "NO_BRAINSTORM_NEEDED", "BRAINSTORM_NEEDED", "no more than three items",
            "one agenda item at a time", "exactly the recorded decisions", "Preselection", "read-only",
            "session history", "Only with selected-production", "owner's rationale")
    require("brainstorm-parent-gate", b.split("## Judge readiness", 1)[0],
            "parent conducts assessment and dialogue", "owner-launched model and effort",
            "neither requires a child call or a saved assignment")
    require("brainstorm-parent-gate", section(b, "## Resolve the material questions with the owner"),
            "missing delegation alone does not block parent dialogue")
    require("brainstorm-assignment", section(b, "## Apply and return the decisions"),
            "Only with selected-production or legacy-repair write authority",
            "Resolve `brainstorm-application`", "[saved-assignment contract](../planner/SKILL.md#saved-planner-assignments)",
            "shared `brainstorming` assignment", "exact binding unchanged in the brief and dispatch",
            "permitted and callable at dispatch", "stops only application", "focused correction question",
            "no recommendation, inferred substitute or fallback binding", "Do not resolve `brainstorm-assessment` for the parent")
    reject("brainstorm-retired-routing", b, "qualified seed rubric", "six applicable factors",
           "family/effort", "Family and Effort rationales", "shared readiness conjunction",
           "owner-selected profile")
    for key in ("planner", "brainstorm", "helper"):
        reject("obsolete-planning-class", texts[key], "sonnet-class", "opus-class")
    require("tiny-source", texts["tiny"], "explicit TinySpec selection/preparation authorization",
            "Outcome and scope", "Decisions and constraints", "Approach", "Acceptance", "Risks and deferrals",
            "do not embed an implementation checklist", "separate task file is mandatory",
            "TinySpec needs no SpecKit", "one combined source/task approval",
            "fresh independent read-only specification review", "On standalone entry, return to planner",
            "No separate pre-task TinySpec source approval is required")
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
    require("batch-legacy", a, "inadequate REQUIRED contracts", "producing review/approval gate", "renewed affected approval")
    require("batch-helper", texts["helper"], "applicable guidelines")
    require("batch-source", texts["tiny"], "task-local REQUIRED checks and worker/reviewer")
    require("batch-brainstorm", texts["brainstorm"], "does not select runtime bindings")
    t = texts["tasks"]
    require("task-contract", t, "SpecKit adapter", "direct adapter", "separate source and tasks file",
            "nonempty string `id`", "Optional `depends`", "IDs must be unique",
            "references must exist", "not cycle", "File order", "do not regenerate old tasks")
    helper_adapter = section(texts["helper"], '## Arrange the bounded planning pass')
    helper_pass = section(texts["helper"], '## Produce and inspect the plan')
    require("adapter", helper_adapter, "planner-managed Standard `plan_create`", "approved specification and approval evidence",
            "SpecKit planning: UNAVAILABLE", "do not write a generic plan", "usable in the delegated context")
    require("adapter", helper_pass, "one same-session pass", "Do not direct the caller to create the plan again")
    require("helper-assignment", helper_adapter,
            "`standard-plan-helper` saved assignment", "exact binding unchanged",
            "permitted and callable at dispatch", "invalid or unavailable", "focused owner-correction question",
            "do not substitute or run a local pass", "observed binding/effort separately; unknown stays unknown")
    require("helper-assignment", helper_pass, "Review/fix the approved specification", "once to create the plan", "Review/fix the produced plan")
    reject("helper-retired-routing", helper_adapter, "Sol/medium", "Sol family",
           "standalone local fallback", "separate-review policies", "fallback may bypass")
    c = texts["coordinator"]
    require("intake", section(c, "## Load and Verify"), "exactly six linter checks",
            "An empty", "Optional context stays intact")
    require("validation-tasks", section(t, '## Give each task sufficient proof'), "smallest relevant project check",
            "optional task context", "not universal acceptance boilerplate", "real outcome")
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
    t_research = section(texts["tiny"], '## Resolve the approach from evidence')
    require("research-tiny", t_research, "[dependency research contract](../planner/references/dependency-research.md)",
            "Before consequential dependency choices", "references are readable",
            "reuse/skip/refresh decision", "actual dependency/version evidence", "recollection cannot replace required evidence",
            "persist reusable guidance in the discovered technical owner and necessary discovery link before claiming readiness",
            "within verified write bounds", "Standalone entry verifies those bounds itself",
            "stop affected design", "impact, allowed bounds and outstanding validation", "do not defer automatically")
    source_contract = section(texts["tiny"], '## Write the what and how')
    require("research-tiny-traceability", source_contract,
            "Distinguish documented recommendations, repository-derived decisions and assumptions",
            "Trace evidence to the implementation constraint and check", "assumptions defined validation")
    research_pos = texts["tiny"].find('## Resolve the approach from evidence')
    approach_pos = texts["tiny"].find('## Write the what and how')
    if research_pos < 0 or approach_pos < 0 or research_pos > approach_pos:
        errors.append("research-order: TinySpec research must precede compact approach production")
    h_pre = section(texts["helper"], '## Resolve architectural choices from evidence')
    require("research-helper", h_pre, "[dependency research contract](../planner/references/dependency-research.md)",
            "Before consequential architecture/plan decisions", "references are readable",
            "within the write bounds above", "standalone production too",
            "No recollection-based completion or automatic deferral", "return exact gaps, affected decisions and needed authority",
            "Do not assume the caller already applied them on standalone entry")
    require("research-helper-adapter", helper_adapter, "Required write authority cannot be inferred from tooling")
    require("research-helper-adapter", helper_pass, "Changes to approved specification content, including research-driven changes",
            "renewed specification approval gate", "standalone entry uses its owner gate")
    h_boundary = helper_adapter
    require("research-boundary", h_boundary,
            "Canonical research-document and necessary discovery-link writes need additional explicit bounded permission",
            "observed destinations, allowed changes and prohibited operations",
            "no arbitrary documentation or product-code edits", "Required write authority cannot be inferred from tooling",
            "Standalone entry must verify equivalent Standard planning/preparation authority")
    require("research-boundary", h_pre, "Translate evidence into plan constraints and observable verification")
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
    entries = (("tiny", '## Establish the source to write', "unified-memory-tiny"),
               ("tasks", '## Draft outcomes from the source', "unified-memory-tasks"),
               ("helper", '## Arrange the bounded planning pass', "unified-memory-helper"))
    for key, heading, label in entries:
        body = section(texts[key], heading)
        if key in ("tasks", "tiny", "helper"):
            require(label, body, "Memory Handling", "verified unified index", "nonblocking",
                    "explicit owner guidance and gotchas", "task-local REQUIRED check",
                    "worker/reviewer briefs")
            require(label, body, "retrieval and authority rules" if key == "tasks" else "retrieval and write safeguards" if key == "tiny" else "retrieval, write and concurrency safeguards")
    require("unified-memory-owner", texts["memory"],
            "One verified", "two distinct evidence kinds", "Owner guidance",
            "Read the whole associated index first", "clear, explicit, future-directed user feedback",
            "Explanation-only questions, ordinary implementation approval", "no feedback write nothing",
            "No routine bookkeeping")
    require("unified-memory-routing", section(c, "## Execute and Integrate"),
            "No arbitrary workflow", "Do not autonomously loop expensive failed runs")
    require("unified-memory-intake", section(c, "## Load and Verify"),
            "Missing memory or STATE is nonblocking", "no automatic summaries/indexes",
            "execution-time feedback/routing")
    require("runtime-authority", section(c, "# Coordinate Implementation"),
            "one LangGraph controller", "SQLite graph checkpoints hold", "not automatic acceptance",
            "sequential by", "explicitly owner-directed path-disjoint workers",
            "sibling mutations quiescent", "never silent", "conversion or replay")
    for key in ("planner", "tiny", "tasks", "helper", "memory", "coordinator", "adoption"):
        reject("unified-memory-unsafe-" + key, texts.get(key, ""),
               "Automatically initialize coordination memory", "Write a run SUMMARY on completion",
               "Refresh the coordination index after every task", "Reflect at blocked pause",
               "Commit evidence separately before the next task", "Infer lessons from failed runs",
               "Automatically create STATE.md", "Update STATE after child-ID return", "Remove finished STATE items")
    # Bounded checks of changed instruction carriers, not a production audit/router.
    for label, key, heading, clauses in AUTHORED_COMMAND_CARRIERS + VERIFICATION_CARRIERS:
        require(label, section(texts.get(key, ""), heading), *clauses)
    for label, key, heading, clauses in COMPOSED_CARRIERS:
        require(label, section(texts.get(key, ""), heading), *clauses)
    for label, key, heading, clauses in RISK_CARRIERS + BOUNDARY_CARRIERS + LINKAGE_CARRIERS:
        require(label, section(texts.get(key, ""), heading), *clauses)
    for label, key, selector, clauses in ATOMIC_OUTCOME_CARRIERS + RISK_HANDOFF_CARRIERS:
        require(label, operational_carrier(texts.get(key, ""), selector), *clauses)
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
    ('composed-tasks', 'tasks', '## Give each task sufficient proof', (
        'separate green components cannot establish a risky boundary',
        'smallest composed check of the final observable, order or custody',
        'Reuse a focused check that already observes it',
        'first boundary with the necessary prerequisites',
        'only for an independently necessary prerequisite',
    )),
    ('composed-adapters', 'tasks', '## Return a checked task artifact', (
        'Worker briefs carry work-specific checks, exclusions and material permission boundaries',
        'mappings established above',
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
    ('risk-tiny', 'tiny', '## Resolve the approach from evidence', (
        '[early risk reduction](../planner/references/early-risk-reduction.md)',
        'reason to select or omit a proof',
        'necessary dependencies',
        'expected findings and tested limits',
        'production acceptance and actual execution gates',
        'actual-helper tests',
        'consequential unknown',
        'applicability/lifetime and disproof/renewal rules',
        'Task-generation decides proof placement',
        'not a task chain',
        'does not authorize execution',
        'references are readable',
        'direct/standalone entry',
    )),
    ('risk-tiny-return', 'tiny', '## Return for review and separate tasks', (
        'research and risk results above',
        'limits, permission gaps and affected approval renewals',
        'verification needs and unresolved blockers',
    )),
    ('risk-helper-preflight', 'helper', '## Resolve architectural choices from evidence', (
        '[early risk reduction](../planner/references/early-risk-reduction.md)',
        'references are readable',
        'missing-install report',
        'standalone entry',
        'Planning schedules proof, not its execution',
    )),
    ('risk-helper-adapter', 'helper', '## Resolve architectural choices from evidence', (
        'justified proof selection/omission',
        'necessary dependencies',
        'Task-generation owns decomposition and task sizing',
    )),
    ('risk-helper-plan', 'helper', '## Produce and inspect the plan', (
        'sequencing, dependencies',
        'verification',
        'evidence-to-constraint-to-check mappings',
        'evidence rules above',
    )),
    ('risk-helper-return', 'helper', '## Return the checked outputs', (
        'research/risk results above',
        'verification needs and remaining capability/permission gaps',
        'not an embedded task chain',
    )),
    ('risk-tasks', 'tasks', '## Give each task sufficient proof', (
        '[early risk reduction](../planner/references/early-risk-reduction.md)',
        'both routes, including direct entry',
        'missing-install report',
        'selection and proof-lifetime rules',
        'ordinary actual-helper tests',
        '**[PROTOTYPE]**',
        'one consequential question',
        'script code and actual observed execution evidence',
        'Planning schedules proof, not execution without authority',
    )),
    ('risk-task-review', 'tasks', '## Return a checked task artifact', (
        'outcome/proof rules above in either route',
        'actual proof consumption',
        'existing producing review and coordinator handoff',
    )),
)


LINKAGE_CARRIERS = (
    ('finish-linkage', 'finish', '## Issue-linked delivery', (
        'PR → qualified delivery issue and issue → qualified PR, regardless of trace host',
        'A PR-hosted trace also needs issue → every confirmed trace part',
        'Reuse verified body or comment links',
        'actual run/target/`link_comment` authority',
        'incomplete pages, missing authority or uncertain readback mean incomplete linkage, never success',
        'When a delivery PR is discovered after finish, establish only missing reciprocal links',
        'refer to the already confirmed trace',
        'Do not republish the trace, rerun implementation or reopen review',
        'Late linkage does not change the reviewed revision, owner acceptance or closure authority',
        'Trace/link comments do not require problem-body quality review',
        'a substantive problem-body change still does',
        'Do not create a PR, push, edit issue/PR bodies or change state',
    )),
    ('tracker-linkage', 'tracker', '## Confirm delivery issue/PR links', (
        'Independently GET the issue identity and each PR\'s issue and pull-request identities',
        'Read the current bodies and all comment pages',
        'Every delivery PR must link its qualified issue and the issue must discover every delivery PR, regardless of trace host',
        'issue links to every confirmed trace part',
        'Read back retained trace parts in full',
        'Reuse verified body/comment links',
        '`link_comment` operation-scoped authority for each destination',
        'reconcile all destination pages and exact candidate bodies/identities',
        'a collision or incomplete scan stops new comments',
        'Late PR discovery establishes only missing reciprocal links',
        'no trace resend, implementation replay or reopened review',
        'partial effects or failed readback are incomplete linkage, not success',
        'Link/trace comments need no separate problem-body quality reviewer',
        'Link confirmation is not owner acceptance or closure authority',
        'Do not create PRs, push, replace issue/PR bodies, close or reopen',
    )),
)


BOUNDARY_CARRIERS = (
    ('task-boundaries', 'tasks', '## Make each outcome independently finishable', (
        'one bounded behavior or interface per task',
        'ordinary tests, evidence, relevant documentation, review preparation and routine teardown with the outcome',
        'independently necessary deliverable, prerequisite, gate, resource boundary or material context incompatibility—not a phase name',
    )),
    ('task-review-boundaries', 'tasks', '## Return a checked task artifact', (
        'outcome/proof rules above',
        'task granularity, necessary support',
        'does not replace independent review or permit upstream requirement changes',
    )),
)


# Contract carriers only: they preserve the six intake-linter rules and do not score tasks.
ATOMIC_OUTCOME_CARRIERS = (
    ('atomic-creator', 'tasks', '## Make each outcome independently finishable', (
        'acceptance that can pass using completed prerequisites',
        'without unfinished downstream implementation',
        'Split a milestone at independently testable seams',
        'Established cross-system wiring may also stay one task',
        'focused test and support work establish the final observable',
    )),
    ('atomic-direct-review', 'tasks', '## Return a checked task artifact', (
        'outcome/proof rules above in either route, including direct tasking',
        'task granularity, necessary support',
    )),
)


# Material risk handoff uses existing review/brief carriers, not a new schema or admission gate.
RISK_HANDOFF_CARRIERS = (
    ('risk-task-handoff', 'tasks', '## Return a checked task artifact', (
        'task-specific material execution risks or prerequisites',
        'affected task',
        'observed evidence versus unknowns',
        'next investigation, mitigation or necessary permission',
        'coordinator must consume these findings before affected worker reliance',
        'later discoveries use the same handoff',
        'No new risk schema',
        'capability, access, paid, data or external authority',
        'affected operation and corrective action',
        'unrelated safe work continues',
    )),
    ("risk-coordinator-prepare", "coordinator", "## Prepare Approved Execution", (
        "Before affected worker reliance", "consume final-review/handoff material risk findings", "investigate or\nprepare routine prerequisites within authority",
        "brief workers with usable interfaces/findings", "evidence limits, and remaining gates", "later discoveries receive\nthe same treatment",
        "unavailable capability, access, paid,\ndata, or external boundary", "exact affected operation and corrective action", "blocks only\nthat work",
    )),
    ("risk-coordinator-triage", "coordinator", "## Question triage", (
        "routine early worker or\nreviewer return is a diagnosis event, not completion or owner debugging", "inspect its invocation,\nunfinished scope, actual checks, and retained effects",
        "supported history/resume or evidence-only reassessment paths", "never blindly retry an\nunchanged expensive failure", "initial-plus-two same-task/session allowance", "compact diagnosis context", "evidence-only review reassessment uses the existing retained evidence", "never a task replay", "Unknown cause or a real permission boundary stops",
    )),
    ("risk-coordinator-review", "coordinator", "## Review and Acceptance", (
        "routine\nreviewer early return or evidence gap as a diagnosis/recovery event", "not completion or an owner-debugging\nrequest",
        "supported targeted resume or evidence-only reassessment path", "Do not repeat an\nunchanged expensive failed review", "stops only the affected continuation",
    )),
)


# Actual producer/consumer inputs, not incidental summary keywords.
DELEGATION_CARRIERS = (
    ("delegate-recovery", "approval", "## Transition and invalidation table", ("Delegate uncertain or substantive artifact corrections", "originating producer context", "fresh bounded correction delegate", "No parent artifact authoring", "substantive task-level or upstream repair, including legacy recovery", "unauthorized delegation stops", "fallback or full transcript handoff")),
    ('delegate-helper', 'helper', '## Arrange the bounded planning pass', (
        'separate fresh bounded context',
        'coordinating caller does not author fresh artifacts or make substantive repairs',
        'uncertain or substantive corrections return to suitable originating producer context or a fresh bounded correction delegate',
        'unauthorized delegation stops',
        '`standard-plan-helper` saved assignment',
        'do not substitute or run a local pass',
    )),
)

AUTHORITY_CARRIERS = (
    ('quality-tiny-producer', 'tiny', '## Write the what and how', (
        'At source creation, read and apply the',
        '[SDD quality guidance]',
        'if unreadable, stop',
        'complete relevant behavior, approach, constraints and observable acceptance in this source',
        'Later tasks consume this source, not SDD as requirements input',
        'governing instructions, memory and actual permission/safety boundaries still apply',
    )),
    ('truth-helper', 'helper', '## Produce and inspect the plan', (
        'specification is requirements truth',
        'plan provides derived architecture and sequencing',
        'Do not forward or reread SDD as direct requirements input',
        'Governing instructions, memory and actual permission/safety boundaries still apply',
    )),
    ('truth-speckit-adapter', 'tasks', '## Draft outcomes from the source', (
        '**SpecKit adapter**',
        'specification as requirements truth',
        'approved plan for derived sequencing only',
        'create-only',
        "Both routes use the source's criteria, not SDD",
        'repository instructions, governing principles',
    )),
    ('truth-direct-adapter', 'tasks', '## Draft outcomes from the source', (
        '**direct adapter**',
        'owner-authorized durable TinySpec or legacy requirement',
        "Both routes use the source's criteria, not SDD",
        'repository instructions, governing principles',
    )),
    ("brief-coverage", "approval", "## Executive brief before approval", ("concrete included scope", "Every actual ordered plan stage separately", "meaningful outcome", "Every actual task ID separately", "execution order", "Never truncate beyond six, merge IDs/stages", "catch-alls or empty headings", "TinySpec has no plan; specification-only approval", "This adds no plan approval gate", "Renewals regenerate the complete brief from current artifacts", "before calling `ask_user`")),
)


AUTHORED_COMMAND_CARRIERS = (
    ('authored-command-shared', 'tasks', '## Encode the tasks for their consumer', (
        'authored deterministic required command once',
        '`checks`, `check`, or `required[].check` field',
        'Keep semantic criteria as prose',
        'never compile prose into shell',
        'leave absent optional checks absent',
    )),
    ('authored-command-tiny', 'tiny', '## Return for review and separate tasks', (
        '[task-generation direct adapter](../task-generation/SKILL.md)',
        'Task-generation owns',
        'executable check fields',
        'Pass authored source checks and semantic criteria to that owner for executable handoff',
    )),
    ("authored-command-standard", "tasks_prompt", "## Task Generation Rules", (
        "authored deterministic", "existing executable fields once", "semantic criteria stay prose", "optional absent checks stay absent",
    )),
    ("authored-command-template", "tasks_template", "## Verification and review", (
        "authored deterministic required", "existing executable field once", "semantic criteria remain prose", "optional absent\nchecks remain absent",
    )),
)


VERIFICATION_CARRIERS = (
    ('verification-practical', 'tasks', '## Give each task sufficient proof', (
        'observes the changed behavior, not generic green output',
        'captures the selected ID at the consumer unchanged',
        'mappings through both routes unchanged',
        'not on ordinary coding tasks',
    )),
    ('verification-legacy', 'tasks', '## Encode the tasks for their consumer', (
        'File order and ID numbering do not determine execution order',
        'do not regenerate old tasks',
        'Existing `required` check mappings remain consumed',
    )),
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
