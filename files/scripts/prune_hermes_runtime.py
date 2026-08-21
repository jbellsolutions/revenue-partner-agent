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

# `hermes_cli/main.py` imports and registers the Slack subcommand parser at module
# scope, so deleting `hermes_cli/subcommands/slack.py` alone makes every `hermes`
# invocation die with ModuleNotFoundError. The pruned module must be detached from
# its call sites in the same operation. Anchors are exact; drift fails the build.
CLI_ENTRY = "hermes_cli/main.py"
CLI_DETACHED_ANCHORS = (
    "from hermes_cli.subcommands.slack import build_slack_parser\n",
    "    build_slack_parser(subparsers, cmd_slack=cmd_slack)\n",
)
# Names that must not survive in the CLI entry once the module is gone. `cmd_slack`
# is deliberately excluded: it is a function body whose import of the pruned
# `slack_cli` is lazy and unreachable once the parser is no longer registered.
CLI_DANGLING_NAMES = ("build_slack_parser",)


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


def _detach_pruned_cli_references(distribution) -> None:
    """Strip module-scope references to the pruned Slack subcommand from the CLI entry.

    Deleting the module without detaching its import leaves `hermes` unrunnable, which
    only surfaces at image-build time. Every anchor must be present exactly once; any
    drift means the vendored CLI moved and the manifest needs review, so fail loudly
    rather than silently shipping a broken interpreter.
    """
    entry = _surface_target(distribution, CLI_ENTRY)
    source = entry.read_text(encoding="utf-8")

    for anchor in CLI_DETACHED_ANCHORS:
        found = source.count(anchor)
        if found != 1:
            raise RuntimeError(
                f"Hermes CLI prune anchor drifted in {CLI_ENTRY}; "
                f"expected exactly 1 occurrence of {anchor!r}, found {found}"
            )
        source = source.replace(anchor, "", 1)

    entry.write_text(source, encoding="utf-8")
    written = entry.read_text(encoding="utf-8")

    # Static verification only: the CLI entry must stay dependency-free to check, because
    # this also runs against a `--no-deps` wheel install where importing it would fail on
    # unrelated third-party modules and mask the condition being tested.
    try:
        compile(written, str(entry), "exec")
    except SyntaxError as exc:
        raise RuntimeError(f"Hermes CLI entry no longer compiles after pruning: {exc}") from exc

    for dangling in CLI_DANGLING_NAMES:
        if dangling in written:
            raise RuntimeError(
                f"Hermes CLI retains a reference to pruned surface {dangling!r} in {CLI_ENTRY}; "
                "the pruned module would fail at interpreter start"
            )
    print(f"hermes_cli_detached {len(CLI_DETACHED_ANCHORS)} {CLI_ENTRY}")


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

    _detach_pruned_cli_references(distribution)

    print(f"hermes_runtime_pruned {len(targets)} {Path(sys.prefix).resolve()}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"hermes runtime prune failed: {exc}", file=sys.stderr)
        raise
