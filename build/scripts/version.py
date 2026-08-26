#!/usr/bin/env python3
"""
AetherOS Version and Metadata Helper
Loads distribution version specifications and generates standardized build metadata.
"""

import os
import sys
import json
import subprocess
from typing import Dict, Any, Optional

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CONFIG_PATH = os.path.join(REPO_ROOT, "build", "config", "version.json")

def load_version_config() -> Dict[str, Any]:
    if not os.path.exists(CONFIG_PATH):
        return {
            "name": "AetherOS",
            "codename": "Solstice",
            "version": "1.0.0",
            "release_channel": "LTS",
            "source_date_epoch": 1700000000,
            "supported_architectures": ["x86_64", "arm64"],
            "profiles": ["live", "installer", "development", "minimal"],
            "default_profile": "live",
            "default_arch": "x86_64",
        }
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def get_git_commit() -> str:
    try:
        res = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=True
        )
        return res.stdout.strip()
    except Exception:
        return "unknown"

def get_git_branch() -> str:
    try:
        res = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=True
        )
        return res.stdout.strip()
    except Exception:
        return "main"

def get_source_date_epoch() -> int:
    env_epoch = os.environ.get("SOURCE_DATE_EPOCH")
    if env_epoch and env_epoch.isdigit():
        return int(env_epoch)
    try:
        res = subprocess.run(
            ["git", "log", "-1", "--format=%ct"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=True
        )
        val = res.stdout.strip()
        if val.isdigit():
            return int(val)
    except Exception:
        pass
    config = load_version_config()
    return int(config.get("source_date_epoch", 1700000000))

def get_iso_filename(profile: str = "live", arch: str = "x86_64") -> str:
    config = load_version_config()
    dist_name = config.get("name", "aetheros").lower()
    version = config.get("version", "1.0.0")
    codename = config.get("codename", "solstice").lower()
    return f"{dist_name}-{version}-{codename}-{profile}-{arch}.iso"

if __name__ == "__main__":
    cfg = load_version_config()
    print(json.dumps({
        **cfg,
        "git_commit": get_git_commit(),
        "git_branch": get_git_branch(),
        "source_date_epoch": get_source_date_epoch(),
        "sample_iso_name": get_iso_filename()
    }, indent=2))
