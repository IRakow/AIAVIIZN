#!/usr/bin/env python3
"""
Direct patches to apply to aiviizn_real_agent.py
These changes ensure GPT-4 formulas flow through to HTML templates
"""

# PATCH 1: Fix extract_calculations_real (around line 1340)
# Replace the end of the method with this:

def patch_extract_calculations_real():
    return '''
        # Get API responses
        api_responses = main_content.get('api_responses', [])
        
        # ENHANCED: Use GPT-4 Turbo instead of Wolfram
        print("    → Starting GPT-4 Turbo analysis...")
        gpt4_results = await self.enhanced_gpt4_analysis(observations, api_responses)
        
        if gpt4_results:
            print(f"    ✓ GPT-4 found {len(gpt4_results)} formulas")
            # CRITICAL: Mark GPT-4 formulas for preservation
            for formula in gpt4_results:
                formula['is_gpt4'] = True  # Special marker
                formula['priority'] = 1  # High priority
            all_calculations.extend(gpt4_results)
            
            # DEBUG: Show what we have
            print(f"    📊 Total calculations collected: {len(all_calculations)}")
            gpt4_count = sum(1 for c in all_calculations if c.get('is_gpt4'))
            print(f"    🤖 GPT-4 formulas: {gpt4_count}")
        
        # Send everything to Claude for final synthesis (keeping your existing flow)
        if all_calculations or api_responses:
            print("    → Sending all findings (including GPT-4) to Claude for synthesis...")
            # CRITICAL: Pass calculations with GPT-4 markers preserved
            return await self.synthesize_calculations_with_claude(all_calculations, api_responses)
        else:
            print("    No calculations found, using fallback")
            return self.get_fallback_calculations()
'''

# PATCH 2: Fix synthesize_calculations_with_claude (around line 1950)
# Add this at the END of the method, before the return statement:

def patch_synthesize_calculations_with_claude():
    return '''
            # CRITICAL: Preserve GPT-4 formulas
            # After getting synthesized from Claude, ensure GPT-4 formulas are included
            gpt4_formulas = [c for c in found_calculations if c.get('is_gpt4')]
            if gpt4_formulas:
                print(f"  → Ensuring {len(gpt4_formulas)} GPT-4 formulas are preserved")
                
                # Check which GPT-4 formulas are in synthesized result
                synthesized_names = {calc['name'] for calc in synthesized}
                
                for gpt4_calc in gpt4_formulas:
                    if gpt4_calc['name'] not in synthesized_names:
                        print(f"    ⚠️ Adding missing GPT-4 formula: {gpt4_calc['name']}")
                        synthesized.append(gpt4_calc)
                
                print(f"  ✓ Final calculation count: {len(synthesized)}")
            
            return synthesized
'''

# PATCH 3: Fix generate_beautiful_template (around line 2089)
# Add debugging right after calc_js generation:

def patch_generate_beautiful_template():
    return '''
        # Generate calculation JavaScript
        calc_js = self.generate_calculation_js(calculations)
        
        # CRITICAL DEBUG: Verify JavaScript generation
        print(f"  📊 DEBUG: Calculations passed to template: {len(calculations)}")
        if calculations:
            gpt4_count = sum(1 for c in calculations if c.get('is_gpt4'))
            print(f"  🤖 DEBUG: GPT-4 formulas in template: {gpt4_count}")
            for calc in calculations[:5]:  # Show first 5
                marker = "GPT-4" if calc.get('is_gpt4') else calc.get('source', 'unknown')
                print(f"     - [{marker}] {calc.get('name', 'unnamed')}")
        
        print(f"  📝 DEBUG: Generated {len(calc_js)} characters of JavaScript")
        if len(calc_js) < 100:
            print(f"  ⚠️ WARNING: JavaScript seems too short!")
            print(f"  JavaScript content: {calc_js}")
        else:
            # Save debug copy
            debug_path = self.project_root / "debug_last_calc_js.js"
            with open(debug_path, 'w') as f:
                f.write(f"// Calculations: {len(calculations)}\\n")
                f.write(f"// Generated at: {datetime.now().isoformat()}\\n\\n")
                f.write(calc_js)
            print(f"  📝 DEBUG: JavaScript saved to {debug_path}")
'''

# PATCH 4: Fix generate_calculation_js (around line 2300)
# Replace the entire method with this enhanced version:

def patch_generate_calculation_js():
    return '''
    def generate_calculation_js(self, calculations: List[Dict]) -> str:
        """Generate JavaScript for all calculations - ENHANCED"""
        js_functions = []
        
        print(f"    → Generating JS for {len(calculations)} calculations")
        
        for i, calc in enumerate(calculations):
            js_code = calc.get('javascript', '')
            
            # Add debug comment for each function
            if js_code:
                # Add source info as comment
                source = "GPT-4 AI" if calc.get('is_gpt4') else calc.get('source', 'unknown')
                debug_comment = f"""
// ========================================
// Calculation #{i+1}: {calc.get('name', 'unnamed')}
// Source: {source}
// Description: {calc.get('description', 'No description')}
// ========================================"""
                
                js_functions.append(debug_comment)
                js_functions.append(js_code)
            elif calc.get('name'):  # Has name but no JS
                print(f"      ⚠️ No JS for: {calc['name']}")
                # Generate basic function
                fallback_js = f"""
// Auto-generated placeholder for: {calc.get('name')}
async function {calc.get('name')}() {{
    console.log('Placeholder for {calc.get('name')}');
    // TODO: Implement {calc.get('formula', 'formula')}
    return 0;
}}"""
                js_functions.append(fallback_js)
        
        result = '\\n\\n'.join(js_functions)
        
        if not result:
            print("      ⚠️ WARNING: No JavaScript generated!")
            # Return minimal fallback
            result = """
// WARNING: No calculations were generated
console.warn('No calculations available for this page');
"""
        
        return result
'''

# PATCH 5: Add verification at the end of replicate_page_real (around line 630)
# Add this right before the print statements at the end:

def patch_replicate_page_real():
    return '''
        # VERIFICATION: Check that calculations made it through
        if template_path and calculations:
            with open(template_path, 'r') as f:
                template_content = f.read()
            
            # Check for GPT-4 formulas
            gpt4_count = sum(1 for c in calculations if c.get('is_gpt4'))
            if gpt4_count > 0:
                if 'GPT-4' in template_content or 'gpt4' in template_content.lower():
                    print(f"  ✅ VERIFIED: GPT-4 formulas appear in template")
                else:
                    print(f"  ⚠️ WARNING: {gpt4_count} GPT-4 formulas may not be in template")
            
            # Check for any calculation functions
            if 'async function' in template_content or 'function calculate' in template_content:
                print(f"  ✅ VERIFIED: Calculation functions found in template")
            else:
                print(f"  ❌ ERROR: No calculation functions found in template!")
'''

print("""
HOW TO APPLY THESE PATCHES:
===========================

1. Make a backup of your aiviizn_real_agent.py:
   cp aiviizn_real_agent.py aiviizn_real_agent.py.backup

2. Apply each patch by finding the method and adding/modifying the code

3. Key changes:
   - Marks GPT-4 formulas with 'is_gpt4' flag
   - Preserves them through synthesis
   - Adds extensive debugging
   - Verifies JavaScript generation
   - Saves debug files

4. After applying, run your agent and watch for the debug output

5. Check these debug files after running:
   - /Users/ianrakow/Desktop/AIVIIZN/debug_last_calc_js.js
   - /Users/ianrakow/Desktop/AIVIIZN/agent.log

The patches will make it very clear if GPT-4 formulas are flowing through.
""")
