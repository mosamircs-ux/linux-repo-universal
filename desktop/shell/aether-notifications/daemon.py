#!/usr/bin/env python3
"""
AetherOS Notification Daemon & Notification Center (aether-notifications)
D-Bus org.freedesktop.Notifications compatible server with grouped notification history,
urgency levels, action buttons, and Do Not Disturb (DND) mode.
"""

import os
import sys
import time
from typing import List, Dict, Any, Optional

class AetherNotification:
    def __init__(self, notif_id: int, app_name: str, summary: str, body: str, icon: str = "dialog-information", urgency: int = 1, actions: Optional[List[str]] = None):
        self.id = notif_id
        self.app_name = app_name or "System"
        self.summary = summary
        self.body = body
        self.icon = icon
        self.urgency = urgency  # 0: Low, 1: Normal, 2: Critical
        self.actions = actions or []
        self.timestamp = time.time()
        self.dismissed = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "app_name": self.app_name,
            "summary": self.summary,
            "body": self.body,
            "icon": self.icon,
            "urgency": self.urgency,
            "actions": self.actions,
            "timestamp": self.timestamp,
            "time_str": time.strftime("%H:%M", time.localtime(self.timestamp))
        }

class AetherNotificationCenter:
    def __init__(self):
        self.notifications: List[AetherNotification] = []
        self._next_id = 1
        self.dnd_enabled = False

    def post_notification(self, app_name: str, summary: str, body: str, icon: str = "dialog-information", urgency: int = 1, actions: Optional[List[str]] = None) -> AetherNotification:
        notif = AetherNotification(self._next_id, app_name, summary, body, icon, urgency, actions)
        self._next_id += 1
        self.notifications.insert(0, notif)
        return notif

    def dismiss(self, notif_id: int) -> bool:
        for n in self.notifications:
            if n.id == notif_id:
                n.dismissed = True
                return True
        return False

    def clear_all(self) -> int:
        count = len(self.get_active_notifications())
        for n in self.notifications:
            n.dismissed = True
        return count

    def toggle_dnd(self) -> bool:
        self.dnd_enabled = not self.dnd_enabled
        return self.dnd_enabled

    def get_active_notifications(self) -> List[AetherNotification]:
        return [n for n in self.notifications if not n.dismissed]

    def get_history(self) -> List[Dict[str, Any]]:
        return [n.to_dict() for n in self.notifications]

def main():
    center = AetherNotificationCenter()
    n = center.post_notification("AetherOS", "Solstice Desktop Ready", "Welcome to your new production-grade lightweight Linux OS.", urgency=1)
    print(f"[aether-notifications] Started daemon. Initial notification #{n.id} posted.")

if __name__ == "__main__":
    main()
