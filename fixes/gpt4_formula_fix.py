#!/usr/bin/env python3
"""
GPT-4 Formula Fix for AIVIIZN Agent
Ensures GPT-4 formulas flow through to HTML templates
"""

import json
import logging

# Set up logging for debugging
logger = logging.getLogger(__name__)

def apply_gpt4_formula_fix(agent_class):
    """
    Apply fixes to ensure GPT-4 formulas reach HTML templates
    This is a monkey-patch that can be applied to the AIVIIZNRealAgent class
    """
    
    # Store original methods
    original_extract_calculations = agent_class.extract_calculations_real
    original_synthesize = agent_class.synthesize_calculations_with_claude
    original_generate_template = agent_class.generate_beautiful_template
    original_generate_js = agent_class.generate_calculation_js
    
    # Enhanced extract_calculations_real with debugging
    async def enhanced_extract_calculations_real(self, main_content):
        """Enhanced version that ensures GPT-4 calculations flow through"""
        print("  → [ENHANCED] Extracting calculations using advanced methods")
        
        all_calculations = []
        gpt4_calculations = []  # Track GPT-4 calculations separately
        
        # Method 1: Excel formulas (keeping original)
        excel_formulas = await self.extract_excel_formulas()
        if excel_formulas:
            print(f"    ✓ Excel formulas extracted: {len(excel_formulas)} sheets")
            for sheet_name, formulas in excel_formulas.items():
                for formula in formulas:
                    all_calculations.append({
                        'name': f"excel_{sheet_name}_{formula['cell']}",
                        'description': f"Excel formula from {sheet_name}!{formula['cell']}",
                        'formula': formula['formula'],
                        'source': 'excel',
                        'verified': True,
                        'javascript': self.convert_excel_to_js(formula['formula'])
                    })
        
        # Method 2: Reverse engineering
        observations = await self.reverse_engineer_calculations()
        if observations:
            print(f"    ✓ Reverse engineered: {len(observations)} relationships")
            for obs in observations:
                all_calculations.append({
                    'name': f"deduced_{obs.get('element_text', 'calc').replace(' ', '_').lower()[:20]}",
                    'description': f"Deduced from input changes: {obs['output_changed']}",
                    'formula': obs.get('likely_formula', 'unknown'),
                    'source': 'reverse_engineering',
                    'verified': False,
                    'delta': obs.get('delta', 0)
                })
        
        # Method 3: API triggers
        api_triggers = await self.analyze_calculation_triggers()
        if api_triggers:
            print(f"    ✓ API triggers found: {len(api_triggers)} endpoints")
            for trigger in api_triggers:
                all_calculations.append({
                    'name': f"api_{trigger['endpoint'].split('/')[-1]}",
                    'description': f"Calculation API: {trigger['endpoint']}",
                    'endpoint': trigger['endpoint'],
                    'method': trigger['method'],
                    'source': 'api_trigger'
                })
        
        # Get API responses
        api_responses = main_content.get('api_responses', [])
        
        # CRITICAL: GPT-4 Analysis with guaranteed flow-through
        print("    → [ENHANCED] Starting GPT-4 Turbo analysis...")
        gpt4_results = await self.enhanced_gpt4_analysis(observations, api_responses)
        
        if gpt4_results:
            print(f"    ✓ [ENHANCED] GPT-4 found {len(gpt4_results)} formulas")
            # Mark GPT-4 formulas specially
            for formula in gpt4_results:
                formula['is_gpt4'] = True  # Special marker
                formula['priority'] = 1  # High priority
                gpt4_calculations.append(formula)
                all_calculations.append(formula)
            
            # Debug: Show GPT-4 formulas
            print("    📊 GPT-4 Formulas Found:")
            for calc in gpt4_calculations:
                print(f"       - {calc['name']}: {calc.get('description', '')}")
        else:
            print("    ⚠️ [ENHANCED] No GPT-4 formulas returned")
        
        # CRITICAL: Ensure GPT-4 calculations are preserved
        print(f"    → [ENHANCED] Total calculations before synthesis: {len(all_calculations)}")
        print(f"    → [ENHANCED] GPT-4 calculations: {len(gpt4_calculations)}")
        
        # If we have calculations, synthesize them
        if all_calculations or api_responses:
            print("    → [ENHANCED] Synthesizing all findings with Claude...")
            synthesized = await self.enhanced_synthesize_with_preservation(
                all_calculations, 
                api_responses,
                gpt4_calculations  # Pass GPT-4 separately to preserve them
            )
            return synthesized
        else:
            print("    No calculations found, using fallback")
            return self.get_fallback_calculations()
    
    # Enhanced synthesis that preserves GPT-4 formulas
    async def enhanced_synthesize_with_preservation(self, all_calculations, api_responses, gpt4_calculations):
        """Synthesize with Claude but ALWAYS preserve GPT-4 formulas"""
        print("  → [ENHANCED] Claude synthesis with GPT-4 preservation")
        
        # Call original synthesis
        synthesized = await original_synthesize(self, all_calculations, api_responses)
        
        # CRITICAL: Ensure GPT-4 formulas are in the result
        gpt4_names = {calc['name'] for calc in gpt4_calculations}
        synthesized_names = {calc['name'] for calc in synthesized}
        
        # Add any missing GPT-4 formulas
        missing_gpt4 = []
        for gpt4_calc in gpt4_calculations:
            if gpt4_calc['name'] not in synthesized_names:
                print(f"    ⚠️ [ENHANCED] GPT-4 formula missing in synthesis: {gpt4_calc['name']}")
                missing_gpt4.append(gpt4_calc)
        
        if missing_gpt4:
            print(f"    → [ENHANCED] Adding {len(missing_gpt4)} missing GPT-4 formulas")
            synthesized.extend(missing_gpt4)
        
        print(f"  ✓ [ENHANCED] Final synthesized calculations: {len(synthesized)}")
        
        # Debug: List all formulas
        print("    📊 Final Formula List:")
        for calc in synthesized:
            source = calc.get('source', 'unknown')
            is_gpt4 = calc.get('is_gpt4', False)
            marker = "🤖 GPT-4" if is_gpt4 else f"📝 {source}"
            print(f"       {marker}: {calc['name']}")
        
        return synthesized
    
    # Enhanced template generation with debugging
    async def enhanced_generate_beautiful_template(self, url, main_content, calculations):
        """Enhanced template generation that ensures calculations are included"""
        print("  → [ENHANCED] Creating beautiful template")
        print(f"    📊 Calculations passed to template: {len(calculations)}")
        
        # Debug: Show what calculations we're working with
        if calculations:
            print("    📊 Calculations to include in template:")
            for calc in calculations[:10]:  # Show first 10
                print(f"       - {calc.get('name', 'unnamed')}: {calc.get('source', 'unknown')}")
                if calc.get('is_gpt4'):
                    print(f"         ⚡ This is a GPT-4 formula!")
        else:
            print("    ⚠️ [ENHANCED] NO CALCULATIONS PASSED TO TEMPLATE!")
        
        # Generate JavaScript for calculations
        calc_js = self.enhanced_generate_calculation_js(calculations)
        
        # Debug: Check if JS was generated
        if calc_js:
            print(f"    ✓ [ENHANCED] Generated {len(calc_js)} characters of JavaScript")
            print(f"    ✓ [ENHANCED] JS Preview (first 200 chars): {calc_js[:200]}...")
        else:
            print("    ❌ [ENHANCED] NO JAVASCRIPT GENERATED!")
            # Generate fallback JS
            calc_js = self.generate_fallback_js()
        
        # Store calc_js for debugging
        debug_js_path = self.project_root / "debug_calc_js.js"
        with open(debug_js_path, 'w') as f:
            f.write(f"// Generated JavaScript for {url}\n")
            f.write(f"// Total calculations: {len(calculations)}\n\n")
            f.write(calc_js)
        print(f"    📝 [ENHANCED] JavaScript saved to: {debug_js_path}")
        
        # Call original template generation with our enhanced calc_js
        # But we need to inject our calc_js properly
        template_path = await original_generate_template(self, url, main_content, calculations)
        
        # CRITICAL: Verify the template has the JavaScript
        with open(template_path, 'r') as f:
            template_content = f.read()
            
        if calc_js and calc_js not in template_content:
            print("    ⚠️ [ENHANCED] JavaScript not found in template, injecting...")
            # Re-inject the JavaScript
            template_content = template_content.replace(
                '// API response data for calculations',
                f'// API response data for calculations\n\n// ENHANCED: Injected GPT-4 Formulas\n{calc_js}\n'
            )
            
            with open(template_path, 'w') as f:
                f.write(template_content)
            print("    ✓ [ENHANCED] JavaScript injected into template")
        
        return template_path
    
    # Enhanced JavaScript generation
    def enhanced_generate_calculation_js(self, calculations):
        """Enhanced JS generation that prioritizes GPT-4 formulas"""
        print(f"    → [ENHANCED] Generating JavaScript for {len(calculations)} calculations")
        
        js_functions = []
        gpt4_count = 0
        
        for calc in calculations:
            if calc.get('is_gpt4'):
                gpt4_count += 1
                # Add special comment for GPT-4 formulas
                js_functions.append(f"""
// 🤖 GPT-4 Formula: {calc.get('name', 'unnamed')}
// Description: {calc.get('description', '')}
// Confidence: {calc.get('confidence', 'unknown')}
{calc.get('javascript', '')}
""")
            else:
                js_functions.append(calc.get('javascript', ''))
        
        print(f"    ✓ [ENHANCED] Included {gpt4_count} GPT-4 formulas in JavaScript")
        
        result = '\n\n'.join(filter(None, js_functions))  # Filter out empty strings
        
        if not result:
            print("    ⚠️ [ENHANCED] JavaScript generation produced empty result")
            return self.generate_fallback_js()
        
        return result
    
    # Fallback JavaScript if all else fails
    def generate_fallback_js(self):
        """Generate fallback JavaScript if no calculations available"""
        return """
// Fallback calculations (no formulas were extracted)
async function calculateRentRoll() {
    console.log('Using fallback rent roll calculation');
    return 0;
}

async function calculateOccupancyRate() {
    console.log('Using fallback occupancy calculation');
    return 0;
}
"""
    
    # Apply the enhanced methods to the class
    agent_class.extract_calculations_real = enhanced_extract_calculations_real
    agent_class.enhanced_synthesize_with_preservation = enhanced_synthesize_with_preservation
    agent_class.generate_beautiful_template = enhanced_generate_beautiful_template
    agent_class.enhanced_generate_calculation_js = enhanced_generate_calculation_js
    agent_class.generate_fallback_js = generate_fallback_js
    
    print("✅ GPT-4 Formula Fix Applied!")
    print("   - Enhanced extraction with debugging")
    print("   - GPT-4 formula preservation")
    print("   - JavaScript verification and injection")
    print("   - Fallback mechanisms")
    
    return agent_class


# Example usage:
if __name__ == "__main__":
    print("GPT-4 Formula Fix Module")
    print("========================")
    print("This module ensures GPT-4 formulas flow through to HTML templates")
    print("\nTo use:")
    print("1. Import your AIVIIZNRealAgent class")
    print("2. Call: apply_gpt4_formula_fix(AIVIIZNRealAgent)")
    print("3. Run your agent as normal")
    print("\nThe fix will add enhanced debugging and ensure formulas reach templates.")
