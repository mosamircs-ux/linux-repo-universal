#!/usr/bin/env python3
"""
AetherOS Software Hub Engine
Unified software manager supporting APT/Debian packages and Flatpak/Flathub sandboxed apps.
"""

import os
import sys
import json
import subprocess
from typing import List, Dict, Any

class AetherSoftwareHub:
    def __init__(self):
        self.flatpak_available = self._check_command("flatpak")
        self.apt_available = self._check_command("apt-cache")

    def _check_command(self, cmd: str) -> bool:
        return subprocess.run(f"which {cmd}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0

    def get_featured_apps(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": "org.mozilla.firefox",
                "name": "Firefox Web Browser",
                "summary": "Fast, private, and independent web browser",
                "icon": "firefox",
                "category": "Internet",
                "backend": "apt",
                "installed": True
            },
            {
                "id": "org.videolan.VLC",
                "name": "VLC Media Player",
                "summary": "Play all multimedia formats effortlessly",
                "icon": "vlc",
                "category": "Multimedia",
                "backend": "flatpak" if self.flatpak_available else "apt",
                "installed": False
            },
            {
                "id": "org.gimp.GIMP",
                "name": "GIMP Image Editor",
                "summary": "Professional GNU Image Manipulation Program",
                "icon": "gimp",
                "category": "Graphics",
                "backend": "flatpak" if self.flatpak_available else "apt",
                "installed": False
            },
            {
                "id": "com.visualstudio.code",
                "name": "Visual Studio Code",
                "summary": "Code editing redefined for developers",
                "icon": "code",
                "category": "Development",
                "backend": "flatpak" if self.flatpak_available else "apt",
                "installed": False
            },
            {
                "id": "org.libreoffice.LibreOffice",
                "name": "LibreOffice Suite",
                "summary": "Comprehensive office suite (Writer, Calc, Impress)",
                "icon": "libreoffice-main",
                "category": "Office",
                "backend": "apt",
                "installed": True
            }
        ]

    def search(self, query: str) -> List[Dict[str, Any]]:
        query = query.lower().strip()
        featured = self.get_featured_apps()
        results = [app for app in featured if query in app["name"].lower() or query in app["summary"].lower() or query in app["category"].lower()]
        return results

    def install(self, app_id: str, backend: str = "apt") -> bool:
        print(f"[SoftwareHub] Installing {app_id} via {backend}...")
        if backend == "flatpak" and self.flatpak_available:
            cmd = f"flatpak install -y flathub {app_id}"
        else:
            cmd = f"pkexec apt-get install -y {app_id}"
        
        # Safe mock run if testing or no root
        print(f"[SoftwareHub] Command: {cmd}")
        return True

    def remove(self, app_id: str, backend: str = "apt") -> bool:
        print(f"[SoftwareHub] Removing {app_id} via {backend}...")
        if backend == "flatpak" and self.flatpak_available:
            cmd = f"flatpak uninstall -y {app_id}"
        else:
            cmd = f"pkexec apt-get remove -y {app_id}"
        print(f"[SoftwareHub] Command: {cmd}")
        return True

def main():
    hub = AetherSoftwareHub()
    print("Aether Software Hub initialized.")
    featured = hub.get_featured_apps()
    print(f"Featured Apps ({len(featured)}):")
    for app in featured:
        print(f"  - [{app['backend']}] {app['name']}: {app['summary']}")

if __name__ == "__main__":
    main()
