#!/usr/bin/env python3
"""Isolated, operation-specific authenticated Orgo transport broker."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
from pathlib import Path
import re
import socket
import ssl
import stat
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

try:
    import certifi
    TLS_CONTEXT = ssl.create_default_context(cafile=certifi.where())
except Exception:
    TLS_CONTEXT = ssl.create_default_context()

ROOT = Path(__file__).resolve().parents[2]
GIT = "/usr/bin/git"
SSH_KEYGEN = "/usr/bin/ssh-keygen"
BROKER_FD_ENV = "REVENUE_PARTNER_BROKER_FD"
BROKER_SECRET_ENV = "REVENUE_PARTNER_BROKER_SECRET"
API_BASE = "https://www.orgo.ai/api"
NAMESPACE = "default"
NAME = "revenue-partner-agent"
VERSION = "1.0.0"
CANONICAL_REF = f"{NAMESPACE}/{NAME}@{VERSION}"
EXTERNAL_POLICY = Path("/etc/revenue-partner/reviewers.allowed_signers")
SIGNATURE_NAMESPACE = "revenue-partner-operation"
REVIEW_SIGNATURE_NAMESPACE = "revenue-partner-review"
REVIEW_ATTESTATIONS_ENV = "REVENUE_PARTNER_REVIEW_ATTESTATIONS"
NONCE_LEDGER_ENV = "REVENUE_PARTNER_NONCE_LEDGER"
BROKER_KEY_SALT = b"revenue-partner-broker-key-v1:"
OPERATION_INTENT_WAIT_SECONDS = 600
MAX_REQUEST_FRAME = 2_000_000
MAX_RESPONSE_FRAME = 6_000_000
MAX_HTTP_BODY = 1_048_576
MAX_SSE_BODY = 4_194_304
MAX_SSE_LINE = 65_536
MAX_SSE_EVENTS = 10_000
MAX_SSE_DEADLINE_SECONDS = 3_600
ID_PATTERN = re.compile(r"[A-Za-z0-9._:-]{1,128}")


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise urllib.error.HTTPError(req.full_url, code, "Orgo redirect refused", headers, fp)


def fail(message: str) -> RuntimeError:
    return RuntimeError(message)


def broker_key_sha256(key: str) -> str:
    return hashlib.sha256(hashlib.sha256(BROKER_KEY_SALT + key.encode("utf-8")).digest()).hexdigest()


def nonce_ledger() -> Path:
    text = os.environ.get(NONCE_LEDGER_ENV, "")
    path = Path(text) if text else Path()
    if not path.is_absolute():
        raise fail("broker nonce ledger path must be absolute")
    try:
        parent = path.parent
        parent_info = parent.lstat()
        if stat.S_ISLNK(parent_info.st_mode):
            parent = parent.resolve()
            parent_info = parent.lstat()
        info = path.lstat()
    except OSError as exc:
        raise fail(f"broker nonce ledger is unavailable: {exc}") from exc
    if (
        not stat.S_ISDIR(parent_info.st_mode)
        or parent_info.st_uid != 0
        or stat.S_IMODE(parent_info.st_mode) != 0o1777
        or stat.S_ISLNK(info.st_mode)
        or not stat.S_ISDIR(info.st_mode)
        or info.st_uid != os.geteuid()
        or stat.S_IMODE(info.st_mode) != 0o700
    ):
        raise fail("broker nonce ledger requires a root-owned sticky parent and an owner-only directory")
    return path


GIT_SAFE_ARGS = ["-c", "core.fsmonitor=false"]


def keyless_subprocess_environment() -> dict[str, str]:
    """Build a from-scratch environment for git/ssh-keygen subprocesses.

    No operator variable survives: gitconfig, fsmonitor hooks, index/object
    redirection, and credential variables cannot reach a child of the
    credential-bearing broker.
    """
    return {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "HOME": "/tmp",
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_GLOBAL": "/dev/null",
    }


def read_regular_nofollow(path: Path, maximum: int, *, required_mode: int | None = None) -> bytes:
    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        descriptor = os.open(path, flags)
    except OSError as exc:
        raise fail(f"broker evidence file is unavailable: {exc}") from exc
    try:
        info = os.fstat(descriptor)
        if (
            not stat.S_ISREG(info.st_mode)
            or info.st_uid != os.geteuid()
            or info.st_size > maximum
            or (required_mode is not None and stat.S_IMODE(info.st_mode) != required_mode)
        ):
            raise fail("broker evidence file ownership, mode, type, or size is invalid")
        data = bytearray()
        while len(data) <= maximum:
            chunk = os.read(descriptor, min(65536, maximum + 1 - len(data)))
            if not chunk:
                break
            data.extend(chunk)
        if len(data) > maximum:
            raise fail("broker evidence file exceeds its byte ceiling")
        return bytes(data)
    finally:
        os.close(descriptor)


def exact_tree() -> str:
    environment = keyless_subprocess_environment()
    tree = subprocess.check_output([GIT, *GIT_SAFE_ARGS, "write-tree"], cwd=ROOT, text=True, env=environment).strip()
    if subprocess.check_output([GIT, *GIT_SAFE_ARGS, "diff", "--name-only"], cwd=ROOT, text=True, env=environment).strip():
        raise fail("broker rejected unstaged tracked drift")
    if subprocess.check_output(
        [GIT, *GIT_SAFE_ARGS, "ls-files", "--others", "--exclude-standard"], cwd=ROOT, text=True, env=environment
    ).strip():
        raise fail("broker rejected non-ignored untracked files")
    return tree


def canonical_products() -> tuple[str, str, dict, bytes]:
    resolved_path = ROOT / f"{NAME}.resolved.json"
    raw = read_regular_nofollow(resolved_path, MAX_HTTP_BODY)
    if len(raw) > MAX_HTTP_BODY:
        raise fail("resolved artifact exceeds broker ceiling")
    try:
        template = json.loads(raw)
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise fail(f"resolved artifact is invalid: {exc}") from exc
    canonical = (json.dumps(template, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    if raw != canonical:
        raise fail("resolved artifact bytes are not canonical")
    envelope = {"namespace": NAMESPACE, "name": NAME, "version": VERSION, "template": template}
    publication = json.dumps(envelope, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest(), hashlib.sha256(publication).hexdigest(), template, publication


def canonical_url(url: object) -> str:
    if not isinstance(url, str):
        raise fail("broker URL must be a string")
    parsed = urllib.parse.urlsplit(url)
    if (
        parsed.scheme != "https"
        or parsed.hostname != "www.orgo.ai"
        or parsed.port not in (None, 443)
        or parsed.username is not None
        or parsed.password is not None
        or not parsed.path.startswith("/api/")
        or parsed.query
        or parsed.fragment
    ):
        raise fail("broker target must use the fixed Orgo API authority")
    return url


def bounded_identity(value: object, label: str) -> str:
    text = str(value or "").strip()
    if ID_PATTERN.fullmatch(text) is None:
        raise fail(f"broker {label} is invalid")
    return text


def validate_request(message: dict, template: dict, publication: bytes) -> tuple[dict, bytes | None]:
    if set(message) != {"operation", "method", "url", "body_b64", "publication", "build", "intent_path", "key_sha256"}:
        raise fail("broker request fields are not exact")
    operation = message["operation"]
    if operation not in {"validate", "publish", "readback", "build", "events", "launch"}:
        raise fail("broker operation is unsupported")
    key_sha256 = message["key_sha256"]
    if re.fullmatch(r"[0-9a-f]{64}", key_sha256 or "") is None:
        raise fail("broker request must bind the exact credential digest")
    method = message["method"]
    url = canonical_url(message["url"])
    body_text = message["body_b64"]
    if body_text is None:
        body = None
    elif isinstance(body_text, str) and len(body_text) <= MAX_REQUEST_FRAME:
        try:
            body = base64.b64decode(body_text, validate=True)
        except ValueError as exc:
            raise fail("broker request body encoding is invalid") from exc
    else:
        raise fail("broker request body is invalid")
    publication_record = message["publication"]
    build_record = message["build"]
    publication_id = None
    publication_digest = None
    if publication_record is not None:
        if not isinstance(publication_record, dict) or set(publication_record) != {"publication_id", "template_ref", "publication_sha256"}:
            raise fail("broker publication identity is malformed")
        publication_id = bounded_identity(publication_record["publication_id"], "publication ID")
        if publication_record["template_ref"] != CANONICAL_REF:
            raise fail("broker publication reference is invalid")
        publication_digest = publication_record["publication_sha256"]
    build_id = None
    if build_record is not None:
        if not isinstance(build_record, dict) or set(build_record) != {"build_id", "publication_id", "publication_sha256"}:
            raise fail("broker build identity is malformed")
        build_id = bounded_identity(build_record["build_id"], "build ID")
        if build_record["publication_id"] != publication_id or build_record["publication_sha256"] != publication_digest:
            raise fail("broker build identity does not bind publication")

    template_bytes = json.dumps(template, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    if operation == "validate":
        expected = ("POST", f"{API_BASE}/templates/validate", template_bytes, False, False)
    elif operation == "publish":
        expected = ("POST", f"{API_BASE}/templates", publication, False, False)
    elif operation == "readback":
        expected = ("GET", f"{API_BASE}/templates/{publication_id}", None, True, False)
    elif operation == "build":
        expected = ("POST", f"{API_BASE}/templates/{publication_id}/build", None, True, False)
    elif operation == "events":
        expected = ("GET", f"{API_BASE}/templates/{publication_id}/builds/{build_id}/events", None, True, True)
    else:
        expected = ("POST", f"{API_BASE}/computers", body, True, False)
    expected_method, expected_url, expected_body, needs_publication, needs_build = expected
    if method != expected_method or url != expected_url or body != expected_body:
        raise fail("broker request does not match canonical operation bytes")
    if needs_publication and publication_id is None:
        raise fail("broker operation requires publication identity")
    if needs_build and build_id is None:
        raise fail("broker operation requires build identity")
    if not needs_publication and publication_record is not None:
        raise fail("broker operation received unexpected publication identity")
    if not needs_build and build_record is not None:
        raise fail("broker operation received unexpected build identity")
    launch = None
    if operation == "launch":
        if not isinstance(body, (bytes, bytearray)):
            raise fail("broker launch body is missing")
        try:
            launch = json.loads(body)
        except (TypeError, UnicodeError, json.JSONDecodeError) as exc:
            raise fail("broker launch body is invalid") from exc
        expected_keys = {"workspace_id", "name", "template_ref", "template_id", "ram", "cpu"}
        if set(launch) != expected_keys or launch != {
            "workspace_id": launch.get("workspace_id"),
            "name": "revenue-partner-smoke",
            "template_ref": CANONICAL_REF,
            "template_id": publication_id,
            "ram": 4,
            "cpu": 1,
        }:
            raise fail("broker launch body is not canonical")
        bounded_identity(launch["workspace_id"], "workspace ID")
    return {
        "operation": operation,
        "method": method,
        "url": url,
        "body": body,
        "publication_id": publication_id,
        "publication_sha256": publication_digest,
        "build_id": build_id,
        "intent_path": message["intent_path"],
        "key_sha256": key_sha256,
        "workspace_id": launch["workspace_id"] if launch is not None else None,
    }, body


def trust_policy() -> str:
    try:
        parent_info = EXTERNAL_POLICY.parent.lstat()
        info = EXTERNAL_POLICY.lstat()
        candidate = subprocess.check_output(
            [GIT, *GIT_SAFE_ARGS, "show", ":.github/reviewers.allowed_signers"],
            cwd=ROOT,
            env=keyless_subprocess_environment(),
        )
        external = EXTERNAL_POLICY.read_bytes()
    except (OSError, subprocess.CalledProcessError) as exc:
        raise fail(f"broker reviewer policy unavailable: {exc}") from exc
    if (
        not stat.S_ISDIR(parent_info.st_mode)
        or stat.S_ISLNK(parent_info.st_mode)
        or parent_info.st_uid != 0
        or stat.S_IMODE(parent_info.st_mode) != 0o755
        or not stat.S_ISREG(info.st_mode)
        or stat.S_ISLNK(info.st_mode)
        or info.st_uid != 0
        or stat.S_IMODE(info.st_mode) != 0o644
    ):
        raise fail("broker reviewer policy requires a root-owned 0755 directory and 0644 regular file")
    if candidate != external:
        raise fail("broker candidate reviewer declaration does not match external policy")
    return str(EXTERNAL_POLICY)


def verify_signature(identity: str, namespace: str, statement: dict, signature_path: Path) -> None:
    if not signature_path.is_absolute():
        raise fail("broker signature path must be absolute")
    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        descriptor = os.open(signature_path, flags)
    except OSError as exc:
        raise fail(f"broker signature is unavailable: {exc}") from exc
    try:
        info = os.fstat(descriptor)
        if (
            not stat.S_ISREG(info.st_mode)
            or info.st_uid != os.geteuid()
            or stat.S_IMODE(info.st_mode) != 0o600
            or info.st_size > 16384
        ):
            raise fail("broker signature ownership, mode, type, or size is invalid")
        canonical = (json.dumps(statement, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
        result = subprocess.run(
            [SSH_KEYGEN, "-Y", "verify", "-f", trust_policy(), "-I", identity,
             "-n", namespace, "-s", f"/dev/fd/{descriptor}"],
            input=canonical,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=keyless_subprocess_environment(),
            pass_fds=(descriptor,),
        )
    finally:
        os.close(descriptor)
    if result.returncode != 0:
        raise fail(f"broker signature verification failed for {identity}")


def verify_reviews(tree: str, artifact_digest: str, publication_digest: str) -> None:
    attestation_text = os.environ.get(REVIEW_ATTESTATIONS_ENV, "")
    path = Path(attestation_text) if attestation_text else Path()
    if not path.is_absolute():
        raise fail("broker exact-tree review attestation is required")
    try:
        record = json.loads(read_regular_nofollow(path, 131072, required_mode=0o600))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise fail(f"broker review attestation is invalid: {exc}") from exc
    expected = {
        "tree": tree,
        "artifact_sha256": artifact_digest,
        "publication_sha256": publication_digest,
    }
    if not isinstance(record, dict) or any(record.get(key) != value for key, value in expected.items()):
        raise fail("broker review attestation does not bind current exact bytes")
    reviews = record.get("reviews")
    if not isinstance(reviews, list) or len(reviews) != 2:
        raise fail("broker requires exactly two independent reviews")
    seen = set()
    signatures = set()
    for review in reviews:
        if not isinstance(review, dict) or set(review) != {"reviewer_id", "statement", "signature_path"}:
            raise fail("broker review entry is malformed")
        reviewer = review["reviewer_id"]
        if reviewer not in {"documentation", "security"}:
            raise fail("broker reviewer identity is unauthorized")
        expected_statement = {**expected, "reviewer_id": reviewer, "verdict": "CLEAR"}
        if review["statement"] != expected_statement:
            raise fail("broker review statement does not bind exact CLEAR verdict")
        signature_path = Path(review["signature_path"]) if isinstance(review["signature_path"], str) else Path()
        verify_signature(reviewer, REVIEW_SIGNATURE_NAMESPACE, expected_statement, signature_path)
        seen.add(reviewer)
        signatures.add(str(signature_path))
    if seen != {"documentation", "security"} or len(signatures) != 2:
        raise fail("broker requires distinct documentation and security signatures")


def consume_intent(request: dict, tree: str, artifact_digest: str, publication_digest: str) -> None:
    text = request["intent_path"]
    path = Path(text) if isinstance(text, str) else Path()
    if not path.is_absolute():
        raise fail("broker operation intent must be an absolute owner-only regular file")
    try:
        record = json.loads(read_regular_nofollow(path, 131072, required_mode=0o600))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise fail(f"broker operation intent is unreadable: {exc}") from exc
    if not isinstance(record, dict) or set(record) != {"statement", "signature_path"} or not isinstance(record["statement"], dict):
        raise fail("broker operation intent record is malformed")
    statement = record["statement"]
    nonce = statement.get("nonce")
    if re.fullmatch(r"[0-9a-f]{64}", nonce or "") is None:
        raise fail("broker operation nonce is invalid")
    assert isinstance(nonce, str)
    issued_at = statement.get("issued_at")
    expires_at = statement.get("expires_at")
    if not isinstance(issued_at, (int, float)) or not isinstance(expires_at, (int, float)):
        raise fail("broker signed intent must carry issued_at and expires_at")
    now = time.time()
    if issued_at > now + 60 or expires_at <= now or expires_at - issued_at > OPERATION_INTENT_WAIT_SECONDS:
        raise fail("broker signed intent is outside its freshness window")
    expected = {
        "operation": request["operation"],
        "nonce": nonce,
        "issued_at": issued_at,
        "expires_at": expires_at,
        "method": request["method"],
        "url": request["url"],
        "body_sha256": hashlib.sha256(request["body"]).hexdigest() if request["body"] is not None else None,
        "template_ref": CANONICAL_REF,
        "publication_id": request["publication_id"],
        "build_id": request["build_id"],
        "tree": tree,
        "artifact_sha256": artifact_digest,
        "publication_sha256": publication_digest,
    }
    if statement != expected:
        raise fail("broker signed intent does not bind exact current request and products")
    statement_bytes = (
        json.dumps(statement, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
    ).encode("utf-8")
    signature = Path(record["signature_path"]) if isinstance(record["signature_path"], str) else Path()
    verify_signature("release-operator", SIGNATURE_NAMESPACE, statement, signature)
    ledger = nonce_ledger()
    marker = ledger / nonce
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        fd = os.open(marker, flags, 0o600)
    except FileExistsError as exc:
        raise fail("broker operation nonce was already consumed") from exc
    try:
        os.write(fd, hashlib.sha256(statement_bytes).hexdigest().encode("ascii") + b"\n")
        os.fsync(fd)
    finally:
        os.close(fd)


def recv_frame(sock: socket.socket, maximum: int) -> bytes | None:
    data = bytearray()
    while True:
        chunk = sock.recv(min(65536, maximum + 1 - len(data)))
        if not chunk:
            return None if not data else bytes(data)
        data.extend(chunk)
        if len(data) > maximum:
            raise fail("broker protocol frame exceeded ceiling")
        if data.endswith(b"\n"):
            return bytes(data[:-1])


def broker_secret() -> bytes:
    text = os.environ.get(BROKER_SECRET_ENV, "")
    if re.fullmatch(r"[0-9a-f]{64}", text or "") is None:
        raise fail("broker MAC secret is unavailable")
    return text.encode("ascii")


def send_frame(sock: socket.socket, payload: dict) -> None:
    raw = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8") + b"\n"
    if len(raw) > MAX_RESPONSE_FRAME:
        raise fail("broker response frame exceeded ceiling")
    mac = hmac.new(broker_secret(), raw, hashlib.sha256).hexdigest().encode("ascii") + b"\n"
    sock.sendall(raw + mac)


def _identity_object(payload: dict, identity_keys: set[str]) -> dict:
    matches = []

    def visit(value):
        if isinstance(value, dict):
            if any(key in value for key in identity_keys):
                matches.append(value)
            for nested in value.values():
                visit(nested)
        elif isinstance(value, list):
            for nested in value:
                visit(nested)

    visit(payload)
    if len(matches) != 1:
        raise fail("broker response must contain exactly one co-resident identity object")
    return matches[0]


def _alias_value(identity: dict, *names: str, required: bool = True):
    present = [(name, identity[name]) for name in names if name in identity and identity[name] not in (None, "")]
    if len(present) > 1:
        raise fail("broker response duplicate identity aliases are prohibited")
    if not present:
        if required:
            raise fail("broker response required identity field is missing")
        return None
    return present[0][1]


def validate_response_semantics(request: dict, status: int, body: bytes, publication_digest: str, template_digest: str) -> None:
    if status < 200 or status >= 300:
        return
    if request["operation"] == "events":
        # SSE bodies are not JSON; parse_sse_events validates them separately.
        return
    try:
        payload = json.loads(body)
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise fail("broker response was not valid JSON") from exc
    if not isinstance(payload, dict):
        raise fail("broker response must be a JSON object")
    operation = request["operation"]
    if operation == "validate":
        identity = _identity_object(payload, {"valid", "template_ref", "ref", "template_sha256", "sha256", "checksum"})
        valid = _alias_value(identity, "valid")
        template_ref = _alias_value(identity, "template_ref", "ref")
        digest = _alias_value(identity, "template_sha256", "sha256", "checksum")
        if valid is not True or template_ref != CANONICAL_REF:
            raise fail("broker validation response is not a bound acceptance")
        if str(digest).lower().removeprefix("sha256:") != template_digest:
            raise fail("broker validation response digest does not match exact template bytes")
    elif operation == "publish":
        identity = _identity_object(payload, {"publication_id", "template_id", "id", "template_ref", "ref", "publication_sha256", "sha256", "checksum"})
        publication_id = _alias_value(identity, "publication_id", "template_id", "id")
        template_ref = _alias_value(identity, "template_ref", "ref")
        digest = _alias_value(identity, "publication_sha256", "sha256", "checksum")
        if not str(publication_id).strip() or template_ref != CANONICAL_REF:
            raise fail("broker publication response identity is invalid")
        if str(digest).lower().removeprefix("sha256:") != publication_digest:
            raise fail("broker publication response digest does not match signed publication bytes")
    elif operation == "readback":
        identity = _identity_object(payload, {"publication_id", "template_id", "id", "template_ref", "ref", "publication_sha256", "sha256", "checksum"})
        publication_id = _alias_value(identity, "publication_id", "template_id", "id")
        template_ref = _alias_value(identity, "template_ref", "ref")
        digest = _alias_value(identity, "publication_sha256", "sha256", "checksum")
        if str(publication_id) != request["publication_id"] or template_ref != CANONICAL_REF:
            raise fail("broker readback response does not match the immutable publication identity")
        if str(digest).lower().removeprefix("sha256:") != publication_digest:
            raise fail("broker readback response digest does not match signed publication bytes")
    elif operation == "build":
        identity = _identity_object(payload, {"build_id", "job_id", "publication_id", "template_id", "publication_sha256", "sha256", "checksum"})
        build_id = _alias_value(identity, "build_id", "job_id")
        publication_id = _alias_value(identity, "publication_id", "template_id")
        digest = _alias_value(identity, "publication_sha256", "sha256", "checksum")
        if not str(build_id).strip() or str(publication_id) != request["publication_id"]:
            raise fail("broker build response does not bind the immutable publication identity")
        if str(digest).lower().removeprefix("sha256:") != publication_digest:
            raise fail("broker build response digest does not match signed publication bytes")
    elif operation == "launch":
        identity = _identity_object(payload, {"computer_id", "id", "workspace_id", "template_ref", "publication_id", "template_id"})
        computer_id = _alias_value(identity, "computer_id", "id")
        workspace_id = _alias_value(identity, "workspace_id")
        template_ref = _alias_value(identity, "template_ref")
        template_id = _alias_value(identity, "publication_id", "template_id")
        if not str(computer_id).strip() or str(workspace_id) != request["workspace_id"]:
            raise fail("broker launch response does not bind the requested workspace")
        if template_ref != CANONICAL_REF or str(template_id) != request["publication_id"]:
            raise fail("broker launch response does not bind the immutable publication identity")


def parse_sse_events(body: bytes, build_id: str) -> tuple[bool, bool]:
    """Parse a bounded SSE body inside the broker; return (ready, failed)."""
    started = time.monotonic()
    total_bytes = 0
    event_count = 0
    ready = False
    failed = False
    for raw_line in body.splitlines(keepends=True):
        if time.monotonic() - started > MAX_SSE_DEADLINE_SECONDS:
            raise fail("broker event stream exceeded its absolute deadline")
        if len(raw_line) > MAX_SSE_LINE:
            raise fail("broker event line exceeded its byte ceiling")
        total_bytes += len(raw_line)
        if total_bytes > MAX_SSE_BODY:
            raise fail("broker event stream exceeded its cumulative byte ceiling")
        text = raw_line.decode("utf-8", errors="replace").rstrip()
        if not text.startswith("data: "):
            continue
        event_count += 1
        if event_count > MAX_SSE_EVENTS:
            raise fail("broker event stream exceeded its event-count ceiling")
        try:
            event = json.loads(text.removeprefix("data: "))
        except json.JSONDecodeError:
            event = {}
        if event.get("phase") == "ready" and event.get("level") == "success":
            event_build_id = str(event.get("build_id") or event.get("job_id") or "")
            if event_build_id == build_id:
                ready = True
            else:
                failed = True
        if event.get("phase") == "failed" or event.get("level") == "error":
            failed = True
        if "build failed" in text.lower() or '"failed"' in text:
            failed = True
    return ready, failed


def read_bounded_response(response, operation: str) -> tuple[int, bytes]:
    limit = MAX_SSE_BODY if operation == "events" else MAX_HTTP_BODY
    declared = response.headers.get("Content-Length")
    if declared is not None:
        try:
            declared_bytes = int(declared)
        except (TypeError, ValueError) as exc:
            raise fail("broker response Content-Length is invalid") from exc
        if declared_bytes > limit:
            raise fail("broker response declared size exceeds ceiling")
    if operation != "events":
        body = response.read(limit + 1)
        if len(body) > limit:
            raise fail("broker response exceeded byte ceiling")
        status_value = getattr(response, "status", None)
        if status_value is None:
            status_value = response.getcode()
        if status_value is None:
            raise fail("broker response status is missing")
        return int(status_value), body
    started = time.monotonic()
    body = bytearray()
    read_chunk = getattr(response, "read1", None)
    if read_chunk is None:
        # urllib.error.HTTPError (non-2xx) has read() but not read1().
        read_chunk = response.read
    while True:
        remaining = MAX_SSE_DEADLINE_SECONDS - (time.monotonic() - started)
        if remaining <= 0:
            raise fail("broker event stream exceeded its absolute deadline")
        chunk = read_chunk(min(65536, MAX_SSE_BODY + 1 - len(body)))
        if time.monotonic() - started > MAX_SSE_DEADLINE_SECONDS:
            raise fail("broker event stream exceeded its absolute deadline")
        if not chunk:
            break
        body.extend(chunk)
        if len(body) > MAX_SSE_BODY:
            raise fail("broker event stream exceeded its cumulative byte ceiling")
    status_value = getattr(response, "status", None)
    if status_value is None:
        status_value = response.getcode()
    if status_value is None:
        raise fail("broker response status is missing")
    return int(status_value), bytes(body)


def main() -> int:
    if not (sys.flags.isolated and sys.flags.ignore_environment and sys.flags.no_user_site):
        raise SystemExit("authenticated broker requires trusted Python -I -s -E")
    fd_text = os.environ.get(BROKER_FD_ENV, "")
    if not fd_text.isdigit():
        raise SystemExit("isolated broker descriptor is unavailable")
    broker_socket = socket.socket(fileno=int(fd_text))
    opener = None
    while True:
        frame = recv_frame(broker_socket, MAX_REQUEST_FRAME)
        if frame is None:
            broker_socket.close()
            return 0
        try:
            message = json.loads(frame)
            if not isinstance(message, dict):
                raise fail("broker request must be an object")
            tree = exact_tree()
            artifact_digest, publication_digest, template, publication = canonical_products()
            request, body = validate_request(message, template, publication)
            if request["publication_sha256"] is not None and request["publication_sha256"] != publication_digest:
                raise fail("broker publication identity digest does not match exact bytes")
            verify_reviews(tree, artifact_digest, publication_digest)
            consume_intent(request, tree, artifact_digest, publication_digest)
            key = os.environ.get("ORGO_API_KEY", "")
            if not key or key != key.strip() or len(key) > 16384 or any(ord(char) < 32 for char in key):
                raise fail("broker ORGO_API_KEY is missing or malformed")
            if request["key_sha256"] != broker_key_sha256(key):
                raise fail("broker request does not bind the exact credential")
            if opener is None:
                opener = urllib.request.build_opener(
                    urllib.request.ProxyHandler({}),
                    urllib.request.HTTPSHandler(context=TLS_CONTEXT),
                    NoRedirect(),
                )
            headers = {"Authorization": f"Bearer {key}"}
            if body is not None:
                headers["Content-Type"] = "application/json"
            network_request = urllib.request.Request(
                request["url"], data=body, method=request["method"], headers=headers
            )
            try:
                response = opener.open(network_request, timeout=30 if request["operation"] == "events" else 60)
            except urllib.error.HTTPError as exc:
                response = exc
            try:
                status, response_body = read_bounded_response(response, request["operation"])
                template_digest = hashlib.sha256(
                    json.dumps(template, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
                ).hexdigest()
                validate_response_semantics(request, status, response_body, publication_digest, template_digest)
                if request["operation"] == "events":
                    ready, failed = parse_sse_events(response_body, request["build_id"])
                    if not ready or failed:
                        raise fail("broker build event stream did not reach a bound ready state")
            finally:
                response.close()
            send_frame(broker_socket, {"status": status, "body_b64": base64.b64encode(response_body).decode("ascii")})
        except Exception as exc:
            send_frame(broker_socket, {"error": str(exc)[:2000]})


if __name__ == "__main__":
    raise SystemExit(main())
