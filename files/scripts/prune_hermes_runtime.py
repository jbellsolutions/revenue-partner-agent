#!/usr/bin/env python3
"""Remove non-release Hermes connector surfaces from the immutable image."""

from __future__ import annotations

import importlib.metadata
from pathlib import Path
import shutil
import sys

EXPECTED_VERSION = "0.18.0"
REMOVED_PATHS = (
    "plugins/spotify",
    "plugins/platforms/slack",
    "plugins/platforms/discord",
    "optional-mcps/linear",
    "hermes_cli/slack_cli.py",
    "hermes_cli/subcommands/slack.py",
    "tools/discord_tool.py",
)
PREFIX_DATA_PATHS = {"optional-mcps/linear"}


def _surface_target(distribution, relative: str) -> Path:
    if relative in PREFIX_DATA_PATHS:
        return (Path(sys.prefix) / relative).resolve()
    prefix = Path(relative)
    entries = []
    for entry in distribution.files or ():
        entry_path = Path(str(entry))
        if entry_path == prefix or prefix in entry_path.parents:
            entries.append((entry, entry_path))
    if not entries:
        raise RuntimeError(f"Hermes connector prune manifest drifted; no wheel entry for {relative}")

    targets = set()
    for entry, entry_path in entries:
        located = Path(str(distribution.locate_file(entry))).resolve()
        extra_parts = len(entry_path.parts) - len(prefix.parts)
        target = located
        for _ in range(extra_parts):
            target = target.parent
        targets.add(target)
    if len(targets) != 1:
        raise RuntimeError(f"Hermes connector wheel entries disagree on target for {relative}: {sorted(map(str, targets))}")
    return targets.pop()


def main() -> int:
    distribution = importlib.metadata.distribution("hermes-agent")
    if distribution.version != EXPECTED_VERSION:
        raise RuntimeError(
            f"refusing Hermes runtime prune for {distribution.version}; expected {EXPECTED_VERSION}"
        )
    targets = [(relative, _surface_target(distribution, relative)) for relative in REMOVED_PATHS]
    missing = [relative for relative, target in targets if not target.exists()]
    if missing:
        raise RuntimeError(f"Hermes connector prune manifest drifted; missing: {missing}")

    for _relative, target in targets:
        if target.is_dir() and not target.is_symlink():
            shutil.rmtree(target)
        else:
            target.unlink()

    survivors = [relative for relative, target in targets if target.exists()]
    if survivors:
        raise RuntimeError(f"Hermes connector surfaces survived pruning: {survivors}")
    print(f"hermes_runtime_pruned {len(targets)} {Path(sys.prefix).resolve()}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"hermes runtime prune failed: {exc}", file=sys.stderr)
        raise
