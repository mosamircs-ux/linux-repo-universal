#!/usr/bin/env python3
"""
AetherOS File Search Engine
Provides fast asynchronous recursive directory search with cancellation and live streaming.
"""

import os
import re
import threading
from typing import List, Dict, Any, Optional, Callable

class SearchEngine:
    def __init__(self):
        self._cancel_event = threading.Event()

    def cancel(self) -> None:
        self._cancel_event.set()

    def search_async(self, root_dir: str, query: str, include_hidden: bool = False, match_callback: Optional[Callable[[Dict[str, Any]], None]] = None, done_callback: Optional[Callable[[List[Dict[str, Any]]], None]] = None) -> threading.Thread:
        self._cancel_event.clear()
        results: List[Dict[str, Any]] = []

        def worker():
            q_lower = query.lower()
            try:
                for root, dirs, files in os.walk(root_dir):
                    if self._cancel_event.is_set():
                        break

                    if not include_hidden:
                        dirs[:] = [d for d in dirs if not d.startswith(".")]

                    for name in dirs + files:
                        if self._cancel_event.is_set():
                            break

                        if not include_hidden and name.startswith("."):
                            continue

                        if q_lower in name.lower():
                            fp = os.path.join(root, name)
                            is_dir = os.path.isdir(fp)
                            size = 0
                            if not is_dir:
                                try:
                                    size = os.path.getsize(fp)
                                except Exception:
                                    pass

                            entry = {
                                "name": name,
                                "path": fp,
                                "is_dir": is_dir,
                                "size": size,
                                "parent": root
                            }
                            results.append(entry)
                            if match_callback:
                                match_callback(entry)

            except Exception:
                pass

            if done_callback:
                done_callback(results)

        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
        return thread
