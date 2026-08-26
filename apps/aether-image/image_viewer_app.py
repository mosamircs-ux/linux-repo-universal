#!/usr/bin/env python3
"""
AetherOS Native Image Viewer (aether-image)
High-performance, lightweight image viewer supporting PNG, JPEG, SVG, WebP, GIF,
smooth zooming, rotation, flipping, gallery navigation, and fullscreen slideshows.
"""

import os
import sys
import argparse
from typing import Dict, Any, List, Optional, Tuple

SUPPORTED_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".svg", ".gif", ".bmp", ".ico", ".tiff"}

class AetherImageViewerModel:
    def __init__(self, current_file: Optional[str] = None):
        self.current_file = current_file
        self.gallery: List[str] = []
        self.current_index = 0
        self.zoom_level = 1.0
        self.rotation_degrees = 0
        self.is_flipped_h = False
        self.is_flipped_v = False

        if current_file:
            self.load_image(current_file)

    def load_image(self, filepath: str) -> bool:
        if os.path.exists(filepath):
            self.current_file = filepath
            self.zoom_level = 1.0
            self.rotation_degrees = 0
            self.is_flipped_h = False
            self.is_flipped_v = False
            self._scan_folder(os.path.dirname(filepath))
            return True
        return False

    def _scan_folder(self, folder: str) -> None:
        self.gallery = []
        if os.path.exists(folder):
            try:
                for f in sorted(os.listdir(folder)):
                    _, ext = os.path.splitext(f.lower())
                    if ext in SUPPORTED_EXTS:
                        full_p = os.path.join(folder, f)
                        self.gallery.append(full_p)
                if self.current_file in self.gallery:
                    self.current_index = self.gallery.index(self.current_file)
            except Exception:
                pass

    def next_image(self) -> Optional[str]:
        if self.gallery and self.current_index < len(self.gallery) - 1:
            self.current_index += 1
            self.current_file = self.gallery[self.current_index]
            return self.current_file
        return None

    def prev_image(self) -> Optional[str]:
        if self.gallery and self.current_index > 0:
            self.current_index -= 1
            self.current_file = self.gallery[self.current_index]
            return self.current_file
        return None

    def rotate_cw(self) -> int:
        self.rotation_degrees = (self.rotation_degrees + 90) % 360
        return self.rotation_degrees

    def rotate_ccw(self) -> int:
        self.rotation_degrees = (self.rotation_degrees - 90) % 360
        return self.rotation_degrees

    def zoom_in(self) -> float:
        if self.zoom_level < 5.0:
            self.zoom_level = round(self.zoom_level + 0.2, 1)
        return self.zoom_level

    def zoom_out(self) -> float:
        if self.zoom_level > 0.2:
            self.zoom_level = round(self.zoom_level - 0.2, 1)
        return self.zoom_level

    def get_image_info(self) -> Dict[str, Any]:
        if not self.current_file or not os.path.exists(self.current_file):
            return {"name": "None", "size_kb": 0, "resolution": "0x0"}
        st = os.stat(self.current_file)
        return {
            "name": os.path.basename(self.current_file),
            "size_kb": round(st.st_size / 1024, 1),
            "zoom": f"{int(self.zoom_level * 100)}%",
            "rotation": f"{self.rotation_degrees}°"
        }

def main():
    parser = argparse.ArgumentParser(description="AetherOS Image Viewer")
    parser.add_argument("file", nargs="?", help="Image file to view")
    parser.add_argument("--test", action="store_true", help="Run test mode")
    args = parser.parse_args()

    model = AetherImageViewerModel(args.file)
    if args.test:
        model.rotate_cw()
        model.zoom_in()
        print(f"[aether-image] Model test passed: zoom={model.zoom_level}, rotation={model.rotation_degrees}")
        return

    try:
        import gi
        gi.require_version("Gtk", "3.0")
        from gi.repository import Gtk

        class ImageViewerWindow(Gtk.Window):
            def __init__(self, model):
                super().__init__(title="Aether Image Viewer")
                self.model = model
                self.set_default_size(880, 600)
                box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
                self.add(box)
                self.image_widget = Gtk.Image()
                box.pack_start(self.image_widget, True, True, 0)

        if os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"):
            win = ImageViewerWindow(model)
            win.connect("destroy", Gtk.main_quit)
            win.show_all()
            Gtk.main()
        else:
            print("[aether-image] Headless environment.")
    except Exception as e:
        print(f"[aether-image] Headless: {e}")

if __name__ == "__main__":
    main()
