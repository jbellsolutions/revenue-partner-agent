from __future__ import annotations

import os
import sys
from pathlib import Path


IGNORED_BUNDLE_NAMES = {
    ".coverage",
    ".DS_Store",
    ".mypy_cache",
    ".nox",
    ".pytest_cache",
    ".ruff_cache",
    ".super-browser",
    ".tox",
    ".venv",
    ".git",
    "__pycache__",
    "build",
    "dist",
    "env",
    "htmlcov",
    "node_modules",
    "venv",
}

IGNORED_BUNDLE_PATTERNS = {
    ".env",
    ".env.*",
    "*.db",
    "*.log",
    "*.pyc",
    "*.pyo",
    "*.sqlite",
    "*.sqlite3",
    "coverage.xml",
}


def discover_repo_root(start: str | Path | None = None) -> Path | None:
    if start is None:
        start = Path(__file__).resolve()
    configured = os.environ.get("SUPER_BROWSER_REPO_ROOT")
    if configured:
        candidate = Path(configured).expanduser().resolve()
        if _looks_like_super_browser_root(candidate):
            return candidate
    discovered = _discover_repo_root(Path(start).expanduser().resolve())
    return discovered or _packaged_asset_root_or_none()


def is_super_browser_root(path: str | Path) -> bool:
    return _looks_like_super_browser_root(Path(path).expanduser().resolve())


def _discover_repo_root(start: Path) -> Path | None:
    candidates = [start if start.is_dir() else start.parent, *start.parents]
    for candidate in candidates:
        if _looks_like_super_browser_root(candidate):
            return candidate.resolve()
    return None


def _looks_like_super_browser_root(path: Path) -> bool:
    return (
        (path / "SKILL.md").is_file()
        and (path / "README.md").is_file()
        and (path / "skills").is_dir()
        and (path / "references").is_dir()
        and (path / "mcp" / "super-browser-server").is_file()
        and (path / "scripts" / "super-browser").is_file()
    )


def _packaged_asset_root_or_none() -> Path | None:
    for candidate in (
        Path(sys.prefix) / "share" / "super-browser",
        Path(sys.base_prefix) / "share" / "super-browser",
    ):
        if _looks_like_super_browser_root(candidate):
            return candidate.resolve()
    return None
