#!/usr/bin/env python3
"""
AetherOS Sound & Audio Settings Backend
Interacts with PipeWire 1.0+ and WirePlumber (wpctl / pw-cli / ALSA).
"""

import subprocess
import shutil
from typing import List, Dict, Any, Tuple

class SoundBackend:
    @staticmethod
    def get_audio_status() -> Dict[str, Any]:
        status = {
            "server": "PipeWire 1.0+ (WirePlumber)",
            "output_volume": 75,
            "output_muted": False,
            "input_volume": 80,
            "input_muted": False,
            "sinks": [
                {"id": 1, "name": "Built-in Audio (Speaker/Headphones)", "type": "speaker", "active": True},
                {"id": 2, "name": "HDMI / DisplayPort Digital Audio", "type": "hdmi", "active": False}
            ],
            "sources": [
                {"id": 10, "name": "Internal Digital Microphone", "type": "microphone", "active": True}
            ]
        }
        if shutil.which("wpctl"):
            try:
                res = subprocess.run(["wpctl", "get-volume", "@DEFAULT_AUDIO_SINK@"], capture_output=True, text=True)
                # Output format: Volume: 0.75 [MUTED]
                if "Volume:" in res.stdout:
                    parts = res.stdout.split()
                    status["output_volume"] = int(float(parts[1]) * 100)
                    status["output_muted"] = ("[MUTED]" in res.stdout)
            except Exception:
                pass
        return status

    @staticmethod
    def set_output_volume(volume: int) -> bool:
        vol = max(0, min(100, volume))
        if shutil.which("wpctl"):
            try:
                subprocess.run(["wpctl", "set-volume", "@DEFAULT_AUDIO_SINK@", f"{vol / 100:.2f}"], capture_output=True)
                return True
            except Exception:
                return False
        return True

    @staticmethod
    def set_output_mute(muted: bool) -> bool:
        if shutil.which("wpctl"):
            try:
                subprocess.run(["wpctl", "set-mute", "@DEFAULT_AUDIO_SINK@", "1" if muted else "0"], capture_output=True)
                return True
            except Exception:
                return False
        return True

    @staticmethod
    def set_input_volume(volume: int) -> bool:
        vol = max(0, min(100, volume))
        if shutil.which("wpctl"):
            try:
                subprocess.run(["wpctl", "set-volume", "@DEFAULT_AUDIO_SOURCE@", f"{vol / 100:.2f}"], capture_output=True)
                return True
            except Exception:
                return False
        return True

    @staticmethod
    def set_default_sink(sink_id: int) -> bool:
        if shutil.which("wpctl"):
            try:
                subprocess.run(["wpctl", "set-default", str(sink_id)], capture_output=True)
                return True
            except Exception:
                return False
        return True
