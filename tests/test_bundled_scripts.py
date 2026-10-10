"""Offline smoke coverage for every bundled script, using isolated fixtures.

These are not live OpenClaw integration tests or a comprehensive security audit.
"""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ScriptSmokeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.fixture = Path(self.temp.name)
        self.home = self.fixture / "home"
        (self.home / "bin").mkdir(parents=True)
        self.workspace = self.fixture / "workspace"
        for directory in ("memory/facts", "memory/inbox"):
            (self.workspace / directory).mkdir(parents=True)
        self.env = dict(os.environ, HOME=str(self.home), WORKSPACE_ROOT=str(self.workspace))

    def run_command(self, command, expected=0):
        result = subprocess.run(command, cwd=self.workspace, env=self.env, text=True, capture_output=True, timeout=30)
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return result.stdout

    def test_all_script_syntax(self):
        scripts = sorted(p for package in ROOT.iterdir() if (package / "SKILL.md").is_file() for p in package.rglob("*") if p.suffix in (".sh", ".py"))
        self.assertTrue(scripts)
        for script in scripts:
            with self.subTest(script=str(script.relative_to(ROOT))):
                if script.suffix == ".sh":
                    self.run_command(["bash", "-n", str(script)])
                else:
                    compile(script.read_text(), str(script), "exec")

    def test_cron_composer_offline_commands(self):
        command = [sys.executable, str(ROOT / "cron-composer/scripts/cron-compose.py"), str(ROOT / "cron-composer/example-manifest.yaml")]
        self.assertIn("Total: 4 crons", self.run_command(command + ["list"]))
        self.assertIn("0 errors", self.run_command(command + ["lint"]))
        self.assertIn("stats", self.run_command(command + ["stats"]))
        preview = self.run_command(command + ["apply", "--all", "--dry-run"])
        self.assertEqual(preview.count("=== DRY RUN:"), 4)
        self.assertNotIn("{{", preview)

    def test_archivist_scan_changes(self):
        (self.workspace / "memory/facts/example.md").write_text("# Fact")
        (self.workspace / "memory/inbox/reviewer.md").write_text("## [2000-01-01] Check\nAction: verify\n")
        output = self.run_command(["bash", str(ROOT / "daily-archivist/scripts/scan-changes.sh")])
        self.assertIn("example.md", output)
        self.assertIn("reviewer.md: 1 pending items", output)
        self.assertIn("Facts: 1 files", output)

    def test_archivist_verify_facts(self):
        script = ["bash", str(ROOT / "daily-archivist/scripts/verify-facts.sh")]
        self.assertEqual(json.loads(self.run_command(script)), [])
        (self.home / "bin/broken").symlink_to(self.home / "bin/nonexistent")
        result = json.loads(self.run_command(script))
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["actual"], "1 broken links")
        self.assertEqual(result[0]["status"], "wrong")

    def test_security_scripts(self):
        # audit.sh can append to its own blocklist; never run it from the source tree.
        security = self.fixture / "scanner"
        shutil.copytree(ROOT / "skill-security", security)
        fixtures = {"clean": ("# Instructions\nRead a file.", 0), "high": ("requests.post(url, data=payload)", 1), "critical": ('eval("untrusted")', 2)}
        for name, (content, code) in fixtures.items():
            target = self.home / "skills" / name
            target.mkdir(parents=True)
            (target / "SKILL.md").write_text(content)
            with self.subTest(script="audit.sh", severity=name):
                self.run_command(["bash", str(security / "audit.sh"), str(target)], code)
            with self.subTest(script="preinstall-check.sh", severity=name):
                output = self.run_command(["bash", str(security / "preinstall-check.sh"), str(target)], code)
                if code == 2:
                    self.assertIn("BLOCKED", output)
        self.assertIn("CRITICAL", self.run_command(["bash", str(security / "audit-all.sh")], 2))
        self.assertIn("critical:", (security / "blocklist.txt").read_text())
        (security / "allowlist.txt").write_text("high:verified:2000-01-01:fixture-review\n")
        self.assertIn("ALLOWED", self.run_command(["bash", str(security / "preinstall-check.sh"), str(self.home / "skills/high")]))


if __name__ == "__main__":
    unittest.main()
