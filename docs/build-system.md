# AetherOS Reproducible Build System & Release Architecture

**Distribution:** AetherOS  
**Release:** 1.0.0 LTS (Solstice)  
**Supported Architectures:** `x86_64` (Primary), `arm64` (AArch64 Tier-2)  
**Profiles:** `live`, `installer`, `development`, `minimal`

---

## 1. Overview & Core Standards

AetherOS features an automated, deterministic, and cryptographically verified Linux distribution build engine. Every ISO artifact is bit-for-bit reproducible when provided with the same `SOURCE_DATE_EPOCH`.

### Key Capabilities:
- **Reproducible ISO Generation:** Clamped timestamps, deterministic file sorting, normalized `0:0` UID/GID ownership, and reproducible `zstd` SquashFS compression.
- **Hybrid UEFI & BIOS Booting:** Generates dual-boot media with UEFI GPT (`bootx64.efi` / `bootaa64.efi`) and El Torito / MBR BIOS fallbacks.
- **4 Specialized ISO Profiles:**
  1. `live`: Standard production Wayland desktop with full shell and first-party apps.
  2. `installer`: Dedicated GUI/CLI live installer that boots straight to disk setup.
  3. `development`: Live desktop with full compiler toolchains (GCC, Clang, Rust, Python-dev, CMake, Meson, Linux headers).
  4. `minimal`: Headless server / container baseline with systemd, networking, and Btrfs storage tools.
- **Cryptographic Signatures & Verification:** Automated `SHA256SUMS`, `SHA512SUMS`, and detached GPG signatures (`.sig` / `.asc` / `SHA256SUMS.gpg`).
- **Complete Build Metadata:** Structured `build-info.json` recording Git commits, toolchains, build duration, and artifact hashes.
- **QEMU Virtualization Testing:** Headless and interactive boot validation scripts with OVMF UEFI and BIOS support.

---

## 2. Directory Layout & Build Scripts

```
/build
├── config/
│   ├── version.json                  # Semantic versioning & distribution info
│   ├── packages-live.list            # Live desktop package manifest
│   ├── packages-installer.list       # Dedicated installer package manifest
│   ├── packages-development.list     # Developer workstation manifest
│   └── packages-minimal.list         # Minimal headless manifest
└── scripts/
    ├── version.py                    # Metadata & artifact naming helper
    ├── build-rootfs.py               # Deterministic RootFS staging engine
    ├── build-squashfs.py             # Reproducible Zstandard SquashFS compressor
    ├── build-iso.py                  # Master Hybrid UEFI/BIOS ISO builder
    ├── validate-iso.py               # Structural and bootloader validator
    ├── sign-artifacts.py             # Checksum & GPG signing tool
    └── reproducible-check.py         # Bit-for-bit dual build verification
```

---

## 3. Quick Start & Build Commands

### Bootstrap Host Dependencies (Clean Machine)
```bash
./scripts/bootstrap.sh
```

### Build Specific Profiles
```bash
# Build default Live Desktop ISO
./scripts/build-live.sh

# Build Dedicated Installer ISO
./scripts/build-installer.sh

# Build Developer Workstation ISO
./scripts/build-dev.sh

# Build Minimal Server ISO
./scripts/build-minimal.sh
```

### Master Build CLI (`./scripts/build.sh`)
```bash
# Build all 4 profiles with clean workspace
./scripts/build.sh --all-profiles --clean

# Build ARM64 minimal ISO
./scripts/build.sh --profile minimal --arch arm64

# Build with automatic QEMU test
./scripts/build.sh --profile live --test
```

### Validate & Test ISO in QEMU
```bash
# Run structural validation and headless smoke test
./scripts/test-iso.sh --headless --iso dist/aetheros-1.0.0-solstice-live-amd64.iso

# Launch interactive UEFI QEMU VM
./scripts/test-iso.sh --uefi --memory 4096
```

### Cryptographic Verification
```bash
# Verify checksums and GPG signatures
./scripts/sign.sh --verify dist/aetheros-1.0.0-solstice-live-amd64.iso
```

---

## 4. Continuous Integration Pipeline

All pull requests and tag releases trigger GitHub Actions workflows in `.github/workflows/build-iso.yml` and `ci/build-iso.yml`. The pipeline:
1. Enforces strict error checking (`set -euo pipefail`).
2. Validates package metadata and runs all unit/integration test suites.
3. Builds the ISO profiles across architectures.
4. Verifies bit-for-bit reproducibility.
5. Executes automated headless QEMU boot tests.
6. Publishes authenticated ISOs, `SHA256SUMS`, `SHA512SUMS`, GPG detached signatures, and `build-info.json` metadata.
