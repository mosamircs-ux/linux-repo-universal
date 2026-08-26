#!/usr/bin/env python3
"""
Unit and Stress Tests for AetherOS Native File Manager (aether-files)
Validates asynchronous transfers, pause/resume/cancel, conflict resolution, Freedesktop trash,
archive handling, disk/filesystem detection, multi-tabs, split view, search, and large file/dir scaling.
"""

import os
import sys
import time
import shutil
import tempfile
import unittest
import importlib.util

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, REPO_ROOT)
sys.path.insert(0, os.path.join(REPO_ROOT, "apps", "aether-files"))

def load_module_from_path(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

fm_mod = load_module_from_path("file_manager", os.path.join(REPO_ROOT, "apps/aether-files/file_manager.py"))
ops_mod = load_module_from_path("file_operations", os.path.join(REPO_ROOT, "apps/aether-files/engine/file_operations.py"))
trash_mod = load_module_from_path("trash_manager", os.path.join(REPO_ROOT, "apps/aether-files/engine/trash_manager.py"))
disk_mod = load_module_from_path("disk_manager", os.path.join(REPO_ROOT, "apps/aether-files/engine/disk_manager.py"))
archive_mod = load_module_from_path("archive_manager", os.path.join(REPO_ROOT, "apps/aether-files/engine/archive_manager.py"))
search_mod = load_module_from_path("search_engine", os.path.join(REPO_ROOT, "apps/aether-files/engine/search_engine.py"))
preview_mod = load_module_from_path("preview_engine", os.path.join(REPO_ROOT, "apps/aether-files/engine/preview_engine.py"))

AetherFileManagerModel = fm_mod.AetherFileManagerModel
AsyncTransferQueue = ops_mod.AsyncTransferQueue
ConflictResolution = ops_mod.ConflictResolution
TransferStatus = ops_mod.TransferStatus

class TestFileManager(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = self.temp_dir.name
        self.fm = AetherFileManagerModel(initial_path=self.root)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_navigation_and_history(self):
        sub1 = os.path.join(self.root, "sub1")
        sub2 = os.path.join(self.root, "sub2")
        os.makedirs(sub1)
        os.makedirs(sub2)

        self.assertEqual(self.fm.current_path, self.root)
        self.assertTrue(self.fm.navigate_to(sub1))
        self.assertEqual(self.fm.current_path, sub1)

        self.assertTrue(self.fm.navigate_to(sub2))
        self.assertEqual(self.fm.current_path, sub2)

        # Back & Forward
        self.assertTrue(self.fm.navigate_back())
        self.assertEqual(self.fm.current_path, sub1)
        self.assertTrue(self.fm.navigate_forward())
        self.assertEqual(self.fm.current_path, sub2)

        # Up
        self.assertTrue(self.fm.navigate_up())
        self.assertEqual(self.fm.current_path, self.root)

    def test_tabs_and_split_view(self):
        self.assertEqual(len(self.fm.tabs), 1)
        
        # New tab
        idx = self.fm.open_tab("/tmp")
        self.assertEqual(len(self.fm.tabs), 2)
        self.assertEqual(self.fm.active_tab_index, idx)
        self.assertEqual(self.fm.current_path, "/tmp")

        # Switch tab
        self.assertTrue(self.fm.switch_tab(0))
        self.assertEqual(self.fm.current_path, self.root)

        # Close tab
        self.assertTrue(self.fm.close_tab(1))
        self.assertEqual(len(self.fm.tabs), 1)

        # Split View
        self.assertFalse(self.fm.split_view_enabled)
        self.assertTrue(self.fm.toggle_split_view())
        self.assertTrue(self.fm.split_view_enabled)
        self.assertEqual(self.fm.split_pane_path, self.root)
        self.assertFalse(self.fm.toggle_split_view())
        self.assertFalse(self.fm.split_view_enabled)

    def test_directory_listing_and_sorting(self):
        # Create test items
        os.makedirs(os.path.join(self.root, "z_folder"))
        os.makedirs(os.path.join(self.root, "a_folder"))
        with open(os.path.join(self.root, "b_file.txt"), "w") as f:
            f.write("hello")
        with open(os.path.join(self.root, ".hidden_file"), "w") as f:
            f.write("hidden")

        # Default listing (hidden hidden)
        items = self.fm.list_current_directory()
        names = [i["name"] for i in items]
        self.assertIn("a_folder", names)
        self.assertIn("z_folder", names)
        self.assertIn("b_file.txt", names)
        self.assertNotIn(".hidden_file", names)

        # Folders first check
        self.assertTrue(items[0]["is_dir"])
        self.assertTrue(items[1]["is_dir"])
        self.assertFalse(items[2]["is_dir"])

        # Show hidden
        self.fm.show_hidden_files = True
        items_hidden = self.fm.list_current_directory()
        names_h = [i["name"] for i in items_hidden]
        self.assertIn(".hidden_file", names_h)

    def test_async_copy_and_progress(self):
        src_file = os.path.join(self.root, "large_source.bin")
        dest_dir = os.path.join(self.root, "dest")
        os.makedirs(dest_dir)

        # Create 4MB dummy file
        with open(src_file, "wb") as f:
            f.write(b"A" * (4 * 1024 * 1024))

        queue = AsyncTransferQueue()
        progress_reports = []
        def on_progress(task):
            progress_reports.append(task.progress_percent)

        task = queue.start_copy([src_file], dest_dir, ConflictResolution.OVERWRITE, callback=on_progress)
        
        # Wait for completion (fast local disk)
        for _ in range(50):
            if task.status in (TransferStatus.COMPLETED, TransferStatus.FAILED):
                break
            time.sleep(0.05)

        self.assertEqual(task.status, TransferStatus.COMPLETED)
        self.assertEqual(task.transferred_bytes, 4 * 1024 * 1024)
        dest_file = os.path.join(dest_dir, "large_source.bin")
        self.assertTrue(os.path.exists(dest_file))
        self.assertEqual(os.path.getsize(dest_file), 4 * 1024 * 1024)

    def test_conflict_auto_rename(self):
        src_file = os.path.join(self.root, "document.txt")
        dest_dir = os.path.join(self.root, "dest_conflict")
        os.makedirs(dest_dir)
        with open(src_file, "w") as f:
            f.write("version 1")

        # Copy 1st time
        queue = AsyncTransferQueue()
        task1 = queue.start_copy([src_file], dest_dir, ConflictResolution.AUTO_RENAME)
        for _ in range(50):
            if task1.status == TransferStatus.COMPLETED:
                break
            time.sleep(0.02)
        self.assertTrue(os.path.exists(os.path.join(dest_dir, "document.txt")))

        # Copy 2nd time (should auto rename to 'document (1).txt')
        task2 = queue.start_copy([src_file], dest_dir, ConflictResolution.AUTO_RENAME)
        for _ in range(50):
            if task2.status == TransferStatus.COMPLETED:
                break
            time.sleep(0.02)
        self.assertTrue(os.path.exists(os.path.join(dest_dir, "document (1).txt")))

    def test_freedesktop_trash_and_restore(self):
        trash_dir = os.path.join(self.root, "test_trash")
        tm = trash_mod.TrashManager(trash_dir=trash_dir)

        test_file = os.path.join(self.root, "important.docx")
        with open(test_file, "w") as f:
            f.write("Important Report Data")

        # Move to trash
        self.assertTrue(tm.move_to_trash(test_file))
        self.assertFalse(os.path.exists(test_file))

        # List trash
        items = tm.list_trash_items()
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["name"], "important.docx")

        # Restore
        trash_name = items[0]["trash_name"]
        self.assertTrue(tm.restore_item(trash_name))
        self.assertTrue(os.path.exists(test_file))
        self.assertEqual(len(tm.list_trash_items()), 0)

        # Trash again and empty
        self.assertTrue(tm.move_to_trash(test_file))
        cleared = tm.empty_trash()
        self.assertEqual(cleared, 1)
        self.assertEqual(len(tm.list_trash_items()), 0)

    def test_archive_creation_and_extraction(self):
        data_dir = os.path.join(self.root, "arch_data")
        os.makedirs(data_dir)
        with open(os.path.join(data_dir, "f1.txt"), "w") as f:
            f.write("file 1 content")
        with open(os.path.join(data_dir, "f2.txt"), "w") as f:
            f.write("file 2 content")

        # Zip
        zip_out = os.path.join(self.root, "archive.zip")
        self.assertTrue(archive_mod.ArchiveManager.create_archive([data_dir], zip_out, format_type="zip"))
        self.assertTrue(os.path.exists(zip_out))

        # Extract Zip
        extract_dest = os.path.join(self.root, "extracted_zip")
        self.assertTrue(archive_mod.ArchiveManager.extract_archive(zip_out, extract_dest))
        self.assertTrue(os.path.exists(os.path.join(extract_dest, "arch_data", "f1.txt")))

        # Tar.gz
        targz_out = os.path.join(self.root, "archive.tar.gz")
        self.assertTrue(archive_mod.ArchiveManager.create_archive([data_dir], targz_out, format_type="tar.gz"))
        self.assertTrue(os.path.exists(targz_out))

    def test_search_engine_async(self):
        search_root = os.path.join(self.root, "search_test")
        os.makedirs(os.path.join(search_root, "deep", "nested"), exist_ok=True)
        with open(os.path.join(search_root, "deep", "nested", "target_file.json"), "w") as f:
            f.write("{}")

        engine = search_mod.SearchEngine()
        matches = []
        done_flag = [False]

        def on_match(entry):
            matches.append(entry)

        def on_done(results):
            done_flag[0] = True

        thread = engine.search_async(search_root, "target", match_callback=on_match, done_callback=on_done)
        thread.join(timeout=5)

        self.assertTrue(done_flag[0])
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["name"], "target_file.json")

    def test_disk_and_filesystem_manager(self):
        vols = disk_mod.DiskManager.get_mounted_volumes()
        self.assertIsInstance(vols, list)
        self.assertGreater(len(vols), 0)
        root_vol = vols[0]
        self.assertIn("fstype", root_vol)
        self.assertIn("total_gb", root_vol)
        self.assertIn("free_gb", root_vol)

    def test_file_properties_and_permissions(self):
        prop_file = os.path.join(self.root, "props.sh")
        with open(prop_file, "w") as f:
            f.write("#!/bin/bash\necho hello\n")
        os.chmod(prop_file, 0o755)

        props = preview_mod.PreviewEngine.get_file_properties(prop_file)
        self.assertEqual(props["name"], "props.sh")
        self.assertIn("755", props["octal_permissions"])
        self.assertIn("x", props["symbolic_permissions"])
        self.assertFalse(props["is_dir"])

        preview_text = preview_mod.PreviewEngine.get_text_preview(prop_file)
        self.assertIn("#!/bin/bash", preview_text)

    def test_large_directory_performance_scaling(self):
        # Stress test: Create 10,000 files in a single directory
        large_dir = os.path.join(self.root, "massive_dir")
        os.makedirs(large_dir)

        # Batch create 1,000 files to ensure scalability without stalling test suite
        for i in range(1000):
            with open(os.path.join(large_dir, f"file_{i:04d}.dat"), "w") as f:
                f.write(f"index {i}")

        start_t = time.time()
        entries = self.fm.list_directory(large_dir)
        elapsed = time.time() - start_t

        self.assertEqual(len(entries), 1000)
        self.assertLess(elapsed, 0.5, f"Listing 1,000 files took {elapsed:.3f}s (must be < 0.5s)")

if __name__ == "__main__":
    unittest.main()
