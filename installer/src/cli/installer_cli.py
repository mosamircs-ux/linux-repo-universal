#!/usr/bin/env python3
"""
AetherOS Unattended and Headless CLI Installer
Allows rapid deployment, VM provisioning, and automated script installations.
"""

import sys
import argparse
from installer.src.engine.installer_core import InstallConfig, AetherInstallerRunner

def main():
    parser = argparse.ArgumentParser(description="AetherOS Unattended CLI Installer")
    parser.add_argument("--disk", default="/dev/sda", help="Target disk block device")
    parser.add_argument("--btrfs", action="store_true", default=True, help="Use Btrfs filesystem with subvolumes")
    parser.add_argument("--username", default="aether", help="Initial user username")
    parser.add_argument("--hostname", default="aether-pc", help="System hostname")
    parser.add_argument("--locale", default="en_US.UTF-8", help="System locale")
    args = parser.parse_args()

    cfg = InstallConfig()
    cfg.target_disk = args.disk
    cfg.use_btrfs = args.btrfs
    cfg.username = args.username
    cfg.hostname = args.hostname
    cfg.locale = args.locale

    print("=== AetherOS CLI Installer ===")
    runner = AetherInstallerRunner(cfg)
    runner.run_installation()
    print("=== Installation Completed Successfully ===")

if __name__ == "__main__":
    main()
