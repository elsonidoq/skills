"""Synthetic engine recordings prove the closed review-chain projection."""
from pathlib import Path
import sys
import json
import subprocess

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "runtime"))

from coherence_workflow.engine import Engine
from coherence_workflow.intake import admit
from coherence_workflow.store import Authority, Blocked
from fixtures.support import ProjectTest
from workflow_monitor.mapping import normalize
from workflow_monitor.public import minimize
from workflow_monitor.reader import Reader

EXECUTOR = {"provider": "fixture", "model": "offline", "effort": "medium",
            "reviewer": {"provider": "fixture", "model": "offline-review", "effort": "medium"}}
SCOPE = {"agent_providers": ["fixture"], "apis": []}


class ChainMappingTests(ProjectTest):
    def _run(self, run_id, adapter, *, checks=False, raises=None):
        task = {"id": "dummy", "description": "synthetic only", "owned_paths": ["owned.txt"]}
        if checks:
            task["checks"] = [["/bin/sh", "-c", 'test "$(cat owned.txt)" = fixed']]
        with Authority(self.project) as owner:
            engine = Engine(owner, run_id, admit({"tasks": [task]}), EXECUTOR, adapter=adapter, paid_scope=SCOPE)
            if raises:
                with self.assertRaisesRegex(Blocked, raises):
                    engine.invoke()
            else:
                engine.invoke()

    def test_four_engine_scenarios_project_only_actual_closed_chain_facts(self):
        project = self.project

        class Approval:
            def __init__(self, *_args, **_kwargs): pass
            def prompt(self, _prompt, **kwargs):
                if kwargs.get("read_only"):
                    return '{"approved":true,"findings":[]}'
                kwargs["claim"]("owned.txt"); project.joinpath("owned.txt").write_text("fixed\n")
                return "PRIVATE-WORKER-ANSWER"

        class Repaired:
            reviews = 0
            def __init__(self, *_args, **_kwargs): pass
            def prompt(self, prompt, **kwargs):
                if kwargs.get("read_only"):
                    Repaired.reviews += 1
                    return ('{"approved":false,"findings":["owned.txt:1 - safe defect", "PRIVATE-SENTINEL"]}'
                            if Repaired.reviews == 1 else '{"approved":true,"findings":[]}')
                if "Actionable findings:" in prompt:
                    kwargs["claim"]("owned.txt"); project.joinpath("owned.txt").write_text("broken\n")
                else:
                    project.joinpath("owned.txt").write_text("fixed\n")
                return "PRIVATE-WORKER-ANSWER"

        class FinalRejection:
            reviews = 0
            def __init__(self, *_args, **_kwargs): pass
            def prompt(self, _prompt, **kwargs):
                if kwargs.get("read_only"):
                    FinalRejection.reviews += 1
                    finding = "owned.txt:1 - first" if FinalRejection.reviews == 1 else "owned.txt:2 - final"
                    return '{"approved":false,"findings":["' + finding + '"]}'
                kwargs["claim"]("owned.txt"); project.joinpath("owned.txt").write_text("fixed\n")
                return "worker"

        class FixerFailure:
            def __init__(self, *_args, **_kwargs): pass
            def prompt(self, prompt, **kwargs):
                if kwargs.get("read_only"):
                    return '{"approved":false,"findings":["owned.txt:1 - defect"]}'
                if "Actionable findings:" in prompt:
                    raise Blocked("synthetic fixer failure")
                kwargs["claim"]("owned.txt"); project.joinpath("owned.txt").write_text("fixed\n")
                return "worker"

        self._run("approved", Approval)
        self._run("repaired", Repaired, checks=True)
        self._run("final", FinalRejection, raises="final")
        self._run("fixer-failure", FixerFailure, raises="fixer failure")

        dto = minimize(normalize(Reader(self.project).open_snapshot()))
        by_run = {run["display_id"]: run["ref"] for run in dto["runs"]}
        repaired = [item for item in dto["chain"] if item["run_ref"] == by_run["repaired"]]
        self.assertEqual([(item["role"], item["outcome"], item["review_ordinal"]) for item in repaired],
                         [("reviewer", "rejected", 1), ("fixer", "approved", 1), ("reviewer", "approved", 2)])
        self.assertEqual(repaired[0]["findings"], ["owned.txt:1 - safe defect"])
        self.assertTrue(repaired[1]["trigger_ref"])
        self.assertTrue(any(edge["type"] == "chain_check" for edge in dto["edges"]))
        failed_checks = [record for record in dto["records"] if record["run_ref"] == by_run["repaired"] and record["kind"] == "failed" and record["exit_code"] == 1]
        self.assertEqual(len(failed_checks), 1)
        self.assertEqual(dto["chain_acceptance"][by_run["repaired"]]["state"], "accepted")
        self.assertTrue(dto["chain_acceptance"][by_run["repaired"]]["terminal_execution_ref"])
        self.assertEqual([item["role"] for item in dto["chain"] if item["run_ref"] == by_run["approved"]], ["reviewer"])
        self.assertEqual([(item["role"], item["outcome"]) for item in dto["chain"] if item["run_ref"] == by_run["final"]],
                         [("reviewer", "rejected"), ("fixer", "approved"), ("reviewer", "rejected")])
        self.assertEqual([(item["role"], item["outcome"]) for item in dto["chain"] if item["run_ref"] == by_run["fixer-failure"]],
                         [("reviewer", "rejected"), ("fixer", "failed")])
        # The selected HTTP boundary must scope newly added chain data as well as
        # occurrences/edges, even when several runs share one underlying reader.
        from starlette.testclient import TestClient
        from workflow_monitor.app import create_app
        assets = self.root / 'dummy-assets'
        assets.mkdir()
        (assets/'index.html').write_text('<main>fixture</main>')
        client = TestClient(create_app(Reader(self.project), assets, 8765), base_url='http://127.0.0.1:8765')
        for reference in by_run.values():
            response = client.get('/api/monitor/v1/runs/' + reference + '/snapshot',
                                  headers={'sec-fetch-site': 'same-origin', 'x-workflow-monitor': '1'})
            self.assertEqual(response.status_code, 200)
            selected = response.json()
            self.assertEqual({item['run_ref'] for item in selected['chain']}, {reference})
            self.assertEqual(set(selected['chain_acceptance']), {reference})
            selected_view = json.loads(subprocess.check_output([
                'node', '--experimental-strip-types', '--input-type=module', '-e',
                "import {graphFor} from './workflow_monitor/web/src/graph.ts'; "
                "let data=''; for await (const chunk of process.stdin) data+=chunk; "
                "console.log(JSON.stringify(graphFor(JSON.parse(data), [], [])))"],
                input=json.dumps(selected).encode(), cwd=ROOT))
            rendered_chain = {node['id'] for node in selected_view['nodes'] if 'chain-node' in node.get('className', '')}
            self.assertEqual(rendered_chain, {item['ref'] for item in selected['chain']})

        # Consume actual producer IDs/relations in the production source module,
        # not a browser-only occurrence-targeted approximation.
        view = json.loads(subprocess.check_output([
            'node', '--experimental-strip-types', '--input-type=module', '-e',
            "import {graphFor} from './workflow_monitor/web/src/graph.ts'; "
            "let data=''; for await (const chunk of process.stdin) data+=chunk; "
            "console.log(JSON.stringify(graphFor(JSON.parse(data), [], [])))"],
            input=json.dumps(dto).encode(), cwd=ROOT))
        nodes = {node['id'] for node in view['nodes']}
        for edge in dto['edges']:
            if edge['type'] not in ('chain_check', 'chain_checkpoint'): continue
            target = next(item for item in dto['occurrences'] if edge['to_ref'] in item['record_refs'])
            self.assertIn(target['ref'], nodes)
            rendered = next(item for item in view['edges'] if item['id'] == edge['ref'])
            self.assertEqual((rendered['source'], rendered['target']), (edge['from_ref'], target['ref']))
        self.assertNotIn("PRIVATE-SENTINEL", repr(dto))
        self.assertNotIn("PRIVATE-WORKER-ANSWER", repr(dto))


if __name__ == "__main__":
    import unittest
    unittest.main()
