"""Tests for Config Manager and Model Prober."""

import os
import tempfile
import unittest
from anamika.config import Config, fetch_available_models


class TestConfig(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, "config.json")

    def test_default_config_properties(self):
        cfg = Config(self.config_file)
        self.assertEqual(cfg.endpoint, "https://api.mandalworkforce.com/v1")
        self.assertEqual(cfg.model, "claude-3-7-sonnet-20250219")
        self.assertFalse(cfg.is_configured)

    def test_save_and_retrieve_config(self):
        cfg = Config(self.config_file)
        cfg.set("endpoint", "https://api.mandalworkforce.com/v1")
        cfg.set("api_key", "sk-test-key-12345")
        cfg.set("model", "claude-sonnet-4-6")
        cfg.set("device_name", "OnePlus-Tab")
        cfg.set("allowed_telegram_users", [7361027380])

        # Reload from disk
        cfg_reloaded = Config(self.config_file)
        self.assertEqual(cfg_reloaded.endpoint, "https://api.mandalworkforce.com/v1")
        self.assertEqual(cfg_reloaded.api_key, "sk-test-key-12345")
        self.assertEqual(cfg_reloaded.model, "claude-sonnet-4-6")
        self.assertEqual(cfg_reloaded.device_name, "OnePlus-Tab")
        self.assertEqual(cfg_reloaded.allowed_telegram_users, [7361027380])
        self.assertTrue(cfg_reloaded.is_configured)


if __name__ == "__main__":
    unittest.main()
