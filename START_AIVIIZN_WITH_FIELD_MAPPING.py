#!/usr/bin/env python3
"""
AIVIIZN Quick Start - WITH FIELD MAPPING & DUPLICATE PREVENTION
"""

import os
import sys
import subprocess
from pathlib import Path

print("""
╔══════════════════════════════════════════════════════════════╗
║     AIVIIZN REAL AGENT - FIELD MAPPING & DEDUPLICATION       ║
║         Intelligent Field Detection & Zero Duplicates         ║
╚══════════════════════════════════════════════════════════════╝
""")

print("✨ NEW FEATURES:")
print("  ✅ Intelligent Field Identification")
print("  ✅ Duplicate Page Prevention")
print("  ✅ Content Checksum Validation")
print("  ✅ Field Semantic Type Detection")
print("  ✅ Pattern-Based Field Mapping")
print("")

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

print("\n" + "="*60)
print("⚠️  IMPORTANT: Database Setup Required")
print("="*60)
print("\n📋 Please run the following SQL in your Supabase SQL editor:")
print("   File: database_field_mapping_schema.sql")
print("\nThis will create:")
print("  • field_mappings table - For storing identified fields")
print("  • Duplicate prevention columns in pages table")
print("  • Pattern matching tables for field detection")
print("\nOnce done, press ENTER to continue...")
input(">>> ")

# Run the enhanced agent
print("\n🚀 Starting AIVIIZN Agent with Field Mapping...")
print("=" * 60)

# Import and run
os.chdir('/Users/ianrakow/Desktop/AIVIIZN')
subprocess.run([sys.executable, 'aiviizn_real_agent_complete_with_field_mapping.py'])
