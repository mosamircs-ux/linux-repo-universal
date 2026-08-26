#!/usr/bin/env python3
"""
AetherOS Privacy & Security Settings Backend
Configures UFW firewall, AppArmor enforcement, SSH server, and privacy/hardware permissions.
"""

import os
import shutil
import subprocess
from typing import Dict, Any, Tuple, List
from .polkit_helper import run_privileged

class SecurityPrivacyBackend:
    @staticmethod
    def get_security_status() -> Dict[str, Any]:
        status = {
            "firewall_active": False,
            "firewall_default_incoming": "deny",
            "apparmor_active": True,
            "ssh_service_active": False,
            "location_enabled": False,
            "camera_access_allowed": True,
            "microphone_access_allowed": True,
            "diagnostics_reporting": False
        }
        # Check UFW
        if shutil.which("ufw"):
            try:
                res = subprocess.run(["ufw", "status"], capture_output=True, text=True)
                status["firewall_active"] = ("Status: active" in res.stdout)
            except Exception:
                pass

        # Check SSH
        if shutil.which("systemctl"):
            try:
                res = subprocess.run(["systemctl", "is-active", "ssh"], capture_output=True, text=True)
                status["ssh_service_active"] = (res.stdout.strip() == "active")
            except Exception:
                pass

        return status

    @staticmethod
    def toggle_firewall(enable: bool) -> Tuple[bool, str]:
        cmd = ["ufw", "enable" if enable else "disable"]
        return run_privileged(cmd)

    @staticmethod
    def toggle_ssh_service(enable: bool) -> Tuple[bool, str]:
        action = "enable --now" if enable else "disable --now"
        cmd = ["systemctl"] + action.split() + ["ssh"]
        return run_privileged(cmd)

    @staticmethod
    def clear_recent_files() -> bool:
        recent_p = os.path.expanduser("~/.local/share/recently-used.xbel")
        if os.path.exists(recent_p):
            try:
                os.remove(recent_p)
                return True
            except Exception:
                return False
        return True
