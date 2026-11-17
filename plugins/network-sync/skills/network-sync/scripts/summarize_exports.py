#!/usr/bin/env python3
"""Summarise Chat Export for Signal / WhatsApp folders for network-sync.

Reads people.jsonl, chats.jsonl and messages.jsonl from each export folder and
prints one JSON object per relevant chat (direct chats, plus small groups) with
per-day message counts and the window's message texts, capped. Standard
library only; Python 3.9 or newer. Read-only: it never changes the exports.

Usage:
  python3 summarize_exports.py --since 2026-11-14 --tz Europe/Berlin EXPORT_DIR...
"""

import argparse
import json
import os
import sys
from collections import defaultdict
from datetime import datetime, timezone

try:
    from zoneinfo import ZoneInfo
except ImportError:  # pragma: no cover
    sys.exit("Python 3.9 or newer is needed (zoneinfo).")

NOTE_TO_SELF = {"note to self", "notiz an mich", "note à soi", "nota personal", "message yourself"}
SKIP_TYPES = {"system", "call", "deleted"}


def read_jsonl(path):
    if not os.path.exists(path):
        return []
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def channel_of(folder):
    try:
        with open(os.path.join(folder, "manifest.json"), encoding="utf-8") as f:
            name = json.load(f).get("generator", {}).get("name", "")
    except (OSError, ValueError):
        name = ""
    hint = (name or os.path.basename(os.path.normpath(folder))).lower()
    if "signal" in hint:
        return "Signal"
    if "whatsapp" in hint:
        return "WhatsApp"
    return "Chat"


def msg_time(m):
    if m.get("sent_at_ms") is not None:
        return datetime.fromtimestamp(m["sent_at_ms"] / 1000, tz=timezone.utc)
    if m.get("sent_at"):
        return datetime.fromisoformat(m["sent_at"].replace("Z", "+00:00"))
    return None


def summarise(folder, since, tz, small_group, max_messages, max_chars, only=None):
    channel = channel_of(folder)
    people = {p["person_id"]: p for p in read_jsonl(os.path.join(folder, "people.jsonl"))}
    me_ids = {pid for pid, p in people.items() if p.get("is_me")} | {"me"}
    chats = {c["chat_id"]: c for c in read_jsonl(os.path.join(folder, "chats.jsonl"))}

    by_chat = defaultdict(list)
    for m in read_jsonl(os.path.join(folder, "messages.jsonl")):
        by_chat[m.get("chat_id")].append(m)

    for chat_id, msgs in by_chat.items():
        if only and chat_id not in only:
            continue
        chat = chats.get(chat_id, {})
        others = [pid for pid in chat.get("member_ids", []) if pid not in me_ids]
        if chat.get("person_id") and chat["person_id"] not in me_ids and chat["person_id"] not in others:
            others.append(chat["person_id"])
        kind = chat.get("type")
        if kind == "direct":
            if not others or (chat.get("name") or "").strip().lower() in NOTE_TO_SELF:
                continue
        elif kind == "group":
            if not others or len(others) > small_group:
                continue
        else:
            continue

        window = []
        for m in msgs:
            t = msg_time(m)
            if t is None or m.get("type") in SKIP_TYPES or m.get("direction") not in ("incoming", "outgoing"):
                continue
            local = t.astimezone(tz)
            if local.date() < since:
                continue
            window.append((local, m))
        if not window:
            continue
        # A group only counts if the user wrote in it: member lists can be incomplete,
        # and a group the user only reads is no exchange with anyone.
        if kind == "group" and not any(m["direction"] == "outgoing" for _, m in window):
            continue
        window.sort(key=lambda x: x[0])

        days = defaultdict(lambda: {"in": 0, "out": 0})
        for local, m in window:
            days[local.date().isoformat()]["in" if m["direction"] == "incoming" else "out"] += 1

        texts = []
        for local, m in (window[-max_messages:] if max_messages > 0 else []):
            text = (m.get("text") or "").strip()
            if not text:
                text = "[" + (m.get("type") or "media") + "]"
            if len(text) > max_chars:
                text = text[: max_chars - 1] + "…"
            who = "me" if m["direction"] == "outgoing" else (m.get("sender_name") or "them")
            texts.append({"at": local.strftime("%Y-%m-%d %H:%M"), "from": who, "text": text})

        yield {
            "channel": channel,
            "chat_id": chat_id,
            "chat_name": chat.get("name"),
            "type": kind,
            "people": [
                {"name": people.get(pid, {}).get("name"), "phone": people.get(pid, {}).get("phone")}
                for pid in others
            ],
            "days": dict(sorted(days.items())),
            "last_from": "me" if window[-1][1]["direction"] == "outgoing" else "them",
            "last_at": window[-1][0].strftime("%Y-%m-%d %H:%M"),
            "messages": texts,
        }


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("folders", nargs="+", help="Export folders (missing ones are skipped)")
    ap.add_argument("--since", required=True, help="First day of the window, YYYY-MM-DD, in --tz")
    ap.add_argument("--tz", default="UTC", help="IANA time zone for days, e.g. Europe/Berlin")
    ap.add_argument("--small-group", type=int, default=3,
                    help="Groups with at most this many other people count as direct chats (0 = skip all groups)")
    ap.add_argument("--max-messages", type=int, default=40, help="Messages per chat to print (0 = counts only)")
    ap.add_argument("--only", action="append", metavar="CHAT_ID", help="Only this chat (repeatable), for working in batches")
    ap.add_argument("--max-chars", type=int, default=300, help="Characters per message to print")
    args = ap.parse_args()

    since = datetime.strptime(args.since, "%Y-%m-%d").date()
    tz = ZoneInfo(args.tz)
    count = 0
    for folder in args.folders:
        if not os.path.isdir(folder):
            print(json.dumps({"skipped": folder, "reason": "not found"}), file=sys.stderr)
            continue
        for row in summarise(folder, since, tz, args.small_group, args.max_messages, args.max_chars,
                             set(args.only) if args.only else None):
            print(json.dumps(row, ensure_ascii=False))
            count += 1
    print(json.dumps({"chats": count}), file=sys.stderr)


if __name__ == "__main__":
    main()
