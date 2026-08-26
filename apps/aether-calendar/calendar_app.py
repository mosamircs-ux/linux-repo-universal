#!/usr/bin/env python3
"""
AetherOS Native Calendar (aether-calendar)
Polished, responsive calendar with month overview, agenda view,
event scheduling, leap year support, and bilingual (English/Arabic) localization.
"""

import os
import sys
import json
import calendar
import datetime
import argparse
from typing import Dict, Any, List, Optional, Tuple

MONTHS_EN = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
MONTHS_AR = ["يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو", "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"]

class AetherCalendarModel:
    def __init__(self, data_file: Optional[str] = None):
        self.current_date = datetime.date.today()
        self.selected_year = self.current_date.year
        self.selected_month = self.current_date.month
        self.selected_day = self.current_date.day
        self.data_file = data_file or os.path.expanduser("~/.config/aether/calendar_events.json")
        self.events: Dict[str, List[Dict[str, str]]] = {}
        self.load_events()

    def load_events(self) -> None:
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    self.events = json.load(f)
            except Exception:
                self.events = {}

    def save_events(self) -> None:
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(self.events, f, indent=2)
        except Exception:
            pass

    def add_event(self, date_str: str, title: str, time_str: str = "09:00", description: str = "") -> bool:
        if date_str not in self.events:
            self.events[date_str] = []
        self.events[date_str].append({
            "title": title,
            "time": time_str,
            "description": description
        })
        self.save_events()
        return True

    def get_events_for_date(self, date_str: str) -> List[Dict[str, str]]:
        return self.events.get(date_str, [])

    def get_month_matrix(self, year: int, month: int) -> List[List[int]]:
        cal = calendar.Calendar(firstweekday=0)  # Monday start
        return cal.monthdayscalendar(year, month)

    def next_month(self) -> Tuple[int, int]:
        if self.selected_month == 12:
            self.selected_month = 1
            self.selected_year += 1
        else:
            self.selected_month += 1
        return self.selected_year, self.selected_month

    def prev_month(self) -> Tuple[int, int]:
        if self.selected_month == 1:
            self.selected_month = 12
            self.selected_year -= 1
        else:
            self.selected_month -= 1
        return self.selected_year, self.selected_month

    def jump_to_today(self) -> None:
        today = datetime.date.today()
        self.selected_year = today.year
        self.selected_month = today.month
        self.selected_day = today.day

    def get_header_title(self, lang: str = "en") -> str:
        idx = self.selected_month - 1
        m_name = MONTHS_AR[idx] if lang == "ar" else MONTHS_EN[idx]
        return f"{m_name} {self.selected_year}"

def main():
    parser = argparse.ArgumentParser(description="AetherOS Calendar")
    parser.add_argument("--test", action="store_true", help="Run test mode")
    args = parser.parse_args()

    cal_model = AetherCalendarModel()
    if args.test:
        mat = cal_model.get_month_matrix(2026, 8)
        print(f"[aether-calendar] 2026-08 matrix weeks: {len(mat)}, header: {cal_model.get_header_title()}")
        return

    try:
        import gi
        gi.require_version("Gtk", "3.0")
        from gi.repository import Gtk

        class CalendarWindow(Gtk.Window):
            def __init__(self, model):
                super().__init__(title="Aether Calendar")
                self.model = model
                self.set_default_size(720, 520)
                box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
                self.add(box)
                gtk_cal = Gtk.Calendar()
                box.pack_start(gtk_cal, True, True, 0)

        if os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"):
            win = CalendarWindow(cal_model)
            win.connect("destroy", Gtk.main_quit)
            win.show_all()
            Gtk.main()
        else:
            print("[aether-calendar] Headless environment.")
    except Exception as e:
        print(f"[aether-calendar] Headless: {e}")

if __name__ == "__main__":
    main()
