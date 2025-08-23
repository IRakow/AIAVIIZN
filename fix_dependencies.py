#!/usr/bin/env python3
"""
Quick dependency check and fix script
"""

import subprocess
import sys

def run_command(cmd):
    """Run a shell command and return success status"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def main():
    print("🔧 AIVIIZN Dependency Fixer")
    print("=" * 50)
    
    # Core dependencies that should be installed
    packages = [
        ("playwright", "1.40.0"),
        ("anthropic", "0.7.8"),
        ("supabase", "2.0.2"),
        ("beautifulsoup4", "4.12.2"),
        ("python-dotenv", "1.0.0"),
        ("wolframalpha", "5.0.0"),
        ("openpyxl", "3.1.2"),
    ]
    
    print("\n📦 Installing packages individually to avoid conflicts...")
    
    for package, version in packages:
        print(f"\nInstalling {package}=={version}...")
        success, stdout, stderr = run_command(f"pip3 install {package}=={version}")
        
        if success:
            print(f"  ✅ {package} installed")
        else:
            # Try without version constraint
            print(f"  ⚠️ Version conflict, trying latest version...")
            success, stdout, stderr = run_command(f"pip3 install --upgrade {package}")
            if success:
                print(f"  ✅ {package} installed (latest version)")
            else:
                print(f"  ❌ Failed to install {package}")
                print(f"     Error: {stderr[:200]}")
    
    # Install playwright browsers
    print("\n🌐 Installing Playwright browsers...")
    success, stdout, stderr = run_command("python3 -m playwright install chromium")
    if success:
        print("  ✅ Chromium browser installed")
    else:
        print("  ⚠️ Failed to install browser (may already be installed)")
    
    print("\n✨ Setup complete!")
    print("\nTo run the agent:")
    print("  python3 aiviizn_real_agent.py")
    
    # Check for .env file
    import os
    if not os.path.exists(".env"):
        print("\n⚠️ Don't forget to create your .env file with API keys!")
        print("  cp .env.example .env")
        print("  # Then edit .env with your actual keys")

if __name__ == "__main__":
    main()
