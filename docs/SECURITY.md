# AetherOS Security & Privacy Whitepaper

**Security Score:** Hardened Production Grade  
**Telemetry Policy:** Absolute Zero (100% Privacy by Default)  

---

## 1. Zero-Telemetry Guarantee
AetherOS does not collect, transmit, or monetize any user data:
- No background telemetry daemons.
- No unique hardware identifiers transmitted over the network.
- Wi-Fi MAC address randomization enabled by default during network probing and per-SSID connection.
- Local-only crash handler (`aether-crash-handler`): backtraces are sanitized to strip IP addresses, email addresses, and home directory usernames before writing to `/var/log/aether/crashes`. All outbound network access is explicitly blocked by AppArmor (`deny network raw`).

---

## 2. AppArmor LSM Confinement
AetherOS enforces AppArmor profiles out-of-the-box:
- All update and packaging utilities run under restricted subprofiles.
- Background daemons cannot modify arbitrary system binaries or access user home directories without explicit capabilities.
- Unprivileged user namespaces are restricted to prevent sandbox escape vectors.

---

## 3. Polkit Granular Privilege Separation
Instead of broad `sudo` access for GUI applications, AetherOS uses Polkit policies under `org.aetheros.*`:
- `org.aetheros.updater.check-and-apply`: Requires authentication to commit upgrades.
- `org.aetheros.snapshots.rollback`: Strict administrator authentication required for snapshot reversion.
- Hardware configuration is gated to active console sessions without exposing root shell access.
