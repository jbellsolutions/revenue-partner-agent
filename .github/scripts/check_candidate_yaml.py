#!/usr/bin/env python3
"""Parse every exact Git-index YAML document with the locked PyYAML."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import subprocess
import sys

import yaml

GIT = os.environ.get("REVENUE_PARTNER_VERIFY_GIT", "/usr/bin/git")


def git(root: Path, *args: str) -> bytes:
    if not Path(GIT).is_absolute() or not os.access(GIT, os.X_OK):
        raise RuntimeError("trusted absolute Git executable unavailable")
    return subprocess.check_output([GIT, "-C", str(root), *args])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    root = args.root.resolve()

    paths = [
        item.decode("utf-8", "surrogateescape")
        for item in git(root, "ls-files", "-z", "--", "*.yaml", "*.yml").split(b"\0")
        if item
    ]
    failures: list[str] = []
    for path in sorted(paths):
        try:
            blob = git(root, "show", f":{path}")
            yaml.safe_load(blob.decode("utf-8"))
        except Exception as exc:
            failures.append(f"{path}: {type(exc).__name__}")

    if failures:
        print("candidate_yaml_failed", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1

    print(f"candidate_yaml_ok {len(paths)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
