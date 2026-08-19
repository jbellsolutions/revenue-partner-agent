# Super Browser — the plugin

Super Browser ships as a **Claude Code plugin** so any host agent (Claude Code, Single Brain, …) can install it
and instantly get: the full documentation to reason over, specialist advisor sub-agents to chat with, and a thin
hosted bridge to execute. **The host agent does the deep planning; Super Browser is the executor + source of
truth** (specialize, don't duplicate).

## Install
```
/plugin marketplace add jbellsolutions/super-browser
/plugin install super-browser
```
(Or point any host at the repo — the plugin is `.claude-plugin/` in the repo root.)

Then, one-time per host, create `~/.super-browser.env` so the executor bridge can reach the live agent:
```
SUPER_BROWSER_URL=https://167.71.241.147.nip.io
SUPER_BROWSER_TOKEN=<bearer token>
```
Docs + advisors work with **no** config; only *executing* tasks needs the URL + token.

## What the host gets

### Specialist advisor sub-agents (chat with the docs — "which tool and why")
- **browser-ecosystem-advisor** — Playwright vs Browser-Use vs Steel vs Hyperbrowser vs Airtop vs Browserbase vs Orgo.
- **scrape-router-advisor** — Apify vs Bright Data datasets vs Firecrawl vs a browser; lead sourcing at scale.
- **apify-specialist** — the ~11k-actor catalog, actor inputs, cost gating, the custom-actor generator.
They read the bundled knowledge (`vault/super_browser/knowledge/`, `references/`) and answer capability-first
with a cost tiebreak — no guessing.

### Skills (invoke capabilities)
- `super-browser` — talk to the live agent and have it DO things (the front door).
- `sb-scrape` — industrial scraping / lead sourcing (discover → negotiate → plan → crawl).
- `sb-apify` — search / run / schedule / generate Apify actors.
- `sb-agents` — the agent registry (create / list / run saved agents).
- Plus the 11 engine browser-provider specialists (playwright, browser-use, steel, hyperbrowser, airtop, orgo, …).

### Commands
- `/super-browser <request>` — execute on the live agent.
- `/sb-why <question>` — route to the right advisor for a grounded "which tool and why" answer.

### Executor bridge
`scripts/sb.mjs` — a dependency-free CLI over the hosted `/ask` endpoint (multi-turn):
```bash
node scripts/sb.mjs chat "<request>"   # keeps context
node scripts/sb.mjs repl               # continuous chat loop
node scripts/sb.mjs ask "<request>"    # one-shot
```

## The capability map (two lanes)
Read `vault/super_browser/knowledge/00-browser-ecosystem-map.md` for the full, honest map. In short:
- **Browser lane** (operate a site): Playwright → Browser-Use → Steel/Hyperbrowser/Airtop → Browserbase → Orgo (desktop).
- **Scrape lane** (get data): Firecrawl (generic pages) · Bright Data (datasets for LinkedIn/FB/Maps) · Apify (the long tail) · discover_sources/industrial_scrape for bulk.
- **Orchestration**: agent registry, provider-selection council, fleets.

## Notes
- The executor is the **hosted** deployed brain (Kimi/OpenRouter) — always current, no local engine per host.
  A fully-local execution mode is a possible later add.
- The engine's MCP server (`.mcp.json` → `mcp/super-browser-server`) is also available for hosts that want the
  low-level routing/verification tools locally.
