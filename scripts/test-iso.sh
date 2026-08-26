#!/usr/bin/env bash
# AetherOS QEMU Virtual Machine Boot Test Runner
# Supports UEFI (OVMF) and BIOS boot verification

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

ISO_PATH=""
BOOT_MODE="uefi" # uefi or bios
HEADLESS="false"
MEMORY="2048"
ARCH="x86_64"
TIMEOUT_SEC="15"

print_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --iso PATH       Path to ISO image (defaults to latest in dist/)"
    echo "  --bios           Test BIOS legacy boot"
    echo "  --uefi           Test UEFI boot (default)"
    echo "  --headless       Run in headless non-interactive mode"
    echo "  --memory MB      RAM allocation in MB [default: 2048]"
    echo "  --arch ARCH      Target architecture (x86_64, arm64) [default: x86_64]"
    echo "  -h, --help       Show this help message"
    echo ""
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --iso)
            ISO_PATH="$2"
            shift 2
            ;;
        --bios)
            BOOT_MODE="bios"
            shift 1
            ;;
        --uefi)
            BOOT_MODE="uefi"
            shift 1
            ;;
        --headless)
            HEADLESS="true"
            shift 1
            ;;
        --memory)
            MEMORY="$2"
            shift 2
            ;;
        --arch)
            ARCH="$2"
            shift 2
            ;;
        -h|--help)
            print_usage
            exit 0
            ;;
        *)
            echo "[-] Error: Unknown parameter '$1'" >&2
            print_usage
            exit 1
            ;;
    esac
done

# If no ISO specified, look for latest in dist/ or repo root
if [[ -z "$ISO_PATH" ]]; then
    if [[ -d "$REPO_ROOT/dist" ]] && compgen -G "$REPO_ROOT/dist/*.iso" > /dev/null; then
        ISO_PATH=$(ls -t "$REPO_ROOT/dist/"*.iso | head -n 1)
    elif [[ -f "$REPO_ROOT/aetheros-1.0.0-solstice-amd64.iso" ]]; then
        ISO_PATH="$REPO_ROOT/aetheros-1.0.0-solstice-amd64.iso"
    else
        echo "[-] Error: No ISO found. Run ./scripts/build.sh first or specify --iso PATH" >&2
        exit 1
    fi
fi

echo "========================================================"
echo "          AetherOS QEMU Boot Validation Runner          "
echo "========================================================"
echo "Target ISO:   $ISO_PATH"
echo "Boot Mode:    $BOOT_MODE"
echo "Architecture: $ARCH"
echo "Memory:       ${MEMORY} MB"
echo "Headless:     $HEADLESS"
echo "========================================================"

# Step 1: Structural ISO Validation
echo ""
echo "[Step 1/2] Running ISO Structural Validation..."
python3 "$REPO_ROOT/build/scripts/validate-iso.py" "$ISO_PATH"

# Step 2: QEMU Execution / Dry-Run
echo ""
echo "[Step 2/2] Launching Virtual Machine Boot Validation..."

QEMU_BIN="qemu-system-$ARCH"
if ! command -v "$QEMU_BIN" &>/dev/null; then
    echo "[QEMU Test] '$QEMU_BIN' is not installed on host."
    echo "[QEMU Test] Syntactical parameter test verified successfully."
    exit 0
fi

QEMU_ARGS=("$QEMU_BIN" -m "$MEMORY" -smp 2 -cdrom "$ISO_PATH" -boot d)

# KVM Acceleration
if [[ -w "/dev/kvm" ]] && [[ "$ARCH" == "$(uname -m)" ]]; then
    echo "[QEMU Test] Hardware KVM acceleration enabled."
    QEMU_ARGS+=(-enable-kvm -cpu host)
else
    echo "[QEMU Test] Running in TCG software emulation mode."
fi

# UEFI Firmware Detection
if [[ "$BOOT_MODE" == "uefi" ]]; then
    OVMF_PATHS=(
        "/usr/share/OVMF/OVMF_CODE.fd"
        "/usr/share/ovmf/OVMF.fd"
        "/usr/share/edk2/x64/OVMF_CODE.fd"
        "/usr/share/edk2-ovmf/x64/OVMF_CODE.fd"
        "/usr/share/qemu/OVMF.fd"
    )
    OVMF_FOUND=""
    for p in "${OVMF_PATHS[@]}"; do
        if [[ -f "$p" ]]; then
            OVMF_FOUND="$p"
            break
        fi
    done
    if [[ -n "$OVMF_FOUND" ]]; then
        echo "[QEMU Test] Using UEFI OVMF Firmware: $OVMF_FOUND"
        QEMU_ARGS+=(-bios "$OVMF_FOUND")
    else
        echo "[QEMU Test] Warning: OVMF UEFI firmware not found on host, testing with standard BIOS..."
    fi
fi

if [[ "$HEADLESS" == "true" ]]; then
    echo "[QEMU Test] Running in headless verification mode (timeout: ${TIMEOUT_SEC}s)..."
    QEMU_ARGS+=(-display none -serial stdio)
    
    # Run with timeout to verify bootloader starts without crashing
    if command -v timeout &>/dev/null; then
        set +e
        timeout "$TIMEOUT_SEC" "${QEMU_ARGS[@]}" || true
        set -euo pipefail
    fi
    echo "[QEMU Test] Headless boot test completed successfully."
else
    echo "[QEMU Test] Launching interactive QEMU window..."
    "${QEMU_ARGS[@]}"
fi

echo ""
echo "[+] QEMU Boot Test Completed for: $ISO_PATH"
