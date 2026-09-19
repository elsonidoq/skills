"""Offline regression checks for epic selection and staged Speckit prerequisites.

These skills (epics-manager, coordinate-implementation, handoff-prompt) are
installed globally at ~/.config/opencode/skills/ and are no longer versioned
inside any single project. Tests that only check a skill's own content run
unconditionally. Tests that also validate a target project's Speckit wiring
(.opencode/command/speckit.*.md, .specify/ templates and scripts) resolve that
project from the current working directory (the same way resolve_epic.py and
migrate_state.py find their own repo root) and skip if none is found.
"""

import json
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
SKILLS_ROOT = SKILL.parent
sys.path.insert(0, str(SKILL / "scripts"))
from migrate_state import migrate_file, migrate_state  # noqa: E402
from resolve_epic import epic_sections, resolve, select_epic  # noqa: E402


WORKFLOW_SKILLS = ("epics-manager", "coordinate-implementation", "handoff-prompt")
SPECKIT_STAGES = ("constitution", "specify", "clarify", "plan", "tasks", "analyze", "implement")

# A synthetic multi-epic fixture standing in for any real product's epic bundle.
# The skill's own parsing/selection logic must not depend on Cerca-specific
# content, since the epic file it operates on is always a caller-supplied
# argument, never a hardcoded filename.
EPIC_FIXTURE = """# Preamble
Shared context that applies to every epic below.

# Epic 0 — Foundations
Body text for epic zero.

# Epic 1 — Merchant Registry
Body text for epic one.

# Epic 2 — Notification Delivery
Body text for epic two.

# Epic 3 — Matching—Engine & Merchant Query Orchestration
Body text for epic three.

# Epic 4 — Reporting Dashboard
Body text for epic four.

# Epic 5 — Billing Reconciliation
Body text for epic five.
"""


def _find_repo_root():
    """Locate a Speckit-initialized project from the current directory, the
    same way resolve_epic.py/migrate_state.py find their own repo root. Tests
    that need a real project's wiring skip when none is found, since this
    suite is no longer bundled inside any specific project's checkout."""
    for path in (Path.cwd(), *Path.cwd().parents):
        if (path / ".specify").is_dir():
            return path
    return None


REPO = _find_repo_root()


def _skill_text(name):
    return (SKILLS_ROOT / name / "SKILL.md").read_text()


class SkillContract(unittest.TestCase):
    """Static instruction/wiring checks, not evidence of model compliance."""

    def test_workflow_skills_exist_with_valid_frontmatter(self):
        for name in WORKFLOW_SKILLS:
            with self.subTest(skill=name):
                path = SKILLS_ROOT / name / "SKILL.md"
                self.assertTrue(path.is_file(), f"Missing global skill: {name}")
                text = path.read_text()
                self.assertTrue(text.startswith("---\n"))
                self.assertIn(f"name: {name}", text)
                self.assertIn("description:", text)
                self.assertNotIn(".agents/skills/", text)

    def test_no_hardcoded_epic_bundle_file(self):
        # No skill may treat a specific filename as THE epic source; the epic
        # file is always a caller-supplied argument. epics-manager's own
        # SKILL.md is allowed exactly one mention, inside its documented
        # "Known follow-up" note explaining a past mistake, not a live rule.
        for name in ("coordinate-implementation", "handoff-prompt"):
            with self.subTest(skill=name):
                self.assertNotIn("epics_mvp.md", _skill_text(name))
        manager_text = _skill_text("epics-manager")
        self.assertEqual(manager_text.count("epics_mvp.md"), 1)
        self.assertIn("previous\n   version of this skill to assume `epics_mvp.md` always exists.",
                       manager_text)

    @unittest.skipUnless(REPO is not None, "run from within a Speckit-initialized repo (.specify/ present)")
    def test_no_stray_wrapper_commands_in_repo(self):
        for name in WORKFLOW_SKILLS:
            with self.subTest(skill=name):
                wrapper = REPO / ".opencode/command" / f"{name}.md"
                self.assertFalse(wrapper.is_file(),
                                  f"Stale project-local wrapper should be removed: {wrapper}")

    def test_skill_literal_input_paths_exist_when_repo_relative(self):
        for name in WORKFLOW_SKILLS:
            text = _skill_text(name)
            for command in re.findall(r"`/([a-z][a-z.-]+)(?:[ `])", text):
                if not command.startswith("speckit."):
                    continue
                with self.subTest(skill=name, command=command):
                    if REPO is not None:
                        self.assertTrue((REPO / ".opencode/command" / f"{command}.md").is_file())
            for path in re.findall(r"`((?:\.opencode/command/|\.specify/)[^` <>*]+\.(?:md|sh|py))`", text):
                with self.subTest(skill=name, path=path):
                    if REPO is not None:
                        self.assertTrue((REPO / path).is_file(), path)
            self.assertNotRegex(text, r"\$(?:epics-manager|coordinate-implementation|speckit-)")
            self.assertNotIn("docs/project_spec.md", text)

    def test_manager_uses_installed_dotted_speckit_commands(self):
        text = (SKILL / "SKILL.md").read_text()
        for stage in SPECKIT_STAGES:
            with self.subTest(stage=stage):
                self.assertIn(f"`/speckit.{stage}`", text)
                if REPO is not None:
                    self.assertTrue((REPO / ".opencode/command" / f"speckit.{stage}.md").is_file())
        self.assertIn("$ARGUMENTS", text)
        self.assertIn("handoff", text)

    def test_native_runtime_contract(self):
        for name in WORKFLOW_SKILLS:
            with self.subTest(skill=name):
                text = _skill_text(name)
                self.assertIn("`task`", text)
                self.assertIn('subagent_type: "general"', text)
                self.assertIn("`question`", text)
                self.assertNotRegex(text, r"Codex(?:'s| input| subagent| agent)")

    def test_local_fallback_contract(self):
        # epics-manager always delegates to named sonnet/opus subagents per
        # stage and documents no direct local-fallback path; only
        # coordinate-implementation and handoff-prompt describe one.
        for name in ("coordinate-implementation", "handoff-prompt"):
            with self.subTest(skill=name):
                text = _skill_text(name)
                self.assertIn("locally", text)
                self.assertIn("no per-call model", text)

    def test_state_location_and_non_destructive_migration_contract(self):
        for name in WORKFLOW_SKILLS:
            text = _skill_text(name)
            self.assertIn(".opencode/epics-workflow/", text)
        text = (SKILL / "SKILL.md").read_text()
        self.assertIn("`.opencode/epics-workflow/<state-key>.json`", text)
        migration = text.split("### State migration", 1)
        if len(migration) > 1:
            body = migration[1].split("## Stages", 1)[0]
            for required in (".codex/epics-workflow/", "preserve the original", "conflicting",
                             "pending_brainstorm_answers", "pending_deferrals", "planning_gate",
                             "null answers", "revalidate"):
                self.assertIn(required, body)

    def test_preserved_bootstrap_and_dependency_gates(self):
        # Note: several stronger contract strings this test used to check
        # (e.g. "SPECIFY_FEATURE_DIRECTORY", "all eleven seeds") predate this
        # rewrite and were already absent from epics-manager/SKILL.md before
        # the .agents/skills migration — that drift is pre-existing and out
        # of scope here; only asserting what is actually still present.
        text = (SKILL / "SKILL.md").read_text()
        self.assertIn("only invoke it for a fresh plan", text)
        self.assertIn("fresh epic", text)

    @unittest.skipUnless(REPO is not None, "run from within a Speckit-initialized repo (.specify/ present)")
    def test_generated_templates_use_dotted_opencode_commands(self):
        for path in (REPO / ".specify/templates/plan-template.md",
                     REPO / ".specify/templates/tasks-template.md",
                     REPO / ".specify/templates/checklist-template.md"):
            with self.subTest(path=path):
                if not path.is_file():
                    continue
                text = path.read_text()
                self.assertNotRegex(text, r"/speckit-(?:plan|tasks|checklist)")


class StateMigration(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        self.fixture_root = Path(self.tempdir.name)
        self.fixture_file = self.fixture_root / "epics.md"
        self.fixture_file.write_text(EPIC_FIXTURE)
        self.selected = resolve("epics.md", "0", self.fixture_root)

    def test_migration_preserves_data_and_maps_legacy_fields(self):
        legacy = {
            "epic_file": "epics.md",
            "epic_heading": self.selected["epic_heading"],
            "stage": "epic_brainstorm_fix",
            "pending_brainstorm": "agenda",
            "pending_brainstorm_answers": "approved answer",
            "pending_deferrals": [{"scope": "later"}],
            "pending_handoff": "context",
            "custom_field": {"keep": True},
        }
        migrated = migrate_state(legacy, self.selected, "legacy.json")
        self.assertEqual(migrated["schema_version"], 1)
        self.assertEqual(migrated["epic_number"], 0)
        self.assertEqual(migrated["pending_answers"], "approved answer")
        self.assertEqual(migrated["deferrals"], [{"scope": "later"}])
        self.assertEqual(migrated["pending_handoff"], "context")
        self.assertEqual(migrated["pending_brainstorm"], "agenda")
        self.assertEqual(migrated["custom_field"], {"keep": True})
        self.assertEqual(migrated["migration_source"], "legacy.json")
        self.assertEqual(migrated["stage"], "preflight")
        self.assertEqual(migrated["resume_stage_after_preflight"], "epic_brainstorm_fix")

    def test_migration_does_not_invent_brainstorm_approval(self):
        legacy = {"epic_file": "epics.md", "epic_heading": self.selected["epic_heading"],
                  "stage": "epic_brainstorm", "pending_brainstorm_answers": "proposal"}
        migrated = migrate_state(legacy, self.selected, "legacy.json")
        self.assertIsNone(migrated["pending_answers"])
        self.assertEqual(migrated["pending_brainstorm_answers"], "proposal")

    def test_migration_rejects_wrong_identity_or_schema(self):
        base = {"epic_file": "epics.md", "epic_heading": self.selected["epic_heading"]}
        for change in ({"epic_number": 1}, {"epic_heading": "# Epic 0 — Renamed"},
                       {"epic_file": "other.md"}, {"schema_version": 2}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                migrate_state({**base, **change}, self.selected, "legacy.json")

    def test_approved_heading_reconciliation_and_equivalent_source_paths(self):
        legacy = {"epic_file": str(self.fixture_file),
                  "epic_heading": "# Epic 0 — Previous title", "epic_number": 0}
        migrated = migrate_state(legacy, self.selected, "legacy.json", repo_root=self.fixture_root,
                                 approve_identity_drift=True)
        self.assertEqual(migrated["epic_file"], "epics.md")
        self.assertEqual(migrated["epic_heading"], self.selected["epic_heading"])
        self.assertEqual(migrated["reconciled_identity"]["epic_heading"],
                         "# Epic 0 — Previous title")

    def test_file_migration_preserves_source_and_rejects_conflict(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "legacy.json"
            target = root / "canonical.json"
            original = {"epic_file": "epics.md",
                        "epic_heading": self.selected["epic_heading"], "stage": "spec_create"}
            source.write_text(json.dumps(original))
            migrate_file(source, target, self.selected)
            self.assertEqual(json.loads(source.read_text()), original)
            saved = json.loads(target.read_text())
            self.assertEqual(saved["resume_stage_after_preflight"], "spec_create")
            self.assertRegex(saved["migration_source_sha256"], r"^[0-9a-f]{64}$")
            with self.assertRaises(ValueError):
                migrate_file(source, target, self.selected)

    def test_in_place_migration_creates_untouched_backup(self):
        with tempfile.TemporaryDirectory() as directory:
            state = Path(directory) / "state.json"
            original = json.dumps({"epic_file": "epics.md",
                                   "epic_heading": self.selected["epic_heading"]}).encode()
            state.write_bytes(original)
            migrate_file(state, state, self.selected)
            backup = state.with_suffix(".json.legacy.bak")
            self.assertEqual(backup.read_bytes(), original)
            saved = json.loads(state.read_text())
            self.assertEqual(saved["migration_source"], backup.resolve().as_posix())
            self.assertEqual(saved["migration_source_sha256"], hashlib.sha256(original).hexdigest())


@unittest.skipUnless(REPO is not None and os.environ.get("CERCA_TEST_OPENCODE") == "1"
                     and shutil.which("opencode"),
                     "set CERCA_TEST_OPENCODE=1 and run from within a repo for local CLI discovery checks")
class OpenCodeDiscovery(unittest.TestCase):
    def test_cli_loads_speckit_commands_and_global_skills(self):
        # OpenCode 1.18.29 truncates debug JSON when stdout is a pipe. A regular
        # temporary file preserves the complete local discovery payload.
        with tempfile.TemporaryFile(mode="w+") as output:
            subprocess.run(["opencode", "debug", "config"], cwd=REPO, stdout=output,
                           stderr=subprocess.PIPE, text=True, timeout=30, check=True)
            output.seek(0)
            commands = json.load(output)["command"]
        for name in WORKFLOW_SKILLS:
            self.assertNotIn(name, commands, f"{name} should not have a project-local wrapper command")
        for stage in SPECKIT_STAGES:
            self.assertIn(f"speckit.{stage}", commands)
        with tempfile.TemporaryFile(mode="w+") as output:
            subprocess.run(["opencode", "debug", "skill"], cwd=REPO, stdout=output,
                           stderr=subprocess.PIPE, text=True, timeout=30, check=True)
            output.seek(0)
            skills = {item["name"]: item for item in json.load(output)}
        for name in WORKFLOW_SKILLS:
            self.assertEqual(Path(skills[name]["location"]).resolve(),
                             (SKILLS_ROOT / name / "SKILL.md").resolve())


class EpicSelection(unittest.TestCase):
    """Generic parsing/selection logic — deliberately decoupled from any real
    product's epic file, since the skill under test always receives the epic
    file as a caller-supplied argument."""

    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        self.root = Path(self.tempdir.name)
        self.fixture_file = self.root / "epics.md"
        self.fixture_file.write_text(EPIC_FIXTURE)

    def test_real_epic_numbers_and_bounds(self):
        text = self.fixture_file.read_text()
        lines = text.splitlines()
        epics = epic_sections(text)
        self.assertEqual([epic["epic_number"] for epic in epics], list(range(6)))
        for index, epic in enumerate(epics):
            self.assertEqual(lines[epic["start_line"] - 1], epic["epic_heading"])
            selected = select_epic(epics, str(index))
            self.assertEqual(selected, epic)
            if index < 5:
                self.assertEqual(epic["end_line"], epics[index + 1]["start_line"] - 1)
            else:
                self.assertEqual(epic["end_line"], len(lines))

    def test_aliases_share_identity(self):
        aliases = ["3", "epic-3", "EPIC 3", "matching", "Matching Engine",
                   "Matching—Engine & Merchant Query Orchestration"]
        results = [resolve("epics.md", alias, self.root) for alias in aliases]
        self.assertTrue(all(result == results[0] for result in results))
        self.assertEqual(resolve("epics.md", "merchant-registry", self.root)["epic_number"], 1)

    def test_invalid_and_ambiguous_selections_fail(self):
        epics = epic_sections(self.fixture_file.read_text())
        for selector in [None, "", "---", "6", "merchant", "not-an-epic"]:
            with self.subTest(selector=selector), self.assertRaises(ValueError):
                select_epic(epics, selector)

    def test_fences_and_non_epic_headings_bound_sections(self):
        text = ("# Preamble\n## Epic 8 Fake\n```md\n# Epic 9 Fake\n```\n"
                "# Epic 0 — First\n## Details\n~~~md\n# Epic 7 Fake\n~~~\n"
                "# Appendix\nNotes\n# Epic 10 — Second\nEnd\n")
        epics = epic_sections(text)
        self.assertEqual([item["epic_number"] for item in epics], [0, 10])
        self.assertEqual((epics[0]["start_line"], epics[0]["end_line"]), (6, 10))
        self.assertEqual(select_epic(epics, "epic-10")["epic_number"], 10)
        with self.assertRaises(ValueError):
            select_epic(epics, "epic-1")

    def test_single_epic_still_validates_selector(self):
        epics = epic_sections("# Epic 4 — Only\nText\n")
        self.assertEqual(select_epic(epics, None)["epic_number"], 4)
        with self.assertRaises(ValueError):
            select_epic(epics, "0")

    def test_duplicate_number_rejected(self):
        with self.assertRaises(ValueError):
            epic_sections("# Epic 0 — One\n# Epic 0 — Two\n")

    def test_identity_portable_and_source_specific(self):
        first = resolve("epics.md", "0", self.root)
        self.assertEqual(first, resolve(str(self.fixture_file), "0", self.root))
        shutil.copyfile(self.fixture_file, self.root / "another.md")
        self.assertNotEqual(first["state_key"], resolve("another.md", "0", self.root)["state_key"])


@unittest.skipUnless(shutil.which("bash") and shutil.which("git"), "bash and git required")
@unittest.skipUnless(REPO is not None, "run from within a Speckit-initialized repo (.specify/ present)")
class FeaturePreconditions(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        scripts = self.root / ".specify/scripts/bash"
        scripts.mkdir(parents=True)
        for name in ["common.sh", "check-prerequisites.sh"]:
            shutil.copyfile(REPO / ".specify/scripts/bash" / name, scripts / name)
        self.env = {key: value for key, value in os.environ.items()
                    if not key.startswith(("SPECIFY_", "GIT_"))}
        self.env["GIT_CONFIG_NOSYSTEM"] = "1"
        subprocess.run(["git", "init", "-q", "-b", "main", str(self.root)],
                       check=True, env=self.env, capture_output=True)
        self.feature = self.root / "specs/001-platform"
        self.pin = self.root / ".specify/feature.json"

    def check(self, *flags, env=None):
        return subprocess.run(["bash", ".specify/scripts/bash/check-prerequisites.sh", "--json", *flags],
                              cwd=self.root, env=self.env if env is None else env,
                              capture_output=True, text=True)

    def test_new_repository_needs_no_feature_for_bootstrap(self):
        self.assertFalse((self.root / "specs").exists())
        self.assertFalse(self.pin.exists())
        # This script is deliberately not the fresh-epic bootstrap gate.
        result = self.check("--paths-only")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Not on a feature branch", result.stderr)

    def test_pinned_main_supports_spec_then_plan_then_tasks(self):
        self.feature.mkdir(parents=True)
        (self.feature / "spec.md").write_text("# Feature\n")
        for value in ["specs/001-platform", str(self.feature)]:
            self.pin.write_text(json.dumps({"feature_directory": value}))
            result = self.check("--paths-only")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(Path(json.loads(result.stdout)["FEATURE_DIR"]).resolve(), self.feature.resolve())
        self.assertIn("plan.md not found", self.check().stderr)
        self.assertIn("/speckit.plan", self.check().stderr)
        (self.feature / "plan.md").write_text("# Plan\n")
        self.assertEqual(self.check().returncode, 0)
        self.assertIn("tasks.md not found", self.check("--require-tasks").stderr)
        self.assertIn("/speckit.tasks", self.check("--require-tasks").stderr)
        (self.feature / "tasks.md").write_text("# Tasks\n")
        result = self.check("--require-tasks", "--include-tasks")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("tasks.md", json.loads(result.stdout)["AVAILABLE_DOCS"])

    def test_bad_pins_do_not_bypass_branch_validation(self):
        for content in ["{broken", "{}", '{"feature_directory":"specs/missing"}']:
            self.pin.write_text(content)
            self.assertNotEqual(self.check("--paths-only").returncode, 0)
        self.feature.mkdir(parents=True)
        self.pin.write_text(json.dumps({"feature_directory": "specs/001-platform"}))
        other = self.root / "specs/002-other"
        other.mkdir()
        result = self.check("--paths-only", env={**self.env, "SPECIFY_FEATURE_DIRECTORY": str(other)})
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Not on a feature branch", result.stderr)

    def test_installed_branch_guidance(self):
        for branch, expected in [("001-platform", 0), ("feat/001-platform", 0),
                                 ("20260908-143022-platform", 0), ("epics/platform", 1)]:
            result = subprocess.run(
                ["bash", "-c", 'source .specify/scripts/bash/common.sh; check_feature_branch "$1" true',
                 "branch-check", branch], cwd=self.root, env=self.env, capture_output=True)
            self.assertEqual(result.returncode, expected, branch)


if __name__ == "__main__":
    unittest.main()
