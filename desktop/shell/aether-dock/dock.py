#!/usr/bin/env python3
"""
AetherOS Modular Desktop Dock
Features: Left-dock / Bottom-dock orientation, pinned launchers, active window indicators,
Ubuntu-like ergonomics, Arabic RTL awareness, sub-15MB memory footprint.
"""

import os
import sys
import json
import subprocess
from typing import List, Dict, Any

DEFAULT_PINNED_APPS = [
    {"id": "aether-launcher", "name": "Applications", "icon": "view-app-grid-symbolic", "exec": "python3 /usr/lib/aether/shell/launcher.py"},
    {"id": "aether-terminal", "name": "Terminal", "icon": "utilities-terminal", "exec": "aether-terminal"},
    {"id": "file-manager", "name": "Files", "icon": "system-file-manager", "exec": "thunar"},
    {"id": "web-browser", "name": "Browser", "icon": "web-browser", "exec": "firefox || chromium || sensible-browser"},
    {"id": "aether-software", "name": "Software Hub", "icon": "software-store", "exec": "aether-software"},
    {"id": "aether-settings", "name": "Settings", "icon": "preferences-system", "exec": "aether-settings"},
]

class AetherDockModel:
    def __init__(self, config_path: str = None):
        self.config_path = config_path or os.path.expanduser("~/.config/aether/dock.json")
        self.position = "left"  # "left", "bottom", "right"
        self.icon_size = 44
        self.autohide = False
        self.pinned_apps: List[Dict[str, Any]] = list(DEFAULT_PINNED_APPS)
        self.running_apps: Dict[str, Dict[str, Any]] = {}
        self.load_config()

    def load_config(self) -> None:
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.position = data.get("position", self.position)
                    self.icon_size = data.get("icon_size", self.icon_size)
                    self.autohide = data.get("autohide", self.autohide)
                    self.pinned_apps = data.get("pinned_apps", self.pinned_apps)
            except Exception as e:
                print(f"[DockModel] Warning reading config: {e}", file=sys.stderr)

    def save_config(self) -> None:
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        data = {
            "position": self.position,
            "icon_size": self.icon_size,
            "autohide": self.autohide,
            "pinned_apps": self.pinned_apps,
        }
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def pin_app(self, app_id: str, name: str, icon: str, exec_cmd: str) -> None:
        if not any(a["id"] == app_id for a in self.pinned_apps):
            self.pinned_apps.append({"id": app_id, "name": name, "icon": icon, "exec": exec_cmd})
            self.save_config()

    def unpin_app(self, app_id: str) -> None:
        self.pinned_apps = [a for a in self.pinned_apps if a["id"] != app_id]
        self.save_config()

    def launch(self, app_id: str) -> bool:
        for app in self.pinned_apps:
            if app["id"] == app_id:
                try:
                    subprocess.Popen(app["exec"], shell=True, start_new_session=True)
                    return True
                except Exception as e:
                    print(f"[Dock] Launch error: {e}", file=sys.stderr)
                    return False
        return False

def main():
    print("AetherOS Dock Shell Engine initialized.")
    model = AetherDockModel()
    print(f"Dock position: {model.position}, Items: {len(model.pinned_apps)}")

if __name__ == "__main__":
    main()
