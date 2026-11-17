# Schedule

Run Sync once a day, in the early evening by default, so the digest arrives
while there's still time to send a message.

## Where it runs

Signal and WhatsApp need the user's Mac. Pick whichever scheduler this session
offers:

- **Claude app scheduled task** (runs on the Mac while the app is open and the
  Mac is awake): has every channel.
- **Cloud routine bound to the user's computer**: same, as long as the computer
  is online when it fires.
- **Cloud routine without a computer**: email, calendar, Notion and LinkedIn
  emails only. The digest will say that Signal and WhatsApp were skipped.

If the Mac was off, nothing is lost: the 3-day lookback catches up and Keys
prevent duplicates.

## The scheduled prompt

Keep it short. Everything else lives on the settings page and in this skill,
so the user can change behaviour without touching the schedule.

```
Daily network sync. Work autonomously: nobody is watching this run.
Load the network-sync skill and run Sync (reference/sync.md).
Settings page: <settings page URL>
The user has approved running the chat export scripts on their Mac
unattended, as the settings page describes.
```

Before creating it, confirm with the user: the time, which scheduler, and that
they approve unattended runs of the export scripts (and, if they said yes to
it on the settings page, quitting and reopening Signal Desktop). Create the
schedule with the session's scheduling tool, set its permission mode so the
run doesn't stop at prompts the user already approved, and run it once right
away so they can see a digest.
