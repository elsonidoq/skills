"""Local HTTP boundary tests; fixtures are offline and no writer is started."""
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
