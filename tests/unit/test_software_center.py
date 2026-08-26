#!/usr/bin/env python3
"""
Unit and Integration Tests for AetherOS Software Center, Update Manager, and distro CLI
Validates APT backend, Flatpak backend, AppStream catalog, Update scanning (OS, Apps, Firmware),
Transactional Btrfs safety snapshots, package database self-healing, and distro CLI suite.
"""

import os
import sys
import tempfile
import unittest
import importlib.util

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO_ROOT)

def load_mod(name, rel_path):
    fpath = os.path.join(REPO_ROOT, rel_path)
    spec = importlib.util.spec_from_file_location(name, fpath)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

apt_mod = load_mod("apt_backend", "apps/aether-software/backend/apt_backend.py")
flatpak_mod = load_mod("flatpak_backend", "apps/aether-software/backend/flatpak_backend.py")
catalog_mod = load_mod("appstream_catalog", "apps/aether-software/backend/appstream_catalog.py")
history_mod = load_mod("history_manager", "apps/aether-software/backend/history_manager.py")
software_hub_mod = load_mod("software_hub", "apps/aether-software/software_hub.py")

update_engine_mod = load_mod("update_engine", "apps/aether-updater/backend/update_engine.py")
recovery_mod = load_mod("transactional_recovery", "apps/aether-updater/backend/transactional_recovery.py")
updater_app_mod = load_mod("updater_app", "apps/aether-updater/updater_app.py")

AptBackend = apt_mod.AptBackend
FlatpakBackend = flatpak_mod.FlatpakBackend
AppStreamCatalog = catalog_mod.AppStreamCatalog
HistoryManager = history_mod.HistoryManager
AetherSoftwareHubModel = software_hub_mod.AetherSoftwareHubModel
UpdateEngine = update_engine_mod.UpdateEngine
TransactionalRecovery = recovery_mod.TransactionalRecovery
AetherUpdateManagerModel = updater_app_mod.AetherUpdateManagerModel

class TestSoftwareCenter(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.history_file = os.path.join(self.temp_dir.name, "software_history.json")
        self.hub = AetherSoftwareHubModel(history_file=self.history_file)
        self.updater = AetherUpdateManagerModel()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_appstream_catalog_categories_and_search(self):
        all_apps = AppStreamCatalog.get_all_apps()
        self.assertGreaterEqual(len(all_apps), 8)

        featured = AppStreamCatalog.get_featured_apps()
        self.assertGreater(len(featured), 0)

        # Test categories
        for cat in ["Internet & Web", "Audio & Video", "Development & Tools", "Graphics & Photography", "Productivity & Office", "System & Utilities", "Games & Entertainment"]:
            cat_apps = AppStreamCatalog.get_by_category(cat)
            self.assertGreater(len(cat_apps), 0, f"Category {cat} should have apps")

        # Test search
        firefox_results = AppStreamCatalog.search("firefox")
        self.assertGreater(len(firefox_results), 0)
        self.assertEqual(firefox_results[0]["id"], "org.mozilla.firefox")

    def test_apt_backend_details(self):
        apt = AptBackend()
        details = apt.get_package_details("htop")
        self.assertEqual(details["package"], "htop")
        self.assertIn("version", details)
        self.assertIn("installed_size_kb", details)

    def test_flatpak_backend_metadata(self):
        fb = FlatpakBackend()
        details = fb.get_app_details("org.videolan.VLC")
        self.assertEqual(details["id"], "org.videolan.VLC")
        self.assertIn("permissions", details)
        self.assertIn("download_size_mb", details)

    def test_transaction_history_recording(self):
        hm = HistoryManager(history_file=self.history_file)
        hm.record_transaction("install", "org.gimp.GIMP", "GIMP Image Editor", "apt", "2.10.38", True)
        
        hist = hm.get_history()
        self.assertEqual(len(hist), 1)
        self.assertEqual(hist[0]["item_id"], "org.gimp.GIMP")
        self.assertEqual(hist[0]["action"], "install")
        self.assertEqual(hist[0]["status"], "success")

    def test_software_hub_model_operations(self):
        featured = self.hub.get_featured_apps()
        self.assertGreater(len(featured), 0)

        # Search
        results = self.hub.search("vlc")
        self.assertGreater(len(results), 0)

        # Install with confirmation
        ok, msg = self.hub.install("org.videolan.VLC", backend="flatpak", confirm=True)
        self.assertTrue(ok)

        # Cancelled confirmation
        ok_cancel, msg_cancel = self.hub.install("org.videolan.VLC", backend="flatpak", confirm=False)
        self.assertFalse(ok_cancel)
        self.assertIn("cancelled", msg_cancel)

    def test_multi_source_update_engine(self):
        engine = UpdateEngine()
        scan = engine.scan_all_updates()

        self.assertIn("total_updates", scan)
        self.assertIn("security_updates_count", scan)
        self.assertIn("os_updates", scan)
        self.assertIn("app_updates", scan)
        self.assertIn("firmware_updates", scan)
        self.assertGreater(scan["total_updates"], 0)

    def test_transactional_recovery_and_healing(self):
        rec = TransactionalRecovery(snapshot_dir=self.temp_dir.name)
        
        # Safety snapshot
        ok, snap_name = rec.create_safety_snapshot("test-pre-upgrade")
        self.assertTrue(ok)
        self.assertIn("snapshot-test-pre-upgrade", snap_name)

        # Database healing
        ok_heal, logs = rec.heal_package_database()
        self.assertTrue(ok_heal)
        self.assertIsInstance(logs, list)

        # Rollback
        ok_rb, msg_rb = rec.rollback_to_snapshot(snap_name)
        self.assertTrue(ok_rb)

    def test_update_manager_apply_with_safety_snapshot(self):
        ok, report = self.updater.apply_all_updates(create_snapshot=True)
        self.assertTrue(ok)
        self.assertIsNotNone(report["snapshot_created"])

if __name__ == "__main__":
    unittest.main()
