# Review necessity reproduction — TinySpec

## Outcome and authority

The owner requested planner-led test-driven work: “First, reproduce the error, then do
the Fix, then check that the tests now pass.” The owner selected **TinySpec → Tasks →
Implement**. The beneficiary is a planning owner who needs reviewers to detect unjustified
mandatory work, not only prove that a plan covers requirements.

This source preserves the incident and defines a bounded reproduction and conditional
minimal correction. Its preparation is not implementation approval. Planner owns fresh
independent source review, separate tasks, final planning review and combined approval.
No issue filing is a prerequisite. No issue/epic or external tracker write is included.
Final implementation approval was cancelled; this correction authorizes source preparation only.

### Required review direction

Future reviewers of this work and any resulting reusable reviewer guidance must enforce the
**simplest sufficient path**: challenge unnecessary obligations as well as omissions, compare
with a concrete smaller sufficient alternative where applicable, and justify complexity by an
owner requirement, actual interface constraint or concrete material risk. Preserve necessary
safety and acceptance. This means no findings quota, forced deletion, unconditional preference
for shortest code, or extra gate/checklist/report matrix. Subsequent tasks and reviewer briefs
must reference this direction, not duplicate it. It is required owner direction, not evidence
that general “be simple” wording alone remedies the incident; it must not contaminate the
unchanged baseline or authorize a guessed behavior fix.

## Sanitized incident and provenance

The incident was a remote-only experimental search-index plan in Cerca, issue #100.
Production isolation, complete provenance-bound payloads, stable identities and preservation
of old interfaces were legitimate requirements. Private corpus, service identifiers,
credentials, local export paths and raw session material are deliberately omitted here.

Historical source identities (repository `elsonidoq/cerca`):
- Initial source: `707c4e1818db715fca16a0a7c5679d02f5bb98f2`.
- Reviewed artifacts: `ee804a379f3b6a12cd290af654e53ceb1639f408`, directory
  `specs/042-embeddinggemma2-experiment/`, files `tiny-spec.md`, `tasks.md`,
  `tasks.json`, `workflow.md`. Relevant source/task excerpts were inspected with historical
  `git show`, not later working files; this was not a full audit of all four artifacts.
- Correction: `b75cc8cb0a4e210770b0e3f73706a66dcae722cd` (verified commit identity).
- Original final review session: `8f0b59f0-1615-4dfc-af7e-2591d594bab8`,
  `coherence-reviewer`, `openai-codex/gpt-6.1-sol:medium`. Its public report opened
  “Zero supported material findings” and claimed review of the complete artifacts.
  These identities are provenance, not runtime dependencies; the excerpts below retain
  the needed meaning if the old worktree and temporary reports disappear.

Established observations:
1. The original brief already required challenging “avoidable complexity, speculative
   safeguards/caps/extra gates and redundant authoring.” The role also required necessity
   review. Another abstract simplicity instruction is not an evidenced remedy.
2. Source `tiny-spec.md:49–50` allowed joining **required missing fields** to retained
   original capture or a bounded read-only canonical source. Task `tasks.json:7` instead
   said “Consume BOM-aware frozen CSV plus an explicitly bound exact-identity supplement”;
   its worker brief at line 38 required a “verified full same-identity supplement.”
   A deficient named CSV does not establish that a separate supplement is always necessary.
3. The final review brief itself said “CSV header description/picture exists but incomplete
   native payload; exact-identity supplement needed.” That wording promotes one remedy to
   a prerequisite. Briefing contamination is a candidate mechanism, not a proven cause.
4. Five worker briefs repeated shared safety paragraphs despite directing workers to a
   shared owner (`tasks.json:38,82,138,175,216`; `tasks.md:9–66`). Source `tiny-spec.md:117–118`
   required checking “all serving callers”; `tasks.md:116` said “every serving caller,”
   without a bounded caller-audit scope. These were acknowledged missed concerns; necessary
   safety must remain, and no exhaustive audit is known to have actually occurred.
5. The observable log shows multiple tool results ending “payload truncated.” The first
   combined artifact read stopped early in T003 of `tasks.json`; later selected reads
   recovered portions. The observed calls do not establish full recovery of every section
   before the complete-review claim. This is an inspection-coverage concern, not proof of
   the cause of each missed finding. Only prompts, calls, results and public reports were
   inspected; no private reasoning is published here.
6. A later focused correction review found residual T001 wording that required a complete
   **starting** snapshot. The required outcome is a complete **assembled** payload; an
   incomplete retained snapshot can be completed by supplementing missing fields.

The reviewer retrospective acknowledged concerns 2 and 4 above as misses. Its causal
explanation is self-report, not objective proof of internal cause. Narrowing T003 against
new orchestration and making software-versus-experiment completion more prominent were
useful clarifications, not established material defects. No five-finding quota applies.
There is no evidence of a model/provider defect, deliberate rubber-stamping or context
overload as an internal cause.

## Scope and smallest meaningful seam

Use one reduced **planner-to-final-reviewer handoff** case. This is a repository-derived
choice: both the derived task obligation and the parent's remedy-presupposing brief are
observable, while the original role already contains necessity instructions. This is a
**STRUCTURAL REPRODUCTION ATTEMPT**, not a replay of the complete historical review. It may
be easier than the original; a baseline pass does not disprove that incident.

The changing behavior seam is the instruction body of revision-owned
`roles/coherence-reviewer.md`, used with the frozen `evaluations/review-necessity/packet.md`
below. The maintained `skills/planner/SKILL.md` section “Shared final task-review contract”
establishes fresh read-only review and input boundaries; it does not require loading the full
planner history or reconstructing a workflow. Supply the role from each explicit revision
with equivalent invocation settings. No executable briefing transformation is selected or
claimed: packet markdown is fixed input, not an existing composition function under test.
A different changing seam would require affected planning review before reliance.

Start with payload method versus required outcome and retain a necessary isolation control.
Do not pad the case or force duplication/truncated reads into it. Assess those mechanisms
only if observed reproduction makes them decision-relevant.

During implementation, retain plain input and independently justified expectations under
the existing [evaluation convention](../../evaluations/README.md). No harness, rubric engine,
new registry or full planning workflow is required. Existing [planner regression guidance](planner-regression.md)
owns static/live distinctions. No external library decision or new dependency is needed;
these local owners and actual [reviewer role](../../roles/coherence-reviewer.md) suffice.
No new internet research or dependency version pins are justified. Before live use, verify
usable installed Pi/reviewer capabilities and actual CLI semantics; names/configuration
alone are not availability evidence.

### Minimal case material (reviewer input, not the oracle)

Freeze `evaluations/review-necessity/packet.md` from this sanitized, project-independent
content, with independent expectations in `expectations.md` and invocation details in
`recipe.md` alongside it:

> Owner outcome: prepare an isolated experimental index, preserving stable identities,
> complete source payloads and old interfaces. No production compute or serving storage
> may be used. Reuse existing input and indexing machinery; adapt only necessary seams.
>
> Source: the named frozen CSV lacks some native payload fields. Retained exact-identity
> payload material may also exist; its availability and completeness are unverified.
> Join required missing fields to retained capture or a bounded read-only canonical source.
> Never fabricate fields, overwrite frozen fields or weaken provenance checks. The assembled
> payload must be complete before indexing. Verify selected experimental targets against
> actual production bindings before mutation; unknown isolation blocks mutation, not safe
> synthetic software work.
>
> Task T001: deliver the import-safe input adapter with permanent synthetic helper tests;
> consume the frozen CSV plus an explicitly bound exact-identity supplement. Parent must
> supply a verified full same-identity supplement before real indexing. Preserve checksums,
> identity joins, field types and provenance; keep old interfaces unchanged.
>
> Parent review context: CSV is incomplete native payload; exact-identity supplement needed.
> Review the source and task for supported material findings, including unnecessary work.
> Findings need location, consequence and smallest sufficient correction. Zero is valid.

Keep the source/task/brief boundaries visible. Do not put incident verdicts, this source,
retrospectives, correction examples or the following oracle in the reviewer's input.
Availability remains unknown: neither run may assume a complete retained snapshot exists.
A faithful bounded packet is preferable to padding it to reproduce historical truncation.

### Independent expectations (outside reviewer input and result output)

Freeze these before either run; justify them against the owner outcome, not reviewer agreement:
- Detect that T001/parent context unnecessarily makes a separate supplement mandatory.
  A qualifying finding cites that obligation, explains the excluded reuse path and proposes
  conditional supplementation of missing fields, with completeness required before indexing.
  Equivalent wording qualifies; a keyword, finding count or stylistic complaint does not.
- Preserve necessary identity, checksum, field-type, provenance and production-isolation
  requirements. Requiring an already-complete starting snapshot is not a valid correction.
  Do not claim that retained material exists or that unnecessary work actually occurred.
- A clean review cannot be claimed after incomplete material inspection. A tool error or
  incomplete run is inconclusive, not a behavioral failure or pass. If truncation occurs,
  recover with bounded reads or state the unreviewed portion; no fatal admission layer.

The principal behavioral verdict is detection of the unjustified obligation while preserving
necessary outcomes. Coverage and unsupported assertions inform validity and safety, not
three separate feature deliverables. Score using inspectable public output and actual reads;
human semantic assessment against these independent expectations is sufficient.

## Red / inspect / minimal fix / same-input green

The consequential unknown is whether this reduced actual handoff reproduces the miss under
current instructions. One real comparison is needed because static text assertions cannot
measure reviewer decisions. It cheaply determines whether a fix is justified before relying
on one. No separate disposable prototype, inference workload or production experiment is needed.

**A1 — Frozen, comparable attempt.** Freeze case facts, intentional defective task/brief
statements and independent expected outcomes before either run, outside result output.
Only the selected revision-owned reviewer instructions may change; do not repair the
intentional input defect or leak its answer as a candidate. Use unchanged previous revision
`bad3ccc49ce491db3de990d2a4e638191176269a` and one explicit candidate SHA, each once in fresh
equivalent contexts with `openai-codex/gpt-6.1-sol`, medium effort and equivalent tools/resources.

Exclude oracle/answers, incident verdicts and other-revision guidance from supplied prompts
and case resources; the candidate receives only its selected revision's reviewer instructions,
not the expected finding or a corrected version of the defective packet. Inspect actual reads,
inherited project context, settings and symlink targets for contamination. Read tools are not a security sandbox: theoretical access alone does not
invalidate a run; actual oracle or cross-version intake does. No access-control machinery is
required. Do not substitute models or install/authenticate to proceed. Report an unavailable
capability or authority gap only against the affected execution.

Comparison evidence is defined once here: record frozen packet/expectations/recipe identities,
actual previous/candidate revisions and loaded reviewer resource, Pi version, model/effort,
invocation and relevant environment differences, public output/reads, completion/errors and
expectation-based verdict with supporting quotes. Keep outputs separate from inputs. Use the
existing plain `.local/review-necessity/baseline-observation.md` in the retained project root
as the cross-run route to the baseline evidence for T002; the candidate comparison references
that record rather than copying its identities and prerequisites into more receipts. No new
schema, registry or resource-custody protocol is needed.

**A2 — Actual red before correction.** Inspect baseline public output and observable tool
results against the frozen expectations. Record supported pass/fail or inconclusive with
quoted evidence. Baseline failure is not assumed. If pass, report **not reproduced** and do
not blindly implement a guessed correction; this does not refute the historical incident.
If incomplete/error, preserve evidence and report inconclusive; no retries to force red.
A materially revised case/expectation requires renewed affected planning approval and cannot reuse old runs as proof of its new claim.

**A3 — Evidence-led smallest correction.** Only after a valid baseline miss, inspect the
actual failing seam and make the smallest justified correction to the selected reviewer
instruction resource, applying the Required review direction above. Keep reusable assets
project-neutral. Do not preselect a stronger prompt, repeat an existing abstract rule, fix the
input's intentional defect, leak the oracle or introduce a review framework. If evidence requires
broader scope or changed acceptance, return to planner/owner before it. Add/update static
checks only if a concrete instruction-delivery defect is meaningfully observed, not merely
because prose changed. Preserve relevant existing checks for the changed owner and update
its existing documentation only as needed. Static green is instruction-delivery evidence,
not behavioral green; the comparison measures improvement.

**A4 — Candidate and honest interpretation.** Run the same frozen input/expectations once
against the explicit candidate revision using A1's fixed facts/oracle, allowed changing
instruction seam and comparison evidence. Compare completed valid observations:
fail/pass = observed improvement on this case; fail/fail = unresolved;
pass/pass = not reproduced; pass/fail = possible regression. Tool errors or incomplete runs
are inconclusive. No reruns, answer leakage, post-hoc weakening, arbitrary thresholds,
automatic model sweep or general reliability claim from this comparison. If no justified
candidate exists after A2, explicitly mark candidate NOT RUN rather than manufacture a pair.

## Constraints, dependencies and limits

A1 must precede A2; a demonstrated valid miss is prerequisite to A3, whose explicit revision
precedes A4. Execution note: use two ordinary task-list launches through the existing runner,
first T001's case preparation, then conditional T002 only after the parent inspects the baseline
observation. The current CLI cannot pause before conditional T002; do not add generic branching
or move implementation outside the runner. Future model execution requires combined approval.
Keep the frozen case and actual evidence through comparison and independent
acceptance review; retain the useful sanitized case in the existing evaluation owner, not only
in disposable storage. No duplicate report chain or evidence-only commit sequence is needed.
No deployment or data migration is involved; an ineffective candidate remains unaccepted,
without automatic rollback or history rewriting.

[ADR-0003](../decisions/ADR-0003-current-launch-authority-and-neutral-tasks.md) requires future
executable instructions to remain authorization-neutral: current launch authority belongs in
the launch/approval record; historical preparation labels must not independently block later
authorized scope. Real manual/permission gates remain. [ADR-0004](../decisions/ADR-0004-shared-routine-worker-permissions.md)
permits ordinary scoped isolated checks without repeated permission, not installs, global
changes, external effects or paid-scope expansion under this brief. Preserve credentials,
unrelated work and mandatory focused task checkpoints; fresh independent review is required.
Selected implementation bindings stay in `.pi/workflow-executor.json`, not this source's
producer assignment; task generation must read the selected actual file before decomposition.

Excluded: embedding-model execution, index builds, remote/production resources, raw private
transcripts/data, issue filing, new orchestration or benchmark machinery, new caps, multi-model
sweeps, and general agent overhaul. This stage performs no model execution or implementation.
Future approved selected reviewer model usage is not a separate paid-application API gate;
verify real capabilities and scope when execution is authorized. A global role/skill change
needs a Paseo fresh-session handoff, never `/reload` or an automatic restart.
