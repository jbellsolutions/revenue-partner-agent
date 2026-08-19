# Cost model — planning evidence only

Cost estimates compare provider records; they do not grant execution authority or prove readiness.

## Executable lanes

| Lane | Image execution | Cost treatment |
|---|---|---|
| Local Playwright | Exact allowlisted fixture only | Local compute/runtime cost; public navigation is non-executable. |
| Raw HTTP / `decodo-http` | Bounded public-IPv4-literal reads | Direct transport is local, responses are capped at 2 MiB, and proxy transport is disabled. |

## Planning-only records

Airtop, Browser Use, Browserbase, Hyperbrowser, Orgo, and Steel are non-executable in this image. Their catalog estimates may help an operator compare a future separately reviewed integration, but the router must not convert an estimate, credential, budget, or historical live-test record into execution readiness.

## Rules

1. Security and approval constraints run before cost optimization.
2. Unknown cost is not zero cost.
3. `max_cost_usd` is a planning ceiling, not spending approval.
4. A proxy, hosted session, fleet, computer, or authenticated profile must never be created by this locked image merely to measure cost.
5. If the enforceable local lane cannot satisfy the task, report the blocker; do not silently fall back to a hosted provider.
6. Record actual usage only from completed executable-lane evidence. Do not infer charges from plans or schema validation.
