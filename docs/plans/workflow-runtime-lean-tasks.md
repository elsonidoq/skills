# Lean workflow runtime — implementation tasks

**Draft; planning only.** Separate requirements truth: [TinySpec](workflow-runtime-lean-tinyspec.md),
commit `d9ee61d27a12baa6c65eb5693eaa1c4277a8a8ca`, raw SHA256
`a6fee2bfee8d9906ee5be4f69deee0bee85717da01fe62ad318a0e42d16266c3`. Direct adapter; no SpecKit or SDD prerequisite.
Authoritative authoring representation: [adjacent JSON](workflow-runtime-lean-tasks.json), existing
`runtime/coherence_workflow/schemas/task.schema.json`. Empty approval refs/null gate refs are honest:
combined approval, implementation and live testing are pending. **Not old-runtime dispatch input**:
`manual.*` checks below are instruction-managed commands/procedures, not registered oracles.
Do not create a registry/harness to make these tasks dispatchable through the broken runtime.

## Shared execution intent / boundaries

- **model_class**: Terra
- **effort**: medium
- **resolution**: resolved
- **provenance**: This conversation: actual owner ask_user answer “Yes — gpt-5.6-terra / medium”; retained in TinySpec Acceptance and remaining gates. Planning producer selected and observed openai-codex/gpt-6.1-sol, medium.
- **decomposition_rationale**: Three coherent production outcomes: first usable configured read/edit/check/commit path and permanent safety tests; compatible durable attempts/history; then actual full-range review and genuine owner-input delivery. Interfaces and consequential choices are explicit for Terra; routine helper organization remains open. No inventory/prototype/report/cleanup chain.
- **assumptions**: Instruction-managed delivery, not execution through the runtime under refactor; bounded sequential writers with moderate scaffolding and writer-owned verified commits. Owner-selected exact implementation binding is separate from Sol/medium planning and the unchanged Sol/medium monitor configuration; callable readiness is verified before later dispatch.
- **compatible_bindings**: `openai-codex/gpt-5.6-terra`, `medium`. Assessment: Owner-selected compatible target for these bounded interfaces and moderate scaffolding; not a claim of current callable SDK readiness or implementation authority. Provenance: Actual owner answer in this conversation and retained TinySpec delivery direction.

All tasks inherit this intent. Envelope `lean-delivery-draft` carries owner-selected Terra/medium;
observer `instruction-managed-owner-selection:1` is a provenance label, not a registered SDK
observer/readiness claim. Existing base/app Sol/medium YAML stays unchanged for delivery.
Future PRODUCT selection is configuration-driven, requested/observed distinct, no guessed provider
equivalence. Verify actual callable capability before dispatch; changing intent needs assessment/
affected review renewal. No ordinary model-token financial gate; paid-service authority unresolved.

Bounded sequential instruction-managed workers deliver this refactor, **not the runtime under
refactor**, and do not restore retired skills. Delivery **writer** verifies/focused-commits each task
before later writes; coordinator independently inspects actual diff/SHA/item proof/residual state.
A2's **product runner** commit is distinct. Preserve hooks/signing/unrelated index and ignored data;
no broad staging, empty-success commit, automatic ledger/STATE/memory or evidence-only checkpoint.
The shared [checkpoint contract](../../skills/memory-handling/references/task-commit-contract.md)
applies. Missing required capability/proof means NOT VERIFIED, not a substituted green result.

## Pending shared gates

- **G-approval** (permission, approval_ref `null`): Combined current-content TinySpec/tasks/scope approval, explicit bounded instruction-managed delivery exception and exact policy amendment decision/rationale; no implementation authorized by drafting. Scope: All three tasks; policy proposal in human document. Evidence: Actual owner decision associated with reviewed current source/tasks, exception and amendment rationale; no fabricated receipt.
- **G-custody** (manual, approval_ref `null`): Before retained implementation, establish actual sole-writer safety and reconcile real competing effects, or obtain authorized clean isolated workspace; clean Git/controller-stopped is insufficient. Scope: Each writer baseline and resume; preserve monitor-app-20261020-0ec48f3fe91b and all historical/ignored evidence. Evidence: Coordinator inspection of real children/process custody and Git/index ownership; unknown effects block affected work without controlling/recovering monitor.
- **G-capability** (capability, approval_ref `null`): Verify exact approved Terra/medium worker, existing local tools/Git/check dependencies and applicable permissions without installation or silent fallback. Scope: Instruction-managed delivery; product tests separately scoped. Evidence: Actual dispatch/check capability evidence, baseline and owned paths; missing capability is NOT VERIFIED.
- **G-live** (permission, approval_ref `null`): Separate explicit live/provider/test/process-custody authority for the real A2 exercise, approved isolated target and usable selected executor/SDK/tools/check command. Scope: T001/V2; later rerun only when changed seams invalidate that proof. No current-run control, process adoption, install, auth changes or worktree creation authorized now. Evidence: Owner live-test scope plus actual available own-child custody and test target; absent authority means NOT RUN and blocks reliance on A2.
- **G-review** (manual, approval_ref `null`): Fresh independent read-only review of actual entire committed refactor range; verified focused finding repairs and current-range rereview before acceptance. Scope: Final acceptance after T003; not a requirement to use the product runner to deliver this refactor. Evidence: Actual independent review base/head, source/criterion proof, finding dispositions and repaired-range review; missing review is NOT VERIFIED.

No implementation/worktree creation/live provider call or test-fixture mutation now. No Authority
construction, DB writes, source/approval renewal, monitor start/resume/control/archive/reset,
kill/adopt/recovery, installs/auth/global settings/push/deploy. Preserve historical approvals,
archives, ignored nested repositories and unrelated custom material. The monitor attempt
`monitor-app-20261020-0ec48f3fe91b` remains running/reservation=1/T001-active/controller-stopped
with uncertain incomplete SDK effects: clean Git is not settled custody. Its tool_poll blocker has
no proven exact cause; tools.py 35,429 bytes versus whole-reader 32,768 cap proves incompatibility
only. Later safe isolation requires separate authority, not a runtime recovery prerequisite.

### Bounded operative amendment proposal requiring combined owner approval

Approve this refactor's instruction-managed migration exception to current planner handoff,
AGENTS adoption execution, REQUIREMENTS executable responsibility and constitution Development
Workflow automatic-runner clauses: bounded sequential workers, writer-owned verified task commits,
coordinator evidence inspection, fresh independent full-range review. No retired skill or runtime
launch catalog/manifest/source-pin/custody-proof ceremony is a prerequisite for manual refactoring.
Actual one-writer/process safety is still required. No unrelated planner routing/fresh-producer
rule or global process rewrite changes; the coordinate skill remains the PRODUCT facade.

Approve replacement of conflicting executable contracts in that skill, operating/schema docs,
workflow/schemas, REQUIREMENTS/adoption and constitution: five readiness facts with checks only at
relevant invalidated boundaries replace immutable full-runtime eligibility, repeated contract/
canonical task-path-check/full-tree proofs; remove SDK document-delivery/parent provenance proof
chains, optional pressure/telemetry/publication vetoes and oversized full-diff bundles. Genuine
answers keep original question/conversation association; actual custody/SDK settlement still
blocks unknown effects. Keep current-content approval, exact bindings, one writer/private data,
real REQUIRED/manual gates, focused commits/hooks/signing and independent full-range acceptance.
Constitution Governance requires an explicit owner amendment decision and rationale; implement
appropriate version/rationale only after that decision, preserving historical amendment 4.0.0
provenance. Rationale: deletion-first usable coding without a replacement platform or weakened
safety. T001 ships its policy exception/operative changes; T002/T003 update changed seams in
lockstep. This proposal does not silently waive current policy or authorize implementation now.

## Ordered delivery

- [ ] T001 Deliver the usable configured scoped read/search/edit/check to focused runner-commit path, deleting tool/proof/telemetry obstacles and retaining real custody; permanent tests and operative policy/docs ship together.
  - **Depends**: none.
  - **order / context_group / envelope**: `0` / `lean-execution` / `lean-delivery-draft`.
  - **owned_paths**: `runtime/coherence_workflow/cli.py`, `runtime/coherence_workflow/intake.py`, `runtime/coherence_workflow/authority.py`, `runtime/coherence_workflow/tools.py`, `runtime/coherence_workflow/tool_process.py`, `runtime/coherence_workflow/pi_adapter.py`, `runtime/coherence_workflow/sessions.py`, `runtime/coherence_workflow/verification.py`, `runtime/coherence_workflow/registry.py`, `runtime/coherence_workflow/git_effects.py`, `runtime/pi-host/host.mjs`, `runtime/coherence_workflow/schemas/host.schema.json`, `runtime/coherence_workflow/schemas/shared.schema.json`, `runtime/coherence_workflow/schemas/workflow.schema.json`, `runtime/coherence_workflow/workflows/coordinate.yaml`, `runtime/tests/test_cli.py`, `runtime/tests/test_intake.py`, `runtime/tests/test_authority.py`, `runtime/tests/test_pi_adapter.py`, `runtime/tests/test_sessions.py`, `runtime/tests/test_host.mjs`, `runtime/tests/test_verification.py`, `runtime/tests/test_git_effects.py`, `runtime/tests/test_custody.py`, `runtime/tests/test_inventory.py`, `docs/coordinate-implementation.md`, `docs/coordinate-implementation-schema.md`, `skills/coordinate-implementation/SKILL.md`, `skills/coordinate-implementation/scripts/test_intake_contract.py`, `skills/coordinate-implementation/scripts/test_batching_contract.py`, `skills/coordinate-implementation/scripts/test_state_contract.py`, `REQUIREMENTS.md`, `AGENTS.md`, `.specify/memory/constitution.md`.

Use existing CLI/Gateway/PiAdapter/host/Verification/Git effects for one usable vertical path.
At admission establish valid tasks, usable exact config/resources/tools, current scoped approval,
one-writer/safe baseline and runnable checks; recheck only relevant invalidated state. Replace
cli._tools no-op-process reads/whole-file replacements and PiAdapter._poll_tools escaping result
errors with scoped source read/search/ranged continuation/edit/real command-check facilities.
Use SDK/tools where suitable; derive limits from real consumers, not universal file caps or
owned-file-only reading. Delete recursive snapshot/reconcile per tool and duplicate canonical
scope/full-contract gates on this path; retain safe paths/private-data/external authority and
Git task-boundary audits including ignored material. Project commands are trusted scoped checks,
not arbitrary network/worker Git authority. Known read/validation/nonzero errors stay correctable;
uncertain launch/settlement/Git still stops. Make host observer genuinely config-driven and remove
optional pressure/headroom vetoes in host/sessions. Permanent tests precede V2; execute the real
read -> owned edit -> real check -> runner commit as soon as this slice works, before downstream
reliance. Generic SDK compatibility remains unproved until V2. T002/T003 remove remaining history/
review debt; T001 is not final A1 acceptance or a prerequisite harness.

- **REQUIRED T001/V1 — A1/A3: five-fact readiness, usable tools, configuration-first binding and correctable safe errors.** Check `manual.execution-seams`, version `1`; args: commands=[C1, C2, C3, C4, C5, C6]; mode=instruction-managed; manual commands, not registered runtime oracles.
  PASS: Named permanent actual-helper tests show scoped read/search/ranged continuation/edit/real command-check wiring, exact selected binding (including a non-Sol configuration without provider-equivalence guessing), actionable ordinary tool/validation/nonzero-check errors returned to the same healthy turn; optional absent/low pressure observations do not veto continuation. No no-op process reads, full-tree-per-tool snapshot/reconcile, duplicate task/path/check authority encodings or mandatory full-contract readmission remain on this tool path. Unknown effects/custody still stop affected work.
  Evidence: Commands, named cases and actual deletion/call-site diff; requested and observed binding distinguished. Static tests do not establish generic live SDK compatibility.
  Producer dependencies: none. Gates: G-approval, G-custody, G-capability.
- **REQUIRED T001/V2 — A2: earliest useful real composed PRODUCT acceptance before downstream reliance.** Check `manual.real-delivery`, version `1`; args: {"procedure":"In separately approved isolated target, use actual configuration-selected executor/SDK and production runner: read normal source with continuation above the former 32768-byte read limit; safely fail a tool call then correct it in the same attempt; make an owned edit; execute applicable real project check; inspect focused runner-created commit. Capture exact command/config and observed result in existing session/test return, not a new ledger.","mode":"separately gated real execution; NOT RUN during task production"}.
  PASS: Real executor performs read -> owned write -> successful real check -> focused runner commit; corrected safe tool error does not poison turn or trigger replacement; continuation exposes content beyond old limit without claiming universal size support. Actual binding, settled custody, check result and owned commit/tree are inspectable, not mocked metadata. Failure/unrun blocks reliance; diagnose before targeted retry.
  Evidence: Owner authority, exact live command/config/environment, requested/observed binding, baseline/result SHA and diff, tool error/correction/continuation, actual check exit/output and settled process evidence; record limits.
  Producer dependencies: none. Gates: G-approval, G-custody, G-capability, G-live.
- **REQUIRED T001/V3 — A3: scoped mutation, required/manual gates and verified commit ordering survive deletions.** Check `manual.execution-safety`, version `1`; args: commands=[C7, C8, C9, C10]; mode=instruction-managed; manual commands, not registered runtime oracles.
  PASS: Focused permanent production-seam tests prove owned paths and unrelated staged/unstaged/ignored/nested material preserved; denied/unmet manual gates or nonzero required checks cannot commit/release dependents; hooks/signing failures stop without configure-around; worker cannot commit. Smallest existing composed fixture observes actual successful check before runner commit and refusal of unresolved tool/host/Git replay, not only helper flags. Custody-sensitive test branches run only with their explicit isolated-process authority; missing authority is NOT RUN.
  Evidence: Named case output and actual fixture Git/check order, unrelated-byte/index comparison, refusal diagnostics and permission limits.
  Producer dependencies: none. Gates: G-approval, G-custody, G-capability.
- **REQUIRED T001/V4 — A1/A4: lockstep operative contracts and bounded delivery amendment.** Check `manual.execution-docs`, version `1`; args: commands=[C11, C12, C13, C14, C15]; mode=instruction-managed; manual commands, not registered runtime oracles.
  PASS: Entry, operating/schema docs, REQUIREMENTS/adoption/constitution describe T001 behavior and explicitly approved migration exception without claiming later T002/T003 pruning complete. Amend obsolete executable-only static guards with changed contract, retaining required gates/checkpoints/review. Preserve historical amendment provenance and portability; tell user /reload after global skill changes. No launch manifest/catalog/source-pin ceremony is imposed on manual refactor delivery.
  Evidence: Named contract-check results and changed code-to-doc/policy comparison, owner amendment decision/rationale and known intermediate limitations.
  Producer dependencies: none. Gates: G-approval, G-custody, G-capability.

- [ ] T002 Deliver minimal durable history and compatible settled-boundary attempts, deleting immutable full-code eligibility and optional-publication vetoes while preserving old records read-only.
  - **Depends**: T001.
  - **order / context_group / envelope**: `1` / `lean-history` / `lean-delivery-draft`.
  - **owned_paths**: `runtime/coherence_workflow/engine.py`, `runtime/coherence_workflow/store.py`, `runtime/coherence_workflow/registry.py`, `runtime/coherence_workflow/intake.py`, `runtime/coherence_workflow/cli.py`, `runtime/coherence_workflow/projections.py`, `runtime/coherence_workflow/schemas/projection.schema.json`, `runtime/coherence_workflow/schemas/execution-result.schema.json`, `runtime/tests/test_engine.py`, `runtime/tests/test_recovery.py`, `runtime/tests/test_projections.py`, `runtime/tests/test_metrics.py`, `runtime/tests/test_migration.py`, `docs/coordinate-implementation.md`, `docs/coordinate-implementation-schema.md`, `REQUIREMENTS.md`.

Consume actual T001/V2,V3 before downstream reliance. Remove Engine._assert_pins/reserve and
registry/source full-code identity eligibility/per-node rehash/reload, keeping recorded runtime/
config revisions and actual schema/config/authority compatibility. Compatible new attempts need
a settled boundary, not rewriting old identity. Reuse SQLite transactions/uniqueness, LangGraph
sync saver and effect reconciliation; do not span saver/waits with app transactions. Keep ordered
task/attempt/dependency/state/SHA/check/approval/review/effect history, retained actual YAML/graph
and honest recorded-state versus liveness. Additive change where sufficient; otherwise explicit
unsupported versions, no auto-migration. Remove optional projection vetoes, retain null/unknown
and privacy. Document versioned SQLite semantic surface, not eternal obsolete tables. Use isolated
historical fixtures; never mutate real old DB/proofs. Identify monitor-v1 reader/data-model/source/
task renewal for removed parent/proof/pin assumptions; no app work or automatic compatibility.
Validate new history against the real A2 attempt, renewing invalidated proof under G-live.

- **REQUIRED T002/V1 — A1/A3: revision-aware attempts and useful ordered history, not immutable runtime eligibility.** Check `manual.history-attempts`, version `1`; args: commands=[C16, C17, C18]; mode=instruction-managed; manual commands, not registered runtime oracles.
  PASS: Production tests show a settled compatible bugfix can start a new attempt with recorded runtime/config revision, without rewriting old attempt identity or full-code rehash before nodes/reserve. Ordered task/dependency/state/baseline/result/check/decision/review/effect facts remain sufficient for interruption reconciliation. Real incompatible schema/config/authority is explicit; incomplete process/SDK/Git intent still blocks replay/replacement. Reuse SQLite transactions, saver and uniqueness/reconciliation; no second runner or recovery subsystem.
  Evidence: Named actual engine/store/settled-attempt and unresolved-effect tests; ordered stored facts and old/new identity comparison; A2 evidence applicability assessment before relying on T001.
  Producer dependencies: T001/V2, T001/V3. Gates: G-approval, G-custody, G-capability.
- **REQUIRED T002/V2 — A3/A4: honest history reader surface and non-authoritative optional observations.** Check `manual.history-readers`, version `1`; args: commands=[C19, C20, C21]; mode=instruction-managed; manual commands, not registered runtime oracles.
  PASS: Permanent tests demonstrate retained historical records/pinned inputs unchanged and historically interpreted or explicitly unsupported (including unknown versions); new versioned documented SQLite semantic surface explains T001 A2 attempt. Retain actual selected workflow/graph definition and optional projection cursor, not every retired proof table. Null/unknown telemetry and failed projection publication preserve authoritative success/state. Recorded running and observed liveness remain separate; public output stays private-data allowlisted.
  Evidence: Named historical reader/unknown-version/publication/null tests; fixture record comparison; item-mapped read of actual A2 facts (or NOT VERIFIED if A2 not run), with no auto-migration.
  Producer dependencies: T001/V2. Gates: G-approval, G-custody, G-capability.
- **REQUIRED T002/V3 — A4: operating/schema/requirements match durable behavior and delimit monitor renewal.** Check `manual.history-docs`, version `1`; args: commands=[C14, C22]; mode=instruction-managed; manual commands, not registered runtime oracles.
  PASS: Docs state supported old/new semantic versions and unsupported behavior, minimal durable fields, schema/config revision rules and actual YAML retention. Explicitly identify monitor-v1 parent/proof/pin/table and exact-source/unchanged-runtime assumptions needing later reader/data-model/source/tasks approval renewal; no claim unchanged monitor is compatible and no app implementation, table-freeze framework or historical proof rewrite.
  Evidence: Concrete changed-code/doc comparison, compatibility limits and affected monitor contract references; optional broad regression remains nonblocking.
  Producer dependencies: T002/V1, T002/V2. Gates: G-approval, G-custody, G-capability.

- [ ] T003 Deliver real full-range independent review and genuine owner answers without full-diff/document/parent proof protocols; remove obsolete routes and align final acceptance/docs.
  - **Depends**: T002.
  - **order / context_group / envelope**: `2` / `lean-review` / `lean-delivery-draft`.
  - **owned_paths**: `runtime/coherence_workflow/verification.py`, `runtime/coherence_workflow/review_documents.py`, `runtime/coherence_workflow/interaction.py`, `runtime/coherence_workflow/notifications/paseo.py`, `runtime/coherence_workflow/cli.py`, `runtime/coherence_workflow/pi_adapter.py`, `runtime/pi-host/host.mjs`, `runtime/coherence_workflow/schemas/agent-result.schema.json`, `runtime/coherence_workflow/schemas/interaction.schema.json`, `runtime/coherence_workflow/schemas/host.schema.json`, `runtime/coherence_workflow/workflows/coordinate.yaml`, `runtime/tests/test_review_documents.py`, `runtime/tests/test_review_repair.py`, `runtime/tests/test_interaction.py`, `runtime/tests/test_parent_transport.py`, `runtime/tests/test_pi_adapter.py`, `runtime/tests/test_host.mjs`, `runtime/tests/test_acceptance.py`, `docs/coordinate-implementation.md`, `docs/coordinate-implementation-schema.md`, `skills/coordinate-implementation/SKILL.md`, `REQUIREMENTS.md`, `README.md`.

Replace ReviewRepair.bundle binary diff with compact actual base/head/source/evidence references
and read-only revision/file access to the FULL range. Remove review_documents attestation/coverage
helpers, callers, schema fields and obsolete tests (delete module if unused); do not replace them
with a new receipt system. Preserve fresh independent reviewer, original criteria, stale-head
rejection, actual findings, verified focused repairs and current-range rereview. Simplify Interaction/
Paseo to genuine scoped answers, original question/conversation association, dedup and honest pending;
remove parent proof bureaucracy and optional-headroom vetoes, not actual transport/custody/authority.
No fresh substitution, fabricated ask_user answer or blind expensive retry/uncertain replay.
Ship operative docs/README and permanent tests with deletions. Audit all three tasks as one real
product path; A2 must apply at final revisions, rerun only affected seams under G-live. Coordinator
obtains independent full-range review after writer checkpoints; authorized finding repairs are
separate verified focused commits and get current-range review. Read-only review has no empty commit.

- **REQUIRED T003/V1 — A1/A4: independent reviewer reads actual range and files without oversized proof delivery.** Check `manual.review-seams`, version `1`; args: commands=[C23, C24, C4, C6]; mode=instruction-managed; manual commands, not registered runtime oracles.
  PASS: Delete full binary diff bundle and mandatory SDK-byte/hash/turn/range document-delivery attestation/coverage machinery and obsolete schema/tests, not a second lean mode. Production permanent tests observe reviewer read-only access to actual base..head/source/evidence with useful continuation, fresh role isolation, stale/wrong-head rejection, verified focused repair and current-range re-review. Retain actual full-range judgment and genuine SDK/process settlement, not document-read receipts as acceptance.
  Evidence: Named actual review/repair/helper results, range/file access and stale-head tests, obsolete-call-site deletion diff; classify mocked/static limits.
  Producer dependencies: T002/V1, T002/V2. Gates: G-approval, G-custody, G-capability.
- **REQUIRED T003/V2 — A1/A3: genuine scoped owner answers with simpler delivery and no telemetry/provenance veto.** Check `manual.owner-input`, version `1`; args: commands=[C25, C26, C4, C6]; mode=instruction-managed; manual commands, not registered runtime oracles.
  PASS: Production tests preserve genuine answer authority, original question/conversation association, deduplication, scope and pending/missing-answer behavior; remove mandatory parent delivery/attempt/provenance proof chains and low/unknown optional-headroom vetoes. No fabricated ask_user answer, silent fresh worker substitution, worker direct owner tool, uncertain turn replay or blind expensive retry. Actual transport/SDK settlement remains meaningful. Real interactive calls, if needed beyond focused tests, retain original separate authority and are NOT RUN without it.
  Evidence: Named real-helper positive/denial/dedup/original-association and uncertain-effect cases; deletion diff and explicit live limits.
  Producer dependencies: T002/V1. Gates: G-approval, G-custody, G-capability.
- **REQUIRED T003/V3 — A1-A4: deletion-first operative path, honest compatibility and final independent acceptance.** Check `manual.final-acceptance`, version `1`; args: commands=[C27, C14, C28]; mode=instruction-managed; manual commands, not registered runtime oracles.
  PASS: Final operative path has five obvious readiness facts plus five small execution rules, with no repeated whole-contract validation, canonical action-scope duplication, whole-tree-per-tool hashes, immutable full-code eligibility, document-delivery proof, telemetry/publication veto or oversized full-diff bundle remaining as hidden blockers. Remove stale routes/config/schema/test/doc mandates with mechanisms. A2 is actually verified at applicable final revisions (rerun only invalidated seams under G-live), A3 safety and A4 historical compatibility/doc agreement hold; independent full-range review findings are resolved with focused verified repairs and current-range rereview. No implementation-complete-as-accepted claim. Writer runs the production/doc checks before its focused checkpoint; G-review is the post-checkpoint acceptance gate, not a precommit review or a waiver of writer verification.
  Evidence: Actual deletion summary and focused command results, docs/code/policy comparison, applicability of T001 A2 and required rerun output if changed, final source/range/criterion review and finding dispositions; all absent live/review proof explicitly NOT VERIFIED.
  Producer dependencies: T001/V1, T001/V2, T001/V3, T001/V4, T002/V1, T002/V2, T002/V3, T003/V1, T003/V2. Gates: G-approval, G-custody, G-capability, G-review.

## Shared checks, dependency evidence and validation

Optional item arrays are empty. Broader regression is optional/nonblocking, not a hidden completeness
programme. The named focused suites are REQUIRED because the deleted mechanisms cross those seams;
retain named case output, not generic green. Reuse each command once with all item mappings, rerun
only invalidated evidence. Tests/docs/routine teardown stay inside delivery; likely owned paths
are explicit above, not indiscriminate repository ownership. Amend affected approval if another
carrying path is needed. Each verified task checkpoints before later retained task writes.

Reuse local pinned LangGraph 1.2.16/saver 3.1.2 (`runtime/pyproject.toml`) and SDK 0.87.1
(`runtime/pi-host/package.json`). Inspected actual sync saver, Gateway settlement, Git effects,
tool/host/session/authority/review seams ground reuse/deletion. No internet/new dependency/install/
version change or alternate SDK API assumption. T001/V2 is the early high-leverage composed proof,
not a separate prototype chain; known safety/history use permanent actual-helper tests. Failed/unrun
proof blocks affected consumers and returns to producing review/renewal, never weaker acceptance.

A1: T001/V1,V4 + T002/V1 + T003/V1,V2,V3. A2: T001/V2, applicability in T002/V1,V2 and
T003/V3. A3: T001/V3 + T002/V1,V2 + T003/V2. A4: T001/V4 + T002/V2,V3 + T003/V1,V3.
TinySpec exclusions and original gates remain intact: no app/planner overhaul/new tracker or
compatibility framework/parallel lean mode/retired skill/source correction/automatic history
migration/current monitor recovery. No runtime builtin action_scope/oracle declaration is claimed;
the manual envelope is authoring metadata, not authentication/dispatch/live permission.

Preparation baseline d9ee61d27a12baa6c65eb5693eaa1c4277a8a8ca was clean before edits. Whole
local memory index had no gotchas; coordination guidelines no approved guidance; no memory writes.
Selected/observed producer openai-codex/gpt-6.1-sol, medium; no nested calls. Authoring checks:
Markdown order, adjacent schema/JSON order in prepared checkout environment, source hash, exact
human/JSON mappings, introduced links, git diff --check and manual A1-A4/dependency/permission/
current-content/doc/feasibility review. Actual results and baseline/result SHA travel in external
producer return, not a repository evidence ledger. Implementation/live checks are NOT RUN here.
Parent review/combined approval remain pending; changed content reopens affected review/approval.

C references below expand to exact args.commands in listed order. `<approved-python>` means an
already available compatible environment verified before execution, not an install/new launcher.
Fixture/process/live tests require applicable actual permission, especially custody-sensitive branches;
missing authority is NOT RUN. No scheduled suite or fixture is executed in planning. Manual
observations are procedures, not builtin executable-oracle claims.

- **C1**: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=runtime <approved-python> -B -m unittest discover -s runtime/tests -p 'test_cli.py'`
- **C2**: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=runtime <approved-python> -B -m unittest discover -s runtime/tests -p 'test_intake.py'`
- **C3**: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=runtime <approved-python> -B -m unittest discover -s runtime/tests -p 'test_authority.py'`
- **C4**: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=runtime <approved-python> -B -m unittest discover -s runtime/tests -p 'test_pi_adapter.py'`
- **C5**: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=runtime <approved-python> -B -m unittest discover -s runtime/tests -p 'test_sessions.py'`
- **C6**: `node --test runtime/tests/test_host.mjs`
- **C7**: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=runtime <approved-python> -B -m unittest discover -s runtime/tests -p 'test_verification.py'`
- **C8**: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=runtime <approved-python> -B -m unittest discover -s runtime/tests -p 'test_git_effects.py'`
- **C9**: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=runtime <approved-python> -B -m unittest discover -s runtime/tests -p 'test_custody.py'`
- **C10**: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=runtime <approved-python> -B -m unittest discover -s runtime/tests -p 'test_inventory.py'`
- **C11**: `PYTHONDONTWRITEBYTECODE=1 <approved-python> -B skills/coordinate-implementation/scripts/test_intake_contract.py`
- **C12**: `PYTHONDONTWRITEBYTECODE=1 <approved-python> -B skills/coordinate-implementation/scripts/test_batching_contract.py`
- **C13**: `PYTHONDONTWRITEBYTECODE=1 <approved-python> -B skills/coordinate-implementation/scripts/test_state_contract.py`
- **C14**: `git diff --check`
- **C15**: `Manual compare T001 production diff, relevant operative owners and exact approved amendment/exception`
- **C16**: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=runtime <approved-python> -B -m unittest discover -s runtime/tests -p 'test_engine.py'`
- **C17**: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=runtime <approved-python> -B -m unittest discover -s runtime/tests -p 'test_recovery.py'`
- **C18**: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=runtime <approved-python> -B -m unittest discover -s runtime/tests -p 'test_migration.py'`
- **C19**: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=runtime <approved-python> -B -m unittest discover -s runtime/tests -p 'test_projections.py'`
- **C20**: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=runtime <approved-python> -B -m unittest discover -s runtime/tests -p 'test_metrics.py'`
- **C21**: `Manual read-only old-record/reader compatibility comparison in isolated existing test fixtures; never open/mutate current monitor storage`
- **C22**: `Manual compare storage DDL/read semantics, engine revisions, projections and docs against T002/V1-V2`
- **C23**: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=runtime <approved-python> -B -m unittest discover -s runtime/tests -p 'test_review_documents.py'`
- **C24**: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=runtime <approved-python> -B -m unittest discover -s runtime/tests -p 'test_review_repair.py'`
- **C25**: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=runtime <approved-python> -B -m unittest discover -s runtime/tests -p 'test_interaction.py'`
- **C26**: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=runtime <approved-python> -B -m unittest discover -s runtime/tests -p 'test_parent_transport.py'`
- **C27**: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=runtime <approved-python> -B -m unittest discover -s runtime/tests -p 'test_acceptance.py'`
- **C28**: `Manual inspect entire baseline..final refactor range, source A1-A4 proof and operative docs; independent fresh read-only final review after writer checkpoints`
