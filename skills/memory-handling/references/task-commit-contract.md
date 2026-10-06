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

Before subsequent task writes, completion reporting, or handoff, the implementer must:

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
subagent owns verification, task commits and evidence-only checkpoints inside its run. Once
these succeed and task-relative state is clean, it continues to the next authorized internal
task without routine coordinator approval. Do not insert a per-task supervisor message or
acknowledgment wait into a healthy batch. Keep the task baseline, SHA and check results in
local durable evidence; return the full ordered checkpoint list when the batch returns.

The coordinator audits every returned task checkpoint at the batch boundary before accepting
the batch or releasing external dependents, not between healthy internal tasks. Failed checks,
commits or evidence persistence, unexpected changes, and genuine owner/dependency gates still
stop the subagent and return the blocker to the coordinator. Coordinator commit recovery is
exceptional, never the normal internal-task path. This is instruction-managed execution, not
an interception guarantee.

## Evidence, interruption, and limits

Record each task/attempt baseline, result SHA, checks and outcomes concisely in the existing
factual evidence/tracker. For new coordination runs, append a compact checkpoint row or
exception to the same run `SUMMARY.md`, not a separate task evidence file. After a task commit,
capture its SHA and commit the resulting run-summary/index update as a distinct, focused
evidence-only checkpoint before later task writes or handoff; it is not an implementation-task
substitute. Older per-task evidence files remain valid and need no default migration. On interruption reconcile commits and pending evidence,
and recover a successful reported SHA without duplicating it. Inspect a failed attempt before
retry or escalation. Later defects require dependency analysis and separate verified correction
tasks, never automatic rollback.

The brief project-owned current-state snapshot follows the
[coordinator snapshot/recovery lifecycle](../../coordinate-implementation/SKILL.md#brief-current-state-and-recovery),
not a new task ledger. Include coordinator state updates only at that owner's exclusive write
boundaries, coalescing same-boundary evidence and skipping unchanged status; polling and healthy
worker internal progress do not require coordinator writes or duplicate checkpoint records.
Local implementer duties remain unchanged. Reference already verified task/evidence commits,
never recursively commit a snapshot's own SHA.
A returned child ID is written immediately; pending coordinator-owned state is explicitly excluded
from worker paths and committed at the safe coordinator boundary, never by racing the worker's
Git/index. This does not waive any internal task/evidence checkpoint, ownership check or failure stop.

Operational assertions can check instructions, and temporary-Git fixtures can demonstrate Git
protocol cases such as scoped commits, hook failures and unrelated-work preservation. Neither
proves that an unrestricted model obeys instructions at runtime.
