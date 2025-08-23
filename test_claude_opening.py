#!/usr/bin/env python3

import subprocess
import webbrowser
import time

def test_claude_opening():
    print("🧪 Testing Claude desktop opening...")
    
    # Test 1: Try to open Claude desktop
    try:
        result = subprocess.run(['open', '-a', 'Claude'], capture_output=True, text=True, timeout=5)
        print(f"✅ Command executed, return code: {result.returncode}")
        if result.stdout:
            print(f"📤 stdout: {result.stdout}")
        if result.stderr:
            print(f"⚠️ stderr: {result.stderr}")
        
        if result.returncode == 0:
            print("✅ Claude desktop should be opening...")
            return True
    except Exception as e:
        print(f"❌ Error running Claude desktop command: {e}")
    
    # Test 2: Try alternative name
    try:
        result = subprocess.run(['open', '-a', 'Claude for Desktop'], capture_output=True, text=True, timeout=5)
        print(f"✅ Alternative command executed, return code: {result.returncode}")
        if result.returncode == 0:
            print("✅ Claude for Desktop should be opening...")
            return True
    except Exception as e:
        print(f"❌ Error with alternative command: {e}")
    
    # Test 3: Fallback to browser
    print("🌐 Falling back to browser...")
    try:
        webbrowser.open("https://claude.ai/chat")
        print("✅ Browser should be opening...")
        return True
    except Exception as e:
        print(f"❌ Browser error: {e}")
    
    return False

if __name__ == "__main__":
    print("🚀 CLAUDE OPENING TEST")
    print("=" * 40)
    
    success = test_claude_opening()
    
    if success:
        print("\n✅ Test completed - some form of Claude should have opened")
    else:
        print("\n❌ Test failed - no Claude opening method worked")
    
    print("\n⏳ Waiting 5 seconds to see if anything opened...")
    time.sleep(5)
    print("✅ Test finished")
