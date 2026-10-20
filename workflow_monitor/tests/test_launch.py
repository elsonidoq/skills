"""Launcher checks use local arguments and never start a persistent server."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from workflow_monitor import __main__


class LaunchTests(unittest.TestCase):
    def test_help_documents_only_safe_flags(self):
        result = subprocess.run([sys.executable, "-m", "workflow_monitor", "--help"], text=True, capture_output=True, check=False)
        self.assertEqual(result.returncode, 0)
        self.assertIn("--project", result.stdout)
        self.assertIn("--assets", result.stdout)
        self.assertNotIn("--host", result.stdout)
        self.assertNotIn("--reload", result.stdout)

    def test_launch_binds_numeric_loopback_without_creating_store(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            assets = root / "assets"
            assets.mkdir()
            (assets / "index.html").write_text("ok")
            project = root / "project"
            project.mkdir()
            reader = object()
            with patch.object(__main__, "Reader", return_value=reader), patch.object(__main__.uvicorn, "run") as run:
                self.assertEqual(__main__.main(["--project", str(project), "--assets", str(assets), "--port", "9876"]), 0)
            self.assertFalse((project / ".coherence").exists())
            self.assertEqual(run.call_args.kwargs["host"], "127.0.0.1")
            self.assertFalse(run.call_args.kwargs["reload"])
            self.assertFalse(run.call_args.kwargs["access_log"])


if __name__ == "__main__":
    unittest.main()
