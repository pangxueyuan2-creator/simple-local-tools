from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "clean-name.py"


class CleanNameTests(unittest.TestCase):
    def run_script(self, folder: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), str(folder)],
            check=True,
            capture_output=True,
            text=True,
        )

    def test_renames_regular_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            original = folder / "hello 世界.txt"
            original.write_text("ok", encoding="utf-8")

            self.run_script(folder)

            self.assertFalse(original.exists())
            self.assertTrue((folder / "hello-世界.txt").exists())

    def test_preserves_dotfiles(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            dotfile = folder / ".env"
            dotfile.write_text("TOKEN=placeholder", encoding="utf-8")

            self.run_script(folder)

            self.assertTrue(dotfile.exists())
            self.assertFalse((folder / "env").exists())

    def test_skips_name_that_becomes_empty(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            original = folder / "【】.txt"
            original.write_text("ok", encoding="utf-8")

            result = self.run_script(folder)

            self.assertTrue(original.exists())
            self.assertIn("skip (empty after cleaning)", result.stdout)


if __name__ == "__main__":
    unittest.main()
