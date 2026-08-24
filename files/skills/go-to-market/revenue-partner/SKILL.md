---
name: revenue-partner
description: "Use when operating a unified Revenue Partner GTM system."
version: 1.0.1
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [go-to-market, revenue, outbound, reactivation, affiliates, content, partnerships]
    category: go-to-market
    related_skills: [grounded-research, agent-observability, agent-knowledge-vaults]
    created_by: agent
---

# Revenue Partner

## Purpose

Design and operate the complete front end as one coordinated Money Desk, not as disconnected channel tasks. Use one approved story, one outcome dashboard, and bounded specialists for research, analysis, and local drafting. External execution is unavailable in this image.

## Trigger Conditions

Load this skill when the user asks to:

- Build or operate a go-to-market/revenue system.
- Qualify an offer or map an ICP.
- Reactivate a database, lapsed customers, dead leads, or unclosed quotes.
- Build Direct outbound, Affiliates/partners, podcast/stage/sponsor opportunities, or Social and content.
- Create a campaign, partner program, prospect list, newsletter, weekly revenue report, or Fit Call map.
- Coordinate several GTM channels or replace disconnected vendors with one operating system.

## Non-Negotiable Outcome

Own the connected system and measure outcomes. Do not optimize for send counts, impressions, scraped-row totals, or draft volume at the expense of booked, attended, qualified, opportunity, pipeline, and closed-revenue outcomes.

## Stage Gate

Every engagement moves through:

`FIT_ASSESSMENT -> MAPPING -> ARCHITECTURE -> INFRASTRUCTURE_READY -> LAUNCH -> OPERATE_AND_OPTIMIZE`

Do not skip a gate. Read `references/operating-system.md` before designing a channel plan. Channel launch is non-executable in this image.

### Fit assessment

Return one of:

- `fit` — paid offer, defined audience, sales capacity, coordinated-system willingness, realistic expectations.
- `conditional_fit` — a fixable readiness gap with an explicit prerequisite plan.
- `not_fit` — no validated paid offer, no target audience, no capacity to close, lowest-price-only intent, or permanent single-channel cherry-picking.

Produce a Fit Map with evidence, unknowns, starting engine, and recommendation.

### Canonical program CTA

When the offer being presented is the Revenue Partner program, use **Book a Fit Call**: a **30–45 minute, no-pitch, honest fit assessment**. The call should determine fit, produce or inform the Fit Map, and say so plainly when the program is not a fit. Do not relabel it as a demo or high-pressure sales call. A client campaign's CTA may differ only when approved in its campaign contract.

## Money Desk

### Engine 1 — owned demand

- Database reactivation.
- Lapsed-customer win-back.
- Dead-lead and unclosed-quote recovery.
- Newsletter and list warming.

### Engine 2 — new demand

- Affiliates and partners.
- Direct outbound.
- Podcasts, stages, conferences, seminars, and sponsors.
- Social and content distribution.

The four channel systems are **Affiliates and partners**, **Direct outbound**, **Reactivation**, and **Social and content**. Use shared positioning and proof across them.

## Four Pillars Readiness Check

For every proposed channel, score:

1. Architecture.
2. Data.
3. Infrastructure.
4. Execution design and local drafts; external execution remains unavailable in this image.

A channel stays blocked until its required owner, story, source data, exclusions, sender/infrastructure, tracking, approvals, and success/stop rules are explicit.

## Default Planning and Drafting Order

1. Inspect owned demand/reactivation first.
2. Prepare targeted outbound plans and drafts when deliverability, data, and sales capacity pass.
3. Design affiliate/partner recruiting and management as an active operating plan, not a passive signup page.
4. Use **SpeakerAgent Riley** to discover and score podcast, stage, conference, seminar, and sponsor opportunities.
5. Coordinate newsletter/social drafts so every channel tells the same approved story.

Phased rollout is supported. Permanent isolated-channel operation is not the Revenue Partner model.

## Campaign Approval

Before any external campaign action, create and obtain approval for `references/campaign-contract.md`.

Autonomous by default when logged:

- Read-only research.
- Source validation.
- Scoring and deduplication.
- Analysis and recommendations.
- Internal drafts and reports.

Campaign approval is audit evidence only in this immutable image; it cannot activate sends, writes, scheduling, spend, authenticated actions, consent actions, or sensitive-data actions. Keep approved work as local drafts and plans. Production execution requires a separately reviewed implementation, rebuilt image, and new release.

## Super Browser and Production-Scale Data

All browser, scraping, research, or lead-generation work begins with a structured **five-round council**:

1. Classify the task.
2. Identify eligible providers and data lanes.
3. Compare at least three viable routes when available.
4. Check live readiness, cost, evidence, and safety.
5. Select execution/fallback plus a verification contract.

Do not claim readiness without proof. Preserve source URL, retrieval status, provenance, evidence/inference labels, deduplication criteria, coverage, exact count, and failures.

If the user requests a list without quantity, target at least **5,000** unique verified records when sources and budget permit. Label pilots as pilots and continue to production scale unless the user asks to stop. Never silently downscope or invent missing fields.

## SpeakerAgent Riley

Riley is a bounded opportunity-research and drafting specialist:

- Find relevant shows, podcasts, conferences, seminars, stages, and sponsors.
- Score audience fit, reachability, strategic value, and evidence quality.
- Draft pitches and preparation in the approved voice.
- Track source, status, owner, and next action.

A human owns the relationship and closing. Riley must not autonomously negotiate terms, promise attendance, accept sponsorship commitments, or impersonate the operator. A campaign approval does not enable those actions in this image.

## Target and Claim Guardrail

The source page says the target is **2–4 booked meetings/day** from hot leads. This is a **target/expectation, not a guarantee or typical result**. Always pair the figure with the caveat that outcomes depend on offer, market, and close rate.

Never invent:

- Price or commission percentage.
- Attribution window.
- Contract/SLA/cancellation terms.
- Case studies or performance history.
- Client names, logos, or proof permission.
- Revenue, ROI, sponsor, placement, attendance, or close-rate guarantees.

### Canonical cost response

When asked “What does it cost?”, answer only from the page:

- The commercial model has three components: an ongoing Money Desk, one-time infrastructure setup, and one-time talent placement.
- The ongoing Money Desk may be structured as an internal base plus commission **or** as straight growth monthly.
- Exact numbers and percentages are not published in the supplied source.
- Offer to **Book a Fit Call** for the fit map, starting point, timing, and a source-authorized commercial discussion. Do not invent a dollar amount, fee, or commission percentage.

## Required Artifacts

Write durable artifacts into the knowledge vault:

- Fit Map.
- Canonical Positioning and Approved Claims.
- Money Desk Map.
- Channel Readiness Matrix.
- Campaign Contract.
- Source and Suppression Ledger.
- Daily Action Queue.
- Opportunity/Partner Scorecard.
- Weekly Revenue Report with `continue|modify|stop` decisions.
- Decision log and postmortems.

Secrets never enter the vault.

## Daily Operating Loop

1. Read `/root/agent-knowledge/INDEX.md` and linked current priorities.
2. Read active campaign contracts and open decisions.
3. Reconcile changed outcomes and blockers.
4. Execute the highest-value approved work.
5. Verify external effects and log evidence.
6. Escalate only decisions, deviations, and failures that require the operator.

## Weekly Operating Loop

1. Reconcile attribution and funnel stages.
2. Report booked, attended, qualified, opportunity, pipeline, and revenue separately.
3. Compare results with the campaign contract.
4. Issue `continue`, `modify`, or `stop` for every experiment.
5. Update source-backed learnings and propose the next bounded test.

## Verification

Before claiming completion:

- Fit decision exists and is evidence-backed.
- Activated channels passed all four pillars.
- Campaign contract is approved for any external action.
- Sources, provenance, deduplication, coverage, and exact counts are reported.
- External writes have durable IDs or read-back evidence.
- Target language includes the non-guarantee caveat.
- Weekly outcomes are separated from activity metrics.
- Failures and approval deviations are visible in observability/logs.

See:

- `references/operating-system.md`
- `references/campaign-contract.md`
- `references/source-ledger.md`
- `references/acceptance-tests.md`
