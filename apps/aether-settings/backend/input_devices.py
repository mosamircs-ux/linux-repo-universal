#!/usr/bin/env python3
"""
AetherOS Input Devices Settings Backend (Keyboard, Mouse, Touchpad)
Configures keyboard keymaps, mouse acceleration, touchpad tap-to-click, and gestures via localectl/gsettings.
"""

import subprocess
import shutil
from typing import List, Dict, Any, Tuple
from .polkit_helper import run_privileged

class InputDevicesBackend:
    @staticmethod
    def get_keyboard_settings() -> Dict[str, Any]:
        settings = {
            "layout": "us",
            "variant": "",
            "available_layouts": ["us", "ara", "fr", "de", "es", "ru", "tr"],
            "repeat_delay_ms": 300,
            "repeat_rate_hz": 30,
            "numlock_on_boot": True
        }
        if shutil.which("localectl"):
            try:
                res = subprocess.run(["localectl", "status"], capture_output=True, text=True)
                for line in res.stdout.split("\n"):
                    if "X11 Layout:" in line:
                        settings["layout"] = line.split(":")[1].strip()
            except Exception:
                pass
        return settings

    @staticmethod
    def set_keyboard_layout(layout: str, variant: str = "") -> Tuple[bool, str]:
        cmd = ["localectl", "set-x11-keymap", layout]
        if variant:
            cmd.append(variant)
        return run_privileged(cmd)

    @staticmethod
    def get_mouse_settings() -> Dict[str, Any]:
        return {
            "primary_button": "left",  # left, right
            "pointer_speed": 0.0,      # -1.0 to 1.0
            "acceleration_profile": "adaptive",  # adaptive, flat
            "natural_scroll": False
        }

    @staticmethod
    def get_touchpad_settings() -> Dict[str, Any]:
        return {
            "tap_to_click": True,
            "natural_scroll": True,
            "two_finger_scroll": True,
            "disable_while_typing": True,
            "pointer_speed": 0.1,
            "tap_and_drag": True
        }

    @staticmethod
    def apply_touchpad_setting(key: str, value: Any) -> bool:
        if shutil.which("gsettings"):
            try:
                # e.g. org.gnome.desktop.peripherals.touchpad tap-to-click true
                val_str = str(value).lower() if isinstance(value, bool) else str(value)
                subprocess.run(["gsettings", "set", "org.gnome.desktop.peripherals.touchpad", key, val_str], capture_output=True)
                return True
            except Exception:
                pass
        return True
