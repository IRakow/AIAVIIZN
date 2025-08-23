#!/usr/bin/env python3
"""
Quick fix to ensure GPT-4 formulas reach HTML templates
This script modifies your aiviizn_real_agent.py directly
"""

import re
from pathlib import Path
import shutil
from datetime import datetime

def apply_gpt4_formula_fixes():
    """Apply fixes to ensure GPT-4 formulas flow through"""
    
    agent_file = Path("/Users/ianrakow/Desktop/AIVIIZN/aiviizn_real_agent.py")
    
    # Create backup
    backup_file = agent_file.parent / f"aiviizn_real_agent.py.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy(agent_file, backup_file)
    print(f"✅ Backup created: {backup_file}")
    
    # Read the file
    with open(agent_file, 'r') as f:
        content = f.read()
    
    print("\n🔧 Applying GPT-4 Formula Fixes...")
    print("=" * 60)
    
    # FIX 1: Mark GPT-4 formulas in enhanced_gpt4_analysis
    print("\n1️⃣ Fixing enhanced_gpt4_analysis to mark formulas...")
    
    # Find the line where GPT-4 formulas are added
    pattern1 = r"(formula\['source'\] = 'gpt4_\w+')"
    replacement1 = r"\1\n                                formula['is_gpt4'] = True  # CRITICAL: Mark as GPT-4 formula"
    
    content = re.sub(pattern1, replacement1, content)
    
    # FIX 2: Debug output in extract_calculations_real
    print("2️⃣ Adding debug output to extract_calculations_real...")
    
    # Find where gpt4_results are extended
    pattern2 = r"(all_calculations\.extend\(gpt4_results\))"
    replacement2 = r"""# DEBUG: Track GPT-4 formulas
            for formula in gpt4_results:
                formula['is_gpt4'] = True  # Mark GPT-4 formulas
            \1
            print(f"    📊 Total calculations: {len(all_calculations)}")
            gpt4_count = sum(1 for c in all_calculations if c.get('is_gpt4'))
            print(f"    🤖 GPT-4 formulas: {gpt4_count}")"""
    
    content = re.sub(pattern2, replacement2, content, count=1)
    
    # FIX 3: Preserve GPT-4 in synthesize_calculations_with_claude
    print("3️⃣ Ensuring GPT-4 preservation in synthesis...")
    
    # Find the return statement in synthesize_calculations_with_claude
    synthesis_pattern = r"(return synthesized if synthesized else self\.get_fallback_calculations\(\))"
    synthesis_replacement = r"""# PRESERVE GPT-4 FORMULAS
                # Ensure GPT-4 formulas are in result
                gpt4_originals = [c for c in found_calculations if c.get('is_gpt4')]
                if gpt4_originals:
                    synthesized_names = {calc['name'] for calc in synthesized}
                    for gpt4_calc in gpt4_originals:
                        if gpt4_calc['name'] not in synthesized_names:
                            print(f"    ⚠️ Re-adding GPT-4 formula: {gpt4_calc['name']}")
                            synthesized.append(gpt4_calc)
                
                \1"""
    
    content = re.sub(synthesis_pattern, synthesis_replacement, content, count=1)
    
    # FIX 4: Debug in generate_beautiful_template
    print("4️⃣ Adding debugging to template generation...")
    
    # Find where calc_js is generated
    template_pattern = r"(calc_js = self\.generate_calculation_js\(calculations\))"
    template_replacement = r"""\1
        
        # DEBUG: Verify calculations
        print(f"  📊 Calculations in template: {len(calculations)}")
        if calculations:
            gpt4_in_template = sum(1 for c in calculations if c.get('is_gpt4'))
            print(f"  🤖 GPT-4 formulas: {gpt4_in_template}")
            for calc in calculations[:3]:
                marker = "GPT-4" if calc.get('is_gpt4') else calc.get('source', '?')
                print(f"     [{marker}] {calc.get('name', 'unnamed')}")
        
        print(f"  📝 Generated {len(calc_js)} chars of JavaScript")
        if len(calc_js) < 50:
            print("  ⚠️ WARNING: JavaScript too short!")"""
    
    content = re.sub(template_pattern, template_replacement, content, count=1)
    
    # FIX 5: Enhance generate_calculation_js
    print("5️⃣ Enhancing JavaScript generation...")
    
    # Find the generate_calculation_js method
    js_pattern = r"(def generate_calculation_js\(self, calculations: List\[Dict\]\) -> str:.*?)(js_functions = \[\])"
    js_replacement = r'\1\2\n        gpt4_count = sum(1 for c in calculations if c.get("is_gpt4"))\n        print(f"    → Generating JS: {len(calculations)} total, {gpt4_count} from GPT-4")'
    
    content = re.sub(js_pattern, js_replacement, content, flags=re.DOTALL, count=1)
    
    # FIX 6: Add GPT-4 markers in JavaScript comments
    print("6️⃣ Adding GPT-4 markers to JavaScript output...")
    
    # Enhance the loop in generate_calculation_js
    js_loop_pattern = r"(for calc in calculations:.*?)(js_functions\.append\(calc\.get\('javascript', ''\)\))"
    js_loop_replacement = r"""\1
            # Add GPT-4 marker comment if applicable
            if calc.get('is_gpt4'):
                js_functions.append(f'// 🤖 GPT-4 Formula: {calc.get("name", "unnamed")}')
            \2"""
    
    content = re.sub(js_loop_pattern, js_loop_replacement, content, flags=re.DOTALL, count=1)
    
    # Write the fixed content
    with open(agent_file, 'w') as f:
        f.write(content)
    
    print("\n✅ ALL FIXES APPLIED!")
    print("=" * 60)
    print("\n📊 Summary of changes:")
    print("  1. GPT-4 formulas marked with 'is_gpt4' flag")
    print("  2. Debug output added to track formula flow")
    print("  3. GPT-4 preservation in Claude synthesis")
    print("  4. Template generation debugging")
    print("  5. Enhanced JavaScript generation")
    print("  6. GPT-4 markers in JavaScript comments")
    
    print("\n🎯 Next steps:")
    print("  1. Run your agent: python aiviizn_real_agent.py")
    print("  2. Watch for debug output showing GPT-4 formulas")
    print("  3. Check generated templates for '🤖 GPT-4 Formula' comments")
    print("  4. Verify calculations work in the browser")
    
    print(f"\n💾 Original backed up to: {backup_file}")
    print("   To restore: cp {backup_file} {agent_file}")
    
    return True

def verify_fixes():
    """Verify the fixes were applied correctly"""
    agent_file = Path("/Users/ianrakow/Desktop/AIVIIZN/aiviizn_real_agent.py")
    
    with open(agent_file, 'r') as f:
        content = f.read()
    
    print("\n🔍 Verifying fixes...")
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
    
    return all_good

if __name__ == "__main__":
    print("GPT-4 FORMULA FIX INSTALLER")
    print("=" * 60)
    print("This will modify your aiviizn_real_agent.py to ensure")
    print("GPT-4 formulas flow through to HTML templates.")
    print()
    
    response = input("Apply fixes? (yes/no): ").strip().lower()
    
    if response == 'yes':
        success = apply_gpt4_formula_fixes()
        
        if success:
            print("\n✅ Fixes applied successfully!")
            
            if verify_fixes():
                print("\n🎉 All verifications passed!")
                print("Your agent should now properly include GPT-4 formulas in templates.")
            else:
                print("\n⚠️ Some verifications failed. Check the file manually.")
        else:
            print("\n❌ Failed to apply fixes.")
    else:
        print("\n❌ Fixes not applied. Run this script with 'yes' to apply.")
