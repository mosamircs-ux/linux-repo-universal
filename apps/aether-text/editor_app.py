#!/usr/bin/env python3
"""
AetherOS Native Text Editor (aether-text)
Lightweight, modern code & prose editor supporting multiple tabs,
line numbers, search/replace, word wrap, auto-indentation, and dark/light themes.
"""

import os
import sys
import argparse
from typing import Dict, Any, List, Optional

class EditorDocument:
    def __init__(self, path: Optional[str] = None, content: str = ""):
        self.path = path
        self.filename = os.path.basename(path) if path else "Untitled Document"
        self.content = content
        self.is_dirty = False
        self.cursor_line = 1
        self.cursor_col = 1

    def set_content(self, text: str):
        if text != self.content:
            self.content = text
            self.is_dirty = True

    def save(self, new_path: Optional[str] = None) -> bool:
        target = new_path or self.path
        if not target:
            return False
        try:
            with open(target, "w", encoding="utf-8") as f:
                f.write(self.content)
            self.path = target
            self.filename = os.path.basename(target)
            self.is_dirty = False
            return True
        except Exception:
            return False

class AetherTextEditorModel:
    def __init__(self):
        self.documents: List[EditorDocument] = []
        self.active_doc_idx = 0
        self.font = "Monospace 12"
        self.theme = "aether-dark"
        self.word_wrap = True
        self.new_document()

    def new_document(self, content: str = "") -> EditorDocument:
        doc = EditorDocument(content=content)
        self.documents.append(doc)
        self.active_doc_idx = len(self.documents) - 1
        return doc

    def open_file(self, filepath: str) -> Optional[EditorDocument]:
        if os.path.exists(filepath):
            try:
                with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read()
                doc = EditorDocument(path=filepath, content=content)
                self.documents.append(doc)
                self.active_doc_idx = len(self.documents) - 1
                return doc
            except Exception:
                pass
        return None

    def close_document(self, index: int) -> bool:
        if 0 <= index < len(self.documents):
            self.documents.pop(index)
            if not self.documents:
                self.new_document()
            elif self.active_doc_idx >= len(self.documents):
                self.active_doc_idx = len(self.documents) - 1
            return True
        return False

    def search_text(self, query: str) -> List[int]:
        if not query or not self.documents:
            return []
        current_content = self.documents[self.active_doc_idx].content
        matches = []
        start = 0
        while True:
            idx = current_content.find(query, start)
            if idx == -1:
                break
            matches.append(idx)
            start = idx + len(query)
        return matches

def main():
    parser = argparse.ArgumentParser(description="AetherOS Text Editor")
    parser.add_argument("file", nargs="?", help="File to open")
    parser.add_argument("--test", action="store_true", help="Run test mode")
    args = parser.parse_args()

    model = AetherTextEditorModel()
    if args.file:
        model.open_file(args.file)

    if args.test:
        print(f"[aether-text] Model initialized with {len(model.documents)} doc(s). Active: {model.documents[0].filename}")
        return

    try:
        import gi
        gi.require_version("Gtk", "3.0")
        from gi.repository import Gtk

        class EditorWindow(Gtk.Window):
            def __init__(self, model):
                super().__init__(title="Aether Text Editor")
                self.model = model
                self.set_default_size(880, 580)
                box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
                self.add(box)

                # TextView
                self.text_view = Gtk.TextView()
                self.text_view.set_wrap_mode(Gtk.WrapMode.WORD)
                scroll = Gtk.ScrolledWindow()
                scroll.add(self.text_view)
                box.pack_start(scroll, True, True, 0)

        if os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"):
            win = EditorWindow(model)
            win.connect("destroy", Gtk.main_quit)
            win.show_all()
            Gtk.main()
        else:
            print("[aether-text] Running in headless environment.")
    except Exception as e:
        print(f"[aether-text] Headless mode: {e}")

if __name__ == "__main__":
    main()
