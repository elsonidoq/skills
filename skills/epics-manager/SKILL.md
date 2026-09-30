---
name: epics-manager
description: Use when preparing or resuming a feature brief through a project's installed SpecKit specification, planning, tasking, and review workflow before implementation.
---

# Epics Manager

Guide an owner-selected brief through the project's installed SpecKit workflow
to reviewed implementation artifacts. This workflow requires SpecKit, prepares
work, and does not implement product code.

## Owner Communication

Speak as a technical manager who does not know the project's internal code or
architecture. Describe decisions in terms of customer or business outcome,
scope, delivery impact, tradeoffs, risks, and evidence. Do not assume the owner
recognizes internal components, file paths, implementation jargon, or prior
technical context. Explain any technical constraint only to the extent needed
to make the decision, using plain language.

Ask every owner question with the runtime's `ask_user` question tool, never as prose. Ask only
when the answer can materially affect product scope, architecture, privacy,
permissions, irreversible behavior, cost, or a settled requirement. Each tool
question must state the decision and its practical impact, offer two to four
concise options when options are known, and mark the recommended option. If
no question tool is available, ask one concise question in prose and end your
turn so the owner can reply; never infer an answer.

## Inputs and Provenance

Before assessing readiness, load the project memory store per the
`memory-handling` skill: read the store's index, then any entries whose triggers
match the target, and treat verified trigger-first gotchas as constraints on
scope and decisions.

Require a brief or source artifact and an unambiguous target within it. Resolve the
target from explicit headings, metadata, or owner input without assuming numbered
epics, a bundle filename, or a custom state directory. Record:

- Source path and selected section.
- Governing repository instructions and principles.
- Settled decisions, acceptance criteria, exclusions, dependencies, and cited
  sources.
- Existing spec, plan, tasks, and review artifacts linked to that source.

Re-read source bounds and links whenever resuming. If provenance is ambiguous,
use the runtime's `ask_user` question tool to obtain an unambiguous target instead of attaching work
to a likely-looking feature.

## Required SpecKit Capabilities

Before starting and before each stage, inspect the project's command registry
and files for the corresponding SpecKit capability and its instructions,
templates, and prerequisite scripts. Verify the specification, clarification,
planning, tasks, and analysis stage commands are installed and usable for this
project. Check the constitution capability when the installed workflow requires
it. Conventional command names and directory layouts are hints, not contracts.
Use only commands and assets observed in the current project.

Report capability checks in this form:

```text
Capability: constitution | specification | clarification | planning | tasks | analysis
Status: AVAILABLE | UNAVAILABLE
Evidence: [command or path found]
Blocker: [missing requirement or none]
```

If any required capability is unavailable, report `UNAVAILABLE` with the
missing command or asset and stop the workflow before producing or approving
downstream artifacts. Do not replace a missing SpecKit stage with generic
Markdown work, simulate a slash command in a shell, install tooling, or
initialize/overwrite project assets without owner authorization. Follow each
detected stage command's current instructions and verify its outputs; the
requirements below supplement the installed workflow rather than replace it.

## Required Runtime Capabilities

This suite pins its runtime: the `subagent` delegation tool (package
`pi-subagents`) and the `ask_user` question tool (package `pi-ask-user`) are
declared in the global configuration repository's `REQUIREMENTS.md`. Verify the
tools are registered and usable before relying on them; never invent a tool,
command, agent, model, or package. If a required runtime capability is
unavailable, report `Delegation: UNAVAILABLE` or `question: UNAVAILABLE` with
the missing package and stop before producing or approving downstream
artifacts.

Before task generation, also verify all of these observable capabilities:

- The delegation runtime can dispatch the required third planning-pipeline
  sub-agent and has a configured Sol planning/task option. Resolve that option
  from current runtime configuration; do not hard-code a provider or model ID.
- The detected project-local SpecKit tasks stage, including its instructions,
  templates, prerequisite scripts, and output path, is usable inside that
  delegated context.
- The runtime can preserve and resume that exact delegated context after the
  main agent validates and corrects the tasks.
- The detected project-local SpecKit analysis stage and its assets are usable
  inside the resumed context.

Report an unavailable item as `Task delegation: UNAVAILABLE`, `SpecKit tasks:
UNAVAILABLE`, `Task-agent resume: UNAVAILABLE`, or `SpecKit analysis:
UNAVAILABLE`, name the missing evidence, and stop at the plan boundary. If the
context is created but later cannot be resumed, stop at that point. Never run a
fresh replacement agent, run either stage locally, simulate a slash command,
or silently substitute generic Markdown.

## Workflow

Run the earliest incomplete or invalid stage:

1. **Principles preflight:** Read the project's governing principles if present.
   If a detected SpecKit workflow requires a constitution and it is missing or
   still template text, use the runtime's `ask_user` question tool to obtain the necessary
   project-specific principles and use the detected constitution capability.
   If that capability is unavailable, stop; do not invent policy.
2. **Brief readiness:** Confirm the target has an outcome, users, scope, exclusions,
   acceptance criteria, dependencies, and no unresolved direction that would change
   the feature materially. Use the runtime's `ask_user` question tool only for genuine product or
   architectural choices.
3. **Specification:** Run the detected SpecKit specification stage. Before
   producing the spec, read the suite's global best-practices document at
   `~/.agents/docs/best_practices_spec_driven_development.md` (equivalently
   `../../docs/best_practices_spec_driven_development.md` relative to this skill's
   installed directory). This is a global suite asset, not a project file: never
   look for it in the project repository's `docs/`. If it is unavailable, stop and
   report an incomplete global configuration installation. Apply **Designing AI-Friendly Specifications for Solo Builders**:
   keep goals outcome-oriented, make inputs/outputs and deterministic business rules
   explicit where relevant, include exclusions, and avoid implementation detail
   unless it is a settled constraint. Verify the recorded admission sizing verdict
   and rationale under **Epic Sizing: When the Pipeline Earns Its Overhead**; if
   absent, establish them before continuing. Resolving ambiguity during readiness,
   clarification, or planning does not invalidate admission. A substantive scope
   change requires the owner's choice through the runtime's `ask_user` question tool and a recorded
   sizing/path decision before continuing; do not silently reroute the work.
   When the epic records the owner-approved directive
   `documentation initialization requires an epic`, preserve that sizing exception.
4. **Clarification:** After specification, run the detected clarification stage.
   Resolve mechanically answerable gaps; send material choices to the owner with
   the runtime's `ask_user` question tool.
5. **Specification approval:** Summarize the specification and clarification results
   in manager-level terms, then use the runtime's `ask_user` question tool to request approval. Record
   explicit specification approval in a project-defined decision or progress
   artifact, or in the specification when none exists. Do not begin planning without
   it.
6. **Plan:** Review the spec, fix non-material defects, then run the detected
   SpecKit planning stage to produce architecture, contracts, sequencing, risks,
   verification, and documentation scope. Identify the documentation that must
   explain each new or modified capability, interface, workflow, configuration,
   operational procedure, or user-visible behavior. Record that scope in the
   plan for task generation. Require an implementable sequence of stages and
   user stories: a stage's required producers must be available in an earlier
   stage or earlier within the same stage. Keep each story's sequential work
   together; if a later stage would have to produce an earlier task's prerequisite,
   revise the stage order or producer placement before task generation. When the
   approved work calls for delegated architectural decomposition, use
   `delegating-architectural-planning` to run the detected planning stage; do not
   produce a substitute plan outside it.
7. **Plan approval:** Inspect the plan against the approved specification, correct
   non-material defects, summarize its delivery phases and material tradeoffs in
   manager-level terms, and request owner approval with the runtime's `ask_user`
   question tool. Record approval for the current plan revision. Do not generate
   tasks from an unapproved or subsequently changed plan.
8. **Delegated tasks:** After plan approval and the task-delegation capability
   checks, dispatch the required third planning-pipeline sub-agent using the
   observed Sol planning/task configuration. Give it the approved specification,
   plan, project instructions and principles, relevant memory constraints, and
   the detected project-local tasks-stage instructions and assets. Instruct it to
   run the installed `/speckit.tasks` capability through its supported runtime
   interface and write the stage's task artifact; a similarly named command is
   acceptable only when it is the capability actually detected in that project.
   Its write scope is limited to task-stage artifacts. It must not implement,
   change approved scope or architecture, contact the owner, commit, push, or
   dispatch agents. Preserve the returned context identifier for analysis.

   Require the generated list to contain dependency-aware, independently
   verifiable tasks. Each task identifies its outcome, prerequisites, likely
   files/interfaces, acceptance evidence, capability needs, `Model class:
   sonnet-class | opus-class`, and a brief rationale for that class. Default to
   `sonnet-class` for bounded, well-specified work. Use `opus-class` only when the
   work cannot be safely decomposed into bounded, independently verifiable tasks.
   Include one or more tasks for the documentation scope recorded in the plan;
   their acceptance evidence must confirm that the documentation matches the
   implemented changes. Number tasks in execution order without gaps, place every
   prerequisite earlier with a smaller task number, and keep each story's tasks
   contiguous after shared setup. The sub-agent returns a material decision as a
   blocker for the main agent rather than choosing or communicating with the
   owner.
9. **Main-agent task validation:** Inspect the actual generated artifact and its
   provenance; do not accept the sub-agent's summary as evidence. Check source ->
   spec -> approved plan -> tasks traceability, omissions, contradictions,
   integration coverage, exclusions, and stage feasibility. Check explicit and
   implicit dependency order and contiguous story order manually. For a task list
   with `T`-numbered Markdown entries and explicit `Depends` fields, also run
   `python3 scripts/check-task-order.py /path/to/tasks.md` from this skill's
   directory when Python 3 is available. If the script cannot run or the format
   differs, report scripted validation as unavailable and retain the manual
   check. Fix every missing, duplicate, out-of-order, forward prerequisite, and
   noncontiguous story finding. If correct sequencing would contradict the plan,
   return to planning and obtain fresh approval for the revised plan rather than
   adding a batching exception.

   Confirm that every planned documentation surface has an implementation-linked
   documentation task and acceptance evidence. Confirm every task has exactly one
   allowed model class and a task-specific rationale. Count the complete list:
   at most 30% may be `opus-class`. If the proposed share exceeds 30%, use the
   runtime's `ask_user` question tool to present the affected task IDs, rationale,
   and delivery impact of reducing the share, and record explicit owner approval
   before finalizing it. The main agent makes all non-material corrections and
   records them for the resumed context; it sends every material scope,
   architecture, privacy, permission, irreversible-behavior, cost, or settled-
   requirement choice to the owner.
10. **Delegated analysis:** Resume the exact Sol sub-agent context from task
    generation. Give it the corrected current artifact paths and the main agent's
    validation record, then instruct it to run the detected project-local
    `/speckit.analyze` capability through its supported runtime interface. Do not
    dispatch a fresh agent or accept a generic review as a substitute. The
    sub-agent may write only outputs required by the installed analysis stage and
    must return evidence and material blockers to the main agent.

    The main agent then reads the analysis output and manually verifies each
    finding against the source, specification, approved plan, tasks, governing
    principles, and repository evidence. It retains judgment over severity,
    disposition, corrections, and completeness; the analysis result is not an
    approval. Apply non-material corrections, repeat the applicable task checks,
    and resume the same context to rerun analysis when those corrections stale its
    evidence. The main agent alone communicates with the owner and requests or
    records approvals.
11. **Overall review:** Using the main-agent task checks and manually inspected
    analysis evidence, check end-to-end traceability, contradictions, omissions,
    dependency and story order, integration coverage, exclusions, governing
    principles, documentation coverage, and model-class rationale/share. Do not
    approve a task list exceeding 30% `opus-class` tasks without recorded owner
    approval. Resolve all non-material findings and route material decisions to
    the owner before continuing.
12. **Overall review approval:** Immediately before requesting approval, present a
    brief bulleted plan summary in manager-level terms: one bullet for the intended
    outcome and one concise bullet for each plan phase. Include a risk, dependency,
    exclusion, or deferral only when it materially affects the approval decision. Then
    use the runtime's `ask_user` question tool to request approval. Record explicit overall review
    approval in a project-defined decision or progress artifact, or in the reviewed
    artifacts when none exists. Do not hand off implementation without it.
13. **Handoff:** Verify all recorded approvals apply to the current artifacts and
    re-run applicable prerequisite or artifact checks. Do not load or run
    `coordinate-implementation` in this session. Instruct the user to run
    `finish-session` or `finish-session-jev` to close the planning session. Then
    provide this copyable prompt for a fresh session, replacing each placeholder with
    the current artifact path:

    ```text
    Use the coordinate-implementation skill to execute the approved work.
    Workflow origin: epics-manager
    Specification: [specification path]
    Plan: [plan path]
    Tasks: [tasks path]
    Source brief: [source brief path]
    Specification approval: [record path and section]
    Plan approval: [record path and section]
    Overall review approval: [record path and section]
    Review evidence and decisions: [record paths and sections]
    ```

    Verify every referenced record is durable and accessible in the target workspace.
    When approvals or review evidence are embedded in a spec or plan, cite that
    artifact and section rather than creating a separate record.

## Decisions and Corrections

Agents may resolve task organization, filenames, internal naming, and mechanically
verifiable defects. Use the runtime's `ask_user` question tool only when alternatives materially
change product scope, architecture, privacy, permissions, irreversible behavior,
cost, or a settled requirement. Apply no speculative answer merely to advance the
workflow.

Record each owner decision and approval with its stage and affected artifact paths
in an existing project-defined decision or progress artifact when one is documented.
Otherwise keep it in the affected spec or plan. Identify the approved artifact
versions or content, preserving any existing project revision/evidence convention, so
a fresh session can detect changes after approval; a bare `approved` label is not
enough. Do not create a global state schema or require a particular progress filename.

## State and Resume

Artifacts are the default durable state. Use a project state mechanism only when
the repository documents one; validate its schema and artifact links before trusting
it. On resume:

1. Verify source and artifact paths still exist.
2. Verify recorded specification, plan, and overall review approvals apply to the
   current artifact revisions. Missing or stale approval returns to that gate.
3. Validate stage outputs and integrations rather than trusting a `done` label.
4. If task generation completed but analysis did not, verify that the exact Sol
   task-agent context can still be resumed. If not, report `Task-agent resume:
   UNAVAILABLE` and stop rather than dispatching a replacement.
5. Continue from the earliest stale, missing, or inconsistent artifact.

## Ready for Implementation

Report readiness only when the spec, plan, and tasks exist, provenance is clear,
dependencies and documentation tasks are represented, specification, plan, and
overall review approvals are recorded for the current artifacts, other owner gates
are resolved or explicitly deferred, and the main agent has recorded both task
validation and its manual inspection of current SpecKit analysis evidence. List
artifact paths, delegated-context evidence, capability checks, checks run, and
unavailable behavior. Artifact readiness does not mean implementation or feature
acceptance is complete.
