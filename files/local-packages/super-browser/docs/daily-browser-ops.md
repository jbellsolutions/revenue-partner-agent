# Daily Browser-Agent Digest

Every morning at **6:00 AM ET**, Super Browser posts a Slack message with **5–10 specific, high-leverage
browser-agent moves** you could run that day — grounded in what your business is actually doing.

Script: [`scripts/daily_browser_ops.py`](../scripts/daily_browser_ops.py)

## What it does

1. **Reads context from `the-operator`** (read-only) — its skills + strategies + mission (`SOUL.md`). This is the
   "what the business runs" signal. `the-operator` is **never modified** — only read.
2. **Reads your recent Slack activity** via the Super Browser bot token — the "what's happening today" signal.
3. **Asks the OSS brain** (GLM-5.2) to propose 5–10 concrete browser-agent tasks, each with a one-line *why now*
   and the exact Super Browser tool to use (`browser_use`, `source_leads`, `run_fleet`, `code_agent`, …).
4. **Posts the digest to Slack** (your DM by default).

## Keeping it separate from `the-operator`

`the-operator` (a different repo + a different machine — its own Orgo box, Obsidian vault `/root/OperatorVault`)
is integrated **read-only**. Only a context snapshot (`skills/`, `strategies/`, `config/SOUL.md` — **secrets
excluded**) is copied to `/opt/the-operator` on the Super Browser box. Refresh it by re-syncing that snapshot, or
set `OPERATOR_GIT_PULL=1` (needs read git creds on the box for the private repo) to `git pull` it each morning.

## Schedule (systemd, on the box)

- `super-browser-daily-ops.service` — runs the script once (oneshot, as `superbrowser`).
- `super-browser-daily-ops.timer` — `OnCalendar=*-*-* 06:00:00 America/New_York`, `Persistent=true`.

Change the time/zone by editing the timer's `OnCalendar` (any IANA tz works), then
`systemctl daemon-reload && systemctl restart super-browser-daily-ops.timer`.

## Configuration (super-browser `.env`)

| Env | Default | Purpose |
|-----|---------|---------|
| `DAILY_OPS_TARGET` | `U01D077J78S` (Justin's DM) | Slack channel or user id to post the digest to |
| `DAILY_OPS_AUTOJOIN` | _(off)_ | `1` → the bot joins each scanned public channel so it can read live messages (visible join; off by default) |
| `DAILY_OPS_SCAN_LIMIT` | `8` | how many channels to scan for context |
| `OPERATOR_CONTEXT_DIR` | `/opt/the-operator` | read-only `the-operator` snapshot |
| `OPERATOR_GIT_PULL` | _(off)_ | `1` → best-effort `git pull` of the snapshot each run |

> Live-message grounding: until the bot is a member of your channels (invite it, or set `DAILY_OPS_AUTOJOIN=1`),
> the digest is grounded in `the-operator` context only. Add the bot to the channels you want it to read.

## Run it manually

```bash
# preview (generate + print, do NOT post)
sudo -H -u superbrowser /opt/super-browser/.venv/bin/python /opt/super-browser/scripts/daily_browser_ops.py --dry-run

# fire a real one now (posts to Slack)
systemctl start super-browser-daily-ops.service
```
