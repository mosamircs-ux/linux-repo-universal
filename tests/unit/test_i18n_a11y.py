#!/usr/bin/env python3
"""
Unit and Integration Tests for AetherOS Internationalization (i18n) & Accessibility (a11y)
Validates:
  - English & Arabic translations
  - BiDi RTL layout direction switching
  - Arabic numerals (Eastern & Western digits)
  - Arabic date/time localization
  - Arabic keyboard layout configuration
  - Accessibility engine (Screen reader, High contrast, Text scaling, Reduced motion, Large cursor, AccessX)
  - 100% Arabic coverage across all .desktop application launchers
  - Automated audit tool (distro i18n-audit)
"""

import os
import sys
import json
import datetime
import tempfile
import unittest
import importlib.util
from importlib.machinery import SourceFileLoader

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO_ROOT)

def load_mod(name, rel_path):
    fpath = os.path.join(REPO_ROOT, rel_path)
    loader = SourceFileLoader(name, fpath)
    spec = importlib.util.spec_from_file_location(name, fpath, loader=loader)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

i18n_mod = load_mod("aether_i18n", "system/i18n/aether_i18n.py")
a11y_mod = load_mod("aether_a11y", "system/accessibility/aether_a11y.py")
audit_mod = load_mod("distro_i18n_audit", "scripts/distro-i18n-audit")

class TestI18nAndAccessibility(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.temp_dir.cleanup()

    # 1. Translation Catalog
    def test_i18n_translation_catalog(self):
        engine = i18n_mod.I18nEngine("en")
        self.assertEqual(engine.translate("Settings"), "Settings")
        self.assertEqual(engine.translate("Terminal"), "Terminal")

        # Switch to Arabic
        self.assertTrue(engine.set_language("ar_SA"))
        self.assertEqual(engine.translate("Settings"), "الإعدادات")
        self.assertEqual(engine.translate("Terminal"), "الطرفية")
        self.assertEqual(engine.translate("Software Center"), "مركز البرمجيات")
        self.assertEqual(engine.translate("Screen Reader"), "قارئ الشاشة")
        self.assertEqual(engine.translate("Install"), "تثبيت")

    # 2. RTL Text Direction
    def test_rtl_and_bidi_text_direction(self):
        engine = i18n_mod.I18nEngine("en")
        self.assertFalse(engine.is_rtl())
        self.assertEqual(engine.get_text_direction(), "ltr")

        engine.set_language("ar")
        self.assertTrue(engine.is_rtl())
        self.assertEqual(engine.get_text_direction(), "rtl")

    # 3. Eastern Arabic Numerals
    def test_eastern_arabic_numerals_conversion(self):
        engine = i18n_mod.I18nEngine("ar")
        res = engine.to_eastern_arabic_digits("2026-08-26 12:34:56")
        self.assertEqual(res, "٢٠٢٦-٠٨-٢٦ ١٢:٣٤:٥٦")

    # 4. Date and Time Localization
    def test_arabic_date_and_time_formatting(self):
        engine = i18n_mod.I18nEngine("ar")
        dt = datetime.datetime(2026, 8, 26, 15, 30)

        # Arabic date
        date_str = engine.format_date(dt)
        self.assertIn("أغسطس", date_str)
        self.assertIn("2026", date_str)

        # Arabic 12h time
        time_str = engine.format_time(dt, use_24h=False)
        self.assertIn("م", time_str)  # PM indicator
        self.assertIn("3:30", time_str)

    # 5. Arabic Keyboard Mapping
    def test_arabic_keyboard_layout_configuration(self):
        engine = i18n_mod.I18nEngine()
        kbd = engine.get_keyboard_layout_config()
        self.assertIn("us,ara", kbd["layout"])
        self.assertIn("grp:alt_shift_toggle", kbd["options"])

    # 6. Accessibility Engine
    def test_accessibility_manager_settings(self):
        cfg_path = os.path.join(self.temp_dir.name, "a11y.json")
        mgr = a11y_mod.AccessibilityManager(config_file=cfg_path)

        # Screen reader
        self.assertTrue(mgr.set_screen_reader(True))
        self.assertTrue(mgr.settings["screen_reader"])

        # High contrast
        self.assertTrue(mgr.set_high_contrast(True))
        self.assertTrue(mgr.settings["high_contrast"])

        # Text scaling factor
        factor = mgr.set_text_scaling(1.5)
        self.assertEqual(factor, 1.5)

        # Pointer size
        psz = mgr.set_pointer_size(48)
        self.assertEqual(psz, 48)
        self.assertTrue(mgr.settings["large_pointer"])

        # AccessX
        self.assertTrue(mgr.set_accessx_feature("sticky_keys", True))
        self.assertTrue(mgr.settings["sticky_keys"])

        # Reload persistence
        mgr2 = a11y_mod.AccessibilityManager(config_file=cfg_path)
        self.assertTrue(mgr2.settings["screen_reader"])
        self.assertEqual(mgr2.settings["text_scaling"], 1.5)

    # 7. Desktop Launchers Arabic Coverage
    def test_all_desktop_files_have_arabic_localization(self):
        auditor = audit_mod.I18nAuditor()
        passed, failed, details = auditor._audit_desktop_launchers()
        self.assertGreaterEqual(passed, 16)
        self.assertEqual(failed, 0, f"Found desktop files without Arabic translations: {details}")

    # 8. Automated i18n Audit Tool
    def test_distro_i18n_audit_tool(self):
        auditor = audit_mod.I18nAuditor()
        rep = auditor.run_audit()
        self.assertEqual(rep["score"], 100)
        self.assertEqual(rep["grade"], "A+")
        self.assertEqual(rep["failed"], 0)
        self.assertEqual(rep["warnings"], 0)

if __name__ == "__main__":
    unittest.main()
