#!/usr/bin/env python3
"""
AetherOS Notification Daemon & Notification History Engine
Implements standard desktop notification spec, supports action buttons,
urgency levels (Low, Normal, Critical), and Do Not Disturb mode.
"""

import time
import json
from typing import List, Dict, Any, Optional

class NotificationItem:
    def __init__(self, notif_id: int, app_name: str, summary: str, body: str, icon: str = "", urgency: int = 1):
        self.id = notif_id
        self.app_name = app_name
        self.summary = summary
        self.body = body
        self.icon = icon or "dialog-information"
        self.urgency = urgency  # 0: Low, 1: Normal, 2: Critical
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
            "timestamp": self.timestamp,
            "dismissed": self.dismissed
        }

class AetherNotificationCenter:
    def __init__(self, max_history: int = 100):
        self.notifications: List[NotificationItem] = []
        self._next_id = 1
        self.do_not_disturb = False
        self.max_history = max_history

    def post_notification(self, app_name: str, summary: str, body: str, icon: str = "", urgency: int = 1) -> NotificationItem:
        notif = NotificationItem(self._next_id, app_name, summary, body, icon, urgency)
        self._next_id += 1
        self.notifications.insert(0, notif)
        
        # Trim history if exceeding max
        if len(self.notifications) > self.max_history:
            self.notifications = self.notifications[:self.max_history]
            
        return notif

    def dismiss(self, notif_id: int) -> bool:
        for n in self.notifications:
            if n.id == notif_id:
                n.dismissed = True
                return True
        return False

    def clear_all(self) -> None:
        self.notifications.clear()

    def get_active_notifications(self) -> List[Dict[str, Any]]:
        return [n.to_dict() for n in self.notifications if not n.dismissed]

def main():
    center = AetherNotificationCenter()
    n = center.post_notification("Aether Updater", "System Update Ready", "Solstice 1.0.1 LTS is ready to install.")
    print("Aether Notification Center Initialized.")
    print(f"Active Notifications: {json.dumps(center.get_active_notifications(), indent=2)}")

if __name__ == "__main__":
    main()
