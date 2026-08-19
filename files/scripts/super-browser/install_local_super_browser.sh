#!/usr/bin/env bash
set -euo pipefail

PACKAGE_ROOT=${1:?usage: install_local_super_browser.sh PACKAGE_ROOT VENV_PYTHON}
VENV_PY=${2:?usage: install_local_super_browser.sh PACKAGE_ROOT VENV_PYTHON}

"$VENV_PY" - "$PACKAGE_ROOT" <<'PY'
from __future__ import annotations

import importlib
import importlib.metadata
import os
from pathlib import Path
import sys
import sysconfig
import tempfile
import tomllib

package_root = Path(sys.argv[1]).resolve(strict=True)
source_root = (package_root / "src").resolve(strict=True)
module_init = source_root / "super_browser/__init__.py"
metadata_file = package_root / "PACKAGE_METADATA.toml"
if not module_init.is_file() or not metadata_file.is_file():
    raise SystemExit("invalid staged Super Browser package root")

project = tomllib.loads(metadata_file.read_text(encoding="utf-8"))
if project.get("name") != "super-browser" or project.get("entry_point") != "super_browser.cli:main":
    raise SystemExit("unexpected Super Browser distribution name")
version = str(project["version"])
if not version or any(ch not in "0123456789." for ch in version):
    raise SystemExit("unexpected Super Browser version")

purelib = Path(sysconfig.get_path("purelib")).resolve()
scripts = Path(sysconfig.get_path("scripts")).resolve()
purelib.mkdir(parents=True, exist_ok=True)
scripts.mkdir(parents=True, exist_ok=True)

dist_info = purelib / f"super_browser-{version}.dist-info"
dist_info.mkdir(mode=0o755, parents=True, exist_ok=True)


def atomic_write(path: Path, content: str, mode: int = 0o644) -> None:
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temporary, mode)
        os.replace(temporary, path)
    finally:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass


atomic_write(purelib / "super_browser_local.pth", f"{source_root}\n")
atomic_write(
    dist_info / "METADATA",
    "Metadata-Version: 2.3\n"
    "Name: super-browser\n"
    f"Version: {version}\n"
    "Summary: Local browser orchestration router for agents\n",
)
atomic_write(
    dist_info / "WHEEL",
    "Wheel-Version: 1.0\n"
    "Generator: revenue-partner-offline-registrar\n"
    "Root-Is-Purelib: true\n"
    "Tag: py3-none-any\n",
)
atomic_write(dist_info / "entry_points.txt", "[console_scripts]\nsuper-browser = super_browser.cli:main\n")
atomic_write(dist_info / "INSTALLER", "revenue-partner-offline-registrar\n")
atomic_write(dist_info / "RECORD", "")
atomic_write(
    scripts / "super-browser",
    f"#!{sys.executable}\n"
    "from super_browser.cli import main\n"
    "if __name__ == '__main__':\n"
    "    raise SystemExit(main())\n",
    0o755,
)

if str(source_root) not in sys.path:
    sys.path.insert(0, str(source_root))
importlib.invalidate_caches()
module = importlib.import_module("super_browser")
if not Path(module.__file__).resolve().is_relative_to(source_root):
    raise SystemExit("Super Browser imported from an unexpected path")
if importlib.metadata.version("super-browser") != version:
    raise SystemExit("Super Browser distribution metadata mismatch")
entry_points = [
    entry
    for entry in importlib.metadata.entry_points(group="console_scripts")
    if entry.name == "super-browser" and entry.dist.name == "super-browser"
]
if len(entry_points) != 1 or entry_points[0].load().__module__ != "super_browser.cli":
    raise SystemExit("Super Browser console entry point verification failed")
print(f"super_browser_registered {version} {source_root}")
PY
