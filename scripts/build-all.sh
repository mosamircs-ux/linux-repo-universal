#!/usr/bin/env bash
# AetherOS Master Build & Release Orchestration Script
set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUTPUT_ISO="${1:-$REPO_ROOT/aetheros-1.0.0-solstice-amd64.iso}"

echo "========================================================"
echo "          AetherOS Solstice LTS Build Pipeline          "
echo "========================================================"

# Step 1: Run Full Test Suite
echo ""
echo "[Step 1/4] Running automated test suites..."
python3 -m unittest discover -s "$REPO_ROOT/tests" -v

# Step 2: Validate Package Definitions
echo ""
echo "[Step 2/4] Validating Debian packaging specifications..."
python3 "$REPO_ROOT/packages/build-packages.py"

# Step 3: Build Release ISO Image
echo ""
echo "[Step 3/4] Building reproducible Live ISO image..."
python3 "$REPO_ROOT/build/scripts/build-iso.py" --output "$OUTPUT_ISO"

# Step 4: Verify SHA256 Checksums
echo ""
echo "[Step 4/4] Verifying build integrity..."
python3 "$REPO_ROOT/build/scripts/reproducible-check.py" "$OUTPUT_ISO"

echo ""
echo "========================================================"
echo "  AetherOS Build Complete: $OUTPUT_ISO"
echo "========================================================"
