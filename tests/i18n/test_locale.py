#!/usr/bin/env python3
"""
Localization & RTL Verification Test
Verifies that all core UI strings exist in both English (en) and Arabic (ar),
and that RTL layout flags are properly honored.
"""

import os
import sys
import unittest
import importlib.util

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def load_module_from_path(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

settings_mod = load_module_from_path("settings_app", os.path.join(REPO_ROOT, "apps/aether-settings/settings_app.py"))

class TestLocalization(unittest.TestCase):
    def test_translation_completeness(self):
        translations = settings_mod.TRANSLATIONS
        self.assertIn("en", translations)
        self.assertIn("ar", translations)

        en_keys = set(translations["en"].keys())
        ar_keys = set(translations["ar"].keys())

        # Check key parity
        missing_in_ar = en_keys - ar_keys
        missing_in_en = ar_keys - en_keys
        self.assertEqual(len(missing_in_ar), 0, f"Keys missing in Arabic: {missing_in_ar}")
        self.assertEqual(len(missing_in_en), 0, f"Keys missing in English: {missing_in_en}")

    def test_arabic_rtl_flag(self):
        model = settings_mod.AetherSettingsModel()
        model.set_language("en")
        self.assertFalse(model.is_rtl())

        model.set_language("ar")
        self.assertTrue(model.is_rtl())

if __name__ == "__main__":
    unittest.main()
