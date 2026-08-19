#!/usr/bin/env python3
"""Execute the Super Browser verifier from the exact assembled template payload."""

from __future__ import annotations

import base64
import io
import json
import os
from pathlib import Path, PurePosixPath
import subprocess
import sys
import tarfile
import tempfile

ROOT = Path(__file__).resolve().parents[2]
RESOLVED = ROOT / "revenue-partner-agent.resolved.json"
PAYLOAD_DESTINATION = "/opt/revenue-partner/payload.tgz.b64"
VERIFY_RELATIVE = PurePosixPath("hermes/local-packages/super-browser/scripts/verify-super-browser")


def _safe_members(archive: tarfile.TarFile) -> list[tarfile.TarInfo]:
    members = archive.getmembers()
    for member in members:
        path = PurePosixPath(member.name)
        if path.is_absolute() or ".." in path.parts:
            raise RuntimeError(f"unsafe archive path: {member.name}")
        if member.issym() or member.islnk() or member.isdev():
            raise RuntimeError(f"unsupported archive entry: {member.name}")
    return members


def main() -> int:
    payload = json.loads(RESOLVED.read_text(encoding="utf-8"))
    entries = [item for item in payload.get("files", []) if item.get("to") == PAYLOAD_DESTINATION]
    if len(entries) != 1:
        raise RuntimeError(f"expected one assembled payload entry, found {len(entries)}")
    encoded = entries[0].get("inline")
    if not isinstance(encoded, str):
        raise RuntimeError("assembled payload is not inline base64 text")
    compressed = base64.b64decode(encoded, validate=True)

    with tempfile.TemporaryDirectory(prefix="revenue-partner-assembled-") as directory:
        root = Path(directory).resolve()
        with tarfile.open(fileobj=io.BytesIO(compressed), mode="r:gz") as archive:
            members = _safe_members(archive)
            if str(VERIFY_RELATIVE) not in {member.name for member in members}:
                raise RuntimeError("assembled payload is missing the Super Browser verifier")
            archive.extractall(root, members=members)

        verifier = root.joinpath(*VERIFY_RELATIVE.parts)
        package_root = verifier.parent.parent
        env = os.environ.copy()
        env["PYTHON_BIN"] = sys.executable
        env["SUPER_BROWSER_REPO_ROOT"] = str(package_root)
        env["SUPER_BROWSER_VERIFY_TMP_DIR"] = str(root / "verify-state")
        env["SUPER_BROWSER_VERIFY_PYCACHE_DIR"] = str(root / "pycache")
        subprocess.run(["bash", str(verifier)], cwd=package_root, env=env, check=True)

    print("assembled_super_browser_verifier_ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
