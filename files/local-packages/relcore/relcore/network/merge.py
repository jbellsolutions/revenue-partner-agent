"""One person, one record: merge Contacts from every source by strong identity.

Strong identities merge automatically: email, phone, a social profile (linkedin:in/..., instagram:...) and a CRM key.
Name alone never merges. Name plus company is only a *candidate*: it is listed for review and kept apart, because two
"Dan Ortiz"es at different jobs are two people and one Dan at the same company is probably one.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field

from .. import normalize
from .sources import handle_key


def strong_ids(c: dict) -> list[str]:
    out = []
    if c.get("email"):
        out.append("email:" + c["email"])
    if c.get("phone"):
        out.append("phone:" + c["phone"])
    for platform, value in (c.get("handles") or {}).items():
        k = handle_key(platform, value)
        if k:
            out.append("handle:" + k)
    if c["source"] == "crm":
        out.append("crm:" + c["key"])
    return out


def ref_ids(value: str) -> list[str]:
    """Identities for a bare reference in a who-knows-who pair (an email or a profile url)."""
    from .sources import platform_of
    value = (value or "").strip()
    if "@" in value and "/" not in value:
        e = normalize.email(value)
        return ["email:" + e] if e else []
    p = platform_of(value)
    k = handle_key(p, value) if p else None
    return ["handle:" + k] if k else []


@dataclass
class Network:
    people: dict = field(default_factory=dict)      # pid -> merged person
    index: dict = field(default_factory=dict)       # identity -> pid
    knows: list = field(default_factory=list)       # (pid, pid, seen_on)
    candidates: list = field(default_factory=list)  # possible same person, not merged
    contacts: int = 0
    by_source: dict = field(default_factory=dict)   # source -> contacts read

    def totals(self) -> dict:
        multi = sum(1 for p in self.people.values() if len(p["sources"]) > 1)
        return {"contacts": self.contacts, "people": len(self.people), "multi_source": multi}


def _pid(ids: list[str], fallback: str) -> str:
    seed = sorted(ids)[0] if ids else fallback
    return "p_" + hashlib.sha256(seed.encode()).hexdigest()[:10]


def _absorb(person: dict, c: dict) -> None:
    person["sources"].add(c["source"])
    person["records"].append({"source": c["source"], "key": c["key"]})
    for k in ("name", "first_name", "last_name", "title", "company", "headline", "location", "email", "phone"):
        if c.get(k) and not person.get(k):
            person[k] = c[k]
    # A CRM or contacts record is the best source for title and company: it overrides a social headline.
    if c["source"] in ("crm", "contacts") and c.get("title"):
        person["title"] = c["title"]
    if c["source"] in ("crm", "contacts") and c.get("company"):
        person["company"] = c["company"]
    for platform, value in (c.get("handles") or {}).items():
        person["handles"].setdefault(platform, value)
    for k in ("tags", "notes"):
        if c.get(k) and c[k] not in person[k]:
            person[k].append(c[k])
    for k in ("last_activity", "connected_on"):
        if c.get(k) and c[k] > (person.get(k) or ""):
            person[k] = c[k]


def build(contacts: list[dict], mutuals: list[dict] | None = None) -> Network:
    net = Network()
    for c in contacts:
        net.contacts += 1
        net.by_source[c["source"]] = net.by_source.get(c["source"], 0) + 1
        ids = strong_ids(c)
        hits = {net.index[i] for i in ids if i in net.index}
        if not hits:
            pid = _pid(ids, f"{c['source']}|{c['key']}")
            while pid in net.people:
                pid = pid + "x"
            net.people[pid] = {"id": pid, "sources": set(), "records": [], "handles": {}, "tags": [], "notes": [],
                               "identities": set()}
        else:
            pid = sorted(hits)[0]
            for other in sorted(hits)[1:]:  # this contact bridges two people we had apart: fold them together
                o = net.people.pop(other)
                for r in o["records"]:
                    net.people[pid]["records"].append(r)
                net.people[pid]["sources"] |= o["sources"]
                net.people[pid]["identities"] |= o["identities"]
                for k, v in o["handles"].items():
                    net.people[pid]["handles"].setdefault(k, v)
                for k in ("name", "title", "company", "email", "phone", "location", "headline"):
                    if o.get(k) and not net.people[pid].get(k):
                        net.people[pid][k] = o[k]
                for i in o["identities"]:
                    net.index[i] = pid
        person = net.people[pid]
        _absorb(person, c)
        person["identities"] |= set(ids)
        for i in ids:
            net.index[i] = pid
    # Candidates (flagged for the owner, never merged): same name and company is a likely match; same name where
    # at most one side names a company is a possible one. Different companies are treated as different people.
    by_name: dict = {}
    for pid, p in net.people.items():
        if p.get("name"):
            by_name.setdefault(normalize.text_key(p["name"]), []).append(pid)
    for _, pids in sorted(by_name.items()):
        for i, a in enumerate(pids):
            for b in pids[i + 1:]:
                ca, cb = (normalize.text_key(net.people[x].get("company") or "") for x in (a, b))
                if ca and cb and ca != cb:
                    continue
                likely = bool(ca and ca == cb)
                seen_on = " and ".join(sorted(net.people[a]["sources"] | net.people[b]["sources"]))
                net.candidates.append({"a": a, "b": b, "confidence": "likely" if likely else "possible",
                                       "reason": "same name and company, no shared email, phone or profile" if likely
                                       else f"same name on {seen_on}; nothing else to confirm it"})
    for m in mutuals or []:
        a = next((net.index[i] for i in ref_ids(m["a"]) if i in net.index), None)
        b = next((net.index[i] for i in ref_ids(m["b"]) if i in net.index), None)
        if a and b and a != b:
            net.knows.append((a, b, m.get("seen_on") or ""))
    return net
