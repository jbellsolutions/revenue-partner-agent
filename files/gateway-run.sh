#!/bin/bash
# ==========================================================================
# Revenue Partner — Hermes gateway wrapper
# ==========================================================================
# This repairs the source VM's broken supervised unit. On that VM the gateway
# ran as user=orgo while inheriting HOME=/root (mode
# 0700), so its config-wait gate could never pass and the supervised gateway
# never actually started. Here we run as root with HOME=/root and load only
# allowlisted environment values without evaluating dotenv content as shell, so
# the gateway is genuinely supervised, reboot-safe, and sees only allowlisted values.
set +e
export HOME=/root
export HERMES_HOME=/root/.hermes
export PATH=/usr/local/bin:/root/.local/bin:/root/.hermes/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH

# Wait for the baked config AND a completed Nous sign-in before starting. This
# keeps the supervised gateway dormant (not crash-looping) until the user runs
# the first-boot onboarding / `hermes auth`, then it comes up cleanly — an
# improvement over the source VM, where the gateway spun with no model creds.
until [ -f "$HERMES_HOME/config.yaml" ] && [ -s "$HERMES_HOME/auth.json" ]; do sleep 5; done

# Lifetime flock: an Orgo boot race can start TWO supervisords, each spawning
# this service — twin gateways then SIGTERM each other via --replace every ~2s,
# forever (field-tested; build-recipe §9). Blocking flock parks the loser.
# The safe bridge atomically refreshes ~/.hermes/.env, exports only allowlisted
# parsed values into this process, and execs without shell evaluation.
mkdir -p /var/lib/orgo
# `flock` without a timeout parks forever behind a STALE holder, and supervisord
# reports the parked process as RUNNING -- so a dead gateway looks healthy and
# every restart is a silent no-op. Field-observed: an orphaned gateway held this
# lock for two days while config changes appeared to deploy and never took
# effect. Bound the wait so a stuck lock surfaces as a non-zero exit that
# supervisord's backoff and status actually reflect. A genuine double-start
# still loses the race and exits, which is the intended behaviour.
exec /usr/local/bin/revenue-partner-env-bridge --exec \
  flock -w 30 -E 75 /var/lib/orgo/hermes-gateway.lock \
  hermes gateway run --replace --accept-hooks
