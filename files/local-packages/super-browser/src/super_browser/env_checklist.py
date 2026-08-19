from __future__ import annotations

import os
from typing import Any

from .providers import PLANNING_ONLY_PROVIDERS, PROVIDERS, provider_readiness
from .redaction import redact


GLOBAL_ENV = [
    "SUPER_BROWSER_STATE_DIR",
    "SUPER_BROWSER_REPO_ROOT",
]

ENV_PURPOSES = {
    "SUPER_BROWSER_REPO_ROOT": "Optional path to the baked Super Browser bundle for MCP resources.",
    "SUPER_BROWSER_STATE_DIR": "Optional durable run-state directory.",
}


def environment_checklist() -> dict[str, Any]:
    readiness_rows = {row["name"]: row for row in provider_readiness()}
    provider_rows = [
        _provider_row(name, readiness_rows[name])
        for name in PROVIDERS
        if name in readiness_rows
    ]
    global_env = [_env_item(name) for name in GLOBAL_ENV]
    return redact(
        {
            "type": "super_browser_env_checklist",
            "status": "local_lanes_only",
            "values_included": False,
            "value_policy": (
                "No hosted-provider credential is required or accepted for execution in this image. "
                "Environment values are omitted."
            ),
            "missing_required_env": [],
            "missing_optional_env": [],
            "providers": provider_rows,
            "global_env": global_env,
            "all_env": global_env,
            "commands": [
                "super-browser env-checklist",
                "super-browser doctor",
                "super-browser live-test --provider local",
                "super-browser live-test --provider fixtures",
                "super-browser bundle-manifest",
            ],
            "provider_signup": [],
            "notes": [
                "Only exact allowlisted local Playwright fixtures and bounded direct public-IP-literal raw HTTP are conditionally executable lanes; public Playwright navigation is non-executable.",
                "Airtop, Browser Use, Browserbase, Hyperbrowser, Orgo, and Steel remain planning-only regardless of credentials.",
                "Task, named, and environment proxy routes are disabled.",
                "External writes, authenticated profiles, unknown intent, and production work remain non-executable.",
            ],
        }
    )


def _provider_row(provider_name: str, readiness: dict[str, Any]) -> dict[str, Any]:
    provider = PROVIDERS[provider_name]
    planning_only = provider_name in PLANNING_ONLY_PROVIDERS
    return {
        "name": provider_name,
        "display_name": provider.display_name,
        "stability": provider.stability,
        "required_env": [],
        "optional_env": [],
        "missing_required_env": [],
        "missing_optional_env": [],
        "readiness_status": readiness.get("readiness_status"),
        "usable_now": False if planning_only else readiness.get("usable_now"),
        "production_ready": False,
        "production_ready_scope": "planning_only" if planning_only else readiness.get("production_ready_scope"),
        "supported_live_workflow_classes": [] if planning_only else list(readiness.get("supported_live_workflow_classes") or []),
        "live_test_commands": [],
        "next_action": (
            "Planning/reference only; no credential or setup action can enable execution in this image."
            if planning_only
            else readiness.get("next_action")
        ),
    }


def _env_item(name: str) -> dict[str, Any]:
    return {
        "name": name,
        "scope": "global",
        "provider": None,
        "required": False,
        "configured": bool(os.environ.get(name)),
        "sensitive": False,
        "purpose": ENV_PURPOSES[name],
        "value_included": False,
    }
