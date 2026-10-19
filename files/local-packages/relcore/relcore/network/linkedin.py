"""Guardrails for reading a prospect's LinkedIn connections through OUR dedicated account.

LinkedIn shows a person's connection list only to their own first-degree connections. So the reader works like this:
our dedicated account sends one connection request to the profile URL the prospect gave us; once they accept, the
agent's browser session (browser-box, logged into our account, never theirs) opens their connections list and saves
what it sees as linkedin.json ([{name, headline, url, connected_on}]) in the run's sources folder.

This module is the part code must own: the caps and the stop rule. The agent calls `allow()` before every invite
and every list page, `record()` after, and `block()` the moment LinkedIn shows a checkpoint, CAPTCHA, warning or
"too many requests". A blocked account stays blocked until a human clears it; nothing here solves or routes around
a challenge, and no messages are sent from this account in v1.
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path

DEFAULTS = {"invite": int(os.environ.get("NETWORK_LI_DAILY_INVITES", "15")),
            "page": int(os.environ.get("NETWORK_LI_PAGES_PER_HOUR", "20")),
            "page_day": int(os.environ.get("NETWORK_LI_PAGES_PER_DAY", "120"))}
WINDOW = {"invite": 86400, "page": 3600, "page_day": 86400}
KIND_OF = {"invite": "invite", "page": "page", "page_day": "page"}  # page_day counts the same page events over a day


class Ledger:
    def __init__(self, home: Path, account: str = "default"):
        self.path = Path(home) / "linkedin-reader" / f"{account}.json"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.data = json.loads(self.path.read_text()) if self.path.exists() else {"events": [], "blocked": None}

    def _save(self) -> None:
        self.path.write_text(json.dumps(self.data))

    def _recent(self, kind: str, now: float) -> int:
        return sum(1 for e in self.data["events"] if e["kind"] == KIND_OF[kind] and now - e["at"] < WINDOW[kind])

    def allow(self, kind: str, now: float | None = None) -> dict:
        """{'ok': bool, 'reason': str, 'left': int} for kind 'invite' or 'page'."""
        now = now or time.time()
        if self.data.get("blocked"):
            return {"ok": False, "reason": f"blocked: {self.data['blocked']['reason']} (a human must clear it)", "left": 0}
        caps = ("invite",) if kind == "invite" else ("page", "page_day")
        for cap in caps:
            if DEFAULTS[cap] - self._recent(cap, now) <= 0:
                per = "hour" if cap == "page" else "day"
                return {"ok": False, "reason": f"{KIND_OF[cap]} cap reached ({DEFAULTS[cap]} per {per})", "left": 0}
        return {"ok": True, "reason": "", "left": min(DEFAULTS[c] - self._recent(c, now) for c in caps)}

    def record(self, kind: str, target: str, now: float | None = None) -> None:
        """Always records: the invite or page view already happened, so it counts even past a cap."""
        now = now or time.time()
        self.data["events"] = [e for e in self.data["events"] if now - e["at"] < 86400 * 2] + \
            [{"kind": kind, "target": target, "at": now}]
        self._save()

    def block(self, reason: str, now: float | None = None) -> None:
        self.data["blocked"] = {"reason": reason, "at": now or time.time()}
        self._save()

    def clear(self) -> None:
        """Owner only (CLI), after checking the account by hand."""
        self.data["blocked"] = None
        self._save()

    def status(self, now: float | None = None) -> dict:
        now = now or time.time()
        return {"blocked": self.data.get("blocked"), "invites_left_today": max(0, DEFAULTS["invite"] - self._recent("invite", now)),
                "pages_left_this_hour": max(0, DEFAULTS["page"] - self._recent("page", now)),
                "pages_left_today": max(0, DEFAULTS["page_day"] - self._recent("page_day", now))}
