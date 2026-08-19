# Apify integration — the long-tail platform-actor lane

Super Browser has full command of [Apify](https://apify.com): a searchable local catalog of ~11k
maintained actors, the whole docs corpus in its knowledge base, cost-gated actor runs, a provider lane,
an "Apify section" of saved agents, and a monthly auto-refresh. Apify sits beside Firecrawl (go get SPECIFIC
data from SPECIFIC sites) — its edge is the **long tail of maintained platform actors** (Instagram, TikTok,
X, Google Maps, Amazon, Zillow, and thousands of niche sites) that no single browser/proxy provider covers.

## When to use it (the routing tiebreak)
1. Named platform / niche site **with a good maintained actor** → **Apify**.
2. Big-3 LinkedIn / Facebook / Google-Maps structured records at bulk → **brightdata-dataset** (`dataset_scrape`).
3. Generic public directory/listing at volume → **Firecrawl** (`industrial_scrape`).
4. Interactive / logged-in / JS flow with no actor → a **browser** (Steel / Browserbase / browser_use).

## Tools (in the brain, flow to Slack/Telegram/HTTP)
- **`apify_search_actors(query, category="", limit=15)`** — search the local catalog (fast, offline,
  monthly-fresh); live Store fallback. Returns ranked actors (id/title/runs/pricing).
- **`apify_actor_info(actor_id)`** — the actor's description + INPUT SCHEMA, so the agent builds valid input.
- **`apify_run_actor(actor_id, actor_input, max_items=10, budget_usd=5)`** — run an actor and get its dataset.
  **Cost gate:** async run with a hard `maxTotalChargeUsd` ceiling (default **$5**) + a small pilot
  (`max_items`, default 10). Raise both deliberately for a real run. Needs `APIFY_TOKEN`.
- **`apify_create_actor_pipeline(source_actor_id, target_actor_id, static_target_input=None, event_type="ACTOR.RUN.SUCCEEDED", description="")`**
  — create a safe actor-to-actor webhook integration. Resolves both actor technical names (for example
  `user/source` and `user/target`) to true opaque actor IDs, then creates a webhook where the source actor's
  succeeded run POSTs to `https://api.apify.com/v2/actors/<target actor id>/runs`. The target input is a JSON
  string template containing the static target input plus `payload.resource="{{resource}}"`.
- **`apify_list_actor_integrations(source_actor_id="", target_actor_id="", event_type="", limit=100)`** — list and normalize
  Apify webhook integrations, optionally filtered by source, target, or event type. `limit` is a positive integer
  from 1 to 1000 and caps returned matches; listing paginates through Apify webhooks until enough matches are
  collected or the remote collection is exhausted.
- **`apify_delete_actor_integration(webhook_id)`** — delete an Apify webhook integration by id.
- Provider lane: `provider="apify"` in `lead_pipeline._scrape` → generic scrape via
  `apify/website-content-crawler`.

⚠️ **Cost safety.** Apify actors charge real money (pay-per-result; one FB actor once burned $165 for zero
results). Every run is capped in code and pilots before scale — never auto-run an unknown actor big.

⚠️ **Workflow safety.** Webhook creation/deletion changes a remote recurring workflow. The code above is only
an API primitive; the conversational layer must get explicit user confirmation before calling
`apify_create_actor_pipeline`, `apify_create_actor_integration`, or `apify_delete_actor_integration`.

Example pipeline:

```python
from scripts.apify_tools import apify_create_actor_pipeline

apify_create_actor_pipeline(
    source_actor_id="acme/source-scraper",
    target_actor_id="acme/result-processor",
    static_target_input={"mode": "dedupe", "destination": "crm"},
)
```

## Actor generator — manufacture the missing tool
- **`apify_create_actor(task, target_url="", name="", run_pilot=True)`** (`scripts/apify_build.py`) — when NO
  Store actor fits a target (a weird SPA, a niche portal), Super Browser **writes a custom actor**: an LLM fills
  a proven httpx+BeautifulSoup template (`scripts/templates/apify_actor/`), the Apify CLI pushes + remote-builds
  it, and a **cost-capped pilot** runs (per-run `memory`/`timeout`/`maxItems`). Returns actor_id + console URL +
  pilot items; logs to `built_actors.jsonl` (gitignored runtime state).
- **Different cost meter:** self-built actors bill as **platform compute units + proxy GB** — the rental
  `maxTotalChargeUsd` cap does NOT cover them. The generator bounds each run by memory+timeout. Measured: a
  build + light pilot draws ~$0.003.
- ⚠️ **Know the real account ceiling before trusting "the platform will stop it."** This account is on
  **STARTER with a $150/month cap** (it was FREE/$5 when this was first written — plans change, and the
  backstop moved 30×). Check it live, don't assume:
  `GET /v2/users/me/limits` → `limits.maxMonthlyUsageUsd` + `current.monthlyUsageUsd`.
  Individual actors can be genuinely expensive — Google Maps Scraper (`compass/crawler-google-places`) has
  billed **$17–20 per run** here. Per-run `maxTotalChargeUsd` is the gate that actually protects you; the
  account cap is a distant, expensive backstop.
- Needs the **Apify CLI** on the host (`npm i -g apify-cli`; `apify login -t <token>` is run per-invocation, so
  it works for the non-keyring `superbrowser` service user) and `APIFY_TOKEN`.

## Catalog + docs (the knowledge surface)
- **`scripts/apify_catalog.py --refresh`** — pulls the full Store (sortBy=popularity) → `catalog.jsonl`
  (index, gitignored — regenerated monthly), `catalog_meta.json` (count + new-actor diff), and curated
  per-category markdown `knowledge/apify/actors/*.md` (top actors by runs — the LLM's routing surface).
  `--seed-agents N` writes the Apify agent section; `--notify-slack` posts the monthly diff.
- **`scripts/apify_docs.py --limit 150`** — Firecrawl-crawls docs.apify.com into `knowledge/apify/docs/`.
- Specialist profile: `knowledge/providers/apify.md` (retrievable via `lookup_knowledge`).

## Agents section
`apify_catalog.py --seed-agents N` writes `vault/super_browser/agents/apify-<slug>.yaml` — tool-mode
profiles bound to `apify_run_actor` for the top actors. They appear in `list_agents` and run via `run_agent`.

## Monthly refresh
`super-browser-apify-catalog.timer` (systemd, `OnCalendar=*-*-01 02:00 America/New_York`, `Persistent=true`)
runs `apify_catalog.py --refresh --seed-agents 12 --notify-slack` monthly and posts the new-actor diff to Slack.

## Env
`APIFY_TOKEN` (or `APIFY_API_TOKEN`/`APIFY_KEY`) for runs; `APIFY_MAX_CHARGE_USD` (default 5),
`APIFY_PILOT_ITEMS` (default 10). Catalog/search/actor-info work without a token.
