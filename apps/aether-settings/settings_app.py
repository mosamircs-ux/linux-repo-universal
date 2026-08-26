#!/usr/bin/env python3
"""
AetherOS System Settings Center
Comprehensive control panel for Display, Appearance, Language/RTL, Network,
Bluetooth, Sound, Users, Power, and System Diagnostics.
Supports English (en) and Arabic (ar) with full RTL text mirroring.
"""

import os
import sys
import json
import subprocess
from typing import Dict, Any, List

TRANSLATIONS = {
    "en": {
        "title": "AetherOS Settings",
        "display": "Display & Screens",
        "appearance": "Appearance & Themes",
        "language": "Language & Region",
        "network": "Network & Wi-Fi",
        "bluetooth": "Bluetooth Devices",
        "sound": "Sound & Audio",
        "users": "Users & Accounts",
        "power": "Power & Battery",
        "about": "About System",
        "dark_mode": "Dark Mode",
        "accent_color": "Accent Color",
        "resolution": "Resolution",
        "refresh_rate": "Refresh Rate",
        "scaling": "Display Scaling",
        "volume": "Master Volume",
        "rollback_ready": "Snapshot Rollback Available",
        "save": "Save Changes",
        "apply": "Apply",
    },
    "ar": {
        "title": "إعدادات نظام أيثر (AetherOS)",
        "display": "العرض والشاشات",
        "appearance": "المظهر والسمات",
        "language": "اللغة والمنطقة",
        "network": "الشبكة والواي فاي",
        "bluetooth": "أجهزة البلوتوث",
        "sound": "الصوت والوسائط",
        "users": "المستخدمون والحسابات",
        "power": "الطاقة والبطارية",
        "about": "حول النظام",
        "dark_mode": "الوضع الداكن",
        "accent_color": "لون التمييز",
        "resolution": "دقة الشاشة",
        "refresh_rate": "معدل التحديث",
        "scaling": "تحجيم الواجهة",
        "volume": "مستوى الصوت الرئيسي",
        "rollback_ready": "إمكانية استعادة اللقطة جاهزة",
        "save": "حفظ التغييرات",
        "apply": "تطبيق",
    }
}

class AetherSettingsModel:
    def __init__(self, config_path: str = None):
        self.config_path = config_path or os.path.expanduser("~/.config/aether/settings.json")
        self.language = "en"
        self.dark_mode = True
        self.accent_color = "#00D2FF"
        self.dock_position = "left"
        self.display_resolution = "1920x1080"
        self.refresh_rate = "60Hz"
        self.scale_factor = 1.0
        self.volume_level = 80
        self.load_settings()

    def get_text(self, key: str) -> str:
        lang_dict = TRANSLATIONS.get(self.language, TRANSLATIONS["en"])
        return lang_dict.get(key, key)

    def is_rtl(self) -> bool:
        return self.language == "ar"

    def load_settings(self) -> None:
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.language = data.get("language", self.language)
                    self.dark_mode = data.get("dark_mode", self.dark_mode)
                    self.accent_color = data.get("accent_color", self.accent_color)
                    self.dock_position = data.get("dock_position", self.dock_position)
                    self.display_resolution = data.get("display_resolution", self.display_resolution)
                    self.refresh_rate = data.get("refresh_rate", self.refresh_rate)
                    self.scale_factor = data.get("scale_factor", self.scale_factor)
                    self.volume_level = data.get("volume_level", self.volume_level)
            except Exception as e:
                print(f"[Settings] Error loading config: {e}", file=sys.stderr)

    def save_settings(self) -> bool:
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        data = {
            "language": self.language,
            "dark_mode": self.dark_mode,
            "accent_color": self.accent_color,
            "dock_position": self.dock_position,
            "display_resolution": self.display_resolution,
            "refresh_rate": self.refresh_rate,
            "scale_factor": self.scale_factor,
            "volume_level": self.volume_level,
        }
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"[Settings] Error saving config: {e}", file=sys.stderr)
            return False

    def set_language(self, lang_code: str) -> bool:
        if lang_code in TRANSLATIONS:
            self.language = lang_code
            self.save_settings()
            return True
        return False

    def get_system_info(self) -> Dict[str, str]:
        return {
            "os_name": "AetherOS",
            "version": "1.0.0 LTS (Solstice)",
            "kernel": os.uname().release,
            "arch": os.uname().machine,
            "desktop": "Wayland (Aether Shell)",
            "compositor": "Wayfire / Labwc",
            "audio_engine": "PipeWire 1.0+",
            "package_manager": "APT & Flatpak",
        }

def main():
    settings = AetherSettingsModel()
    print("========================================")
    print(settings.get_text("title"))
    print(f"Current Language: {settings.language} (RTL: {settings.is_rtl()})")
    print("System Diagnostics:")
    for k, v in settings.get_system_info().items():
        print(f"  - {k}: {v}")
    print("========================================")

if __name__ == "__main__":
    main()
