# Super Browser Runtime Lock

Generated from the pinned Super Browser source at `552822fd86a74d574ff9c0d87db6e6b82f929d96` with:

```bash
uv lock --project files/local-packages/super-browser --upgrade-package mcp --upgrade-package playwright
uv export --project files/local-packages/super-browser --locked --extra mcp --extra playwright --no-dev --no-emit-project --format requirements-txt --output-file files/local-packages/super-browser/requirements-runtime.lock
```

Verified direct versions:

- `mcp==2.0.0`
- `playwright==1.62.0`
- Playwright Chromium revision: `1234`
- Playwright Chromium headless-shell revision: `1234`

`requirements-runtime.lock` pins the full transitive graph with hashes. The image builder installs that lock with `--require-hashes`, then installs the local Super Browser project editable with `--no-deps`, downloads Chromium revision 1234 through Playwright 1.62.0, imports all eight adapters/MCP resources, and launches a real headless browser.
