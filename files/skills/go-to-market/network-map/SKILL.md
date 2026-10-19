---
name: network-map
description: "Use when mapping everyone a client already knows (CRM, LinkedIn, email lists, contacts, social followers) into living contact cards and finding the next revenue spots."
version: 1.0.0
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [go-to-market, network, relationships, referrals, partners, reactivation]
    category: go-to-market
    related_skills: [revenue-partner, grounded-research]
    created_by: agent
---

# Network Map

## Purpose

Turn everyone a client already knows into one living contact card per person, then answer: who else am I connected to, and where is the next revenue spot? The work runs in three steps:
1. Inputs come in from the client's own sources.
2. People are merged across sources into cards.
3. The connections are mapped and scored, and each top spot gets a warm path and a draft opener.

The engine is the local `relcore` MCP server. Cards live in SQLite and render into the Obsidian vault under `Relationships/`.

## Trigger Conditions

Load this skill when the user asks to:

- Map a client's network, connections, followers, list or CRM.
- Find warm intros, referral partners, connectors, or "who do I already know who could buy".
- Reactivate a CRM or old list by finding who is worth a conversation now.
- Show the progress of a network map run, or its revenue spots.

## Inputs

Each run is a folder: `/root/.hermes/revenue-partner/relationship/network/<run>/`.
- `<run>` is a short slug of lowercase letters, digits and dashes.
- The folder holds `client.json` plus one file per source in `sources/`.
- Write these with the file tool. If the file tool refuses that folder, stop and ask the owner to drop the files there. The run reads them from disk.

`client.json` holds the client's profile:

```json
{"name": "Summit Roofing", "offer": "Roof replacement and repair",
 "buyers": {"industries": ["Residential"], "titles": ["Homeowner", "Property manager"], "geo": "Denver, CO"},
 "partner_types": ["realtor", "home-inspector", "insurance-adjuster"], "value_per_customer": 12000}
```

| Source | How it arrives | File in `sources/` |
|---|---|---|
| CRM | GoHighLevel, HubSpot, Salesforce or Pipedrive contact export. Composio is not in this image, so this is an export file. | `crm.csv` (any of those column sets) |
| Email list | ESP export: Mailchimp, ActiveCampaign, beehiiv, Kit, Klaviyo, Constant Contact | `email_list.csv` |
| Contacts | Google or Outlook CSV, or an iPhone/iCloud vCard | `contacts.csv` or `contacts.vcf` |
| LinkedIn | Our dedicated reader account (see below), or the client's own Connections.csv if they offer it | `linkedin.json` `[{name, headline, url, connected_on}]` |
| Facebook, Instagram, X, TikTok, YouTube, Threads | Public follower or friend lists from the profile URL: `scrape-creators` public routes or `browser-box` read; or the platform's own data download | `facebook.json`, `instagram.json` ... `[{name, url, city}]` |
| Other pages | Team, testimonial, partner, podcast-guest and event pages via `browser-box` read | `web.json` `[{name, title, company, url}]` |
| Who knows who | Mutual connections seen while reading | `mutuals.json` `[{a, b, seen_on}]` (profile URLs or emails) |

## LinkedIn: a reader account, never theirs, and read only

This is purely about who the client is connected to. Send no messages and post no content, ever.

1. The client gives a profile URL. They never log in, connect their account, or hand over anything else.
2. The reader runs where the client runs this agent: their own computer or their Orgo box. It is logged into a dedicated LinkedIn account that is not the client's.
3. LinkedIn shows a connection list only to first-degree connections.
   - If the reader account is already connected to the client, there is nothing to send.
   - If it is not, the only write is one connection request to the client, who expects it. It goes through Super Browser's approval lifecycle, or the owner sends it by hand. Call `rel_network_li_allow` with `kind: invite` first, and `rel_network_li_record` right after.
   - If the client would rather, their LinkedIn connections export (Connections.csv) does the same job with zero writes. Use it whenever they offer it.
4. Read their connections list with `browser-box` (session and read) logged into the reader account.
   - Call `rel_network_li_allow` with `kind: page` before every page, and `rel_network_li_record` after it.
   - Work at a human pace.
5. If LinkedIn shows a checkpoint, CAPTCHA, warning, restriction or "too many requests", call `rel_network_li_block` at once and stop all LinkedIn work. Never solve or route around it. Only the owner clears a block (`relcore network li-clear`).

The defaults are 15 invites a day, 20 list pages an hour and 120 a day. A "no" from `rel_network_li_allow` is final for that window.

## Workflow

1. **Plan:** call `rel_network_plan` with the run. It reports what each file holds and how people merge, and writes nothing. Fix any skipped file before mapping.
2. **Map:** call `rel_network_map`. It runs in the background and writes `report.json`.
3. **Progress:** watch it with `rel_network_job`. It shows one bar per source, then one per stage (merge, classify, map, spots), with real counts. Report progress from these numbers only.
4. **Report:** call `rel_network_report` with `spots_only: true`. For each spot, give:
   - who they are;
   - why they are a spot;
   - the warm path (you, then whoever you both know, then them);
   - the draft opener.
5. **Present:** show totals (contacts read, people, multi-source people, buyers, partners, connectors), the top spots, and the candidates list. Candidates are possible duplicates: same name with nothing else to confirm it. Ask the owner about those, and never merge them yourself.
6. **Cards:** writing every person into the cards is a bulk import, so the owner runs it:
   `python3 -m relcore network apply <run folder> --yes`
   After that, use `rel_context` before any message, and `rel_facts_record`, `rel_loop_update` and `rel_research_record` as conversations happen.

## Deep pass: who they know, and what it could bring

After the map, go deeper on a sample (default 12, at most 20): the top revenue spots, then the best-connected people the client knows least about.

1. **Sample:** call `rel_network_deep_plan`. It lists each person with what is already known and how many pages they have.
2. **Evidence:** for each person, find their public pages: website, team and about pages, association, chamber and board pages, event and speaker pages, news, podcasts, and their social profiles. Read them with `browser-box` (read or fetch).
   - Save each with `rel_network_page_add`. Set `found_via`: `own_profile` for a profile URL from the client's own sources, `linked` for a page linked from it, `search` for anything found by name. Code checks own profiles against the sources.
   - LinkedIn pages go through `rel_network_li_allow` and `rel_network_li_record` first, like any LinkedIn read, or the page is refused.
   - Never log into anything as the person, never message them, and skip private or paywalled pages.
3. **Run:** call `rel_network_deep`. Five agents run on Claude Opus 5.5: the card mapper, the connection researcher (facts with verbatim quotes, and "potentially knows" inferences), quality control (is each page this same person, does each quote back its fact), the opportunity brainstorm, and the connections expert. Watch it with `rel_network_job` and `deep: true`.
4. **Present:** call `rel_network_report` with `deep: true`. Give the headline, the top opportunities with their first steps, the shared hubs, and each person's brief.
   - Say "potentially knows" for inferences, never "knows".
   - Label facts from likely pages as likely the same person.
   - List the "needs your check" pages (same name, nothing else ties them) as questions for the owner. Never use them until the owner confirms.
   - Report what quality control dropped and why when the owner asks.

If `rel_network_deep` says no frontier model is configured, tell the owner it needs `ANTHROPIC_API_KEY` (Claude Opus 5.5) or `OPENROUTER_API_KEY`. Never run the deep pass on a weaker model.

## Classification and reasoning

- Classification uses TypeSafe Jev when `TYPESAFE_API_KEY` is set, otherwise GLM 5.3 Flash on OpenRouter, otherwise offline rules. The report's `engine` field says which one ran.
- Only titles, companies, headlines and locations are sent. Emails and phones are never sent.
- The reasons and openers come from the facts. An opener never claims a conversation that did not happen.

## Rules

- The client's do-not-contact list always wins. Use `rel_suppress` the moment someone opts out.
- Never store health, religion, politics, sexual orientation, minors, government IDs, payment cards or passwords.
- No paid enrichment unless the owner turns a specific paid tool on for this client.
- Openers are drafts. Nothing is sent without the owner's approval.
- A report shows which identities exist (email, phone, profile), never their values.

## Verification

- `rel_network_job` ends in `complete`, and every source shows `done` or a stated reason it was `skipped`.
- Every spot's path starts at `me` and ends at that person, and everyone on the path is in the report.
- The totals in your summary match `report.json`.
- Every fact you quote from the deep pass is in `deep.json` with its page, and every opportunity you give cites verified ids there.
