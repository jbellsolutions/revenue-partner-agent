---
name: super-browser
description: Plan browser/computer tasks and execute only constrained local public-read lanes in the locked image.
---

# Super Browser

Super Browser is now plugin-first. Prefer the role skills in `skills/` and the CLI/MCP runtime.

## Onboarding (first message)

When a user drops this repo link, say:

> This locked Super Browser image plans across eight provider records, but executes only exact allowlisted local Playwright fixtures and bounded direct raw HTTP for public IPv4-literal endpoints. Public Playwright navigation and hosted/autonomous providers are non-executable. Plan before run, stop for approval-required work, and verify before claiming success.

## Quick Start

```bash
./scripts/super-browser doctor
./scripts/super-browser providers
./scripts/super-browser plan --goal "Extract product names from https://example.com"
./scripts/super-browser plan --goal "Extract public data" --allow-provider playwright --max-cost-usd 0
./scripts/super-browser run --goal "Fetch a public IP-literal endpoint" --url "http://93.184.216.34/" --timeout-seconds 60
./scripts/super-browser run --goal "Draft a LinkedIn comment but do not publish"
./scripts/super-browser deny <run-id> --by human --reason "production execution is disabled in this template"
./scripts/super-browser get <run-id>
./scripts/super-browser handoff <run-id>
./scripts/super-browser runs --status awaiting_approval --limit 20
./scripts/super-browser resume <run-id>
./scripts/super-browser verify <run-id>
./scripts/super-browser live-test --provider local
./scripts/verify-super-browser
```

CLI commands return JSON on success and redacted stderr JSON with `error` and `error_type` for known Super Browser command failures. MCP tools advertise `inputSchema` plus read-only/execution annotations, validate required fields, provider enums, cost ceilings, timeout ceilings, booleans, non-blank string fields, and unknown arguments before execution, and return `structuredContent` for direct JSON consumption. Install/config-write, profile create/delete, and Slack-daemon controls are absent from MCP and CLI in this immutable image.

Treat `resume_browser_run` as execution-capable for read-only work. Approval-required runs cannot be approved or executed inside this template runtime.

Recoverable tool errors and unexpected exceptions inside known tools return `isError: true` with redacted structured error details and `error_type`; unknown tools, unsupported protocol methods, malformed `resources/read` envelopes, malformed JSON, and non-object JSON-RPC requests remain protocol errors. Well-formed JSON-RPC notifications without an `id`, including `notifications/initialized`, are consumed without a response. Malformed or non-object requests return a `null` id and must not reuse an earlier request id.

Use MCP `resources/list` and `resources/read` to load read-only provider docs and playbooks when the agent does not have filesystem access. Stable resource URIs include `super-browser://references/provider-matrix`, `super-browser://references/routing-playbook`, and `super-browser://skills/<skill-name>`. Resource docs are exposed only from a verified Super Browser repository, installed bundle root, or packaged `share/super-browser` asset tree, never from an arbitrary MCP current working directory.

This image already contains the locked skill and MCP wiring. Install, config-write, and package-copy commands are intentionally absent; changes require a separately reviewed image rebuild.

Use `./scripts/verify-super-browser` as the default shipped-package verification entrypoint before claiming the curated package or a change is ready. It verifies the shipped inventory, MCP/resource parity, policy hard stops, CLI status surfaces, and Python compilation using temporary state/cache directories. When Playwright is present—as it is in the baked runtime—it also runs the exact loopback readiness test; set `SUPER_BROWSER_VERIFY_REQUIRE_LOCAL_LIVE=1` to require that lane explicitly. The template build independently installs hash-locked Playwright Python dependencies, extracts SHA-256-verified fixed-version Chromium/headless-shell/FFmpeg archives, and proves a real launch. Set `SUPER_BROWSER_VERIFY_TMP_DIR`, `SUPER_BROWSER_VERIFY_STATE_DIR`, or `SUPER_BROWSER_VERIFY_PYCACHE_DIR` only when debugging and you need to keep verifier artifacts.

## Agent Roles

- `super-browser-orchestrator`: Owns the workflow end to end.
- `super-browser-planner`: Chooses providers and builds the execution plan.
- Provider specialists: Record capability provenance, immutable blockers, limits, and non-executable future integration requirements.
- `publishing-safety-specialist`: Gates external writes.
- `super-browser-verifier`: Checks traces, artifacts, and confidence.

## Approval Lifecycle

External writes and credential-bearing tasks create a run in `awaiting_approval`.

External writes include posting, commenting, replying/responding, sending email, sending messages/DMs, submitting non-search/state-changing forms, uploading, liking/reacting/upvoting/downvoting, quote/repost/share-to-story actions, starring/watching/forking repos, bookmarking/saving/pinning/favoriting platform content, following/connecting, joining/creating groups, creating events/pages, accepting/declining/removing/canceling/confirming requests, invites, or connections, removing followers/friends/members, RSVPs, event attendance/check-ins/interested/going marks, reporting/blocking/muting, notification toggles, message/email archive/read-state changes, tagging/mentioning people, booking/scheduling/reserving, requesting info/demo/quotes/pricing, applying, subscribing, reviews, poll votes, CRM lead/contact/customer create/assign/enroll/stage/list updates, project/repository issue, ticket, task, card, pull-request, and repo changes, cloud file/folder/document creation, renames, moves, copies, sharing/access/permission/public-visibility changes, app/integration install/authorize/connect changes, settings/preference saves, API-key/token creation, rotation, or revocation, secret reveal/copy requests, webhook creation or updates, deployment creation, promotion, rollback, or redeploys, DNS record/nameserver changes, environment-variable changes, billing trial/plan/payment-method changes, trading orders, asset sales, swaps, staking, unstaking, position opens/closes/liquidations, withdrawals, deposits, fund transfers, ACH/wire/bank transfers, bank/wallet/brokerage/payout account changes, legal signatures/certifications/attestations, tax and court filings, insurance claim/policy changes, benefits or health-plan enrollment changes, prescription refills, medical form/record delivery, passport/visa/government-ID actions, voter registration, regulated address changes, emergency contact changes, workspace/channel/server/community/page creation, rename, archive, or unarchive changes, member additions, kicks, bans, unbans, role changes, thread/comment locks, ad creation/boosting/promotion, cart/basket/bag/wishlist/waitlist additions, removals, or quantity changes, checkout address changes, promo/coupon/offer actions, order placement/cancellation/returns/refunds/payments, purchases/bids/donations/checkouts, profile/account changes, destructive account actions, and clicking/tapping/pressing/selecting/activating final write buttons or controls.

Treat undo/removal wording as external write wording too: unlike, unreact, unbookmark, unsave, unfavorite, unstar, stop watching, trash/restore cloud files, cancel/reschedule calendar events, cancel scheduled posts/messages/emails, remove CRM records from campaigns or sequences, and unenroll contacts.

Draft-only text preparation does not require approval when the request explicitly says not to publish, post, comment, reply, respond, message/DM, send, or submit. **Revenue Partner exception:** any request containing an ad/advert/advertisement/advertising/campaign object is approval-gated if routed through Super Browser; prepare internal campaign drafts as local Hermes text work instead. The provider prompt must derive the draft-only boundary from current policy classification, not only from mutable stored plan flags, and must still tell the browser agent to stop before any final publish, post, comment, reply, respond, message/DM, send, submit, upload, follow, connect, react, share, CRM/cart/order/payment/trading/banking/payout/legal/government/health/insurance/identity/project/repository/cloud-file/sharing/integration/settings/secrets/infrastructure/billing/workspace/channel/role/moderation/notification/message-state/member/account change, click, tap, press, select, or activate control. Hyphenated content terms such as "follow-up" do not count as the platform action "follow" unless the request actually asks for a follow/following action. Business/content phrases such as "lead magnet," "invite template," "posting schedule," "apply a filter," "book notes," or "review summary" stay non-external unless the request also asks for a real site/account state change. Public documentation, help articles, guides, policy pages, best-practice pages, examples, and local notes about sharing, OAuth, tokens, auth, integrations, API keys, webhooks, DNS records, environment variables, billing, trading, banking, ACH/wire transfers, payouts, legal forms, tax filing, insurance claims, prescriptions, medical records, passports, visas, government IDs, channels, workspaces, roles, or moderation stay read-only when the full request stays reference-only. Creating local lead/contact/prospect/customer lists, CSVs, JSON files, or run artifacts from extracted data is local output, not an external write; writing or syncing those records into CRM, Salesforce, HubSpot, Pipedrive, Zoho, Apollo, campaigns, sequences, or pipelines remains approval-gated. File uploads, credential-bearing work, and ambiguous "draft and post" or "write and send" requests still require approval.

Read-only scanning of visible public posts, comments, forum messages, and group content is allowed as a read task only when the full request stays read-only. Reading personal inboxes, DMs, or private messages is credential-bearing and requires approval. A browse/read/search/list prefix does not neutralize a later write: scanning plus posting, commenting, replying, responding, sending, liking, following, connecting, submitting, CRM updates, cart/order/payment/trading/banking/payout changes, legal/government/health/insurance/identity changes, project/repository updates, cloud-file/sharing/integration/settings changes, secret/API-key changes, webhook/deployment/DNS/environment-variable changes, billing/payment-method changes, workspace/channel/role/moderation changes, thread locks, notification toggles, archive/read-state changes, member removals, or pressing final write controls remains approval-gated.

Submitting public search, filter, or sort forms only to fetch visible public results is read-only when the query does not include credentials, private/personal data, or another external action. Public documentation, help articles, guides, policy pages, best-practice pages, examples, and local notes about sharing, OAuth, tokens, auth, integrations, API keys, webhooks, DNS records, environment variables, billing, trading, banking, ACH/wire transfers, payouts, legal forms, tax filing, insurance claims, prescriptions, medical records, passports, visas, government IDs, channels, workspaces, roles, or moderation are also read-only when the full request stays reference-only. These exceptions do not cover a later like, save, bookmark, share, follow, connect, CRM update, cart/order/payment/trading/banking/payout change, legal/government/health/insurance/identity change, project/repository update, cloud-file/sharing/integration/settings change, secret/API-key change, webhook/deployment/DNS/environment-variable change, billing/payment-method change, workspace/channel/role/moderation change, notification toggle, message/email state change, or other external write in the same request. Lead, contact, application, checkout, signup, comment, message, quote, demo, pricing, upload, payment, registration, review, poll, booking, appointment, reservation, subscribe, and unsubscribe forms remain approval-gated.

Local delivery wording such as "send me a summary" or "send us the report" is read-only only when it is not combined with an external action. A mixed request like "send me the findings, then post a comment" or "send me a summary and email this lead" is still an external write and stops for approval.

Local production approval and execution are disabled in this template. Approval-required runs remain `awaiting_approval`; activation requires an operator-reviewed integration outside the agent runtime and a rebuilt release.

Use `super-browser deny <run-id> --by <actor> --reason <audit-note>` or `deny_browser_run` with `by` and `reason` to record denial and prove the write was stopped.

The low-level `execute_plan()` adapter path is guarded too. It re-checks task policy and unconditionally blocks approval-gated plans. It has no approval boolean or approval-context parameter.

Approval requests retain approval id, required stage, action fingerprint, and plan fingerprint as audit evidence. This template has no approval command or production resume path: every approval-required plan remains stopped, including retries and hand-built run records.

Legacy approval timestamps remain verifier evidence only. They never enable provider execution in this template.

Provider prompts must include the current policy boundary for read-only, authenticated read/navigation, draft-only, and external-write runs. Prompt safety is a provider-control layer only; never treat it as a substitute for durable approval records, adapter/runtime guards, target-scope checks, duplicate-write retry protection, verifier policy guards, or handoff approval-integrity checks.

## Resume Lifecycle

Use `super-browser get <run-id>` or `get_browser_run` for read-only lookup. Use `super-browser handoff <run-id>` or `handoff_browser_run` when another agent needs the compact run summary, route, provider readiness, approval state, verifier summary, commands, docs, and next steps. Handoff safety and durability fields such as `task.external_write`, `task.requires_auth`, `task.draft_only`, `task.long_running`, `route.approval_required`, and `approval.required` must come from verifier `policy_guard`, not only from mutable stored plan flags. Use `super-browser runs --status <status> --limit 20` or `list_browser_runs` when an agent needs to discover saved runs after compaction, handoff, or a lost run id. Run lists are compact summaries by default; use CLI `--details` or MCP `include_details=true` only when the full payload list is needed. Empty lookup/list calls do not create `.super-browser` state. If a stored run payload cannot be decoded, lookup/list should surface `store_payload_corrupt` as a low-confidence failed record; resume must block before provider dispatch, and the agent should create a new run instead of treating it as a provider failure.

Use `super-browser resume <run-id>` or `resume_browser_run` only for approval-free read-only runs. Approval-required runs stay stopped. Read-only execution is atomically claimed, active leases remain no-ops, stale leases are recovered conservatively, and integrity or provider-constraint failures block before dispatch.

## Routing Defaults

Routing is capability-first: the router asks "what does the task need?" and filters providers by capability (auth, anti-bot, CAPTCHA, profiles, proxy injection, fleet, desktop, raw HTTP). An escalation rank then orders equally capable providers from cheapest/most deterministic to most expensive — it is a cost tie-breaker, not the routing model. See `references/routing-playbook.md` for the capability table.

- Local Playwright → exact allowlisted loopback/local-file fixtures only. JavaScript and downloads are disabled; requests are bodyless GET/HEAD only; text and viewport screenshot artifacts are bounded. Public-web navigation is non-executable.
- Airtop, Browser Use, Browserbase, Hyperbrowser, Orgo, and Steel → planning/reference only. This image cannot enforce target DNS, redirect, and connected-peer policy inside hosted or autonomous execution, so construction is blocked.
- Raw HTTP → only a concrete public IP-literal `http://`/`https://` endpoint. Hostname targets and hostname redirects are blocked because direct/proxy resolution cannot be pinned.
- If neither executable lane satisfies the request, stop and report the exact peer-address-enforcement blocker.
- Caller-supplied, named, and operator/environment proxy routes are non-executable in this image.

## Council Reports

Every `super-browser plan` result includes `council_report`. Use it to inspect capability/provenance comparisons, technically eligible local lanes, review loops, immutable blockers, and the verification contract before execution.

Use `--allow-provider` for strict provider allowlists, `--max-cost-usd` for cost-floor routing, and `--timeout-seconds` for a provider execution ceiling. Planning fails if no provider satisfies the constraints. The planner avoids URL-required providers when no starting URL is available. Raw HTTP/API tasks require a concrete `http://` or `https://` starting URL; if the endpoint is missing, planning fails instead of silently switching to a browser provider. URLs embedded in prose or Markdown goals have common trailing delimiters stripped, including `>`, `]`, quotes, and sentence punctuation; explicit URLs with raw whitespace are rejected and should use percent encoding. Runtime execution, verifier, handoff, and direct resume re-check task payload validity, URL-derived target scope, provider allowlists, file-URL provider restrictions, unknown providers, URL-required primary providers without a starting URL, raw HTTP without an HTTP endpoint, and max-cost ceilings before provider dispatch, so a stale or hand-built plan cannot smuggle malformed constraints, downgrade a sensitive target scope, or widen the selected sequence. Inspect `cost_estimate`, `task.timeout_seconds`, and `council_report.planner_decision.timeout_seconds` before execution.

Use `super-browser doctor` or `browser_doctor` before executable local reads. Treat `usable_now` as conditional on the current task and target evidence. Hosted/autonomous records remain `non_executable_in_image` regardless of credentials or historical evidence. `runtime_missing` means the local Playwright runtime cannot launch. `decodo-http` can be `usable_direct_http_no_proxy`, which means direct raw HTTP may run only for a policy-eligible public IP-literal endpoint without a proxy.

Use `super-browser production-readiness` or MCP `production_readiness` as a local-lane status report. Hosted providers remain planning-only regardless of credentials or historical live evidence. Playwright readiness certifies the exact fixture workflow only, never public navigation.

Use `super-browser setup` or MCP `setup_walkthrough` for baked-runtime verification, doctor output, and read-only fixture verification. The provider-signup registry is empty. Hosted-provider credentials and proxy configuration do not create an executable route in this image.

Use `super-browser bundle-manifest` or MCP `bundle_manifest` before handing Super Browser to another agent, auditing an installed bundle, or preparing a release. The manifest is the authoritative hashed inventory of bundle files, entrypoints, specialist skills, providers, MCP tools, and docs resources. Installed bundles include `super-browser-manifest.json`.

Provider transport overrides, credentials, and historical live-test records do not activate hosted or autonomous providers. Their records are planning/provenance only.

Use `super-browser live-test --provider fixtures` to run local browser fixtures for login, infinite scroll, draft-only forms, social feed scanning plus comment drafting without publishing, lead-generation extraction to local output without CRM/email actions, modal handling, upload selection, blocked pages, and resume recovery.

Use `workflow_class=external_write_gate` to prove a provider-locked post/comment-style task stops in `awaiting_approval` before any provider execution starts. This is a safety-gate proof; it does not approve or execute a real external write.

## Execution Reports

Eligible read-only runs execute the primary local provider and then eligible planned fallbacks until one succeeds or all stop. Approval-required and hosted-provider work cannot execute or resume in this image; approval records are audit evidence only. If an adapter raises unexpectedly, treat it as a redacted failed provider attempt with `provider-exception.json` metadata. If the runtime execution boundary raises after a run is claimed, treat `runtime-exception.json` plus the failed `run-report.json` as execution evidence; external-write retries remain non-executable. Inspect `run-report.json` or `super-browser verify <run-id>` to see every provider attempt, blocked reason, selected provider, artifact manifest, timeout checks, cost estimate, `plan_sha256`, and confidence.

`super-browser verify <run-id>` actively checks artifact paths, SHA-256 hashes, the run-report plan fingerprint, provider sequence constraints, final-provider/attempt consistency, approval id/stage/fingerprint/decision integrity, and `run-report.json`, reports provider cost band and trace links, lists failures, and writes `verification-report.json` when a report directory exists. Inspect `plan_integrity` before trusting artifacts; a mismatch means the stored run plan and run report do not match. Handoff and direct resume treat `plan_integrity.status=mismatch` or `missing`, verifier failures `missing_run_report`, `missing_artifact_path`, `artifact_hash_mismatch`, `status_mismatch`, impossible final-provider/attempt evidence, provider constraint failures, and `approval_integrity.status=missing`, `mismatch`, `missing_fingerprint`, `missing_approval_id`, `missing_required_before`, `invalid_required_before`, `missing_decision_metadata`, or `unknown_status` as unsafe to resume. Inspect `approval_integrity` as audit evidence only; any approved state remains non-executable in this image, and a mismatch means the record no longer matches the current plan. Inspect `policy_guard` for target scope, approval state, safety events, blocked reasons, and duplicate-write retry state before trusting or retrying a run.

Use `super-browser handoff <run-id>` or `handoff_browser_run` when another agent needs the same verifier policy guard and approval integrity in a compact, read-only package. Treat `approval_status=missing` or `approval_integrity.status=mismatch` as a broken approval-gate record, not as permission to run.

Any external-write retry remains blocked because local production approval and execution are disabled.

Agent-facing CLI/MCP output, saved reports, raw HTTP text/JSON bodies, provider output JSON, and page text artifacts redact cookies, authorization headers, API keys, bearer tokens, token query parameters, passwords, and client secrets. Provider session IDs stay visible when they are needed for debugging. Binary raw HTTP bodies are preserved with metadata.

Do not place credentials in a URL. Super Browser rejects starting URLs with embedded username/password credentials, and redaction strips URL userinfo if a provider returns it in logs or artifacts.

Use local `file://` URLs only with Playwright/local fixtures. Super Browser extracts local file URLs from either the explicit URL field or the goal text, will not route them to cloud providers or raw HTTP, and runtime provider-sequence checks block stale or hand-built file-URL plans before provider dispatch. Raw HTTP supports only `http://` and `https://` and must include that endpoint during planning. `local_file` targets require approval because they can expose machine data.

Inspect `target_scope` in every plan. `loopback`, `private_network`, `link_local`, and `local_file` all require approval and are non-executable by default. Loopback and local-file execution exist only in explicit process-level test mode when the exact URL appears in the operator-declared JSON test allowlist; adapters re-check this boundary.

Raw HTTP public execution accepts only public IP-literal starting URLs and public IP-literal redirects. Hostname redirects and sensitive-address literals are blocked before follow-up requests.

Local Playwright runs only exact allowlisted loopback/local-file fixtures. It disables JavaScript, downloads, service workers, WebSockets, and auxiliary channels; permits only bodyless GET/HEAD; bounds extracted text and viewport screenshots; and rejects every public-web target before browser construction.

Hosted and autonomous URL providers are blocked before construction because this image cannot verify their connected peer address or constrain every redirect. Target-scope, address-pinning, and provider-enforcement failures are non-resumable; create a new plan only after changing to an enforceable lane.

## References

- `references/provider-matrix.md`
- `references/routing-playbook.md`
- `references/cost-model.md`
- `references/security-and-approval-policy.md`

