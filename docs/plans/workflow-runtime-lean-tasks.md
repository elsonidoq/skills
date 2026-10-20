# Lean workflow runtime — implementation tasks

**Draft; planning only.** [TinySpec](workflow-runtime-lean-tinyspec.md) is requirements truth,
source commit `d9ee61d27a12baa6c65eb5693eaa1c4277a8a8ca`, SHA256
`a6fee2bfee8d9906ee5be4f69deee0bee85717da01fe62ad318a0e42d16266c3`. Direct adapter; no SpecKit/SDD prerequisite.
[Adjacent JSON](workflow-runtime-lean-tasks.json) is the sole authoritative machine representation,
matching the existing packaged task schema. Approval refs are empty; gate refs null. Combined
approval/implementation remain pending. `manual.*` checks are instruction-managed procedures,
not registered runtime oracles or old-runtime dispatch eligibility. No new test harness/registry.

## Shared intent, delivery and approval

- **model_class**: Terra
- **effort**: medium
- **resolution**: resolved
- **provenance**: This conversation: actual owner ask_user answer “Yes — gpt-5.6-terra / medium”; retained in TinySpec Acceptance and remaining gates. Planning producer selected and observed openai-codex/gpt-6.1-sol, medium.
- **decomposition_rationale**: Three production outcomes: usable configured task/check/commit path; compatible durable attempts/history; simpler product review/owner input. Terra gets explicit interfaces and moderate scaffolding. Focused actual-helper tests and one early A2 live exercise, not historical migration/fault programmes. Independent full-range delivery acceptance follows writer checkpoints.
- **assumptions**: Instruction-managed delivery, not execution through the runtime under refactor; bounded sequential writers with moderate scaffolding and writer-owned verified commits. Owner-selected exact implementation binding is separate from Sol/medium planning and the unchanged Sol/medium monitor configuration; callable readiness is verified before later dispatch.
- **compatible_bindings**: provider `openai-codex`, model `gpt-5.6-terra`, effort `medium`. Assessment: Owner-selected compatible target for these bounded interfaces and moderate scaffolding; not a claim of current callable SDK readiness or implementation authority. Provenance: Actual owner answer in this conversation and retained TinySpec delivery direction.

All tasks inherit envelope `lean-delivery-draft`; its observer label records owner selection,
not SDK observation. Monitor/base Sol/medium YAML stays unchanged for delivery; future PRODUCT
bindings come from selected config, requested/observed distinct. No runtime dispatch claim.

Bounded sequential writers deliver manually, not through this runtime or retired skills. Each
writer verifies/focused-commits before later writes; coordinator inspects diff/SHA/item proof.
A2's PRODUCT runner commit is distinct. Shared protections: one writer, scoped paths/private data/
external authority, unrelated staged/unstaged/ignored/nested material, real REQUIRED/manual gates,
hooks/signing, inspected retry/no uncertain replay and independent acceptance. The
[checkpoint contract](../../skills/memory-handling/references/task-commit-contract.md) applies;
no STATE/memory/tracker/ledger upkeep or empty evidence commit.

**Combined approval must explicitly approve the bounded policy change:** exception to current
planner/adoption/REQUIREMENTS/constitution automatic-runner clauses for these instruction-managed
writers/checkpoints and independent final review; no runtime manifest/catalog/source-pin ceremony
to bootstrap manual work. Amend affected coordinate skill, operating/schema docs, packaged workflow/
schemas and REQUIREMENTS/adoption/constitution to five readiness facts checked at relevant
invalidation boundaries, retiring repeated contract/canonical-scope/full-tree/runtime-eligibility,
SDK document/parent provenance, telemetry/publication veto and binary-bundle protocols. Keep the
source safety/authority invariants and original question/conversation association. Constitution
Governance needs actual explicit decision/rationale and appropriate version, preserving historical
amendments. Rationale: deletion-first usable coding, not a replacement platform or planner overhaul.
T001 changes its operative seams; T002/T003 align theirs in lockstep. No policy is waived now.

No implementation/live tests/fixture mutation/DB or Authority writes, worktree creation, monitor
control/start/resume/archive/reset/kill/adoption/recovery, installs/auth/global settings/push/deploy
now. Monitor `monitor-app-20261020-0ec48f3fe91b` custody remains uncertain; stopped controller/clean
Git does not settle effects. tool_poll cause remains unproved; the old read-limit incompatibility
is not a diagnosis. Preserve old approvals/records/archives; no rewriting old proofs or app renewal.

### Pending gates

- **G-approval** (permission; approval_ref `null`): Current source/tasks/scope combined approval, including bounded manual-route exception and explicit constitutional amendment decision/rationale. Scope: T001-T003 retained delivery and scoped local fixture checks. Evidence: Actual owner decision tied to reviewed current content; no invented receipt.
- **G-custody** (manual; approval_ref `null`): Establish actual sole-writer/process safety or obtain authorized clean isolation; clean Git/controller-stopped is insufficient. Scope: Each delivery baseline/resume; uncertain monitor remains untouched. Evidence: Coordinator inspection of real effects/children and Git/index ownership; unknown effects stop affected writes.
- **G-capability** (capability; approval_ref `null`): Verify exact Terra/medium worker and available local tools/Git/check dependencies; no install or silent substitution. Scope: Instruction-managed delivery, not runtime launch preflight. Evidence: Actual usable binding/check capability and owned baseline; unavailable is NOT VERIFIED.
- **G-process-test** (permission; approval_ref `null`): Explicit isolated test/own-child custody authority for the four selected FocusedCheckpointTests methods and their existing fixture lifecycle. Scope: T001/V3 selected Git cases only; COHERENCE_TEST_CGROUP_PARENT must be approved. No launch-crash, SIGKILL or live provider programme. Evidence: Approved delegated test parent/temporary target and actual selected-case results; missing authority is NOT RUN.
- **G-live** (permission; approval_ref `null`): Separate explicit live/test/custody authority and usable configuration-selected executor for the single real A2 exercise. Scope: T001/V2 isolated target; only invalidated A2 seams rerun later. No current-monitor control/recovery, installs or auth changes. Evidence: Owner test scope, exact real invocation/binding and settled effects; absent authority is NOT RUN.

All REQUIRED items have **default gates** G-approval, G-custody, G-capability; extras below expand
that exact list. Missing required authority/capability/evidence is NOT RUN/NOT VERIFIED, not pass.

## Task-local checks and ownership notation

Python `args.command` expands exactly to the following prefix followed by that item's
`existing_selectors` then `proposed_selectors` in listed order (excluding a `::` Node selector):
`PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=runtime:runtime/tests:skills/coordinate-implementation/scripts <approved-python> -B -m unittest`.
`<approved-python>` is the existing compatible approved environment, not an install/new launcher.
**Proposed selectors do not exist yet:** implement these permanent cases against actual production
helpers inside the named existing modules; collect and run them before claiming pass. Existing
selectors were inspected for scope; update their retired proof assumptions without weakening useful
safety. Offline/local fixtures only unless a specific gate says otherwise; no entire mixed suite.

Ownership expands prefixes **R**=`runtime/coherence_workflow/`, **T**=`runtime/tests/`,
**S**=`skills/coordinate-implementation/`, **D**=`docs/`; unprefixed paths are repository-relative.
These are exact expected owned_paths, not instructions to touch every file. Required checks/evidence
stay with each outcome; optional broad suites are nonblocking. Additional ownership needs renewal.

- [ ] T001 Deliver the usable configured scoped read/search/edit/check to focused runner-commit path, deleting tool/proof/telemetry obstacles and retaining real custody; permanent tests and operative policy/docs ship together.
  - **Depends**: none.
  - **order / context_group**: `0` / `lean-execution`.
  - **owned_paths**: R: `cli.py`, `intake.py`, `authority.py`, `tools.py`, `tool_process.py`, `pi_adapter.py`, `sessions.py`, `verification.py`, `registry.py`, `git_effects.py`, `schemas/host.schema.json`, `schemas/shared.schema.json`, `schemas/workflow.schema.json`, `workflows/coordinate.yaml`; T: `test_cli.py`, `test_intake.py`, `test_authority.py`, `test_pi_adapter.py`, `test_sessions.py`, `test_host.mjs`, `test_verification.py`, `test_git_effects.py`, `test_custody.py`, `test_inventory.py`; S: `SKILL.md`, `scripts/test_intake_contract.py`, `scripts/test_batching_contract.py`, `scripts/test_state_contract.py`; D: `coordinate-implementation.md`, `coordinate-implementation-schema.md`; root: `runtime/pi-host/host.mjs`, `REQUIREMENTS.md`, `AGENTS.md`, `.specify/memory/constitution.md`.

First deliver a usable CLI/Gateway/PiAdapter/host/Verification/Git vertical slice. Readiness:
valid tasks; usable exact config/resources/tools; current scoped approval; one writer/safe baseline;
runnable checks. Replace cli._tools whole-file/no-op reads and escaping _poll_tools errors with
scoped read/search/edit/check and consumer-limit continuation; remove per-tool full-tree proofs.
Use existing mechanisms, not another mode. Permanent focused cases precede the single A2 trial.
**While T002/T003 code remains:** a fresh separately approved isolated A2 target uses the T001
runtime revision unchanged during the attempt, so old immutable revision checks do not prevent
the task checkpoint. Observe that real commit, not full run acceptance; old final-review bundle/
attestation debt is not exercised as an early acceptance prerequisite. Later tasks remove that debt.
Do not alter/recover the monitor or add a harness/stop protocol to obtain the milestone.

**REQUIRED T001/V1 — A1/A3: five-fact readiness, usable tools, configuration-first binding and correctable safe errors.** Check `manual.execution-seams`, version `1`.
- **args.existing_selectors**: `test_intake.ExecutionIntentTests.test_binding_is_explicit_not_inferred_from_planner_or_reviewer`, `test_authority.AuthorityAdmissionTests.test_external_gateway_denials_have_zero_sends`.
- **args.proposed_selectors**: `test_cli.LeanReadinessTests.test_five_facts_and_invalidation_boundaries`, `test_pi_adapter.LeanToolTests.test_scoped_tools_continue_after_safe_error`, `test_sessions.SessionPolicyTests.test_unknown_metrics_do_not_veto_settled_original`, `runtime/tests/test_host.mjs::lean configured binding and optional telemetry`.
- **args.command**: shared Python expansion above.
- **args.node_command**: `node --test --test-name-pattern='^lean configured binding and optional telemetry$' runtime/tests/test_host.mjs`.
- **PASS**: Actual helpers enforce five-fact readiness only at relevant boundaries; scoped read/search/edit/check supports consumer-sized continuation and same-attempt safe-error correction. Selected exact non-Sol configuration reaches host; unknown/low optional metrics do not veto settled original reuse. No no-op reads, per-tool tree proofs, duplicate canonical scopes or repeated whole-contract admission; unscoped external actions have zero sends.
- **Evidence**: Named selected/proposed cases and production deletion diff; offline/zero-send tests are not live SDK proof.
- **producer_dependencies**: []. **gates**: defaults.

**REQUIRED T001/V2 — A2: earliest useful real composed PRODUCT acceptance before downstream reliance.** Check `manual.real-delivery`, version `1`.
- **args.procedure**: Under G-live in an approved isolated target, use the actual selected-config executor and production runner: read normal source with continuation beyond 32768 bytes; safely fail and correct one tool call in the same attempt; make an owned edit; run an applicable real project check; observe the focused runner commit. Record the exact invocation/config/environment and custody in the existing session/test return. Stop observation at the verified checkpoint boundary; no new stop flag or final-review harness.
- **PASS**: Real selected-config executor completes read -> owned write -> successful real check -> focused runner commit, with usable above-old-limit continuation and one safe tool error corrected in the same settled attempt. Actual binding/tree/check/custody are observed, not mocked. This single live exercise replaces unrelated summary/retry/control/death/cutover prerequisites; failure/unrun blocks reliance.
- **Evidence**: Exact invocation/config, requested/observed binding, baseline/result SHA, diff, actual check output, error/correction/continuation and settled custody; limits.
- **producer_dependencies**: []. **gates**: defaults + G-live.

**REQUIRED T001/V3 — A3: scoped mutation, required/manual gates and verified commit ordering survive deletions.** Check `manual.execution-safety`, version `1`.
- **args.existing_selectors**: `test_git_effects.FocusedCheckpointTests.test_actual_commit_preserves_unrelated_staged_unstaged_untracked`, `test_git_effects.FocusedCheckpointTests.test_read_only_no_empty_commit_and_failed_evidence_blocks`, `test_git_effects.FocusedCheckpointTests.test_owned_overlap_symlink_unrelated_drift_and_hook_failure_stop`, `test_git_effects.FocusedCheckpointTests.test_actual_signing_failure_blocks_without_disabling_or_retry`.
- **args.proposed_selectors**: `test_inventory.LeanScopeTests.test_owned_edit_preserves_ignored_material_and_rejects_escape`, `test_cli.LeanCheckpointTests.test_required_check_and_gate_precede_commit`, `test_pi_adapter.LeanToolTests.test_unsettled_effect_blocks_replacement`.
- **args.command**: shared Python expansion above.
- **PASS**: Actual-helper tests preserve scoped ownership and unrelated staged/unstaged/untracked/ignored/nested material. Failed REQUIRED/manual gates and unresolved tool/host/Git effects cause zero commit/replacement. Selected real Git cases retain focused commits and hook/signing failure stops; new verify/checkpoint case observes production ordering, A2 its successful integration. Replace obsolete full-tree assertions, not meaningful safety; no death injection or worker commits.
- **Evidence**: Named results, real fixture tree/index preservation, hook/signing outcomes and zero dispatch on failed gates/unresolved effects; only selected Git fixture custody.
- **producer_dependencies**: []. **gates**: defaults + G-process-test.

**REQUIRED T001/V4 — A1/A4: lockstep operative contracts and bounded delivery amendment.** Check `manual.execution-docs`, version `1`.
- **args.existing_selectors**: [].
- **args.proposed_selectors**: `test_intake_contract.IntakeContractTests.test_lean_entry_and_bounded_delivery_exception`.
- **args.command**: shared Python expansion above.
- **PASS**: Focused contract case plus manual comparison show operative T001 behavior and approved bounded writer-checkpoint exception in entry/docs/REQUIREMENTS/adoption/constitution. Historical amendments, authority/custody/checks/final acceptance remain; no manual-delivery launch/catalog/pin ceremony. T002/T003 debt is not called complete; only changed obsolete static expectations are revised.
- **Evidence**: Named proposed contract case, code/doc carrying spans and actual amendment decision/rationale; later global skill changes require /reload.
- **producer_dependencies**: []. **gates**: defaults.

- [ ] T002 Deliver minimal durable history and compatible settled-boundary attempts, deleting immutable full-code eligibility and optional-publication vetoes while preserving old records read-only.
  - **Depends**: T001.
  - **order / context_group**: `1` / `lean-history`.
  - **owned_paths**: R: `engine.py`, `store.py`, `registry.py`, `intake.py`, `cli.py`, `projections.py`, `schemas/projection.schema.json`, `schemas/execution-result.schema.json`; T: `test_engine.py`, `test_recovery.py`, `test_projections.py`, `test_metrics.py`; D: `coordinate-implementation.md`, `coordinate-implementation-schema.md`; root: `REQUIREMENTS.md`.

After T001's real V2 and safety V3, prune immutable eligibility/per-node rehash in Engine/reserve
and keep revision-aware settled attempts, minimal ordered history and actual retained YAML/graph.
Reuse SQLite transactions, saver and unresolved-effect reconciliation; no migration/recovery platform.
Old records remain read-only/historical or explicitly unsupported. Projection failures/unknown metrics
are observations. Identify later monitor reader/data-model/source/tasks renewal; do not implement app
or freeze obsolete proof tables. Check real A2 history/applicability, rerun only invalidated seams.

**REQUIRED T002/V1 — A1/A3: revision-aware attempts and useful ordered history, not immutable runtime eligibility.** Check `manual.history-attempts`, version `1`.
- **args.existing_selectors**: [].
- **args.proposed_selectors**: `test_engine.LeanAttemptTests.test_settled_revision_change_and_unsettled_effect_refusal`, `test_engine.LeanHistoryTests.test_persisted_task_check_commit_order_and_readonly_reopen`.
- **args.command**: shared Python expansion above.
- **PASS**: Real Engine/Store/saver tests show revision-aware compatible new attempts only at settled boundaries, with no full-code eligibility/per-node rehash/old-identity rewrite. Ordered task/check/SHA/decision/review/effect history survives close/reopen. Incompatible schema/config/authority or incomplete SDK/tool/Git effects block affected replay/reliance, without SIGKILL/recovery/cutover trials.
- **Evidence**: Named proposed tests, real stored order/old-new identities and A2 applicability assessment.
- **producer_dependencies**: T001/V2, T001/V3. **gates**: defaults.

**REQUIRED T002/V2 — A3/A4: honest history reader surface and non-authoritative optional observations.** Check `manual.history-readers`, version `1`.
- **args.existing_selectors**: `test_recovery.VersionRecoveryTests.test_future_schema_rejected_without_downgrade_or_deserialization`, `test_metrics.UsageSegmentsTests.test_missing_counter_independent_fields_and_no_fake_agent`.
- **args.proposed_selectors**: `test_engine.LeanHistoryTests.test_old_records_unchanged_and_versioned_reader`, `test_projections.LeanProjectionTests.test_unknown_metrics_and_publication_failure_preserve_result`.
- **args.command**: shared Python expansion above.
- **PASS**: Old records/pins remain unchanged and historically interpreted or explicitly unsupported. Versioned semantic history explains actual A2 and retains workflow/graph. Unknown metrics/publication failure cannot overwrite authoritative success; liveness stays distinct from recorded state and public fields private-data allowlisted. No auto-migration or obsolete-table guarantee.
- **Evidence**: Named reader/unknown-version/null/publication results, fixture before/after comparison and actual A2 history mapping; otherwise NOT VERIFIED.
- **producer_dependencies**: T001/V2. **gates**: defaults.

**REQUIRED T002/V3 — A4: operating/schema/requirements match durable behavior and delimit monitor renewal.** Check `manual.history-docs`, version `1`.
- **args.procedure**: git diff --check; compare changed DDL/reader semantics, attempt revisions and publication behavior with operating/schema/REQUIREMENTS docs and monitor-v1 compatibility assumptions.
- **PASS**: Docs match supported history/reader versions, retained YAML, revisions and explicit unsupported behavior. Name later monitor reader/data-model/source/tasks approval renewal for removed parent/proof/pin assumptions; no unchanged-app compatibility, app implementation, table-freeze framework or old-evidence rewrite.
- **Evidence**: Changed code/doc spans and affected monitor contract references; no historical acceptance/evidence dependency.
- **producer_dependencies**: T002/V1, T002/V2. **gates**: defaults.

- [ ] T003 Deliver product full-range review and genuine owner-input paths without document/parent proof protocols; remove obsolete routes and align operative docs before writer checkpoint.
  - **Depends**: T002.
  - **order / context_group**: `2` / `lean-review`.
  - **owned_paths**: R: `verification.py`, `review_documents.py`, `interaction.py`, `notifications/paseo.py`, `cli.py`, `pi_adapter.py`, `schemas/agent-result.schema.json`, `schemas/interaction.schema.json`, `schemas/host.schema.json`, `workflows/coordinate.yaml`; T: `test_review_documents.py`, `test_review_repair.py`, `test_interaction.py`, `test_parent_transport.py`, `test_pi_adapter.py`, `test_host.mjs`; S: `SKILL.md`; D: `coordinate-implementation.md`, `coordinate-implementation-schema.md`; root: `runtime/pi-host/host.mjs`, `REQUIREMENTS.md`, `README.md`.

Replace inline full-binary-diff/doc-attestation review with actual range/source/evidence references
and read-only file access; preserve fresh reviewer, stale-head protection, finding/repair/current-range
review. Simplify Interaction/Paseo to genuine scoped original-associated answers/dedup/pending, not
parent proof chains or telemetry vetoes. No fabricated answers, fresh substitution or blind replay.
Delete obsolete routes/schema/tests with mechanisms; retain data-loss/credential/external-action checks.
Writer verification and focused commit finish this delivery; independent acceptance happens afterward.

**REQUIRED T003/V1 — A1/A4: independent reviewer reads actual range and files without oversized proof delivery.** Check `manual.review-seams`, version `1`.
- **args.existing_selectors**: [].
- **args.proposed_selectors**: `test_review_repair.LeanReviewTests.test_range_reads_stale_denial_and_repair_rereview`.
- **args.command**: shared Python expansion above.
- **PASS**: Independent read-only product review gets actual range/source/evidence/file continuation, not binary bundles or SDK document-delivery coverage. New temporary-Git helper case observes range/file access, missing/stale-review denial and verified repair/current-head rereview, without the old coordinate_fixture SDK manifest/cgroup setup. Delete obsolete helpers/schema/tests, retain authority/custody. No extra live reviewer trial.
- **Evidence**: Named range/file/repair/stale-head results and deletion diff; local tests are wiring proof, not reviewer judgment.
- **producer_dependencies**: T002/V1, T002/V2. **gates**: defaults.

**REQUIRED T003/V2 — A1/A3: genuine scoped owner answers with simpler delivery and no telemetry/provenance veto.** Check `manual.owner-input`, version `1`.
- **args.existing_selectors**: [].
- **args.proposed_selectors**: `test_interaction.LeanAnswerTests.test_scoped_original_answer_dedup_and_uncertain_delivery`, `test_parent_transport.LeanAnswerTests.test_untrusted_or_unavailable_answer_remains_pending`.
- **args.command**: shared Python expansion above.
- **PASS**: Interaction/transport helpers accept only genuine scoped original-associated answers, deduplicate, and keep missing/untrusted answers pending. Remove parent proofs/headroom vetoes, not authority/settlement. Uncertain delivery cannot blindly resend/reask or substitute fresh worker. Proposed local helper/SQLite cases need no actual UI/provider/reconnect/death/control programme.
- **Evidence**: Named proposed cases, zero delivery for untrusted/missing/uncertain input and deletion diff; no fake ask_user/live claim.
- **producer_dependencies**: T002/V1. **gates**: defaults.

**REQUIRED T003/V3 — A1-A4: writer verification of the deletion-first path, operative docs, compatibility and final-candidate A2 applicability.** Check `manual.final-path-check`, version `1`.
- **args.procedure**: Before T003 writer commit: git diff --check; inspect changed production/doc/test/config path and entire refactor deletion diff from 548a33d2d6be8645ae032ff57b059bffc72a5f88..working-tree candidate; map A1-A4 and assess final-revision applicability of the actual T001 A2 proof. Rerun only invalidated A2 seams under G-live before claiming this item passes.
- **PASS**: Before writer commit, code/docs/deletion audit confirms five readiness facts/five execution rules without hidden retired blockers; changed safety/history/reader tests pass and A2 remains applicable (rerun affected seams only under G-live). Retire obsolete assertions, preserve data-loss/credential/external-action checks. Independent delivery review is strictly post-checkpoint acceptance, not this item or a task gate.
- **Evidence**: Precommit changed-code/doc audit, named focused results and A1-A4/A2 applicability mapping; no old migration evidence/candidate_files/reviewer receipts.
- **producer_dependencies**: T001/V1, T001/V2, T001/V3, T001/V4, T002/V1, T002/V2, T002/V3, T003/V1, T003/V2. **gates**: defaults.

## Post-checkpoint final acceptance — not task verification

POST-CHECKPOINT FINAL ACCEPTANCE ONLY (not task verification): fresh independent read-only reviewer of the full actual refactor range 548a33d2d6be8645ae032ff57b059bffc72a5f88..final-HEAD, separate from implementers. Inspect source, actual commits/diffs and A1-A4 evidence; resolve findings by authorized focused verified repair commits and current-range rereview. Missing review blocks final acceptance, never writer task checkpoints; no empty report/evidence commit. Historical migration baseline/evidence/reviewer receipts are not this refactor acceptance.

That capability entry is manual acceptance metadata, not a runtime registry action or current
approval. The fixed review base is the clean pre-refactor planning baseline above; coordinator
also records each actual implementation task's starting HEAD. Review all resulting committed
code/docs and evidence, not historical migration baseline `75353862...`, old t010/evidence.json,
candidate_files or prior reviewer receipts. No G-review gate is attached to writer REQUIRED items.

## Evidence basis and authoring validation

Reuse inspected local LangGraph 1.2.16/saver 3.1.2/SDK 0.87.1 seams. Generic SDK compatibility
is unproved until A2. No internet/install/version change/prototype/report chain/generic harness.
One A2 supplies live proof; unrelated summary/retry/control/death/cutover or historical acceptance
programmes are not prerequisites. Retire obsolete assertions, never rewrite old proofs or weaken
meaningful safety to obtain green.

A1 = T001/V1,V4 + T002/V1 + T003/V1,V2,V3; A2 = T001/V2, applicability checked in T002/V1,V2
and T003/V3; A3 = T001/V3 + T002/V1,V2 + T003/V2; A4 = T001/V4 + T002/V2,V3 + T003/V1,V3
and post-checkpoint final acceptance. Optional arrays are empty; broad regressions are optional.
Run each shared selected check once, retain named item mappings, rerun only invalidated proof.
Source exclusions/manual gates apply; no app/planner overhaul/new tracker/parallel lean mode.

This correction starts from clean `548a33d2d6be8645ae032ff57b059bffc72a5f88`; original source
and hash above unchanged. Local memory index/guidelines remain empty; no memory writes. Producer
Sol/medium, no nested calls. Authoring-only validation: schema/order, exact human/JSON mappings,
selector existence/proposed status by source inspection, source hash/local links, manual dependency/
permission/current-content/docs/feasibility review and git diff --check. Commands/results and focused
SHA are in external producer return. Implementation/fixture/live tests NOT RUN; approvals pending.
