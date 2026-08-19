#!/bin/bash
# ==========================================================================
# Revenue Partner — first-boot onboarding (runs on the desktop, once)
# ==========================================================================
# Walks a new user through the steps that need a human:
#   1. Nous model auth   (device-code — required for the agent to think)
#   2. Telegram bot      (scan a QR — the signature onboarding)
#   3. 1Password vault   (optional narrow model/Telegram/telemetry map)
#   4. immutable connector status and future-release requirements
#
# Launched by an XFCE autostart entry inside a terminal. Idempotent: each
# step is skipped once satisfied, so re-running only does what's left.
set +e
export HOME=/root
export HERMES_HOME=/root/.hermes
export DISPLAY="${DISPLAY:-:99}"
export PATH=/usr/local/bin:/root/.local/bin:/root/.hermes/bin:/usr/bin:/bin:$PATH

VENV_PY=/usr/local/lib/hermes-agent/venv/bin/python
ENV_FILE="$HERMES_HOME/.env"
OP_ENV="$HERMES_HOME/.op.env"
STAMP=/var/lib/orgo/revenue-partner-onboarded
mkdir -p /var/lib/orgo "$HERMES_HOME"

hr() { printf '\n\033[1;36m%s\033[0m\n' "────────────────────────────────────────────────────────"; }
say() { printf '\033[1;32m%s\033[0m\n' "$*"; }

clear 2>/dev/null
say "  Welcome to Revenue Partner — Hermes agent setup"
hr

# --- 1. Nous model auth ----------------------------------------------------
if [ ! -s "$HERMES_HOME/auth.json" ]; then
  say "Step 1/4 — Connect your Nous account (model: gpt-5.5)"
  echo "A device-code sign-in will open. Follow the URL + code it prints."
  echo "(Prefer ChatGPT? Later run: hermes auth add openai-codex, then set"
  echo " model.default: gpt-5.6-sol / provider: openai-codex in config.yaml.)"
  echo
  hermes auth add nous --type oauth
  echo
  if [ -s "$HERMES_HOME/auth.json" ]; then
    # 1-token sanity call: a zero-credit Nous account 404s on every model
    # call while everything looks green — fail loudly here, not silently.
    echo "Verifying the model can think (1-token test call)…"
    if hermes -z "Reply with exactly: ok" >/tmp/revenue-partner-modelcheck 2>&1 \
       && grep -qi "ok" /tmp/revenue-partner-modelcheck; then
      say "Model check passed ✓"
    else
      printf '\033[1;31m%s\033[0m\n' "Model test call FAILED — most often a Nous account with zero credits."
      echo "Add credits at portal.nousresearch.com, or connect ChatGPT instead:"
      echo "  hermes auth add openai-codex"
    fi
  fi
else
  say "Step 1/4 — Model account already connected ✓"
fi

# --- 2. Telegram bot via QR ------------------------------------------------
if ! grep -q '^TELEGRAM_BOT_TOKEN=..' "$ENV_FILE" 2>/dev/null; then
  hr
  say "Step 2/4 — Create your Telegram bot (scan the QR)"
  echo "A QR code opens in Chrome. Scan it with your phone, then tap"
  echo "'Create Bot' in Telegram. Your bot + allowlist are set automatically."
  echo
  "$VENV_PY" /usr/local/bin/revenue-partner-telegram-pair.py
  if grep -q '^TELEGRAM_BOT_TOKEN=..' "$ENV_FILE" 2>/dev/null; then
    say "Telegram connected — restarting the gateway to enable it…"
    supervisorctl restart hermes-gateway 2>/dev/null || \
      { [ -f "$HERMES_HOME/gateway.pid" ] && kill -USR1 "$(cat "$HERMES_HOME/gateway.pid")" 2>/dev/null; }
  fi
else
  say "Step 2/4 — Telegram bot already connected ✓"
fi

# --- 3. 1Password (optional, but it IS the stack's secret plane) -----------
hr
if [ -s "$OP_ENV" ]; then
  say "Step 3/4 — 1Password already connected ✓"
else
  say "Step 3/4 — Connect 1Password (optional, recommended)"
  cat <<'OPINTRO'
  One service-account token resolves only the allowlisted model, Telegram,
  and optional telemetry values in config.yaml. It does not expose or activate
  disabled connector credentials.
  Setup (once, on 1password.com): create vault "Hermes" -> a Secure Note
  named "Hermes Agent Secrets" -> add only the allowlisted fields you use ->
  create a service account that can read vault "Hermes".
OPINTRO
  printf '  Paste your service-account token (ops_…) or press Enter to skip: '
  read -r OPTOK
  if [ -n "$OPTOK" ]; then
    umask 077
    printf 'OP_SERVICE_ACCOUNT_TOKEN=%s\n' "$OPTOK" > "$OP_ENV"
    unset OPTOK
    python3 /usr/local/bin/revenue-partner-op-enable || true
    echo "Checking…"
    hermes secrets onepassword status || true
    supervisorctl restart hermes-gateway 2>/dev/null || true
    say "1Password wired — keys resolve at every hermes start."
  else
    echo "Skipped. Re-run this setup any time, or: echo 'OP_SERVICE_ACCOUNT_TOKEN=ops_…' > ~/.hermes/.op.env"
  fi
fi

# --- 4. Optional integrations -----------------------------------------------
hr
say "Step 4/4 — The rest of your stack"
cat <<'NEXT'
  The named production connectors below are non-executable in this immutable
  image. Do not add provider keys or run connector login commands
  expecting AgentMail, AgentCard, Composio, AgentPhone, Orgo, Linear, X, or
  external memory to activate. Credentials and restarts cannot enable them.

  Enabling any such integration requires operator-controlled source and
  configuration changes, complete verification, a fresh exact-tree review,
  a rebuilt image, and a new release. Latitude tracing is the only optional
  credentialed observability path described here; it captures no content by
  default and must be configured and verified separately by the operator.
NEXT
hr

# Stamp only when the two required steps are done, so we stop auto-launching.
if [ -s "$HERMES_HOME/auth.json" ] && grep -q '^TELEGRAM_BOT_TOKEN=..' "$ENV_FILE" 2>/dev/null; then
  date -Iseconds > "$STAMP"
  say "Setup complete. This window won't reappear. Talk to your agent on Telegram!"
else
  say "Setup paused — re-open 'Revenue Partner Setup' from the desktop to finish."
fi
echo
read -r -p "Press Enter to close…" _
