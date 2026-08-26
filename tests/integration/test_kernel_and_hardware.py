#!/usr/bin/env python3
"""
Integration Tests for Kernel, Drivers, Modprobe, UDev, and Upstream Firmware
Verifies system hardware configs, udev rules, modprobe driver options, and firmware integration.
"""

import os
import sys
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestKernelAndHardware(unittest.TestCase):
    def test_modprobe_configurations(self):
        modprobe_dir = os.path.join(REPO_ROOT, "kernel", "modprobe.d")
        self.assertTrue(os.path.isdir(modprobe_dir))
        
        gpu_conf = os.path.join(modprobe_dir, "50-aether-gpu.conf")
        power_conf = os.path.join(modprobe_dir, "50-aether-power.conf")
        storage_conf = os.path.join(modprobe_dir, "50-aether-storage.conf")
        
        self.assertTrue(os.path.exists(gpu_conf))
        self.assertTrue(os.path.exists(power_conf))
        self.assertTrue(os.path.exists(storage_conf))

        with open(gpu_conf, "r") as f:
            content = f.read()
            self.assertIn("i915 enable_guc=3", content)
            self.assertIn("amdgpu ppfeaturemask", content)
            self.assertIn("nouveau modeset=1", content)

        with open(power_conf, "r") as f:
            content = f.read()
            self.assertIn("snd_hda_intel power_save=1", content)
            self.assertIn("iwlwifi power_save=1", content)

        with open(storage_conf, "r") as f:
            content = f.read()
            self.assertIn("nvme_core default_ps_max_latency_us=0", content)

    def test_modules_load_configuration(self):
        mod_conf = os.path.join(REPO_ROOT, "kernel", "modules-load.d", "aether-modules.conf")
        self.assertTrue(os.path.exists(mod_conf))
        
        with open(mod_conf, "r") as f:
            content = f.read()
            required_modules = ["zram", "btrfs", "nvme", "ahci", "uas", "hid_multitouch", "xpad", "wacom", "btusb", "snd_hda_intel"]
            for mod in required_modules:
                self.assertIn(mod, content, f"Module {mod} missing from aether-modules.conf")

    def test_udev_hardware_rules(self):
        udev_file = os.path.join(REPO_ROOT, "system", "udev", "99-aether-hardware.rules")
        self.assertTrue(os.path.exists(udev_file))
        
        with open(udev_file, "r") as f:
            content = f.read()
            # Backlight / brightness
            self.assertIn("SUBSYSTEM==\"backlight\"", content)
            # Render nodes
            self.assertIn("KERNEL==\"renderD*\"", content)
            # DualShock / DualSense / Xbox / Nintendo / Steam controllers
            self.assertIn("054c", content) # Sony
            self.assertIn("045e", content) # Microsoft
            self.assertIn("057e", content) # Nintendo
            self.assertIn("28de", content) # Valve Steam
            # Drawing tablets
            self.assertIn("ID_INPUT_TABLET", content)
            # IPP-USB driverless printing
            self.assertIn("ipp-usb", content)
            # Scanner SANE
            self.assertIn("libsane_matched", content)
            # USB-C DisplayPort / Type-C
            self.assertIn("SUBSYSTEM==\"typec\"", content)

    def test_firmware_dependencies_in_packages(self):
        control_file = os.path.join(REPO_ROOT, "packages", "aether-base", "debian", "control")
        self.assertTrue(os.path.exists(control_file))
        
        with open(control_file, "r") as f:
            content = f.read()
            self.assertIn("linux-firmware", content)
            self.assertIn("intel-microcode", content)
            self.assertIn("amd64-microcode", content)
            self.assertIn("sof-firmware", content)
            self.assertIn("wireless-regdb", content)
            self.assertIn("upower", content)
            self.assertIn("ipp-usb", content)
            self.assertIn("sane-airscan", content)

if __name__ == "__main__":
    unittest.main()
