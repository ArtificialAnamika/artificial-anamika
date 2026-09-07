"""Tests for SQLite Memory and Context Manager."""

import os
import tempfile
import unittest
from anamika.memory import MemoryManager


class TestMemory(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_memory.db")
        self.memory = MemoryManager(self.db_path)

    def test_message_history(self):
        session_id = "test_sess_1"
        self.memory.add_message(session_id, "user", "Hello Anamika")
        self.memory.add_message(session_id, "assistant", "Hello Anant! Kaise help kar sakti hoon?")

        history = self.memory.get_history(session_id)
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]["role"], "user")
        self.assertEqual(history[0]["content"], "Hello Anamika")
        self.assertEqual(history[1]["role"], "assistant")

    def test_durable_facts(self):
        self.memory.set_fact("device_model", "OnePlus Pad 2")
        self.memory.set_fact("battery_type", "Li-Po 9510 mAh")

        facts = self.memory.get_all_facts()
        self.assertEqual(facts.get("device_model"), "OnePlus Pad 2")
        self.assertEqual(facts.get("battery_type"), "Li-Po 9510 mAh")

    def test_clear_history(self):
        session_id = "test_sess_2"
        self.memory.add_message(session_id, "user", "Test message")
        self.memory.clear_history(session_id)
        history = self.memory.get_history(session_id)
        self.assertEqual(len(history), 0)


if __name__ == "__main__":
    unittest.main()
