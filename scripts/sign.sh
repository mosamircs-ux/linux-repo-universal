#!/usr/bin/env bash
# Cryptographic Checksum and GPG Signing Script
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
exec python3 "$REPO_ROOT/build/scripts/sign-artifacts.py" "$@"
