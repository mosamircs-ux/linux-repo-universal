#!/usr/bin/env python3
"""
AetherOS Package Builder & Linter
Builds and validates Debian packages for aether-base, aether-desktop-core,
aether-artwork, aether-settings, and aether-installer.
"""

import os
import sys
import glob
import shutil
import subprocess

PACKAGES_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(PACKAGES_DIR, "output")

def validate_package(pkg_name: str) -> bool:
    pkg_path = os.path.join(PACKAGES_DIR, pkg_name)
    control_file = os.path.join(pkg_path, "debian", "control")
    
    if not os.path.exists(control_file):
        print(f"[-] Missing control file for {pkg_name}", file=sys.stderr)
        return False
        
    with open(control_file, "r", encoding="utf-8") as f:
        content = f.read()
        
    required_fields = ["Package:", "Maintainer:", "Description:"]
    for req in required_fields:
        if req not in content:
            print(f"[-] Package {pkg_name} missing required field '{req}'", file=sys.stderr)
            return False
            
    print(f"[+] Package specification verified: {pkg_name}")
    return True

def main():
    print("=== AetherOS Package Build & Validation ===")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    packages = ["aether-base", "aether-desktop-core", "aether-artwork", "aether-settings", "aether-installer"]
    all_passed = True
    
    for pkg in packages:
        if not validate_package(pkg):
            all_passed = False
            
    if all_passed:
        print("=== All package recipes validated successfully ===")
        sys.exit(0)
    else:
        print("=== Package validation failed ===", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
