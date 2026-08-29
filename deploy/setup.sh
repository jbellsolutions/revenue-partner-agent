#!/usr/bin/env bash
# Beginner-first VPS + Slack setup for the current Revenue Partner runtime.
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HERMES_IMAGE="nousresearch/hermes-agent:v2026.8.27@sha256:e0df6adebddf29b91112aefc999d4aaf6846c9eb544faca5672a16a13590ff79"
BASE_DIR="${REVENUE_PARTNER_BASE_DIR:-/srv/revenue-partner}"
DATA_DIR="$BASE_DIR/data"

say() { printf '\n%s\n' "$*"; }
fail() { printf '\nSetup stopped: %s\n' "$*" >&2; exit 1; }
secret() { local value; read -r -s -p "$1: " value; printf '\n' >&2; printf '%s' "$value"; }

upsert_env() {
  local key=$1 value=$2 temp
  [[ "$key" =~ ^[A-Z][A-Z0-9_]*$ ]] || fail "invalid setting name"
  [[ "$value" != *$'\n'* ]] || fail "a setting cannot contain a new line"
  temp="$(mktemp "$DATA_DIR/.env.tmp.XXXXXX")"
  [ ! -f "$DATA_DIR/.env" ] || awk -v key="$key" 'index($0, key "=") != 1 { print }' "$DATA_DIR/.env" > "$temp"
  printf '%s=%s\n' "$key" "$value" >> "$temp"
  chmod 600 "$temp"
  mv "$temp" "$DATA_DIR/.env"
}

[ "$(uname -s)" = "Linux" ] || fail "run this on the Ubuntu VPS, not on your personal computer"
if [ "$(id -u)" -eq 0 ]; then
  ELEVATE=()
else
  command -v sudo >/dev/null 2>&1 || fail "this server account needs sudo access"
  ELEVATE=(sudo)
fi

say "Revenue Partner — current VPS and Slack setup"
echo "This keeps the working Revenue Partner persona and skills, while running"
echo "the current reviewed Hermes Agent 0.20.6 container."

if ! command -v git >/dev/null 2>&1 || ! command -v python3 >/dev/null 2>&1; then
  "${ELEVATE[@]}" apt-get update -qq
  "${ELEVATE[@]}" apt-get install -y -qq git python3 ca-certificates curl
fi
if ! command -v docker >/dev/null 2>&1; then
  install_script="$(mktemp)"
  curl -fsSL https://get.docker.com -o "$install_script"
  "${ELEVATE[@]}" sh "$install_script"
fi
"${ELEVATE[@]}" systemctl enable --now docker >/dev/null 2>&1 || true
if ! docker compose version >/dev/null 2>&1; then
  "${ELEVATE[@]}" apt-get update -qq
  "${ELEVATE[@]}" apt-get install -y -qq docker-compose-plugin
fi
if docker info >/dev/null 2>&1; then
  DOCKER=(docker)
elif "${ELEVATE[@]}" docker info >/dev/null 2>&1; then
  DOCKER=("${ELEVATE[@]}" docker)
else
  fail "Docker is installed but not running"
fi
"${DOCKER[@]}" compose version >/dev/null 2>&1 || fail "the Docker Compose plugin is required"

"${ELEVATE[@]}" mkdir -p "$DATA_DIR"
"${ELEVATE[@]}" chown -R "$(id -u):$(id -g)" "$BASE_DIR"

if [ ! -f "$DATA_DIR/config.yaml" ]; then
  say "Step 1 of 6 — Connect the model"
  echo "The official Hermes setup screen opens now. Choose the model account"
  echo "you want to use. Messaging can be skipped there; Slack is the next step."
  "${DOCKER[@]}" run -it --rm \
    -v "$DATA_DIR:/opt/data" \
    "$HERMES_IMAGE" setup
else
  say "Step 1 of 6 — The model is already configured"
fi

say "Step 2 of 6 — Install the Revenue Partner skill set"
python3 "$REPO_DIR/deploy/sync_seed.py" "$REPO_DIR" "$DATA_DIR"
chmod 600 "$DATA_DIR/.env" 2>/dev/null || true

say "Step 3 of 6 — Create the complete Slack manifest"
"${DOCKER[@]}" run --rm \
  -v "$DATA_DIR:/opt/data" \
  "$HERMES_IMAGE" slack manifest \
    --agent-view \
    --name "Revenue Partner" \
    --description "Your private Revenue Partner GTM operator" \
    --write /opt/data/slack-manifest.json >/dev/null
echo "Manifest created at: $DATA_DIR/slack-manifest.json"
echo "Open https://api.slack.com/apps and choose:"
echo "  Create New App → From an app manifest → your workspace"
echo "Paste that JSON, review it, and click Create. Agent view is the current"
echo "Slack experience and cannot be changed back after Slack applies it."

say "Step 4 of 6 — Install the Slack app and collect three values"
echo "In Slack App Settings, choose Install App → Install to Workspace."
echo "Copy the Bot User OAuth Token beginning xoxb-."
slack_bot_value="$(secret "Paste the xoxb- Bot Token")"
[[ "$slack_bot_value" == xoxb-* ]] || fail "the Bot Token must begin with xoxb-"
echo "Open Basic Information → App-Level Tokens → Generate Token and Scopes."
echo "Name it revenue-partner-socket and grant connections:write."
slack_app_value="$(secret "Paste the xapp- App Token")"
[[ "$slack_app_value" == xapp-* ]] || fail "the App Token must begin with xapp-"
echo "In Slack, open your profile → More → Copy member ID."
read -r -p "Paste the allowed Slack member ID (starts U or W): " SLACK_ALLOWED_USERS
[[ "$SLACK_ALLOWED_USERS" =~ ^[UW][A-Z0-9]+(,[UW][A-Z0-9]+)*$ ]] || \
  fail "enter one Member ID, or comma-separated Member IDs"
read -r -p "Optional home channel ID for scheduled reports (press Enter to skip): " SLACK_HOME_CHANNEL
if [ -n "$SLACK_HOME_CHANNEL" ]; then
  [[ "$SLACK_HOME_CHANNEL" =~ ^[CGD][A-Z0-9]+$ ]] || fail "that does not look like a Slack channel ID"
fi
upsert_env SLACK_BOT_TOKEN "$slack_bot_value"
upsert_env SLACK_APP_TOKEN "$slack_app_value"
upsert_env SLACK_ALLOWED_USERS "$SLACK_ALLOWED_USERS"
upsert_env SLACK_HOME_CHANNEL "$SLACK_HOME_CHANNEL"
unset slack_bot_value slack_app_value

say "Step 5 of 6 — Start Revenue Partner"
cp "$REPO_DIR/deploy/compose.yml" "$BASE_DIR/compose.yml"
cat > "$BASE_DIR/compose.env" <<EOF
REVENUE_PARTNER_DATA_DIR=$DATA_DIR
HERMES_PORT=8642
HERMES_MEM_LIMIT=5g
HERMES_CPUS=3.0
EOF
chmod 600 "$BASE_DIR/compose.env"
(
  cd "$BASE_DIR"
  "${DOCKER[@]}" compose --env-file compose.env pull
  "${DOCKER[@]}" compose --env-file compose.env up -d
)
sleep 5
state="$("${DOCKER[@]}" inspect revenue-partner --format '{{.State.Status}}' 2>/dev/null || true)"
[ "$state" = "running" ] || {
  "${DOCKER[@]}" logs --tail 100 revenue-partner || true
  fail "the container did not stay running"
}

say "Step 6 of 6 — Prove Slack works"
echo "In Slack, open Revenue Partner under Apps and send: hello"
echo "In a channel, first run /invite @Revenue Partner, then start with:"
echo "  @Revenue Partner give me a one-sentence status"
echo "After the first mention, continue inside its thread without mentioning it."
echo
echo "Useful checks:"
echo "  docker logs --tail 100 revenue-partner"
echo "  docker exec revenue-partner hermes skills list"
echo "  docker exec revenue-partner hermes skills audit"
echo
echo "Private dashboard tunnel:"
echo "  ssh -L 8642:127.0.0.1:8642 <your-server>"
echo "Then open http://localhost:8642"
echo
echo "Setup is complete after the Slack DM receives a real answer."
