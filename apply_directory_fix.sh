#!/bin/bash

echo "🔧 Fixing Template Directory Structure"
echo "======================================"
echo ""

python3 << 'EOF'
import re

# Read the agent file
agent_file = "/Users/ianrakow/Desktop/AIVIIZN/aiviizn_real_agent_with_ai_intelligence_updated.py"

with open(agent_file, 'r') as f:
    content = f.read()

# Check if we already have the enhanced visibility
if 'CREATING TEMPLATE RIGHT NOW' in content:
    print("✓ Template visibility already added")
    
    # Now update to add proper directory categorization
    # Find the section after "CREATING TEMPLATE RIGHT NOW" logging
    
    # Look for the save_template method
    start_idx = content.find('def save_template(self, url: str, html: str) -> str:')
    if start_idx != -1:
        # Find the current template_dir assignment
        section_start = content.find('# Determine template location', start_idx)
        if section_start == -1:
            section_start = content.find('if len(path_parts) > 1:', start_idx)
        
        if section_start != -1:
            # Find where we set template_path
            section_end = content.find('# SHOW WHAT', start_idx)
            if section_end == -1:
                section_end = content.find('print(f"\\n{', start_idx)
            
            if section_end != -1:
                # Replace the directory logic
                new_logic = """
            # Determine proper directory based on URL/content type
            url_lower = url.lower()
            path_str = parsed.path.lower()
            
            # CATEGORY MAPPING - determine which directory the template belongs in
            if 'vacancies' in path_str or 'vacancy' in path_str:
                template_dir = self.templates_dir / 'leasing'
                filename = 'vacancies.html'
            elif 'tenant' in path_str or 'residents' in path_str:
                template_dir = self.templates_dir / 'people'
                filename = 'tenants.html'
            elif 'rental' in path_str and 'application' in path_str:
                template_dir = self.templates_dir / 'leasing'
                filename = 'rental_applications.html'
            elif 'lease' in path_str:
                template_dir = self.templates_dir / 'leasing'
                filename = 'leases.html'
            elif 'property' in path_str and 'dashboard' in path_str:
                template_dir = self.templates_dir
                filename = 'property_dashboard.html'
            elif 'rent_roll' in path_str:
                template_dir = self.templates_dir
                filename = 'rent_roll.html'
            elif 'income_statement' in path_str:
                template_dir = self.templates_dir
                filename = 'income_statement.html'
            elif 'delinquency' in path_str:
                template_dir = self.templates_dir
                filename = 'delinquency_report.html'
            elif 'maintenance' in path_str or 'work_order' in path_str:
                template_dir = self.templates_dir / 'maintenance'
                filename = path_parts[-1] + '.html' if path_parts[-1] else 'work_orders.html'
            elif 'accounting' in path_str or 'bank' in path_str:
                template_dir = self.templates_dir / 'accounting'
                filename = path_parts[-1] + '.html' if path_parts[-1] else 'accounting.html'
            elif 'memorized_reports' in path_str:
                template_dir = self.templates_dir / 'memorized_reports'
                import re as regex
                id_match = regex.search(r'/(\d+)', parsed.path)
                if id_match:
                    filename = f"{id_match.group(1)}.html"
                else:
                    filename = 'report.html'
            elif 'report' in path_str:
                template_dir = self.templates_dir / 'reports'
                filename = path_parts[-1] + '.html' if path_parts[-1] else 'report.html'
            else:
                # Default: use URL structure
                if len(path_parts) > 1:
                    template_dir = self.templates_dir / '/'.join(path_parts[:-1])
                    filename = f"{path_parts[-1]}.html" if path_parts[-1] else 'index.html'
                else:
                    template_dir = self.templates_dir
                    filename = f"{path_parts[0]}.html" if path_parts[0] else 'index.html'
            
            # Ensure directory exists
            template_dir.mkdir(parents=True, exist_ok=True)
            template_path = template_dir / filename
            
            """
                
                # Replace the section
                before = content[:section_start]
                after = content[section_end:]
                content = before + new_logic + after
                
                # Write back
                with open(agent_file, 'w') as f:
                    f.write(content)
                    
                print("✅ FIXED! Template directory structure updated!")
                print("\nTemplates will now be saved in correct directories:")
                print("   • /leasing/vacancies.html - for vacancy pages")
                print("   • /people/tenants.html - for tenant pages")
                print("   • /maintenance/ - for work orders")
                print("   • /accounting/ - for financial pages")
                print("   • /reports/ - for report pages")
            else:
                print("❌ Could not find section end")
        else:
            print("❌ Could not find section start")
    else:
        print("❌ Could not find save_template method")
else:
    print("❌ Template visibility not found - run inject_visibility.py first")
EOF

echo ""
echo "Now restart your agent to use the corrected directory structure!"
