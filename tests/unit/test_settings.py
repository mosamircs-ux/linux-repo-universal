#!/usr/bin/env python3
"""
Unit tests for AetherOS Settings Subsystem
"""

import os
import sys
import unittest
import tempfile
import importlib.util

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO_ROOT)

def load_module_from_path(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

settings_mod = load_module_from_path("settings_app", os.path.join(REPO_ROOT, "apps/aether-settings/settings_app.py"))
AetherSettingsModel = settings_mod.AetherSettingsModel
TRANSLATIONS = settings_mod.TRANSLATIONS

class TestAetherSettings(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.cfg_file = os.path.join(self.temp_dir.name, "settings.json")
        self.model = AetherSettingsModel(config_path=self.cfg_file)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_default_values(self):
        self.assertEqual(self.model.language, "en")
        self.assertTrue(self.model.dark_mode)
        self.assertEqual(self.model.accent_color, "#00D2FF")
        self.assertFalse(self.model.is_rtl())

    def test_language_switch_and_rtl(self):
        self.assertTrue(self.model.set_language("ar"))
        self.assertEqual(self.model.language, "ar")
        self.assertTrue(self.model.is_rtl())
        self.assertIn("إعدادات", self.model.get_text("title"))

    def test_persistence(self):
        self.model.set_language("ar")
        self.model.accent_color = "#6366F1"
        self.model.volume_level = 95
        self.assertTrue(self.model.save_settings())

        # Load fresh model
        loaded = AetherSettingsModel(config_path=self.cfg_file)
        self.assertEqual(loaded.language, "ar")
        self.assertEqual(loaded.accent_color, "#6366F1")
        self.assertEqual(loaded.volume_level, 95)

    def test_system_info(self):
        info = self.model.get_system_info()
        self.assertEqual(info["os_name"], "AetherOS")
        self.assertIn("Solstice", info["version"])

if __name__ == "__main__":
    unittest.main()
