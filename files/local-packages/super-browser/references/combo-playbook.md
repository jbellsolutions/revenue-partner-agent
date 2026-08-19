# Super Browser Combo Playbook — locked image

This image does not execute provider combinations. A plan may compare provider records for cost, capability, and provenance, but execution is limited to one enforceable local read lane.

## Executable choices

1. **Exact local Playwright fixtures** — loopback/local-file only under process test mode and an exact URL allowlist, with JavaScript/downloads disabled, bodyless GET/HEAD enforcement, bounded text, and a fixed viewport screenshot.
2. **Bounded direct raw HTTP** — public IPv4-literal HTTP(S) starts and redirects, with no proxy and a strict 2 MiB response ceiling.

Public-web Playwright navigation is non-executable because hostile navigation bytes cannot be strictly bounded in this immutable image.

## Planning-only records

Airtop, Browser Use, Browserbase, Hyperbrowser, Orgo, and Steel may appear only in comparison/provenance output. Do not construct a hosted session, connect CDP, submit a prompt or URL, configure credentials, or run a provider live test in this image.

If a request needs anti-bot cloud infrastructure, geo-targeting, a proxy, an authenticated profile, a hosted browser, or computer use, stop and report the exact enforcement blocker. A separately reviewed integration and rebuilt release are required.

## Approval and verification

External writes, credentials, authenticated profiles, production changes, and unknown or ambiguous intent stop before provider construction. Planning evidence is never execution evidence. A complete executable read records the selected single lane, target evidence, provider attempt, blocked requests, artifact hashes, and verifier result.
