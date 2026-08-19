import hashlib
import hmac
import http.client
import importlib.util
import json
import stat
import tempfile
import threading
import time
import unittest
import urllib.request
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("agentphone_bridge.py")
spec = importlib.util.spec_from_file_location("agentphone_bridge_under_test", MODULE_PATH)
bridge = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(bridge)


class EventOrderingTests(unittest.TestCase):
    def test_group_event_has_no_authorized_outbound_target(self):
        payload = {
            "event": "agent.message",
            "channel": "imessage",
            "data": {
                "from": "+15555550123",
                "direction": "inbound",
                "message": "private request",
                "group": {"groupId": "unauthorized-group"},
            },
        }
        fields = bridge.extract_event_fields(payload)

        self.assertTrue(fields["is_group"])
        self.assertEqual(fields["reply_to"], "+15555550123")
        self.assertEqual(bridge.authorized_reply_target(fields, {"+15555550123"}), "")

    def test_signed_group_webhook_is_rejected_before_job_creation(self):
        with tempfile.TemporaryDirectory() as tmp:
            original = (bridge.CONFIG, bridge.WEBHOOK_SECRET, bridge.BRIDGE_DIR, bridge.EVENTS_LOG, bridge.start_conversation_job)
            secret = "test-webhook-secret"
            started = []
            setattr(bridge, "CONFIG", {"AGENTPHONE_ALLOWED_SENDERS": "+15555550123"})
            setattr(bridge, "WEBHOOK_SECRET", secret)
            setattr(bridge, "BRIDGE_DIR", Path(tmp))
            setattr(bridge, "EVENTS_LOG", Path(tmp) / "events.log")
            setattr(bridge, "start_conversation_job", lambda *args: started.append(args))
            server = bridge.BridgeHTTPServer(("127.0.0.1", 0), bridge.Handler)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            payload = {
                "event": "agent.message",
                "channel": "imessage",
                "data": {
                    "conversationId": "conv-group",
                    "from": "+15555550123",
                    "direction": "inbound",
                    "message": "private request",
                    "messageId": "msg-group",
                    "receivedAt": "2026-07-10T00:27:04.656000Z",
                    "group": {"groupId": "unauthorized-group"},
                },
            }
            raw = json.dumps(payload).encode()
            signature_ts = str(int(time.time()))
            signature = "sha256=" + hmac.new(
                secret.encode(), signature_ts.encode() + b"." + raw, hashlib.sha256
            ).hexdigest()
            request = urllib.request.Request(
                f"http://127.0.0.1:{server.server_port}/hooks/agentphone",
                data=raw,
                method="POST",
                headers={
                    "Content-Type": "application/json",
                    "X-Webhook-Timestamp": signature_ts,
                    "X-Webhook-Signature": signature,
                },
            )
            try:
                with urllib.request.urlopen(request, timeout=5) as response:
                    body = json.loads(response.read())
                self.assertEqual(body["ignored"], "group audience not allowlisted")
                self.assertEqual(started, [])
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=2)
                for name, value in zip(("CONFIG", "WEBHOOK_SECRET", "BRIDGE_DIR", "EVENTS_LOG", "start_conversation_job"), original):
                    setattr(bridge, name, value)

    def test_direct_sender_binds_outbound_target_to_allowlisted_sender(self):
        fields = bridge.extract_event_fields({
            "event": "agent.message",
            "channel": "sms",
            "data": {"from": "+1 (555) 555-0123", "direction": "inbound", "message": "hello"},
        })

        self.assertFalse(fields["is_group"])
        self.assertEqual(bridge.authorized_reply_target(fields, {"+15555550123"}), "+15555550123")

    def test_agentphone_api_base_requires_exact_approved_https_origin(self):
        self.assertEqual(bridge.validate_agentphone_base_url("https://api.agentphone.ai/"), bridge.API_BASE)
        for invalid in (
            "http://api.agentphone.ai",
            "https://evil.example",
            "https://api.agentphone.ai.evil.example",
            "https://user:pass@api.agentphone.ai",
            "https://api.agentphone.ai:8443",
            "https://api.agentphone.ai/v1",
            "https://api.agentphone.ai?next=https://evil.example",
        ):
            with self.subTest(invalid=invalid):
                with self.assertRaisesRegex(ValueError, "exact approved HTTPS origin"):
                    bridge.validate_agentphone_base_url(invalid)


    def test_agentphone_api_redirects_are_disabled(self):
        handler = bridge.NoRedirectHandler()
        request = urllib.request.Request("https://api.agentphone.ai/v1/agents")
        self.assertIsNone(
            handler.redirect_request(
                request,
                None,
                302,
                "Found",
                {},
                "https://evil.example/steal",
            )
        )

    def test_agentphone_network_execution_is_immutable_hard_stop(self):
        self.assertFalse(bridge.AGENTPHONE_EXECUTION_AVAILABLE)
        for call in (
            lambda: bridge.api_request("POST", "/v1/messages", {"to": "+15555550123"}),
            bridge.start_cloudflared,
            lambda: bridge.register_agent_webhook("https://public.example"),
            lambda: bridge.start_conversation_job({"conversation_id": "c"}, "+15555550123"),
            lambda: bridge.run_hermes_and_reply({}, {"sender": "+15555550123"}, "web"),
            lambda: bridge.send_agentphone_message("+15555550123", "test"),
            lambda: bridge.send_agentphone_reply("+15555550123", "test"),
            lambda: bridge.send_typing("conversation"),
            bridge.start_http_server,
        ):
            with self.assertRaisesRegex(RuntimeError, "non-executable in this immutable image"):
                call()
        self.assertEqual(bridge.main(), 78)

    def test_oversized_webhook_is_rejected_before_body_read(self):
        with tempfile.TemporaryDirectory() as tmp:
            original_config = bridge.CONFIG
            original_events = bridge.EVENTS_LOG
            original_bridge_dir = bridge.BRIDGE_DIR
            setattr(bridge, "CONFIG", {"AGENTPHONE_MAX_WEBHOOK_BODY_BYTES": "1024"})
            setattr(bridge, "BRIDGE_DIR", Path(tmp))
            setattr(bridge, "EVENTS_LOG", Path(tmp) / "events.log")
            server = bridge.BridgeHTTPServer(("127.0.0.1", 0), bridge.Handler)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=2)
            try:
                connection.putrequest("POST", bridge.HOOK_PATH)
                connection.putheader("Content-Length", "1025")
                connection.endheaders()
                response = connection.getresponse()
                self.assertEqual(response.status, 413)
                self.assertEqual(json.loads(response.read()), {"ok": False, "error": "payload too large"})
            finally:
                connection.close()
                server.shutdown()
                server.server_close()
                thread.join(timeout=2)
                setattr(bridge, "CONFIG", original_config)
                setattr(bridge, "BRIDGE_DIR", original_bridge_dir)
                setattr(bridge, "EVENTS_LOG", original_events)

    def test_extract_event_fields_prefers_message_received_at_over_delivery_timestamp(self):
        payload = {
            "event": "agent.message",
            "channel": "imessage",
            "timestamp": "2026-07-10T00:28:01.000000Z",
            "data": {
                "conversationId": "conv-1",
                "from": "+15555550123",
                "direction": "inbound",
                "message": "older message delivered late",
                "messageId": "msg-old",
                "receivedAt": "2026-07-10T00:26:21.184000Z",
            },
        }

        fields = bridge.extract_event_fields(payload)

        self.assertEqual(fields["timestamp"], "2026-07-10T00:26:21.184000Z")

    def test_late_older_message_is_rejected_by_conversation_watermark(self):
        with tempfile.TemporaryDirectory() as tmp:
            watermark_path = Path(tmp) / "conversation_watermarks.json"
            newer = {
                "conversation_id": "conv-1",
                "sender": "+15555550123",
                "message_id": "msg-new",
                "timestamp": "2026-07-10T00:27:04.656000Z",
            }
            older_delivered_late = {
                "conversation_id": "conv-1",
                "sender": "+15555550123",
                "message_id": "msg-old",
                "timestamp": "2026-07-10T00:26:21.184000Z",
            }

            accepted_new, _ = bridge.mark_conversation_event_if_fresh(newer, watermark_path)
            accepted_old, latest = bridge.mark_conversation_event_if_fresh(older_delivered_late, watermark_path)

            self.assertTrue(accepted_new)
            self.assertFalse(accepted_old)
            self.assertEqual(latest, newer["timestamp"])
            stored = json.loads(watermark_path.read_text())
            self.assertEqual(stored["conv-1"]["timestamp"], newer["timestamp"])

    def test_http_handler_does_not_start_job_for_stale_message(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            secret = "test-webhook-secret"
            started_message_ids = []
            original = {
                "CONFIG": bridge.CONFIG,
                "WEBHOOK_SECRET": bridge.WEBHOOK_SECRET,
                "BRIDGE_DIR": bridge.BRIDGE_DIR,
                "SEEN_PATH": bridge.SEEN_PATH,
                "EVENTS_LOG": bridge.EVENTS_LOG,
                "mark": bridge.mark_conversation_event_if_fresh,
                "reaction": bridge.handle_reaction_only,
                "start": bridge.start_conversation_job,
                "run": bridge.run_hermes_and_reply,
            }
            watermark_path = tmp_path / "watermarks.json"
            bridge.CONFIG = {
                "AGENTPHONE_ALLOWED_SENDERS": "+15555550123",
            }
            bridge.WEBHOOK_SECRET = secret
            setattr(bridge, "BRIDGE_DIR", tmp_path)
            bridge.SEEN_PATH = tmp_path / "seen.json"
            bridge.EVENTS_LOG = tmp_path / "events.log"
            bridge.mark_conversation_event_if_fresh = (
                lambda fields: original["mark"](fields, watermark_path)
            )
            bridge.handle_reaction_only = lambda fields: False

            def fake_start(fields, reply_target):
                started_message_ids.append(fields["message_id"])
                return {"interrupted_previous": False}

            bridge.start_conversation_job = fake_start
            bridge.run_hermes_and_reply = lambda *args: None
            server = bridge.BridgeHTTPServer(("127.0.0.1", 0), bridge.Handler)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()

            def post(message_id, received_at, text):
                payload = {
                    "event": "agent.message",
                    "channel": "imessage",
                    "timestamp": "2026-07-10T00:30:00Z",
                    "data": {
                        "conversationId": "conv-1",
                        "from": "+15555550123",
                        "direction": "inbound",
                        "message": text,
                        "messageId": message_id,
                        "receivedAt": received_at,
                    },
                }
                raw = json.dumps(payload).encode()
                signature_ts = str(int(time.time()))
                signature = "sha256=" + hmac.new(
                    secret.encode(), signature_ts.encode() + b"." + raw, hashlib.sha256
                ).hexdigest()
                req = urllib.request.Request(
                    f"http://127.0.0.1:{server.server_port}/hooks/agentphone",
                    data=raw,
                    method="POST",
                    headers={
                        "Content-Type": "application/json",
                        "X-Webhook-Timestamp": signature_ts,
                        "X-Webhook-Signature": signature,
                    },
                )
                with urllib.request.urlopen(req, timeout=5) as response:
                    return response.status, json.loads(response.read())

            try:
                fresh_status, fresh_body = post(
                    "msg-new", "2026-07-10T00:27:04.656000Z", "newer"
                )
                stale_status, stale_body = post(
                    "msg-old", "2026-07-10T00:26:21.184000Z", "older delivered late"
                )
                time.sleep(0.05)

                self.assertEqual(fresh_status, 200)
                self.assertTrue(fresh_body["accepted"])
                self.assertEqual(stale_status, 200)
                self.assertEqual(stale_body["ignored"], "stale message")
                self.assertEqual(started_message_ids, ["msg-new"])
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=2)
                bridge.CONFIG = original["CONFIG"]
                bridge.WEBHOOK_SECRET = original["WEBHOOK_SECRET"]
                setattr(bridge, "BRIDGE_DIR", original["BRIDGE_DIR"])
                bridge.SEEN_PATH = original["SEEN_PATH"]
                bridge.EVENTS_LOG = original["EVENTS_LOG"]
                bridge.mark_conversation_event_if_fresh = original["mark"]
                bridge.handle_reaction_only = original["reaction"]
                bridge.start_conversation_job = original["start"]
                bridge.run_hermes_and_reply = original["run"]


class MediaBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self.tmp.name)
        self.generated = self.tmp_path / "generated"
        self.cache = self.tmp_path / "cache"
        self.bridge_dir = self.tmp_path / "bridge"
        self.generated.mkdir()
        self.bridge_dir.mkdir()
        self.original = {
            "CONFIG": bridge.CONFIG,
            "BRIDGE_DIR": bridge.BRIDGE_DIR,
            "EVENTS_LOG": bridge.EVENTS_LOG,
            "MEDIA_CACHE_DIR": bridge.MEDIA_CACHE_DIR,
            "PUBLIC_URL": bridge.PUBLIC_URL,
            "MEDIA_REGISTRY": bridge.MEDIA_REGISTRY,
        }
        setattr(bridge, "CONFIG", {
            "AGENTPHONE_MEDIA_GENERATED_ROOT": str(self.generated),
            "AGENTPHONE_MEDIA_MAX_BYTES": str(1024 * 1024),
        })
        setattr(bridge, "BRIDGE_DIR", self.bridge_dir)
        setattr(bridge, "EVENTS_LOG", self.bridge_dir / "events.log")
        setattr(bridge, "MEDIA_CACHE_DIR", self.cache)
        setattr(bridge, "PUBLIC_URL", "")
        setattr(bridge, "MEDIA_REGISTRY", {})

    def tearDown(self):
        setattr(bridge, "CONFIG", self.original["CONFIG"])
        setattr(bridge, "BRIDGE_DIR", self.original["BRIDGE_DIR"])
        setattr(bridge, "EVENTS_LOG", self.original["EVENTS_LOG"])
        setattr(bridge, "MEDIA_CACHE_DIR", self.original["MEDIA_CACHE_DIR"])
        setattr(bridge, "PUBLIC_URL", self.original["PUBLIC_URL"])
        setattr(bridge, "MEDIA_REGISTRY", self.original["MEDIA_REGISTRY"])
        self.tmp.cleanup()

    def test_generated_media_inside_approved_root_is_publishable(self):
        generated = self.generated / "reply.png"
        generated.write_bytes(b"generated-image")

        urls = bridge.resolve_media_refs([str(generated)])

        self.assertEqual(len(urls), 1)
        self.assertIn("/media/", urls[0])
        self.assertEqual(len(list(self.cache.glob("*_reply.png"))), 1)
        self.assertEqual(stat.S_IMODE(self.cache.stat().st_mode), 0o700)
        cached = next(self.cache.glob("*_reply.png"))
        self.assertEqual(stat.S_IMODE(cached.stat().st_mode), 0o600)

    def test_arbitrary_absolute_local_media_path_is_rejected(self):
        private = self.tmp_path / "private-customer.pdf"
        private.write_bytes(b"private")

        self.assertIsNone(bridge.approved_local_media_path(private))
        self.assertEqual(bridge.resolve_media_refs([str(private)]), [])

    def test_relative_traversal_outside_generated_root_is_rejected(self):
        outside = self.tmp_path / "outside.pdf"
        outside.write_bytes(b"outside")

        self.assertIsNone(bridge.approved_local_media_path(Path("../outside.pdf")))
        self.assertEqual(bridge.resolve_media_refs(["../outside.pdf"]), [])

    def test_symlink_escape_from_generated_root_is_rejected(self):
        outside = self.tmp_path / "outside.pdf"
        outside.write_bytes(b"outside")
        link = self.generated / "reply.pdf"
        try:
            link.symlink_to(outside)
        except (OSError, NotImplementedError):
            self.skipTest("symlinks unavailable")

        self.assertIsNone(bridge.approved_local_media_path(link))
        self.assertEqual(bridge.resolve_media_refs([str(link)]), [])

    def test_nested_directory_symlink_escape_is_rejected(self):
        outside_dir = self.tmp_path / "private"
        outside_dir.mkdir()
        private = outside_dir / "customer.pdf"
        private.write_bytes(b"private")
        link_dir = self.generated / "linked"
        try:
            link_dir.symlink_to(outside_dir, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("symlinks unavailable")

        escaped = link_dir / private.name
        self.assertIsNone(bridge.approved_local_media_path(escaped))
        self.assertEqual(bridge.resolve_media_refs([str(escaped)]), [])

    def test_arbitrary_remote_media_is_always_rejected(self):
        refs = [
            "https://cdn.example.com/reply.png",
            "http://cdn.example.com/reply.png",
            "https://localhost/reply.png",
            "https://127.0.0.1/reply.png",
            "https://2130706433/reply.png",
            "https://10.0.0.1/reply.png",
            "https://169.254.169.254/latest/meta-data",
            "https://attacker-controlled.example/reply.png",
            "https://user:password@example.com/reply.png",
        ]
        self.assertTrue(all(not bridge.approved_remote_media_url(ref) for ref in refs))
        self.assertEqual(bridge.resolve_media_refs(refs), [])

    def test_symlinked_media_cache_is_rejected(self):
        generated = self.generated / "reply.png"
        generated.write_bytes(b"generated-image")
        outside_cache = self.tmp_path / "outside-cache"
        outside_cache.mkdir()
        try:
            self.cache.symlink_to(outside_cache, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("symlinks unavailable")

        self.assertEqual(bridge.resolve_media_refs([str(generated)]), [])
        self.assertEqual(list(outside_cache.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
