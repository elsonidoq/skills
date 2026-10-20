# ADR decisions — TinySpec planning review

## Scope and authority

Planner-owned review, not an independent implementation review. Owner selected
TinySpec, Sol/medium planning producers, and granular outcomes suitable for intended
Terra/medium implementation. Exact implementation binding remains for later selection.
**Planning was approved and implementation was subsequently authorized by the owner;
see Approval below. This record does not claim implementation has started or finished.**

Owner permits planning in this concurrently edited checkout confined to our created
files. A temporary no-commit instruction has now been lifted. No unrelated files,
shared indexes, skills, runtime, application files or memory were edited by this review.

## Reviewed content

SHA-256 of complete UTF-8 file bytes (approval applies to these contents):

| Artifact | SHA-256 |
| --- | --- |
| `docs/plans/adr-decisions-tinyspec.md` | `46cf0345aa87853abd92351635b7a50d0a09998e7215cce7edd6d5d50ad8d35b` |
| `docs/plans/adr-decisions-tasks.md` | `90042a3b3c08e92e6b84730451892254651615e808b1812c42fdbc602501c449` |
| `docs/plans/adr-decisions-tasks.json` | `b4612ad05521a861affd4463167c95716757e4c9d6939dc06cfded56a966a568` |

Source checkpoint: `4207aba5461c8c400b99f1c85516a3e0ac3db2c3`.
Task checkpoint: `728da6060233ab82e4543a426f0da9d0109cdc44`.
Unrelated HEAD advancement is expected; approval comparison uses these scoped contents.

## Findings and disposition

- Initial broad planning/execution milestones were too coarse for the owner's later
  Terra/medium sizing requirement. Corrected by the original producers: source records
  intended executor and task-sizing constraint; task list now has eleven bounded outcomes.
- T001 delivers the canonical contract (A1/A2); T002 closeout (A3); T003 adoption (A4).
  T004–T009 separate orchestration, source/task adapter, brainstorming, architecture,
  implementation-skill and paired review contracts (A5). T010 owns only actual engine
  prompt text/captures (A5). T011 publishes bounded docs and composes delivered evidence (A6).
- Each task has owned paths, a consumed interface and local completion oracle. Ordinary
  tests/docs/checkpoints stay with delivery. Thin consumers depend on the canonical
  contract; shared test-file edits require sequential ownership checks, not invented
  producer dependencies. Documentation integration depends on delivered consumers.
- Accepted outcomes and explicitly mandated mechanisms remain protected. Compatible
  helper deletion adds no gate. Approval, implementation status and permission to act
  are distinct; proposed supersession cannot authorize conflicting changes.
- Specs/current docs retain their owners; no bulk migration, historical backfill,
  guessed ADR-store location, new approval ceremony or enforcement subsystem is included.
  Missing storage alone does not block unrelated legacy work.
- Runtime scope is justified by the final reviewer's disabled automatic skill loading.
  T010 changes only two existing prompts and their tests, not the host/runtime design.
  Fresh sole-writer/path checks still prevent overlap with another running workflow;
  there is no prohibition on this workflow delivering its own runtime changes.
- No separate prototype or external research is justified for these known local seams.
  Pressure/contract scenarios and actual prompt captures are proportional; they do not
  prove unrestricted model obedience. No mandatory paid/provider/live test is introduced.
- Shared-index links are deferred to T011, honoring current created-files-only authority.
  Paseo activation later needs a fresh-session handoff, not automatic reload/restart.

**Review result: no unresolved planning blocker in reviewed content.** This is not
feature acceptance, proof of current capabilities, or implementation authorization.

## Verification

PASS: both actual task-order validators:

- `python3 skills/task-generation/scripts/check-task-order.py docs/plans/adr-decisions-tasks.json`
- `python3 skills/task-generation/scripts/check-task-order.py docs/plans/adr-decisions-tasks.md`

PASS: parent inspected complete source and both task representations, producer commits
and actual scoped diffs. Focused Python assertions checked eleven tasks, A1–A6 coverage,
check/pass/evidence fields, owned paths/consumed interfaces, argv command shapes, separate
Terra/Sol intent, and minimal T010 runtime paths. Source/task paths have no uncommitted
changes; reviewed SHA-256 identities are above. Owned whitespace checks passed.

NOT RUN: future feature/contract/runtime acceptance tests, live model behavior, actual
adoption, store creation and independent final implementation review. They are not
claimed satisfied by planning syntax or scenario descriptions.

## Approval

Owner answered **“Approve planning only”** through `ask_user` after the full task brief.
This approves the combined source/task contents identified by the SHA-256 values above,
not implementation. The owner subsequently authorized implementation: “launch the workflow,
you will be the only one doing an implementation in this worktree”. They then explicitly
removed the one-time restriction on executing through the runtime being changed:
“Forget about that rule. That was a one-time thing. Remove that rule at all.
Whatever that rule is written, delete it.” The content identities above reflect only
that bounded removal from the reviewed source/tasks; all A1–A6 criteria and eleven
outcomes remain unchanged. This owner direction renews approval for that removal,
not unrelated scope changes. Intended implementation family/effort remains Terra/medium;
exact binding and usable configuration remain for preflight. Any future material source/task
change requires affected review and renewed approval; current runtime/path state must be
inspected again before implementation.

## Independent implementation review and acceptance

The fresh Sol 6.1 full-range reviewer inspected
`81cabbac7fbdbaa9556747f88af42cae41ece34c..14741a43fbb14f6ef11a0aaccc59f9307b6add58`
and returned **NOT APPROVED** with two findings: missing canonical `save-adr` links in
planner/TinySpec/task-generation, and preselection instructions excluding read-only
existing-ADR discovery. Its separate review of
`14741a43fbb14f6ef11a0aaccc59f9307b6add58..2cc0402ef36fd264abde4bb5b1bdb7a2a46f80a6`
returned **APPROVE** for separate worker/reviewer executor configuration. Review session:
`d6312a55-a1c8-4f32-9e35-89d993991af3` (Sol 6.1/high, launched before the owner's
subsequent medium-effort selection for future workflow reviews).

A different Sol 6.1/medium writer corrected the two findings in
`06ad7c2d4aea099a4216c546e9783315bd420bb9` and
`9a4f3043f0c24ae8a2ba234dba8ecff9cd907242`. The writer reported resolving-link and
omission checks, corrected read-only discovery/resume assertions and synthetic disposable
walkthroughs, plus 146 planner tests passing after each correction. Parent inspection
confirmed the focused commits and source changes; the writer is not the final reviewer.

Fresh independent **Sol 6.1/medium** recheck session
`c19b9a99-9950-43ac-a1ac-393586bea558` inspected
`2cc0402ef36fd264abde4bb5b1bdb7a2a46f80a6..9a4f3043f0c24ae8a2ba234dba8ecff9cd907242`
and returned: **“No issues found. Verdict: APPROVE corrected ADR implementation.
Merge verdict: OK.”** Both original findings were explicitly resolved; no necessary
corrective follow-up remained within scope. Combined correction diff SHA-256:
`4374fe4b3c93144f7996c320df1e7bfafb45b3bef860c6aaa094657ef6d900a1`.
This acceptance combines the original full-range review with the focused independent
recheck; unchanged reviewer configuration retains its separate approval.

Limits: reviewers inspected committed source/diffs, not live model behavior, and did not
independently rerun the reported test suites. Earlier worker validation reported 146
planner, 189 initialization and 12 engine tests; the separate configuration change passed
20 synthetic CLI/engine tests. Static/scenario/prompt wiring does not prove actual agent
obedience. Workflow-script attempts retain their actual failed history; this independent
acceptance does not relabel them successful or alter SQLite. No runtime installation,
project ADR store creation, fleet refresh or activation is claimed. In Paseo, activation
requires a fresh session that verifies this checkout and its loaded capabilities.
