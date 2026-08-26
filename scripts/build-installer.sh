#!/usr/bin/env bash
# Build AetherOS Dedicated Installer ISO
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$SCRIPT_DIR/build.sh" --profile installer "$@"
