# Sync

One run: read recent conversations, update Notion, send the digest. Scheduled
runs are unattended: nobody is watching, so never stop to ask a question.
Anything that needs the user goes into the digest instead.

Below, "the user" is the owner of the tracker, `TZ` is the time zone from the
settings page and `WORK` is the working folder on their Mac (default
`~/network-tracker`).

## Step 0: settings

Fetch the settings page first. It overrides this file where they differ
(except the Rules in SKILL.md). Take the two data source IDs from its Wiring
section and fetch both data sources for the exact schema. If Notion is
unreachable, stop without changes and say so.

**Window**: from N days ago, 00:00 in `TZ`, until now (N from Lookback,
default 3). If Interactions has no rows yet, it is the first run: use the
first-run lookback (default 60 days).

## Step 1: load state

Query all People rows (Name, Email, Phone, Signal name, WhatsApp name,
Channels, Last contact, Cadence, Open loops, Next topic, Needs review) and the
Key of every Interactions row with Date inside the window, so duplicates can
be skipped. SQL works for both (dates are `"date:Date:start"` etc.), but
Notion's SQL can't read formula properties such as Reach out by: see Step 7.

## Step 2: Signal and WhatsApp (needs a shell on the user's Mac)

Use the local shell if this session runs on that Mac, else the tools for the
linked computer (load them with ToolSearch if they are deferred). If no
computer is reachable, skip this step, go on with the cloud sources, and say
so in the digest.

Exports go to `WORK/exports/<app>-<YYYY-MM-DD>` (create the folder if
missing). Always pass `--no-attachments` and `--since <window start date>`.

**a) WhatsApp.** If the `whatsapp-export` skill is available, load it and
follow its Step 0 to get its scripts folder `SCRIPTS` (normally
`~/.chat-export-for-whatsapp`). If the skill isn't listed but
`~/.chat-export-for-whatsapp/whatsapp-export.sh` exists, use that. Otherwise
skip WhatsApp and say in the digest that the plugin isn't installed. Run
`bash SCRIPTS/whatsapp-export.sh doctor`, then
`bash SCRIPTS/whatsapp-export.sh export --since <date> --no-attachments --out WORK/exports/whatsapp-<today>`.
If macOS blocks access, skip WhatsApp and say so.

**b) Signal.** Same pattern with the `signal-export` skill (scripts normally
in `~/.chat-export-for-signal`). Run doctor. Signal's database can't be read
while Signal Desktop is running:

- If the settings page says yes to quitting Signal: if it is running, quit it
  with `osascript -e 'quit app "Signal"'`, wait up to 30 seconds until no
  Signal process is left, run
  `bash SCRIPTS/signal-export.sh export --since <date> --no-attachments --out WORK/exports/signal-<today>`,
  and **always** reopen it afterwards with `open -a Signal`, even if the
  export failed.
- Otherwise, if Signal is running, skip Signal and say so in the digest.

If a keychain prompt blocks the export or it fails, reopen Signal if you
closed it, skip Signal and say so.

**c) Summarise on the Mac.** Copy `scripts/summarize_exports.py` from this
skill to `WORK/` (replace an older copy) and run it there:

```
python3 WORK/summarize_exports.py --since <window start date> --tz <TZ> \
  --small-group <N from the group-chat rule, default 3> \
  WORK/exports/whatsapp-<today> WORK/exports/signal-<today>
```

It prints one JSON object per relevant chat: channel, chat_id, the other
people (name, phone), per-day counts of incoming and outgoing messages, who
wrote last, and the window's message texts (the last 40, each cut to 300
characters). It leaves out group chats bigger than the rule allows, groups
the user didn't write in, Note to Self, chats with only system or call
entries, and attachments. Don't print the export files any other way.

With many chats (a first run, or a busy week), keep the output small: run it
once with `--max-messages 0` for the overview (counts only), then fetch the
texts in batches of about 10 chats with `--only <chat_id>` (repeatable), and
write each batch to Notion (Steps 4 to 6) before reading the next.

**d) LinkedIn data export.** If `WORK/linkedin-inbox` holds a LinkedIn export
(a .zip, or a folder with `messages.csv`) whose name is not listed in
`WORK/linkedin-inbox/imported.txt`, read `messages.csv` for conversations in
the last 60 days, treat them as chats with channel LinkedIn, then append the
file name to `imported.txt`.

## Step 3: cloud sources

Use each one only if it's on the settings page and its connector is there.

**a) Email.** Threads in the window where the user sent a message (Gmail:
`in:sent after:<YYYY/MM/DD>`), plus incoming threads from people already in
People. Skip newsletters, notifications, automated mail, job-application and
recruiting-system mail, and anything from no-reply addresses. Read each
relevant thread, but only the messages inside the window, and ignore the
quoted history below each reply (lines after "On ... wrote:", "Am ...
schrieb", or a forwarded header).

**b) LinkedIn message emails.** Gmail:
`from:(messaging-digest-noreply@linkedin.com OR notifications-noreply@linkedin.com) after:<date>`.
Use only the ones about messages (not invitations, job alerts, posts): sender
name and the preview. Channel LinkedIn, direction Them → me. Digests that
only say "You have 1 new message" without naming the sender can't be matched
to anyone: skip them.

**c) Calendar.** Events in the window that have already happened, with at
least one attendee other than the user. Skip declined events, focus or
blocked time and all-day placeholders, and events without attendees (even if
the title names someone). Channel Meeting. If the user's own response is
still "needs action" on a recurring event, you can't tell whether it took
place: don't log it, list it under "Check" in the digest instead.

**d) Notion meeting notes** in the window: participants and the gist; channel
Meeting. If it's the same meeting as a calendar event, merge the two.

## Step 4: match people

Match each counterpart to a People row by Email, then Phone (compare the
digits of the E.164 form), then Signal name or WhatsApp name, then full name.
If two rows could fit, merge with neither and list it in the digest under
"Check".

Add new people only as the settings page allows (default: a two-way exchange,
or a meeting). Never add the user themself, businesses, automated senders or
anyone on the ignore list. New rows get: Name; Email, Phone, Signal name and
WhatsApp name as known; Channels; Company and Role if evident; a Context tag
only if it is obvious and exists on the page; Cadence "C · quarterly"; Needs
review checked.

## Step 5: write Interactions

One row per person, channel and day with activity. Key =
`<Channel>|<chat_id, email address, or calendar/meeting id>|<YYYY-MM-DD>`
(day in `TZ`). Skip a row whose Key already exists. Fill in:

- Summary: one line in your own words on what it was about
- Person, Date, Channel
- Direction: Both, Me → them, Them → me, or Meeting
- Messages: the count
- Follow-up: only if someone promised or asked for something concrete
  ("send Anna the deck")
- Follow-up due: only if a date was named
- Source: Auto

Create rows in batches.

## Step 6: update People that had activity

- **Last contact**: the latest interaction date; only ever move it forward.
  Also Last channel, and add the channel to Channels.
- **Last summary**: 1 or 2 sentences on the latest exchange.
- **Next topic**: one line on what the user could raise next time: an open
  question, the other person's news, something they care about.
- **Open loops**: add new promises (prefix each with its date); remove ones the
  conversation shows are done.
- **Waiting on them**: checked if the user's message was the last one in the
  thread and has gone unanswered for 2 or more days; unchecked once they reply.
- Fill in empty Email, Phone, Signal name, WhatsApp name, Company and Role.

Never overwrite Name, Cadence, Context, Notes or a non-empty Company or Role.
Never delete rows.

## Step 7: digest

Query People whose Cadence is not Paused and whose Reach out by is today or
earlier, or whose Open loops is not empty. Reach out by is a formula, so use a
rows query with a formula filter on its date result (for example
`date_is_on_or_before` `today`), not SQL. Pick at most 5 people to reach out
to: first those whose Reach out by is today or earlier (most overdue first,
Cadence A before B before C before D), then those with open loops or
follow-ups due. For each: the name, why now ("last talked 5 weeks ago on
Signal, about her fundraising"), and a one-line opener in the tone the
settings page asks for, in the language they use with that person.

Then list, briefly:

- new people added (Needs review)
- Interactions follow-ups due in the next 2 days
- "Check": matches you weren't sure about, and meetings you couldn't confirm
- channels skipped, and why (what the user can do about it)

Send it with a push or message tool if one is available, and repeat it as the
final reply. Keep it phone-sized; no message quotes. If there was no activity
and nobody is due, one line is enough.

## Cleanup

Leave the export folders in place (the user decides when to delete them; say
so in the README, not in each digest). Delete nothing.
