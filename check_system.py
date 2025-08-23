#!/usr/bin/env python3
"""
CHECK PYTHON VERSION AND DEPENDENCIES
Quick check to ensure we have Python 3 and required packages
"""

import sys
import subprocess

def check_python_version():
    """Check Python version"""
    print("🐍 PYTHON VERSION CHECK")
    print("=" * 40)
    
    version = sys.version_info
    print(f"Python Version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3:
        print("❌ ERROR: Python 3 is required!")
        print("📥 INSTALL PYTHON 3:")
        print("   macOS: brew install python3")
        print("   Ubuntu: sudo apt-get install python3 python3-pip")
        print("   Windows: Download from python.org")
        return False
    elif version.minor < 7:
        print("⚠️ WARNING: Python 3.7+ recommended")
        print("   You have Python 3.{}, some features may not work".format(version.minor))
    else:
        print("✅ Python version is compatible")
    
    return True

def check_packages():
    """Check required packages"""
    print("\n📦 CHECKING REQUIRED PACKAGES")
    print("=" * 40)
    
    required_packages = [
        'anthropic',
        'asyncio',  # Built-in since Python 3.4
        'json',     # Built-in
        're',       # Built-in
        'pathlib',  # Built-in since Python 3.4
        'logging',  # Built-in
        'dataclasses'  # Built-in since Python 3.7
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package in ['asyncio', 'json', 're', 'pathlib', 'logging', 'dataclasses']:
                # These are built-in, just try to import them
                __import__(package)
                print(f"✅ {package} (built-in)")
            else:
                __import__(package)
                print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - MISSING")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n📥 TO INSTALL MISSING PACKAGES:")
        print(f"pip3 install {' '.join(missing_packages)}")
        return False
    
    print("✅ All required packages available")
    return True

def main():
    """Main check function"""
    print("🔧 AIVIIZN BUILDER - DEPENDENCY CHECK")
    print("=" * 50)
    
    python_ok = check_python_version()
    packages_ok = check_packages()
    
    print("\n" + "=" * 50)
    
    if python_ok and packages_ok:
        print("🎉 SYSTEM READY!")
        print("✅ Python 3 detected")
        print("✅ All packages available")
        print("\n🚀 You can now run:")
        print("   python3 enhanced_aiviizn_builder_with_db.py")
    else:
        print("❌ SETUP REQUIRED")
        if not python_ok:
            print("🔧 Install Python 3 first")
        if not packages_ok:
            print("🔧 Install missing packages with pip3")

if __name__ == "__main__":
    main()
