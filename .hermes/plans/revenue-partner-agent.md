# Revenue Partner Agent — Implementation and Publication Contract

## Objective

Turn `nickvasilescu/nicks-stack` into a publishable, source-grounded **Revenue Partner go-to-market agent**. The agent must implement the operating model described by the supplied Revenue Partner landing page and the deployment/agent architecture demonstrated in the three supplied videos.

The supplied Orgo workspace UUID is only a deployment destination. Do not use its dashboard name as product branding. The template, agent, files, launch computer, and documentation use **Revenue Partner** naming.

## Source Basis

Primary sources:

- `https://aiintegraterz.com/revenue-partner`
- `https://youtu.be/kdvm_kRZk8A`
- `https://youtu.be/fAhwYrjmQRk`
- `https://youtu.be/BI-MNjm1tTQ`

Local research evidence is kept under `.artifacts/research/` and excluded from git. A concise source ledger with URLs, claims, caveats, and video timestamps will be committed with the skill.

## Product Contract

### Core role

The agent is the operator-facing Revenue Partner: one GTM orchestrator accountable for the connected front end, not a single-channel copywriter or email sender.

It maintains:

1. One canonical offer, ICP, positioning, approved-claims, and proof layer.
2. One Money Desk split into:
   - **Owned demand:** database reactivation, lapsed customers, dead leads, unclosed quotes, newsletter/list warming.
   - **New demand:** affiliates/partners, targeted outbound, podcasts/stages/sponsors, and social/content distribution.
3. Four coordinated channel systems:
   - Affiliates and partners.
   - Direct outbound.
   - Reactivation.
   - Social and content.
4. Four readiness pillars for every channel:
   - Architecture.
   - Data.
   - Infrastructure.
   - Execution.
5. One outcome dashboard and one weekly continue/modify/stop report.

### Fit gate

Before campaign execution, the agent must classify the business as `fit`, `conditional_fit`, or `not_fit` using explicit evidence.

Hard requirements:

- A paid offer with real commercial validation.
- A defined audience or customer profile.
- Capacity to answer and close qualified conversations.
- Willingness to run a coordinated system rather than permanently isolate one channel.
- Expectations aligned with compounding execution, not overnight spikes.

The agent must not invent readiness or relax the paid-offer gate to create activity.

### Operating sequence

Implement the source-defined stages:

`FIT_ASSESSMENT -> MAPPING -> ARCHITECTURE -> INFRASTRUCTURE_READY -> LAUNCH -> OPERATE_AND_OPTIMIZE`

Default sequencing after fit:

1. Analyze owned demand/reactivation first because it is usually the fastest source-grounded starting point.
2. Launch targeted outbound when positioning, data, deliverability, tracking, and capacity are ready.
3. Add affiliate/partner recruiting and management.
4. Add podcast, stage, conference, and sponsor opportunity work.
5. Use newsletter/social content as the shared narrative layer connecting all channels.

Do not launch every channel simultaneously by default.

### SpeakerAgent Riley behavior

Implement Riley as a bounded research-and-drafting specialist inside the Revenue Partner system:

- Discover shows, conferences, seminars, stages, and sponsorship opportunities.
- Score each on audience fit, reachability, evidence, and strategic value.
- Draft pitches and booking preparation in the approved voice.
- Preserve provenance and explain scores.
- Route relationship ownership, deal negotiation, sponsor commitments, and closing to a human.

The agent may automate discovery and preparation; it must not claim that AI replaces human relationship management.

### Approval model

Read-only research, scoring, deduplication, analysis, drafts, internal reports, and recommendations may run autonomously when logged.

A campaign becomes executable only after the operator approves a written campaign contract containing:

- Audience and exclusions.
- Source and provenance.
- Channel and sender identity.
- Approved claims and message variants.
- Volume, schedule, budget, and geography.
- Suppression/opt-out policy.
- Success, pause, and stop thresholds.
- CRM field mapping and source-of-truth rules.

After approval, the agent may operate only inside those bounds. It pauses and escalates on scope drift, unusual complaint/bounce behavior, missing consent, authentication changes, new spend, or reputation risk.

Always require fresh explicit approval for:

- New campaigns or material scope changes.
- Pricing, discounts, contracts, affiliate terms, sponsorship terms, or other commitments.
- Publishing under the user's identity outside an approved campaign.
- Destructive/bulk CRM changes.
- New integrations or permission expansion.
- Purchases or paid placements.
- Sensitive data disclosure.

### Evidence and claims policy

- Separate direct source facts, self-reported claims, targets, inference, and verified results.
- The `2–4 booked meetings/day` figure is a target only, never a guarantee or typical-result claim.
- Track booked, attended, qualified, opportunity, pipeline, and closed-revenue metrics separately.
- Do not invent price, commission percentage, attribution window, case study, contract term, SLA, or performance history.
- Use only approved proof; label self-reported and unverified claims.
- Preserve client ownership/exportability of infrastructure, data, campaign history, and strategy artifacts.

### Production-scale research contract

All browser, scraping, lead research, and broad source discovery starts with the Super Browser five-round council. The agent must:

- Compare at least three viable lanes when available.
- Verify provider readiness instead of assuming it.
- Prefer source-appropriate data lanes and use browser rendering only when needed.
- Preserve provenance, retrieval status, evidence, deduplication criteria, and failures.
- When a list quantity is unspecified, treat the deliverable as production-scale and target at least 5,000 unique verified records when sources and budget permit; pilots are preflights, not final delivery.
- Never invent missing fields or silently downscope.

## Agent Architecture

Use one operator-facing orchestrator and narrow specialists to reduce blast radius:

- Fit/intake and Money Desk mapping.
- Account/contact/partner research.
- Reactivation analysis.
- Outbound campaign preparation.
- Affiliate recruiting and enablement.
- Riley opportunity research.
- Content/newsletter coordination.
- Pipeline reporting and experiment analysis.

The main agent keeps the shared story, approval contract, and outcome dashboard. Specialists receive only the tools/context needed for their bounded function.

Persistent context lives in a seeded Markdown/Obsidian-compatible knowledge vault. Skills contain procedures; the vault contains company, offer, ICP, claims, campaign, decision, and result records. Secrets never enter either.

## File Impact

### Modify

- `.gitignore`
  - Ignore `.artifacts/`, resolved build output, caches, and temporary verification files.
- `README.md`
  - Explain the Revenue Partner edition, source-derived capabilities, local verification, Orgo publication, launch, and credential gates.
- `files/SOUL.md`
  - Replace the generic orchestration persona with the Revenue Partner operating contract while preserving strong tool-use, verification, and safety behavior.
- `files/config.yaml`
  - Enable the bundled Super Browser MCP server.
  - Pass provider credentials only by environment reference.
  - Preserve existing channels, memory, observability, and connector configuration.
- `files/onepassword/hermes-env-map.txt`
  - Add optional Super Browser provider secret mappings without values.
- `build_template.py`
  - Rename the template to `revenue-partner-agent` and bump immutable semver.
  - Install the vendored Super Browser package into the Hermes venv with MCP and Playwright support.
  - Install Chromium, place CLI/server wrappers on PATH, and verify provider/MCP imports during build.
  - Seed the Revenue Partner knowledge vault.
  - Keep personal credentials out of the image.
  - Make launch output machine-readable and use plan-compatible computer resources.

### Add

- `files/skills/go-to-market/revenue-partner/SKILL.md`
  - Main trigger, workflow, approval model, artifacts, metrics, and verification.
- `files/skills/go-to-market/revenue-partner/references/operating-system.md`
  - Two engines, four channels, four pillars, stages, decision rules, daily/weekly loop.
- `files/skills/go-to-market/revenue-partner/references/campaign-contract.md`
  - Approval contract and pause/stop thresholds.
- `files/skills/go-to-market/revenue-partner/references/source-ledger.md`
  - URLs, landing-page claims/caveats, video-derived architecture, exact timestamps, and evidence limits.
- `files/skills/go-to-market/revenue-partner/references/acceptance-tests.md`
  - Fit, research, drafting, approval, CRM, failure, observability, isolation, and template smoke tests.
- `files/agent-knowledge/`
  - Seed vault with indexes and canonical templates for company profile, offer, ICP, approved claims, permissions, campaigns, decisions, metrics, and current priorities.
- `files/local-packages/super-browser/`
  - Vendor the minimal clean runtime from `jbellsolutions/super-browser` upstream commit `552822fd86a74d574ff9c0d87db6e6b82f929d96`; exclude caches and local state.
- `tests/test_revenue_partner_template.py`
  - Deterministic static/config/template tests.
- `tests/test_revenue_partner_behavior.py`
  - Contract tests for fit gates, target caveats, approval boundaries, source ledger, and no-secret policy.

## Test-First Implementation Order

1. Write failing tests for template naming/versioning, required files, Super Browser config/install, knowledge-vault seed, source links, explicit non-guarantees, and approval gates.
2. Add the Revenue Partner skill, references, SOUL, and knowledge-vault seed until behavior/static tests pass.
3. Vendor Super Browser from the recorded upstream commit and wire build/config installation until import/config tests pass.
4. Update README and publication helpers.
5. Assemble the resolved template and validate locally and remotely.

## Verification Ladder

### Local

- Python syntax/compile checks.
- Unit and contract tests.
- YAML parse and required-key checks.
- Orgo template schema validation.
- Super Browser source compile, provider count, CLI help, and MCP import.
- Secret scan proving no supplied key or credential value is committed or embedded.
- Build artifact inspection and exact file-count/size report.

### Independent review

Run a separate code-review subagent against the final diff for correctness, security, source fidelity, deployment reliability, and missing tests. Resolve all high/medium findings or document grounded blockers.

### Orgo publication

- Remote validate.
- Publish immutable version.
- Trigger build and poll/stream to `ready`.
- Read back the published template/build status.

### Live smoke

If the supplied workspace is used for a smoke machine, the machine and agent remain named `revenue-partner-*`, not after the workspace dashboard label.

Verify on the launched machine:

- Computer reaches `running`.
- `hermes` exists.
- Revenue Partner skill and knowledge vault exist.
- Super Browser reports eight known providers.
- Local Playwright runtime is actually ready.
- Super Browser MCP starts and Hermes can enumerate/test it.
- Existing observability/plugin/package checks still pass.
- No credential values appear in golden-image files.

A model-backed behavioral conversation is reported separately from infrastructure readiness. If the clean VM lacks model authentication, stop at the exact login/provider requirement rather than copying the operator's personal OAuth token into the image.

## Replanning Triggers

Stop and revise this contract if:

- Orgo rejects publication due to account-plan limits.
- The final inline template exceeds the API payload limit.
- Playwright browser installation makes the template build exceed limits.
- The current upstream Super Browser runtime fails in the Orgo base image.
- Existing nicks-stack functionality regresses.
- A required source claim conflicts with another supplied source.
- Publication succeeds but the launched VM cannot pass the real MCP/runtime checks.

## Completion Definition

The task is complete only when:

1. Source-derived agent behavior and knowledge files exist in the isolated worktree.
2. Local tests, schema checks, secret scans, and independent review pass.
3. The immutable Orgo template is published and built to `ready`, or the exact grounded account/API blocker is reported.
4. A live smoke machine is verified when publication/launch permissions allow it.
5. The user receives the repo location, branch/commit, template ref, machine ID if launched, verification evidence, and only the credentials still genuinely required.
