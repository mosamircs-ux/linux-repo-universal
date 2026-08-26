# AetherOS Security & Privacy Architecture Model

This document outlines the security specifications, threat models, privilege separation boundaries, sandboxing strategies, and zero-telemetry guarantees of AetherOS.

---

## 1. Zero-Telemetry & User Privacy Guarantee

AetherOS enforces an uncompromising zero-telemetry policy:

1. **No Outbound Analytics:** No background daemons, scheduled tasks, or services transmit usage telemetry, hardware identifiers, or personal data to remote servers.
2. **Local-Only Crash Reporting (`aether-crash-handler`):**
   - When an application encounters a segmentation fault or crash, the crash handler intercepts the signal.
   - All backtraces and memory dumps are parsed locally to sanitize sensitive information:
     - IP addresses are scrubbed and replaced with `[REDACTED_IP]`.
     - Email addresses are scrubbed and replaced with `[REDACTED_EMAIL]`.
     - User home directory paths (e.g., `/home/username/`) are scrubbed and replaced with `/home/[USER]/`.
   - Sanitized crash logs are stored exclusively on the local filesystem at `/var/log/aether/crashes/` and are never automatically transmitted over the network.
3. **Network MAC Address Randomization:**
   - Wi-Fi probe scanning uses randomized MAC addresses to prevent tracking in public locations.
   - NetworkManager generates a distinct, randomized MAC address per Wi-Fi connection profile.

---

## 2. Mandatory Access Control: AppArmor LSM

AetherOS runs AppArmor in enforcing mode by default with tailored profiles located in `/system/security/apparmor.d/`:

### 2.1 Update Tooling Profile (`usr.bin.aether-updater`)
- Confinements:
  - Grants read access to `/etc/aether/**` and `/etc/apt/**`.
  - Grants write access strictly to `/var/lib/aether/**` and `/var/log/aether/**`.
  - Mediates execution transitions to APT (`child_apt`), dpkg (`child_dpkg`), flatpak (`child_flatpak`), and Btrfs snapshot utilities (`child_btrfs`).
  - Restricts arbitrary process execution outside of package management paths.

### 2.2 Crash Handler Profile (`usr.bin.aether-crash-handler`)
- Confinements:
  - Grants read access to `/proc/*/cmdline` and `/proc/*/status` for stack inspection.
  - Grants write access strictly to `/var/log/aether/crashes/**`.
  - **Explicit Network Egress Block:** Employs `deny network raw` and `deny network packet` rules to guarantee zero network leakage at the kernel LSM boundary.

---

## 3. Privilege Separation via Polkit (`org.aetheros.*`)

AetherOS eliminates blanket `sudo` elevation for desktop GUI tools by implementing fine-grained Polkit policies in `/system/polkit/org.aetheros.policy`:

| Action ID | Description | Default Authorization |
|---|---|---|
| `org.aetheros.updater.check-and-apply` | Apply system packages & create snapshots | `auth_admin_keep` (authenticated user session) |
| `org.aetheros.settings.manage-hardware` | Modify display resolution, audio, network | `yes` (active console user allowed without root) |
| `org.aetheros.snapshots.rollback` | Revert system root to a previous snapshot | `auth_admin` (explicit administrator password) |

---

## 4. Application Sandboxing & Flatpak Portals

- **Desktop Application Isolation:** Non-core user applications installed via Flatpak execute in unprivileged bubblewrap containers.
- **XDG Desktop Portals:** Applications access host resources (file chooser, camera, microphone, screen sharing, printing) through user-prompted D-Bus portal interfaces (`xdg-desktop-portal-wlr` / `xdg-desktop-portal-gtk`), preventing unauthorized background access.
- **Rootless User Execution:** The entire desktop shell and all widgets run strictly under unprivileged user permissions (`UID 1000+`).

---

## 5. Memory Safety & Service Hardening

- **Memory-Safe Implementations:** Security-sensitive backend services are implemented in memory-safe languages (Rust and type-checked Python 3.12).
- **systemd Service Sandboxing:** Custom systemd unit files utilize security directives:
  - `ProtectSystem=strict`
  - `ProtectHome=read-only` (or `true` for system services)
  - `NoNewPrivileges=true`
  - `PrivateTmp=true`
  - `ProtectKernelTunables=true`
  - `ProtectControlGroups=true`

---

## 6. Secure Boot & Cryptographic Verification

- **UEFI Secure Boot:** Compatible with Microsoft 3rd-Party UEFI CA via signed GRUB2 and Linux kernel images.
- **Package Integrity:** All official APT repository packages and Flatpak runtimes are cryptographically signed using GPG and OSTree ed25519 signatures.
- **ISO Verification:** Every release ISO image includes a deterministic SHA256 checksum file signed with the official AetherOS Release Engineering key.
