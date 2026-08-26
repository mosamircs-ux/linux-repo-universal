#!/usr/bin/env python3
"""
AetherOS File Preview & Properties Engine
Generates detailed file properties, permissions (octal / symbolic), MIME classification,
and content previews for text, images, media, and archives.
"""

import os
import stat
import mimetypes
import datetime
import zipfile
import tarfile
from typing import Dict, Any, Optional

class PreviewEngine:
    @staticmethod
    def get_file_properties(file_path: str) -> Dict[str, Any]:
        if not os.path.exists(file_path):
            return {"error": "File does not exist"}

        try:
            st = os.lstat(file_path)
            mode = st.st_mode
            is_dir = stat.S_ISDIR(mode)
            is_link = stat.S_ISLNK(mode)

            # Permissions
            octal_perms = oct(stat.S_IMODE(mode))[2:].zfill(4)
            symbolic_perms = stat.filemode(mode)
            
            # MIME type
            mime_type, _ = mimetypes.guess_type(file_path)
            if is_dir:
                mime_type = "inode/directory"
            elif not mime_type:
                mime_type = "application/octet-stream"

            mod_time = datetime.datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
            access_time = datetime.datetime.fromtimestamp(st.st_atime).strftime("%Y-%m-%d %H:%M:%S")

            props = {
                "name": os.path.basename(file_path),
                "path": os.path.abspath(file_path),
                "parent_dir": os.path.dirname(os.path.abspath(file_path)),
                "size_bytes": st.st_size,
                "size_human": PreviewEngine._format_size(st.st_size) if not is_dir else "--",
                "is_dir": is_dir,
                "is_symlink": is_link,
                "mime_type": mime_type,
                "octal_permissions": octal_perms,
                "symbolic_permissions": symbolic_perms,
                "owner_uid": st.st_uid,
                "group_gid": st.st_gid,
                "modified": mod_time,
                "accessed": access_time
            }

            # Link target
            if is_link:
                try:
                    props["symlink_target"] = os.readlink(file_path)
                except Exception:
                    pass

            return props
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def get_text_preview(file_path: str, max_lines: int = 60, max_bytes: int = 16384) -> Optional[str]:
        if not os.path.isfile(file_path):
            return None

        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read(max_bytes)
                lines = content.splitlines()[:max_lines]
                return "\n".join(lines)
        except Exception:
            return None

    @staticmethod
    def get_archive_preview(file_path: str, max_items: int = 50) -> Optional[list]:
        lower = file_path.lower()
        items = []
        try:
            if lower.endswith(".zip"):
                with zipfile.ZipFile(file_path, "r") as zf:
                    for idx, info in enumerate(zf.infolist()[:max_items]):
                        items.append({
                            "name": info.filename,
                            "size": info.file_size,
                            "is_dir": info.is_dir()
                        })
                return items
            elif lower.endswith((".tar.gz", ".tgz", ".tar.xz", ".tar")):
                with tarfile.open(file_path, "r:*") as tf:
                    for idx, member in enumerate(tf.getmembers()[:max_items]):
                        items.append({
                            "name": member.name,
                            "size": member.size,
                            "is_dir": member.isdir()
                        })
                return items
        except Exception:
            pass
        return None

    @staticmethod
    def _format_size(size_bytes: int) -> str:
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}" if unit != "B" else f"{size_bytes} B"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"
