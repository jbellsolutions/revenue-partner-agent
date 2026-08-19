# Tool watch — the weekly freshness check

Super Browser depends on ~18 moving vendors. They ship constantly. Before this, you found out from
Twitter: Browserbase shipped, Codex shipped a browser agent, Decodo shipped a CLI — and the agent knew
about none of it.

## Why the previous one didn't work

`scripts/weekly-provider-intelligence.py` (retired) ran every Monday via GitHub Actions and **failed
every run from at least 2026-07-13** — five-plus consecutive failures, ~40 seconds each. Three causes:

1. It fetched changelogs with raw `urllib`. Two of its three URLs now 404
   (`docs.browserbase.com/changelog`, `docs.hyperbrowser.ai/changelog` — verified).
2. Its `--commit` was gated on `verify-super-browser`, an unrelated test suite that died on
   `ModuleNotFoundError: httpx` because CI installed no dependencies.
3. **It reported nothing when it failed.** No Slack, no email. `references/.provider-intel-cache/` was
   never written even once.

It also watched 3 vendors of ~18. Decodo, Apify, Firecrawl, Bright Data, Orgo, browser-use, Playwright
and Codex were entirely unwatched.

The lesson encoded here: *a watchdog with no pulse of its own is worse than none*, because silence reads
as "nothing changed."

## How this one works

### Detection surfaces, ranked
| Tier | Surface | Why this order |
|---|---|---|
| 1 | **GitHub releases → tags → latest commit** | Can't drift, can't be blocked, dated and versioned. Used for every vendor with a repo. |
| 2 | **Changelog page via Firecrawl** | Only where there's no repo (Orgo, Decodo's proxy product). Firecrawl renders and follows redirects, which is precisely what raw `urllib` failed at. |
| — | **Newsletters / agent email** | Deliberately not built. Marketing-shaped, per-vendor manual signup, needs parsing, and tells us nothing tiers 1–2 don't. |

A repo with no releases *and* no tags falls back to the latest commit SHA. Without that, such a source
would report "ok" forever with an empty fingerprint and could never detect anything — healthy-looking
and useless.

### The watch list includes vendors we dropped
`vault/super_browser/watch/watchlist.yaml`, editable in Obsidian. `status:` is one of:
- `active` — wired and in use
- `dropped` — removed from the lineup, **still watched**, because a significant release reopens the
  decision (exactly the Browserbase case)
- `adjacent` — not a provider; agent tooling whose changes affect what we should build (Codex, Claude Code)

### Two passes: "changed" is not "matters"
1. **Detect** — fingerprint each source, diff against `vault/super_browser/watch/state.json`.
2. **Judge** — each real change gets one LLM call grounded in `01-capability-index.md` and
   `00-browser-ecosystem-map.md`, returning a TL;DR, the lane it touches, whether it changes a routing
   rule, and a verdict: `ignore` · `note` · `consider` · `act now`.

A diff feed is not a briefing. The second pass is the point.

### Delivery
- **Obsidian briefing** — `vault/super_browser/briefings/<date>-tool-watch.md`, with YAML frontmatter.
- **Slack, every week, unconditionally** — including quiet weeks, because proof of life is the feature
  the old job lacked. Every post ends with a health footer:
  `sources 17 · ok 17 · failed 0`.
- **Failure alarm** — any uncaught exception posts `🚨 tool-watch FAILED` with the error. It cannot die
  quietly again.

### It proposes; it never applies
The retired script auto-stamped knowledge docs and auto-committed. This one does neither. The briefing
recommends doc and routing changes; you approve; the agent applies. An unattended job does not get to
rewrite the source of truth.

## Commands

```bash
python3 scripts/tool_watch.py --check          # resolve every source; non-zero exit if any fail
python3 scripts/tool_watch.py --run --dry-run  # detect + judge, print, write nothing
python3 scripts/tool_watch.py --run            # the weekly job
```

`--check` is the one to run when a week looks suspiciously quiet.

## Schedule + env

`deploy/vps/super-browser-tool-watch.{service,timer}` — Mondays 08:00 ET, `Persistent=true`, mirroring
the Apify catalog pair. It runs **on the box, not in CI**, because the box holds the keys; the CI runner
holding none is a root cause of the old failure, not an incident.

| Var | Purpose |
|---|---|
| `FIRECRAWL_API_KEY` | tier-2 changelog fetching (already on the box) |
| `SLACK_BOT_TOKEN` | delivery (already on the box) |
| `TOOL_WATCH_SLACK_TARGET` | channel/DM; falls back to `DAILY_OPS_TARGET` |
| `GITHUB_TOKEN` | optional — raises the 60 req/hr unauthenticated GitHub limit |

Install on the box:
```bash
systemctl daemon-reload && systemctl enable --now super-browser-tool-watch.timer
```
