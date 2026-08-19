#!/usr/bin/env python3
"""Scan exact Git index blobs for credential material without printing values."""

from __future__ import annotations

import argparse
import ast
import os
from pathlib import Path
import re
import subprocess
import sys


DEFAULT_ROOT = Path(__file__).resolve().parents[2]
GIT = os.environ.get("REVENUE_PARTNER_VERIFY_GIT", "/usr/bin/git")
PATTERNS: tuple[tuple[str, re.Pattern[bytes]], ...] = (
    ("private_key", re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----")),
    ("github_token", re.compile(rb"\bgh[pousr]_[A-Za-z0-9]{20,}\b")),
    ("openai_style_key", re.compile(rb"\bsk-[A-Za-z0-9_-]{20,}\b")),
    ("anthropic_key", re.compile(rb"\bsk-ant-[A-Za-z0-9_-]{20,}\b")),
    ("xai_key", re.compile(rb"\bxai-[A-Za-z0-9_-]{20,}\b")),
    ("onepassword_service_token", re.compile(rb"\bops_[A-Za-z0-9_-]{20,}\b")),
    ("telegram_bot_token", re.compile(rb"\b[0-9]{6,}:[A-Za-z0-9_-]{20,}\b")),
    ("google_api_key", re.compile(rb"\bAIza[A-Za-z0-9_-]{30,}\b")),
    ("gitlab_token", re.compile(rb"\bglpat-[A-Za-z0-9_-]{20,}\b")),
    ("live_secret", re.compile(rb"\b(?:sk_live|whsec)_[A-Za-z0-9._-]{12,}\b")),
    ("aws_access_key", re.compile(rb"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b")),
    ("slack_token", re.compile(rb"\bxox[baprs]-[A-Za-z0-9-]{16,}\b")),
    ("jwt", re.compile(rb"\beyJ[A-Za-z0-9_-]{12,}\.[A-Za-z0-9_-]{12,}\.[A-Za-z0-9_-]{12,}\b")),
)
STATIC_SECRET_ENV_NAMES = (
    "ORGO_API_KEY",
    "AGENTPHONE_API_KEY",
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "GITHUB_TOKEN",
    "GH_TOKEN",
    "LATITUDE_API_KEY",
    "TELEGRAM_BOT_TOKEN",
    "OP_SERVICE_ACCOUNT_TOKEN",
    "ONEPASSWORD_SERVICE_ACCOUNT_TOKEN",
    "AI_GATEWAY_API_KEY",
    "MODEL_API_KEY",
    "OPENROUTER_API_KEY",
    "XAI_API_KEY",
    "COMPOSIO_CONSUMER_KEY",
    "AGENTMAIL_API_KEY",
    "SUPPLIED_TEST_SECRET",
)
PLACEHOLDERS = {"", "...", "[redacted]", "redacted", "changeme", "example", "placeholder", "none", "null", "~"}


def git_output(root: Path, *args: str) -> bytes:
    if not Path(GIT).is_absolute() or not os.access(GIT, os.X_OK):
        raise RuntimeError("trusted absolute Git executable unavailable")
    return subprocess.check_output([GIT, *args], cwd=root)


def index_paths(root: Path) -> list[str]:
    raw = git_output(root, "ls-files", "-z")
    return [item.decode("utf-8", errors="surrogateescape") for item in raw.split(b"\0") if item]


def index_blob(root: Path, path: str) -> bytes:
    return git_output(root, "show", f":{path}")


def bridge_env_names(root: Path) -> tuple[str, ...]:
    data = index_blob(root, "files/safe-env-bridge.py").decode("utf-8")
    tree = ast.parse(data)
    names: set[str] = set(STATIC_SECRET_ENV_NAMES)
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if not any(isinstance(target, ast.Name) and target.id == "MANAGED_KEYS" for target in node.targets):
            continue
        value = ast.literal_eval(node.value)
        if not isinstance(value, tuple) or not all(isinstance(item, str) for item in value):
            raise ValueError("MANAGED_KEYS must be a literal string tuple")
        names.update(value)
    return tuple(sorted(names))


def supplied_values(root: Path) -> list[bytes]:
    values: list[bytes] = []
    for name in bridge_env_names(root):
        value = os.environ.get(name, "")
        if len(value) >= 12 and value not in PLACEHOLDERS:
            values.append(value.encode("utf-8"))
    supplied_file = os.environ.get("REVENUE_PARTNER_SUPPLIED_SECRETS_FILE", "")
    if supplied_file:
        for value in Path(supplied_file).read_bytes().split(b"\0"):
            if len(value) >= 12 and value.decode("utf-8", errors="ignore") not in PLACEHOLDERS:
                values.append(value)
    return values


def _is_safe_placeholder(name: str, value: str) -> bool:
    normalized = value.strip().rstrip(",").strip().strip("'\"").strip()
    lowered = normalized.lower()
    if lowered in PLACEHOLDERS:
        return True
    if lowered.startswith(("<", "${")) and lowered.endswith((">", "}")):
        return True
    if normalized in {f"${name}", f"${{{name}}}"}:
        return True
    if normalized.startswith("op://"):
        return True
    return any(marker in lowered for marker in ("redacted", "placeholder", "example-only", "test-only"))


def credential_env_names(root: Path) -> tuple[str, ...]:
    markers = ("API_KEY", "TOKEN", "SECRET", "PASSWORD", "PRIVATE_KEY", "CREDENTIAL")
    static = set(STATIC_SECRET_ENV_NAMES)
    return tuple(
        name for name in bridge_env_names(root)
        if name in static or any(marker in name for marker in markers)
    )


def assigned_secret_names(data: bytes, names: tuple[str, ...]) -> list[str]:
    """Find dotenv/shell/YAML assignments with non-placeholder values.

    Key names are accepted only when unquoted at the beginning of a line. This
    avoids treating Python/JSON inventories as credentials while covering the
    configuration formats consumed by this release.
    """
    text = data.decode("utf-8", errors="ignore")
    findings: list[str] = []
    for name in names:
        pattern = re.compile(
            rf"(?m)^\s*(?:export\s+)?{re.escape(name)}\s*(?:=|:\s+)\s*([^\r\n#]*)"
        )
        for match in pattern.finditer(text):
            if not _is_safe_placeholder(name, match.group(1)):
                findings.append(name)
                break
    return findings


def scan(root: Path) -> list[tuple[str, str]]:
    findings: list[tuple[str, str]] = []
    secret_names = credential_env_names(root)
    exact_values = supplied_values(root)
    for path in index_paths(root):
        data = index_blob(root, path)
        for label, pattern in PATTERNS:
            if pattern.search(data):
                findings.append((path, label))
        if any(value in data for value in exact_values):
            findings.append((path, "supplied_secret_value"))
        for name in assigned_secret_names(data, secret_names):
            findings.append((path, f"non_placeholder_assignment:{name}"))
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    args = parser.parse_args()
    root = args.root.resolve()
    try:
        findings = scan(root)
    except (OSError, UnicodeError, ValueError, SyntaxError, subprocess.CalledProcessError) as exc:
        print(f"candidate credential scan failed: {type(exc).__name__}", file=sys.stderr)
        return 2
    if findings:
        print("Credential material found in exact Git index blobs:", file=sys.stderr)
        for path, label in sorted(set(findings)):
            print(f"- {path}: {label}", file=sys.stderr)
        return 1
    print(f"candidate_credentials_ok {len(index_paths(root))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
