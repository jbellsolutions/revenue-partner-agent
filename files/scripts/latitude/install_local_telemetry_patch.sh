#!/usr/bin/env bash
set -euo pipefail

VENV_PY="${LATITUDE_TELEMETRY_VENV_PY:-/usr/local/lib/hermes-agent/venv/bin/python}"
PKG_DIR="${LATITUDE_TELEMETRY_PACKAGE_DIR:-/root/.hermes/local-packages/latitude-telemetry-hermes}"
VALIDATE="${LATITUDE_TELEMETRY_VALIDATE_SCRIPT:-/root/.hermes/scripts/latitude/dewey_observability_validate.py}"

if [[ ! -x "$VENV_PY" ]]; then
  echo "Hermes venv Python not found: $VENV_PY" >&2
  exit 1
fi

# Resolve the core loop from the locked venv's own purelib rather than a fixed
# path. Hermes installs into <venv>/lib/pythonX.Y/site-packages, so any hardcoded
# default both omits that segment and pins an interpreter version; asking the venv
# keeps this correct across Python minor versions.
CORE_LOOP="${LATITUDE_TELEMETRY_CORE_LOOP:-$("$VENV_PY" -c 'import pathlib, sysconfig; print(pathlib.Path(sysconfig.get_paths()["purelib"]) / "agent" / "conversation_loop.py")')}"
if [[ ! -f "$PKG_DIR/latitude_telemetry_hermes/__init__.py" ]]; then
  echo "Local telemetry package not found: $PKG_DIR" >&2
  exit 1
fi
if [[ ! -f "$CORE_LOOP" ]]; then
  echo "Hermes conversation loop not found: $CORE_LOOP" >&2
  exit 1
fi

# Reapply the exact reasoning_config hook after the locked Hermes runtime is
# installed. The patch is idempotent and fails if the expected anchor drifts.
"$VENV_PY" - "$CORE_LOOP" <<'PY'
from pathlib import Path
import sys

path = Path(sys.argv[1])
text = path.read_text(encoding="utf-8")
needle = "                            reasoning_config=agent.reasoning_config,\n"
if needle not in text:
    anchor = (
        "                            max_tokens=agent.max_tokens,\n"
        "                            started_at=api_start_time,\n"
    )
    replacement = (
        "                            max_tokens=agent.max_tokens,\n"
        "                            reasoning_config=agent.reasoning_config,\n"
        "                            started_at=api_start_time,\n"
    )
    if anchor not in text:
        raise SystemExit(f"Hermes pre_api_request hook anchor not found: {path}")
    path.write_text(text.replace(anchor, replacement, 1), encoding="utf-8")
    print("Patched Hermes pre_api_request reasoning_config hook")
else:
    print("Hermes pre_api_request reasoning_config hook already present")
PY

# Register the staged source directly with deterministic metadata. This uses
# only the locked venv's Python standard library: no build backend, package
# resolver, network access, or ambient setuptools/wheel version participates.
"$VENV_PY" - "$PKG_DIR" <<'PY'
from pathlib import Path
import importlib.metadata as md
import os
import shutil
import sys
import sysconfig
import tempfile

package_root = Path(sys.argv[1]).resolve(strict=True)
package_init = package_root / "latitude_telemetry_hermes" / "__init__.py"
if not package_init.is_file():
    raise SystemExit(f"telemetry package missing: {package_init}")

purelib = Path(sysconfig.get_paths()["purelib"]).resolve()
purelib.mkdir(parents=True, exist_ok=True)
version = "0.1.0+revenuepartner.1"
dist_info = purelib / f"latitude_telemetry_hermes-{version}.dist-info"
stage_root = Path(tempfile.mkdtemp(prefix=".latitude-telemetry-stage-", dir=purelib))
staged_dist_info = stage_root / dist_info.name
staged_dist_info.mkdir(mode=0o755)


def atomic_text(path: Path, content: str) -> None:
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as handle:
        handle.write(content)
        handle.flush()
        os.fsync(handle.fileno())
        temp_path = Path(handle.name)
    os.chmod(temp_path, 0o644)
    os.replace(temp_path, path)


atomic_text(purelib / "latitude_telemetry_hermes.pth", f"{package_root}\n")
atomic_text(
    staged_dist_info / "METADATA",
    "Metadata-Version: 2.1\n"
    "Name: latitude-telemetry-hermes\n"
    f"Version: {version}\n"
    "Summary: Hermes telemetry integration for Revenue Partner\n"
    "Requires-Python: >=3.11,<3.15\n"
    "Requires-Dist: certifi (>=2024.2.2)\n\n",
)
atomic_text(
    staged_dist_info / "WHEEL",
    "Wheel-Version: 1.0\nGenerator: revenue-partner-stdlib-registration\n"
    "Root-Is-Purelib: true\nTag: py3-none-any\n",
)
atomic_text(
    staged_dist_info / "entry_points.txt",
    "[hermes_agent.plugins]\nlatitude = latitude_telemetry_hermes\n",
)
atomic_text(staged_dist_info / "INSTALLER", "revenue-partner-stdlib-registration\n")

backup = purelib / f".{dist_info.name}.previous"
if backup.exists():
    shutil.rmtree(backup)
if dist_info.exists():
    os.replace(dist_info, backup)
try:
    os.replace(staged_dist_info, dist_info)
except BaseException:
    if backup.exists() and not dist_info.exists():
        os.replace(backup, dist_info)
    raise
else:
    if backup.exists():
        shutil.rmtree(backup)
finally:
    shutil.rmtree(stage_root, ignore_errors=True)

for stale in purelib.glob("latitude_telemetry_hermes-*.dist-info"):
    if stale != dist_info:
        shutil.rmtree(stale)

print("registered", purelib / "latitude_telemetry_hermes.pth")
print("metadata", dist_info)
PY

"$VENV_PY" - <<'PY'
import importlib.metadata as md
import pathlib
import latitude_telemetry_hermes

version = md.version("latitude-telemetry-hermes")
if version != "0.1.0+revenuepartner.1":
    raise SystemExit(f"unexpected telemetry version: {version}")
entry_points = md.entry_points()
plugins = tuple(entry_points.select(group="hermes_agent.plugins", name="latitude"))
if len(plugins) != 1 or plugins[0].value != "latitude_telemetry_hermes":
    raise SystemExit(f"unexpected telemetry entry point: {plugins}")
plugins[0].load()
print("latitude-telemetry-hermes", version)
print("module_file", pathlib.Path(latitude_telemetry_hermes.__file__).resolve())
PY

if [[ -f "$VALIDATE" ]]; then
  python3 "$VALIDATE"
fi
