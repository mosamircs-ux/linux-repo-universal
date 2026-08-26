#!/usr/bin/env python3
"""
AetherOS Users & Accounts Settings Backend
Manages local accounts, administrator privileges, passwords, and auto-login via Polkit.
"""

import os
import pwd
import grp
import subprocess
from typing import List, Dict, Any, Tuple
from .polkit_helper import run_privileged

class UsersBackend:
    @staticmethod
    def get_users() -> List[Dict[str, Any]]:
        users: List[Dict[str, Any]] = []
        try:
            for p in pwd.getpwall():
                if 1000 <= p.pw_uid < 60000:
                    # Check if user is in sudo / admin / wheel group
                    is_admin = False
                    try:
                        sudo_members = grp.getgrnam("sudo").gr_mem
                        wheel_members = grp.getgrnam("wheel").gr_mem if "wheel" in [g.gr_name for g in grp.getgrall()] else []
                        is_admin = (p.pw_name in sudo_members or p.pw_name in wheel_members or p.pw_uid == 1000)
                    except Exception:
                        is_admin = (p.pw_uid == 1000)

                    users.append({
                        "username": p.pw_name,
                        "uid": p.pw_uid,
                        "fullname": p.pw_gecos.split(",")[0] or p.pw_name,
                        "home": p.pw_dir,
                        "shell": p.pw_shell,
                        "is_admin": is_admin,
                        "is_current": (p.pw_name == os.environ.get("USER", ""))
                    })
        except Exception:
            pass

        if not users:
            curr = os.environ.get("USER", "aether")
            users.append({
                "username": curr,
                "uid": 1000,
                "fullname": curr.capitalize(),
                "home": f"/home/{curr}",
                "shell": "/bin/bash",
                "is_admin": True,
                "is_current": True
            })
        return users

    @staticmethod
    def add_user(username: str, fullname: str, is_admin: bool = False) -> Tuple[bool, str]:
        cmd = ["useradd", "-m", "-c", fullname, username]
        if is_admin:
            cmd.extend(["-G", "sudo"])
        return run_privileged(cmd)

    @staticmethod
    def delete_user(username: str, remove_home: bool = True) -> Tuple[bool, str]:
        cmd = ["userdel"]
        if remove_home:
            cmd.append("-r")
        cmd.append(username)
        return run_privileged(cmd)

    @staticmethod
    def set_user_role(username: str, is_admin: bool) -> Tuple[bool, str]:
        if is_admin:
            cmd = ["usermod", "-aG", "sudo", username]
        else:
            cmd = ["gpasswd", "-d", username, "sudo"]
        return run_privileged(cmd)
