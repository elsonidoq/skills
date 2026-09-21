---
name: epics-manager
description: Use when preparing or resuming any epic/spec file in OpenCode before handing reviewed spec/plan/tasks artifacts to coordinate-implementation.
---

# Epics Manager

Use `/epics-manager <epic-file> [selector]` — for example `/epics-manager
docs/poc/01-recall-audit-and-fix.md` or `/epics-manager docs/poc/epics.md 2`.
There is no default epic file; the first argument is always required. This
skill prepares reviewed artifacts; it does not implement the product.

Pipeline (fixed after constitution initialization, no per-project variation without an
explicit owner decision):

```
brainstorm_gate → [epic_brainstorm → epic_brainstorm_fix] → spec_create (sonnet)
  → plan_create (opus) → tasks_create (sonnet) → overall_review → done
```

There is no `epic_critique`/`epic_fix`, `spec_critique`/`spec_fix`, `plan_critique`/`plan_fix`,
or separate `tasks_critique`/`tasks_fix`. `epic_brainstorm_fix` is the epic's only fix
pass, applying exactly the owner's brainstorm decisions — nothing else edits the epic.
`plan_create` does create-review-fix as **one** agent turn: the same agent that finds an
issue fixes it. `tasks_create` is **create-only** — the agent writes the best task list it
can and does not self-critique or fix. A single `overall_review` stage then runs
`/speckit.analyze` across spec, plan and tasks: core spec/plan issues go to the owner via
the Flagged-item protocol, while task-level issues are fixed autonomously and reported as a
brief. See "Flagged-item protocol" for how owner input is captured.

## Runtime and delegation

This is a global skill (`~/.config/opencode/skills/epics-manager/SKILL.md`),
available in any OpenCode project via opencode's native global skill discovery —
no project-local wrapper command exists. Load it with the `skill` tool by name,
or invoke `/epics-manager <epic-file> [selector]` in prose.

The installed Speckit OpenCode commands own stage instructions:

| Stage | OpenCode command | Instruction file |
| --- | --- | --- |
| Constitution preflight | `/speckit.constitution` | `.opencode/command/speckit.constitution.md` |
| Spec creation | `/speckit.specify` | `.opencode/command/speckit.specify.md` |
| Clarification (optional, on request only) | `/speckit.clarify` | `.opencode/command/speckit.clarify.md` |
| Planning | `/speckit.plan` | `.opencode/command/speckit.plan.md` |
| Tasks | `/speckit.tasks` | `.opencode/command/speckit.tasks.md` |
| Analysis | `/speckit.analyze` | `.opencode/command/speckit.analyze.md` |
| Implementation handoff | `/speckit.implement` | `.opencode/command/speckit.implement.md` |

Within this orchestration, read and follow the matching command body with explicit
stage input in place of `$ARGUMENTS`. Slash commands are user entry points, not shell
executables. Do not launch nested `opencode run` sessions to simulate a stage.

**Model binding.** Named subagents with pinned models are configured globally in
`~/.config/opencode/opencode.json` under `agent.*` (not per-project) — in particular
`sonnet` → `anthropic/claude-sonnet-5` and `opus` → `anthropic/claude-opus-5`. Use
the `task` tool with `subagent_type: "sonnet"` or `subagent_type: "opus"` exactly as
specified per stage below; do not substitute `"general"` for a stage that names a
model, and do not invent a model identifier — if a named subagent is ever missing
from that config, stop and tell the user rather than guessing a replacement.

**Task model tags.** Downstream of this pipeline, `plan_create` records a model class
(`sonnet` or `opus`) for every phase/task, and `tasks_create` tags each task `[sonnet]`
or `[opus]`. `coordinate-implementation` dispatches by that tag and keeps every batch
homogeneous by class. Use only these two classes; do not invent a tier.

Give each delegated agent one stage, the reading contract below, exact write scope,
and the previous handoff. Use a fresh `task` call for each **new** stage; when a
stage needs to apply owner answers to its own prior output (see "Flagged-item
protocol"), resume that same delegated task with its `task_id` instead of spawning a
new one — the agent that found the issue already has the context to fix it.

The coordinator (this session) owns all user dialogue through OpenCode's `question`
tool — delegated subagents cannot ask. Use its `questions` array with `header`,
`question`, and `options` (`label`/`description`); the tool adds "Other" automatically.
If `question` is unavailable or the session is noninteractive, save state and ask one
concise question in the final response, then resume when answered.

## Resolve the epic before setup or state lookup

Input is `<epic-file> [selector]`, always resolved from the repository root:

```sh
python3 ~/.config/opencode/skills/epics-manager/scripts/resolve_epic.py <epic-file> [selector]
```

Only unfenced, level-one `#` headings are epics/specs. A missing selector is
automatic only when exactly one such heading exists in the file; otherwise list the
candidates and ask. The helper returns the canonical heading, number, normalized
slug, stable state key, and inclusive line bounds — never edit past those bounds,
even inside a multi-epic bundle file.

Echo the resolved heading back to the user before running the first stage. Re-resolve
on every resume; never reuse stale line numbers after the file has been edited.

### Constitution initialization

Before bootstrap, ensure the repository has been initialized with SpecKitToolkit. The
required initialization assets are `.specify/`, every Speckit command file named in the
table above, `.specify/templates/spec-template.md`, `plan-template.md`,
`tasks-template.md`, `checklist-template.md`, and `.specify/scripts/bash/common.sh`,
`check-prerequisites.sh`, and `setup-plan.sh`. If any is missing, tell the user to run
`specify init .` from the repository root. Do not run it for them. Then wait for the
user to confirm completion and re-check the assets; if any remain absent, stop and
report the missing paths.

Check `.specify/memory/constitution.md`. A file is valid only when it exists, contains
substantive project-specific principles rather than headings or boilerplate alone, and
contains no unreplaced template markers. Treat `[PROJECT_NAME]`, `[PRINCIPLE_…]`, and
all unreplaced template markers as a template. A valid constitution skips this section permanently
and proceeds to Bootstrap.

If the constitution is missing or still a template, conduct a short interview through
the `question` tool before any Epic stage. Ask only what is needed to establish:

1. The project's purpose, intended users, and primary outcome.
2. The non-negotiable engineering or product principles that should govern trade-offs.
3. The delivery, quality, security, privacy, compatibility, or operational constraints
   that must not be compromised.

Summarize answers as `## Constitution interview` with one concise bullet per answer.
Then spawn one **sonnet** sub-agent (`task` tool, `subagent_type: "sonnet"`) with the
following instruction:

```
Create the project constitution using /speckit.constitution.

Read `.opencode/command/speckit.constitution.md` and follow its command body with the
Constitution interview below as explicit stage input in place of `$ARGUMENTS`. Write
only the constitution artifact required by that command; do not create a spec, plan,
tasks, or edit the Epic.

## Constitution interview
[paste the coordinator's summarized answers]
```

When the sub-agent returns, re-read `.specify/memory/constitution.md`. Continue only
when it passes the validity check; otherwise stop and report that constitution
initialization did not produce a usable file. Do not repeat the interview or retry the
sub-agent automatically. Once a usable constitution exists, this initialization never
runs again for that project. Do not seed it from a specific source file; that coupling
caused the previous
   version of this skill to assume `epics_mvp.md` always exists.

## Bootstrap (run once per state file)

1. Read `AGENTS.md` and the target epic/spec section. Inspect `git status`; preserve
   existing edits and use the current checkout/worktree — do not require a new
   worktree merely to run this skill (see `using-git-worktrees` conventions for when
   isolation is actually warranted).
2. Verify the command files listed above and `.specify/scripts/bash/common.sh`,
   `check-prerequisites.sh`, `setup-plan.sh` exist.
3. Confirm `.specify/memory/constitution.md` is valid. Constitution initialization
   must already have created it when needed; if it is missing or still a template,
   stop and report that the constitution preflight was not completed.
4. Do not require `specs/`, `feature.json`, spec, plan, or tasks to exist yet for a
   fresh epic. Do not run product tests as a planning baseline.

Prerequisite checks are stage-specific, run from the repository root with quoted
paths:

- Before `plan_create`: `check-prerequisites.sh --json --paths-only`, plus verify
  `spec.md` exists and belongs to the target.
- Before `tasks_create`: `check-prerequisites.sh --json`, plus the spec check above.
- Before `done`: `check-prerequisites.sh --json --require-tasks --include-tasks`,
  plus the spec check above.

`setup-plan.sh` copies the plan template: only invoke it for a fresh plan; on resume,
read the existing `plan.md` and follow the planning instructions without recopying.

## Durable state

`.opencode/epics-workflow/<state-key>.json` (created when needed; key from the
resolver, not the raw selector, so aliases resume the same workflow).

```json
{
  "schema_version": 2,
  "epic_file": null,
  "epic_heading": null,
  "epic_number": null,
  "worktree_path": null,
  "spec_dir": null,
  "stage": "brainstorm_gate",
  "pending_brainstorm": null,
  "pending_brainstorm_answers": null,
  "pending_flagged": null,
  "pending_answers": null,
  "pending_task_id": null,
  "pending_handoff": null,
  "decisions": [],
  "deferrals": []
}
```

Persist before asking a question and after each stage completes. If an existing
state file has no `schema_version` or `schema_version: 1`, it predates this pipeline
redesign (it may reference retired stages such as `epic_critique`, `spec_fix`,
`planning_gate`) — tell the user this state is from the old pipeline and ask whether
to discard it and restart at `brainstorm_gate`, or treat the existing `spec_dir` (if
any) as already-created input to `plan_create`. Do not attempt automatic migration.

**Interrupted-flag recovery:** if the loaded stage is `plan_create` or `overall_review`
and `pending_flagged` is non-null while `pending_answers` is null, the previous
session ended after the agent flagged items but before the owner answered. Recover:
tell the user "Resuming — re-presenting flagged items," then re-run the **Flagged-item
protocol** using the existing `pending_flagged` and `pending_task_id`.

**Interrupted-brainstorm recovery:** if the loaded stage is `epic_brainstorm` and
`pending_brainstorm_answers` is null, re-run `epic_brainstorm` using the existing
`pending_brainstorm` agenda.

## Reading and source contract (every stage)

Every delegated agent's prompt instructs it to:

1. Read `<epic-file>` (the section under `<epic-heading>` when the file bundles
   several; ignore the others).
2. Read that section's `Settled decisions` / `Non-obvious facts` (or a spec-file's
   equivalent "Settled requirements" / "Global constraints" sections) and **reflect
   them verbatim — do not re-derive them**.
3. Read every document the target section names as a source of truth. Optional
   references are read if present; record absence without inventing content.
4. Read `.specify/memory/constitution.md` (non-negotiable principles — never dilute
   or silently reinterpret) and `AGENTS.md` (its `<!-- SPECKIT START -->`/
   `<!-- SPECKIT END -->` markers point at the current active plan, if any).
5. Treat the target's `Settled decisions`/`NOT included`/`Acceptance criteria` (or
   equivalent) as hard constraints; violating one is a defect, not a style choice.

If the target cites another epic/spec or an ADR as a precondition, read it as a
source; changing it is an explicit coordinated decision, not an incidental fix made
while working the current target.

Each stage's prompt embeds this by reference as "the Reading contract."

## Flagged-item protocol

Replaces the old create → critique → fix round trip. Applies to **every** remaining
point in the pipeline where a delegated agent might otherwise want to ask the
owner something: `plan_create`'s review of the spec, and `overall_review`'s
cross-artifact review of spec, plan and tasks. `tasks_create` is create-only and does
not flag; `overall_review` flags only core spec/plan issues and resolves task-level
findings itself.

**The test — only two kinds of things get flagged:**

- **(a) Friction/complexity:** resolving it one way over another would add scope,
  an extra approval gate, a new abstraction, or otherwise measurably increase what
  gets built or how it gets built.
- **(b) Spec deviation:** it is a genuine ambiguity in, or departure from, the
  target's own stated intent, settled decisions, or acceptance criteria — a
  product-level question, not an implementation one.

**Never flag:** task ordering or grouping, which file to touch first, batch sizing,
internal refactor/naming choices, how to fix a code-internals defect, or any other
detail of *how* the work gets arranged or executed. The agent resolves these itself
and reports what it did in its own output — it does not ask, and the coordinator
does not surface them as questions.

**Within the two flaggable categories, still auto-accept when there is only one
real option:** if the agent's own recommendation has no genuine alternative (the
question would have exactly one option besides the tool's automatic "Other"), the
agent applies it directly and lists it as auto-applied in its output rather than
holding it open — do not hold something open merely because it is technically in
category (a)/(b).

**Agent-side behavior (part of every `plan_create`/`tasks_create` prompt):**
Apply your own best default for every item, including flagged ones, so the artifact
is always in a finished, usable state — never leave a placeholder or block on an
answer. Then report, in this shape:

```
## Fixes applied
[everything you resolved yourself: spec/task defects, ordering, coverage gaps —
one line each, no owner input needed]

## Flagged for owner
[omit this section entirely if nothing qualifies]
For each item:
- What you found and the default you applied
- Why it's flagged: (a) adds friction/complexity, or (b) spec deviation
- The genuine alternative, if changing the default would mean something different
```

**Coordinator-side behavior:** parse the agent's output.
- No "## Flagged for owner" section, or it's empty → advance to the next stage
  immediately, no `question` call.
- Non-empty → convert each item into a question via the `question` tool (1–4 per
  call, recommended = the agent's applied default, labeled "(Recommended)"; batch
  sequential calls if more than 4). Save `pending_flagged` and the agent's
  `task_id` as `pending_task_id` before asking, `pending_answers` after collecting
  them. If every answer confirms the agent's default, no further agent call is
  needed — just record the confirmation and advance. If any answer overrides a
  default, **resume the same task via `pending_task_id`** with the overrides
  formatted as `## [item]\nAnswer: [chosen option] — [detail]`, instructing it to
  apply them and finalize the artifact(s); capture the updated handoff, then
  advance.

Scan every answer round for deferral language ("defer", "later", "post-MVP", "out
of scope") and record it in `deferrals`; append a `## Deferrals` section to the
resume prompt if present, asking the agent to add a `### Deferred` note.

## Handoff context protocol

Every create/review/fix-capable agent's prompt ends with:

```
## Handoff context (required)
At the very end of your response, output a section titled "## Handoff context".
Include:
- Key decisions you made and the reasoning behind them
- Trade-offs taken and what was intentionally deferred
- Uncertainties or fragile areas the next agent should scrutinize
- Anything non-obvious that would be lost if only the artifact files were read
Be specific and concise — this is the only way context survives to the next stage.
```

Capture it into `pending_handoff`. If non-null, prepend the next stage's prompt with:

```
## Context from previous stage
[paste pending_handoff verbatim]

---
```

## Stakeholder communication

The user is a product and technical stakeholder but is not immersed in the
artifacts. Every question must be self-contained — explain what each reference
points to before asking about it.

---

## Stages

### `brainstorm_gate`

Spawn a **general** sub-agent (`task` tool, `subagent_type: "general"`):

```
## Goal
Decide whether this epic/spec needs a brainstorming / owner-direction session BEFORE
any spec work begins. Brainstorming is warranted ONLY when the target cannot be
specced as-is because of:
(a) open-ended design — a generative "what should this even be?" question not
    derivable from the target text or its sources of truth;
(b) a product-direction decision the owner must make;
(c) a technical decision with materially different trade-offs where the wrong pick
    forces a re-plan later.
Do NOT trigger for bounded clarifications or decisions with an obvious default —
those are resolved later by plan_create/tasks_create's own judgment, or flagged per
the Flagged-item protocol if they qualify. Bias toward NO: a target whose Settled
decisions already fix its direction and whose Open questions are all bounded picks
needs NO brainstorm.

## Reading contract
[paste, substituting <epic-file> and <epic-heading>]

## Output format
FIRST line exactly one of: `NO_BRAINSTORM_NEEDED` | `BRAINSTORM_NEEDED`.
If NO_BRAINSTORM_NEEDED: one sentence why it's spec-ready as-is, then stop.
If BRAINSTORM_NEEDED: a `## Brainstorm agenda`, top 3 items max, each with Topic,
Type (open-design | product-decision | technical-tradeoff), why it blocks speccing,
and 2-4 concrete options/directions with a recommended default.
Audience: self-contained.

## Handoff context (required)
[standard]
```

- `NO_BRAINSTORM_NEEDED` → tell the user, save `{ "stage": "spec_create",
  "pending_handoff": "<handoff>" }`, advance to `spec_create`.
- `BRAINSTORM_NEEDED` → save `{ "stage": "epic_brainstorm", "pending_brainstorm":
  "<agenda>", "pending_handoff": "<handoff>" }`, advance to `epic_brainstorm`.

---

### `epic_brainstorm`

Orchestrator-driven and interactive — do not delegate to a sub-agent.

1. Tell the user the epic needs direction; summarize the agenda in plain language.
2. Work each item: `product-decision`/`technical-tradeoff` → `question` tool
   (2-4 options, recommended first, "(Recommended)"); `open-design` → a brief
   inline dialogue converging on a concrete, spec-able direction.
3. Scan for discussion signals ("let's discuss", "not sure") and engage inline.
   Scan for deferral language; record in `deferrals`.
4. Format outcomes as `## [item]\nDecision: [direction] — [detail]` and save to
   `pending_brainstorm_answers`.

Save `{ "stage": "epic_brainstorm_fix", "pending_brainstorm_answers": "<formatted>" }`,
advance.

---

### `epic_brainstorm_fix`

Spawn a **sonnet** sub-agent (`subagent_type: "sonnet"`). Prepend handoff if non-null.

```
Edit <epic-file> to fold the owner's brainstorm decisions into the target section
(heading "<epic-heading>"; do not touch other sections in the file).

## Brainstorm agenda
[pending_brainstorm verbatim]

## Owner decisions
[pending_brainstorm_answers verbatim]

Add each resolved direction to Settled decisions; update Intent/Goal, User
stories/tasks, Acceptance criteria, NOT included, and Open questions so they
reflect the resolved direction and no longer present it as open. Do not introduce
scope beyond what the decisions imply. Keep the existing section structure. If the
answers included deferrals, add a `### Deferred` subsection with a one-sentence
rationale each. Output a brief bullet-point summary of what you changed.

## Handoff context (required)
[standard]
```

Save `{ "stage": "spec_create", "pending_brainstorm": null,
"pending_brainstorm_answers": null, "pending_handoff": "<handoff>" }`, advance.

---

### `spec_create`

Spawn a **sonnet** sub-agent (`subagent_type: "sonnet"`). Prepend handoff if non-null.

```
Create the spec for the target using /speckit.specify.

## Reading contract
[paste]

Before writing, read
`~/.config/opencode/skills/epics-manager/best_practices_spec_driven_development.md`
and write the spec to its standard for AI-friendly specifications: outcome-oriented
goals, explicit input/output contracts where they apply, a "Not included" section,
and deterministic IF-THEN business rules, kept lean per the "Specification
Hierarchy" sizing rather than padded.

Read Settled decisions/Non-obvious facts before writing — reflect them verbatim.
Preserve the target's user stories and any traceability it defines. Run
/speckit.specify with the target's intent as the feature description. After it
completes, read `.specify/feature.json` for the spec directory, verify spec.md
exists, and output the exact spec directory path.

## Handoff context (required)
[standard]
```

Save `{ "stage": "plan_create", "spec_dir": "<path>", "pending_handoff": "<handoff>" }`,
advance. This is a create-only stage — no self-critique here; `plan_create` reviews
the spec next with a stronger model.

---

### `plan_create`

Spawn an **opus** sub-agent (`subagent_type: "opus"`). Prepend handoff if non-null.
Record its `task_id` as `pending_task_id` for a possible resume.

```
Your job is to both critically review <spec_dir>/spec.md AND write the
implementation plan for it, in this same pass — there is no separate spec-critique
or spec-fix stage.

## What to read
- <spec_dir>/spec.md
- <spec_dir>/checklists/requirements.md (if present)

## Reading contract
[paste]

## Step 1 — Review and fix the spec directly
Check the spec against the target's Settled decisions, Non-obvious facts, NOT
included, and its own internal consistency, using spec-driven-development best
practices. Edit spec.md directly to fix what you find, EXCEPT items that meet the
Flagged-item test below — apply your best default to those too, but report them
separately instead of silently finalizing them.

## Flagged-item test
[paste "The test" and "Never flag" bullets from the Flagged-item protocol]

## Step 2 — Write the plan
Then run /speckit.plan. The plan must honor the target's Settled decisions and
Non-obvious facts (sequencing, regression gates, test runner, acceptance steps) and
must not violate any NOT included item.

**Model assignment — record it in the plan.** For every phase and every task, record
a model class in the plan: `sonnet` (mechanical, testable work) or `opus`
(judgment-heavy work where a wrong answer is costly and hard to verify). Add a short
model-assignment section to `plan.md` mapping each phase/task to its class. Default
to sonnet; reserve opus for the genuinely judgment-heavy steps. Downstream,
`tasks_create` tags tasks from this section and `coordinate-implementation` keeps
each batch homogeneous by class. Do not invent a model tier.

**Complexity constraint — this is binding, not a suggestion:** tasks.md will be
implemented by sonnet-class models, not by you. Design accordingly: prefer a small
number of straightforward, mechanically-executable steps over an elegant but
judgment-heavy architecture. Where you have a choice between a design that needs a
sonnet-class implementer to make a nontrivial judgment call and one that doesn't,
choose the one that doesn't, even at the cost of being less general. If a step
genuinely cannot be made mechanical, say so explicitly in the plan rather than
hiding the complexity in prose a task-writer might miss.

After /speckit.plan completes, verify plan.md exists at <spec_dir>/plan.md and
output its path.

## Output format
## Fixes applied
[spec defects you fixed directly, one line each]

## Plan summary
[what the plan's shape is, in a few sentences]

## Flagged for owner
[omit if empty — see the Flagged-item protocol for the exact shape]

## Handoff context (required)
[standard]
```

Run the Flagged-item protocol's coordinator-side behavior. Once resolved (or if
nothing was flagged), save `{ "stage": "tasks_create", "pending_flagged": null,
"pending_answers": null, "pending_task_id": null, "pending_handoff": "<handoff>" }`,
advance.

---

### `tasks_create`

Spawn a **sonnet** sub-agent (`subagent_type: "sonnet"`). Prepend handoff if non-null.
Record its `task_id` as `pending_task_id` for a possible resume.

```
Your job is to write the task list for <spec_dir>, to the best of your ability.
Write only — do not self-critique, self-review or fix. A separate `overall_review`
stage will analyze spec, plan and tasks afterward.

## What to read
- <spec_dir>/spec.md
- <spec_dir>/plan.md
- <epic-file> (the "<epic-heading>" section)
- .specify/memory/constitution.md

## Reading contract
[paste]

## Step 1 — Write the tasks
Run /speckit.tasks. Tasks must cover every in-scope user story, keep each story
independently testable, include any lockstep documentation edits the target
requires, and end each story with the target's acceptance steps. Do NOT include
anything the target lists under NOT included.

**Tag every task with exactly one model class** — `[sonnet]` or `[opus]` — taken
from the plan's model-assignment section, defaulting to `[sonnet]`. The tag is part
of the task line, e.g. `- [ ] T012 [P] [US1] [sonnet] …`. When a story mixes
classes, order same-class tasks contiguously and note the class boundary, because
`coordinate-implementation` may only form batches that are homogeneous by class.

After writing, verify tasks.md exists and output its path.

## Output format
## Tasks written
[tasks.md path; task count; phase/story shape; the model-class split]

## Handoff context (required)
[standard]
```

Save `{ "stage": "overall_review", "pending_handoff": "<handoff>" }`, advance to
`overall_review`.

---

### `overall_review`

Spawn a fresh review sub-agent (use the project's configured review agent; the owner may
name one for a run, e.g. `deepseek 4.1`). Prepend handoff if non-null. Record its
`task_id` as `pending_task_id` for a possible resume.

```
Your job is the single review pass over <spec_dir> after tasks.md was written. There is
no separate tasks_critique/tasks_fix stage; you are it.

## What to read
- <spec_dir>/spec.md
- <spec_dir>/plan.md
- <spec_dir>/tasks.md
- <epic-file> (the "<epic-heading>" section)
- .specify/memory/constitution.md

## Reading contract
[paste]

## Step 1 — Analyze
Run /speckit.analyze read-only across spec.md, plan.md and tasks.md. Read its output as
evidence, then apply your own judgment on top of it.

## Step 2 — Resolve every finding, splitting by severity

- **Core spec or core plan issues** — a genuine ambiguity in, or departure from, the
  target's Settled decisions or Acceptance criteria, or a plan-level decision that would
  add scope, an extra approval gate or a new abstraction — go to the owner. Apply your own
  best default so the artifacts stay finished, and report each one under
  "## Flagged for owner" with the default applied and the genuine alternative.
- **Task-level issues** — ordering, grouping, coverage gaps, broken dependencies, batch
  sizing, implementation-detail or file-path mismatches, terminology drift — are fixed
  **autonomously, with no owner input**. Do not ask about them.

Apply every fix directly to the relevant artifact (spec.md, plan.md or tasks.md) unless it
is a flagged core issue, in which case apply your default and report it.

## Output format
## Fixes applied
[task-level and auto-applied fixes, one line each]

## Brief — decisions made
[the autonomous decisions and any flagged-item defaults, with a one-line rationale each]

## Flagged for owner
[omit if empty — core spec/plan issues only; for each: what you found, the default you
applied, why it is flagged (a)/(b), and the genuine alternative]

## Handoff context (required)
[standard]
```

Run the Flagged-item protocol's coordinator-side behavior. Once resolved (or if nothing
was flagged), save `{ "stage": "done", "pending_flagged": null, "pending_answers": null,
"pending_task_id": null, "pending_handoff": null }`, advance to `done`.

---

### `done`

Verify spec.md/plan.md/tasks.md exist and are internally consistent with the
resolved `spec_dir` (re-run `check-prerequisites.sh --json --require-tasks
--include-tasks` if resuming here after a gap). Output:

---

**The "<epic-heading>" target is ready for implementation.**

Artifacts:
- `<spec_dir>/spec.md`
- `<spec_dir>/plan.md`
- `<spec_dir>/tasks.md`

Run `/coordinate-implementation <spec_dir>` from this workspace (`<spec_dir>` is a
relative path; launching from elsewhere will fail to find the artifacts).

---

If resuming at an already-`done` state, recheck the three files still exist and are
consistent before repeating this message; if they've drifted, return to the
earliest affected stage instead of reporting stale completion.

## Known follow-up (not addressed by this rewrite)

`scripts/migrate_state.py` and `tests/test_compatibility.py` still reference the
retired stage names (`epic_critique`, `spec_fix`, `planning_gate`, etc.) from the
previous pipeline. They are not invoked anywhere in the stages above and do not
affect this skill's behavior, but they will give misleading output if run as-is.
Update or remove them before relying on the "Maintaining this skill" regression
checks again.
