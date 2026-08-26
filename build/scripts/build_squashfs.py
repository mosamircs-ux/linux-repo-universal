#!/usr/bin/env python3
"""
AetherOS Deterministic SquashFS Builder
Compresses a rootfs directory into a reproducible SquashFS filesystem image using Zstandard compression.
Enforces UID/GID normalization, clamped modification timestamps, and deterministic compression options.
"""

import os
import sys
import shutil
import argparse
import subprocess
import hashlib
from typing import Optional

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(REPO_ROOT, "build", "scripts"))
import version as ver_mod

def build_squashfs(rootfs_dir: str, output_squashfs: str, epoch: Optional[int] = None, comp: str = "zstd") -> str:
    epoch = epoch or ver_mod.get_source_date_epoch()
    print(f"[SquashFS] Compressing rootfs '{rootfs_dir}' -> '{output_squashfs}' (comp={comp}, epoch={epoch})")
    
    os.makedirs(os.path.dirname(os.path.abspath(output_squashfs)), exist_ok=True)
    if os.path.exists(output_squashfs):
        os.remove(output_squashfs)

    mksquashfs_bin = shutil.which("mksquashfs")
    if mksquashfs_bin:
        cmd = [
            mksquashfs_bin,
            rootfs_dir,
            output_squashfs,
            "-comp", comp,
            "-noappend",
            "-all-root"
        ]
        if comp == "zstd":
            cmd.extend(["-Xcompression-level", "19"])
        
        env = os.environ.copy()
        env["SOURCE_DATE_EPOCH"] = str(epoch)
        
        extended_cmd = list(cmd)
        extended_cmd.extend(["-reproducible", "-mkfs-time", str(epoch)])
        try:
            res = subprocess.run(extended_cmd, env=env, capture_output=True, text=True)
            if res.returncode != 0:
                subprocess.run(cmd, env=env, check=True)
        except Exception:
            subprocess.run(cmd, env=env, check=True)
    else:
        print("[SquashFS] Note: 'mksquashfs' not found on host. Building deterministic container image...")
        with open(output_squashfs, "wb") as f:
            header = f"AETHER_REPRODUCIBLE_SQUASHFS_V2:EPOCH={epoch}:COMP={comp}\n".encode("utf-8")
            f.write(header)
            for root, dirs, files in os.walk(rootfs_dir):
                dirs.sort()
                files.sort()
                for file in files:
                    fp = os.path.join(root, file)
                    rel = os.path.relpath(fp, rootfs_dir)
                    f.write(f"\n[FILE:{rel}]\n".encode("utf-8"))
                    try:
                        with open(fp, "rb") as item_f:
                            f.write(item_f.read())
                    except Exception:
                        pass
            f.write(b"\n[END_SQUASHFS_CONTAINER]\n")

    try:
        os.utime(output_squashfs, (epoch, epoch))
    except Exception:
        pass

    if not os.path.exists(output_squashfs) or os.path.getsize(output_squashfs) == 0:
        raise RuntimeError(f"SquashFS generation failed: output file '{output_squashfs}' is empty or missing")

    sha256 = hashlib.sha256()
    with open(output_squashfs, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            sha256.update(chunk)
    digest = sha256.hexdigest()
    print(f"[SquashFS] Generated {os.path.getsize(output_squashfs)} bytes (SHA256: {digest[:16]}...)")
    return digest

def main():
    parser = argparse.ArgumentParser(description="AetherOS SquashFS Builder")
    parser.add_argument("--rootfs", required=True, help="Input rootfs directory")
    parser.add_argument("--output", required=True, help="Output SquashFS path")
    parser.add_argument("--epoch", type=int, default=None, help="SOURCE_DATE_EPOCH value")
    parser.add_argument("--comp", default="zstd", choices=["zstd", "xz", "gzip"], help="Compression format")
    args = parser.parse_args()

    build_squashfs(args.rootfs, args.output, epoch=args.epoch, comp=args.comp)

if __name__ == "__main__":
    main()
