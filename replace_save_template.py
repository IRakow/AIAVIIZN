#!/usr/bin/env python3
"""
Direct replacement of save_template method with proper directory structure
"""

import re

# Read the agent file
agent_file = "/Users/ianrakow/Desktop/AIVIIZN/aiviizn_real_agent_with_ai_intelligence_updated.py"

with open(agent_file, 'r') as f:
    content = f.read()

# Complete save_template method with proper categorization
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
                filename = 'tenants.html' if 'tenant' in path_str else 'residents.html'
            elif 'rental' in path_str and 'application' in path_str:
                template_dir = self.templates_dir / 'leasing'
                filename = 'rental_applications.html'
            elif 'lease' in path_str and 'leasing' not in path_str:
                template_dir = self.templates_dir / 'leasing'
                filename = 'leases.html'
            elif 'listing' in path_str:
                template_dir = self.templates_dir / 'leasing'
                filename = 'listings.html'
            elif 'renewal' in path_str:
                template_dir = self.templates_dir / 'leasing'
                filename = 'renewals.html'
            elif 'property' in path_str and 'dashboard' in path_str:
                template_dir = self.templates_dir
                filename = 'property_dashboard.html'
            elif 'properties' in path_str:
                template_dir = self.templates_dir / 'properties'
                filename = 'properties.html'
            elif 'rent_roll' in path_str:
                template_dir = self.templates_dir
                filename = 'rent_roll.html'
            elif 'income_statement' in path_str:
                template_dir = self.templates_dir
                filename = 'income_statement.html'
            elif 'delinquency' in path_str:
                template_dir = self.templates_dir
                filename = 'delinquency_report.html'
            elif 'balance' in path_str and 'sheet' in path_str:
                template_dir = self.templates_dir
                filename = 'balance_sheet.html'
            elif 'maintenance' in path_str or 'work_order' in path_str:
                template_dir = self.templates_dir / 'maintenance'
                if 'work_order' in path_str:
                    filename = 'work_orders.html'
                else:
                    filename = path_parts[-1] + '.html' if path_parts[-1] else 'maintenance.html'
            elif 'inspection' in path_str:
                template_dir = self.templates_dir / 'maintenance'
                filename = 'inspections.html'
            elif 'unit_turn' in path_str:
                template_dir = self.templates_dir / 'maintenance'
                filename = 'unit_turns.html'
            elif 'accounting' in path_str or 'bank' in path_str or 'gl_account' in path_str:
                template_dir = self.templates_dir / 'accounting'
                if 'bank' in path_str:
                    filename = 'bank_accounts.html'
                elif 'gl' in path_str:
                    filename = 'gl_accounts.html'
                else:
                    filename = path_parts[-1] + '.html' if path_parts[-1] else 'accounting.html'
            elif 'payable' in path_str:
                template_dir = self.templates_dir / 'accounting'
                filename = 'payables.html'
            elif 'receivable' in path_str:
                template_dir = self.templates_dir / 'accounting'
                filename = 'receivables.html'
            elif 'memorized_reports' in path_str:
                template_dir = self.templates_dir / 'memorized_reports'
                # Extract report ID if present
                id_match = re.search(r'/(\\d+)', parsed.path)
                if id_match:
                    filename = f"{id_match.group(1)}.html"
                else:
                    filename = path_parts[-1] + '.html' if path_parts[-1] else 'report.html'
            elif 'buffered_reports' in path_str:
                template_dir = self.templates_dir / 'buffered_reports'
                filename = path_parts[-1] + '.html' if path_parts[-1] else 'report.html'
            elif 'report' in path_str:
                template_dir = self.templates_dir / 'reports'
                filename = path_parts[-1] + '.html' if path_parts[-1] else 'report.html'
            elif 'owner' in path_str:
                template_dir = self.templates_dir / 'people'
                filename = 'owners.html'
            elif 'vendor' in path_str:
                template_dir = self.templates_dir / 'people'
                filename = 'vendors.html'
            elif 'auth' in path_str or 'login' in path_str or 'sign_in' in path_str:
                template_dir = self.templates_dir / 'auth'
                filename = 'login.html'
            elif 'user' in path_str and 'admin' not in path_str:
                template_dir = self.templates_dir / 'users'
                filename = 'sign_in.html'
            elif 'admin' in path_str:
                template_dir = self.templates_dir / 'admin'
                filename = path_parts[-1] + '.html' if path_parts[-1] else 'admin.html'
            elif 'dashboard' in path_str:
                template_dir = self.templates_dir
                filename = 'dashboard.html'
            elif 'calendar' in path_str:
                template_dir = self.templates_dir
                filename = 'calendar.html'
            elif 'inbox' in path_str:
                template_dir = self.templates_dir
                filename = 'inbox.html'
            elif 'payment' in path_str:
                template_dir = self.templates_dir
                filename = 'online_payments.html'
            elif 'metric' in path_str:
                template_dir = self.templates_dir / 'leasing'
                filename = 'metrics.html'
            elif 'communication' in path_str or 'letter' in path_str:
                template_dir = self.templates_dir / 'communication'
                filename = 'letters.html'
            elif 'phone' in path_str and 'log' in path_str:
                template_dir = self.templates_dir / 'communication'
                filename = 'phone_logs.html'
            elif 'search' in path_str:
                template_dir = self.templates_dir / 'search'
                filename = 'advanced_search.html'
            elif 'stack' in path_str or 'marketplace' in path_str:
                template_dir = self.templates_dir / 'marketplace'
                filename = 'stack_marketplace.html'
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

# Find the save_template method
pattern = r'(    def save_template\(self, url: str, html: str\) -> str:.*?)(?=\n    def |\n\nclass |\Z)'
match = re.search(pattern, content, re.DOTALL)

if match:
    # Replace the entire method
    content = content[:match.start()] + new_save_template + '\n' + content[match.end():]
    
    # Write back
    with open(agent_file, 'w') as f:
        f.write(content)
    
    print("✅ SUCCESS! save_template method completely replaced!")
    print("\n📁 Directory mappings now active:")
    print("   • /vacancies → /templates/leasing/vacancies.html ✓")
    print("   • /tenants → /templates/people/tenants.html")
    print("   • /work_orders → /templates/maintenance/work_orders.html")
    print("   • /bank_accounts → /templates/accounting/bank_accounts.html")
    print("   • /rental_applications → /templates/leasing/rental_applications.html")
    print("   • /properties → /templates/properties/properties.html")
    print("   • /memorized_reports/123 → /templates/memorized_reports/123.html")
    print("   • /reports/* → /templates/reports/*.html")
    print("\n🎯 The agent will now organize templates properly!")
else:
    print("❌ Could not find save_template method")
    print("Searching for alternative pattern...")
    
    # Try a simpler search
    if 'def save_template' in content:
        print("✓ Method exists but couldn't match pattern")
        print("Manual intervention may be needed")
    else:
        print("❌ save_template method not found in file")
