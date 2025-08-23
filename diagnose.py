#!/usr/bin/env python3

print("🔍 AIVIIZN DIAGNOSTIC SCRIPT")
print("=" * 50)

# Test 1: Basic imports and path
try:
    import os
    print(f"✅ Current directory: {os.getcwd()}")
    print(f"✅ Python imports working")
except Exception as e:
    print(f"❌ Import error: {e}")

# Test 2: Check if main script exists
script_path = "/Users/ianrakow/Desktop/AIVIIZN/autonomous_appfolio_builder.py"
if os.path.exists(script_path):
    print(f"✅ Main script found: {script_path}")
else:
    print(f"❌ Main script NOT found: {script_path}")

# Test 3: Try to import main script
try:
    import sys
    sys.path.append("/Users/ianrakow/Desktop/AIVIIZN")
    from autonomous_appfolio_builder import AutonomousAppFolioBuilder
    
    builder = AutonomousAppFolioBuilder()
    print(f"✅ Builder created successfully")
    print(f"📋 URLs loaded: {len(builder.priority_urls)}")
    
    if len(builder.priority_urls) > 0:
        print(f"📄 First page: {builder.get_page_name(builder.priority_urls[0])}")
    
except Exception as e:
    print(f"❌ Builder import error: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Test Claude opening methods
print("\n🔍 Testing Claude opening methods...")

import subprocess
import webbrowser

# Test Claude desktop
try:
    result = subprocess.run(['which', 'open'], capture_output=True, text=True)
    if result.returncode == 0:
        print("✅ 'open' command available")
    else:
        print("❌ 'open' command not found")
except:
    print("❌ Cannot test 'open' command")

# Test application presence
try:
    result = subprocess.run(['ls', '/Applications/'], capture_output=True, text=True)
    apps = result.stdout
    if 'Claude' in apps:
        print("✅ Claude app found in /Applications/")
    else:
        print("⚠️ Claude app not visible in /Applications/")
        print("📋 Available apps containing 'Claude':")
        for line in apps.split('\n'):
            if 'claude' in line.lower():
                print(f"   - {line}")
except:
    print("❌ Cannot check /Applications/")

print("\n🎯 RECOMMENDATION:")
print("1. Run: ./start_builder.sh")
print("2. Choose option 5 (immediate start)")
print("3. Watch for debug messages")
print("4. If Claude doesn't open, it will fall back to browser")
