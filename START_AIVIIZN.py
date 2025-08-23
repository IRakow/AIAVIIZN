#!/usr/bin/env python3
"""
AIVIIZN Quick Start Script
Automatically sets up and runs the agent
"""

import os
import sys
import subprocess
from pathlib import Path

print("""
╔══════════════════════════════════════════════════════╗
║         AIVIIZN REAL AGENT - QUICK START             ║
║       Beautiful Page Replication System              ║
╚══════════════════════════════════════════════════════╝
""")

# Check Python version
if sys.version_info < (3, 8):
    print("❌ Python 3.8+ required!")
    sys.exit(1)

print("✅ Python version OK")

# Install dependencies
print("\n📦 Installing dependencies...")
packages = [
    'playwright',
    'supabase',
    'anthropic', 
    'beautifulsoup4',
    'python-dotenv',
    'openai',
    'openpyxl'
]

for package in packages:
    subprocess.run([sys.executable, '-m', 'pip', 'install', '-q', package])
print("✅ All packages installed")

# Install Playwright browsers
print("\n🌐 Setting up browser...")
subprocess.run([sys.executable, '-m', 'playwright', 'install', 'chromium'])
print("✅ Browser ready")

# Run the agent
print("\n🚀 Starting AIVIIZN Agent...")
print("=" * 60)

# Import and run
os.chdir('/Users/ianrakow/Desktop/AIVIIZN')
subprocess.run([sys.executable, 'aiviizn_real_agent_complete.py'])
