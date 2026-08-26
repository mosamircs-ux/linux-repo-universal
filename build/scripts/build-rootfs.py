#!/usr/bin/env python3
import os
import sys
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(REPO_ROOT, "build", "scripts"))
import build_rootfs

if __name__ == "__main__":
    build_rootfs.main()
