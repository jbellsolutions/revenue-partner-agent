---
name: sb-apify
description: Use Apify through Super Browser — search the ~11k-actor catalog, read an actor's inputs, run an actor safely (cost-gated), schedule recurring runs, or generate a custom actor when none fits. Use when asked to "find an apify actor", "scrape X with apify", "how much will this apify run cost", "run this actor", or "build an actor for this site".
argument-hint: <platform/site to scrape, or actor + input>
allowed-tools: Bash, Read
---

# sb-apify — the Apify lane via Super Browser

Apify = the long tail of maintained platform actors (Instagram, TikTok, X, Google Maps, Amazon, Zillow, and
thousands of niche sites) + a generator for custom ones. Deep reference: the `apify-specialist` sub-agent and
`${CLAUDE_PLUGIN_ROOT}/vault/super_browser/knowledge/apify/` (catalog + docs) and `docs/apify.md`.

## The flow (all via the bridge)
```bash
node ${CLAUDE_PLUGIN_ROOT}/scripts/sb.mjs chat "search apify for a tiktok profile scraper"      # find
node ${CLAUDE_PLUGIN_ROOT}/scripts/sb.mjs chat "show me the inputs for apify/instagram-scraper"  # actor_info
node ${CLAUDE_PLUGIN_ROOT}/scripts/sb.mjs chat "run apify/website-content-crawler on example.com, pilot 5"  # run
node ${CLAUDE_PLUGIN_ROOT}/scripts/sb.mjs chat "no store actor fits acme-portal.com — build one that grabs the listings"  # generate
node ${CLAUDE_PLUGIN_ROOT}/scripts/sb.mjs chat "schedule apify/... to run every Monday 6am"     # schedule
node ${CLAUDE_PLUGIN_ROOT}/scripts/sb.mjs chat "after acme/source-scraper succeeds, send its resource to acme/result-processor with mode=dedupe"  # actor pipeline
```

## Safety (always)
Apify runs cost real money — one FB actor once burned $165 for nothing. Every run is **cost-gated** (hard
`maxTotalChargeUsd`, default $5) and **pilots ~10 items first**; never scale an unknown actor blind. For big-3
LinkedIn/FB/Maps bulk, Bright Data datasets are usually cheaper (use sb-scrape). When unsure which fits, ask the
`scrape-router-advisor` or `apify-specialist`.

Actor-to-actor pipelines are Apify webhooks. Creating or deleting one changes a remote recurring workflow and
must require explicit user confirmation at the conversational layer. The code primitive resolves technical
names to true actor IDs, uses bearer auth only, targets `/v2/actors/<target actor id>/runs`, and injects
`payload.resource="{{resource}}"` into a JSON-string target input template.
