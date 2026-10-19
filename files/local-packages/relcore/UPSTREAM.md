# relcore (vendored)

Source: github.com/jbellsolutions/true-revenue-partner, branch `network-map`, commit `c2e58cd55e51588949a2a0e79b5bec7727b7ad79`.
Copied as is: `relcore/` (stdlib Python, no dependencies), `policies/permissions.json`,
`policies/mcp-tool-allowlist.json`, `data/revenue-partnerships.json` (the 339 partnership types).

Do not edit here. Change relcore upstream, run its tests (`python3 -m unittest discover -s tests`),
then re-copy and update the commit above.

On the box this lands at `/root/.hermes/local-packages/relcore` and runs as the `relcore` MCP server
(stdio, `python3 -m relcore.mcp_server --mode plugin`) with `PYTHONPATH` and `TRP_REPO` pointing here.
Cards render into the Obsidian vault at `/root/Documents/HermesVault/Relationships`.
