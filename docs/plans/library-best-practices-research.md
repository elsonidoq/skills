# Library best-practices research — TinySpec source

## Context and authorization

The owner requests evidence-backed dependency design in both TinySpec and Standard: consequential choices involving unfamiliar external libraries must not rely silently on generic model knowledge. Beneficiaries are owners and implementers using this portable planning suite, who need reusable guidance and explicit implementation constraints.

Provenance: the current owner request, plus the inspected repository authorities below. The owner explicitly selected TinySpec preparation and `openai-codex/gpt-6.1-sol` as the bounded-work/sonnet-class binding. This artifact records source production only: no artifact approval, implementation authorization, tasks, commits, push, or additional agents. The binding is supplied context, not an independently tested model capability.

The authoritative source is `docs/plans/library-best-practices-research.md`, published by the parent from the preparation output. Separate implementation tasks belong to a later stage. This source is prepared, not approved for implementation.

## Inspected authorities and verified constraints

- [Repository policy](/home/dev/projects/skills/AGENTS.md): global assets must remain portable; no assumed project layout, path, dependency, model, or deployment. Future global skill changes require advising `/reload`.
- [Documentation index](/home/dev/projects/skills/docs/index.md): update the most specific technical owner, then discovery links; this suite declares no project-memory adoption. No memory initialization is required here.
- [Planner](/home/dev/projects/skills/skills/planner/SKILL.md): preselection is read-only; selection authorizes preparation only; planner owns detection/discovery, bounded stage briefs, review, and existing approvals. Standard-only prerequisites follow selection.
- [TinySpec](/home/dev/projects/skills/skills/tiny-spec/SKILL.md): compact what/how, separate tasks, no obligatory intermediate research/design artifact chain, no standalone source approval.
- [Architectural helper](/home/dev/projects/skills/skills/delegating-architectural-planning/SKILL.md): Standard adapter performs the entire review-spec/create-plan/review-plan pass once. Its current boundary permits only specified SpecKit planning artifacts unless separately authorized; canonical dependency documentation therefore needs explicit additional bounded authorization.
- [SDD reference](/home/dev/projects/skills/docs/best_practices_spec_driven_development.md): evidence-backed constraints, independently observable acceptance, material owner gates, and depth-specific approval lifecycles remain authoritative.
- [Static checker](/home/dev/projects/skills/scripts/check-planner-workflow.py) and [fixture tests](/home/dev/projects/skills/scripts/test-planner-workflow.py): operational phrase/section checks, mutations, and offline fixtures exist; they are not model-obedience proof.
- [Regression guide](/home/dev/projects/skills/docs/plans/planner-regression.md): deterministic versus live evidence is explicitly separated; full production scenarios require separate authorization and isolation.

## Scope and exclusions

Smallest intended change surface:

| Surface | Responsibility |
| --- | --- |
| `skills/planner/SKILL.md` | Detect research need, preserve preselection boundary, hand off evidence/capabilities/write scope, review reuse and traceability. |
| New `skills/planner/references/dependency-research.md` | Single shared detailed research, provenance, persistence, and capability-failure contract. |
| `skills/tiny-spec/SKILL.md` | Apply/link shared contract before consequential approach decisions, including direct use. |
| `skills/delegating-architectural-planning/SKILL.md` | Apply/link shared contract before consequential architecture decisions, including standalone use; resolve narrow documentation write scope. |
| Existing checker/tests and minimal documentation | Focused regression protection, shared-contract discoverability, and evidence limitations. |

Do not introduce a standalone research skill, duplicate workflow, forced TinySpec research artifact chain, global knowledge store, fixed target-project path, or task-generation/brainstorm/coordinator rewrites. Do not change owner depth choice, material-choice gates, approvals, SpecKit requirements, model classes, or implementation boundaries. Durable reusable dependency guidance is technical documentation, not a new approval stage.

## Decisions and approach

### Shared proportional research contract

1. Discover repository instructions, dependency declarations/lockfiles, existing technical owners, documentation indices, and relevant project guidance before researching. Determine the actual dependency/version in use or explicitly flag an unresolved selection; do not guess a version.
2. Research triggers are first repository use, insufficient existing guidance, performance/reliability/architecture-sensitive behavior, or uncertainty. Trivial use and relevant sufficiently documented use can skip new internet research. Record a short reason/evidence for reuse or skip rather than impose a ceremony on every import. Risk-sensitive behavior still requires sufficient evidence; an old document alone is not sufficient.
3. Reuse applicable repository guidance. Check version-sensitive, stale, conflicting, or missing portions; refresh only those portions. A recent research date is useful context, not proof of applicability or a universal freshness deadline.
4. Before required external research, inspect actually available permitted search/fetch/browser or equivalent capabilities in the executing context. Tool names/configuration alone do not prove usability. Use proportional current internet research, favoring official documentation, official guides/examples/repositories, maintainers, reputable technical sources, and selective community evidence. Prefer source material for the installed/targeted version; label newer-version differences.
5. Research only relevant architecture and operational concerns: batching/concurrency, I/O, synchronization/persistence, memory, lifecycle, transactions, caching/indexing, retries/rate limits, deployment, pitfalls, and version behavior. Do not turn this into a dependency-wide audit or invent universal library rules.
6. Separate documented recommendations (with source and version applicability), repository-derived decisions (with local evidence and rationale), and assumptions needing validation. Unsupported snippets, uninspected URLs, uncertain statements, and generic model recollections are not source evidence. Corroborate weaker evidence or retain its uncertainty; required insufficient evidence blocks consequential design.
7. Translate evidence into explicit implementation constraints and observable verification in the compact TinySpec source or Standard plan. Preserve a traceable chain: source recommendation/local evidence → derived decision/constraint → validation. Cite meaningful supporting sections, not merely a URL list. Relevant assumptions require a defined check; material unresolved choices return to the existing owner gate.
8. Persist reusable guidance in the target repository during authorized selected production, before readiness. Prefer an existing specific technical owner and its discoverability index. When none exists, discover conventions and obtain/verify bounded write authority for a suitable owner and discovery location; do not assume this suite's paths apply elsewhere. Preserve unrelated content and re-read before targeted changes.

### Durable guidance content

Canonical target-repository documentation must identify the dependency and relevant version/range, applicable practices and pitfalls, repository-derived decisions/rationale, primary URLs and their supporting claims, and the research date for evolving guidance. Include validation needs/uncertainty where relevant. Planning artifacts link to that owner and carry the execution constraints; they need not duplicate the entire research note. Reused guidance receives only necessary targeted corrections, not a wholesale rewrite or a decorative date bump.

### Route integration and safe failure

Planner may inspect and research read-only during preselection when needed for assessment; it must not persist dependency docs, source, plan, or decisions then. Carry findings in session context until selected production is authorized.

TinySpec uses the shared contract before writing consequential approach decisions and persists the reusable technical guidance within authorized preparation bounds. Its standalone entry applies the same contract and verifies destination/write authority without inferring planner selection or adding approval gates.

Standard receives research triggers/context early enough that consequential dependency constraints in specification work are not invented; architectural research and durable guidance are completed before consequential plan decisions. Specification changes caused by research retain existing renewed-approval rules. Planner supplies the helper with explicit bounded authorization to update canonical research docs and necessary discovery links **in addition to** detected SpecKit artifacts, including observed destinations and prohibited operations. The helper's preflight/boundary must recognize this narrow permission; standalone use must verify equivalent permission or report missing authority. Do not authorize arbitrary documentation changes or code writes.

If required research tools, usable sources, version evidence, or write authority are unavailable/insufficient, stop the affected branch and return the exact gap, affected decisions, and evidence needed. Planner may obtain an explicit owner deferral through existing gates; no silent generic-knowledge fallback, invented sources, automatic deferral, install, or premature readiness. Existing adequate repository guidance can satisfy research without a new search call. Explicit deferrals must state their impact, allowed bounds, and outstanding validation; they do not fabricate evidence or waive unrelated gates.

Planner review checks shared-reference resolution, direct/standalone coverage, canonical documentation/discovery, version/provenance, targeted reuse, source-to-constraint-to-validation traceability, unresolved assumptions and capability/permission gaps before existing approvals/readiness.

## Acceptance and validation

- **R1 — Both routes and standalone:** TinySpec and Standard/helper consult the same contract before material dependency design, including direct invocations. No change to existing depth or approval gates.
- **R2 — Proportional reuse:** repository discovery precedes internet work; adequate guidance/trivial usage avoids unnecessary research; version-sensitive outdated portions receive targeted refresh only.
- **R3 — Evidence and constraints:** durable discoverable guidance contains dependency/version, practices/pitfalls, derived decisions, primary URLs, and evolving-guidance research date. Planning constraints and verification trace back to classified evidence; assumptions are not presented as documented rules.
- **R4 — Safe failures:** required unavailable/insufficient research stops or returns for explicit owner deferral; unsupported sources and generic recollection cannot satisfy readiness. Delegated Standard documentation writes have explicit bounded authority.
- **R5 — Authorization:** no preselection documentation writes; persistence occurs during authorized selected production before readiness. Preserve unrelated content and unchanged owner gates.
- **R6 — Regression integrity:** existing checks continue to pass; focused static/fixture additions detect missing shared references, route/standalone omissions, preselection-write permission, provenance/traceability loss, and unsafe fallback/boundary weakening. Mutation tests must demonstrate checks reject removed obligations, not just accept happy-path keywords.

Regression scenarios cover an unfamiliar indexing engine with batching/flush/lifecycle questions (evidence determines library-specific constraints; no universal rule is assumed), recent applicable guidance reuse, trivial skip, outdated-version targeted refresh, unavailable search with inadequate repository guidance, unsupported source evidence, both planning routes and standalone entry, and preselection with no docs writes. Offline fixtures may simulate sources/capabilities but must be labelled simulated. Semantic review examines real supporting spans and resulting constraints; static/fixture success is not proof of internet quality, genuine SpecKit integration, or model compliance. Separately authorized behavioral runs must capture research use, write timing/scope, artifact snapshots, and actual source-to-validation correspondence.

Expected implementation validation: `python3 scripts/check-planner-workflow.py`, `python3 scripts/test-planner-workflow.py`, `bash scripts/check-skills-lint.sh`, focused link/traceability review, and `git diff --check`. Keep existing execution freeze and preservation assertions intact. No live/model/internet test authorization is inferred.

## Current evidence, risks, and blockers

Baseline on the inspected unchanged checkout: Python 3.12.3; `PYTHONDONTWRITEBYTECODE=1 python3 scripts/check-planner-workflow.py` PASS; `PYTHONDONTWRITEBYTECODE=1 python3 scripts/test-planner-workflow.py` PASS (56 tests); `git diff --check` PASS. Initial and post-check `git status --short` and staged-file listing were empty. No implementation or tests were changed.

This preparation runtime exposes repository/file/shell tools but no dedicated callable internet research interface. No dependency-specific consequential architecture is being selected in this source, so no external-library research is required for this stage and no external source claims are made. Future affected stages must verify their own usable permitted research capabilities; shell availability is not research capability evidence.

No material source-production decision remains unresolved. The existing Standard helper documentation-write mismatch is verified and explicitly resolved by the proposed narrow authorization contract above, not by claiming permission already exists. Residual risks are natural-language compliance and quality/applicability of real research; deterministic coverage cannot establish either. Live research, real SpecKit production, binding usability, implementation review, and owner approval have not been performed or claimed.
