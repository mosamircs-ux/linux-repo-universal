#!/usr/bin/env python3
"""
Unit tests for AetherOS System Settings Subsystem (aether-settings)
Validates all 26 backend subsystem connectors, Polkit privilege validation,
safe display 15s confirmation rollback, Btrfs snapshots, and bilingual persistence.
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
polkit_mod = load_module_from_path("polkit_helper", os.path.join(REPO_ROOT, "apps/aether-settings/backend/polkit_helper.py"))

AetherSettingsModel = settings_mod.AetherSettingsModel
SECTIONS = settings_mod.SECTIONS

class TestAetherSettings(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.cfg_file = os.path.join(self.temp_dir.name, "settings.json")
        self.model = AetherSettingsModel(config_path=self.cfg_file)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_all_26_sections_defined(self):
        self.assertEqual(len(SECTIONS), 26)
        expected_sections = [
            "wifi", "ethernet", "vpn", "bluetooth", "display", "sound",
            "keyboard", "mouse", "touchpad", "printers", "users", "privacy",
            "security", "applications", "default_apps", "notifications",
            "appearance", "accessibility", "datetime", "language", "region",
            "power", "storage", "backup", "updates", "about"
        ]
        actual_ids = [s["id"] for s in SECTIONS]
        for sec in expected_sections:
            self.assertIn(sec, actual_ids, f"Section {sec} missing from SECTIONS")

    def test_get_all_26_sections_data(self):
        for sec in SECTIONS:
            sec_id = sec["id"]
            data = self.model.get_section_data(sec_id)
            self.assertIsInstance(data, dict, f"Section data for {sec_id} is not a dict")

    def test_polkit_privileged_whitelist(self):
        # Whitelisted command check
        self.assertIn("timedatectl", polkit_mod.ALLOWED_COMMANDS)
        self.assertIn("btrfs", polkit_mod.ALLOWED_COMMANDS)
        self.assertIn("ufw", polkit_mod.ALLOWED_COMMANDS)

        # Forbidden command should fail validation
        ok, msg = polkit_mod.run_privileged(["rm", "-rf", "/"])
        self.assertFalse(ok)
        self.assertIn("whitelist", msg)

    def test_display_rollback_watchdog(self):
        disp_backend = self.model.display
        displays = disp_backend.get_displays()
        self.assertGreaterEqual(len(displays), 1)

        # Apply mode with watchdog confirmation
        ok, msg = disp_backend.apply_display_mode(displays[0]["name"], "1920x1080", "60.00Hz", scale=1.25, require_confirmation=True)
        self.assertTrue(ok)
        self.assertIsNotNone(disp_backend._rollback_timer)

        # User confirms
        confirmed = disp_backend.confirm_display_mode()
        self.assertTrue(confirmed)
        self.assertIsNone(disp_backend._rollback_timer)

    def test_sound_backend(self):
        sound = self.model.sound
        status = sound.get_audio_status()
        self.assertIn("output_volume", status)
        self.assertIn("sinks", status)

        self.assertTrue(sound.set_output_volume(85))
        self.assertTrue(sound.set_output_mute(False))

    def test_network_and_vpn_backend(self):
        net = self.model.network
        status = net.get_status()
        self.assertIn("wifi_enabled", status)
        
        wifis = net.scan_wifi_networks()
        self.assertIsInstance(wifis, list)
        self.assertGreater(len(wifis), 0)

        eths = net.get_ethernet_interfaces()
        self.assertIsInstance(eths, list)

        vpns = net.get_vpn_connections()
        self.assertIsInstance(vpns, list)

    def test_bluetooth_backend(self):
        bt = self.model.bluetooth
        status = bt.get_adapter_status()
        self.assertIn("powered", status)

        devices = bt.get_paired_devices()
        self.assertIsInstance(devices, list)
        if devices:
            self.assertIn("mac", devices[0])

    def test_users_backend(self):
        users_b = self.model.users
        users = users_b.get_users()
        self.assertIsInstance(users, list)
        self.assertGreater(len(users), 0)
        self.assertIn("username", users[0])
        self.assertIn("uid", users[0])

    def test_security_and_privacy_backend(self):
        sec = self.model.security
        status = sec.get_security_status()
        self.assertIn("firewall_active", status)
        self.assertIn("apparmor_active", status)
        self.assertTrue(sec.clear_recent_files())

    def test_backup_btrfs_backend(self):
        backup = self.model.backup
        snapshots = backup.get_snapshots()
        self.assertIsInstance(snapshots, list)
        self.assertGreater(len(snapshots), 0)
        self.assertIn("name", snapshots[0])

    def test_language_switch_and_rtl(self):
        self.assertTrue(self.model.set_language("ar"))
        self.assertEqual(self.model.language, "ar")
        self.assertTrue(self.model.is_rtl())
        self.assertIn("إعدادات", self.model.get_text("title"))

        self.assertTrue(self.model.set_language("en"))
        self.assertEqual(self.model.language, "en")
        self.assertFalse(self.model.is_rtl())

    def test_persistence(self):
        self.model.set_language("ar")
        self.model.accent_color = "#6366F1"
        self.model.volume_level = 95
        self.model.active_section = "display"
        self.assertTrue(self.model.save_settings())

        # Load fresh model
        loaded = AetherSettingsModel(config_path=self.cfg_file)
        self.assertEqual(loaded.language, "ar")
        self.assertEqual(loaded.accent_color, "#6366F1")
        self.assertEqual(loaded.volume_level, 95)
        self.assertEqual(loaded.active_section, "display")

if __name__ == "__main__":
    unittest.main()
