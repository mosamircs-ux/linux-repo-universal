#!/usr/bin/env python3
"""
Unit tests for AetherOS System Daemons (Rollback Agent, Crash Handler, Updater)
"""

import os
import sys
import unittest
import tempfile
import importlib.util

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def load_module_from_path(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

rollback_mod = load_module_from_path("rollback", os.path.join(REPO_ROOT, "services/aether-rollback-agent/rollback_agent.py"))
crash_mod = load_module_from_path("crash", os.path.join(REPO_ROOT, "services/aether-crash-handler/crash_handler.py"))
updater_mod = load_module_from_path("updater", os.path.join(REPO_ROOT, "services/aether-updater-daemon/updater_daemon.py"))

class TestServices(unittest.TestCase):
    def test_rollback_agent_counting(self):
        with tempfile.TemporaryDirectory() as td:
            state_f = os.path.join(td, "boot_health.json")
            agent = rollback_mod.BootHealthAgent(state_file=state_f)
            self.assertEqual(agent.state["boot_attempts"], 0)

            # Record boot starts
            agent.record_boot_start()
            self.assertEqual(agent.state["boot_attempts"], 1)

            agent.record_boot_start()
            self.assertEqual(agent.state["boot_attempts"], 2)

            # Boot success resets
            agent.record_boot_success()
            self.assertEqual(agent.state["boot_attempts"], 0)

    def test_crash_handler_privacy_sanitization(self):
        with tempfile.TemporaryDirectory() as td:
            handler = crash_mod.CrashHandler(log_dir=td)
            raw_trace = "Segfault in /home/alice/secret_project.py on host 10.0.0.42 by alice@company.org"
            sanitized = handler.sanitize_text(raw_trace)

            self.assertNotIn("10.0.0.42", sanitized)
            self.assertIn("[REDACTED_IP]", sanitized)
            self.assertNotIn("alice@company.org", sanitized)
            self.assertIn("[REDACTED_EMAIL]", sanitized)
            self.assertNotIn("/home/alice", sanitized)
            self.assertIn("/home/[USER]", sanitized)

            # Record crash file
            crash_file = handler.record_crash("test-app", 999, 11, raw_trace)
            self.assertTrue(os.path.exists(crash_file))

    def test_updater_daemon_check(self):
        daemon = updater_mod.AetherUpdateDaemon()
        res = daemon.check_for_updates()
        self.assertEqual(res["status"], "success")

if __name__ == "__main__":
    unittest.main()
