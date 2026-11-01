# Issue-derived evaluations

This collection is initially empty: it contains no behavioral cases or results and makes no
correctness claim. Existing static checks and historical fixtures remain separate; see the
[validation guide](../README.md#validation-and-documentation) and
[planner regression guide](../docs/plans/planner-regression.md).

## Later issue resolution

File issues with available context first; evaluation is not a prerequisite for filing. When
later resolving an actual issue, select a useful minimal reproduction and the smallest meaningful
seam: an isolated skill if sufficient, integration or a full workflow if the failure concerns
interactions or the complete workflow. Record the issue/context link, tiny relevant input,
prerequisites and independently stated expected behavior in plain files or prose. Freeze input
and expectations outside result output before inspecting candidate output, normally before either
run. Do not include expectations in the model prompt when they would reveal the answer. If
expectations change, disclose the change: old runs are not evidence against the new expectations.
Retain useful real cases after issue work, not every incident or disposable probe.

When an improvement claim matters to a delivery decision, compare once on an explicit previous
revision and once on an explicit candidate revision, using
the same frozen input, expectations, model, effort and relevant environment. Record revision and
resource identities, Pi version, prompt/input and relevant environment differences. Use separate
fresh equivalent workspaces and outputs. Select cases deliberately; do not automatically run the
whole collection or retry to force an outcome.

## Isolated skill example

This future recipe reflects installed Pi **1.4.0**; recheck the applicable installed CLI, skills
and configuration documentation if the version changes. It is not a universal workflow adapter.
Use distinct previous/candidate checkouts or exports at explicit revisions. `RUN_CWD` is a fresh
case workspace, `RESOURCE_ROOT` is that run's absolute checkout, and `PROMPT_FILE` is shared
frozen input outside both resource trees. All variables are operator inputs; choose distinct
`EVENTS_FILE` and `ERRORS_FILE` paths for each run. Run separately once for each revision:

```sh
(cd "$RUN_CWD" && pi --mode json --no-session --no-approve \
  --no-context-files --no-extensions --no-mcp --no-prompt-templates --no-themes \
  --no-skills --skill "$RESOURCE_ROOT/skills/$SKILL" --tools read \
  --provider "$PROVIDER" --model "$MODEL" --thinking "$EFFORT" \
  "/skill:$SKILL $(cat "$PROMPT_FILE")") > "$EVENTS_FILE" 2> "$ERRORS_FILE"
# Record the actual exit status immediately; inspect events and behavior separately.
```

Explicit `--skill` loads the selected skill despite disabled discovery; `/skill:name` requests
its instructions explicitly. Ensure every supporting skill, reference and script comes from that
run's revision; add explicit skill paths only as needed. Prevent baseline access to candidate or
global guidance through discovery, prompts, symlinks or cross-checkout references. Inspect user
settings and system additions for unchanged, candidate-free guidance. `--no-context-files`
disables discovered AGENTS/CLAUDE files, not all user system additions; `--no-approve` ignores
trust-gated project configuration. If repository guidance is itself under test, explicitly supply
the appropriate revision's guidance rather than suppressing the behavior under test.

This isolates resources and settings, **not security**: the read tool can access other paths.
Inspect actual reads, startup diagnostics and errors; cross-version contamination invalidates the
comparison. Use existing approved Pi credential mechanisms; never copy credentials into cases or
logs. Cases needing dialogs, writes, extensions or full workflows need suitable actual interfaces,
scoped tools and permission gates, potentially in a disposable repository; do not force them
through this read-only recipe.

## Interpret and report

Inspect completion, event output, errors and behavior rather than relying on exit status alone.
An error, aborted or incomplete run, or missing prerequisite is inconclusive, not a behavioral
pass or failure.

Before adding work, distinguish implementation failure, a test that does not measure the intended
behavior, and uncertainty in the expected result. Judge disputed expectations against the original
request and actual constraints—not reviewer agreement or the desired answer. Freezing an expectation
does not make it correct. Keep unresolved cases uncertain; change binding acceptance only through
its existing approval gate.

Add another experiment only when its possible outcomes could change a concrete delivery decision.
Otherwise, report the narrower conclusion. Instruction delivery is not proof of correct decisions;
detection on a different case is not evidence that a fix improved the original behavior. Use the
comparison table only for completed, comparable observations with justified expectations:

| Previous / candidate | Interpretation |
| --- | --- |
| fail / pass | Observed improvement on this case |
| fail / fail | Failure remains |
| pass / pass | Cannot reproduce the reported failure |
| pass / fail | Possible regression |

Prefer deterministic assertions where they observe the intended behavior; human judgment is
acceptable, and use an LLM only when the real behavior needs it, not as a generic judge. Keep
commands, inspectable output/logs, actual results and a brief interpretation in ordinary issue/PR
evidence without credentials or sensitive session payloads. Include token statistics only when
readily available from existing output. One observation per revision is bounded evidence, not
statistical assurance or proof of general correctness.
