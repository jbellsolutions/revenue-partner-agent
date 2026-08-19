from __future__ import annotations

from typing import Any

from .setup_helpers import discover_repo_root, is_super_browser_root


def launch_setup(*, client: str | None = None) -> dict[str, Any]:
    """Describe the baked Revenue Partner runtime without mutating it."""
    from .env_checklist import environment_checklist

    root = discover_repo_root()
    repo_path = str(root) if root else None
    steps = [
        {
            "step": 1,
            "title": "Use the baked runtime",
            "natural_language": (
                "Use the Super Browser package and browser dependencies already baked from committed locks. "
                "Do not clone another checkout or install packages into this image."
            ),
            "commands": [],
            "done": bool(repo_path and is_super_browser_root(repo_path)),
        },
        {
            "step": 2,
            "title": "Confirm enforceable local lanes",
            "natural_language": (
                "Only exact allowlisted local Playwright fixtures and bounded direct public-IP-literal raw HTTP reads can execute. "
                "Hosted providers remain planning-only regardless of credentials."
            ),
            "commands": [],
            "done": None,
        },
        {
            "step": 3,
            "title": "Check readiness",
            "natural_language": "Use the baked CLI to report local-lane readiness and planning-only provider blockers.",
            "commands": ["super-browser doctor"],
            "done": None,
        },
        {
            "step": 4,
            "title": "Verify read-only fixtures",
            "natural_language": "Run only local fixture verification before trusting a read-only lane.",
            "commands": ["super-browser live-test --provider fixtures"],
            "done": None,
        },
        {
            "step": 5,
            "title": "Respect the production hard stop",
            "natural_language": (
                "Approval-required work remains awaiting_approval. This image has no local approval or "
                "production-resume path; enabling one requires reviewed operator infrastructure and a rebuilt release."
            ),
            "commands": [],
            "done": None,
        },
    ]
    return {
        "type": "super_browser_setup_walkthrough",
        "welcome": (
            "Revenue Partner includes a baked local Super Browser runtime for council-based read-only research. "
            "Use committed locks and the verified image; do not replace the runtime from an unpinned source. "
            "Approval-required production work remains non-executable."
        ),
        "repo": "https://github.com/jbellsolutions/super-browser",
        "docs": {
            "quickstart": "docs/agent-quickstart.md",
            "walkthrough": "docs/setup-walkthrough.md",
        },
        "repo_root": repo_path,
        "client_hint": client,
        "provider_signup": [],
        "env_checklist": environment_checklist(),
        "steps": steps,
        "one_liner_for_agent": (
            "Use the baked Super Browser MCP/CLI, run the five-round council, execute read-only work only, "
            "and leave every approval-required request stopped."
        ),
    }
