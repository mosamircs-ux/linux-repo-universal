#!/usr/bin/env python3
"""
AetherOS Accessibility Architecture Engine (aether-a11y)
Manages assistive technologies across desktop sessions:
  - Screen Reader (Orca / Speech Dispatcher / AT-SPI2)
  - High Contrast Theme & Focus Indicators
  - Fractional Text Scaling (1.0x to 2.0x)
  - Reduced Motion (Compositor animation toggles)
  - Cursor Pointer Scaling (24px to 64px)
  - AccessX Keyboard Modifiers (Sticky Keys, Slow Keys, Bounce Keys, Mouse Keys)
  - Visual Notification Bell Flash
"""

import os
import sys
import json
import shutil
import subprocess
from typing import Dict, Any, List, Optional

class AccessibilityManager:
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or os.path.expanduser("~/.config/aether/accessibility.json")
        self.settings: Dict[str, Any] = {
            "screen_reader": False,
            "high_contrast": False,
            "text_scaling": 1.0,
            "reduced_motion": False,
            "large_pointer": False,
            "pointer_size": 24,
            "sticky_keys": False,
            "slow_keys": False,
            "bounce_keys": False,
            "mouse_keys": False,
            "visual_bell": False
        }
        self.load_settings()

    def load_settings(self) -> Dict[str, Any]:
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as f:
                    data = json.load(f)
                    self.settings.update(data)
            except Exception:
                pass
        return self.settings

    def save_settings(self) -> bool:
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, "w") as f:
                json.dump(self.settings, f, indent=2)
            return True
        except Exception:
            return False

    def set_screen_reader(self, enabled: bool) -> bool:
        self.settings["screen_reader"] = enabled
        self.save_settings()
        if enabled and shutil.which("orca"):
            try:
                subprocess.Popen(["orca", "--replace"])
            except Exception:
                pass
        return enabled

    def set_high_contrast(self, enabled: bool) -> bool:
        self.settings["high_contrast"] = enabled
        self.save_settings()
        return enabled

    def set_text_scaling(self, factor: float) -> float:
        val = max(1.0, min(2.0, round(factor, 2)))
        self.settings["text_scaling"] = val
        self.save_settings()
        return val

    def set_reduced_motion(self, enabled: bool) -> bool:
        self.settings["reduced_motion"] = enabled
        self.save_settings()
        return enabled

    def set_pointer_size(self, size: int) -> int:
        sz = max(24, min(64, size))
        self.settings["pointer_size"] = sz
        self.settings["large_pointer"] = (sz > 24)
        self.save_settings()
        return sz

    def set_accessx_feature(self, feature: str, enabled: bool) -> bool:
        if feature in self.settings:
            self.settings[feature] = enabled
            self.save_settings()
            return enabled
        return False

    def get_summary(self) -> Dict[str, Any]:
        return self.settings

# Global instance
a11y = AccessibilityManager()
