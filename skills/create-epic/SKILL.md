---
name: create-epic
description: Use when an evidence-backed feature brief needs an epic or an owner-approved direct task list.
---

# Create Epic

Turn the user's brief or named source artifact into an evidence-backed feature epic that the `epics-manager`
skill can continue without rediscovering its essential facts. Do not implement
product code.

If the request does not identify a brief or source path, use the runtime's question tool
(the `ask_user` tool when the `pi-ask-user` package is installed) to ask for one, or both.
If no question tool is available, ask one concise question in prose and end your turn so the
user can reply. Read every source artifact it names.

## Required Reference

Read the global configuration repository's
[`docs/best_practices_spec_driven_development.md`](../../docs/best_practices_spec_driven_development.md)
before assessing the brief. If it is unavailable, stop and report an incomplete
global configuration installation. Apply **Designing AI-Friendly Specifications for
Solo Builders** to the epic's requirements and **Epic Sizing: When the Pipeline Earns
Its Overhead** to the sizing decision.

## Discovery

Read applicable repository instructions and existing epic, specification, task,
decision, and index artifacts. Load the project memory store per the `memory-handling`
skill before assessing the brief: read the store's index, then any entries whose
triggers match the brief's subject, and treat non-obvious trigger-first gotchas as
verified constraints on scope and sizing. Discover the project's established epic location,
format, numbering, and artifact links; do not assume a path, a filename, a
constitution filename, or a tracker. If no destination or format can be inferred,
ask the owner before creating an artifact.

## Evidence and Decisions

Treat source claims as claims, not facts. Verify load-bearing positive and negative
claims at their source layer. Record citations that let a fresh-context agent find
the evidence, and retain resolved evidence so it is not re-derived later. Mark any
claim that cannot be checked as `UNVERIFIED`.

Treat an "already satisfied" or "no task needed" claim as high risk: inspect the
code that allegedly satisfies it and record the result. Prefer a symbol-oriented
`file:line` citation with the relevant verbatim evidence over a paraphrase. Retire an
unknown empirically when a bounded command or inspection can settle it now rather
than turning it into a clarification question.

Separate each decision into one of these categories:

- **Settled:** decided by the owner, existing behavior, or governing instructions;
  record the decision and rationale.
- **Open:** materially changes product scope, architecture, privacy, permissions,
  irreversible behavior, cost, expected task count, pipeline use, or a settled
  requirement.
- **Mechanical:** a consequence that does not need owner choice.

Resolve mechanically answerable gaps. Use the runtime's question tool (the `ask_user`
tool when available) only for material open decisions; if no question tool is available,
ask one concise question in prose and end your turn so the owner can reply. Provide two to four
concrete options, lead with a recommendation, and cite verified evidence for factual
claims. Preserve the owner's reasoning with each answer. Do not invent a beneficiary;
ask if it is unclear.

## Sizing

State the sizing verdict before writing an epic. Use the full SpecKit pipeline only
when all three conditions hold: at least eight expected tasks, at least one
unresolved material design decision, and multiple subsystems.

Exception: when a parent command passes the explicit owner-approved directive
`documentation initialization requires an epic`, create the documentation epic
even if the normal sizing conditions are not met. Record the directive and the
normal sizing verdict in the epic so the exception remains auditable.

If the brief fails a condition, recommend a direct, independently verifiable task
list unless the documentation-initialization exception applies. Record the owner's
decision in the established decision artifact, or in the brief when none exists.
With owner approval, preserve the durable requirement/source and route it to the
`requirements-manager` skill for shared brainstorming, direct task generation, review, and
current approval. Do not create a plan or specification. Report that lightweight route and
its source path; requirements-manager supplies the coordinator handoff after approval.

For a justified epic, list mechanically obvious work that does not depend on a design
output as separately scheduled work. Record its exclusion and rationale so later
pipeline tasks do not duplicate it.

## Epic Content

Use the discovered project format. When no complete format exists, include:

1. Title, beneficiary, source, scope, and sizing verdict.
2. Overview of user stories or outcomes and affected surfaces.
3. Verified evidence, including resolved claims that must not become tasks.
4. Settled decisions with rationale and non-obvious verified constraints.
5. Remaining open design decisions, including scope impact.
6. Deterministic, outcome-oriented acceptance criteria with explicit inputs,
   outputs, business rules, and observable verification where relevant.
7. Exclusions, separately scheduled work, dependencies, and authoritative sources.

Before handing the epic to the `epics-manager` skill, resolve every `UNVERIFIED` claim that
affects scope, acceptance criteria, dependencies, or settled decisions, or record
the owner's explicit deferral. Confirm no pipeline task can duplicate or contradict
an exclusion.

## Report

State the created artifact path, sizing verdict, verified corrections to the input,
separately scheduled work, remaining `UNVERIFIED` claims or deferrals, and the next
`epics-manager` handoff. For the lightweight route, report the durable requirement/source
and the next `requirements-manager` handoff instead.
