# Contributing

## Development requirements

- Python 3.11
- `uv`
- Git
- Bash

Do not put credentials, customer data, generated launch files, resolved template output, or raw research captures in Git.

## Workflow

1. Create a focused branch.
2. Update tests before or with behavior changes.
3. Keep customer facts unset in reusable template files.
4. Run the local matrix.
5. Document security/source/deployment effects.
6. Obtain independent review for release-sensitive changes.
7. Publish a new immutable template version; never overwrite a reviewed remote version.

## Required checks

```bash
REVENUE_PARTNER_VERIFY_PYTHON=/absolute/path/to/trusted/python3.11 bash .github/scripts/verify_release
```

Hosted CI uses the same launcher and supplies its trusted absolute interpreter from the pinned `setup-python` action. Its non-Python launcher exports one exact Git-index tree under a scrubbed isolated interpreter, creates a disposable Python environment, and installs `requirements-ci.lock` under `--require-hashes`. The matrix parses exact-index YAML and skill frontmatter, scans exact-index credentials, validates links/assets, runs the Revenue Partner, Latitude telemetry, packaged Super Browser, and AgentPhone suites, compiles all shipped Python, checks tracked and embedded shell programs, rechecks exact-tree parity, validates against the checksum-bound Orgo schema, assembles the template, and verifies the decoded assembled Super Browser payload.

## Approval-policy changes

Natural-language authorization changes require end-to-end tests, not only regex assertions.

Tests must:

- use `execute=True`;
- replace provider execution with a sentinel;
- assert production variants persist `awaiting_approval`;
- assert zero provider calls;
- probe articles, synonyms, modifiers, plurality, punctuation, word order, pronouns, and mixed intents;
- pair blocked forms with narrow safe reads;
- audit early local-output, local-delivery, public-search, draft, and read-only exceptions.

Prefer architectural separation over trying to enumerate every possible production verb. Campaign drafting is local Hermes work; any campaign request routed to Super Browser is approval-gated except strict read-only/public-search forms.

## Source-grounding changes

When adding a claim:

1. cite the direct source;
2. classify it as direct, self-reported, target, inference, unknown, or verified result;
3. include evidence limitations;
4. do not invent missing pricing, proof, consent, attribution, legal, contract, or performance facts;
5. update the source ledger and behavior tests.

## Vendored Super Browser changes

- Preserve the recorded upstream base revision.
- Document every downstream change in `LOCAL_PATCHES.md`.
- Do not claim locally modified files are byte-identical to upstream.
- Keep runtime locks and required bundle paths complete.
- Do not commit caches, virtual environments, local state, or unrelated upstream changes.

## Pull requests

A PR should contain:

- problem and scope;
- files/components changed;
- security and approval impact;
- source-grounding impact;
- tests and exact counts;
- schema/build evidence;
- deployment impact and required credentials/tier;
- remaining limitations.

Do not claim a live deployment based only on local tests or a successful push.