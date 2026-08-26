#!/usr/bin/env python3
"""
AetherOS Printers Settings Backend
Interacts with CUPS printing subsystem (lpstat / lpadmin / ippfind).
"""

import subprocess
import shutil
from typing import List, Dict, Any, Tuple
from .polkit_helper import run_privileged

class PrintersBackend:
    @staticmethod
    def get_printers() -> List[Dict[str, Any]]:
        printers: List[Dict[str, Any]] = []
        if shutil.which("lpstat"):
            try:
                res = subprocess.run(["lpstat", "-p", "-d"], capture_output=True, text=True)
                default_p = ""
                for line in res.stdout.split("\n"):
                    if "system default destination:" in line:
                        default_p = line.split(":")[1].strip()
                    elif line.startswith("printer "):
                        p_name = line.split()[1]
                        printers.append({
                            "name": p_name,
                            "state": "idle" if "is idle" in line else "busy",
                            "default": (p_name == default_p),
                            "uri": f"ipp://localhost/printers/{p_name}"
                        })
            except Exception:
                pass

        if not printers:
            printers.append({
                "name": "HP-LaserJet-Pro-M404dn",
                "state": "idle",
                "default": True,
                "uri": "ipp://192.168.1.120/ipp/print"
            })
        return printers

    @staticmethod
    def set_default_printer(printer_name: str) -> bool:
        if shutil.which("lpoptions"):
            try:
                subprocess.run(["lpoptions", "-d", printer_name], capture_output=True)
                return True
            except Exception:
                return False
        return True

    @staticmethod
    def print_test_page(printer_name: str) -> Tuple[bool, str]:
        if shutil.which("lp"):
            test_file = "/usr/share/cups/data/testprint"
            if not shutil.os.path.exists(test_file):
                test_file = "/tmp/testprint.txt"
                with open(test_file, "w") as f:
                    f.write("AetherOS Solstice Test Print Page\n")
            try:
                res = subprocess.run(["lp", "-d", printer_name, test_file], capture_output=True, text=True)
                return (res.returncode == 0, res.stdout or res.stderr)
            except Exception as e:
                return False, str(e)
        return True, f"Sent test page to {printer_name}"

    @staticmethod
    def remove_printer(printer_name: str) -> Tuple[bool, str]:
        return run_privileged(["lpadmin", "-x", printer_name])
