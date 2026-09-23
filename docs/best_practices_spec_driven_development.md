# Spec-Driven Development: Operational Reference

## SDD Role and Lifecycle

Treat the specification as the source of truth for intended behavior, not as disposable setup for coding. It constrains agent assumptions, preserves decisions across sessions, and provides the basis for planning, tasks, tests, and review.

Use this lifecycle, adapting artifact names and tooling to the repository:

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
- Planning must not begin until the specification and clarification results have explicit human approval.

### Planning, Tasks, and Analysis

- Plan only from the approved specification. Cover contracts, integration points, migration and rollback where relevant, sequencing, risks, and verification.
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

## Epic Sizing: When the Pipeline Earns Its Overhead

Use the full specification -> clarification -> plan -> tasks -> analysis -> implementation pipeline only when **all three** conditions hold:

1. **At least eight expected tasks:** below this, pipeline overhead usually exceeds coordination value.
2. **At least one unresolved material design decision:** its answer changes implementation shape, such as an authorization model, data location, shared contract, or algorithm.
3. **Multiple subsystems or workstreams:** coordination crosses boundaries such as client, server, data, infrastructure, or independent workstreams sharing a contract.

If any condition fails, prefer a direct, independently verifiable task list with the applicable decisions and evidence. Typical direct-task-list cases are four or fewer mechanically obvious tasks, a single component or internal tool, or design already resolved during prior discussion. For intermediate sizes, apply the same all-three rule rather than using task count alone.

Merge candidate epics before sizing when:

- One epic depends on a design output from another and separate planning would cause rework.
- Both modify the same execution surface in interleaved ways, making separate task lists harder to coordinate.
- Their combined work reaches or approaches a coherent pipeline-sized scope, such as two small epics forming six to eight related tasks. After merging, the full pipeline still requires all three conditions above.

Red flags during epic writing:

- A one-bullet scope is probably too small for the full pipeline.
- No open design question means clarification and planning may add no value; write tasks directly.
- Exclusions longer than included scope suggest a sub-task that should be merged into its parent feature.
- A dependency on another epic's design output, rather than only its delivered interface, suggests the epics should merge.

Record the sizing verdict and rationale. Human approval is required for the selected pipeline or direct-task-list path when project workflow calls for that gate.
