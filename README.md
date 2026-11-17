# Network Sync

A personal CRM in Notion that keeps itself up to date, run by Claude.

Every day it looks at whom you talked to (on Signal, WhatsApp, email,
LinkedIn, calendar meetings and Notion meeting notes) and then:

- **logs each exchange** as one short row per person, channel and day,
  summarised in Claude's own words: no message text is copied
- **keeps a card per person** current: last contact, what you last talked
  about, open promises either way, what to bring up next time, and whether
  you're waiting on them
- **sends you a digest**: at most five people to reach out to today, why now,
  and a one-line opener, plus new people to review and follow-ups coming due

You decide how often you want to hear from each person (every 2 weeks,
monthly, quarterly, yearly, or paused). The digest surfaces whoever is due.

All settings live on one Notion page in plain words: channels, lookback,
group-chat rule, who gets added, an ignore list, digest tone. Change the page
and the next run follows it.

## Examples

Once installed, ask Claude:

- *"Set up a network tracker for me."*
- *"Sync my network."*
- *"Who should I reach out to this week?"*
- *"I had lunch with Anna today, she's moving to Berlin. I promised to intro her to Ben."*
- *"Run the network sync every evening at 6:40."*

## What you need

- **Notion**, connected to Claude (required)
- Any of these, all optional:
  - **Gmail** and **Google Calendar** connectors (other mail and calendar
    connectors work too)
  - **Signal** and **WhatsApp** on a Mac, through the companion plugins
    [Chat Export for Signal](https://github.com/phillippmueller/chat-export-for-signal)
    and [Chat Export for WhatsApp](https://github.com/phillippmueller/chat-export-for-whatsapp).
    Claude needs a shell on that Mac: Claude Code running there, or the Claude
    desktop app with the computer linked.
  - **LinkedIn**: message notification emails in Gmail (daily, partial), and
    LinkedIn's own data download dropped into `~/network-tracker/linkedin-inbox`
    whenever you request one (full)

Channels that aren't available are skipped, and the digest says so.

## Install

**Claude app**: open **Customize → Plugins**, click **Add → Add marketplace →
Add from a repository**, enter `phillippmueller/network-sync`, and install
**Network Sync**. Install the two chat-export plugins the same way if you want
Signal and WhatsApp.

**Claude Code**:

```
/plugin marketplace add phillippmueller/network-sync
/plugin install network-sync@network-sync
```

Then say *"Set up a network tracker"*. Claude asks a few questions (your
name and addresses, time zone, channels, context tags, digest tone), creates
the Notion page and databases, runs a first sync over the last 60 days, and
offers to schedule a daily run.

## What it will and won't do

- **Read-only** on every channel: it never sends, replies, drafts, labels,
  archives or deletes anything, and never touches LinkedIn directly.
- **Summaries only** in Notion and in the digest. Phone numbers only go into
  the Phone field.
- **Never deletes** Notion rows or files, and never overwrites the fields you
  own (name, cadence, context, notes).
- **Never gets around a privacy prompt.** The first chat export may make macOS
  ask you to click Allow (or grant Full Disk Access); that click is yours.
- Signal Desktop has to be closed while its database is read. During setup
  you choose whether unattended runs may quit and reopen it, or skip Signal
  while it's open.
- Raw chat exports stay in `~/network-tracker/exports` on your Mac. Delete them
  whenever you like; the tracker doesn't need them after a run.

## Files

```
plugins/network-sync/skills/network-sync/
  SKILL.md                 modes, requirements, rules
  reference/setup.md       settings page and database schemas
  reference/sync.md        the daily run, step by step
  reference/schedule.md    running it every day
  scripts/summarize_exports.py   turns chat exports into compact per-chat summaries
tests/                     python3 -m unittest discover tests
```

## License

MIT. See [LICENSE](LICENSE) and [PRIVACY.md](PRIVACY.md).
