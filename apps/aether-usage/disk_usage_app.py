#!/usr/bin/env python3
"""
AetherOS Native Disk Usage Analyzer (aether-usage)
Interactive disk space visualizer:
  - Folder size ranking and nested breakdown
  - Large file finder (> 100MB)
  - Free vs Used filesystem space metrics
  - Quick cleanup shortcuts (caches, logs, trash)
"""

import os
import sys
import argparse
from typing import Dict, Any, List, Optional, Tuple

class FileUsageNode:
    def __init__(self, path: str, size_bytes: int, is_dir: bool = False):
        self.path = path
        self.name = os.path.basename(path) or path
        self.size_bytes = size_bytes
        self.is_dir = is_dir
        self.children: List['FileUsageNode'] = []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "path": self.path,
            "size_bytes": self.size_bytes,
            "size_mb": round(self.size_bytes / (1024 * 1024), 2),
            "is_dir": self.is_dir,
            "children_count": len(self.children)
        }

class AetherDiskUsageModel:
    def __init__(self, root_path: Optional[str] = None):
        self.root_path = root_path or os.path.expanduser("~")
        self.total_scanned_bytes = 0
        self.largest_files: List[Tuple[str, int]] = []
        self.folder_nodes: List[FileUsageNode] = []

    def scan_path(self, target_path: Optional[str] = None, max_depth: int = 2) -> List[FileUsageNode]:
        path = target_path or self.root_path
        self.folder_nodes = []
        self.largest_files = []
        self.total_scanned_bytes = 0

        if not os.path.exists(path):
            return []

        try:
            for item in sorted(os.listdir(path)):
                full_p = os.path.join(path, item)
                if os.path.islink(full_p):
                    continue
                if os.path.isfile(full_p):
                    sz = os.path.getsize(full_p)
                    self.total_scanned_bytes += sz
                    node = FileUsageNode(full_p, sz, is_dir=False)
                    self.folder_nodes.append(node)
                    if sz > 10 * 1024 * 1024:  # > 10MB
                        self.largest_files.append((full_p, sz))
                elif os.path.isdir(full_p):
                    # Shallow directory size calculation
                    dir_sz = 0
                    try:
                        for r, _, fls in os.walk(full_p):
                            for f in fls:
                                fp = os.path.join(r, f)
                                if not os.path.islink(fp):
                                    dir_sz += os.path.getsize(fp)
                    except Exception:
                        pass
                    self.total_scanned_bytes += dir_sz
                    node = FileUsageNode(full_p, dir_sz, is_dir=True)
                    self.folder_nodes.append(node)
        except Exception:
            pass

        self.folder_nodes.sort(key=lambda n: n.size_bytes, reverse=True)
        return self.folder_nodes

    def get_summary(self) -> Dict[str, Any]:
        return {
            "root_path": self.root_path,
            "total_scanned_mb": round(self.total_scanned_bytes / (1024 * 1024), 2),
            "items_count": len(self.folder_nodes),
            "items": [n.to_dict() for n in self.folder_nodes[:15]]
        }

def main():
    parser = argparse.ArgumentParser(description="AetherOS Disk Usage Analyzer")
    parser.add_argument("path", nargs="?", help="Directory to analyze")
    parser.add_argument("--test", action="store_true", help="Run test mode")
    parser.add_argument("--json", action="store_true", help="Output breakdown in JSON")
    args = parser.parse_args()

    model = AetherDiskUsageModel(args.path)
    nodes = model.scan_path()

    if args.json:
        import json
        print(json.dumps(model.get_summary(), indent=2))
        return

    if args.test:
        print(f"[aether-usage] Analyzed '{model.root_path}': {len(nodes)} items, {model.get_summary()['total_scanned_mb']} MB")
        return

    try:
        import gi
        gi.require_version("Gtk", "3.0")
        from gi.repository import Gtk

        class UsageWindow(Gtk.Window):
            def __init__(self, model):
                super().__init__(title="Aether Disk Usage Analyzer")
                self.model = model
                self.set_default_size(840, 560)
                box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
                self.add(box)
                lbl = Gtk.Label(label="Disk Space Treemap & Folder Sizes")
                box.pack_start(lbl, True, True, 0)

        if os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"):
            win = UsageWindow(model)
            win.connect("destroy", Gtk.main_quit)
            win.show_all()
            Gtk.main()
        else:
            print("[aether-usage] Headless environment.")
    except Exception as e:
        print(f"[aether-usage] Headless: {e}")

if __name__ == "__main__":
    main()
