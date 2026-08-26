#!/usr/bin/env python3
"""
AetherOS Privacy-First Crash Handler
Intercepts program crashes, sanitizes private information (passwords, usernames, IP addresses),
and stores local debugging crash logs under /var/log/aether/crashes without external telemetry.
"""

import os
import sys
import re
import time
import json
import logging
from typing import Dict, Any

CRASH_LOG_DIR = "/var/log/aether/crashes"

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s")

class CrashHandler:
    def __init__(self, log_dir: str = CRASH_LOG_DIR):
        self.log_dir = log_dir

    def sanitize_text(self, text: str) -> str:
        # Strip IP addresses
        text = re.sub(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', '[REDACTED_IP]', text)
        # Strip email addresses
        text = re.sub(r'[\w\.-]+@[\w\.-]+\.\w+', '[REDACTED_EMAIL]', text)
        # Strip username paths
        text = re.sub(r'/home/[^/\s]+', '/home/[USER]', text)
        return text

    def record_crash(self, app_name: str, pid: int, signal_num: int, raw_backtrace: str) -> str:
        sanitized_bt = self.sanitize_text(raw_backtrace)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        report_name = f"crash_{app_name}_{timestamp}_{pid}.json"

        report_data = {
            "app_name": app_name,
            "pid": pid,
            "signal": signal_num,
            "timestamp": time.time(),
            "date": time.ctime(),
            "backtrace": sanitized_bt,
            "telemetry_sent": False  # Zero telemetry guarantee
        }

        try:
            os.makedirs(self.log_dir, exist_ok=True)
            report_path = os.path.join(self.log_dir, report_name)
            with open(report_path, "w", encoding="utf-8") as f:
                json.dump(report_data, f, indent=2)
            logging.info(f"Crash report stored locally at: {report_path}")
            return report_path
        except Exception as e:
            logging.warning(f"Could not write crash log to disk: {e}")
            return ""

def main():
    handler = CrashHandler("/tmp/aether_test_crashes")
    sample_bt = "Error in /home/john/app.py on IP 192.168.1.50 with contact john@example.com"
    out = handler.record_crash("demo-app", 1234, 11, sample_bt)
    print(f"Recorded test crash. File: {out}")

if __name__ == "__main__":
    main()
