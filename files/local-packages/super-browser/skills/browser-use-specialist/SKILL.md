---
name: browser-use-specialist
description: "Planning-only Browser Use reference; execution is hard-blocked in this Revenue Partner release."
---

# Browser Use Specialist — planning only

Browser Use remains in the provider catalog for capability comparison and future operator-controlled integration work. **It cannot execute in this image.**

Its autonomous agent loop cannot be constrained to read-only behavior by prompt text alone: page-level prompt injection could induce clicking, typing, submission, uploads, or other external mutation. `execute_plan()` therefore blocks every plan containing `browser-use` before adapter construction, even when the request is nominally read-only and credentials are present.

For current work, replan only to an exact allowlisted local Playwright fixture or bounded raw HTTP with a public IPv4-literal target and redirects. Public Playwright navigation and hosted alternatives are non-executable. If neither lane satisfies the task, stop and report the blocker.

Enabling Browser Use requires an independently enforced read-only action interceptor or a separately reviewed operator-controlled production integration, updated locks, a rebuilt image, and a new release.

Reference docs: https://docs.browser-use.com/cloud/guides/mcp-server
