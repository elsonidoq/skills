# TinySpec: SpecKit assets in Coherence initialization

Status: owner-selected TinySpec; preparation only. Separate reviewed tasks and combined
current-content owner approval remain required before implementation.

## Outcome and authority

Owner request (verbatim): “the skill /skill:initialize-coherence should make sure the SpecKit commands, templates, and scripts are present in the directory. If they are not present, the skill should install them”. Follow-up: “use /skill:planner to address this”.

The settled outcome is reliable project-local SpecKit assets for people initializing,
refreshing or reusing Coherence. Check on **every initialization**, including compatible
adoption and refresh. Missing/incomplete assets receive official toolkit installation or
repair for the detected agent integration, only through the existing proposal-first gate.
Preserve custom files; conflicts and installation failures stop the affected operation.
The owner chose “TinySpec → Tasks → Implement (recommended)” through `ask_user`:
preparation authorization, not installation or implementation authorization. No material
design question remains; brainstorming was unnecessary. Planning producer selection was
`openai-codex/gpt-6.1-sol:medium`; this does not select implementation routing.

## Scope and preserved constraints

Include the operational [initialize-coherence contract](../../skills/initialize-coherence/SKILL.md),
its existing [regression owner](../../skills/initialize-coherence/scripts/test_contract.py)
and necessary fixtures, plus [README setup](../../README.md) and
[REQUIREMENTS runtime](../../REQUIREMENTS.md). A concise supporting reference inside the
skill is allowed if needed for safe version-specific instructions; the skill remains the
canonical dependency owner. Deliver the coupled contract/regression/docs outcome coherently,
not as phase-only work units. This source is not an implementation checklist.

Exclude actual SpecKit installation in this or other projects during this delivery,
provider/live probes, application/test/generated application changes, databases,
deployment, general prerequisite installation, new test infrastructure, tasks in this
source, STATE upkeep, coordination/memory records and constitutional changes.
TinySpec/direct tasking still does **not** require SpecKit. Standard retains its capability
gates. The exception is initialization's project-asset provisioning, not automatic global
CLI/runtime installation or a new planning-depth rule.

Preserve the dirty capability **first** gate; initial untracked files remain dirty.
Preserve fresh read-only dirty-project investigation, exact dirty-target overlap approval,
owner denial/ambiguity stops, concurrent-change stops, project-root/symlink bounds,
unrelated bytes, existing constitution, custom integration metadata, instructions and
memory paths/content. Compatible adoption remains an instructions/memory no-op, not an
exit that bypasses the SpecKit check. Documentation shell readiness is not substantive
completion. No blanket `specify init --here --force` against an existing repository.
Governing [AGENTS](../../AGENTS.md), [constitution](../../.specify/memory/constitution.md),
[checkpoint](../../skills/memory-handling/references/task-commit-contract.md) and
[approval](../../skills/planner/references/approval-and-recovery.md) contracts remain intact.
Associated `memory/MEMORY.md` has no gotchas; coordination guidelines have no applicable
approved guidance. Neither needs a write.

## Evidence, decisions and approach

Repository evidence at baseline `2400788df837878b1a23d9ee7cd155020eed3115`:
initialize-coherence Preflight lines 23–25 restrict SpecKit to Standard and prohibit
installation; Approval line 90 owns proposal-first writes; Adoption lines 111–112 owns
the compatible no-op; Validation lines 182–185 owns structural readiness. README lines
20–39 and REQUIREMENTS lines 9–23 carry the setup/prerequisite distinction. These carrying
surfaces must change together, narrowly excepting project SpecKit assets while preserving
other missing-runtime stop/report behavior.

**Inspected official implementation/help, version 1.0.12 (2026-10-14; local, read-only):**
`specify --version` reports `specify 1.0.12`; `specify init --help` says assets are bundled,
initialization needs no network, supports `--integration`, `--script`, `--non-interactive`,
a fresh project directory and `--here`; `--force` explicitly permits merge/overwrite.
Package provenance: installed `specify-cli` 1.0.12 METADATA identifies GitHub Spec Kit;
primary upstream is [github/spec-kit](https://github.com/github/spec-kit), with
[official docs](https://github.github.io/spec-kit/). These URLs identify provenance, not
newly fetched web evidence. Inspected installed modules under
`specify_cli` in the local uv tool environment: `command_init.py:671–765` installs agent
commands, saves manifests, writes integration metadata and installs shared infrastructure;
`shared_infra.py:403–427` documents hash-aware managed refresh and customization
preservation, but `force=True` overwrites regular files. `command_init.py:211–255` preserves
an existing constitution. Local `.specify/init-options.json` and `integration.json` identify
pi/sh, version 1.0.12; `.specify/integrations/` contains shared and pi manifests. These are
evidence for this checkout, **not** portable hardcoded destinations or an all-version recipe.

**Repository-derived decisions:** Discover target project integration, script variant,
command location, recorded version and relevant options from actual metadata/configuration.
Do not let CLI noninteractive Copilot defaults silently choose a different integration.
Compare an authoritative expected asset inventory for that integration/version with actual
readable, nonempty command/template/script files and required script permissions/references.
Use bundle/manifest knowledge, not directory existence or a manifest's presence alone:
empty directory shells, absent file families, missing individual files and incomplete
manifests are incomplete. Preserve valid custom content; hash differences alone are not
permission to overwrite. Ambiguous integration, unsupported version, malformed metadata,
unreadable assets or unsafe paths yield a specific gap/conflict report, not guessed readiness.

Use the installed official CLI's current help/source before choosing the exact install/repair
recipe. For 1.0.12, a preservation-oriented shape is official scaffolding into an isolated
fresh staging directory with explicitly detected integration/script/options, followed by an
approved missing-file-only transfer into the target. Inspect the candidate inventory/diff
first; exclude incidental scaffold outputs, `.git`, constitution replacements and unrelated
metadata changes. Do not blindly copy scaffold manifests over existing custom metadata;
reconcile only approved necessary entries, and ensure recorded inventory describes actual
installed files. Unknown safe merge behavior stops rather than inventing old flags or
falling back to `--force`. The staging shape is a bounded instructional approach, **not a
claim that this run executed or proved an installation**. Missing usable CLI is a reported
blocker for repair; do not silently install/upgrade global tooling.

Integrate read-only asset discovery after the dirty-first capability gate, include detected
integration/version, status and exact prospective asset/metadata writes in the existing
approval proposal, then perform only approved repair. Re-read targets immediately before
writes; stop on conflict, drift or CLI failure, preserving existing/custom files and reporting
any partial outputs. No destructive rollback or automatic retry. Revalidate the resulting
inventory; repeat runs with complete assets propose no redundant asset rewrite. Report
SpecKit completeness/repair/no-op/blockers alongside adoption and documentation readiness;
missing required assets prevent an initialization-ready claim even on compatible adoption.

Reusable dependency guidance belongs in the operational skill (and optional local reference)
during implementation, not a separate research artifact. Evidence reuse is proportional:
local current help/source resolves the consequential flags and overwrite risk; internet
research and a disposable prototype add no needed evidence for this bounded instruction
change. Other versions require renewed local help/source evidence before execution.

## Acceptance and smallest sufficient verification

| ID | Observable acceptance / REQUIRED verification need |
| --- | --- |
| A1 | Every new, compatible and refresh route checks all three asset families for detected integration/version; complete assets remain unchanged. Focused positive source scenarios plus deletion/bypass mutations reject a compatible-adoption early exit. |
| A2 | Empty directory shells, wholly missing families, individual missing files and incomplete manifests cannot pass completeness. The contract requires a version-aware expected inventory and actual-file validation; positive/negative fixtures reject existence-only and metadata-only checks. |
| A3 | Missing/incomplete assets produce an exact official install/repair proposal, with integration/options and target bounds, before any write. Approval denial/cancellation/ambiguity and missing mandatory approval capability authorize nothing. Mutations reject unconditional installation, silent defaults and broad `--force`; missing CLI/uncertain recipe is reported, not installed or guessed. |
| A4 | Custom files/constitution/metadata and unrelated work survive; exact dirty overlaps require separate approval and drift/conflicts/CLI failures stop without a ready claim. Retain dirty-first/investigation guards and add focused unsafe-permission cases for overwrite, conflict continuation and failure-as-success. Partial output is reported honestly; no automatic retry or destructive rollback. |
| A5 | Validation/reporting includes actual asset completeness, no-op/repair and blockers; compatible adoption cannot imply readiness with missing assets. README/REQUIREMENTS state the bounded initialization exception, unchanged TinySpec independence and other prerequisite stop/report behavior; introduced references resolve and global skill changes require `/reload`. |
| A6 | Existing source provenance remains immutable: original `sources`, supporting historical text, revision and `SOURCE_HASHES` are unchanged. Amend only live ledger expectations/ownership explanations needed for this owner-directed exception; do not rewrite historical evidence as new proof or weaken unrelated guards. Full focused checks and stage-deletion/contradictory-permission mutation sensitivity pass. |

Use `python3 skills/initialize-coherence/scripts/test_contract.py` as the existing permanent
source-contract/scenario/mutation check, including its baseline mode
`python3 skills/initialize-coherence/scripts/test_contract.py --baseline`. Inspect the actual
diff for preserved source provenance, permission gates, recipe constraints and synchronized
docs; run `git diff --check` and resolve introduced local Markdown references. Demonstrate
new relevant expectations fail against the old contract and pass after the change where
practical, without weakening preservation tests. Baseline observed here: 138 tests PASS.
The existing `requirements` ledger row requires the current blanket no-install phrase;
its live expectations need an explicit bounded exception. The `noop` row remains valid for
association only. Stage order, source hashes, deletion and unsafe-permission tests remain
load-bearing, not obstacles to remove.

These checks prove instruction consistency/sensitivity only, **not** agent obedience or
successful real installation. No prototype, duplicate harness or live probe is required.
Actual CLI execution/installation or model-behavior verification is NOT RUN and outside this
delivery's authorization; any future claim needs separate permission, a disposable target,
actual version/integration/tool capability and observed before/after evidence. No consumers
may rely on an unrun installation as proof. Material disproof or changed scope reopens
only affected source/task review and current-content approval.

## Handoff and residual risk

Separate tasks must map A1–A6 to stable REQUIRED evidence with the above commands/pass
conditions, manual diff checks and permission gates; planner reviews source and tasks before
combined approval. Coordinator owns execution routing and independent final review.
Authorized retained work checkpoints explicit owned paths before handoff. No feature
acceptance or implementation authorization is claimed by this source commit.

Remaining risk: CLI/version/integration variance and source-only checks cannot establish
runtime obedience or real install success. The fail-closed discovery/recipe rule and truthful
NOT RUN reporting contain this risk; no material design deferral or preparation blocker remains.
