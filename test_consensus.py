#!/usr/bin/env python3
"""
Test script for triple AI consensus field matching
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_consensus():
    """Test the consensus field analyzer"""
    
    print("=" * 60)
    print("TESTING TRIPLE AI CONSENSUS FIELD MATCHING")
    print("=" * 60)
    
    # Import the consensus analyzer
    from field_consensus_analyzer import ConsensusFieldAnalyzer
    import google.generativeai as genai
    from openai import AsyncOpenAI
    import anthropic
    
    # Initialize all three models
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
    
    # Claude
    anthropic_client = None
    if os.getenv('ANTHROPIC_API_KEY'):
        anthropic_client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        print("✓ Claude Opus initialized")
    else:
        print("✗ Anthropic API key not found")
    
    # Create consensus analyzer
    analyzer = ConsensusFieldAnalyzer(gemini_model, openai_client, anthropic_client)
    
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
        }
    ]
    
    print("\n🧪 Testing consensus analysis on sample fields...")
    print("-" * 60)
    
    for field in test_fields:
        print(f"\n📋 Field: {field['name']}")
        print(f"   Attributes: {field['attrs']}")
        
        # Analyze with consensus
        result = await analyzer.analyze_with_consensus(
            field['name'],
            field['attrs'],
            "Property management system for tracking tenant information and lease details"
        )
        
        print(f"\n   Results:")
        print(f"   • AI Name: {result.get('ai_generated_name')}")
        print(f"   • Semantic Type: {result.get('semantic_type')}")
        print(f"   • Data Type: {result.get('data_type')}")
        print(f"   • Confidence: {result.get('confidence', 0):.1%}")
        print(f"   • Provider: {result.get('provider')}")
        
        if result.get('consensus_count'):
            print(f"   • Models that succeeded: {result.get('consensus_count')}")
        
        if result.get('unit_of_measure'):
            print(f"   • Unit: {result.get('unit_of_measure')}")
        
        if result.get('is_calculated'):
            print(f"   • Is Calculated: Yes")
            if result.get('calculation_formula'):
                print(f"   • Formula: {result.get('calculation_formula')}")
    
    print("\n" + "=" * 60)
    print("✅ Test complete!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_consensus())
