# Start Here: Revenue Partner in Slack

This is the recommended installation for a new owner. It runs Revenue Partner
continuously on a private Ubuntu VPS and connects it to Slack with the current
Hermes Agent messaging experience.

The package is pinned to Hermes Agent 0.20.6 (`v2026.8.27`) and preserves the
Revenue Partner persona, Money Desk knowledge structure, campaign rules, and
installed specialist skills. The older deterministic Orgo template remains in
the repository for advanced operators and is not changed by this walkthrough.

## The easiest method

Give this message to Claude Code or Codex:

```text
Install my Revenue Partner from this repository:
https://github.com/jbellsolutions/revenue-partner-agent

Read START-HERE.md, docs/SLACK-SETUP.md, and docs/TOOLS.md first. Create or use a private Ubuntu
VPS, connect over SSH, and run deploy/setup.sh. Handle every technical step.
Walk me through Slack one screen at a time and ask for only one account choice
or private value at a time. Never display or commit a token after I provide it.

Use the included Slack Agent-view manifest. Require my Slack Member ID, invite
the app only to approved channels, and prove both a DM and a channel thread
work. Then list the Revenue Partner and bundled Hermes skills, audit installed
skills, connect Calendar/inbox tools and PandaDoc proposals with the included
guided helper, and show me the safe update commands. Finish only when the
container is running and a real Slack message receives a real answer.
```

The setup agent operates the terminal and browser. The owner approves the VPS
charge, account sign-ins, and Slack installation.

## What happens

1. A fresh Ubuntu VPS is created. Four vCPU and 8 GB RAM is comfortable.
2. The repository is cloned to the server.
3. The official Hermes setup connects the chosen model account.
4. Revenue Partner's persona, knowledge templates, GTM skill, references, and
   browser specialist skills are copied into the private data directory.
5. The full current Hermes toolset is enabled for the private CLI and approved
   Slack owners, with owner review for agent-created skill changes.
6. Hermes generates a complete 50-command Slack Agent-view manifest.
7. The Slack app is created from that manifest.
8. The installer privately records the `xoxb-` bot token, `xapp-` Socket Mode
   token, and the owner's Slack Member ID.
9. The guided connector offers Calendar, inbox, files, CRM, and other business
   apps through Composio plus proposals through PandaDoc.
10. The owner proves a DM, channel thread, and the connected tools they selected.

## Manual server command

On a fresh Ubuntu server:

```bash
git clone https://github.com/jbellsolutions/revenue-partner-agent.git
cd revenue-partner-agent
./deploy/setup.sh
```

The installer explains every next screen. For screenshots or webinar delivery,
follow [the complete Slack walkthrough](docs/SLACK-SETUP.md).
The [business-tool walkthrough](docs/TOOLS.md) explains the safe read-only tests.

## Definition of done

- The `revenue-partner` container is running after a restart.
- Only approved Slack members can talk to it.
- A DM receives an answer.
- A channel `@Revenue Partner` mention receives a threaded answer.
- `/help`, `/reload-skills`, `/btw`, `/stop`, and `/approve` appear in Slack.
- `!skills` and `!revenue-partner` work as typed bot commands.
- `hermes skills list` shows the Revenue Partner skill and the bundled catalog.
- `hermes skills audit` completes without an unresolved dangerous finding.
- Calendar/inbox and proposal connections selected during setup pass a real
  read-only test; write-capable actions pause for approval.
- No token or private Slack ID appears in Git.
