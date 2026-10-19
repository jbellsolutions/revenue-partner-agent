"""Read every place a business knows people into one shape: a Contact.

A Contact is a plain dict:
  source      linkedin | crm | email_list | contacts | facebook | instagram | x | tiktok | youtube | threads | web
  key         stable id inside that source (profile url, crm id, email)
  name, first_name, last_name, title, company, headline, location
  email, phone
  handles     {platform: url-or-handle}   e.g. {"linkedin": "https://www.linkedin.com/in/dan"}
  tags, notes, last_activity, connected_on   (strings, may be empty)

Readers never call the network. The LinkedIn and social readers parse what the agent's browser session or a
platform data download already saved; the CRM readers parse exports or the JSON a read-only API call returned.
`detect()` picks a reader from the file name and its columns, so a dropped file needs no instructions.
"""
from __future__ import annotations

import csv
import io
import json
import re
from pathlib import Path

from .. import normalize

PLATFORMS = ("linkedin", "facebook", "instagram", "x", "tiktok", "youtube", "threads")
SOCIAL_HOSTS = {"linkedin.com": "linkedin", "facebook.com": "facebook", "fb.com": "facebook", "instagram.com": "instagram",
                "x.com": "x", "twitter.com": "x", "tiktok.com": "tiktok", "youtube.com": "youtube", "threads.net": "threads"}


def contact(source: str, key: str, **kw) -> dict:
    name = (kw.get("name") or " ".join(x for x in (kw.get("first_name"), kw.get("last_name")) if x) or "").strip()
    first = kw.get("first_name") or (name.split(" ")[0] if name else "")
    last = kw.get("last_name") or (" ".join(name.split(" ")[1:]) if name else "")
    headline = (kw.get("headline") or "").strip()
    title, company = (kw.get("title") or "").strip(), (kw.get("company") or "").strip()
    if headline and not (title or company):
        title, company = split_headline(headline)
    return {"source": source, "key": str(key), "name": name, "first_name": first.strip(), "last_name": last.strip(),
            "title": title, "company": company, "headline": headline, "location": (kw.get("location") or "").strip(),
            "email": normalize.email(kw.get("email") or "") or "", "phone": normalize.phone(kw.get("phone") or "") or "",
            "handles": {k: v for k, v in (kw.get("handles") or {}).items() if v}, "tags": (kw.get("tags") or "").strip(),
            "notes": (kw.get("notes") or "").strip(), "last_activity": (kw.get("last_activity") or "").strip(),
            "connected_on": (kw.get("connected_on") or "").strip()}


def split_headline(headline: str) -> tuple[str, str]:
    """'VP Operations at Beacon Engineering' -> ('VP Operations', 'Beacon Engineering'). Leaves unknown shapes as title."""
    m = re.match(r"^(.*?)\s+(?:at|@)\s+(.+?)(?:\s*[|·,]\s.*)?$", headline.strip())
    return (m.group(1).strip(), m.group(2).strip()) if m else (headline.strip(), "")


def handle_key(platform: str, value: str) -> str | None:
    """A stable identity for a social profile: 'linkedin:in/dan-ortiz', 'instagram:danortiz'."""
    value = (value or "").strip()
    if not value:
        return None
    v = re.sub(r"^https?://", "", value.lower()).removeprefix("www.").removeprefix("m.").split("?")[0].rstrip("/")
    for host in SOCIAL_HOSTS:
        if v.startswith(host + "/"):
            v = v[len(host) + 1:]
            break
    v = v.lstrip("@")
    return f"{platform}:{v}" if v else None


def platform_of(url: str) -> str | None:
    host = re.sub(r"^https?://", "", (url or "").lower()).removeprefix("www.").removeprefix("m.").split("/")[0]
    return SOCIAL_HOSTS.get(host)


# ------------------------------------------------------------------ helpers
def _rows(text: str) -> list[dict]:
    text = text.lstrip("﻿")
    # LinkedIn's own export puts a few note lines above the header.
    lines = text.splitlines()
    for i, line in enumerate(lines[:12]):
        if line.lower().startswith(("first name,", '"first name",')):
            text = "\n".join(lines[i:])
            break
    return [{(k or "").strip(): (v or "").strip() for k, v in r.items()} for r in csv.DictReader(io.StringIO(text))]


def _pick(row: dict, *names: str) -> str:
    low = {k.lower(): v for k, v in row.items()}
    for n in names:
        if low.get(n.lower()):
            return low[n.lower()]
    return ""


# ------------------------------------------------------------------ readers
def read_linkedin(text: str, kind: str) -> list[dict]:
    """Our reader's JSON ([{name, headline, url, connected_on}]) or LinkedIn's Connections.csv."""
    out = []
    if kind == "json":
        for r in json.loads(text):
            out.append(contact("linkedin", r.get("url") or r["name"], name=r.get("name"), headline=r.get("headline"),
                               location=r.get("location"), connected_on=r.get("connected_on"),
                               handles={"linkedin": r.get("url")}))
        return out
    for r in _rows(text):
        url = _pick(r, "URL", "Profile URL")
        out.append(contact("linkedin", url or _pick(r, "Email Address") or f"{_pick(r, 'First Name')} {_pick(r, 'Last Name')}",
                           first_name=_pick(r, "First Name"), last_name=_pick(r, "Last Name"), email=_pick(r, "Email Address"),
                           company=_pick(r, "Company"), title=_pick(r, "Position"), connected_on=_pick(r, "Connected On"),
                           handles={"linkedin": url}))
    return out


def read_crm(text: str, system: str = "crm") -> list[dict]:
    """GoHighLevel, HubSpot, Salesforce, Pipedrive and generic CRM exports (column names vary; all are tried)."""
    out = []
    for i, r in enumerate(_rows(text)):
        email = _pick(r, "Email", "Email Address", "E-mail")
        key = _pick(r, "Contact Id", "Record ID", "Id", "Contact ID") or email or f"row{i}"
        out.append(contact("crm", f"{system}:{key}", first_name=_pick(r, "First Name", "FirstName"),
                           last_name=_pick(r, "Last Name", "LastName"), name=_pick(r, "Full Name", "Name", "Contact Name"),
                           email=email, phone=_pick(r, "Phone", "Phone Number", "Mobile Phone", "MobilePhone"),
                           company=_pick(r, "Company Name", "Company", "Account Name", "Associated Company"),
                           title=_pick(r, "Job Title", "Title"), location=_pick(r, "City", "Mailing City"),
                           tags=_pick(r, "Tags", "Lifecycle Stage", "Lead Status", "Status"), notes=_pick(r, "Notes", "Description"),
                           last_activity=_pick(r, "Last Activity", "Last Activity Date", "Last Contacted", "LastActivityDate"),
                           handles={"linkedin": _pick(r, "LinkedIn", "LinkedIn URL", "LinkedIn Bio")}))
    return out


def read_email_list(text: str) -> list[dict]:
    """ESP exports: Mailchimp, ActiveCampaign, beehiiv, Kit, Klaviyo, Constant Contact."""
    out = []
    for r in _rows(text):
        email = _pick(r, "email", "Email Address", "Email", "E-mail")
        if not email:
            continue
        out.append(contact("email_list", email, email=email, first_name=_pick(r, "first_name", "First Name", "FNAME"),
                           last_name=_pick(r, "last_name", "Last Name", "LNAME"), tags=_pick(r, "tags", "TAGS", "Lists"),
                           last_activity=_pick(r, "subscribed", "Subscribed At", "OPTIN_TIME", "created_at")))
    return out


def read_contacts_csv(text: str) -> list[dict]:
    """Google Contacts and Outlook contact exports."""
    out = []
    for i, r in enumerate(_rows(text)):
        email = _pick(r, "E-mail 1 - Value", "E-mail Address", "Email 1", "Email")
        phone = _pick(r, "Phone 1 - Value", "Mobile Phone", "Business Phone", "Phone")
        out.append(contact("contacts", email or phone or f"row{i}", name=_pick(r, "Name"),
                           first_name=_pick(r, "Given Name", "First Name"), last_name=_pick(r, "Family Name", "Last Name"),
                           email=email, phone=phone, company=_pick(r, "Organization 1 - Name", "Company"),
                           title=_pick(r, "Organization 1 - Title", "Job Title"), notes=_pick(r, "Notes")))
    return out


def read_vcard(text: str) -> list[dict]:
    """iPhone, iCloud and Android .vcf exports."""
    out = []
    for i, block in enumerate(re.findall(r"BEGIN:VCARD(.*?)END:VCARD", text, flags=re.S | re.I)):
        field = lambda tag: next((ln.split(":", 1)[1].strip() for ln in block.splitlines()
                                  if ln.upper().split(";")[0].split(":")[0] == tag and ":" in ln), "")
        n = field("N").split(";")
        out.append(contact("contacts", field("EMAIL") or field("TEL") or f"vcard{i}", name=field("FN"),
                           last_name=n[0] if n and n[0] else "", first_name=n[1] if len(n) > 1 else "",
                           email=field("EMAIL"), phone=field("TEL"), company=field("ORG").split(";")[0], title=field("TITLE")))
    return out


def read_social(text: str, platform: str) -> list[dict]:
    """Followers, following or friends of a profile, as our reader saved them ([{name, url, city?}]) or the
    platform's own data download (Facebook friends_v2, Instagram string_list_data)."""
    data = json.loads(text)
    rows = []
    if isinstance(data, dict):
        for key in ("friends_v2", "friends", "relationships_followers", "relationships_following", "followers", "following"):
            if key in data:
                data = data[key]
                break
    for item in data if isinstance(data, list) else []:
        if "string_list_data" in item:  # Instagram data download
            for s in item["string_list_data"]:
                rows.append({"name": s.get("value"), "url": s.get("href")})
        else:
            rows.append(item)
    out = []
    for r in rows:
        url = r.get("url") or r.get("href") or ""
        name = r.get("name") or r.get("title") or r.get("value") or ""
        if not (url or name):
            continue
        out.append(contact(platform, url or name, name=name, location=r.get("city") or r.get("location"),
                           headline=r.get("bio") or r.get("headline"), handles={platform: url}))
    return out


def read_web(text: str) -> list[dict]:
    """People the agent found on pages (team, testimonials, partners, podcast guests): [{name, title, company, url, page}]."""
    out = []
    for r in json.loads(text):
        url = r.get("url") or ""
        plat = platform_of(url)
        out.append(contact("web", url or f"{r.get('name')}|{r.get('page')}", name=r.get("name"), title=r.get("title"),
                           company=r.get("company"), headline=r.get("headline"), notes=r.get("page") or "",
                           handles={plat: url} if plat else {}))
    return out


def read_mutuals(text: str) -> list[dict]:
    """Who-knows-who seen while reading: [{a, b, seen_on}] where a and b are profile urls or emails."""
    return [m for m in json.loads(text) if m.get("a") and m.get("b")]


# ------------------------------------------------------------------ detection
def detect(path: Path) -> tuple[str, str]:
    """(reader, platform) for a dropped file. Raises ValueError for a file no reader understands."""
    name = path.name.lower()
    text = path.read_text(errors="replace")[:4000].lower()
    if name.endswith(".vcf") or "begin:vcard" in text:
        return "vcard", "contacts"
    if name.startswith("mutuals"):
        return "mutuals", "mutuals"
    if name.endswith(".json"):
        for p in PLATFORMS:
            if name.startswith(p) or f"{p}.com/" in text or (p == "x" and "x.com/" in text):
                return ("linkedin_json", "linkedin") if p == "linkedin" else ("social", p)
        if "friends_v2" in text:
            return "social", "facebook"
        if "string_list_data" in text:
            return "social", "instagram"
        if name.startswith(("web", "pages", "people")):
            return "web", "web"
    if name.endswith(".csv"):
        head = text.splitlines()[0] if text else ""
        joined = text[:1500]
        if "connected on" in joined and "first name" in joined:
            return "linkedin_csv", "linkedin"
        if "e-mail 1 - value" in head or "given name" in head or ("e-mail address" in head and "job title" in head):
            return "contacts_csv", "contacts"
        if name.startswith(("email", "subscribers", "list", "audience")) or head.startswith(("email,", '"email"', "email address")):
            return "email_list", "email_list"
        return "crm_csv", "crm"
    raise ValueError(f"{path.name}: not a contacts file this reader knows")


def read_path(path: Path) -> tuple[list[dict], list[dict]]:
    """Contacts and who-knows-who pairs from one file."""
    reader, platform = detect(path)
    text = path.read_text(errors="replace")
    if reader == "mutuals":
        return [], read_mutuals(text)
    contacts = {
        "vcard": lambda: read_vcard(text), "linkedin_json": lambda: read_linkedin(text, "json"),
        "linkedin_csv": lambda: read_linkedin(text, "csv"), "social": lambda: read_social(text, platform),
        "web": lambda: read_web(text), "contacts_csv": lambda: read_contacts_csv(text),
        "email_list": lambda: read_email_list(text), "crm_csv": lambda: read_crm(text, path.stem.split("-")[0]),
    }[reader]()
    return contacts, []
