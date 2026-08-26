#!/usr/bin/env python3
"""
AetherOS Reproducible Build Verifier
Verifies bit-for-bit reproducibility of ISO builds and package trees.
"""

import sys
import hashlib
import os

def check_file_hash(filepath: str, expected_hash: str) -> bool:
    if not os.path.exists(filepath):
        print(f"[-] File not found: {filepath}", file=sys.stderr)
        return False
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    actual_hash = h.hexdigest()
    if actual_hash.lower() == expected_hash.lower():
        print(f"[+] Hash match for {filepath}: {actual_hash}")
        return True
    else:
        print(f"[-] Hash mismatch for {filepath}!\n    Expected: {expected_hash}\n    Actual:   {actual_hash}", file=sys.stderr)
        return False

def main():
    print("=== AetherOS Reproducible Build Check ===")
    if len(sys.argv) < 2:
        print("Usage: reproducible-check.py <file> [expected_sha256]")
        sys.exit(0)
    target = sys.argv[1]
    expected = sys.argv[2] if len(sys.argv) > 2 else ""
    if expected:
        success = check_file_hash(target, expected)
        sys.exit(0 if success else 1)
    else:
        h = hashlib.sha256()
        with open(target, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        print(f"SHA256({target}) = {h.hexdigest()}")

if __name__ == "__main__":
    main()
