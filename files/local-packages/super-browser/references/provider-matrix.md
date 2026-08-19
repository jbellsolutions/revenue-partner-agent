# Provider matrix — locked Revenue Partner image

Provider records support planning, comparison, and provenance. A record does not imply execution readiness.

| Provider | Record role | Execution in this image | Enforced reason |
|---|---|---|---|
| `playwright` | Local deterministic browser | Conditional read-only | Public hostname must resolve exclusively to public addresses, have a public IPv4 pin, run without a proxy, and remain same-host. Exact local fixtures require process-level test mode and an exact URL allowlist. |
| `decodo-http` | Direct raw HTTP lane | Conditional read-only | Public target and every redirect must be a public IP literal; proxy transport is disabled. |
| `airtop` | Hosted-browser planning record | No | Target DNS, redirects, and connected peer cannot be enforced from this image. |
| `browser-use` | Autonomous-browser planning record | No | Read-only behavior cannot be guaranteed before provider construction. |
| `browserbase` | Hosted-browser planning record | No | No enforceable target peer/redirect boundary and no executable adapter contract. |
| `hyperbrowser` | Hosted-browser planning record | No | Target DNS, redirects, and connected peer cannot be enforced from this image. |
| `orgo` | Computer-use planning record | No | Autonomous desktop interaction is not technically constrained to read-only behavior. |
| `steel` | Hosted-CDP planning record | No | Target DNS, redirects, and connected peer cannot be enforced from this image. |

## Authorization boundary

- `loopback`, `private_network`, `link_local`, and `local_file` require approval and remain non-executable by default.
- The only test exception requires `SUPER_BROWSER_TEST_MODE=1` and an exact URL in `SUPER_BROWSER_TEST_TARGET_ALLOWLIST_JSON`; it applies only to loopback/local-file fixture URLs and is rechecked at the adapter boundary.
- Authenticated profiles, external writes, production controls, mutations, unknown intent, and ambiguous intent remain approval-blocked before provider construction.
- Caller-supplied and operator/environment proxy routes are non-executable in this image.
- A credential, live-test record, profile, resume request, or request field never converts a non-executable provider into an executable one.

## Readiness semantics

`doctor` reports Airtop, Browser Use, Browserbase, Hyperbrowser, Orgo, and Steel as `non_executable_in_image` regardless of credentials or historical evidence. Playwright readiness covers exact allowlisted local fixtures only; raw HTTP readiness covers bounded public-IPv4-literal reads only. Readiness is not production approval.
