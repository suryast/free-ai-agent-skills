import importlib.util
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "cron-compose.py"
SPEC = importlib.util.spec_from_file_location("cron_compose", SCRIPT)
assert SPEC and SPEC.loader
cron_compose = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(cron_compose)


class BlockPathTests(unittest.TestCase):
    def test_valid_nested_block_is_loaded(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            blocks_dir = Path(tmp)
            block = blocks_dir / "env" / "safe.md"
            block.parent.mkdir()
            block.write_text("safe content", encoding="utf-8")

            self.assertEqual(cron_compose.load_block(blocks_dir, "env/safe"), "safe content")

    def test_parent_traversal_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, "Invalid block name"):
                cron_compose.load_block(Path(tmp), "../secret")

    def test_absolute_path_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, "Invalid block name"):
                cron_compose.load_block(Path(tmp), "/etc/passwd")

    def test_symlink_escape_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as outside:
            blocks_dir = Path(tmp)
            (blocks_dir / "linked").symlink_to(outside, target_is_directory=True)

            with self.assertRaisesRegex(ValueError, "escapes blocks directory"):
                cron_compose.load_block(blocks_dir, "linked/secret")


class ManifestTests(unittest.TestCase):
    def test_manifest_root_must_be_mapping(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            manifest = Path(tmp) / "manifest.yaml"
            manifest.write_text("- not\n- a\n- mapping\n", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "manifest root must be a mapping"):
                cron_compose.load_yaml(manifest)


if __name__ == "__main__":
    unittest.main()