# AetherOS Kernel Configuration & Hardware Subsystem

This directory manages kernel runtime parameters, boot command line defaults, sysctl performance tuning, and module auto-loading for AetherOS.

## Specifications
- **Kernel Base:** Linux 6.8+ LTS with Ubuntu/Debian hardware enablement (HWE) stack.
- **I/O Scheduler:** Multi-queue NVMe/SSD default (`none`/`mq-deadline`) with `BFQ` for rotational disks.
- **Memory Compression:** zRAM backed by `zstd` algorithm (configured via `systemd-zram-generator`).
- **Network Stack:** Google BBR congestion control (`tcp_congestion_control=bbr`) paired with `fq` fair queuing.
- **Security:** AppArmor LSM active by default with kernel pointer restrictions and restricted unprivileged BPF.
