#!/usr/bin/env python3
"""
Quick check to see the current state of GPT-4 formula handling
"""

from pathlib import Path
import re

def check_current_state():
    """Check the current state of the agent file"""
    
    agent_file = Path("/Users/ianrakow/Desktop/AIVIIZN/aiviizn_real_agent.py")
    
    print("GPT-4 FORMULA FIX STATUS CHECK")
    print("=" * 60)
    
    with open(agent_file, 'r') as f:
        content = f.read()
    
    # Check for various fixes
    print("\n✅ FIXES ALREADY APPLIED:")
    print("-" * 40)
    
    if "formula['is_gpt4'] = True" in content:
        count = content.count("formula['is_gpt4'] = True")
        print(f"✓ GPT-4 marking: Found {count} locations")
        
        # Find which sources are marked
        patterns = [
            "gpt4_observation_analysis",
            "gpt4_api_analysis", 
            "gpt4_domain_knowledge"
        ]
        for pattern in patterns:
            if pattern in content:
                # Check if is_gpt4 is near this pattern
                index = content.find(pattern)
                snippet = content[index-100:index+200]
                if "is_gpt4" in snippet:
                    print(f"  ✓ {pattern} is marked")
                else:
                    print(f"  ⚠️ {pattern} found but not marked")
    
    if "GPT-4 formulas:" in content:
        print("✓ Template debugging: Added")
    
    if "🤖 GPT-4 Formula" in content:
        print("✓ JavaScript markers: Added")
    
    print("\n❌ FIXES STILL NEEDED:")
    print("-" * 40)
    
    if "PRESERVE GPT-4 FORMULAS" not in content:
        print("✗ GPT-4 preservation in synthesis: MISSING")
        print("  This is the critical fix!")
        print("  Run: python fix_preservation.py")
    else:
        count = content.count("PRESERVE GPT-4 FORMULAS")
        print(f"✓ GPT-4 preservation: Found {count} block(s)")
    
    # Check specific method signatures
    print("\n📊 METHOD ANALYSIS:")
    print("-" * 40)
    
    # Find synthesize_calculations_with_claude
    if "def synthesize_calculations_with_claude" in content:
        print("✓ synthesize_calculations_with_claude found")
        
        # Extract the method
        start = content.find("def synthesize_calculations_with_claude")
        if start != -1:
            # Find the next method (approximate end)
            next_def = content.find("\n    def ", start + 50)
            if next_def == -1:
                next_def = len(content)
            
            method_content = content[start:next_def]
            
            # Check what's in the method
            if "PRESERVE GPT-4" in method_content:
                print("  ✓ Has preservation code")
            else:
                print("  ✗ Missing preservation code")
            
            if "verified_calculations.append" in method_content:
                print("  ✓ Builds verified_calculations list")
            
            if "found_calculations" in method_content:
                print("  ✓ References found_calculations")
    
    # Find generate_calculation_js
    if "def generate_calculation_js" in content:
        print("✓ generate_calculation_js found")
        
        start = content.find("def generate_calculation_js")
        if start != -1:
            next_def = content.find("\n    def ", start + 50)
            if next_def == -1:
                next_def = start + 1000
            
            method_content = content[start:next_def]
            
            if "is_gpt4" in method_content:
                print("  ✓ Checks for GPT-4 flag")
            else:
                print("  ✗ Doesn't check for GPT-4 flag")
    
    print("\n🎯 RECOMMENDED ACTION:")
    print("=" * 60)
    
    if "PRESERVE GPT-4 FORMULAS" not in content:
        print("1. Run: python fix_preservation.py")
        print("   OR")
        print("2. Follow: python manual_preservation_fix.py")
        print("\nThis is the only missing piece!")
    else:
        print("All fixes appear to be in place! 🎉")
        print("\nTest by running your agent and looking for:")
        print("  - 'GPT-4 formulas: X' where X > 0")
        print("  - '⚠️ Re-adding missing GPT-4 formula' messages")
        print("  - Check generated templates for calculation functions")

if __name__ == "__main__":
    check_current_state()
