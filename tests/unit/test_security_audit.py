#!/usr/bin/env python3
"""
Unit and Integration Tests for AetherOS Security Hardening & Audit Engine
Validates the 15-vector security audit inspector, kernel sysctl mitigations,
AppArmor profiles, Polkit rules, and SSH hardening configurations.
"""

import os
import sys
import unittest
import importlib.util

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO_ROOT)

from importlib.machinery import SourceFileLoader

def load_mod(name, rel_path):
    fpath = os.path.join(REPO_ROOT, rel_path)
    loader = SourceFileLoader(name, fpath)
    spec = importlib.util.spec_from_file_location(name, fpath, loader=loader)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

audit_mod = load_mod("distro_security_audit", "scripts/distro-security-audit")
SecurityAuditor = audit_mod.SecurityAuditor

class TestSecurityAudit(unittest.TestCase):
    def setUp(self):
        self.auditor = SecurityAuditor()

    def test_security_audit_15_vectors_present(self):
        rep = self.auditor.run_full_audit()
        self.assertEqual(len(rep["checks"]), 15)
        
        expected_keys = [
            "dangerous_permissions",
            "exposed_services",
            "weak_configuration",
            "unnecessary_listening_ports",
            "insecure_systemd_services",
            "suspicious_startup_entries",
            "modified_system_files",
            "package_integrity",
            "outdated_security_packages",
            "apparmor_status",
            "firewall_status",
            "ssh_configuration",
            "authentication_configuration",
            "suid_sgid_files",
            "world_writable_files",
        ]
        for k in expected_keys:
            self.assertIn(k, rep["checks"])
            check_data = rep["checks"][k]
            self.assertIn(check_data["status"], ("PASS", "WARN", "FAIL"))
            self.assertIsInstance(check_data["message"], str)

    def test_security_score_calculation(self):
        rep = self.auditor.run_full_audit()
        self.assertGreaterEqual(rep["score"], 80)
        self.assertIn(rep["grade"], ("A+", "A", "B"))
        self.assertEqual(rep["passed"] + rep["warnings"] + rep["failed"], 15)

    def test_kernel_sysctl_hardening_file(self):
        sysctl_fp = os.path.join(REPO_ROOT, "system/sysctl/99-aether-security.conf")
        self.assertTrue(os.path.exists(sysctl_fp))
        with open(sysctl_fp, "r") as f:
            content = f.read()

        self.assertIn("kernel.randomize_va_space = 2", content)
        self.assertIn("kernel.yama.ptrace_scope = 1", content)
        self.assertIn("kernel.kptr_restrict = 2", content)
        self.assertIn("kernel.dmesg_restrict = 1", content)
        self.assertIn("kernel.unprivileged_bpf_disabled = 1", content)
        self.assertIn("net.core.bpf_jit_harden = 2", content)
        self.assertIn("net.ipv4.tcp_syncookies = 1", content)
        self.assertIn("net.ipv4.conf.all.rp_filter = 1", content)
        self.assertIn("fs.protected_hardlinks = 1", content)
        self.assertIn("fs.protected_symlinks = 1", content)

    def test_apparmor_profiles_present(self):
        aa_dir = os.path.join(REPO_ROOT, "system/security/apparmor.d")
        self.assertTrue(os.path.exists(aa_dir))
        profiles = os.listdir(aa_dir)
        self.assertIn("usr.bin.aether-settings", profiles)
        self.assertIn("usr.bin.aether-files", profiles)
        self.assertIn("usr.bin.aether-software", profiles)
        self.assertIn("usr.bin.aether-updater", profiles)

        # Check content of a profile
        with open(os.path.join(aa_dir, "usr.bin.aether-settings"), "r") as f:
            aa_content = f.read()
            self.assertIn("/usr/bin/aether-settings", aa_content)
            self.assertIn("deny /etc/shadow* rw", aa_content)

    def test_polkit_least_privilege_rules(self):
        polkit_fp = os.path.join(REPO_ROOT, "system/polkit/10-aether-security.rules")
        self.assertTrue(os.path.exists(polkit_fp))
        with open(polkit_fp, "r") as f:
            content = f.read()
        self.assertIn("polkit.addRule", content)
        self.assertIn("org.freedesktop.NetworkManager.", content)
        self.assertIn("org.aetheros.settings.", content)

    def test_ssh_hardening_configuration(self):
        ssh_fp = os.path.join(REPO_ROOT, "system/ssh/99-aether-hardened.conf")
        self.assertTrue(os.path.exists(ssh_fp))
        with open(ssh_fp, "r") as f:
            content = f.read()
        self.assertIn("PermitRootLogin no", content)
        self.assertIn("MaxAuthTries 3", content)
        self.assertIn("X11Forwarding no", content)
        self.assertIn("chacha20-poly1305", content)

    def test_json_audit_output_schema(self):
        rep = self.auditor.run_full_audit()
        import json
        json_str = json.dumps(rep)
        self.assertIsInstance(json_str, str)
        parsed = json.loads(json_str)
        self.assertEqual(len(parsed["checks"]), 15)
        self.assertIn("score", parsed)
        self.assertIn("grade", parsed)

if __name__ == "__main__":
    unittest.main()
