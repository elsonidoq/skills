# Optimized Seam Contracts

## Shared contract

Every seam:

1. Forms an explicit list of 2–50 candidates with stable opaque IDs.
2. Retains the complete original evidence outside telemetry.
3. Calls only `jev_rank`, never raw shell or MCP Jev, for measured assistance.
4. Treats all proposals as advisory ordering/grouping evidence.
5. Sends no credentials, secrets, personal data, or unauthorized sensitive payloads.
6. Manually reviews uncertain, ambiguous, and high-impact items.
7. Records one `jev_disposition` for each proposal it accepts, overrides, or does not use; absence
   remains pending.
8. Preserves its existing required final verification and owner/authorization gates.
9. Uses the original manual path if Jev-on mode is not active or a tracked call returns no proposals.

The caller owns candidate construction and complete evidence retention. The tracker owns invocation,
proposal, disposition, and metrics arithmetic.

## Global-suite seams

### `scientific-method-debugging`

- **Candidates**: observed log/test-output chunks from the current coarse investigation scope.
- **Criterion**: rank by relevance to the active observed failure.
- **Main-agent work**: inspect anomalies, form and test root-cause hypotheses, trace upstream/downstream,
  and retain low-ranked evidence when needed.
- **Unchanged verification**: reproduce, establish a failing check, fix one root cause, and rerun
  affected checks.

### `receiving-code-review`

- **Candidates**: review comments awaiting evidence-backed evaluation.
- **Criterion**: rank investigation priority, increasing priority for ambiguity and high impact.
- **Main-agent work**: classify and visibly disposition every original comment; Jev cannot reject a
  finding.
- **Unchanged verification**: inspect cited code/requirements and rerun narrow then affected checks.

### `coordinate-implementation`

- **Candidates**: an existing explicit list of targeted tests applicable to the current batch.
- **Criterion**: rank diagnostic relevance to the batch's changed integration surface.
- **Main-agent work**: select checks when uncertain and preserve dependency sequencing.
- **Unchanged verification**: required affected checks, acceptance checks, and final review remain
  mandatory regardless of rank.

### `track-open-issue`

- **Candidates**: existing open-issue entries found by deterministic search as possible overlaps.
- **Criterion**: rank likelihood of overlap with the verified new issue.
- **Main-agent work**: inspect likely matches and decide create/update/deduplicate from primary
  evidence.
- **Unchanged verification**: register format, evidence, status, resumption condition, and duplicate
  search remain required.

## SpecKit preset seams

### `speckit-analyze`

- **Candidates**: candidate requirement-task associations and low-risk cross-artifact findings from
  complete deterministic inventories.
- **Criterion**: rank priority for deeper inspection; do not score constitution conflicts away.
- **Main-agent work**: verify all coverage, severity, conflicts, and constitution alignment.
- **Unchanged verification**: preserve full inventories and the command's read-only behavior.

### `speckit-checklist`

- **Candidates**: checklist inclusion candidates and near-duplicate group candidates, only after the
  command has constructed the complete candidate set.
- **Criterion**: rank inclusion value and likely near-duplicate grouping when the set is large.
- **Main-agent work**: review exclusions/groups and retain required, high-risk, and owner-requested
  coverage.
- **Unchanged verification**: requirement-quality focus and existing file-preservation rules remain.

### `speckit-clarify`

- **Candidates**: explicit ambiguity/question candidates when more than five are available.
- **Criterion**: rank value of asking each candidate within the five-question limit.
- **Main-agent work**: choose the questions and handle every material product, architecture, privacy,
  permission, cost, security, or irreversible decision.
- **Unchanged verification**: no more than five questions and each accepted answer is integrated and
  validated as the core command requires.

### `speckit-tasks`

- **Candidates**: likely user-story matches for each entity or interface contract.
- **Criterion**: rank the candidate stories for the named entity/contract.
- **Main-agent work**: assign stories, design tasks, order dependencies, and preserve all entities and
  contracts.
- **Unchanged verification**: complete coverage and valid dependency order remain mandatory.

## Fixture proof per seam

Each seam fixture must show:

- bounded candidate count and unique IDs,
- the complete original set remains accessible,
- the tool request contains only the intended candidates,
- one proposal ID per candidate on success,
- explicit disposition outcomes or visible pending proposals,
- manual fallback on unavailable/malformed result,
- unchanged final-verification instructions, and
- no raw fixture sentinel in telemetry entries or closeout CSV.
