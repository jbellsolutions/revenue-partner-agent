#!/bin/bash
# ==========================================================================
# Revenue Partner — AgentPhone webhook-bridge wrapper (supervised entrypoint)
# ==========================================================================
# This release packages the reviewed bridge source for a future integration,
# but credentials, restarts, approval records, and audience allowlists cannot
# activate its network or messaging paths in this immutable image.
printf '%s\n' 'AgentPhone bridge is non-executable in this image; a separately reviewed integration, rebuilt image, and new release are required.' >&2
exec sleep infinity
