"""Focused examples for the task-order review helper."""

import importlib.util
import unittest
from pathlib import Path


spec = importlib.util.spec_from_file_location("check_task_order", Path(__file__).with_name("check-task-order.py"))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class TaskOrderTests(unittest.TestCase):
    def test_valid_story_and_backward_dependencies(self):
        self.assertEqual(
            module.check("""\
- [ ] T001 Setup
  - **Depends**: none. **Evidence**: ready
- [ ] T002 [US1] Build
  - **Depends**: T001 (setup). **Evidence**: built
- [ ] T003 [US1] Test
  - **Depends**: T002. **Evidence**: tested
- [ ] T004 [US2] Integrate
  - **Depends**: T001–T003. **Evidence**: integrated
"""),
            [],
        )

    def test_forward_self_edge_and_repeated_story(self):
        errors = module.check("""\
- [ ] T001 [US1] Consumer
  - **Depends**: T003. **Evidence**: pending
- [ ] T002 [US2] Other
  - **Depends**: T002. **Evidence**: pending
- [ ] T003 [US1] Producer
  - **Depends**: none. **Evidence**: pending
""")
        self.assertTrue(any("T001 depends on later-numbered T003" in error for error in errors))
        self.assertTrue(any("T002 depends on itself" in error for error in errors))
        self.assertTrue(any("US1 resumes" in error for error in errors))

    def test_missing_duplicate_and_out_of_order(self):
        errors = module.check("""\
- [ ] T002 First
  - **Depends**: T001
- [ ] T002 Again
  - **Depends**: none
- [ ] T001 Last
""")
        self.assertTrue(any("missing or out-of-order T001" in error for error in errors))
        self.assertTrue(any("duplicate task number" in error for error in errors))
        self.assertTrue(any("not numbered immediately after" in error for error in errors))
        self.assertTrue(any("no explicit Depends" in error for error in errors))

    def test_none_and_range_are_valid(self):
        self.assertEqual(
            module.check("""\
- [ ] T001 Setup
  - **Depends**: none
- [ ] T002 Build
  - **Depends**: T001–T001
"""),
            [],
        )

    def test_no_tasks_is_not_a_pass(self):
        self.assertTrue(module.check("# Empty list\n"))

    def test_numbering_gap_is_not_a_pass(self):
        errors = module.check("""\
- [ ] T001 Start
  - **Depends**: none
- [ ] T003 Next
  - **Depends**: T001
""")
        self.assertTrue(any("not numbered immediately after" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
