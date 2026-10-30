"""Check failure propagation and contract selection without installing toolchains."""
import importlib.machinery
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
loader = importlib.machinery.SourceFileLoader("fogmachine_dev", str(ROOT / "dev"))
spec = importlib.util.spec_from_loader(loader.name, loader)
dev = importlib.util.module_from_spec(spec)
loader.exec_module(dev)

class AdapterTests(unittest.TestCase):
    def test_mcp_uses_frozen_lock_and_real_groups(self):
        self.assertEqual(dev.commands("mcp", "setup"), [["uv", "sync", "--frozen", "--group", "dev", "--group", "ci"]])
        self.assertIn(["uv", "run", "--frozen", "pytest"], dev.commands("mcp", "check"))

    def test_core_keeps_required_rust_checks(self):
        self.assertIn(["cargo", "test", "--workspace", "--all-features"], dev.commands("core", "check"))

    def test_mcp_pin_match_and_mismatch(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            pin = root / ".python-version"
            pin.write_text(dev.PINS["python"])
            dev.validate_repo(root, "mcp")
            pin.write_text("0.0")
            with self.assertRaises(ValueError):
                dev.validate_repo(root, "mcp")
            pin.unlink()
            with self.assertRaises(OSError):
                dev.validate_repo(root, "mcp")

    def test_missing_or_unknown_profile_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            command = [sys.executable, str(ROOT / "dev"), "check", "--dry-run"]
            self.assertNotEqual(subprocess.run(command, cwd=directory, capture_output=True).returncode, 0)
            (Path(directory) / ".fogmachine.json").write_text('{"profile":"unknown"}')
            self.assertNotEqual(subprocess.run(command, cwd=directory, capture_output=True).returncode, 0)

    def test_required_child_failure_returns_nonzero_and_report(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            subprocess.run(["git", "-c", "user.name=Test", "-c", "user.email=test@example.invalid", "commit", "--allow-empty", "-qm", "fixture"], cwd=root, check=True)
            (root / ".python-version").write_text(dev.PINS["python"])
            # A controlled child fails before any external tool or installation is invoked.
            original_commands, original_argv = dev.commands, sys.argv
            try:
                dev.commands = lambda *_: [[sys.executable, "-c", "raise SystemExit(7)"]]
                sys.argv = ["dev", "check", "--profile", "mcp"]
                import os
                previous = Path.cwd()
                os.chdir(root)
                try:
                    self.assertEqual(dev.main(), 7)
                finally:
                    os.chdir(previous)
            finally:
                dev.commands, sys.argv = original_commands, original_argv
            report = json.loads(next((root / ".fogmachine-runs").glob("*/report.json")).read_text())
            self.assertFalse(report["pass"])
            self.assertEqual(report["steps"][0]["exit_code"], 7)

if __name__ == "__main__":
    unittest.main()
