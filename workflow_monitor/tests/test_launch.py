"""Prepared launcher checks use isolated local repositories and one local server."""
from __future__ import annotations

import contextlib
import io
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time
import unittest
from urllib.request import Request, urlopen
from unittest.mock import patch

from workflow_monitor import __main__

ROOT = Path(__file__).resolve().parents[2]


class LaunchTests(unittest.TestCase):
    def _port(self) -> int:
        with socket.socket() as probe:
            probe.bind(("127.0.0.1", 0))
            return probe.getsockname()[1]

    def _repositories(self, root: Path) -> None:
        for name in ("alpha", "beta"):
            project = root / name
            project.mkdir()
            subprocess.run(["git", "init", "-q", str(project)], check=True, capture_output=True)

    def _files(self, root: Path) -> dict[Path, bytes]:
        return {path.relative_to(root): path.read_bytes() for path in root.rglob("*")
                if path.is_file() and not path.is_symlink()}

    def _launch_and_list(self, root: Path, assets: Path, home: Path, *, configured: bool,
                         expected_projects: int = 2) -> None:
        port = self._port()
        unrelated = home / "unrelated"
        unrelated.mkdir()
        command = [sys.executable, "-B", "-m", "workflow_monitor", "--assets", str(assets), "--port", str(port)]
        if configured:
            command.extend(["--projects-root", str(root)])
        environment = os.environ.copy()
        environment["HOME"] = str(home)
        # The prepared module is made importable explicitly, not through the unrelated cwd.
        environment["PYTHONPATH"] = os.pathsep.join((str(ROOT), str(ROOT / "runtime")))
        process = subprocess.Popen(command, cwd=unrelated, env=environment,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.addCleanup(self._stop, process)
        headers = {"sec-fetch-site": "same-origin", "x-workflow-monitor": "1"}
        url = f"http://127.0.0.1:{port}/api/monitor/v1/projects"
        for _ in range(100):
            if process.poll() is not None:
                _, stderr = process.communicate()
                self.fail(f"prepared launcher exited early: {stderr.decode()}")
            try:
                with urlopen(Request(url, headers=headers), timeout=.2) as response:
                    self.assertEqual(response.status, 200)
                    self.assertEqual(len(json.loads(response.read())["projects"]), expected_projects)
                    return
            except OSError:
                time.sleep(.02)
        self.fail("prepared launcher did not serve its one configured loopback port")

    @staticmethod
    def _stop(process: subprocess.Popen[bytes]) -> None:
        if process.poll() is None:
            process.terminate()
            process.communicate(timeout=5)

    def test_help_documents_only_safe_flags(self):
        result = subprocess.run([sys.executable, "-m", "workflow_monitor", "--help"], text=True, capture_output=True, check=False)
        self.assertEqual(result.returncode, 0)
        self.assertIn("--projects-root", result.stdout)
        self.assertIn("--assets", result.stdout)
        self.assertNotIn("--project ", result.stdout)
        self.assertNotIn("--host", result.stdout)
        self.assertNotIn("--reload", result.stdout)

    def test_prepared_launcher_uses_default_expanded_home_projects_from_unrelated_cwd(self):
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary) / "home"
            root = home / "projects"
            root.mkdir(parents=True)
            self._repositories(root)
            assets = Path(temporary) / "assets"
            assets.mkdir()
            (assets / "index.html").write_text("ok")
            before = self._files(root)
            self._launch_and_list(root, assets, home, configured=False)
            self.assertEqual(before, self._files(root))
            self.assertFalse(any(path.name == ".coherence" for path in root.rglob(".coherence")))

    def test_prepared_launcher_uses_configured_root_from_unrelated_cwd(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            root = base / "configured projects"
            root.mkdir()
            self._repositories(root)
            home = base / "home"
            home.mkdir()
            assets = base / "assets"
            assets.mkdir()
            (assets / "index.html").write_text("ok")
            self._launch_and_list(root, assets, home, configured=True)

    def test_empty_root_starts_with_an_honest_empty_inventory(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            root = base / "empty"
            root.mkdir()
            home = base / "home"
            home.mkdir()
            assets = base / "assets"
            assets.mkdir()
            (assets / "index.html").write_text("ok")
            self._launch_and_list(root, assets, home, configured=True, expected_projects=0)

    def test_invalid_root_is_actionable_and_is_not_created(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            assets = root / "assets"
            assets.mkdir()
            (assets / "index.html").write_text("ok")
            missing = root / "missing"
            error = io.StringIO()
            with self.assertRaisesRegex(SystemExit, "2"), contextlib.redirect_stderr(error), patch.object(__main__.uvicorn, "run"):
                __main__.main(["--projects-root", str(missing), "--assets", str(assets)])
            self.assertIn("--projects-root: projects root", error.getvalue())
            self.assertFalse(missing.exists())

    def test_launch_binds_numeric_loopback_without_creating_store(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            assets = root / "assets"
            assets.mkdir()
            (assets / "index.html").write_text("ok")
            projects = object()
            with patch.object(__main__, "Projects", return_value=projects), patch.object(__main__.uvicorn, "run") as run:
                self.assertEqual(__main__.main(["--projects-root", str(root), "--assets", str(assets), "--port", "9876"]), 0)
            self.assertFalse((root / ".coherence").exists())
            self.assertEqual(run.call_args.kwargs["host"], "127.0.0.1")
            self.assertEqual(run.call_args.kwargs["port"], 9876)
            self.assertFalse(run.call_args.kwargs["reload"])
            self.assertFalse(run.call_args.kwargs["access_log"])


if __name__ == "__main__":
    unittest.main()
