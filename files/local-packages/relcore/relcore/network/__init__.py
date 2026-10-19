"""Network map: everyone a client already knows, as living contact cards, and where the next revenue is.

A run is a folder:
    <run>/client.json        what the client sells, to whom, through which partner types
    <run>/sources/*          one file per source (CRM export, LinkedIn reader output, email list, contacts, social)
                             (files may also sit next to client.json; reserved names below are skipped)
The pipeline reads each source (one progress bar each), merges people across sources, classifies them
(Jev, then GLM, then rules), scores and paths them, and writes <run>/report.json (the NetworkReport) plus
<run>/classes.json, so `apply` writes the same judgments the report showed without asking a model again.

    python3 -m relcore network plan <run>              dry run: what each source holds and how people merge
    python3 -m relcore network run <run> [--classifier rules|llm|jev] [--spots 12] [--example]
    python3 -m relcore network report <run> [--spots]  print the report (or just the spots)
    python3 -m relcore network apply <run> --yes       owner only: write the cards into this install
    python3 -m relcore network li-status [--account default]
    python3 -m relcore network li-clear --account default --yes    owner only, after checking the account by hand

Agent tools (MCP) can plan, map (report only, no cards), read the report and job, and check and record the
LinkedIn reader's caps. Writing cards is a bulk import, so it stays the owner's CLI.
"""
from __future__ import annotations

import json
import os
import re
import threading
from datetime import date
from pathlib import Path

from .. import clock
from . import classify, mapper, merge, reasoning
from .job import Job
from .linkedin import Ledger
from .sources import detect, read_path

RESERVED = {"client.json", "truth.json", "job.json", "report.json", "classes.json", "plan.json"}
LABELS = {"linkedin": "LinkedIn", "crm": "CRM", "email_list": "Email list", "contacts": "Phone and contacts",
          "facebook": "Facebook", "instagram": "Instagram", "x": "X", "tiktok": "TikTok", "youtube": "YouTube",
          "threads": "Threads", "web": "Web pages", "mutuals": "Mutual connections"}


def source_files(run: Path) -> list[Path]:
    run = Path(run)
    folder = run / "sources" if (run / "sources").is_dir() else run
    return sorted(f for f in folder.iterdir() if f.is_file() and f.name not in RESERVED and not f.name.startswith("."))


def _client(run: Path) -> dict:
    return json.loads((Path(run) / "client.json").read_text())


def _read(run: Path, job: Job | None = None) -> tuple[list[dict], list[dict], list[dict]]:
    contacts, mutuals, sources = [], [], []
    for f in source_files(run):
        name = f.stem
        if job:
            job.source(name, state="reading")
        try:
            platform = detect(f)[1]
            c, m = read_path(f)
        except (ValueError, OSError, json.JSONDecodeError) as err:
            if job:
                job.source(name, state="skipped", note=str(err)[:200])
            sources.append({"source": name, "label": name, "state": "skipped", "found": 0, "note": str(err)[:200]})
            continue
        contacts += c
        mutuals += m
        found = len(c) or len(m)
        if job:
            job.source(name, state="done", found=found, total=found)
        sources.append({"source": name, "platform": platform, "label": LABELS.get(platform, platform), "state": "done",
                        "found": found, "unit": "pairs" if m and not c else "people", "pairs": len(m)})
    return contacts, mutuals, sources


def _today(client: dict) -> date:
    return date.fromisoformat(client["today"]) if client.get("today") else clock.now().date()


def plan(run: Path) -> dict:
    """What a run would do, without classifying, scoring or writing anything."""
    contacts, mutuals, sources = _read(run)
    net = merge.build(contacts, mutuals)
    return {"sources": sources, "totals": net.totals(), "candidates": len(net.candidates),
            "candidate_sample": net.candidates[:10]}


def run(run_dir: Path, *, classifier=None, writer=None, spots: int = 12, example: bool | None = None) -> dict:
    run_dir = Path(run_dir)
    client = _client(run_dir)
    job = Job(run_dir, [f.stem for f in source_files(run_dir)])
    try:
        contacts, mutuals, sources = _read(run_dir, job)
        job.stage("merge", 0, len(contacts))
        net = merge.build(contacts, mutuals)
        job.stage("merge", len(contacts), len(contacts))
        people = list(net.people.values())
        clf = classifier or classify.pick()
        job.stage("classify", 0, len(people))
        classes = clf.classify(people, client, progress=lambda d, t: job.stage("classify", d, t))
        job.stage("map", 0, len(people))
        scores = mapper.score(net, classes, _today(client))
        job.stage("map", len(people), len(people))
        base = writer or (reasoning.llm(client) if not isinstance(clf, classify.Rules) else reasoning.template)
        count = {"n": 0}

        def counted(person, path, kind):
            out = base(person, path, kind)
            count["n"] += 1
            job.stage("spots", count["n"], min(spots, sum(1 for s in scores.values() if s["spot_score"] > 0)))
            return out
        report = mapper.report(net, classes, client, today=_today(client), sources=sources, spots=spots,
                               writer=counted, example=bool(example) if example is not None else False)
        _write(run_dir / "report.json", report)
        _write(run_dir / "classes.json", classes)
        job.finish("complete")
        return report
    except Exception as err:
        job.state["error"] = str(err)[:300]
        job.finish("failed")
        raise


def apply(run_dir: Path, store) -> dict:
    """Owner only. Writes the run's people into the store as cards, using the judgments saved by `run`."""
    from . import cards
    run_dir = Path(run_dir)
    if not (run_dir / "classes.json").exists():
        raise SystemExit("run the map first (relcore network run <run>); apply writes what the report showed")
    contacts, mutuals, _ = _read(run_dir)
    net = merge.build(contacts, mutuals)
    return cards.apply(store, net, _client(run_dir), json.loads((run_dir / "classes.json").read_text()))


def _write(path: Path, data) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=1, sort_keys=True, default=sorted))
    os.replace(tmp, path)


# ---------------------------------------------------------------- MCP tools (agent side)
RUN_ID = re.compile(r"[a-z0-9][a-z0-9-]{0,63}")


def _run_dir(srv, run_id: str) -> Path:
    if not RUN_ID.fullmatch(run_id or ""):
        raise ValueError("run is a short slug: lowercase letters, digits and dashes")
    d = srv.paths.home / "network" / run_id
    if not (d / "client.json").exists():
        raise LookupError(f"no run {run_id}: put client.json and the source files in {d}")
    return d


def _t_plan(srv, run):
    return plan(_run_dir(srv, run))


def _t_map(srv, run, spots=12, wait=False):
    d = _run_dir(srv, run)
    if wait:
        r = run_pipeline(d, spots=spots)
        return {"state": "complete", "totals": r["totals"], "spots": len(r["spots"])}
    threading.Thread(target=_quiet, args=(d, spots), daemon=True).start()
    return {"state": "started", "job": "call rel_network_job with this run to watch progress"}


def _quiet(d, spots):
    try:
        run_pipeline(d, spots=spots)
    except Exception:
        pass  # the job file records the failure


def _t_job(srv, run):
    d = _run_dir(srv, run)
    return json.loads((d / "job.json").read_text()) if (d / "job.json").exists() else {"state": "not_started"}


def _t_report(srv, run, spots_only=False):
    d = _run_dir(srv, run)
    if not (d / "report.json").exists():
        return {"state": "not_mapped", "next": "rel_network_map"}
    r = json.loads((d / "report.json").read_text())
    if spots_only:
        names = {p["id"]: p for p in r["people"]}
        return {"totals": r["totals"], "spots": [{**s, "person_card": names.get(s["person"])} for s in r["spots"]]}
    return r


def _t_li_allow(srv, kind, account="default"):
    return Ledger(srv.paths.home, account).allow(kind)


def _t_li_record(srv, kind, target, account="default"):
    led = Ledger(srv.paths.home, account)
    led.record(kind, target)  # it already happened: always counted, even past a cap
    return {**led.status(), "next": led.allow(kind)}


def _t_li_block(srv, reason, account="default"):
    Ledger(srv.paths.home, account).block(reason)
    srv.store.audit("linkedin_reader_blocked", None, {"account": account, "reason": reason[:200]}, actor="agent")
    return {"blocked": True, "next": "stop all LinkedIn work on this account and tell the owner; only the owner can clear it"}


run_pipeline = run
_RUN = {"type": "string", "pattern": "^[a-z0-9][a-z0-9-]{0,63}$", "description": "The run folder name under <home>/network/."}
_KIND = {"type": "string", "enum": ["invite", "page"]}
_ACCOUNT = {"type": "string", "pattern": "^[a-z0-9-]{1,32}$"}
MCP_TOOLS = [
    {"name": "rel_network_plan", "read": True, "handler": _t_plan,
     "description": "Dry run of a network-map run: what each source file holds and how many people merge across sources. "
                    "Writes nothing.",
     "inputSchema": {"type": "object", "additionalProperties": False, "required": ["run"], "properties": {"run": _RUN}}},
    {"name": "rel_network_map", "read": False, "handler": _t_map,
     "description": "Map a run: merge every source, classify each person (Jev, then GLM, then rules), score warmth and fit, "
                    "find warm paths, and write the run's report.json. Does not create cards (the owner applies). "
                    "Runs in the background unless wait is true; watch it with rel_network_job.",
     "inputSchema": {"type": "object", "additionalProperties": False, "required": ["run"],
                     "properties": {"run": _RUN, "spots": {"type": "integer", "minimum": 1, "maximum": 50},
                                    "wait": {"type": "boolean"}}}},
    {"name": "rel_network_job", "read": True, "handler": _t_job,
     "description": "Progress of a run: one entry per source (queued, reading, done, skipped) and per stage "
                    "(merge, classify, map, spots) with real counts.",
     "inputSchema": {"type": "object", "additionalProperties": False, "required": ["run"], "properties": {"run": _RUN}}},
    {"name": "rel_network_report", "read": True, "handler": _t_report,
     "description": "The NetworkReport for a run: totals, the people shown, who-knows-who edges, and the revenue spots "
                    "(person, kind, score, warm path, why, a draft opener). Openers are drafts for the owner to approve.",
     "inputSchema": {"type": "object", "additionalProperties": False, "required": ["run"],
                     "properties": {"run": _RUN, "spots_only": {"type": "boolean"}}}},
    {"name": "rel_network_li_allow", "read": True, "handler": _t_li_allow,
     "description": "Ask before every LinkedIn invite or connections-list page on our reader account. Returns ok=false "
                    "when the daily invite cap, the hourly page cap, or a block stops it. Never work around a no.",
     "inputSchema": {"type": "object", "additionalProperties": False, "required": ["kind"],
                     "properties": {"kind": _KIND, "account": _ACCOUNT}}},
    {"name": "rel_network_li_record", "read": False, "handler": _t_li_record,
     "description": "Record one LinkedIn invite or page view on our reader account right after it happens (counts toward the caps).",
     "inputSchema": {"type": "object", "additionalProperties": False, "required": ["kind", "target"],
                     "properties": {"kind": _KIND, "target": {"type": "string", "maxLength": 300}, "account": _ACCOUNT}}},
    {"name": "rel_network_li_block", "read": False, "handler": _t_li_block,
     "description": "Call the moment LinkedIn shows a checkpoint, CAPTCHA, warning, restriction or 'too many requests'. "
                    "Stops all LinkedIn reading on the account until the owner clears it by hand.",
     "inputSchema": {"type": "object", "additionalProperties": False, "required": ["reason"],
                     "properties": {"reason": {"type": "string", "maxLength": 300}, "account": _ACCOUNT}}},
]


# ---------------------------------------------------------------- owner CLI
def main(argv=None) -> int:
    import argparse
    from .. import config
    from ..store import Store
    ap = argparse.ArgumentParser(prog="relcore network", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("action", choices=["plan", "run", "report", "apply", "li-status", "li-clear"])
    ap.add_argument("run", nargs="?")
    ap.add_argument("--classifier", choices=["rules", "llm", "jev"])
    ap.add_argument("--spots", type=int, default=12)
    ap.add_argument("--example", action="store_true", help="mark the report as synthetic example data")
    ap.add_argument("--account", default="default")
    ap.add_argument("--yes", action="store_true")
    a = ap.parse_args(argv)
    if a.action in ("plan", "run", "report", "apply") and not a.run:
        ap.error(f"{a.action} needs a run folder")
    if a.action == "plan":
        print(json.dumps(plan(Path(a.run)), indent=1))
    elif a.action == "run":
        clf = classify.pick(a.classifier) if a.classifier else None
        example = a.example or bool(_client(Path(a.run)).get("example"))
        r = run(Path(a.run), classifier=clf, spots=a.spots, example=example)
        print(json.dumps({"totals": r["totals"], "engine": r["engine"], "spots": len(r["spots"]),
                          "report": str(Path(a.run) / "report.json")}, indent=1))
    elif a.action == "report":
        print((Path(a.run) / "report.json").read_text())
    elif a.action == "apply":
        if not a.yes:
            print("apply writes every person in this run as a card in this install. Re-run with --yes.")
            return 2
        print(json.dumps(apply(Path(a.run), Store(config.resolve(), render=True)), indent=1))
    elif a.action == "li-status":
        print(json.dumps(Ledger(config.resolve().home, a.account).status(), indent=1))
    elif a.action == "li-clear":
        if not a.yes:
            print("Clear the block only after logging into the reader account by hand and checking it is in good standing. "
                  "Re-run with --yes.")
            return 2
        Ledger(config.resolve().home, a.account).clear()
        print(json.dumps(Ledger(config.resolve().home, a.account).status(), indent=1))
    return 0
