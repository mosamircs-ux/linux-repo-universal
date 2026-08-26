# AetherOS Developer Guide

This guide describes how to develop, test, and contribute to AetherOS core components.

---

## 1. Repository Structure

```
/kernel      - Kernel parameters, sysctl, and module lists
/system      - systemd units, polkit rules, pipewire, and security policies
/desktop     - Wayland compositor configs and desktop shell modules
/apps        - First-party GUI applications (Settings, Software, Updater)
/packages    - Debian metapackages and control recipes
/installer   - Bilingual installer backend and wizard
/themes      - SVG vector artwork, wallpapers, and GTK/GRUB themes
/services    - System daemons (update coordinator, rollback agent, crash logger)
/tests       - Unit, integration, localization, and QEMU boot test suites
/build       - Rootfs assembler and reproducible ISO generator
/docs        - Complete architectural and operational guides
/scripts     - Build orchestration and development tools
/ci          - Continuous integration workflows
```

---

## 2. Running Tests Locally

```bash
# Run all automated test suites
python3 -m unittest discover -s tests -v

# Run package validation
python3 packages/build-packages.py
```

---

## 3. Building the Release ISO

```bash
chmod +x scripts/build-all.sh
./scripts/build-all.sh
```

---

## 4. Booting in QEMU

```bash
chmod +x scripts/run-vm-test.sh
./scripts/run-vm-test.sh aetheros-1.0.0-solstice-amd64.iso
```
