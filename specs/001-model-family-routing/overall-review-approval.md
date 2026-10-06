# Model family routing — overall review and implementation approval

Producer: planner; depth: Standard. On 2026-10-06 the owner answered **“Approve tasks and assignments”** at the single combined `ask_user` gate after the complete T001–T012 scope/assignment table and independent reviewer proposal were displayed. This authorizes coordinator preflight and, if its fresh checks pass, the reviewed implementation scope. It is not a waiver of dispatch, Git safety, acceptance, independent review or separate operational permissions.

## Current-content scope

- Approved specification: `spec.md` SHA-256 `e2e903f36672c3882da06b30ba095ab68487b3c312bef396572caaf9b5bcaf00`; separate specification approval is in `spec-approval.md`.
- Approved plan: `plan.md` SHA-256 `5f41fcfcd31e3d40d20716325335be0a1c97453daba13aebf18f9f907f58d7a8`.
- Approved task contracts and serial dependency graph: `tasks.md` SHA-256 `fa81735de24f8ee0251f1f45c9afcca66a9b2336717ff100cf62c53358e0c78c` at checkpoint `d79072c`. The sole `d79072c` change after review of `56cdbd0` replaces the final sentence's pending-review status with its actual run ID; the approved task scope, acceptance, dependencies and proposed assignment rows did not change. Execution order is T001 → T002 → … → T012, each with separate verified checks/commits and factual evidence checkpoints.
- Supporting approved-plan context: `research.md` SHA-256 `1653817fc0823be19abd0758bb0f9683a340a61597eae4e877170c2b2c7437f0`; `data-model.md` SHA-256 `9dbb8e090a7550820c8b3ecb5a57596ce2531f6c174b90bb0285fc923225a341`; `quickstart.md` SHA-256 `be22fcb2c8912635b3cdec161e2351454f4bc66d3cbb064f3ac5baaccf71aafb`.

## Distinct approved routing selections

| Task | Family / exact binding / requested effort |
| --- | --- |
| T001 | Terra / `openai-codex/gpt-5.6-terra` / medium |
| T002 | Sol / `openai-codex/gpt-6.1-sol` / medium |
| T003 | Sol / `openai-codex/gpt-6.1-sol` / medium |
| T004 | Terra / `openai-codex/gpt-5.6-terra` / medium |
| T005 | Sol / `openai-codex/gpt-6.1-sol` / medium |
| T006 | Terra / `openai-codex/gpt-5.6-terra` / medium |
| T007 | Sol / `openai-codex/gpt-6.1-sol` / medium |
| T008 | Sol / `openai-codex/gpt-6.1-sol` / medium |
| T009 | Sol / `openai-codex/gpt-6.1-sol` / medium |
| T010 | Sol / `openai-codex/gpt-6.1-sol` / medium |
| T011 | Terra / `openai-codex/gpt-5.6-terra` / medium |
| T012 | Sol / `openai-codex/gpt-6.1-sol` / medium |

Independent final implementation reviewer: fresh-context read-only `reviewer`, Astra / `openai-codex/gpt-6-astra` / medium; separate from the T012 writer, not an automatic fourth attempt. These are exact owner selections, not an instruction to substitute unavailable models or to grant Luna runtime scope. Bounded retry-family routing is the task-listed Luna → Terra → Sol sequence, starting at the selected family, at most three attempts; after failure inspect cause and safely recover before a supported independently justified least-adequate retry effort within existing owner-selected authority. No preselected retry effort, automatic increase, skipped family or blanket per-retry approval. Out-of-authority routing, changed scope or uncertain safety/capability stops for owner decision.

## Reviewed evidence and boundaries

Independent fresh-context read-only Astra/medium planning reviewer `4e7eb1aa-263b-4699-beb8-a90da8526491` inspected the committed `56cdbd0` five-file reconciliation and current spec/approval; found no blocker and returned **OK with notes**. The status-only `d79072c` task edit was inspected separately against that delta. Task-order checker and scoped whitespace checks PASS. Four prior owner-authorized probes and planning reviews establish basic requested-binding/effort callability, not internal effort, task-specific writer success, cost or future availability. Lower-effort adequacy remains unverified; weak Terra terminal evidence, differing benchmark harnesses and unknown pricing were disclosed and accepted as bounded advisory uncertainty. T009's executable temporary-Git recovery oracle remains mandatory before accepting recovery behavior. The raw 369-row CSV remains byte-preserved with its previously documented CRLF-only full-range whitespace exception; routine agents consult relevant rows on demand.

At preflight and each dispatch, recheck exact runtime binding/effort, writer or reviewer tools/context, user question and async delegation capability, ownership, artifact revisions, current safeguards and required tests. An absent or drifted hard gate stops work; no silent substitution or additional routine assignment question. Preserve unrelated `.env` and `docs/plans/mandatory-task-commits.md` without staging them. This approval does **not** authorize paid benchmark/provider experiments beyond implementation dispatch, changing model settings, push/deploy, real-world rollback, or changes to `memory/coordination/GUIDELINES.md` (separate exact-content owner approval required). Material changes to approved spec, plan, task contracts or assignments require appropriate re-review and renewed affected approval; factual execution-status/evidence updates alone do not change task contracts.
