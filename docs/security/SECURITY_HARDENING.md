# AetherOS System Security & Hardening Architecture

## 1. Executive Summary & Threat Model
AetherOS is designed with a **Defense-in-Depth** security philosophy. The operating system assumes that any individual layer (kernel, userland application, network interface) may be targeted by adversaries. Hardening is applied at the kernel, access control, systemd sandboxing, network firewall, and application isolation layers without introducing hidden telemetry, proprietary blobs, or remote backdoors.

---

## 2. Layer 1: Kernel & Memory Mitigations ([`system/sysctl/99-aether-security.conf`](file:///mnt/c/Users/mohamedsamir/Documents/linux-repo-universal/system/sysctl/99-aether-security.conf))

| Parameter | Value | Rationale & Threat Mitigated |
| :--- | :--- | :--- |
| `kernel.randomize_va_space` | `2` | Full Address Space Layout Randomization (ASLR) of stack, VDSO, heap, and mmap bases against Return-Oriented Programming (ROP) exploits. |
| `kernel.yama.ptrace_scope` | `1` | Yama LSM restricts `ptrace` system calls so that unprivileged processes can only trace direct child processes, stopping memory scraping of browsers/passwords. |
| `kernel.kptr_restrict` | `2` | Hides kernel symbols and pointers from `/proc/kallsyms` for unprivileged users, preventing kernel address leaks. |
| `kernel.dmesg_restrict` | `1` | Restricts `dmesg` buffer reading to root only, preventing hardware memory map leakage. |
| `kernel.unprivileged_bpf_disabled` | `1` | Prevents unprivileged users from loading eBPF programs, mitigating speculative execution and side-channel attacks (Spectre/Meltdown). |
| `net.core.bpf_jit_harden` | `2` | Enables constant blinding across all eBPF JIT-compiled binaries. |
| `fs.protected_hardlinks` / `symlinks` | `1` | Mitigates time-of-check to time-of-use (TOCTOU) symlink attacks in `/tmp` and sticky directories. |
| `fs.protected_fifos` / `regular` | `2` | Restricts FIFO and regular file creation in world-writable sticky directories. |
| `fs.suid_dumpable` | `0` | Disables core dumps for setuid executables to prevent memory extraction of credential processes. |
| `net.ipv4.tcp_syncookies` | `1` | Protects TCP stack from SYN flood Denial-of-Service attacks. |
| `net.ipv4.conf.all.rp_filter` | `1` | Strict Reverse Path Filtering mitigates IP address spoofing. |
| `net.ipv4.conf.all.accept_redirects` | `0` | Disables ICMP route redirects, preventing malicious routing table modifications. |

---

## 3. Layer 2: Mandatory Access Control & Least Privilege (AppArmor & Polkit)

- **AppArmor MAC Profiles** ([`system/security/apparmor.d/`](file:///mnt/c/Users/mohamedsamir/Documents/linux-repo-universal/system/security/apparmor.d/)):
  - Custom profiles for `aether-settings`, `aether-files`, `aether-software`, `aether-updater`, and crash handlers.
  - Strict denials for `/etc/shadow`, `/etc/sudoers`, `/dev/mem`, `/dev/kmem`, and unconfined raw device access.
- **Polkit Authorization Rules** ([`system/polkit/10-aether-security.rules`](file:///mnt/c/Users/mohamedsamir/Documents/linux-repo-universal/system/polkit/10-aether-security.rules)):
  - Explicit administrator authentication (`AUTH_ADMIN_KEEP`) required for system-wide configuration, package installation, and firewall changes.
  - Active seat console users allowed routine desktop tasks (network switching, removable USB mounting, session poweroff) without excessive root escalation.

---

## 4. Layer 3: Systemd Sandboxing & Seccomp
AetherOS systemd units are hardened with strict containerized directives:
- `ProtectSystem=strict`: Mounts `/usr`, `/boot`, `/etc` read-only for daemon processes.
- `ProtectHome=true`: Prevents system services from accessing user `/home` directories.
- `NoNewPrivileges=true`: Disables SUID execution within the service process tree.
- `PrivateTmp=true`: Allocates isolated `/tmp` namespaces.
- `ProtectKernelTunables=true` & `ProtectKernelModules=true`: Locks `/proc/sys` and prevents module loading.
- `SystemCallFilter=@system-service @network-io`: Enforces Linux Seccomp syscall filtering.

---

## 5. Layer 4: Network & SSH Hardening

- **Default-Deny Firewall** ([`system/ufw/ufw.conf`](file:///mnt/c/Users/mohamedsamir/Documents/linux-repo-universal/system/ufw/ufw.conf)):
  - Default Incoming policy: `DROP` / `DENY`.
  - Default Outgoing policy: `ACCEPT`.
- **Hardened SSH Server** ([`system/ssh/99-aether-hardened.conf`](file:///mnt/c/Users/mohamedsamir/Documents/linux-repo-universal/system/ssh/99-aether-hardened.conf)):
  - `PermitRootLogin no` (root login strictly prohibited over SSH).
  - `MaxAuthTries 3` (brute-force rate limiting).
  - `X11Forwarding no` & `AllowTcpForwarding no`.
  - High-grade post-quantum & Curve25519 cryptography (`ssh-ed25519`, `chacha20-poly1305`, `curve25519-sha256`).

---

## 6. Layer 5: Unattended Security Updates & Safe Recovery
- **Automatic Security Patches** ([`system/apt/50unattended-upgrades`](file:///mnt/c/Users/mohamedsamir/Documents/linux-repo-universal/system/apt/50unattended-upgrades)): Automatically pulls and verifies cryptographic signatures for upstream security updates.
- **Btrfs Pre-Update Safety Snapshots**: All package transactions automatically snapshot `/.snapshots` before writing changes, guaranteeing instant one-click rollback if any update is interrupted.

---

## 7. Layer 6: Security Audit Engine (`distro security-audit`)
The diagnostic command `distro security-audit` evaluates 15 key vectors:
1. Dangerous File & Credential Permissions
2. Exposed / Unencrypted Network Services
3. System Security & Kernel Sysctls
4. Listening Network Ports
5. Systemd Services Sandboxing
6. Startup Entries & Cron Persistence
7. System Binary Integrity
8. Repository GPG Signatures
9. Security Package Updates
10. AppArmor LSM Enforcement
11. Firewall (UFW / nftables) Status
12. Hardened SSH Server Configuration
13. Authentication & Password Hashing
14. SUID / SGID Binaries Audit
15. World-Writable Files in System Paths
