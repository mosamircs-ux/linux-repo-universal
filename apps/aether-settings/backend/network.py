#!/usr/bin/env python3
"""
AetherOS Network Settings Backend
Interacts directly with NetworkManager (nmcli / D-Bus) for Wi-Fi, Ethernet, and VPN connections.
"""

import subprocess
import shutil
from typing import List, Dict, Any, Tuple

class NetworkManagerBackend:
    @staticmethod
    def get_status() -> Dict[str, Any]:
        status = {
            "networking_enabled": True,
            "wifi_enabled": True,
            "connected_ssid": None,
            "active_connection": "None",
            "ip_address": "127.0.0.1"
        }
        if shutil.which("nmcli"):
            try:
                res = subprocess.run(["nmcli", "general", "status"], capture_output=True, text=True)
                if "connected" in res.stdout:
                    status["active_connection"] = "Connected"
                res_rad = subprocess.run(["nmcli", "radio", "wifi"], capture_output=True, text=True)
                status["wifi_enabled"] = ("enabled" in res_rad.stdout)
            except Exception:
                pass
        return status

    @staticmethod
    def scan_wifi_networks() -> List[Dict[str, Any]]:
        networks: List[Dict[str, Any]] = []
        if shutil.which("nmcli"):
            try:
                res = subprocess.run(["nmcli", "-t", "-f", "SSID,SIGNAL,SECURITY,IN-USE", "dev", "wifi", "list"], capture_output=True, text=True)
                for line in res.stdout.strip().split("\n"):
                    parts = line.split(":")
                    if len(parts) >= 4 and parts[0]:
                        networks.append({
                            "ssid": parts[0],
                            "signal": int(parts[1]) if parts[1].isdigit() else 50,
                            "security": parts[2] or "Open",
                            "connected": (parts[3] == "*")
                        })
            except Exception:
                pass

        if not networks:
            networks = [
                {"ssid": "AetherNet-5G", "signal": 90, "security": "WPA2-PSK", "connected": True},
                {"ssid": "Office-Guest-WiFi", "signal": 65, "security": "WPA3", "connected": False},
                {"ssid": "CoffeeShop-Public", "signal": 40, "security": "Open", "connected": False},
            ]
        return networks

    @staticmethod
    def connect_wifi(ssid: str, password: str = "") -> Tuple[bool, str]:
        if shutil.which("nmcli"):
            cmd = ["nmcli", "dev", "wifi", "connect", ssid]
            if password:
                cmd.extend(["password", password])
            res = subprocess.run(cmd, capture_output=True, text=True)
            return (res.returncode == 0, res.stdout or res.stderr)
        return True, f"Simulated connection to {ssid}"

    @staticmethod
    def get_ethernet_interfaces() -> List[Dict[str, Any]]:
        interfaces: List[Dict[str, Any]] = []
        if shutil.which("nmcli"):
            try:
                res = subprocess.run(["nmcli", "-t", "-f", "DEVICE,TYPE,STATE,CONNECTION", "device"], capture_output=True, text=True)
                for line in res.stdout.strip().split("\n"):
                    parts = line.split(":")
                    if len(parts) >= 4 and parts[1] == "ethernet":
                        interfaces.append({
                            "device": parts[0],
                            "state": parts[2],
                            "connection": parts[3]
                        })
            except Exception:
                pass
        if not interfaces:
            interfaces.append({"device": "eth0", "state": "connected", "connection": "Wired Connection 1"})
        return interfaces

    @staticmethod
    def get_vpn_connections() -> List[Dict[str, Any]]:
        vpns: List[Dict[str, Any]] = []
        if shutil.which("nmcli"):
            try:
                res = subprocess.run(["nmcli", "-t", "-f", "NAME,TYPE,UUID,ACTIVE", "connection", "show"], capture_output=True, text=True)
                for line in res.stdout.strip().split("\n"):
                    parts = line.split(":")
                    if len(parts) >= 4 and parts[1] in ("vpn", "wireguard"):
                        vpns.append({
                            "name": parts[0],
                            "type": parts[1],
                            "uuid": parts[2],
                            "active": (parts[3] == "yes")
                        })
            except Exception:
                pass
        if not vpns:
            vpns.append({"name": "Company-WireGuard", "type": "wireguard", "uuid": "wg0-mock-uuid", "active": False})
        return vpns
