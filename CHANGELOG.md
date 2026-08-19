# Changelog

All notable changes to Revenue Partner Agent are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and releases use semantic versioning.

## [1.0.0] - Release candidate

### Added

- Source-grounded Revenue Partner persona and GTM operating skill.
- Money Desk model spanning owned-demand recovery and new-demand acquisition.
- Fit gate, phased operating sequence, campaign contract, source ledger, and acceptance tests.
- Operator-controlled company/offer/ICP/claims/permissions/campaign/reporting knowledge vault.
- Vendored, pinned Super Browser runtime with eight provider adapters and deterministic runtime lock.
- Hash-locked Hermes/QR/uv runtime and checksum-verified Node, 1Password CLI, and Obsidian artifacts; model-callable filesystem MCP is absent and named upstream connector plugin/CLI/catalog surfaces are removed by an exact-version build pruner.
- Revenue Partner-specific fail-closed campaign/ad approval hardening.
- AgentPhone future-integration source with immutable main/job/tunnel/API/send hard stops and retained exact-origin/audience defenses.
- Allowlisted, non-evaluating, atomic mode-`0600` environment bridge.
- Fail-closed local/remote template validation, immutable publication, image-build, and launch workflow.
- Unit, behavior, payload, schema, credential, shell, and execution-sentinel tests.
- Public architecture, operator, deployment, security, source-grounding, verification, contributing, and vulnerability-reporting documentation.
- GitHub Actions validation workflow.

### Security

- Any campaign/ad request routed through Super Browser is approval-gated unless it matches a strict whole-request read-only or bounded public-search form.
- Internal campaign drafts remain local Hermes text work and cannot authorize provider execution.
- Mixed read/write, draft/write, local-output/write, and pronoun-follow-up smuggling variants fail closed.
- Agent-facing Super Browser self-approval is removed; human approval is confined to separate operator channels with Hermes host-manual confirmation enabled.
- Generic outbound verbs fail closed; AgentPhone rejects arbitrary remote attachment URLs and oversized webhook bodies before buffering or signature work.
- Caller-supplied proxy URLs fail closed, and autonomous Browser Use/Orgo plans stop before adapter construction even when nominally read-only.
- Credentials remain external to the repository and template image.

### Verification

- Revenue Partner tests: 70/70 passed on the current release candidate.
- Latitude telemetry tests: 7/7 passed, including canonical-origin, no-proxy/no-redirect, and repeat-registration regressions.
- The canonical verifier always creates a fresh hash-locked environment, ignores caller-forged bootstrap markers, parses every exact Git-index YAML document, scans exact Git-index blobs for credentials, and executes every shipped test lane plus the exact packaged Super Browser verifier from the locked environment.
- Hosted provider council entries are comparison-only, expose no credential/setup path, and cannot enter the execution sequence.
- Approval records remain audit evidence only across campaign contracts, runtime retry state, handoff output, and legacy/tampered run states.
- AgentPhone ordering/media/webhook-boundary tests: 17/17 passed.

- Checksum-bound local Orgo JSON Schema validation passed.
- Authenticated Orgo schema validation is not evidenced for this exact tree: a historical pre-release candidate received HTTP 200, but authenticated validation must be repeated with exact-tree-bound attestations before release.
- GitHub release notes, rather than this changelog, bind the exact release commit and final independent-review verdict so superseded candidate bytes cannot inherit clearance.

### Known deployment status

- GitHub publication and CI are tracked separately from Orgo deployment.
- Orgo template publication was not completed because the authenticated workspace tier lacked template-publishing entitlement.
- No Orgo publication ID, image-ready event, computer ID, live endpoint, or live smoke result is claimed for 1.0.0 yet.