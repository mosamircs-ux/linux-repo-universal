#!/usr/bin/env python3
"""
AetherOS About System Backend
Gathers detailed system specifications, hardware data, kernel version, and OS build metadata.
"""

import os
import sys
from typing import Dict, Any

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(REPO_ROOT, "kernel"))

try:
    import hardware_detector
except ImportError:
    hardware_detector = None

class AboutBackend:
    @staticmethod
    def get_system_specifications() -> Dict[str, Any]:
        specs = {
            "os_name": "AetherOS",
            "version": "1.0.0 LTS (Solstice)",
            "os_type": "64-bit",
            "windowing_system": "Wayland (Wayfire / Labwc)",
            "kernel": os.uname().release,
            "architecture": os.uname().machine,
            "processor": "Generic Multi-core CPU",
            "memory": "16.0 GB",
            "graphics": "Intel / AMD / NVIDIA KMS",
            "disk_capacity": "512.0 GB",
            "base_distribution": "Debian GNU/Linux 12 (Bookworm)"
        }

        if hardware_detector:
            try:
                detector = hardware_detector.HardwareDetector()
                cpu = detector.get_cpu_info()
                ram = detector.get_ram_info()
                gpus = detector.get_gpu_info()
                storage = detector.get_storage_info()

                specs["processor"] = cpu.get("model", specs["processor"])
                specs["memory"] = f"{ram.get('total_mb', 0) / 1024:.1f} GB"
                if gpus:
                    specs["graphics"] = gpus[0].get("vendor", specs["graphics"])
                if storage:
                    total_gb = sum(s.get("size_gb", 0) for s in storage)
                    specs["disk_capacity"] = f"{total_gb:.1f} GB"
            except Exception:
                pass

        return specs
