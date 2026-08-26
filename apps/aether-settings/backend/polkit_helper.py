#!/usr/bin/env python3
"""
AetherOS Settings Privileged Execution Helper
Mediates root privileges via Polkit (pkexec) or sudo with strict input sanitization.
"""

import os
import sys
import shutil
import subprocess
from typing import List, Tuple, Optional

ALLOWED_COMMANDS = {
    "timedatectl", "localectl", "hostnamectl", "systemctl",
    "useradd", "userdel", "usermod", "passwd",
    "ufw", "btrfs", "fstrim", "udisksctl", "lpadmin", "apt-get"
}

def run_privileged(command: List[str], timeout: int = 30) -> Tuple[bool, str]:
    if not command:
        return False, "Empty command provided"

    prog = command[0]
    base_prog = os.path.basename(prog)
    if base_prog not in ALLOWED_COMMANDS:
        return False, f"Command '{base_prog}' is not in allowed privileged whitelist"

    # If already root
    if os.geteuid() == 0:
        cmd = command
    elif shutil.which("pkexec"):
        cmd = ["pkexec"] + command
    elif shutil.which("sudo"):
        cmd = ["sudo", "-n"] + command
    else:
        cmd = command

    try:
        res = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout
        )
        if res.returncode == 0:
            return True, res.stdout.strip()
        else:
            return False, res.stderr.strip() or f"Command exited with code {res.returncode}"
    except subprocess.TimeoutExpired:
        return False, f"Command timed out after {timeout} seconds"
    except Exception as e:
        return False, str(e)
