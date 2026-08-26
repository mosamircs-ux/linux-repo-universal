#!/usr/bin/env python3
"""
AetherOS Archive & Compression Engine
Compresses and extracts archive formats (.zip, .tar.gz, .tar.xz, .tar.zst, .tar, .7z) with progress reporting.
"""

import os
import sys
import zipfile
import tarfile
import shutil
import subprocess
from typing import List, Dict, Any, Optional, Callable

SUPPORTED_ARCHIVES = [
    ".zip", ".tar.gz", ".tgz", ".tar.xz", ".txz", ".tar.bz2", ".tbz2", ".tar.zst", ".tar", ".7z"
]

class ArchiveManager:
    @staticmethod
    def is_archive(filename: str) -> bool:
        lower = filename.lower()
        return any(lower.endswith(ext) for ext in SUPPORTED_ARCHIVES)

    @staticmethod
    def create_archive(sources: List[str], output_path: str, format_type: str = "zip", progress_callback: Optional[Callable[[int, int, str], None]] = None) -> bool:
        try:
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

            if format_type == "zip" or output_path.endswith(".zip"):
                with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
                    for src in sources:
                        if os.path.isfile(src):
                            zf.write(src, os.path.basename(src))
                        elif os.path.isdir(src):
                            base_name = os.path.basename(src.rstrip("/"))
                            for root, _, files in os.walk(src):
                                for f in files:
                                    fp = os.path.join(root, f)
                                    rel = os.path.relpath(fp, os.path.dirname(src.rstrip("/")))
                                    zf.write(fp, rel)
                return True

            elif format_type in ("tar.gz", "tgz") or output_path.endswith((".tar.gz", ".tgz")):
                with tarfile.open(output_path, "w:gz") as tf:
                    for src in sources:
                        tf.add(src, arcname=os.path.basename(src))
                return True

            elif format_type in ("tar.xz", "txz") or output_path.endswith((".tar.xz", ".txz")):
                with tarfile.open(output_path, "w:xz") as tf:
                    for src in sources:
                        tf.add(src, arcname=os.path.basename(src))
                return True

            elif format_type == "tar" or output_path.endswith(".tar"):
                with tarfile.open(output_path, "w") as tf:
                    for src in sources:
                        tf.add(src, arcname=os.path.basename(src))
                return True

        except Exception as e:
            print(f"[ArchiveManager] Error creating archive: {e}", file=sys.stderr)
            return False

        return False

    @staticmethod
    def extract_archive(archive_path: str, destination_dir: str, progress_callback: Optional[Callable[[int, int, str], None]] = None) -> bool:
        if not os.path.exists(archive_path):
            return False

        os.makedirs(destination_dir, exist_ok=True)
        lower = archive_path.lower()

        try:
            if lower.endswith(".zip"):
                with zipfile.ZipFile(archive_path, "r") as zf:
                    members = zf.infolist()
                    total = len(members)
                    for idx, member in enumerate(members):
                        zf.extract(member, destination_dir)
                        if progress_callback:
                            progress_callback(idx + 1, total, member.filename)
                return True

            elif lower.endswith((".tar.gz", ".tgz", ".tar.xz", ".txz", ".tar.bz2", ".tbz2", ".tar")):
                with tarfile.open(archive_path, "r:*") as tf:
                    members = tf.getmembers()
                    total = len(members)
                    for idx, member in enumerate(members):
                        tf.extract(member, destination_dir)
                        if progress_callback:
                            progress_callback(idx + 1, total, member.name)
                return True

            elif lower.endswith(".7z") and shutil.which("7z"):
                res = subprocess.run(["7z", "x", archive_path, f"-o{destination_dir}", "-y"], capture_output=True)
                return (res.returncode == 0)

        except Exception as e:
            print(f"[ArchiveManager] Error extracting archive: {e}", file=sys.stderr)
            return False

        return False
