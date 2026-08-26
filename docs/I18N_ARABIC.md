# AetherOS Arabic & Bilingual Localization Specification

AetherOS delivers first-class, out-of-the-box support for the Arabic language (`ar`) with full right-to-left (RTL) layout mirroring and high-quality typography.

---

## 1. Typography & Font Stack
- **Interface Font:** *Cairo* and *Tajawal* for modern, legible Arabic display at all UI scales.
- **Traditional / Document Serif:** *Amiri* for high-fidelity classical Arabic typesetting.
- **Monospace Code Font:** *JetBrains Mono* / *Fira Code* with Arabic character coverage.

---

## 2. RTL Layout Mirroring
When Arabic locale is selected (`LANG=ar_EG.UTF-8`, `LANG=ar_SA.UTF-8`, etc.):
1. **The Dock:** Automatically mirrors to the right edge of the display.
2. **TopBar:** Pager and app trigger shift to the top-right; clock and quick settings move to the top-left.
3. **Application Windows:** Navigation sidebars mirror to the right; close/minimize window controls mirror according to user preference.

---

## 3. Switching Languages

Language can be switched instantly via **Settings > Language & Region** or via command line:
```bash
aether-settings --set-lang ar
```
