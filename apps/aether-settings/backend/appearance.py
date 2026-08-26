#!/usr/bin/env python3
"""
AetherOS Appearance & Themes Settings Backend
Manages Dark/Light mode, accent colors, wallpapers, and font scaling via gsettings and swaybg.
"""

import os
import subprocess
import shutil
from typing import Dict, Any, List

ACCENT_COLORS = {
    "cyan": "#00D2FF",
    "blue": "#3B82F6",
    "indigo": "#6366F1",
    "purple": "#A855F7",
    "emerald": "#10B981",
    "rose": "#F43F5E",
    "orange": "#F97316"
}

WALLPAPERS = [
    {"id": "solstice-dark", "name": "Solstice Dark", "path": "/usr/share/backgrounds/aether/wallpaper-solstice-dark.svg"},
    {"id": "solstice-light", "name": "Solstice Light", "path": "/usr/share/backgrounds/aether/wallpaper-solstice-light.svg"}
]

class AppearanceBackend:
    @staticmethod
    def get_appearance_state() -> Dict[str, Any]:
        return {
            "dark_mode": True,
            "accent_color": "cyan",
            "accent_hex": ACCENT_COLORS["cyan"],
            "current_wallpaper": WALLPAPERS[0]["path"],
            "wallpapers": WALLPAPERS,
            "accent_colors": ACCENT_COLORS,
            "font_size_pt": 11,
            "font_scaling": 1.0
        }

    @staticmethod
    def set_theme_mode(dark: bool) -> bool:
        theme_name = "Aether-Dark" if dark else "Aether-Light"
        wall_file = "wallpaper-solstice-dark.svg" if dark else "wallpaper-solstice-light.svg"
        if shutil.which("gsettings"):
            try:
                subprocess.run(["gsettings", "set", "org.gnome.desktop.interface", "color-scheme", "prefer-dark" if dark else "prefer-light"], capture_output=True)
                subprocess.run(["gsettings", "set", "org.gnome.desktop.interface", "gtk-theme", theme_name], capture_output=True)
            except Exception:
                pass
        if shutil.which("swaybg"):
            try:
                subprocess.run(["swaybg", "-i", f"/usr/share/backgrounds/aether/{wall_file}", "-m", "fill"], capture_output=True)
            except Exception:
                pass
        return True

    @staticmethod
    def set_wallpaper(wallpaper_path: str) -> bool:
        if shutil.which("swaybg"):
            try:
                subprocess.run(["swaybg", "-i", wallpaper_path, "-m", "fill"], capture_output=True)
                return True
            except Exception:
                return False
        return True
