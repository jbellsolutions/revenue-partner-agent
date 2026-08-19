#!/usr/bin/env python3
"""Split authenticated Orgo transport from the key-less release builder."""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
import secrets
import socket
import sys

ROOT = Path(__file__).resolve().parent
BROKER = ROOT / ".github" / "scripts" / "orgo_release_broker.py"
BUILDER = ROOT / "build_template.py"
BROKER_FD_ENV = "REVENUE_PARTNER_BROKER_FD"
BROKER_SECRET_ENV = "REVENUE_PARTNER_BROKER_SECRET"
BROKER_KEY_SHA256_ENV = "REVENUE_PARTNER_BROKER_KEY_SHA256"
BROKER_KEY_SALT = b"revenue-partner-broker-key-v1:"


def broker_key_sha256(key: str) -> str:
    return hashlib.sha256(hashlib.sha256(BROKER_KEY_SALT + key.encode("utf-8")).digest()).hexdigest()


RELEASE_ALLOWLIST = (
    "ORGO_API_KEY",
    "REVENUE_PARTNER_REVIEW_ATTESTATIONS",
    "REVENUE_PARTNER_OPERATION_INTENT_DIRECTORY",
    "REVENUE_PARTNER_NONCE_LEDGER",
)


def _scrubbed_child_environment() -> dict[str, str]:
    """Build a from-scratch environment for both children.

    Only the explicit release allowlist survives into the broker or builder
    process: gitconfig, fsmonitor hooks, index/object redirection, and every
    other operator variable cannot reach a process that holds ORGO_API_KEY.
    """
    environment = {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "HOME": "/tmp",
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_GLOBAL": "/dev/null",
    }
    for name in RELEASE_ALLOWLIST:
        if name in os.environ:
            environment[name] = os.environ[name]
    return environment


def main() -> int:
    if not (sys.flags.isolated and sys.flags.ignore_environment and sys.flags.no_user_site):
        raise SystemExit("authenticated release entry requires trusted Python -I -s -E")
    if "ORGO_API_KEY" not in os.environ:
        raise SystemExit("ORGO_API_KEY is required by the isolated release broker")
    if BROKER_FD_ENV in os.environ:
        raise SystemExit(f"caller-supplied {BROKER_FD_ENV} is prohibited")
    if BROKER_SECRET_ENV in os.environ:
        raise SystemExit(f"caller-supplied {BROKER_SECRET_ENV} is prohibited")
    if BROKER_KEY_SHA256_ENV in os.environ:
        raise SystemExit(f"caller-supplied {BROKER_KEY_SHA256_ENV} is prohibited")
    key = os.environ["ORGO_API_KEY"]
    key_sha256 = broker_key_sha256(key)
    mac_secret = secrets.token_hex(32)
    builder_socket, broker_socket = socket.socketpair(socket.AF_UNIX, socket.SOCK_STREAM)
    builder_socket.set_inheritable(True)
    broker_socket.set_inheritable(True)
    child = os.fork()
    if child == 0:
        builder_socket.close()
        broker_env = _scrubbed_child_environment()
        broker_env[BROKER_FD_ENV] = str(broker_socket.fileno())
        broker_env[BROKER_SECRET_ENV] = mac_secret
        broker_env[BROKER_KEY_SHA256_ENV] = key_sha256
        os.execve(
            sys.executable,
            [sys.executable, "-I", "-s", "-E", str(BROKER)],
            broker_env,
        )
        raise AssertionError("unreachable")

    broker_socket.close()
    builder_env = _scrubbed_child_environment()
    builder_env.pop("ORGO_API_KEY", None)
    builder_env[BROKER_FD_ENV] = str(builder_socket.fileno())
    builder_env[BROKER_SECRET_ENV] = mac_secret
    builder_env[BROKER_KEY_SHA256_ENV] = key_sha256
    os.execve(
        sys.executable,
        [sys.executable, "-I", "-s", "-E", str(BUILDER), *sys.argv[1:]],
        builder_env,
    )
    raise AssertionError("unreachable")


if __name__ == "__main__":
    raise SystemExit(main())
