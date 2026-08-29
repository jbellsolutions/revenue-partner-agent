# Security Policy

## Supported versions

Security fixes are applied to the latest published release and active development branch. Version `1.0.x` is the initial supported line.

## Reporting a vulnerability

Please use GitHub’s **Report a vulnerability** / private security advisory flow for this repository.

Include:

- affected commit/version;
- component and path;
- reproduction steps using local fixtures where possible;
- expected versus observed approval/runtime state;
- whether provider execution, credentials, customer data, consent, suppression, spend, or external writes are affected;
- suggested mitigation if known.

Do not open a public issue containing:

- API keys or tokens;
- customer or prospect data;
- private campaign content;
- exploit-ready approval bypass details against a live account;
- live infrastructure identifiers.

## Security-sensitive areas

Review changes especially carefully in:

- `files/local-packages/super-browser/src/super_browser/policy.py`
- `files/local-packages/super-browser/src/super_browser/runtime.py`
- `files/local-packages/super-browser/src/super_browser/adapters.py`
- `files/safe-env-bridge.py`
- `files/gateway-run.sh`
- `files/agentphone-bridge/`
- `build_template.py`
- `deploy/setup.sh`, `deploy/update.sh`, and `deploy/compose.yml`
- `slack-manifest.json` and Slack user/channel allowlists
- template lifecycle and secret-manager configuration

## Disclosure expectations

The maintainer will acknowledge a complete private report, reproduce it against the exact affected revision, classify severity, and coordinate a fix/release. Public disclosure should wait until a fixed release is available and credential/customer-data exposure has been remediated.

## Security model

See [`docs/SECURITY_MODEL.md`](docs/SECURITY_MODEL.md) for trust boundaries, approvals, secrets, failure behavior, and known enforcement limits.
