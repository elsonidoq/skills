"""The producer linter uses the executable six-check intake, including forward edges."""
import importlib.util
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location('check_task_order', Path(__file__).with_name('check-task-order.py'))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class TaskOrderTests(unittest.TestCase):
    def test_forward_dependencies_arbitrary_numbering_and_story_groups(self):
        self.assertEqual(module.check('''- [ ] T008 [US1] Consumer
  - **Depends**: T002
- [ ] T002 [US2] Producer
- [ ] T090 [US1] Independent
'''), [])

    def test_duplicate_missing_and_cycles(self):
        for text, diagnostic in [('''- [ ] T002 First
- [ ] T002 Again
''', 'duplicate task id'), ('''- [ ] T002 Consumer
  - **Depends**: T001
''', 'missing dependency'), ('''- [ ] T001 Self
  - **Depends**: T001
''', 'dependency cycle')]:
            self.assertIn(diagnostic, module.check(text)[0])

    def test_empty_and_optional_dependency_fields(self):
        self.assertEqual(module.check('# Empty\n'), [])
        self.assertEqual(module.check('- [ ] fix Fix title\n'), [])
        self.assertEqual(module.check_structured([]), [])

    def test_range_dependencies(self):
        self.assertEqual(module.check('''- [ ] T004 Consumer
  - **Depends**: T001–T003
- [ ] T001 Producer
- [ ] T002 Producer
- [ ] T003 Producer
'''), [])

    def test_structured_minimal_schema_and_optional_old_context(self):
        self.assertEqual(module.check_structured({'tasks': [
            {'id': 'consumer', 'description': 'Consume', 'depends': ['producer'], 'order': 0},
            {'id': 'producer', 'outcome': 'Produce', 'context_group': 'x'}]}), [])
        self.assertTrue(module.check_structured([{'id': 'no-work'}]))
        self.assertTrue(module.check_structured([{'outcome': 'no ID'}]))


if __name__ == '__main__':
    unittest.main()
