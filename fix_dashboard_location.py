#!/usr/bin/env python3
"""
Fix dashboard categorization - put dashboards in their proper context folders
"""

import re

# Read the agent file
agent_file = "/Users/ianrakow/Desktop/AIVIIZN/aiviizn_real_agent_with_ai_intelligence_updated.py"

with open(agent_file, 'r') as f:
    content = f.read()

# Find the dashboard handling section in save_template
# We need to improve the logic to check context

# Look for the save_template method and find dashboard handling
if 'def save_template' in content:
    # Find where we handle dashboard
    dashboard_pattern = r"elif 'dashboard' in path_str:\s+template_dir = self\.templates_dir\s+filename = 'dashboard\.html'"
    
    # Better dashboard categorization
    better_dashboard_logic = """elif 'dashboard' in path_str:
                # Determine dashboard context from URL
                if 'leasing' in url_lower or 'lease' in url_lower or 'rental' in url_lower:
                    template_dir = self.templates_dir / 'leasing'
                    filename = 'dashboard.html'
                elif 'property' in url_lower:
                    template_dir = self.templates_dir
                    filename = 'property_dashboard.html'
                elif 'maintenance' in url_lower:
                    template_dir = self.templates_dir / 'maintenance'
                    filename = 'dashboard.html'
                elif 'accounting' in url_lower:
                    template_dir = self.templates_dir / 'accounting'
                    filename = 'dashboard.html'
                elif 'report' in url_lower:
                    template_dir = self.templates_dir / 'reports'
                    filename = 'dashboard.html'
                else:
                    # Check if we're coming from a specific section
                    if '/leasing/' in url_lower or 'vacancies' in parsed.path.lower():
                        template_dir = self.templates_dir / 'leasing'
                        filename = 'dashboard.html'
                    else:
                        # Default main dashboard
                        template_dir = self.templates_dir
                        filename = 'dashboard.html'"""
    
    # Replace simple dashboard logic with context-aware logic
    if "elif 'dashboard' in path_str:" in content:
        # Find the start of this elif block
        start_idx = content.find("elif 'dashboard' in path_str:")
        if start_idx != -1:
            # Find the next elif or else to know where this block ends
            next_elif = content.find("elif ", start_idx + 1)
            next_else = content.find("else:", start_idx + 1)
            
            # Determine end position
            end_idx = min(x for x in [next_elif, next_else, len(content)] if x > start_idx)
            
            # Find the indentation
            line_start = content.rfind('\n', 0, start_idx) + 1
            line = content[line_start:start_idx]
            indent = len(line) - len(line.lstrip())
            
            # Add proper indentation to replacement
            indented_replacement = '\n'.join(
                ' ' * indent + line if line.strip() else line
                for line in better_dashboard_logic.split('\n')
            )
            
            # Replace the section
            content = content[:start_idx] + indented_replacement + '\n' + content[end_idx:]
            
            # Write back
            with open(agent_file, 'w') as f:
                f.write(content)
            
            print("✅ Fixed dashboard categorization!")
            print("\nDashboards will now be categorized by context:")
            print("   • Leasing context → /templates/leasing/dashboard.html")
            print("   • Property context → /templates/property_dashboard.html")
            print("   • Maintenance context → /templates/maintenance/dashboard.html")
            print("   • Accounting context → /templates/accounting/dashboard.html")
            print("   • Main/generic → /templates/dashboard.html")
        else:
            print("⚠️ Could not find dashboard handling section")
    else:
        print("⚠️ Dashboard logic not found in current form")
        print("Will add comprehensive categorization...")
        
        # Try to add after property_dashboard handling
        property_pattern = r"elif 'property' in path_str and 'dashboard' in path_str:"
        if property_pattern in content or "'property_dashboard'" in content:
            print("✓ Found property dashboard section, updating...")
else:
    print("❌ save_template method not found")
