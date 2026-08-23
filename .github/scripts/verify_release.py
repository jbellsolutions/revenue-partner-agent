#!/usr/bin/env python3
"""Run the exact Revenue Partner release matrix used by CI and operators."""

from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[2]
LOCK = ROOT / "requirements-ci.lock"
LOCKED_CHILD = ROOT / ".github/scripts/_verify_release_locked.py"
GIT = os.environ.get("REVENUE_PARTNER_VERIFY_GIT", "")
STEP_NAMES = (
    "pip --require-hashes requirements-ci.lock",
    "candidate index YAML parse",
    "candidate skill frontmatter parse",
    "candidate index credential scan",
    "exact candidate tree parity",
    "markdown links/assets",
    "revenue partner tests",
    "latitude telemetry tests",
    "packaged super browser verifier",
    "agentphone tests",

    "python compile",
    "tracked and embedded shell syntax",
    "git diff checks",
    "template schema assembly",
    "assembled hosted-attach verifier",
)


def run(command: list[str], label: str, *, env: dict[str, str] | None = None) -> None:
    print(f"==> {label}", flush=True)
    subprocess.run(command, cwd=ROOT, check=True, env=env)


def git_text(*args: str) -> str:
    if not Path(GIT).is_absolute() or not os.access(GIT, os.X_OK):
        raise RuntimeError("trusted absolute Git executable missing from launcher environment")
    return subprocess.check_output([GIT, *args], cwd=ROOT, text=True).strip()


def assert_exact_candidate_tree() -> None:
    expected = os.environ.get("REVENUE_PARTNER_CANDIDATE_TREE", "")
    if not re_full_tree(expected):
        raise RuntimeError("missing exact candidate-tree identity from trusted launcher")
    actual = git_text("write-tree")
    if actual != expected:
        raise RuntimeError("candidate index tree changed during verification")
    if subprocess.run([GIT, "diff", "--quiet", "--"], cwd=ROOT).returncode != 0:
        raise RuntimeError("tracked worktree bytes differ from exact candidate index")
    if git_text("ls-files", "--others", "--exclude-standard"):
        raise RuntimeError("untracked non-ignored files exist in exact candidate export")


def re_full_tree(value: str) -> bool:
    return len(value) == 40 and all(char in "0123456789abcdef" for char in value)


def clean_generated_state() -> None:

    for cache in ROOT.rglob("__pycache__"):
        if ".git" not in cache.parts:
            shutil.rmtree(cache, ignore_errors=True)


def run_locked_matrix() -> None:
    python = sys.executable
    assert_exact_candidate_tree()
    run([python, ".github/scripts/check_candidate_yaml.py"], "candidate index YAML parse")
    run([python, ".github/scripts/check_skill_frontmatter.py"], "candidate skill frontmatter parse")
    run([python, ".github/scripts/check_candidate_credentials.py"], "candidate index credential scan")
    run([python, ".github/scripts/check_markdown_links.py"], "markdown links/assets")
    run([python, "-m", "unittest", "discover", "-s", "tests", "-v"], "revenue partner tests")
    latitude_env = os.environ.copy()
    latitude_env["PYTHONPATH"] = str(ROOT / "files/local-packages/latitude-telemetry-hermes")
    run(
        [python, "-m", "unittest", "discover", "-s", "files/local-packages/latitude-telemetry-hermes/tests", "-v"],
        "latitude telemetry tests",
        env=latitude_env,
    )
    run(["bash", "files/local-packages/super-browser/scripts/verify-super-browser"], "packaged super browser verifier")
    run([python, "files/agentphone-bridge/test_event_ordering.py"], "agentphone tests")

    run(
        [python, "-m", "compileall", "-q", "build_template.py", "tests", "files", ".github/scripts"],
        "python compile",
    )
    run([python, ".github/scripts/check_shell_syntax.py"], "tracked and embedded shell syntax")
    assert_exact_candidate_tree()
    run([GIT, "diff", "--check"], "working-tree diff check")
    run([GIT, "diff", "--cached", "--check"], "staged diff check")
    run([python, "build_template.py"], "template schema assembly")
    run([python, ".github/scripts/verify_assembled_super_browser.py"], "assembled hosted-attach verifier")
    assert_exact_candidate_tree()


def bootstrap_locked_environment() -> int:
    with tempfile.TemporaryDirectory(prefix="revenue-partner-verify-") as temp_dir:
        temp_root = Path(temp_dir).resolve()
        venv = temp_root / "venv"
        bootstrap_env = os.environ.copy()
        for name in ("PYTHONHOME", "PYTHONPATH", "VIRTUAL_ENV"):
            bootstrap_env.pop(name, None)
        bootstrap_env["PYTHONNOUSERSITE"] = "1"
        subprocess.run([sys.executable, "-m", "venv", str(venv)], cwd=ROOT, env=bootstrap_env, check=True)
        python = venv / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
        print("==> pip --require-hashes requirements-ci.lock", flush=True)
        subprocess.run(
            [
                str(python),
                "-m",
                "pip",
                "install",
                "--disable-pip-version-check",
                "--require-hashes",
                "-r",
                str(LOCK),
            ],
            cwd=ROOT,
            env=bootstrap_env,
            check=True,
        )
        env = bootstrap_env.copy()
        env["PATH"] = os.pathsep.join([str(python.parent), env.get("PATH", "")])
        if os.name != "posix":
            print("locked verifier requires inherited POSIX file-descriptor authority", file=sys.stderr)
            return 78
        read_fd, write_fd = os.pipe()
        env.update(
            {
                "REVENUE_PARTNER_VERIFY_AUTH_FD": str(read_fd),
                "REVENUE_PARTNER_VERIFY_VENV": str(venv),
                "REVENUE_PARTNER_VERIFY_PARENT_PID": str(os.getpid()),
            }
        )
        try:
            child = subprocess.Popen(
                [str(python), "-I", "-s", str(LOCKED_CHILD)],
                cwd=ROOT,
                env=env,
                pass_fds=(read_fd,),
            )
            os.close(read_fd)
            read_fd = -1
            try:
                os.write(write_fd, os.urandom(32))
            finally:
                os.close(write_fd)
                write_fd = -1
            result_code = child.wait()
        finally:
            if read_fd >= 0:
                os.close(read_fd)
            if write_fd >= 0:
                os.close(write_fd)
        if result_code == 0:
            print("release_verification_ok", flush=True)
        return result_code


def main() -> int:
    if not sys.flags.isolated or not sys.flags.ignore_environment or not sys.flags.no_user_site:
        print("usage: invoke the canonical .github/scripts/verify_release launcher", file=sys.stderr)
        return 2
    if sys.argv[1:] == ["--list"]:
        print("\n".join(STEP_NAMES))
        return 0
    if sys.argv[1:]:
        print("usage: verify_release.py [--list]", file=sys.stderr)
        return 2
    return bootstrap_locked_environment()


if __name__ == "__main__":
    raise SystemExit(main())
