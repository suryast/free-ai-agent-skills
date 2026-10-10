"""Deterministic positive/negative format fixtures; no runtime or network access."""
from pathlib import Path
import tempfile
import unittest

from scripts.validate_skills import discover_packages, main, validate_package

ROOT = Path(__file__).resolve().parents[1]


class FormatTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.package = self.root / "test-skill"
        self.package.mkdir()

    def write(self, header=None, body="# Instructions\nDo the task."):
        header = header if header is not None else "name: test-skill\ndescription: Use when testing skills."
        (self.package / "SKILL.md").write_text(f"---\n{header}\n---\n{body}\n", encoding="utf-8")

    def errors(self):
        return validate_package(self.package, self.root)

    def test_minimal(self):
        self.write()
        self.assertEqual(self.errors(), [])

    def test_existing_packages(self):
        packages = discover_packages(ROOT)
        self.assertTrue(packages, "must discover real packages")
        for package in packages:
            with self.subTest(package=package.name):
                self.assertEqual(validate_package(package, ROOT), [])

    def test_names(self):
        for name in ("Bad", "-bad", "bad-", "bad--name", "bad_name", "bad name", "a" * 65, "other-name", " test-skill ", "123", ""):
            with self.subTest(name=name):
                self.write(f'name: "{name}"\ndescription: Valid description.')
                self.assertTrue(self.errors())

    def test_boundary_and_numeric_names(self):
        for name in ("a" * 64, "123"):
            self.package.rename(self.root / name)
            self.package = self.root / name
            self.write(f'name: "{name}"\ndescription: Use when testing names.')
            self.assertEqual(self.errors(), [])

    def test_symlink_resource_escape(self):
        with tempfile.TemporaryDirectory() as outside:
            target = Path(outside) / "guide.md"
            target.write_text("# Guide")
            (self.package / "guide.md").symlink_to(target)
            self.write(body="[Guide](guide.md)")
            self.assertTrue(self.errors())

    def test_unicode_name(self):
        self.package.rename(self.root / "技能")
        self.package = self.root / "技能"
        self.write("name: 技能\ndescription: Use when testing Unicode names.")
        self.assertEqual(self.errors(), [])

    def test_required_and_scalar_types(self):
        for header in ("description: Valid", "name: test-skill", "name: [test-skill]\ndescription: Valid", "name: test-skill\ndescription: true", "name: test-skill\ndescription: null", "name: test-skill\ndescription: ' '"):
            with self.subTest(header=header):
                self.write(header)
                self.assertTrue(self.errors())

    def test_limits_and_optional_types(self):
        prefix = "name: test-skill\ndescription: Valid\n"
        for field in ("description: " + "x" * 1025, "compatibility: " + "x" * 501, "compatibility: ''", "compatibility: []", "metadata: []", "metadata:\n  version: 1", "metadata:\n  author: true", "metadata:\n  1: text", "license: []", "allowed-tools: []", "platform: universal"):
            with self.subTest(field=field):
                # Replace description rather than adding a duplicate for its limit check.
                self.write("name: test-skill\n" + field if field.startswith("description:") else prefix + field)
                self.assertTrue(self.errors())
        self.write("name: test-skill\ndescription: " + "x" * 1024 + "\ncompatibility: " + "x" * 500 + '\nmetadata:\n  version: "1"\nlicense: MIT\nallowed-tools: Bash(git:*) Read')
        self.assertEqual(self.errors(), [])

    def test_yaml_failures(self):
        for header in ("name: [broken", "- list", "name: test-skill\nname: test-skill", "name: test-skill\ndescription: Trigger: unquoted colon", "name: test-skill\ndescription: !!python/object/apply:os.system ['false']"):
            with self.subTest(header=header):
                self.write(header)
                self.assertTrue(self.errors())
        for text in ("# No frontmatter", "---\nname: test-skill", "---extra\nname: test-skill\n---\nbody"):
            (self.package / "SKILL.md").write_text(text)
            self.assertTrue(self.errors())

    def test_exact_case_and_empty_body(self):
        self.write(body="")
        self.assertTrue(self.errors())
        (self.package / "SKILL.md").rename(self.package / "skill.md")
        self.assertEqual(discover_packages(self.root), [self.package])
        self.assertIn("missing exact-case SKILL.md", self.errors())

    def test_resources(self):
        resources = self.package / "references"
        resources.mkdir()
        (resources / "guide.md").write_text("# Guide")
        (self.root / "LICENSE").write_text("MIT")
        self.write(body="[Guide](references/guide.md) [License](../LICENSE) [External](https://example.com) [Anchor](#usage)\n`references/guide.md`\n[guide]: references/guide.md\n```\n[Template](missing.md)\n```")
        self.assertEqual(self.errors(), [])
        for body in ("[Missing](references/missing.md)", "`scripts/missing.py`", "[Missing][ref]\n[ref]: missing.md", "[Escape](../../outside.md)", "[Encoded](references/missing%20file.md)"):
            with self.subTest(body=body):
                self.write(body=body)
                self.assertTrue(self.errors())
        self.write()
        (self.package / "README.md").write_text("[Missing](references/missing.md)")
        self.assertTrue(self.errors())

    def test_extra_files_and_unrestricted_body(self):
        (self.package / "README.md").write_text("# Extra documentation")
        (self.package / "custom").mkdir()
        self.write(body="No emoji required.\n" * 501)
        self.assertEqual(self.errors(), [])

    def test_empty_discovery_fails(self):
        self.assertEqual(main([str(self.root)]), 1)


if __name__ == "__main__":
    unittest.main()
