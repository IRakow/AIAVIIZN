# GPT-4 Formula Fix Guide

## The Problem
GPT-4 formulas are being successfully extracted and stored in Supabase, but they're NOT appearing in the generated HTML templates.

## The Solution
We need to ensure formulas flow through 3 critical stages:
1. **Extraction** - Mark GPT-4 formulas with a special flag
2. **Synthesis** - Preserve them through Claude's synthesis
3. **Template** - Verify they're included in the JavaScript

## Quick Start

### Option 1: Automatic Fix (Recommended)
```bash
cd /Users/ianrakow/Desktop/AIVIIZN/fixes
python apply_gpt4_fixes.py
# Type 'yes' when prompted
```

### Option 2: Manual Fix
Follow the instructions in `minimal_manual_fix.py`:
```bash
python minimal_manual_fix.py
# Follow the 3 simple changes shown
```

### Option 3: Test First
Run the test to see how formulas should flow:
```bash
python test_formula_flow.py
# This shows the expected behavior
```

## Files Created

1. **`apply_gpt4_fixes.py`** - Automatically applies all fixes to your agent
2. **`minimal_manual_fix.py`** - Shows exact manual changes needed (just 3!)
3. **`test_formula_flow.py`** - Tests the formula flow independently
4. **`gpt4_formula_fix.py`** - Complete fix module (advanced)
5. **`direct_patches.py`** - Detailed patches for each method

## The 3 Critical Changes

### 1. Mark GPT-4 Formulas
In `enhanced_gpt4_analysis()`, add:
```python
formula['is_gpt4'] = True  # Mark as GPT-4 formula
```

### 2. Preserve Through Synthesis
In `synthesize_calculations_with_claude()`, add preservation logic:
```python
# Preserve GPT-4 formulas
gpt4_originals = [c for c in found_calculations if c.get('is_gpt4')]
for gpt4_calc in gpt4_originals:
    if gpt4_calc['name'] not in result_names:
        verified_calculations.append(gpt4_calc)
```

### 3. Debug Output
In `generate_beautiful_template()`, add:
```python
gpt4_count = sum(1 for c in calculations if c.get('is_gpt4'))
print(f"  🤖 GPT-4 formulas: {gpt4_count}")
```

## How to Verify It's Working

1. **During Execution** - Look for these messages:
   ```
   ✓ GPT-4 found 5 formulas
   🤖 GPT-4 formulas: 5
   📝 Generated 2500 characters of JavaScript
   ```

2. **In Templates** - Check generated HTML files for:
   - `async function calculate...` functions
   - Comments like `// GPT-4 Formula:`
   - Multiple calculation functions

3. **Debug Files** - Check:
   - `/Users/ianrakow/Desktop/AIVIIZN/debug_last_calc_js.js`
   - Contains the generated JavaScript

## Troubleshooting

### If GPT-4 formulas show as 0:
- The `is_gpt4` flag isn't being set
- Check line ~1742 in `enhanced_gpt4_analysis()`

### If JavaScript is empty:
- Formulas aren't reaching `generate_calculation_js()`
- Check the synthesis step isn't filtering them out

### If template doesn't have functions:
- The `{calc_js}` variable isn't being replaced
- Check line ~2200 in template generation

## Expected Output

After fixes, you should see:
```
🧠 GPT-4 Turbo mathematical analysis...
  ✓ GPT-4 identified: calculateLateFee - Late fee calculation
  ✓ GPT-4 identified: calculateOccupancyRate - Occupancy calculation
  ✓ GPT-4 found in API: calculateRentRoll
  ✓ Standard formula: calculateProration
✓ GPT-4 identified 10 total calculations

[Later in template generation:]
📊 Calculations in template: 15 total
🤖 GPT-4 formulas: 10
📝 Generated 3500 chars of JavaScript
```

## Support

If issues persist after applying fixes:
1. Check `/Users/ianrakow/Desktop/AIVIIZN/agent.log`
2. Run `test_formula_flow.py` to verify expected behavior
3. Look for debug files in `/test_results/` directory

The automatic fix creates a backup, so you can always restore:
```bash
ls *.backup_*  # Find your backup
cp aiviizn_real_agent.py.backup_[timestamp] aiviizn_real_agent.py
```

## Success Criteria

You'll know it's working when:
- ✅ GPT-4 formulas appear in debug output
- ✅ Generated templates contain calculation functions
- ✅ JavaScript includes GPT-4 formula comments
- ✅ Templates show "GPT-4 formulas: X" where X > 0
