#!/usr/bin/env bash
# Build AetherOS Minimal Server ISO
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$SCRIPT_DIR/build.sh" --profile minimal "$@"
