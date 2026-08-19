---
name: playwright-specialist
description: "Use for exact allowlisted local Playwright fixtures; deterministic fixture verification only because public navigation is non-executable."
---

# Playwright Specialist

## Use For

- Local deterministic browser control.
- Web app testing and visual verification.
- Known selectors, screenshots, DOM extraction, and read-only fixture sites.
- Exact allowlisted loopback/local-file fixture verification.

## Do Not Use For

- Advanced anti-bot sites such as Meta, LinkedIn, Cloudflare-heavy pages, PerimeterX, or DataDome.
- Any public-web navigation or logged-in personal Chrome session.
- Tasks where natural-language exploration is more important than deterministic control.

## Setup

Use Playwright and Chromium baked by the verified image builder from committed locks. Do not install packages into the running image.

## Verification

Use bounded text and fixed-viewport screenshots for the exact fixture lane. JavaScript, downloads, service workers, WebSockets, auxiliary channels, request bodies, and non-GET/HEAD methods are disabled.

`super-browser doctor` must report `ready_local` with `browser_runtime_available=true` before treating local Playwright as usable. If it reports `runtime_missing`, stop. An operator must update committed locks, rebuild the image, run complete release verification, and publish a new release; runtime installation is prohibited.

Super Browser rejects public Playwright targets before browser construction. Exact fixture targets require process test mode and an exact URL allowlist. Any method, request-body, target-scope, or artifact-size block is a non-resumable safety stop.
