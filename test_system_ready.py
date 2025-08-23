#!/usr/bin/env python3
"""
Test script to verify AIVIIZN system is ready
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment
load_dotenv()

print("🔍 AIVIIZN System Check")
print("=" * 50)

# Check environment variables
env_vars = [
    'SUPABASE_URL',
    'SUPABASE_KEY', 
    'SUPABASE_SERVICE_KEY',
    'ANTHROPIC_API_KEY',
    'OPENAI_API_KEY'
]

print("\n✓ Environment Variables:")
all_good = True
for var in env_vars:
    value = os.getenv(var)
    if value:
        print(f"  ✅ {var}: {value[:20]}...")
    else:
        print(f"  ❌ {var}: Not found")
        all_good = False

# Check Python packages
print("\n✓ Python Packages:")
packages = [
    'playwright',
    'supabase',
    'anthropic',
    'bs4',
    'openai',
    'dotenv'
]

for package in packages:
    try:
        __import__(package)
        print(f"  ✅ {package}: Installed")
    except ImportError:
        print(f"  ❌ {package}: Not installed")
        all_good = False

# Check Supabase connection
print("\n✓ Supabase Connection:")
try:
    from supabase import create_client
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_SERVICE_KEY')
    
    if url and key:
        client = create_client(url, key)
        
        # Test connection by checking companies table
        result = client.table('companies').select('name').limit(1).execute()
        print(f"  ✅ Connected to Supabase")
        
        # Check for AIVIIZN company
        aiviizn = client.table('companies').select('id, name').eq('name', 'AIVIIZN').execute()
        if aiviizn.data:
            print(f"  ✅ AIVIIZN company exists: {aiviizn.data[0]['id']}")
        else:
            print(f"  ⚠️  AIVIIZN company not found - will be created on first run")
    else:
        print(f"  ❌ Missing Supabase credentials")
        all_good = False
        
except Exception as e:
    print(f"  ❌ Supabase error: {e}")
    all_good = False

# Check directories
print("\n✓ Project Directories:")
dirs = [
    Path("/Users/ianrakow/Desktop/AIVIIZN"),
    Path("/Users/ianrakow/Desktop/AIVIIZN/templates"),
    Path("/Users/ianrakow/Desktop/AIVIIZN/static"),
    Path("/Users/ianrakow/Desktop/AIVIIZN/data"),
    Path("/Users/ianrakow/Desktop/AIVIIZN/screenshots")
]

for dir_path in dirs:
    if dir_path.exists():
        print(f"  ✅ {dir_path.name}: Exists")
    else:
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"  ✅ {dir_path.name}: Created")

# Summary
print("\n" + "=" * 50)
if all_good:
    print("✅ SYSTEM READY! You can run the agent now.")
    print("\nRun with:")
    print("  bash /Users/ianrakow/Desktop/AIVIIZN/run_agent_complete.sh")
    print("\nOr directly:")
    print("  python3 /Users/ianrakow/Desktop/AIVIIZN/aiviizn_real_agent_complete.py")
else:
    print("⚠️  Some issues found. Please fix them before running.")
    print("\nTo install missing packages:")
    print("  pip3 install playwright supabase anthropic beautifulsoup4 python-dotenv openai")
    print("  python3 -m playwright install chromium")

print("\n" + "=" * 50)
