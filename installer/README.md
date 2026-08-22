# AetherOS System Installer

This directory contains the system installer for AetherOS, supporting both modern bilingual graphical installation (English and Arabic RTL) and automated CLI/unattended installations.

## Features
- **Storage Management:** Automatic GPT/EFI and MBR/BIOS partition layout.
- **Btrfs Integration:** Sets up `@`, `@home`, `@snapshots`, and `@var_log` subvolumes with transparent `zstd:3` compression.
- **Bilingual Interface:** Instant language switching between English and Arabic with full RTL layout mirroring.
- **Bootloader Configuration:** Automated GRUB2 installation with UEFI NVRAM registration and Secure Boot compatibility.
- **Unattended Deployment:** CLI mode for scripted server and VM provisioning.
