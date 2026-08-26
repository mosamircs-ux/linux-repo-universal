#!/usr/bin/env python3
"""
AetherOS Dock Engine (aether-dock)
Ubuntu-style ergonomic dock supporting left/bottom positioning, pinned and active applications,
unread badges, auto-hide, and full RTL layout mirroring for Arabic localization.
"""

import os
import sys
import json
import subprocess
from typing import List, Dict, Any, Optional

DEFAULT_PINNED_APPS = [
    {"id": "thunar", "name": "Files", "icon": "system-file-manager", "exec": "thunar", "running": False, "badge": 0},
    {"id": "foot", "name": "Terminal", "icon": "utilities-terminal", "exec": "foot", "running": False, "badge": 0},
    {"id": "aether-software", "name": "Software Hub", "icon": "software-store", "exec": "aether-software", "running": False, "badge": 0},
    {"id": "aether-settings", "name": "Settings", "icon": "preferences-system", "exec": "aether-settings", "running": False, "badge": 0},
    {"id": "firefox", "name": "Firefox", "icon": "firefox", "exec": "firefox", "running": False, "badge": 0}
]

class AetherDockModel:
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or os.path.expanduser("~/.config/aether/dock.json")
        self.position = "left"  # "left", "bottom", "right" (for RTL)
        self.autohide = False
        self.icon_size = 48
        self.pinned_apps = list(DEFAULT_PINNED_APPS)
        self.running_apps: List[Dict[str, Any]] = []
        self.rtl = False
        self.load_config()

    def load_config(self) -> None:
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.position = data.get("position", self.position)
                    self.autohide = data.get("autohide", self.autohide)
                    self.icon_size = data.get("icon_size", self.icon_size)
                    self.rtl = data.get("rtl", self.rtl)
                    if "pinned_apps" in data:
                        self.pinned_apps = data["pinned_apps"]
            except Exception:
                pass

    def save_config(self) -> None:
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump({
                    "position": self.position,
                    "autohide": self.autohide,
                    "icon_size": self.icon_size,
                    "rtl": self.rtl,
                    "pinned_apps": self.pinned_apps
                }, f, indent=2)
        except Exception:
            pass

    def pin_app(self, app_id: str, name: str, icon: str, exec_cmd: str) -> None:
        if not any(a["id"] == app_id for a in self.pinned_apps):
            self.pinned_apps.append({
                "id": app_id,
                "name": name,
                "icon": icon,
                "exec": exec_cmd,
                "running": False,
                "badge": 0
            })
            self.save_config()

    def unpin_app(self, app_id: str) -> None:
        self.pinned_apps = [a for a in self.pinned_apps if a["id"] != app_id]
        self.save_config()

    def set_app_running(self, app_id: str, running: bool = True, badge: int = 0) -> None:
        for app in self.pinned_apps:
            if app["id"] == app_id:
                app["running"] = running
                app["badge"] = badge
                return

    def set_rtl(self, enabled: bool) -> None:
        self.rtl = enabled
        if self.rtl and self.position == "left":
            self.position = "right"
        elif not self.rtl and self.position == "right":
            self.position = "left"

    def launch_app(self, app_id: str) -> bool:
        for app in self.pinned_apps:
            if app["id"] == app_id:
                try:
                    subprocess.Popen(app["exec"].split(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    app["running"] = True
                    return True
                except Exception:
                    return False
        return False

def main():
    dock = AetherDockModel()
    print(f"[aether-dock] Started: position={dock.position}, pinned={len(dock.pinned_apps)}")

    # GTK UI if graphical display is active
    try:
        import gi
        gi.require_version("Gtk", "3.0")
        from gi.repository import Gtk, Gdk

        class DockWindow(Gtk.Window):
            def __init__(self, model):
                super().__init__(type=Gtk.WindowType.TOPLEVEL)
                self.model = model
                self.set_title("aether-dock")
                self.set_decorated(False)
                self.set_app_paintable(True)
                self.set_default_size(64, 800)
                self.set_keep_above(True)

                css_provider = Gtk.CssProvider()
                css = """
                window {
                    background-color: rgba(11, 15, 25, 0.90);
                    border-right: 1px solid rgba(255, 255, 255, 0.08);
                }
                .dock-btn {
                    background: transparent;
                    border: none;
                    border-radius: 12px;
                    padding: 8px;
                    margin: 4px 6px;
                }
                .dock-btn:hover {
                    background-color: rgba(255, 255, 255, 0.15);
                }
                .running-dot {
                    background-color: #00d2ff;
                    border-radius: 2px;
                    min-width: 4px;
                    min-height: 4px;
                }
                """
                css_provider.load_from_data(css.encode())
                Gtk.StyleContext.add_provider_for_screen(
                    Gdk.Screen.get_default(),
                    css_provider,
                    Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
                )

                box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
                box.set_margin_top(12)
                box.set_margin_bottom(12)
                self.add(box)

                # Launcher Grid Button at Top (Ubuntu Style)
                grid_btn = Gtk.Button(label="▦")
                grid_btn.get_style_context().add_class("dock-btn")
                grid_btn.connect("clicked", lambda b: subprocess.Popen(["python3", "/usr/lib/aether/shell/launcher.py"]))
                box.pack_start(grid_btn, False, False, 0)

                # Pinned Apps
                for app in self.model.pinned_apps:
                    btn = Gtk.Button(label=app["name"][:2])
                    btn.set_tooltip_text(app["name"])
                    btn.get_style_context().add_class("dock-btn")
                    btn.connect("clicked", lambda b, aid=app["id"]: self.model.launch_app(aid))
                    box.pack_start(btn, False, False, 0)

        if os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"):
            win = DockWindow(dock)
            win.connect("destroy", Gtk.main_quit)
            win.show_all()
            Gtk.main()
    except Exception as e:
        print(f"[aether-dock] Running in headless/model mode ({e})")

if __name__ == "__main__":
    main()
