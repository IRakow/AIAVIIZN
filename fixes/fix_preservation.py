#!/usr/bin/env python3
"""
Fix the missing GPT-4 preservation in synthesize_calculations_with_claude
"""

import re
from pathlib import Path
from datetime import datetime

def fix_gpt4_preservation():
    """Apply the missing preservation fix"""
    
    agent_file = Path("/Users/ianrakow/Desktop/AIVIIZN/aiviizn_real_agent.py")
    
    # Read the file
    with open(agent_file, 'r') as f:
        content = f.read()
    
    print("🔧 Applying GPT-4 Preservation Fix...")
    print("=" * 60)
    
    # Find the synthesize_calculations_with_claude method
    # Look for the specific return statements we need to modify
    
    # Pattern 1: Fix the first return in synthesize_calculations_with_claude
    pattern1 = r"(if json_match:.*?synthesized = json\.loads.*?return synthesized.*?)(\n\s+else:)"
    
    # Check if we can find this pattern
    if re.search(pattern1, content, re.DOTALL):
        print("✅ Found first return statement in synthesize_calculations_with_claude")
        
        replacement1 = r"""\1
                
                # PRESERVE GPT-4 FORMULAS
                gpt4_originals = [c for c in found_calculations if c.get('is_gpt4')]
                if gpt4_originals:
                    synthesized_names = {calc['name'] for calc in synthesized}
                    for gpt4_calc in gpt4_originals:
                        if gpt4_calc['name'] not in synthesized_names:
                            print(f"    ⚠️ Re-adding missing GPT-4 formula: {gpt4_calc['name']}")
                            synthesized.append(gpt4_calc)
                    print(f"  ✓ Ensured {len(gpt4_originals)} GPT-4 formulas are preserved")
                
                return synthesized
\2"""
        content = re.sub(pattern1, replacement1, content, count=1, flags=re.DOTALL)
    
    # Pattern 2: Fix the second return (for verified_calculations)
    # This is around line 2030-2040
    pattern2 = r"(verified_calculations\.append\(calc\).*?)(return verified_calculations if verified_calculations else self\.get_fallback_calculations\(\))"
    
    if re.search(pattern2, content, re.DOTALL):
        print("✅ Found second return statement with verified_calculations")
        
        replacement2 = r"""\1
                
                # PRESERVE GPT-4 FORMULAS (from found_calculations)
                if 'found_calculations' in locals():
                    gpt4_originals = [c for c in found_calculations if c.get('is_gpt4')]
                    if gpt4_originals:
                        verified_names = {calc['name'] for calc in verified_calculations}
                        for gpt4_calc in gpt4_originals:
                            if gpt4_calc['name'] not in verified_names:
                                print(f"    ⚠️ Re-adding missing GPT-4 formula: {gpt4_calc['name']}")
                                # Ensure JavaScript is present
                                if 'javascript' not in gpt4_calc:
                                    gpt4_calc['javascript'] = self.generate_calculation_function(gpt4_calc)
                                verified_calculations.append(gpt4_calc)
                        print(f"  ✓ Preserved {len(gpt4_originals)} GPT-4 formulas in final result")
                
                \2"""
        
        content = re.sub(pattern2, replacement2, content, count=1, flags=re.DOTALL)
    
    # Alternative approach: Look for a simpler pattern
    if "PRESERVE GPT-4 FORMULAS" not in content:
        print("\n⚠️ Standard patterns not found, trying alternative approach...")
        
        # Find the end of synthesize_calculations_with_claude method
        # Look for the return statement with get_fallback_calculations
        simple_pattern = r"(return verified_calculations if verified_calculations else self\.get_fallback_calculations\(\))"
        
        if re.search(simple_pattern, content):
            print("✅ Found fallback return statement")
            
            simple_replacement = r"""# PRESERVE GPT-4 FORMULAS
                if 'found_calculations' in locals():
                    gpt4_originals = [c for c in found_calculations if c.get('is_gpt4')]
                    if gpt4_originals and verified_calculations:
                        verified_names = {calc['name'] for calc in verified_calculations}
                        for gpt4_calc in gpt4_originals:
                            if gpt4_calc['name'] not in verified_names:
                                print(f"    ⚠️ Re-adding GPT-4: {gpt4_calc['name']}")
                                if 'javascript' not in gpt4_calc:
                                    gpt4_calc['javascript'] = self.generate_calculation_function(gpt4_calc)
                                verified_calculations.append(gpt4_calc)
                
                \1"""
            
            content = re.sub(simple_pattern, simple_replacement, content, count=1)
            print("✅ Applied preservation fix using alternative pattern")
    
    # Write back
    with open(agent_file, 'w') as f:
        f.write(content)
    
    # Verify the fix
    with open(agent_file, 'r') as f:
        new_content = f.read()
    
    if "PRESERVE GPT-4 FORMULAS" in new_content:
        print("\n✅ SUCCESS: GPT-4 preservation code has been added!")
        print("   The fix ensures GPT-4 formulas survive Claude's synthesis")
        
        # Count how many preservation blocks we added
        count = new_content.count("PRESERVE GPT-4 FORMULAS")
        print(f"   Added {count} preservation block(s)")
    else:
        print("\n⚠️ Manual intervention needed. Add this code manually:")
        print("=" * 60)
        print("""
In synthesize_calculations_with_claude(), right before the final return statement
(around line 2030-2040), add:

                # PRESERVE GPT-4 FORMULAS
                gpt4_originals = [c for c in found_calculations if c.get('is_gpt4')]
                if gpt4_originals:
                    verified_names = {calc['name'] for calc in verified_calculations}
                    for gpt4_calc in gpt4_originals:
                        if gpt4_calc['name'] not in verified_names:
                            print(f"    ⚠️ Re-adding GPT-4: {gpt4_calc['name']}")
                            verified_calculations.append(gpt4_calc)
                
                return verified_calculations if verified_calculations else self.get_fallback_calculations()
""")
        print("=" * 60)
    
    return "PRESERVE GPT-4 FORMULAS" in new_content

def verify_all_fixes():
    """Verify all fixes are in place"""
    agent_file = Path("/Users/ianrakow/Desktop/AIVIIZN/aiviizn_real_agent.py")
    
    with open(agent_file, 'r') as f:
        content = f.read()
    
    print("\n🔍 Final Verification:")
    print("=" * 60)
    
    checks = {
        "is_gpt4 flag": "formula['is_gpt4'] = True" in content,
        "GPT-4 preservation": "PRESERVE GPT-4 FORMULAS" in content,
        "Template debugging": "GPT-4 formulas:" in content,
        "JS generation tracking": "Generating JS:" in content,
        "GPT-4 markers": "🤖 GPT-4 Formula" in content
    }
    
    all_good = True
    for check, passed in checks.items():
        status = "✅" if passed else "❌"
        print(f"  {status} {check}")
        if not passed:
            all_good = False
    
    if all_good:
        print("\n🎉 All fixes verified successfully!")
        print("Your GPT-4 formulas should now flow through to templates.")
    else:
        print("\n⚠️ Some checks still failing. See above.")
    
    return all_good

if __name__ == "__main__":
    print("GPT-4 PRESERVATION FIX")
    print("=" * 60)
    print("This will add the missing preservation code.")
    print()
    
    success = fix_gpt4_preservation()
    
    if success:
        print("\n✅ Preservation fix applied!")
    
    # Run full verification
    verify_all_fixes()
    
    print("\n📝 Next steps:")
    print("1. Run your agent: python aiviizn_real_agent.py")
    print("2. Look for '⚠️ Re-adding GPT-4' messages during synthesis")
    print("3. Check that 'GPT-4 formulas: X' shows X > 0 in template generation")
