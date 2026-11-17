# Privacy statement

Network Sync is a set of instructions and one small script that Claude
follows on your behalf. Its author runs no server and collects no data from
you.

## What it processes

When it runs, Claude reads, through the connectors and computer access you
gave it: recent email threads, calendar events, Notion meeting notes, and, if
you use the chat-export plugins, recent direct messages from Signal and
WhatsApp exported on your own Mac. The helper script runs on your Mac and only
reads those export files.

## Where data goes

- **Your Notion workspace**: short summaries written in Claude's words, names,
  email addresses, phone numbers and dates. No message text is copied.
- **Your Mac**: the chat exports, in `~/network-tracker/exports`. They stay
  until you delete them.
- **Your Claude conversation**: what Claude reads during a run (including the
  message excerpts the helper script prints) is part of that conversation and
  is handled under Anthropic's privacy policy and your Claude settings.

Nothing is sent anywhere else. The skill tells Claude never to send, post or
reply on any channel.

## The people in your tracker

The tracker holds information about other people. Keep it private, and honour
anyone who asks you to remove them: add them to the ignore list on the
settings page and delete their rows.
