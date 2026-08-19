#!/usr/bin/env python3
"""Validate YAML frontmatter for every exact-index SKILL.md blob."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import subprocess
import sys

import yaml

DEFAULT_ROOT = Path(__file__).resolve().parents[2]
GIT = os.environ.get("REVENUE_PARTNER_VERIFY_GIT", "/usr/bin/git")


def git_output(root: Path, *args: str) -> bytes:
    if not Path(GIT).is_absolute() or not os.access(GIT, os.X_OK):
        raise RuntimeError("trusted absolute Git executable unavailable")
    return subprocess.check_output([GIT, *args], cwd=root)


def skill_paths(root: Path) -> list[str]:
    raw = git_output(root, "ls-files", "-z")
    return sorted(
        item.decode("utf-8", errors="surrogateescape")
        for item in raw.split(b"\0")
        if item and item.decode("utf-8", errors="surrogateescape").endswith("SKILL.md")
    )


def index_blob(root: Path, path: str) -> str:
    return git_output(root, "show", f":{path}").decode("utf-8")


def validate(root: Path) -> list[tuple[str, str]]:
    findings: list[tuple[str, str]] = []
    for path in skill_paths(root):
        text = index_blob(root, path)
        lines = text.splitlines()
        if not lines or lines[0] != "---":
            findings.append((path, "missing opening frontmatter delimiter"))
            continue
        try:
            end = lines.index("---", 1)
        except ValueError:
            findings.append((path, "missing closing frontmatter delimiter"))
            continue
        try:
            metadata = yaml.safe_load("\n".join(lines[1:end]))
        except yaml.YAMLError as exc:
            findings.append((path, type(exc).__name__))
            continue
        if not isinstance(metadata, dict):
            findings.append((path, "frontmatter must be a mapping"))
            continue
        for key in ("name", "description"):
            value = metadata.get(key)
            if not isinstance(value, str) or not value.strip():
                findings.append((path, f"missing non-empty {key}"))
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    args = parser.parse_args()
    root = args.root.resolve()
    try:
        findings = validate(root)
        count = len(skill_paths(root))
    except (OSError, UnicodeError, subprocess.CalledProcessError) as exc:
        print(f"skill frontmatter validation failed: {type(exc).__name__}", file=sys.stderr)
        return 2
    if findings:
        print("Invalid exact-index skill frontmatter:", file=sys.stderr)
        for path, reason in findings:
            print(f"- {path}: {reason}", file=sys.stderr)
        return 1
    print(f"candidate_skill_frontmatter_ok {count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
