#!/usr/bin/env python3
"""
AetherOS Freedesktop Trash Manager
Implements the FreeDesktop.org Trash specification for safe file deletion, inspection,
restoration, and emptying.
"""

import os
import sys
import time
import shutil
import urllib.parse
from datetime import datetime
from typing import List, Dict, Any, Optional

class TrashManager:
    def __init__(self, trash_dir: Optional[str] = None):
        if trash_dir:
            self.trash_dir = trash_dir
        else:
            xdg_data = os.environ.get("XDG_DATA_HOME", os.path.expanduser("~/.local/share"))
            self.trash_dir = os.path.join(xdg_data, "Trash")

        self.files_dir = os.path.join(self.trash_dir, "files")
        self.info_dir = os.path.join(self.trash_dir, "info")
        self._ensure_dirs()

    def _ensure_dirs(self) -> None:
        os.makedirs(self.files_dir, exist_ok=True)
        os.makedirs(self.info_dir, exist_ok=True)

    def move_to_trash(self, target_path: str) -> bool:
        if not os.path.exists(target_path):
            return False

        self._ensure_dirs()
        abs_path = os.path.abspath(target_path)
        base_name = os.path.basename(abs_path)

        # Unique trash filename if conflict
        trash_name = base_name
        dest_file_path = os.path.join(self.files_dir, trash_name)
        counter = 1
        name_root, name_ext = os.path.splitext(base_name)
        while os.path.exists(dest_file_path):
            trash_name = f"{name_root}_{counter}{name_ext}"
            dest_file_path = os.path.join(self.files_dir, trash_name)
            counter += 1

        info_path = os.path.join(self.info_dir, f"{trash_name}.trashinfo")
        now_str = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        encoded_path = urllib.parse.quote(abs_path)

        info_content = f"""[Trash Info]
Path={encoded_path}
DeletionDate={now_str}
"""
        try:
            with open(info_path, "w", encoding="utf-8") as f:
                f.write(info_content)
            shutil.move(abs_path, dest_file_path)
            return True
        except Exception:
            return False

    def list_trash_items(self) -> List[Dict[str, Any]]:
        self._ensure_dirs()
        items: List[Dict[str, Any]] = []

        if not os.path.exists(self.info_dir):
            return items

        for info_file in os.listdir(self.info_dir):
            if not info_file.endswith(".trashinfo"):
                continue

            trash_name = info_file[:-10]  # Strip .trashinfo
            actual_file_path = os.path.join(self.files_dir, trash_name)
            info_fp = os.path.join(self.info_dir, info_file)

            orig_path = ""
            del_date = ""

            try:
                with open(info_fp, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.startswith("Path="):
                            orig_path = urllib.parse.unquote(line.split("=", 1)[1].strip())
                        elif line.startswith("DeletionDate="):
                            del_date = line.split("=", 1)[1].strip()
            except Exception:
                continue

            size = 0
            is_dir = False
            if os.path.exists(actual_file_path):
                is_dir = os.path.isdir(actual_file_path)
                try:
                    if not is_dir:
                        size = os.path.getsize(actual_file_path)
                except Exception:
                    pass

            items.append({
                "trash_name": trash_name,
                "original_path": orig_path,
                "name": os.path.basename(orig_path) if orig_path else trash_name,
                "deletion_date": del_date,
                "file_path": actual_file_path,
                "size": size,
                "is_dir": is_dir
            })

        return items

    def restore_item(self, trash_name: str) -> bool:
        info_fp = os.path.join(self.info_dir, f"{trash_name}.trashinfo")
        file_fp = os.path.join(self.files_dir, trash_name)

        if not os.path.exists(info_fp) or not os.path.exists(file_fp):
            return False

        orig_path = ""
        try:
            with open(info_fp, "r", encoding="utf-8") as f:
                for line in f:
                    if line.startswith("Path="):
                        orig_path = urllib.parse.unquote(line.split("=", 1)[1].strip())
        except Exception:
            return False

        if not orig_path:
            return False

        os.makedirs(os.path.dirname(orig_path), exist_ok=True)
        try:
            shutil.move(file_fp, orig_path)
            os.remove(info_fp)
            return True
        except Exception:
            return False

    def empty_trash(self) -> int:
        self._ensure_dirs()
        count = 0
        for f in os.listdir(self.files_dir):
            fp = os.path.join(self.files_dir, f)
            try:
                if os.path.isdir(fp):
                    shutil.rmtree(fp)
                else:
                    os.remove(fp)
                count += 1
            except Exception:
                pass

        for inf in os.listdir(self.info_dir):
            try:
                os.remove(os.path.join(self.info_dir, inf))
            except Exception:
                pass

        return count
