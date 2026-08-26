#!/usr/bin/env python3
"""
AetherOS Quick Settings (aether-quicksettings)
Unified slide-out control center providing Network, Bluetooth, Audio Volume/Mic sliders,
Brightness, Dark/Light Mode toggle, Night Light, Battery reporting, and Power session controls.
"""

import os
import sys
import json
import subprocess
from typing import Dict, Any, Optional

class QuickSettingsState:
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or os.path.expanduser("~/.config/aether/quicksettings.json")
        self.wifi_enabled = True
        self.bluetooth_enabled = True
        self.dark_mode = True
        self.night_light = False
        self.airplane_mode = False
        self.dnd_enabled = False
        self.volume = 75
        self.microphone_volume = 80
        self.brightness = 85
        self.power_profile = "balanced"  # performance, balanced, power-saver
        self.battery_level = 92
        self.battery_charging = False
        self.load_state()

    def load_state(self) -> None:
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.wifi_enabled = data.get("wifi_enabled", self.wifi_enabled)
                    self.bluetooth_enabled = data.get("bluetooth_enabled", self.bluetooth_enabled)
                    self.dark_mode = data.get("dark_mode", self.dark_mode)
                    self.night_light = data.get("night_light", self.night_light)
                    self.volume = data.get("volume", self.volume)
                    self.brightness = data.get("brightness", self.brightness)
                    self.power_profile = data.get("power_profile", self.power_profile)
            except Exception:
                pass

    def save_state(self) -> None:
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump({
                    "wifi_enabled": self.wifi_enabled,
                    "bluetooth_enabled": self.bluetooth_enabled,
                    "dark_mode": self.dark_mode,
                    "night_light": self.night_light,
                    "volume": self.volume,
                    "brightness": self.brightness,
                    "power_profile": self.power_profile
                }, f, indent=2)
        except Exception:
            pass

    def toggle_wifi(self) -> bool:
        self.wifi_enabled = not self.wifi_enabled
        cmd = ["nmcli", "radio", "wifi", "on" if self.wifi_enabled else "off"]
        try:
            subprocess.run(cmd, capture_output=True)
        except Exception:
            pass
        self.save_state()
        return self.wifi_enabled

    def toggle_bluetooth(self) -> bool:
        self.bluetooth_enabled = not self.bluetooth_enabled
        cmd = ["bluetoothctl", "power", "on" if self.bluetooth_enabled else "off"]
        try:
            subprocess.run(cmd, capture_output=True)
        except Exception:
            pass
        self.save_state()
        return self.bluetooth_enabled

    def toggle_dark_mode(self) -> bool:
        self.dark_mode = not self.dark_mode
        theme_name = "Aether-Dark" if self.dark_mode else "Aether-Light"
        wall_file = "wallpaper-solstice-dark.svg" if self.dark_mode else "wallpaper-solstice-light.svg"
        
        # Set GTK theme via gsettings
        try:
            subprocess.run(["gsettings", "set", "org.gnome.desktop.interface", "color-scheme", "prefer-dark" if self.dark_mode else "prefer-light"], capture_output=True)
            subprocess.run(["gsettings", "set", "org.gnome.desktop.interface", "gtk-theme", theme_name], capture_output=True)
            # Update wallpaper
            subprocess.run(["swaybg", "-i", f"/usr/share/backgrounds/aether/{wall_file}", "-m", "fill"], capture_output=True)
        except Exception:
            pass
        self.save_state()
        return self.dark_mode

    def toggle_night_light(self) -> bool:
        self.night_light = not self.night_light
        if self.night_light:
            try:
                subprocess.Popen(["wlsunset", "-t", "4000", "-T", "6500"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception:
                pass
        else:
            try:
                subprocess.run(["pkill", "-f", "wlsunset"], capture_output=True)
            except Exception:
                pass
        self.save_state()
        return self.night_light

    def set_volume(self, value: int) -> int:
        self.volume = max(0, min(100, int(value)))
        try:
            subprocess.run(["wpctl", "set-volume", "@DEFAULT_AUDIO_SINK@", f"{self.volume / 100:.2f}"], capture_output=True)
        except Exception:
            pass
        self.save_state()
        return self.volume

    def set_brightness(self, value: int) -> int:
        self.brightness = max(1, min(100, int(value)))
        try:
            subprocess.run(["brightnessctl", "set", f"{self.brightness}%"], capture_output=True)
        except Exception:
            pass
        self.save_state()
        return self.brightness

    def set_power_profile(self, profile: str) -> str:
        if profile in ("performance", "balanced", "power-saver"):
            self.power_profile = profile
            try:
                subprocess.run(["powerprofilesctl", "set", profile], capture_output=True)
            except Exception:
                pass
            self.save_state()
        return self.power_profile

    # Power Actions
    def action_lock(self) -> None:
        try:
            subprocess.Popen(["swaylock", "-f", "-c", "0B0F19", "--indicator-radius", "100", "--ring-color", "00D2FF"])
        except Exception:
            pass

    def action_sleep(self) -> None:
        try:
            subprocess.run(["systemctl", "suspend"], capture_output=True)
        except Exception:
            pass

    def action_logout(self) -> None:
        try:
            subprocess.run(["loginctl", "terminate-user", os.environ.get("USER", "")], capture_output=True)
        except Exception:
            pass

    def action_restart(self) -> None:
        try:
            subprocess.run(["systemctl", "reboot"], capture_output=True)
        except Exception:
            pass

    def action_shutdown(self) -> None:
        try:
            subprocess.run(["systemctl", "poweroff"], capture_output=True)
        except Exception:
            pass

def main():
    qs = QuickSettingsState()
    print("[aether-quicksettings] Active state:")
    print(json.dumps({
        "wifi": qs.wifi_enabled,
        "bluetooth": qs.bluetooth_enabled,
        "dark_mode": qs.dark_mode,
        "night_light": qs.night_light,
        "volume": qs.volume,
        "brightness": qs.brightness,
        "power_profile": qs.power_profile
    }, indent=2))

    try:
        import gi
        gi.require_version("Gtk", "3.0")
        from gi.repository import Gtk, Gdk

        class QuickSettingsWindow(Gtk.Window):
            def __init__(self, state):
                super().__init__(type=Gtk.WindowType.TOPLEVEL)
                self.state = state
                self.set_title("aether-quicksettings")
                self.set_decorated(False)
                self.set_default_size(360, 480)
                self.set_position(Gtk.WindowPosition.NONE)
                self.set_keep_above(True)

                css_provider = Gtk.CssProvider()
                css = """
                window {
                    background-color: rgba(11, 15, 25, 0.96);
                    border: 1px solid rgba(255, 255, 255, 0.12);
                    border-radius: 16px;
                }
                .toggle-card {
                    background-color: rgba(255, 255, 255, 0.07);
                    border: 1px solid transparent;
                    color: #f8fafc;
                    padding: 12px;
                    border-radius: 12px;
                    font-size: 13px;
                }
                .toggle-card:checked, .toggle-card.active {
                    background-color: #00d2ff;
                    color: #0b0f19;
                    font-weight: bold;
                }
                .power-btn {
                    background-color: rgba(255, 255, 255, 0.08);
                    border: none;
                    border-radius: 50%;
                    min-width: 40px;
                    min-height: 40px;
                    color: #f8fafc;
                }
                .power-btn:hover {
                    background-color: rgba(239, 68, 68, 0.35);
                    color: #ef4444;
                }
                scale trough {
                    background-color: rgba(255, 255, 255, 0.15);
                    border-radius: 4px;
                    min-height: 8px;
                }
                scale highlight {
                    background-color: #00d2ff;
                    border-radius: 4px;
                }
                """
                css_provider.load_from_data(css.encode())
                Gtk.StyleContext.add_provider_for_screen(
                    Gdk.Screen.get_default(),
                    css_provider,
                    Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
                )

                main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
                main_box.set_margin_top(16)
                main_box.set_margin_bottom(16)
                main_box.set_margin_start(18)
                main_box.set_margin_end(18)
                self.add(main_box)

                # Quick Toggles Grid (2x3)
                grid = Gtk.Grid()
                grid.set_column_spacing(10)
                grid.set_row_spacing(10)
                grid.set_column_homogeneous(True)

                self.btn_wifi = Gtk.Button(label="📶 Wi-Fi")
                self.btn_wifi.get_style_context().add_class("toggle-card")
                if self.state.wifi_enabled:
                    self.btn_wifi.get_style_context().add_class("active")
                self.btn_wifi.connect("clicked", self.on_toggle_wifi)
                grid.attach(self.btn_wifi, 0, 0, 1, 1)

                self.btn_bt = Gtk.Button(label="ᛒ Bluetooth")
                self.btn_bt.get_style_context().add_class("toggle-card")
                if self.state.bluetooth_enabled:
                    self.btn_bt.get_style_context().add_class("active")
                self.btn_bt.connect("clicked", self.on_toggle_bt)
                grid.attach(self.btn_bt, 1, 0, 1, 1)

                self.btn_theme = Gtk.Button(label="🌙 Dark Mode" if self.state.dark_mode else "☀️ Light Mode")
                self.btn_theme.get_style_context().add_class("toggle-card")
                self.btn_theme.connect("clicked", self.on_toggle_theme)
                grid.attach(self.btn_theme, 0, 1, 1, 1)

                self.btn_night = Gtk.Button(label="👁️ Night Light")
                self.btn_night.get_style_context().add_class("toggle-card")
                if self.state.night_light:
                    self.btn_night.get_style_context().add_class("active")
                self.btn_night.connect("clicked", self.on_toggle_night)
                grid.attach(self.btn_night, 1, 1, 1, 1)

                main_box.pack_start(grid, False, False, 0)

                # Audio Volume Slider
                vol_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
                vol_lbl = Gtk.Label(label="🔊")
                vol_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 1)
                vol_scale.set_value(self.state.volume)
                vol_scale.connect("value-changed", lambda s: self.state.set_volume(int(s.get_value())))
                vol_box.pack_start(vol_lbl, False, False, 0)
                vol_box.pack_start(vol_scale, True, True, 0)
                main_box.pack_start(vol_box, False, False, 0)

                # Brightness Slider
                bri_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
                bri_lbl = Gtk.Label(label="☀️")
                bri_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 1, 100, 1)
                bri_scale.set_value(self.state.brightness)
                bri_scale.connect("value-changed", lambda s: self.state.set_brightness(int(s.get_value())))
                bri_box.pack_start(bri_lbl, False, False, 0)
                bri_box.pack_start(bri_scale, True, True, 0)
                main_box.pack_start(bri_box, False, False, 0)

                # Power & Session Controls Footer
                sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
                main_box.pack_start(sep, False, False, 4)

                footer = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
                
                # Lock
                btn_lock = Gtk.Button(label="🔒")
                btn_lock.get_style_context().add_class("power-btn")
                btn_lock.set_tooltip_text("Lock Screen (Super+L)")
                btn_lock.connect("clicked", lambda b: (self.state.action_lock(), self.destroy()))
                footer.pack_start(btn_lock, False, False, 0)

                # Sleep
                btn_sleep = Gtk.Button(label="💤")
                btn_sleep.get_style_context().add_class("power-btn")
                btn_sleep.set_tooltip_text("Suspend to RAM")
                btn_sleep.connect("clicked", lambda b: (self.state.action_sleep(), self.destroy()))
                footer.pack_start(btn_sleep, False, False, 0)

                # Restart
                btn_reboot = Gtk.Button(label="🔄")
                btn_reboot.get_style_context().add_class("power-btn")
                btn_reboot.set_tooltip_text("Restart System")
                btn_reboot.connect("clicked", lambda b: (self.state.action_restart(), self.destroy()))
                footer.pack_start(btn_reboot, False, False, 0)

                # Shutdown
                btn_power = Gtk.Button(label="⏻")
                btn_power.get_style_context().add_class("power-btn")
                btn_power.set_tooltip_text("Power Off")
                btn_power.connect("clicked", lambda b: (self.state.action_shutdown(), self.destroy()))
                footer.pack_end(btn_power, False, False, 0)

                main_box.pack_end(footer, False, False, 0)

            def on_toggle_wifi(self, btn):
                active = self.state.toggle_wifi()
                if active:
                    btn.get_style_context().add_class("active")
                else:
                    btn.get_style_context().remove_class("active")

            def on_toggle_bt(self, btn):
                active = self.state.toggle_bluetooth()
                if active:
                    btn.get_style_context().add_class("active")
                else:
                    btn.get_style_context().remove_class("active")

            def on_toggle_theme(self, btn):
                dark = self.state.toggle_dark_mode()
                btn.set_label("🌙 Dark Mode" if dark else "☀️ Light Mode")

            def on_toggle_night(self, btn):
                active = self.state.toggle_night_light()
                if active:
                    btn.get_style_context().add_class("active")
                else:
                    btn.get_style_context().remove_class("active")

        if os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"):
            win = QuickSettingsWindow(qs)
            win.connect("destroy", Gtk.main_quit)
            win.show_all()
            Gtk.main()
    except Exception as e:
        print(f"[aether-quicksettings] Running in headless mode ({e})")

if __name__ == "__main__":
    main()
