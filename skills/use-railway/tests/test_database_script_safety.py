import base64
import importlib.util
import re
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import dal


def load_script(name: str):
    path = SCRIPTS / name
    spec = importlib.util.spec_from_file_location(name.removesuffix(".py"), path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


enable_pg_stats = load_script("enable-pg-stats.py")
pg_extensions = load_script("pg-extensions.py")


class EnablePgStatsTests(unittest.TestCase):
    def test_restart_command_resolves_to_shared_helper(self):
        self.assertTrue(hasattr(enable_pg_stats, "run_railway_command"))
        self.assertIs(enable_pg_stats.run_railway_command, dal.run_railway_command)


class RemoteSqlTransportTests(unittest.TestCase):
    def test_psql_query_is_encoded_before_remote_shell_transport(self):
        query = 'SELECT "$(touch /tmp/injected)"; `touch /tmp/backtick`'

        with patch.object(dal, "run_ssh_query", return_value=(0, "ok", "")) as run:
            code, output = dal.run_psql_query("postgres", query)

        self.assertEqual((code, output), (0, "ok"))
        command = run.call_args.args[1]
        self.assertNotIn(query, command)
        self.assertNotIn("touch /tmp", command)
        encoded = re.search(r"printf '%s' '([A-Za-z0-9+/=]+)'", command).group(1)
        self.assertEqual(base64.b64decode(encoded).decode(), query)
        self.assertIn("base64 -d", command)
        self.assertIn("-v ON_ERROR_STOP=1", command)
        guarded_decode = re.search(
            r"sql=\$\(printf '%s' '[A-Za-z0-9+/=]+' \| base64 -d\) "
            r"\|\| exit \$\?;",
            command,
        )
        self.assertIsNotNone(guarded_decode)
        self.assertLess(guarded_decode.end(), command.index("psql"))
        self.assertIn("printf '%s' \"$sql\" |", command)


class ExtensionValidationTests(unittest.TestCase):
    def test_rejects_extension_name_before_querying(self):
        with patch.object(pg_extensions, "run_psql_query", return_value=(0, "")) as run:
            with self.assertRaises(ValueError):
                pg_extensions.is_extension_available("postgres", 'postgis"; DROP DATABASE app; --')
        run.assert_not_called()

    def test_rejects_extension_version_before_mutation(self):
        responses = [(0, "1"), (0, ""), (0, ""), (0, ""), (0, "1.0")]
        with patch.object(pg_extensions, "run_psql_query", side_effect=responses), \
                patch.object(pg_extensions, "confirm_with_user", return_value=True):
            with self.assertRaises(ValueError):
                pg_extensions.install_extension(
                    "postgres", "postgis", "1.0'; DROP DATABASE app; --"
                )

    def test_accepts_common_extension_and_version_characters(self):
        with patch.object(pg_extensions, "run_psql_query", return_value=(0, "1")) as run:
            self.assertTrue(pg_extensions.is_extension_available("postgres", "uuid-ossp"))
        self.assertIn("uuid-ossp", run.call_args.args[1])


if __name__ == "__main__":
    unittest.main()
