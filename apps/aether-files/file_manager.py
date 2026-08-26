#!/usr/bin/env python3
"""
AetherOS Native Lightweight File Manager (aether-files)
High-performance Wayland/GTK file manager featuring asynchronous non-blocking transfers,
tabs, dual-pane split view, Freedesktop trash, archive operations, and disk/filesystem detection.
"""

import os
import sys
import json
import stat
import shutil
import mimetypes
import datetime
import subprocess
from typing import List, Dict, Any, Optional, Tuple

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(REPO_ROOT, "apps", "aether-files"))

from engine.file_operations import AsyncTransferQueue, TransferTask, TransferStatus, ConflictResolution
from engine.trash_manager import TrashManager
from engine.disk_manager import DiskManager
from engine.archive_manager import ArchiveManager
from engine.search_engine import SearchEngine
from engine.preview_engine import PreviewEngine

STANDARD_PLACES = [
    {"id": "home", "name": "Home", "icon": "user-home", "path": os.path.expanduser("~")},
    {"id": "desktop", "name": "Desktop", "icon": "user-desktop", "path": os.path.expanduser("~/Desktop")},
    {"id": "documents", "name": "Documents", "icon": "folder-documents", "path": os.path.expanduser("~/Documents")},
    {"id": "downloads", "name": "Downloads", "icon": "folder-download", "path": os.path.expanduser("~/Downloads")},
    {"id": "music", "name": "Music", "icon": "folder-music", "path": os.path.expanduser("~/Music")},
    {"id": "pictures", "name": "Pictures", "icon": "folder-pictures", "path": os.path.expanduser("~/Pictures")},
    {"id": "videos", "name": "Videos", "icon": "folder-videos", "path": os.path.expanduser("~/Videos")},
    {"id": "trash", "name": "Trash", "icon": "user-trash", "path": "trash://"}
]

class AetherFileManagerModel:
    def __init__(self, initial_path: Optional[str] = None):
        start_dir = initial_path or os.path.expanduser("~")
        if not os.path.exists(start_dir):
            start_dir = "/"

        self.tabs: List[str] = [os.path.abspath(start_dir)]
        self.active_tab_index = 0
        self.split_view_enabled = False
        self.split_pane_path = os.path.abspath(start_dir)
        self.show_hidden_files = False
        self.view_mode = "detailed"  # "detailed", "icons"
        self.sort_by = "name"        # "name", "size", "modified", "type"
        self.sort_reverse = False

        self.history: List[str] = [os.path.abspath(start_dir)]
        self.history_index = 0
        self.selected_items: List[str] = []
        self.clipboard: Optional[Dict[str, Any]] = None

        # Engine instances
        self.transfer_queue = AsyncTransferQueue()
        self.trash_manager = TrashManager()
        self.disk_manager = DiskManager()
        self.archive_manager = ArchiveManager()
        self.search_engine = SearchEngine()
        self.preview_engine = PreviewEngine()

        self.bookmarks = self._load_bookmarks()

    @property
    def current_path(self) -> str:
        if 0 <= self.active_tab_index < len(self.tabs):
            return self.tabs[self.active_tab_index]
        return os.path.expanduser("~")

    def _load_bookmarks(self) -> List[Dict[str, str]]:
        bm = list(STANDARD_PLACES)
        bm_file = os.path.expanduser("~/.config/gtk-3.0/bookmarks")
        if os.path.exists(bm_file):
            try:
                with open(bm_file, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("file://"):
                            p = line[7:].split()[0]
                            name = os.path.basename(p)
                            bm.append({"id": f"bm_{name}", "name": name, "icon": "folder", "path": p})
            except Exception:
                pass
        return bm

    def navigate_to(self, path: str) -> bool:
        if path == "trash://":
            self.tabs[self.active_tab_index] = path
            return True

        abs_path = os.path.abspath(os.path.expanduser(path))
        if os.path.isdir(abs_path):
            self.tabs[self.active_tab_index] = abs_path
            self.selected_items.clear()
            
            # History
            if self.history_index < len(self.history) - 1:
                self.history = self.history[:self.history_index + 1]
            self.history.append(abs_path)
            self.history_index = len(self.history) - 1
            return True
        return False

    def navigate_up(self) -> bool:
        if self.current_path == "trash://" or self.current_path == "/":
            return False
        parent = os.path.dirname(self.current_path)
        return self.navigate_to(parent)

    def navigate_back(self) -> bool:
        if self.history_index > 0:
            self.history_index -= 1
            self.tabs[self.active_tab_index] = self.history[self.history_index]
            self.selected_items.clear()
            return True
        return False

    def navigate_forward(self) -> bool:
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.tabs[self.active_tab_index] = self.history[self.history_index]
            self.selected_items.clear()
            return True
        return False

    def open_tab(self, path: Optional[str] = None) -> int:
        target = path or self.current_path
        self.tabs.append(os.path.abspath(target) if target != "trash://" else target)
        self.active_tab_index = len(self.tabs) - 1
        return self.active_tab_index

    def close_tab(self, index: int) -> bool:
        if len(self.tabs) > 1 and 0 <= index < len(self.tabs):
            self.tabs.pop(index)
            if self.active_tab_index >= len(self.tabs):
                self.active_tab_index = len(self.tabs) - 1
            return True
        return False

    def switch_tab(self, index: int) -> bool:
        if 0 <= index < len(self.tabs):
            self.active_tab_index = index
            self.selected_items.clear()
            return True
        return False

    def toggle_split_view(self) -> bool:
        self.split_view_enabled = not self.split_view_enabled
        if self.split_view_enabled:
            self.split_pane_path = self.current_path
        return self.split_view_enabled

    def list_current_directory(self) -> List[Dict[str, Any]]:
        return self.list_directory(self.current_path, self.show_hidden_files, self.sort_by, self.sort_reverse)

    def list_directory(self, dir_path: str, show_hidden: bool = False, sort_by: str = "name", reverse: bool = False) -> List[Dict[str, Any]]:
        if dir_path == "trash://":
            return self.trash_manager.list_trash_items()

        if not os.path.exists(dir_path) or not os.path.isdir(dir_path):
            return []

        entries: List[Dict[str, Any]] = []
        try:
            with os.scandir(dir_path) as it:
                for entry in it:
                    if not show_hidden and entry.name.startswith("."):
                        continue

                    try:
                        st = entry.stat(follow_symlinks=False)
                        is_dir = entry.is_dir(follow_symlinks=False)
                        is_link = entry.is_symlink()
                        size = st.st_size if not is_dir else 0
                        
                        perms = stat.filemode(st.st_mode)
                        mod_time = datetime.datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M")
                        
                        mime = "inode/directory" if is_dir else (mimetypes.guess_type(entry.name)[0] or "application/octet-stream")

                        icon = "folder" if is_dir else "text-x-generic"
                        if not is_dir:
                            if mime.startswith("image/"):
                                icon = "image-x-generic"
                            elif mime.startswith("audio/"):
                                icon = "audio-x-generic"
                            elif mime.startswith("video/"):
                                icon = "video-x-generic"
                            elif ArchiveManager.is_archive(entry.name):
                                icon = "package-x-generic"

                        entries.append({
                            "name": entry.name,
                            "path": entry.path,
                            "is_dir": is_dir,
                            "is_symlink": is_link,
                            "size": size,
                            "size_human": PreviewEngine._format_size(size) if not is_dir else "--",
                            "modified": mod_time,
                            "permissions": perms,
                            "mime": mime,
                            "icon": icon
                        })
                    except Exception:
                        continue
        except PermissionError:
            return [{"name": "Permission Denied", "path": dir_path, "is_dir": False, "size": 0, "size_human": "--", "modified": "--", "permissions": "---------", "mime": "error", "icon": "dialog-error"}]
        except Exception:
            return []

        # Sorting: Folders always first, then by sort_by attribute
        def sort_key(item):
            folder_weight = 0 if item["is_dir"] else 1
            val = item.get(sort_by, item["name"])
            if isinstance(val, str):
                val = val.lower()
            return (folder_weight, val)

        entries.sort(key=sort_key, reverse=reverse)
        return entries

    # Clipboard & Operations
    def copy_selection(self) -> None:
        if self.selected_items:
            self.clipboard = {"op": "copy", "items": list(self.selected_items)}

    def cut_selection(self) -> None:
        if self.selected_items:
            self.clipboard = {"op": "cut", "items": list(self.selected_items)}

    def paste(self, destination: Optional[str] = None, conflict_strategy: ConflictResolution = ConflictResolution.AUTO_RENAME) -> Optional[TransferTask]:
        if not self.clipboard or not self.clipboard.get("items"):
            return None
        target_dest = destination or self.current_path
        if target_dest == "trash://":
            return None

        items = self.clipboard["items"]
        if self.clipboard["op"] == "copy":
            task = self.transfer_queue.start_copy(items, target_dest, conflict_strategy)
        else:
            task = self.transfer_queue.start_move(items, target_dest, conflict_strategy)
            self.clipboard = None
        return task

    def move_to_trash(self, target_paths: List[str]) -> int:
        count = 0
        for p in target_paths:
            if self.trash_manager.move_to_trash(p):
                count += 1
        return count

    def delete_permanently(self, target_paths: List[str]) -> TransferTask:
        return self.transfer_queue.start_delete(target_paths)

    def rename_item(self, target_path: str, new_name: str) -> bool:
        if not os.path.exists(target_path):
            return False
        parent = os.path.dirname(target_path)
        dest = os.path.join(parent, new_name)
        if os.path.exists(dest):
            return False
        try:
            os.rename(target_path, dest)
            return True
        except Exception:
            return False

    def create_directory(self, dir_name: str) -> bool:
        target = os.path.join(self.current_path, dir_name)
        if os.path.exists(target):
            return False
        try:
            os.makedirs(target, exist_ok=True)
            return True
        except Exception:
            return False

    def create_file(self, file_name: str) -> bool:
        target = os.path.join(self.current_path, file_name)
        if os.path.exists(target):
            return False
        try:
            with open(target, "w", encoding="utf-8") as f:
                pass
            return True
        except Exception:
            return False

    def compress_items(self, items: List[str], archive_name: str, format_type: str = "zip") -> bool:
        out_path = os.path.join(self.current_path, archive_name)
        return self.archive_manager.create_archive(items, out_path, format_type)

    def extract_archive(self, archive_path: str, destination_dir: Optional[str] = None) -> bool:
        dest = destination_dir or self.current_path
        return self.archive_manager.extract_archive(archive_path, dest)

    def change_permissions(self, file_path: str, mode_octal: str) -> bool:
        try:
            mode_int = int(mode_octal, 8)
            os.chmod(file_path, mode_int)
            return True
        except Exception:
            return False

def main():
    fm = AetherFileManagerModel()
    print("================================================================")
    print("           AetherOS Files (aether-files Native Manager)         ")
    print("================================================================")
    print(f"Current Directory: {fm.current_path}")
    print(f"Tabs: {len(fm.tabs)} active | Split View: {fm.split_view_enabled}")
    
    entries = fm.list_current_directory()
    print(f"Directory items ({len(entries)} items):")
    for e in entries[:8]:
        t_flag = "[DIR]" if e["is_dir"] else "[FILE]"
        print(f"  {t_flag:6} {e['permissions']}  {e['size_human']:>8}  {e['modified']}  {e['name']}")
    if len(entries) > 8:
        print(f"  ... and {len(entries) - 8} more items")
    print("================================================================")

    # Launch GTK UI if Wayland/X11 display is available
    try:
        import gi
        gi.require_version("Gtk", "3.0")
        from gi.repository import Gtk, Gdk, GLib

        class FileManagerWindow(Gtk.Window):
            def __init__(self, model):
                super().__init__(type=Gtk.WindowType.TOPLEVEL)
                self.model = model
                self.set_title("AetherOS Files")
                self.set_default_size(1080, 680)
                self.set_position(Gtk.WindowPosition.CENTER)

                # HeaderBar
                header = Gtk.HeaderBar()
                header.set_show_close_button(True)
                header.set_title("Files")
                self.set_titlebar(header)

                btn_back = Gtk.Button(label="◀")
                btn_back.connect("clicked", lambda b: (self.model.navigate_back(), self.refresh_view()))
                header.pack_start(btn_back)

                btn_fwd = Gtk.Button(label="▶")
                btn_fwd.connect("clicked", lambda b: (self.model.navigate_forward(), self.refresh_view()))
                header.pack_start(btn_fwd)

                btn_up = Gtk.Button(label="▲")
                btn_up.connect("clicked", lambda b: (self.model.navigate_up(), self.refresh_view()))
                header.pack_start(btn_up)

                self.path_entry = Gtk.Entry()
                self.path_entry.set_text(self.model.current_path)
                self.path_entry.connect("activate", lambda e: (self.model.navigate_to(e.get_text()), self.refresh_view()))
                header.set_custom_title(self.path_entry)

                btn_split = Gtk.Button(label="⊞ Split")
                btn_split.connect("clicked", self.on_toggle_split)
                header.pack_end(btn_split)

                btn_newtab = Gtk.Button(label="+ Tab")
                btn_newtab.connect("clicked", lambda b: (self.model.open_tab(), self.refresh_view()))
                header.pack_end(btn_newtab)

                # Paned (Sidebar | Content)
                main_paned = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
                self.add(main_paned)

                # Sidebar (Places & Disks)
                side_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
                side_box.set_size_request(200, -1)
                side_box.set_margin_start(8)
                side_box.set_margin_top(8)

                side_scroll = Gtk.ScrolledWindow()
                side_scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
                side_list = Gtk.ListBox()
                for p in self.model.bookmarks:
                    row = Gtk.ListBoxRow()
                    row.target_path = p["path"]
                    lbl = Gtk.Label(label=f"📁 {p['name']}", xalign=0)
                    row.add(lbl)
                    side_list.add(row)
                side_list.connect("row-selected", lambda lb, r: (self.model.navigate_to(r.target_path), self.refresh_view()) if r else None)
                side_scroll.add(side_list)
                side_box.pack_start(side_scroll, True, True, 0)
                main_paned.pack1(side_box, False, False)

                # Main Content Area
                self.content_paned = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
                
                # Left Pane Files List
                self.file_scroll = Gtk.ScrolledWindow()
                self.file_list = Gtk.ListBox()
                self.file_scroll.add(self.file_list)
                self.content_paned.pack1(self.file_scroll, True, False)

                main_paned.pack2(self.content_paned, True, False)
                self.refresh_view()

            def on_toggle_split(self, btn):
                self.model.toggle_split_view()
                self.refresh_view()

            def refresh_view(self):
                self.path_entry.set_text(self.model.current_path)
                for child in self.file_list.get_children():
                    self.file_list.remove(child)

                entries = self.model.list_current_directory()
                for e in entries:
                    row = Gtk.ListBoxRow()
                    row.entry_data = e
                    box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
                    icon_lbl = Gtk.Label(label="📁" if e["is_dir"] else "📄")
                    name_lbl = Gtk.Label(label=e["name"], xalign=0)
                    size_lbl = Gtk.Label(label=e["size_human"])
                    box.pack_start(icon_lbl, False, False, 0)
                    box.pack_start(name_lbl, True, True, 0)
                    box.pack_end(size_lbl, False, False, 0)
                    row.add(box)
                    self.file_list.add(row)

                self.file_list.show_all()

        if os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"):
            win = FileManagerWindow(fm)
            win.connect("destroy", Gtk.main_quit)
            win.show_all()
            Gtk.main()
    except Exception as e:
        print(f"[aether-files] Running in headless mode ({e})")

if __name__ == "__main__":
    main()
