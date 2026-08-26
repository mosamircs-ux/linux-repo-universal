#!/usr/bin/env python3
"""
Unit Tests for AetherOS Hardware Detection & Diagnostics Engine
Verifies that hardware detector correctly queries and structures CPU, RAM, GPU,
storage, network, audio, Bluetooth, displays, battery, kernel, and firmware data.
"""

import os
import sys
import unittest
import json
import subprocess

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(REPO_ROOT, "kernel"))
sys.path.insert(0, os.path.join(REPO_ROOT, "scripts"))

import hardware_detector

class TestHardwareDetector(unittest.TestCase):
    def setUp(self):
        self.detector = hardware_detector.HardwareDetector()

    def test_cpu_detection(self):
        cpu = self.detector.get_cpu_info()
        self.assertIsInstance(cpu, dict)
        self.assertIn("architecture", cpu)
        self.assertIn("threads", cpu)
        self.assertGreaterEqual(cpu["threads"], 1)
        self.assertIn("model", cpu)
        self.assertIn("vulnerabilities", cpu)

    def test_ram_detection(self):
        ram = self.detector.get_ram_info()
        self.assertIsInstance(ram, dict)
        self.assertIn("total_mb", ram)
        self.assertIn("free_mb", ram)
        self.assertIn("zram", ram)
        self.assertIsInstance(ram["zram"], dict)

    def test_gpu_detection(self):
        gpus = self.detector.get_gpu_info()
        self.assertIsInstance(gpus, list)
        self.assertGreaterEqual(len(gpus), 1)
        first_gpu = gpus[0]
        self.assertIn("card", first_gpu)
        self.assertIn("driver", first_gpu)
        self.assertIn("vendor", first_gpu)
        self.assertIn("connectors", first_gpu)

    def test_storage_detection(self):
        storage = self.detector.get_storage_info()
        self.assertIsInstance(storage, list)
        for s in storage:
            self.assertIn("device_path", s)
            self.assertIn("type", s)
            self.assertIn("size_gb", s)
            self.assertIn("trim_supported", s)

    def test_network_devices(self):
        nets = self.detector.get_network_devices()
        self.assertIsInstance(nets, list)
        for n in nets:
            self.assertIn("interface", n)
            self.assertIn("type", n)
            self.assertIn("operstate", n)

    def test_audio_info(self):
        audio = self.detector.get_audio_info()
        self.assertIsInstance(audio, dict)
        self.assertIn("server", audio)
        self.assertIn("PipeWire", audio["server"])
        self.assertIn("bluetooth_audio_codecs", audio)
        self.assertIn("LDAC", audio["bluetooth_audio_codecs"])

    def test_bluetooth_info(self):
        bt = self.detector.get_bluetooth_info()
        self.assertIsInstance(bt, dict)
        self.assertIn("available", bt)
        self.assertIn("adapters", bt)

    def test_displays_info(self):
        displays = self.detector.get_displays_info()
        self.assertIsInstance(displays, list)
        self.assertGreaterEqual(len(displays), 1)
        self.assertIn("connector", displays[0])
        self.assertIn("resolution", displays[0])

    def test_battery_and_power(self):
        power = self.detector.get_battery_and_power_info()
        self.assertIsInstance(power, dict)
        self.assertIn("has_battery", power)
        self.assertIn("ac_adapter_online", power)
        self.assertIn("thermal_zones", power)

    def test_firmware_status(self):
        fw = self.detector.get_firmware_status()
        self.assertIsInstance(fw, dict)
        self.assertIn("firmware_packages_installed", fw)
        self.assertIn("licensing", fw)

    def test_full_report_structure(self):
        report = self.detector.get_full_report()
        self.assertIsInstance(report, dict)
        required_keys = ["kernel", "cpu", "ram", "gpu", "storage", "network", "audio", "bluetooth", "displays", "battery_and_power", "loaded_drivers", "firmware"]
        for k in required_keys:
            self.assertIn(k, report)

    def test_distro_hardware_info_cli_json(self):
        cli_path = os.path.join(REPO_ROOT, "scripts", "distro-hardware-info")
        res = subprocess.run([sys.executable, cli_path, "--json"], capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f"CLI error: {res.stderr}")
        data = json.loads(res.stdout)
        self.assertIn("cpu", data)
        self.assertIn("gpu", data)
        self.assertIn("ram", data)

    def test_distro_hardware_info_cli_subsystem(self):
        cli_path = os.path.join(REPO_ROOT, "scripts", "distro-hardware-info")
        res = subprocess.run([sys.executable, cli_path, "--json", "--subsystem", "cpu"], capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f"CLI error: {res.stderr}")
        data = json.loads(res.stdout)
        self.assertIn("architecture", data)

    def test_distro_hardware_info_check_compatibility(self):
        cli_path = os.path.join(REPO_ROOT, "scripts", "distro-hardware-info")
        res = subprocess.run([sys.executable, cli_path, "--check-compatibility"], capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f"Compatibility check failed: {res.stderr}")
        self.assertIn("Compatibility Check SUCCESSFUL", res.stdout)

if __name__ == "__main__":
    unittest.main()
