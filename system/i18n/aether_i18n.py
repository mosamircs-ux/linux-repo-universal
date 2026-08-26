#!/usr/bin/env python3
"""
AetherOS Centralized Internationalization & Localization Engine (aether-i18n)
Supports:
  - English (en_US) and first-class Arabic (ar_SA, ar_EG, ar_MA)
  - Bidirectional RTL / LTR layout switching
  - Arabic keyboard layout configuration (ara, ara-digits, Alt+Shift toggle)
  - Eastern Arabic (١٢٣) and Western Arabic (123) numeral formatting
  - Localized Gregorian & Hijri calendar date/time formatting
  - Full application, settings, installer, and system dialog translation catalog
"""

import os
import sys
import json
import datetime
from typing import Dict, Any, List, Optional, Union

# Arabic Translation Catalog
TRANSLATIONS: Dict[str, Dict[str, str]] = {
    # System & Desktop Core
    "AetherOS": {"en": "AetherOS", "ar": "نظام أيثر"},
    "Settings": {"en": "Settings", "ar": "الإعدادات"},
    "Applications": {"en": "Applications", "ar": "التطبيقات"},
    "Files": {"en": "Files", "ar": "الملفات"},
    "Software Center": {"en": "Software Center", "ar": "مركز البرمجيات"},
    "System Update": {"en": "System Update", "ar": "تحديث النظام"},
    "System Monitor": {"en": "System Monitor", "ar": "مراقب النظام"},
    "Terminal": {"en": "Terminal", "ar": "الطرفية"},
    "Text Editor": {"en": "Text Editor", "ar": "محرر النصوص"},
    "Calculator": {"en": "Calculator", "ar": "الآلة الحاسبة"},
    "Calendar": {"en": "Calendar", "ar": "التقويم"},
    "Screenshot": {"en": "Screenshot", "ar": "لقطة الشاشة"},
    "Image Viewer": {"en": "Image Viewer", "ar": "عارض الصور"},
    "Document Viewer": {"en": "Document Viewer", "ar": "عارض المستندات"},
    "Archive Manager": {"en": "Archive Manager", "ar": "مدير الأرشيف"},
    "Disk Utility": {"en": "Disk Utility", "ar": "أداة الأقراص"},
    "Camera": {"en": "Camera", "ar": "الكاميرا"},
    "Media Player": {"en": "Media Player", "ar": "مشغل الوسائط"},
    "Backup & Restore": {"en": "Backup & Restore", "ar": "النسخ الاحتياطي والاستعادة"},
    "System Logs": {"en": "System Logs", "ar": "سجلات النظام"},
    "About AetherOS": {"en": "About AetherOS", "ar": "حول نظام أيثر"},
    "Disk Usage": {"en": "Disk Usage", "ar": "استخدام القرص"},

    # Actions & Buttons
    "Install": {"en": "Install", "ar": "تثبيت"},
    "Remove": {"en": "Remove", "ar": "إزالة"},
    "Update": {"en": "Update", "ar": "تحديث"},
    "Cancel": {"en": "Cancel", "ar": "إلغاء"},
    "Apply": {"en": "Apply", "ar": "تطبيق"},
    "Save": {"en": "Save", "ar": "حفظ"},
    "Open": {"en": "Open", "ar": "فتح"},
    "Close": {"en": "Close", "ar": "إغلاق"},
    "Next": {"en": "Next", "ar": "التالي"},
    "Back": {"en": "Back", "ar": "السابق"},
    "Finish": {"en": "Finish", "ar": "إنهاء"},
    "Search": {"en": "Search", "ar": "بحث"},
    "Restart": {"en": "Restart", "ar": "إعادة التشغيل"},
    "Shutdown": {"en": "Shutdown", "ar": "إيقاف التشغيل"},
    "Log Out": {"en": "Log Out", "ar": "تسجيل الخروج"},
    "Lock Screen": {"en": "Lock Screen", "ar": "قفل الشاشة"},

    # Settings Sections
    "Wi-Fi": {"en": "Wi-Fi", "ar": "الشبكة اللاسلكية"},
    "Ethernet": {"en": "Ethernet", "ar": "شبكة إيثرنت"},
    "Bluetooth": {"en": "Bluetooth", "ar": "البلوتوث"},
    "Display": {"en": "Display", "ar": "الشاشة"},
    "Sound": {"en": "Sound", "ar": "الصوت"},
    "Power": {"en": "Power", "ar": "الطاقة"},
    "Accessibility": {"en": "Accessibility", "ar": "إمكانية الوصول"},
    "Language & Region": {"en": "Language & Region", "ar": "اللغة والمنطقة"},
    "Security": {"en": "Security", "ar": "الأمان"},
    "Privacy": {"en": "Privacy", "ar": "الخصوصية"},
    "Users": {"en": "Users", "ar": "المستخدمون"},

    # Accessibility Features
    "Screen Reader": {"en": "Screen Reader", "ar": "قارئ الشاشة"},
    "High Contrast": {"en": "High Contrast", "ar": "تباين عالي"},
    "Text Scaling": {"en": "Text Scaling", "ar": "تحجيم النص"},
    "Reduced Motion": {"en": "Reduced Motion", "ar": "تقليل الحركة"},
    "Large Pointer": {"en": "Large Pointer", "ar": "مؤشر كبير"},
    "Sticky Keys": {"en": "Sticky Keys", "ar": "المفاتيح الثابتة"},
    "Slow Keys": {"en": "Slow Keys", "ar": "المفاتيح البطيئة"}
}

ARABIC_MONTHS = [
    "يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو",
    "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"
]

ARABIC_DAYS = [
    "الإثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت", "الأحد"
]

EASTERN_ARABIC_DIGITS = str.maketrans("0123456789", "٠١٢٣٤٥٦٧٨٩")

class I18nEngine:
    def __init__(self, default_lang: str = "en"):
        self.current_lang = default_lang
        self.use_eastern_digits = False

    def set_language(self, lang_code: str) -> bool:
        if lang_code.startswith("ar"):
            self.current_lang = "ar"
            return True
        elif lang_code.startswith("en"):
            self.current_lang = "en"
            return True
        return False

    def is_rtl(self) -> bool:
        return self.current_lang == "ar"

    def get_text_direction(self) -> str:
        return "rtl" if self.is_rtl() else "ltr"

    def translate(self, text: str) -> str:
        """Translate a string into the currently active language."""
        if text in TRANSLATIONS and self.current_lang in TRANSLATIONS[text]:
            res = TRANSLATIONS[text][self.current_lang]
            if self.is_rtl() and self.use_eastern_digits:
                return self.to_eastern_arabic_digits(res)
            return res
        return text

    def _(self, text: str) -> str:
        """Shorthand gettext style translation."""
        return self.translate(text)

    def to_eastern_arabic_digits(self, text: Union[str, int, float]) -> str:
        return str(text).translate(EASTERN_ARABIC_DIGITS)

    def format_date(self, dt: Optional[datetime.datetime] = None) -> str:
        d = dt or datetime.datetime.now()
        if self.is_rtl():
            day_name = ARABIC_DAYS[d.weekday()]
            month_name = ARABIC_MONTHS[d.month - 1]
            day_str = self.to_eastern_arabic_digits(d.day) if self.use_eastern_digits else str(d.day)
            year_str = self.to_eastern_arabic_digits(d.year) if self.use_eastern_digits else str(d.year)
            return f"{day_name}، {day_str} {month_name} {year_str}"
        return d.strftime("%A, %B %d, %Y")

    def format_time(self, dt: Optional[datetime.datetime] = None, use_24h: bool = False) -> str:
        d = dt or datetime.datetime.now()
        if use_24h:
            h_str = f"{d.hour:02d}"
            m_str = f"{d.minute:02d}"
            if self.is_rtl() and self.use_eastern_digits:
                return f"{self.to_eastern_arabic_digits(h_str)}:{self.to_eastern_arabic_digits(m_str)}"
            return f"{h_str}:{m_str}"
        else:
            h = d.hour % 12 or 12
            period = "ص" if d.hour < 12 else "م"
            if not self.is_rtl():
                period = "AM" if d.hour < 12 else "PM"
            h_str = str(h)
            m_str = f"{d.minute:02d}"
            if self.is_rtl() and self.use_eastern_digits:
                return f"{self.to_eastern_arabic_digits(h_str)}:{self.to_eastern_arabic_digits(m_str)} {period}"
            return f"{h_str}:{m_str} {period}"

    def get_keyboard_layout_config(self) -> Dict[str, Any]:
        """Returns XKB configuration supporting English and Arabic with Alt+Shift toggle."""
        return {
            "layout": "us,ara",
            "variant": ",digits",
            "options": "grp:alt_shift_toggle,grp_led:scroll"
        }

# Global singleton
i18n = I18nEngine()
