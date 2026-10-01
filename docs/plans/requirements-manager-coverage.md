# Requirements Manager source-derived coverage baseline

**Final-review status: FR1–FR3 and second corrections are committed; T012 recheck remains pending.** The initial `verified` cells meant initial static checks only and did not resolve the NOT_READY review. Second corrections address A1 (section-local static/mutation coverage), A2 (constitution repair/verification), A3 (new authorized fresh-small routing), A4 (historical helper integration), A5 (truthful tracker state), and A6 (preexisting sizing duplication). The rows remain `verified` only for named deterministic prompt-contract checks, not semantic acceptance, arbitrary natural-language completeness, or runtime behavior. See preserved historical [findings](reviews/requirements-manager-final-semantic-review.md), [Astra review](reviews/requirements-manager-astra-suite-review.md), and [Sol recheck](reviews/requirements-manager-sol-final-recheck.md).

**Derivation order:** This matrix was drafted before replacement-skill text. It derives
requirements from the owner-approved [design](requirements-manager.md), the revision-4
[tasks](requirements-manager-tasks.md), historical `epics-manager` at
`32e12feb382a6a0acb7e9d7f2e82559e3d397f2e:skills/epics-manager/SKILL.md`, and
pre-change protections at `fa41d5f3f5aeb7ddfa9963222eff2c0447533059` (current
`epics-manager`, `coordinate-implementation`, and `create-epic`). Supporting sources
were `REQUIREMENTS.md`, `docs/best_practices_spec_driven_development.md`, and the
existing task-order checker and units under `skills/epics-manager/scripts/`.

Status meanings: **preserved** remains required; **changed-deliberate** is an
owner-approved replacement; **removed-deliberate** must not be restored;
**removed-unaccounted** would block completion. Evidence is **planned** until the named
check is run by its implementing task, **verified** only with recorded output, or
**missing**.

| ID | Source citation | Required behavior | Carrying stage/rule | Status | Rationale | Task IDs | Check/test IDs | Evidence status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| B01 | historical `Pipeline`, `brainstorm_gate` | Gate emits exact `NO_BRAINSTORM_NEEDED` or `BRAINSTORM_NEEDED`; bias to skip settled/bounded work | shared brainstorming gate | preserved | historical mechanism | T002,T004,T007,T009 | workflow gate contracts | verified |
| B02 | historical `epic_brainstorm`, owner design `Shared brainstorming primitive` | At most three agenda items with concrete options/recommendation; material owner dialogue one item at a time | shared brainstorming | preserved | no generic substitute | T002,T004,T007,T009 | workflow agenda contracts | verified |
| B03 | historical `epic_brainstorm_fix` | Apply exactly approved decisions only to the bounded selected source; retain deferrals | decision application | preserved | prevents scope invention | T002,T004,T007,T009 | workflow decision-application contracts | verified |
| B04 | historical `Interrupted-brainstorm recovery`, `Handoff context protocol` | Durable agenda/answers, deferrals, concise handoff, and resumption | shared brainstorming | preserved | interruption safety | T002,T004,T007,T009 | workflow resume contracts | verified |
| B05 | historical `Reading and source contract` | Read selected source, settled constraints, cited sources, instructions/principles; do not re-derive settled facts | manager source contract | preserved | provenance | T004,T007,T009 | workflow source contracts | verified |
| B06 | historical `spec_create`; pre-change EPIC `Workflow` steps 1–5 | EPIC retains SpecKit preflight, constitution/principles, source readiness, specification creation and explicit current spec approval | EPIC `spec_create` checkpoint | preserved | EPIC safeguards | T004,T009 | workflow EPIC contracts | verified |
| B07 | historical `plan_create`; owner design `EPIC Manager` | One opus-class pass reviews/fixes spec and creates plan; material planning changes renew spec approval | EPIC `plan_create` | changed-deliberate | current approvals replace old state machinery | T004,T009,T010 | operational/mutation contracts | verified |
| B08 | historical `tasks_create`; pre-change EPIC `Workflow` step 7 | Task creation is create-only; task corrections belong to overall review | EPIC `tasks_create` | preserved | stage ownership | T004,T009,T010 | operational/mutation contracts | verified |
| B09 | historical `overall_review`; pre-change EPIC `Workflow` steps 8–10 | Independent observed reviewer reviews artifacts; required current approvals/evidence before fresh handoff | EPIC `overall_review` | preserved | approval/provenance safety | T004,T009,T010 | workflow approval contracts | verified |
| B10 | historical `Flagged-item protocol` | Flag only material friction/spec deviation; never flag task ordering/files/batches/internal fixes; resolve single-option mechanics | manager decision rule | preserved | owner-gate discipline | T004,T009 | workflow flagged-item contracts | verified |
| B11 | historical `Flagged-item protocol`, `Handoff context protocol` | Capture decisions/deferrals and same-session correction after owner override | manager correction/resume | preserved | durable context | T004,T009 | workflow recovery contracts | verified |
| B12 | historical `done`; pre-change EPIC `State and Resume` | Validate artifacts/content/links and stale approvals on resume; report readiness, not feature acceptance | EPIC `done`/resume | preserved | no label-only completion | T004,T009 | workflow resume contracts | verified |
| B13 | historical fixed stages/classes; owner design `EPIC Manager` | Canonical executable order: gate → optional brainstorm/fix → spec → plan → tasks → review → done; gate/fix/spec/tasks sonnet-class, plan opus-class | EPIC stages | changed-deliberate | class names portable; no named bindings | T004,T009,T010 | order/class contracts | verified |
| B14 | pre-change EPIC `Required SpecKit Capabilities`; owner design | Detect installed SpecKit stage capabilities/instructions and stop safely when required EPIC capability is absent | EPIC preflight/wrappers | preserved | no simulated tooling | T004,T009 | capability contracts | verified |
| B15 | pre-change `create-epic` `Sizing`; best-practices `Epic Sizing` | Use existing sizing evidence; route choice is owner-gated on substantive scope change; retain documentation-init exception | both managers | preserved | no sizing redesign | T004,T007,T009 | workflow sizing contracts | verified |
| B16 | pre-change EPIC `Workflow` tasks/review; checker/tests | Shared task contract: outcome, prerequisites, files/interfaces, evidence, capabilities, class/rationale, docs/integration/acceptance coverage | task-generation | preserved | task quality | T003,T009 | task-order units + contracts | verified |
| B17 | pre-change EPIC `Workflow` tasks/review; checker/tests | Consecutive T001 IDs, only earlier dependencies, contiguous stories/setup, plus manual implicit-dependency/stage-feasibility review | task-generation validator | preserved | safe order | T003,T009,T010 | `check-task-order.py` units | verified |
| B18 | owner design `Shared task-generation contract` | sonnet-class default; opus-class only non-decomposable work; <=30% unless recorded owner exception; discover local format then Markdown fallback | task-generation | preserved | bounded delegation | T003,T009 | task contracts | verified |
| B19 | pre-change coordinator `Load and Verify` | EPIC origin still requires spec, plan, both current approvals, review evidence, provenance; ambiguous origin blocks | coordinator intake | preserved | no safeguard downgrade | T006,T009,T010 | intake contracts | verified |
| B20 | owner design `Requirements Manager`, `Origin-neutral execution boundary` | Direct requirement/source + tasks + current review/approval works without plan/SpecKit; no fabricated artifacts | requirements intake | changed-deliberate | approved lightweight route | T006,T007,T009,T010 | direct-input contracts | verified |
| B21 | pre-change coordinator `Execution Capability Preflight`; `REQUIREMENTS.md` Runtime/model mapping | Check usable question/delegation and owner-selected class bindings; stop/report unavailable, do not silently switch | capability preflight | preserved | runtime safety | T004,T006,T007,T009 | capability contracts | verified |
| B22 | owner design `Execution strategy` | Complete implementation count excludes standalone reviews: <=3 may be local only if class/context fit; >3 delegates; resume retains strategy absent scope/safety evidence | coordinator selection | changed-deliberate | replaces mandatory delegation | T006,T009,T010 | threshold contracts | verified |
| B23 | pre-change coordinator `Build the Execution Graph`; owner design `Execution strategy` | One dependency-preserving graph; sequence producers before consumers; defects return to producer review; never reorder to fill batches | coordinator graph | preserved | safe integration | T005,T006,T009,T010 | graph/mutation contracts | verified |
| B24 | pre-change coordinator batching; owner design `Execution strategy` | Consecutive homogeneous batches amortize startup/context; internal dependencies/shared files/headings may remain together after producer checks; target 5–7 only when safe | shared batching | changed-deliberate | replaces isolation-first splits | T005,T009,T010 | batching scenarios/mutations | verified |
| B25 | owner design `Execution strategy` | Split only for evidenced class/gate/context/incompatible scope/external integration boundary; no parallel implementation batches; async-only delegation | batching/session rule | changed-deliberate | owner-selected safety boundary | T005,T006,T009,T010 | batching contracts | verified |
| B26 | owner design `Execution strategy`; pre-change coordinator `Select Execution Capability` | Reuse only matching useful retained context with observed headroom; hand off/rotate conservatively; inspect failures before retry | session rule | changed-deliberate | replaces forced per-class reuse | T005,T006,T009 | session contracts | verified |
| B27 | owner design `Execution strategy` | Verify and commit every implementation task separately; no per-task review; one fresh independent final review of full committed range | execution/review | changed-deliberate | replaces batch commits | T006,T009,T010 | commit/review contracts | verified |
| B28 | owner design `Requirements Manager` | Capture durable requirement scope, acceptance criteria, exclusions, constraints, sources, decisions; review traceability and current approval before coordinator handoff | requirements manager | preserved | plan-free is not evidence-free | T007,T009 | requirements contracts | verified |
| B29 | owner design `Regression strategy` | Deterministic operational and in-memory mutation checks are routine validation; static checks do not prove model obedience | verification | preserved | explicit limitation | T009,T010,T011 | workflow/mutation entry point | verified |
| B30 | historical runtime/state sections; owner design exclusions | Do not restore obsolete platform paths/tools, rigid resolver/state schema, named agents/provider IDs, or speculative material defaults | portability/exclusions | removed-deliberate | global portability/current owner gates | T002,T004,T007,T008,T009,T010 | lint + legacy mutations | verified |

## Historical behavior inventory

The historical source also requires: gate assessment; optional orchestrator-owned
brainstorm; exact owner-decision application; the reading/source contract; spec creation;
combined plan spec-review/create/fix; create-only tasking; one overall review; flagged-item
categories and never-flag list; single-option mechanical resolution; owner dialogue and
decision capture; same-session correction; deferrals; handoff context; interrupted-stage
recovery; a done report; and fixed stage classes. B01–B13 account for each. Current owner
gates supersede historical speculative material defaults (B07, B10, B15, B30), rather than
removing the protections.

## Capability and fallback inventory

| Capability | Source | Required fallback/stop | Carrying IDs | Evidence |
| --- | --- | --- | --- | --- |
| SpecKit constitution/specification/clarification/planning/tasks/analysis | pre-change EPIC `Required SpecKit Capabilities` | report `UNAVAILABLE` and stop at affected EPIC stage; never simulate/install | B14 | verified |
| Question and delegation tools | `REQUIREMENTS.md` Runtime; pre-change coordinator preflight | verify usable; report unavailable; owner dialogue fallback only where specified; do not invent a tool | B21 | verified |
| Owner class/model binding | `REQUIREMENTS.md` Model class mapping; owner-approved tasks provenance | verify usable binding and obtain/retain owner selection; no provider/model IDs in skills | B13,B21 | verified |
| Applicable memory and principles | `REQUIREMENTS.md` Memory; pre-change manager inputs/preflight | use documented memory contract; read detected principles; do not invent policy | B05,B06,B21 | verified |
| Independent reviewer | pre-change EPIC overall review; owner design | use observed permitted independent reviewer; unavailable reviewer blocks approval/final review | B09,B27 | verified |
| Context/session observation | owner design `Execution strategy` | record unavailable metrics and narrow/rotate conservatively; no forced reuse | B26 | verified |

## Deliberate changes and omissions watchlist

- Mandatory delegation is replaced by B22's bounded local-or-delegated selection.
- Isolation-first story/file batching and per-batch commits are replaced by B24–B27's
  context-continuity, separate-task-commit policy.
- Obsolete platform-specific tools/paths, resolver and JSON state schema, named agents,
  provider IDs, and historical speculative defaults are deliberately excluded (B30).
- A1–A6 dispositions are recorded in the execution tracker. Static predicates are deliberately
  bounded: they do not establish exhaustive semantic coverage, model obedience, or live workflow
  success. Any later source behavior not mapped above is a blocker rather than silently accepted.

## Baseline checks

Before this artifact was written: suite lint passed (21 skills), the original five
`check-task-order` unit tests passed, task ordering passed for the approved task artifact,
and `git diff --check` passed. These validate the pre-change baseline only.

## T011 integration evidence

Initial matrix evidence was static and was insufficient for semantic readiness. After FR1–FR2,
B05–B07, B09–B11, B15, B20–B21, B29–B30 are covered by focused contract checks and the
operational checker/mutations; B17 also has a T001-first validator unit. `verified` means only
that the named deterministic prompt-contract checks passed; it does not claim a live model,
question tool, delegation, SpecKit, or reviewer obeyed it.

| Scenario group | Outcome | Evidence / limitation |
| --- | --- | --- |
| Settled and ambiguous requirement; lightweight sizing; documentation-init EPIC exception | PASS (static) | Requirements-manager and create-epic contracts require durable source, shared gate, owner route decision, and preserve the exception. No owner dialogue was run. |
| Three suitable local tasks; four tasks and resume with three remaining | PASS (static) | Coordinator contract checker requires full-list count, class/context suitability, and retained delegation strategy. No runtime scheduling occurred. |
| Context-heavy work, rotation/resumption unavailable, inspected failure | PASS (static) | Coordinator contract requires observed headroom, conservative handoff/rotation, and inspected failures. Context metrics and child resumption were unavailable. |
| Coherent shared-file work across headings; genuine class/gate/context splits | PASS (static) | Batching checker and named mutations require continuity and evidenced splits without reorder. No delegated batch ran. |
| Commit-policy conflict; stale/ambiguous approval; edited resume; forward dependencies | PASS (static) | Coordinator/task-order contracts require owner resolution or producing-gate return and reject invalid order. No conflicting project policy was encountered. |
| No SpecKit and installed SpecKit with direct input; missing tools/classes/reviewer; >30% opus | PASS (static) | Direct adapter/REQUIREMENTS and capability/class-share wording are checked. Capabilities were not live-probed; unavailable must be reported, not passed. |
| Live owner dialogue, model obedience, SpecKit stages, async delegation, final independent review | NOT RUN / UNAVAILABLE | Out of scope for static implementation validation; no paid probe, installer, delegate, or reviewer was launched. |

No baseline behavior is classified `removed-unaccounted`; B30 remains the deliberate
portability exclusion. The final independent review must inspect the complete committed range,
not this clean-tree summary.
