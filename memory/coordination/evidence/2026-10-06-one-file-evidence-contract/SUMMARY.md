# One-file coordination evidence contract — current-run record

Date: 2026-10-06. Tags: coordination, evidence layout, task checkpoints, review.
**Disposition:** approved future-run contract and bounded historical compaction committed; independent content review passed, with one **unresolved historical process deviation** recorded below. No guideline mutation or external push. `/reload` needed in pi.

## Authorization and checkpoints

The owner approved one concise `SUMMARY.md` per new run with a shared index, compact task/check and attribution pointers, reflection and exact guideline approval, while retaining distinct per-task Git/evidence commits. Only the 2026-10-06 batch-routing planning and implementation runs were approved for historical compaction; other older runs stay unchanged.

| Task | Baseline → result | Verification and outcome |
| --- | --- | --- |
| Shared contract/checker/docs | `f9d85cd` → `f17244a` | Planner checker PASS/80 tests OK; coordination tests 21 OK; task-commit checker PASS/12 tests OK; skills lint OK; diff check PASS. Constitution 2.2.0 records approved layout; no guideline changes. Parent implemented and inspected; no live model test. |
| Two-run compaction (sub-agent) | `f17244a` → `b6efb76` | Worker verified links, SHAs, approval digests and archive pointers; 137 reported tests PASS; diff check PASS, clean index/worktree. Scoped run bytes 56,791 → 16,266 (71.4%). Deleted ten task records and one reflection after consolidating; original facts retrievable with `git show f17244a:<path>`. Parent inspected both resulting summaries and scoped diff/clean state. |

Independent read-only reviewer compared `f9d85cd..b6efb76` to archived records and active contracts: content ready, no blocking artifact defect; static checkers and range whitespace PASS. Reviewer did not rerun all 137 tests or inspect live sessions. Offline symbolic tests are not live model performance or runtime-obedience evidence. Older run summaries retain their own first-attempt failures, status/attribution, approvals and parent audits.

**Checkpoint deviation (important):** these were two independently verifiable tasks, but after `f17244a` the required distinct factual evidence-only checkpoint was not committed **before** later task writes for `b6efb76`. This late record repairs durable discoverability, **not** the chronological task-commit violation. Neither owner design approval nor the later compaction waived the rule; do not present this as compliant execution or rewrite history. This record and its index update are the corrective evidence-only checkpoint; no implementation-task substitute or empty retroactive commit. Root cause: parent advanced to delegated compaction after the contract commit without persisting current-run evidence first. Future tasks must stop until their timely checkpoint is committed.

## Reflection

One missed checkpoint reinforces the existing task-commit rule; it does not establish a model capability failure or a new project guideline. No update proposed. The approved file-layout change is a shared process contract, not an automatic learned-guideline write. Remaining limitation: the elapsed checkpoint order cannot be repaired retroactively; no historical live comparison was performed.
