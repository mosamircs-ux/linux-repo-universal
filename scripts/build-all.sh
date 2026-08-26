#!/usr/bin/env bash
# AetherOS Master Release Orchestration Script
# Strict error handling: never silently ignores failures

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "========================================================"
echo "          AetherOS Solstice LTS Release Pipeline        "
echo "========================================================"

# Step 1: Run Full Test Suite
echo ""
echo "[Step 1/5] Running automated test suites..."
python3 -m unittest discover -s "$REPO_ROOT/tests" -v

# Step 2: Validate Debian Package Metadata
echo ""
echo "[Step 2/5] Validating Debian packaging specifications..."
python3 "$REPO_ROOT/packages/build-packages.py"

# Step 3: Build Release ISOs
echo ""
echo "[Step 3/5] Building reproducible ISO images (Live, Installer, Minimal)..."
"$REPO_ROOT/scripts/build-live.sh" --clean
"$REPO_ROOT/scripts/build-installer.sh" --clean
"$REPO_ROOT/scripts/build-minimal.sh" --clean

# Step 4: Verify Bit-for-Bit Reproducibility
echo ""
echo "[Step 4/5] Verifying bit-for-bit build reproducibility..."
python3 "$REPO_ROOT/build/scripts/reproducible-check.py" --profile minimal

# Step 5: Validate Artifact Checksums & Signatures
echo ""
echo "[Step 5/5] Validating output distribution artifacts..."
python3 "$REPO_ROOT/build/scripts/sign-artifacts.py" --verify "$REPO_ROOT/dist/"*.iso

echo ""
echo "========================================================"
echo "  AetherOS Master Build & Release Pipeline COMPLETE!    "
echo "  Artifacts available in: $REPO_ROOT/dist/              "
echo "========================================================"
