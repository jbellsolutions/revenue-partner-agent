# Security And Approval Policy

Super Browser can interact with real websites and computers. Policy must be enforced in code and in agent instructions.

## Risk Classes

| Risk | Examples | Default |
| --- | --- | --- |
| Read-only | Open page, screenshot, extract text, inspect DOM | Allow |
| Mutating browser/provider | Type into a page, fill a field, click a control, or otherwise change interactive state | Require approval; non-executable in this image |
| External write | Post, comment, reply/respond, DM, email, submit non-search/state-changing form, upload file, like/react/upvote/downvote/follow/connect/share/quote/repost/story, star/watch/fork repos, bookmark/save/pin/favorite content, join/create group, create event/page, accept/decline/remove/cancel/confirm requests/invites/connections, remove followers/friends/members, RSVP/check in/interested/going, report/block/mute, notification toggles, message/email archive/read-state changes, tag/mention, book/schedule, request info/demo/quotes/pricing, apply, subscribe, review, poll vote, CRM lead/contact/customer create/assign/enroll/stage/list updates, project/repository issue, ticket, task, card, pull-request, and repo changes, cloud file/folder/document creation, renames, moves, copies, sharing/access/permission/public-visibility changes, app/integration install/authorize/connect changes, settings/preference saves, API-key/token creation, rotation, or revocation, secret reveal/copy requests, webhook creation or updates, deployment creation/promotion/rollback/redeploys, DNS record/nameserver changes, environment-variable changes, billing trial/plan/payment-method changes, trading orders, asset sales, swaps, staking, unstaking, position opens/closes/liquidations, withdrawals, deposits, fund transfers, ACH/wire/bank transfers, bank/wallet/brokerage/payout account changes, legal signatures/certifications/attestations, tax and court filings, insurance claim/policy changes, benefits or health-plan enrollment changes, prescription refills, medical form/record delivery, passport/visa/government-ID actions, voter registration, regulated address changes, emergency contact changes, workspace/channel/server/community/page creation, rename, archive, or unarchive changes, member additions, kicks, bans, unbans, role changes, thread/comment locks, create/boost/promote ads, add/remove/change cart/basket/bag/wishlist/waitlist items, change checkout addresses, apply promo/coupon/offer actions, place/cancel/return/refund/pay orders, purchase/bid/donate/checkout, click/tap/press/select/activate final write controls | Require approval |
| Credential-bearing | Login, 2FA, OAuth, cookies, profiles, tokens, API keys, client secrets, private keys | Require approval and audit |
| Destructive | Delete, reset, purchase, cancel, account settings | Require explicit approval |

Undo and removal actions are still external writes. Unlike/unreact, unbookmark/unsave/unfavorite, unstar/stop watching, trash/restore cloud files, cancel/reschedule calendar events, cancel scheduled posts/messages/emails, remove CRM records from campaigns or sequences, and unenroll contacts all require approval.

## Approval Payload

Before an external write, show:

- Target site and URL.
- Account/profile identity if known.
- Exact content or action.
- Audience or recipient.
- Irreversible consequences.
- Provider and trace/artifact.
- Fallback if denied.

## Draft-Only Workflows

Draft-only text preparation is allowed without approval only as local Hermes text work, with no browser/provider interaction. Typing into a page, filling a field, clicking a control, or otherwise changing interactive state is `mutating`, requires approval, and is non-executable in this image. A request to use Super Browser for draft placement must stop at `awaiting_approval`; draft language never authorizes provider execution. Policy classification is recomputed from the current request rather than trusted from mutable stored `task.draft_only` state. Examples:

- Draft a comment locally but do not publish it.
- Draft a reply as local text without opening or editing the destination page.
- Prepare form copy locally without filling the remote form.

Read-only scanning of visible public posts, comments, forum messages, and group content is allowed as a read task only when the full request stays read-only. Reading personal inboxes, DMs, private messages, or private/member-only content is credential-bearing and requires approval. A browse/read/search/list prefix does not neutralize a later write. If a scanning task also asks the agent to post, comment, reply, send, follow, connect, submit, update CRM state, change cart/order/payment/trading/banking/payout state, change legal/government/health/insurance/identity state, update project/repository state, change cloud-file/sharing/integration/settings state, change secrets/API keys, change webhooks/deployments/DNS/environment variables, change billing/payment methods, change workspace/channel/role/moderation state, lock a thread, toggle notifications, archive or mark messages/email, remove a member, or click, tap, press, select, or activate a like/follow/send/submit/publish-style control, treat it as an external write.

Submitting public search, filter, or sort forms only to fetch visible public results is read-only when the query does not include credentials, private/personal data, or another external action. Public documentation, help articles, guides, policy pages, best-practice pages, examples, and local notes about sharing, OAuth, tokens, auth, integrations, API keys, webhooks, DNS records, environment variables, billing, trading, banking, ACH/wire transfers, payouts, legal forms, tax filing, insurance claims, prescriptions, medical records, passports, visas, government IDs, channels, workspaces, roles, or moderation are also read-only when the full request stays reference-only. These exceptions do not cover a later like, save, bookmark, share, follow, connect, CRM update, cart/order/payment/trading/banking/payout change, legal/government/health/insurance/identity change, project/repository update, cloud-file/sharing/integration/settings change, secret/API-key change, webhook/deployment/DNS/environment-variable change, billing/payment-method change, workspace/channel/role/moderation change, notification toggle, message/email state change, or other external write in the same request. Lead, contact, application, checkout, signup, comment, message, quote, demo, pricing, upload, payment, registration, review, poll, booking, appointment, reservation, subscribe, and unsubscribe forms remain approval-gated.

Local delivery wording such as "send me a summary" or "send us the report" is read-only only when it is not bundled with an external action. A mixed request that asks for local delivery and also asks the agent to post, email, DM, submit, like, follow, or press a final write control must stop for approval.

The system must still stop before any publish, post, comment, reply/respond, send, DM, non-search/state-changing submit, upload, like, react, upvote/downvote, star/watch/fork repo, bookmark/save/pin platform content, follow/connect, share, join/leave group, accept/decline/remove request/invite/connection, remove a member, RSVP/check in/mark interested/mark going, report/block/mute, toggle notifications, archive or mark email/messages, tag/mention, book/schedule/reserve, request info/demo/quote/pricing, apply, subscribe, CRM lead/contact/customer creation, assignment, enrollment, stage, status, list, campaign, or sequence change, project/repository issue, ticket, task, card, pull-request, or repo changes, cloud file/folder/document creation, rename, move, copy, sharing/access/permission/public-visibility changes, app/integration install/authorize/connect changes, settings/preference saves, API-key/token creation/rotation/revocation, secret reveal/copy requests, webhook creation/updates, deployment creation/promotion/rollback/redeploys, DNS record/nameserver changes, environment-variable changes, billing trial/plan/payment-method changes, trading orders, asset sales, swaps, staking, unstaking, position opens/closes/liquidations, withdrawals, deposits, fund transfers, ACH/wire/bank transfers, bank/wallet/brokerage/payout account changes, legal signatures/certifications/attestations, tax and court filings, insurance claim/policy changes, benefits or health-plan enrollment changes, prescription refills, medical form/record delivery, passport/visa/government-ID actions, voter registration, regulated address changes, emergency contact changes, workspace/channel/server/community/page creation, rename, archive, or unarchive changes, member additions, kicks, bans, unbans, role changes, thread/comment locks, cart/basket/bag/wishlist/waitlist additions/removals/quantity changes, checkout address changes, promo/coupon/offer actions, order placement/cancellation/returns/refunds/payments, purchase, account change, credential use, destructive action, or click/tap/press/select/activate action on a final write button, icon, link, or control. Uploads are treated as external writes even when later form submission is not requested, because selecting a file can expose local data to a website.

Provider prompts must carry the current policy boundary in addition to the runtime gate. Only policy-classified read work may reach a technically read-only extraction provider in this image. Credential-bearing, mutating, external-write, and destructive plans remain `awaiting_approval` and never reach adapter/provider execution. Prompt instructions are defense in depth, not authorization. Because Browser Use and Orgo expose autonomous interaction without an independently enforced action interceptor, any plan containing either is blocked before adapter construction, including nominally read-only plans.

Caller-controlled proxy URLs are not accepted. Named task values and operator/environment proxy configuration also resolve to no executable route in this image; proxy-dependent work stops before network access.

## Logging

Every run records:

- Provider choice and fallback providers.
- Missing env vars.
- Risk class.
- Target scope: public web, loopback, private network, link-local, local file, or none.
- Approval-required flag.
- Artifact list.
- Verification confidence.
- Pending, approved, or denied approval requests.
- External-write attempt fingerprints and retry blocks.

## Combined Credential And Write Risk

Treat risk as cumulative. A task such as "use my logged-in profile to post a comment" is both credential-bearing and an external write. The external-write flag must remain set so duplicate-write retry protection applies after a failed approved attempt.

Credential-bearing browser use includes authenticated sessions, cookies, tokens, passwords, passkeys, API keys, access tokens, client secrets, private keys, service account keys, and local Chrome/browser profiles. Public profile extraction is read-only unless the task also asks to use a logged-in, authenticated, local, existing, or user-owned profile/session.

## Production Write Protection

Approval requests retain ids, stages, action fingerprints, and plan fingerprints as audit evidence. No local interface can approve them, and runtime plus low-level adapters unconditionally block every approval-required plan. External writes never start or retry in this template.

## Redaction

Super Browser redacts high-risk secrets before writing provider metadata, provider output JSON, raw HTTP text/JSON body artifacts, page text artifacts, `run-report.json`, `verification-report.json`, stored run payloads, and CLI/MCP run responses. Redacted values include:

- Authorization and proxy-authorization headers.
- Cookies and set-cookie headers.
- API keys and `x-api-key` headers.
- Bearer/basic tokens, JWT-like strings, and token env assignments.
- `token`, `access_token`, `refresh_token`, `id_token`, `api_key`, `client_secret`, `password`, `secret`, and similar query parameters.
- URL username/password userinfo.

Provider session IDs and run IDs remain visible unless they are explicitly token-like, because they are needed for debugging and provider support. Binary raw HTTP response bodies are preserved as binary artifacts with metadata; text and JSON raw HTTP bodies are redacted before being written.

Starting URLs with embedded username/password credentials are rejected before state is created. Explicit URLs with raw whitespace are rejected; agents should percent-encode spaces as `%20`. URLs extracted from prose or Markdown goals strip common trailing delimiters such as `>`, `]`, quotes, and sentence punctuation before target-scope classification. Use environment variables, browser profiles, or provider-native auth instead of URL userinfo.

Local `file://` URLs are supported only for local Playwright fixtures and local browser testing. Router URL extraction detects local file URLs in goal text as well as explicit URL fields. Router constraints keep file URLs on Playwright, and the raw HTTP adapter rejects non-HTTP schemes even for hand-built plans. Raw HTTP/API planning requires a concrete `http://` or `https://` endpoint, so missing endpoints and `file://` targets do not fall through to browser providers. `local_file` targets require explicit approval because they can expose machine data.

Provider routing constraints are security controls, not hints. The planner must avoid URL-required providers when no starting URL is available and must reject raw HTTP/API work unless an HTTP endpoint is present. Verifier, handoff, direct resume, and low-level `execute_plan()` must re-check the stored task payload plus primary/fallback sequence before provider dispatch. Malformed task constraints, embedded URL credentials, stale stored target scopes that no longer match the URL-derived scope, unknown providers, providers outside `providers_allowed`, non-Playwright providers for local `file://` URLs, URL-required primary providers without a starting URL, raw HTTP without an HTTP endpoint, and providers above `max_cost_usd` must block with provider-constraint evidence instead of calling an adapter.

Live-test evidence is a trust-scoped signal, not an unrestricted credential for production use. Doctor must filter persisted evidence to the workflow classes the provider supports and to records whose embedded provider identity matches the provider being certified before setting `readiness_status`, `certified_workflow_classes`, or `production_ready_scope`. Hand-built, stale, incompatible, copied, or provider-mismatched evidence must be listed in `ignored_unsupported_evidence_workflow_classes` or `ignored_provider_mismatch_evidence_workflow_classes` and must not make the provider appear production-ready for that class.

HTTP and file targets are classified by scope. `loopback`, `private_network`, `link_local`, and `local_file` targets force council-mode visibility so agents do not confuse localhost, intranet, metadata-service, or machine-file access with ordinary public-web browsing. Raw HTTP and Playwright metadata include the same `target_scope`.

`loopback`, `private_network`, `link_local`, and `local_file` targets require approval and remain non-executable by default. The only fixture exception requires process-level `SUPER_BROWSER_TEST_MODE=1` plus the exact loopback/local-file URL in `SUPER_BROWSER_TEST_TARGET_ALLOWLIST_JSON`; policy and the final adapter boundary both re-check it. This is not production approval.

Raw HTTP public execution requires a public IP-literal start and public IP-literal redirects. Hostname redirects and sensitive/reserved literals are blocked before follow-up requests; no response body is saved for the blocked attempt.

Local Playwright executes only exact allowlisted loopback/local-file fixtures under process test mode. Public-web targets are rejected before browser construction. Fixture contexts disable JavaScript, downloads, service workers, WebSockets, and auxiliary channels; allow only bodyless GET/HEAD; and bound extracted text and viewport screenshot artifacts.

Local DNS preflight alone is never authorization. Public Playwright navigation is non-executable because hostile navigation bytes cannot be strictly bounded. Raw HTTP avoids target DNS by requiring public IPv4 literals and aborts responses beyond 2 MiB. Airtop, Browser Use, Browserbase, Hyperbrowser, Orgo, and Steel are blocked before construction because this image cannot verify their connected peer or constrain every redirect. These safety stops are non-resumable.

Hosted-provider transport overrides and credentials do not enable execution in this image. Blocked providers are stopped before transport construction, so credentials and target URLs are not sent. Exact local fixture access uses only the narrow test-mode URL allowlist described above.

`timeout_seconds` is an execution-control field, not a safety approval. It sets a provider operation ceiling and is recorded in task plans, handoff output, provider metadata, and verification checks. Adapters must enforce it with native browser, HTTP, SDK, or CLI timeouts rather than unbounded background workers.

## CLI And MCP

```bash
super-browser get <run-id>
super-browser handoff <run-id>
super-browser runs --status awaiting_approval --limit 20
super-browser deny <run-id> --by "human" --reason "not approved"
```

Approval and denial actors and reasons are required. Empty decision actors or reasons are rejected so every approval record has a human/agent identity and audit note tied to the exact action being approved or denied.

MCP tools:

- `get_browser_run`
- `handoff_browser_run`
- `list_browser_runs`
- `deny_browser_run`
- `production_readiness`
- `bundle_manifest`
- `env_checklist`
`get`, `handoff`, `runs`, `get_browser_run`, `handoff_browser_run`, and `list_browser_runs` are read-only. They must not create provider attempts, approvals, resume events, or empty `.super-browser` state when no run database exists. `handoff` may compute verifier state in memory, but it must not write `verification-report.json`. Run lists return compact summaries by default; callers must explicitly request details when they need full payload lists. If a stored row payload cannot be decoded, read-only lookup/listing must surface a low-confidence failed record with `store_payload_corrupt`; it must not hide the row or crash the agent.

MCP tool annotations label read-only inspection and eligible read execution tools for client planning, but policy is enforced in the router, runtime, and adapter guard. Clients must not treat annotations as a substitute for policy checks. MCP schemas reject all proxy input, validate `timeout_seconds` as an integer of at least 1, and reject whitespace-only string arguments before execution is dispatched. Approval is absent from MCP, CLI, handoff, and agent command surfaces; approval-required runs remain non-executable inside this template runtime. `resume_browser_run` can dispatch only approval-free technically read-only plans. `env_checklist`, `bundle_manifest`, and `setup_walkthrough` are read-only and return no secret values. Install/config-write, profile create/delete, and Slack-daemon controls are absent from MCP and CLI; integration changes require a separately reviewed rebuild.

CLI commands return JSON on success and redacted stderr JSON with `error` and `error_type` for known Super Browser command failures. Recoverable MCP tool failures, including missing runs, rejected arguments, malformed `tools/call` params, missing or blank tool names, non-object tool arguments, and unexpected exceptions from known tools, return `isError: true` with redacted structured error details and `error_type`. Unknown tools, unsupported protocol methods, malformed `resources/read` envelopes, malformed JSON, and non-object JSON-RPC requests remain protocol errors. Well-formed JSON-RPC notifications without an `id` are consumed without a response. Malformed JSON or non-object requests return a `null` id and must not inherit an earlier request id.

MCP `resources/list` and `resources/read` expose only allowlisted read-only markdown docs from `README.md`, `SKILL.md`, `references/`, and `skills/*/SKILL.md`. Resource paths are resolved and must stay inside a verified Super Browser repository, installed bundle root, or packaged `share/super-browser` asset tree, so symlinks, path escapes, invalid `SUPER_BROWSER_REPO_ROOT` values, package current working directories, and unrelated project files are skipped in listings and rejected on direct reads. Resource reads must not expose arbitrary filesystem paths or create local state.

There is no local approval or production-execution command. Resume is limited to approval-free read-only runs.

Executing runs carry a durable lease. A resume call during an active lease records a no-op and preserves the lease; it must not dispatch another provider worker. Long-running lease duration must derive from current policy classification as well as stored task flags so stale run records cannot shorten monitor, overnight, recurring, or crawl runs. When provider execution reaches a terminal result, the runtime clears the lease so later handoffs do not treat the finished run as still active.

Verifier and handoff output must expose `policy_guard` with target scope, approval-required flag, approval status, external-write/auth/draft/long-running flags, safety events, blocked reasons, and duplicate-write retry state. Handoff top-level safety and durability fields, including `task.external_write`, `task.requires_auth`, `task.draft_only`, `task.long_running`, `route.approval_required`, and `approval.required`, must use the same policy-derived values so stale stored plan flags cannot make the compact package appear safe or less durable. They must also expose `approval_integrity` so agents can see whether the latest pending, approved, or denied request still has an id, valid stage, fingerprints, and required decision metadata. Agents must inspect both before retrying or trusting a run. `approval_status=missing` means the plan required approval but the approval record is absent; `approval_integrity.status=mismatch` means the approval record no longer matches the current plan. Treat either as a policy bug and do not execute. Direct resume must record `resume_blocked` before any execution claim when approval integrity is `missing`, `mismatch`, `missing_fingerprint`, `missing_approval_id`, `missing_required_before`, `invalid_required_before`, `missing_decision_metadata`, or `unknown_status`.

Run reports must include `run_id` and `plan_sha256`, and verifier/handoff output must expose `run_id_integrity` and `plan_integrity`. Run ids must be safe generated `run_*` ids; dot-segment or otherwise invalid ids must be reported as `invalid_run_id` and must not define artifact roots. Ordinary terminal failed, blocked, or complete runs must have a readable `run-report.json`; if not, verifier must report `missing_run_report`. A `run-report.json` whose `run_id` does not match the saved run id must be reported as `run_report_run_id_mismatch`. Artifact paths are trusted only when they resolve inside `.super-browser/artifacts/<run-id>/` or the configured `SUPER_BROWSER_STATE_DIR` equivalent; verifier must not read or hash outside paths and must report `untrusted_artifact_path` instead. Missing artifact paths must be reported as `missing_artifact_path`, and changed artifact hashes must be reported as `artifact_hash_mismatch`. If multiple run-report artifacts exist, verifier must use the newest one. A successful resumed provider execution must replace stale execution artifact records while preserving the durable plan artifact and event history, so old failed report hashes cannot make the current run look corrupted. If the stored run id is invalid, if the stored payload is marked `store_payload_corrupt`, if the terminal run report is missing outside stale-recovery or retry-approval setup, if an artifact path is missing or hash-mismatched, if the report belongs to a different run id, if the stored run plan does not match the report fingerprint, if `run-report.json` `final_status` does not match the saved run status, if the final provider or attempt history is inconsistent with the stored provider sequence, if artifact paths are outside the run's artifact directory, or if verifier reports a provider sequence constraint failure, treat the run as untrusted evidence. Handoff must mark resume unsafe when `run_id_integrity` is invalid, when `plan_integrity` is `mismatch` or `missing`, when verifier failures include `invalid_run_id`, `store_payload_corrupt`, `missing_run_report`, `missing_artifact_path`, `artifact_hash_mismatch`, `run_report_run_id_mismatch`, `untrusted_artifact_path`, `status_mismatch`, `run_report_final_provider_not_planned`, `run_report_complete_without_complete_attempt`, `run_report_final_provider_attempt_mismatch`, `run_report_final_provider_attempt_missing`, or `run_report_final_status_attempt_mismatch` outside explicit stale read-only recovery, or when provider constraints fail; direct resume must record `resume_blocked` before any provider retry. Do not retry it as a provider failure; inspect the run store and artifacts or create a new run.

The low-level adapter API must not be an escape hatch. `execute_plan()` re-checks task policy, task payload validity, URL-derived target scope, and provider sequence constraints, and unconditionally blocks approval-gated plans. It exposes no approval boolean or approval-context parameter.

Provider adapter exceptions are execution evidence, not approval or policy bypasses. `execute_plan()` must redact the exception message, save `provider-exception.json`, mark that provider attempt `failed`, and continue only to providers already present in the approved/planned sequence. An adapter crash must not clear an approval gate, widen the fallback list, leak secrets, or leave the run without a final run report when the execution loop can still return a structured result.

Runtime execution exceptions after a durable read-only claim are execution evidence, not active workers. The runtime must redact the exception message, save `runtime-exception.json`, write a failed `run-report.json` with `run_id` and `plan_sha256`, and clear the execution lease. Approval-required plans never reach this point.

## Non-Negotiables

- Never request API keys or passwords in chat.
- Never put secrets in prompts, logs, screenshots, or traces when avoidable.
- Never auto-submit posts, comments, DMs, account changes, payments, or destructive actions by default.
- Do not retry an external write after a crash without deduplication and review.
