#!/usr/bin/env python3
"""Static routing/mutation fixtures; not live dispatch or model-obedience proof."""

from pathlib import Path
import unittest

TEXT = (Path(__file__).parents[1] / "SKILL.md").read_text(encoding="utf-8")

# Source-named guards: deleting any guard must invalidate the instruction carrier.
GUARDS = {
    "support": ("provider-documented supported effort", "permitted usable runtime capability",
                "task-specific writer/reviewer role, actual tools, permissions and observed context"),
    "approval": ("complete approved task/reviewer assignment snapshot", "single combined final approval",
                 "no routine second assignment-approval question", "Missing/changed approval"),
    "drift": ("Immediately before each dispatch", "advisory applicability/uncertainty disposition",
              "Drift or unusable selection stops", "never substitution"),
    "effort": ("least provider-documented usable supported effort justified as adequate after decomposition",
               "Higher effort needs concrete residual reasoning or lower-setting counterevidence",
               "reviewer role, family name or spare budget alone never justify high/max",
               "returns for decomposition/stronger observable acceptance, not reflexive max"),
    "advisory": ("not a synthetic", "noncomparable benchmark harnesses cannot be ranked",
                 "owner preference is not a measured advantage", "Never fabricate",
                 "no qualifying row is not automatically excluded", "explicit bounded owner uncertainty disposition",
                 "never automatic whole-CSV prompts"),
    "retry": ("Luna → Terra → Sol", "three total attempts from Luna, two from Terra, one from Sol",
              "Astra is never an automatic fourth attempt", "Do not skip an unavailable next family",
              "Inspect the failed run and invocation, diagnose", "Unknown invocation/cause stops",
              "Only after\ninspection and established safe task state", "least adequate supported retry effort",
              "within existing owner-selected routing authority", "no preselected retry effort",
              "automatic effort increment or blanket per-retry owner question",
              "changed scope or unclear safety/capability stops for renewed owner decision",
              "grants no failed-attempt commit/inverse or real rollback authority"),
    "batch": ("complete approved implementation task list, including completed tasks",
              "Up to three bounded implementation tasks may run locally only",
              "current owner-selected exact binding/effort matches each task",
              "observed context capacity is adequate", "More than three implementation tasks require delegation",
              "consecutive task entries in the approved list", "approved compatible exact binding/effort and context",
              "delegate only asynchronously in the background", "run implementation batches in parallel",
              "Never pull\n   a distant producer forward or reorder a prerequisite"),
    "review": ("usable fresh independent reviewer before implementation", "No per-task reviews",
               "one fresh independent\nfinal review", "implementer cannot self-certify independent review"),
    "checkpoint": ("commits each task separately", "evidence-only checkpoint before later task writes or handoff",
                   "Inspect the failed run and tool invocation before retry or relaunch"),
    "context": ("observed context\n  headroom is adequate", "smaller fresh brief with durable handoff context",
                "do not force reuse or equate billed tokens with occupied context"),
}


def contract_errors(text):
    return [f"{name}: missing {phrase}" for name, phrases in GUARDS.items()
            for phrase in phrases if phrase not in text]


class BatchingContractTests(unittest.TestCase):
    def test_current_source_has_all_dispatch_guards(self):
        self.assertEqual(contract_errors(TEXT), [])
        for obsolete in ("sonnet-class", "opus-class", "model/class", "model-class", "required model class"):
            self.assertNotIn(obsolete, TEXT)

    def test_named_negative_guard_deletions(self):
        for name, phrases in GUARDS.items():
            for phrase in phrases:
                with self.subTest(seam=name, missing=phrase):
                    self.assertTrue(any(e.startswith(name + ":") for e in
                                        contract_errors(TEXT.replace(phrase, "REMOVED"))))

    def test_unsafe_policy_replacements(self):
        fixtures = (
            ("support", "provider-documented supported effort", "catalog-listed effort is enough"),
            ("support", "permitted usable runtime capability", "runtime support is optional"),
            ("effort", "Higher effort needs concrete residual reasoning or lower-setting counterevidence",
             "high-risk tasks and reviewers always use high"),
            ("effort", "returns for decomposition/stronger observable acceptance, not reflexive max",
             "weak oracles use max"),
            ("advisory", "no qualifying row is not automatically excluded", "no row means reject"),
            ("advisory", "explicit bounded owner uncertainty disposition", "uncertainty stays hidden"),
            ("advisory", "owner preference is not a measured advantage", "owner preference scores 99"),
            ("drift", "never substitution", "silently substitute another binding"),
            ("approval", "no routine second assignment-approval question", "always ask selection again"),
            ("retry", "Do not skip an unavailable next family", "skip Terra if unavailable"),
            ("retry", "Astra is never an automatic fourth attempt", "retry with Astra fourth"),
            ("retry", "automatic effort increment or blanket per-retry owner question",
             "automatically increase effort and ask on every retry"),
            ("retry", "within existing owner-selected routing authority", "choose any effort after failure"),
            ("retry", "Only after\ninspection and established safe task state", "choose retry effort before diagnosis"),
            ("batch", "More than three implementation tasks require delegation", "four tasks may run locally"),
            ("batch", "approved compatible exact binding/effort and context", "one required model class"),
            ("review", "usable fresh independent reviewer before implementation", "writer reviews itself"),
        )
        for name, old, unsafe in fixtures:
            with self.subTest(seam=name, policy=unsafe):
                self.assertTrue(any(e.startswith(name + ":") for e in contract_errors(TEXT.replace(old, unsafe))))

    def test_coherent_sequential_work_is_not_split_by_incidental_boundaries(self):
        self.assertIn("amortize startup and retain\n   useful context", TEXT)
        self.assertIn("Internal dependencies, shared files, and phase/story headings do not require", TEXT)
        self.assertIn("verifies each producer before its\n   consumer", TEXT)
        self.assertIn("Aim for 5–7 tasks only when scope and observed context permit", TEXT)
        self.assertIn("binding/effort changes, owner gates, context limits, genuinely incompatible scope", TEXT)


if __name__ == "__main__":
    unittest.main()
