# Setup

Creates the settings page and the two databases in the user's Notion, then
runs a first sync. Takes a few minutes. Ask the questions below in one
message, offering the defaults so the user can just say "defaults are fine".

## 1. Ask

1. **Your name** as it appears in email and chats, and your own email
   addresses and phone number. These tell the run which side is you, and they
   are never added to People. Don't rely on memory or the account profile for
   the addresses: read them from the connected mail and calendar accounts
   (the sender of the user's sent mail, the attendee marked as self) and ask
   the user to confirm or add others.
2. **Time zone** (default: the one the computer or calendar reports).
3. **Channels** to use: Signal, WhatsApp, Email, Calendar, Notion meeting
   notes, LinkedIn. Check what is connected (connector tools, a shell on a
   Mac) and preselect those.
4. **Contexts**: a few tags for where people come from (default: Work,
   Ex-colleague, Investor, Community, Academia, Friend, Family).
5. **Digest language and tone** (default: match each person's language;
   direct and friendly).
6. **Signal Desktop** (only if Signal is chosen): Signal's database can only
   be read while Signal Desktop is closed. May an unattended run quit it and
   reopen it afterwards? (default: no, skip Signal while it's open).
7. **Where in Notion** to put the page (default: top level of their
   workspace, private).

## 2. Create in Notion

Create a page **"Network tracker"** (icon 🕸️) with the settings template
below, filled in with the answers. Then create the two databases **inside it**
and fill in the Wiring section with their URLs and data source IDs.

### People

| Property | Type | Notes |
| :- | :- | :- |
| Name | title | |
| Email | email | |
| Phone | phone_number | E.164 |
| Signal name | text | Name as shown in Signal |
| WhatsApp name | text | Name as shown in WhatsApp |
| Company | text | |
| Role | text | |
| Context | multi_select | The user's context tags |
| Channels | multi_select | Signal, WhatsApp, Email, Meeting, LinkedIn, Phone, In person |
| Cadence | select | A · 2 weeks, B · monthly, C · quarterly, D · yearly, Paused |
| Last contact | date | |
| Last channel | select | Same options as Channels |
| Last summary | text | What the last exchange was about |
| Next topic | text | What to bring up next time |
| Open loops | text | Promises either side made that are still open |
| Waiting on them | checkbox | My last message is unanswered |
| Follow-up due | date | Explicit date to reach out; wins over cadence if earlier |
| Needs review | checkbox | Added automatically; check name, context and cadence |
| Notes | text | The user's own; never touched by a run |
| Reach out by | formula | See below |
| Interactions | relation | Two-way, to Interactions.Person |

**Reach out by**: Last contact plus the cadence (14, 30, 91 or 365 days),
or Follow-up due if that is earlier; empty for Paused. For example:

```
lets(
  days, ifs(
    prop("Cadence") == "A · 2 weeks", 14,
    prop("Cadence") == "B · monthly", 30,
    prop("Cadence") == "C · quarterly", 91,
    prop("Cadence") == "D · yearly", 365,
    0),
  due, if(days > 0 and !empty(prop("Last contact")),
          dateAdd(prop("Last contact"), days, "days"), prop("Follow-up due")),
  fu, prop("Follow-up due"),
  if(!empty(fu) and fu < due, fu, due)
)
```

If Notion rejects the formula, adjust it until it saves. After the first sync,
check Reach out by on a few rows and fix the formula if the dates are off.

### Interactions

| Property | Type | Notes |
| :- | :- | :- |
| Summary | title | One line in your own words |
| Person | relation | To People (the two-way relation above) |
| Date | date | |
| Channel | select | Same options as People.Channels |
| Direction | select | Both, Me → them, Them → me, Meeting |
| Messages | number | Messages that day |
| Follow-up | text | Action promised by me or them |
| Follow-up due | date | |
| Done | checkbox | |
| Key | text | `<Channel>\|<chat id, email or meeting id>\|<YYYY-MM-DD>`, used to skip duplicates |
| Source | select | Auto, Manual |

Suggested views: People sorted by Reach out by (ascending, hide Paused);
People where Needs review is checked; Interactions by Date, newest first.

## Settings page template

```markdown
Who I've talked to, on which channel, and whom to reach out to next and about
what. Kept up to date by the network-sync skill. Edit anything under
Settings: every run reads this page first and follows it.

## Settings

### Me
- Name: <name>
- My emails: <addresses>
- My phone: <number>
- Time zone: <IANA zone, e.g. Europe/Berlin>
- Working folder on my Mac: ~/network-tracker

### Channels
- Signal: direct chats via Chat Export for Signal on my Mac. Quit and reopen Signal Desktop for the export: <yes/no>
- WhatsApp: direct chats via Chat Export for WhatsApp on my Mac
- Email: threads where I wrote or replied (skip newsletters, notifications, job alerts, automated mail)
- Calendar: meetings with at least one other attendee
- Notion meeting notes: meetings with named participants
- LinkedIn (daily, partial): LinkedIn's message notification emails; who wrote me and a preview, incoming only
- LinkedIn (full, now and then): I download my data from LinkedIn (Settings → Data privacy → Get a copy of your data → Messages) and drop it into ~/network-tracker/linkedin-inbox; the next run imports it once
- Phone calls, in person: I log these myself
(Delete a line to turn that channel off.)

### Lookback
- Daily run: last 3 days (catches up if the computer was off; duplicates are skipped by Key)
- First run (Interactions empty): last 60 days

### Group chats
- Skip group chats. Exception: a group with 3 or fewer people other than me counts as a direct chat with each of them.

### Who gets added to People
- Anyone I had a two-way exchange with (they wrote and I wrote) in a direct chat or an email thread, or met in a meeting.
- New people get Needs review checked and Cadence "C · quarterly". I set the real cadence.
- Never add: businesses, automated senders, delivery or booking services, no-reply addresses, people on the ignore list.

### Ignore list (names, numbers, emails or domains; one per line)
-

### Content policy
- Never copy message text into Notion. Short summaries in my own words: topics, decisions, promises, personal news worth remembering.
- Phone numbers only in the Phone property.

### Digest
- At most 5 people to reach out to, each with the reason and a one-line opener idea.
- Language and tone: <answer>
- Plus: new people needing review, follow-ups due in the next 2 days, unsure matches, skipped channels.

## Wiring (filled in by setup; don't edit)
- People: <database URL>, data source <collection://...>
- Interactions: <database URL>, data source <collection://...>
```

## 3. First run and next steps

1. Run Sync (`reference/sync.md`) right away. It uses the 60-day first-run
   window. Tell the user that macOS may ask them to click Allow for the chat
   exports, so they stay near the computer for this run.
2. Ask the user to go through the rows with Needs review: fix names, set
   Context and Cadence, uncheck Needs review.
3. Offer to schedule it (`reference/schedule.md`).
