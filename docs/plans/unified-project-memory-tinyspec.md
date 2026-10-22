# Unified project memory — TinySpec

## Outcome and authority

The owner wants one project-associated memory store/index for appropriate technical gotchas **and explicit future-directed owner guidance**, so planning, execution preparation and closeout cannot recreate a separate coordination-guidelines subsystem. This source captures the conversation-only request; the owner selected **TinySpec, planning only** through `ask_user`. Source preparation/checkpoint is authorized; separate tasks, planner inspection and combined owner approval follow. This is not implementation approval or a task checklist.

The latest owner direction is: **“Do not maintain old memory/coordination records. They are worthless”.** This supersedes separate-store maintenance and historical preservation-in-place instructions for the bounded cleanup proposed below. No historical deletion/relocation occurs during planning. The preselection assessment returned `NO_BRAINSTORM_NEEDED`; its claim that the owner permanently prohibited deletion was incorrect and is not a constraint here.

Applicable accepted decisions remain binding:

- [ADR-0003](../decisions/ADR-0003-current-launch-authority-and-neutral-tasks.md#decision): executable task instructions/check permissions are authorization-neutral; temporary planning-only status belongs in approval records. Later current owner-authorized execution is not blocked merely by historical phase wording. Preserve requirements, actual gates and historical approvals; do not change runner prompts here.
- [ADR-0004](../decisions/ADR-0004-shared-routine-worker-permissions.md#decision): preserve shared routine scoped worker permissions, small isolated tests/databases, ordinary scoped fixes and their data/resource/credential/external-action limits. No new permission service, repeated ordinary approval gate or runtime change.

## Behavior and constraints

**One association, one index.** Make [Memory Handling](../../skills/memory-handling/SKILL.md) the single reusable retrieval/write authority. Discover the actual project association/index from its instructions/configuration; respect custom paths. This repository retains `memory/MEMORY.md`, not a second `GUIDELINES.md`. Gotchas and owner guidance may have labeled sections/entry kinds in that index; both use compact trigger/relevance pointers and optional selectively opened entries, not parallel indexes or stores. Global skills must not hardcode this repository's paths or contain project-specific knowledge.

Read the **whole associated index first**, open only relevant entries in full, and recheck after memory writes. No wholesale history intake. Missing optional storage/STATE remains nonblocking; an unverified required association is reported/routed through existing adoption rules, never guessed or replaced by global memory. Do not silently create storage while reading. Approved new adoption may create the bounded unified skeleton; authorized feedback uses the verified association and allowed paths, not a fallback coordination root.

**Different evidence, same store.** Technical gotchas remain verified, non-obvious, durable action-triggered warnings with consequence and evidence, not ordinary documentation or inferred process lessons disguised as gotchas. Explicit owner guidance carries the actual user provenance and concise future trigger/action; it need not masquerade as a technical surprise. Guidance authority is **only explicit future-directed user feedback**. Explanation-only questions, ordinary implementation approval, agent observations, failed runs and inferred lessons authorize no guidance write. Clear bounded feedback needs no routine second approval; ambiguity asks before writing; an explicit no-write boundary wins. Memory never overrides current owner/source authority.

Carry relevant guidance into source observables, dependency/gate and task-local REQUIRED checks and worker/reviewer briefs where applicable; do not add execution-time feedback/routing intake, model selection policy or memory-writing obligations. Keep the existing technical-gotcha retrieval seam. Preserve this owner guidance **verbatim**, with conversation provenance, in the unified project memory during approved implementation (not during this preparation):

> Routine task transitions/completions and steering-status updates must not wake the parent agent or require acknowledgment. Only agent questions and terminal workflow completion, whether success or error, should trigger a parent turn.

This records guidance only. Investigating, implementing or testing parent-wakeup/runtime behavior is out of scope.

**Closeout is conditional, not reflection.** `finish-session` uses the same association/index for both kinds. Route verified technical gotchas and explicitly authorized future guidance separately by their authority, then update/reuse relevant entries without duplication. No feedback means no guidance write. Unrelated closeout need not search for memory unless the existing discovery contract requires it. Recheck after writes; compaction uses only an actual configured/user-selected target and existing approval/safety rules. `compact-memory` must recognize valid owner guidance as keepable (not drop/migrate it merely because it is not a gotcha); preserve provenance, explicit authority and all compaction backup/approval protections. `finish-session-jev` inherits the unified base workflow; optional classification cannot authorize guidance, infer lessons or suppress manual review. No new Jev dependency or issue-management changes.

**Safety and non-bookkeeping.** Preserve project-local path/symlink containment, sensitive-data exclusion, readable-file/owner checks, dirty/custom/unrelated content, reread-before-write and concurrent-drift stops. Owner-authorized concurrency is valid with explicit path ownership; overlap/uncertain ownership stops affected writes, not all concurrency. Preserve focused validated task checkpoints, hooks/signing, current-content approvals, required/manual/permission gates, safe failure diagnosis/retry and independent implementation review. No automatic reflection, per-task memory writes, progress ledgers, STATE maintenance, routine summaries/index refreshes or evidence-only commits. A real authorized memory change may update its index and checkpoint as its substantive deliverable; that is not routine bookkeeping.

## Approach and verified change inventory

Repository-derived approach: reuse the existing Markdown association/index and local contract/fixture checks; delete the separate contract after moving only its still-required authority/safety semantics into Memory Handling and its existing owners. Do not leave an operational redirect/shim that preserves the separate subsystem. Recovery stays with its existing coordinator owner and checkpoints with their existing shared owner; do not duplicate their protocols in memory.

Inspection baseline: `5088b25877467887dd41c9547197c6da43b3c165` on `plan-unified-project-memory-cleanup`. Citations below refer to that revision; line spans locate verified seams, not permanent line-number APIs.

| Classification / inspected seam | Consequence for the approved change |
| --- | --- |
| Active authority: [Memory Handling](../../skills/memory-handling/SKILL.md), lines 8–17, 29–60, 62–78; [separate reference](../../skills/memory-handling/references/project-coordination.md), lines 7–44 | Consolidate retrieval/feedback/safety semantics; remove separate guideline discovery/creation and the reference file. Retarget active links to Memory Handling; preserve no-routine-write rules. |
| Active checkpoint owner: [task-commit contract](../../skills/memory-handling/references/task-commit-contract.md), lines 89–97 | Replace feedback link/absent-coordination wording only; preserve checkpoint behavior and recovery ownership. |
| Active producers/consumers: [planner](../../skills/planner/SKILL.md), lines 40–68 and Selected production/stage handoffs; [TinySpec](../../skills/tiny-spec/SKILL.md), Inputs/preflight; [task generation](../../skills/task-generation/SKILL.md), lines 16–38, both adapters; [architectural helper](../../skills/delegating-architectural-planning/SKILL.md), lines 27–37 and 48–49 | All direct, standalone, resumed and managed paths use unified intake and propagation; retain accepted-ADR/source truth and REQUIRED mappings, not merely renamed links. |
| Active execution facade: [coordinate-implementation](../../skills/coordinate-implementation/SKILL.md), lines 21–32 | Remove separate feedback owner; retain gotcha reads, approved-constraint consumption, nonblocking missing memory and no automatic writes. No runner/executor behavior change. |
| Active closeout: [finish-session](../../skills/finish-session/SKILL.md), Core invariants 4/7, Step 3 routing, Steps 5/6; [compact-memory](../../skills/compact-memory/SKILL.md), Preconditions 3, Safety and KEEP/MIGRATE/MERGE/DROP; [finish-session-jev](../../skills/finish-session-jev/SKILL.md), base inheritance and memory choice | Remove gotcha-only exclusions for valid owner guidance; unify closeout without reflection or classification-as-authorization. |
| Active adoption: [initialize-coherence](../../skills/initialize-coherence/SKILL.md), Adoption Memory/Coordination bullets, skeleton and refresh/Validation | New adoption produces one association/index supporting both kinds; refresh preserves custom paths/content and requires existing bounded approval. No second-store scaffold, propagation or implicit migration/deletion in other projects. |
| Active repository owners: [AGENTS](../../AGENTS.md), Coherence gotcha-memory paragraph; [README](../../README.md), Context-first recovery and Asset boundaries; [REQUIREMENTS](../../REQUIREMENTS.md), lines 119–134; [constitution](../../.specify/memory/constitution.md), II/III/VI and Project Constraints; [docs routing](../index.md), feedback routing row, association paragraph and guidance links; [memory index](../../memory/MEMORY.md), lines 3–10 | Align operative policy and this repository's association. The approved change includes necessary memory-related constitutional amendment/rationale under existing governance, not unrelated policy revision. Preserve historical amendment text as provenance. |
| Active checker assumptions: [check-planner-workflow.py](../../scripts/check-planner-workflow.py), PATHS, lines 496–527 and load_texts link checks; [test-planner-workflow.py](../../scripts/test-planner-workflow.py), ProjectCoordinationWiringTests and feedback-carrier tests; [coordination tests](../../skills/memory-handling/scripts/test_coordination_contract.py), GUARDS and creation fixture | Replace positive separate-owner/creation expectations with unified carrier/association assertions and focused negative reintroduction mutations. Reuse the existing test file if useful; its name alone is not an active separate store. Do not delete safety assertions to get green. |
| Active adoption tests: [initialization tests](../../skills/initialize-coherence/scripts/test_contract.py), lines 322–369 and WorkflowOwnershipOutputTests; [output fixtures](../../skills/initialize-coherence/scripts/fixtures/workflow-ownership-outputs.json), new/full/refresh outputs and policy-only files_before/files_after | Replace the positive “coordination memory remains a separate” assertion. Add unified new/refresh outputs and custom-path assertions. Existing custom/coordination fixture bytes are preservation inputs, not authority to initialize, read or maintain a second subsystem; policy-only unrelated-file preservation remains valid. |
| Mixed regression guide: [planner regression](planner-regression.md), current feedback-contract section versus historical run evidence | Update current validation instructions; retain historical claims and repair deleted-target provenance links without rewriting recorded approvals/results. |

Discovery used tracked `memory/coordination` inventory and `rg -n --hidden -g '!.git'` searches for `coordination/`, `project-coordination`, `GUIDELINES.md`, coordination-memory and equivalent guideline/feedback/memory wording across skills, scripts, docs, `.pi` and `.specify`. Hidden SpecKit prompts/templates did not reveal an additional separate-store producer; their file-based coordination is not memory. `planning-brainstorming` consumes applicable memory without its own separate-store instruction. This is a verified starting inventory, not permission to skip a changed-reference/equivalent-term scan during implementation. Extend only for demonstrated active contradictions, not every historical keyword.

Distinguish negative regression strings that intentionally reject automatic initialization/reflection from positive propagation. Preserve frozen historical fixtures such as `skills/initialize-coherence/scripts/fixtures/old-initialize-coherence.txt` and `source-contract.json` as attributed baselines, not current templates; adjust only invalidated active expectations. Prior `docs/plans/` and `specs/001-*`, `002-*`, `003-*` mentions are historical requirements/approval/execution context, not policy to normalize wholesale.

## Historical disposition for combined approval

**Proposed consequential disposition:** remove all 41 tracked files below `memory/coordination` during approved implementation, after replacing necessary inbound references with precise Git-revision provenance. Do not retain or relocate the directory wholesale, create an archive/evidence store, or promote run/reflection summaries to memory. This explicitly reconciles the latest deletion direction with historical approval preservation: bytes remain in Git, not in an actively maintained memory tree.

The whole legacy evidence index was read first. `GUIDELINES.md` says “No approved project coordination guidelines yet”; the associated gotcha index also has no entries. Relevant selective inspection confirmed substantive approval provenance in `evidence/planner-delegation-approval/SUMMARY.md`, lines 5–44 (owner answer, scope and exact source/task digests), and autonomy direction in `evidence/2026-10-05-batch-commit-autonomy/SUMMARY.md`, lines 3–9; the latter is already covered by the task-commit contract. This is not a claim that every historical sentence was reread or that historical evidence constitutes approved guidance. Preserve still-applicable rules already owned by current instructions/contracts; the new verbatim parent-turn instruction above comes from current explicit feedback, not historical reflection.

Use baseline revision `5088b25877467887dd41c9547197c6da43b3c165` plus exact removed path for each historical target (including the retired `project-coordination.md` reference). Example retrieval: `git show 5088b25877467887dd41c9547197c6da43b3c165:memory/coordination/evidence/planner-delegation-approval/SUMMARY.md`. For clickable references use the existing origin's immutable blob form, e.g. `https://github.com/elsonidoq/skills/blob/5088b25877467887dd41c9547197c6da43b3c165/memory/coordination/evidence/planner-delegation-approval/SUMMARY.md`; local Git object/path validation is authoritative here, remote publication/access is not assumed or required. Keep exact target/fragment where meaningful and identify historical scope; no push is authorized. Repair live routing/index links and historical inbound links to removed files by pinning only their reference destinations, preserving historical text, source/task shapes, answers, digests, failed/withdrawn attempts and uncertainty. Relative paths inside archived content resolve against that same revision when retrieved, not today's tree.

Affected inbound owners include `docs/index.md`, `docs/plans/index.md`, historical source/tasks/briefs/regression records and `specs/001-model-family-routing` / `specs/002-batch-routing-contracts` records. Classify each incoming reference: operative contract → unified owner; historical claim/approval → revision/path, never a silently substituted current contract. Before deletion, verify every target exists in Git and guidance/provenance disposition is complete. Unexpected substantive guidance with uncertain current authority stops only its deletion/disposition for parent/owner resolution; do not keep the whole directory by default or erase that guidance. A material policy alternative requires renewed affected approval. Git is also the rollback/retrieval mechanism; no automatic revert or new backup subsystem.

Exact tracked inventory (paths relative to `memory/coordination/`; first is an empty guidance placeholder, second a historical retrieval map, remaining 39 are historical evidence, not unified-memory entries):

```text
GUIDELINES.md
evidence/INDEX.md
evidence/2026-10-05-batch-commit-autonomy/REFLECTION.md
evidence/2026-10-05-batch-commit-autonomy/REVIEW.md
evidence/2026-10-05-batch-commit-autonomy/SUMMARY.md
evidence/2026-10-05-batch-commit-autonomy/T001.md
evidence/2026-10-05-mandatory-initialization/REFLECTION.md
evidence/2026-10-05-mandatory-initialization/SUMMARY.md
evidence/2026-10-05-mandatory-initialization/T001.md
evidence/2026-10-05-mandatory-task-commits-implementation/CLOSEOUT.md
evidence/2026-10-05-mandatory-task-commits-implementation/REFLECTION.md
evidence/2026-10-05-mandatory-task-commits-implementation/RF001.md
evidence/2026-10-05-mandatory-task-commits-implementation/SUMMARY.md
evidence/2026-10-05-mandatory-task-commits-implementation/T001.md
evidence/2026-10-05-mandatory-task-commits-implementation/T002.md
evidence/2026-10-05-mandatory-task-commits-implementation/T003.md
evidence/2026-10-05-mandatory-task-commits-implementation/T004.md
evidence/2026-10-05-mandatory-task-commits-implementation/T005.md
evidence/2026-10-05-mandatory-task-commits-implementation/T006.md
evidence/2026-10-05-mandatory-task-commits-implementation/T007.md
evidence/2026-10-05-mandatory-task-commits-planning/REFLECTION.md
evidence/2026-10-05-mandatory-task-commits-planning/SUMMARY.md
evidence/2026-10-05-speckit-setup/REFLECTION.md
evidence/2026-10-05-speckit-setup/SUMMARY.md
evidence/2026-10-05-speckit-setup/T001.md
evidence/2026-10-06-active-planning-routing/SUMMARY.md
evidence/2026-10-06-batch-routing-implementation/SUMMARY.md
evidence/2026-10-06-batch-routing-planning/SUMMARY.md
evidence/2026-10-06-brief-current-state/SUMMARY.md
evidence/2026-10-06-coherence-adoption/SUMMARY.md
evidence/2026-10-06-coordinator-approval-cadence/SUMMARY.md
evidence/2026-10-06-one-file-evidence-contract/SUMMARY.md
evidence/2026-10-07-coordinator-dispatch-readiness/SUMMARY.md
evidence/2026-10-07-early-risk-reduction/SUMMARY.md
evidence/2026-10-07-task-verification-contracts/SUMMARY.md
evidence/2026-10-08-ephemeral-recovery-state/SUMMARY.md
evidence/2026-10-08-planner-commit-authority/SUMMARY.md
evidence/2026-10-08-planner-job-first/SUMMARY.md
evidence/2026-10-08-state-current-only/SUMMARY.md
evidence/2026-10-09-comparative-routing-learning/SUMMARY.md
evidence/planner-delegation-approval/SUMMARY.md
```

## Observable acceptance and smallest sufficient checks

These are future implementation criteria, not claims of implementation acceptance. Separate tasks must preserve each relevant criterion's pass condition, focused check/evidence and real gates as task-local REQUIRED items.

| ID | Pass condition | Smallest sufficient check / expected evidence |
| --- | --- | --- |
| A1 — Unified semantics | One project association/index admits both verified gotchas and explicit future guidance; whole-index-first, selective full reads and recheck-after-write remain. No active separate store discovery/read/create/maintain/propagate rule or equivalent renamed subsystem. | Inspect actual Memory Handling/index/consumer carrying spans and bounded active-reference scan; adapt existing memory/planner carrier tests. Positive custom-path/index cases pass; mutation restoring separate-owner intake fails. |
| A2 — Authority and safety | Clear future feedback writes only within authority; explanation/ordinary approval/agent failure or inference/no feedback writes nothing; ambiguity asks/no write, explicit no-write prevails. No automatic bookkeeping. Existing path/symlink/secrets/dirty/concurrent/ownership/checkpoint protections remain. | Adapt `python3 skills/memory-handling/scripts/test_coordination_contract.py` and relevant planner mutations. Positive unified authorized entry/index case and negative authority/bookkeeping/safety mutations pass with named diagnostics; actual instructions/diff inspected because symbolic fixtures are not a write engine. |
| A3 — Producers and closeout | All listed direct/managed/resumed consumers use unified guidance and carry relevant constraints to checks/briefs. Finish-session does not infer guidance; compact-memory retains legitimate guidance/provenance; Jev cannot grant authority. Planning/execution/model/task semantics otherwise unchanged, including ADR-0003/0004 outcomes. | Focused planner wiring/carrier tests plus manual before/after review of finish-session routing, compact-memory classes, Jev inheritance and coordinator seam. `python3 scripts/check-planner-workflow.py` and `python3 scripts/test-planner-workflow.py` pass after corresponding expectations converge; preserve unrelated assertions and config bytes. |
| A4 — Initialization | New adoption/approved refresh cannot seed a second guidelines system. Custom association/content, policy-only scope, existing approvals and safe no-op behavior survive; no implicit cleanup in unrelated adopted projects. | `python3 skills/initialize-coherence/scripts/test_contract.py` with authored new/refresh unified outputs, custom paths and preserved custom bytes. Mutation introducing separate-store setup/propagation fails. Positive policy-only preservation fixtures may contain inert old custom files without reading/maintaining them. |
| A5 — Guidance and history | Exact parent-turn guidance survives in this repository's unified memory with current-feedback provenance, without runtime work. All 41 specified legacy files and retired separate reference are removed only after approved disposition; still-required rules remain in existing owners; historical approvals/links remain retrievable at precise Git revision/path. | Compare inventory to actual deletion diff; verify preserved quote byte-for-byte and relevant owner coverage. Validate changed live references/anchors and each pinned historical target using `git cat-file -e <revision>:<path>` (and referenced sections as applicable). No dangling changed target, wholesale archive/move or reflection promotion. |
| A6 — Delivery bounds | Only memory-related operative docs/governance/tests change; no new runtime/framework/issue system or altered stages, task formats, approvals, model assignments/executor. Global activation uses fresh-session handoff in Paseo, fresh checkout/capability verification, no automatic reload/restart or owner reload command. | Inspect explicit owned-path diffs and changed links; run `git diff --check`. Use existing task-checkpoint checks when its owner changes: `python3 scripts/check-task-commit-contract.py` and `python3 scripts/test-task-commit-contract.py`. Existing `bash scripts/check-skills-lint.sh` is integration regression, not a new admission ceremony; report any unrelated failure honestly. |

Use `PYTHONDONTWRITEBYTECODE=1` for local Python checks. Existing helper tests and bounded temporary-filesystem/Git fixtures are sufficient for this known instruction/fixture seam. No consequential dependency/API unknown requires internet research, new dependency guidance, disposable prototype or live/provider/runtime investigation. Reuse inspected repository contracts and actual local helper commands; no dependency versions change. Static checks establish carrier sensitivity and authored fixture outcomes, **not model obedience, live runtime behavior or parent-wakeup delivery**. Validate changed references, not an unrelated repository-wide audit. Rerun only checks invalidated by subsequent edits.

No material product question remains for source preparation. Combined owner approval must explicitly cover the historical removal/revision-reference disposition, unified guidance preservation and memory-related constitutional alignment. New conflicting guidance/provenance/ownership evidence returns only the affected mapping to owner dialogue; it is not automatic deletion permission.

## Downstream planning and activation boundary

Future task production reads the actual selected executor **`.pi/workflow-executor.json`** before decomposition: currently Terra/medium workers and Sol 6.1/medium fresh reviewers. Carry that exact path unchanged; this source's saved `tinyspec-source` assignment (`openai-codex/gpt-6.1-sol`, medium) is not an implementation assignment. Expect multiple bounded independently testable outcomes sized for that executor, not one bundled milestone; do not author tasks in this source. Contract/consumer agreement must precede relying on unified behavior, and provenance resolution precedes historical deletion, without inventing a prototype/report/cleanup artifact chain.

Parent inspects this source/checkpoint before separate task generation. Planning remains planning-only through combined approval unless the owner explicitly changes that scope. Later global skill activation in Paseo needs a fresh-session handoff: the fresh agent verifies checkout/revision, current approvals, loaded skills and usable required capabilities before launching approved work. Do not install, push, reload or restart automatically; do not tell the Paseo owner to execute a reload slash command.
