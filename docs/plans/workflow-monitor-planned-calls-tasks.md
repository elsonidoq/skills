# Workflow monitor planned calls — executable tasks

[Authoritative TinySpec](workflow-monitor-planned-calls-tinyspec.md) · [Executable JSON](workflow-monitor-planned-calls-tasks.json)

## Preparation and approval record

Owner selected TinySpec → Tasks → Implement and authorized task preparation/checkpointing. This is a separate task artifact, not approval. Parent inspection, independent planning review and combined **current-content** source/task approval (including the proposed palette) remain pending. Implementation and visual acceptance have not occurred. Temporary preparation labels are provenance here, not worker instructions.

Producer verified clean branch `update-workflow-monitor-planned-agent-calls`, task-production baseline `51174c0e19f699a51dae85082c8eb67aa5c220e6`. Source SHA256: `a8f31142f3fcf0c949b131ada3cea776de4f156fe35844b9cd8b606631d92da1`; source itself remains unchanged. Source's older implementation baseline is historical context, not task-production HEAD.

Producer directly read `/home/dev/.paseo/worktrees/0zfm1a0e/vengeful-camel/.pi/workflow-executor.json` **before decomposition**: worker `openai-codex/gpt-5.6-terra`, effort `medium`; every fresh independent reviewer `openai-codex/gpt-6.1-sol`, effort `medium`. Saved task producer `openai-codex/gpt-6.1-sol / medium` is unchanged, not an implementation binding. Six outcomes split the retained contract, dispatch readback, graph reconciliation, rendered lifecycle, nonmetric Details and metric presentation at independently testable seams. Shared-path dependencies are sequential; each task verifies/checkpoints before the next. No arbitrary quota, prototype programme or tests-only milestone.

## Shared worker brief

Read this brief, the whole linked TinySpec and your JSON task entry. The TinySpec alone owns product requirements; preserve **R1–R5 and A1–A5 unchanged**. Historical readability/complete-graph/activity plans and SDD guidance are not additional intake. Consume predecessor interfaces and still-applicable permanent test evidence; failed/unrun proof cannot release dependent reliance. The JSON's task-local REQUIRED items supply pass conditions, actual production-path checks, evidence and permissions; they are not a new startup schema.

### Accepted decisions and authority

Carry these applicable source outcomes into implementation and review (links plus the task-local mappings below, not link-only compliance):

- [ADR-0003](../decisions/ADR-0003-current-launch-authority-and-neutral-tasks.md): executable task instructions are authorization-neutral; current scoped launch authority supersedes historical planning-only wording without rewriting history. Returned execution is **not acceptance** (R1/R2). Preserve real checks/manual gates and unrelated-work/paid-scope boundaries.
- [ADR-0004](../decisions/ADR-0004-shared-routine-worker-permissions.md): ordinary scoped fixes and small isolated fixtures/databases need no repeated approval; preserve unrelated data, credentials, actual checks and external-action boundaries. The current owner's narrower exclusions control: **no dependency install/link/bootstrap, real paid workflow, agent restart/reload or external operations without applicable authorization**. No automatic setup fallback.

ADR-0003 maps concretely to T001/V2 neutral task/check handling, T002/V2 full-snapshot execution versus acceptance, T003/V2 and T004/V1 successful rejecting reviewers, T005/V2 preserved verdicts and T006/V2 separate final review/visual acceptance. ADR-0004 maps concretely to each task's local synthetic fixture permissions and actual non-waivable checks, especially T001/V2 privacy/nonfatal recording, T002/V1 actual-helper proof and T004/V1/T006/V1 bounded local browser/databases with narrower exclusions. No memory/guideline/STATE/admin-ledger update is work scope.

### Production boundaries

- Retain explicit full work description and initial-review intent additively. Generic phases do not schedule a review. Old missing text says “Full task text not recorded”; never reconstruct from current task files. Record no private prompts/answers/arbitrary payloads; keep optional recording nonfatal and public DTOs closed/sanitized.
- Before UI reliance, prove exact worker root/kind/chain and review dispatch identity through real producer/Store/Reader helpers. Unique same-run/task initial worker root only; no earliest/label/first-task match. Multiple roots stay distinct/unknown. Initial review binds unique ordinal 1 plus exact ID. Fixing round is not a prompt call: round-only notice in Details/history, exact individual nodes only on invocation evidence. Subsequent review only on actual dispatch, not rejection. Preserve attempts/rejected history and unknown relations. Add only demonstrated necessary binding facts with a reason; return material contract changes for affected approval rather than guess.
- Reuse `app.py` full-snapshot `_execution_details`/`_task_progress`; paged records cannot authoritatively imply running, success, waiting or blocked. Stopped unstarted plans do not promise future work. Task checkpoint completion is not call success. Declared dependencies are distinct from recorded causal links.
- Every task-associated node has useful designation/source-order Task N, title and role, with human Fix 1/Review 2 distinctions. No opaque IDs or raw keys/enums/dotted provenance anywhere in graph labels, Details, history or expanders. Do not relocate dumps. Keep internal identities for attribution/API/URLs/history/correction navigation and preserve safe typed history/findings.
- Translate metric evidence, not arithmetic: This call / Task total / Overall run; Session total only separate context. Preserve subtotals, dispatch/interval coverage, missing attribution and artifact continuity. No session substitution, cumulative summing or already-included subset addition. Only supported Input tokens / Output tokens / Cost / Duration facts.
- Palette proposed for combined approval: grey pending, blue running, green successful, red failed, amber evidence-backed waiting/blocked; neutral unknown with explicit text, readable dark text and legend. Reviewer verdict stays separate from execution color.
- Preserve flat measured ELK DOWN, status-only identity/viewport reuse, selection/pan/zoom/drag, size/topology relayout without arbitrary reset, stale guards, 60-second polling, navigation/filter/Back/Forward/history/correction lookup and read-only SQLite/HTTP/security. Reuse README graph-layout guidance and locked ReactFlow 12.12.0 / ELK 0.11.1. No groups/layout rewrite, dependency/engine change, database migration without demonstrated need, new metrics system or harness. Monitor never imports/invokes writer or repairs stores.

### Checks, environment and checkpoints

JSON check commands were selected from actual package scripts (`build`: `tsc --noEmit && vite build`; `test`: Playwright), test files and runner `runtime/coherence_workflow/intake.py` / `verification.py`. Runner consumes `checks` and optional REQUIRED `check` commands; these tasks list each command once in `checks`. REQUIRED mappings explain observable evidence rather than duplicating commands. Working directory is repository root. Backend commands explicitly use `workflow_monitor/.venv/bin/python` and `PYTHONPATH=runtime:runtime/tests` (including the existing fixture support imports); browser config uses already-installed `/usr/bin/google-chrome`, and production fixture uses that same monitor interpreter. No initialized execution store/model launch is needed for planning intake validation.

**Focused readiness gap:** `workflow_monitor/.venv` and `workflow_monitor/web/node_modules` are absent here. Application tests/build/browser checks are **NOT RUN / tooling UNAVAILABLE**, not green. Execution verification requires a supplied prepared isolated interpreter with locked monitor dependencies, installed locked web dependencies, local Chrome and built assets; verify actual versions/capabilities, build before serving. Do not install/link/bootstrap or borrow unrelated checkout state. Missing tools stop affected checks/reliance until supplied or separately authorized; this is not an environment-repair task. Local synthetic fixture servers are allowed; no automatic agent restart/reload. Fixture teardown stays with each task and touches only its own temporary resources.

Keep ordinary fixes/tests/docs with delivery. Use permanent actual production helper tests, not disposable prototype reports. T001 and T002 establish data evidence before T003; T004 composes producer → Reader/HTTP → **built production browser** at the first usable UI boundary. T005/T006 extend that same case, not a second harness. Existing `test_chain.spec.ts` source-Vite geometry tests remain valuable interaction evidence but do not substitute for production-browser evidence. Rerun affected proof after changes; retain unchanged applicable evidence without ceremonial duplication.

Own only the exact JSON `owned_paths`. Preserve unrelated work/old rows/hooks/signing. Runner owns actual verification, diff inspection and focused explicit-path task commits in executable runs; workers do not stage/commit. Missing verification or Git/ownership conflicts stop the affected checkpoint, never configure around them. A necessary unlisted producer fix is an affected ownership/scope gap, not permission to edit outside paths. README updates compare documentation with each delivered behavior, not historical plan rewrites.

## Ordered human view

The JSON is executable authority for work units; this is a concise parity view. Each task's normal tests/docs and teardown are included.

- [ ] T001 Retain explicit task work text and initial review intent safely
  - **Depends**: none
  - Additive descriptor → normalized closed public readback; actual Store/Reader proof, old compatibility/privacy and nonfatal recording.
- [ ] T002 Expose exact scheduled calls and round-only notices before observations
  - **Depends**: T001
  - Safe dispatch/attempt/invocation facts and full-snapshot qualification; exact-binding sufficiency proof before graph reliance.
- [ ] T003 Reconcile planned slots with exact calls in the production graph projection
  - **Depends**: T002
  - Persistent known plans, unique exact reconciliation, distinct attempts, human labels and declared-versus-recorded edges; production `graphFor` tests.
- [ ] T004 Render planned-call lifecycle with stable measured interactions
  - **Depends**: T003
  - Lifecycle palette/text/legend and first synthetic production-browser boundary; matching/transitions plus geometry, refresh, selection and navigation.
- [ ] T005 Present full task text and human typed Details/history without identity dumps
  - **Depends**: T004
  - Every nonmetric selection/expander/history variant; full retained text, useful typed history, readable navigation without removing routing identities.
- [ ] T006 Translate scoped metric evidence and complete representative production-view acceptance
  - **Depends**: T005
  - Accurate human metric scopes/incomplete evidence, complete forbidden-content union and representative production screenshots; relevant security/continuity and full web regressions.

## REQUIRED source coverage

This table maps the unchanged source criteria to task-local pass/evidence/permission items in JSON. No criterion is replaced by a successful process exit or documentation link.

| Source | Delivery and observable evidence |
| --- | --- |
| R1 / A1 | T001/V1 retains explicit pre-agent intent/text; T002/V2 provides pre-page qualified state; T003/V1 proves all plans/later nodes/stable exact matching across polling; T004/V1–V2 observes production-browser transitions, retained selection, stopped/unknown qualifications. |
| R2 / A2 | T002/V1–V2 proves dispatch-before-observation, round-only versus exact prompts, retained rejection/attempts and execution/acceptance; T003/V1–V2 proves exact roots/review identity/ambiguity and declared versus actual edges; T004/V1 composes recorded rejection → fixing → rereview without prediction. |
| R1/R3/R4 / A3 | T001/V1 full long work text and old absence; T003/V2 designation/source-order numbering/title/role/repetition; T004/V1 readable lifecycle/legend/verdict; T005/V1 every task/call Details variant with full text/state/outcome/findings; T006/V1 available scoped metrics. |
| R4/R5 / A4 | T005/V1–V2 nonmetric forbidden-content/typed-history translations and routing/history continuity; T006/V1 numerical scopes/subtotals/coverage/no double counting; T006/V2 all graph/Details/history/expanded exclusions, including seeded IDs, raw keys/enums and dotted provenance, with navigation preserved. |
| Preservation / A5 | T001/V2 closed DTO/old compatibility/nonfatal recording; T002/V2 read-only HTTP/paged-evidence/lineage/metric continuity; T003/V2 unchanged flat DOWN engine; T004/V2 measured geometry/edges/drag/pan/zoom/selection/status-only reuse/stale guards/60-second polling; T005/V2 navigation/history; T006/V1–V2 artifact/security/build/browser regression union. |

All five required behaviors and all five acceptance criteria have concrete REQUIRED mappings; paths, commands and local permission evidence are in the corresponding task entries. These are permanent delivery tests, not an additional eligibility machine.

## Post-run handoff and acceptance convention

The selected executor runs the six tasks sequentially with focused checkpoints and **fresh independent read-only full-range implementation review** (Sol 6.1/medium); do not substitute task returns or review of only the last commit. Report actual range, findings/dispositions and real check outcomes, including missing evidence.

Retain representative **built-production** screenshots via Playwright `testInfo.outputPath`, attach/return accessible artifact paths and tested revision. Show overview/node text/state legend/dependencies, expanded full task text/Details, and usable interactions; automated geometry/interaction assertions accompany them. Do not stage generated screenshot directories or invent new evidence-ledger files. Preserve/copy necessary ephemeral artifacts to the run's existing accessible output area before cleanup; report location to parent/owner.

**Owner post-run visual acceptance stays pending until explicit inspection/approval.** It is not a pre-dispatch gate for screenshots that do not exist, and the worker must not halt to ask for screenshot approval. Automation/screenshots and successful independent review do not supply owner visual approval. Do not claim feature fully accepted beforehand or same-run/live observation from synthetic tests. No real paid workflow is required. Planning review/combined approval must disclose the exact tooling gap above rather than assert execution readiness.
