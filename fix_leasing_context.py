#!/usr/bin/env python3
"""
Fix to ensure pages go to correct directories based on URL context
Special focus on dashboard placement
"""

import re

agent_file = "/Users/ianrakow/Desktop/AIVIIZN/aiviizn_real_agent_with_ai_intelligence_updated.py"

with open(agent_file, 'r') as f:
    content = f.read()

# Find the save_template method
if 'def save_template' in content:
    # We need to add logic at the beginning to check URL context first
    
    # Find where we start checking path_str
    check_start = content.find("# CATEGORY MAPPING")
    
    if check_start != -1:
        # Add comprehensive URL analysis at the beginning
        new_logic = '''            # CATEGORY MAPPING - determine which directory the template belongs in
            # First, analyze the FULL URL for context clues
            
            # Check if we're in a leasing context (even if the word isn't in the final path)
            if any(x in url_lower for x in ['/leasing/', '/vacancies', '/rental', '/lease', '/guest_card', '/showing']):
                # This is leasing-related
                if 'dashboard' in path_str:
                    template_dir = self.templates_dir / 'leasing'
                    filename = 'dashboard.html'
                elif 'vacancies' in path_str or 'vacancy' in path_str:
                    template_dir = self.templates_dir / 'leasing'
                    filename = 'vacancies.html'
                elif 'rental' in path_str and 'application' in path_str:
                    template_dir = self.templates_dir / 'leasing'
                    filename = 'rental_applications.html'
                elif 'guest_card' in path_str:
                    template_dir = self.templates_dir / 'leasing'
                    filename = 'guest_cards.html'
                elif 'showing' in path_str:
                    template_dir = self.templates_dir / 'leasing'
                    filename = 'showings.html'
                elif 'listing' in path_str:
                    template_dir = self.templates_dir / 'leasing'
                    filename = 'listings.html'
                elif 'renewal' in path_str:
                    template_dir = self.templates_dir / 'leasing'
                    filename = 'renewals.html'
                else:
                    # Generic leasing page
                    template_dir = self.templates_dir / 'leasing'
                    if path_parts and path_parts[-1]:
                        filename = f"{path_parts[-1]}.html"
                    else:
                        filename = 'leasing_page.html'
            '''
        
        # Find the line with "# CATEGORY MAPPING" and replace from there
        lines = content.split('\n')
        new_lines = []
        replaced = False
        
        for i, line in enumerate(lines):
            if '# CATEGORY MAPPING' in line and not replaced:
                # Insert our new logic
                # Keep the indentation
                indent = len(line) - len(line.lstrip())
                new_lines.append(line)  # Keep the comment
                
                # Add the new logic with proper indentation
                for new_line in new_logic.split('\n'):
                    if new_line.strip():  # Skip empty lines
                        new_lines.append(new_line)
                
                # Skip the next line if it's the old vacancies check
                if i + 1 < len(lines) and 'vacancies' in lines[i + 1]:
                    replaced = True
                    continue
            elif replaced and 'elif' in line and 'vacancies' in line:
                # Skip the old vacancies logic since we handled it above
                continue
            else:
                new_lines.append(line)
                if replaced and ('elif' in line or 'else:' in line) and 'vacancies' not in line:
                    replaced = False  # Stop skipping lines
        
        content = '\n'.join(new_lines)
        
        # Write back
        with open(agent_file, 'w') as f:
            f.write(content)
        
        print("✅ Fixed directory categorization!")
        print("\n📁 Improved context detection:")
        print("   • URLs with /leasing/ → leasing folder")
        print("   • URLs with /vacancies → leasing folder")
        print("   • URLs with /rental → leasing folder")
        print("   • Dashboards in leasing context → /leasing/dashboard.html")
        print("\n✅ Now any page in a leasing context goes to the leasing folder!")
    else:
        print("⚠️ Could not find CATEGORY MAPPING section")
else:
    print("❌ save_template not found")
