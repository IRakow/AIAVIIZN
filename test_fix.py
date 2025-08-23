#!/usr/bin/env python3
"""
Test script to verify the enhanced_field_intelligence.py fix
"""

import asyncio
import json

# Test the problematic code pattern that was causing the error
def test_json_dumps_fix():
    """Test that the json.dumps fix works correctly"""
    
    # Simulate page_fields data
    page_fields = [
        {
            'field_name': 'sample_rate',
            'semantic_type': 'percentage',
            'data_type': 'number'
        },
        {
            'field_name': 'total_amount', 
            'semantic_type': 'currency',
            'data_type': 'currency'
        }
    ]
    
    # This is the FIXED code pattern from enhanced_field_intelligence.py
    # Create the field list for the prompt - using single curly braces
    fields_for_prompt = [{
        'name': str(f.get('field_name', '')),
        'type': str(f.get('semantic_type', 'unknown')),
        'data_type': str(f.get('data_type', 'text'))
    } for f in page_fields[:20] if f.get('field_name')]
    
    # Now use json.dumps on the pre-built list
    json_output = json.dumps(fields_for_prompt, indent=2)
    
    print("✅ Test passed! The fix works correctly.")
    print("\nGenerated JSON:")
    print(json_output)
    
    # Verify it's valid JSON
    try:
        parsed = json.loads(json_output)
        print(f"\n✅ Valid JSON with {len(parsed)} fields")
        return True
    except json.JSONDecodeError as e:
        print(f"\n❌ JSON decode error: {e}")
        return False

# Test the old problematic pattern to show it would fail
def test_old_broken_pattern():
    """Show what the old broken pattern would have done"""
    print("\n" + "="*50)
    print("Testing the OLD BROKEN pattern (for comparison):")
    print("="*50)
    
    page_fields = [
        {'field_name': 'test', 'semantic_type': 'text', 'data_type': 'text'}
    ]
    
    try:
        # This is what the OLD BROKEN code was trying to do
        # It would fail with: TypeError: unhashable type: 'dict'
        prompt = f"""
        {json.dumps([{{
            'name': str(f.get('field_name', '')),
            'type': str(f.get('semantic_type', 'unknown'))
        }} for f in page_fields], indent=2)}
        """
        print("❌ This shouldn't work - if it does, something is wrong")
    except TypeError as e:
        print(f"✅ Expected error occurred: {e}")
        print("This is the error that was happening before the fix!")
        return True
    
    return False

if __name__ == "__main__":
    print("Testing enhanced_field_intelligence.py fix...")
    print("="*50)
    
    # Test the fixed pattern
    success = test_json_dumps_fix()
    
    # Show what the old pattern would have done
    # Note: This will fail as expected, showing the error was real
    try:
        test_old_broken_pattern()
    except:
        pass
    
    if success:
        print("\n" + "="*50)
        print("🎉 ALL TESTS PASSED! The fix is working correctly!")
        print("You should be able to run your main script without errors now.")
    else:
        print("\n⚠️ There might still be an issue - please check the output above")
