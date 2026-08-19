# LinkedIn Post Commenters → Verified Emails — Build Handoff

Account-free pipeline: **post URL → every commenter → company → verified work email.** No personal
LinkedIn account, no browser automation, no false-positive emails.

> 🔑 **Keys are NOT in this doc.** They're delivered out-of-band via the handoff zip / secure channel.
> Each project drops its own into a gitignored `.env.local` (template: `.env.local.example`). Never
> commit live keys — this doc lives in a repo, so it stays redacted.

## Pipeline (3 services, all REST, all account-free)
1. **Apify** — actor `apimaestro~linkedin-post-comments-replies-engagements-scraper-no-cookies`.
   Post URL → **ALL** commenters (name, profile URL, headline). No login. **$5 / 1,000 results.**
2. **Bright Data datasets** — "LinkedIn people profiles" `gd_l1viktl72bvl7bjuj0` → current company.
   (Posts dataset `gd_lyy3tktm25m4avu764` returns only the top ~10 comments — used as a fallback.)
3. **FullEnrich** — bulk waterfall (20+ vendors: Hunter, ContactOut, Wiza, Snov…). name+company+
   LinkedIn → **verified work email.** Pay-per-hit (~1 credit/email; phones are 10 — we do **emails only**).

## Credentials (put in `<project>/.env.local`, gitignored)
```
APIFY_TOKEN=<apify.com → Settings → Integrations → Personal API token>
FULLENRICH_API_KEY=<app.fullenrich.com → API; account needs credits>
BRIGHTDATA_API_KEY=<brightdata.com → Settings → API token>
BRIGHTDATA_SERP_ZONE=serp_api1                # optional; only for the SERP-email fallback
```

## The exact API calls (for porting)
- **Apify:** `POST https://api.apify.com/v2/acts/apimaestro~linkedin-post-comments-replies-engagements-scraper-no-cookies/run-sync-get-dataset-items?token=$APIFY_TOKEN`
  body `{"postIds":["<post url>"],"page_number":N}` → array of comments; loop `page_number` 1.. until a page returns <100. Fields: `author.name`, `author.profile_url`/`author.url`, `author.headline`.
- **Bright Data profiles:** `POST https://api.brightdata.com/datasets/v3/scrape?dataset_id=gd_l1viktl72bvl7bjuj0&format=json`, `Authorization: Bearer $BRIGHTDATA_API_KEY`, body `[{"url":"<linkedin url>"}, …]` → records with `url` + `current_company.name`. **Match by lowercased `/in/<slug>`** (profiles come back with country subdomains + mixed casing).
- **FullEnrich:** `POST https://app.fullenrich.com/api/v2/contact/enrich/bulk`, `Authorization: Bearer $FULLENRICH_API_KEY`, body `{"name":"batch","data":[{"first_name","last_name","company_name","linkedin_url","enrich_fields":["contact.work_emails","contact.personal_emails"],"custom":{"lead_id":"0"}}, …]}` (≤100). Returns `{enrichment_id}`. **Poll** `GET /contact/enrich/bulk/{enrichment_id}` until `status:"FINISHED"` (terminal errors: `CREDITS_INSUFFICIENT`, `FAILED`). Results in `data[]`; map back via `custom.lead_id`.

## Reference code (stdlib only, no deps)
In this repo under `scripts/`:
- **`post_to_leads.py`** — orchestrator: post URL → Apify → Bright Data → FullEnrich → CSV.
- **`fullenrich.py`** — FullEnrich bulk enrich + poll + defensive result parsing.
- **`deep_lookup_enrich.py`** — `load_env()` (reads `.env.local`) + token resolution (reused by the others).

## Run
```bash
python3 scripts/post_to_leads.py "https://www.linkedin.com/posts/…" [out.csv]
# → CSV: full_name, company, linkedin_url, email, email_status, phone, source
```

## Gotchas
- **FullEnrich needs credits** — `CREDITS_INSUFFICIENT` means buy a plan (emails ≈ 1 credit each).
- Apify returns **all** commenters (paginated); Bright Data alone only the top ~10.
- **Phones** are not in this flow (emails only). Add later by scraping each company site's `tel:` /
  contact page via **Firecrawl** or **Bright Data Web Unlocker** — no FullEnrich phone credits.
- Validated live: a 35-commenter post → 35 commenters + companies, account-free; emails fill once
  FullEnrich has credits.
