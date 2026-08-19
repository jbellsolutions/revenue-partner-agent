#!/usr/bin/env python3
"""Private matrix child invoked only by the lock-bootstrapping verifier."""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import sys


VERIFIER = Path(__file__).resolve().with_name("verify_release.py")
SPEC = importlib.util.spec_from_file_location("revenue_partner_verify_release", VERIFIER)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot load locked verifier: {VERIFIER}")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def _consume_parent_authority() -> bool:
    fd_text = os.environ.pop("REVENUE_PARTNER_VERIFY_AUTH_FD", "")
    venv_text = os.environ.pop("REVENUE_PARTNER_VERIFY_VENV", "")
    parent_text = os.environ.pop("REVENUE_PARTNER_VERIFY_PARENT_PID", "")
    try:
        if int(parent_text) != os.getppid():
            return False
        authority_fd = int(fd_text)
        if authority_fd < 3:
            return False
        venv = Path(venv_text).resolve(strict=True)
        if Path(sys.prefix).resolve(strict=True) != venv:
            return False
        expected_bin = venv / ("Scripts" if os.name == "nt" else "bin")
        if Path(sys.executable).parent.resolve(strict=True) != expected_bin.resolve(strict=True):
            return False
        challenge = os.read(authority_fd, 33)
        trailing = os.read(authority_fd, 1)
        os.close(authority_fd)
        if len(challenge) != 32 or trailing:
            return False
    except (OSError, ValueError):
        return False
    return True


def main() -> int:
    if not _consume_parent_authority():
        print("locked matrix child refused: fresh parent authority required", file=sys.stderr)
        return 78
    try:
        MODULE.run_locked_matrix()
    finally:
        MODULE.clean_generated_state()
    print("locked_matrix_child_ok", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
