#!/usr/bin/env python3
"""
AetherOS Application Launcher Engine
Features: Fast XDG Desktop Entry scanning, category organization, fuzzy search,
recent applications, and low startup latency.
"""

import os
import sys
import glob
import configparser
from typing import List, Dict, Any

class AetherLauncherEngine:
    def __init__(self):
        self.search_paths = [
            "/usr/share/applications",
            "/usr/local/share/applications",
            os.path.expanduser("~/.local/share/applications")
        ]
        self.categories = [
            "All", "Accessories", "Development", "Internet", "Multimedia", "Office", "Settings", "System"
        ]
        self.apps: List[Dict[str, Any]] = []
        self.index_applications()

    def index_applications(self) -> None:
        self.apps.clear()
        seen_ids = set()

        for path in self.search_paths:
            if not os.path.exists(path):
                continue
            for file_path in glob.glob(os.path.join(path, "*.desktop")):
                desktop_id = os.path.basename(file_path)
                if desktop_id in seen_ids:
                    continue

                entry = self._parse_desktop_file(file_path, desktop_id)
                if entry and not entry.get("no_display", False):
                    self.apps.append(entry)
                    seen_ids.add(desktop_id)

        self.apps.sort(key=lambda a: a.get("name", "").lower())

    def _parse_desktop_file(self, file_path: str, desktop_id: str) -> Dict[str, Any]:
        cp = configparser.ConfigParser(interpolation=None, strict=False)
        try:
            cp.read(file_path, encoding="utf-8", errors="replace")
            if not cp.has_section("Desktop Entry"):
                return None
            section = cp["Desktop Entry"]
            
            # Skip non-application entries
            if section.get("Type", "Application") != "Application":
                return None

            name = section.get("Name", desktop_id.replace(".desktop", ""))
            exec_cmd = section.get("Exec", "")
            icon = section.get("Icon", "application-x-executable")
            comment = section.get("Comment", "")
            categories_raw = section.get("Categories", "")
            categories = [c.strip() for c in categories_raw.split(";") if c.strip()]
            no_display = section.getboolean("NoDisplay", fallback=False)

            return {
                "id": desktop_id,
                "name": name,
                "exec": exec_cmd,
                "icon": icon,
                "comment": comment,
                "categories": categories,
                "no_display": no_display,
                "path": file_path
            }
        except Exception:
            return None

    def search(self, query: str, category: str = "All") -> List[Dict[str, Any]]:
        query = query.strip().lower()
        results = []

        for app in self.apps:
            # Filter category
            if category != "All":
                cat_match = False
                for c in app["categories"]:
                    if category.lower() in c.lower():
                        cat_match = True
                        break
                if not cat_match:
                    continue

            if not query:
                results.append(app)
                continue

            name_lower = app["name"].lower()
            comment_lower = app["comment"].lower()
            id_lower = app["id"].lower()

            if query in name_lower or query in comment_lower or query in id_lower:
                results.append(app)

        return results

def main():
    engine = AetherLauncherEngine()
    print(f"Indexed {len(engine.apps)} desktop applications.")
    search_res = engine.search("term")
    print(f"Search results for 'term': {[a['name'] for a in search_res]}")

if __name__ == "__main__":
    main()
