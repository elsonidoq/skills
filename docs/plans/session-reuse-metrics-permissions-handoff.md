# Execute the approved session-reuse, metrics and recovery tasks

Implement the 22 tasks in `docs/plans/session-reuse-metrics-permissions-tasks.json`, preserving their individual acceptance criteria, dependency order and focused commits. Deliver the requested runtime behavior and independent final review—not another planning round. This prompt is self-contained; no prior chat, temporary report or agent session is needed.

## Owner authority and review

After the source/task review, the owner requested a fresh-context execution prompt, finish-session closeout, commit and push. In an explicit approval question naming the reviewed 22-task source/task set and fresh-agent implementation, the owner selected **“Approve and authorize execution.”** The question retained separately scoped paid API approval. This is combined source/task approval and implementation authority, not merely permission to commit planning files.

This authority supersedes the earlier **pending approval / implementation forbidden** preparation labels in the linked source, human tasks and individual task descriptions. It changes no requirement, task acceptance or paid/external-action boundary. Do not ask for the same combined approval again. Material scope changes still require the owner.

Fresh independent Sol 6.1/medium planning review read the source, human tasks and JSON fully and found **no issues** in (1) parsimony, (2) Terra/medium task granularity or (3) substantive correctness/coverage. Its verdict was ready for combined approval; the explicit approval above followed. Review checked text/JSON structure, dependencies and committed whitespace, with selected read-only runtime inspection. It did **not** run application/runtime/provider acceptance.

Reviewed content identities, for provenance rather than new launch/hash gates:

| Artifact | SHA256 |
| --- | --- |
| `docs/plans/session-reuse-metrics-permissions-tinyspec.md` | `af92ea8835af9ac06bb69a4b1765f2edbbe082507934f711179b139c30229af2` |
| `docs/plans/session-reuse-metrics-permissions-tasks.md` | `179c8749917302aee12af83a4d4f0e190b650e513a7805237228cc826040b24d` |
| `docs/plans/session-reuse-metrics-permissions-tasks.json` | `328546066da2188bc57414905e3b79af2e290e77d8ae7a83851841013dfbbd1c` |

Source checkpoints: `070a73d` removes filesystem gates; `b560ad8` adds ordinary recovery. Task checkpoint: `14741a4`. Later commits from other work are not a reason to reset, require the old HEAD, or reject execution.

## Workspace and read first

- Continue in the **same worktree**: `/home/dev/.paseo/worktrees/0zfm1a0e/tearful-alpacka`.
- Branch: `follow-attached-workflow-migration-instructions`; remote: `origin` (`git@github.com:elsonidoq/skills.git`). Do not create another worktree or switch/reset branches.
- Read `AGENTS.md`, then `memory/MEMORY.md` in full and only matching gotchas. The index was empty at closeout; consult current content, not a global substitute.
- Read the **entire** TinySpec and task JSON above; the human task file is the concise dependency/outcome map. TinySpec is requirements truth; JSON carries complete work descriptions, scopes and REQUIRED commands.
- Read `skills/coordinate-implementation/SKILL.md`, `docs/coordinate-implementation.md`, `docs/coordinate-implementation-schema.md`, and `skills/memory-handling/references/task-commit-contract.md` for current execution, persistence and checkpoints.
- `docs/index.md` routes documentation ownership. Consult applicable accepted decisions through the existing `save-adr` discovery/propagation contract; do not invent an ADR store or turn its absence into a general execution gate.
- `.pi/workflow-executor.json` is the repository-selected launch configuration: **`openai-codex/gpt-5.6-terra`, medium workers; `openai-codex/gpt-6.1-sol`, medium fresh reviewers**. The planning model is not an implementation assignment. Do not substitute historical executor files or silently change profiles.

Other agents may concurrently prepare monitor plans. Their files and commits are unrelated unless an actual assigned action needs them. At preparation, another agent was editing the monitor-complete-graph task pair and plans-index entries. That separate plan is **not** part of this execution. Inspect current task actions and preserve unrelated staged/unstaged/untracked work; do not require a clean tree or registration of unrelated files.

## Non-negotiable owner decisions

1. **No filesystem/Git continuation policing.** Any file appearance, modification, deletion, size change, generated output, index change or incoming commit is not a stop/permission trigger. Delete HEAD/full-index/dirty/unclaimed-path gates and snapshot admissions at startup, commands, task boundaries and resume. No renamed conflict watcher, proof-of-unrelatedness, whole-tree inventory or passive check-invalidation veto. Status/diff can inform actual task edits/commits, not authorize a halt.
2. **Protect actual actions, not an unchanged worktree.** Edit only assigned source; stage/commit exact intended task paths/hunks; never adopt, overwrite or delete unrelated work. Generated-output declarations guide commands/selective known-artifact cleanup, not admission. No broad staging, blanket `dist/` cleanup, `git clean`, reset/rebase/history rewrite, hook bypass or disabled signing. Preserve incoming ancestry, actual checkpoint parent and the original selected review-base→actually-reviewed-head range.
3. **Automatically correct ordinary errors.** Runner-owned check/checkpoint failures must deliver actual command/error back to the authorized same-task/fixing context for reasoned scoped repair and real affected REQUIRED reruns. This must work at engine boundaries, not just prompt wording. Ordinary read-size/pagination/argument/edit errors, local isolated dependency setup, whitespace/source/hook issues and SDK-supported transient recovery are not first-error terminal failures. Required history writes recover safely before dependent mutation; optional metrics/monitor/telemetry-storage failures report gaps and continue. Lock busy means cancellable waiting/busy, not failed tasks or expensive attempts.
4. **Recovery is not blind replay.** Record real failures and attempts. Reconcile possibly successful commits before retry; never duplicate completed tasks/effects or invent missing history. Inspect terminal expensive failures and their failed invocation before cause-targeted continuation, preferably in the existing session. No blind expensive relaunch, provider/model escalation, automatic auth refresh, unapproved paid launch, daemon, novel retry framework, invented budgets/timeouts or unchanged failed-command spin. Correct ordinary problems autonomously; retain honest limits for denied authority, cancellation, unresolved unsafe replay and genuinely unrecoverable failures.
5. **Keep the review chain bounded.** Implementation→Review 1→ONE fixing round→Review 2. Immediate approval skips fixing/re-review. Safely correctable errors within that fixing round remain within it; ordinary pre-review task correction consumes no post-review round. Every reviewer is fresh, independent and read/search-only. Maximum TWO actual reviews and ONE fixing round across resume. Normalize safely recoverable review formatting only without inventing a verdict or extra execution. Final rejection/unrecoverable failure retains findings/work and notifies the owner. Record/display actual distinct executions and explicit causal edges; preserve initial rejection, never infer execution from names/timestamps.
6. **Synthetic acceptance only.** Never use a real implementation task, task list, historical/current run or actual project build as a regression workload. **Never reproduce historical T010 or run the actual monitor web build for validation.** Use tiny purpose-built dummy work/disposable projects against production helpers/SDK/Git boundaries. Delivering this approved list is implementation, not permission to replay it as an acceptance fixture. V8 is ONE small synthetic case—new unrelated doc, modified unrelated file, intervening commit—not an extensive matrix. Frontend checks use existing source-module tooling/synthetic fixtures; no new browser/package download for V9.
7. **Retain the original product requirements.** Reuse requires settled compatible resources/role/affinity/authority and measured effective pre-compaction headroom **>=150000 tokens** by default; unknown/ineligible state selects fresh, not a workflow halt. Preserve per-task input/output/cache categories, available estimated USD, successful compactions and distinct task membership without cumulative double counting; unknown is not zero and reviewers have separate totals. Explicit same-run resume preserves original inputs, authority, completed checkpoints, attempts and review range. Keep ELK layered RIGHT/React Flow and initially fit MOST actual execution context into the available graph panel, retaining pan/zoom/details and deliberate navigation on unchanged polling.

Routine scoped fixes, isolated tests/servers, necessary isolated dependency setup and task-generated-output lifecycle are authorized. Before affected paid calls, settle any **missing explicit** selected-provider/live-validation or application/test API scope through current owner input, once per unchanged scope; credentials do not imply consent. This approval is not blanket permission for global installs, credentials changes, deployment, arbitrary paid services or pushes from implementation workers. Do not silently skip a required live claim: report NOT RUN/UNAVAILABLE and its precise dependency if permission/capability is absent.

## Task order and current state

No T001–T022 implementation or runtime acceptance was performed during planning. Begin with dependency-ready **T001**; follow actual JSON dependencies, not only the numbering. Each task includes its own tests/docs and verified explicit-owned-path checkpoint before dependents.

| Task | Bounded outcome |
| --- | --- |
| T001 | Routine authority propagation to all roles |
| T002 | Paid scope settled before affected calls |
| T003 | Remove passive path policing; action-scoped source/artifacts |
| T004 | Runner-check failure→same-task corrective return |
| T005 | Original inputs and operation-local attempts/history |
| T006 | Required persistence correction before mutation |
| T007 | Checkpoint correction and actual commit reconciliation |
| T008 | SDK saved-session reopen/rebinding and ordinary recovery |
| T009 | Deterministic pure session selection |
| T010 | Compatible task routing and corrective continuations |
| T011 | Honest usage/compaction deltas |
| T012 | Distinct membership/reporting and nonblocking telemetry gaps |
| T013 | Durable review/fix identities, findings and consumed rounds |
| T014 | Explicit optional execution-chain recording |
| T015 | One scoped fixer consuming check/checkpoint correction |
| T016 | Bounded reviews/fixer controller and safe result correction |
| T017 | Actual-chain projection and safe findings |
| T018 | Actual-chain view with initial graph overview |
| T019 | Cancellable lock waiting/busy without failed work |
| T020 | Explicit same-run resume without drift admission |
| T021 | Unfinished task/artifact actions from operation history |
| T022 | Actual cancelled-writer drain before explicit continuation |

Useful historical implementation references are `a5638c0` (selector/SDK/delta accounting), `053352e` (projection/recovery principles), `aa19186` (removed 150k rule), `ae04e6c` (attempt/history compatibility), and `b9ab5a7` (broad deletion). Adapt the useful seams; do not wholesale restore old graph scheduling, manifests, receipts, cgroups, custody/effect frameworks or historical migrations.

## Launch and delivery

- Use `coordinate-implementation` and the actual current CLI help/operating guide; do not improvise an alternative orchestration protocol. Reconcile actual implementation writers/unfinished effects without treating unrelated filesystem activity or old SQL rows as authority.
- In a fresh Paseo session, verify the checkout and loaded `coordinate_implementation_start` **and** `coordinate_implementation_reply` tools. They were available in the preparing session; that does not prove availability in yours. Do not run `/reload`, automatically restart, install extensions, broaden trust or silently fall back to a detached shell/CLI if the required parent bridge is missing. Report the concrete capability needed.
- For attached launch, call `coordinate_implementation_start` with `tasks` set to the absolute canonical JSON path, `executor` set to the absolute `.pi/workflow-executor.json` path, and a new descriptive `run` ID. Answer exact pending owner questions via the correlated reply tool. Do not launch now merely to inspect history.
- Never recursively launch the workflow from a worker or let workers stage/commit/manage its state. The runner owns sequential selection, actual required checks, focused commits and review. Native delegated work, if specifically needed and authorized, remains background-only with one writer; do not replace the governed runner after an infrastructure failure without owner approval.
- The starting runtime does **not** yet have the planned reuse/resume/recovery behavior. Do not assume a successful start proves it, use missing future commands, restart a historical failed run, or test new recovery against the delivery run. Prove each new seam with its specified synthetic acceptance, and update the existing skill/guide/schema owners in the task that changes them.
- Preserve sole implementation-writer ownership, real checkpoints, old SQLite rows and actual failure history. Correct routine problems without per-task approval ceremonies. Ask only at material authority/product/complexity boundaries; no new launch gate, universal suite, arbitrary size limit or evidence-only commit.

## Verification already performed and return contract

**PASS, planning only:** both Markdown/JSON task-order validators; 22 matching outcomes/dependencies and source mappings; pure parsing/links and scoped whitespace checks; fresh independent review with no findings. **NOT RUN:** implementation, real SDK/provider lifecycle/usage/compaction, check/checkpoint/storage recovery, resume/cancellation, monitor/view acceptance or deployment.

At task boundaries retain actual task/attempt identity, owned commit SHA/parent, checks/results and precise residual state using existing runtime/session conventions—not new STATE files or narrative evidence commits. A green component is not proof of its consumer; run the task's smallest required production-boundary check. Never label unrun/failed proof as passed.

Return the ordered task checkpoints, actual verification and independent full-range review/fixing outcome, unresolved blockers and NOT RUN/UNAVAILABLE items. Close with `finish-session` against attributable changes; no inferred memory lessons, unrelated issue edits, automatic deploy, reload/restart or new permission assumptions.

**Exact next action:** in the verified worktree above, read the authoritative source/task/config/contracts, verify the fresh parent bridge and actual writer ownership, settle only genuinely missing paid scope, then start the approved 22-task execution with `.pi/workflow-executor.json`. No re-planning or repeat combined approval is needed.
