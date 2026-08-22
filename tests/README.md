# AetherOS Automated Testing Suite

This directory contains unit tests, integration tests, localization checks, and ISO boot validation suites for AetherOS.

## Test Suites
- **`tests/unit/`**:
  - `test_settings.py`: Settings model, localization switching, and persistence.
  - `test_installer.py`: Partition calculations, EFI/BIOS flags, and Btrfs subvolumes.
  - `test_desktop_shell.py`: Dock pinning, launcher search indexing, quick settings toggles, and notification queue.
  - `test_services.py`: Rollback agent counter logic, privacy crash handler data sanitization.
- **`tests/integration/`**:
  - `test_packaging_and_security.py`: Polkit XML validation, AppArmor profile egress checks, sysctl syntax.
- **`tests/i18n/`**:
  - `test_locale.py`: Parity between English and Arabic UI translation dictionaries and RTL flag triggers.
- **`tests/qemu-boot/`**:
  - `test_iso_boot.py`: End-to-end ISO assembly validation, bootloader structure, and virtualized boot checks.
