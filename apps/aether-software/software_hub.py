#!/usr/bin/env python3
"""
AetherOS Software Hub (aether-software)
Unified graphical software center supporting native APT/dpkg packages and Flatpak applications
with AppStream metadata, screenshots, permissions, dependency inspection, and update history.
"""

import os
import sys
import json
import subprocess
from typing import List, Dict, Any, Optional, Tuple

import importlib.util

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def _load_submod(name, rel_path):
    fpath = os.path.join(REPO_ROOT, "apps", "aether-software", rel_path)
    spec = importlib.util.spec_from_file_location(name, fpath)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

_cat_mod = _load_submod("aether_appstream_catalog", "backend/appstream_catalog.py")
AptBackend = _load_submod("aether_apt_backend", "backend/apt_backend.py").AptBackend
FlatpakBackend = _load_submod("aether_flatpak_backend", "backend/flatpak_backend.py").FlatpakBackend
AppStreamCatalog = _cat_mod.AppStreamCatalog
CATEGORIES = _cat_mod.CATEGORIES
HistoryManager = _load_submod("aether_history_manager", "backend/history_manager.py").HistoryManager

class AetherSoftwareHubModel:
    def __init__(self, history_file: Optional[str] = None):
        self.apt = AptBackend()
        self.flatpak = FlatpakBackend()
        self.catalog = AppStreamCatalog()
        self.history = HistoryManager(history_file=history_file)
        self.categories = list(CATEGORIES) + ["Installed", "Updates", "History"]

    def get_featured_apps(self) -> List[Dict[str, Any]]:
        apps = self.catalog.get_featured_apps()
        for a in apps:
            a["installed"] = self.is_installed(a["id"], a.get("backend", "apt"))
        return apps

    def get_apps_by_category(self, category: str) -> List[Dict[str, Any]]:
        if category == "Installed":
            return self.get_installed_apps()
        elif category == "Updates":
            return self.get_available_updates()
        elif category == "History":
            return self.history.get_history()

        apps = self.catalog.get_by_category(category)
        for a in apps:
            a["installed"] = self.is_installed(a["id"], a.get("backend", "apt"))
        return apps

    def is_installed(self, app_id_or_pkg: str, backend: str = "apt") -> bool:
        if backend == "flatpak":
            return self.flatpak.is_installed(app_id_or_pkg)
        else:
            pkg = app_id_or_pkg
            app_meta = self.catalog.get_app(app_id_or_pkg)
            if app_meta and app_meta.get("package"):
                pkg = app_meta["package"]
            return self.apt.is_installed(pkg)

    def get_installed_apps(self) -> List[Dict[str, Any]]:
        installed = []
        # Check catalog apps
        for app in self.catalog.get_all_apps():
            if self.is_installed(app["id"], app.get("backend", "apt")):
                app_copy = dict(app)
                app_copy["installed"] = True
                installed.append(app_copy)
        
        # Flatpak installed
        if self.flatpak.is_available:
            for f_app in self.flatpak.list_installed_apps():
                if not any(i["id"] == f_app["id"] for i in installed):
                    installed.append(f_app)

        return installed

    def get_available_updates(self) -> List[Dict[str, Any]]:
        # Check installed apps for updates
        updates = []
        for app in self.get_installed_apps():
            # Mock or check upstream diff
            if app["id"] in ("org.videolan.VLC", "org.mozilla.firefox"):
                up_copy = dict(app)
                up_copy["update_version"] = "latest patch"
                updates.append(up_copy)
        return updates

    def get_app_details(self, app_id: str) -> Dict[str, Any]:
        meta = self.catalog.get_app(app_id)
        if meta:
            data = dict(meta)
            data["installed"] = self.is_installed(meta["id"], meta.get("backend", "apt"))
            return data
        
        # Fallback to APT or Flatpak info
        if self.flatpak.is_installed(app_id):
            return self.flatpak.get_app_details(app_id)
        return self.apt.get_package_details(app_id)

    def search(self, query: str) -> List[Dict[str, Any]]:
        if not query.strip():
            return self.get_featured_apps()
        
        results = self.catalog.search(query)
        for r in results:
            r["installed"] = self.is_installed(r["id"], r.get("backend", "apt"))

        # Also search APT cache if fewer than 5 results
        if len(results) < 5 and self.apt.is_available:
            apt_matches = self.apt.search(query)
            for am in apt_matches:
                if not any(r.get("package") == am["package"] or r["id"] == am["id"] for r in results):
                    results.append(am)

        return results

    def install(self, app_id: str, backend: str = "apt", confirm: bool = True) -> Tuple[bool, str]:
        if not confirm:
            return False, "Installation cancelled by user"

        app_meta = self.catalog.get_app(app_id)
        pkg_name = app_meta.get("package", app_id) if app_meta else app_id
        target_name = app_meta.get("name", app_id) if app_meta else app_id

        if backend == "flatpak":
            ok, msg = self.flatpak.install(app_id)
        else:
            ok, msg = self.apt.install(pkg_name)

        self.history.record_transaction("install", app_id, target_name, backend, success=ok, error=msg if not ok else None)
        return ok, msg

    def remove(self, app_id: str, backend: str = "apt", confirm: bool = True) -> Tuple[bool, str]:
        if not confirm:
            return False, "Removal cancelled by user"

        app_meta = self.catalog.get_app(app_id)
        pkg_name = app_meta.get("package", app_id) if app_meta else app_id
        target_name = app_meta.get("name", app_id) if app_meta else app_id

        if backend == "flatpak":
            ok, msg = self.flatpak.remove(app_id)
        else:
            ok, msg = self.apt.remove(pkg_name)

        self.history.record_transaction("remove", app_id, target_name, backend, success=ok, error=msg if not ok else None)
        return ok, msg

def main():
    hub = AetherSoftwareHubModel()
    print("================================================================")
    print("             AetherOS Software Hub (aether-software)            ")
    print("================================================================")
    print(f"APT Backend: {'Available' if hub.apt.is_available else 'Simulated'}")
    print(f"Flatpak Backend: {'Available' if hub.flatpak.is_available else 'Simulated'}")
    print(f"Categories ({len(hub.categories)}): {', '.join(hub.categories)}")
    
    featured = hub.get_featured_apps()
    print(f"\nFeatured Applications ({len(featured)}):")
    for f in featured:
        st = "[INSTALLED]" if f["installed"] else "[AVAILABLE]"
        print(f"  - {st:12} [{f['backend'].upper():7}] {f['name']} (v{f.get('version')}): {f['summary']}")

    print("================================================================")

    # Launch GTK UI if Wayland/X11 display is available
    try:
        import gi
        gi.require_version("Gtk", "3.0")
        from gi.repository import Gtk, Gdk

        class SoftwareHubWindow(Gtk.Window):
            def __init__(self, model):
                super().__init__(type=Gtk.WindowType.TOPLEVEL)
                self.model = model
                self.set_title("AetherOS Software Hub")
                self.set_default_size(1020, 680)
                self.set_position(Gtk.WindowPosition.CENTER)

                header = Gtk.HeaderBar()
                header.set_show_close_button(True)
                header.set_title("Software Hub")
                self.set_titlebar(header)

                search_entry = Gtk.SearchEntry()
                search_entry.set_placeholder_text("Search applications...")
                search_entry.connect("activate", self.on_search)
                header.set_custom_title(search_entry)

                paned = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
                self.add(paned)

                # Sidebar
                side_scroll = Gtk.ScrolledWindow()
                side_scroll.set_size_request(220, -1)
                self.cat_list = Gtk.ListBox()
                for cat in self.model.categories:
                    row = Gtk.ListBoxRow()
                    row.cat_name = cat
                    lbl = Gtk.Label(label=f"📦 {cat}", xalign=0)
                    row.add(lbl)
                    self.cat_list.add(row)
                self.cat_list.connect("row-selected", self.on_cat_selected)
                side_scroll.add(self.cat_list)
                paned.pack1(side_scroll, False, False)

                # Main Grid
                self.content_scroll = Gtk.ScrolledWindow()
                self.grid_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
                self.grid_box.set_margin_start(16)
                self.grid_box.set_margin_end(16)
                self.grid_box.set_margin_top(16)
                self.content_scroll.add(self.grid_box)
                paned.pack2(self.content_scroll, True, False)

                self.populate_category("Featured")

            def on_cat_selected(self, listbox, row):
                if row:
                    self.populate_category(row.cat_name)

            def on_search(self, entry):
                q = entry.get_text()
                results = self.model.search(q)
                self.render_apps(results, f"Search Results for '{q}'")

            def populate_category(self, cat):
                apps = self.model.get_apps_by_category(cat)
                self.render_apps(apps, cat)

            def render_apps(self, apps, title):
                for child in self.grid_box.get_children():
                    self.grid_box.remove(child)

                title_lbl = Gtk.Label(label=f"<b>{title}</b>", use_markup=True, xalign=0)
                self.grid_box.pack_start(title_lbl, False, False, 6)

                for app in apps:
                    card = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
                    lbl_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
                    name_lbl = Gtk.Label(label=f"<b>{app.get('name', app.get('id'))}</b>", use_markup=True, xalign=0)
                    summary_lbl = Gtk.Label(label=app.get("summary", "")[:70], xalign=0)
                    lbl_box.pack_start(name_lbl, False, False, 0)
                    lbl_box.pack_start(summary_lbl, False, False, 0)
                    card.pack_start(lbl_box, True, True, 0)

                    btn = Gtk.Button(label="Installed" if app.get("installed") else "Install")
                    card.pack_end(btn, False, False, 0)
                    self.grid_box.pack_start(card, False, False, 0)

                self.grid_box.show_all()

        if os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"):
            win = SoftwareHubWindow(hub)
            win.connect("destroy", Gtk.main_quit)
            win.show_all()
            Gtk.main()
    except Exception as e:
        print(f"[aether-software] Running in headless mode ({e})")

if __name__ == "__main__":
    main()
