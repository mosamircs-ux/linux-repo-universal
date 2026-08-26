#!/usr/bin/env python3
"""
AetherOS System Settings Center (aether-settings)
Complete graphical control center featuring 26 dedicated sections, direct Linux system API
integrations, secure Polkit escalation, display rollback watchdog, and full English/Arabic RTL support.
"""

import os
import sys
import json
import subprocess
from typing import Dict, Any, List, Optional

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(REPO_ROOT, "apps", "aether-settings"))

from backend.network import NetworkManagerBackend
from backend.bluetooth import BluetoothBackend
from backend.display import DisplayBackend
from backend.sound import SoundBackend
from backend.input_devices import InputDevicesBackend
from backend.printers import PrintersBackend
from backend.users import UsersBackend
from backend.security import SecurityPrivacyBackend
from backend.applications import ApplicationsBackend
from backend.datetime_locale import DateTimeLocaleBackend
from backend.power import PowerBackend
from backend.storage import StorageBackend
from backend.backup import BackupBackend
from backend.updates import UpdatesBackend
from backend.appearance import AppearanceBackend
from backend.accessibility import AccessibilityBackend
from backend.notifications import NotificationsBackend
from backend.about import AboutBackend

SECTIONS = [
    {"id": "wifi", "icon": "network-wireless", "category": "Connectivity", "name_en": "Wi-Fi", "name_ar": "الواي فاي"},
    {"id": "ethernet", "icon": "network-wired", "category": "Connectivity", "name_en": "Ethernet", "name_ar": "الشبكة السلكية"},
    {"id": "vpn", "icon": "network-vpn", "category": "Connectivity", "name_en": "VPN", "name_ar": "الشبكة الافتراضية (VPN)"},
    {"id": "bluetooth", "icon": "bluetooth", "category": "Connectivity", "name_en": "Bluetooth", "name_ar": "البلوتوث"},
    {"id": "display", "icon": "video-display", "category": "Hardware", "name_en": "Display", "name_ar": "العرض والشاشات"},
    {"id": "sound", "icon": "audio-volume-high", "category": "Hardware", "name_en": "Sound", "name_ar": "الصوت والوسائط"},
    {"id": "keyboard", "icon": "input-keyboard", "category": "Hardware", "name_en": "Keyboard", "name_ar": "لوحة المفاتيح"},
    {"id": "mouse", "icon": "input-mouse", "category": "Hardware", "name_en": "Mouse", "name_ar": "الفأرة"},
    {"id": "touchpad", "icon": "input-touchpad", "category": "Hardware", "name_en": "Touchpad", "name_ar": "لوحة اللمس"},
    {"id": "printers", "icon": "printer", "category": "Hardware", "name_en": "Printers", "name_ar": "الطابعات"},
    {"id": "users", "icon": "system-users", "category": "Personal & Accounts", "name_en": "Users", "name_ar": "المستخدمون والحسابات"},
    {"id": "privacy", "icon": "security-high", "category": "Personal & Accounts", "name_en": "Privacy", "name_ar": "الخصوصية والأذونات"},
    {"id": "security", "icon": "emblem-readonly", "category": "Personal & Accounts", "name_en": "Security", "name_ar": "الأمان وجدار الحماية"},
    {"id": "applications", "icon": "applications-other", "category": "Personal & Accounts", "name_en": "Applications", "name_ar": "التطبيقات المثبتة"},
    {"id": "default_apps", "icon": "application-default-icon", "category": "Personal & Accounts", "name_en": "Default Applications", "name_ar": "التطبيقات الافتراضية"},
    {"id": "notifications", "icon": "preferences-desktop-notification", "category": "Personal & Accounts", "name_en": "Notifications", "name_ar": "الإشعارات"},
    {"id": "appearance", "icon": "preferences-desktop-theme", "category": "Personalization", "name_en": "Appearance", "name_ar": "المظهر والسمات"},
    {"id": "accessibility", "icon": "preferences-desktop-accessibility", "category": "Personalization", "name_en": "Accessibility", "name_ar": "إمكانية الوصول"},
    {"id": "datetime", "icon": "preferences-system-time", "category": "Personalization", "name_en": "Date & Time", "name_ar": "التاريخ والوقت"},
    {"id": "language", "icon": "preferences-desktop-locale", "category": "Personalization", "name_en": "Language", "name_ar": "اللغة"},
    {"id": "region", "icon": "preferences-desktop-locale", "category": "Personalization", "name_en": "Region", "name_ar": "المنطقة والتنسيقات"},
    {"id": "power", "icon": "battery", "category": "System", "name_en": "Power", "name_ar": "الطاقة والبطارية"},
    {"id": "storage", "icon": "drive-harddisk", "category": "System", "name_en": "Storage", "name_ar": "التخزين والأقراص"},
    {"id": "backup", "icon": "system-file-manager", "category": "System", "name_en": "Backup", "name_ar": "النسخ الاحتياطي والاستعادة"},
    {"id": "updates", "icon": "software-update-available", "category": "System", "name_en": "Updates", "name_ar": "تحديثات النظام"},
    {"id": "about", "icon": "help-about", "category": "System", "name_en": "About", "name_ar": "حول النظام"}
]

TRANSLATIONS = {
    "en": {
        "title": "AetherOS Settings",
        "search_placeholder": "Search settings...",
        "save": "Save Changes",
        "apply": "Apply",
        "cancel": "Cancel",
        "confirm": "Confirm",
        "status": "Status",
        "enabled": "Enabled",
        "disabled": "Disabled",
        "refresh": "Refresh",
        "rollback_ready": "Snapshot Rollback Available",
    },
    "ar": {
        "title": "إعدادات نظام أيثر (AetherOS)",
        "search_placeholder": "البحث في الإعدادات...",
        "save": "حفظ التغييرات",
        "apply": "تطبيق",
        "cancel": "إلغاء",
        "confirm": "تأكيد",
        "status": "الحالة",
        "enabled": "مفعل",
        "disabled": "معطل",
        "refresh": "تحديث",
        "rollback_ready": "إمكانية استعادة اللقطة جاهزة",
    }
}

class AetherSettingsModel:
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or os.path.expanduser("~/.config/aether/settings.json")
        self.language = "en"
        self.dark_mode = True
        self.accent_color = "#00D2FF"
        self.dock_position = "left"
        self.display_resolution = "1920x1080"
        self.refresh_rate = "60Hz"
        self.scale_factor = 1.0
        self.volume_level = 80
        self.active_section = "wifi"
        
        # Subsystem Backends
        self.network = NetworkManagerBackend()
        self.bluetooth = BluetoothBackend()
        self.display = DisplayBackend()
        self.sound = SoundBackend()
        self.input_devices = InputDevicesBackend()
        self.printers = PrintersBackend()
        self.users = UsersBackend()
        self.security = SecurityPrivacyBackend()
        self.applications = ApplicationsBackend()
        self.datetime_locale = DateTimeLocaleBackend()
        self.power = PowerBackend()
        self.storage = StorageBackend()
        self.backup = BackupBackend()
        self.updates = UpdatesBackend()
        self.appearance = AppearanceBackend()
        self.accessibility = AccessibilityBackend()
        self.notifications = NotificationsBackend()
        self.about = AboutBackend()

        self.load_settings()

    def get_text(self, key: str) -> str:
        lang_dict = TRANSLATIONS.get(self.language, TRANSLATIONS["en"])
        return lang_dict.get(key, key)

    def is_rtl(self) -> bool:
        return self.language == "ar"

    def set_language(self, lang_code: str) -> bool:
        if lang_code in ("en", "ar"):
            self.language = lang_code
            self.save_settings()
            return True
        return False

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
                    self.active_section = data.get("active_section", self.active_section)
            except Exception:
                pass

    def save_settings(self) -> bool:
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump({
                    "language": self.language,
                    "dark_mode": self.dark_mode,
                    "accent_color": self.accent_color,
                    "dock_position": self.dock_position,
                    "display_resolution": self.display_resolution,
                    "refresh_rate": self.refresh_rate,
                    "scale_factor": self.scale_factor,
                    "volume_level": self.volume_level,
                    "active_section": self.active_section
                }, f, indent=2, ensure_ascii=False)
            return True
        except Exception:
            return False

    def get_section_data(self, section_id: str) -> Dict[str, Any]:
        if section_id == "wifi":
            return {"status": self.network.get_status(), "networks": self.network.scan_wifi_networks()}
        elif section_id == "ethernet":
            return {"interfaces": self.network.get_ethernet_interfaces()}
        elif section_id == "vpn":
            return {"vpns": self.network.get_vpn_connections()}
        elif section_id == "bluetooth":
            return {"status": self.bluetooth.get_adapter_status(), "devices": self.bluetooth.get_paired_devices()}
        elif section_id == "display":
            return {"displays": self.display.get_displays()}
        elif section_id == "sound":
            return self.sound.get_audio_status()
        elif section_id == "keyboard":
            return self.input_devices.get_keyboard_settings()
        elif section_id == "mouse":
            return self.input_devices.get_mouse_settings()
        elif section_id == "touchpad":
            return self.input_devices.get_touchpad_settings()
        elif section_id == "printers":
            return {"printers": self.printers.get_printers()}
        elif section_id == "users":
            return {"users": self.users.get_users()}
        elif section_id in ("privacy", "security"):
            return self.security.get_security_status()
        elif section_id == "applications":
            return {"apps": self.applications.list_installed_apps()}
        elif section_id == "default_apps":
            return {"defaults": self.applications.get_default_applications()}
        elif section_id == "notifications":
            return self.notifications.get_notification_settings()
        elif section_id == "appearance":
            return self.appearance.get_appearance_state()
        elif section_id == "accessibility":
            return self.accessibility.get_accessibility_settings()
        elif section_id == "datetime":
            return self.datetime_locale.get_datetime_status()
        elif section_id in ("language", "region"):
            return self.datetime_locale.get_locale_status()
        elif section_id == "power":
            return self.power.get_power_status()
        elif section_id == "storage":
            return {"drives": self.storage.get_storage_overview()}
        elif section_id == "backup":
            return {"snapshots": self.backup.get_snapshots()}
        elif section_id == "updates":
            return self.updates.check_updates()
        elif section_id == "about":
            return self.about.get_system_specifications()
        return {}

    def get_system_info(self) -> Dict[str, str]:
        return self.about.get_system_specifications()

def main():
    model = AetherSettingsModel()
    print("================================================================")
    print(f"       {model.get_text('title')} (AetherOS Solstice)           ")
    print("================================================================")
    print(f"Language: {model.language} (RTL: {model.is_rtl()}) | Active Section: {model.active_section}")
    print(f"Indexed Settings Sections: {len(SECTIONS)} sections loaded.")
    for s in SECTIONS:
        name = s["name_ar"] if model.is_rtl() else s["name_en"]
        print(f"  - [{s['category']}] {name} ({s['id']})")
    print("================================================================")

    # Graphical Interface Launch
    try:
        import gi
        gi.require_version("Gtk", "3.0")
        from gi.repository import Gtk, Gdk

        class SettingsWindow(Gtk.Window):
            def __init__(self, model):
                super().__init__(type=Gtk.WindowType.TOPLEVEL)
                self.model = model
                self.set_title(self.model.get_text("title"))
                self.set_default_size(980, 640)
                self.set_position(Gtk.WindowPosition.CENTER)

                # CSS Styling
                css_provider = Gtk.CssProvider()
                css = """
                window {
                    background-color: #0B0F19;
                    color: #F8FAFC;
                    font-family: 'Inter', 'Cairo', sans-serif;
                }
                .sidebar-row {
                    padding: 8px 12px;
                    border-radius: 8px;
                }
                .sidebar-row:selected {
                    background-color: #00D2FF;
                    color: #0B0F19;
                    font-weight: bold;
                }
                .content-box {
                    background-color: #131B2E;
                    border-radius: 12px;
                    padding: 20px;
                }
                """
                css_provider.load_from_data(css.encode())
                Gtk.StyleContext.add_provider_for_screen(
                    Gdk.Screen.get_default(),
                    css_provider,
                    Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
                )

                # HeaderBar
                header = Gtk.HeaderBar()
                header.set_show_close_button(True)
                header.set_title(self.model.get_text("title"))
                self.set_titlebar(header)

                # Main Box
                main_paned = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
                self.add(main_paned)

                # Left: Sidebar
                side_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
                side_box.set_size_request(240, -1)
                side_box.set_margin_start(10)
                side_box.set_margin_end(10)
                side_box.set_margin_top(10)
                side_box.set_margin_bottom(10)

                search_entry = Gtk.SearchEntry()
                search_entry.set_placeholder_text(self.model.get_text("search_placeholder"))
                side_box.pack_start(search_entry, False, False, 0)

                scroll = Gtk.ScrolledWindow()
                scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
                self.listbox = Gtk.ListBox()
                self.listbox.connect("row-selected", self.on_row_selected)
                scroll.add(self.listbox)
                side_box.pack_start(scroll, True, True, 0)
                main_paned.pack1(side_box, False, False)

                # Right: Detail View Container
                self.detail_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
                self.detail_container.set_margin_start(16)
                self.detail_container.set_margin_end(16)
                self.detail_container.set_margin_top(16)
                self.detail_container.set_margin_bottom(16)
                main_paned.pack2(self.detail_container, True, False)

                # Populate Sidebar
                for sec in SECTIONS:
                    name = sec["name_ar"] if self.model.is_rtl() else sec["name_en"]
                    row = Gtk.ListBoxRow()
                    row.sec_id = sec["id"]
                    row.get_style_context().add_class("sidebar-row")
                    lbl = Gtk.Label(label=f"{sec['category']}: {name}", xalign=0)
                    row.add(lbl)
                    self.listbox.add(row)

                self.listbox.select_row(self.listbox.get_row_at_index(0))

            def on_row_selected(self, listbox, row):
                if not row:
                    return
                for child in self.detail_container.get_children():
                    self.detail_container.remove(child)

                sec_id = row.sec_id
                data = self.model.get_section_data(sec_id)

                card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
                card.get_style_context().add_class("content-box")
                title_lbl = Gtk.Label(label=f"<b>{sec_id.upper()} SETTINGS</b>", use_markup=True, xalign=0)
                card.pack_start(title_lbl, False, False, 0)

                info_lbl = Gtk.Label(label=json.dumps(data, indent=2, ensure_ascii=False), xalign=0)
                info_lbl.set_selectable(True)
                card.pack_start(info_lbl, True, True, 0)

                self.detail_container.pack_start(card, True, True, 0)
                self.detail_container.show_all()

        if os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"):
            win = SettingsWindow(model)
            win.connect("destroy", Gtk.main_quit)
            win.show_all()
            Gtk.main()
    except Exception as e:
        print(f"[aether-settings] Running in headless mode ({e})")

if __name__ == "__main__":
    main()
