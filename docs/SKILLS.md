# Skills: Included, Installed, and Updated

Hermes skills are reusable operating procedures loaded only when needed. They
are different from memory: skills explain how to do repeatable work, while
memory stores durable facts about the owner and business.

Official reference: [Hermes Skills Hub](https://hermes-agent.nousresearch.com/docs/skills).

## Included with Revenue Partner

The repository seeds:

- `revenue-partner` — the Money Desk, fit gate, operating sequence, evidence,
  campaign, approval, and reporting system;
- its campaign contract, source ledger, operating-system, and acceptance-test
  references;
- the complete Revenue Partner knowledge-vault structure;
- Super Browser planning, routing, verification, provider, scraping, agent, and
  publishing-safety specialist skills already shipped in this repository.

The current Hermes image also seeds its bundled skill catalog. That includes
document, research, development, browser, creative, planning, and agent
orchestration procedures. Bundled skills are updated by a reviewed image change
without silently replacing locally edited copies.

## See and use skills in Slack

```text
!skills
!skills search research
!revenue-partner assess this offer for fit
/reload-skills
```

Slack reserves native slash commands in its picker and caps each app at 50.
Hermes therefore accepts `!skill-name` as the reliable typed form in Slack;
`/hermes skills ...` remains a fallback. Skills also load naturally when a
request matches their description.

## Browse and install optional skills

From the server:

```bash
docker exec -it revenue-partner hermes skills list
docker exec -it revenue-partner hermes skills browse --source official
docker exec -it revenue-partner hermes skills search calendar
docker exec -it revenue-partner hermes skills inspect official/security/1password
docker exec -it revenue-partner hermes skills install official/security/1password
```

Inspect before installing. Official optional skills are the safest default.
Community skills receive security scanning and should not be forced through a
warning unless an operator has reviewed the complete skill and its support
files.

## Skill write approval

Hermes can create or improve a skill after learning a repeatable workflow. Turn
on review when the owner wants every agent-authored change staged first:

```text
!skills approval on
!skills pending
!skills diff <id>
!skills approve <id>
!skills reject <id>
```

This works in Slack as well as the CLI. Pending changes survive a restart.

## Check and update safely

```bash
docker exec revenue-partner hermes skills check
docker exec revenue-partner hermes skills audit
docker exec -it revenue-partner hermes skills update
```

`skills update` replaces only upstream-installed skills with available updates.
Locally edited skills are skipped unless `--force` is used. Do not force-update
the Revenue Partner skill or an owner-customized skill without reviewing the
diff and keeping a backup.

`deploy/setup.sh` and `deploy/update.sh` use a seed manifest to update unchanged
repository skills while preserving owner-edited deployed files.
