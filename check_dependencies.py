#!/usr/bin/env python3
"""
Quick check to see if everything is installed
"""

import sys

print("\n🔍 Checking dependencies...")
print("-" * 40)

errors = []

# Check Playwright
try:
    from playwright.sync_api import sync_playwright
    print("✅ Playwright installed")
except ImportError:
    print("❌ Playwright NOT installed")
    errors.append("pip3 install playwright && playwright install chromium")

# Check Supabase
try:
    from supabase import create_client
    print("✅ Supabase installed")
except ImportError:
    print("❌ Supabase NOT installed")
    errors.append("pip3 install supabase")

# Check Anthropic
try:
    import anthropic
    print("✅ Anthropic installed")
except ImportError:
    print("❌ Anthropic NOT installed")
    errors.append("pip3 install anthropic")

# Check dotenv
try:
    from dotenv import load_dotenv
    print("✅ Python-dotenv installed")
except ImportError:
    print("❌ Python-dotenv NOT installed")
    errors.append("pip3 install python-dotenv")

# Check .env file
import os
from pathlib import Path

env_file = Path("/Users/ianrakow/Desktop/AIVIIZN/.env")
if env_file.exists():
    print("✅ .env file found")
    
    # Load and check keys
    from dotenv import load_dotenv
    load_dotenv()
    
    if os.getenv('SUPABASE_URL'):
        print("  ✓ SUPABASE_URL set")
    else:
        print("  ✗ SUPABASE_URL missing")
        
    if os.getenv('SUPABASE_SERVICE_KEY'):
        print("  ✓ SUPABASE_SERVICE_KEY set")
    else:
        print("  ✗ SUPABASE_SERVICE_KEY missing")
        
    if os.getenv('ANTHROPIC_API_KEY'):
        print("  ✓ ANTHROPIC_API_KEY set")
    else:
        print("  ✗ ANTHROPIC_API_KEY missing")
else:
    print("❌ .env file NOT found")
    errors.append("Create .env file with API keys")

print("-" * 40)

if errors:
    print("\n⚠️  TO FIX ERRORS, RUN:")
    for error in errors:
        print(f"   {error}")
    print("\nOr just run: ./setup.sh")
    sys.exit(1)
else:
    print("\n✅ ALL DEPENDENCIES INSTALLED!")
    print("\nReady to run:")
    print("   python3 process_next_page.py")
    sys.exit(0)
