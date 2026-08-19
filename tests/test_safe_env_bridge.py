from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "files/safe-env-bridge.py"


def load_bridge():
    spec = importlib.util.spec_from_file_location("safe_env_bridge", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SafeEnvironmentBridgeTests(unittest.TestCase):
    def setUp(self):
        self.bridge = load_bridge()

    def test_shell_significant_values_are_quoted_not_executed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "hermes.env"
            marker = root / "executed"
            value = f"http://user:p@ss word;$(touch {marker})#@proxy.example:8080"
            target.write_text("KEEP=value\nDECODO_PROXY=old\n")

            count = self.bridge.update_env(
                target,
                [target],
                environ={"DECODO_PROXY": value, "BROWSER_USE_API_KEY": "safe value"},
            )
            self.assertEqual(count, 2)
            self.assertEqual(stat.S_IMODE(target.stat().st_mode), 0o600)
            self.assertIn("KEEP=value", target.read_text())

            command = [
                "bash",
                "-c",
                "set -a; . \"$1\"; printf '%s' \"$DECODO_PROXY\"",
                "bridge-test",
                str(target),
            ]
            result = subprocess.run(command, text=True, capture_output=True, check=False, env={"PATH": os.environ["PATH"]})
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout, value)
            self.assertFalse(marker.exists())

    def test_newlines_and_unparseable_source_values_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source.env"
            target = root / "target.env"
            source.write_text("STEEL_API_KEY=$(touch bad file)\nSAFE_OTHER=keep\n")
            self.bridge.update_env(target, [source], environ={"STEEL_API_KEY": "line1\nline2"})
            self.assertNotIn("STEEL_API_KEY", target.read_text())

    def test_exec_exports_allowlisted_values_without_shell_evaluation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source.env"
            target = root / "target.env"
            marker = root / "must-not-exist"
            value = f"value with spaces;$(touch {marker})"
            source.write_text(f"DECODO_PROXY={value!r}\nUNMANAGED=blocked\n")
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--target",
                    str(target),
                    "--source",
                    str(source),
                    "--exec",
                    sys.executable,
                    "-c",
                    "import os; print(os.environ['DECODO_PROXY']); assert 'UNMANAGED' not in os.environ",
                ],
                text=True,
                capture_output=True,
                check=False,
                env={"PATH": os.environ["PATH"]},
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn(value, result.stdout)
            self.assertFalse(marker.exists())


if __name__ == "__main__":
    unittest.main()
