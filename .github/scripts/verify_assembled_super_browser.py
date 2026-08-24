#!/usr/bin/env python3
"""Assert the assembled template attaches Super Browser by URL and vendors nothing.

This gate previously executed the packaged Super Browser's own verifier out of
the assembled payload. That package is no longer shipped: Super Browser is a
hosted MCP server the agent attaches to by URL, so a second copy in the image
could only drift from the server.

Vendoring it also carried a concrete cost. The install program pip-installed the
packaged copy's `requirements-runtime.lock` into the *same* interpreter as
`build-locks/hermes-runtime.lock`. Both are hash-locked and deterministic in
isolation; installed in sequence the second silently upgraded six shared pins,
including `mcp` 1.26.0 -> 2.0.0 against an agent that pins `mcp==1.26.0` exactly.
That broke every HTTP MCP connection and was invisible to every gate here,
because each one reads a single lock.

The check therefore runs at the same altitude as before -- the exact assembled
artifact, not the source tree -- but asserts the inverse property.
"""

from __future__ import annotations

import base64
import io
import json
from pathlib import Path
import sys
import tarfile

ROOT = Path(__file__).resolve().parents[2]
RESOLVED = ROOT / "revenue-partner-agent.resolved.json"
PAYLOAD_DESTINATION = "/opt/revenue-partner/payload.tgz.b64"


def fail(message: str) -> None:
    print(f"assembled_super_browser_verifier FAILED: {message}", file=sys.stderr)
    raise SystemExit(1)


def main() -> int:
    if not RESOLVED.exists():
        fail(f"missing assembled artifact: {RESOLVED}")
    template = json.loads(RESOLVED.read_text())

    servers = template.get("files", [])
    payload = next((f for f in servers if f.get("to") == PAYLOAD_DESTINATION), None)
    if payload is None:
        fail(f"assembled template has no payload at {PAYLOAD_DESTINATION}")

    archive = base64.b64decode(payload["inline"])
    with tarfile.open(fileobj=io.BytesIO(archive), mode="r:gz") as tar:
        names = tar.getnames()

    vendored = [n for n in names if "local-packages/super-browser" in n]
    if vendored:
        fail(f"payload still vendors Super Browser ({len(vendored)} entries)")

    extra_locks = [n for n in names if n.endswith("requirements-runtime.lock")]
    if extra_locks:
        fail(f"payload ships a second dependency lock: {extra_locks}")

    install = template["apps"][0]["install"]
    locks = {line.rsplit("/", 1)[-1] for line in install.split() if line.endswith(".lock")}
    if locks != {"hermes-runtime.lock"}:
        fail(f"install program must consume exactly one runtime lock; found {sorted(locks)}")

    for absent in ("super-browser-server", "install_local_super_browser.sh", "SB_ROOT"):
        if absent in install:
            fail(f"install program still references the vendored copy: {absent}")

    print(f"assembled_super_browser_verifier_ok hosted-attach payload_files={len(names)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
