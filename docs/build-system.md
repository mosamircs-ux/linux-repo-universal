# AetherOS Build System & Release Engineering Architecture

This document specifies the pipeline for assembling, packaging, compressing, and validating reproducible AetherOS Live ISO distribution images.

---

## 1. Build Pipeline Overview

The AetherOS build architecture is divided into five deterministic stages:

```
+-------------------------------------------------------------------------+
| [Stage 1] Automated Verification & Package Linting                     |
| - Execute unit tests (tests/unit/)                                      |
| - Verify packaging control files (packages/build-packages.py)            |
| - Validate Polkit XML and AppArmor profiles (tests/integration/)         |
+-------------------------------------------------------------------------+
                                    │
                                    ▼
+-------------------------------------------------------------------------+
| [Stage 2] Root Filesystem Assembly (build-rootfs.py)                   |
| - Create standard FHS directory structure (bin, sbin, usr, etc.)        |
| - Stage /kernel sysctl, modules-load, and boot cmdline defaults         |
| - Stage /system services, pipewire, networkmanager, and udev rules       |
| - Stage /themes artwork, wallpapers, GTK CSS themes, and fonts          |
| - Inject /etc/os-release identifying AetherOS Solstice 1.0 LTS          |
+-------------------------------------------------------------------------+
                                    │
                                    ▼
+-------------------------------------------------------------------------+
| [Stage 3] SquashFS Compression (mksquashfs)                             |
| - Compress rootfs using Zstandard algorithm (zstd -Xcompression-level 19)|
| - Output compressed image to iso_root/casper/filesystem.squashfs         |
| - Generate kernel (vmlinuz) and initial ramdisk (initrd) artifacts      |
+-------------------------------------------------------------------------+
                                    │
                                    ▼
+-------------------------------------------------------------------------+
| [Stage 4] Bootloader Configuration & ISO Assembly (build-iso.py)        |
| - Stage UEFI GRUB2 configuration in /EFI/BOOT/grub.cfg                  |
| - Stage BIOS GRUB2 configuration in /boot/grub/grub.cfg                 |
| - Execute xorriso / mkisofs to build hybrid UEFI/BIOS bootable ISO      |
+-------------------------------------------------------------------------+
                                    │
                                    ▼
+-------------------------------------------------------------------------+
| [Stage 5] Reproducibility Check & Cryptographic Verification            |
| - Compute SHA256 checksum (reproducible-check.py)                       |
| - Output aetheros-1.0.0-solstice-amd64.iso.sha256                       |
+-------------------------------------------------------------------------+
```

---

## 2. Key Build Scripts & Roles

### 2.1 Package Validator (`packages/build-packages.py`)
- Inspects `debian/control` and rules files for all core packages:
  - `aether-base`
  - `aether-desktop-core`
  - `aether-artwork`
  - `aether-settings`
  - `aether-installer`
- Asserts strict dependency versioning and package metadata integrity.

### 2.2 RootFS Assembler (`build/scripts/build-rootfs.py`)
- Prepares the target staging filesystem.
- Installs `/system`, `/kernel`, `/themes`, and application files into their correct absolute paths.
- Writes the standard `/etc/os-release` manifest.

### 2.3 ISO Generator (`build/scripts/build-iso.py`)
- Configures GRUB2 live boot entries with default boot parameters:
  - `boot=casper quiet splash zswap.enabled=0 apparmor=1 security=apparmor`
  - Safe graphics fallback mode (`nomodeset`)
  - Memory test entry
  - UEFI firmware setup entry
- Executes `mksquashfs` with `zstd:19` for optimal decompression speed during live boot.
- Builds the hybrid ISO using `xorriso` with El Torito BIOS boot catalog and EFI System Partition headers.

### 2.4 Master Build Orchestrator (`scripts/build-all.sh`)
- Coordinates the complete build process end-to-end with a single command:
  ```bash
  ./scripts/build-all.sh
  ```

---

## 3. Reproducibility & Determinism Standards

To ensure bit-for-bit reproducible builds:
1. **Pinned Timestamps:** File modification times within archives and SquashFS are normalized using `SOURCE_DATE_EPOCH`.
2. **Deterministic Compression:** `zstd` is executed with deterministic block sizes (128KB) and duplicate elimination enabled.
3. **Automated Checksum Verification:** Every build produces an authenticated SHA256 manifest:
   ```bash
   python3 build/scripts/reproducible-check.py aetheros-1.0.0-solstice-amd64.iso
   ```

---

## 4. Continuous Integration Pipeline (`/ci`)

AetherOS includes GitHub Actions workflows:
- **`ci/lint.yml`:** Automatically executes all test suites and package validators on pull requests.
- **`ci/build-iso.yml`:** Compiles release ISO images on tag creation and attaches verified ISO and SHA256 checksum artifacts.
