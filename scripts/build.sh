#!/usr/bin/env bash
# AetherOS Master Unified Build Entrypoint
# Strict error handling: never silently ignores failures

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUILD_SCRIPT="$REPO_ROOT/build/scripts/build-iso.py"

PROFILE="live"
ARCH="x86_64"
OUTPUT=""
SIGN="true"
VALIDATE="true"
TEST_VM="false"
CLEAN="false"
ALL_PROFILES="false"

print_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --profile PROFILE   Target ISO profile (live, installer, development, minimal) [default: live]"
    echo "  --arch ARCH         Target architecture (x86_64, arm64) [default: x86_64]"
    echo "  --all-profiles      Build all 4 profiles (live, installer, development, minimal)"
    echo "  --output PATH       Specify custom output ISO path"
    echo "  --no-sign           Skip GPG detached signing and checksums"
    echo "  --no-validate       Skip automated ISO validation"
    echo "  --test              Launch QEMU test after successful build"
    echo "  --clean             Clean staging directory after build"
    echo "  -h, --help          Show this help message"
    echo ""
}

# Parse command-line arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --profile)
            PROFILE="$2"
            shift 2
            ;;
        --arch)
            ARCH="$2"
            shift 2
            ;;
        --all-profiles)
            ALL_PROFILES="true"
            shift 1
            ;;
        --output)
            OUTPUT="$2"
            shift 2
            ;;
        --no-sign)
            SIGN="false"
            shift 1
            ;;
        --no-validate)
            VALIDATE="false"
            shift 1
            ;;
        --test)
            TEST_VM="true"
            shift 1
            ;;
        --clean)
            CLEAN="true"
            shift 1
            ;;
        -h|--help)
            print_usage
            exit 0
            ;;
        *)
            echo "[-] Error: Unknown argument '$1'" >&2
            print_usage
            exit 1
            ;;
    esac
done

echo "========================================================"
echo "          AetherOS Solstice LTS Build Pipeline          "
echo "========================================================"

# Step 1: Package Definitions Validation
echo ""
echo "[Step 1] Validating Debian packaging specifications..."
python3 "$REPO_ROOT/packages/build-packages.py"

# Step 2: Build ISO(s)
build_single_profile() {
    local prof="$1"
    local ar="$2"
    echo ""
    echo "[Step 2] Building ISO profile: $prof ($ar)..."
    
    local cmd=(python3 "$BUILD_SCRIPT" --profile "$prof" --arch "$ar")
    if [[ -n "$OUTPUT" ]]; then
        cmd+=(--output "$OUTPUT")
    fi
    if [[ "$SIGN" == "false" ]]; then
        cmd+=(--no-sign)
    fi
    if [[ "$VALIDATE" == "false" ]]; then
        cmd+=(--no-validate)
    fi
    if [[ "$CLEAN" == "true" ]]; then
        cmd+=(--clean)
    fi

    "${cmd[@]}"
}

if [[ "$ALL_PROFILES" == "true" ]]; then
    for p in live installer development minimal; do
        build_single_profile "$p" "$ARCH"
    done
else
    build_single_profile "$PROFILE" "$ARCH"
fi

# Step 3: Run QEMU Test if requested
if [[ "$TEST_VM" == "true" ]]; then
    echo ""
    echo "[Step 3] Running QEMU test on generated ISO..."
    "$REPO_ROOT/scripts/test-iso.sh" --headless
fi

echo ""
echo "========================================================"
echo "  All requested AetherOS builds completed successfully! "
echo "========================================================"
