# AetherOS (Solstice LTS)

<div align="center">
  <img src="themes/artwork/logo.svg" width="160" height="160" alt="AetherOS Logo" />
  <h1>AetherOS</h1>
  <p><strong>A Production-Grade Lightweight Linux Operating System</strong></p>
  <p>Inspired by Ubuntu workflow ergonomics • Original Identity • Wayland Native • Bilingual EN/AR RTL • Safe Rollback Protection</p>
</div>

---

## Highlights

- **Ubuntu-like Usability:** Intuitive left dock, top panel, full application launcher, unified quick settings, and workspace switcher.
- **Wayland Native:** Modern, hardware-accelerated compositor (Wayfire / Labwc) with smooth window snapping.
- **Transactional Safety:** Automatic pre-update Btrfs snapshots with 1-click recovery and boot-failure auto-rollback.
- **First-Class Bilingual Support:** Instant switching between English and Arabic (`ar`) with full right-to-left (RTL) layout mirroring.
- **Zero-Telemetry Security:** Hardened AppArmor profiles, fine-grained Polkit rules, and sanitized local-only crash logs.
- **Reproducible ISO Builds:** Complete deterministic ISO build engine for UEFI & BIOS boots.

---

## Repository Layout

```
├── /kernel      # Kernel performance parameters, sysctl tuning, module auto-load
├── /system      # systemd units, PipeWire audio, NetworkManager, Polkit, AppArmor
├── /desktop     # Wayland compositor configs & modular desktop shell (dock, topbar, launcher)
├── /apps        # Aether Settings, Software Hub, Updater, and Welcome wizard
├── /packages    # Debian metapackages (aether-base, aether-desktop-core, aether-artwork)
├── /installer   # Graphical & CLI bilingual installer with Btrfs/EFI support
├── /themes      # Original vector SVG logos, 4K wallpapers, GTK 3/4 themes, Plymouth, GRUB
├── /services    # Update daemon, rollback agent, and privacy-respecting crash handler
├── /tests       # Unit, integration, localization, and QEMU boot test suites
├── /build       # Rootfs assembly and reproducible ISO builder
├── /docs        # Complete system architecture and administration documentation
├── /scripts     # Master build orchestration and VM test runners
└── /ci          # Continuous integration lint and release pipelines
```

---

## Quick Start: Build & Test

```bash
# 1. Run full test suite
python3 -m unittest discover -s tests -v

# 2. Build release ISO
./scripts/build-all.sh

# 3. Test in QEMU VM
./scripts/run-vm-test.sh aetheros-1.0.0-solstice-amd64.iso
```

---

## Documentation

- [System Architecture](docs/ARCHITECTURE.md)
- [Security & Privacy Model](docs/SECURITY.md)
- [System Administration Guide](docs/ADMIN_GUIDE.md)
- [User Guide](docs/USER_GUIDE.md)
- [Developer Guide](docs/DEVELOPER_GUIDE.md)
- [Arabic Localization Guide](docs/I18N_ARABIC.md)

---

## License

GPL-3.0 / MIT. AetherOS Project.
