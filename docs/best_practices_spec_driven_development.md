# Spec-Driven Development: Operational Reference

## SDD Role and Lifecycle

Treat the specification as the source of truth for intended behavior, not as disposable setup for coding. It constrains agent assumptions, preserves decisions across sessions, and provides the basis for planning, tasks, tests, and review.

Use this lifecycle for Standard, adapting artifact names and observed tooling to the
repository. TinySpec deliberately combines what/how in one source and has only the
combined source/task approval described below; do not impose Standard's separate
specification approval or planning artifacts on it:

1. **Principles:** Read governing product, architecture, quality, and security rules. Do not invent missing policy.
2. **Specify:** Define what must be true and why, without prescribing implementation unless a technical choice is already settled.
3. **Clarify:** Remove ambiguity and resolve material choices before planning.
4. **Approve specification:** Obtain and record human approval of the current specification.
5. **Plan:** Define architecture, interfaces, data flow, sequencing, risks, migration or rollout, and verification.
6. **Tasks:** Derive dependency-aware, independently verifiable implementation tasks from the approved plan.
7. **Analyze:** Check source -> specification -> plan -> tasks traceability, consistency, completeness, dependencies, and exclusions.
8. **Approve reviewed artifacts:** Record human approval after analysis and before implementation handoff.
9. **Implement and verify:** Execute tasks against the approved artifacts; update artifacts or seek a decision when implementation reveals a material conflict.

Resume at the earliest missing, stale, or inconsistent stage. Artifact status never substitutes for validating its content and links.

## Designing AI-Friendly Specifications for Solo Builders

A specification must be lean but deterministic. Include:

- **Outcomes and beneficiaries:** State the user or system outcome and why it matters. Describe required behavior, not coding steps.
- **Scope:** Identify affected workflows and externally observable behavior.
- **Inputs and outputs:** Define relevant request, event, data, state, error, and interface contracts. Use precise examples or machine-readable schemas when useful, but do not require a particular schema technology.
- **Deterministic rules:** Express decisions unambiguously, preferably as `IF <condition>, THEN <result>`, including boundaries, precedence, retries, idempotency, and null or empty behavior where relevant.
- **Exclusions:** State what is not included and ensure downstream work cannot silently reintroduce it.
- **Dependencies and constraints:** Record authoritative sources, settled technical constraints, privacy or security rules, compatibility needs, and external dependencies.
- **Verifiable acceptance criteria:** Make each criterion observable and pass/fail. Include normal flows, relevant failures and edge cases, and any required quality attributes. Do not invent arbitrary metrics.

Avoid vague adjectives, hidden defaults, speculative implementation detail, and requirements that cannot be tested or inspected. Verify load-bearing claims against available evidence; mark unresolved claims rather than presenting assumptions as facts.

### Clarification and Human Decisions

- Resolve facts and mechanically derivable consequences through bounded inspection or testing.
- Ask a human when alternatives materially change product scope, architecture, privacy, permissions, irreversible behavior, cost, or a settled requirement.
- Present concrete options, relevant tradeoffs, and a recommendation; record the decision and rationale in the applicable artifact.
- Do not choose speculatively to keep the workflow moving.
- In Standard, planning must not begin until the specification and clarification results have explicit human approval. TinySpec resolves material choices but does not add a separate pre-task source approval.

### Planning, Tasks, and Analysis

- Standard plans only from the approved specification. TinySpec records its bounded approach in the compact source. Both cover contracts, integration points, migration and rollback where relevant, sequencing, risks, and verification.
- Make tasks dependency-aware and independently verifiable. Each task states its outcome, prerequisites, likely files or interfaces, acceptance evidence, and required capabilities.
- Keep implementation choices in the plan or tasks, not retroactively in requirements, unless they become settled constraints.
- Analyze all artifacts for omissions, contradictions, unsupported assumptions, dependency order, integration coverage, exclusions, and governing-rule compliance.
- Material changes return to specification clarification and approval; non-material corrections may be made directly and recorded.

### Verification, Security, and Review

- Derive tests and checks from acceptance criteria. Use the smallest mix of unit, integration, end-to-end, contract, property, performance, migration, and manual checks that covers the stated risks.
- Where practical, demonstrate that a new or corrected test fails before implementation and passes afterward.
- Run applicable formatting, linting, type, build, test, and static-analysis gates; report commands, results, and unavailable checks.
- Review concurrency and repeated execution, null and empty inputs, failure recovery, data integrity, compatibility, and performance regressions where relevant.
- Verify authorization, sensitive-data handling, secret management, input validation, dependency risk, and governing security rules.
- Use an independent review pass when practical. Review against the approved specification and plan, not merely for code style.
- Do not claim readiness while required checks fail, material requirements lack evidence, or approvals are stale.

## Adaptive Planning Depth: Assess, Do Not Route

`planner` is the public entry point. Understand the structured requirement, inspect
load-bearing code/contracts/tests and applicable memory, then brainstorm only material
uncertainty. Before depth selection this is read-only: no coordination auto-init,
routine summaries/index updates, evidence-only commits, reflection or STATE maintenance.
Consult relevant existing guidance through the
[Memory Handling](../skills/memory-handling/SKILL.md); missing store
is nonblocking. Only explicit future-directed user feedback permits bounded guideline writes.

Assess reasoning complexity and coordination cost, not estimated diff size or a fixed
task threshold. Present approximate evidence and uncertainty about affected subsystems,
architecture, data/API contracts, dependencies, migrations, compatibility, security,
concurrency, deployment, test complexity, reversibility, sequencing and likely work units.
Inspection is bounded by those questions, not an automatic repository-wide audit.

Signals favoring **TinySpec**: localized or mechanically repetitive work, stable interfaces,
settled approach, reversible changes, few integration boundaries, directly observable checks.
A large mechanical diff can still fit this path.

Signals favoring **Standard**: valuable separation of behavioral and architectural reasoning,
shared contracts or data migrations, security/concurrency risks, difficult rollback, external
integration/rollout, cross-subsystem sequencing or complex verification. A small diff can
justify this path. Resolved product uncertainty does not eliminate architectural value.

Always present both paths and stop for explicit owner choice through `ask_user`:

- **TinySpec → Tasks → Implement:** one compact what/how source plus mandatory separate tasks.
  No SpecKit dependency or extra specification/plan/research/design chain.
- **Standard: Specify → Plan → Tasks → Implement:** genuine installed SpecKit capabilities,
  separate specification approval before planning, analysis/independent review and final approval.

A recommendation is information, not a routing rule. The owner may intentionally choose
either depth. Preserve that selection on resume; reopen only for substantive scope change
or owner direction, with recorded rationale. No new Epic artifact/concept or documentation
exception selects depth for the owner. Related requirements sharing a design output or
interleaved interfaces may warrant a coherent combined scope; explain this before choice.

Both paths use `task-generation` semantics and converge on `coordinate-implementation`.
Planning stages stop on their required unavailable capabilities; never simulate SpecKit
or impose its stages on direct tasks merely because it is installed.

## Common Authorization and Handoff

Planning selection authorizes preparation, not execution. TinySpec and its separate tasks
receive planner review then one combined owner approval; no separate pre-task source
approval. Standard retains the lifecycle above. Current-content review and authorization
are required for both, with durable evidence and earliest-invalid-stage recovery.

Before EVERY artifact approval or renewal, present an owner-visible executive brief in
4–6 short bullets BEFORE calling `ask_user`: outcome, scope/exclusions, important decisions,
risks/deferrals, actual review/validation results, current artifacts and exact authorization
including the next phase. Permit withholding approval/requesting changes. After affirmative
approval, immediately start the next authorized phase; do not ask for routine continuation.
Final approval starts coordinator preflight by default unless the owner explicitly requested
planning-only or a separate-session handoff. Missing capabilities/material gates still stop;
older preparation-only approvals do not retroactively authorize execution. A label or chat-only answer is insufficient for a fresh executor.
The operational transitions and legacy repair rules are owned by
[planner's approval/recovery contract](../skills/planner/references/approval-and-recovery.md).

The handoff names producer/depth, source/task/supporting artifact paths, current content
or revisions, review/validation evidence, decisions/deferrals, applicable approvals and
explicit implementation scope. Standard includes spec/plan and both approvals. TinySpec
includes its combined approval. Use project conventions, not a new universal state file.
Task outcomes reference authoritative source criteria rather than duplicate the whole source.
Legacy artifacts retain their original shapes and gates; changed names never waive provenance.

## Retained task checkpoints

After required verification, each authorized retained repository task uses the shared
[task-commit contract](../skills/memory-handling/references/task-commit-contract.md): explicitly stage only owned
paths and make a focused commit before subsequent task writes, completion reporting, or handoff. Source and task-list
production are separate retained deliverables; their existing preparation/combined-approval gates remain unchanged.
Read-only/no-change work creates no empty commit. Preserve unrelated dirty work and stop on uncertain ownership,
missing Git/identity, failed hooks/checks, or conflicting policy rather than offering a waiver. Coordinators inspect
actual diffs/SHA/check evidence and only recover understood verified contextual work; fresh implementers return unknown
state without writing. Return concrete check/commit proof in existing task/runtime conventions, without routine persistence. Static assertions and temporary
Git fixtures demonstrate policy/Git examples, not runtime model obedience.
