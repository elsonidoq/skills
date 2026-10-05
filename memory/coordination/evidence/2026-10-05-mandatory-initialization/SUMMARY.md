# Mandatory project-local coordination initialization

Date: 2026-10-05
Areas/tags: coordination-memory, skill-contracts, initialization, persistence, verification
Run ID: 2026-10-05-mandatory-initialization

## Source and authority

Owner correction in this session: “if the skill finds those files are not present in the
project directory, it must automatically initialize them and let the user know and commit
them ... and proceed.” Owner clarified “project local,” and that the skills themselves
must generate missing files in future projects, not merely initialize this checkout.
This supersedes the earlier approved optional-store/handoff-only design, not the separate
approval requirement for learned-guideline changes. No further setup approval was requested.

## Observed outcome

Initialized empty `memory/coordination/GUIDELINES.md` and `evidence/INDEX.md`, notified owner,
and committed only those files in `e619156`. Changed the shared contract and all five
consumers so future entry points perform mandatory missing-file creation, notification and
path-limited commit before continuing. Removed handoff-only persistence; failures stop.
Existing declared project-local layouts are reused; otherwise default is project-root
`memory/coordination/`. Existing files and unrelated staged work are preserved.

Focused checker PASS; planner suite 78 PASS; coordination suite 20 PASS; skill lint and all
bundled suites PASS after correcting one doc wording regression; whitespace PASS.
See [T001](T001.md) for attempts/checks and [reflection](REFLECTION.md).
Independent correction review pending. Live agent/SpecKit obedience NOT RUN.
No learned guidelines added; existing untracked `.pi/` and `.specify/` untouched.
