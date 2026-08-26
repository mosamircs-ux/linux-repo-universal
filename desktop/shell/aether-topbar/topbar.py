#!/usr/bin/env python3
"""
AetherOS Top Panel (aether-topbar)
Modular top status panel providing Activities launcher, workspace pager, dynamic clock/calendar,
system status indicators (Network, Audio, Bluetooth, Battery), and Quick Settings trigger.
"""

import os
import sys
import time
import datetime
import subprocess
from typing import Dict, Any, List

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

class AetherTopBarModel:
    def __init__(self):
        self.active_workspace = 1
        self.total_workspaces = 4
        self.calendar_open = False
        self.active_window_title = "Desktop"
        self.network_status = {
            "type": "wifi",
            "connected": True,
            "ssid": "AetherNet-5G",
            "signal_percent": 85
        }
        self.audio_status = {
            "volume_percent": 75,
            "muted": False
        }
        self.battery_status = {
            "present": True,
            "percentage": 92,
            "charging": False,
            "time_remaining": "4h 15m"
        }
        self.bluetooth_status = {
            "enabled": True,
            "connected_devices": 1
        }
        self.unread_notifications_count = 0

    def get_status_payload(self) -> Dict[str, Any]:
        now = datetime.datetime.now()
        return {
            "time_str": now.strftime("%H:%M"),
            "date_str": now.strftime("%a, %b %d"),
            "full_date_str": now.strftime("%A, %B %d, %Y"),
            "active_workspace": self.active_workspace,
            "total_workspaces": self.total_workspaces,
            "active_window_title": self.active_window_title,
            "network": self.network_status,
            "audio": self.audio_status,
            "battery": self.battery_status,
            "bluetooth": self.bluetooth_status,
            "unread_notifications": self.unread_notifications_count,
            "calendar_open": self.calendar_open
        }

    def switch_workspace(self, workspace_num: int) -> bool:
        if 1 <= workspace_num <= self.total_workspaces:
            self.active_workspace = workspace_num
            # Notify Wayfire/Labwc via IPC or keybinding simulation if available
            return True
        return False

    def toggle_calendar(self) -> bool:
        self.calendar_open = not self.calendar_open
        return self.calendar_open

    def set_active_window(self, title: str) -> None:
        self.active_window_title = title or "Desktop"

    def set_volume(self, percent: int, muted: bool = False) -> None:
        self.audio_status["volume_percent"] = max(0, min(100, percent))
        self.audio_status["muted"] = muted

    def set_network(self, net_type: str, connected: bool, ssid: str = "") -> None:
        self.network_status["type"] = net_type
        self.network_status["connected"] = connected
        self.network_status["ssid"] = ssid

def main():
    bar = AetherTopBarModel()
    print("[aether-topbar] Initialized status payload:")
    print(bar.get_status_payload())

    # If PyGObject and GTK are available, launch GTK bar
    try:
        import gi
        gi.require_version("Gtk", "3.0")
        from gi.repository import Gtk, GLib, Gdk

        class TopBarWindow(Gtk.Window):
            def __init__(self, model):
                super().__init__(type=Gtk.WindowType.TOPLEVEL)
                self.model = model
                self.set_title("aether-topbar")
                self.set_decorated(False)
                self.set_app_paintable(True)
                self.set_default_size(1920, 32)
                self.set_keep_above(True)

                # Visual CSS
                css_provider = Gtk.CssProvider()
                css = """
                window {
                    background-color: rgba(11, 15, 25, 0.92);
                    color: #f8fafc;
                    font-family: 'Inter', sans-serif;
                    font-size: 13px;
                }
                button {
                    background: transparent;
                    border: none;
                    color: #f8fafc;
                    padding: 4px 10px;
                    border-radius: 6px;
                }
                button:hover {
                    background-color: rgba(255, 255, 255, 0.12);
                }
                .pill {
                    background-color: rgba(255, 255, 255, 0.08);
                    border-radius: 12px;
                    padding: 2px 10px;
                }
                .active-ws {
                    background-color: #00d2ff;
                    color: #0b0f19;
                    font-weight: bold;
                }
                """
                css_provider.load_from_data(css.encode())
                Gtk.StyleContext.add_provider_for_screen(
                    Gdk.Screen.get_default(),
                    css_provider,
                    Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
                )

                # Layout
                box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
                box.set_margin_start(12)
                box.set_margin_end(12)
                self.add(box)

                # Left: Activities + Workspace Pager
                left_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
                act_btn = Gtk.Button(label="Activities")
                act_btn.connect("clicked", lambda b: subprocess.Popen(["python3", "/usr/lib/aether/shell/launcher.py"]))
                left_box.pack_start(act_btn, False, False, 0)

                for i in range(1, 5):
                    ws_btn = Gtk.Button(label=str(i))
                    if i == 1:
                        ws_btn.get_style_context().add_class("active-ws")
                    left_box.pack_start(ws_btn, False, False, 0)
                box.pack_start(left_box, False, False, 0)

                # Center: Clock Pill
                center_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
                self.clock_label = Gtk.Label(label=datetime.datetime.now().strftime("%a %b %d  %H:%M"))
                self.clock_label.get_style_context().add_class("pill")
                center_box.pack_start(self.clock_label, True, True, 0)
                box.set_center_widget(center_box)

                # Right: Status Icons + Quick Settings
                right_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
                qs_btn = Gtk.Button(label="📶  🔊 75%  🔋 92%")
                qs_btn.get_style_context().add_class("pill")
                qs_btn.connect("clicked", lambda b: subprocess.Popen(["python3", "/usr/lib/aether/shell/quicksettings.py"]))
                right_box.pack_end(qs_btn, False, False, 0)
                box.pack_end(right_box, False, False, 0)

                # Periodic clock update
                GLib.timeout_add_seconds(1, self.update_clock)

            def update_clock(self):
                self.clock_label.set_text(datetime.datetime.now().strftime("%a %b %d  %H:%M"))
                return True

        if os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"):
            win = TopBarWindow(bar)
            win.connect("destroy", Gtk.main_quit)
            win.show_all()
            Gtk.main()
    except Exception as e:
        print(f"[aether-topbar] Running in headless/model mode ({e})")

if __name__ == "__main__":
    main()
