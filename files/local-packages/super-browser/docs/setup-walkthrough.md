# Local Super Browser setup walkthrough

Super Browser is already baked into the Revenue Partner image from committed locks. Do **not** clone another checkout, run a floating installer, or install packages into the running image.

## 1. Confirm the baked runtime

```bash
super-browser doctor
```

The report distinguishes the constrained local lanes from planning-only provider records. Credentials cannot promote a planning-only provider to execution.

## 2. Confirm the enforceable lanes

Only exact allowlisted local Playwright fixtures and bounded direct public-IP-literal raw HTTP reads can execute. Public Playwright navigation is non-executable. All hosted providers remain planning-only regardless of credentials.

## 3. Verify local read-only behavior

```bash
super-browser live-test --provider fixtures
```

Use fixture verification as local evidence only. It does not prove cloud-provider readiness or a live deployment.

## 4. Use the five-round council

Before browser work, classify the task, identify eligible data lanes, compare at least three viable options when available, check readiness/cost/evidence/safety, then select an execution and fallback plan with a verification contract.

## 5. Respect the hard stop

Approval-required requests remain `awaiting_approval`. The packaged MCP, CLI, Slack, handoff, runtime, agent, and adapter surfaces cannot approve or execute them. Activation requires separately reviewed operator-controlled infrastructure, updated locks where needed, a rebuilt image, and a new release.

There is no hosted-provider signup, credential setup, runtime installation, or proxy activation path in this image.
