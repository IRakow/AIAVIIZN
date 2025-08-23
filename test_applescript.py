#!/usr/bin/env python3

import subprocess
import time

def test_applescript_automation():
    print("🧪 TESTING APPLESCRIPT AUTOMATION")
    print("=" * 50)
    
    test_message = "🧪 TEST: This is an automated test message from the AIVIIZN script!"
    
    try:
        print("📱 Opening Claude desktop...")
        
        # First open Claude desktop
        result = subprocess.run(['open', '-a', 'Claude'], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ Claude desktop not found")
            return False
        
        print("✅ Claude desktop opened")
        print("🤖 Testing automated new chat creation...")
        
        # AppleScript to test automation
        applescript = f'''
        tell application "Claude"
            activate
        end tell
        
        delay 3
        
        tell application "System Events"
            tell process "Claude"
                -- Create new chat (Cmd+N)
                key code 45 using command down
                delay 2
                
                -- Type test message
                keystroke "{test_message}"
                delay 1
                
                -- Send the message (Enter)
                key code 36
            end tell
        end tell
        '''
        
        print("🚀 Executing AppleScript automation...")
        result = subprocess.run(['osascript', '-e', applescript], 
                               capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ AppleScript automation successful!")
            print("🎯 Check Claude desktop - you should see a new chat with the test message")
            return True
        else:
            print(f"❌ AppleScript error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ AppleScript automation timed out")
        return False
    except Exception as e:
        print(f"❌ Automation error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 APPLESCRIPT AUTOMATION TEST")
    print("This will:")
    print("1. Open Claude desktop")
    print("2. Create new chat (Cmd+N)")
    print("3. Type a test message")
    print("4. Send the message")
    print("")
    
    input("Press ENTER to start the test...")
    
    success = test_applescript_automation()
    
    if success:
        print("\n✅ TEST PASSED!")
        print("🎉 AppleScript automation is working correctly")
        print("🚀 Ready to run the full AIVIIZN script with automation")
    else:
        print("\n❌ TEST FAILED!")
        print("⚠️ AppleScript automation needs troubleshooting")
        print("📋 The main script will fall back to manual mode")
    
    print("\n🔄 Run './start_builder.sh' to start the full automation")
