#!/usr/bin/env python3
"""
Test and diagnose the AIVIIZN Real Agent setup
"""

import os
import sys
import subprocess
from pathlib import Path

def check_dependency(module_name, package_name=None):
    """Check if a Python module is installed"""
    if package_name is None:
        package_name = module_name
    
    try:
        __import__(module_name)
        return True, "✅ Installed"
    except ImportError:
        return False, f"❌ Not installed - run: pip3 install {package_name}"

def check_env_var(var_name, required=True):
    """Check if an environment variable is set"""
    from dotenv import load_dotenv
    load_dotenv()
    
    value = os.getenv(var_name)
    if value:
        # Hide sensitive data
        if "KEY" in var_name or "SECRET" in var_name:
            return True, f"✅ Set ({len(value)} characters)"
        else:
            return True, f"✅ Set: {value[:50]}..."
    else:
        if required:
            return False, "❌ Not set (required)"
        else:
            return False, "⚠️ Not set (optional)"

def main():
    print("🔍 AIVIIZN Real Agent Diagnostic")
    print("=" * 60)
    
    # Check Python version
    print("\n📊 Python Version:")
    print(f"   {sys.version}")
    
    # Check dependencies
    print("\n📦 Required Dependencies:")
    dependencies = [
        ("playwright", None),
        ("anthropic", None),
        ("supabase", None),
        ("bs4", "beautifulsoup4"),
        ("dotenv", "python-dotenv"),
        ("wolframalpha", None),
        ("openpyxl", None),
    ]
    
    all_installed = True
    for module, package in dependencies:
        installed, message = check_dependency(module, package)
        print(f"   {module:15} {message}")
        if not installed:
            all_installed = False
    
    if not all_installed:
        print("\n⚠️ Some dependencies missing. Run:")
        print("   python3 fix_dependencies.py")
        return
    
    # Check environment variables
    print("\n🔑 Environment Variables:")
    env_vars = [
        ("SUPABASE_URL", True),
        ("SUPABASE_KEY", True),
        ("SUPABASE_SERVICE_KEY", True),
        ("ANTHROPIC_API_KEY", True),
        ("WOLFRAM_APP_ID", False),  # Optional
    ]
    
    env_ok = True
    for var, required in env_vars:
        is_set, message = check_env_var(var, required)
        print(f"   {var:20} {message}")
        if required and not is_set:
            env_ok = False
    
    if not env_ok:
        print("\n⚠️ Required environment variables missing!")
        print("   Edit your .env file with actual API keys")
        return
    
    # Check Playwright browsers
    print("\n🌐 Playwright Browsers:")
    try:
        result = subprocess.run(
            ["python3", "-c", "from playwright.sync_api import sync_playwright; p = sync_playwright().start(); b = p.chromium.launch(headless=True); b.close(); p.stop()"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("   ✅ Chromium browser installed and working")
        else:
            print("   ❌ Chromium not installed. Run:")
            print("      python3 -m playwright install chromium")
    except Exception as e:
        print(f"   ❌ Error checking browsers: {e}")
    
    # Check project structure
    print("\n📁 Project Structure:")
    required_dirs = [
        "templates",
        "static",
        "data",
    ]
    
    for dir_name in required_dirs:
        dir_path = Path(dir_name)
        if dir_path.exists():
            print(f"   ✅ {dir_name}/ exists")
        else:
            print(f"   ⚠️ {dir_name}/ missing - will be created on first run")
    
    # Final status
    print("\n" + "=" * 60)
    if all_installed and env_ok:
        print("✅ System ready! You can run:")
        print("   python3 aiviizn_real_agent.py")
        print("\n💡 Tips:")
        print("   - Make sure you're logged into AppFolio before starting")
        print("   - The browser window will open - don't close it")
        print("   - Press Enter when you're ready to start extraction")
    else:
        print("⚠️ Please fix the issues above before running the agent")

if __name__ == "__main__":
    main()
