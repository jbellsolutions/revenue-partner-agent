# Routing playbook — locked Revenue Partner image

## 1. Classify before routing

Derive and persist:

- intent/risk: `read`, `mutating`, `external_write`, `credential`, `destructive`, or fail-closed unknown;
- target scope from the actual URL: `public_web`, `loopback`, `private_network`, `link_local`, `local_file`, or `none`;
- authentication/profile requirement;
- raw HTTP versus browser rendering requirement;
- whether the request requires a proxy (which makes it non-executable in this image);
- approval and production-control state.

Never trust a caller-declared target scope when it disagrees with URL-derived scope.

## 2. Approval stop

Stop before provider construction for mutations, external writes, production/live controls, authenticated profiles, credentials, sensitive targets, unknown intent, or ambiguous intent. Resume, plan fields, tool arguments, environment credentials, and stored run records cannot self-attest approval.

## 3. Executable lanes

### Local Playwright

Use only for a public, read-classified, unauthenticated target when all conditions hold:

1. no proxy resolves for the task;
2. the initial hostname resolves exclusively to public addresses;
3. at least one validated public IPv4 address exists;
4. Chromium launches with the initial hostname mapped to one validated address;
5. a request guard is installed before navigation;
6. every network request remains on the initial hostname;
7. later DNS evidence never contains loopback, private, link-local, reserved, multicast, or unspecified addresses.

Cross-host redirects and subresources are aborted. If pinning or the request guard cannot be guaranteed, stop.

### Raw HTTP / `decodo-http`

Use only for a concrete public IP-literal HTTP(S) URL without a proxy. Every redirect must also be a public IP literal and must remain outside sensitive/reserved ranges. Hostname targets, hostname redirects, and proxy transport are non-executable because connected-peer identity cannot be pinned.

### Exact local fixtures

Loopback/local-file execution exists only when the process sets `SUPER_BROWSER_TEST_MODE=1` and places the exact URL in `SUPER_BROWSER_TEST_TARGET_ALLOWLIST_JSON`. This is a fixture mechanism, not production approval, and adapters recheck it directly.

## 4. Planning-only provider records

Airtop, Browser Use, Browserbase, Hyperbrowser, Orgo, and Steel may appear in capability, cost, or provenance comparisons. Do not construct, call, connect, navigate, submit URLs, run provider live tests, or treat credentials as readiness. Their hosted/autonomous network and action boundaries are not enforceable by this image.

## 5. Failure behavior

Treat these as non-resumable safety stops:

- target-scope mismatch;
- approval-required task;
- target address not pinned;
- proxy-side DNS required;
- hosted peer-address enforcement unavailable;
- cross-host browser request;
- raw HTTP hostname or hostname redirect;
- sensitive/reserved address evidence;
- provider or adapter non-executable in image.

Replan only after changing to an enforceable lane or after a separately reviewed image release adds a technical enforcement boundary.

## 6. Verification contract

A complete read must record the selected lane, derived target scope, pinning/guard checks, provider attempts, artifact hashes, and any blocked requests. Planning output alone is not execution evidence. A schema validation is not deployment, and historical evidence never transfers release clearance to another source tree.
