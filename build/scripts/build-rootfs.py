#!/usr/bin/env python3
"""
AetherOS Modular RootFS Assembler
Prepares the target root directory structure for specific profiles (live, installer, development, minimal),
stages kernel and system configurations, normalizes permissions and timestamps for reproducible builds,
and outputs package manifests and OS release files.
"""

import os
import sys
import shutil
import argparse
import json
from pathlib import Path
from typing import List, Dict, Any

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(REPO_ROOT, "build", "scripts"))
import version as ver_mod

def load_profile_packages(profile: str) -> List[str]:
    list_path = os.path.join(REPO_ROOT, "build", "config", f"packages-{profile}.list")
    if not os.path.exists(list_path):
        list_path = os.path.join(REPO_ROOT, "build", "config", "packages.list")
    
    packages = []
    if os.path.exists(list_path):
        with open(list_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    packages.append(line)
    return sorted(list(set(packages)))

def assemble_rootfs(target_dir: str, profile: str = "live", arch: str = "x86_64", epoch: int = 1700000000) -> Dict[str, Any]:
    print(f"[RootFS] Assembling AetherOS rootfs: profile={profile}, arch={arch} into '{target_dir}'")
    os.makedirs(target_dir, exist_ok=True)
    
    # 1. Standard Linux FHS directory hierarchy
    fhs_dirs = [
        "bin", "sbin", "usr/bin", "usr/sbin", "usr/lib", "usr/share",
        "usr/local/bin", "usr/local/sbin", "usr/local/share",
        "etc", "etc/systemd", "etc/sysctl.d", "etc/modules-load.d",
        "var", "var/log", "var/lib", "var/cache", "var/tmp",
        "tmp", "proc", "sys", "dev", "run", "boot", "boot/efi",
        "home", "root", "mnt", "media", "opt", "srv"
    ]
    for d in fhs_dirs:
        os.makedirs(os.path.join(target_dir, d), exist_ok=True)

    # 2. System configurations
    sys_src = os.path.join(REPO_ROOT, "system")
    if os.path.exists(sys_src):
        print("[RootFS] Staging system configurations...")
        # zram-generator
        zram_dest = os.path.join(target_dir, "etc/systemd")
        os.makedirs(zram_dest, exist_ok=True)
        zram_src = os.path.join(sys_src, "systemd/zram-generator.conf")
        if os.path.exists(zram_src):
            shutil.copy2(zram_src, zram_dest)

        # polkit
        polkit_dest = os.path.join(target_dir, "usr/share/polkit-1/actions")
        os.makedirs(polkit_dest, exist_ok=True)
        polkit_src = os.path.join(sys_src, "polkit/org.aetheros.policy")
        if os.path.exists(polkit_src):
            shutil.copy2(polkit_src, polkit_dest)

        # pipewire (if not minimal)
        if profile != "minimal":
            pw_dest = os.path.join(target_dir, "etc/pipewire/pipewire.conf.d")
            os.makedirs(pw_dest, exist_ok=True)
            pw_src = os.path.join(sys_src, "pipewire/pipewire.conf.d/10-aether-audio.conf")
            if os.path.exists(pw_src):
                shutil.copy2(pw_src, pw_dest)

        # AppArmor security profiles
        sec_dest = os.path.join(target_dir, "etc/apparmor.d")
        os.makedirs(sec_dest, exist_ok=True)
        sec_src = os.path.join(sys_src, "security")
        if os.path.exists(sec_src):
            for item in os.listdir(sec_src):
                s_fp = os.path.join(sec_src, item)
                if os.path.isfile(s_fp):
                    shutil.copy2(s_fp, sec_dest)

    # 3. Kernel optimizations
    kernel_src = os.path.join(REPO_ROOT, "kernel")
    if os.path.exists(kernel_src):
        print("[RootFS] Staging kernel optimizations...")
        sysctl_dest = os.path.join(target_dir, "etc/sysctl.d")
        os.makedirs(sysctl_dest, exist_ok=True)
        sysctl_src = os.path.join(kernel_src, "sysctl.d/99-aether-performance.conf")
        if os.path.exists(sysctl_src):
            shutil.copy2(sysctl_src, sysctl_dest)

    # 4. Themes, Artwork, Fonts (for GUI profiles)
    if profile in ("live", "development", "installer"):
        themes_src = os.path.join(REPO_ROOT, "themes")
        if os.path.exists(themes_src):
            print("[RootFS] Staging desktop artwork and themes...")
            bg_dest = os.path.join(target_dir, "usr/share/backgrounds/aether")
            os.makedirs(bg_dest, exist_ok=True)
            for wall in ["wallpaper-solstice-dark.svg", "wallpaper-solstice-light.svg", "logo.svg"]:
                w_src = os.path.join(themes_src, "artwork", wall)
                if os.path.exists(w_src):
                    shutil.copy2(w_src, bg_dest)

    # 5. Profile-specific flags and desktop files
    if profile == "installer":
        # Create installer autostart flag
        autostart_dir = os.path.join(target_dir, "etc/xdg/autostart")
        os.makedirs(autostart_dir, exist_ok=True)
        with open(os.path.join(autostart_dir, "aether-installer-live.desktop"), "w", encoding="utf-8") as f:
            f.write("[Desktop Entry]\nType=Application\nName=AetherOS Installer\nExec=aether-installer --gui\nHidden=false\nNoDisplay=false\nX-GNOME-Autostart-enabled=true\n")

    # 6. Generate /etc/os-release and version metadata
    cfg = ver_mod.load_version_config()
    dist_name = cfg.get("name", "AetherOS")
    ver_str = cfg.get("version", "1.0.0")
    codename = cfg.get("codename", "Solstice")
    channel = cfg.get("release_channel", "LTS")
    
    os_release_content = f"""NAME="{dist_name}"
VERSION="{ver_str} {channel} ({codename}) - {profile.capitalize()}"
ID=aetheros
ID_LIKE="ubuntu debian"
PRETTY_NAME="{dist_name} {ver_str} {channel} ({codename}) [{profile}]"
VERSION_ID="{ver_str}"
VARIANT="{profile}"
VARIANT_ID="{profile}"
ARCH="{arch}"
HOME_URL="{cfg.get('url', 'https://aetheros.org')}"
BUG_REPORT_URL="{cfg.get('bug_report_url', 'https://github.com/aetheros/aetheros/issues')}"
BUILD_ID="{ver_mod.get_git_commit()}"
SOURCE_DATE_EPOCH="{epoch}"
"""
    with open(os.path.join(target_dir, "etc", "os-release"), "w", encoding="utf-8") as f:
        f.write(os_release_content)

    # 7. Package Manifest Generation
    packages = load_profile_packages(profile)
    manifest_data = {
        "distribution": dist_name,
        "version": ver_str,
        "codename": codename,
        "profile": profile,
        "architecture": arch,
        "source_date_epoch": epoch,
        "git_commit": ver_mod.get_git_commit(),
        "packages_count": len(packages),
        "packages": packages
    }
    
    # Write /etc/aether-manifest.json
    with open(os.path.join(target_dir, "etc", "aether-manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2, sort_keys=True)
        f.write("\n")

    # Write /etc/packages.manifest (plain list)
    with open(os.path.join(target_dir, "etc", "packages.manifest"), "w", encoding="utf-8") as f:
        for pkg in packages:
            f.write(f"{pkg}\n")

    # 8. Deterministic normalization of timestamps and permissions
    print(f"[RootFS] Normalizing permissions and clamping timestamps to epoch {epoch}...")
    for root, dirs, files in os.walk(target_dir):
        # Sort dirs in place for deterministic walk order
        dirs.sort()
        files.sort()
        for d in dirs:
            d_path = os.path.join(root, d)
            try:
                os.chmod(d_path, 0o755)
                os.utime(d_path, (epoch, epoch))
            except Exception:
                pass
        for file in files:
            f_path = os.path.join(root, file)
            try:
                # Keep executable bit if file is in bin/sbin or starts with #!
                is_exec = False
                if "bin" in f_path.split(os.sep) or "sbin" in f_path.split(os.sep):
                    is_exec = True
                else:
                    try:
                        with open(f_path, "rb") as test_f:
                            if test_f.read(2) == b"#!":
                                is_exec = True
                    except Exception:
                        pass
                os.chmod(f_path, 0o755 if is_exec else 0o644)
                os.utime(f_path, (epoch, epoch))
            except Exception:
                pass

    print(f"[RootFS] Assembly complete for profile '{profile}' ({len(packages)} packages).")
    return manifest_data

def main():
    parser = argparse.ArgumentParser(description="AetherOS RootFS Assembler")
    parser.add_argument("--output", default="/tmp/aether-rootfs", help="Target rootfs directory")
    parser.add_argument("--profile", default="live", choices=["live", "installer", "development", "minimal"], help="Target profile")
    parser.add_argument("--arch", default="x86_64", choices=["x86_64", "arm64"], help="Target architecture")
    parser.add_argument("--source-date-epoch", type=int, default=None, help="Deterministic timestamp")
    args = parser.parse_args()

    epoch = args.source_date_epoch or ver_mod.get_source_date_epoch()
    manifest = assemble_rootfs(args.output, profile=args.profile, arch=args.arch, epoch=epoch)
    print(f"[RootFS] Successfully created rootfs manifest with {manifest['packages_count']} packages.")

if __name__ == "__main__":
    main()
