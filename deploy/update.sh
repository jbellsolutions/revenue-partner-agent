#!/usr/bin/env bash
# Safe container, skill, and Slack-manifest refresh for an installed VPS copy.
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BASE_DIR="${REVENUE_PARTNER_BASE_DIR:-/srv/revenue-partner}"
DATA_DIR="$BASE_DIR/data"
HERMES_IMAGE="nousresearch/hermes-agent:v2026.8.27@sha256:e0df6adebddf29b91112aefc999d4aaf6846c9eb544faca5672a16a13590ff79"

[ -f "$BASE_DIR/compose.yml" ] || { echo "Run deploy/setup.sh first." >&2; exit 1; }
if docker info >/dev/null 2>&1; then DOCKER=(docker); else DOCKER=(sudo docker); fi

git -C "$REPO_DIR" pull --ff-only
python3 "$REPO_DIR/deploy/sync_seed.py" "$REPO_DIR" "$DATA_DIR"
cp "$REPO_DIR/deploy/compose.yml" "$BASE_DIR/compose.yml"
(
  cd "$BASE_DIR"
  "${DOCKER[@]}" compose --env-file compose.env pull
  "${DOCKER[@]}" compose --env-file compose.env up -d
)
"${DOCKER[@]}" exec revenue-partner hermes skills check || true
"${DOCKER[@]}" exec revenue-partner hermes skills audit || true
"${DOCKER[@]}" run --rm -v "$DATA_DIR:/opt/data" "$HERMES_IMAGE" \
  slack manifest --agent-view --name "Revenue Partner" \
  --description "Your private Revenue Partner GTM operator" \
  --write /opt/data/slack-manifest.json >/dev/null

echo "Runtime refreshed from the repository's reviewed image pin."
echo "Owner-edited skills were preserved. Review available skill updates before running:"
echo "  docker exec revenue-partner hermes skills update"
echo "Refresh Slack commands with: $DATA_DIR/slack-manifest.json"
