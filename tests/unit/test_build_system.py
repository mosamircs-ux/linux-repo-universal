#!/usr/bin/env python3
"""
Unit Tests for AetherOS Build System Engine
Verifies version configuration, package manifests, rootfs assembly, squashfs builder,
checksum/signing engine, ISO validator, and reproducibility checker.
"""

import os
import sys
import unittest
import tempfile
import json
import shutil

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(REPO_ROOT, "build", "scripts"))

import version as ver_mod
import build_rootfs
import build_squashfs
import sign_artifacts
import validate_iso
import build_iso

class TestBuildSystem(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="aether-test-build-")

    def tearDown(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_version_config(self):
        cfg = ver_mod.load_version_config()
        self.assertEqual(cfg.get("name"), "AetherOS")
        self.assertEqual(cfg.get("codename"), "Solstice")
        self.assertEqual(cfg.get("version"), "1.0.0")
        self.assertIn("live", cfg.get("profiles", []))
        self.assertIn("installer", cfg.get("profiles", []))
        self.assertIn("development", cfg.get("profiles", []))
        self.assertIn("minimal", cfg.get("profiles", []))
        self.assertIn("x86_64", cfg.get("supported_architectures", []))
        self.assertIn("arm64", cfg.get("supported_architectures", []))

    def test_package_manifest_loading(self):
        for profile in ["live", "installer", "development", "minimal"]:
            pkgs = build_rootfs.load_profile_packages(profile)
            self.assertGreater(len(pkgs), 0, f"Profile {profile} has empty package list")
            self.assertIn("btrfs-progs", pkgs, f"Profile {profile} missing btrfs-progs")

    def test_rootfs_assembly_and_manifest(self):
        rootfs_target = os.path.join(self.temp_dir, "rootfs")
        manifest = build_rootfs.assemble_rootfs(
            target_dir=rootfs_target,
            profile="minimal",
            arch="x86_64",
            epoch=1700000000
        )
        self.assertEqual(manifest["profile"], "minimal")
        self.assertEqual(manifest["architecture"], "x86_64")
        self.assertTrue(os.path.exists(os.path.join(rootfs_target, "etc", "os-release")))
        self.assertTrue(os.path.exists(os.path.join(rootfs_target, "etc", "aether-manifest.json")))
        self.assertTrue(os.path.exists(os.path.join(rootfs_target, "etc", "packages.manifest")))

        # Check os-release contents
        with open(os.path.join(rootfs_target, "etc", "os-release"), "r") as f:
            content = f.read()
            self.assertIn("AetherOS", content)
            self.assertIn("minimal", content)

    def test_squashfs_generation(self):
        rootfs_target = os.path.join(self.temp_dir, "rootfs")
        build_rootfs.assemble_rootfs(rootfs_target, profile="minimal", epoch=1700000000)
        
        squash_dest = os.path.join(self.temp_dir, "filesystem.squashfs")
        digest = build_squashfs.build_squashfs(rootfs_target, squash_dest, epoch=1700000000)
        
        self.assertTrue(os.path.exists(squash_dest))
        self.assertGreater(os.path.getsize(squash_dest), 0)
        self.assertEqual(len(digest), 64)

    def test_sign_and_checksum_artifacts(self):
        test_file = os.path.join(self.temp_dir, "test-artifact.iso")
        with open(test_file, "wb") as f:
            f.write(b"SAMPLE_AETHEROS_ISO_PAYLOAD_FOR_TESTING\n")

        results = sign_artifacts.process_artifacts([test_file], target_dir=self.temp_dir, sign=True)
        self.assertIn("test-artifact.iso", results)
        self.assertTrue(os.path.exists(f"{test_file}.sha256"))
        self.assertTrue(os.path.exists(f"{test_file}.sha512"))
        self.assertTrue(os.path.exists(os.path.join(self.temp_dir, "SHA256SUMS")))
        self.assertTrue(os.path.exists(os.path.join(self.temp_dir, "SHA512SUMS")))

        # Verify
        self.assertTrue(sign_artifacts.verify_artifact(test_file))

    def test_iso_building_and_validation(self):
        out_iso = os.path.join(self.temp_dir, "dist", "aether-test.iso")
        builder = build_iso.AetherISOBuilder(
            profile="minimal",
            arch="x86_64",
            work_dir=os.path.join(self.temp_dir, "work"),
            output_iso=out_iso,
            dist_dir=os.path.join(self.temp_dir, "dist"),
            source_date_epoch=1700000000
        )
        built_iso = builder.build(sign=True, validate=True, clean=False)
        self.assertEqual(built_iso, out_iso)
        self.assertTrue(os.path.exists(out_iso))
        self.assertTrue(os.path.exists(f"{out_iso}.sha256"))
        
        # Validate metadata file
        meta_files = [f for f in os.listdir(os.path.join(self.temp_dir, "dist")) if f.endswith("-build-info.json")]
        self.assertEqual(len(meta_files), 1)
        with open(os.path.join(self.temp_dir, "dist", meta_files[0]), "r") as f:
            meta = json.load(f)
            self.assertEqual(meta["profile"], "minimal")
            self.assertEqual(meta["architecture"], "x86_64")
            self.assertEqual(meta["source_date_epoch"], 1700000000)

if __name__ == "__main__":
    unittest.main()
