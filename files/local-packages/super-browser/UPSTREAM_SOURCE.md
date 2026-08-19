# Vendored Super Browser Runtime

- Source: https://github.com/jbellsolutions/super-browser
- Ref: `origin/master`
- Commit: `552822fd86a74d574ff9c0d87db6e6b82f929d96`
- Vendored: 2026-08-18
- Included: `.codex-plugin/plugin.json`, `.mcp.json`, `ENGINE.md`, inert downstream `PACKAGE_METADATA.toml`, `requirements-runtime.lock`, `RUNTIME_LOCK.md`, `src/`, `mcp/`, `references/`, `skills/`, `configs/`, curated local-runtime `docs/`, `scripts/super-browser`, `scripts/verify-super-browser`, `README.md`, `SKILL.md`
- Excluded downstream: the upstream daily Slack digest and its guide because it depended on absent service scripts and no schedule or hosted service exists in this image.
- Excluded: upstream package-build metadata and unused resolver lock, stale hosted-service env template, local state, virtualenv, other non-runtime scripts, tests, caches, generated artifacts, and uncommitted working-tree changes.

The target template installs the hash-locked runtime graph, registers this staged source directly in the locked Hermes environment, installs Chromium, imports all eight provider adapters, imports the MCP server, and launches a real headless browser during image build.

## Local security delta

The vendored runtime has a reviewed downstream security delta over the pinned commit. Protected production work remains non-executable; autonomous Browser Use and Orgo adapters are blocked before construction; caller-supplied proxy URLs are rejected; and strict read-only/public-reference forms remain available only through technically read-only extraction lanes. Internal campaign drafting remains local Hermes text work and does not authorize browser-provider execution. See `LOCAL_PATCHES.md` and the parent template regression suite.
