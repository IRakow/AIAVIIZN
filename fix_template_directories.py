#!/usr/bin/env python3
"""
Fix template directory structure - ensure pages are saved in correct subdirectories
"""

import sys

# Read the agent file
agent_file = "/Users/ianrakow/Desktop/AIVIIZN/aiviizn_real_agent_with_ai_intelligence_updated.py"

with open(agent_file, 'r') as f:
    content = f.read()

# Enhanced save_template with proper directory categorization
new_save_template = '''    def save_template(self, url: str, html: str) -> str:
        """Save template to file with PROPER DIRECTORY STRUCTURE"""
        try:
            parsed = urlparse(url)
            path_parts = parsed.path.strip('/').split('/')
            
            # Determine proper directory based on URL/content type
            url_lower = url.lower()
            path_str = parsed.path.lower()
            
            # CATEGORY MAPPING - determine which directory the template belongs in
            if 'vacancies' in path_str or 'vacancy' in path_str:
                template_dir = self.templates_dir / 'leasing'
                filename = 'vacancies.html'
            elif 'tenant' in path_str or 'residents' in path_str:
                template_dir = self.templates_dir / 'people'
                filename = path_parts[-1] + '.html' if path_parts[-1] else 'tenants.html'
            elif 'owner' in path_str:
                template_dir = self.templates_dir / 'people'
                filename = 'owners.html'
            elif 'property' in path_str or 'properties' in path_str:
                if 'dashboard' in path_str:
                    template_dir = self.templates_dir
                    filename = 'property_dashboard.html'
                else:
                    template_dir = self.templates_dir / 'properties'
                    filename = path_parts[-1] + '.html' if path_parts[-1] else 'properties.html'
            elif 'maintenance' in path_str or 'work_order' in path_str:
                template_dir = self.templates_dir / 'maintenance'
                filename = path_parts[-1] + '.html' if path_parts[-1] else 'work_orders.html'
            elif 'accounting' in path_str or 'bank' in path_str or 'gl_account' in path_str or 'payable' in path_str:
                template_dir = self.templates_dir / 'accounting'
                filename = path_parts[-1] + '.html' if path_parts[-1] else 'accounting.html'
            elif 'report' in path_str or 'income_statement' in path_str or 'balance_sheet' in path_str or 'rent_roll' in path_str:
                if 'memorized' in path_str:
                    template_dir = self.templates_dir / 'memorized_reports'
                    # Extract report ID if present
                    import re
                    id_match = re.search(r'/(\d+)', parsed.path)
                    if id_match:
                        filename = f"{id_match.group(1)}.html"
                    else:
                        filename = path_parts[-1] + '.html' if path_parts[-1] else 'report.html'
                elif 'buffered' in path_str:
                    template_dir = self.templates_dir / 'buffered_reports'
                    filename = path_parts[-1] + '.html' if path_parts[-1] else 'report.html'
                else:
                    template_dir = self.templates_dir / 'reports'
                    filename = path_parts[-1] + '.html' if path_parts[-1] else 'report.html'
            elif 'lease' in path_str or 'rental' in path_str or 'application' in path_str:
                template_dir = self.templates_dir / 'leasing'
                if 'application' in path_str:
                    filename = 'rental_applications.html'
                else:
                    filename = path_parts[-1] + '.html' if path_parts[-1] else 'leases.html'
            elif 'auth' in path_str or 'login' in path_str or 'sign_in' in path_str:
                template_dir = self.templates_dir / 'auth'
                filename = 'login.html'
            elif 'user' in path_str or 'admin' in path_str:
                template_dir = self.templates_dir / 'admin'
                filename = path_parts[-1] + '.html' if path_parts[-1] else 'users.html'
            elif 'dashboard' in path_str:
                template_dir = self.templates_dir
                filename = 'dashboard.html'
            elif 'inbox' in path_str or 'message' in path_str:
                template_dir = self.templates_dir
                filename = 'inbox.html'
            elif 'stack' in path_str or 'marketplace' in path_str:
                template_dir = self.templates_dir / 'marketplace'
                filename = path_parts[-1] + '.html' if path_parts[-1] else 'stack.html'
            elif 'communication' in path_str or 'letter' in path_str or 'phone' in path_str:
                template_dir = self.templates_dir / 'communication'
                filename = path_parts[-1] + '.html' if path_parts[-1] else 'communications.html'
            elif 'search' in path_str:
                template_dir = self.templates_dir / 'search'
                filename = 'advanced_search.html'
            elif 'calendar' in path_str:
                template_dir = self.templates_dir
                filename = 'calendar.html'
            elif 'metric' in path_str:
                template_dir = self.templates_dir
                filename = 'metrics.html'
            elif 'payment' in path_str:
                template_dir = self.templates_dir
                filename = 'online_payments.html'
            elif 'listing' in path_str or 'renewal' in path_str or 'signal' in path_str:
                template_dir = self.templates_dir / 'leasing'
                filename = path_parts[-1] + '.html' if path_parts[-1] else 'listings.html'
            elif 'vendor' in path_str:
                template_dir = self.templates_dir / 'people'
                filename = 'vendors.html'
            elif 'inspection' in path_str:
                template_dir = self.templates_dir / 'maintenance'
                filename = 'inspections.html'
            elif 'inventory' in path_str:
                template_dir = self.templates_dir / 'maintenance'
                filename = 'inventory.html'
            elif 'purchase_order' in path_str:
                template_dir = self.templates_dir / 'maintenance'
                filename = 'purchase_orders.html'
            elif 'project' in path_str:
                template_dir = self.templates_dir / 'maintenance'
                filename = 'projects.html'
            elif 'unit_turn' in path_str:
                template_dir = self.templates_dir / 'maintenance'
                filename = 'unit_turns.html'
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
            
            # SHOW WHAT'S BEING CREATED RIGHT NOW
            print(f"\\n{'='*60}")
            print(f"🎯 CREATING TEMPLATE RIGHT NOW:")
            print(f"📂 DIRECTORY: {template_dir}")
            print(f"📄 FILENAME: {filename}")
            print(f"🔗 FULL PATH: {template_path}")
            print(f"💾 SIZE: {len(html):,} bytes")
            print(f"🌐 FROM URL: {url}")
            print(f"{'='*60}\\n")
            
            with open(template_path, 'w', encoding='utf-8') as f:
                f.write(html)
            
            return str(template_path)
            
        except Exception as e:
            print(f"❌ ERROR SAVING: {e}")
            import traceback
            print(traceback.format_exc())
            return ""'''

# Find and replace the save_template method
import re

# Pattern to find the save_template method
pattern = r'(    def save_template\(self.*?\n(?:.*?\n)*?            return .*?\n)'
match = re.search(pattern, content)

if match:
    # Replace with new version
    content = content[:match.start()] + new_save_template + content[match.end():]
    
    # Write back
    with open(agent_file, 'w') as f:
        f.write(content)
    
    print("✅ FIXED! Template directory structure now properly organized:")
    print("\n📁 Templates will now be saved in correct directories:")
    print("   • /leasing/ - vacancies, rentals, applications, listings, renewals")
    print("   • /people/ - tenants, owners, vendors")
    print("   • /properties/ - property listings and details")
    print("   • /maintenance/ - work orders, inspections, inventory, projects")
    print("   • /accounting/ - bank accounts, GL accounts, payables")
    print("   • /reports/ - various reports")
    print("   • /memorized_reports/ - saved report configurations")
    print("   • /admin/ - user and system settings")
    print("   • /auth/ - login and authentication pages")
    print("\n🎯 Example: /vacancies will now save to /templates/leasing/vacancies.html")
else:
    print("❌ Could not find save_template method to patch")
