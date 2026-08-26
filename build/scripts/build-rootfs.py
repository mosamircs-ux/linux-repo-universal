#!/usr/bin/env python3
"""
AetherOS RootFS Assembler
Prepares the target root directory structure, copies first-party files,
configures defaults for users, networking, and systemd units.
"""

import os
import sys
import shutil
import argparse
import subprocess

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def assemble_rootfs(target_dir: str) -> bool:
    print(f"[RootFS] Assembling AetherOS root filesystem into: {target_dir}")
    os.makedirs(target_dir, exist_ok=True)
    
    # 1. Create standard Linux directory tree
    for d in ["bin", "sbin", "usr/bin", "usr/sbin", "usr/lib", "usr/share", "etc", "var", "tmp", "proc", "sys", "dev", "run", "boot/efi", "home", "root"]:
        os.makedirs(os.path.join(target_dir, d), exist_ok=True)
        
    # 2. Copy AetherOS /system configurations
    sys_src = os.path.join(REPO_ROOT, "system")
    if os.path.exists(sys_src):
        print("[RootFS] Installing /system configs...")
        # systemd zram generator
        zram_dest = os.path.join(target_dir, "etc/systemd")
        os.makedirs(zram_dest, exist_ok=True)
        shutil.copy(os.path.join(sys_src, "systemd/zram-generator.conf"), zram_dest)
        
        # polkit
        polkit_dest = os.path.join(target_dir, "usr/share/polkit-1/actions")
        os.makedirs(polkit_dest, exist_ok=True)
        shutil.copy(os.path.join(sys_src, "polkit/org.aetheros.policy"), polkit_dest)
        
        # pipewire
        pw_dest = os.path.join(target_dir, "etc/pipewire/pipewire.conf.d")
        os.makedirs(pw_dest, exist_ok=True)
        shutil.copy(os.path.join(sys_src, "pipewire/pipewire.conf.d/10-aether-audio.conf"), pw_dest)

    # 3. Copy AetherOS /kernel optimizations
    kernel_src = os.path.join(REPO_ROOT, "kernel")
    if os.path.exists(kernel_src):
        print("[RootFS] Installing kernel sysctl and module configs...")
        sysctl_dest = os.path.join(target_dir, "etc/sysctl.d")
        os.makedirs(sysctl_dest, exist_ok=True)
        shutil.copy(os.path.join(kernel_src, "sysctl.d/99-aether-performance.conf"), sysctl_dest)

    # 4. Copy AetherOS /themes & artwork
    themes_src = os.path.join(REPO_ROOT, "themes")
    if os.path.exists(themes_src):
        print("[RootFS] Installing themes and wallpapers...")
        wall_dest = os.path.join(target_dir, "usr/share/backgrounds/aether")
        os.makedirs(wall_dest, exist_ok=True)
        shutil.copy(os.path.join(themes_src, "artwork/wallpaper-solstice-dark.svg"), wall_dest)

    # 5. Create /etc/os-release
    with open(os.path.join(target_dir, "etc/os-release"), "w", encoding="utf-8") as f:
        f.write("""NAME="AetherOS"
VERSION="1.0.0 LTS (Solstice)"
ID=aetheros
ID_LIKE="ubuntu debian"
PRETTY_NAME="AetherOS 1.0.0 LTS (Solstice)"
VERSION_ID="1.0.0"
HOME_URL="https://aetheros.org"
SUPPORT_URL="https://aetheros.org/support"
BUG_REPORT_URL="https://github.com/aetheros/aetheros/issues"
PRIVACY_POLICY_URL="https://aetheros.org/privacy"
UBUNTU_CODENAME=noble
""")

    print("[RootFS] Root filesystem assembly completed successfully.")
    return True

def main():
    parser = argparse.ArgumentParser(description="AetherOS RootFS Builder")
    parser.add_argument("--output", default="/tmp/aether-rootfs", help="Target rootfs directory")
    args = parser.parse_args()
    assemble_rootfs(args.output)

if __name__ == "__main__":
    main()
