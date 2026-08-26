#!/usr/bin/env python3
import os
import sys
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(REPO_ROOT, "build", "scripts"))
import sign_artifacts

if __name__ == "__main__":
    sign_artifacts.main()
