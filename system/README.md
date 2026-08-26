# AetherOS System Layer

This directory contains operating system level configurations, systemd services, audio routing, network management, Polkit privilege separation rules, and AppArmor security policies.

## Subsystems
- **Audio:** Native PipeWire with PulseAudio and JACK compatibility bridges, configured for low-latency desktop use.
- **Networking:** NetworkManager configured with automatic Wi-Fi MAC address randomization for scanning and roaming.
- **Privilege Separation:** Fine-grained Polkit policies under `org.aetheros.*` avoiding blank root/sudo delegation.
- **Security:** AppArmor profiles enforcing memory limits and zero-telemetry egress rules.
- **Memory Optimization:** Automatic dynamic zRAM swap device with zstd compression enabled via `systemd-zram-generator`.
