# AetherOS Master Technical Architecture

**Distribution Name:** AetherOS  
**Codename:** Solstice  
**Release Model:** Long Term Support (LTS) & Point Releases  
**Base Foundation:** Ubuntu 24.04 LTS / Debian 12 Stable  
**Primary Architecture:** `x86_64` (AMD64) with `aarch64` (ARM64) tier-2 target  

---

## 1. Executive Summary & Design Philosophy

AetherOS is a lightweight, production-grade Linux operating system engineered to combine the workflow ergonomics and user-friendliness of Ubuntu with an independent visual identity, high-performance Wayland compositor, low-latency kernel tuning, zero-telemetry security, first-class bilingual Arabic/English internationalization, and transactional snapshot rollback resilience.

### Core Architectural Principles:
1. **Lightest Mature Technology:** Avoid reinventing core OS components where stable, optimized Linux standards already excel (systemd, PipeWire, NetworkManager, Wayland/wlroots, Btrfs, AppArmor, Polkit).
2. **Modular Decoupling:** Desktop shell widgets (Dock, TopBar, Launcher, QuickSettings, Notifications) operate as independent, decoupled processes communicate over D-Bus and Wayland protocols; a failure in any individual widget never crashes the compositor or desktop session.
3. **Transactional Safety:** Every system update automatically creates an atomic filesystem snapshot. A boot health monitor automatically reverts to the last known good state if boot failures occur.
4. **Zero Telemetry by Construction:** No analytics, tracking, or network telemetry daemons exist in the distribution. Diagnostic reports are sanitized locally and retained strictly on the user's machine.
5. **Universal Internationalization:** Full bi-directional (LTR/RTL) rendering engine out of the box with complete parity between English and Arabic.

---

## 2. Monorepo Repository Structure

The complete distribution source code, configurations, packaging definitions, and build pipelines are maintained in a structured monorepo:

```
/mnt/c/Users/mohamedsamir/Documents/linux-repo-universal/
├── /kernel
│   ├── /sysctl.d            # Low-latency virtual memory and network parameters
│   ├── /cmdline.d           # Bootloader kernel command line defaults
│   └── /modules-load.d      # Early kernel modules (zram, overlay, btrfs)
├── /system
│   ├── /systemd             # Custom systemd services, targets, and zram-generator
│   ├── /polkit              # Granular privilege policies (org.aetheros.*)
│   ├── /pipewire            # Low-latency audio profiles and PulseAudio bridge
│   ├── /networkmanager      # NetworkManager config with MAC address randomization
│   ├── /security            # AppArmor profiles (aether-updater, crash-handler)
│   └── /udev                # UDev rules for backlight, GPU render nodes, audio
├── /desktop
│   ├── /compositor          # Wayfire and Labwc Wayland compositor configurations
│   └── /shell
│       ├── /aether-dock     # Desktop dock engine (left/bottom, RTL support)
│       ├── /aether-topbar   # Status panel, workspace pager, clock/calendar
│       ├── /aether-launcher # Categorized fuzzy-search application launcher
│       ├── /aether-quicksettings # Control center (WiFi, BT, Volume, Night Light)
│       ├── /aether-notifications # Freedesktop D-Bus notification daemon
│       └── /aether-session  # Wayland session startup scripts and desktop entry
├── /apps
│   ├── /aether-settings     # Bilingual Control Center (Display, Network, Language, Audio)
│   ├── /aether-software     # Unified package manager (APT + Flatpak / Flathub)
│   ├── /aether-updater      # Update manager with Btrfs snapshot rollback UI
│   ├── /aether-welcome      # First-boot interactive onboarding wizard
│   └── /aether-terminal     # Terminal launcher wrapper and palette
├── /packages
│   ├── /aether-base         # Core system configuration metapackage
│   ├── /aether-desktop-core # Wayland desktop environment metapackage
│   ├── /aether-artwork      # Wallpapers, GTK themes, icons, boot themes
│   ├── /aether-settings     # Packaging recipe for settings manager
│   ├── /aether-installer    # Packaging recipe for system installer
│   └── build-packages.py    # Packaging build and validation tool
├── /installer
│   ├── /src
│   │   ├── /engine          # Partitioning engine (GPT/EFI, Btrfs subvolumes, EXT4)
│   │   ├── /gui             # Modern GTK bilingual wizard with Arabic RTL
│   │   └── /cli             # Unattended / headless installation runner
│   └── /assets              # Installer branding and assets
├── /themes
│   ├── /artwork             # Vector SVG logos, 4K wallpapers (Solstice Dark/Light)
│   ├── /gtk-theme           # Modern GTK 3.0 and GTK 4.0 CSS stylesheets
│   ├── /icon-theme          # Scalable vector icon theme manifest
│   ├── /plymouth            # Animated glowing boot splash
│   ├── /grub                # HD 1080p/4K GRUB2 bootloader theme
│   └── /fonts               # Fontconfig rules for Cairo, Tajawal, Amiri, Inter
├── /services
│   ├── /aether-updater-daemon # Background update check coordinator
│   ├── /aether-rollback-agent # Boot health watchdog and automated snapshot revert
│   └── /aether-crash-handler  # Privacy-respecting local crash logger
├── /tests
│   ├── /unit                # Unit tests for settings, installer, shell, services
│   ├── /integration         # Packaging, Polkit XML, AppArmor security tests
│   ├── /i18n                # Arabic/English translation completeness & RTL tests
│   └── /qemu-boot           # Headless QEMU automated boot validation runner
├── /build
│   ├── /config              # Package manifests (packages.list)
│   └── /scripts             # RootFS assembler, ISO generator, reproducible checker
├── /docs                    # Architecture, components, security, build, testing specs
├── /scripts                 # Orchestration scripts (build-all.sh, run-vm-test.sh)
└── /ci                      # Continuous integration workflows (lint.yml, build-iso.yml)
```

---

## 3. Subsystem Technical Breakdown

### 3.1 Kernel & Low-Latency Tuning Strategy
- **Kernel Stream:** Linux 6.8+ LTS with Ubuntu HWE (Hardware Enablement) patches for broad silicon compatibility (Intel Core Ultra, AMD Ryzen 7000/8000, Qualcomm ARM64).
- **Virtual Memory Tuning (`/kernel/sysctl.d/99-aether-performance.conf`):**
  - `vm.swappiness = 15`: Favors RAM page residency over aggressive disk swapping.
  - `vm.vfs_cache_pressure = 50`: Retains directory and inode caches in memory to accelerate filesystem operations and application launch times.
  - `vm.dirty_ratio = 10` & `vm.dirty_background_ratio = 5`: Prevents large I/O stalls during heavy disk writes.
  - `vm.page-cluster = 0`: Optimizes paging for zRAM compressed memory.
- **Inotify & File Descriptors:** `fs.inotify.max_user_watches = 524288` to accommodate modern IDEs and file watchers without starvation.
- **Network Optimization:** Google BBR congestion control (`net.ipv4.tcp_congestion_control = bbr`) with Fair Queuing (`net.core.default_qdisc = fq`) for low network latency under bufferbloat.
- **Memory Compression:** `systemd-zram-generator` initializes `/dev/zram0` with `zstd` compression dynamically sized to 50% of physical RAM (up to 8GB), eliminating disk thrashing on low-memory systems.

### 3.2 Init, systemd & Boot Architecture
- **Init Manager:** `systemd` (PID 1) leveraging socket-activated services, slice-based cgroup isolation (`user.slice`, `system.slice`), and parallelized target transitions.
- **Boot Optimization Target:** Sub-3-second kernel-to-greeter handoff on NVMe SSDs.
- **Bootloader Strategy:** Dual UEFI (ESP partition with `bootx64.efi`) and Legacy BIOS (El Torito / MBR) support via GRUB2.
- **Plymouth Splash:** Flicker-free graphical transition using kernel mode setting (DRM/KMS) directly into the desktop session.
- **Service Minimization:** Unnecessary background daemons (telemetry, legacy print daemons unless activated, indexers) are omitted from the default boot graph.

### 3.3 Display Server & Desktop Architecture
- **Primary Display Protocol:** Wayland native.
- **Compositor Engine:**
  - **Wayfire (Primary):** Modular 3D Wayland compositor built on `wlroots`, delivering smooth animations, Ubuntu-style window tiling (`Super+Left`, `Super+Right`, `Super+Up`), workspace expo, and low input latency.
  - **Labwc (Fallback):** Ultra-lightweight stacking Wayland compositor for low-spec hardware and virtual machines.
- **XWayland Bridge:** Transparent background XWayland server started on-demand for legacy X11 applications and gaming compatibility.
- **Modular Shell:**
  - **Aether Dock:** Pinned applications, active window indicators, configurable orientation (left or bottom), and automatic RTL alignment.
  - **Aether TopBar:** Global status, workspace indicator, clock/calendar, and Quick Settings toggle.
  - **Aether AppLauncher:** Categorized full-text fuzzy search indexing `.desktop` files.
  - **Aether QuickSettings:** Slide-out control center for Wi-Fi, Bluetooth, PipeWire volume/mic sliders, brightness, Night Light (`wlsunset`), and Dark Mode.
  - **Aether Notifications:** D-Bus `org.freedesktop.Notifications` server with grouped history and action buttons.

### 3.4 Audio Architecture
- **Audio Engine:** PipeWire 1.0+ with WirePlumber session manager.
- **Compatibility Layers:** Native `pipewire-pulse` (PulseAudio emulation) and `pipewire-alsa` (ALSA plugin bridge) providing 100% compatibility for existing Linux applications and games.
- **Latency Profile (`/system/pipewire/pipewire.conf.d/10-aether-audio.conf`):** Configured for 48,000 Hz sample rate with a 256-quantum buffer size and real-time scheduling priority (`rt.prio = 88`), ensuring jitter-free audio and low-latency audio capture.

### 3.5 Networking & Bluetooth Architecture
- **Network Manager:** NetworkManager with `wpa_supplicant` / `iwd` backend for high-speed Wi-Fi roaming and 802.1X enterprise authentication.
- **Privacy Hardening:** Wi-Fi MAC address randomization enabled by default during network probing and unique randomized MAC generated per SSID connection profile.
- **Bluetooth Stack:** BlueZ 5 with PipeWire SPA Bluetooth audio plugin supporting LDAC, AAC, aptX, and SBC codecs with automatic HID device reconnection.

### 3.6 Storage Architecture & Filesystem Strategy
- **Primary Filesystem:** Btrfs with transparent Zstandard compression (`compress=zstd:3`).
- **Subvolume Layout:**
  - `@` (mounted at `/`): Root operating system filesystem.
  - `@home` (mounted at `/home`): User data, configuration, and personal documents.
  - `@snapshots` (mounted at `/.snapshots`): Read-only pre-update and manual restore points.
  - `@var_log` (mounted at `/var/log`): System log files preserved across rollbacks.
- **Fallback Filesystem:** EXT4 standard journaling filesystem for legacy BIOS or specialized embedded deployments.

### 3.7 Update & Rollback Recovery Architecture
- **Transactional Update Hook:** Pre-upgrade hook (`aether-snapshot-pre-upgrade`) creates an atomic snapshot before APT or Flatpak upgrades are committed.
- **Boot-Health Watchdog (`aether-rollback-agent`):** Tracks consecutive boot attempts. If the system fails to reach `graphical.target` 3 consecutive times, it automatically switches the Btrfs default subvolume back to the last verified snapshot.
- **GRUB Btrfs Integration:** All snapshots are indexed in the GRUB boot menu, allowing users to boot into any previous system state directly from the bootloader.

### 3.8 Security & Permissions Model
- **LSM (Linux Security Module):** AppArmor active in enforcing mode with tailored profiles for update tools, browsers, and background services.
- **Privilege Separation:** Granular Polkit policies under `org.aetheros.*` eliminate blank `sudo` requirements for desktop settings, network management, and updater tasks.
- **Zero Telemetry Guarantee:** Crash handler (`aether-crash-handler`) sanitizes backtraces (redacting IPs, emails, and home usernames) and stores reports strictly in `/var/log/aether/crashes` with explicit AppArmor rules denying raw network egress (`deny network raw`).

### 3.9 Package Management & Application Delivery
- **Base Packages:** `apt` and `dpkg` utilizing curated AetherOS repositories combined with Ubuntu 24.04 LTS upstream mirrors.
- **Sandboxed Application Delivery:** Flatpak pre-configured with Flathub out-of-the-box, providing isolated application execution and fine-grained portal permissions.
- **Aether Software Hub:** Unified graphical store allowing users to search, install, update, and manage both native APT packages and sandboxed Flatpaks seamlessly.

### 3.10 Internationalization & Arabic RTL Support
- **First-Class Dual Language:** Immediate live switching between English (`en`) and Arabic (`ar`).
- **RTL Mirroring:** Full right-to-left layout adaptation across desktop dock, panels, settings, and installer.
- **Font Stack (`/themes/fonts/50-aether-fonts.conf`):**
  - UI Sans-Serif: *Inter* with *Cairo* & *Tajawal* Arabic glyph fallbacks.
  - Serif: *Amiri* for classical typesetting.
  - Monospace: *JetBrains Mono* for code and terminal clarity.
