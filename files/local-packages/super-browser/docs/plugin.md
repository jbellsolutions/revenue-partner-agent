# Super Browser integration in Revenue Partner

Revenue Partner vendors Super Browser as a pinned local package. The built image exposes its stdio MCP server at `/usr/local/bin/super-browser-server` and its CLI at `/usr/local/bin/super-browser`.

This repository does **not** claim a hosted Super Browser executor, public bridge, running browser session, or deployed Orgo computer. Hosted providers remain planning-only regardless of credentials.

## Safety boundary

- Execution is limited to exact allowlisted local Playwright fixtures or bounded direct public-IP-literal raw HTTP when policy permits. Public Playwright navigation is non-executable.
- The five-round council is required before execution.
- Approval-required production work remains stopped.
- Local CLI, Slack, MCP, handoff, agent, runtime, and adapter surfaces cannot approve or execute production work.

See `../SKILL.md`, `../references/provider-matrix.md`, and `../references/security-and-approval-policy.md` for the local contract.
