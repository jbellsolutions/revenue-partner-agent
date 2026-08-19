"""latitude — Hermes plugin that streams sessions to Latitude as OTLP traces.

Traces Hermes conversations, LLM calls, and tool usage to Latitude. One Hermes
turn becomes one trace: an ``interaction`` root span with an ``llm_request``
child per model call and a ``tool_execution`` child per tool call. Spans follow
Latitude's GenAI semantic conventions (``gen_ai.*``) so they render natively in
the Latitude trace viewer.

Activation is handled by the Hermes plugin system — this plugin only loads when
enabled via ``hermes plugins enable latitude``. At runtime it also
requires credentials; if they're missing the hooks are inert (fail-open: a
telemetry error never affects the agent).

Required env vars (set in your environment or ``~/.hermes/.env``):
  LATITUDE_API_KEY   - Latitude API key
  LATITUDE_PROJECT   - Latitude project slug (or LATITUDE_PROJECT_SLUG)

The ingest origin is fixed to ``https://ingest.latitude.so`` in this image and
cannot be changed by environment values.

Optional env vars:
  LATITUDE_USER_ID   - stable end-user id attached to each trace
  LATITUDE_USER_EMAIL - end-user email attached to each trace, when known
  LATITUDE_USER_NAME - end-user display name attached to each trace, when known
  LATITUDE_HERMES_ALLOW_CONTENT - explicit "true" opt-in to export recursively
                                  redacted prompt/response/tool content
  LATITUDE_NO_CONTENT - legacy force-off switch; "true" always disables content
  LATITUDE_HERMES_PROFILE - Hermes profile name, default: HERMES_PROFILE/default
  LATITUDE_HERMES_APPROVAL_MODE - operator approval mode marker, when known
  LATITUDE_DEBUG     - "true" for verbose logging
"""

from __future__ import annotations

import logging
import os
import ssl
import threading
from typing import Any, Dict, Optional


def _ssl_context() -> ssl.SSLContext:
    """Verified TLS context, preferring certifi's CA bundle.

    Some Python installs (notably python.org builds on macOS) ship without a
    usable system CA store, so a plain ``urlopen`` to https can raise
    CERTIFICATE_VERIFY_FAILED. Hermes's HTTP stack already depends on certifi,
    so use it when available; otherwise fall back to the system default.
    """
    try:
        import certifi

        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        return ssl.create_default_context()


_SSL_CONTEXT = _ssl_context()

logger = logging.getLogger(__name__)

SCOPE_NAME = "latitude-telemetry-hermes"
PKG_VERSION = "0.1.0+revenuepartner.1"
LATITUDE_INGEST_ORIGIN = "https://ingest.latitude.so"

# Bound on live trace state, so turns that never reach a clean finish
# (interrupted / tool-only final step) can't leak forever.
_MAX_RUNS = 256


# ─────────────────────────── config ────────────────────────────────────────


def _env(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


_CONFIG: Optional[Dict[str, Any]] = None
_CONFIG_LOCK = threading.Lock()


def _load_config() -> Dict[str, Any]:
    api_key = _env("LATITUDE_API_KEY")
    project = _env("LATITUDE_PROJECT") or _env("LATITUDE_PROJECT_SLUG")

    enabled_flag = _env("LATITUDE_HERMES_TELEMETRY_ENABLED") or _env("LATITUDE_TELEMETRY_ENABLED")
    enabled = enabled_flag.lower() not in {"0", "false", "no"} if enabled_flag else True
    allow_flag = _env("LATITUDE_HERMES_ALLOW_CONTENT") or _env("LATITUDE_ALLOW_CONTENT")
    no_content = _env("LATITUDE_HERMES_NO_CONTENT") or _env("LATITUDE_NO_CONTENT")
    allow_content = allow_flag.lower() in {"1", "true", "yes"}
    if no_content.lower() in {"1", "true", "yes"}:
        allow_content = False
    profile = _env("LATITUDE_HERMES_PROFILE") or _env("HERMES_PROFILE") or "default"
    return {
        "api_key": api_key,
        "project": project,
        "base_url": LATITUDE_INGEST_ORIGIN,
        "enabled": bool(enabled and api_key and project),
        "allow_content": allow_content,
        "capture_level": "redacted_content_opt_in" if allow_content else "redacted_summary",
        "profile": profile,
        "platform": _env("LATITUDE_HERMES_PLATFORM") or _env("HERMES_PLATFORM"),
        "approval_mode": _env("LATITUDE_HERMES_APPROVAL_MODE") or _env("HERMES_APPROVAL_MODE"),
        "debug": _env("LATITUDE_DEBUG").lower() in {"1", "true"},
        "user_id": _env("LATITUDE_USER_ID") or _env("HERMES_USER_ID"),
        "user_email": _env("LATITUDE_USER_EMAIL"),
        "user_name": _env("LATITUDE_USER_NAME"),
    }


def _config() -> Dict[str, Any]:
    global _CONFIG
    if _CONFIG is None:
        with _CONFIG_LOCK:
            if _CONFIG is None:
                _CONFIG = _load_config()
    return _CONFIG


def _debug(message: str) -> None:
    if _config().get("debug"):
        logger.info("Latitude tracing: %s", message)
