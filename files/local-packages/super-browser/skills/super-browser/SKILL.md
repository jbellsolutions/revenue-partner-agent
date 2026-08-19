---
name: super-browser
description: Talk to the live Super Browser agent and have it DO things — browser automation, scraping, Apify actors, lead sourcing, computer-use, running saved agents. Use when asked to "ask super browser", "run super browser", "have super browser do X", "chat with super browser / hermes", or to execute any browser/scrape/automation task on the deployed agent. Runs over a thin hosted bridge (no local setup).
argument-hint: <what you want Super Browser to do>
allowed-tools: Bash, Read
---

# Super Browser — the executor bridge

Super Browser is a deployed agent (Kimi/OpenRouter brain) with all the real hands: browser-use, computer-use
(Orgo), the full scrape lane (Firecrawl / Bright Data / Apify's 11k actors), industrial scrape, an agent
registry, fleets, and a council. This skill talks to it over a thin HTTP bridge — no local engine, no keys to
set up on this host; it's always current.

**When to reach for a specialist instead:** if the ask is "which tool and why" (not "do it"), invoke the
`browser-ecosystem-advisor`, `scrape-router-advisor`, or `apify-specialist` sub-agents — they read the bundled
docs and answer. This skill is for EXECUTION and general chat.

## How to run it

```bash
node ${CLAUDE_PLUGIN_ROOT}/scripts/sb.mjs chat "<your request>"     # one turn, keeps context
node ${CLAUDE_PLUGIN_ROOT}/scripts/sb.mjs repl                       # continuous chat loop
node ${CLAUDE_PLUGIN_ROOT}/scripts/sb.mjs ask "<request>"            # one-shot, no history
node ${CLAUDE_PLUGIN_ROOT}/scripts/sb.mjs reset                      # clear the conversation
```

The agent decides which of its tools to call and reports back (it may take a while for heavy tasks like a
crawl or an Apify run — that's normal). Multi-turn context is kept client-side, so follow-ups work.

## Config (one-time per host)
`~/.super-browser.env` with:
```
SUPER_BROWSER_URL=https://167.71.241.147.nip.io
SUPER_BROWSER_TOKEN=<bearer token>
```
(Or set the same as environment variables.) Without the token, POSTs are rejected.

## Examples
- `sb.mjs chat "scrape all the PR firms in Miami"` → it runs discover → negotiate scale → crawl.
- `sb.mjs chat "search apify for a google maps reviews actor and pilot it"` → catalog search + capped pilot.
- `sb.mjs chat "make me a saved agent that scrapes AI-hiring companies weekly"` → creates a registry agent.

## Failure modes
- HTTP 401 → missing/invalid `SUPER_BROWSER_TOKEN`. HTTP 502 → the agent is booting (~15s), retry.
- Long silence on a heavy task is expected; the reply comes when the tool finishes.
