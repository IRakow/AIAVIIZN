def generate_calculation_js(calculations):
    """Generate JavaScript code for all calculations"""
    if not calculations:
        return "// No calculations found"
    
    js_code = [
        "// ===== AIVIIZN Calculations =====",
        "// Generated from GPT-4 and Claude analysis",
        ""
    ]
    
    # Add each calculation as a JavaScript function
    for calc in calculations:
        if 'javascript' in calc:
            # Use the pre-generated JavaScript
            js_code.append(f"// {calc.get('description', calc['name'])}")
            js_code.append(calc['javascript'])
            js_code.append("")  # Empty line for readability
        elif 'formula' in calc:
            # Generate JavaScript from formula
            name = calc.get('name', 'unknownCalc')
            formula = calc.get('formula', '')
            description = calc.get('description', '')
            
            js_code.append(f"// {description}")
            js_code.append(f"// Formula: {formula}")
            js_code.append(f"async function {name}() {{")
            js_code.append(f"    // TODO: Implement {formula}")
            js_code.append(f"    return 0;")
            js_code.append(f"}}")
            js_code.append("")  # Empty line
    
    # Add a master function to run all calculations
    js_code.append("// Run all calculations and update UI")
    js_code.append("async function runAllCalculations() {")
    js_code.append("    const results = {};")
    js_code.append("    ")
    
    for calc in calculations:
        name = calc.get('name', 'unknownCalc')
        js_code.append(f"    try {{")
        js_code.append(f"        results['{name}'] = await {name}();")
        js_code.append(f"        console.log('✓ {name}:', results['{name}']);")
        js_code.append(f"    }} catch (e) {{")
        js_code.append(f"        console.error('✗ {name} failed:', e);")
        js_code.append(f"    }}")
        js_code.append("    ")
    
    js_code.append("    return results;")
    js_code.append("}")
    js_code.append("")
    
    # Add function to update UI with calculation results
    js_code.append("// Update UI with calculation results")
    js_code.append("function updateUIWithCalculations(results) {")
    js_code.append("    // Update metric cards and displays")
    
    for calc in calculations:
        name = calc.get('name', '')
        if 'rentroll' in name.lower() or 'rent_roll' in name.lower():
            js_code.append(f"    if (results['{name}'] !== undefined) {{")
            js_code.append(f"        const el = document.querySelector('[data-metric=\"rent-roll\"], #rentRoll, .rent-roll-value');")
            js_code.append(f"        if (el) el.textContent = '$' + results['{name}'].toLocaleString();")
            js_code.append(f"    }}")
        elif 'occupancy' in name.lower():
            js_code.append(f"    if (results['{name}'] !== undefined) {{")
            js_code.append(f"        const el = document.querySelector('[data-metric=\"occupancy\"], #occupancyRate, .occupancy-value');")
            js_code.append(f"        if (el) el.textContent = results['{name}'] + '%';")
            js_code.append(f"    }}")
        elif 'late' in name.lower() and 'fee' in name.lower():
            js_code.append(f"    if (results['{name}'] !== undefined) {{")
            js_code.append(f"        const el = document.querySelector('[data-metric=\"late-fees\"], #lateFees, .late-fees-value');")
            js_code.append(f"        if (el) el.textContent = '$' + results['{name}'].toLocaleString();")
            js_code.append(f"    }}")
    
    js_code.append("}")
    js_code.append("")
    
    # Add auto-run on page load
    js_code.append("// Auto-run calculations when called")
    js_code.append("async function updateAllCalculations() {")
    js_code.append("    const results = await runAllCalculations();")
    js_code.append("    updateUIWithCalculations(results);")
    js_code.append("    return results;")
    js_code.append("}")
    
    return "\n".join(js_code)

# Test the function
test_calculations = [
    {
        "name": "calculateLateFee",
        "description": "5% late fee on rent",
        "formula": "lateFee = monthlyRent * 0.05",
        "variables": ["monthlyRent"],
        "confidence": "high",
        "javascript": "function calculateLateFee(monthlyRent) { return monthlyRent * 0.05; }"
    },
    {
        "name": "calculateOccupancyRate",
        "description": "Percentage of occupied units",
        "formula": "occupancyRate = (occupiedUnits / totalUnits) * 100",
        "variables": ["occupiedUnits", "totalUnits"],
        "confidence": "high",
        "javascript": "function calculateOccupancyRate(occupiedUnits, totalUnits) { return totalUnits > 0 ? (occupiedUnits / totalUnits * 100).toFixed(2) : 0; }"
    }
]

print(generate_calculation_js(test_calculations))
