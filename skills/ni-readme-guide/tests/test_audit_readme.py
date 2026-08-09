"""Offline tests for the bilingual README audit."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "audit_readme.py"


class AuditReadmeTests(unittest.TestCase):
    def run_audit(self, root: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), str(root)],
            capture_output=True,
            check=False,
            text=True,
        )

    def write_valid_pair(self, root: Path) -> None:
        assets = root / "assets" / "readme"
        assets.mkdir(parents=True)
        (assets / "hero.svg").write_text(
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 320">'
            "<title>Project hero</title></svg>",
            encoding="utf-8",
        )
        shared = """
![Project hero](./assets/readme/hero.svg)

## SECTION

[Docs](./docs.md)

```bash
python -m project
```
"""
        (root / "docs.md").write_text("docs", encoding="utf-8")
        (root / "README.md").write_text(
            "# 项目\n\n中文 | [English](./README.en.md)\n" + shared.replace("SECTION", "快速开始"),
            encoding="utf-8",
        )
        (root / "README.en.md").write_text(
            "# Project\n\n[中文](./README.md) | English\n" + shared.replace("SECTION", "Quick start"),
            encoding="utf-8",
        )

    def test_valid_pair_passes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_valid_pair(root)
            result = self.run_audit(root)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("OK: bilingual links", result.stdout)

    def test_missing_english_readme_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "README.md").write_text("# 项目", encoding="utf-8")
            result = self.run_audit(root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("README.en.md", result.stdout)

    def test_language_link_and_code_drift_fail(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_valid_pair(root)
            english = (root / "README.en.md").read_text(encoding="utf-8")
            english = english.replace("[中文](./README.md) | English", "English")
            english = english.replace("python -m project", "python -m other")
            (root / "README.en.md").write_text(english, encoding="utf-8")
            result = self.run_audit(root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("README.en.md missing link", result.stdout)
            self.assertIn("fenced code blocks differ", result.stdout)


if __name__ == "__main__":
    unittest.main()
