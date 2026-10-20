"""Local HTTP boundary tests; fixtures are offline and no writer is started."""
import copy
import json
from pathlib import Path
import socket
import tempfile
import threading
import time
import unittest
from urllib.request import Request, urlopen

from starlette.testclient import TestClient
import uvicorn

from workflow_monitor.app import create_app
from workflow_monitor.mapping import normalize
from workflow_monitor.public import minimize
from workflow_monitor.tests.test_mapping import snapshot


class Reader:
    def __init__(self):
        self.value = snapshot()

    def open_snapshot(self):
        return self.value


class HttpTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        assets = Path(self.tmp.name) / "assets"
        assets.mkdir()
        (assets / "index.html").write_text("<main>safe asset</main>")
        (assets / "app.js").write_text("console.log('safe')")
        (assets / "secret.map").write_text("PRIVATE-SENTINEL")
        (assets / "raw-ref.txt").write_text("PRIVATE-SENTINEL")
        (assets / "outside").symlink_to("/etc/passwd")
        self.reader = Reader()
        self.client = TestClient(create_app(self.reader, assets, 8765), base_url="http://127.0.0.1:8765")
        self.api_headers = {"sec-fetch-site": "same-origin", "x-workflow-monitor": "1"}

    def assert_safe(self, response):
        self.assertEqual(response.headers["cache-control"], "no-store")
        self.assertIn("default-src 'self'", response.headers["content-security-policy"])
        self.assertNotIn("PRIVATE-SENTINEL", response.text)

    def test_allowed_snapshot_history_and_detail_are_closed(self):
        runs = self.client.get("/api/monitor/v1/runs", headers=self.api_headers)
        self.assertEqual(runs.status_code, 200)
        self.assert_safe(runs)
        run_ref = runs.json()["runs"][0]["ref"]
        view = self.client.get(f"/api/monitor/v1/runs/{run_ref}/snapshot", headers=self.api_headers)
        self.assertEqual(view.status_code, 200)
        self.assert_safe(view)
        record = view.json()["records"][0]["ref"]
        snapshot_ref = view.json()["snapshot_ref"]
        history = self.client.get(f"/api/monitor/v1/runs/{run_ref}/history?snapshot={snapshot_ref}", headers=self.api_headers)
        self.assertEqual(history.status_code, 200)
        detail = self.client.get(f"/api/monitor/v1/runs/{run_ref}/records/{record}?snapshot={snapshot_ref}", headers=self.api_headers)
        self.assertEqual(detail.status_code, 200)
        self.assertEqual(self.client.get("/").status_code, 200)

    def test_unknown_null_sequences_are_paginated_without_a_server_error(self):
        malformed = copy.deepcopy(snapshot())
        malformed["runs"] = [row for row in malformed["runs"] if row["run_id"] == "run-a"]
        malformed["runs"][0]["description"] = "not-json"
        malformed["observations"] = [{"seq": number, "run_id": "run-a", "occurrence_id": f"bad-{number}",
                                       "phase": "worker", "task_id": None, "kind": "future", "recorded_at": number,
                                       "facts": "{}"} for number in range(1, 55)]
        self.reader.value = malformed
        run = self.client.get("/api/monitor/v1/runs", headers=self.api_headers).json()["runs"][0]["ref"]
        first = self.client.get(f"/api/monitor/v1/runs/{run}/snapshot", headers=self.api_headers)
        self.assertEqual(first.status_code, 200)
        pages = [first.json()]
        while pages[-1]["next_cursor"]:
            response = self.client.get(f"/api/monitor/v1/runs/{run}/history?snapshot={pages[-1]['snapshot_ref']}&cursor={pages[-1]['next_cursor']}&limit=50", headers=self.api_headers)
            self.assertEqual(response.status_code, 200)
            pages.append(response.json())
        retained = [item for page in pages for item in page["records"] + page["unknown_records"]]
        self.assertEqual(len(retained), 55)
        self.assertEqual(len({item["ref"] for item in retained}), 55)
        self.assertTrue(any(item["source_seq"] is None for item in retained))

    def test_multiple_null_unknowns_cross_page_boundaries(self):
        for mixed in (False, True):
            with self.subTest(mixed=mixed):
                raw = copy.deepcopy(snapshot())
                raw["runs"] = [row for row in raw["runs"] if row["run_id"] == "run-a"]
                import json
                description = json.loads(raw["runs"][0]["description"])
                description["phases"].extend([{"PRIVATE-SENTINEL": "withheld"}] * 55)
                raw["runs"][0]["description"] = json.dumps(description)
                if not mixed:
                    raw["observations"] = []
                self.reader.value = raw
                run = self.client.get("/api/monitor/v1/runs", headers=self.api_headers).json()["runs"][0]["ref"]
                first = self.client.get(f"/api/monitor/v1/runs/{run}/snapshot", headers=self.api_headers).json()
                expected = first["inventory"]["total_count"]
                pages = [first]
                while pages[-1]["next_cursor"]:
                    response = self.client.get(f"/api/monitor/v1/runs/{run}/history?snapshot={first['snapshot_ref']}&cursor={pages[-1]['next_cursor']}&limit=2", headers=self.api_headers)
                    self.assertEqual(response.status_code, 200)
                    self.assert_safe(response)
                    pages.append(response.json())
                retained = [item for page in pages for item in page["records"] + page["unknown_records"]]
                self.assertEqual(len(retained), expected)
                self.assertEqual(len({item["ref"] for item in retained}), expected)
                self.assertEqual(sum(item.get("source_seq") is None for item in retained), 55)
                bad = self.client.get(f"/api/monitor/v1/runs/{run}/history?snapshot={first['snapshot_ref']}&cursor=cursor_unknown_not_this_run", headers=self.api_headers)
                self.assertEqual(bad.status_code, 400)

    def test_pre_page_execution_summary_uses_return_and_answer_after_page_50(self):
        raw = snapshot()
        raw['runs'] = [row for row in raw['runs'] if row['run_id'] == 'run-a']
        rows = [{'seq': number, 'run_id': 'run-a', 'occurrence_id': f'noise-{number}', 'phase': 'check',
                 'task_id': 'one', 'kind': 'started', 'recorded_at': number, 'facts': json.dumps({'ordinal': number})}
                for number in range(1, 51)]
        rows.extend([
            {'seq': 51, 'run_id': 'run-a', 'occurrence_id': 'worker', 'phase': 'worker', 'task_id': 'one',
             'kind': 'started', 'recorded_at': 51, 'facts': json.dumps({'role': 'worker'})},
            {'seq': 52, 'run_id': 'run-a', 'occurrence_id': 'question', 'phase': 'worker', 'task_id': 'one',
             'kind': 'question_requested', 'recorded_at': 52, 'facts': json.dumps({'parent_occurrence_id': 'worker'})},
            {'seq': 53, 'run_id': 'run-a', 'occurrence_id': 'question', 'phase': 'worker', 'task_id': 'one',
             'kind': 'answer_returned', 'recorded_at': 53, 'facts': json.dumps({'parent_occurrence_id': 'worker'})},
            {'seq': 54, 'run_id': 'run-a', 'occurrence_id': 'worker', 'phase': 'worker', 'task_id': 'one',
             'kind': 'returned', 'recorded_at': 54, 'facts': json.dumps({'role': 'worker'})},
        ])
        raw['observations'] = rows
        self.reader.value = raw
        run = self.client.get('/api/monitor/v1/runs', headers=self.api_headers).json()['runs'][0]['ref']
        first = self.client.get(f'/api/monitor/v1/runs/{run}/snapshot', headers=self.api_headers).json()
        later = self.client.get(f"/api/monitor/v1/runs/{run}/history?snapshot={first['snapshot_ref']}&cursor={first['next_cursor']}", headers=self.api_headers).json()
        worker = next(item for item in first['occurrences'] if item['role'] == 'worker')
        self.assertEqual(worker['execution_summary'], {'state': 'success', 'qualification': None})
        self.assertEqual(first['runs'][0]['acceptance_summary'], later['runs'][0]['acceptance_summary'])
        self.assertEqual(worker['execution_summary'], next(item for item in later['occurrences'] if item['role'] == 'worker')['execution_summary'])
        self.assert_safe(self.client.get(f'/api/monitor/v1/runs/{run}/history?snapshot={first["snapshot_ref"]}&cursor={first["next_cursor"]}', headers=self.api_headers))

    def test_snapshot_scopes_graph_entities_to_selected_root(self):
        runs = self.client.get("/api/monitor/v1/runs", headers=self.api_headers).json()["runs"]
        selected, unrelated = (item["ref"] for item in runs)
        view = self.client.get(f"/api/monitor/v1/runs/{selected}/snapshot", headers=self.api_headers).json()
        self.assertEqual({item["run_ref"] for key in ("phases", "tasks", "occurrences", "records", "unknown_records", "edges") for item in view[key]}, {selected})
        self.assertNotEqual(selected, unrelated)
        self.assertEqual({item["ref"] for item in view["runs"]}, {selected, unrelated})

    def test_actual_loopback_server_serves_a_closed_api_response(self):
        with socket.socket() as probe:
            probe.bind(("127.0.0.1", 0))
            port = probe.getsockname()[1]
        assets = Path(self.tmp.name) / "assets"
        server = uvicorn.Server(uvicorn.Config(create_app(self.reader, assets, port), host="127.0.0.1", port=port,
                                             access_log=False, log_level="critical"))
        thread = threading.Thread(target=server.run)
        thread.start()
        self.addCleanup(lambda: (setattr(server, "should_exit", True), thread.join(5)))
        for _ in range(50):
            if server.started:
                break
            time.sleep(.02)
        request = Request(f"http://127.0.0.1:{port}/api/monitor/v1/runs", headers=self.api_headers)
        with urlopen(request, timeout=2) as response:
            self.assertEqual(response.status, 200)
            self.assertEqual(response.headers["Cache-Control"], "no-store")

    def test_startup_asset_inventory_rejects_later_symlink_substitutions(self):
        assets = Path(self.tmp.name) / "assets"
        private = Path(self.tmp.name) / "PRIVATE-SENTINEL"
        private.write_text("PRIVATE-SENTINEL")
        (assets / "app.js").unlink()
        (assets / "app.js").symlink_to(private)
        response = self.client.get("/app.js")
        self.assertEqual(response.status_code, 404)
        self.assert_safe(response)
        nested = assets / "nested"; nested.mkdir()
        (nested / "safe.js").write_text("safe")
        nested_client = TestClient(create_app(self.reader, assets, 8765), base_url="http://127.0.0.1:8765")
        (nested / "safe.js").unlink(); nested.rmdir(); nested.symlink_to(private.parent)
        response = nested_client.get("/nested/safe.js")
        self.assertEqual(response.status_code, 404)
        self.assert_safe(response)

    def test_host_origin_method_and_raw_paths_are_rejected(self):
        bad = self.client.get("/api/monitor/v1/runs", headers={"host": "localhost:8765", **self.api_headers})
        self.assertEqual((bad.status_code, bad.json()["code"]), (400, "bad_request"))
        foreign = self.client.get("/api/monitor/v1/runs", headers={"origin": "http://evil.invalid", **self.api_headers})
        self.assertEqual((foreign.status_code, foreign.json()["code"]), (400, "bad_request"))
        self.assertEqual(self.client.options("/api/monitor/v1/runs").status_code, 400)
        for path in ("/secret.map", "/raw-ref.txt", "/outside", "/../etc/passwd", "/api/monitor/v1/runs/run_raw/snapshot"):
            response = self.client.get(path, headers=self.api_headers)
            self.assertEqual(response.status_code, 404 if path.startswith("/api/") else 404)
            self.assert_safe(response)

    def test_actual_server_error_is_closed_and_safe(self):
        class Broken:
            def open_snapshot(self):
                raise RuntimeError("PRIVATE-SENTINEL")
        assets = Path(self.tmp.name) / "assets"
        client = TestClient(create_app(Broken(), assets, 8765), base_url="http://127.0.0.1:8765")
        response = client.get("/api/monitor/v1/runs", headers=self.api_headers)
        self.assertEqual((response.status_code, response.json()["code"]), (500, "internal"))
        self.assert_safe(response)


if __name__ == "__main__":
    unittest.main()
