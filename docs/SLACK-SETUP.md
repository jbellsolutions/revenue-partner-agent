# Slack Setup: Screen by Screen

This is the exact Slack path for the recommended VPS installation. It uses
Socket Mode, so the VPS does not need a public webhook or Slack-facing port.

## Before the installer starts

The owner needs:

- permission to install an app in the intended Slack workspace;
- a model account selected during Hermes setup;
- their Slack Member ID;
- one or more channels where the app may be invited.

The included [`slack-manifest.json`](../slack-manifest.json) was generated from
Hermes Agent 0.20.6 with Agent view. `deploy/setup.sh` generates another copy
from the exact installed image at `/srv/revenue-partner/data/slack-manifest.json`.
Use that generated copy when available.

## 1. Create the app from the manifest

1. Open [Slack App Settings](https://api.slack.com/apps).
2. Select **Create New App**.
3. Select **From an app manifest**.
4. Pick the workspace.
5. Choose the **JSON** tab.
6. Paste the complete contents of `slack-manifest.json`.
7. Select **Next**, review the requested access, then select **Create**.

The manifest enables Slack's current Agent messaging experience. Slack warns
that an app cannot switch back from Agent view after applying it. This is
expected for a newly created Revenue Partner app.

The manifest also enables Socket Mode, messages, files, reactions, Agent DMs,
and every current Hermes slash command. No public request URL is required.

## 2. Install the app and copy the bot token

1. In the app sidebar, open **Install App**.
2. Select **Install to Workspace**.
3. Review the workspace and permissions.
4. Select **Allow**.
5. Copy the **Bot User OAuth Token** beginning `xoxb-`.
6. Paste it only into the installer's hidden `xoxb-` prompt.

Do not paste the token into ordinary Slack messages, documentation, or GitHub.

## 3. Create the Socket Mode token

1. Open **Settings → Basic Information**.
2. Scroll to **App-Level Tokens**.
3. Select **Generate Token and Scopes**.
4. Name it `revenue-partner-socket`.
5. Add the `connections:write` scope.
6. Select **Generate**.
7. Copy the token beginning `xapp-`.
8. Paste it only into the installer's hidden `xapp-` prompt.

The `xoxb-` token acts as the bot. The `xapp-` token opens the private Socket
Mode connection. Both are required.

## 4. Allow the owner

Hermes denies Slack users by default. To copy the owner's Member ID:

1. Open the owner's profile in Slack.
2. Select **More**.
3. Select **Copy member ID**.
4. Paste the `U…` or `W…` value into the installer.

For more than one owner, enter comma-separated Member IDs. Do not use a display
name or email address.

## 5. Choose a home channel

The home channel receives scheduled reports and proactive messages. To use one:

1. Open the intended channel.
2. Open **Channel details → About**.
3. Copy the Channel ID at the bottom.
4. Paste the `C…` or `G…` value into the optional installer prompt.
5. In that channel, run `/invite @Revenue Partner`.

Skip the home-channel prompt if scheduled Slack delivery is not needed yet.

## 6. Test the actual Slack behavior

### Direct message

Open **Apps → Revenue Partner** and send:

```text
hello
```

The app answers every authorized DM without an `@mention`.

### Channel

Invite the app, then send:

```text
@Revenue Partner give me a one-sentence status
```

In channels, an `@mention` starts the conversation. Revenue Partner replies in
a thread. Once it is active in that thread, follow-up replies do not need
another mention.

### Commands and buttons

Type `/` and confirm commands such as `/help`, `/new`, `/reload-skills`, `/btw`,
`/stop`, `/approve`, and `/deny` appear. Slack caps an app at 50 native slash
commands, so use `!skills` or `/hermes skills` for the skill manager and
`!revenue-partner <request>` for the Revenue Partner skill. When it asks a bounded
multiple-choice question, Slack shows one-tap buttons plus an **Other…** choice.

## 7. Keep Slack current

After a repository runtime update, regenerate the manifest:

```bash
cd revenue-partner-agent
./deploy/update.sh
```

Then open **Slack App Settings → Revenue Partner → Features → App Manifest →
Edit**, paste `/srv/revenue-partner/data/slack-manifest.json`, and save. Reinstall
the app if Slack requests it. This refreshes scopes, events, Agent view metadata,
and newly added slash commands.

## Troubleshooting

| Symptom | Fix |
|---|---|
| App is offline | Run `docker logs --tail 100 revenue-partner` and verify both tokens were entered |
| DM is ignored | Confirm the sender's exact Member ID is in `SLACK_ALLOWED_USERS` |
| Channel mention is ignored | Run `/invite @Revenue Partner` in that channel |
| Commands are missing | Regenerate and reapply the manifest, then reinstall when prompted |
| Replies appear outside the expected place | Begin with an `@mention` in the intended channel and continue in its thread |
| A token was exposed | Revoke it immediately in Slack, generate a replacement, and rerun setup |
