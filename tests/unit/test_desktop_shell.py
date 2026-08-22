#!/usr/bin/env python3
"""
Unit tests for AetherOS Desktop Shell (Dock, TopBar, Launcher, QuickSettings, Notifications)
"""

import os
import sys
import unittest
import tempfile
import importlib.util

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO_ROOT)

# Dynamic import helpers for folders with hyphens
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

            # Unpin
            dock.unpin_app("custom-app")
            self.assertFalse(any(a["id"] == "custom-app" for a in dock.pinned_apps))

    def test_topbar_model(self):
        bar = topbar_mod.AetherTopBarModel()
        status = bar.get_status_payload()
        self.assertEqual(status["active_workspace"], 1)
        self.assertIn("time_str", status)
        self.assertTrue(bar.switch_workspace(3))
        self.assertEqual(bar.active_workspace, 3)

    def test_launcher_search(self):
        engine = launcher_mod.AetherLauncherEngine()
        # Add mock apps for deterministic testing
        engine.apps = [
            {"id": "firefox.desktop", "name": "Firefox Web Browser", "categories": ["Internet"], "comment": "Browse the web", "exec": "firefox"},
            {"id": "thunar.desktop", "name": "Files", "categories": ["System", "Accessories"], "comment": "File Manager", "exec": "thunar"},
            {"id": "foot.desktop", "name": "Aether Terminal", "categories": ["System", "Development"], "comment": "Terminal Emulator", "exec": "foot"},
        ]
        
        results = engine.search("terminal")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "Aether Terminal")

        # Category filter
        internet_results = engine.search("", category="Internet")
        self.assertEqual(len(internet_results), 1)
        self.assertEqual(internet_results[0]["name"], "Firefox Web Browser")

    def test_quicksettings_toggles(self):
        qs = quicksettings_mod.QuickSettingsState()
        self.assertTrue(qs.wifi_enabled)
        toggled_wifi = qs.toggle_wifi()
        self.assertFalse(toggled_wifi)

        vol = qs.set_volume(90)
        self.assertEqual(vol, 90)

    def test_notifications_daemon(self):
        center = notifications_mod.AetherNotificationCenter()
        n1 = center.post_notification("TestApp", "Header 1", "Body text 1", urgency=1)
        self.assertEqual(len(center.get_active_notifications()), 1)
        self.assertEqual(n1.summary, "Header 1")

        # Dismiss
        self.assertTrue(center.dismiss(n1.id))
        self.assertEqual(len(center.get_active_notifications()), 0)

if __name__ == "__main__":
    unittest.main()
