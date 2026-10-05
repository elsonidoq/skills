# Project coordination memory — implementation tasks

## Authority and execution boundaries

Direct-adapter tasks derived from [TinySpec source](project-coordination-memory.md), canonical path `docs/plans/project-coordination-memory.md`, SHA-256 `1a51f7888d7b90e4a655981965f0c926468c181a8a43ab00bcccf73c0697acb9`. Source acceptance A1–A12 and its inspected authorities govern these tasks. The owner selected TinySpec and `openai-codex/gpt-6.1-sol` for sonnet-class **preparation**, not implementation. These tasks are prepared, not approved. Parent owns source/task review and current-content combined approval.

Future execution requires coordinator provenance/authorization and capability preflight, owner-selected usable implementation and independent-review bindings, preserved workspace changes, and current approved source/task content. Implementation model selection is not inferred from preparation. All seven tasks are bounded sonnet-class; opus-class share is 0/7 (0%). Per-task commits and sequential execution remain coordinator requirements after implementation authorization; this preparation creates no commits.

Before each write, re-read targets and preserve unrelated content; stop on concurrent or unapproved overlap. Preserve existing untracked `.pi/`, `.specify/`, and prepared planning artifacts. No actual project store is initialized by these tasks. Generic support, templates and labelled fictional fixtures are distinct from separately approved adoption in a target project. No mandatory migration or new optional-memory blocker is authorized; existing required gotcha-memory gates survive.

**Excluded:** ML, bandits, embeddings, scoring/retention frameworks, automatic optimization, synthetic model benchmarks, global/cross-project stores, concrete model policy, unbounded guideline growth, automatic guideline mutation, bulk history reads, parallel implementation batches, unrelated skill changes, legacy-port changes, dependency installation, paid/live/provider/model/end-to-end SpecKit runs, push/deploy or external messaging. Separately authorized live evidence is required to prove model adherence; offline checks must not claim it. No helper/engine may be added merely to make fixtures executable.

## Tasks

### Shared contract and planning consumers

- [x] T001 [Coordination contract] Establish optional coordination discovery and two-store persistence rules.
  - **Depends**: none.
  - **Prerequisites**: future execution preflight above; read source Association and the two knowledge layers, Retrieval and planning integration, repository policy, memory-handling and existing gotcha-memory association/write rules.
  - **Outcome**: extend memory-handling through one shared portable reference, keeping compact synthesized coordination guidelines separate from gotcha entries and factual execution evidence.
  - **Files/interfaces**: `skills/memory-handling/SKILL.md`; new `skills/memory-handling/references/project-coordination.md`. Consumers use a resolvable relative link to this canonical contract. No project-store or association writes.
  - **Acceptance**: compare carrying sections to source: explicit association from project instructions/configuration; declared equivalent layouts respected; proposed new layout only after bounded owner approval; undeclared optional memory means no writes/no invented knowledge/existing behavior; declared missing/unreadable content reported distinctly from required gotcha-memory failures. Document `GUIDELINES.md`, `evidence/INDEX.md`, unique safe run ID with resume reuse, separate `SUMMARY.md`/task Markdown/`REFLECTION.md`, qualitative scoped guidance and evidence pointers, unknown outcomes and distinguishable attempts, bounded logs and sensitive-data exclusion. Record precedes compact single-row-per-run index refresh; resume reconciles interrupted record/index updates without erasing prior runs. Historical retrieval starts with index, opens only relevant records for justified clarification/synthesis, and retains uncertainty on no match. Ordinary planning reads guidelines, not index/history. Shared contract also defines conservative reflection and the explicit approval/current-content boundary consumed in T004; no substitute workflow.
  - **Source acceptance**: A1–A10 (shared producer); Approach and persistence contract.
  - **Required verification**: manual clause/layout mapping and relative-link resolution; focused checker baseline before consumers. Check actual write and discovery language for global fallback, guessed association, automatic setup or ledger writes into gotcha memory. Expected effort is local Markdown review and existing static checks; no persistence engine or live model test needed.
  - **Capabilities**: bounded local read/edit/write/search, Markdown/diff review, Python 3 for available static checks.
  - **Model class**: sonnet-class.
  - **Rationale**: settled portable format and retrieval/write constraints are independently comparable to the source.

- [x] T002 [Planning integration] Consume compact guidance before choice and propagate it through both task adapters.
  - **Depends**: T001.
  - **Prerequisites**: verified canonical coordination contract and links; read planner discovery/preselection/handoff, TinySpec inputs/source, shared task-generation and Standard stage contracts together.
  - **Outcome**: associated guidance reaches assessment before Planner → Choose, both selected source routes, task decomposition/checkpoints/verification and coordinator briefs without default history intake or changes to owner depth selection.
  - **Files/interfaces**: targeted sections of `skills/planner/SKILL.md`, `skills/tiny-spec/SKILL.md`, `skills/task-generation/SKILL.md`; canonical reference links and stage handoffs. Standard uses existing planner/SpecKit handoff and shared task adapter; no new helper or Standard workflow.
  - **Acceptance**: inspect stage placement and handoff showing exact applicable guideline constraints/evidence references carried into observables, task dependencies and required verification; direct TinySpec/task entry follows the same discovery boundary rather than assuming planner invocation. No-memory path stays read-only and unchanged; required gotcha memory retains its distinct stops. Planner does not automatically read evidence index/history and cannot turn raw outcomes into instructions or let memory override source/owner authority. Clarifying tentative/conflicting guidance follows T001 selective retrieval. Owner still selects TinySpec or Standard; preselection creates no files. Optional residual-reasoning notes do not require migration or alter class/share/approval rules.
  - **Source acceptance**: A1, A2, A10, A11 (planning notes), A12.
  - **Required verification**: focused before-choice and downstream-constraint walkthrough with a labelled fictional heuristic/manual-checkpoint guideline; no-store walkthrough; resolve shared links; compare existing route/approval/task rules to baseline. Run existing planner and task-generation contract checks. Expected effort is bounded wiring review; static checks cannot prove model obedience or real SpecKit execution.
  - **Capabilities**: bounded local editing/search, Python 3 and link/stage/diff inspection.
  - **Model class**: sonnet-class.
  - **Rationale**: localized consumer hooks against T001, with established workflow stages unchanged.

### Coordinator checkpoints and reflection

- [x] T003 [Execution evidence and routing] Record task/run outcomes and preserve safe real-work delegation experiments.
  - **Depends**: T001, T002.
  - **Prerequisites**: canonical store contract, applicable planning handoff, coordinator checkpoint/retry/class-selection baseline and execution-freeze marker inspected. Verify associated evidence write authority before future project writes.
  - **Outcome**: coordinator records attributable attempts/checks/manual observations in separate run/task files and maintains a compact index at existing checkpoints, including failures/partial work; optional residual reasoning informs class-compatible owner-selected routing without new model taxonomy.
  - **Files/interfaces**: `skills/coordinate-implementation/SKILL.md` load/preflight, capability selection, briefs and task checkpoints; `skills/memory-handling/references/project-coordination.md` routing details if needed; `scripts/check-planner-workflow.py` execution digest **only for reviewed authorized coordinator additions**. Preserve all existing checker safety assertions; T004 will refresh the digest for its own additional changes.
  - **Acceptance**: evidence includes task/type, areas/tags, optional low/medium/high rationale, approved class, capability role, observed model/effort or unknown, attempt outcomes, checks/reviewer findings, failure cause/retries/escalation, surprises and manual findings. Reuse safe existing run ID or retain a unique safe ID; resume retains attempts and correct index row. Record-before-index and interrupted-write reconciliation are explicit. No association/write authority means observations remain in existing handoff with optional setup proposal, not silently created stores. Low favors cheaper compatible selected option; medium requires strong executable oracle plus stronger verification/review; high favors stronger compatible reasoning without forced opus reclassification/share bypass. Failure requires inspected child/invocation, preserved valid/unrelated work, authorized failed-task isolation/restore if supported, verified stronger capability and owner selection; unknown cause/state/capability stops. Record both outcomes without permanent rule after one failure. No concrete provider/model policy added to skills.
  - **Source acceptance**: A3–A5, A11, A12.
  - **Required verification**: clause-level evidence and routing walkthrough, including failed/partial/unknown/manual and absent-store cases; inspect coordinator diff against frozen baseline and update digest only after preserving sequential batches, task commits, owner class selection, inspected retries and fresh final review. Run planner checker and coordinator intake/batching checks. Expected effort is local contract/check review, not paid model experimentation or real project writes.
  - **Capabilities**: bounded local edits/search, Python 3, hash/diff inspection; future project writes and delegation are subject to coordinator preflight, not exercised by this task.
  - **Model class**: sonnet-class.
  - **Rationale**: existing checkpoints and capability gates supply bounded seams; experiment behavior is fully specified.

- [x] T004 [Reflection and approval] Add conservative closeout proposals and approval-controlled guideline mutation.
  - **Depends**: T001, T002, T003.
  - **Prerequisites**: verified evidence/index producer and current guideline discovery; read existing executive-brief/current-content approval and coordinator final-review/finish boundaries.
  - **Outcome**: after verification and independent review, or at a blocked pause, coordinator reflects on useful project-specific lessons, records evidence separately and offers exact scoped guideline changes for accept/edit/reject/add through existing question interaction.
  - **Files/interfaces**: `skills/coordinate-implementation/SKILL.md` reflection/finish and relevant approval handoff; canonical `skills/memory-handling/references/project-coordination.md` approval procedure; `scripts/check-planner-workflow.py` deliberate coordinator digest refresh. No unrelated approval skill rewrite or project guideline writes.
  - **Acceptance**: carrying phase asks all nine source reflection questions, separating reusable/incidental, project/general, reinforcement/contradiction, delegation/manual surprises and evidence sufficiency. Direct observation, tentative/repeated pattern, stable guidance, insufficient and conflicting evidence stay distinguishable without numerical scoring. Write attributable evidence/update index separately from `REFLECTION.md` candidate add/refine/supersede/remove/evidence-only; include supporting/contrary pointers and no-update outcome. Present executive brief plus exact candidate diff before `ask_user`; implementation approval grants no guideline authority. Explicit accepted/edited/added **resulting content** and comparable baseline/decision evidence are recorded; reject preserves guideline bytes while keeping evidence/disposition. Pending, unavailable, cancelled and ambiguous answers mutate no guidelines. Re-read baseline immediately before approved bounded application; concurrent drift stops overwrite and requires renewed approval. Re-check relevant guidance after writes. Optional memory approval pending/rejected is reported separately from implementation/feature acceptance.
  - **Source acceptance**: A6–A9, A10 (synthesis retrieval), A11 (no single-outcome permanent rules), A12.
  - **Required verification**: manual decision-state walkthrough for accept/edit/add/reject/pending/unavailable/cancelled/ambiguous and concurrent drift; inspect actual mutation authority and phase order, not just keywords. Re-run planner and coordinator preservation checks and review the refreshed execution digest against only authorized additions. Expected effort is bounded lifecycle/approval review; no real owner interaction is simulated as production approval.
  - **Capabilities**: local bounded edits/search, Python 3, Markdown/phase/diff/hash review.
  - **Model class**: sonnet-class.
  - **Rationale**: finite explicit approval transitions and conservative reflection criteria require no architecture invention.

### Focused assurance and documentation

- [x] T005 [Deterministic assurance] Add source-derived contract/mutation checks and clearly simulated lifecycle fixtures.
  - **Depends**: T001, T002, T003, T004.
  - **Prerequisites**: verified integrated operational carriers; inspect existing checker section/stage loaders, mutation patterns and coordinator/task tests; identify actual changed seam before adding cases.
  - **Outcome**: focused offline tests detect missing early retrieval, selective-reading/evidence boundaries, unsafe approval/mutation or routing changes and lost existing safeguards; finite temporary-project fixtures demonstrate the specified persistence layout and decision lifecycle without claiming to execute skill instructions.
  - **Files/interfaces**: `scripts/check-planner-workflow.py`, `scripts/test-planner-workflow.py`; focused `skills/memory-handling/scripts/test_coordination_contract.py` and/or bounded `scripts/fixtures/planner/` fixtures as needed; existing coordinator/task contract tests only where the affected assertions require extension. No broad new test infrastructure.
  - **Acceptance**: A1–A12 map to named positives and meaningful rejections. Test associated/no-memory distinction, before-choice/downstream propagation, two runs/multiple separate task files, failed/partial/manual/unknown attempts, new/resumed rows without duplicates and interrupted-index repair, reflection evidence-only/tentative/contrary/no-update cases, pending/unavailable/cancelled/ambiguous no-write states, explicit accepted/edited/added content, rejection byte identity, baseline-drift refusal, index-first relevant-only reads with unrelated records unread/no-match uncertainty, class-compatible optional routing and both attempts without permanent provider rules. Instruction-removal/unsafe-clause mutations must fail specific diagnostics for missing carrying stage/link, late/bulk reads, silent mutation, missing current-content/selection/inspected-failure boundaries and lost existing safety clauses even if summary keywords remain. Preserve execution freeze with reviewed additions and existing negative tests; do not weaken checks to obtain PASS. Label filesystem fixtures simulated contract examples, not production approval/persistence/model/SpecKit execution. If implementation genuinely introduces a persistence helper, test it directly instead of maintaining a duplicate fixture implementation; do not invent such a helper for testing alone.
  - **Source acceptance**: A1–A12.
  - **Required verification**: run new focused test command and existing planner/coordinator/task checks; record named positive/rejection results and demonstrate a missing-boundary mutation fails. Lowest sufficient layer is static instruction wiring plus small temporary-file examples; no exhaustive infrastructure, synthetic benchmark or live run. Report limitations honestly.
  - **Capabilities**: Python 3, local test edits, temporary directories, in-memory/isolated mutations, bounded shell/log inspection.
  - **Model class**: sonnet-class.
  - **Rationale**: finite source-derived cases reuse existing checker/fixture patterns; broader behavioral evidence is explicitly separate.

- [x] T006 [Lockstep documentation] Document optional adoption, selective access and reviewed feedback lifecycle.
  - **Depends**: T001, T002, T003, T004, T005.
  - **Prerequisites**: implemented contracts and actual named test results; re-read documentation routing, requirements memory/model sections, README flow and regression guide before edits.
  - **Outcome**: users can discover generic coordination support, propose an explicitly approved project association and understand compact guidance versus indexed evidence, no-memory fallback, conservative routing/reflection and verification limits.
  - **Files/interfaces**: bounded updates to `README.md`, `REQUIREMENTS.md`, `docs/index.md`, `docs/plans/planner-regression.md`; links to canonical shared contract and prepared source/tasks. No AGENTS/adoption skill or actual project-store initialization is presumed authorized.
  - **Acceptance**: documentation describes guidelines before choice, selective history only on justified triggers, separate per-run/task records and compact index, explicit setup/write bounds, accept/edit/reject/add with byte-preserving rejection/current-content protection and no automatic mutation. Retain two model classes and runtime requirements, distinguish optional coordination absence from required gotcha-memory gates, preserve this repository's no-adoption declaration. Examples are portable and fictional; motivating heuristic/manual checkpoint is not a global mandate or real evidence. Compare statements and invocations to actual operational sections/test results, distinguish static/simulated PASS from NOT RUN real model/SpecKit behavior, and advise `/reload` after global skill changes. All added links resolve.
  - **Source acceptance**: A1, A2, A4–A12 (discoverability and evidence limits).
  - **Required verification**: targeted Markdown link and documentation-to-contract/test comparison; no repository-wide historical rewrite. Expected effort is small lockstep edits after behavior/test producers, not another planning framework.
  - **Capabilities**: local bounded editing/search, link/diff/test-output inspection.
  - **Model class**: sonnet-class.
  - **Rationale**: documentation follows verified producer contracts and finite test outcomes.

### Integration reconciliation

- [x] T007 [Integration acceptance] Reconcile all source criteria and preserved execution gates.
  - **Depends**: T001, T002, T003, T004, T005, T006.
  - **Prerequisites**: current approved source/tasks and producer check evidence; no unresolved material scope/authorization drift. Coordinator fresh independent final review remains separate and required, not replaced by this implementer check.
  - **Outcome**: attributable A1–A12 acceptance packet in existing task/execution conventions, with only demonstrated in-scope integration defects repaired and material changes returned through existing gates.
  - **Files/interfaces**: integrated changed contracts/tests/docs and existing execution evidence/task status; no new mandatory tracker or project memory store.
  - **Acceptance**: inspect attributable tracked/untracked changes, canonical links and A1–A12 coverage. Run required new coordination test plus `python3 scripts/check-planner-workflow.py`, `python3 scripts/test-planner-workflow.py`, `python3 skills/coordinate-implementation/scripts/test_intake_contract.py`, `python3 skills/coordinate-implementation/scripts/test_batching_contract.py`, `python3 skills/task-generation/scripts/test_contract.py`, `python3 skills/task-generation/scripts/test_check_task_order.py`, `python3 skills/task-generation/scripts/check-task-order.py docs/plans/project-coordination-memory-tasks.md`, `bash scripts/check-skills-lint.sh`, and `git diff --check`. Record actual commands/results and unavailable checks, with Python bytecode disabled when appropriate. Manually inspect early-read/handoff wiring, partial/index/approval lifecycle, uncertainty and class-compatible routing; confirm TinySpec/direct and Standard/SpecKit/legacy approval routes, task order/class share, sequential batches, inspected retry, task commits and independent review remain intact. Verify coordinator digest changes match approved additions rather than erased safeguards. Distinguish local static/simulated evidence from live model/real SpecKit NOT RUN; do not claim instruction compliance proven. Record residual risks and next review action; advise `/reload`. Feature acceptance is coordinator-owned, never inferred from this task's checkbox.
  - **Source acceptance**: A1–A12 and all exclusions/preservation constraints.
  - **Required verification**: focused aggregate commands above plus source → carrier → named positive/rejection case mapping and bounded manual diff review. Repair only concrete changed-seam failures; unrelated recovery work needs separate authority. No live/provider permissions inferred.
  - **Capabilities**: local Python 3/shell/search/diff/lint/link checks; independent reviewer capability is separately coordinator-verified.
  - **Model class**: sonnet-class.
  - **Rationale**: finite integration checks consume prior producers; no new design or live experiment.

## Traceability and coherent execution context

| Source criterion | Implementing tasks | Verification consumer |
| --- | --- | --- |
| A1 early associated guidelines and downstream constraints | T001, T002 | T005 early-read/link/removal checks; T007 walkthrough |
| A2 optional no-memory compatibility, required gotcha distinction | T001, T002, T003 | T005 no-association/no-write checks; T006 docs; T007 |
| A3 attributable checkpoint evidence | T001, T003 | T005 failed/partial/manual/unknown fixtures; T007 |
| A4 separate run/task history | T001, T003 | T005 two-run/multi-task fixture; T006 docs; T007 |
| A5 compact index new/resume/interruption maintenance | T001, T003 | T005 unique-row/repair cases; T007 |
| A6 conservative reflection and evidence-only uncertainty | T001, T004 | T005 tentative/contradictory/no-update cases; T007 |
| A7 no mutation before explicit memory approval | T001, T004 | T005 pending/unavailable/cancel/ambiguity negatives; T007 |
| A8 approved exact edits/additions and drift safeguards | T001, T004 | T005 accept/edit/add/drift cases; T007 |
| A9 rejected proposals preserve guidelines | T001, T004 | T005 byte-identity plus retained evidence/disposition; T007 |
| A10 selective index-first historical retrieval | T001, T002, T004 | T005 selected-read/no-match/bulk-read rejection; T007 |
| A11 cautious real-work routing and recorded attempts | T001–T004 | T005 class/failure/single-outcome mutations; T007 |
| A12 existing workflow and execution safeguards | T002–T004 | T005 preserved/mutated safety checks; T007 regressions |

All tasks are one consecutive sonnet-class sequence. T001 owns discovery/storage/approval protocol before consumers; T002 provides early-read and downstream handoff before T003–T004 coordinator use; T003 supplies evidence/index producers before T004 reflection; T005 consumes all operational contracts, T006 documents actual behavior/tests and T007 reconciles integration. No distant work is reordered or padded and no implicit forward producer is needed. Shared context is source A1–A12, canonical coordination reference, existing stage/approval contracts and checker safety baseline. Verify each task before releasing its consumer. Useful checkpoints are T001 store/write mapping, T002 before-choice propagation, T003 record/index/routing boundaries, T004 decision/current-content lifecycle, T005 named rejections and T006 doc truth/link review. Coordinator alone decides sequential batch boundaries from observed context, class and owner gates; task phases, shared files and internal dependencies do not require split sessions.

## Preparation findings

Task-generation contract, source, existing repository task format and validator were read in full. Relevant planner, TinySpec, memory-handling, coordinator, approval/recovery, dependency-research, SDD, requirements, repository policy, documentation-routing and checker contracts were inspected. No declared project-memory association exists here, so no project knowledge is invented or initialized. No new dependency or external research is required. Source digest matches the source producer report. Preparation writes only this task artifact; no implementation, test/skill/global edits, commits or staged files. Parent combined review/approval and coordinator execution preflight remain pending.

Preparation task-order and whitespace validation results are recorded in the separate runtime report. Those checks establish task-format/order consistency, not feature acceptance. Residual risks: natural-language adherence and genuine SpecKit behavior require authorized live evidence; simulated filesystem examples cannot prove production mutation or approval. Index growth and evidence quality remain operational concerns addressed through short rows, selective reads and conservative synthesis, not a retention/scoring framework.
