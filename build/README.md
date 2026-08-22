# AetherOS Build System & ISO Assembler

This directory contains the root filesystem assembler, SquashFS compression generator, package manifests, and reproducible hybrid UEFI/BIOS ISO image build pipelines.

## Scripts
- **`build/config/packages.list`**: Curated list of kernel, system, and desktop packages.
- **`build/scripts/build-rootfs.py`**: Assembles the staging rootfs, installs custom systemd units, polkit rules, and configurations.
- **`build/scripts/build-iso.py`**: Compresses rootfs into SquashFS with `zstd:19`, configures GRUB2 EFI and BIOS bootloaders, generates bootable ISO, and produces SHA256 checksums.
- **`build/scripts/reproducible-check.py`**: Validates deterministic build outputs.
