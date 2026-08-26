#!/usr/bin/env bash
# AetherOS Wayland Session Startup Script
set -e

# Export standard environment variables
export XDG_CURRENT_DESKTOP=AetherOS
export XDG_SESSION_DESKTOP=AetherOS
export XDG_SESSION_TYPE=wayland
export GDK_BACKEND=wayland,x11
export QT_QPA_PLATFORM=wayland;xcb
export SDL_VIDEODRIVER=wayland
export CLUTTER_BACKEND=wayland
export MOZ_ENABLE_WAYLAND=1

# Audio & Bus Activation
systemctl --user import-environment WAYLAND_DISPLAY XDG_CURRENT_DESKTOP || true
dbus-update-activation-environment --systemd WAYLAND_DISPLAY XDG_CURRENT_DESKTOP || true

# Start Wayland Compositor (Wayfire or Labwc fallback)
if command -v wayfire >/dev/null 2>&1; then
    exec wayfire -c /etc/wayfire/wayfire.ini
elif command -v labwc >/dev/null 2>&1; then
    exec labwc -c /etc/labwc/labwc.xml
else
    echo "Error: No Wayland compositor found." >&2
    exit 1
fi
