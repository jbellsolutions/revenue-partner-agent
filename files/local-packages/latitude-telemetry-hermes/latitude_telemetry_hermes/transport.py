from __future__ import annotations

import json
import threading
from typing import Any, Dict, Optional
from urllib import request as _urlreq

from .config import _SSL_CONTEXT, _config, _debug


class _NoRedirect(_urlreq.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        del req, fp, code, msg, headers, newurl
        return None


_NO_PROXY_HANDLER = _urlreq.ProxyHandler({})
_NO_REDIRECT_HANDLER = _NoRedirect()
_OPENER = _urlreq.build_opener(
    _NO_PROXY_HANDLER,
    _urlreq.HTTPSHandler(context=_SSL_CONTEXT),
    _NO_REDIRECT_HANDLER,
)


def _post_traces(payload: Dict[str, Any]) -> None:
    cfg = _config()
    url = cfg["base_url"].rstrip("/") + "/v1/traces"
    data = json.dumps(payload).encode("utf-8")
    req = _urlreq.Request(
        url,
        data=data,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {cfg['api_key']}",
            "X-Latitude-Project": cfg["project"],
        },
    )
    try:
        with _OPENER.open(req, timeout=10) as resp:  # exact canonical HTTPS origin; redirects/proxies disabled
            _debug(f"ingest HTTP {resp.status}")
    except _urlreq.HTTPError as exc:
        with exc:
            _debug(f"ingest failed: {exc}")
    except Exception as exc:  # fail-open
        _debug(f"ingest failed: {exc}")


def _ship(result: Optional[Dict[str, Any]]) -> None:
    if not result:
        return
    # Use a non-daemon thread so short-lived `hermes chat -q` processes do not
    # exit before the OTLP POST has been attempted.  `_post_traces` is
    # fail-open and has a bounded timeout, so telemetry can delay process exit
    # briefly but cannot break the agent.
    threading.Thread(target=_post_traces, args=(result,), daemon=False).start()
