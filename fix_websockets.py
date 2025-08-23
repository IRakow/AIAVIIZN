#!/usr/bin/env python3
"""
Fix websockets compatibility issue
"""

import subprocess
import sys

def main():
    print("🔧 Fixing websockets compatibility issue...")
    print("=" * 60)
    
    # The issue is websockets.asyncio module not found
    # This is because the installed websockets version is incompatible
    
    print("\n📦 Reinstalling websockets and realtime packages...")
    
    # Uninstall and reinstall in correct order
    commands = [
        "pip3 uninstall -y websockets realtime",
        "pip3 install websockets==11.0.3",  # Compatible version
        "pip3 install --upgrade supabase",
    ]
    
    for cmd in commands:
        print(f"\n  Running: {cmd}")
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("    ✅ Success")
        else:
            print(f"    ⚠️ Warning: {result.stderr[:100]}")
    
    print("\n✅ Websockets fix applied!")
    print("\nNow testing import...")
    
    # Test the import
    try:
        from supabase import create_client
        print("  ✅ Supabase import successful!")
        
        import websockets
        print(f"  ✅ Websockets version: {websockets.__version__}")
        
        print("\n✨ Fix successful! You can now run:")
        print("   python3 aiviizn_real_agent.py")
        
    except Exception as e:
        print(f"\n❌ Import still failing: {e}")
        print("\nTry manual fix:")
        print("  pip3 uninstall -y websockets realtime supabase")
        print("  pip3 install supabase")

if __name__ == "__main__":
    main()
