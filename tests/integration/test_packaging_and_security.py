#!/usr/bin/env python3
"""
Integration tests for AetherOS Debian Packaging, AppArmor, Polkit, and Sysctl configs
"""

import os
import sys
import unittest
import xml.etree.ElementTree as ET

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestPackagingAndSecurity(unittest.TestCase):
    def test_polkit_policy_xml(self):
        policy_path = os.path.join(REPO_ROOT, "system/polkit/org.aetheros.policy")
        self.assertTrue(os.path.exists(policy_path))
        tree = ET.parse(policy_path)
        root = tree.getroot()
        self.assertEqual(root.tag, "policyconfig")

        actions = root.findall("action")
        self.assertGreaterEqual(len(actions), 3)
        action_ids = [a.get("id") for a in actions]
        self.assertIn("org.aetheros.updater.check-and-apply", action_ids)
        self.assertIn("org.aetheros.snapshots.rollback", action_ids)

    def test_apparmor_profiles_exist(self):
        updater_profile = os.path.join(REPO_ROOT, "system/security/apparmor.d/usr.bin.aether-updater")
        crash_profile = os.path.join(REPO_ROOT, "system/security/apparmor.d/usr.bin.aether-crash-handler")
        self.assertTrue(os.path.exists(updater_profile))
        self.assertTrue(os.path.exists(crash_profile))

        with open(crash_profile, "r") as f:
            content = f.read()
            self.assertIn("deny network raw", content)

    def test_sysctl_performance_config(self):
        sysctl_path = os.path.join(REPO_ROOT, "kernel/sysctl.d/99-aether-performance.conf")
        self.assertTrue(os.path.exists(sysctl_path))
        with open(sysctl_path, "r") as f:
            content = f.read()
            self.assertIn("vm.swappiness = 15", content)
            self.assertIn("tcp_congestion_control = bbr", content)

    def test_debian_control_files(self):
        packages = ["aether-base", "aether-desktop-core", "aether-artwork", "aether-settings", "aether-installer"]
        for pkg in packages:
            ctrl = os.path.join(REPO_ROOT, f"packages/{pkg}/debian/control")
            self.assertTrue(os.path.exists(ctrl), f"Missing {ctrl}")
            with open(ctrl, "r") as f:
                txt = f.read()
                self.assertIn(f"Package: {pkg}", txt)
                self.assertIn("Maintainer:", txt)

if __name__ == "__main__":
    unittest.main()
