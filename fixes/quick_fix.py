#!/usr/bin/env python3
"""
QUICK FIX RUNNER
Run this to apply the missing preservation fix and verify everything
"""

import subprocess
import sys
from pathlib import Path

def run_command(cmd, description):
    """Run a command and show output"""
    print(f"\n{'='*60}")
    print(f"🔧 {description}")
    print(f"{'='*60}")
    try:
        result = subprocess.run(
            ["python3"] + cmd.split(),
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent
        )
        print(result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    print("GPT-4 FORMULA QUICK FIX")
    print("="*60)
    
    # Step 1: Check current status
    print("\n📊 Checking current status...")
    run_command("check_status.py", "Current Status Check")
    
    response = input("\n👉 Apply preservation fix? (yes/no): ").strip().lower()
    
    if response == 'yes':
        # Step 2: Apply preservation fix
        print("\n🔧 Applying preservation fix...")
        success = run_command("fix_preservation.py", "Applying Preservation Fix")
        
        if success:
            # Step 3: Verify
            print("\n✅ Verifying all fixes...")
            run_command("check_status.py", "Final Verification")
            
            # Step 4: Show flow
            print("\n📊 Showing calculation flow...")
            run_command("trace_flow.py", "Calculation Flow Trace")
            
            print("\n🎉 DONE!")
            print("="*60)
            print("\n✅ All fixes should now be in place!")
            print("\n📝 Next steps:")
            print("1. Run your agent: python aiviizn_real_agent.py")
            print("2. Look for 'GPT-4 formulas: X' in the output")
            print("3. Check generated templates for calculation functions")
        else:
            print("\n⚠️ Automated fix may have failed.")
            print("Run: python manual_preservation_fix.py")
            print("for manual instructions.")
    else:
        print("\n❌ Fix not applied.")
        print("\nTo apply manually:")
        print("  python manual_preservation_fix.py")

if __name__ == "__main__":
    main()
