#!/usr/bin/env python3
"""
Unit and Integration Tests for AetherOS Developer Workstation Layer (distro-dev)
Validates tool catalog, bundles resolution, installation/removal simulations,
doctor health diagnostics, environment variables, and CLI subcommands.
"""

import os
import sys
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

dev_mod = load_mod("distro_dev", "scripts/distro-dev")
TOOL_CATALOG = dev_mod.TOOL_CATALOG
BUNDLES = dev_mod.BUNDLES
DevWorkstationManager = dev_mod.DevWorkstationManager

class TestDevWorkstation(unittest.TestCase):
    def setUp(self):
        self.mgr = DevWorkstationManager()

    def test_catalog_contains_all_26_required_tools(self):
        required_tools = [
            "git", "gcc", "clang", "llvm", "make", "cmake", "ninja",
            "python", "nodejs", "npm", "pnpm", "rust", "go", "java", "php",
            "podman", "docker", "kubectl", "helm",
            "ssh", "openssl", "curl", "wget", "jq", "ripgrep", "fd", "tmux"
        ]
        for t in required_tools:
            self.assertIn(t, TOOL_CATALOG, f"Missing tool '{t}' in TOOL_CATALOG")
            self.assertIn("name", TOOL_CATALOG[t])
            self.assertIn("packages", TOOL_CATALOG[t])
            self.assertIn("binaries", TOOL_CATALOG[t])
            self.assertIn("version_cmd", TOOL_CATALOG[t])

    def test_bundle_definitions_and_resolution(self):
        self.assertIn("essentials", BUNDLES)
        self.assertIn("c-cpp", BUNDLES)
        self.assertIn("web", BUNDLES)
        self.assertIn("containers", BUNDLES)
        self.assertIn("cloud", BUNDLES)
        self.assertIn("all", BUNDLES)

        # Test bundle resolution
        res_cpp = self.mgr.resolve_targets(["c-cpp"])
        self.assertIn("gcc", res_cpp)
        self.assertIn("clang", res_cpp)
        self.assertIn("cmake", res_cpp)
        self.assertIn("ninja", res_cpp)

        res_web = self.mgr.resolve_targets(["web"])
        self.assertIn("nodejs", res_web)
        self.assertIn("npm", res_web)
        self.assertIn("pnpm", res_web)

        res_mixed = self.mgr.resolve_targets(["rust", "go", "cloud"])
        self.assertIn("rust", res_mixed)
        self.assertIn("go", res_mixed)
        self.assertIn("kubectl", res_mixed)
        self.assertIn("helm", res_mixed)

    def test_doctor_diagnostic_report(self):
        rep = self.mgr.doctor()
        self.assertIsInstance(rep, dict)
        self.assertEqual(rep["total_tools"], len(TOOL_CATALOG))
        self.assertIsInstance(rep["installed_count"], int)
        self.assertIsInstance(rep["coverage_pct"], float)
        self.assertGreaterEqual(len(rep["tools"]), 26)
        self.assertIn("environment", rep)
        self.assertIn("GOPATH", rep["environment"])
        self.assertIn("CARGO_HOME", rep["environment"])

    def test_dry_run_install_and_remove(self):
        # Dry-run install
        ok_inst = self.mgr.install(["c-cpp", "web", "rust"], dry_run=True)
        self.assertTrue(ok_inst)

        # Dry-run remove
        ok_rem = self.mgr.remove(["php", "java"], dry_run=True)
        self.assertTrue(ok_rem)

        # Dry-run update
        ok_upd = self.mgr.update(["essentials"], dry_run=True)
        self.assertTrue(ok_upd)

if __name__ == "__main__":
    unittest.main()
