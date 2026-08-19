---
name: sb-scrape
description: Scrape data at scale with Super Browser — source leads, crawl directories, get structured records. Use when asked to "scrape all X", "get me N leads", "source companies/people", "crawl this directory", or extract records from LinkedIn/Facebook/Google-Maps. Routes across the scrape lane (Firecrawl / Bright Data / Apify) with discover → negotiate scale → plan → crawl, and never returns a tiny hand-picked list for a bulk ask.
argument-hint: <what to scrape and how many>
allowed-tools: Bash, Read
---

# sb-scrape — industrial scraping via Super Browser

The data lane: "go get SPECIFIC data from SPECIFIC sites." Runs on the deployed agent through the bridge.

## The doctrine (what the agent does for a bulk ask)
1. **discover_sources** — enumerate the real directories/sources + a sourced total estimate.
2. **negotiate scale** — it asks how many (100 / 500 / 1k / 10k) = the spend authorization.
3. **plan_infrastructure** — a provider-selection council picks the cheapest-capable stack.
4. **industrial_scrape** — paginates every source in parallel, dedupes globally, stops at target/budget, streams progress.

For structured platform records (LinkedIn/FB/Maps) it uses **dataset_scrape** (Bright Data). For a single page
you already have, `source_leads`. The tiebreak (Apify vs Bright Data vs Firecrawl vs browser) lives with the
**scrape-router-advisor** sub-agent and in `${CLAUDE_PLUGIN_ROOT}/vault/super_browser/knowledge/providers/`.

## Run it

```bash
node ${CLAUDE_PLUGIN_ROOT}/scripts/sb.mjs chat "scrape all the marketing agencies in Texas — target 500"
node ${CLAUDE_PLUGIN_ROOT}/scripts/sb.mjs chat "get 1000 LinkedIn company records for fintech in the UK"
```

Heavy crawls take minutes and stream progress; the final reply includes counts, cost, and the CSV path.
Ask the `scrape-router-advisor` first if you're unsure which tool/lane fits — it reads the docs and explains.
