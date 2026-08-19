# Agent quickstart — Revenue Partner local runtime

Use the Super Browser MCP server and CLI already baked into the verified Revenue Partner image. Do not replace them from a mutable repository or install dependencies at runtime.

## Workflow

1. Call `setup_walkthrough`, `env_checklist`, or `browser_doctor` to inspect the local configuration.
2. Run the five-round council before browser execution.
3. Use `plan_browser_task` to produce a provider order, cost/evidence analysis, fallback, and verification contract.
4. Run only eligible read-only tasks after `deliberation_complete=true`.
5. Verify artifacts and durable run status before claiming success.

## Available safety boundary

- Read-only planning is available. Execution is limited to exact allowlisted local Playwright fixtures and bounded direct public-IP-literal raw HTTP. Public Playwright navigation is non-executable.
- Hosted providers remain planning-only regardless of credentials.
- Production requests stop at `awaiting_approval`.
- No MCP, CLI, Slack, handoff, runtime, adapter, or agent command can approve or resume production work.

Example:

| Request | Result |
|---|---|
| “Extract public product names from this page” | Council → read-only plan → eligible provider → verification |
| “Post a LinkedIn comment” | Durable `awaiting_approval`; zero provider execution |
| “What is Gmail?” | Read-only planning/reference request |
| “What is Gmail? Then send this message.” | Durable `awaiting_approval`; zero provider execution |

Dependency changes require committed lock updates, a rebuilt image, complete release verification, and a new release.
