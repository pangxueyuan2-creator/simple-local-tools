import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "find-big.py"


class FindBigCliTests(unittest.TestCase):
    def run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            text=True,
            capture_output=True,
            check=False,
        )

    def test_rejects_missing_directory(self) -> None:
        result = self.run_cli("definitely-missing-directory")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("not a directory", result.stderr)

    def test_rejects_non_positive_top(self) -> None:
        result = self.run_cli("--top", "0")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("must be greater than zero", result.stderr)

    def test_lists_only_requested_number_of_largest_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "small.txt").write_bytes(b"a")
            (root / "medium.txt").write_bytes(b"b" * 5)
            (root / "large.txt").write_bytes(b"c" * 10)

            result = self.run_cli("--top", "2", str(root))

        self.assertEqual(result.returncode, 0, result.stderr)
        lines = result.stdout.strip().splitlines()
        self.assertEqual(len(lines), 2)
        self.assertIn("large.txt", lines[0])
        self.assertIn("medium.txt", lines[1])
        self.assertNotIn("small.txt", result.stdout)


if __name__ == "__main__":
    unittest.main()
