#!/usr/bin/env bash
# AetherOS Wayland Session Coordinator & Entrypoint
set -euo pipefail

# Handle session management CLI commands
if [[ "${1:-}" == "--lock" ]]; then
    exec swaylock -f -c 0B0F19 --indicator-radius 100 --ring-color 00D2FF --key-hl-color 6366F1
elif [[ "${1:-}" == "--logout" ]]; then
    exec loginctl terminate-user "$USER"
elif [[ "${1:-}" == "--suspend" ]]; then
    exec systemctl suspend
elif [[ "${1:-}" == "--reboot" ]]; then
    exec systemctl reboot
elif [[ "${1:-}" == "--poweroff" ]]; then
    exec systemctl poweroff
fi

# Export standard Wayland environment variables
export XDG_CURRENT_DESKTOP=AetherOS
export XDG_SESSION_DESKTOP=AetherOS
export XDG_SESSION_TYPE=wayland
export GDK_BACKEND=wayland,x11
export QT_QPA_PLATFORM="wayland;xcb"
export SDL_VIDEODRIVER=wayland
export CLUTTER_BACKEND=wayland
export MOZ_ENABLE_WAYLAND=1
export _JAVA_AWT_WM_NONREPARENTING=1

# Audio & Bus Activation
systemctl --user import-environment WAYLAND_DISPLAY XDG_CURRENT_DESKTOP || true
dbus-update-activation-environment --systemd WAYLAND_DISPLAY XDG_CURRENT_DESKTOP || true

# Start Wayland Compositor (Wayfire primary, Labwc fallback)
if command -v wayfire >/dev/null 2>&1; then
    exec wayfire -c /etc/wayfire/wayfire.ini
elif command -v labwc >/dev/null 2>&1; then
    exec labwc -c /etc/labwc/labwc.xml
else
    echo "Error: No Wayland compositor found (wayfire or labwc required)." >&2
    exit 1
fi
