#!/usr/bin/env bash
# AetherOS Clean-Machine Bootstrap & Toolchain Installer
# Prepares the host environment with all necessary compilers, ISO authoring tools, and emulators.

set -euo pipefail

echo "========================================================"
echo "      AetherOS Host Bootstrap & Toolchain Setup         "
echo "========================================================"

# Detect Package Manager
if command -v apt-get &>/dev/null; then
    echo "[Bootstrap] Detected Debian/Ubuntu host. Installing prerequisites via apt..."
    export DEBIAN_FRONTEND=noninteractive
    sudo apt-get update -qq
    sudo apt-get install -y --no-install-recommends \
        python3 \
        python3-pip \
        python3-venv \
        squashfs-tools \
        xorriso \
        grub-pc-bin \
        grub-efi-amd64-bin \
        mtools \
        dosfstools \
        gnupg \
        zstd \
        qemu-system-x86 \
        ovmf \
        ca-certificates \
        curl \
        git
elif command -v dnf &>/dev/null; then
    echo "[Bootstrap] Detected Fedora/RHEL host. Installing prerequisites via dnf..."
    sudo dnf install -y \
        python3 \
        squashfs-tools \
        xorriso \
        grub2-tools-extra \
        mtools \
        dosfstools \
        gnupg2 \
        zstd \
        qemu-system-x86 \
        edk2-ovmf \
        curl \
        git
elif command -v pacman &>/dev/null; then
    echo "[Bootstrap] Detected Arch Linux host. Installing prerequisites via pacman..."
    sudo pacman -Sy --noconfirm \
        python \
        squashfs-tools \
        xorriso \
        grub \
        mtools \
        dosfstools \
        gnupg \
        zstd \
        qemu-system-x86 \
        edk2-ovmf \
        curl \
        git
else
    echo "[Bootstrap] Warning: Unknown package manager. Please ensure Python 3, xorriso, squashfs-tools, and GRUB are installed."
fi

echo ""
echo "[Bootstrap] Verifying installed toolchain:"
for tool in python3 xorriso mksquashfs gpg; do
    if command -v "$tool" &>/dev/null; then
        echo "  [+] $tool: $(command -v "$tool")"
    else
        echo "  [-] $tool: NOT FOUND (builds will use deterministic fallback mode)"
    fi
done

echo ""
echo "[Bootstrap] Environment preparation complete."
