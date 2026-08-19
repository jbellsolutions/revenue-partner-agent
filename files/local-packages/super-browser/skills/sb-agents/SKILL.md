---
name: sb-agents
description: Create, list, and run saved Super Browser agents ("profiles") — reusable, named automations. Use when asked to "make an agent that…", "save this as an agent", "run my <X> agent", "list my agents", or to turn a repeatable browser/scrape task into something you can re-run with new inputs.
argument-hint: <make | list | run> an agent
allowed-tools: Bash, Read
---

# sb-agents — the Super Browser agent registry

Super Browser can turn any repeatable task into a saved, named agent you re-run with different inputs. Agents
are task-shaped (not tool-shaped) — the provider council picks the actual tool per run. Profiles persist in the
agent's vault (`vault/super_browser/agents/<slug>.yaml`) and are also exposed over HTTP for a GUI.

## Run it (via the bridge)
```bash
node ${CLAUDE_PLUGIN_ROOT}/scripts/sb.mjs chat "make me an agent that scrapes all PR firms in {region}"
node ${CLAUDE_PLUGIN_ROOT}/scripts/sb.mjs chat "list my agents"
node ${CLAUDE_PLUGIN_ROOT}/scripts/sb.mjs chat "run my pr-firm-scraper agent for region=Miami"
```

## Direct HTTP (for a GUI or another service)
```
GET  {SUPER_BROWSER_URL}/agents
POST {SUPER_BROWSER_URL}/agents            {"request":"scrape all PR firms in {region}","name":"PR firm scraper"}
POST {SUPER_BROWSER_URL}/agents/{slug}/run {"inputs":{"region":"Miami"}}
```
(Bearer token required on POSTs.) Schema + details: `${CLAUDE_PLUGIN_ROOT}/docs/agent-profiles.md`.

Modes: a `tool` agent binds one tool + fixed args (fast); a `goal` agent runs a natural-language goal through
the full loop. After you finish a task you'll obviously repeat, offer to save it as an agent.
