# Quickstart Validation Guide: Measurable Jev Skill Assistance

This guide describes post-implementation validation. It is fixture-driven and must not make a live
Jev judgment or run an A/B benchmark. Run from the repository root.

## Prerequisites

- Pi 0.87.x (`pi --version`)
- Node.js 22 or compatible (`node --version`)
- Python 3 and POSIX shell for existing installer/SpecKit fixture scripts
- SpecKit 1.0.12 for preset fixture validation (`specify --version`)
- No Jev credential is needed for deterministic tests; fake process adapters supply all responses

The event, tool, seam, installation, and CSV rules are defined in [contracts/](contracts/). Entity
invariants and state transitions are in [data-model.md](data-model.md).

## 1. Run deterministic extension checks

```bash
node --test extensions/jev-metrics/test/*.test.js
```

Expected:

- one successful attempt with three candidates reports `attempts=1`, `successes=1`,
  `proposals=3`, and `pending=3`;
- two accepted plus one overridden reports exactly `2/1/0/0`, and replay is unchanged;
- missing auth/CLI, malformed/partial output, nonzero exits, and cancellation count attempts but not
  successes/proposals;
- reload, resume, fork, and tree-navigation fixtures use only the active branch;
- unknown, cross-session, duplicate, and conflicting dispositions do not inflate counters;
- missing/corrupt history is explicit rather than a historical zero;
- candidate/log/credential sentinel strings are absent from custom entries, metrics output, and CSV.

## 2. Run install-mode checks

```bash
scripts/tests/test-install-jev.sh
```

Expected:

- manual/default installation succeeds with Jev and tracker absent and leaves all four global skills
  on their manual path;
- every Jev-on fixture missing Pi compatibility, tracker load, Jev CLI compatibility, or auth fails
  before any optimized seam is active;
- a fully satisfied fixture activates the tracker before seams;
- an injected activation failure restores the pre-install state.

The script uses fake executables and temporary homes. It must not invoke the real `jev auth test`.

## 3. Verify the project-owned SpecKit override

```bash
scripts/tests/test-install-jev-speckit.sh
```

Expected:

- a temporary SpecKit 1.0.12 project receives one project-local preset;
- `speckit.analyze`, `speckit.checklist`, `speckit.clarify`, and `speckit.tasks` each resolve to the
  full core command plus one append layer from the preset;
- direct generated-prompt modifications are absent;
- missing/incompatible preset capability disables all four seams, not a subset;
- uninstall/rollback reconciles the original core prompts.

For diagnosis inside the temporary fixture, the test may run:

```bash
specify preset resolve speckit.analyze
specify preset resolve speckit.checklist
specify preset resolve speckit.clarify
specify preset resolve speckit.tasks
specify artifact info speckit.analyze --json
specify artifact info speckit.checklist --json
specify artifact info speckit.clarify --json
specify artifact info speckit.tasks --json
```

## 4. Verify all eight seams

The extension suite loads one fixture per seam from
`extensions/jev-metrics/fixtures/seams/`.

```bash
node --test extensions/jev-metrics/test/extension.test.js \
  extensions/jev-metrics/test/privacy.test.js
```

Expected for each source-named fixture:

- 2–50 unique candidate IDs;
- complete original candidate set retained by the caller;
- one proposal ID per successful candidate;
- manual fallback on unavailable/malformed result;
- explicit dispositions or visible pending proposals;
- unchanged main-agent authority and final-verification instructions.

The covered IDs are:

```text
scientific-method-debugging
receiving-code-review
coordinate-implementation
track-open-issue
speckit-analyze
speckit-checklist
speckit-clarify
speckit-tasks
```

## 5. Verify session closeout CSV

The CSV tests isolate state under a temporary `XDG_STATE_HOME`:

```bash
node --test extensions/jev-metrics/test/csv-store.test.js
```

Expected:

- first closeout creates the fixed header and exactly one row;
- repeated closeout for the same Pi session returns `already_exported` and leaves one row;
- the row satisfies `accepted + overridden + not_used + pending = proposals`;
- the row contains `instrumented-only` and no project path or forbidden sentinel;
- invalid/unreadable stores return `store_error` and remain untouched.

## 6. Run repository checks

```bash
scripts/check-skills-lint.sh
.specify/scripts/bash/check-prerequisites.sh --json --require-spec
```

Expected:

- skill lint passes;
- SpecKit reports `research.md`, `data-model.md`, `contracts/`, and `quickstart.md` available;
- no task or implementation stage is implied by this check.

## 7. Optional local Pi smoke test after implementation approval

Only perform this after the owner authorizes implementation and explicitly selects Jev-on mode.
The real Jev-on installer will run a fixed `jev auth test`; it is a network prerequisite check, not a
benchmark.

```bash
scripts/install.sh --jev-on
```

Then run `/reload` in Pi and verify:

1. `/jev-metrics help` names the coverage boundary and all counters.
2. A synthetic approved seam call returns stable proposal IDs.
3. Disposition replay does not change `/jev-metrics` totals.
4. `finish-session` reports `appended` or `already_exported` for the session row.
5. A raw shell/MCP Jev call, if independently made, is still described as untracked and is not added
   to measured totals.

Do not use production logs, credentials, personal data, or sensitive candidate text for this smoke
test. Do not compare token use, latency, or quality against the manual workflow.

## Completion criteria

Validation is complete only when all deterministic commands pass and evidence maps to SC-001 through
SC-006. A live Jev result, a generated ranking, or successful installation alone is not feature
acceptance.
