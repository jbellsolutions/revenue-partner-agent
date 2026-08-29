#!/usr/bin/env python3
"""Seed Revenue Partner identity, knowledge, and skills without overwriting edits."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import sys


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sync_tree(source: Path, target: Path, prior: dict[str, str], current: dict[str, str]) -> tuple[int, int]:
    copied = 0
    preserved = 0
    for source_file in sorted(path for path in source.rglob("*") if path.is_file()):
        relative = source_file.relative_to(source).as_posix()
        target_file = target / relative
        key = target_file.as_posix()
        source_digest = digest(source_file)
        previous_digest = prior.get(key)
        may_replace = not target_file.exists()
        if target_file.exists() and previous_digest:
            may_replace = digest(target_file) == previous_digest
        if may_replace:
            target_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_file, target_file)
            current[key] = source_digest
            copied += 1
        else:
            if previous_digest:
                current[key] = previous_digest
            preserved += 1
    return copied, preserved


def main() -> int:
    if len(sys.argv) != 3:
        raise SystemExit("usage: sync_seed.py REPOSITORY_ROOT DATA_DIR")
    root = Path(sys.argv[1]).resolve()
    data = Path(sys.argv[2]).resolve()
    data.mkdir(parents=True, exist_ok=True)
    manifest_path = data / ".revenue-partner-seed-manifest.json"
    try:
        prior = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    except (OSError, ValueError):
        prior = {}
    current: dict[str, str] = {}

    soul_target = data / "SOUL.md"
    if not soul_target.exists():
        shutil.copy2(root / "files/SOUL.md", soul_target)

    copied = preserved = 0
    for source, target in (
        (root / "files/agent-knowledge", data / "agent-knowledge"),
        (root / "files/skills", data / "skills"),
        (root / "files/local-packages/super-browser/skills", data / "skills/browser"),
    ):
        added, kept = sync_tree(source, target, prior, current)
        copied += added
        preserved += kept

    manifest_path.write_text(json.dumps(current, indent=2, sort_keys=True) + "\n")
    print(f"Revenue Partner seed synced: {copied} files updated, {preserved} owner edits preserved.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
