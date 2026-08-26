#!/usr/bin/env python3
"""
Unit and Integration Tests for AetherOS Essential Native Desktop Applications
Validates models, logic, desktop integration, and operations across all 16 native applications:
  Terminal, Text Editor, Calculator, Calendar, Screenshot, Image Viewer,
  PDF Viewer, Archive Manager, Disk Utility, System Monitor, Camera,
  Media Player, Backup Manager, Log Viewer, System Info, and Disk Usage Analyzer.
"""

import os
import sys
import tempfile
import unittest
import importlib.util
from importlib.machinery import SourceFileLoader

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO_ROOT)

def load_mod(name, rel_path):
    fpath = os.path.join(REPO_ROOT, rel_path)
    loader = SourceFileLoader(name, fpath)
    spec = importlib.util.spec_from_file_location(name, fpath, loader=loader)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

# Load all application modules
term_mod = load_mod("aether_terminal", "apps/aether-terminal/terminal_app.py")
text_mod = load_mod("aether_text", "apps/aether-text/editor_app.py")
calc_mod = load_mod("aether_calc", "apps/aether-calc/calculator_app.py")
cal_mod = load_mod("aether_calendar", "apps/aether-calendar/calendar_app.py")
shot_mod = load_mod("aether_screenshot", "apps/aether-screenshot/screenshot_app.py")
img_mod = load_mod("aether_image", "apps/aether-image/image_viewer_app.py")
pdf_mod = load_mod("aether_pdf", "apps/aether-pdf/pdf_viewer_app.py")
arch_mod = load_mod("aether_archive", "apps/aether-archive/archive_app.py")
disk_mod = load_mod("aether_disks", "apps/aether-disks/disk_utility_app.py")
mon_mod = load_mod("aether_monitor", "apps/aether-monitor/monitor_app.py")
cam_mod = load_mod("aether_camera", "apps/aether-camera/camera_app.py")
play_mod = load_mod("aether_player", "apps/aether-player/player_app.py")
bkup_mod = load_mod("aether_backup", "apps/aether-backup/backup_app.py")
log_mod = load_mod("aether_logs", "apps/aether-logs/log_viewer_app.py")
sys_mod = load_mod("aether_sysinfo", "apps/aether-sysinfo/sysinfo_app.py")
use_mod = load_mod("aether_usage", "apps/aether-usage/disk_usage_app.py")

class TestEssentialDesktopApps(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.temp_dir.cleanup()

    # 1. Terminal
    def test_terminal_model(self):
        model = term_mod.AetherTerminalModel()
        self.assertEqual(len(model.tabs), 1)
        model.add_tab("Tab 2")
        self.assertEqual(len(model.tabs), 2)
        self.assertEqual(model.active_tab_idx, 1)
        model.set_theme("nord")
        self.assertEqual(model.theme, "nord")
        self.assertIn("bg", model.get_color_scheme())

    # 2. Text Editor
    def test_text_editor_model(self):
        model = text_mod.AetherTextEditorModel()
        doc = model.documents[0]
        doc.set_content("Hello AetherOS World\nSecond Line\nHello again")
        self.assertTrue(doc.is_dirty)
        matches = model.search_text("Hello")
        self.assertEqual(len(matches), 2)

        save_path = os.path.join(self.temp_dir.name, "test_doc.txt")
        self.assertTrue(doc.save(save_path))
        self.assertFalse(doc.is_dirty)
        self.assertTrue(os.path.exists(save_path))

    # 3. Calculator
    def test_calculator_model(self):
        calc = calc_mod.AetherCalculatorModel()
        calc.append_token("25")
        calc.append_token("+")
        calc.append_token("75")
        res = calc.evaluate()
        self.assertEqual(res, "100")
        self.assertEqual(len(calc.history), 1)

        # Memory actions
        calc.memory_action("M+")
        self.assertEqual(calc.memory, 100.0)
        calc.memory_action("MC")
        self.assertEqual(calc.memory, 0.0)

    # 4. Calendar
    def test_calendar_model(self):
        cal = cal_mod.AetherCalendarModel(data_file=os.path.join(self.temp_dir.name, "cal.json"))
        mat = cal.get_month_matrix(2026, 8)
        self.assertGreaterEqual(len(mat), 4)
        cal.add_event("2026-08-26", "AetherOS Release Party", "18:00")
        evs = cal.get_events_for_date("2026-08-26")
        self.assertEqual(len(evs), 1)
        self.assertEqual(evs[0]["title"], "AetherOS Release Party")

    # 5. Screenshot Tool
    def test_screenshot_model(self):
        shot = shot_mod.AetherScreenshotModel(output_dir=self.temp_dir.name)
        ok, path = shot.capture(mode="fullscreen", delay=0)
        self.assertTrue(ok)
        self.assertTrue(os.path.exists(path))
        self.assertTrue(path.endswith(".png"))

    # 6. Image Viewer
    def test_image_viewer_model(self):
        img_path = os.path.join(self.temp_dir.name, "sample.png")
        with open(img_path, "wb") as f:
            f.write(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82')

        viewer = img_mod.AetherImageViewerModel(img_path)
        self.assertEqual(viewer.rotation_degrees, 0)
        viewer.rotate_cw()
        self.assertEqual(viewer.rotation_degrees, 90)
        viewer.zoom_in()
        self.assertEqual(viewer.zoom_level, 1.2)
        info = viewer.get_image_info()
        self.assertEqual(info["name"], "sample.png")

    # 7. Document / PDF Viewer
    def test_pdf_viewer_model(self):
        pdf_path = os.path.join(self.temp_dir.name, "sample.pdf")
        with open(pdf_path, "wb") as f:
            f.write(b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF\n")

        pdf_viewer = pdf_mod.AetherPdfViewerModel(pdf_path)
        self.assertEqual(pdf_viewer.current_page, 1)
        self.assertFalse(pdf_viewer.dark_mode_invert)
        pdf_viewer.toggle_dark_invert()
        self.assertTrue(pdf_viewer.dark_mode_invert)
        info = pdf_viewer.get_document_info()
        self.assertEqual(info["title"], "sample.pdf")

    # 8. Archive Manager
    def test_archive_manager_model(self):
        # Create dummy files to zip
        f1 = os.path.join(self.temp_dir.name, "file1.txt")
        with open(f1, "w") as f:
            f.write("AetherOS Archive Test")

        zip_p = os.path.join(self.temp_dir.name, "bundle.zip")
        arch = arch_mod.AetherArchiveModel()
        self.assertTrue(arch.create_zip_archive(zip_p, [f1]))

        # Open and inspect
        self.assertTrue(arch.open_archive(zip_p))
        self.assertEqual(len(arch.entries), 1)
        self.assertEqual(arch.entries[0].name, "file1.txt")

        # Extract
        extract_dir = os.path.join(self.temp_dir.name, "extracted")
        self.assertTrue(arch.extract_all(extract_dir))
        self.assertTrue(os.path.exists(os.path.join(extract_dir, "file1.txt")))

    # 9. Disk Utility
    def test_disk_utility_model(self):
        model = disk_mod.AetherDisksModel()
        drives = model.scan_drives()
        self.assertGreaterEqual(len(drives), 1)
        summary = model.get_summary()
        self.assertGreater(summary["total_storage_gb"], 0)

    # 10. System Monitor
    def test_system_monitor_model(self):
        model = mon_mod.AetherSystemMonitorModel()
        summary = model.get_system_summary()
        self.assertIn("cpu_usage_pct", summary)
        self.assertIn("ram_used_mb", summary)
        self.assertGreater(summary["ram_total_mb"], 0)
        self.assertGreaterEqual(len(model.processes), 1)

    # 11. Webcam Camera
    def test_webcam_camera_model(self):
        model = cam_mod.AetherCameraModel(output_dir=self.temp_dir.name)
        devices = model.scan_devices()
        self.assertGreaterEqual(len(devices), 1)
        ok, path = model.take_photo()
        self.assertTrue(ok)
        self.assertTrue(os.path.exists(path))

    # 12. Media Player
    def test_media_player_model(self):
        model = play_mod.AetherMediaPlayerModel()
        track = os.path.join(self.temp_dir.name, "song.mp3")
        with open(track, "w") as f:
            f.write("audio")

        self.assertTrue(model.add_to_playlist(track))
        self.assertTrue(model.play(0))
        self.assertTrue(model.is_playing)
        model.pause()
        self.assertFalse(model.is_playing)
        status = model.get_current_status()
        self.assertEqual(status["playlist_size"], 1)

    # 13. Backup Application
    def test_backup_snapshots_model(self):
        model = bkup_mod.AetherBackupModel(snapshot_root=self.temp_dir.name)
        ok, sp_path = model.create_snapshot(label="test-snap")
        self.assertTrue(ok)
        self.assertGreaterEqual(len(model.snapshots), 1)
        summary = model.get_summary()
        self.assertGreaterEqual(summary["total_snapshots"], 1)

    # 14. Log Viewer
    def test_log_viewer_model(self):
        model = log_mod.AetherLogViewerModel()
        entries = model.fetch_logs()
        self.assertGreaterEqual(len(entries), 1)
        model.priority_filter = "INFO"
        filtered = model.filter_entries()
        self.assertTrue(all(e.priority == "INFO" for e in filtered))

        export_path = os.path.join(self.temp_dir.name, "exported_logs.txt")
        self.assertTrue(model.export_to_file(export_path))
        self.assertTrue(os.path.exists(export_path))

    # 15. System Information
    def test_system_info_model(self):
        model = sys_mod.AetherSysinfoModel()
        self.assertEqual(model.data["os_name"], "AetherOS")
        self.assertEqual(model.data["os_version"], "1.0.0")
        self.assertIn("kernel", model.data)
        self.assertIn("cpu_model", model.data)

    # 16. Disk Usage Analyzer
    def test_disk_usage_analyzer_model(self):
        # Create nested folders & files in temp
        sub = os.path.join(self.temp_dir.name, "subfolder")
        os.makedirs(sub, exist_ok=True)
        with open(os.path.join(sub, "large_file.dat"), "wb") as f:
            f.write(b"0" * 1024 * 1024)  # 1MB

        model = use_mod.AetherDiskUsageModel(self.temp_dir.name)
        nodes = model.scan_path()
        self.assertGreaterEqual(len(nodes), 1)
        summary = model.get_summary()
        self.assertGreater(summary["total_scanned_mb"], 0)

    # 17. Desktop Integration Verification
    def test_desktop_files_exist_for_all_apps(self):
        expected_desktop_files = [
            "apps/aether-terminal/aether-terminal.desktop",
            "apps/aether-text/aether-text.desktop",
            "apps/aether-calc/aether-calc.desktop",
            "apps/aether-calendar/aether-calendar.desktop",
            "apps/aether-screenshot/aether-screenshot.desktop",
            "apps/aether-image/aether-image.desktop",
            "apps/aether-pdf/aether-pdf.desktop",
            "apps/aether-archive/aether-archive.desktop",
            "apps/aether-disks/aether-disks.desktop",
            "apps/aether-monitor/aether-monitor.desktop",
            "apps/aether-camera/aether-camera.desktop",
            "apps/aether-player/aether-player.desktop",
            "apps/aether-backup/aether-backup.desktop",
            "apps/aether-logs/aether-logs.desktop",
            "apps/aether-sysinfo/aether-sysinfo.desktop",
            "apps/aether-usage/aether-usage.desktop",
        ]
        for df in expected_desktop_files:
            full_p = os.path.join(REPO_ROOT, df)
            self.assertTrue(os.path.exists(full_p), f"Missing desktop entry: {df}")
            with open(full_p, "r") as f:
                content = f.read()
                self.assertIn("[Desktop Entry]", content)
                self.assertIn("Exec=", content)
                self.assertIn("Icon=", content)

if __name__ == "__main__":
    unittest.main()
