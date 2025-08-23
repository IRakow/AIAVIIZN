#!/usr/bin/env python3
"""
MANUAL FIX INSTRUCTIONS for GPT-4 Preservation
If the automated fix doesn't work, follow these exact instructions
"""

print("""
================================================================================
MANUAL FIX FOR GPT-4 PRESERVATION
================================================================================

Since the automated preservation fix didn't apply, here's the EXACT manual fix:

1. Open aiviizn_real_agent.py in your editor

2. Search for: "synthesize_calculations_with_claude"
   (This should be around line 1950-2000)

3. Go to the END of this method (around line 2030-2040)

4. Find this line:
   return verified_calculations if verified_calculations else self.get_fallback_calculations()

5. ADD THIS CODE RIGHT BEFORE that return line:
================================================================================
                # PRESERVE GPT-4 FORMULAS
                gpt4_originals = [c for c in found_calculations if c.get('is_gpt4')]
                if gpt4_originals:
                    verified_names = {calc['name'] for calc in verified_calculations}
                    for gpt4_calc in gpt4_originals:
                        if gpt4_calc['name'] not in verified_names:
                            print(f"    ⚠️ Re-adding missing GPT-4 formula: {gpt4_calc['name']}")
                            if 'javascript' not in gpt4_calc:
                                gpt4_calc['javascript'] = self.generate_calculation_function(gpt4_calc)
                            verified_calculations.append(gpt4_calc)
                    print(f"  ✓ Preserved {len(gpt4_originals)} GPT-4 formulas")
                
================================================================================

So the end of the method should look like:
----------------------------------------
                # PRESERVE GPT-4 FORMULAS
                gpt4_originals = [c for c in found_calculations if c.get('is_gpt4')]
                if gpt4_originals:
                    verified_names = {calc['name'] for calc in verified_calculations}
                    for gpt4_calc in gpt4_originals:
                        if gpt4_calc['name'] not in verified_names:
                            print(f"    ⚠️ Re-adding missing GPT-4 formula: {gpt4_calc['name']}")
                            if 'javascript' not in gpt4_calc:
                                gpt4_calc['javascript'] = self.generate_calculation_function(gpt4_calc)
                            verified_calculations.append(gpt4_calc)
                    print(f"  ✓ Preserved {len(gpt4_originals)} GPT-4 formulas")
                
                return verified_calculations if verified_calculations else self.get_fallback_calculations()
                
        except Exception as e:
            logger.error(f"Claude analysis error: {e}")
            return self.get_fallback_calculations()

================================================================================
ALSO CHECK: There might be TWO places to add this:
================================================================================

1. First location: After Claude creates 'synthesized' list (around line 1990)
   Look for: synthesized = json.loads(json_match.group())
   Add preservation code before: return synthesized

2. Second location: After 'verified_calculations' list (around line 2030)
   Look for: return verified_calculations if verified_calculations
   Add preservation code before this return

================================================================================
HOW TO VERIFY IT WORKED:
================================================================================

After making this change, search for "PRESERVE GPT-4" in the file.
You should find it at least once (preferably twice).

When you run the agent, you should see messages like:
  ⚠️ Re-adding missing GPT-4 formula: calculateLateFee
  ✓ Preserved 5 GPT-4 formulas

================================================================================
QUICK TEST:
================================================================================

import re

# Read your file
with open('aiviizn_real_agent.py', 'r') as f:
    content = f.read()

# Check if fix is present
if "PRESERVE GPT-4 FORMULAS" in content:
    print("✅ Fix is present!")
    count = content.count("PRESERVE GPT-4 FORMULAS")
    print(f"   Found {count} preservation block(s)")
else:
    print("❌ Fix not found - add it manually")
""")
