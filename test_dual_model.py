#!/usr/bin/env python3
"""
Test script for dual model (Gemini + OpenAI) field matching
Claude is excluded from this field analysis
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_dual_model():
    """Test the dual model analyzer with Gemini and OpenAI only"""
    
    print("=" * 60)
    print("TESTING DUAL MODEL FIELD MATCHING (Gemini + OpenAI)")
    print("Claude excluded from field analysis")
    print("=" * 60)
    
    # Import the dual model analyzer
    from dual_model_analyzer import DualModelFieldAnalyzer
    import google.generativeai as genai
    from openai import AsyncOpenAI
    
    # Initialize both models
    print("\n🔧 Initializing AI models...")
    
    # Gemini
    gemini_model = None
    if os.getenv('GEMINI_API_KEY'):
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        gemini_model = genai.GenerativeModel(
            'gemini-1.5-pro-002',
            generation_config={
                'temperature': 0.1,
                'response_mime_type': 'application/json'
            }
        )
        print("✓ Gemini Ultra initialized")
    else:
        print("✗ Gemini API key not found")
    
    # OpenAI
    openai_client = None
    if os.getenv('OPENAI_API_KEY'):
        openai_client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        print("✓ OpenAI GPT-4 initialized")
    else:
        print("✗ OpenAI API key not found")
    
    print("ℹ️ Claude is available but excluded from field analysis")
    
    # Create dual model analyzer
    analyzer = DualModelFieldAnalyzer(gemini_model, openai_client)
    
    # Test fields
    test_fields = [
        {
            'name': 'tenant_first_name',
            'attrs': {'type': 'text', 'placeholder': 'John', 'required': True}
        },
        {
            'name': 'monthly_rent_amt',
            'attrs': {'type': 'number', 'placeholder': '0.00'}
        },
        {
            'name': 'lease_start_dt',
            'attrs': {'type': 'date'}
        },
        {
            'name': 'security_deposit',
            'attrs': {'type': 'number', 'placeholder': 'Security deposit amount'}
        }
    ]
    
    print("\n🧪 Testing dual model analysis...")
    print("-" * 60)
    
    # Test 1: Dual consensus (both models)
    print("\n📊 Test 1: Dual Consensus Mode (Both Models)")
    for field in test_fields[:2]:
        print(f"\n📋 Field: {field['name']}")
        
        result = await analyzer.analyze_with_dual_consensus(
            field['name'],
            field['attrs'],
            "Property management system for tracking tenant information and lease details"
        )
        
        print(f"   • AI Name: {result.get('ai_generated_name')}")
        print(f"   • Semantic Type: {result.get('semantic_type')}")
        print(f"   • Data Type: {result.get('data_type')}")
        print(f"   • Confidence: {result.get('confidence', 0):.1%}")
        print(f"   • Provider: {result.get('provider')}")
        
        if result.get('agreement'):
            print(f"   • Agreement: {result.get('agreement')}")
        
        if result.get('unit_of_measure'):
            print(f"   • Unit: {result.get('unit_of_measure')}")
    
    # Test 2: Fallback mode (Gemini first, then OpenAI)
    print("\n\n⚡ Test 2: Fallback Mode (Cost Optimized)")
    for field in test_fields[2:]:
        print(f"\n📋 Field: {field['name']}")
        
        result = await analyzer.analyze_with_fallback(
            field['name'],
            field['attrs'],
            "Property management system"
        )
        
        print(f"   • AI Name: {result.get('ai_generated_name')}")
        print(f"   • Semantic Type: {result.get('semantic_type')}")
        print(f"   • Provider Used: {result.get('provider')}")
        print(f"   • Confidence: {result.get('confidence', 0):.1%}")
    
    print("\n" + "=" * 60)
    print("✅ Dual model test complete!")
    print("\nSummary:")
    print("• Gemini + OpenAI work together for field analysis")
    print("• Claude remains available for other tasks (templates, etc.)")
    print("• Two modes: Consensus (accurate) or Fallback (fast/cheap)")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_dual_model())
