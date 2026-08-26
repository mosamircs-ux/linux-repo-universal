# AetherOS Developer Workstation Layer (`distro-dev`)

AetherOS provides an on-demand, modular developer workstation layer. To maintain maximum performance, minimal memory footprint, and fast boot times, **the developer stack is NOT pre-installed by default on standard desktop or minimal images**. Developers can install, manage, diagnose, and update toolchains as needed via the **`distro-dev`** CLI.

---

## 1. Supported Developer Toolchains & Bundles

| Category | Tools Included | Bundle Alias |
| :--- | :--- | :--- |
| **Essentials & CLI** | `git`, `ssh` (OpenSSH), `openssl`, `curl`, `wget`, `jq`, `ripgrep` (rg), `fd` (fdfind), `tmux` | `essentials` |
| **C / C++ & Native** | `gcc`, `g++`, `clang`, `llvm`, `make`, `cmake`, `ninja` | `c-cpp` |
| **Python** | `python3`, `python3-pip`, `python3-venv`, `python3-dev` | `python` |
| **Web / JavaScript** | `nodejs`, `npm`, `pnpm` | `web` |
| **Rust** | `rustc`, `cargo` | `rust` |
| **Go** | `golang-go` | `go` |
| **Java** | `default-jdk` (OpenJDK) | `jvm` |
| **PHP** | `php-cli`, `php-common`, `composer` | `php` |
| **Containers** | `podman`, `docker` (docker.io) | `containers` |
| **Cloud Native & K8s** | `kubectl` (Kubernetes CLI), `helm` (Helm Package Manager) | `cloud` |
| **Complete Workstation** | All 26 developer toolchains and compilers | `all` |

---

## 2. CLI Usage & Commands

### A. Health & Toolchain Diagnostics (`doctor`)
Inspects active compilers, language runtimes, versions, binary paths, and environment variables:
```bash
distro-dev doctor
# Or output machine-readable JSON:
distro-dev doctor --json
```

### B. Installing Toolchains & Stacks (`install`)
Install specific tools or entire workflows:
```bash
# Install individual tools
distro-dev install rust go podman

# Install workflow bundles
distro-dev install c-cpp web cloud

# Install full developer workstation suite
distro-dev install all
```

### C. Removing Toolchains (`remove`)
Cleanly remove installed packages without disturbing system core dependencies:
```bash
distro-dev remove php jvm
```

### D. Updating Toolchains (`update`)
Updates all installed developer tools to the latest upstream stable releases:
```bash
distro-dev update
```

### E. Catalog Inspection (`list`)
Lists available stacks and tools:
```bash
distro-dev list
```
