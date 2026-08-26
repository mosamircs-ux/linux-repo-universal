#!/usr/bin/env python3
"""
AetherOS Notifications Settings Backend
Configures system-wide notifications, Do Not Disturb, sound alerts, and lock screen privacy.
"""

from typing import Dict, Any, List

class NotificationsBackend:
    @staticmethod
    def get_notification_settings() -> Dict[str, Any]:
        return {
            "do_not_disturb": False,
            "show_banners": True,
            "show_on_lock_screen": False,
            "play_sound": True,
            "apps": [
                {"id": "firefox", "name": "Firefox", "enabled": True, "sound": True},
                {"id": "thunderbird", "name": "Thunderbird", "enabled": True, "sound": True},
                {"id": "aether-updater", "name": "System Updater", "enabled": True, "sound": True},
            ]
        }
