#!/usr/bin/env python3
"""Fail when shipped Markdown or HTML points to a missing local path."""

from __future__ import annotations

from pathlib import Path
import re
import sys
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[2]
SKIP_PARTS = {".git", ".artifacts", "node_modules"}
MARKDOWN_LINK = re.compile(r"(?<!!)\[[^\]]*\]\(([^)]+)\)")
MARKDOWN_IMAGE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
HTML_ASSET = re.compile(r"\b(?:src|href)\s*=\s*[\"']([^\"']+)[\"']", re.IGNORECASE)
EXTERNAL_PREFIXES = ("http://", "https://", "mailto:", "tel:", "data:", "javascript:", "#")


def _references(document: Path, text: str):
    for pattern in (MARKDOWN_LINK, MARKDOWN_IMAGE):
        for match in pattern.finditer(text):
            yield match.group(1).strip().split()[0].strip("<>")
    for match in HTML_ASSET.finditer(text):
        yield match.group(1).strip()


def _target(document: Path, href: str) -> Path | None:
    if not href or href.lower().startswith(EXTERNAL_PREFIXES):
        return None
    raw = unquote(href.split("#", 1)[0].split("?", 1)[0])
    if not raw:
        return None
    if raw.startswith("/"):
        return ROOT / raw.lstrip("/")
    return document.parent / raw


def main() -> int:
    broken: list[str] = []
    checked = 0
    documents = [*ROOT.rglob("*.md"), *ROOT.rglob("*.html")]
    for document in documents:
        if SKIP_PARTS.intersection(document.parts):
            continue
        text = document.read_text(encoding="utf-8", errors="replace")
        for href in _references(document, text):
            target = _target(document, href)
            if target is None:
                continue
            checked += 1
            if not target.resolve().exists():
                broken.append(f"{document.relative_to(ROOT)} -> {href}")

    if broken:
        print("Broken local Markdown/HTML links or assets:", file=sys.stderr)
        for item in broken:
            print(f"- {item}", file=sys.stderr)
        return 1
    print(f"markdown_links_ok {checked}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
