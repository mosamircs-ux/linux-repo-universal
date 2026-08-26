#!/usr/bin/env python3
"""
Unit tests for AetherOS Installer Partitioning and Runner Subsystems
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from installer.src.engine.partitioner import PartitionPlan, scan_available_disks
from installer.src.engine.installer_core import InstallConfig, AetherInstallerRunner

class TestInstaller(unittest.TestCase):
    def test_efi_btrfs_partition_plan(self):
        plan = PartitionPlan(target_disk="/dev/nvme0n1", use_btrfs=True, is_efi=True)
        self.assertEqual(len(plan.partitions), 2)
        
        # Partition 1: ESP
        esp = plan.partitions[0]
        self.assertEqual(esp["fs_type"], "fat32")
        self.assertEqual(esp["mountpoint"], "/boot/efi")
        self.assertIn("boot", esp["flags"])
        self.assertIn("esp", esp["flags"])

        # Partition 2: Btrfs Root
        root = plan.partitions[1]
        self.assertEqual(root["fs_type"], "btrfs")
        self.assertEqual(root["mountpoint"], "/")

        # Subvolumes check
        subvols = plan.get_btrfs_subvolumes()
        self.assertEqual(len(subvols), 4)
        sub_names = [s["name"] for s in subvols]
        self.assertIn("@", sub_names)
        self.assertIn("@home", sub_names)
        self.assertIn("@snapshots", sub_names)
        self.assertIn("@var_log", sub_names)

    def test_bios_ext4_partition_plan(self):
        plan = PartitionPlan(target_disk="/dev/sda", use_btrfs=False, is_efi=False)
        self.assertEqual(len(plan.partitions), 2)
        bios_boot = plan.partitions[0]
        self.assertIn("bios_grub", bios_boot["flags"])
        root = plan.partitions[1]
        self.assertEqual(root["fs_type"], "ext4")
        self.assertEqual(len(plan.get_btrfs_subvolumes()), 0)

    def test_installer_runner_progress(self):
        cfg = InstallConfig()
        cfg.target_disk = "/dev/vda"
        runner = AetherInstallerRunner(cfg)
        
        progress_events = []
        def on_progress(p, msg):
            progress_events.append((p, msg))

        success = runner.run_installation(progress_callback=on_progress)
        self.assertTrue(success)
        self.assertEqual(len(progress_events), 7)
        self.assertEqual(progress_events[-1][0], 100)

if __name__ == "__main__":
    unittest.main()
