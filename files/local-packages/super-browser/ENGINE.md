# Super Browser in Revenue Partner

Revenue Partner includes a **baked local Super Browser runtime** assembled from committed dependency locks. This release does not install from a mutable Git branch, expose a hosted bridge, or provide local production approval.

## Runtime contract

1. Classify the browser/research goal.
2. Run the required five-round council.
3. Report eligible providers, readiness, cost, evidence, safety, fallback, and verification contract.
4. Execute only eligible read-only work through the configured local MCP/CLI.
5. Keep every approval-required request in `awaiting_approval` with zero provider execution.

Dependency or browser changes require updates to committed locks, a rebuilt image, complete verification, and a new release. Do not install packages into a running image.

## Local surfaces

- MCP server: baked `/usr/local/bin/super-browser-server`
- CLI: baked `/usr/local/bin/super-browser`
- State and artifacts: local `.super-browser/` runtime state
- Provider credentials: operator-supplied environment values; connectivity is not approval

Useful checks:

```bash
super-browser doctor
super-browser live-test --provider fixtures
```

No command in this distribution can approve or resume production work. A future production path requires separately reviewed operator-controlled infrastructure and a rebuilt release.

See [provider matrix](references/provider-matrix.md), [routing playbook](references/routing-playbook.md), and [security policy](references/security-and-approval-policy.md).
