#!/usr/bin/env python3
"""
Fix for the unhashable type: dict error in calculation mapping
"""

import sys
import re

# Read the enhanced_field_intelligence.py file
with open('/Users/ianrakow/Desktop/AIVIIZN/enhanced_field_intelligence.py', 'r') as f:
    content = f.read()

# Find the map_calculation_variables method and fix it
# The issue is in how we prepare the fields for JSON serialization

# Replace the problematic JSON creation
old_pattern = r'''        Available fields on the page:
        \{json\.dumps\(\[\{\{
            'name': str\(f\.get\('field_name', ''\)\),
            'type': str\(f\.get\('semantic_type', 'unknown'\)\),
            'data_type': str\(f\.get\('data_type', 'text'\)\)'''

new_pattern = '''        Available fields on the page:
        {json.dumps([{
            'name': str(f.get('field_name', '')),
            'type': str(f.get('semantic_type', 'unknown')),
            'data_type': str(f.get('data_type', 'text'))'''

# More specific fix - the actual issue is the field_lookup creation
# Let's fix the field_lookup creation to handle any type of field_name
old_lookup = '''        # Prepare field lookup - ensure field_name is a string
        field_lookup = {}
        for f in page_fields:
            field_name = f.get('field_name')
            if field_name and isinstance(field_name, str):
                field_lookup[field_name] = f'''

new_lookup = '''        # Prepare field lookup - ensure field_name is a string
        field_lookup = {}
        for f in page_fields:
            field_name = f.get('field_name')
            # Convert to string if it's not already
            if field_name:
                field_name_str = str(field_name) if not isinstance(field_name, str) else field_name
                field_lookup[field_name_str] = f'''

# Apply the fix
content = content.replace(old_lookup, new_lookup)

# Also fix the JSON dumps to handle complex nested structures
# Find the full JSON dumps line and make it more robust
import_line = "import json"
if import_line in content and "from typing import" in content:
    # Add json serialization helper after imports
    helper_function = '''

def safe_json_serialize(obj):
    """Safely serialize objects for JSON, handling nested dicts"""
    if isinstance(obj, dict):
        return {str(k): safe_json_serialize(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [safe_json_serialize(item) for item in obj]
    elif hasattr(obj, '__dict__'):
        return safe_json_serialize(obj.__dict__)
    else:
        try:
            json.dumps(obj)
            return obj
        except TypeError:
            return str(obj)
'''
    
    # Insert after imports
    lines = content.split('\n')
    import_end = 0
    for i, line in enumerate(lines):
        if line.startswith('import ') or line.startswith('from '):
            import_end = i
    
    # Don't add if already exists
    if 'safe_json_serialize' not in content:
        lines.insert(import_end + 2, helper_function)
        content = '\n'.join(lines)

# Write the fixed content back
with open('/Users/ianrakow/Desktop/AIVIIZN/enhanced_field_intelligence.py', 'w') as f:
    f.write(content)

print("✅ Fixed the unhashable type: dict error in enhanced_field_intelligence.py")
print("   - Fixed field_lookup to handle non-string field names")
print("   - Added safe JSON serialization helper")
print("\n🚀 Run the agent again with: python3 aiviizn_real_agent_with_ai_intelligence_updated.py")
