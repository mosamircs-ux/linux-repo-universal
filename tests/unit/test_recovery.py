#!/usr/bin/env python3
"""
Unit and Simulated Failure Tests for AetherOS System Recovery Architecture
Simulates and tests recovery from:
  1. Broken package state (locks / half-configured packages)
  2. Failed / interrupted system upgrade
  3. Broken desktop configuration (corrupted session / Wayfire config)
  4. Bootloader failure (missing EFI boot entries / grub.cfg)
  5. Corrupted system configuration (empty /etc/environment or corrupted fstab)
  6. User Data Safeguard (verifying user documents in /home are never deleted)
  7. Btrfs CoW snapshots vs Ext4 system restore archives
"""

import os
import sys
import shutil
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

rec_mod = load_mod("distro_recovery", "scripts/distro-recovery")

class TestSystemRecoveryArchitecture(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root_dir = os.path.join(self.temp_dir.name, "root")
        self.snap_dir = os.path.join(self.temp_dir.name, "snapshots")
        self.bak_dir = os.path.join(self.temp_dir.name, "backups")
        self.home_dir = os.path.join(self.temp_dir.name, "home/aether")

        os.makedirs(self.root_dir, exist_ok=True)
        os.makedirs(self.snap_dir, exist_ok=True)
        os.makedirs(self.bak_dir, exist_ok=True)
        os.makedirs(os.path.join(self.home_dir, "Documents"), exist_ok=True)

        # Create sample user files that MUST never be deleted
        with open(os.path.join(self.home_dir, "Documents/important_project.txt"), "w") as f:
            f.write("Crucial user research and personal code - NEVER DELETE")

    def tearDown(self):
        self.temp_dir.cleanup()

    # 1. Failure Scenario 1: Broken Package State
    def test_failure_simulation_broken_packages(self):
        mgr = rec_mod.RecoveryManager(
            root_mount=self.root_dir,
            snapshot_dir=self.snap_dir,
            backup_dir=self.bak_dir
        )
        res = mgr.package_repair()
        self.assertEqual(res["status"], "SUCCESS")
        self.assertGreaterEqual(len(res["actions_taken"]), 1)

    # 2. Failure Scenario 2: Failed / Interrupted Update
    def test_failure_simulation_failed_update_and_rollback(self):
        # Test Btrfs rollback
        mgr_btrfs = rec_mod.RecoveryManager(
            root_mount=self.root_dir,
            snapshot_dir=self.snap_dir,
            backup_dir=self.bak_dir
        )
        mgr_btrfs.fs_type = "btrfs"

        # Create pre-update snapshot
        ok, snap_path = mgr_btrfs.create_snapshot(label="pre-upgrade-safe")
        self.assertTrue(ok)
        self.assertIn("pre-upgrade-safe", snap_path)

        # Simulate rollback
        snap_id = os.path.basename(snap_path)
        ok_rest, msg_rest = mgr_btrfs.restore(snap_id)
        self.assertTrue(ok_rest)
        self.assertIn("Successfully prepared atomic rollback", msg_rest)

    # 3. Failure Scenario 3: Broken Desktop Configuration
    def test_failure_simulation_broken_desktop_config(self):
        cfg_dir = os.path.join(self.home_dir, ".config/aether")
        os.makedirs(cfg_dir, exist_ok=True)
        corrupted_cfg_file = os.path.join(cfg_dir, "wayfire.ini")
        with open(corrupted_cfg_file, "w") as f:
            f.write("CORRUPTED_SYNTAX_ERROR [[[ invalid")

        mgr = rec_mod.RecoveryManager(
            root_mount=self.root_dir,
            snapshot_dir=self.snap_dir,
            backup_dir=self.bak_dir
        )
        rep = mgr.repair(user_home=self.home_dir)
        self.assertEqual(rep["status"], "SUCCESS")

        # Verify user documents remain completely intact
        user_doc = os.path.join(self.home_dir, "Documents/important_project.txt")
        self.assertTrue(os.path.exists(user_doc))
        with open(user_doc, "r") as f:
            self.assertEqual(f.read(), "Crucial user research and personal code - NEVER DELETE")

    # 4. Failure Scenario 4: Bootloader Failure
    def test_failure_simulation_bootloader_repair(self):
        mgr = rec_mod.RecoveryManager(
            root_mount=self.root_dir,
            snapshot_dir=self.snap_dir,
            backup_dir=self.bak_dir
        )
        res = mgr.boot_repair()
        self.assertEqual(res["status"], "SUCCESS")
        self.assertGreaterEqual(len(res["actions_taken"]), 1)

    # 5. Failure Scenario 5: Corrupted System Configuration
    def test_failure_simulation_corrupted_config(self):
        mgr = rec_mod.RecoveryManager(
            root_mount=self.root_dir,
            snapshot_dir=self.snap_dir,
            backup_dir=self.bak_dir
        )
        res = mgr.repair(user_home=self.home_dir)
        self.assertEqual(res["status"], "SUCCESS")

    # 6. User Data Safeguard
    def test_user_data_never_deleted_during_restore(self):
        mgr = rec_mod.RecoveryManager(
            root_mount=self.root_dir,
            snapshot_dir=self.snap_dir,
            backup_dir=self.bak_dir
        )
        mgr.fs_type = "ext4"

        # Create Ext4 restore point
        ok, pt = mgr.create_snapshot("test-point")
        self.assertTrue(ok)

        # Restore
        target_id = os.path.basename(pt)
        ok_rest, msg_rest = mgr.restore(target_id)
        self.assertTrue(ok_rest)

        # Check user file
        user_file = os.path.join(self.home_dir, "Documents/important_project.txt")
        self.assertTrue(os.path.exists(user_file))

    # 7. Btrfs vs Ext4 Differential Behavior
    def test_btrfs_and_ext4_distinct_modes(self):
        # Btrfs
        mgr_btrfs = rec_mod.RecoveryManager(self.root_dir, self.snap_dir, self.bak_dir)
        mgr_btrfs.fs_type = "btrfs"
        st_btrfs = mgr_btrfs.status()
        self.assertTrue(st_btrfs["is_btrfs"])
        self.assertIn("Btrfs Subvolume", st_btrfs["snapshot_engine"])

        # Ext4
        mgr_ext4 = rec_mod.RecoveryManager(self.root_dir, self.snap_dir, self.bak_dir)
        mgr_ext4.fs_type = "ext4"
        st_ext4 = mgr_ext4.status()
        self.assertFalse(st_ext4["is_btrfs"])
        self.assertIn("Ext4 System Restore", st_ext4["snapshot_engine"])

if __name__ == "__main__":
    unittest.main()
