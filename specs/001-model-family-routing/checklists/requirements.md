# Specification Quality Checklist: Model Family and Reasoning Effort Routing

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-10-06
**Feature**: [spec.md](../spec.md)
**Lifecycle**: Built-in specification-stage requirements checklist, maintained under the detected `speckit.specify` instructions; not an implementation completion checklist.
**Marker Semantics**: `[x]` means reviewed and satisfied for requirements quality only. Independent acceptance review remains required.

## Content Quality

- [x] CHK001 No implementation details (languages, frameworks, APIs)
- [x] CHK002 Focused on user value and business needs
- [x] CHK003 Written for non-technical stakeholders
- [x] CHK004 All mandatory sections completed

## Requirement Completeness

- [x] CHK005 No [NEEDS CLARIFICATION] markers remain
- [x] CHK006 Requirements are testable and unambiguous
- [x] CHK007 Success criteria are measurable
- [x] CHK008 Success criteria are technology-agnostic (no implementation details)
- [x] CHK009 All acceptance scenarios are defined
- [x] CHK010 Edge cases are identified
- [x] CHK011 Scope is clearly bounded
- [x] CHK012 Dependencies and assumptions identified

## Feature Readiness

- [x] CHK013 All functional requirements have clear acceptance criteria
- [x] CHK014 User scenarios cover primary flows
- [x] CHK015 Feature meets measurable outcomes defined in Success Criteria
- [x] CHK016 No implementation details leak into specification

## Notes

- **Validation iteration 7: 16/16 specification-quality items satisfied; renewed owner specification approval REQUIRED before any plan/task revision.** The owner now replaces exact-version/effort benchmark-only eligibility with the advisory rubric in OD9, superseding OD8 without erasing its approval history. Family suitability and effort are independently justified; provider documentation, runtime support and owner authorization remain hard gates. Q1–Q3 recovery decisions are unchanged. This correction reads supplied CSVs and existing research, not new fetched sources; no implementation model selection, dispatch, plan/task/research/approval-record edit, skill implementation or live rollback is performed.
- **CHK005/CHK006/CHK013 resolution**: No clarification markers remain. FR-017–FR-020 and Story 4 now distinguish an existing implementation commit from a new failed-attempt checkpoint, require a separate ordinary inverse, prohibit empty/mixed-ownership/unsafe commits, and make approval boundaries and blocked recovery observable. Current verified-only task-commit policy is explicitly a future implementation seam, not silently treated as changed.
- **Content review**: No language, framework, API, storage schema, fetch implementation, dispatch algorithm, or rollback command is prescribed. Family names, existing artifact/approval vocabulary, indexed evidence, history-preserving task commits, and the retry sequence are owner-set behavioral constraints. Source paths are provenance, not a proposed implementation layout.
- **Outcome review**: SC-001–SC-007 use complete coverage, zero prohibited behaviors, and exact attempt bounds rather than invented latency, cost, accuracy, or benchmark targets. Checked CHK015 means intended outcomes are specified and traceable, not that this unimplemented feature has achieved them.
- **Traceability review**: Stories 1–2, FR-003–FR-008, FR-013, FR-025–FR-027 and SC-001–SC-002/SC-007 carry OD9's advisory rubric, uncertainty, independent family/effort reasoning and assignment-table-before-final-approval boundary. OD8 is explicitly historical/superseded; S1–S3, original safeguards and settled Q1–Q3 remain. All five supplied CSVs have source links, parsed row counts and SHA-256 identities in the spec; no historical label or obsolete approval digest grants current routing authority.
- **Dependency review**: Missing qualifying benchmark coverage lowers confidence and triggers targeted research or an explicit bounded owner uncertainty decision, not automatic rejection of a supported pairing. FR-003–FR-008 retain provider-documentation/runtime support and owner authority as hard gates, distinguish source labels from firsthand verification, and forbid naive cross-harness percentage ranking, synthetic owner-preference scores, universal thresholds and fixed effort ladders. Existing [research](../research.md) and [approval history](../spec-approval.md) are unchanged; their benchmark-only assertions are historical for this correction and need authorized later reconciliation after renewed specification approval.
- **Safety review**: Stories 4–5, edge cases, and FR-014–FR-024 cover bounded attempts, missing failure inspection, environment versus reasoning diagnosis, baseline/ownership/dependency stops, evidence checkpoint BEFORE a failed-attempt commit or inverse, history/unrelated-work preservation, no automatic Astra retry, evidence/index durability, and exact-content guideline approval with drift protection.
- **Compatibility review**: FR-025–FR-026 preserve TinySpec/Standard/legacy provenance and approval gates, ordering, sequential coordination, per-task and evidence checkpoints, and independent review; active obsolete class routing is removed without rewriting historical facts.
- **Stage inspection**: Before-specification hook registry `.specify/extensions.yml` was absent. Installed template resolution selected the core spec/checklist templates; sequential numbering and absent `specs/` selected `specs/001-model-family-routing`. No branch hook or slash-command shell simulation was used. The ignored `.specify/feature.json` pointer is checkout-local, not part of the retained commit. Post-specification inspection also found no hook registry; no before/after hooks required dispatch.
- **Authorized correction checkpoint**: Baseline `c1dd9dd7aadd3c8e5b3d36645ad0a430651ac85d` on `main`, tracked worktree clean and index empty before this focused clarification. The preceding unapproved rubric correction's spec digest was `4989fa504feb2003c83c3e934ebd53d1fa60b15d71f20a82c75b212f0da70a27`; OD10 clarifies the same pending revision, not a new approval. The prior approved spec digest is `48dd80c9ada5e2e1ab87c9f2eb042b8e876da2ac6687eb57ba46a6695534d99d`; the unchanged approval record preserves that authority as history, not approval of corrected bytes. Only `spec.md` and this checklist are task-owned paths. Unrelated untracked `.env` and `docs/plans/mandatory-task-commits.md` must remain byte-identical and uncommitted; no secret values are read into artifacts. No other source, documentation, settings, pointer, or coordination evidence writes are authorized. Result digest and commit evidence are returned to the planner, not recursively embedded in their own committed artifact.
- **Supplied-data review**: Full CSV parsing confirms 369 effort rows/22 pairings with coding/tool-use coverage for every pairing, plus 45 Astra, 11 Luna, 35 Terra and 14 Sol BenchLM rows. Snapshot and reasoning mode are unspecified throughout the effort dataset; 346 rows omit evaluation dates, 267 are secondary OpenRouter/AA and 113 secondary numerical results are not independently primary-verified. The supplied verification labels are not new primary-source verification. The spec separates AA Terminal-Bench's 66-task/three-repeat mini-swe-agent setup from the prior 330-trial leaderboard, distinguishes benchmark versions/splits/composites/overlapping subsets, and prohibits performance guarantees or a naive ranking.
- **On-demand access review**: OD10, FR-009, Story 2 scenario 6 and SC-002 explicitly require a future project-owned raw CSV archive with source identity/digest and compact research/index discovery. Routine context contains concise rubric/citations only, with zero automatic whole-CSV loads or full-dataset task prompts; agents retain on-demand matching-row access and must not infer missing metadata. No archive or downstream artifact is created/edited by this clarification. Review should recheck this traceability and access/context distinction while retaining OD9's advisory rubric and hard support/owner gates.
- **Next gate**: Independent acceptance review, then planner-owned renewed current-content specification approval covering the advisory-policy correction and OD10's on-demand dataset clarification. Only after renewal may the affected research/plan/tasks be reconciled under their own bounded authority. Future reviewed tasks need the assignment table before one final owner approval; this correction supplies neither assignments nor implementation authority. Quality-check completion and settled Q1–Q3 do not substitute for renewal.
