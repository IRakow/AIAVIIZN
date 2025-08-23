#!/usr/bin/env python3
"""
Runner for the ALL_IN_ONE_FIX from the main directory
"""

import subprocess
import sys
from pathlib import Path

# Run the fix from the fixes directory
fixes_dir = Path(__file__).parent / "fixes"
fix_script = fixes_dir / "ALL_IN_ONE_FIX.py"

if fix_script.exists():
    print("Running complete fix...")
    subprocess.run([sys.executable, str(fix_script)])
else:
    print("Error: Fix script not found!")
    print("Please run from the fixes directory:")
    print("  cd fixes")
    print("  python3 ALL_IN_ONE_FIX.py")
