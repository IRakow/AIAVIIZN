#!/usr/bin/env python3
"""
Quick check to see what's in each file
"""

# Check what methods are in each file
complete_file = "/Users/ianrakow/Desktop/AIVIIZN/aiviizn_real_agent_complete.py"
field_mapping_file = "/Users/ianrakow/Desktop/AIVIIZN/aiviizn_real_agent_complete_with_field_mapping.py"

# Key methods that should exist
key_methods = [
    "replicate_page_real",
    "capture_real_page", 
    "extract_main_content_real",
    "extract_forms_data",
    "extract_tables_data",
    "extract_navigation_data",
    "extract_calculations_real",
    "extract_api_responses_real",
    "generate_beautiful_template",
    "save_template",
    "take_screenshot",
    "store_in_supabase",
    "discover_links"
]

# Key classes that should exist
key_classes = [
    "class AIVIIZNRealAgent",
    "class FieldMapper",
    "class DuplicatePreventor"
]

print("CHECKING COMPLETE FILE:")
print("-" * 40)
try:
    with open(complete_file, 'r') as f:
        content1 = f.read()
    
    for method in key_methods:
        if f"async def {method}" in content1 or f"def {method}" in content1:
            print(f"✅ {method}")
        else:
            print(f"❌ {method}")
    
    for cls in key_classes:
        if cls in content1:
            print(f"✅ {cls}")
        else:
            print(f"❌ {cls}")
            
    print(f"\nFile size: {len(content1)} bytes")
    print(f"Lines: {len(content1.splitlines())}")
except Exception as e:
    print(f"Error: {e}")

print("\n\nCHECKING FIELD MAPPING FILE:")
print("-" * 40)
try:
    with open(field_mapping_file, 'r') as f:
        content2 = f.read()
    
    for method in key_methods:
        if f"async def {method}" in content2 or f"def {method}" in content2:
            print(f"✅ {method}")
        else:
            print(f"❌ {method}")
    
    for cls in key_classes:
        if cls in content2:
            print(f"✅ {cls}")
        else:
            print(f"❌ {cls}")
            
    print(f"\nFile size: {len(content2)} bytes")
    print(f"Lines: {len(content2.splitlines())}")
except Exception as e:
    print(f"Error: {e}")

print("\n\nSUMMARY:")
print("-" * 40)
print("The field mapping file has the new classes but is MISSING")
print("the core replication methods!")
print("\nNeed to MERGE both files to get everything.")
