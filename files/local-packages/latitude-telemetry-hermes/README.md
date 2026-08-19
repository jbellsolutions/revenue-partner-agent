# latitude-telemetry-hermes Revenue Partner package

Staged local fork of `latitude-telemetry-hermes` with redacted summary capture and per-call reasoning-effort observability for Hermes Agent.

Content capture is disabled by default even when ordinary Latitude credentials are configured. An operator must explicitly set `LATITUDE_HERMES_ALLOW_CONTENT=true` to include recursively redacted prompt, response, or tool content. `LATITUDE_HERMES_NO_CONTENT=true` always forces summary-only capture. System prompts and raw tool I/O are never exported by default.

Each LLM span records the live Hermes-configured effort and the effective provider request value separately. This makes provider clamps and models that use native/provider-default reasoning visible instead of mislabeling them as the global configuration value.

The image builder registers this staged fork directly in `/usr/local/lib/hermes-agent/venv` using atomically written `.pth` and `.dist-info` metadata. Registration uses only the locked venv's Python standard library: no pip, setuptools, wheel, PEP 517 backend, resolver, build isolation, or network access.

The registration installer also applies the reviewed Hermes core hook and verifies the package version, import path, entry point, and plugin loading:

```bash
bash /root/.hermes/scripts/latitude/install_local_telemetry_patch.sh
python3 /root/.hermes/scripts/latitude/dewey_observability_validate.py
```
