#!/usr/bin/env python3
"""
AetherOS Reproducibility Verification Engine
Validates that two independent builds generated with the same SOURCE_DATE_EPOCH
yield bit-for-bit identical cryptographic checksums and identical filesystem structures.
"""

import os
import sys
import shutil
import hashlib
import argparse
import subprocess
import tempfile

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(REPO_ROOT, "build", "scripts"))
import version as ver_mod
import sign_artifacts

def compute_sha256(filepath: str) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

def verify_reproducibility(profile: str = "minimal", arch: str = "x86_64", epoch: int = 1700000000) -> bool:
    print(f"=== Running Reproducibility Test (Profile: {profile}, Arch: {arch}, Epoch: {epoch}) ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        build1_dir = os.path.join(temp_dir, "build1")
        build2_dir = os.path.join(temp_dir, "build2")
        iso1_path = os.path.join(temp_dir, "build1.iso")
        iso2_path = os.path.join(temp_dir, "build2.iso")
        
        build_script = os.path.join(REPO_ROOT, "build", "scripts", "build_iso.py")
        
        print("[Reproducibility] Executing Build Run 1...")
        cmd1 = [
            sys.executable, build_script,
            "--profile", profile,
            "--arch", arch,
            "--workdir", build1_dir,
            "--output", iso1_path,
            "--source-date-epoch", str(epoch),
            "--no-sign",
            "--no-validate"
        ]
        subprocess.run(cmd1, check=True, capture_output=True)
        hash1 = compute_sha256(iso1_path)
        print(f"[Reproducibility] Build 1 SHA256: {hash1}")

        print("[Reproducibility] Executing Build Run 2...")
        cmd2 = [
            sys.executable, build_script,
            "--profile", profile,
            "--arch", arch,
            "--workdir", build2_dir,
            "--output", iso2_path,
            "--source-date-epoch", str(epoch),
            "--no-sign",
            "--no-validate"
        ]
        subprocess.run(cmd2, check=True, capture_output=True)
        hash2 = compute_sha256(iso2_path)
        print(f"[Reproducibility] Build 2 SHA256: {hash2}")

        if hash1 == hash2:
            print("\n[+] SUCCESS: Bit-for-bit deterministic reproducibility verified!")
            print(f"    Identical SHA256: {hash1}")
            return True
        else:
            print("\n[-] FAILURE: Build output hashes differ!", file=sys.stderr)
            print(f"    Build 1: {hash1}", file=sys.stderr)
            print(f"    Build 2: {hash2}", file=sys.stderr)
            return False

def main():
    parser = argparse.ArgumentParser(description="AetherOS Reproducibility Checker")
    parser.add_argument("--profile", default="minimal", choices=["live", "installer", "development", "minimal"], help="Profile to test")
    parser.add_argument("--arch", default="x86_64", choices=["x86_64", "arm64"], help="Architecture to test")
    parser.add_argument("--epoch", type=int, default=1700000000, help="SOURCE_DATE_EPOCH to test")
    parser.add_argument("target_iso", nargs="?", help="Optional existing ISO file to verify against its .sha256")
    args = parser.parse_args()

    if args.target_iso:
        ok = sign_artifacts.verify_artifact(args.target_iso)
        sys.exit(0 if ok else 1)
    else:
        ok = verify_reproducibility(profile=args.profile, arch=args.arch, epoch=args.epoch)
        sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()
