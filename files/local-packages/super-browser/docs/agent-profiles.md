# Agent Profiles — the Super Browser agent factory + registry

Super Browser can **create, save, list, and run** named, reusable agents. An *agent* is a saved task —
task-shaped, not tool-shaped: you describe what you want done, and the provider council picks the actual
tool/stack per run. Profiles are plain YAML in the Obsidian vault, so they persist across restarts, show up
in the graph, and a GUI can read/render/drive them.

- **Storage:** `scripts/agent_registry.py` (pure storage) → `vault/super_browser/agents/<slug>.yaml`
- **Factory + run logic:** `create_agent` / `list_agents` / `run_agent` in `scripts/talk_super_browser.py`
  (they need the LLM + the tool dispatcher, so they live in the brain, not the storage module)
- **Surfaces:** chat (Slack/Telegram/CLI, via the concierge doctrine) **and** HTTP (for the GUI)

## Profile schema (`vault/super_browser/agents/<slug>.yaml`)

| Field | Type | Meaning |
|---|---|---|
| `name` | str | Human name ("PR-firm scraper"). |
| `slug` | str | Filename id, auto-derived from `name` (`slugify`). Stable handle for `run_agent`. |
| `description` | str | One line: what it does. |
| `kind` | enum | `scrape` \| `research` \| `monitor` \| `browse` \| `custom` — for GUI grouping/icons. |
| `mode` | enum | **`tool`** = one bound tool + fixed args (fast, one-shot). **`goal`** = a natural-language goal run through the full agent loop (multi-step, flexible). |
| `tool` | str\|null | (mode `tool`) the bound Super Browser tool name, e.g. `source_leads`, `industrial_scrape`. |
| `tool_args` | object | (mode `tool`) fixed args; `{input}` placeholders are filled from `inputs` at run time. |
| `goal` | str\|null | (mode `goal`) the goal text; `{input}` placeholders filled at run time. |
| `inputs` | list | Runtime params the user varies: `[{name, description, default}]`. Referenced as `{name}` in `goal`/`tool_args`. |
| `provider` | str | `auto` (the council picks per run — the default) or a pinned provider name. |
| `created` | str | ISO timestamp (auto). |
| `runs` | int | Times run (auto, via `record_run`). |
| `last_run` | str | ISO timestamp of the last run (auto). |
| `last_result` | str | Truncated summary of the last run (auto). |

### Example — a `goal`-mode scraper

```yaml
name: PR firm scraper
slug: pr-firm-scraper
description: Discover and scrape all PR firms in a region at scale.
kind: scrape
mode: goal
tool: null
tool_args: {}
goal: Scrape all PR firms in {region}. Discover sources, negotiate scale, run an exhaustive crawl, return a deduped CSV.
inputs:
  - name: region
    description: Metro or region to target
    default: United States
provider: auto
```

Run it: `run_agent('pr-firm-scraper', {"region": "Miami"})`. Because it's a saved run, it proceeds
autonomously with sensible defaults (it will **not** re-ask the scale).

## HTTP endpoints (the GUI contract)

Served by `scripts/super_browser_server.py` (default `127.0.0.1:8088`; set `SUPER_BROWSER_TOKEN` to require
`Authorization: Bearer <token>` on POSTs).

| Method + path | Body | Returns |
|---|---|---|
| `GET /agents` | — | `{"agents": [ {slug, name, description, kind, mode, inputs, runs, last_run} ]}` |
| `POST /agents` | `{"request": "...", "name": "..."}` | `{"status":"created","agent":{slug,name,description,kind,mode,inputs},"how_to_run":"run_agent('<slug>')"}` |
| `POST /agents/{slug}/run` | `{"inputs": {"region":"Miami"}}` | `{"status":"ran","agent":"<slug>","mode":"tool|goal","result": ...}` |

`POST /agents` runs the LLM architect to design + save the profile from the free-text `request`. `name`
optionally overrides the generated name.

### curl

```bash
curl -s localhost:8088/agents
curl -s -XPOST localhost:8088/agents \
  -d '{"request":"scrape all PR firms in {region}","name":"PR firm scraper"}'
curl -s -XPOST localhost:8088/agents/pr-firm-scraper/run \
  -d '{"inputs":{"region":"Miami"}}'
```

## Chat surface (concierge)

The `HERMES_SUPER_PROMPT` teaches front-door triage: a browser question → answer it; "run my X" →
`list_agents`/`run_agent`; a repeatable task or "make/save an agent that…" → `create_agent`; a big one-off →
just do it. After finishing a task Justin will obviously repeat, it offers to save it as an agent.
