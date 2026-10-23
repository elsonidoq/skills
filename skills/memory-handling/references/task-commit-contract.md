# Mandatory task-commit contract

This is the single owner for package-managed task checkpoints. Consumers link here and
state only their role-specific boundary; they do not copy or weaken this policy.

## Applicability and task boundary

A task is an approved, independently verifiable work unit, not a tool call, phase label,
or entire multi-task batch. A retained repository deliverable (including authorized source,
task-list, evidence, review-fix, documentation, or closeout output) is committed after its
required verification. A read-only, verified no-change, disposable-scratch, or external-only
task creates no empty commit unless it retains a repository deliverable. Standalone writing
skills treat their bounded deliverable as the task.

Existing authorization remains required for every write. This contract neither authorizes
creation, uploads, external operations, guideline changes, adaptation, nor planning changes.

## Required checkpoint

Before subsequent task writes, completion reporting, or handoff, the authorized checkpoint owner must
(the writer in instruction-managed/planning work; the runner in executable runs):

1. establish a task baseline and allowed paths, and inspect the current index/worktree;
2. make only assigned, understood changes and run the required verification;
3. inspect the actual task diff and explicitly stage only task-owned paths; and
4. create one focused path-limited task commit (for example, `git commit --only -- <paths>`
   where compatible) so unrelated staged changes are preserved, using compatible repository
   message, branch, sign-off and signing conventions; then report the baseline/resulting SHA,
   changed files, checks, and residual state.

There is no skip/defer question, owner-exception record, no-Git fallback, or batch commit
substitute. Missing Git, identity/signing/permission failure, a hook/check failure, policy
conflict, uncertain ownership, or missing verification stops with the exact reason. Never
configure identity, disable hooks/signing, initialize a repository, push, rewrite history,
or stage broadly to make a checkpoint pass.

Task-relative cleanliness means no unresolved task-owned changes; it never requires erasing
unrelated staged or unstaged work. Preserve it, including shared-path changes. Same-file or
other ambiguous ownership blocks automatic staging and committing. A workflow that explicitly
uses an initially clean isolated workspace may require whole-worktree cleanliness only for
that workflow.

## Executable run responsibility

For authorized executable Coordinate Implementation runs, workers may propose/produce owned task changes but do not stage, commit, select work or own workflow persistence. The runner establishes baseline/ownership, runs actual specified project checks and manual gates, inspects actual owned diffs, and creates one focused verified owned-path task or repair commit before subsequent mutation or handoff. Never blindly replay Git after interruption: inspect the actual commit and partial work. Unknown/live work, missing verification/Git authority, failed hooks/checks/signing or ownership conflict block the affected operation; no configure-around, broad staging, reset, history rewrite or discard. Read-only/no-change creates no empty commit. Planning/standalone retained artifacts continue to use their authorized writer's existing focused task-checkpoint contract. Ordinary SQLite task progress is permitted; no agent-written narrative STATE, routine summaries/indexes, reflection or inferred guidance. Preserve independent review, existing STATE/custom content, technical gotchas, historical rows, unrelated dirty work and explicit scope/permission approvals. Six task-linter checks govern task validity; no graph, cgroup, manifest, original-session, intent-settlement or evidence-receipt eligibility is required.

This scope is specific to authorized executable runs. Instruction-managed bootstrap work
continues its existing writer checkpoints.
The following coordinator/implementer duties apply to instruction-managed execution only.

## Coordinator and fresh implementer duties

Before first retained writes, and again on resume as relevant, the coordinator verifies usable
Git/commit prerequisites, HEAD, index, allowed paths, required check baselines, and any
pre-existing dirty ownership. It records the task/attempt ID, baseline, allowed paths and
ownership in the existing tracker/evidence convention.

Before writing, a fresh or resumed implementer compares the supplied baseline with repository
state. Unexpected changes or an unresolved prior checkpoint means no edits, cleanup, or
commit: return the blocker and observations. A fresh implementer never adopts unknown work.

The coordinator independently inspects the actual task diff, focused commit, SHA, check
evidence and residual task-owned changes. A report, clean tree, or commit existence alone is
not proof. It rejects discarded, empty-success, unauthorized, or combined-task checkpoints.
If understood, verified task changes remain uncommitted, only the coordinator may recover them
with a focused commit. Insufficient context/ownership/evidence, or a failed recovery commit,
stops dispatch; retain recoverable state and do not bounce a fresh implementer.

A coherent sequential batch still checkpoints every internal task before the next one. The
subagent owns verification, task commits  inside its run. Once
these succeed and task-relative state is clean, it continues to the next authorized internal
task without routine coordinator approval. Do not insert a per-task supervisor message or
acknowledgment wait into a healthy batch. Keep the task baseline, SHA and check results in
the task/runtime return; return the full ordered checkpoint list when the batch returns.

The coordinator audits every returned task checkpoint at the batch boundary before accepting
the batch or releasing external dependents, not between healthy internal tasks. Failed checks,
or commits, unexpected changes, and genuine owner/dependency gates still
stop the subagent and return the blocker to the coordinator. Coordinator commit recovery is
exceptional, never the normal internal-task path. This is instruction-managed execution, not
an interception guarantee.

## Evidence, interruption, and limits

Return each task/attempt baseline, result SHA, checks and outcomes with concrete
command/output/artifact references in existing task/runtime/session conventions.
No automatic STATE maintenance, routine summaries/index updates, reflection or separate
evidence-only checkpoint is required. Missing optional memory storage is nonblocking.
On interruption reconcile actual commits and check evidence; recover a successful SHA
without duplicating its task commit. Inspect failed run/invocation before targeted retry;
unknown cause stops. Later defects need dependency analysis and separately verified
correction tasks, never automatic rollback. Authorized memory guidance follows
[Memory Handling](../SKILL.md).

Operational assertions can check instructions, and temporary-Git fixtures can demonstrate Git
protocol cases such as scoped commits, hook failures and unrelated-work preservation. Neither
proves that an unrestricted model obeys instructions at runtime.
