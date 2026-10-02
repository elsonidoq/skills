# Unified Planner Refactor

## Approved design and authorization

The owner approved one public `planner`, a separate `tiny-spec` producer, no new Epic
concept, genuine installed SpecKit for Standard, a shared task contract, and unchanged
implementation execution. The owner explicitly authorized implementation in the existing
feature worktree. This record captures those decisions; it does not invent review or
implementation acceptance evidence.

- Before path selection: read-only discovery and proportional brainstorming, session-history
  decisions only, no source edits or planning files. Recover missing answers by asking.
- Present an approximate qualitative scope assessment and both paths; stop for user choice.
- TinySpec: compact what/how source → separate tasks → planner review → combined owner approval.
- Standard: observed SpecKit specify → specification approval → plan → tasks → independent
  analysis/review → overall approval. Preserve operational stage safeguards.
- Every artifact approval, including renewals, requires an owner-visible executive brief
  before `ask_user`. Depth selection authorizes preparation, never implementation.
- Task semantics stay in `task-generation`; execution stays in `coordinate-implementation`.
- Existing approved and partially planned work retains original provenance and applicable gates.
- No live model-based scenario tests, installed SpecKit trials, or global installation are
  authorized by this implementation request. Deterministic validation is authorized.

## Baseline captured before replacement

Clean worktree on branch `redesign-planning-workflow-tinyspec-standard`; baseline revision
`a04e3df68b09`. `scripts/check-skills-lint.sh` passed before changes (output captured at
`/tmp/planner-baseline.log`). This is static verification, not model-obedience evidence.
The baseline source remains available in Git. Previous behavior inventory:
[Requirements Manager coverage](requirements-manager-coverage.md), B01–B30, and its linked
historical reviews. Those records remain historical and are not rewritten to claim this
refactor was tested.

## Preservation ledger

Derive these rows from baseline sources before replacing skills. Test identifiers refer to
planned checks, not passed evidence. Any unmapped behavior blocks retirement/acceptance.

| ID | Baseline source / behavior | New owner | Disposition | Regression check |
| --- | --- | --- | --- | --- |
| P01 | create-epic Discovery/Evidence: selected bounds, citations, positive/negative claims, no-task claims, UNVERIFIED/deferrals, beneficiary | planner discovery | preserve | discovery contracts; false-satisfied scenario |
| P02 | create-epic Sizing/Content: exclusions, separately scheduled mechanical work, no duplication | planner/source/task review | preserve without Epic | traceability scenario |
| P03 | epic-brainstorming gate: exact results, ≤3 agenda items, concrete options, bias to skip mechanical uncertainty | planning-brainstorming | preserve | brainstorm contracts/mutations |
| P04 | epic-brainstorming dialogue/application: one owner item, exact answers/rationale, bounded edits, deferrals | planning-brainstorming | preserve; apply after choice | decision/resume scenarios |
| P05 | both managers: durable source before dialogue | planner/session record | deliberate change: read-only until choice | preselection trace/write attempts |
| P06 | managers/reference sizing: all-three rule, conditional routing, documentation Epic exception | planner/reference | deliberate removal; qualitative assessment and unconditional choice | owner-override scenarios/mutations |
| P07 | epics-manager preflight: authoritative reference, observed SpecKit stages, constitution repair/verification, valid principles stay settled | planner Standard | preserve; Standard checks after choice | stage-local contracts/capability scenarios |
| P08 | epics-manager every-stage: verbatim constraints, cited authorities, prior handoff, unanswered flags, originating correction context | planner stage briefs | preserve | delegation-input/resume scenarios |
| P09 | epics-manager spec_create: sonnet class, optional clarification, current spec approval before plan | planner Standard | preserve plus executive brief | stage order/class/approval mutations |
| P10 | plan_create/helper: opus class, same-session spec-review/fix → one plan → plan-review/fix, no adapter double-run, renew spec approval | planner/helper | preserve | adapter/session/renewal contracts |
| P11 | tasks_create: sonnet class, create-only, prepare authorization, no circular final-approval prerequisite | planner/task-generation | preserve | producer ownership/authorization mutations |
| P12 | overall_review: observed independent owner-selected reviewer, analysis, mechanics fixed internally, material defaults forbidden | planner Standard | preserve | reviewer/correction scenarios |
| P13 | requirements-manager review: lightweight review then combined current source/task/implementation approval | planner TinySpec | preserve; no independent planning reviewer requirement | TinySpec approval/denial scenarios |
| P14 | all approvals/resume: current content, external evidence, earliest-invalid return, no label-only proof | planner/coordinator | preserve; all renewals briefed | stale-evidence/brief trace fixtures |
| P15 | requirements-manager source may live inside tasks | legacy planner repair/coordinator intake | preserve for legacy only; new TinySpec separate | legacy embedded-source fixture |
| P16 | task-generation: format discovery, IDs/dependencies/story continuity, full metadata, 30% exception, docs/integration, manual fallback | task-generation | unchanged semantics | existing parser units + shared contracts |
| P17 | coordinate intake: origin-specific authorization, other documented origins, ambiguous origin stop, SpecKit applicability/fallback | coordinator/planner legacy repair | preserve with mapped recovery | intake contracts/legacy scenarios |
| P18 | coordinator from Execution Capability Preflight onward: classes, local threshold/full count, graph, async sequential batching, context, inspected failure, mutation tools, task commits, final range review | coordinator | byte-identical | execution-section digest + existing batching/intake tests |
| P19 | memory-handling: verified association, whole index first, matching entries only, no global guess | existing consumers/planner | preserve | memory contracts/scenarios |
| P20 | initialize-documentation: fresh dirty-project investigation, plan approval, owner/shell separation, schema owners, concurrent edits | initialize-documentation/planner | preserve; no mandatory Epic | docs contracts/migration scenarios |
| P21 | install-memory: proposal-first, marked section, unrelated bytes intact, dirty/concurrent protection, no fabricated memory | install-memory | preserve plus bounded refresh | adoption scenarios |
| P22 | installer: symlinks/discovery/reference, collision safety | installer | retired ownership-only cleanup; new foreign collisions preserve/report | isolated installer filesystem tests |
| P23 | global portability: no invented model/provider/path/state; observed capabilities and safe unavailable branches | all active skills | preserve | lint/negative mutations |
| P24 | auto brainstorming process: design depth not execution-path choice | planner/brainstorming | explicit boundary | choice/extra-gate mutations |

## Implementation sequence

1. Baseline/ledger and test oracles before retiring carriers.
2. Shared preselection mechanism, TinySpec primitive, unified planner with full Standard stages.
3. Shared task adapters, helper and coordinator intake/legacy recovery; freeze execution body.
4. Adoption/docs/current guides, safe installation migration and discovery.
5. Static/mutation/fixture/trace tests and a bounded RPC scenario runner; no live runs without
   separate owner authorization. Retire old carriers only after mapping their behavior.
6. Run deterministic checks, inspect full diff, report remaining evidence limitations.

## Validation evidence

- Baseline: PASS static suite checks before replacement.
- Candidate: PASS `scripts/check-skills-lint.sh` (23 skills; 56 offline tests across six
  suites, including instruction mutations, trace oracles, installer fixtures and fake RPC).
- Both synthetic adapter task fixtures: PASS existing `check-task-order.py`.
- Shell syntax, Python compilation and `git diff --check`: PASS.
- Coordinator execution body: identical to baseline, verified by preserved digest.
- Initial independent Astra review: core architecture/safeguards preserved; blocked on
  trace lifecycle integrity and disconnected shared-invocation mutation coverage.
- F1 reproduced with orphan/wrong-tool/reversed/duplicate choice traces and fixed by
  validating tracked gate lifecycle before accepting an answer.
- F2 reproduced with operational invocation/application deletion mutations and fixed
  with section-local caller checks, including TinySpec/direct-task invocation.
- F3 fixed with supervisor-authored exact option-title mapping rather than title prefixes.
- Tests failed before these fixes (`/tmp/planner-review-reproduction.log`); all pass after.
- Independent targeted Astra recheck: READY, merge verdict OK with notes; F1–F3 fixed,
  no remaining issues found in the corrective scope. See the durable
  [initial review](reviews/planner-astra-initial-review.md) and
  [final recheck](reviews/planner-astra-final-recheck.md).
  This is independent review of the refactor and corrections, not live workflow acceptance.
- Real-agent behavior and installed SpecKit integration: NOT RUN.
- Global installation: subsequently authorized explicitly by owner and completed from
  this feature worktree. All 23 suite links and guidance verified; retired skill links
  removed from discovery. Previous suite links backed up outside discovery directories.
- Discovery-only Pi RPC `get_commands`: PASS, new planner commands present and all four
  retired commands absent; no prompt/model call. Model-based discovery probe: NOT RUN.

Command-labelled final output is captured at `/tmp/planner-final-verification.log`; tests are reproducible
from the repository. Passing fixture or static checks is not a live workflow claim.
See [regression guide](planner-regression.md) for scenario evidence and limitations.
Subsequent owner testing led to the [approval UX follow-up](planner-approval-ux.md):
explicit bullet-list briefs and automatic approved-phase continuation. Its verification
and review status are recorded separately; initial review evidence above is historical.
