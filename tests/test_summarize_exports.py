"""Tests for summarize_exports.py, on a small synthetic export. Run: python3 -m unittest discover tests"""

import json
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, "..", "plugins", "network-sync", "skills", "network-sync", "scripts", "summarize_exports.py")


def write_jsonl(path, rows):
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")


def msg(chat, sender, direction, at, text="hi", kind="text"):
    return {"chat_id": chat, "sender_id": sender, "sender_name": sender, "direction": direction,
            "type": kind, "sent_at": at, "text": text}


class SummarizeTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        d = self.dir = os.path.join(self.tmp.name, "whatsapp-2026-11-17")
        os.makedirs(d)
        with open(os.path.join(d, "manifest.json"), "w") as f:
            json.dump({"generator": {"name": "chat-export-for-whatsapp"}}, f)
        write_jsonl(os.path.join(d, "people.jsonl"), [
            {"person_id": "me", "name": "Me", "is_me": True},
            {"person_id": "anna", "name": "Anna Example", "phone": "+15550100", "is_me": False},
            {"person_id": "ben", "name": "Ben", "is_me": False},
            {"person_id": "c1", "name": "C1"}, {"person_id": "c2", "name": "C2"},
            {"person_id": "c3", "name": "C3"}, {"person_id": "c4", "name": "C4"},
        ])
        write_jsonl(os.path.join(d, "chats.jsonl"), [
            {"chat_id": "wa:anna", "name": "Anna Example", "type": "direct", "person_id": "anna", "member_ids": ["me", "anna"]},
            {"chat_id": "wa:self", "name": "Note to Self", "type": "direct", "person_id": "me", "member_ids": ["me"]},
            {"chat_id": "wa:small", "name": "Trio", "type": "group", "member_ids": ["me", "anna", "ben"]},
            {"chat_id": "wa:lurk", "name": "Read only", "type": "group", "member_ids": ["me", "ben"]},
            {"chat_id": "wa:big", "name": "Big", "type": "group", "member_ids": ["me", "c1", "c2", "c3", "c4"]},
            {"chat_id": "wa:calls", "name": "Ben", "type": "direct", "person_id": "ben", "member_ids": ["me", "ben"]},
        ])
        write_jsonl(os.path.join(d, "messages.jsonl"), [
            msg("wa:anna", "anna", "incoming", "2026-11-10T09:00:00Z", "too old"),
            msg("wa:anna", "anna", "incoming", "2026-11-15T09:00:00Z", "x" * 500),
            msg("wa:anna", "me", "outgoing", "2026-11-15T22:30:00Z", "late reply"),  # 23:30 Berlin, same day
            msg("wa:anna", "me", "outgoing", "2026-11-16T08:00:00Z", "", kind="image"),
            msg("wa:self", "me", "outgoing", "2026-11-16T08:00:00Z"),
            msg("wa:small", "ben", "incoming", "2026-11-16T08:00:00Z"),
            msg("wa:small", "me", "outgoing", "2026-11-16T09:00:00Z"),
            msg("wa:lurk", "ben", "incoming", "2026-11-16T08:00:00Z"),
            msg("wa:big", "c1", "incoming", "2026-11-16T08:00:00Z"),
            msg("wa:calls", None, None, "2026-11-16T08:00:00Z", "", kind="call"),
        ])

    def tearDown(self):
        self.tmp.cleanup()

    def run_script(self, *extra):
        out = subprocess.run([sys.executable, SCRIPT, "--since", "2026-11-14", "--tz", "Europe/Berlin", *extra, self.dir],
                             capture_output=True, text=True, check=True).stdout
        return {r["chat_id"]: r for r in map(json.loads, out.splitlines())}

    def test_filters_and_counts(self):
        rows = self.run_script()
        self.assertEqual(set(rows), {"wa:anna", "wa:small"})
        anna = rows["wa:anna"]
        self.assertEqual(anna["channel"], "WhatsApp")
        self.assertEqual(anna["people"], [{"name": "Anna Example", "phone": "+15550100"}])
        self.assertEqual(anna["days"], {"2026-11-15": {"in": 1, "out": 1}, "2026-11-16": {"in": 0, "out": 1}})
        self.assertEqual(anna["last_from"], "me")
        self.assertEqual(len(anna["messages"][0]["text"]), 300)
        self.assertEqual(anna["messages"][2]["text"], "[image]")

    def test_groups_off(self):
        self.assertEqual(set(self.run_script("--small-group", "0")), {"wa:anna"})

    def test_counts_only_and_only_filter(self):
        rows = self.run_script("--max-messages", "0", "--only", "wa:anna")
        self.assertEqual(set(rows), {"wa:anna"})
        self.assertEqual(rows["wa:anna"]["messages"], [])
        self.assertEqual(rows["wa:anna"]["days"]["2026-11-15"], {"in": 1, "out": 1})

    def test_message_cap(self):
        self.assertEqual(len(self.run_script("--max-messages", "1")["wa:anna"]["messages"]), 1)


if __name__ == "__main__":
    unittest.main()
