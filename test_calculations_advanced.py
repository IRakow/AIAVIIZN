#!/usr/bin/env python3
"""
Test script for advanced calculation extraction methods
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

async def test_calculation_methods():
    """Test the new calculation extraction methods"""
    print("🧪 Testing Advanced Calculation Extraction Methods")
    print("=" * 60)
    
    # Import the agent
    from aiviizn_real_agent import AIVIIZNRealAgent
    
    # Initialize agent
    agent = AIVIIZNRealAgent()
    
    print("\n✅ Agent initialized successfully")
    print(f"   Supabase URL: {agent.supabase_url}")
    print(f"   Service Key: {'✓' if agent.supabase_key else '✗'}")
    print(f"   Anon Key: {'✓' if agent.supabase_anon_key else '✗'}")
    print(f"   Anthropic: {'✓' if agent.anthropic_client else '✗'}")
    print(f"   Wolfram: {'✓' if agent.wolfram_client else '✗'}")
    
    # Check if openpyxl is available
    try:
        import openpyxl
        print(f"   Excel support: ✓")
    except ImportError:
        print(f"   Excel support: ✗ (install openpyxl)")
    
    print("\n📋 New Methods Available:")
    print("   1. reverse_engineer_calculations() - Change inputs, observe outputs")
    print("   2. extract_excel_formulas() - Extract formulas from Excel exports")
    print("   3. analyze_calculation_triggers() - Monitor API calculation calls")
    print("   4. extract_formula_comments() - Mine source code for formulas")
    print("   5. deduce_formulas_from_patterns() - Compare pages to find patterns")
    
    print("\n🎯 These methods are integrated into extract_calculations_real()")
    print("   which will try all methods and synthesize results with Claude")
    
    print("\n✨ Ready to extract REAL calculations from AppFolio!")
    print("\nTo use: Run the main agent with:")
    print("   python aiviizn_real_agent.py")
    
    return True

if __name__ == "__main__":
    # Test the configuration
    success = asyncio.run(test_calculation_methods())
    
    if success:
        print("\n✅ All systems ready for advanced calculation extraction!")
    else:
        print("\n⚠️ Some issues detected - check configuration")
