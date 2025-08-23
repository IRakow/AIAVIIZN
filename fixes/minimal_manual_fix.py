#!/usr/bin/env python3
"""
MINIMAL FIX for GPT-4 Formula Flow
These are the EXACT changes to make manually in aiviizn_real_agent.py
"""

print("""
================================================================================
MINIMAL MANUAL FIX FOR GPT-4 FORMULAS
================================================================================

Make these 3 simple changes to aiviizn_real_agent.py:

================================================================================
CHANGE #1: Mark GPT-4 Formulas (around line 1742-1762)
================================================================================

FIND this in enhanced_gpt4_analysis():
----------------------------------------
                        for formula in formulas:
                            if isinstance(formula, dict) and 'name' in formula:
                                formula['source'] = 'gpt4_observation_analysis'
                                gpt4_calculations.append(formula)

CHANGE TO:
----------
                        for formula in formulas:
                            if isinstance(formula, dict) and 'name' in formula:
                                formula['source'] = 'gpt4_observation_analysis'
                                formula['is_gpt4'] = True  # ADD THIS LINE
                                gpt4_calculations.append(formula)

Do the same for the other two places where formulas are added:
- Around line 1799: formula['source'] = 'gpt4_api_analysis'
- Around line 1836: formula['source'] = 'gpt4_domain_knowledge'

Add formula['is_gpt4'] = True after each.

================================================================================
CHANGE #2: Preserve in Synthesis (around line 2040)
================================================================================

FIND this at the END of synthesize_calculations_with_claude(), before return:
------------------------------------------------------------------------------
                return verified_calculations if verified_calculations else self.get_fallback_calculations()

CHANGE TO:
----------
                # Preserve GPT-4 formulas
                gpt4_originals = [c for c in found_calculations if c.get('is_gpt4')]
                if gpt4_originals:
                    result_names = {calc['name'] for calc in verified_calculations}
                    for gpt4_calc in gpt4_originals:
                        if gpt4_calc['name'] not in result_names:
                            verified_calculations.append(gpt4_calc)
                
                return verified_calculations if verified_calculations else self.get_fallback_calculations()

================================================================================
CHANGE #3: Debug Template (around line 2089)
================================================================================

FIND this in generate_beautiful_template():
--------------------------------------------
        # Generate calculation JavaScript
        calc_js = self.generate_calculation_js(calculations)

ADD AFTER IT:
-------------
        # Generate calculation JavaScript
        calc_js = self.generate_calculation_js(calculations)
        
        # DEBUG
        print(f"  📊 Calculations: {len(calculations)} total")
        gpt4_count = sum(1 for c in calculations if c.get('is_gpt4'))
        print(f"  🤖 GPT-4 formulas: {gpt4_count}")
        print(f"  📝 JavaScript: {len(calc_js)} characters")

================================================================================
THAT'S IT! These 3 changes will ensure GPT-4 formulas reach your templates.
================================================================================

HOW TO TEST:
1. Make these changes
2. Run your agent
3. Look for "🤖 GPT-4 formulas: X" in the output
4. Check the generated HTML templates for the formulas

If you see "GPT-4 formulas: 0", then the formulas aren't being marked.
If you see a number > 0, they're flowing through!
""")

# Also create a verification script
verification_code = '''
def verify_gpt4_flow(template_path):
    """Quick verification that GPT-4 formulas made it"""
    with open(template_path, 'r') as f:
        content = f.read()
    
    checks = {
        "Has async functions": "async function" in content,
        "Has calculation functions": "calculate" in content.lower(),
        "Has GPT-4 markers": "gpt" in content.lower() or "GPT" in content,
        "Has multiple functions": content.count("function") > 2,
        "Has Supabase integration": "supabase" in content
    }
    
    print("Template Verification:")
    for check, passed in checks.items():
        print(f"  {'✅' if passed else '❌'} {check}")
    
    # Count functions
    func_count = content.count("async function") + content.count("function ")
    print(f"\\nTotal functions found: {func_count}")
    
    return all(checks.values())
'''

print("\nBonus: Here's a function to verify your templates:")
print("=" * 60)
print(verification_code)
