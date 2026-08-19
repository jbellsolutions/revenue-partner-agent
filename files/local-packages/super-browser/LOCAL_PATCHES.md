# Local Security Patches

The vendor baseline is pinned by `UPSTREAM_COMMIT`. The Revenue Partner template applies this narrowly scoped, reviewable delta:

## Baked-runtime documentation curation

- Files: `README.md`, `docs/index.html`, `docs/agent-profiles.md`, `src/super_browser/mcp_server.py`, `src/super_browser/cli.py`, and `UPSTREAM_SOURCE.md`; obsolete daily-digest script/guide removed.
- Reason: upstream marketing and onboarding described absent chat/HTTP scripts, a hosted multi-model service, a scheduled Slack digest, and mutable clone/install flows that do not exist in this image.
- Change: MCP-readable and packaged public guidance now documents only the baked local CLI/MCP runtime, runtime-derived provider readiness, read-only execution, and the production hard stop. CI scans Markdown, code, YAML/JSON, shell, and HTML resources for the removed capability markers.
- Safety effect: agents cannot infer or invoke nonexistent hosted/service paths from shipped documentation.

## Ad/campaign approval classification

- File: `src/super_browser/policy.py`
- Reason: the upstream keyword-only classifier recognized `launch ad` but missed common article-bearing variants such as `launch an ad campaign` and `create an ad`.
- Change: ad/campaign requests fail closed to the approval flow unless the whole request matches a narrow read-only or bounded public-search form. Clause-level action/object patterns additionally make common activation language explicit; grammar between the action and object is not restricted to a modifier whitelist.
- Draft boundary: internal campaign drafting remains autonomous in Hermes as local text work, but a campaign-draft request sent to Super Browser is approval-gated. No draft-language exception can authorize provider execution.
- Exception integrity: campaign-related local-output requests cannot bypass the protected gate, and campaign-related local-delivery or public-search requests must match a strict whole-request grammar. The protected object family includes `ad`, `advert`, `advertisement`, `advertising`, and `campaign` singular/plural forms.
- Safety effect: matching requests are external writes and create runs in `awaiting_approval`; they remain non-executable in this image. Enabling production requires a separately reviewed operator-controlled integration and rebuilt release.
- Regression coverage: `tests/test_revenue_partner_template.py::test_super_browser_ad_campaign_phrases_require_approval`.

## Generic outbound fail-closed classification

- File: `src/super_browser/policy.py`
- Reason: ordinary production verbs such as `dispatch`, `deliver`, `forward`, and `transmit`, plus verb-light communication-surface requests such as `Email Alice the note through Gmail` or `Use the contact form to reach out`, could otherwise fall through to read-only classification.
- Change: outbound execution verbs are explicit external-write signals; non-read-only references to email, e-mail, mail, Gmail, or communication forms are treated as external-write objects regardless of the chosen verb; and Unicode/hyphen variants of final-action icons are normalized before classification.
- Safety effect: ordinary email/message/form delivery language and UI aliases such as `paper-plane`, `paper plane`, `airplane button`, and `send icon` persist `awaiting_approval` and cannot reach provider execution. Public communication-reference exceptions are whole-request anchored, so a safe prefix such as `What is Gmail?` cannot hide a follow-up send or UI action.
- Regression coverage: `tests/test_revenue_partner_template.py::test_super_browser_ad_campaign_phrases_require_approval` uses a provider-execution sentinel for these variants.

## Production-surface fail-closed classification

- File: `src/super_browser/policy.py`
- Reason: operational requests such as `Push the dashboard to production` and `Ship the UI to prod` did not use the narrower upstream deployment grammar.
- Change: `push`, `ship`, `release`, `promote`, `roll out`, `deploy`, and `publish` remain explicit external-write signals when the same clause includes a production environment and a UI/dashboard/site/app target. More importantly, every generic interactive `mutating` plan—including typing, filling, or clicking—is approval-required, so synonyms and icon labels are not the authorization boundary.
- Safety effect: production-surface and all other mutating browser/provider requests persist `awaiting_approval` and cannot reach provider execution in this image. Only policy-classified read work can dispatch.
- Regression coverage: the provider-execution sentinel in `tests/test_revenue_partner_template.py::test_super_browser_ad_campaign_phrases_require_approval` covers explicit deployment variants plus indirect controls such as `make live`, `go live`, `rocket icon`, and `final action button`.

## Autonomous-provider and proxy hard stops

- Files: `src/super_browser/adapters.py`, `src/super_browser/proxy.py`, provider skills/references, and the parent template regression suite.
- Reason: textual read-only prompts cannot constrain autonomous Browser Use or Orgo agents after page-level prompt injection, and caller-supplied proxy URLs could route nominally public reads through internal endpoints.
- Change: any plan containing `browser-use` or `orgo` is blocked before adapter construction; only technically read-only extraction adapters may execute. Proxy inputs and environment activation are absent from MCP/CLI and rejected at router, helper, and concrete network-construction boundaries.
- Safety effect: autonomous interaction and every proxy route fail before provider or network construction.

## Curated runtime resources

- Files: package-data inventory plus `docs/`, `examples/`, `configs/`, `references/`, MCP/CLI schemas, setup/readiness surfaces, and provider specialist guidance.
- Reason: the pinned upstream included historical hosted-service research, Slack setup, write-oriented workflows, arbitrary-proxy help, and executable Browser Use/Orgo examples that contradict this image.
- Change: obsolete research/service/write examples are excluded and removed; MCP and CLI proxy inputs are absent; doctor reports all six hosted providers as `non_executable_in_image`; old live evidence cannot certify them for reads; setup does not recommend credentials or signup paths.
- Safety effect: every shipped agent-readable resource and discovery surface matches the technically read-only execution boundary.

## Approval time integrity

- Files: `build_template.py`, `src/super_browser/runtime.py`
- Reason: an unauthenticated HTTP `Date` header must never control the root VM clock or approval freshness.
- Change: resume no longer executes `date -s`; platform time synchronization remains authoritative, and future-dated approval decisions fail closed alongside expired decisions.
- Regression coverage: `tests/test_revenue_partner_template.py::test_production_approval_requires_host_confirmation_and_is_not_agent_self_service` rejects HTTP clock setting and requires the negative-age guard.

## No local production approval surface

- Files: `src/super_browser/runtime.py`, `src/super_browser/cli.py`, former upstream `src/super_browser/agent.py` (removed below), `src/super_browser/mcp_server.py`, `src/super_browser/handoff.py`, `SKILL.md`, `docs/setup-walkthrough.md`, and `references/security-and-approval-policy.md`.
- Reason: an agent-facing approval tool allowed the same principal that proposed a production action to self-attest its approval actor and reason.
- Change: approval is absent from MCP, CLI, Slack, handoff, and agent command surfaces. `approve_run()` fails closed, and `_execute_run()` blocks every approval-required plan even if run state is tampered to `approved`.
- Safety effect: the model may plan, inspect, verify, deny, or resume read-only work, but it cannot approve or execute a production action from inside the runtime. Enabling production requires a separately reviewed operator-controlled integration and new release.

## Agent-facing dependency remediation

- Files: `src/super_browser/setup_walkthrough.py`, former upstream `src/super_browser/agent.py` (removed below), and `src/super_browser/adapters.py`.
- Reason: the upstream generic package exposed floating package-install commands in setup/error text; an autonomous agent could follow those strings and mutate the verified runtime outside committed locks.
- Behavior: missing optional dependencies now direct operators to update committed locks and rebuild the image; no floating install command is emitted.

## Immutable MCP/CLI surface

- Files: `src/super_browser/mcp_server.py`, `src/super_browser/cli.py`, `src/super_browser/setup_helpers.py`, `src/super_browser/bundle.py`, `PACKAGE_METADATA.toml`, and package documentation.
- Reason: upstream install/config-write, persistent-profile mutation, and Slack-daemon surfaces could mutate the reviewed runtime or advertise an unavailable hosted ingress.
- Change: those tools and commands are absent from MCP discovery and CLI parsing; direct MCP calls return unknown-tool errors; setup helpers retain only read-only bundle-root discovery; the unused Slack daemon module was removed. Profile list/get remain read-only and do not create state directories. Unused upstream `pyproject.toml`/`uv.lock` build surfaces were replaced by inert `PACKAGE_METADATA.toml`; the image registers source through the audited standard-library installer.

All downstream changes preserve the pinned source identity while explicitly documenting every routing, policy, resource, and runtime difference in this ledger.