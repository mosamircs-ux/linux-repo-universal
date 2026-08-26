#!/usr/bin/env python3
"""
AetherOS Date, Time, Language & Region Settings Backend
Interacts directly with systemd (timedatectl / localectl) to configure clock, timezones, and locales.
"""

import subprocess
import shutil
from typing import Dict, Any, List, Tuple
from .polkit_helper import run_privileged

class DateTimeLocaleBackend:
    @staticmethod
    def get_datetime_status() -> Dict[str, Any]:
        status = {
            "timezone": "UTC",
            "ntp_active": True,
            "rtc_in_local_tz": False,
            "time_format_24h": True
        }
        if shutil.which("timedatectl"):
            try:
                res = subprocess.run(["timedatectl", "status"], capture_output=True, text=True)
                for line in res.stdout.split("\n"):
                    if "Time zone:" in line:
                        status["timezone"] = line.split(":")[1].strip().split()[0]
                    elif "NTP service:" in line:
                        status["ntp_active"] = ("active" in line)
            except Exception:
                pass
        return status

    @staticmethod
    def set_timezone(tz: str) -> Tuple[bool, str]:
        return run_privileged(["timedatectl", "set-timezone", tz])

    @staticmethod
    def set_ntp(enable: bool) -> Tuple[bool, str]:
        return run_privileged(["timedatectl", "set-ntp", "1" if enable else "0"])

    @staticmethod
    def get_locale_status() -> Dict[str, Any]:
        status = {
            "system_locale": "en_US.UTF-8",
            "available_locales": [
                "en_US.UTF-8", "en_GB.UTF-8", "ar_EG.UTF-8", "ar_SA.UTF-8",
                "fr_FR.UTF-8", "de_DE.UTF-8", "es_ES.UTF-8", "ja_JP.UTF-8"
            ]
        }
        if shutil.which("localectl"):
            try:
                res = subprocess.run(["localectl", "status"], capture_output=True, text=True)
                for line in res.stdout.split("\n"):
                    if "System Locale:" in line:
                        status["system_locale"] = line.split("=")[1].strip()
            except Exception:
                pass
        return status

    @staticmethod
    def set_locale(locale_str: str) -> Tuple[bool, str]:
        return run_privileged(["localectl", "set-locale", f"LANG={locale_str}"])
