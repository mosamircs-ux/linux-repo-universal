# AetherOS System Administration Guide

This guide covers daily maintenance, system upgrades, Btrfs snapshot rollbacks, service management, and network deployments.

---

## 1. System Upgrades & Transactional Snapshots

AetherOS integrates automated safety snapshots before every update.

### Command Line Upgrades
```bash
# Check and apply updates safely
aether-updater --check
aether-updater --apply
```

### Manual Snapshot Management
```bash
# Create a named snapshot
sudo btrfs subvolume snapshot / /.snapshots/@manual-backup-$(date +%F)

# List snapshots
ls -la /.snapshots/

# Revert to a previous snapshot
sudo btrfs subvolume set-default /.snapshots/@manual-backup-2026-08-22
sudo reboot
```

---

## 2. Audio & Device Management

AetherOS uses PipeWire for audio routing:
```bash
# Inspect PipeWire status
wpctl status

# Set default audio output volume
wpctl set-volume @DEFAULT_AUDIO_SINK@ 75%
```

---

## 3. Unattended / Automated Network Deployments

Use `installer_cli.py` to deploy AetherOS on servers or VM pools:
```bash
python3 /usr/lib/aether/installer/installer_cli.py \
    --disk /dev/nvme0n1 \
    --btrfs \
    --username admin \
    --hostname aether-server-01 \
    --locale en_US.UTF-8
```
