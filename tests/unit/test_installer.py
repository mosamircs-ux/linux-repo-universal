#!/usr/bin/env python3
"""
Unit and Integration Tests for AetherOS Installer (aether-installer)
Validates disk/OS detection, Btrfs subvolumes, Ext4, LUKS encryption, LVM, Dual Boot,
pre-flight dry-run validation, destructive warnings, and 7-point post-install verification.
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

part_mod = load_mod("partitioner", "installer/src/engine/partitioner.py")
core_mod = load_mod("installer_core", "installer/src/engine/installer_core.py")
gui_mod = load_mod("installer_gui", "installer/src/gui/installer_gui.py")
ver_mod = load_mod("post_install_verifier", "installer/src/engine/post_install_verifier.py")

DiskDevice = part_mod.DiskDevice
PartitionPlan = part_mod.PartitionPlan
PartitionStrategy = part_mod.PartitionStrategy
scan_available_disks = part_mod.scan_available_disks
InstallConfig = core_mod.InstallConfig
AetherInstallerRunner = core_mod.AetherInstallerRunner
AetherInstallerWizardModel = gui_mod.AetherInstallerWizardModel
PostInstallVerifier = ver_mod.PostInstallVerifier

class TestInstaller(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.target_dir = self.temp_dir.name

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_disk_probing_and_os_detection(self):
        disks = scan_available_disks()
        self.assertIsInstance(disks, list)
        self.assertGreater(len(disks), 0)
        
        d0 = disks[0]
        self.assertIn("path", d0.to_dict())
        self.assertGreater(d0.size_gb, 0)
        self.assertIsInstance(d0.is_ssd, bool)

    def test_efi_btrfs_partition_plan(self):
        plan = PartitionPlan(
            target_disk="/dev/nvme0n1",
            strategy=PartitionStrategy.BTRFS_AUTO,
            is_efi=True
        )
        self.assertEqual(len(plan.partitions), 2)
        
        # ESP
        p1 = plan.partitions[0]
        self.assertEqual(p1["label"], "ESP")
        self.assertEqual(p1["fs_type"], "fat32")
        self.assertEqual(p1["mountpoint"], "/boot/efi")
        self.assertEqual(p1["size_mb"], 512)

        # Root Btrfs
        p2 = plan.partitions[1]
        self.assertEqual(p2["label"], "AetherRoot")
        self.assertEqual(p2["fs_type"], "btrfs")
        self.assertEqual(p2["mountpoint"], "/")

        # Subvolumes
        subvols = plan.get_btrfs_subvolumes()
        subvol_names = [s["name"] for s in subvols]
        self.assertIn("@", subvol_names)
        self.assertIn("@home", subvol_names)
        self.assertIn("@snapshots", subvol_names)
        self.assertIn("@var_log", subvol_names)

    def test_bios_ext4_partition_plan(self):
        plan = PartitionPlan(
            target_disk="/dev/sda",
            strategy=PartitionStrategy.EXT4_AUTO,
            is_efi=False,
            swap_size_mb=4096
        )
        self.assertEqual(len(plan.partitions), 3)

        # BIOS Boot
        self.assertEqual(plan.partitions[0]["label"], "BIOS-BOOT")
        self.assertEqual(plan.partitions[0]["size_mb"], 2)

        # Swap
        self.assertEqual(plan.partitions[1]["label"], "AetherSwap")
        self.assertEqual(plan.partitions[1]["fs_type"], "swap")

        # Root Ext4
        self.assertEqual(plan.partitions[2]["label"], "AetherRoot")
        self.assertEqual(plan.partitions[2]["fs_type"], "ext4")

    def test_encrypted_luks_partition_plan(self):
        plan = PartitionPlan(
            target_disk="/dev/nvme0n1",
            strategy=PartitionStrategy.ENCRYPTED_LUKS,
            is_efi=True,
            use_encryption=True,
            encryption_passphrase="SecretPassword123"
        )
        self.assertTrue(plan.partitions[1]["encrypted"])
        ok_val, errors = plan.validate_plan(512.0)
        self.assertTrue(ok_val)

    def test_separate_home_and_swap_plan(self):
        plan = PartitionPlan(
            target_disk="/dev/sda",
            strategy=PartitionStrategy.EXT4_AUTO,
            is_efi=True,
            separate_home=True,
            swap_size_mb=8192
        )
        mounts = [p["mountpoint"] for p in plan.partitions]
        self.assertIn("/boot/efi", mounts)
        self.assertIn("none", mounts)  # swap
        self.assertIn("/", mounts)
        self.assertIn("/home", mounts)

    def test_dry_run_plan_validation(self):
        # 1. Disk too small
        plan1 = PartitionPlan("/dev/sdb", PartitionStrategy.BTRFS_AUTO, is_efi=True)
        ok1, errors1 = plan1.validate_plan(disk_size_gb=10.0)
        self.assertFalse(ok1)
        self.assertTrue(any("smaller than minimum" in e for e in errors1))

        # 2. Missing encryption passphrase
        plan2 = PartitionPlan("/dev/nvme0n1", PartitionStrategy.ENCRYPTED_LUKS, is_efi=True, use_encryption=True, encryption_passphrase="")
        ok2, errors2 = plan2.validate_plan(disk_size_gb=128.0)
        self.assertFalse(ok2)
        self.assertTrue(any("passphrase" in e for e in errors2))

    def test_destructive_warning_generation(self):
        plan = PartitionPlan("/dev/nvme0n1", PartitionStrategy.BTRFS_AUTO, is_efi=True)
        warn = plan.get_destructive_warning()
        self.assertIn("WARNING", warn)
        self.assertIn("/dev/nvme0n1", warn)
        self.assertIn("ESP", warn)
        self.assertIn("AetherRoot", warn)
        self.assertIn("PERMANENTLY ERASED", warn)

    def test_installer_runner_progress(self):
        cfg = InstallConfig()
        cfg.target_disk = "/dev/sda"
        cfg.username = "testuser"
        cfg.hostname = "aether-test"

        runner = AetherInstallerRunner(cfg, target_mount=self.target_dir)
        progress_log = []

        def on_prog(pct, msg):
            progress_log.append((pct, msg))

        ok = runner.run_installation(progress_callback=on_prog)
        self.assertTrue(ok)
        self.assertGreaterEqual(len(progress_log), 7)
        self.assertEqual(progress_log[-1][0], 100)

        # Verify staged files
        self.assertTrue(os.path.exists(os.path.join(self.target_dir, "etc/fstab")))
        self.assertTrue(os.path.exists(os.path.join(self.target_dir, "etc/hostname")))
        self.assertTrue(os.path.exists(os.path.join(self.target_dir, "etc/passwd")))
        self.assertTrue(os.path.exists(os.path.join(self.target_dir, "boot/grub/grub.cfg")))

    def test_post_install_verification_all_7_checks(self):
        # Setup dummy target environment
        os.makedirs(os.path.join(self.target_dir, "boot/efi/EFI/AetherOS"), exist_ok=True)
        os.makedirs(os.path.join(self.target_dir, "boot/grub"), exist_ok=True)
        os.makedirs(os.path.join(self.target_dir, "etc/NetworkManager"), exist_ok=True)
        os.makedirs(os.path.join(self.target_dir, "etc/sudoers.d"), exist_ok=True)
        os.makedirs(os.path.join(self.target_dir, "usr/share/wayland-sessions"), exist_ok=True)
        
        with open(os.path.join(self.target_dir, "etc/fstab"), "w") as f:
            f.write("UUID=root / btrfs defaults 0 0\n")
        with open(os.path.join(self.target_dir, "etc/passwd"), "w") as f:
            f.write("aether:x:1000:1000:Aether User:/home/aether:/bin/bash\n")
        with open(os.path.join(self.target_dir, "boot/grub/grub.cfg"), "w") as f:
            f.write("menuentry 'AetherOS' { linux /vmlinuz }\n")

        res = PostInstallVerifier.verify_all(self.target_dir, username="aether", is_efi=True, use_btrfs=True)
        self.assertTrue(res["all_passed"])
        self.assertEqual(len(res["checks"]), 7)
        self.assertTrue(res["checks"]["bootloader"]["passed"])
        self.assertTrue(res["checks"]["root_filesystem"]["passed"])
        self.assertTrue(res["checks"]["essential_packages"]["passed"])
        self.assertTrue(res["checks"]["user_creation"]["passed"])
        self.assertTrue(res["checks"]["network"]["passed"])
        self.assertTrue(res["checks"]["desktop"]["passed"])
        self.assertTrue(res["checks"]["bootability"]["passed"])

    def test_bilingual_wizard_model_and_rtl(self):
        wizard = AetherInstallerWizardModel(language="en")
        self.assertFalse(wizard.is_rtl)
        self.assertIn("Page 1", wizard.get_summary_text())

        # Switch to Arabic RTL
        wizard.set_language("ar")
        self.assertTrue(wizard.is_rtl)
        self.assertEqual(wizard.config.language, "ar")
        self.assertEqual(wizard.config.keyboard_layout, "ara")

        # Step through pages
        self.assertEqual(wizard.next_page(), 1)
        self.assertEqual(wizard.next_page(), 2)
        self.assertEqual(wizard.prev_page(), 1)

if __name__ == "__main__":
    unittest.main()
