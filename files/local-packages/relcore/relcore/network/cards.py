"""Write a mapped network into living contact cards (the same store and Obsidian vault as every other card).

Each merged person becomes one person card with every identity it was found under, plus:
- first name, last name, title (plain fields) and a role fact;
- the sources it came from (Sources hub) and where they are (Regions hub);
- where they work, as a partner card for the company (`works_at`);
- one `connected_on` link from the owner listing every platform they're connected on;
- `knows` links for every who-knows-who pair seen while reading.

Classification is model judgment, so it is tagged (PartnerTypes / Industries hubs) with source "research",
never written into a protected field. The owner corrects it on the card like any other research.

This is a bulk import: the owner runs it (`relcore network apply`), never the agent, matching
data.export_or_bulk_import. Vault rendering runs once at the end, not per card.
"""
from __future__ import annotations

from .. import normalize
from .merge import Network

SOURCE_LABELS = {"linkedin": "LinkedIn", "crm": "CRM", "email_list": "Email list", "contacts": "Phone and contacts",
                 "facebook": "Facebook", "instagram": "Instagram", "x": "X", "tiktok": "TikTok", "youtube": "YouTube",
                 "threads": "Threads", "web": "Web pages"}


def apply(store, net: Network, client: dict, classes: dict | None = None) -> dict:
    s = store
    render, s.render_enabled = s.render_enabled, False
    me = s.upsert("person", client.get("name") or "Me", identities={"handle": "owner:me"}, internal=True,
                  by="import", source="record", source_ref="network:owner")
    ids, companies, refused = {}, {}, []
    try:
        for pid, p in net.people.items():
            idents = {"email": p.get("email") or None, "phone": p.get("phone") or None,
                      "handle": [i.split(":", 1)[1] for i in sorted(p["identities"]) if i.startswith("handle:")] or None,
                      "crm": [r["key"] for r in p["records"] if r["source"] == "crm"] or None}
            fields = {"first_name": normalize.first_name(p.get("first_name") or p.get("name") or ""),
                      "last_name": (p.get("last_name") or "").strip(), "title": p.get("title") or ""}
            eid = s.upsert("person", p.get("name") or p.get("email") or "Unknown", identities=idents,
                           fields={k: v for k, v in fields.items() if v}, by="import", source="record",
                           source_ref=f"network:{pid}")
            ids[pid] = eid
            if p.get("company"):
                key = normalize.text_key(p["company"])
                if key not in companies:
                    companies[key] = s.upsert("partner", p["company"], identities={"handle": f"company:{key}"},
                                              by="import", source="record", source_ref=f"network:company:{key}")
                s.link(eid, "works_at", companies[key], source="record", source_ref=f"network:{pid}")
            s.link(me, "connected_on", eid, source="record", source_ref=f"network:{pid}",
                   props={"platforms": sorted(p["sources"]), "since": p.get("connected_on") or ""})
            hubs = {"Sources": [SOURCE_LABELS.get(x, x) for x in sorted(p["sources"])]}
            if p.get("location"):
                hubs["Regions"] = [normalize.region(p["location"])]
            facts = [{"slot": "role", "value": p["title"] + (f" at {p['company']}" if p.get("company") else "")}] \
                if p.get("title") else []
            r = s.remember(eid, facts=facts, hubs=hubs, note="\n".join(p.get("notes") or []) or None, source="record",
                           source_ref=f"network:{pid}", by="import", recorder="import")
            refused += [f"{pid}: {x}" for x in r["report"]["refused"]]
            c = (classes or {}).get(pid) or {}
            tags = {}
            if c.get("partner_type"):
                tags["PartnerTypes"] = [c["partner_type"]]
            if c.get("industry"):
                tags["Industries"] = [c["industry"]]
            if tags:
                s.remember(eid, hubs=tags, source="research", source_ref=f"network:classify:{c.get('engine', '')}:{pid}",
                           by="model", recorder="network-map")
        for a, b, seen_on in net.knows:
            s.link(ids[a], "knows", ids[b], props={"seen_on": seen_on}, source="record", source_ref="network:mutuals")
    finally:
        s.render_enabled = render
    if render:
        s.vault.render_around(set(ids.values()) | {me} | set(companies.values()))
    s.audit("network_apply", me, {"people": len(ids), "companies": len(companies), "knows": len(net.knows)}, actor="owner")
    return {"people": len(ids), "companies": len(companies), "knows": len(net.knows), "owner": me, "refused": refused}
