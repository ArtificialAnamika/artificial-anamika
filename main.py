#!/usr/bin/env python3
"""Artificial Anamika — Main Executable Entry Point."""

import sys
import os

# Ensure package path is resolved
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from anamika.cli import main

if __name__ == "__main__":
    main()
