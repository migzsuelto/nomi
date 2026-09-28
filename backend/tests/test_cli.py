import subprocess
import sys
import unittest
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]


class CliTests(unittest.TestCase):
    def run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-m", "app.cli", *args],
            cwd=BACKEND_DIR,
            check=False,
            capture_output=True,
            text=True,
        )

    def test_greet_accepts_a_name(self) -> None:
        result = self.run_cli("greet", "Ada")

        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "Hello, Ada!\n")

    def test_greet_is_listed_in_help(self) -> None:
        result = self.run_cli("--help")

        self.assertEqual(result.returncode, 0)
        self.assertIn("greet", result.stdout)
        self.assertIn("Greet someone by name.", result.stdout)

    def test_greet_rejects_an_empty_name(self) -> None:
        result = self.run_cli("greet", "")

        self.assertEqual(result.returncode, 2)
        self.assertIn("name must not be empty", result.stderr)


if __name__ == "__main__":
    unittest.main()
