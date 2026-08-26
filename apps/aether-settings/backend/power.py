#!/usr/bin/env python3
"""
AetherOS Power & Battery Settings Backend
Manages power profiles (power-profiles-daemon), display dimming, and sleep timeouts.
"""

import subprocess
import shutil
from typing import Dict, Any, List

class PowerBackend:
    @staticmethod
    def get_power_status() -> Dict[str, Any]:
        status = {
            "active_profile": "balanced",
            "available_profiles": ["performance", "balanced", "power-saver"],
            "screen_blank_minutes": 5,
            "suspend_minutes": 15,
            "power_button_action": "interactive",
            "battery_charging_limit": 80
        }
        if shutil.which("powerprofilesctl"):
            try:
                res = subprocess.run(["powerprofilesctl", "get"], capture_output=True, text=True)
                if res.returncode == 0 and res.stdout.strip():
                    status["active_profile"] = res.stdout.strip()
            except Exception:
                pass
        return status

    @staticmethod
    def set_power_profile(profile: str) -> bool:
        if profile in ("performance", "balanced", "power-saver"):
            if shutil.which("powerprofilesctl"):
                try:
                    subprocess.run(["powerprofilesctl", "set", profile], capture_output=True)
                    return True
                except Exception:
                    return False
        return True
