#!/usr/bin/env python3
"""
AetherOS Application Launcher & Universal Search (aether-launcher)
Fast, fuzzy-search application launcher indexing standard .desktop specifications with
categorized browsing, keyboard navigation, and recent apps.
"""

import os
import sys
import glob
import subprocess
from typing import List, Dict, Any, Optional

CATEGORIES = ["All", "Internet", "Development", "Office", "Multimedia", "System", "Settings", "Accessories"]

class AetherLauncherEngine:
    def __init__(self):
        self.apps: List[Dict[str, Any]] = []
        self.recent_apps: List[str] = []
        self.load_installed_apps()

    def load_installed_apps(self) -> None:
        app_dirs = [
            "/usr/share/applications",
            "/usr/local/share/applications",
            os.path.expanduser("~/.local/share/applications")
        ]
        
        seen_ids = set()
        for d in app_dirs:
            if not os.path.exists(d):
                continue
            for fp in glob.glob(os.path.join(d, "*.desktop")):
                app_id = os.path.basename(fp)
                if app_id in seen_ids:
                    continue
                
                parsed = self._parse_desktop_file(fp)
                if parsed and not parsed.get("nodisplay", False):
                    seen_ids.add(app_id)
                    self.apps.append(parsed)

        # Fallback default apps if running in minimal test/container environments
        if not self.apps:
            self.apps = [
                {"id": "firefox.desktop", "name": "Firefox Web Browser", "categories": ["Internet"], "comment": "Explore the World Wide Web", "exec": "firefox", "icon": "firefox"},
                {"id": "thunar.desktop", "name": "Files", "categories": ["System", "Accessories"], "comment": "Browse files and folders", "exec": "thunar", "icon": "system-file-manager"},
                {"id": "foot.desktop", "name": "Aether Terminal", "categories": ["System", "Development"], "comment": "Fast Wayland terminal emulator", "exec": "foot", "icon": "utilities-terminal"},
                {"id": "aether-settings.desktop", "name": "Settings", "categories": ["Settings", "System"], "comment": "Control Center & System Preferences", "exec": "aether-settings", "icon": "preferences-system"},
                {"id": "aether-software.desktop", "name": "Software Hub", "categories": ["System", "Development"], "comment": "Install and manage applications", "exec": "aether-software", "icon": "software-store"},
            ]

    def _parse_desktop_file(self, filepath: str) -> Optional[Dict[str, Any]]:
        try:
            name, exec_cmd, icon, comment = "", "", "application-x-executable", ""
            categories = []
            nodisplay = False
            
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                in_entry = False
                for line in f:
                    line = line.strip()
                    if line == "[Desktop Entry]":
                        in_entry = True
                        continue
                    if line.startswith("[") and line != "[Desktop Entry]":
                        in_entry = False
                    if not in_entry:
                        continue
                    
                    if line.startswith("Name=") and not name:
                        name = line.split("=", 1)[1]
                    elif line.startswith("Exec="):
                        exec_cmd = line.split("=", 1)[1]
                    elif line.startswith("Icon="):
                        icon = line.split("=", 1)[1]
                    elif line.startswith("Comment="):
                        comment = line.split("=", 1)[1]
                    elif line.startswith("Categories="):
                        categories = [c.strip() for c in line.split("=", 1)[1].split(";") if c.strip()]
                    elif line.startswith("NoDisplay=true"):
                        nodisplay = True

            if name and exec_cmd:
                return {
                    "id": os.path.basename(filepath),
                    "name": name,
                    "exec": exec_cmd,
                    "icon": icon,
                    "comment": comment,
                    "categories": categories,
                    "nodisplay": nodisplay
                }
        except Exception:
            pass
        return None

    def search(self, query: str = "", category: str = "All") -> List[Dict[str, Any]]:
        query = query.strip().lower()
        results = []

        for app in self.apps:
            # Category filter
            if category and category != "All":
                if not any(category.lower() in c.lower() for c in app.get("categories", [])):
                    continue
            
            # Fuzzy match name, exec, or comment
            if not query:
                results.append(app)
            else:
                name_match = query in app["name"].lower()
                exec_match = query in app.get("exec", "").lower()
                comm_match = query in app.get("comment", "").lower()
                if name_match or exec_match or comm_match:
                    results.append(app)

        # Sort by relevance (exact prefix first, then alphabetical)
        results.sort(key=lambda a: (0 if a["name"].lower().startswith(query) else 1, a["name"].lower()))
        return results

    def launch(self, app_id: str) -> bool:
        for app in self.apps:
            if app["id"] == app_id:
                clean_cmd = app["exec"].split("%")[0].strip()
                try:
                    subprocess.Popen(clean_cmd.split(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    if app_id in self.recent_apps:
                        self.recent_apps.remove(app_id)
                    self.recent_apps.insert(0, app_id)
                    return True
                except Exception:
                    return False
        return False

def main():
    engine = AetherLauncherEngine()
    print(f"[aether-launcher] Indexed {len(engine.apps)} applications across system.")

    try:
        import gi
        gi.require_version("Gtk", "3.0")
        from gi.repository import Gtk, Gdk

        class LauncherWindow(Gtk.Window):
            def __init__(self, engine):
                super().__init__(type=Gtk.WindowType.TOPLEVEL)
                self.engine = engine
                self.set_title("aether-launcher")
                self.set_decorated(False)
                self.set_default_size(720, 520)
                self.set_position(Gtk.WindowPosition.CENTER)
                self.set_keep_above(True)

                css_provider = Gtk.CssProvider()
                css = """
                window {
                    background-color: rgba(11, 15, 25, 0.96);
                    border: 1px solid rgba(0, 210, 255, 0.25);
                    border-radius: 16px;
                }
                entry {
                    background-color: rgba(255, 255, 255, 0.08);
                    color: #ffffff;
                    border: 1px solid rgba(255, 255, 255, 0.15);
                    border-radius: 10px;
                    padding: 12px 16px;
                    font-size: 16px;
                }
                entry:focus {
                    border-color: #00d2ff;
                }
                .cat-btn {
                    background: transparent;
                    border: none;
                    color: #94a3b8;
                    padding: 6px 12px;
                    border-radius: 8px;
                }
                .cat-btn:checked, .cat-btn:hover {
                    background-color: rgba(0, 210, 255, 0.18);
                    color: #00d2ff;
                }
                .app-card {
                    background: rgba(255, 255, 255, 0.04);
                    border: 1px solid transparent;
                    border-radius: 12px;
                    padding: 12px;
                }
                .app-card:hover {
                    background: rgba(255, 255, 255, 0.10);
                    border-color: rgba(0, 210, 255, 0.4);
                }
                """
                css_provider.load_from_data(css.encode())
                Gtk.StyleContext.add_provider_for_screen(
                    Gdk.Screen.get_default(),
                    css_provider,
                    Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
                )

                main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
                main_box.set_margin_top(20)
                main_box.set_margin_bottom(20)
                main_box.set_margin_start(24)
                main_box.set_margin_end(24)
                self.add(main_box)

                # Search Entry
                self.entry = Gtk.Entry()
                self.entry.set_placeholder_text("Type to search applications and commands...")
                self.entry.connect("changed", self.on_search_changed)
                main_box.pack_start(self.entry, False, False, 0)

                # Category Bar
                cat_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
                self.selected_category = "All"
                for cat in CATEGORIES:
                    btn = Gtk.Button(label=cat)
                    btn.get_style_context().add_class("cat-btn")
                    btn.connect("clicked", lambda b, c=cat: self.on_category_clicked(c))
                    cat_box.pack_start(btn, False, False, 0)
                main_box.pack_start(cat_box, False, False, 0)

                # Scrollable Results Grid
                scroll = Gtk.ScrolledWindow()
                scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
                self.grid = Gtk.FlowBox()
                self.grid.set_valign(Gtk.Align.START)
                self.grid.set_max_children_per_line(3)
                self.grid.set_selection_mode(Gtk.SelectionMode.NONE)
                scroll.add(self.grid)
                main_box.pack_start(scroll, True, True, 0)

                # Escape key to close
                self.connect("key-press-event", self.on_key_press)
                self.populate_results()

            def on_key_press(self, widget, event):
                if event.keyval == Gdk.KEY_Escape:
                    self.destroy()
                    return True
                return False

            def on_category_clicked(self, category):
                self.selected_category = category
                self.populate_results()

            def on_search_changed(self, entry):
                self.populate_results()

            def populate_results(self):
                for child in self.grid.get_children():
                    self.grid.remove(child)

                query = self.entry.get_text()
                matches = self.engine.search(query, self.selected_category)
                for app in matches[:18]:
                    card = Gtk.Button()
                    card.get_style_context().add_class("app-card")
                    card_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
                    name_lbl = Gtk.Label(label=f"<b>{app['name']}</b>", use_markup=True)
                    desc_lbl = Gtk.Label(label=app.get("comment", "")[:40])
                    desc_lbl.get_style_context().add_class("dim-label")
                    card_box.pack_start(name_lbl, False, False, 0)
                    card_box.pack_start(desc_lbl, False, False, 0)
                    card.add(card_box)
                    card.connect("clicked", lambda b, aid=app["id"]: (self.engine.launch(aid), self.destroy()))
                    self.grid.add(card)

                self.grid.show_all()

        if os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"):
            win = LauncherWindow(engine)
            win.connect("destroy", Gtk.main_quit)
            win.show_all()
            Gtk.main()
    except Exception as e:
        print(f"[aether-launcher] Running in headless mode ({e})")

if __name__ == "__main__":
    main()
