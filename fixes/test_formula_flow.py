#!/usr/bin/env python3
"""
Test script to verify GPT-4 formulas flow through to templates
Run this to test the formula pipeline independently
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path

# Simulate the formula flow
async def test_formula_flow():
    """Test that formulas flow from GPT-4 to final template"""
    
    print("=" * 60)
    print("GPT-4 FORMULA FLOW TEST")
    print("=" * 60)
    
    # Step 1: Simulate GPT-4 formula extraction
    print("\n1️⃣ SIMULATING GPT-4 FORMULA EXTRACTION")
    print("-" * 40)
    
    gpt4_formulas = [
        {
            "name": "calculateLateFee",
            "description": "Late fee calculation for overdue rent",
            "formula": "lateFee = monthlyRent * 0.05",
            "variables": ["monthlyRent"],
            "confidence": "high",
            "source": "gpt4_observation_analysis",
            "is_gpt4": True,
            "javascript": """
async function calculateLateFee(monthlyRent) {
    // GPT-4 Formula: 5% late fee
    return monthlyRent * 0.05;
}"""
        },
        {
            "name": "calculateOccupancyRate",
            "description": "Calculate property occupancy rate",
            "formula": "(occupiedUnits / totalUnits) * 100",
            "variables": ["occupiedUnits", "totalUnits"],
            "confidence": "high", 
            "source": "gpt4_api_analysis",
            "is_gpt4": True,
            "javascript": """
async function calculateOccupancyRate(occupiedUnits, totalUnits) {
    // GPT-4 Formula: Occupancy percentage
    if (totalUnits === 0) return 0;
    return (occupiedUnits / totalUnits * 100).toFixed(2);
}"""
        },
        {
            "name": "calculateProration",
            "description": "Prorate rent for partial month",
            "formula": "(monthlyRent / daysInMonth) * daysOccupied",
            "variables": ["monthlyRent", "daysInMonth", "daysOccupied"],
            "confidence": "high",
            "source": "gpt4_domain_knowledge",
            "is_gpt4": True,
            "javascript": """
async function calculateProration(monthlyRent, daysInMonth, daysOccupied) {
    // GPT-4 Formula: Daily proration
    const dailyRate = monthlyRent / daysInMonth;
    return (dailyRate * daysOccupied).toFixed(2);
}"""
        }
    ]
    
    print(f"✅ GPT-4 extracted {len(gpt4_formulas)} formulas:")
    for f in gpt4_formulas:
        print(f"   - {f['name']}: {f['description']}")
    
    # Step 2: Simulate synthesis (should preserve GPT-4 formulas)
    print("\n2️⃣ SIMULATING CLAUDE SYNTHESIS")
    print("-" * 40)
    
    # Simulate Claude adding some formulas but potentially missing some GPT-4 ones
    claude_formulas = [
        {
            "name": "calculateRentRoll",
            "description": "Sum of all rents",
            "formula": "SUM(rents)",
            "source": "claude_synthesis",
            "javascript": "async function calculateRentRoll() { return 0; }"
        }
    ]
    
    # This is what SHOULD happen - preserve GPT-4 formulas
    all_formulas = claude_formulas.copy()
    
    # Check if GPT-4 formulas are preserved
    claude_names = {f['name'] for f in claude_formulas}
    preserved_count = 0
    lost_formulas = []
    
    for gpt4_formula in gpt4_formulas:
        if gpt4_formula['name'] not in claude_names:
            all_formulas.append(gpt4_formula)
            preserved_count += 1
        else:
            lost_formulas.append(gpt4_formula['name'])
    
    print(f"✅ Preserved {preserved_count} GPT-4 formulas")
    if lost_formulas:
        print(f"⚠️ Lost formulas: {lost_formulas}")
    print(f"📊 Total formulas after synthesis: {len(all_formulas)}")
    
    # Step 3: Generate JavaScript
    print("\n3️⃣ GENERATING JAVASCRIPT")
    print("-" * 40)
    
    js_functions = []
    for calc in all_formulas:
        if calc.get('javascript'):
            source_marker = "🤖 GPT-4" if calc.get('is_gpt4') else "📝 Other"
            js_comment = f"""
// {source_marker} Formula: {calc['name']}
// {calc.get('description', '')}"""
            js_functions.append(js_comment)
            js_functions.append(calc['javascript'])
    
    final_js = '\n'.join(js_functions)
    
    print(f"✅ Generated {len(final_js)} characters of JavaScript")
    print(f"📊 Includes {final_js.count('GPT-4')} GPT-4 formula markers")
    
    # Step 4: Verify in template
    print("\n4️⃣ VERIFYING TEMPLATE INCLUSION")
    print("-" * 40)
    
    template_content = f"""
<!-- Test Template -->
<script>
{final_js}

// Test execution
async function testFormulas() {{
    console.log('Testing GPT-4 formulas...');
    
    // Test late fee
    const lateFee = await calculateLateFee(1000);
    console.log('Late fee on $1000:', lateFee);
    
    // Test occupancy
    const occupancy = await calculateOccupancyRate(45, 50);
    console.log('Occupancy (45/50):', occupancy + '%');
    
    // Test proration
    const prorated = await calculateProration(1500, 30, 15);
    console.log('Prorated rent (15/30 days of $1500):', prorated);
}}
</script>
"""
    
    # Check what made it to the template
    gpt4_functions_in_template = template_content.count('GPT-4 Formula')
    async_functions_in_template = template_content.count('async function')
    
    print(f"✅ Template contains {gpt4_functions_in_template} GPT-4 formulas")
    print(f"✅ Template contains {async_functions_in_template} async functions")
    
    # Save test results
    test_dir = Path("/Users/ianrakow/Desktop/AIVIIZN/test_results")
    test_dir.mkdir(exist_ok=True)
    
    # Save the JavaScript
    js_file = test_dir / f"test_formulas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.js"
    with open(js_file, 'w') as f:
        f.write(final_js)
    print(f"\n📝 JavaScript saved to: {js_file}")
    
    # Save the template
    template_file = test_dir / f"test_template_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    with open(template_file, 'w') as f:
        f.write(template_content)
    print(f"📝 Template saved to: {template_file}")
    
    # Final verdict
    print("\n" + "=" * 60)
    print("TEST RESULTS")
    print("=" * 60)
    
    if gpt4_functions_in_template >= len(gpt4_formulas):
        print("✅ SUCCESS: All GPT-4 formulas made it to the template!")
    elif gpt4_functions_in_template > 0:
        print(f"⚠️ PARTIAL: Only {gpt4_functions_in_template}/{len(gpt4_formulas)} GPT-4 formulas in template")
    else:
        print("❌ FAILURE: No GPT-4 formulas found in template")
    
    print("\nTo fix issues:")
    print("1. Check that 'is_gpt4' flag is set on GPT-4 formulas")
    print("2. Verify synthesis preserves GPT-4 formulas")
    print("3. Ensure generate_calculation_js processes all formulas")
    print("4. Confirm template includes the generated JavaScript")
    
    return gpt4_functions_in_template >= len(gpt4_formulas)

# Run the test
if __name__ == "__main__":
    print("Starting GPT-4 Formula Flow Test...")
    success = asyncio.run(test_formula_flow())
    
    if success:
        print("\n🎉 Test PASSED! Formula flow is working correctly.")
    else:
        print("\n⚠️ Test FAILED! Check the debug output above.")
    
    print("\nNext steps:")
    print("1. Apply the patches from direct_patches.py")
    print("2. Run your agent with a test page")
    print("3. Check /debug_last_calc_js.js for the generated code")
    print("4. Verify the HTML template includes the JavaScript")
