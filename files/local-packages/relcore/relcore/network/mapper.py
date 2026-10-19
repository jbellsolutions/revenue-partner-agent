"""Where's the next revenue spot: score every person, find the warm path to them, and write the NetworkReport.

Scoring is plain code (spec section 3), so the same network always ranks the same way:
  warmth = min(sources, 3)/3 * 0.5 + recency * 0.3 + relationship * 0.2
  buyers and partners:  spot = fit * (0.6 + 0.4 * warmth)
  connectors:           spot = reach * (0.6 + 0.4 * warmth)   reach = buyer-fit people they know / most anyone knows
Paths run from "me" (the client) through people they know, shortest first.
"""
from __future__ import annotations

from collections import deque
from datetime import date

from .merge import Network

RELATIONSHIP_TAGS = ("customer", "client", "partner", "affiliate", "referral", "won", "closed")
LOOP_WORDS = ("check back", "follow up", "next quarter", "in the spring", "after tax season", "not right now", "maybe later")


def _recency(p: dict, today: date) -> float:
    stamp = (p.get("last_activity") or p.get("connected_on") or "")[:10]
    try:
        d = date.fromisoformat(stamp if len(stamp) == 10 else stamp[:7] + "-01")
    except ValueError:
        return 0.2
    days = (today - d).days
    return 1.0 if days <= 90 else 0.7 if days <= 365 else 0.4 if days <= 730 else 0.2


def warmth(p: dict, today: date) -> float:
    rel = 1.0 if any(t in " ".join(p.get("tags") or []).lower() for t in RELATIONSHIP_TAGS) else 0.0
    return round(min(len(p["sources"]), 3) / 3 * 0.5 + _recency(p, today) * 0.3 + rel * 0.2, 3)


def open_loops(p: dict) -> list[str]:
    text = " ".join((p.get("notes") or []) + (p.get("tags") or [])).lower()
    loops = []
    if any(w in text for w in LOOP_WORDS):
        loops.append("They asked you to check back")
    if "old quote" in text or "quote" in text and "customer" not in text:
        loops.append("An old quote that never closed")
    return loops


def adjacency(net: Network) -> dict:
    adj = {pid: set() for pid in net.people}
    adj["me"] = set(net.people)  # the client knows everyone in their own network directly
    for a, b, _ in net.knows:
        adj[a].add(b)
        adj[b].add(a)
    return adj


def path_to(adj: dict, target: str, via_first: set | None = None, max_hops: int = 3) -> list[str]:
    """Shortest path from me. When `via_first` is given (a person the client knows only weakly), prefer a two-hop
    path through someone stronger, because a warm intro beats a cold DM."""
    if via_first:
        for mid in sorted(via_first):
            if target in adj.get(mid, ()):
                return ["me", mid, target]
    seen, q = {"me": None}, deque(["me"])
    while q:
        n = q.popleft()
        if n == target:
            out = []
            while n is not None:
                out.append(n)
                n = seen[n]
            return out[::-1]
        if len(_unwind(seen, n)) > max_hops:
            continue
        for m in sorted(adj.get(n, ())):
            if m not in seen:
                seen[m] = n
                q.append(m)
    return []


def _unwind(seen, n):
    out = []
    while n is not None:
        out.append(n)
        n = seen[n]
    return out


def score(net: Network, classes: dict, today: date) -> dict:
    """pid -> {warmth, reach, spot_score, kind}."""
    adj = adjacency(net)
    buyerish = {pid for pid, c in classes.items() if c["segment"] == "buyer" and c["fit"] >= 0.5}
    knows_buyers = {pid: len(adj[pid] & buyerish) for pid in net.people}
    most = max(knows_buyers.values() or [0]) or 1
    out = {}
    for pid, p in net.people.items():
        c = classes.get(pid) or {"segment": "other", "fit": 0}
        w = warmth(p, today)
        reach = round(knows_buyers[pid] / most, 3)
        if c["segment"] in ("buyer", "partner"):
            s = c["fit"] * (0.6 + 0.4 * w)
        elif c["segment"] == "connector" or reach >= 0.5:
            s = max(reach, c["fit"] * 0.5) * (0.6 + 0.4 * w)
        else:
            s = 0.0
        out[pid] = {"warmth": w, "reach": reach, "knows_buyers": knows_buyers[pid], "spot_score": round(s, 3)}
    return out


def report(net: Network, classes: dict, client: dict, *, today: date, sources: list[dict], spots: int = 12,
           sample: int = 40, writer=None, example: bool = False) -> dict:
    """The NetworkReport (spec section 5). `writer(person, path, kind)` adds why/opener; a plain template otherwise."""
    from . import reasoning
    writer = writer or reasoning.template
    adj = adjacency(net)
    scores = score(net, classes, today)
    seg_count = {s: 0 for s in ("buyer", "partner", "connector")}
    for c in classes.values():
        if c["segment"] in seg_count:
            seg_count[c["segment"]] += 1
    strong = {pid for pid, p in net.people.items() if len(p["sources"]) > 1 or warmth(p, today) >= 0.6}
    ranked = sorted((pid for pid in net.people if scores[pid]["spot_score"] > 0),
                    key=lambda pid: (-scores[pid]["spot_score"], pid))
    out_spots, on_paths = [], set()
    for pid in ranked:
        if len(out_spots) >= spots:
            break
        c = classes[pid]
        kind = c["segment"] if c["segment"] in ("buyer", "partner") else "connector"
        weak = len(net.people[pid]["sources"]) == 1 and warmth(net.people[pid], today) < 0.45
        path = path_to(adj, pid, via_first={s for s in strong if s != pid and pid in adj[s]} if weak else None)
        on_paths |= set(path) - {"me"}
        words = writer(_public(net.people[pid], classes, scores), [_name(net, x) for x in path], kind)
        out_spots.append({"person": pid, "kind": kind, "score": scores[pid]["spot_score"], "path": path, **words})
    shown = list(dict.fromkeys([s["person"] for s in out_spots] + sorted(on_paths) +
                               sorted(net.people, key=lambda pid: (-scores[pid]["spot_score"], pid))[:sample]))
    people = [_public(net.people[pid], classes, scores) for pid in shown]
    shown_set = set(shown)
    edges = [{"from": "me", "to": pid, "kind": "connected_on", "sources": sorted(net.people[pid]["sources"])} for pid in shown]
    edges += [{"from": a, "to": b, "kind": "knows", "source": src} for a, b, src in net.knows if a in shown_set and b in shown_set]
    totals = {**net.totals(), **{s + "s": n for s, n in seg_count.items()}}
    return {"version": 1, "example": bool(example or client.get("example")),
            "client": {k: client.get(k) for k in ("name", "offer", "buyers", "partner_types", "value_per_customer")},
            "sources": sources, "totals": totals, "candidates": net.candidates[:50],
            "people": people, "edges": edges, "spots": out_spots,
            "engine": sorted({c.get("engine", "") for c in classes.values()})}


def _name(net: Network, pid: str) -> str:
    return "you" if pid == "me" else (net.people[pid].get("name") or "someone")


def _public(p: dict, classes: dict, scores: dict) -> dict:
    """What a report may show about a person: no raw notes, emails only as presence."""
    c = classes.get(p["id"]) or {}
    s = scores.get(p["id"]) or {}
    return {"id": p["id"], "name": p.get("name") or "", "title": p.get("title") or "", "company": p.get("company") or "",
            "industry": p.get("industry") or "", "location": p.get("location") or "", "sources": sorted(p["sources"]),
            "identities": sorted({i.split(":", 1)[0] for i in p["identities"]}),
            "segment": c.get("segment", "other"), "fit": c.get("fit", 0), "partner_type": c.get("partner_type"),
            "confidence": c.get("confidence", 0), "warmth": s.get("warmth", 0), "spot_score": s.get("spot_score", 0),
            "knows_buyers": s.get("knows_buyers", 0), "open_loops": open_loops(p)}
