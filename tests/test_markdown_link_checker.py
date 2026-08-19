from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import unittest


CHECKER_PATH = Path(__file__).resolve().parents[1] / ".github/scripts/check_markdown_links.py"
SPEC = importlib.util.spec_from_file_location("check_markdown_links", CHECKER_PATH)
assert SPEC and SPEC.loader
CHECKER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECKER)


class MarkdownLinkCheckerTests(unittest.TestCase):
    def _run_fixture(self, body: str) -> int:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "README.md").write_text(body, encoding="utf-8")
            previous = getattr(CHECKER, "ROOT")
            setattr(CHECKER, "ROOT", root)
            try:
                return CHECKER.main()
            finally:
                setattr(CHECKER, "ROOT", previous)

    def test_missing_markdown_image_is_rejected(self) -> None:
        self.assertEqual(self._run_fixture("![missing](assets/missing.svg)\n"), 1)

    def test_missing_html_assets_are_rejected(self) -> None:
        body = '<img src="assets/missing.png"><a href="docs/missing.html">missing</a>\n'
        self.assertEqual(self._run_fixture(body), 1)

    def test_external_and_existing_assets_pass(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "asset.png").write_bytes(b"fixture")
            (root / "README.md").write_text(
                "![local](asset.png)\n<img src=\"https://example.com/asset.png\">\n",
                encoding="utf-8",
            )
            previous = getattr(CHECKER, "ROOT")
            setattr(CHECKER, "ROOT", root)
            try:
                self.assertEqual(CHECKER.main(), 0)
            finally:
                setattr(CHECKER, "ROOT", previous)


if __name__ == "__main__":
    unittest.main()
