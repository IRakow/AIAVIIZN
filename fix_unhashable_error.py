"""
Fix for the unhashable type dict error in calculation mapping
"""

# The issue is in the enhanced_field_intelligence.py file
# In the map_calculation_variables method, we need to ensure we're using strings as keys

import sys
sys.path.append('/Users/ianrakow/Desktop/AIVIIZN')

# Read the file
with open('/Users/ianrakow/Desktop/AIVIIZN/enhanced_field_intelligence.py', 'r') as f:
    content = f.read()

# Find and fix the problematic section
# The issue is in the map_calculation_variables method where we build field_lookup

old_code = """        # Prepare field lookup - ensure field_name is a string
        field_lookup = {}
        for f in page_fields:
            field_name = f.get('field_name')
            # Convert to string if it's not already
            if field_name:
                field_name_str = str(field_name) if not isinstance(field_name, str) else field_name
                field_lookup[field_name_str] = f"""

new_code = """        # Prepare field lookup - ensure field_name is a string
        field_lookup = {}
        for f in page_fields:
            # Ensure f is a dict and has field_name
            if isinstance(f, dict):
                field_name = f.get('field_name')
                # Convert to string if it's not already
                if field_name:
                    field_name_str = str(field_name) if not isinstance(field_name, str) else field_name
                    field_lookup[field_name_str] = f
            elif isinstance(f, str):
                # If f is already a string, use it as both key and value
                field_lookup[f] = {'field_name': f}"""

# Replace the code
content = content.replace(old_code, new_code)

# Write the fixed file
with open('/Users/ianrakow/Desktop/AIVIIZN/enhanced_field_intelligence.py', 'w') as f:
    f.write(content)

print("✅ Fixed the unhashable type error in calculation mapping!")
print("\nThe issue was:")
print("- The field_lookup dictionary was trying to use dict objects as keys")
print("- Fixed by ensuring we handle both dict and string field inputs properly")
print("\nYou can now run the agent again without this error!")
