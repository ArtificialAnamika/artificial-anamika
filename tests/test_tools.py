"""Tests for Tool Registry and Android Tool Schemas."""

import unittest
from anamika.tools import create_default_registry, ToolRegistry
from anamika.tools.hardware import set_torch
from anamika.tools.android_os import APP_PACKAGES, SETTINGS_INTENTS


class TestTools(unittest.TestCase):

    def setUp(self):
        self.registry = create_default_registry()

    def test_default_tools_registered(self):
        tools = self.registry.tools
        self.assertIn("get_battery_status", tools)
        self.assertIn("set_torch", tools)
        self.assertIn("vibrate", tools)
        self.assertIn("list_sms", tools)
        self.assertIn("send_sms", tools)
        self.assertIn("tts_speak", tools)
        self.assertIn("launch_app", tools)
        self.assertIn("execute_shell", tools)
        self.assertIn("take_photo", tools)

    def test_schema_generation(self):
        schemas = self.registry.get_schemas()
        self.assertTrue(len(schemas) > 15)
        
        torch_schema = next(s for s in schemas if s["function"]["name"] == "set_torch")
        self.assertEqual(torch_schema["type"], "function")
        self.assertIn("state", torch_schema["function"]["parameters"]["properties"])

    def test_torch_validation(self):
        res = set_torch("invalid_state")
        self.assertIn("error", res)

    def test_app_packages_mapping(self):
        self.assertEqual(APP_PACKAGES["whatsapp"], "com.whatsapp")
        self.assertEqual(APP_PACKAGES["youtube"], "com.google.android.youtube")
        self.assertIn("wifi", SETTINGS_INTENTS)


if __name__ == "__main__":
    unittest.main()
