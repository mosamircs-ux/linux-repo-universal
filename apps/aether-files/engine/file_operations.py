#!/usr/bin/env python3
"""
AetherOS Asynchronous File Transfer & Operations Engine
Executes non-blocking chunked copy, move, and delete operations with progress reporting,
throughput calculation (MB/s), ETA estimation, pause, resume, cancel, and conflict resolution.
"""

import os
import sys
import time
import shutil
import threading
from enum import Enum
from typing import List, Dict, Any, Optional, Callable

CHUNK_SIZE = 1024 * 1024  # 1MB chunk size for high throughput

class TransferStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"

class ConflictResolution(Enum):
    OVERWRITE = "overwrite"
    AUTO_RENAME = "auto_rename"
    SKIP = "skip"
    ASK = "ask"

class TransferTask:
    def __init__(self, task_id: str, op_type: str, sources: List[str], destination: str, conflict_strategy: ConflictResolution = ConflictResolution.AUTO_RENAME):
        self.task_id = task_id
        self.op_type = op_type  # "copy", "move", "delete"
        self.sources = sources
        self.destination = destination
        self.conflict_strategy = conflict_strategy
        
        self.status = TransferStatus.PENDING
        self.total_bytes = 0
        self.transferred_bytes = 0
        self.total_items = 0
        self.transferred_items = 0
        self.current_file = ""
        self.speed_bytes_sec = 0.0
        self.eta_seconds = 0
        self.error_message: Optional[str] = None
        
        self._pause_event = threading.Event()
        self._pause_event.set()  # Not paused by default
        self._cancel_flag = False
        self._start_time = 0.0

    @property
    def progress_percent(self) -> float:
        if self.total_bytes == 0:
            return 100.0 if self.status == TransferStatus.COMPLETED else 0.0
        return min(100.0, (self.transferred_bytes / self.total_bytes) * 100.0)

    def pause(self) -> None:
        if self.status == TransferStatus.RUNNING:
            self._pause_event.clear()
            self.status = TransferStatus.PAUSED

    def resume(self) -> None:
        if self.status == TransferStatus.PAUSED:
            self.status = TransferStatus.RUNNING
            self._pause_event.set()

    def cancel(self) -> None:
        self._cancel_flag = True
        self._pause_event.set()  # Unblock if paused so thread can exit
        self.status = TransferStatus.CANCELLED

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "op_type": self.op_type,
            "sources_count": len(self.sources),
            "destination": self.destination,
            "status": self.status.value,
            "total_bytes": self.total_bytes,
            "transferred_bytes": self.transferred_bytes,
            "progress_percent": round(self.progress_percent, 1),
            "current_file": os.path.basename(self.current_file) if self.current_file else "",
            "speed_mb_s": round(self.speed_bytes_sec / (1024 * 1024), 2),
            "eta_seconds": self.eta_seconds,
            "error_message": self.error_message
        }

class AsyncTransferQueue:
    def __init__(self):
        self.tasks: Dict[str, TransferTask] = {}
        self._lock = threading.Lock()

    def start_copy(self, sources: List[str], destination: str, conflict_strategy: ConflictResolution = ConflictResolution.AUTO_RENAME, callback: Optional[Callable[[TransferTask], None]] = None) -> TransferTask:
        task_id = f"task_{int(time.time() * 1000)}_{len(self.tasks)}"
        task = TransferTask(task_id, "copy", sources, destination, conflict_strategy)
        with self._lock:
            self.tasks[task_id] = task

        thread = threading.Thread(target=self._execute_transfer, args=(task, callback), daemon=True)
        thread.start()
        return task

    def start_move(self, sources: List[str], destination: str, conflict_strategy: ConflictResolution = ConflictResolution.AUTO_RENAME, callback: Optional[Callable[[TransferTask], None]] = None) -> TransferTask:
        task_id = f"task_{int(time.time() * 1000)}_{len(self.tasks)}"
        task = TransferTask(task_id, "move", sources, destination, conflict_strategy)
        with self._lock:
            self.tasks[task_id] = task

        thread = threading.Thread(target=self._execute_transfer, args=(task, callback), daemon=True)
        thread.start()
        return task

    def start_delete(self, sources: List[str], callback: Optional[Callable[[TransferTask], None]] = None) -> TransferTask:
        task_id = f"task_{int(time.time() * 1000)}_{len(self.tasks)}"
        task = TransferTask(task_id, "delete", sources, "", ConflictResolution.OVERWRITE)
        with self._lock:
            self.tasks[task_id] = task

        thread = threading.Thread(target=self._execute_delete, args=(task, callback), daemon=True)
        thread.start()
        return task

    def _calculate_total_size(self, sources: List[str]) -> int:
        total = 0
        for src in sources:
            if os.path.isfile(src) or os.path.islink(src):
                try:
                    total += os.path.getsize(src)
                except Exception:
                    pass
            elif os.path.isdir(src):
                for root, _, files in os.walk(src):
                    for f in files:
                        fp = os.path.join(root, f)
                        try:
                            total += os.path.getsize(fp)
                        except Exception:
                            pass
        return max(1, total)

    def _resolve_destination_path(self, dest_path: str, strategy: ConflictResolution) -> Optional[str]:
        if not os.path.exists(dest_path):
            return dest_path
        if strategy == ConflictResolution.OVERWRITE:
            return dest_path
        elif strategy == ConflictResolution.SKIP:
            return None
        elif strategy == ConflictResolution.AUTO_RENAME:
            base, ext = os.path.splitext(dest_path)
            counter = 1
            while os.path.exists(f"{base} ({counter}){ext}"):
                counter += 1
            return f"{base} ({counter}){ext}"
        return dest_path

    def _execute_transfer(self, task: TransferTask, callback: Optional[Callable[[TransferTask], None]]):
        task.status = TransferStatus.RUNNING
        task.total_bytes = self._calculate_total_size(task.sources)
        task._start_time = time.time()
        last_time = task._start_time
        last_bytes = 0

        os.makedirs(task.destination, exist_ok=True)

        try:
            for src in task.sources:
                if task._cancel_flag:
                    break

                dest_file_target = os.path.join(task.destination, os.path.basename(src))
                resolved_dest = self._resolve_destination_path(dest_file_target, task.conflict_strategy)
                if resolved_dest is None:
                    continue

                if os.path.isfile(src) or os.path.islink(src):
                    self._copy_single_file(src, resolved_dest, task)
                    if task.op_type == "move" and not task._cancel_flag and task.status != TransferStatus.FAILED:
                        try:
                            os.remove(src)
                        except Exception:
                            pass
                elif os.path.isdir(src):
                    self._copy_directory_recursive(src, resolved_dest, task)
                    if task.op_type == "move" and not task._cancel_flag and task.status != TransferStatus.FAILED:
                        try:
                            shutil.rmtree(src)
                        except Exception:
                            pass

                # Update Speed & ETA
                now = time.time()
                elapsed = now - last_time
                if elapsed >= 0.25:
                    delta_bytes = task.transferred_bytes - last_bytes
                    task.speed_bytes_sec = delta_bytes / elapsed
                    remaining_bytes = max(0, task.total_bytes - task.transferred_bytes)
                    if task.speed_bytes_sec > 0:
                        task.eta_seconds = int(remaining_bytes / task.speed_bytes_sec)
                    last_time = now
                    last_bytes = task.transferred_bytes

                if callback:
                    callback(task)

            if task._cancel_flag:
                task.status = TransferStatus.CANCELLED
            elif task.status == TransferStatus.RUNNING:
                task.status = TransferStatus.COMPLETED
                task.transferred_bytes = task.total_bytes
        except Exception as e:
            task.status = TransferStatus.FAILED
            task.error_message = str(e)

        if callback:
            callback(task)

    def _copy_single_file(self, src: str, dest: str, task: TransferTask):
        task.current_file = src
        with open(src, "rb") as fsrc, open(dest, "wb") as fdest:
            while True:
                if task._cancel_flag:
                    break
                task._pause_event.wait()

                buf = fsrc.read(CHUNK_SIZE)
                if not buf:
                    break
                fdest.write(buf)
                task.transferred_bytes += len(buf)

        # Preserve permissions
        try:
            shutil.copymode(src, dest)
        except Exception:
            pass

    def _copy_directory_recursive(self, src_dir: str, dest_dir: str, task: TransferTask):
        os.makedirs(dest_dir, exist_ok=True)
        for root, dirs, files in os.walk(src_dir):
            if task._cancel_flag:
                break
            rel_path = os.path.relpath(root, src_dir)
            target_sub = os.path.join(dest_dir, rel_path) if rel_path != "." else dest_dir
            os.makedirs(target_sub, exist_ok=True)

            for f in files:
                if task._cancel_flag:
                    break
                task._pause_event.wait()
                s_fp = os.path.join(root, f)
                d_fp = os.path.join(target_sub, f)
                self._copy_single_file(s_fp, d_fp, task)

    def _execute_delete(self, task: TransferTask, callback: Optional[Callable[[TransferTask], None]]):
        task.status = TransferStatus.RUNNING
        task.total_items = len(task.sources)

        try:
            for src in task.sources:
                if task._cancel_flag:
                    break
                task.current_file = src
                if os.path.islink(src) or os.path.isfile(src):
                    os.remove(src)
                elif os.path.isdir(src):
                    shutil.rmtree(src)
                task.transferred_items += 1
                if callback:
                    callback(task)

            task.status = TransferStatus.CANCELLED if task._cancel_flag else TransferStatus.COMPLETED
        except Exception as e:
            task.status = TransferStatus.FAILED
            task.error_message = str(e)

        if callback:
            callback(task)
