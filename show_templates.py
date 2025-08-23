#!/usr/bin/env python3
"""
Show all templates that have been created and their structure
"""

from pathlib import Path
import json

print("\n" + "="*60)
print("📁 CURRENT TEMPLATE STRUCTURE")
print("="*60)

templates_dir = Path("/Users/ianrakow/Desktop/AIVIIZN/templates")

# Count templates
total_templates = 0
template_types = {
    'reports': [],
    'forms': [],
    'dashboards': [],
    'auth': [],
    'properties': [],
    'people': [],
    'maintenance': [],
    'accounting': [],
    'other': []
}

# Walk through templates
for template_file in templates_dir.rglob('*.html'):
    if template_file.is_file() and not template_file.name.startswith('.'):
        total_templates += 1
        
        # Categorize
        relative_path = template_file.relative_to(templates_dir)
        path_str = str(relative_path).lower()
        
        if 'report' in path_str or 'income_statement' in path_str or 'balance' in path_str or 'rent_roll' in path_str:
            template_types['reports'].append(relative_path)
        elif 'dashboard' in path_str:
            template_types['dashboards'].append(relative_path)
        elif 'auth' in path_str or 'login' in path_str or 'sign' in path_str:
            template_types['auth'].append(relative_path)
        elif 'properties' in path_str or 'property' in path_str:
            template_types['properties'].append(relative_path)
        elif 'people' in path_str or 'tenant' in path_str or 'owner' in path_str:
            template_types['people'].append(relative_path)
        elif 'maintenance' in path_str or 'work_order' in path_str:
            template_types['maintenance'].append(relative_path)
        elif 'accounting' in path_str or 'bank' in path_str or 'payable' in path_str:
            template_types['accounting'].append(relative_path)
        else:
            template_types['other'].append(relative_path)

print(f"\n📊 TEMPLATE STATISTICS:")
print(f"   Total Templates: {total_templates}")
print(f"   Directories: {len(list(templates_dir.glob('*/')))} ")

# Show by category
print(f"\n📂 TEMPLATES BY CATEGORY:\n")

for category, templates in template_types.items():
    if templates:
        print(f"🏷️  {category.upper()} ({len(templates)} templates)")
        for template in templates[:5]:  # Show first 5
            print(f"   • {template}")
        if len(templates) > 5:
            print(f"   ... and {len(templates) - 5} more")
        print()

# Show directory structure
print("📁 DIRECTORY STRUCTURE:")
directories = sorted([d for d in templates_dir.glob('*/') if d.is_dir() and not d.name.startswith('.')])
for dir_path in directories:
    file_count = len(list(dir_path.glob('*.html')))
    print(f"   📂 {dir_path.name}/ ({file_count} files)")

print("\n" + "="*60)
print("\n✨ Your agent is creating templates in this structure!")
print("   Each template corresponds to a page from the target site")
print("   The directory structure mirrors the URL paths")
print("\n" + "="*60)
