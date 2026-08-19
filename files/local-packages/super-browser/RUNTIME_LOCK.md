# Super Browser Runtime Lock

## Provenance

`requirements-runtime.lock` was generated outside the runtime image from pristine Super Browser source at commit `552822fd86a74d574ff9c0d87db6e6b82f929d96`, selecting the MCP and Playwright runtime requirements before downstream curation. The upstream project-build metadata and resolver lock are intentionally not shipped in this image; these bytes are not regenerated or resolved at image-build time.

Verified direct versions:

- `mcp==2.0.0`
- `playwright==1.62.0`
- Playwright Chromium revision: `1234`
- Playwright Chromium headless-shell revision: `1234`

## Consumed build path

`requirements-runtime.lock` pins the complete transitive runtime graph with hashes. The image builder:

1. installs that exact lock with uv's hash-enforcing requirements mode;
2. registers the staged pure-Python Super Browser source with `files/scripts/super-browser/install_local_super_browser.sh`;
3. creates and verifies `.pth`, `.dist-info`, and the `super-browser` console entry point using only the locked venv's Python standard library;
4. downloads Chromium revision 1234 through the already locked Playwright 1.62.0 package;
5. imports all eight adapter definitions and MCP resources; and
6. launches a real headless Chromium process.

Local source registration does not invoke project-package installation, setuptools, wheel, PEP 517, a resolver, build isolation, or network access.

## Maintenance

To change the dependency graph, regenerate and review the lock from a separate pristine checkout of the pinned upstream source, verify Linux x86_64/Python 3.11 hashes, update the pinned browser evidence, bump the template version, and rebuild the image. Do not resolve dependencies or replace package source inside a running Revenue Partner image.
