#!/usr/bin/env python3
"""Syntax-check every tracked shell program and assembled template shell body."""

from __future__ import annotations

from contextlib import redirect_stdout
import importlib.util
import io
import os
from pathlib import Path
import subprocess
import sys


ROOT = Path.cwd()
GIT = os.environ.get("REVENUE_PARTNER_VERIFY_GIT", "/usr/bin/git")


def tracked_paths() -> list[Path]:
    if not Path(GIT).is_absolute() or not os.access(GIT, os.X_OK):
        raise RuntimeError("trusted absolute Git executable unavailable")
    result = subprocess.run(
        [GIT, "ls-files", "-z"],
        check=True,
        capture_output=True,
    )
    return [Path(raw.decode()) for raw in result.stdout.split(b"\0") if raw]


def is_shell_program(path: Path) -> bool:
    if not path.is_file():
        return False
    with path.open("rb") as handle:
        first = handle.readline(256).decode("utf-8", errors="ignore").strip()
    if not first.startswith("#!"):
        return False
    interpreter = first[2:].strip().split()
    if not interpreter:
        return False
    executable = Path(interpreter[0]).name
    if executable in {"bash", "sh"}:
        return True
    return executable == "env" and len(interpreter) > 1 and interpreter[1] in {"bash", "sh"}


def embedded_template_programs() -> list[tuple[str, str]]:
    builder_path = ROOT / "build_template.py"
    spec = importlib.util.spec_from_file_location("shell_check_build_template", builder_path)
    if not spec or not spec.loader:
        raise RuntimeError(f"cannot load {builder_path}")
    module = importlib.util.module_from_spec(spec)
    with redirect_stdout(io.StringIO()):
        spec.loader.exec_module(module)
    template = module.template
    programs: list[tuple[str, str]] = []
    for index, app in enumerate(template.get("apps", [])):
        install = app.get("install")
        if isinstance(install, str):
            programs.append((f"template.apps[{index}].install", install))
    for name, body in template.get("hooks", {}).items():
        if isinstance(body, str):
            programs.append((f"template.hooks.{name}", body))
    return programs


def validate_program(label: str, body: str) -> str | None:
    result = subprocess.run(
        ["bash", "-n"],
        input=body,
        text=True,
        capture_output=True,
    )
    if result.returncode:
        return f"{label}: {result.stderr.strip() or 'bash -n failed'}"
    return None


def main() -> int:
    programs = [(str(path), path.read_text()) for path in tracked_paths() if is_shell_program(path)]
    failures: list[str] = []
    try:
        programs.extend(embedded_template_programs())
    except Exception as exc:
        failures.append(f"build_template.py: unable to inspect embedded shell: {exc}")
    for label, body in programs:
        failure = validate_program(label, body)
        if failure:
            failures.append(failure)
    if failures:
        print("\n".join(failures), file=sys.stderr)
        return 1
    print(f"shell_syntax_ok {len(programs)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
