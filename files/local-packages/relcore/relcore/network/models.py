"""Which frontier model runs the deep-pass agents, and one call shape for all of them.

    ask(system, prompt, schema) -> dict     one JSON answer, checked against a small JSON schema

Backends, in pick() order (NETWORK_DEEP_ENGINE forces one):
  anthropic   Claude Opus 5.5 on the Anthropic API (NETWORK_DEEP_MODEL, default claude-opus-5-5). Needs ANTHROPIC_API_KEY
              and the `anthropic` package. Imported only here, so relcore stays stdlib-only without it.
  claude      The Claude Code CLI (`claude -p`), on a logged-in Claude subscription. Tools off.
  openrouter  OpenRouter (NETWORK_DEEP_OPENROUTER_MODEL, default anthropic/claude-opus-5.5). Needs OPENROUTER_API_KEY.
  codex       The Codex CLI (`codex exec`) on a ChatGPT subscription. Read-only sandbox, run from an empty folder.
              Local example runs only: it is never picked automatically, because page text is untrusted and
              codex can read files. Set NETWORK_DEEP_ENGINE=codex to use it on purpose.

Every backend runs from an empty temp folder (CLIs) and gets the page text as data inside the user turn,
never as instructions. A reply that is not valid JSON for the schema is retried once, then raised.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile

from .classify import _post, env_key

ANTHROPIC_MODEL = "claude-opus-5-5"


class ModelError(RuntimeError):
    pass


# ---------------------------------------------------------------- schema check (small, stdlib)
def check(value, schema: dict, where: str = "$") -> None:
    t = schema.get("type")
    if t == "object":
        if not isinstance(value, dict):
            raise ModelError(f"{where}: expected an object")
        for k in schema.get("required", []):
            if k not in value:
                raise ModelError(f"{where}: missing {k}")
        for k, sub in (schema.get("properties") or {}).items():
            if k in value and value[k] is not None:
                check(value[k], sub, f"{where}.{k}")
    elif t == "array":
        if not isinstance(value, list):
            raise ModelError(f"{where}: expected a list")
        for i, v in enumerate(value):
            check(v, schema.get("items") or {}, f"{where}[{i}]")
    elif t == "string":
        if not isinstance(value, str):
            raise ModelError(f"{where}: expected text")
        if schema.get("enum") and value not in schema["enum"]:
            raise ModelError(f"{where}: {value!r} is not one of {schema['enum']}")
    elif t == "number":
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise ModelError(f"{where}: expected a number")
    elif t == "boolean":
        if not isinstance(value, bool):
            raise ModelError(f"{where}: expected true or false")


def strict(schema: dict) -> dict:
    """The same schema with additionalProperties false and every property required, for structured outputs."""
    s = dict(schema)
    if s.get("type") == "object":
        props = {k: strict(v) for k, v in (s.get("properties") or {}).items()}
        s.update(properties=props, required=list(props), additionalProperties=False)
    elif s.get("type") == "array":
        s["items"] = strict(s.get("items") or {})
    return s


def parse(text: str) -> dict:
    text = (text or "").strip()
    if text.startswith("```"):
        text = text.strip("`")
        text = text[text.find("{"):] if "{" in text else text
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end < start:
        raise ModelError("the reply held no JSON object")
    try:
        return json.loads(text[start:end + 1])
    except json.JSONDecodeError as err:
        raise ModelError(f"the reply was not valid JSON: {err}") from err


def _framed(system: str, prompt: str, schema: dict) -> str:
    return (f"{system}\n\n{prompt}\n\nReply with one JSON object and nothing else. It must match this JSON schema:\n"
            f"{json.dumps(strict(schema))}")


# ---------------------------------------------------------------- backends
class Engine:
    name = "none"
    model = ""

    def raw(self, system: str, prompt: str, schema: dict) -> str:  # pragma: no cover - interface
        raise NotImplementedError

    def ask(self, system: str, prompt: str, schema: dict) -> dict:
        last = None
        for attempt in range(2):
            try:
                text = self.raw(system, prompt if attempt == 0 else
                                prompt + f"\n\nYour last reply was rejected ({last}). Reply with valid JSON only.", schema)
                data = parse(text) if isinstance(text, str) else text
                check(data, schema)
                return data
            except ModelError as err:
                last = str(err)[:200]
        raise ModelError(f"{self.name}: {last}")

    def label(self) -> str:
        return f"{self.name}:{self.model}" if self.model else self.name


class Anthropic(Engine):
    """Claude Opus 5.5 with adaptive thinking, structured JSON output and the server-side refusal fallback."""
    name = "anthropic"

    def __init__(self, client=None, model: str | None = None, effort: str | None = None):
        self.model = model or os.environ.get("NETWORK_DEEP_MODEL", ANTHROPIC_MODEL)
        self.effort = effort or os.environ.get("NETWORK_DEEP_EFFORT", "high")
        self._client = client

    def client(self):
        if self._client is None:
            import anthropic  # optional dependency, only for this backend
            self._client = anthropic.Anthropic(api_key=env_key("ANTHROPIC_API_KEY"), max_retries=3)
        return self._client

    def request(self, system: str, prompt: str, schema: dict) -> dict:
        return {"model": self.model, "max_tokens": 16000, "system": system,
                "messages": [{"role": "user", "content": prompt}],
                "thinking": {"type": "adaptive"},
                "output_config": {"effort": self.effort, "format": {"type": "json_schema", "schema": strict(schema)}},
                "betas": ["server-side-fallback-2026-07-01"], "extra_body": {"fallbacks": "default"}}

    def raw(self, system: str, prompt: str, schema: dict):
        import anthropic
        try:
            msg = self.client().beta.messages.create(**self.request(system, prompt, schema))
        except anthropic.APIConnectionError as err:
            raise ModelError(f"connection: {err}") from err
        except anthropic.APIStatusError as err:
            if err.status_code in (400, 401, 403, 404):
                raise  # a request or key problem: retrying with the same body cannot fix it
            raise ModelError(f"API {err.status_code}") from err
        if msg.stop_reason == "refusal":
            raise ModelError("the model declined this item")
        if msg.stop_reason == "max_tokens":
            raise ModelError("the reply ran past max_tokens")
        return "".join(b.text for b in msg.content if getattr(b, "type", "") == "text")


def _scratch() -> str:
    return tempfile.mkdtemp(prefix="relcore-deep-")


class ClaudeCLI(Engine):
    name = "claude"

    def __init__(self, model: str | None = None):
        self.model = model or os.environ.get("NETWORK_DEEP_MODEL", ANTHROPIC_MODEL)

    def raw(self, system: str, prompt: str, schema: dict) -> str:
        cwd = _scratch()
        try:
            p = subprocess.run(["claude", "-p", "--model", self.model, "--output-format", "json", "--tools", ""],
                               input=_framed(system, prompt, schema), capture_output=True, text=True, cwd=cwd,
                               timeout=600)
        except (OSError, subprocess.TimeoutExpired) as err:
            raise ModelError(f"claude cli: {err}") from err
        finally:
            shutil.rmtree(cwd, ignore_errors=True)
        try:
            out = json.loads(p.stdout)
        except json.JSONDecodeError as err:
            raise ModelError(f"claude cli: {(p.stdout or p.stderr)[-200:]}") from err
        if out.get("is_error"):
            raise ModelError(f"claude cli: {str(out.get('result'))[:200]}")
        return out.get("result") or ""

    @staticmethod
    def available() -> bool:
        if not shutil.which("claude"):
            return False
        try:
            p = subprocess.run(["claude", "-p", "--output-format", "json", "--tools", ""], input="Reply OK.",
                               capture_output=True, text=True, cwd=tempfile.gettempdir(), timeout=60)
            return not json.loads(p.stdout or "{}").get("is_error", True)
        except Exception:
            return False


class Codex(Engine):
    name = "codex"

    def __init__(self, model: str | None = None):
        self.model = model or os.environ.get("NETWORK_DEEP_CODEX_MODEL", "")

    def raw(self, system: str, prompt: str, schema: dict) -> str:
        cwd = _scratch()
        out = os.path.join(cwd, "last.txt")
        cmd = ["codex", "exec", "--skip-git-repo-check", "--sandbox", "read-only", "--ephemeral",
               "--output-last-message", out]
        if self.model:
            cmd += ["--model", self.model]
        try:
            p = subprocess.run(cmd + ["-"], input=_framed(system, prompt, schema), capture_output=True, text=True,
                               cwd=cwd, timeout=900)
            if p.returncode != 0 or not os.path.exists(out):
                raise ModelError(f"codex exit {p.returncode}: {p.stderr[-200:]}")
            if not self.model:
                for line in p.stderr.splitlines():
                    if line.startswith("model:"):
                        self.model = line.split(":", 1)[1].strip()
            return open(out).read()
        except (OSError, subprocess.TimeoutExpired) as err:
            raise ModelError(f"codex: {err}") from err
        finally:
            shutil.rmtree(cwd, ignore_errors=True)


class OpenRouter(Engine):
    name = "openrouter"

    def __init__(self, model: str | None = None):
        self.model = model or os.environ.get("NETWORK_DEEP_OPENROUTER_MODEL", "anthropic/claude-opus-5.5")

    def raw(self, system: str, prompt: str, schema: dict) -> str:
        try:
            r = _post("https://openrouter.ai/api/v1/chat/completions",
                      {"model": self.model, "messages": [{"role": "system", "content": system},
                                                         {"role": "user", "content": _framed("", prompt, schema)}],
                       "response_format": {"type": "json_object"}},
                      {"Authorization": f"Bearer {env_key('OPENROUTER_API_KEY')}"}, timeout=300)
            return r["choices"][0]["message"]["content"]
        except Exception as err:
            raise ModelError(f"openrouter: {str(err)[:200]}") from err


def _has_sdk() -> bool:
    try:
        import anthropic  # noqa: F401
        return True
    except ImportError:
        return False


def pick(name: str | None = None) -> Engine:
    """The strongest model this install can reach. Raises when none is configured: the deep pass never falls back
    to a weak model or to rules, because its whole point is frontier-model judgment."""
    name = name or os.environ.get("NETWORK_DEEP_ENGINE")
    if name:
        return {"anthropic": Anthropic, "claude": ClaudeCLI, "codex": Codex, "openrouter": OpenRouter}[name]()
    if env_key("ANTHROPIC_API_KEY") and _has_sdk():
        return Anthropic()
    if ClaudeCLI.available():
        return ClaudeCLI()
    if env_key("OPENROUTER_API_KEY"):
        return OpenRouter()
    raise ModelError("no frontier model configured: set ANTHROPIC_API_KEY (Claude Opus 5.5), log in the claude CLI, "
                     "set OPENROUTER_API_KEY, or NETWORK_DEEP_ENGINE=codex for a local example run")
