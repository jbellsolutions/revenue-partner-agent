---
name: super-browser-orchestrator
description: Orchestrate browser research through Super Browser. Classify risk, compare providers, execute only enforceable local read lanes, and verify results.
---

# Super Browser Orchestrator

## Role

Own the whole job. Convert the user request into a safe, executable browser/computer automation workflow.

## Workflow

0. On first use or when runtime state is unclear, call `super-browser setup` or MCP `setup_walkthrough`, then `env_checklist` / `browser_doctor`. These are baked-runtime reports, not credential or installation workflows.
1. Classify the task as read-only, mutating, external write, credential-bearing, destructive, long-running, authenticated, anti-bot, desktop, or raw HTTP.
2. Call `super-browser plan --goal "<goal>"` or the `plan_browser_task` MCP tool.
3. Read `council_report`; review all `review_loops` (3 direct / 5 council), `deliberation_complete`, `execution_pattern`, and `documented_recommendations` before execution.
4. Report whether an exact allowlisted local Playwright fixture or bounded direct public-IP-literal HTTP can satisfy the request; otherwise stop with the enforceability blocker.
5. Dispatch execution only after `deliberation_complete` is true and the plan is an eligible technically read-only lane.
6. Call `super-browser verify <run-id>` or `verify_browser_run`.
7. Inspect `policy_guard`, `plan_integrity`, `approval_integrity`, and run-report final-provider/attempt consistency before retrying, handing off, or making final claims.
8. Return the final run report with provider, cost notes, artifacts, failures, policy guard, and confidence.

## Defaults

- Prefer the cheapest reliable tool, not the cheapest tool blindly.
- Use local Playwright only for exact allowlisted loopback/local-file fixtures; public navigation is non-executable.
- Use Decodo/raw HTTP only for public IPv4-literal endpoints and redirects, with the fixed 2 MiB ceiling.
- Treat Airtop, Browser Use, Browserbase, Hyperbrowser, Orgo, and Steel as planning/reference records; this image blocks their construction because target peer/action enforcement is unavailable.
- Stop when neither enforceable lane satisfies the task.
- Reject every proxy input. Proxy execution is unavailable in this image.
- Require approval for posting, commenting, messaging, submitting, uploading, payments, trading, banking, payouts, legal, government, health, insurance, identity, account changes, credentials, secrets, infrastructure, billing, workspace/channel/role/moderation changes, or destructive actions.

## References

- Read `../../references/routing-playbook.md` for provider routing.
- Read `../../references/combo-playbook.md` and `../../references/providers/README.md` for strategic provider use.
- Read `../../references/security-and-approval-policy.md` before external writes.
- Treat local fixture checks as local evidence only; hosted-provider readiness requires operator-owned evidence outside this image.
