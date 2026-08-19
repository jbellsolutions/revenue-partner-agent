from __future__ import annotations

import os
import threading
import unittest
from typing import Any, cast
from unittest import mock

from latitude_telemetry_hermes import config, hooks, transport


class TelemetrySecurityTests(unittest.TestCase):
    def setUp(self) -> None:
        hooks._REGISTERED_CONTEXT_IDS.clear()

    def test_environment_cannot_override_canonical_ingest_origin(self) -> None:
        with mock.patch.dict(
            os.environ,
            {
                "LATITUDE_BASE_URL": "https://attacker.invalid",
                "LATITUDE_INGEST_URL": "https://attacker.invalid/v1/traces",
            },
            clear=False,
        ):
            loaded = config._load_config()
        self.assertEqual(loaded["base_url"], config.LATITUDE_INGEST_ORIGIN)
        self.assertEqual(loaded["base_url"], "https://ingest.latitude.so")

    def test_transport_disables_proxies_and_redirects(self) -> None:
        self.assertEqual(getattr(transport._NO_PROXY_HANDLER, "proxies", None), {})
        handlers = getattr(transport._OPENER, "handlers", [])
        proxy_handlers = [handler for handler in handlers if isinstance(handler, transport._urlreq.ProxyHandler)]
        redirect_handlers = [handler for handler in handlers if isinstance(handler, transport._urlreq.HTTPRedirectHandler)]
        self.assertEqual(proxy_handlers, [])
        self.assertEqual(redirect_handlers, [transport._NO_REDIRECT_HANDLER])
        self.assertIsNone(
            transport._NO_REDIRECT_HANDLER.redirect_request(
                cast(Any, None),
                cast(Any, None),
                302,
                "redirect",
                cast(Any, {}),
                "https://attacker.invalid",
            )
        )

    def test_registration_is_repeat_safe_and_thread_safe(self) -> None:
        class Context:
            def __init__(self) -> None:
                self.calls: list[tuple[str, object]] = []

            def register_hook(self, name: str, callback: object) -> None:
                self.calls.append((name, callback))

        ctx = Context()
        threads = [threading.Thread(target=hooks.register, args=(ctx,)) for _ in range(12)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        hooks.register(ctx)
        self.assertEqual(len(ctx.calls), 6)
        self.assertEqual(len({name for name, _ in ctx.calls}), 6)


if __name__ == "__main__":
    unittest.main()
