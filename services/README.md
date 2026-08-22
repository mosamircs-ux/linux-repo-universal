# AetherOS System Daemons & Services

This directory contains system-level daemons running in background user/system units.

## Services
- **`aether-updater-daemon`**: Background update check and notification coordinator.
- **`aether-rollback-agent`**: Boot-time health monitor ensuring safe automatic rollback to previous Btrfs snapshots if unrecoverable boot failures occur.
- **`aether-crash-handler`**: Privacy-respecting crash reporter that strips sensitive data (IPs, emails, usernames) and saves crash backtraces locally without telemetry.
