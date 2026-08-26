#!/usr/bin/env python3
"""
AetherOS Software Updates Settings Backend
Checks upstream Debian/Ubuntu APT repositories for security patches and system updates.
"""

import subprocess
import shutil
from typing import Dict, Any, List, Tuple
from .polkit_helper import run_privileged

class UpdatesBackend:
    @staticmethod
    def check_updates() -> Dict[str, Any]:
        info = {
            "status": "up-to-date",
            "channel": "LTS (Long Term Support)",
            "available_updates": 0,
            "security_updates": 0,
            "last_checked": "Just now",
            "packages": []
        }
        if shutil.which("apt-get"):
            try:
                res = subprocess.run(["apt-get", "-s", "upgrade"], capture_output=True, text=True)
                for line in res.stdout.split("\n"):
                    if "upgraded," in line and "newly installed," in line:
                        parts = line.split(",")
                        count = int(parts[0].split()[0])
                        info["available_updates"] = count
                        if count > 0:
                            info["status"] = "updates-available"
            except Exception:
                pass
        return info

    @staticmethod
    def install_updates() -> Tuple[bool, str]:
        return run_privileged(["apt-get", "dist-upgrade", "-y"])
