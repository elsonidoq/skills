#!/usr/bin/env python3
"""Source-first static Coherence checks. Fixtures are not model-obedience evidence."""
import contextlib
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import types
import unittest
from unittest import mock

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASELINE = json.loads((HERE / "fixtures/source-contract.json").read_text())
SKILL = HERE.parent / "SKILL.md"
SCENARIOS = json.loads((HERE / "fixtures/scenarios.json").read_text())
ROWS = {row["id"]: row for row in BASELINE["ledger"]}
STAGES = ("Preflight", "Discovery", "Investigation", "Approval", "Adoption", "Documentation", "Validation")
BOOKKEEPING_UNSAFE = {
    "permission-auto-state": r"automatically (?:create|update|remove) state\.md",
    "permission-auto-coordination": r"automatically initialize coordination memory",
    "permission-routine-reflection": r"reflect at blocked pause",
    "permission-summary": r"write a run summary on completion",
}
UNSAFE = {
    "permission-assets-existence": r"\btreat directory existence alone as asset completeness\b",
    "permission-assets-manifest": r"\btreat manifest presence alone as asset completeness\b",
    "permission-assets-permissions": r"\bskip required script permissions checks\b",
    "permission-assets-references": r"\bskip asset reference checks\b",
    "permission-assets-empty": r"\bclaim ready with empty or missing asset files\b",
    "permission-assets-bypass": r"\breturn immediately after compatible adoption\b",
    "permission-assets-default": r"\buse default integration for asset repair\b",
    "permission-assets-unapproved": r"\binstall speckit assets without approval\b",
    "permission-assets-force": r"\brun specify init \-\-here \-\-force in the existing repository\b",
    "permission-assets-global-install": r"\bautomatically install the missing global speckit cli\b",
    "permission-assets-overwrite": r"\boverwrite existing custom assets\b",
    "permission-assets-conflict": r"\bcontinue asset repair after conflict or drift\b",
    "permission-assets-ready": r"\bclaim ready after cli failure or partial output\b",
    "permission-assets-retry": r"\bautomatically retry failed asset repair\b",
    "permission-assets-rollback": r"\bdestructively roll back partial asset repair\b",
    "permission-assets-metadata": r"\bblindly copy staging metadata over custom metadata\b",
    "permission-unapproved": r"\bwrite any target without approval\b",
    "permission-denial": r"\bdenial grants writes\b",
    "permission-ambiguous": r"\bambiguous answers authorize writes\b",
    "permission-dirty-overlap": r"\bedit dirty targets without approval\b",
    "permission-concurrent": r"\bcontinue after concurrent changes\b",
    "permission-tinyspec": r"\bspeckit is mandatory for tinyspec\b",
    "permission-memory-reset": r"\breset existing memory on refresh\b",
    "permission-custom-path": r"\breplace custom memory paths with the default\b",
    "permission-global": r"\buse global memory when association is missing\b",
    "permission-fabrication": r"\bfill the memory skeleton with invented gotchas\b",
    "ownership-memory-ban": r"\bdo not create a memory store anywhere in this workflow\b",
    "ownership-docs-ban": r"\bnever create documentation directories in this workflow\b",
    "permission-merged-writes": r"\ball merged-stage writes are unconditionally permitted\b",
    "permission-untracked": r"\btreat untracked files as clean\b",
    "permission-dirty-substantive": r"\bwrite substantive documentation on non-clean projects\b",
    "permission-changed-code": r"\bassume changed code is live and intentional\b",
    "permission-missing-ready": r"\bclaim readiness despite missing required structure\b",
    "permission-shell-complete": r"\bshell initialization is substantive completion\b",
    "permission-planner": r"\bhandoff substantive work without planner\b",
    "permission-depth": r"\bforce standard for documentation handoff\b",
    "permission-epic": r"\bautomatically create a new epic\b",
}
# T001 live expectations; original attribution and hashes remain untouched.
SPECKIT_RULES = {
 "assets-absent-metadata": ('Discovery',
 ['Distinguish absent SpecKit metadata from malformed or conflicting metadata; absence is not '
  'an unsupported integration.',
  'When metadata is absent, inspect installed official CLI source/help read-only for supported '
  'integration, script, version and options; use current runtime/repository evidence to '
  'prepare explicit supported choices for Approval, not guessed or silent defaults.',
  'Use the installed official CLI version verified from source evidence when no recorded '
  'project version exists; unresolved selections or unknown/unsupported recipes stop until '
  'resolved, without readiness.']),
 'assets-discovery': ('Discovery',
                      ['After the dirty-first capability gate, check SpecKit project assets on '
                       'every full initialization: new adoption, compatible adoption and refresh.',
                       'Detect integration, script variant, command location, recorded version and '
                       'relevant options from target metadata/configuration; do not silently '
                       'select noninteractive Copilot defaults.',
                       'Compare an authoritative expected inventory from the official bundle for '
                       'the detected integration/version against commands, templates and scripts.',
                       'Check every expected actual file is readable and nonempty, required script '
                       'permissions are usable, and command/template/script references resolve '
                       'inside safe project-root/symlink bounds.',
                       'Empty directory shells, missing families, individual missing files and '
                       'incomplete manifests are incomplete; directory or manifest existence alone '
                       'cannot establish readiness.',
                       'Valid custom files remain valid; hash differences alone grant no overwrite '
                       'permission.',
                       'Ambiguous integration, unsupported version, malformed metadata, unreadable '
                       'assets or unsafe paths stop the affected operation with specific '
                       'gaps/conflicts, not guessed readiness.']),
 'assets-proposal': ('Approval',
                     ['For absent metadata, obtain material owner selection of integration, script, command '
                      'location and relevant options via `ask_user` under the existing brief/capability/denial '
                      'gates; selection alone grants no writes, then present the exact staging/target proposal '
                      'for explicit approval.',
                      'Include SpecKit integration/version/options, three-family status, '
                      'conflicts, exact prospective asset paths and necessary manifest/metadata '
                      'entry changes in the current-content proposal before permission to repair.',
                      'Complete assets propose no asset rewrite; missing assets require an exact '
                      'official install/repair recipe and bounded target writes.',
                      'Missing usable CLI is a reported blocker for repair; do not silently '
                      'install/upgrade global tooling.',
                      'Before future execution inspect the installed official CLI version, current '
                      'help and source; unknown safe recipe/version/integration stops.',
                      'For inspected official 1.0.12, assets are bundled offline; use isolated '
                      'fresh staging with explicit `--integration`, `--script` and detected '
                      'relevant options, not silent CLI defaults.',
                      'Propose the exact staging command and options, staging location, candidate '
                      'inventory/diff and approved missing-file-only transfer paths before any '
                      'staging or target write.',
                      'No blanket `specify init --here --force` against an existing repository: '
                      '`--force` permits merge/overwrite and managed refresh is not an overwrite '
                      'waiver.']),
 'assets-continuation': ('Adoption',
                         ['Compatible association remains an association/memory no-op, not an exit '
                          'that bypasses the full-initialization SpecKit check; approved bounded policy changes remain separate.',
                          'Full new, compatible and refresh routes continue from Discovery through '
                          'Approval to the approved asset operation below and final Validation; no '
                          'adoption early return.',
                          'Asset repair is separately bounded by Approval, not authority to change '
                          'instructions/memory or documentation.',
                          'Only after explicit approval, scaffold with the verified official '
                          'recipe into the isolated fresh staging directory; inspect candidate '
                          'inventory/diff before approved missing-file-only transfer.',
                          'Preserve existing custom assets, constitution and integration metadata; '
                          'exclude incidental scaffold outputs, `.git`, constitution replacements '
                          'and unrelated metadata changes.',
                          'Never blindly copy scaffold manifests over custom metadata; reconcile '
                          'only necessary approved entries so the recorded inventory describes '
                          'actual installed files.',
                          'Apply Preflight dirty-target/exact-overlap and concurrent-change '
                          'protections to staging, asset and metadata writes; re-read each target '
                          'immediately before writing.',
                          'Conflict, drift, CLI failure or partial output stops the affected '
                          'operation; report partial outputs and blockers without readiness, '
                          'automatic retry or destructive rollback.',
                          'Complete assets remain untouched on repeat runs; revalidate the actual '
                          'three-family inventory after approved repair.']),
 'assets-report': ('Validation',
                   ['On full new, compatible and refresh routes, report detected SpecKit '
                    'integration/version, actual commands/templates/scripts completeness, repair '
                    'or no-op, partial outputs and blockers.',
                    'Missing or incomplete required SpecKit project assets block '
                    'initialization-ready claims even on compatible adoption; documentation shell '
                    'readiness is not asset completeness.',
                    'Revalidate the authoritative expected inventory against actual readable, '
                    'nonempty files, required permissions and resolving references; manifest-only '
                    'success or CLI exit status is insufficient.',
                    'manifest-only success or CLI exit status is insufficient.'])}

DECISION_RULES = {
    "decision-discovery": ("Discovery", ["actual project decision owner, index and record convention",
        "do not assume a global or default decision store", "absent store alone does not block unrelated legacy work"]),
    "decision-approval": ("Approval", ["new adoption or explicitly approved bounded refresh",
        "discovered decision owner/index, canonical contract location and exact managed before/after instructions diff",
        "incidental skill use does not authorize that addition"]),
    "decision-managed-consultation": ("Adoption", ["resolve the installed canonical `save-adr/SKILL.md`",
        "not a fixed developer path", "read the whole discovered decision index, then relevant accepted records in full",
        "A capability removal that conflicts with an accepted outcome needs explicit approved supersession",
        "does not create an unapproved store or replace a custom owner",
        "do not incidentally refresh a project merely because `save-adr` is consulted"]),
}

ISSUE_OWNER_RULES = {
    "github-issue-owner": ("Discovery", [
        "Resolve the unresolved-work owner from project routing.",
        "An explicitly configured GitHub Issues target is an external owner, not a local documentation file",
        "do not create or require `docs/open_issues.md`",
        "Confirm the explicit target and usable `gh`, authenticated issue-read capability as specified by `track-open-issue`.",
        "Missing or conflicting target, `gh`, authentication, or issue capability is an actionable `issue tracking: UNAVAILABLE` gap",
        "do not claim that owner/readiness is satisfied or fall back to a local tracker.",
    ]),
    "github-issue-owner-association": ("Adoption", [
        "canonical unresolved-work register via `track-open-issue`",
        "explicitly configured GitHub Issues target remains external and does not require a local register",
    ]),
}

POLICY_RULES = {
    "policy-selection": ("Preflight", ["Full initialization is the default", "Only explicit policy-only refresh intent",
        "targeted dirty ownership", "missing capability required for the bounded operation stops it"]),
    "policy-discovery": ("Discovery", ["existing approved association and equivalent instructions owner",
        "not policy-only refresh", "not silent initialization"]),
    "policy-investigation": ("Investigation", ["Policy-only skips broad documentation investigation"]),
    "policy-approval": ("Approval", ["exact instructions target, subsection bounds and before/after policy diff"]),
    "policy-copy": ("Adoption", ["compare actual policy text", "irrelevant whitespace/line endings",
        "Dates, hashes, versions, receipts, headings or links are not currency proof",
        "coherence-parsimony:start", "including equivalent local policy",
        "specific keep/reconcile/location choice", "separate explicit overlap approval",
        "Re-read immediately before patching", "concurrent drift stops", "every unrelated byte",
        "Never regenerate the outer contract wholesale"]),
    "policy-docs": ("Documentation", ["Full initialization only", "Policy-only refresh does not discover/repair documentation"]),
    "policy-validation": ("Validation", ["policy refresh applied", "policy already current",
        "not full initialization/Standard readiness", "no empty commit"]),
}


SOURCE_HASHES = {
    "skills/install-memory/SKILL.md": "7894452bb308c5292c13f5cfb3d19ed945842d88e1a31e1d5dbb8861dddc715f",
    "skills/initialize-documentation/SKILL.md": "978b51d11867496a6237d233987886e9dcb718a6ac3beedf7fc52a1f16c24b32",
}


def normalized(text):
    return " ".join(text.split()).casefold()


def stage(text, name):
    marker = f"## {name}"
    start = text.find(marker)
    if start < 0:
        return ""
    end = text.find("\n## ", start + len(marker))
    return text[start:] if end < 0 else text[start:end]


def check_contract(text):
    errors = []
    if re.findall(r"^## (.+)$", text, re.M) != list(STAGES):
        errors.append("stage-order: missing, duplicated or reordered carrying stages")
    for diagnostic, pattern in (UNSAFE | BOOKKEEPING_UNSAFE).items():
        if re.search(pattern, normalized(text)):
            errors.append(f"{diagnostic}: contradictory permission")
    for diagnostic, (name, phrases) in (SPECKIT_RULES | POLICY_RULES | DECISION_RULES | ISSUE_OWNER_RULES).items():
        body = normalized(stage(text, name))
        for phrase in phrases:
            if normalized(phrase) not in body:
                errors.append(f"{diagnostic}: missing {phrase!r} in {name}")
    for row in BASELINE["ledger"]:
        body = normalized(stage(text, row["stage"]))
        for phrase in row["requires"]:
            if normalized(phrase) not in body:
                errors.append(f"{row['id']}: missing {phrase!r} in {row['stage']}")
    return errors


class BaselineTests(unittest.TestCase):
    def test_adoption_cannot_seed_removed_bookkeeping(self):
        text = SKILL.read_text()
        for clause, diagnostic in (
            ("Automatically create STATE.md", "permission-auto-state"),
            ("Automatically initialize coordination memory", "permission-auto-coordination"),
            ("Reflect at blocked pause", "permission-routine-reflection"),
            ("Write a run SUMMARY on completion", "permission-summary"),
        ):
            self.assertTrue(any(e.startswith(diagnostic + ":") for e in check_contract(text + "\n" + clause)))

    def test_original_sources_are_attributed_and_immutable(self):
        self.assertEqual(BASELINE["revision"], "7f6c0cb0cbdd15967d91c84b2295a45f3c64a2d3")
        for path, digest in SOURCE_HASHES.items():
            self.assertEqual(hashlib.sha256(BASELINE["sources"][path].encode()).hexdigest(), digest)

    def test_every_original_operational_line_has_a_ledger_carrier(self):
        for path, text in BASELINE["sources"].items():
            covered = set()
            for row in BASELINE["ledger"]:
                for citation in row["citations"]:
                    if citation["path"] == path:
                        covered.update(range(citation["start"], citation["end"] + 1))
            for number, line in enumerate(text.splitlines(), 1):
                if number >= 8 and line.strip():
                    self.assertIn(number, covered, f"unaccounted source clause {path}:{number}")

    def test_rows_have_behavior_stages_checks_and_ownership_decisions(self):
        ids = set()
        for row in BASELINE["ledger"]:
            self.assertNotIn(row["id"], ids); ids.add(row["id"])
            for key in ("behavior", "stage", "ownership_change", "task", "positive", "negative", "evidence", "requires"):
                self.assertTrue(row[key], (row["id"], key))
            for citation in row["citations"]:
                path = citation["path"]
                text = BASELINE.get("sources", {}).get(path, BASELINE["supporting"].get(path, ""))
                self.assertTrue(text, path)
                self.assertLessEqual(citation["end"], len(text.splitlines()))
        self.assertEqual(set(BASELINE["acceptance"]), {"A1", "A2", "A3", "A4", "A5"})
        self.assertEqual({r["behavior_group"] for r in BASELINE["ledger"]}, {f"B{i}" for i in range(1, 9)})


class CandidateTests(unittest.TestCase):
    def test_candidate_carrying_stages(self):
        self.assertTrue(SKILL.exists(), "initialize-coherence candidate missing")
        self.assertEqual(check_contract(SKILL.read_text()), [])

    def test_activation_guidance_is_host_specific_and_regression_sensitive(self):
        def assert_guidance(source):
            validation = stage(source, "Validation")
            paseo = ("in Paseo, prepare a fresh-session handoff; the fresh agent verifies the checkout "
                     "and loaded required capabilities before launching approved workflow. Do not instruct "
                     "the owner to run `/reload`, and do not automatically reload, restart or install.")
            outside = "Outside Paseo, tell the user to run `/reload` inside pi."
            self.assertIn(paseo, validation)
            self.assertIn(outside, validation)

        source = SKILL.read_text()
        assert_guidance(source)
        for old, new in (
            ("fresh-session handoff", "current-session reload"),
            ("Do not instruct the owner to run `/reload`", "Tell the owner to run `/reload`"),
            ("Outside Paseo, tell the user to run `/reload` inside pi.",
             "Outside Paseo, prepare a fresh-session handoff."),
        ):
            with self.subTest(regression=new):
                self.assertIn(old, source)
                with self.assertRaises(AssertionError):
                    assert_guidance(source.replace(old, new, 1))

    def test_frontmatter_single_entry_and_probe_inventory(self):
        text = SKILL.read_text()
        self.assertTrue(text.startswith("---\nname: initialize-coherence\ndescription: Use when"))
        self.assertIn("# Initialize Coherence", text)
        names = {p.parent.name for p in (ROOT / "skills").glob("*/SKILL.md")}
        self.assertIn("initialize-coherence", names)
        self.assertTrue({"install-memory", "initialize-documentation"}.isdisjoint(names))
        probe = (ROOT / "scripts/probe-pi-load.sh").read_text().split("REQUIRED=(", 1)[1].split(")", 1)[0]
        self.assertEqual(probe.count("initialize-coherence"), 1)
        for retired in ("install-memory", "initialize-documentation"):
            self.assertNotIn(retired, probe)

    def test_stage_sequence_and_dirty_first_gate(self):
        text = SKILL.read_text()
        self.assertEqual(re.findall(r"^## (.+)$", text, re.M), list(STAGES))
        pre = stage(text, "Preflight")
        self.assertLess(pre.index("git status --short"), pre.index("FIRST verify"))
        self.assertIn("no adoption write may precede this dirty capability gate", normalized(pre))
        investigation = stage(text, "Investigation")
        self.assertEqual(re.findall(r"^(\d)\. ", investigation, re.M), ["1", "2", "3", "4"])
        self.assertIn("skip this stage only for an initially clean project", normalized(investigation))

    def test_consumer_routes_preserve_noninitializing_closeout_and_memory_rules(self):
        for path in BASELINE["active_consumers"]:
            text = (ROOT / path).read_text()
            for retired in ("install-memory", "initialize-documentation"):
                self.assertNotIn(retired, text, path)
            self.assertIn("initialize-coherence", text, path)
        memory = normalized((ROOT / "skills/memory-handling/SKILL.md").read_text())
        for phrase in ("memory adoption: missing — run initialize-coherence", "do not create, guess, or modify a global store", "read the whole index first", "index → matching entries"):
            self.assertIn(phrase, memory)
        compact = normalized((ROOT / "skills/compact-memory/SKILL.md").read_text())
        for phrase in ("no verified project memory store", "do not create a memory store or modify global memory", "stop on a concurrent change", "fresh, independent backup"):
            self.assertIn(phrase, compact)
        finish = normalized((ROOT / "skills/finish-session/SKILL.md").read_text())
        gate = normalized(stage((ROOT / "skills/finish-session/SKILL.md").read_text(), "Step 0: Documentation Initialization Gate"))
        for phrase in ("existence check only", "do not audit documentation accuracy, create missing files", "database-schema owner", "documentation-routing guide", "initialize-coherence", "and stop"):
            self.assertIn(phrase, gate)
        self.assertIn("do not create or modify one implicitly", finish)

    def test_setup_matches_branch_and_readiness_bounds(self):
        readme = normalized((ROOT / "README.md").read_text())
        requirements = normalized((ROOT / "REQUIREMENTS.md").read_text())
        for phrase in ("proposal-first", "compatible adoption", "bounded refresh", "fresh read-only investigation", "empty/template shells", "structural readiness", "outstanding work", "fresh-session handoff", "authorize separately"):
            self.assertIn(phrase, readme)
        for doc in (readme, requirements):
            for phrase in ("every full initialization", "commands, templates and scripts", "compatible adoption and refresh", "approved missing-file-only transfer", "missing usable cli", "other missing runtime prerequisites", "tinyspec/direct tasking", "no blanket", "--force", "fresh-session handoff"):
                self.assertIn(phrase, doc)
            self.assertTrue("no automatic reload or restart" in doc or
                            "no automatic reload or restart occurs" in doc or
                            "instead of reloading or restarting the current session" in doc)
        for phrase in ("0.87.x", "0.87.1", "pi-subagents@0.73.1", "pi-ask-user@0.15.1", "tinyspec/direct tasking does not require it", "manual routing", "schema owner", "missing required structure blocks readiness"):
            self.assertIn(phrase, requirements)

    def test_introduced_references_and_repo_association(self):
        for path in ("README.md", "docs/index.md", "skills/initialize-coherence/SKILL.md"):
            for target in re.findall(r"\]\(([^)]+)\)", (ROOT / path).read_text()):
                if not target.startswith(("http", "#")):
                    self.assertTrue((ROOT / path).parent.joinpath(target.split("#", 1)[0]).exists(), (path, target))
        index = (ROOT / "docs/index.md").read_text()
        agents = (ROOT / "AGENTS.md").read_text()
        gotchas = (ROOT / "memory/MEMORY.md").read_text()
        self.assertIn("<!-- coherence-suite-contract:start -->", agents)
        self.assertIn("associated store is `memory/`", normalized(agents))
        self.assertIn("No project gotchas recorded yet.", gotchas)
        self.assertIn("[gotcha-memory index](../memory/MEMORY.md)", index)
        self.assertIn("[Plans directory index](plans/index.md)", index)
        self.assertIn("coordination memory remains a separate", normalized(index))
        self.assertIn("no default suite-level database is created by adoption", normalized(index))
        self.assertIn("[Runtime schema owner](coordinate-implementation-schema.md)", index)
        self.assertIn("thin executable interface", normalized(index))


class PolicyRefreshTests(unittest.TestCase):
    """Static carrying clauses and authored diffs, never an executed updater."""

    def test_policy_only_route_custody_and_limited_result(self):
        text = SKILL.read_text()
        for name, clauses in {
            "Preflight": ("Full initialization is the default", "explicit policy-only", "targeted dirty ownership"),
            "Discovery": ("approved association", "equivalent instructions owner", "not policy-only"),
            "Investigation": ("Policy-only skips broad documentation investigation",),
            "Adoption": ("compare actual policy text", "coherence-parsimony:start", "equivalent local policy",
                         "Re-read immediately before patching", "concurrent drift stops", "every unrelated byte"),
            "Validation": ("policy refresh applied", "policy already current", "no empty commit", "not full initialization/Standard readiness"),
        }.items():
            body = stage(text, name)
            for clause in clauses:
                self.assertIn(clause, body, (name, clause))


    def test_authored_policy_copies_and_bounded_diffs(self):
        rows = json.loads((HERE / "fixtures/workflow-ownership-outputs.json").read_text())
        canonical = (ROOT / "skills/planner/references/parsimony.md").read_text()
        start, end = "<!-- coherence-parsimony:start -->", "<!-- coherence-parsimony:end -->"
        def fragment(text):
            return text.split(start, 1)[1].split(end, 1)[0]
        expected = " ".join(fragment(canonical).split())  # whitespace only, not casefold
        changed = []
        for row in rows:
            with self.subTest(case=row["name"], expected=row["outcome"]):
                before, after = row["before"], row["after"]
                if row["route"] == "full" or row.get("change") in ("insertion", "replacement") or row["name"] == "unchanged-repeat":
                    self.assertEqual(after.count(start), 1)
                    self.assertEqual(after.count(end), 1)
                    self.assertEqual(" ".join(fragment(after).split()), expected)
                if row["route"] != "policy-only":
                    continue
                self.assertEqual(row["files_before"], row["files_after"])
                self.assertIn("custom/gotchas/MEMORY.md", before)
                self.assertIn("Local override: keep exports", after)
                if row["writes"]:
                    self.assertTrue(row["approved"])
                    self.assertEqual(row["writes"], [row["target"]])
                    prefix, tail = after.split(start, 1)
                    suffix = tail.split(end, 1)[1]
                    if row["change"] == "insertion":
                        self.assertEqual(before, prefix + suffix.lstrip("\n"))
                    else:
                        self.assertEqual(before.split(start, 1)[0], prefix)
                        self.assertEqual(before.split(end, 1)[1], suffix)
                    self.assertTrue(prefix.count("coherence-suite-contract:start") == 1)
                    self.assertIn("coherence-suite-contract:end", suffix)
                    self.assertEqual(row["outcome"], "policy refresh applied")
                    changed.append(row["name"])
                else:
                    self.assertEqual(before, after)
                    self.assertEqual(row["change"], "none")
        self.assertEqual(changed, ["compatible-missing-policy-unrelated-assets-absent", "managed-outdated-policy"])
        by_name = {row["name"]: row for row in rows}
        self.assertEqual(by_name["equivalent-approved-owner"]["target"], "PROJECT.md")
        self.assertEqual(by_name["equivalent-approved-owner"]["choice"], "keep")
        self.assertIn("choice required", by_name["customized-policy-choice"]["outcome"])
        self.assertFalse(by_name["denied-dirty-overlap"]["overlap_approved"])
        self.assertNotEqual(by_name["concurrent-drift"]["approved_before"], by_name["concurrent-drift"]["before"])
        self.assertIn("stop affected patch", by_name["concurrent-drift"]["outcome"])
        self.assertIn("escaping symlink", by_name["unsafe-path"]["outcome"])
        self.assertEqual(by_name["unchanged-repeat"]["outcome"], "policy already current")
        self.assertEqual(by_name["compatible-missing-policy-unrelated-assets-absent"]["unrelated_missing"],
                         ["SpecKit inventory", "documentation routing"])

    def test_compare_proposal_approval_reread_patch_validation_order(self):
        text = stage(SKILL.read_text(), "Adoption").split("### Managed parsimony comparison and refresh", 1)[1]
        steps = ("1. Compare canonical text", "2. Propose the exact target", "obtain normal",
                 "3. Re-read immediately before patching", "4. Patch only the approved", "5. Validate by re-reading")
        positions = [text.index(step) for step in steps]
        self.assertEqual(positions, sorted(positions))

    def test_route_clauses_are_required_in_carrying_stages(self):
        text = SKILL.read_text()
        self.assertEqual(check_contract(text), [])
        for diagnostic, (name, phrases) in POLICY_RULES.items():
            with self.subTest(boundary=diagnostic):
                # One representative deletion per actual boundary, not a sentence matrix.
                phrase = phrases[0]
                pattern = r"\s+".join(re.escape(word) for word in phrase.split())
                body = stage(text, name)
                changed = text.replace(body, re.sub(pattern, "REMOVED", body, count=1), 1)
                self.assertTrue(any(e.startswith(diagnostic + ":") for e in check_contract(changed)))

    def test_operator_docs_and_repo_copy_match_route(self):
        owner = (ROOT / "skills/planner/references/parsimony.md").read_text()
        agents = (ROOT / "AGENTS.md").read_text()
        start, end = "<!-- coherence-parsimony:start -->", "<!-- coherence-parsimony:end -->"
        self.assertEqual(agents.count(start), 1)
        self.assertEqual(owner.split(start)[1].split(end)[0], agents.split(start)[1].split(end)[0])
        for path in ("README.md", "REQUIREMENTS.md"):
            doc = normalized((ROOT / path).read_text())
            for clause in ("policy-only", "installation", "does not refresh", "explicitly selected",
                           "exact bounded", "dirty exact overlap", "policy already current", "no-op" if path == "README.md" else "no write",
                           "not full initialization/standard readiness" if path == "README.md" else "never full initialization/standard readiness"):
                self.assertIn(clause, doc, path)


class DecisionConsultationTests(unittest.TestCase):
    """Authored managed-instruction diffs, not an adoption runner."""

    def test_decision_fixture_diffs_preserve_owner_and_stops(self):
        rows = {row["name"]: row for row in SCENARIOS if "managed_diff" in row}
        self.assertEqual(set(rows), {"decision-new-adoption", "decision-approved-custom-refresh",
                                     "decision-unchanged-repeat", "decision-denial",
                                     "decision-dirty-overlap", "decision-concurrent-drift"})
        for name, row in rows.items():
            with self.subTest(case=name):
                diff = row["managed_diff"]
                self.assertIn("history/decisions/index.md", diff["before"])
                self.assertIn("Local decision owner", diff["before"])
                if diff["writes"]:
                    self.assertTrue(diff["approved"])
                    self.assertIn("read the whole discovered decision index", diff["after"])
                    self.assertIn("relevant accepted records", diff["after"])
                    self.assertIn("capability removal", diff["after"])
                    self.assertIn("history/decisions/index.md", diff["after"])
                    self.assertIn("Local decision owner", diff["after"])
                else:
                    self.assertEqual(diff["before"], diff["after"])
        self.assertEqual(rows["decision-unchanged-repeat"]["managed_diff"]["outcome"], "no write: already current")
        self.assertFalse(rows["decision-denial"]["managed_diff"]["approved"])
        self.assertFalse(rows["decision-dirty-overlap"]["managed_diff"]["overlap_approved"])
        self.assertEqual(rows["decision-concurrent-drift"]["managed_diff"]["outcome"], "stop affected patch: concurrent drift")

    def test_decision_carrying_clauses_reject_deletion(self):
        text = SKILL.read_text()
        self.assertEqual(check_contract(text), [])
        for diagnostic, (name, phrases) in DECISION_RULES.items():
            with self.subTest(boundary=diagnostic):
                phrase = phrases[0]
                body = stage(text, name)
                pattern = r"\s+".join(re.escape(word) for word in phrase.split())
                changed = text.replace(body, re.sub(pattern, "REMOVED", body, count=1), 1)
                self.assertTrue(any(error.startswith(diagnostic + ":") for error in check_contract(changed)))


class ExternalIssueOwnerTests(unittest.TestCase):
    """Static owner association cases; they do not probe GitHub or authenticate."""

    def test_external_owner_and_actionable_gap_cases(self):
        text = SKILL.read_text()
        discovery = stage(text, "Discovery")
        adoption = stage(text, "Adoption")
        cases = {
            "configured-github-owner": (discovery, "An explicitly configured GitHub Issues target is an external owner, not a local documentation file"),
            "no-local-register": (discovery, "do not create or require `docs/open_issues.md`"),
            "missing-or-conflicting-target": (discovery, "Missing or conflicting target"),
            "missing-gh-or-auth": (discovery, "`gh`, authentication, or issue capability is an actionable `issue tracking: UNAVAILABLE` gap"),
            "no-fallback-or-false-readiness": (discovery, "do not claim that owner/readiness is satisfied or fall back to a local tracker"),
            "approved-external-association": (adoption, "explicitly configured GitHub Issues target remains external and does not require a local register"),
        }
        for name, (carrier, expectation) in cases.items():
            with self.subTest(case=name):
                self.assertIn(normalized(expectation), normalized(carrier))

    def test_optional_jev_inherits_the_external_issue_owner_boundary(self):
        # Jev triage is advisory: the base workflow remains the single routing path,
        # whose managed current contract requires a qualified GitHub target or an
        # actionable unavailable/deferred result rather than a local register.
        jev = (ROOT / "skills/finish-session-jev/SKILL.md").read_text()
        self.assertIn("read the installed sibling\n`../finish-session/SKILL.md` in full", jev)
        # Inspect the composed active consumer, not only initialization's promise.
        base = (ROOT / "skills/finish-session/SKILL.md").read_text()
        for clause in (
            "follow the project's declared canonical owner",
            "never create a local fallback or write to a retained historical register",
            "does not reactivate old local ownership",
            "load and follow `track-open-issue`",
            "issue tracking: UNAVAILABLE",
            "This is an existence check only",
            "Do not execute deployment procedures",
            "Do not create, edit or remove STATE",
        ):
            self.assertIn(clause, base)
        target = "https://github.com/elsonidoq/skills/issues"
        self.assertIn(target, (ROOT / "AGENTS.md").read_text())
        self.assertIn(target, (ROOT / "docs/index.md").read_text())
        lifecycle = (ROOT / "skills/track-open-issue/SKILL.md").read_text()
        self.assertIn('gh auth status --hostname "$HOST"', lifecycle)
        self.assertIn("After every create, update, close, or reopen, independently GET", lifecycle)
        self.assertIn("required write authority is unavailable", lifecycle)
        discovery = stage(SKILL.read_text(), "Discovery")
        for clause in (
            "explicitly configured GitHub Issues target is an external owner",
            "issue tracking: UNAVAILABLE",
            "do not create or require `docs/open_issues.md`",
            "do not claim that owner/readiness is satisfied or fall back to a local tracker",
        ):
            with self.subTest(clause=clause):
                self.assertIn(normalized(clause), normalized(discovery))

    def test_external_owner_guards_reject_deletion(self):
        text = SKILL.read_text()
        self.assertEqual(check_contract(text), [])
        for diagnostic, (name, phrases) in ISSUE_OWNER_RULES.items():
            with self.subTest(boundary=diagnostic):
                phrase = phrases[0]
                body = stage(text, name)
                pattern = r"\s+".join(re.escape(word) for word in phrase.split())
                changed = text.replace(body, re.sub(pattern, "REMOVED", body, count=1), 1)
                self.assertTrue(any(error.startswith(diagnostic + ": missing") for error in check_contract(changed)))


class WorkflowOwnershipOutputTests(unittest.TestCase):
    """Authored adoption outputs, not a generator or live agent simulation."""
    def test_new_and_refresh_resolve_contracts_preserve_associations(self):
        rows = json.loads((HERE / "fixtures/workflow-ownership-outputs.json").read_text())
        adoption = stage(SKILL.read_text(), "Adoption")
        self.assertEqual(len([row for row in rows if row.get("route") != "policy-only"]), 2)
        rows = [row for row in rows if row.get("route") != "policy-only"]
        for row in rows:
            with self.subTest(case=row["name"]):
                custom = row["before"].split("<!-- coherence-suite-contract:start -->")[0]
                self.assertTrue(row["after"].startswith(custom))
                for target in re.findall(r"\]\(INSTALL/([^)]+)\)", row["after"]):
                    self.assertIn(target, adoption)
                    self.assertTrue((ROOT / "skills" / target).is_file(), target)
                self.assertEqual(len(re.findall(r"\]\(INSTALL/", row["after"])), 5)
                self.assertNotIn("request →", row["after"])
                self.assertIn("no upkeep", row["after"])
                self.assertIn("Refer to these owners rather than reproduce their workflow rules", adoption)
                self.assertIn("missing installed contracts stop adoption/refresh", adoption)
                self.assertIn("preserve custom memory paths, docs, policy", adoption)
                self.assertIn("no STATE initialization or upkeep", adoption)
                self.assertIn("Package references do not supersede local product policy or authorize work", adoption)

    def test_unsafe_expansion_and_dirty_approval_guards(self):
        text = SKILL.read_text()
        for clause, diagnostic in (
            ("Automatically create STATE.md", "permission-auto-state"),
            ("Reset existing memory on refresh", "permission-memory-reset"),
            ("Edit dirty targets without approval", "permission-dirty-overlap"),
            ("All merged-stage writes are unconditionally permitted", "permission-merged-writes"),
        ):
            with self.subTest(unsafe=diagnostic):
                self.assertTrue(any(e.startswith(diagnostic + ":") for e in check_contract(text + "\n" + clause)))
        self.assertIn("Proposal-first", stage(text, "Approval"))
        self.assertIn("general plan approval is not an overlap waiver", stage(text, "Preflight"))


class PreservationTests(unittest.TestCase):
    """Each original ledger row has a separately named carrying-stage check."""


def positive_check(row):
    def test(self):
        body = normalized(stage(SKILL.read_text(), row["stage"]))
        for phrase in row["requires"]:
            self.assertIn(normalized(phrase), body, row["id"])
    return test


for row in BASELINE["ledger"]:
    setattr(PreservationTests, row["positive"], positive_check(row))


class ScenarioTests(unittest.TestCase):
    """Pressure contexts select source clauses; no agent transcript or write simulator."""
    def test_fixture_rows_and_source_groups_are_accounted(self):
        seen = set()
        for scenario in SCENARIOS:
            self.assertTrue(scenario["context"])
            self.assertTrue(scenario["bound"])
            self.assertIn(scenario["branch"], ("all", "clean", "non-clean"))
            for row in scenario["rows"]:
                self.assertIn(row, ROWS); seen.add(row)
        self.assertEqual(seen, set(ROWS))


def scenario_check(scenario):
    def test(self):
        text = SKILL.read_text()
        for name in scenario["rows"]:
            row = ROWS[name]
            body = normalized(stage(text, row["stage"]))
            for phrase in row["requires"]:
                self.assertIn(normalized(phrase), body, f"{scenario['name']}: {scenario['bound']}")
        for rule in scenario.get("asset_rules", []) + scenario.get("policy_rules", []) + scenario.get("decision_rules", []):
            self.assertFalse(any(e.startswith(rule + ":") for e in check_contract(text)), scenario["name"])
        if scenario.get("asset_route"):
            self.assertLess(normalized(text).index("first verify"),
                            normalized(text).index(normalized(SPECKIT_RULES["assets-discovery"][1][0])))
            self.assertEqual(check_contract(text), [])
            bypass = text.replace(stage(text, "Adoption"), stage(text, "Adoption") + "\nReturn immediately after compatible adoption.\n", 1)
            self.assertIn("permission-assets-bypass: contradictory permission", check_contract(bypass))
        if scenario["branch"] == "non-clean":
            self.assertIn("on a non-clean project first verify", normalized(stage(text, "Preflight")))
        elif scenario["branch"] == "clean":
            self.assertIn("on the clean branch", normalized(stage(text, "Documentation")))
    return test


for scenario in SCENARIOS:
    setattr(ScenarioTests, f"test_{scenario['name']}", scenario_check(scenario))


class StatusFixtureTests(unittest.TestCase):
    def status(self, kind):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            def git(*args):
                return subprocess.check_output(["git", "-C", directory, *args], text=True)
            git("init", "-q")
            if kind == "tracked":
                (root / "tracked.txt").write_text("baseline\n")
                git("add", "tracked.txt")
                git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                    "-c", "core.hooksPath=/dev/null", "commit", "-qm", "isolated fixture")
                (root / "tracked.txt").write_text("changed\n")
            elif kind == "untracked":
                (root / "untracked.txt").write_text("fixture\n")
            return git("status", "--short")

    def test_clean_has_no_status_output(self):
        self.assertEqual(self.status("clean"), "")
        self.assertIn("clean means no output", normalized(stage(SKILL.read_text(), "Preflight")))

    def test_tracked_dirty_is_nonclean(self):
        self.assertIn(" M tracked.txt", self.status("tracked"))
        self.assertIn("on a non-clean project first verify", normalized(stage(SKILL.read_text(), "Preflight")))

    def test_untracked_only_is_nonclean(self):
        self.assertEqual(self.status("untracked"), "?? untracked.txt\n")
        self.assertIn("untracked files make the project non-clean", normalized(stage(SKILL.read_text(), "Preflight")))


class MutationTests(unittest.TestCase):
    def test_original_candidate_passes_before_mutation(self):
        self.assertEqual(check_contract(SKILL.read_text()), [])

    def test_every_carrying_stage_deletion_fails_even_with_summary_mentions(self):
        text = SKILL.read_text()
        for name in STAGES:
            with self.subTest(stage=name):
                body = stage(text, name)
                summaries = "Summary only: " + " ".join(phrase for row in BASELINE["ledger"]
                                                    if row["stage"] == name for phrase in row["requires"])
                changed = summaries + "\n" + text.replace(body, "", 1)
                errors = check_contract(changed)
                self.assertTrue(any(e.startswith("stage-order:") for e in errors), errors)
                for diagnostic, (carrying, _) in SPECKIT_RULES.items():
                    if carrying == name:
                        self.assertTrue(any(e.startswith(diagnostic + ": missing") for e in errors), diagnostic)
                for row in BASELINE["ledger"]:
                    if row["stage"] == name:
                        self.assertTrue(any(e.startswith(row["id"] + ":") for e in errors), row["id"])

    def test_stage_reordering_fails_named_diagnostic(self):
        text = SKILL.read_text()
        a, b = stage(text, "Approval"), stage(text, "Adoption")
        changed = text.replace(a, "TEMP_STAGE", 1).replace(b, a, 1).replace("TEMP_STAGE", b, 1)
        self.assertIn("stage-order: missing, duplicated or reordered carrying stages", check_contract(changed))

    def test_contradictory_permission_vectors_fail_specific_diagnostics(self):
        vectors = json.loads((HERE / "fixtures/unsafe-permissions.json").read_text())
        self.assertEqual({v["diagnostic"] for v in vectors}, set(UNSAFE))
        text = SKILL.read_text()
        for vector in vectors:
            with self.subTest(diagnostic=vector["diagnostic"]):
                body = stage(text, vector["stage"])
                changed = text.replace(body, body + "\n" + vector["text"] + "\n", 1)
                self.assertIn(vector["diagnostic"] + ": contradictory permission", check_contract(changed))


def deletion_check(row):
    def test(self):
        text = SKILL.read_text()
        body = stage(text, row["stage"])
        for phrase in row["requires"]:
            with self.subTest(guard=phrase):
                pattern = r"\s+".join(re.escape(word) for word in phrase.split())
                altered, count = re.subn(pattern, "[guard removed]", body, count=1, flags=re.I)
                self.assertEqual(count, 1, phrase)
                errors = check_contract(text.replace(body, altered, 1))
                self.assertTrue(any(e.startswith(row["id"] + ": missing") for e in errors), errors)
    return test


for row in BASELINE["ledger"]:
    setattr(MutationTests, row["negative"], deletion_check(row))


# Frozen source oracle, not current operational guidance: exact old SKILL.md bytes
# from a9db66274d51a61bafd537f1ba8511201fbfb21f, captured via explicit repository audit.
OLD_CONTRACT_SHA256 = "2a8d31f15e5933cefd9c6181e7e82f5002acc893e0e28b76a017460812800667"


class SpecKitTests(unittest.TestCase):
    """Scoped source pressure checks, not execution of SpecKit or invented filesystem proof."""
    def test_new_expectations_fail_old_contract_with_named_diagnostics(self):
        old_bytes = (HERE / "fixtures/old-initialize-coherence.txt").read_bytes()
        self.assertEqual(hashlib.sha256(old_bytes).hexdigest(), OLD_CONTRACT_SHA256)
        old = old_bytes.decode("utf-8")
        errors = check_contract(old)
        for diagnostic in SPECKIT_RULES:
            self.assertTrue(any(e.startswith(diagnostic + ": missing") for e in errors), diagnostic)
        self.assertEqual(check_contract(SKILL.read_text()), [])


def asset_positive(rule):
    def test(self):
        self.assertFalse(any(e.startswith(rule + ":") for e in check_contract(SKILL.read_text())))
    return test


def asset_deletion(rule):
    def test(self):
        text = SKILL.read_text()
        name, phrases = SPECKIT_RULES[rule]
        body = stage(text, name)
        for phrase in phrases:
            with self.subTest(guard=phrase):
                pattern = r"\s+".join(re.escape(word) for word in phrase.split())
                altered, count = re.subn(pattern, "[asset guard removed]", body, count=1, flags=re.I)
                self.assertEqual(count, 1, phrase)
                # A summary elsewhere cannot replace an operational carrying clause.
                changed = "Summary only: " + phrase + "\n" + text.replace(body, altered, 1)
                self.assertTrue(any(e.startswith(rule + ": missing") for e in check_contract(changed)))
    return test


for rule in SPECKIT_RULES:
    setattr(SpecKitTests, "test_" + rule.replace("-", "_") + "_positive", asset_positive(rule))
    setattr(SpecKitTests, "test_" + rule.replace("-", "_") + "_deletion_rejected", asset_deletion(rule))


class InstallerMutationTests(unittest.TestCase):
    """Run existing isolated behavioral LinkTests against in-memory installer mutants."""
    def test_installer_guard_mutations_fail_specific_existing_fixtures(self):
        filename = ROOT / "scripts/test-planner-workflow.py"
        spec = importlib.util.spec_from_file_location("coherence_link_fixtures", filename)
        fixtures = importlib.util.module_from_spec(spec); spec.loader.exec_module(fixtures)
        source = (ROOT / "scripts/install-links.py").read_text()
        mutations = [
            ("retirement-inventory", '           "install-memory", "initialize-documentation")', ')',
             "test_coherence_retirement_inventory_is_explicit"),
            ("retirement-proof", "old.is_symlink() and target(old) == skills / name", "old.is_symlink()",
             "test_coherence_retired_foreign_and_uncertain_entries_preserved"),
            ("retirement-race", "not path.is_symlink() or identity(path) != expected_identity\n            or target(path) != expected_target", "False",
             "test_retirement_race_preserves_replaced_foreign_link"),
            ("late-retirement-race", "not path.is_symlink() or identity(path) != expected_identity\n            or target(path) != expected_target", "False",
             "test_retirement_race_during_backup_directory_creation"),
            ("settings-byte-race", "before != settings_before or identity(settings) != settings_identity", "json.loads(before) != data",
             "test_settings_byte_race_preserves_equivalent_json"),
            ("late-settings-race", "settings.read_text() != before or identity(settings) != settings_identity", "False",
             "test_settings_race_after_temp_write_preserves_foreign_bytes"),
            ("current-link-race", "elif target(dst) != src:", "elif False:",
             "test_current_link_race_preserves_foreign_work"),
        ]
        for diagnostic, old, new, test_name in mutations:
            with self.subTest(diagnostic=diagnostic):
                self.assertIn(old, source)
                baseline = unittest.TestResult()
                fixtures.LinkTests(test_name).run(baseline)
                self.assertTrue(baseline.wasSuccessful(), baseline.errors + baseline.failures)
                changed = source.replace(old, new)
                if diagnostic == "settings-byte-race":
                    # Both snapshot checks protect this race. Recreate the demonstrated
                    # old behavior, not a partial mutant caught by the later guard.
                    later = "settings.read_text() != before or identity(settings) != settings_identity"
                    self.assertIn(later, changed)
                    changed = changed.replace(later, "settings.read_text() != before")
                mutant = types.ModuleType("coherence_installer_mutant")
                exec(compile(changed, str(ROOT / "scripts/install-links.py"), "exec"), mutant.__dict__)
                result = unittest.TestResult()
                with mock.patch.object(fixtures, "links", mutant), contextlib.redirect_stdout(io.StringIO()):
                    fixtures.LinkTests(test_name).run(result)
                self.assertFalse(result.wasSuccessful(), f"{diagnostic}: surviving mutant")
                self.assertTrue(any(test.id().endswith(test_name) or test_name in test.id()
                                    for test, _ in result.errors + result.failures), diagnostic)


if __name__ == "__main__":
    baseline_only = "--baseline" in sys.argv
    if baseline_only:
        sys.argv.remove("--baseline")
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(BaselineTests)
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        raise SystemExit(not result.wasSuccessful())
    unittest.main(verbosity=2)
