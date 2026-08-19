from __future__ import annotations

# This immutable image exposes no provider signup workflow. All hosted providers
# are planning/provenance records, and executable proxy routing is disabled.
# Adding a credential-acquisition path requires separate operator review and a
# rebuilt release with enforceable connection boundaries.
PROVIDER_SIGNUP: dict[str, dict[str, object]] = {}
