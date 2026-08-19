---
name: decodo-http-specialist
description: "Use the direct raw HTTP lane for public IP-literal endpoints when browser rendering is unnecessary."
---

# Direct Raw HTTP Specialist

## Use For

- Public IP-literal HTTP(S) API endpoints.
- Bulk reads where browser rendering is unnecessary.
- Deterministic direct transport without a proxy.

## Do Not Use For

- Hostname starting URLs or hostname redirects.
- Any proxy, geo-targeting, or IP-rotation requirement.
- Sites requiring browser rendering or authenticated sessions.
- Loopback, private-network, link-local, reserved, multicast, or unspecified addresses outside an exact operator test fixture.

## Environment

No provider credential or proxy environment variable is consumed. Proxy construction is disabled in this immutable image.

## Verification

Record status code, final URL, target-scope evidence, response size, redirect count, and artifact hash. Every start and redirect must remain a public IP literal. Treat target-scope or redirect blocks as non-resumable safety stops.
