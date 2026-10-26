# State and ownership model

Derived from [spec.md](spec.md); implementation evidence/choices in [research.md](research.md). This describes behavioral entities, not a new schema or migration.

| Entity | Existing information and relationship | Invariant / transition |
| --- | --- | --- |
| Task | `id`, work description, optional `depends`, path limits and checks | Dependency readiness requires successful producer completion, never worker transport return alone. Existing six intake rules unchanged. |
| Worker invocation | Existing prompt, invocation identity, return/error, saved session and correction history | Returned means control returned; blocked/failed/incomplete work cannot transition task to complete. Harmless corrected errors do not permanently poison success. |
| Required command attempt | Existing `command`, `exit_code`, `output` via `checks`, `check`, `required[].check` | Failed → safe same-task correction → actual successful rerun, or unsuccessful task. Absent optional checks are not failed required checks. Semantic acceptance stays distinct. |
| Focused checkpoint | Selected paths, parent/SHA, no-change and existing generated-artifact facts | Only known owned results enter checkpoint. No-change success needs no empty commit. A checkpoint does not itself establish acceptance. |
| Scoped repair | Diagnosed failure, explicit necessary paths, selected executor, relevant checks/checkpoint | Outside original worker paths is not outside coordinator authority by definition. Separate authorized scope repairs; verified checkpoint precedes retained unfinished continuation. Unknown cause stops blind relaunch. |
| Review finding | Existing string location/defect, boolean review verdict and findings list | Single line or numeric range is syntax compatibility only. Preserve exact string and verdict; malformed output remains incomplete. |
| Issue | Qualified host/repository/number/URL, actual body/state, intent/evidence | RCA facts/hypotheses precede creation. Created/read-back does not imply independently reviewed. Concurrent change defers unsafe overwrite. No parallel local store. |
| Issue assessment | Separate read-only review of actual body against original intent/evidence | Actionable finding → evaluated narrow correction → independent readback. Missing reviewer means incomplete review, not fabricated success. |
| Exact-file handoff | Explicitly identified and authorized file plus observed starting content; relationship to receiving task | Untracked or tracked-modified target can transfer without erasing prior bytes. Broad path limits never confer transfer. Unknown/drifted/unapproved targets remain protected. Reuse task-local ownership facts, no grant registry. |

No new universal task fields, result schema, permission schema, evidence receipts or history rewriting. Optional exact-file handoff representation must remain separate from `owned_paths`, use the existing execution input path, and be exercised at claim/edit/checkpoint. Existing public history remains readable; new outcomes are recorded truthfully in ordinary existing progress/error history.
