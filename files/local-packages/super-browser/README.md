# Super Browser — Revenue Partner local runtime

Revenue Partner ships a **baked, local, unlaunched** Super Browser runtime assembled from committed dependency locks. It is the browser/research orchestration front door for the template. This release does not provide a hosted bridge, public endpoint, autonomous service, scheduled digest, or local production-approval mechanism.

## Runtime contract

- Use the configured `super-browser` MCP server or `/usr/local/bin/super-browser` after an Orgo image is built.
- The runtime exposes eight provider adapters and its committed MCP resources.
- Runtime readiness reports distinguish the two enforceable local lanes from planning-only hosted-provider records. Credentials cannot promote hosted providers to execution.
- Policy-classified `read` work may execute only through a technically read-only extraction provider.
- Browser Use and Orgo are planning/reference adapters in this release; their autonomous interaction paths are blocked before construction because prompt text is not an action-level write barrier.
- Task input, environment variables, direct helpers, MCP, and CLI cannot activate a proxy. Proxy execution is unavailable.
- `mutating`, credential-bearing, external-write, and destructive work remains `awaiting_approval` and cannot execute in this image.
- Credentials establish connectivity only; they never grant operational approval.

## Verify the baked runtime

```bash
super-browser doctor
super-browser providers
super-browser live-test --provider fixtures
```

Fixture verification is local evidence only. It does not prove cloud-provider readiness, authenticated access, a deployed agent, or a live Orgo computer.

## Plan and run read-only work

```bash
super-browser plan --goal "Compare the public pricing pages for these three vendors"
super-browser run --goal "Summarize the public documentation at this URL" --url https://example.com/docs
super-browser runs
super-browser verify <RUN_ID>
```

Before execution, use the five-round council:

1. classify the task;
2. identify eligible providers and data lanes;
3. compare at least three viable options when available;
4. check readiness, cost, evidence, and safety;
5. select an execution/fallback plan and verification contract.

Google result discovery should use a configured Fast Search API when available, followed by target-site extraction through the selected crawl/data lane.

## Production hard stop

Approval-required work cannot be activated through MCP, CLI, Slack, handoff data, run records, caller parameters, generic browser controls, or low-level adapters. The runtime and adapter recompute policy immediately before dispatch. Autonomous Browser Use/Orgo execution is also disabled for nominally read-only plans until an independently enforced action interceptor exists.

Enabling production execution requires a separately reviewed operator-controlled integration, updated locks/configuration, a rebuilt image, and a new immutable release. Do not mutate a running image or install floating dependencies.

## Local files

- `ENGINE.md` — runtime behavior and readiness contract
- `SKILL.md` — agent routing and safety instructions
- `references/provider-matrix.md` — provider planning records and execution boundaries
- `references/security-and-approval-policy.md` — approval boundary
- `docs/setup-walkthrough.md` — baked-runtime and enforceable-lane verification
- `LOCAL_PATCHES.md` — Revenue Partner downstream hardening record
- `UPSTREAM_SOURCE.md` — pinned upstream provenance

## Status

The source and local schema are verified as part of the Revenue Partner release process. Orgo schema acceptance is not publication, image readiness, launch, provider readiness, or live smoke-test evidence.
