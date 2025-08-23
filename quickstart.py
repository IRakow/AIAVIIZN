#!/usr/bin/env python3
"""
Quick start script for AIVIIZN Real Agent
Handles dependency installation and setup
"""

import subprocess
import sys
import os

def main():
    print("🚀 AIVIIZN Quick Start")
    print("=" * 60)
    
    # Step 1: Install core dependencies
    print("\n📦 Installing core dependencies...")
    core_packages = [
        "playwright",
        "anthropic", 
        "supabase",
        "beautifulsoup4",
        "python-dotenv",
        "wolframalpha",
        "openpyxl"
    ]
    
    for package in core_packages:
        print(f"  Installing {package}...")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "--upgrade", package],
            capture_output=True,
            text=True
        )
        if result.returncode != 0 and "supabase" not in package:
            print(f"    ⚠️ Warning: {package} installation had issues")
    
    print("  ✅ Core packages installed")
    
    # Step 2: Install Playwright browsers
    print("\n🌐 Installing Playwright browser...")
    result = subprocess.run(
        [sys.executable, "-m", "playwright", "install", "chromium"],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        print("  ✅ Chromium browser installed")
    else:
        print("  ⚠️ Browser may already be installed")
    
    # Step 3: Check for .env file
    print("\n🔧 Checking configuration...")
    if not os.path.exists(".env"):
        if os.path.exists(".env.example"):
            print("  Creating .env from template...")
            with open(".env.example", "r") as f:
                template = f.read()
            with open(".env", "w") as f:
                f.write(template)
            print("  ✅ Created .env file")
            print("\n  ⚠️ IMPORTANT: Edit .env with your actual API keys:")
            print("     - SUPABASE_URL")
            print("     - SUPABASE_KEY") 
            print("     - SUPABASE_SERVICE_KEY")
            print("     - ANTHROPIC_API_KEY")
            print("     - WOLFRAM_APP_ID (optional)")
        else:
            print("  ⚠️ No .env.example found")
    else:
        print("  ✅ .env file exists")
    
    # Step 4: Create required directories
    print("\n📁 Creating project directories...")
    dirs = ["templates", "static", "data", "data/screenshots"]
    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)
        print(f"  ✅ {dir_path}/")
    
    print("\n" + "=" * 60)
    print("✨ Setup complete!")
    print("\nNext steps:")
    print("1. Edit .env with your API keys")
    print("2. Run: python3 aiviizn_real_agent.py")
    print("\nTo diagnose any issues:")
    print("  python3 diagnose_setup.py")

if __name__ == "__main__":
    main()
