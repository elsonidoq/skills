# SpecKit assets in Coherence initialization — tasks

Status: combined source/task/scope approval granted through `ask_user` on 2026-10-14:
“Approve and start coordinator preflight”. Approved content is the TinySpec and tasks at
`39a7eac25b444e8725b14216e53f697b322d26c6`: source SHA256
`3943ce3fd5d6b97e906004d872955725e92be6b51e0b84c14ea0e5aa404ec2d9`, tasks SHA256
`46fbc1269b7b15c1714c8d4edf665fced9d95c9d587392b765b15843a7ff3374`.
Planner review passed A1–A6 traceability, exclusions, REQUIRED gates and task order.
This status-only approval record leaves the reviewed T001 contract unchanged; coordinator
preflight starts now. Exact execution routing approval and fresh independent final review
remain required. Actual SpecKit installation and live probes remain excluded.

Requirements truth: [TinySpec](coherence-speckit-initialization-tinyspec.md), committed at
`a9db66274d51a61bafd537f1ba8511201fbfb21f`, SHA256
`3943ce3fd5d6b97e906004d872955725e92be6b51e0b84c14ea0e5aa404ec2d9`.
Direct TinySpec adapter; no plan or SpecKit task-stage capability required. No SDD guide
is used as direct requirements input. Governing [AGENTS](../../AGENTS.md),
[constitution](../../.specify/memory/constitution.md),
[approval](../../skills/planner/references/approval-and-recovery.md),
[early risk reduction](../../skills/planner/references/early-risk-reduction.md) and
[checkpoint](../../skills/memory-handling/references/task-commit-contract.md) contracts apply.
Associated `memory/MEMORY.md` and `memory/coordination/GUIDELINES.md` were read in full:
no gotchas or applicable guidance; no memory/coordination writes.

## Ordered delivery

- [ ] T001 Deliver safe every-initialization SpecKit asset checks and approved repair guidance
  - **Depends**: none (start only after combined current-content approval and coordinator routing authorization).
  - **Outcome**: The canonical initialization skill checks real project-local commands,
    templates and scripts on every route, proposes official version-aware repair only within
    approved bounds, preserves existing/custom content, and reports completeness honestly.
    Permanent focused regressions and README/REQUIREMENTS agree with this bounded exception.
    These coupled carrying surfaces are one independently verifiable outcome; tests,
    evidence, docs, review preparation and routine fixture teardown stay inside delivery.
  - **Likely files/interfaces**: `skills/initialize-coherence/SKILL.md` (canonical owner),
    `skills/initialize-coherence/scripts/test_contract.py`, its existing
    `fixtures/source-contract.json`, `fixtures/scenarios.json`, `fixtures/unsafe-permissions.json`,
    `README.md`, `REQUIREMENTS.md`. Only if needed, a concise supporting reference under
    `skills/initialize-coherence/references/`, discoverable from the skill. No new harness,
    competing dependency owner or generic prerequisite installation policy.
  - **Shared context / internal order**: Inspect existing stage-scoped `check_contract`,
    dynamically generated ledger preservation/deletion checks, scenario checks and
    `MutationTests`; retain their seven carrying stages and unrelated safety guards.
    Add permanent new positive/negative expectations first and establish old-contract
    sensitivity before relying on their final PASS. Then reconcile the canonical contract,
    live ledger expectations and setup/runtime docs; validate final integrated bytes.
    The `requirements` ledger row's blanket no-install expectation needs the bounded project
    asset exception; the `noop` row still protects association-only no-op semantics.
    Do not repurpose historical acceptance IDs or historical evidence as this delivery's proof.
  - **Implementation constraints carried into the worker brief**:
    - Check on every initialization, including compatible adoption and refresh.
    - TinySpec/direct tasking still does not require SpecKit.
    - Compatible adoption remains an instructions/memory no-op, not an exit that bypasses the SpecKit check.
    - No blanket specify init --here --force against an existing repository.
    - Missing usable CLI is a reported blocker for repair; do not silently install/upgrade global tooling.
    - Existing source provenance remains immutable: original sources, supporting historical text, revision and SOURCE_HASHES are unchanged.
    - After the dirty-first capability gate, discover integration, script variant, command
      location, recorded version/options from target metadata/configuration. Do not silently
      select noninteractive Copilot defaults. Validate an authoritative integration/version
      inventory against readable, nonempty actual files, script permissions and references;
      neither directory/manifest existence nor hash difference proves readiness or grants
      overwrite permission. Ambiguous integration, unsupported version, malformed metadata,
      unreadable assets and unsafe paths yield specific gaps/conflicts, not guesses.
    - Reuse the source's inspected official 1.0.12 help/package evidence: bundled offline
      assets, explicit integration/script/options, force overwrite risk, constitution preservation
      and managed-refresh limits. Describe isolated fresh staging with inspected candidate
      inventory/diff and approved missing-file-only transfer; exclude incidental scaffolding,
      `.git`, constitution replacement and unrelated metadata. Reconcile only necessary approved
      manifest entries so inventory matches installed files; never blindly replace custom metadata.
      Before any future execution, inspect that installed version's current official help/source;
      unknown safe merge behavior stops. Other versions need renewed applicable evidence.
    - Include exact asset/metadata target writes, integration/version/options, status and conflicts
      in the existing approval proposal. Preserve dirty-first (including untracked-only dirty),
      fresh read-only dirty-project investigation, exact dirty-overlap approval separate from
      general plan approval, denial/cancellation/ambiguity/missing-capability stops, project-root/
      symlink bounds, custom instructions/memory paths/content, constitution and unrelated bytes.
      Re-read before each write; drift/conflict/CLI failure stops. Report partial outputs without
      destructive rollback or automatic retry. Revalidate after approved repair; complete repeat
      runs propose no redundant rewrite. Missing assets block initialization-ready claims.
  - **REQUIRED acceptance** (inline coordinator/worker union; source A1–A6):
    - **T001/V1 — A1 every route / idempotence**: New, compatible and refresh routes all reach
      the three-family integration/version check; complete assets need no asset rewrite and
      compatible association remains untouched. Smallest check: stage-scoped permanent positive
      route scenarios in the existing owner plus deletion/bypass mutations, including an
      adoption early return despite a discovery check. PASS requires the composed source route
      from dirty-first discovery through adoption to final completeness reporting, not separate
      green helpers or scenario labels. Evidence: C1 named route/deletion/bypass results and
      C4 actual carrying spans for route continuation/no-op. Permissions: local static checks
      and manual inspection only; future initialization writes require their original approval.
    - **T001/V2 — A2 genuine completeness**: Empty shells, missing families, individual missing
      files and incomplete manifests cannot be ready; complete/custom valid files remain valid.
      Smallest check: focused positive/negative source scenarios and mutations require expected
      version-aware inventory plus actual-file readability/nonempty/permission/reference checks,
      rejecting existence-only and metadata-only alternatives. Evidence: C1 named results and
      C4 inventory requirements in operational guidance. PASS is static sensitivity to each
      specified incomplete case, not demonstrated installation. Permissions: local fixtures only;
      malformed/unsupported/unsafe discovery stops rather than invents readiness.
    - **T001/V3 — A3 proposal before repair**: Exact official install/repair proposal carries
      detected integration/options and bounded target/metadata writes before permission to act;
      denied/cancelled/ambiguous approval or unavailable mandatory approval capability grants
      nothing. Missing CLI or uncertain recipe reports a blocker without tooling installation.
      Smallest check: existing approval scenarios extended for asset repair, plus contradictory
      permission/default-integration/unconditional-install/blanket-force mutations. Evidence:
      C1 named positive/negative results and C4 proposal/recipe-to-source comparison. PASS rejects
      installation without approval, silent defaults and force overwrite while retaining bounded
      approved missing-file transfer. Permissions: no CLI installation, network or actual repair
      in this delivery; future repair keeps explicit current-content and overlap approval gates.
    - **T001/V4 — A4 custody and failure**: Preserve custom assets/constitution/metadata,
      unrelated work and instructions/memory; dirty-first/investigation/overlap/concurrent rules
      remain operative. Conflict/drift/CLI failure or partial output cannot claim ready, retry
      automatically or roll back destructively. Smallest check: retain existing dirty/untracked,
      investigation, overlap, concurrent and refresh checks; add focused custom preservation,
      unsafe overwrite/conflict continuation/failure-as-ready/partial-output/no-retry source cases
      and contradictory-permission mutations. Evidence: C1 named results plus C4 exact actual
      diff showing safety order and preservation-oriented staging/transfer constraints. PASS
      rejects each unsafe alternative, not merely mention of preservation in a summary.
      Permissions: local tests/manual diff; existing exact overlap and renewed approval remain
      necessary before any future write, with drift first stopping the affected patch.
    - **T001/V5 — A5 report and lockstep docs**: Validation reports actual three-family
      completeness, repair/no-op and blockers on all routes; missing assets never imply ready.
      README setup and REQUIREMENTS runtime match the skill's bounded project-asset exception,
      unchanged TinySpec independence and other missing-runtime stop/report behavior; `/reload`
      remains required after global skill changes. Smallest check: extend existing
      `test_setup_matches_branch_and_readiness_bounds` and source reporting scenarios/mutations;
      C3 resolves introduced local references and C4 compares docs with implemented guidance.
      Evidence: C1 named results, C3 target/anchor results and C4 changed-carrier comparison.
      PASS requires operational/doc agreement, not link existence alone. Permissions: local
      checks/manual review only; docs cannot broaden installation or planning-depth authority.
    - **T001/V6 — A6 provenance and retained oracle**: Original `sources`, `supporting`,
      `revision` and `SOURCE_HASHES` remain identical; only necessary live ledger expectations/
      ownership explanations change. Preserve unrelated guards and all stage-deletion and
      contradictory-permission mutation sensitivity. Smallest check: C2's four BaselineTests,
      C1 full focused suite, plus C4 comparison of immutable JSON fields and Python hash constant
      against the task baseline (the existing baseline mode alone does not protect every
      supporting historical byte). Evidence: commands/counts/named results, explicit unchanged
      field/constant comparison, and new expectations FAIL on the old contract / PASS on final
      contract. Obtain old skill bytes read-only with `git show a9db66274d51a61bafd537f1ba8511201fbfb21f:skills/initialize-coherence/SKILL.md`;
      exercise new scoped checks via existing in-memory checker/test seams, without resetting
      the worktree or altering provenance to make green. PASS requires named expected diagnostics,
      not an unrelated failure. Permissions: local Python/Git/manual checks; no historical rewrite.
  - **Capabilities / gates**: V1–V6 require Python 3, readable existing owners, local Git/file
    tools and approved bounded implementation authority. No representative-sample owner STOP
    or special live capability is needed for this static delivery. Missing REQUIRED evidence
    or capability is NOT VERIFIED and blocks reliance/dispatch or acceptance at the applicable
    gate. Report material disproof or changed scope to planner for affected review/renewed
    current-content approval; no weakened replacement acceptance. Coordinator owns exact
    execution routing and fresh independent final implementation review, not the task producer.
  - **Verification effort / checkpoint**: Bounded existing source/scenario/mutation checks,
    new expectation old/new sensitivity, introduced links and manual actual diff/provenance/doc
    comparison. The full existing focused suite is required for immutable-source and unrelated
    guard preservation; no broader suite or new infrastructure is justified. Reuse each shared
    final command once with all item mappings, rerunning only invalidated evidence. Return
    named results, limitations, baseline/result SHA, actual owned diff and residual state; validate
    and checkpoint explicit task-owned paths under the shared task-commit contract before handoff.

## Shared checks and authorization bounds

| Check | Command / smallest observation | REQUIRED mapping |
| --- | --- | --- |
| C1 | `PYTHONDONTWRITEBYTECODE=1 python3 skills/initialize-coherence/scripts/test_contract.py` — named positive/scenario/deletion/unsafe-permission results; extend the existing fixtures/checker as above | V1–V6 |
| C2 | `PYTHONDONTWRITEBYTECODE=1 python3 skills/initialize-coherence/scripts/test_contract.py --baseline` — original attribution/hash/coverage/ledger checks, four baseline tests retained | V6 |
| C3 | Resolve only introduced local Markdown file/anchor references, including optional skill-local guidance; use existing reference test where sufficient | V5 |
| C4 | `git diff --check` plus manual actual owned diff, immutable provenance comparison and docs-to-guidance comparison; retain item-mapped findings in runtime return | V1–V6 |

A shared check must retain each item's named case/pass condition; a generic green count cannot
replace missing item evidence. Old/new sensitivity belongs inside C1/V6, not a separate task.
Optional broader lint/regression is nonblocking unless a concrete changed seam warrants renewed
scope; no default skills/docs lint or exhaustive matrix.

Exclusions: actual SpecKit install/repair in any project; CLI execution trials, live/provider/model
behavior, network/auth/probes, application/test/generated application changes, databases/deployment,
general prerequisite installation, new test infrastructure, constitutional/planning-depth changes,
source modification, STATE upkeep and memory/coordination records. Actual CLI install and model
behavior are **NOT RUN / NOT VERIFIED**, outside authorization, and cannot release runtime reliance.
Future runtime proof needs separate permission, disposable target, actual version/integration/tool
capability and observed before/after evidence. Permanent static checks prove instruction consistency
and mutation sensitivity only, not agent obedience or successful installation.

## Risk selection and task-production validation

No prototype or independent prerequisite: the consequential overwrite/adoption-bypass risk is
bounded operational guidance, already informed by inspected official 1.0.12 local help/source.
Permanent existing source checks plus targeted mutations are the earliest sufficient delivery
proof. No disposable experiment, internet research or duplicate proof/report chain adds needed
static evidence. Version variance and unproved runtime behavior remain explicit limits; fail-closed
version discovery and truthful NOT RUN reporting contain them. Guidance stays canonical in the
skill and optional discoverable local reference, not a new research artifact.

Preparation baseline `a9db66274d51a61bafd537f1ba8511201fbfb21f`, main, clean index/worktree;
source hash verified; Python 3.12.3 available. Producer writes are limited to this separate tasks
file and its discovery entry in `docs/plans/index.md`. Source-only 138 focused tests and four
baseline tests PASS are supplied reusable baseline evidence, not final implementation acceptance.

Task-production validation: PASS
`python3 skills/task-generation/scripts/check-task-order.py docs/plans/coherence-speckit-initialization-tasks.md`
(one T001, explicit none, no forward/implicit producers or interrupted stories); PASS introduced
local links, six A-to-V mappings and exact constraint carry-through; PASS `git diff --check` and
manual scope/traceability/exclusion/gate/doc/proof-limit review. Scheduled C1–C4 implementation
acceptance is NOT RUN by this producer. Exact artifact digest and focused checkpoint result travel
in the producer return (no recursive self-hash). Any changed source/tasks reopen affected producing
review and approval. Combined current-content approval and later coordinator routing/final
independent review remain pending.
