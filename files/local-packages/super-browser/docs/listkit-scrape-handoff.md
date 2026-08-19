# ListKit In-Tab Scrape — Resolved (v0.7.0)

**Status: working & verified against live `next.listkit.io` People results.** The engine was
diagnosed and rewritten against the *real* logged-in DOM (not a synthetic fixture), then verified
end-to-end.

## What was actually wrong (v0.6.1)

The previous port diverged from the real Instant Data Scraper algorithm (the one that already
works on ListKit) while being tuned against a hand-authored fixture. Root causes, confirmed by
reading the real IDS `…/ofaokhiedipichpaobibbnahnkdoiiah/1.4.4_0/src/onload.js` and the live DOM:

1. **Pagination (primary bug).** ListKit's pager is numbered `<button>`s in
   `<div class="flex items-center gap-1">` — **not** inside a `nav`/`.pagination`, and the active
   page is marked **only by background color** (`bg-[#EBECF0]`), no `aria-current`. The old
   `clickNext` only searched inside `nav`, so it never advanced → "25 rows, all page 1".
2. **Engine divergence.** The port added a `homogeneity < 0.5` hard filter + `aside ×0.05` penalty
   that real IDS lacks; on a React/Tailwind grid these can suppress the correct block.
3. **Dead IDS bridge.** `background.js` used `chrome.tabs.sendMessage(tabId, …, { extensionId })`
   — not a valid API, and IDS declares no `externally_connectable`. It never fired; every run
   silently fell back to the diverged port.
4. **Load-time drift.** During a page transition the grid is briefly empty, so the biggest
   repeating block becomes the **filter sidebar** ("Funding", "Industry"…). Extracting then yields
   junk.

## What the live DOM showed (diagnosis)

- The people grid is a `<div class="divide-y divide-gray-200 flex-1">` of 25 rows
  `<div class="flex items-center bg-white hover:bg-gray-50">`, ~19 cells each.
- Under faithful `area × children²` it ranks #1 by **>30×** (96.8% of body area). Selection was
  never the core problem on the People view; **pagination was.**
- **Not virtualized:** 25 DOM rows = 25 visible = one page; numbered pagination, 25/page.
- Extraction is **rich**: 10–13 populated fields/row (name, company, title, website, country,
  city, industry, employees, …). Emails are behind ListKit's credit wall (not in the free grid).

## What changed (v0.7.0)

| File | Change |
|------|--------|
| `extension/ids-engine.js` | Faithful `area × children²` scoring (2% min area), **homogeneity filter + aside penalty removed**; ≥2-column preference so a 1-col sidebar isn't locked during load; **numbered-pager / generic-next / load-more / infinite-scroll / `?page=` pagination**; visual table picker (`highlight`/`cycleTable`/`pickByClick`) + `locateNext` capture; per-host persisted selectors; SPA-safe `tableSignature` re-scan |
| `extension/tab-scraper.js` | Thin delegation to the engine; strategy plumbing; contact-field inference |
| `extension/background.js` | **Dead IDS bridge removed**; robust inject (probe-then-inject, survives SPA/reload) |
| `extension/sidepanel/*` | New 3-step UI (Table / Pagination / Run); **client-side CSV export (Blob, no backend)**; Stop button; live log |
| `extension/manifest.json` | `0.7.0` |
| `extension/test-fixtures/listkit-b2b.html` | Rebuilt to mirror the real structure (sidebar decoy + Tailwind grid + numbered button pager) |

## Verification (live + integrated)

- **Live `next.listkit.io` People (logged in):** faithful engine ranks the grid #1; extraction
  returns clean rows (`claudia woerheide / transcontinental… / ceo / tfaadmin.com / united states`,
  25×13); numbered advance clicked pages 1→2→3→4 with the grid repopulating distinct people; grid
  selector stable across pages (Tailwind classes).
- **Integrated (real engine + tab-scraper in a browser, fixture):** `waitForRows → advancePage →
  waitForRows` picks the 5-row grid over the 12-row sidebar, extracts 10 cols, advances, page 2 is
  distinct. PASS.
- **CSV exporter (unit):** dedupe + column union + comma/quote escaping verified.

## Remaining / next

- **User run is the final oracle for the Chrome message plumbing** (`background.js` ↔ side panel)
  and the interactive **Pick manually** / **Locate next button** flows — verify in the user's own
  Chrome and read the side-panel log.
- Optional polish: map path-based column headers to ListKit's real header labels; a second
  non-ListKit directory site for generality.

## Run it

1. `chrome://extensions` → Reload **Super Saiyan Browser** (public repo `extension/` or Desktop copy:
   `/Users/home/Desktop/super-browser-extension`).
2. Open ListKit **People** results (logged in). Side panel → **Detect table** → **Run scrape** →
   **Export CSV**. No API/login/sync needed.

**Public extension repo:** [super-saiyan-browser](https://github.com/jbellsolutions/super-saiyan-browser)
