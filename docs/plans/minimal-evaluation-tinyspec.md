# Minimal Coherence evaluation — TinySpec

## Problem and outcome

Coherence maintainers need proportionate evidence that fixes improve skills/workflows,
not an evaluation platform. Owner-selected TinySpec preparation follows read-only discovery;
the owner request in the source-producer brief is the requirements provenance. The initial
behavioral regression collection **must be empty**: this issue adds no behavioral cases,
including hypothetical or artificial fixtures. An empty collection proves no correctness.
Existing static tests, historical fixtures and evidence remain intact and separate.

The existing issue lifecycle remains: encounter a problem during use → fork the session and
file a GitHub issue with context → later select/group issues → derive a minimal repro →
evaluate previous behavior → fix → evaluate candidate → retain useful cases. Evaluation is
not a prerequisite for initially filing an issue. This capability supports that later work.

## Settled approach and bounds

Use a convention-first, documentation-only MVP. `evaluations/README.md` will be the single
operational owner for adding and selectively running future issue-derived cases. A README-only
collection is empty even though Git cannot retain an empty directory. No new runner or skill
is justified. Add only discovery links in README's Validation section and `docs/index.md`,
the repository-local DoD in `AGENTS.md`, and the narrow constitutional reconciliation below.
Do not turn these links into duplicate procedures or alter reusable global workflows.

A future case needs only its issue/context link, tiny relevant input, invocation prerequisites,
and independently stated expected behavior. Plain files and prose suffice; no schema,
registry or case-generator is required. Freeze input and expectations outside result output
before inspecting candidate output (normally before either run). Keep expectations out of
the model's task prompt when they would disclose the answer. If expectations change, disclose
that change; old runs are not evidence against the new expectations.

Select the smallest meaningful seam: one isolated skill when sufficient; integration or E2E
only when the failure concerns interactions or complete workflow behavior. These are choices
for a case, not three systems to build. Reuse existing Pi launches, completion and logging;
full workflows may later need a scoped disposable repository and their actual tools/gates.
Do not force workflows through a read-only isolated-skill recipe.

Default: run the same case **once on previous and once on candidate**, with the same frozen
expectations, model/effort and relevant environment. Identify the actual revisions/resources,
Pi version, prompt/input and relevant differences. Inspect outputs, not just exit status:

| Previous / candidate | Interpretation |
| --- | --- |
| fail / pass | Observed improvement on this case |
| fail / fail | Failure remains |
| pass / pass | Cannot reproduce the reported failure |
| pass / fail | Possible regression |

No automatic retries or repetition to force a failure. An error, aborted/incomplete run or
missing prerequisite is reported as such, not silently counted as behavioral failure/pass.
Report inability to reproduce honestly. Prefer deterministic assertions where they observe
the intended behavior; qualitative human judgment is acceptable. Use an LLM only when the
real behavior needs it, not a generic judge. Retain useful real cases after later issue work,
not every incident or disposable probe.

Keep inspectable Pi output/logs and a brief interpretation in ordinary issue/PR evidence,
with commands and actual results. No ledger or reporting service; no credentials or sensitive
session payloads. Report tokens only if readily available from existing output; no new cost
instrumentation. Select cases deliberately; never automatically run the full collection.

## Verified dependency guidance and practical invocation

Repository-derived evidence: [README Validation](../../README.md#validation-and-documentation)
and [static entry point](../../scripts/check-skills-lint.sh) already own deterministic checks.
The [RPC smoke helper](../../scripts/planner-rpc-smoke.py) is planner-specific/dialog-only,
with an older restrictive profile; do not generalize it. The [issue #37 observations](planner-regression.md#issue-37--simplest-sufficient-review-effectiveness-2026-10-30)
demonstrate isolated JSON processes, not causal previous/candidate evidence. Preserve their
historical scope; do not import those synthetic examples into this empty collection.

Documented interface, verified locally against installed **Pi 1.4.0** (`pi --version` and
package metadata): [CLI modes/resources/prompts](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/cli.md),
[skill loading](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/skills.md),
and [configuration/context](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/configuration.md).
Inspected installed copies live under the package's `docs/` in
`/home/dev/.pi/agent/install/releases/1.4.0/node_modules/@earendil-works/pi-coding-agent/`;
upstream main may change. Recheck applicable installed documentation if the version changes.
Local guidance is sufficient; no internet research, install or new dependency is needed.

The CLI documents JSON mode as one-shot JSONL output, `--no-session` as no saved session,
and `--no-skills` as disabling discovered/configured skills while explicit `--skill` paths
still load. Explicit `/skill:name` forces instruction loading; mere discovery advertises
metadata. These facts support a future convention containing this direct recipe shape,
not a new executable wrapper:

```sh
# Run separately for previous and candidate; all variables are case/operator inputs.
# RUN_CWD is a fresh case workspace, RESOURCE_ROOT is that version's absolute checkout.
(cd "$RUN_CWD" && pi --mode json --no-session --no-approve \
  --no-context-files --no-extensions --no-mcp --no-prompt-templates --no-themes \
  --no-skills --skill "$RESOURCE_ROOT/skills/$SKILL" --tools read \
  --provider "$PROVIDER" --model "$MODEL" --thinking "$EFFORT" \
  "/skill:$SKILL $(cat "$PROMPT_FILE")") > "$EVENTS_FILE" 2> "$ERRORS_FILE"
# Record the actual exit status immediately; inspect events and behavior separately.
```

Use distinct previous/candidate checkouts or exports at explicit revision identities, with
separate fresh equivalent case workspaces and distinct output files. Freeze shared case input
outside both resource trees. All required supporting skills/references/scripts must resolve
to that run's revision; add explicit skill paths only as the case needs them. A baseline must
not read candidate/global skill guidance by discovery or through case prompts, symlinks or
cross-checkout references. Inspect relevant user settings/system additions and ensure they
are unchanged and contain no candidate-only guidance. `--no-context-files` disables discovered
AGENTS/CLAUDE instructions, not all user system additions; `--no-approve` ignores trust-gated
project configuration. If repository guidance itself is under test, supply the appropriate
version explicitly instead of accidentally suppressing the behavior being evaluated.

This is resource/settings isolation, **not a security sandbox**: read can access other paths.
Inspect actual reads and startup/errors; cross-version contamination invalidates the comparison.
Keep provider credentials through existing approved Pi mechanisms; never copy them into cases
or logs. Cases needing writes, dialogs, extensions or a whole workflow use existing suitable
Pi interfaces and scoped tools with actual permissions, not a universal adapter in this MVP.
The future README must make these limits visible rather than promising universal replay.

## Local DoD and policy reconciliation

Repository-local DoD, to be placed in `AGENTS.md`:

> When a practical, meaningful evaluation is possible at a proportionate cost, the issue
> should include evidence that the intended behavior improved.

Usually this is repro-baseline/fix evidence, not mandatory automated tests. Simpler evidence
or a brief impractical/expensive/low-value justification is sufficient; do not manufacture
compliance tests. Keep the explanation with ordinary issue/PR work, not a new artifact chain.

The constitution's [Development Workflow](../../.specify/memory/constitution.md#development-workflow)
currently requires focused fixtures and relevant suite checks for shared skill-contract
changes. Plan a narrow replacement of that sentence: require proportionate verification of
the changed behavior, permit useful simpler evidence or a brief impractical/expensive/low-value
justification instead of mandatory new fixtures, and preserve applicable existing tests,
security and permission gates. This is not permission to skip failing relevant existing checks.
Prepare exact operative amendment text, rationale, appropriate version/date and affected-owner
check for explicit **current-content owner approval at the later combined gate**; this source
does not enact the amendment or silently waive it. No extra ADR is warranted for this local
convention/policy adjustment.

## Acceptance and smallest sufficient verification

- **A1 — Empty, discoverable capability:** Read-only file/diff inspection shows one canonical
  evaluation README, only necessary discovery links/local policy alignment, and zero retained
  behavioral cases added by this change. Historical tests/evidence are preserved. Empty means
  no evaluation results and no correctness claim, not absence of old fixtures elsewhere.
- **A2 — Useful future-case convention:** Manual review can follow how to select an actual
  issue, add tiny input/independent expectations, choose the smallest seam, load explicit
  previous/candidate resources, run once each and inspect output. The documented recipe matches
  installed Pi flags; resource isolation limits and version/environment identities are explicit.
  This is documentation acceptance, not a live comparison or model-obedience claim.
- **A3 — Honest evidence:** Manual inspection finds all four outcome interpretations, clear
  error/inconclusive handling, no forced retries, independent frozen expectations and ordinary
  inspectable issue/PR evidence. Deterministic/human/necessary-LLM judgment and selective runs
  are supported without mandatory automation, token accounting or a generic judge.
- **A4 — Proportionate policy:** Exact DoD and narrowly reconciled constitution permit simpler
  evidence/brief justification without compulsory new fixtures or evaluation at issue filing.
  Applicable existing checks/safety remain. Amendment content requires explicit owner approval
  before application; approval status belongs in approval records, not executable task wording.
- **A5 — Bounded delivery:** Diff/link checks and applicable existing static checks pass or
  report actual failures/unavailability without bypass. No runner, infrastructure, behavioral
  fixtures, real evaluation, global workflow rewrite or historical evidence migration is added.
  Independent review checks omissions **and unnecessary machinery**, plus ADR constraints below.

No executable prototype or disposable smoke is needed: the chosen deliverable documents a
known inspected interface, introduces no helper, and deliberately has no real case yet. Static
and manual checks validate the delivered convention only. A later actual issue supplies the
first meaningful comparison; no artificial retained regression is justified to demonstrate
an empty collection. If a consequential undocumented CLI uncertainty arises, stop affected
reliance and ask before a materially more complex alternative or separately authorized live
proof; no unrun experiment is treated as evidence.

## Constraints, deferrals and handoff

[ADR-0003](../decisions/ADR-0003-current-launch-authority-and-neutral-tasks.md) requires current
scoped authority and authorization-neutral executable tasks: downstream task/review acceptance
must preserve these, leaving historical preparation status in approval records.
[ADR-0004](../decisions/ADR-0004-shared-routine-worker-permissions.md) permits small scoped local
checks/routine technical actions without repeated approval, while retaining paid-scope,
credentials, external-action, unrelated-data and no-blind-expensive-retry boundaries. Downstream
briefs and review must explicitly retain these gates; neither ADR authorizes live models here.
[Memory index](../../memory/MEMORY.md) guidance keeps routine transitions non-notifying and
routine technical decisions autonomous; material scope/product changes still return to owner.

No framework, speculative abstraction, dashboard, reporting/configuration/orchestration layer,
hypothetical cases, forced E2E/full-suite evaluation, duplicate Pi functionality, installation,
ongoing infrastructure or documentation bureaucracy. Mechanism must stay simpler/cheaper than
the problems. Future real-case representativeness and stochastic reliability remain unproven;
a once-per-version observation is bounded evidence, not statistical assurance.

This source creates no implementation tasks. Fresh independent read-only intent review precedes
separate task production, planner review and combined approval. Later task production consumes
`/home/dev/.paseo/worktrees/0zfm1a0e/joyous-manatee/.pi/workflow-executor.json` directly; this source
does not choose implementation models. Carry A1–A5 into task-local REQUIRED evidence/briefs,
with A4's exact-amendment approval gate before policy mutation. There is no technical prototype
producer/consumer prerequisite or hidden live-evaluation dependency. Implementation and real
issue evaluation remain separate from this bounded source-production checkpoint.
