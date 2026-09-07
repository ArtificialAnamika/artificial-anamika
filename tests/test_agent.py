"""Tests for Agent Reasoning and Tool Loop."""

import os
import tempfile
import unittest
from unittest.mock import MagicMock
from anamika.config import Config
from anamika.memory import MemoryManager
from anamika.tools import ToolRegistry
from anamika.agent import Agent
from anamika.client import LLMResponse


class TestAgent(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.cfg = Config(os.path.join(self.temp_dir, "config.json"))
        self.cfg.set("endpoint", "https://api.mandalworkforce.com/v1")
        self.cfg.set("api_key", "sk-mock-key")
        self.cfg.set("model", "claude-3-7-sonnet")
        self.memory = MemoryManager(os.path.join(self.temp_dir, "mem.db"))
        
        self.tools = ToolRegistry()
        def mock_battery():
            return {"percentage": 92, "status": "discharging"}
        self.tools.register(mock_battery, name="get_battery_status")

        self.agent = Agent(self.cfg, tools=self.tools, memory=self.memory)

    def test_direct_response_without_tools(self):
        self.agent.client.chat_completion = MagicMock(return_value=LLMResponse(
            content="Anant, main bilkul ready hoon!"
        ))
        res = self.agent.chat("Status batao", session_id="test_sess")
        self.assertEqual(res["content"], "Anant, main bilkul ready hoon!")
        self.assertEqual(len(res["tools_executed"]), 0)

    def test_tool_calling_loop(self):
        # Step 1: LLM returns a tool call
        tool_call_resp = LLMResponse(
            content="",
            tool_calls=[{
                "id": "call_123",
                "function": {
                    "name": "get_battery_status",
                    "arguments": "{}"
                }
            }]
        )
        # Step 2: LLM returns final response after seeing tool output
        final_resp = LLMResponse(
            content="Anant, battery abhi 92% hai aur discharging state me hai."
        )

        self.agent.client.chat_completion = MagicMock(side_effect=[tool_call_resp, final_resp])
        
        res = self.agent.chat("Phone ki battery check karo", session_id="test_tool_sess")
        self.assertEqual(len(res["tools_executed"]), 1)
        self.assertEqual(res["tools_executed"][0]["name"], "get_battery_status")
        self.assertEqual(res["tools_executed"][0]["result"]["percentage"], 92)
        self.assertEqual(res["content"], "Anant, battery abhi 92% hai aur discharging state me hai.")


if __name__ == "__main__":
    unittest.main()
