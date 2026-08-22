# AetherOS System Architecture Specification

**Version:** 1.0.0 LTS (*Solstice*)  
**Architecture:** x86_64 / ARM64  
**Kernel Base:** Linux 6.8+ LTS  
**Display Server:** Native Wayland (XWayland fallback)  

---

## 1. Architectural Overview

AetherOS is designed as a modular, lightweight, and high-responsiveness Linux distribution providing Ubuntu-style workflow ergonomics with an independent identity, enhanced performance, and robust recovery capabilities.

```
+-------------------------------------------------------------------------+
|                              Desktop Layer                              |
|   +---------------+ +-----------------+ +-------------+ +-----------+   |
|   |  Aether Dock  | |  Aether TopBar  | | AppLauncher | | QuickSet. |   |
|   +---------------+ +-----------------+ +-------------+ +-----------+   |
|   |  Settings Hub | |  Software Hub   | |   Updater   | | Welcome   |   |
|   +---------------+ +-----------------+ +-------------+ +-----------+   |
+-------------------------------------------------------------------------+
|                             Compositor Layer                            |
|             Wayfire (Primary) / Labwc (Fallback) + XWayland             |
+-------------------------------------------------------------------------+
|                              System Services                            |
|    PipeWire | NetworkManager | BlueZ | AppArmor | Polkit | systemd      |
|    Aether Rollback Agent | Aether Crash Handler | Update Daemon         |
+-------------------------------------------------------------------------+
|                        Kernel & Hardware Enablement                     |
|    Linux Kernel 6.8+ (BBR, zRAM zstd:3, Low-Latency sysctl, UDev)       |
+-------------------------------------------------------------------------+
|                              Storage Layer                              |
|    Btrfs Subvolumes (@, @home, @snapshots, @var_log) / EXT4 + GPT/EFI   |
+-------------------------------------------------------------------------+
```

---

## 2. Key Subsystems

### 2.1 Kernel and Memory Management
- **zRAM Swap:** Dynamically allocated compressed RAM swap (50% of physical memory, up to 8GB) using `zstd` compression.
- **Sysctl Low-Latency Tuning:** Reduced swappiness (`vm.swappiness=15`), aggressive cache retention (`vm.vfs_cache_pressure=50`), and Google BBR TCP congestion control (`net.ipv4.tcp_congestion_control=bbr`).
- **I/O Scheduler:** Multi-queue NVMe/SSD scheduling with `BFQ` for rotational storage.

### 2.2 Desktop Environment
- **Compositor:** Wayfire 3D Wayland compositor offering smooth hardware-accelerated transitions and window snapping (`Super+Left`, `Super+Right`, `Super+Up`).
- **Shell Components:** Modular Python/GTK-LayerShell components running as independent processes. A crash in one panel does not crash the session.
- **Bi-Directional LTR/RTL Engine:** Real-time layout mirroring for Arabic locales.

### 2.3 Storage and Transactional Rollbacks
- **Btrfs Layout:**
  - `@`: Root filesystem mounted with `noatime,compress=zstd:3`.
  - `@home`: User personal data.
  - `@snapshots`: Stored pre-upgrade and manual system snapshots.
  - `@var_log`: Persistent system logs preserved across rollbacks.
- **Automatic Fallback:** `aether-rollback-agent` detects 3 consecutive failed boots and restores the previous known good snapshot automatically.
