# Epic: Measurable, bounded Jev assistance in coding-agent skills

## Source and admission

- **Source:** Owner decisions in the conversation requesting a Jev optimization epic: all four proposed global-suite skills and all four proposed SpecKit skills, excluding `compact-memory` for now. The owner requires Pi-specific, easily retrievable counts of Jev use and main-agent acceptance before enabling optimizations, without running a benchmark yet.
- **Beneficiary:** A Pi user who wants to know whether bounded Jev suggestions are actually used while retaining the coding model's engineering judgment.
- **Sizing:** Full epic pipeline warranted: at least eight independently verifiable skill integrations plus a shared metrics harness; the Pi-to-SpecKit ownership/distribution and disposition-recording contracts require material design; work spans the global skill suite, Pi extension, and project-installed SpecKit skills. This is an admission verdict, not permission to run a SpecKit pipeline that is absent from this repository.
- **Current state:** Brief only. No Jev integration or metrics harness is implemented by this epic's creation; no benchmark has been run.

## Outcome and boundaries

A Pi extension records Jev invocations and the main agent's explicit disposition of Jev-proposed decisions. After using any optimized skill, the user can retrieve session totals and per-skill totals without asking the model to remember or sum them. Each optimization narrows an explicit candidate set; it never makes architecture, root-cause, code generation, final correctness, owner authorization, or irreversible decisions. The full candidate set and original skill behavior remain available. No global tool routing.

The metrics harness is the **first delivery dependency**. A Jev-optimized path must not be enabled until its invocation and proposal/disposition events can be captured or its untracked state is made explicit to the user. A failure to instrument must not silently produce a misleading zero.

### Metrics contract to specify before implementation

- Count **Jev invocations** as attempted calls through the instrumented Pi integration, including failures; report successful calls separately so attempted use is not confused with usable output. Define a stable invocation ID, skill ID, session ID, result status, and timestamp.
- Count **proposed decisions** as individual typed choices or ranked candidates emitted by a successful Jev call. One batched invocation may yield many proposals; do not equate proposal count with invocation count. Define the unit for a ranking explicitly (for example, one shortlist recommendation versus one score per candidate) and keep it stable per seam.
- Count a proposal as **accepted** only when the agent emits a structured disposition referencing that proposal ID after using it in a decision. Also track `overridden`, `not_used`, and `pending/unknown`. A Jev result, confidence score, silent continuation, or model prose alone does not prove acceptance. Totals never treat pending as rejected or accepted. The agent emits events; the harness performs counting.
- Provide a Pi-native, easy-to-use retrieval path such as `/jev-metrics`: display session totals and per-skill attempts, successes, proposals, accepted, overridden, not used, and pending, with clear denominators. Determine whether cross-session retrieval/export is needed during planning; session retrieval is required. Never claim to observe uninstrumented CLI/MCP calls.
- Avoid recording raw candidate text, logs, secrets, personal data, or API credentials in telemetry. Define session/branch and reload behavior, duplicate-event handling, malformed events, unavailable Jev, and failed calls. Instrumentation must not force a Jev call or block manual fallback.

## Candidate skill seams

Each seam begins in shadow/advisory mode with visible fallback. The main model verifies consequential outcomes; scoring confidence is not assumed calibrated. Prefer ordering over hard exclusion and treat low-confidence or ambiguous cases as main-model work. Initial low-risk acceptance may use a conservative `>= 0.90` threshold, subject to later calibration; high-impact decisions never pass automatically.

| Skill | Bounded Jev proposal | Main-model fallback and non-negotiable work |
| --- | --- | --- |
| `scientific-method-debugging` | Rank chunks from a large observed log/test output by relevance to the active failure. | Retain the complete output; investigate ambiguous and low-ranked evidence when needed. Main model forms and tests root-cause hypotheses. |
| `receiving-code-review` | Batch-rank many review comments for investigation priority, flagging ambiguous/high-impact items. | Every comment receives evidence-backed disposition by the main model; no Jev rejection of a finding. |
| `coordinate-implementation` | Rank an explicit list of existing targeted tests by diagnostic relevance to the current batch. | Main model chooses when uncertain; required affected and final acceptance checks remain mandatory. |
| `track-open-issue` | Rank existing issue entries by possible overlap with a verified new issue. | Keep the full register; main model checks likely matches and decides whether to create/update. |
| `speckit-analyze` | Rank candidate requirement–task associations and low-risk cross-artifact findings for deeper inspection. | Preserve full inventories; main model verifies coverage, severity, conflicts, and all constitution alignment. |
| `speckit-checklist` | Group near-duplicate candidate requirements-quality questions and rank inclusion candidates when the set is large. | Main model reviews exclusions and preserves required, high-risk, and owner-requested coverage. |
| `speckit-clarify` | Rank explicit ambiguity/question candidates when more candidates exist than the five-question limit. | Main model selects questions and handles all material owner decisions, especially security, privacy, and architecture. |
| `speckit-tasks` | Batch-rank likely user-story matches for each entity or interface contract. | Preserve all items; main model assigns stories and designs tasks, sequencing, and dependencies. |

## Evidence and constraints

- Global workflow and fallback rules: `skills/scientific-method-debugging/SKILL.md` (Steps 2–4), `skills/receiving-code-review/SKILL.md` (Evaluate Feedback), `skills/coordinate-implementation/SKILL.md` (Execute and Integrate), and `skills/track-open-issue/SKILL.md` (Record in the Local Register).
- SpecKit examples inspected at `/home/dev/projects/cerca/.agents/skills/speckit-{analyze,checklist,clarify,tasks}/SKILL.md`: analysis builds requirement/task mappings and caps findings at 50; checklist consolidates candidate items above 40; clarify limits questions to five; tasks maps entities/contracts to stories. These are **project-installed external assets**, not files owned by this repository. Detect the target project's actual installed toolkit before integration; obtain authorization and determine a portable distribution/patch strategy rather than assuming those paths on another machine.
- `skills/finish-session-jev/SKILL.md` already includes optional Jev triage and per-closeout reporting, but does not implement a Pi-wide invocation/acceptance counter. Its documented `jev pick` example and `~/.agents/skills/jev` dependency in `REQUIREMENTS.md` should be checked against the installed `jev-cli` capability before reuse; do not assume that example is an available interface.
- Pi extension documentation at the installed `docs/extensions.md` supports model-callable tools, event handlers, non-context session entries, and commands. A hook observing Jev use can count calls; it **cannot infer semantic agent acceptance** without an explicit disposition contract. Instrumented tool calls are the reliable coverage boundary; raw shell/MCP Jev use may remain untracked unless deliberately integrated.
- `jev` is discoverable at `/home/dev/.local/bin/jev` in the inspection environment. Presence is not evidence of authentication or availability in another project. If unavailable or unauthenticated, retain manual skill behavior. Do not install tooling or transmit sensitive payloads implicitly.
- The owner supplied evidence of mixed whole-agent Jev benchmark results and requested skill-local optimization rather than global steering. Those results motivate conservative boundaries, not a predicted gain for this repository.

## Decisions and design questions

**Settled:** All eight named seams are in scope; `compact-memory`, global tool steering, benchmark execution now, and irreversible/deployment actions are out of scope. The Pi harness and easily consumed usage/acceptance counts precede activation. Jev only reduces candidate width; the main model retains deep reasoning. No raw sensitive telemetry.

**Open for specification/planning:** (1) How a Pi extension exposes an instrumented Jev interface and structured per-proposal disposition without making the agent manually maintain counters; (2) where local metrics live and whether cross-session export is required beyond the session command; (3) how changes to project-installed SpecKit skills are sourced, authorized, tested, and distributed without hard-coded project paths; (4) how to define acceptance for rankings, partial acceptance, and abandoned/pending proposals. These materially affect the interface and ownership; do not silently choose them in implementation.

**Mechanical:** Provide stable proposal IDs, schema validation, duplicate-event protection, explicit coverage limitations, manual fallback, and deterministic fixture-driven tests for counter arithmetic and display. Do not create a task merely to re-investigate a source claim already verified above.

## Acceptance criteria

1. In Pi, after an instrumented skill attempts Jev once and receives three proposals, the metrics view shows one attempted invocation, one successful invocation, three proposals, and zero accepted until dispositions are emitted.
2. If the agent accepts two of those proposals, overrides one, and records each disposition once, the view shows two accepted and one overridden; duplicate events do not increment counts. A partial ranking acceptance uses the explicitly documented unit and rule.
3. Failed Jev calls count as attempts but not successful decisions; malformed/unavailable results invoke the existing manual behavior and do not produce false accepted counts.
4. The Pi user can request readable metrics after a skill run without requiring the model to recount messages; results identify the skill, session, denominators, pending items, and whether any Jev path was uninstrumented.
5. Each approved skill seam runs only on an explicit bounded candidate set; uncertain/high-impact judgments return to the main model, the original evidence remains recoverable, and required final verification is unchanged.
6. A project without Jev authentication, without the metrics extension, or without a compatible SpecKit installation still follows the original manual skill path, without claiming measured Jev usage.
7. Privacy and compatibility checks demonstrate that persisted metrics contain no raw candidate bodies or credentials, and that session resume/reload/branch behavior does not silently inflate or misattribute counts.
8. No A/B benchmark is run as part of writing this epic. Before claiming any token, latency, or quality improvement, a later owner-approved evaluation compares paired existing-skill versus instrumented-skill runs, including downstream regret and fallback rate.

## Exclusions, dependencies, and handoff

- Excluded: `compact-memory`, universal skill routing, global agent-loop steering, automatic suppression of evidence, production rollouts without approval, and a benchmark at this stage.
- Dependency order: approve specification and external ownership boundary → design Pi telemetry contract → implement and validate instrumentation → integrate eight seams individually with original fallbacks → separately approve any activation/evaluation. No optimization should precede observable instrumentation.
- This repository does not contain an installed SpecKit toolkit or a project-associated memory store named by its instructions. `epics-manager` must verify a target project's actual SpecKit capabilities and memory contract before running stages; if missing, stop with the prescribed unavailable report rather than simulating them. The unrelated pre-existing deletion of `skills/expert` observed at admission is out of scope.
- Handoff: use `epics-manager` with this path when a project-installed SpecKit pipeline and project adoption are available; otherwise retain this brief as the approved scope candidate and do not claim implementation readiness.
