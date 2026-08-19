from __future__ import annotations

from .models import TaskSpec

# Proxy execution is intentionally unavailable in this locked image. These
# helpers retain the upstream call shape while preventing process environment,
# task fields, or direct imports from constructing a network proxy route.


def decodo_ports() -> tuple[int, ...]:
    return ()


def sticky_port_for_key(key: str, ports: tuple[int, ...] | None = None) -> int:
    raise RuntimeError("proxy routing is disabled in this image")


def build_decodo_proxy_url(*, profile_name: str | None = None, port: int | None = None) -> None:
    if profile_name is not None or port is not None:
        raise ValueError("proxy routing is disabled in this image")
    return None


def resolve_proxy_url(task: TaskSpec) -> None:
    explicit = (getattr(task, "proxy", None) or "").strip()
    if explicit:
        raise ValueError("proxy routing is disabled in this image")
    return None


def playwright_proxy_settings(proxy_url: str | None) -> None:
    if proxy_url:
        raise ValueError("proxy routing is disabled in this image")
    return None


def proxy_dict_for_requests(proxy_url: str | None) -> None:
    if proxy_url:
        raise ValueError("proxy routing is disabled in this image")
    return None
