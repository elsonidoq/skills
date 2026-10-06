# Mandatory task commits — TinySpec

## Provenance and status

Producer: `planner`; depth: **TinySpec**, explicitly selected by the owner. Preparation binding: `openai-codex/gpt-6.1-sol`, selected through `ask_user` as “Current Sol”; this is a run-local binding for bounded `sonnet-class` preparation, not a global model policy.

Status: preparation; separate tasks and planner review precede combined source/task/implementation approval. The owner's “I approve” settled the pragmatic design below, not an unseen implementation task list.

Input: [original draft](mandatory-task-commits.md) and owner dialogue. This TinySpec supersedes the draft's proposed runtime extension gate and mandatory adapter availability. The draft remains historical input, not parallel implementation authority.

Owner requirements: every retained task change must be committed; never ask whether to skip/defer the checkpoint. Owner-approved approach: implementer commits; coordinator independently checks and recovers missing commits; a fresh implementer encountering unexpected changes does not write or commit and returns to the coordinator. Check every task, including tasks inside reused batches. No runtime extension gate.

## Outcome and scope

Provide a consistent, non-waivable task-commit contract across the 22 distributed skills, their operational references and relevant package prompt entry points. Prevent starting subsequent work with uncommitted task-owned changes under package-managed execution and retain evidence sufficient for inspected retry/recovery.

Include authorized retained source/planning, implementation, skill, documentation, review-fix, memory/evidence and closeout changes. Read-only and verified no-change tasks need no empty commit. Disposable scratch work and external-only operations need no repository commit unless they retain repository deliverables. Existing authorization remains necessary before any write.

Global asset portability, task/class semantics, sequential delegation, coherent batches, model selection, guideline approval and independent final implementation review remain unchanged.

Exclude runtime extensions/tool interception, new orchestration engines or mandatory execution-state schemas, model-routing changes, automatic history rewrites, pushes/deployments, package installation and paid/live probes. Do not rewrite historical review records into current policy.

## Verified constraints and evidence

- `skills/coordinate-implementation/SKILL.md`, Execute and Integrate: already requires separate verified task commits before the next task; nearby policy and Finish text explicitly permits owner skip/defer decisions. Remove these exceptions.
- Its batching and briefing sections preserve task checkpoints inside coherent sequential batches; final review occurs after implementation commits, not after every task.
- `skills/infographic/SKILL.md` currently says not to commit without an explicit user request. Align authorized retained repository output with automatic checkpoints without granting creation/upload authority.
- `skills/memory-handling/references/project-coordination.md` requires focused initialization commits, explicit paths, unrelated-index/worktree preservation and failure stops. Reuse this safety boundary, not blanket staging or whole-repository cleanup.
- `skills/incorporate-skill/SKILL.md` prohibits writes/commits before adaptation-plan approval; preserve that approval boundary. `using-git-worktrees` prohibits silently changing ignore rules; preserve its workspace/setup choices, never turn them into a commit waiver.
- `scripts/check-planner-workflow.py` freezes coordinator execution with `EXECUTION_SHA256`; intentional policy changes need a reviewed updated digest plus specific assertions/mutations, not removal of protection.
- Existing coordinator tests check text only. Do not claim these prove actual agent compliance.
- Project coordination store: `memory/coordination/`; guidelines: no approved entries. No gotcha-memory association is declared in AGENTS.md; coordination association is declared in README. No learned guidelines are changed.
- Dependencies: existing Python 3 validation and Git only. No new dependency/API research is needed because runtime integration is excluded. Direct Git behavior must be tested in temporary repositories rather than assumed from prompt wording.

## Required behavior and bounded approach

### A1 — Single policy owner and complete coverage

Create a shared reference at `skills/memory-handling/references/task-commit-contract.md`, distributed through the package's existing reference/link conventions. All skill entry points link the shared owner and specify their applicable role/boundary. Update AGENTS.md, REQUIREMENTS.md, README, docs/index.md, relevant SDD guidance and constitution consistently. Audit package prompts, including SpecKit implementation entry, so active routes cannot offer an alternate waiver path. Do not change vendor planning semantics unrelated to commits.

A task is an approved independently verifiable work unit, not each tool call, an entire multi-task batch, or an arbitrary phase label. Standalone writing skills define the bounded deliverable as their task; preparation source and task-list production remain separate deliverables. Factual execution evidence is part of a bounded task or an explicitly identified evidence-only closeout task, not a reason to leave task deliverables uncommitted.

### A2 — Mandatory commit, no waiver question

After required verification, each retained-writing task has a focused Git commit before subsequent task writes, completion reporting or handoff. No skill asks to omit/defer it or proceed without Git; no owner-exception record or commit-every-batch substitute exists.

Missing Git, identity/signing/permissions, conflicting policy, failed checks/hooks/commit, uncertain ownership or missing verification blocks execution with the exact reason. Respect higher-priority instructions; policy conflicts stop rather than bypass them. Compatible message/branch/sign-off conventions remain valid. Never auto-configure identity, disable hooks/signing, initialize a repository, push or rewrite history to make a checkpoint pass.

### A3 — Coordinator preflight and baseline

Before the first task's retained writes, coordinator verifies usable Git/commit prerequisites and inspects HEAD, index, allowed scope and required check baselines. Repeat relevant checks on resume.

Record task/attempt ID, baseline revision, allowed paths and pre-existing dirty ownership in the existing tracker/evidence convention. If overlapping pre-existing changes prevent safe ownership/recovery, use an already-authorized isolated workspace or stop. Never assume HEAD captures dirty baseline content.

“Clean” means no unresolved uncommitted task-owned changes, not an obligation to erase unrelated work. Entire-worktree cleanliness is required only for a workflow explicitly using an initially clean isolated workspace. Preserve unrelated staged and unstaged changes, including within shared paths; ambiguous same-file ownership blocks automatic staging/commit.

### A4 — Implementer checkpoint and fresh-session guard

Implementer verifies and commits only assigned changes, then reports task ID, baseline/commit SHA, changed files, actual required check outcomes and remaining state. In a multi-task batch this happens before each next internal task, without requiring a new agent session or per-task independent review.

Before any writes, every fresh/resumed implementer checks its supplied baseline and repository state. Unexpected changes or an unresolved prior checkpoint mean no edits, cleanup or commits. Return the blocker and observations to the coordinator. A fresh implementer never adopts or commits unknown work.

### A5 — Coordinator verification and recovery ownership

Coordinator checks Git state, actual task diff and required check evidence; an agent report, clean worktree or commit existence alone is insufficient. Verify a task-specific focused commit, authorized content and no residual task-owned deliverable changes. Reject discarded changes, empty-success reports and several tasks combined into one checkpoint.

If verified, understood task changes remain uncommitted, coordinator commits them and checks the result. If context, ownership or check evidence is insufficient, inspect/re-verify within authority or stop. Never commit failing or unknown changes as successful work. If recovery commit fails, retain recoverable state and stop; do not launch a fresh implementer or create a bouncing retry loop.

Coordinator-only committing requires an implementer pause after every task until commit verification completes. A delegated batch that commits successfully itself may continue internally only after that task's direct Git/check checkpoint; the coordinator audits each returned checkpoint before declaring batch completion/releasing external dependents. This remains instruction-managed execution, not an interception guarantee.

### A6 — Durable completion, interrupted recovery and retries

Completion requires task/attempt baseline, resulting SHA and check evidence. Record metadata in the existing task/run artifacts. Avoid self-referential SHA claims: capture the task SHA after commit, and commit ensuing evidence updates as a bounded evidence-only checkpoint before subsequent task writes/handoff; distinguish this from implementation task commits.

On interruption, reconcile actual commits and pending evidence before resuming; recover a successful-but-unreported commit without duplicating it. Evidence-write failure remains a blocker.

Inspect failed attempt cause before retry/escalation. Preserve evidence and unrelated work; restore only the established failed-task baseline where authorized. Never infer weak-model causation from failure alone. A defect discovered after dependent commits requires affected-dependency analysis and separately verified correction tasks; no automatic unsafe single-commit rollback.

### A7 — Proportionate verification and truthful limits

Add operational-section consistency assertions and mutation tests for omitted rules/links, skip/defer questions, missing fresh-implementer guards and missing coordinator recovery/stops. Extend relevant existing checks rather than introducing an unrelated framework.

Use real temporary-Git fixtures to verify scoped commits, unrelated staged/unstaged preservation, residual task changes, missing/incorrect/combined task commits, failing hooks and interrupted SHA recovery. Fixtures must not modify the current repository/configuration or invoke providers. Label them Git/protocol fixtures, not live model-obedience proof.

No new runtime requirement is introduced. The enforced package contract has layered explicit guards and observable checkpoints but does not mechanically prohibit an unrestricted model from ignoring them. Acceptance and documentation must state this limitation.

## Acceptance and required checks

All A1–A7 are REQUIRED. Validate each against concrete inventory rows, operational text, mutation outcomes and bounded Git fixture results. In particular: no commit-waiver question; no next-task start after unresolved checkpoint; coordinator alone recovers contextual commits; no fresh-agent blind commit; unrelated work preserved; all retained-writing skill routes covered.

Run the existing skill lint, coordinator intake/batching tests, planner workflow and mutation suites, task-generation dependency checks, new focused commit-contract/Git fixtures and `git diff --check`. Run broader checks only for a demonstrated changed seam. Live model tests, extension tests and provider operations are excluded; report no runtime-obedience proof. Fresh independent final implementation review remains required at coordinator acceptance.

## Risks and rollout

Package-wide retained-artifact commits intentionally change currently opt-in commit behavior, particularly infographic output and standalone closeout. This is the requested policy change; creation/adaptation/guideline approvals remain intact. No migration of prior history or automatic cleanup of dirty repositories. Adoption documentation must explain hard stops under incompatible policies. After implemented global skill/config changes, instruct `/reload` inside pi; plan-only documents need no reload.
