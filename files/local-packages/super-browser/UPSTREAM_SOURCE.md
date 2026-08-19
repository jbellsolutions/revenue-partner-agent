# Vendored Super Browser Runtime

- Source: https://github.com/jbellsolutions/super-browser
- Ref: `origin/master`
- Commit: `552822fd86a74d574ff9c0d87db6e6b82f929d96`
- Vendored: 2026-08-18
- Included: `.codex-plugin/plugin.json`, `.mcp.json`, `pyproject.toml`, `uv.lock`, `requirements-runtime.lock`, `RUNTIME_LOCK.md`, `src/`, `mcp/`, `references/`, `skills/`, `configs/`, `docs/`, `scripts/super-browser`, `scripts/verify-super-browser`, `README.md`, `SKILL.md`
- Excluded: local state, virtualenv, other non-runtime scripts, tests, caches, generated artifacts, and uncommitted working-tree changes.

The target template installs this bundle into the Hermes virtual environment with MCP and Playwright extras, installs Chromium, imports all eight provider adapters, imports the MCP server, and launches a real headless browser during image build.

## Local security delta

`src/super_browser/policy.py` contains one reviewed local hardening delta over the pinned commit: natural-language ad/campaign activation requests are classified as external writes and enter the durable approval flow, while explicit internal drafts remain non-production work. See `LOCAL_PATCHES.md` and the parent template regression suite.
