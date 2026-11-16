---
name: planning-brainstorming
description: Use when unresolved design or owner-direction questions may block scope assessment or downstream planning artifacts.
---

# Planning Brainstorming

Decide whether the request is ready for the caller's next stage. If a material decision is
missing, help the owner make it and return the actual decision, rationale and any deferral.
The parent conducts assessment and dialogue with the owner-launched model and effort; neither
requires a child call or a saved assignment. This skill does not choose TinySpec/Standard or
produce a specification, plan, task list or implementation.

## Judge readiness

Use the caller's request or bounded source, mode and readiness target. Read relevant source
evidence, repository instructions and principles. Use [Memory Handling](../memory-handling/SKILL.md)
to retrieve applicable guidance and gotchas. Before affected assessment, including fresh or
resumed standalone entry, consult [save-adr](../save-adr/SKILL.md#consult-and-propagate) for current
accepted constraints and source links. Discover existing decision ownership and consult its
index and relevant records even if the caller did not supply them; session history supplements,
not replaces, this consultation. An absent decision store alone is nonblocking. Apply the
owner's conflict rules only to the affected decision.

Keep the mode's authority clear:

- **Preselection:** inspect existing evidence read-only and retain answers in session history.
  The target is informed scope assessment, not immediate task production. Create no source,
  decision or state files, including for resume.
- **Selected production / legacy repair:** use the explicitly selected source or section and
  established project artifacts. Existing task-embedded requirements remain valid; this skill
  imposes no new source shape.

Apply [Parsimony and Actionable Checks](../planner/references/parsimony.md) to distinguish a
material question from ordinary technical work. Current source content and applicable accepted
outcomes inform the judgment; they do not grant new decision authority. Retain exactly one result:

- `NO_BRAINSTORM_NEEDED`: direction is settled, or evidence/mechanical work resolves the ambiguity.
  Explain why the target is ready. Bias toward this result for naming, file placement, task
  ordering, grouping, bounded clarification or an obvious mechanical default.
- `BRAINSTORM_NEEDED`: an open design question, product-direction decision or material technical
  trade-off blocks readiness. Return `## Brainstorm agenda` with no more than three items.
  For each, state the topic, type (`open-design`, `product-decision` or `technical-tradeoff`),
  blocking reason, two to four concrete alternatives and a recommended direction.

## Resolve the material questions with the owner

The parent, not a delegated worker, presents one agenda item at a time. Verify the question
capability and ability to retain answers under [runtime requirements](../../REQUIREMENTS.md).
If the permitted fallback is prose interaction, ask in prose and end the turn; otherwise report
the missing capability and stop. A caller's mandatory preflight can stop earlier. Missing
answers, cancellation or unavailable dialogue never authorize inferred decisions or downstream
production; missing delegation alone does not block parent dialogue.

Offer alternatives and a recommendation for product decisions and technical trade-offs; converge
open-design discussion on a specific direction usable by the next stage. Retain each actual
answer and the owner's rationale in the mode's permitted carrier:

```text
## [item]
Decision: [direction] — [detail]
```

Record deferrals and their rationale rather than treating them as answers. Planning depth remains
the planner's owner choice, not a brainstorming design-depth label.

## Apply and return the decisions

Only with selected-production or legacy-repair write authority, delegate bounded application of
exactly the recorded decisions to the selected source. Resolve `brainstorm-application` through
the planner's [saved-assignment contract](../planner/SKILL.md#saved-planner-assignments), which
supplies the shared `brainstorming` assignment. Pass that exact binding unchanged in the brief
and dispatch, and verify it is permitted and callable at dispatch. An invalid or unavailable
binding stops only application with the owner's focused correction question; no recommendation,
inferred substitute or fallback binding. Do not resolve `brainstorm-assessment` for the parent.

Change only affected decisions, outcome, acceptance, exclusions and open questions. Preserve the
source format and add a concise note for deferred work; do not expand scope or rewrite unrelated
sections. Checkpoint authorized retained changes under the shared
[task-commit contract](../memory-handling/references/task-commit-contract.md). Read-only
preselection creates no empty commit and no mode may adopt inherited work.

Return the readiness result, agenda if any, decisions/rationale, deferrals, accepted constraints
and source links, trade-offs and remaining uncertainties for the caller's readiness target.
Include relevant research links, guidelines and observable verification needs; task generation
owns their task-level mapping, and this planning assignment does not select runtime bindings.
Use session history before selection and established project conventions after selection.

On resume, repeat the applicability consultation above and validate the bounded source and saved
decisions. Re-present the saved agenda for missing answers rather than reconstructing decisions.
If source or decisions changed materially, run the readiness judgment again before downstream
production.
