#!/usr/bin/env python3
"""
Unit tests for AetherOS Desktop Shell (Dock, TopBar, Launcher, QuickSettings, Notifications)
Verifies models, light/dark theme toggles, fuzzy search, workspace management, and power actions.
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

dock_mod = load_module_from_path("dock", os.path.join(REPO_ROOT, "desktop/shell/aether-dock/dock.py"))
topbar_mod = load_module_from_path("topbar", os.path.join(REPO_ROOT, "desktop/shell/aether-topbar/topbar.py"))
launcher_mod = load_module_from_path("launcher", os.path.join(REPO_ROOT, "desktop/shell/aether-launcher/launcher.py"))
quicksettings_mod = load_module_from_path("quicksettings", os.path.join(REPO_ROOT, "desktop/shell/aether-quicksettings/quicksettings.py"))
notifications_mod = load_module_from_path("notifications", os.path.join(REPO_ROOT, "desktop/shell/aether-notifications/daemon.py"))

class TestDesktopShell(unittest.TestCase):
    def test_dock_model(self):
        with tempfile.TemporaryDirectory() as td:
            cfg_file = os.path.join(td, "dock.json")
            dock = dock_mod.AetherDockModel(config_path=cfg_file)
            self.assertEqual(dock.position, "left")
            self.assertGreater(len(dock.pinned_apps), 3)

            # Pin new app
            dock.pin_app("custom-app", "Custom App", "app-icon", "/usr/bin/custom")
            self.assertTrue(any(a["id"] == "custom-app" for a in dock.pinned_apps))

            # Running indicator
            dock.set_app_running("custom-app", running=True, badge=3)
            app_entry = next(a for a in dock.pinned_apps if a["id"] == "custom-app")
            self.assertTrue(app_entry["running"])
            self.assertEqual(app_entry["badge"], 3)

            # RTL Mirroring
            dock.set_rtl(True)
            self.assertEqual(dock.position, "right")
            dock.set_rtl(False)
            self.assertEqual(dock.position, "left")

            # Unpin
            dock.unpin_app("custom-app")
            self.assertFalse(any(a["id"] == "custom-app" for a in dock.pinned_apps))

    def test_topbar_model(self):
        bar = topbar_mod.AetherTopBarModel()
        status = bar.get_status_payload()
        self.assertEqual(status["active_workspace"], 1)
        self.assertIn("time_str", status)
        self.assertIn("network", status)
        self.assertIn("audio", status)
        self.assertIn("battery", status)

        # Workspace switching
        self.assertTrue(bar.switch_workspace(3))
        self.assertEqual(bar.active_workspace, 3)
        self.assertFalse(bar.switch_workspace(99))  # Out of range

        # Calendar toggle
        cal = bar.toggle_calendar()
        self.assertTrue(cal)

        # Volume update
        bar.set_volume(85, muted=False)
        self.assertEqual(bar.audio_status["volume_percent"], 85)

    def test_launcher_search(self):
        engine = launcher_mod.AetherLauncherEngine()
        engine.apps = [
            {"id": "firefox.desktop", "name": "Firefox Web Browser", "categories": ["Internet"], "comment": "Browse the web", "exec": "firefox"},
            {"id": "thunar.desktop", "name": "Files", "categories": ["System", "Accessories"], "comment": "File Manager", "exec": "thunar"},
            {"id": "foot.desktop", "name": "Aether Terminal", "categories": ["System", "Development"], "comment": "Terminal Emulator", "exec": "foot"},
            {"id": "code.desktop", "name": "Code Studio", "categories": ["Development"], "comment": "Code Editor", "exec": "code"},
        ]
        
        # Search query
        results = engine.search("terminal")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "Aether Terminal")

        # Category filter
        dev_results = engine.search("", category="Development")
        self.assertEqual(len(dev_results), 2)

        # Combined search + category
        query_dev = engine.search("code", category="Development")
        self.assertEqual(len(query_dev), 1)
        self.assertEqual(query_dev[0]["name"], "Code Studio")

    def test_quicksettings_toggles_and_power(self):
        with tempfile.TemporaryDirectory() as td:
            cfg = os.path.join(td, "qs.json")
            qs = quicksettings_mod.QuickSettingsState(config_path=cfg)
            
            # Wi-Fi toggle
            self.assertTrue(qs.wifi_enabled)
            toggled_wifi = qs.toggle_wifi()
            self.assertFalse(toggled_wifi)

            # Bluetooth toggle
            self.assertTrue(qs.bluetooth_enabled)
            toggled_bt = qs.toggle_bluetooth()
            self.assertFalse(toggled_bt)

            # Dark / Light Mode toggle
            self.assertTrue(qs.dark_mode)
            light_mode = not qs.toggle_dark_mode()
            self.assertTrue(light_mode)
            # Revert to dark
            qs.toggle_dark_mode()
            self.assertTrue(qs.dark_mode)

            # Night light
            self.assertFalse(qs.night_light)
            nl = qs.toggle_night_light()
            self.assertTrue(nl)

            # Sliders
            vol = qs.set_volume(90)
            self.assertEqual(vol, 90)
            bri = qs.set_brightness(60)
            self.assertEqual(bri, 60)

            # Power profile
            profile = qs.set_power_profile("power-saver")
            self.assertEqual(profile, "power-saver")

    def test_notifications_daemon(self):
        center = notifications_mod.AetherNotificationCenter()
        n1 = center.post_notification("TestApp", "Header 1", "Body text 1", urgency=1, actions=["Open", "Dismiss"])
        self.assertEqual(len(center.get_active_notifications()), 1)
        self.assertEqual(n1.summary, "Header 1")
        self.assertEqual(n1.actions, ["Open", "Dismiss"])

        n2 = center.post_notification("Mail", "New Email", "You received a new message.", urgency=2)
        self.assertEqual(len(center.get_active_notifications()), 2)

        # DND
        dnd = center.toggle_dnd()
        self.assertTrue(dnd)

        # Dismiss single
        self.assertTrue(center.dismiss(n1.id))
        self.assertEqual(len(center.get_active_notifications()), 1)

        # Clear all
        cleared = center.clear_all()
        self.assertEqual(cleared, 1)
        self.assertEqual(len(center.get_active_notifications()), 0)
        self.assertEqual(len(center.get_history()), 2)

if __name__ == "__main__":
    unittest.main()
