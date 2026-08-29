#!/usr/bin/env bash
# Guided business-tool connections for the current Revenue Partner VPS path.
set -euo pipefail

BASE_DIR="${REVENUE_PARTNER_BASE_DIR:-/srv/revenue-partner}"
DATA_DIR="$BASE_DIR/data"

say() { printf '\n%s\n' "$*"; }
fail() { printf '\nTool setup stopped: %s\n' "$*" >&2; exit 1; }
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

if docker info >/dev/null 2>&1; then
  DOCKER=(docker)
elif command -v sudo >/dev/null 2>&1 && sudo docker info >/dev/null 2>&1; then
  DOCKER=(sudo docker)
else
  fail "Docker is not running"
fi
[ -f "$DATA_DIR/config.yaml" ] || fail "run deploy/setup.sh first"
state="$("${DOCKER[@]}" inspect revenue-partner --format '{{.State.Status}}' 2>/dev/null || true)"
[ "$state" = "running" ] || fail "the revenue-partner container is not running"

hermes_set() {
  "${DOCKER[@]}" exec revenue-partner hermes config set "$1" "$2" >/dev/null
}

restart_agent() {
  "${DOCKER[@]}" restart revenue-partner >/dev/null
  echo "Revenue Partner restarted with the new connection."
}

say "Revenue Partner — connect Calendar, inboxes, files, CRM, and proposals"
echo "This helper never prints a private key. Every connected service is marked"
echo "untrusted, so Hermes asks for approval before tools marked as write-capable run."

while true; do
  cat <<'MENU'

  1. Connect Calendar, Gmail, Outlook, Drive, and business apps (Composio)
  2. Connect PandaDoc proposals
  3. Show connection status
  4. Finish
MENU
  read -r -p "Choose a number: " choice
  case "$choice" in
    1)
      cat <<'TEXT'

Open https://app.composio.dev in your browser.
Choose For You → Connect my agent, then copy the consumer key beginning ck_.
Do not use a Platform project key beginning ak_.
TEXT
      composio_value="$(secret "Paste the ck_ consumer key")"
      [[ "$composio_value" == ck_* ]] || fail "the Composio consumer key must begin with ck_"
      upsert_env COMPOSIO_API_KEY "$composio_value"
      unset composio_value
      hermes_set mcp_servers.composio.url https://connect.composio.dev/mcp
      hermes_set mcp_servers.composio.headers.x-consumer-api-key '${COMPOSIO_API_KEY}'
      hermes_set mcp_servers.composio.trust untrusted
      hermes_set mcp_servers.composio.timeout 180
      hermes_set mcp_servers.composio.connect_timeout 60
      hermes_set mcp_servers.composio.enabled true
      restart_agent
      cat <<'TEXT'
In Composio, use Connect Apps to approve only the accounts Revenue Partner needs.
Then send this safe first test in Slack:

  Read my next three calendar events. Do not create, change, or cancel anything.

For inbox access, test with:

  List three recent message subject lines. Do not send, move, or change anything.
TEXT
      ;;
    2)
      echo
      echo "Choose the region shown in the address where you sign in to PandaDoc:"
      echo "  1. app.pandadoc.com (Global)"
      echo "  2. app.pandadoc.eu (Europe)"
      read -r -p "Choose 1 or 2: " region
      case "$region" in
        1) pandadoc_url=https://mcp.pandadoc.com/v1/mcp ;;
        2) pandadoc_url=https://mcp.pandadoc.eu/v1/mcp ;;
        *) echo "Choose 1 or 2."; continue ;;
      esac
      hermes_set mcp_servers.pandadoc.url "$pandadoc_url"
      hermes_set mcp_servers.pandadoc.auth oauth
      hermes_set mcp_servers.pandadoc.trust untrusted
      hermes_set mcp_servers.pandadoc.timeout 180
      hermes_set mcp_servers.pandadoc.connect_timeout 60
      hermes_set mcp_servers.pandadoc.enabled true
      cat <<'TEXT'

Hermes now prints a secure PandaDoc authorization link. Open it and approve.
If the browser ends on a localhost connection error, that is expected: copy the
complete URL from the address bar and paste it back at the terminal prompt.
TEXT
      if "${DOCKER[@]}" exec -it revenue-partner hermes mcp login pandadoc; then
        restart_agent
        cat <<'TEXT'
Test in Slack with:

  List my three most recent PandaDoc documents. Do not create, send, or change anything.

After that read-only test passes, create a private unsent proposal draft. Sending
or requesting a signature still requires approval for the exact document and recipients.
TEXT
      else
        echo "PandaDoc did not authenticate. Nothing was sent or changed. Choose option 2 to retry."
      fi
      ;;
    3)
      "${DOCKER[@]}" exec revenue-partner hermes mcp list
      ;;
    4)
      echo "Business-tool setup is finished."
      break
      ;;
    *) echo "Choose a number from 1 through 4." ;;
  esac
done
