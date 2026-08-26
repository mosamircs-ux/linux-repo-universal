#!/usr/bin/env python3
"""
AetherOS Applications & Default Applications Settings Backend
Inspects installed applications and manages default MIME associations via xdg-settings / xdg-mime.
"""

import os
import glob
import subprocess
import shutil
from typing import Dict, Any, List, Tuple

MIME_CATEGORIES = {
    "web_browser": "x-scheme-handler/http",
    "mail_client": "x-scheme-handler/mailto",
    "text_editor": "text/plain",
    "file_manager": "inode/directory",
    "music_player": "audio/mpeg",
    "video_player": "video/mp4",
    "photo_viewer": "image/jpeg"
}

class ApplicationsBackend:
    @staticmethod
    def get_default_applications() -> Dict[str, str]:
        defaults = {
            "web_browser": "firefox.desktop",
            "mail_client": "thunderbird.desktop",
            "text_editor": "featherpad.desktop",
            "file_manager": "thunar.desktop",
            "music_player": "rhythmbox.desktop",
            "video_player": "vlc.desktop",
            "photo_viewer": "viewnior.desktop"
        }
        if shutil.which("xdg-mime"):
            for cat, mime in MIME_CATEGORIES.items():
                try:
                    res = subprocess.run(["xdg-mime", "query", "default", mime], capture_output=True, text=True)
                    if res.returncode == 0 and res.stdout.strip():
                        defaults[cat] = res.stdout.strip()
                except Exception:
                    pass
        return defaults

    @staticmethod
    def set_default_application(category: str, desktop_id: str) -> bool:
        mime = MIME_CATEGORIES.get(category)
        if not mime:
            return False

        if shutil.which("xdg-mime"):
            try:
                subprocess.run(["xdg-mime", "default", desktop_id, mime], capture_output=True)
                if category == "web_browser" and shutil.which("xdg-settings"):
                    subprocess.run(["xdg-settings", "set", "default-web-browser", desktop_id], capture_output=True)
                return True
            except Exception:
                return False
        return True

    @staticmethod
    def list_installed_apps() -> List[Dict[str, str]]:
        apps = []
        for d in ["/usr/share/applications", os.path.expanduser("~/.local/share/applications")]:
            if os.path.exists(d):
                for fp in glob.glob(os.path.join(d, "*.desktop")):
                    app_id = os.path.basename(fp)
                    name = app_id.replace(".desktop", "").replace("-", " ").capitalize()
                    apps.append({"id": app_id, "name": name})
        if not apps:
            apps = [
                {"id": "firefox.desktop", "name": "Firefox"},
                {"id": "thunar.desktop", "name": "Files"},
                {"id": "foot.desktop", "name": "Aether Terminal"},
            ]
        return apps
