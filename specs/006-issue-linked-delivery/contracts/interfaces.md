# Interface contracts

Proposed implementation contracts derived from [current spec](../spec.md), not current
runtime claims. Proposed names/fields and transport mechanics may use simpler equivalents
under the [design boundary](../plan.md#requirements-versus-proposed-mechanisms), preserving
existing consumers and required outcomes. [Plan](../plan.md) owns sequencing/policy proposals;
[research](../research.md) owns exact dependency applicability and evidence limits.

## CLI and attached parent

Keep `scripts/coordinate-implementation` and existing actions: intake, start, status,
history, resume, recover-task, abandon, authorize-routine-repairs and refresh-review-target.
Keep original project/run/executor addressing and actual failure diagnostics. An empty task
list creates no storage or provider call. Intake remains exactly the six current checks.

- `start --project ROOT --tasks FILE --executor CONFIG [--run ID] [--parallel]`:
  sequential unless the coordinator passes `--parallel` under actual owner concurrency
  direction. Retain this selection with original run input. The flag does not itself
  establish owner permission; it selects how authorized work executes. Disjoint paths and
  effect safety are checked at the affected wave/mutation, not a new task-file linter.
- Parent `coordinate_implementation_start` adds optional `parallel: boolean`, start-only.
  Existing `tasks`, `executor`, `run`, `resume`, `recovery_action` and `diagnosis` retain
  their meanings. Resume uses the recorded mode/executor, not a changed config file.
- Optional top-level `delivery_issue` is a qualified issue URL. Skills propagate it; bare
  task lists remain valid. Missing issue access blocks only the relevant tracker action.
- `resume --project ROOT --run ID` resumes the latest graph checkpoint. A pending interrupt
  is presented through the actual terminal or attached-parent question consumer. Use
  `Command(resume={interrupt_id: answer})` when mapping multiple pending branches; never
  feed an answer to a different task or use checkpoint time travel as recovery.
- Noninteractive/no attached answer leaves a durable paused run and an actionable message:
  “Run RUN is waiting for QUESTION_ID; resume interactively or through the attached parent
  to answer the pending operation.” Do not expose private question content in safe history.
- `--recovery-action continue|fresh|escalate --diagnosis TEXT` remains inspected coordinator
  recovery. Unknown causes/effects stop; a failed explicit implementation escalation retains
  its owner-direction stop. Routine correction is not a repeated approval request.
- Existing external completion transfer and review-refresh actions feed reconciled results
  into graph state while preserving original scope, actual checks and fresh review. No
  resets, implicit adoption or broadened #28/#43 repairs.
- Legacy execution actions return a concrete compatible-runtime diagnostic before mutation:
  “Run RUN is legacy, not a LangGraph thread. Inspect its saved call and use
  LEGACY_SUITE/scripts/coordinate-implementation resume --project ROOT --run RUN from the
  retained pre-cutover revision 4c1725ebded2f89dec6933b8d193bf34997c62ce with its compatible
  dependencies.” Substitute the requested action and its existing arguments as appropriate.
  `LEGACY_SUITE` is an operator-selected retained checkout, never an automatically created
  path or downloaded executable. Status/history still read legacy records.

Parent reply tools retain `run`, `request_id`, `answer` and owner-only separation. Map the
current request to a framework interrupt; preserve IDs across one outstanding question,
and re-establish a live bridge request on reopen without changing the underlying question.
Serialize interactive questions if several branches wait. Replace the bridge's singleton
steering target with an exact-target map; route steering only to matching
run/task/invocation/session/role. Closed/stale targets report unknown or rejected, never
broadcast to another worker. Routine status remains non-waking; questions and terminal
completion retain existing notification behavior.

## Pi question pause and continuation

A question must survive a durable graph pause and reach the actual affected operation on
resume. Preserve current callers, correlated target identity and owner-only reply separation.
An unavailable answer stays pending; denial performs no gated effect. No synthetic answer,
rerun of a settled provider/tool effect or redispatch of an uncertain call is permitted.

The proposed `pauseQuestions` / `waiting` adaptation and SDK settlement rationale live in
[plan](../plan.md#questions-reach-the-actual-consumer); do not treat those spellings as owner
requirements. The external observable is settled safe pause, reopen and real answer delivery
to the correct retained task context, with independently identified subsequent invocation
usage. [Quickstart](../quickstart.md#composed-execution-and-recovery) owns the actual-boundary
proof required before reliance. No live callback is assumed recoverable after process loss.

## Local monitoring configuration

Monitoring is opt-in and metadata-only; application execution does not depend on exporter
availability. Proposed settings in `runtime/phoenix.env.example` and launch instructions in
existing `docs/coordinate-implementation.md` use one Docker container, not Compose or a new
service manager. These paths are future implementation outputs, not created by this plan.

- Workflow config explicitly enables monitoring and selects
  `http://127.0.0.1:6006/v1/traces`; UI is `http://127.0.0.1:6006`.
  Use a numeric loopback address, explicit port and exact OTLP path. Do not inherit OTLP
  endpoint/proxy/headers or hosted graph tracing from the environment. Nonlocal settings
  refuse export with a safe corrective message; they do not block otherwise safe execution.
- Pin the official Phoenix 21.0.0 image by the digest in [research](../research.md#sources-and-minimal-deployment).
  Publish only `127.0.0.1:6006:6006`. Container-internal HTTP binding must accept that mapping;
  do not use host networking, publish-all, gRPC/Prometheus ports or remote collectors.
  `PHOENIX_TELEMETRY_ENABLED=false`, `PHOENIX_ALLOW_EXTERNAL_RESOURCES=false`, and
  `PHOENIX_WORKING_DIR=/data` are explicit container settings. Do not pass through the host
  environment, cloud credentials, provider integrations or external-resource configuration.
  The privacy flags also suppress automatic model-price downloads; check actual behavior.
  Retain the image's authentication default for its non-loopback container bind; use local
  Phoenix credentials only, privately stored with documented recovery, never in Git or
  telemetry. Explicit local authorization is the only allowed credential header; no inherited
  auth. This is ordinary local setup, not a hosted-account approval ceremony.
- Proposed durable private bind directory:
  `${XDG_DATA_HOME:-$HOME/.local/share}/coherence/PROJECT_KEY/phoenix`, where `PROJECT_KEY`
  is the project's explicit stable local identifier, not a disposable worktree name.
  The local project maintainer owns the directory and its access. Document the selected
  absolute path, image pin and ordinary restart/recovery command in existing project operating
  guidance; recover by reusing that same owned SQLite volume, not creating an empty replacement.
  Keep source/config in Git and private database bytes out of Git. Verify directory ownership
  and image-user write access at setup, without broad permission changes or adoption of
  unknown bytes. A known existing directory is reused only after confirming its owner/purpose.
- An occupied port, foreign container or ambiguous data directory stops affected local setup
  with the collision and corrective choice; do not stop, overwrite or silently adopt it.
  Missing Docker/access is an affected setup gap, not a global execution/startup gate or
  authority to install globally. Ordinary future scoped setup needs no new consent ritual.
  No automatic shutdown, deletion, expiry, retention purge or resource ceilings.

The adapter's safe IDs and attributes map run→task→invocation, role/model/status/time and
known invocation-local usage/cost. No raw input/output/error/path even locally; no baggage or
automatic exception/status text. [Research](../research.md#standard-adapter-and-concrete-privacy-seams)
owns final transport/resource controls. Export completed small boundary spans while the run
continues. Do not promise display of an open span or root-only completion as progress proof.
Actual local UI observation is the removal prerequisite, not another approval question.

## Delivery issue and acceptance

Use the project's declared owner and `track-open-issue` capabilities/target/authority rules;
no new tracker client/service. Direct planner intake has no issue prerequisite. Associate
an existing issue after understanding or create the requested issue when authorized; carry
its qualified URL through current artifacts, task context and coordinator handoff.

After checks/checkpoints/fresh independent review, use the same meaningful executive text
in issue and chat, with these content elements (not a rigid API schema):

- outcome and important changes;
- actual verification and unrun/failed limits;
- what the owner should inspect;
- exact presented commit, attributable task/repair links and unrelated context limits;
- awaiting explicit acceptance, or the actual acceptance/correction record.

Classify each correction by purpose, not just time/author: approved implementation/internal
review fix, owner-review correction, or new/changed requirement. New requirements renew
applicable approval; corrected delivery gets a new exact summary/review commit. Do not
attribute all commits in a range to the issue. Read back comment/label/closure effects before
reporting them. If issue publication succeeds and chat delivery fails (or vice versa), report
the partial result and retry only the missing operation after inspection; no false delivery.

Normal coordinator/finish-session delivery publishes after actual checks and fresh independent
review, then awaits real feedback/acceptance. Corrections and closure are conditional real
branches, not a worker demonstration. Unobserved branches are NOT VERIFIED, not passes; do
not manufacture corrections, unrelated issues, acceptance or closure to exercise them.

Explicit acceptance identifies the presented revision. It does not automatically authorize
RCA, a skill edit, PR or acceptance of later changes. Close only with actual closure authority
and readback, retaining the acceptance trace even if closure is unavailable.

### Issue #44 final skill-diff gate

At this migration's normal final delivery review, after implementation, specified checks and
fresh independent technical review, present **one combined complete actual net patch** for
T001/T002/T003/T015/T016's changed skills (eight existing and one new) and any actual
task-authorized coupled skill references/scripts/tests. Include additions, deletions and
modifications, not just `SKILL.md` edits. Identify exact Git baseline, reviewed commit,
attributed paths and contributing task/repair commits. Inspect attribution; exclude unrelated
or concurrent changes rather than blindly presenting a Git range as this task's work.

Show the full patch through normal chat/host diff presentation; a file list, links or summary
alone does not suffice. Publish the normal evidence with “awaiting owner skill-diff approval”
when pending; do not wait for approval before showing what must be approved. Record the actual
owner response and its patch identity in the existing issue/chat trail under existing tracker
authority/readback. No automatic browser viewer, push, PR, required patch file or new registry.

Until explicit owner approval, this issue's delivery DoD/completion/acceptance and closure
remain pending. Plan approval, green checks and agent review are not owner skill approval.
Normal verified task checkpoints, technical review and internal runtime completion may finish
first. No worker failure solely for this pending final gate, repeated task-by-task confirmation,
new orchestration state machine or global/adopting-project skill policy is required.

Reuse precise prior owner approval for unchanged skill content. Later affected skill edits
renew only affected approval; unrelated commits alone do not invalidate it. Skill approval is
not overall delivery acceptance or closure authority. Natural feedback, unobserved branches
and the delivery/closure rules above remain intact.

### Issue #44 functional evidence

Supply one concise owner/reviewer-inspectable package of actual non-skill behavior with the
final skill patch. Show actual browser-rendered local Phoenix captures at successive moments
of an evolving representative CLI run **before root completion**, with hierarchy and progress;
a mockup, generated image or only a finished trace is not a substitute. Readable actual CLI/
terminal output must show dependency execution/checkpoints, pause/restart/actual reply,
explicitly authorized parallel work/accepted join and relevant real Git commits/results.

For each shared demonstration, state exact application and reviewed revisions, actions,
expected/observed results and limits, reproduction commands and local URL/access instructions
without secrets. Label actual SDK deterministic fixture-provider runs as local-mechanism proof,
not live model judgment. Captures supplement required runtime/recovery/privacy/security tests;
missing proof is NOT RUN, UNAVAILABLE or FAIL, never a pass from scheduled checks. Skill-diff
approval, overall acceptance and closure authority stay distinct; no screenshot approval ritual.

**Producer/consumer reuse:** T011's public CLI boundary supplies initial readable functional
output; T013 supplies the authorized parallel/join extension. T017 consumes applicable evidence
and closes composed execution/recovery gaps with the smallest shared run, not repeated task
demos. T020 uses coordinator browser capture for the required real evolving local UI run;
T021 consumes that proof before removal and supplies only changed post-removal CLI/history
observations. T019 retains its actual assessment results/links under its existing tracker gate,
not a forced extra browser scenario. No fifteen-task matrix, feature replay or new proof task.

**Capture and retention:** Existing `docs/evidence/` subject directories establish an evidence
convention, but inspected `host.mjs` write/edit hooks claim UTF-8 writes and `FocusedGit.checkpoint`
selects claimed edit paths, not arbitrary external binary output. Do not assume a parent screenshot
will enter a worker commit, fake an edit/claim, or expand #28/#43 transfer work. Select the existing
project-owned durable local storage convention instead: a sibling `evidence/issue-44/` beneath
`${XDG_DATA_HOME:-$HOME/.local/share}/coherence/PROJECT_KEY/`, outside disposable worktrees and
separate from Phoenix database/credentials. The project maintainer owns these captures/results.
Retain them with the generating outcome, linking its actual task checkpoint/application revision
and explicit persistent asset paths in the existing issue/chat evidence trail. Reproducible source,
configuration and any necessary test-script changes still use ordinary task-owned Git checkpoints;
external-only captures create neither an empty nor an evidence-only commit.

The parent reports registered `chrome-devtools_screenshot` with optional `filePath`. Use the
existing parent/coordinator capture capability, not an assumed worker MCP tool. At capture time,
verify the browser can render the local UI and persist actual screenshot bytes to the selected
path (or copy its returned capture there), then verify owner/reviewer access. Registered tool
presence is not proven usable browser/capture access; inability is an actionable evidence gap,
not authority to install a browser framework. No browser or capture was run during planning.

Use approved metadata only. Exclude sensitive paths, credentials and private prompts/responses/
errors; disclose cropping/redaction without changing or fabricating behavior. Existing local
storage ownership/recovery guidance must identify the actual evidence directory and how to reopen
its assets after the session/worktree ends; concise existing issue/chat links describe access and
observations, not a new manifest, registry or archive service. Do not rely only on transient tool
attachments or `/tmp`, publish externally without authority, or force shutdown/cleanup.

## Manual assessment

Entry: `/skill:assess-skill-improvements` in a host supporting normal skill invocation;
otherwise load that skill explicitly through the host's normal mechanism. It runs only on
an owner request, never at delivery completion/acceptance.

Resolve the declared GitHub target. Read all pages using the existing pattern
`gh api --method GET --hostname HOST --paginate "repos/OWNER/REPO/issues?state=all&per_page=100"`;
exclude records with `pull_request`. Read all relevant comment pages, linked artifacts and
supported commits for the selected assessment set. Do not substitute search-result limits
or open-only listing for complete discovery. Report access/page failures as incomplete
discovery, not an empty set. Allow explicit repository/issue selection by the owner; do not
silently sample discovered matches. Reassessment can explicitly select already labelled issues.

Default state labels, when equivalent existing labels are absent:

| Label state | Meaning / write condition |
| --- | --- |
| None of the three | Unassessed; open or closed and accepted or unaccepted can be selected. |
| `skill-assessment:proposed` | Evidence-backed analysis/proposal presented; no claim of implementation. |
| `skill-assessment:no-change` | Assessment delivered with rationale, including explicit uncertainty or insufficient evidence if applicable. |
| `skill-assessment:addressed` | Approved improvement actually delivered; link its exact implementation/verification evidence. |

Create/apply labels and issue comments only with scoped tracker write authority. Update only
assessment labels; preserve unrelated labels/content. If conflicting states already exist,
inspect the issue trail and correct only with known current evidence and authority. For a
grouped proposal, link source issues and its existing planning/delivery destination; mark a
source addressed only when that source's proposed change is delivered. Partial write failure
must not be reported as a complete transition. Do not allocate a new ledger or require a
new issue for every cause.

The response/issue trail distinguishes original intent, approved source/tasks, observed
feedback/correction effects, changed requirements, supported omissions (planning/task/
implementation/review), unnecessary workflow complexity, and uncertain attribution. Missing
approval or acceptance records are evidence gaps, not automatic exclusions. Proposed changes
must be minimal and owned by existing skills; project-specific learning stays local unless
portable guidance is actually justified and approved. Existing planning/implementation and
separately authorized PR routes handle delivery; the assessment skill cannot self-edit.
