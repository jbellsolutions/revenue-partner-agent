#!/usr/bin/env python3
"""Safely bridge allowlisted runtime values into Hermes and optionally exec.

Dotenv content is parsed without expansion or command evaluation. Values are
serialized with POSIX-safe quoting and written atomically with mode 0600.
"""

from __future__ import annotations

import argparse
from collections.abc import Mapping, Sequence, Set
import os
from pathlib import Path
import re
import shlex
import tempfile


MANAGED_KEYS = (
    # Non-secret operational defaults.
    "AGENT_BROWSER_EXECUTABLE_PATH",
    "TERMINAL_TIMEOUT",
    "TERMINAL_LIFETIME_SECONDS",
    "BROWSER_SESSION_TIMEOUT",
    "BROWSER_INACTIVITY_TIMEOUT",
    "OBSIDIAN_VAULT_PATH",
    "WIKI_PATH",
    "LATITUDE_BASE_URL",
    "LATITUDE_INGEST_URL",
    "LATITUDE_SERVICE_NAME",
    "LATITUDE_HERMES_NO_CONTENT",
    "LATITUDE_HERMES_TELEMETRY_ENABLED",
    "AGENTPHONE_BASE_URL",
    # Runtime credentials and identifiers.
    "COMPOSIO_CONSUMER_KEY",
    "ORGO_API_KEY",
    "ORGO_DEFAULT_COMPUTER_ID",
    "NOTION_API_KEY",
    "EXA_API_KEY",
    "FIRECRAWL_API_KEY",
    "BROWSER_USE_API_KEY",
    "AIRTOP_API_KEY",
    "DECODO_PROXY",
    "HYPERBROWSER_API_KEY",
    "STEEL_API_KEY",
    "BROWSERBASE_API_KEY",
    "VIDIQ_API_KEY",
    "VIDIQ_MCP_API_KEY",
    "SLACK_BOT_TOKEN",
    "SLACK_APP_TOKEN",
    "SLACK_SIGNING_SECRET",
    "AGENTPHONE_API_KEY",
    "AGENTPHONE_AGENT_ID",
    "AGENTPHONE_PHONE_NUMBER",
    "AGENTPHONE_NUMBER",
    "AGENTPHONE_NUMBER_ID",
    "AGENTMAIL_API_KEY",
    "AGENTMAIL_INBOX_ID",
    "AGENTMAIL_INBOX",
    "ONEPASSWORD_SERVICE_ACCOUNT_TOKEN",
    "OP_SERVICE_ACCOUNT_TOKEN",
    "OBSIDIAN_API_KEY",
    "LATITUDE_API_KEY",
    "LATITUDE_PROJECT_ID",
    "LATITUDE_PROJECT",
    "LANGFUSE_PUBLIC_KEY",
    "LANGFUSE_SECRET_KEY",
    "OPENAI_API_KEY",
    "OPENROUTER_API_KEY",
    "XAI_API_KEY",
    "HONCHO_API_KEY",
    "AI_GATEWAY_API_KEY",
    "MODEL_API_KEY",
    "X_APP_ONLY_BEARER_TOKEN",
    "IDEABROWSER_KEY",
    "HERMES_SPOTIFY_CLIENT_ID",
    "DISCORD_BOT_TOKEN",
    "TELEGRAM_BOT_TOKEN",
    "TELEGRAM_ALLOWED_USERS",
    "TELEGRAM_HOME_CHANNEL",
    "TELEGRAM_BOT_USERNAME",
    "GITHUB_TOKEN",
    "GH_TOKEN",
    "OWNER_EMAIL",
)

_ASSIGNMENT = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)$")


def _decode_value(raw: str) -> str | None:
    """Parse one dotenv RHS without expansion or command evaluation."""
    try:
        parts = shlex.split(raw, comments=False, posix=True)
    except ValueError:
        return None
    if len(parts) != 1:
        return None
    value = parts[0]
    if any(char in value for char in ("\x00", "\r", "\n")):
        return None
    return value


def read_allowlisted(path: Path, allowed: Set[str]) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.is_file():
        return values
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        match = _ASSIGNMENT.match(line)
        if not match or match.group(1) not in allowed:
            continue
        value = _decode_value(match.group(2))
        if value is not None:
            values[match.group(1)] = value
    return values


def collect_values(
    sources: Sequence[Path],
    environ: Mapping[str, str] | None = None,
    managed_keys: Sequence[str] = MANAGED_KEYS,
) -> dict[str, str]:
    allowed = set(managed_keys)
    values: dict[str, str] = {}
    for source in sources:
        values.update(read_allowlisted(source, allowed))

    current_env = os.environ if environ is None else environ
    for key in managed_keys:
        value = current_env.get(key)
        if not value or any(char in value for char in ("\x00", "\r", "\n")):
            continue
        values[key] = value
    return values


def update_env(
    target: Path,
    sources: Sequence[Path],
    environ: Mapping[str, str] | None = None,
    managed_keys: Sequence[str] = MANAGED_KEYS,
) -> int:
    allowed = set(managed_keys)
    values = collect_values(sources, environ, managed_keys)

    preserved: list[str] = []
    if target.is_file():
        for line in target.read_text(encoding="utf-8", errors="replace").splitlines():
            match = _ASSIGNMENT.match(line)
            if not match or match.group(1) not in allowed:
                preserved.append(line)

    rendered = preserved[:]
    for key in managed_keys:
        if key in values:
            rendered.append(f"{key}={shlex.quote(values[key])}")
    body = "\n".join(rendered).rstrip("\n") + "\n"

    target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd, temporary = tempfile.mkstemp(prefix=f".{target.name}.", dir=target.parent)
    temporary_path = Path(temporary)
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(body)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, target)
        os.chmod(target, 0o600)
    finally:
        temporary_path.unlink(missing_ok=True)
    return len(values)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", type=Path, default=Path("/root/.hermes/.env"))
    parser.add_argument("--source", action="append", type=Path)
    parser.add_argument("--only", action="append", choices=MANAGED_KEYS)
    parser.add_argument("--exec", dest="exec_command", nargs=argparse.REMAINDER)
    args = parser.parse_args()

    sources = args.source or [Path("/root/.env"), args.target]
    managed_keys = tuple(args.only) if args.only else MANAGED_KEYS
    count = update_env(args.target, sources, managed_keys=managed_keys)
    print(f"bridged {count} allowlisted environment values", flush=True)

    if args.exec_command:
        child_env = os.environ.copy()
        child_env.update(collect_values([args.target], child_env, managed_keys))
        os.execvpe(args.exec_command[0], args.exec_command, child_env)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
