#!/usr/bin/env python3
"""
Test the AI Field Intelligence Integration
Quick test to ensure everything is connected properly
"""

import asyncio
import os
from dotenv import load_dotenv
import anthropic
from openai import AsyncOpenAI

# Load environment
load_dotenv()

# Import the modules
from enhanced_field_intelligence import EnhancedFieldMapper, CalculationVariableMapper

async def test_field_intelligence():
    """Test the AI field intelligence"""
    
    print("🧪 Testing AI Field Intelligence Integration")
    print("=" * 50)
    
    # Initialize clients
    anthropic_client = anthropic.Anthropic(
        api_key=os.getenv('ANTHROPIC_API_KEY')
    )
    
    openai_client = None
    if os.getenv('OPENAI_API_KEY'):
        openai_client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        print("✓ OpenAI client initialized")
    
    print("✓ Anthropic client initialized")
    
    # Create mapper
    mapper = EnhancedFieldMapper(anthropic_client, openai_client)
    calc_mapper = CalculationVariableMapper(anthropic_client)
    
    print("\n📝 Test Cases:")
    print("-" * 50)
    
    # Test 1: Cryptic field name
    print("\n1. Testing cryptic field name...")
    test_field = {
        'name': 'field_123_abc',
        'type': 'number',
        'placeholder': '0.00'
    }
    
    result = await mapper.analyze_field_intelligently(
        field_name='field_123_abc',
        field_attributes=test_field,
        page_context='Property management rent roll showing tenant payments and balances',
        surrounding_fields=['tenant_name', 'unit_number', 'lease_start']
    )
    
    print(f"   Original: {result.original_name}")
    print(f"   AI Name: {result.ai_generated_name}")
    print(f"   Type: {result.semantic_type}")
    print(f"   Data Type: {result.data_type}")
    print(f"   Confidence: {result.confidence:.1%}")
    
    # Test 2: Calculation detection
    print("\n2. Testing calculation field...")
    calc_field = {
        'name': 'total_amount',
        'type': 'text',
        'readonly': True
    }
    
    result2 = await mapper.analyze_field_intelligently(
        field_name='total_amount',
        field_attributes=calc_field,
        page_context='Invoice showing line items with subtotal, tax, and total',
        surrounding_fields=['subtotal', 'tax_amount', 'discount']
    )
    
    print(f"   Field: {result2.ai_generated_name}")
    print(f"   Is Calculated: {result2.is_calculated}")
    if result2.calculation_formula:
        print(f"   Formula: {result2.calculation_formula}")
    
    # Test 3: Variable mapping
    print("\n3. Testing calculation variable mapping...")
    test_formula = "total_rent = base_rent + utilities + late_fees"
    test_fields = [
        {'field_name': 'base_rent', 'semantic_type': 'rent_amount', 'data_type': 'currency'},
        {'field_name': 'utilities', 'semantic_type': 'utility_charge', 'data_type': 'currency'},
        {'field_name': 'late_fees', 'semantic_type': 'fee', 'data_type': 'currency'}
    ]
    
    variables = await calc_mapper.map_calculation_variables(
        test_formula,
        test_fields,
        "Rent payment calculation page"
    )
    
    print(f"   Formula: {test_formula}")
    print(f"   Variables found: {len(variables)}")
    for var in variables:
        print(f"   - {var.get('variable_name')} → {var.get('semantic_meaning')}")
    
    print("\n✅ All tests completed!")
    print("=" * 50)

if __name__ == "__main__":
    # Check for API keys
    if not os.getenv('ANTHROPIC_API_KEY'):
        print("❌ Error: ANTHROPIC_API_KEY not set in .env file")
        exit(1)
    
    # Run tests
    asyncio.run(test_field_intelligence())
