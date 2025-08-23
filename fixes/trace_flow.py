#!/usr/bin/env python3
"""
Trace the exact flow of calculations through the agent
This helps identify where GPT-4 formulas might be getting lost
"""

from pathlib import Path
import re
import json

def trace_calculation_flow():
    """Trace how calculations flow through the agent"""
    
    agent_file = Path("/Users/ianrakow/Desktop/AIVIIZN/aiviizn_real_agent.py")
    
    print("CALCULATION FLOW TRACE")
    print("=" * 60)
    print("This shows how calculations flow through your agent:\n")
    
    with open(agent_file, 'r') as f:
        content = f.read()
    
    # Flow stages
    stages = []
    
    # Stage 1: GPT-4 Analysis
    print("1️⃣ STAGE 1: GPT-4 Analysis (enhanced_gpt4_analysis)")
    print("-" * 40)
    if "async def enhanced_gpt4_analysis" in content:
        print("✓ Method exists")
        
        # Check what it returns
        if "gpt4_calculations = []" in content:
            print("✓ Creates gpt4_calculations list")
        
        if "formula['is_gpt4'] = True" in content:
            print("✓ Marks formulas with is_gpt4 flag")
        else:
            print("⚠️ Does NOT mark formulas with is_gpt4 flag")
            stages.append("not_marked")
        
        if "return gpt4_calculations" in content:
            print("✓ Returns gpt4_calculations")
    else:
        print("❌ Method not found!")
    
    # Stage 2: Extract Calculations
    print("\n2️⃣ STAGE 2: Extract Calculations (extract_calculations_real)")
    print("-" * 40)
    if "async def extract_calculations_real" in content:
        print("✓ Method exists")
        
        # Find the method
        start = content.find("async def extract_calculations_real")
        end = content.find("\n    async def ", start + 50)
        if end == -1:
            end = content.find("\n    def ", start + 50)
        if end == -1:
            end = len(content)
        
        method = content[start:end]
        
        if "gpt4_results = await self.enhanced_gpt4_analysis" in method:
            print("✓ Calls enhanced_gpt4_analysis")
        
        if "all_calculations.extend(gpt4_results)" in method:
            print("✓ Adds GPT-4 results to all_calculations")
        
        if "return await self.synthesize_calculations_with_claude" in method:
            print("✓ Passes to synthesis")
        
        # Check for debugging
        if "GPT-4 formulas:" in method or "gpt4_count" in method:
            print("✓ Has GPT-4 debugging output")
        else:
            print("⚠️ No GPT-4 specific debugging")
    
    # Stage 3: Synthesis
    print("\n3️⃣ STAGE 3: Synthesis (synthesize_calculations_with_claude)")
    print("-" * 40)
    if "async def synthesize_calculations_with_claude" in content:
        print("✓ Method exists")
        
        # Find the method
        start = content.find("async def synthesize_calculations_with_claude")
        end = content.find("\n    async def ", start + 50)
        if end == -1:
            end = content.find("\n    def ", start + 50)
        if end == -1:
            end = len(content)
        
        method = content[start:end]
        
        if "found_calculations" in method:
            print("✓ Receives found_calculations parameter")
        
        if "PRESERVE GPT-4 FORMULAS" in method:
            print("✓ Has GPT-4 preservation code")
        else:
            print("❌ MISSING GPT-4 preservation code!")
            print("  This is where GPT-4 formulas get lost!")
            stages.append("lost_in_synthesis")
        
        if "return verified_calculations" in method or "return synthesized" in method:
            print("✓ Returns calculations")
    
    # Stage 4: Template Generation
    print("\n4️⃣ STAGE 4: Template Generation (generate_beautiful_template)")
    print("-" * 40)
    if "async def generate_beautiful_template" in content:
        print("✓ Method exists")
        
        # Find the method
        start = content.find("async def generate_beautiful_template")
        end = content.find("\n    async def ", start + 50)
        if end == -1:
            end = content.find("\n    def ", start + 50)
        if end == -1:
            end = len(content)
        
        method = content[start:end]
        
        if "calculations: List[Dict]" in method or "calculations)" in method:
            print("✓ Receives calculations parameter")
        
        if "calc_js = self.generate_calculation_js(calculations)" in method:
            print("✓ Generates JavaScript from calculations")
        
        if "GPT-4 formulas:" in method:
            print("✓ Has GPT-4 debugging")
        else:
            print("⚠️ No GPT-4 specific debugging")
        
        if "{calc_js}" in method:
            print("✓ Inserts JavaScript into template")
    
    # Stage 5: JavaScript Generation
    print("\n5️⃣ STAGE 5: JavaScript Generation (generate_calculation_js)")
    print("-" * 40)
    if "def generate_calculation_js" in content:
        print("✓ Method exists")
        
        # Find the method
        start = content.find("def generate_calculation_js")
        end = content.find("\n    def ", start + 50)
        if end == -1:
            end = content.find("\n    async def ", start + 50)
        if end == -1:
            end = start + 500
        
        method = content[start:end]
        
        if "for calc in calculations:" in method:
            print("✓ Loops through calculations")
        
        if "calc.get('is_gpt4')" in method:
            print("✓ Checks for GPT-4 flag")
        else:
            print("⚠️ Doesn't check for GPT-4 flag")
        
        if "🤖 GPT-4 Formula" in method:
            print("✓ Adds GPT-4 markers to output")
    
    # Diagnosis
    print("\n🔍 DIAGNOSIS:")
    print("=" * 60)
    
    if "lost_in_synthesis" in stages:
        print("❌ PROBLEM IDENTIFIED: GPT-4 formulas are being lost in synthesis!")
        print("\n   The issue is in synthesize_calculations_with_claude()")
        print("   Claude's synthesis is not preserving the GPT-4 formulas.")
        print("\n   FIX: Run 'python fix_preservation.py' to add preservation code")
    elif "not_marked" in stages:
        print("⚠️ PROBLEM: GPT-4 formulas are not being marked with is_gpt4 flag")
        print("\n   Without the flag, they can't be tracked through the pipeline.")
        print("\n   FIX: Re-run 'python apply_gpt4_fixes.py'")
    elif "PRESERVE GPT-4 FORMULAS" not in content:
        print("⚠️ MAIN ISSUE: No preservation code in synthesis")
        print("\n   GPT-4 formulas are extracted but not preserved through synthesis.")
        print("\n   FIX: Run 'python fix_preservation.py'")
    else:
        print("✅ All stages appear to be properly configured!")
        print("\n   If formulas still aren't appearing:")
        print("   1. Check that GPT-4 API is returning formulas")
        print("   2. Verify calculations list isn't empty")
        print("   3. Check debug output when running the agent")
    
    # Show the expected flow
    print("\n📊 EXPECTED FLOW:")
    print("=" * 60)
    print("""
    1. enhanced_gpt4_analysis() → Returns list with is_gpt4=True
                ↓
    2. extract_calculations_real() → Combines all calculations
                ↓
    3. synthesize_calculations_with_claude() → PRESERVES GPT-4 formulas
                ↓
    4. generate_beautiful_template() → Receives full list
                ↓
    5. generate_calculation_js() → Creates JavaScript
                ↓
    6. Template includes JavaScript with GPT-4 formulas
    """)

if __name__ == "__main__":
    trace_calculation_flow()
    
    print("\n💡 TIP: After fixing, run your agent and watch for these messages:")
    print("  - 'GPT-4 found X formulas'")
    print("  - 'Re-adding missing GPT-4 formula'")
    print("  - 'GPT-4 formulas: X' in template generation")
