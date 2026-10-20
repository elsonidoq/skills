"""Production delivery boundary checks; no writer or persistent server is started."""
from pathlib import Path
import tempfile
import unittest

from workflow_monitor.app import create_app


class DeliveryTests(unittest.TestCase):
    def test_packaged_launcher_and_locked_runtime_dependencies_are_declared(self):
        root = Path(__file__).resolve().parents[1]
        metadata = (root / "pyproject.toml").read_text()
        lock = (root / "requirements.lock").read_text()
        self.assertIn('workflow-monitor = "workflow_monitor.__main__:main"', metadata)
        self.assertIn("starlette==0.46.2", lock)
        self.assertIn("uvicorn==0.34.0", lock)

    def test_missing_or_symlinked_asset_root_has_a_safe_actionable_error(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            with self.assertRaisesRegex(ValueError, "assets directory is missing or unreadable"):
                create_app(object(), root / "missing", 8765)
            assets = root / "assets"
            assets.mkdir()
            (assets / "index.html").write_text("safe")
            alias = root / "assets-link"
            alias.symlink_to(assets, target_is_directory=True)
            with self.assertRaisesRegex(ValueError, "assets must be a regular directory"):
                create_app(object(), alias, 8765)


if __name__ == "__main__":
    unittest.main()
