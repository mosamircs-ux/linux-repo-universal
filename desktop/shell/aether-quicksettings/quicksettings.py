#!/usr/bin/env python3
"""
AetherOS Quick Settings Control Panel Engine
Features: Toggles for Wi-Fi, Bluetooth, Dark Mode, Night Light, Power Profiles,
and volume/mic sliders.
"""

import os
import sys
import json
import subprocess
from typing import Dict, Any

class QuickSettingsState:
    def __init__(self):
        self.wifi_enabled = True
        self.bluetooth_enabled = True
        self.dark_mode = True
        self.night_light = False
        self.power_profile = "balanced"  # "power-saver", "balanced", "performance"
        self.volume = 75
        self.mic_volume = 80
        self.brightness = 100

    def toggle_wifi(self) -> bool:
        self.wifi_enabled = not self.wifi_enabled
        try:
            cmd = f"nmcli radio wifi {'on' if self.wifi_enabled else 'off'}"
            subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass
        return self.wifi_enabled

    def toggle_bluetooth(self) -> bool:
        self.bluetooth_enabled = not self.bluetooth_enabled
        try:
            cmd = f"bluetoothctl power {'on' if self.bluetooth_enabled else 'off'}"
            subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass
        return self.bluetooth_enabled

    def toggle_dark_mode(self) -> bool:
        self.dark_mode = not self.dark_mode
        return self.dark_mode

    def toggle_night_light(self) -> bool:
        self.night_light = not self.night_light
        try:
            if self.night_light:
                subprocess.Popen("wlsunset -t 4000 -T 6500", shell=True)
            else:
                subprocess.run("killall wlsunset", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass
        return self.night_light

    def set_volume(self, level: int) -> int:
        self.volume = max(0, min(150, level))
        try:
            subprocess.run(f"wpctl set-volume @DEFAULT_AUDIO_SINK@ {self.volume}%", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass
        return self.volume

    def set_brightness(self, level: int) -> int:
        self.brightness = max(5, min(100, level))
        try:
            subprocess.run(f"brightnessctl set {self.brightness}%", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass
        return self.brightness

    def to_dict(self) -> Dict[str, Any]:
        return {
            "wifi_enabled": self.wifi_enabled,
            "bluetooth_enabled": self.bluetooth_enabled,
            "dark_mode": self.dark_mode,
            "night_light": self.night_light,
            "power_profile": self.power_profile,
            "volume": self.volume,
            "mic_volume": self.mic_volume,
            "brightness": self.brightness
        }

def main():
    qs = QuickSettingsState()
    print("AetherOS Quick Settings Initialized.")
    print(json.dumps(qs.to_dict(), indent=2))

if __name__ == "__main__":
    main()
