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

    def test_lone_t002_is_rejected(self):
        errors = module.check("""\
- [ ] T002 First
  - **Depends**: none
""")
        self.assertTrue(any("first task must be T001" in error for error in errors))

    def test_numbering_gap_is_not_a_pass(self):
        errors = module.check("""\
- [ ] T001 Start
  - **Depends**: none
- [ ] T003 Next
  - **Depends**: T001
""")
        self.assertTrue(any("not numbered immediately after" in error for error in errors))



class AdapterParityTests(unittest.TestCase):
    """Static propagation + actual shared intake; no LLM-obedience claims."""
    def test_same_acceptance_different_executor_scaffolding_both_origins(self):
        import copy
        import sys
        import tempfile
        root = Path(__file__).resolve().parents[3]
        sys.path[:0] = [str(root/'runtime'),str(root/'runtime/tests')]
        from test_intake import approved_fixture, declare_builtin_actions
        from fixtures.support import make_project
        from coherence_workflow.registry import validate_schema
        for origin in ('TinySpec','Standard'):
            with tempfile.TemporaryDirectory() as tmp:
                project=make_project(Path(tmp)/'project')
                contract,_=approved_fixture(project,'config',origin)
                for index,task in enumerate(contract['tasks']):
                    task['id']=f'T{index+1:03d}';task['order']=index
                    task['depends']=['T001'] if index else []
                    for number,item in enumerate(task['required'],1):
                        item['id']=task['id']+'/V'+str(number)
                        item['producer_dependencies']=list(task['depends'])
                # These are draft planning examples, not fictional current owner approvals.
                contract['approval_refs']=[]
                declare_builtin_actions(contract)
                luna=copy.deepcopy(contract);sol=copy.deepcopy(contract)
                planner_profile={'model_class':'Sol','effort':'medium'}
                luna['execution_intent']['model_class']='Luna'
                luna['execution_intent']['resolution']='unresolved'
                luna['execution_intent']['compatible_bindings']=[]
                self.assertNotEqual(planner_profile['model_class'],luna['execution_intent']['model_class'])
                self.assertNotIn('planner_profile',luna['execution_intent'])
                luna['execution_intent']['decomposition_rationale']='Name exact byte interface, ordered read/replace guidance and edge cases; narrow outcomes, no implicit architecture'
                sol['execution_intent']['decomposition_rationale']='Exact outcome and invariants; routine editing choices left open'
                separator='\nImplementation guidance: '
                for explicit,outcome_oriented in zip(luna['tasks'],sol['tasks']):
                    path=explicit['owned_paths'][0]
                    objective=explicit['outcome']
                    explicit['outcome']=objective+separator+(
                        '1. Use read_file on '+path+'; its complete current bytes are the input interface. '
                        '2. Use write_file to replace that file with the EXACT bytes in the objective; preserve the final newline. '
                        'Do not append or change other paths. 3. Preserve the dependency checkpoint before the consumer; '
                        'the unchanged FileBytes oracle verifies the exact result, not a success narrative.')
                    outcome_oriented['outcome']=objective+separator+(
                        'Meet the exact file-byte objective and all original ownership/dependency/REQUIRED gates; '
                        'routine choice of editing steps remains open. No acceptance or safety reduction.')
                    self.assertEqual(explicit.keys(),outcome_oriented.keys(),'no unnecessary public guidance schema fields')
                    self.assertEqual(explicit['outcome'].split(separator,1)[0],outcome_oriented['outcome'].split(separator,1)[0])
                    self.assertNotEqual(explicit['outcome'],outcome_oriented['outcome'])
                    for field in explicit.keys()-{'outcome'}:
                        self.assertEqual(explicit[field],outcome_oriented[field],field)
                    self.assertIn('read_file on '+path,explicit['outcome'])
                    self.assertIn('preserve the final newline',explicit['outcome'])
                self.assertEqual(len(luna['tasks']),len(sol['tasks']))
                self.assertEqual(len(luna['tasks']),2,'no extra micro-tasks or routing quotas')
                for value in (luna,sol):
                    validate_schema('task.schema.json',value)
                    self.assertEqual(module.check_structured(value,value['execution_intent']),[])
                    wrong=copy.deepcopy(value['execution_intent']);wrong['effort']='low'
                    self.assertIn('human/machine',module.check_structured(value,wrong)[0])
                    missing=copy.deepcopy(value);del missing['execution_intent']
                    self.assertIn('missing executor',module.check_structured(missing)[0])
                for bad in ('id','depends','context_group'):
                    value=copy.deepcopy(sol)
                    if bad=='id':value['tasks'][1]['id']='T004'
                    elif bad=='depends':value['tasks'][0]['depends']=['T002']
                    else:
                        value['tasks'] += [copy.deepcopy(value['tasks'][0])]
                        value['tasks'][1]['context_group']='other'
                    self.assertTrue(module.check_structured(value))

    def test_origin_cli_and_intent_denials_use_real_runtime_intake(self):
        import os,subprocess,sys
        root=Path(__file__).resolve().parents[3]
        result=subprocess.run([sys.executable,'-m','unittest','test_intake'],cwd=root,
            env=dict(os.environ,PYTHONPATH='runtime:runtime/tests',PYTHONDONTWRITEBYTECODE='1'),
            capture_output=True,text=True,timeout=30)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        self.assertIn('Ran 8 tests',result.stderr)
        self.assertIn('TinySpec actual CLI intake 0',result.stdout)
        self.assertIn('Standard actual CLI intake 0',result.stdout)
        print(result.stdout,result.stderr)

if __name__ == "__main__":
    unittest.main()
