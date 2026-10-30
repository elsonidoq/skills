# Global Agent Instructions

## Purpose

This repository contains global pi configuration, commands, and skills. Keep global assets portable across
unrelated projects. Project-specific policy belongs in that project's instructions or local skills.

## Skill Policy

Automatically use only these global process skills:

- `brainstorming`
- `using-git-worktrees`
- `requesting-code-review`
- `receiving-code-review`
- In suite-adopting projects, load the project memory store per the `memory-handling`
  skill before planning or implementing.

Use another skill only when the user explicitly requests it or the task requires a named external capability.
Global skills may depend on a reusable capability such as SpecKit, Railway, Supabase, GitHub, or a configured
agent only after verifying it is available and stating an unavailable fallback.

## Global Assets

- Commands and skills must not assume a project name, repository layout, branch, local path, deployed state, or
  configured model or agent.
- Do not add project-specific workflow, data, or historical rationale to global assets.
- After changing global configuration, commands, or skills, use a fresh-session handoff in
  Paseo; elsewhere follow the host's normal reload guidance.

## Parsimony and Actionable Checks

Prefer the smallest working solution using existing mechanisms. Demonstrate a real end-to-end workflow
before generalizing; supporting machinery must not become the main deliverable.

- Keep workflow readiness linter-like: a handful of obvious, independent rules about the actual workflow
  (valid tasks/configuration, available skills/scripts/executor, clear ownership). Aim for five primary
  checks and normally no more than five to ten operational rules a human can remember. More requires a
  concrete justification; do not hide a large protocol behind a few umbrella labels. This is a design
  budget, not a numerical cap on ordinary test assertions or real external interface constraints.
- Checks must earn their cost: prevent a specific serious risk, enforce an explicit requirement, or
  address a demonstrated failure. Hypothetical future problems do not justify new blocking machinery.
- Check at the relevant boundary; repeat only when changed state can invalidate the result. Prefer
  existing SDK/tool/compiler/test behavior over duplicate validation and custom enforcement layers.
- Every blocking diagnostic must name the problem, affected operation and concrete corrective action.
  Let the running agent autonomously correct ordinary errors within its authority; do not turn normal
  tool failures into unusable runs or new subsystems. Ask only for material scope/permission decisions.
- Observe/report by default; block when continuing creates a concrete risk or cannot yield a valid
  result. Optional telemetry/audit data must not block execution. Derive limits from actual consumers;
  do not invent caps, thresholds or universal file-size rules.
- Preserve cheap protections against data loss, credential exposure and unauthorized external actions.
  Do not weaken a necessary check to claim success. Keep application acceptance tests distinct from
  workflow-startup ceremony, and resolve conflicting existing mandates explicitly rather than silently
  bypassing them or adding another layer of policy.

## Repository-local Definition of Done

When a practical, meaningful evaluation is possible at a proportionate cost, the issue
should include evidence that the intended behavior improved.

Useful simpler evidence or a brief justification that evaluation is impractical, expensive,
or low-value is sufficient; do not manufacture new fixtures or compliance tests. Evaluation
belongs to later issue resolution, not initial issue filing. Preserve applicable existing
checks, security and permission gates; this does not authorize skipping failing relevant
existing checks or automatically running the whole behavioral collection. Follow the
repository's evaluation convention in [evaluations/README.md](evaluations/README.md).

## Expensive Subagent Failures

Never relaunch an expensive subagent, including `opus`, after a failure unless the failure cause
has been inspected and a retry directly addresses that cause. The same rule applies to batches
delegated through the suite's `subagent` tool: inspect the failed child run before resuming or
re-dispatching, and never relaunch on an uninspected failure. A generic tool abort, cancellation,
timeout, or missing error detail is not evidence that retrying will work.

Before any relaunch:

1. Inspect the existing task session and the failed tool invocation.
2. Determine whether the subagent can be resumed with a targeted correction.
3. Resume the existing session when it retains relevant analysis or work.
4. If the cause is unavailable or uncertain, stop and report the blocker to the owner.

Only launch a new expensive subagent after the owner explicitly requests it or the inspected
failure proves that a fresh session is necessary.

## Mandatory Task Checkpoints

For authorized retained repository work, apply the shared
[task-commit contract](skills/memory-handling/references/task-commit-contract.md): each independently
verifiable task is validated and committed with explicit owned paths before later task work,
completion reporting, or handoff. This does not authorize writes, adaptation, external operations,
or guideline changes; read-only/no-change work makes no empty commit. Preserve unrelated dirty work;
Git/policy/ownership/verification conflicts stop rather than waive the checkpoint.

<!-- coherence-suite-contract:start -->
## Coherence suite adoption for this repository

Owner-approved 2026-10-06. This section associates **this repository**, not unrelated
projects, with its local memory and documentation owners. Preserve the global portability
rules above for reusable skills and commands.

- Required runtime: pi coding agent, pinned
  `npm:pi-subagents@0.73.1` and `npm:pi-ask-user@0.15.1`. Verify registered, usable
  capabilities before applicable stages; report missing requirements rather than install.
  SpecKit is required only for a project's Standard planning stages, not TinySpec;
  Jev is optional for `finish-session-jev` with manual routing fallback.
- Work routing for this repository:
  - **Direct work:** handle small, bounded inspection, edits and focused checks in the current
    session without a workflow. File counts are examples, not eligibility rules.
  - **Ordinary delegation:** delegate bounded unplanned work to an agent or agents, including
    unexpected repairs during coordinated implementation. Multiple consecutive delegations are
    allowed; do not manufacture a new Coherence workflow for ad hoc work.
  - **Planned Coherence work:** derive implementation tasks from specifications under the
    applicable planning and approval contracts, then execute those approved tasks. Launching a
    workflow runner alone is not using Coherence; adoption is not a blanket workflow requirement.
  - **Larger unexpected work:** ask the owner whether to address it now through bounded delegation,
    plan it through Coherence, or file an issue with the declared tracker and continue the original
    work. Do not infer the answer from agent, file or action counts.
  - Routing grants no new scope or external effects and waives no required acceptance, review,
    safety or permission gates. Preserve ordinary scoped repair authority and existing local overrides.
- Planning (when routed to Coherence): request → `planner` understanding/brainstorming/scope → explicit owner
  TinySpec/Standard choice → reviewed tasks → approved handoff →
  `coordinate-implementation` → `finish-session`. TinySpec uses `tiny-spec`, separate
  tasks and combined approval; Standard uses installed SpecKit and specification/final
  approval gates. Neither automatically creates an Epic.
- Unified memory: this repository's associated store is `memory/`, with `MEMORY.md` as
  its single index for verified trigger-first gotchas and explicit future-directed owner
  guidance. Follow `memory-handling`: read the whole index first, then only matching
  entries; recheck it after writes. Do not substitute global memory. Missing store is
  nonblocking. Only explicit future-directed user feedback authorizes guidance changes,
  never agent-inferred lessons or routine records; executable runs consume approved task
  constraints, not execution-time feedback routing.
- Consequential decisions: before affected planning or changes, use `save-adr` to discover
  the decision owner from this project's routing, read its whole index and relevant accepted
  records, and carry applicable accepted outcomes/source links into briefs and reviews.
  This repository's canonical ADR store is `docs/decisions/`, indexed by
  `docs/decisions/index.md` (owner-selected during bounded initialization on 2026-10-21).
  Absent or ambiguous ownership stops only the affected decision operation for owner confirmation.
- Recovery: no automatic STATE maintenance, summaries/index updates, evidence-only commits
  or reflection. Preserve existing STATE/custom content. Use available conversation summary/
  recent context, selective artifact/Git/check reconstruction and active-child reconciliation
  under the executable interface's [context-first recovery contract](skills/coordinate-implementation/SKILL.md#recover-context).
  Pi sessions record conversation. This repository's canonical active unresolved-work owner is
  [GitHub Issues](https://github.com/elsonidoq/skills/issues), target `github.com/elsonidoq/skills`,
  via `track-open-issue`; `docs/open_issues.md` is preserved historical source only, not an active
  register. Actual historical migration is NOT RUN; future import requires separate apply authority,
  reviewed preview, OI-4/#2 mapping choice and full independent readback. Missing GitHub capability
  or scoped write authority defers the candidate in the response, never creates a local fallback.
- The owner decides whether workers run concurrently or sequentially, including in the same
  checkout. Do not require sole-writer ownership when the owner authorizes concurrency; this
  direction supersedes conflicting single-writer instructions in skills or workflow guidance.
  Concurrent workers must keep explicit task-owned paths and preserve one another's changes;
  overlapping edits or uncertain ownership require coordination, not a blanket concurrency ban.
  Execution delivery retains verified focused task checkpoints.
  Planning must produce granular,
  independently verifiable tasks sized for the selected executor configuration.
  Split independently testable concerns rather than bundling milestones into implementation tasks.
  Product bindings remain selected-config driven; the planning model is not an implementation assignment.
  Every workflow launch in this repository, including continuations and corrective runs, uses
  `.pi/workflow-executor.json`: Terra/medium workers and `openai-codex/gpt-6.1-sol`
  at medium effort for every fresh reviewer session. Do not reuse historical Terra-only
  executor files for new launches or rewrite historical reviewer records.
  Historical approvals stay historical. The latest owner direction supersedes older graph/SQL/
  custody/evidence eligibility mandates: task startup linter has only readable file, parsed list,
  ID/work description, unique IDs, existing dependency references and acyclic dependencies.
- Execution: the existing `coordinate-implementation` CLI runs sequential tasks with normal SDK
  tools, actual specified project checks/manual gates, focused explicit-owned-path Git commits and
  fresh independent read-only final review. SQLite stores ordinary progress/history, not effect
  proof. No manifest, catalogue, cgroup provisioning, session/parent receipts or binding assessment.
  Preserve task-owned path boundaries, unrelated work, hooks/signing, old rows and actual errors.
  Current terminal input is authority when needed; no automatic install, auth refresh, reload,
  legacy restart, expensive failure retry loop or mass conversion.
- Documentation: `docs/index.md` is the routing guide and root directory index;
  `docs/plans/index.md` and `docs/plans/reviews/index.md` map their direct files.
  `README.md` owns setup/workflow, `REQUIREMENTS.md` runtime requirements,
  `.specify/memory/constitution.md` project principles, and each skill's `SKILL.md`
  its operational contract. Follow the routing guide for all other owners.
- **Paseo activation:** In Paseo-hosted sessions the owner cannot execute Pi slash
  commands such as `/reload`. Do not instruct the owner to run `/reload`. When changed
  extensions or tools must be loaded, prepare a fresh-session handoff; the fresh agent
  verifies the checkout, revision, current approval and loaded capabilities before
  launching approved workflow. Do not automatically reload or restart the current session.

<!-- coherence-parsimony:start -->
### Parsimony and Actionable Checks

- Start with the smallest working solution. A speculative concern is not a requirement.
  Omit unnecessary optional behavior without asking about every imagined safeguard;
  surface consequential unresolved trade-offs. Job first; bookkeeping is subordinate.
- New safeguards, limits or blockers need an explicit requirement, actual external/interface/
  platform constraint, or concrete material implementation risk. Cheap necessary protection
  for serious exposed security/data-loss risk need not wait for an incident. Preserve real
  budgets/platform limits; invent no thresholds.
- Weigh false blocking, availability loss, interruption, recovery friction, maintenance and
  legitimate behavior prevented. Unrequested shutdown, expiration, deletion, cleanup,
  throttling and spending/resource ceilings are out of scope by default. Observe/report
  where safe, never instead of necessary protection.
- Reuse SDK/tool/compiler/platform behavior. Check the relevant boundary; repeat only when
  changed state invalidates evidence. Return ordinary safe errors with actionable correction:
  a file-read size error calls for a smaller/paginated read, not a fatal workflow gate.
  Concrete unsafe/invalid state such as target drift stops affected continuation.
- Distinguish original requirements, necessary implementation choices with their basis,
  and optional hardening in existing fields. Agent assumptions remain revisitable, not
  original requirements merely because a plan labeled them REQUIRED. Change binding
  approvals/acceptance only through existing gates.
- Review unnecessary additions as well as omissions. Application/task acceptance proves
  the requested outcome; framework regression/internal proofs are not application startup
  or admission ceremonies. Preserve real tests, permissions and safety protections.
<!-- coherence-parsimony:end -->
<!-- coherence-suite-contract:end -->
