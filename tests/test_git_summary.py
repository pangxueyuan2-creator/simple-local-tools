import importlib.util
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "git-summary.py"
SPEC = importlib.util.spec_from_file_location("git_summary", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
git_summary = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(git_summary)


class GitSummaryArgumentTests(unittest.TestCase):
    def test_default_days(self):
        self.assertEqual(git_summary.parse_args([]).days, 14)

    def test_custom_positive_days(self):
        self.assertEqual(git_summary.parse_args(["--days", "30"]).days, 30)

    def test_rejects_zero_and_negative_days(self):
        for value in ("0", "-3"):
            with self.subTest(value=value), self.assertRaises(SystemExit):
                git_summary.parse_args(["--days", value])

    def test_rejects_non_integer_days(self):
        with self.assertRaises(SystemExit):
            git_summary.parse_args(["--days", "abc"])

    def test_rejects_missing_days_value(self):
        with self.assertRaises(SystemExit):
            git_summary.parse_args(["--days"])

    def test_rejects_unknown_arguments(self):
        with self.assertRaises(SystemExit):
            git_summary.parse_args(["--unknown"])


if __name__ == "__main__":
    unittest.main()
