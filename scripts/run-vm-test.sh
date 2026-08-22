#!/usr/bin/env bash
# AetherOS Virtual Machine Test Runner (QEMU / KVM)
set -e

ISO_PATH="${1:-aetheros-1.0.0-solstice-amd64.iso}"
RAM="${2:-2048M}"
CORES="${3:-2}"

if [ ! -f "$ISO_PATH" ]; then
    echo "[-] Error: ISO image not found at $ISO_PATH" >&2
    echo "    Please run ./scripts/build-all.sh first." >&2
    exit 1
fi

ACCEL="-enable-kvm -cpu host"
if [ ! -e /dev/kvm ] || [ ! -r /dev/kvm ]; then
    echo "[!] /dev/kvm not available, using standard TCG CPU emulation..."
    ACCEL="-cpu max"
fi

echo "=== Launching AetherOS in QEMU Virtual Machine ==="
echo "ISO: $ISO_PATH"
echo "RAM: $RAM | Cores: $CORES"

qemu-system-x86_64 \
    $ACCEL \
    -m "$RAM" \
    -smp "$CORES" \
    -vga virtio \
    -display gtk,gl=on \
    -device virtio-net-pci,netdev=net0 \
    -netdev user,id=net0 \
    -device intel-hda -device hda-duplex \
    -cdrom "$ISO_PATH" \
    -boot d
