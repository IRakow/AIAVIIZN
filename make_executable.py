#!/usr/bin/env python3

import subprocess
import os

# Make all shell scripts executable
scripts = [
    'setup_dependencies.sh',
    'quick_start.sh', 
    'monitor_progress.sh'
]

for script in scripts:
    if os.path.exists(script):
        subprocess.run(['chmod', '+x', script])
        print(f"Made {script} executable")

print("All scripts are now executable!")
