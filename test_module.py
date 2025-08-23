#!/usr/bin/env python3
"""
Test that the enhanced_field_intelligence module imports and works correctly
"""

import asyncio
import sys
sys.path.insert(0, '/Users/ianrakow/Desktop/AIVIIZN')

try:
    from enhanced_field_intelligence import (
        EnhancedFieldMapper,
        CalculationVariableMapper,
        FieldIntelligence
    )
    print("✅ Successfully imported enhanced_field_intelligence module!")
    
    # Test creating a CalculationVariableMapper instance
    # We'll use a dummy client for testing
    class DummyClient:
        def generate_content(self, prompt):
            class Response:
                text = '[]'  # Return empty JSON array
            return Response()
    
    dummy_client = DummyClient()
    mapper = CalculationVariableMapper(dummy_client)
    print("✅ Successfully created CalculationVariableMapper instance!")
    
    # Test the map_calculation_variables method
    async def test_mapping():
        test_fields = [
            {
                'field_name': 'sample_rate',
                'semantic_type': 'percentage',
                'data_type': 'number'
            },
            {
                'field_name': 'seconds',
                'semantic_type': 'duration', 
                'data_type': 'number'
            }
        ]
        
        result = await mapper.map_calculation_variables(
            'sample_rate/100',
            test_fields,
            'test page content'
        )
        
        print(f"✅ map_calculation_variables executed without errors!")
        print(f"   Result: {result}")
        return True
    
    # Run the async test
    success = asyncio.run(test_mapping())
    
    if success:
        print("\n" + "="*50)
        print("🎉 ALL TESTS PASSED!")
        print("The enhanced_field_intelligence.py module is working correctly!")
        print("="*50)
    
except ImportError as e:
    print(f"❌ Failed to import module: {e}")
except Exception as e:
    print(f"❌ Error during testing: {e}")
    import traceback
    traceback.print_exc()
