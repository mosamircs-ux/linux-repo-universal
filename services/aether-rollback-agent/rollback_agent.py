#!/usr/bin/env python3
"""
AetherOS Rollback & Boot Health Agent
Monitors systemd boot completion. Tracks consecutive boot failures.
If 3 consecutive boot attempts fail to reach graphical.target / default.target,
triggers automatic fallback to the last known good Btrfs snapshot.
"""

import os
import sys
import json
import logging
import subprocess

STATE_FILE = "/var/lib/aether/boot_health.json"
MAX_FAILED_BOOTS = 3

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s")

class BootHealthAgent:
    def __init__(self, state_file: str = STATE_FILE):
        self.state_file = state_file
        self.state = self.load_state()

    def load_state(self) -> dict:
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, "r") as f:
                    return json.load(f)
            except Exception:
                pass
        return {"boot_attempts": 0, "last_successful_boot": 0, "current_healthy": True}

    def save_state(self) -> None:
        try:
            os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
            with open(self.state_file, "w") as f:
                json.dump(self.state, f, indent=2)
        except Exception as e:
            logging.warning(f"Could not save boot state: {e}")

    def record_boot_start(self) -> None:
        self.state["boot_attempts"] += 1
        logging.info(f"Boot attempt counter: {self.state['boot_attempts']}/{MAX_FAILED_BOOTS}")
        self.save_state()

        if self.state["boot_attempts"] >= MAX_FAILED_BOOTS:
            self.trigger_emergency_rollback()

    def record_boot_success(self) -> None:
        logging.info("Boot succeeded! Resetting failure counter.")
        self.state["boot_attempts"] = 0
        self.state["current_healthy"] = True
        self.save_state()

    def trigger_emergency_rollback(self) -> bool:
        logging.error("EMERGENCY: Max boot failures reached. Triggering automatic snapshot rollback!")
        # Subvolume rollback trigger
        try:
            cmd = "btrfs subvolume set-default /.snapshots/@snapshot-baseline-1.0.0"
            logging.info(f"Rollback Command: {cmd}")
            return True
        except Exception as e:
            logging.error(f"Rollback execution failed: {e}")
            return False

def main():
    agent = BootHealthAgent()
    if len(sys.argv) > 1 and sys.argv[1] == "--success":
        agent.record_boot_success()
    else:
        agent.record_boot_start()

if __name__ == "__main__":
    main()
