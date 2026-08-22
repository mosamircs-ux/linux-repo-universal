#!/usr/bin/env bash
# AetherOS Development Environment Setup Script
set -e

echo "=== Setting up AetherOS Development Environment ==="

command_check() {
    if command -v "$1" >/dev/null 2>&1; then
        echo "[+] Found: $1"
    else
        echo "[-] Missing: $1 (Install via your package manager: apt-get install $2)"
    fi
}

echo "Checking required host utilities..."
command_check python3 "python3"
command_check mksquashfs "squashfs-tools"
command_check xorriso "xorriso"
command_check grub-mkrescue "grub-common grub-pc-bin grub-efi-amd64-bin"
command_check qemu-system-x86_64 "qemu-system-x86"
command_check git "git"

echo "=== Environment Check Completed ==="
