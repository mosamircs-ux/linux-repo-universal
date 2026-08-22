# AetherOS Quality Assurance & Automated Testing Strategy

This document outlines the multi-tiered testing strategy and validation methodology for AetherOS.

---

## 1. Quality Assurance Mandate

**Core Rule:** *Never claim a component or feature works unless it has been tested and verified.*

Every subsystem in AetherOS is covered by automated testing:
- **Unit Tests:** Verify individual business logic, state machines, and data models in isolation.
- **Integration Tests:** Verify configurations, XML schemas, security policies, and packaging metadata across subsystem boundaries.
- **Localization Tests:** Verify translation key completeness, syntax, and bi-directional (RTL) layout switching.
- **Boot & Virtualization Tests:** Verify ISO filesystem integrity, bootloader headers, and QEMU virtualized execution.

---

## 2. Test Suite Architecture (`/tests`)

```
/tests/
├── /unit
│   ├── test_settings.py       # Settings state, language switching, persistence, system info
│   ├── test_installer.py      # Btrfs/EXT4 partition calculations, EFI/BIOS flags, runner progress
│   ├── test_desktop_shell.py  # Dock pinning, TopBar state, Launcher search, QuickSettings, Notifications
│   └── test_services.py       # Rollback agent failure counter, Crash handler privacy sanitization
├── /integration
│   └── test_packaging_and_security.py # Polkit XML validity, AppArmor network blocking, sysctl checks
├── /i18n
│   └── test_locale.py         # English and Arabic translation parity and RTL orientation
└── /qemu-boot
    └── test_iso_boot.py       # ISO-9660 / hybrid signature checks and QEMU invocation tests
```

---

## 3. Test Suites & Verification Criteria

### 3.1 Unit Testing (`tests/unit/`)
- **Settings Subsystem (`test_settings.py`):**
  - Asserts default language (`en`), dark mode (`True`), and accent color (`#00D2FF`).
  - Asserts language switching to Arabic (`ar`) correctly triggers `is_rtl() == True` and returns Arabic strings.
  - Asserts JSON configuration file persistence and reload capability.
- **Installer Subsystem (`test_installer.py`):**
  - Asserts that UEFI installation creates partition 1 as `fat32` ESP at `/boot/efi` with `boot, esp` flags.
  - Asserts that Btrfs mode configures subvolumes: `@`, `@home`, `@snapshots`, and `@var_log` with `compress=zstd:3`.
  - Asserts that BIOS installation creates a `bios_grub` partition.
  - Asserts installer runner progress reporting triggers all 7 installation milestones up to 100%.
- **Desktop Shell Subsystem (`test_desktop_shell.py`):**
  - Asserts dock pinning and unpinning updates the persistent JSON model.
  - Asserts application launcher indexes `.desktop` files, performs fuzzy search, and filters by category.
  - Asserts quick settings toggles (Wi-Fi, Bluetooth, Night Light, Dark Mode) and volume scaling.
  - Asserts notification queue posting, urgency levels, and dismissal.
- **Services Subsystem (`test_services.py`):**
  - Asserts rollback agent increments failure count and resets upon boot success.
  - Asserts crash handler scrubs IP addresses (`[REDACTED_IP]`), emails (`[REDACTED_EMAIL]`), and home directory paths (`/home/[USER]`).

### 3.2 Integration & Security Testing (`tests/integration/`)
- **Polkit XML Validation:** Parses `org.aetheros.policy` using Python XML `ElementTree` to ensure valid DTD compliance and action declarations (`org.aetheros.updater.check-and-apply`, `org.aetheros.snapshots.rollback`).
- **AppArmor Egress Check:** Confirms `usr.bin.aether-crash-handler` contains explicit `deny network raw` rules.
- **Packaging Syntax:** Verifies all 5 Debian metapackages contain required `Package:`, `Maintainer:`, and `Description:` fields.

### 3.3 Localization & RTL Testing (`tests/i18n/`)
- Verifies symmetric key parity between `TRANSLATIONS["en"]` and `TRANSLATIONS["ar"]`.
- Ensures zero untranslated UI strings in the Arabic dictionary.

### 3.4 Virtualization & Boot Testing (`tests/qemu-boot/`)
- Verifies that the assembled ISO contains valid bootloader signatures (`CD001`, `EFI`, or `AETHEROS`).
- Validates QEMU command line parameters for headless and hardware-accelerated execution (`scripts/run-vm-test.sh`).

---

## 4. Executing the Test Suite

```bash
# Run all automated test suites
python3 -m unittest discover -s tests -v
```

Expected output:
```
Ran 23 tests in ~1.1s
OK
```
