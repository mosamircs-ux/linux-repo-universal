#!/usr/bin/env python3
"""
Unit and Integration Tests for AetherOS Desktop Hardware Diagnostic Doctors
Validates diagnostics, scoring, actionable recommendations, and JSON formatting for:
  - Network Doctor (distro network-doctor)
  - Audio Doctor (distro audio-doctor)
  - Bluetooth Doctor (distro bluetooth-doctor)
  - Printer & Scanner Doctor (distro printer-doctor)
"""

import os
import sys
import json
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

net_mod = load_mod("distro_network_doctor", "scripts/distro-network-doctor")
aud_mod = load_mod("distro_audio_doctor", "scripts/distro-audio-doctor")
bt_mod = load_mod("distro_bluetooth_doctor", "scripts/distro-bluetooth-doctor")
prn_mod = load_mod("distro_printer_doctor", "scripts/distro-printer-doctor")

class TestHardwareDoctors(unittest.TestCase):

    # 1. Network Doctor
    def test_network_doctor(self):
        doc = net_mod.NetworkDoctor()
        rep = doc.run_diagnostics()
        self.assertEqual(rep["subsystem"], "Networking")
        self.assertEqual(len(rep["checks"]), 8)
        self.assertGreaterEqual(rep["score"], 80)
        self.assertIn(rep["grade"], ("A+", "A", "B"))
        self.assertEqual(rep["passed"] + rep["warnings"] + rep["failed"], 8)

        expected = [
            "daemon_status", "link_carrier", "ip_assignment",
            "gateway_reachability", "dns_resolution", "wifi_radio",
            "internet_connectivity", "proxy_configuration"
        ]
        for k in expected:
            self.assertIn(k, rep["checks"])
            self.assertIn(rep["checks"][k]["status"], ("PASS", "WARN", "FAIL"))

    # 2. Audio Doctor
    def test_audio_doctor(self):
        doc = aud_mod.AudioDoctor()
        rep = doc.run_diagnostics()
        self.assertEqual(rep["subsystem"], "Audio")
        self.assertEqual(len(rep["checks"]), 8)
        self.assertGreaterEqual(rep["score"], 80)
        self.assertIn(rep["grade"], ("A+", "A", "B"))

        expected = [
            "pipewire_daemon", "wireplumber", "pulse_compat",
            "alsa_cards", "default_sink", "default_source",
            "bluetooth_audio", "active_streams"
        ]
        for k in expected:
            self.assertIn(k, rep["checks"])
            self.assertIn(rep["checks"][k]["status"], ("PASS", "WARN", "FAIL"))

    # 3. Bluetooth Doctor
    def test_bluetooth_doctor(self):
        doc = bt_mod.BluetoothDoctor()
        rep = doc.run_diagnostics()
        self.assertEqual(rep["subsystem"], "Bluetooth")
        self.assertEqual(len(rep["checks"]), 8)
        self.assertGreaterEqual(rep["score"], 80)
        self.assertIn(rep["grade"], ("A+", "A", "B"))

        expected = [
            "daemon_status", "hci_adapter", "rfkill_status",
            "power_state", "paired_devices", "hid_input",
            "audio_profile", "obex_transfer"
        ]
        for k in expected:
            self.assertIn(k, rep["checks"])
            self.assertIn(rep["checks"][k]["status"], ("PASS", "WARN", "FAIL"))

    # 4. Printer Doctor
    def test_printer_doctor(self):
        doc = prn_mod.PrinterDoctor()
        rep = doc.run_diagnostics()
        self.assertEqual(rep["subsystem"], "Printing & Scanning")
        self.assertEqual(len(rep["checks"]), 8)
        self.assertGreaterEqual(rep["score"], 80)
        self.assertIn(rep["grade"], ("A+", "A", "B"))

        expected = [
            "cups_daemon", "avahi_mdns", "usb_printers",
            "network_printers", "print_queues", "sane_backend",
            "scanner_discovery", "pdf_virtual_printer"
        ]
        for k in expected:
            self.assertIn(k, rep["checks"])
            self.assertIn(rep["checks"][k]["status"], ("PASS", "WARN", "FAIL"))

    # 5. JSON Output Schema
    def test_doctor_json_output(self):
        doctors = [
            net_mod.NetworkDoctor(),
            aud_mod.AudioDoctor(),
            bt_mod.BluetoothDoctor(),
            prn_mod.PrinterDoctor()
        ]
        for doc in doctors:
            rep = doc.run_diagnostics()
            json_str = json.dumps(rep)
            parsed = json.loads(json_str)
            self.assertIn("score", parsed)
            self.assertIn("grade", parsed)
            self.assertIn("checks", parsed)
            self.assertIn("recommendations", parsed)

if __name__ == "__main__":
    unittest.main()
