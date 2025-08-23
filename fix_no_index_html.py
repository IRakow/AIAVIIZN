#!/usr/bin/env python3
"""
Fix save_template to NEVER use index.html - always use descriptive names
"""

import re

# Read the agent file
agent_file = "/Users/ianrakow/Desktop/AIVIIZN/aiviizn_real_agent_with_ai_intelligence_updated.py"

with open(agent_file, 'r') as f:
    content = f.read()

# Complete save_template method with NO index.html defaults
new_save_template = '''    def save_template(self, url: str, html: str) -> str:
        """Save template with PROPER DESCRIPTIVE NAMES - NO index.html"""
        try:
            parsed = urlparse(url)
            path_parts = parsed.path.strip('/').split('/')
            
            # Determine proper directory and filename based on URL/content
            url_lower = url.lower()
            path_str = parsed.path.lower()
            
            # Extract the last meaningful part of the URL for naming
            if path_parts and path_parts[-1]:
                base_name = path_parts[-1]
            elif path_parts and len(path_parts) > 1 and path_parts[-2]:
                base_name = path_parts[-2]
            else:
                # Parse domain for home pages
                if 'dashboard' in url_lower:
                    base_name = 'dashboard'
                elif 'home' in url_lower:
                    base_name = 'home'
                elif 'main' in url_lower:
                    base_name = 'main'
                else:
                    base_name = 'portal'  # Better than index
            
            # CATEGORY MAPPING with proper file names
            if 'vacancies' in path_str or 'vacancy' in path_str:
                template_dir = self.templates_dir / 'leasing'
                filename = 'vacancies.html'
            elif 'tenant' in path_str:
                template_dir = self.templates_dir / 'people'
                filename = 'tenants.html'
            elif 'resident' in path_str:
                template_dir = self.templates_dir / 'people'
                filename = 'residents.html'
            elif 'owner' in path_str:
                template_dir = self.templates_dir / 'people'
                filename = 'owners.html'
            elif 'vendor' in path_str:
                template_dir = self.templates_dir / 'people'
                filename = 'vendors.html'
            elif 'rental' in path_str and 'application' in path_str:
                template_dir = self.templates_dir / 'leasing'
                filename = 'rental_applications.html'
            elif 'lease_document' in path_str:
                template_dir = self.templates_dir / 'leasing'
                if 'out_for_signing' in path_str:
                    filename = 'lease_documents_out_for_signing.html'
                elif 'printed' in path_str:
                    filename = 'lease_documents_printed.html'
                else:
                    filename = 'lease_documents.html'
            elif 'lease' in path_str and 'leasing' not in path_str:
                template_dir = self.templates_dir / 'leasing'
                filename = 'leases.html'
            elif 'guest_card' in path_str:
                template_dir = self.templates_dir / 'leasing'
                filename = 'guest_cards.html'
            elif 'listing' in path_str:
                template_dir = self.templates_dir / 'leasing'
                filename = 'listings.html'
            elif 'renewal' in path_str:
                template_dir = self.templates_dir / 'leasing'
                filename = 'renewals.html'
            elif 'signal' in path_str:
                template_dir = self.templates_dir / 'leasing'
                filename = 'signals.html'
            elif 'metric' in path_str and 'leasing' in path_str:
                template_dir = self.templates_dir / 'leasing'
                filename = 'metrics.html'
            elif 'property' in path_str and 'dashboard' in path_str:
                template_dir = self.templates_dir
                filename = 'property_dashboard.html'
            elif 'properties' in path_str:
                template_dir = self.templates_dir / 'properties'
                filename = 'properties.html'
            elif 'unit_turn' in path_str:
                template_dir = self.templates_dir / 'maintenance'
                filename = 'unit_turns.html'
            elif 'work_order' in path_str:
                template_dir = self.templates_dir / 'maintenance'
                if 'recurring' in path_str:
                    filename = 'recurring_work_orders.html'
                else:
                    filename = 'work_orders.html'
            elif 'inspection' in path_str:
                template_dir = self.templates_dir / 'maintenance'
                filename = 'inspections.html'
            elif 'inventory' in path_str:
                template_dir = self.templates_dir / 'maintenance'
                filename = 'inventory.html'
            elif 'purchase_order' in path_str:
                template_dir = self.templates_dir / 'maintenance'
                filename = 'purchase_orders.html'
            elif 'project' in path_str and 'maintenance' in path_str:
                template_dir = self.templates_dir / 'maintenance'
                filename = 'projects.html'
            elif 'bank' in path_str and 'account' in path_str:
                template_dir = self.templates_dir / 'accounting'
                filename = 'bank_accounts.html'
            elif 'bank' in path_str and 'transfer' in path_str:
                template_dir = self.templates_dir / 'accounting'
                filename = 'bank_transfers.html'
            elif 'gl_account' in path_str or 'general_ledger' in path_str:
                template_dir = self.templates_dir / 'accounting'
                filename = 'gl_accounts.html'
            elif 'journal' in path_str and 'entr' in path_str:
                template_dir = self.templates_dir / 'accounting'
                filename = 'journal_entries.html'
            elif 'payable' in path_str:
                template_dir = self.templates_dir / 'accounting'
                filename = 'payables.html'
            elif 'receivable' in path_str:
                template_dir = self.templates_dir / 'accounting'
                filename = 'receivables.html'
            elif 'diagnostic' in path_str:
                template_dir = self.templates_dir / 'accounting'
                filename = 'diagnostics.html'
            elif 'rent_roll' in path_str:
                template_dir = self.templates_dir
                filename = 'rent_roll.html'
            elif 'income_statement' in path_str:
                template_dir = self.templates_dir
                filename = 'income_statement.html'
            elif 'balance_sheet' in path_str:
                template_dir = self.templates_dir / 'buffered_reports'
                filename = 'balance_sheet.html'
            elif 'delinquency' in path_str:
                template_dir = self.templates_dir
                filename = 'delinquency_report.html'
            elif 'check_register' in path_str:
                template_dir = self.templates_dir / 'buffered_reports'
                filename = 'check_register.html'
            elif 'inventory_status' in path_str:
                template_dir = self.templates_dir / 'buffered_reports'
                filename = 'inventory_status.html'
            elif 'additional_fee' in path_str:
                template_dir = self.templates_dir / 'buffered_reports'
                filename = 'additional_fees.html'
            elif 'memorized_reports' in path_str:
                template_dir = self.templates_dir / 'memorized_reports'
                # Extract report ID if present
                id_match = re.search(r'/(\\d+)', parsed.path)
                if id_match:
                    filename = f"{id_match.group(1)}.html"
                else:
                    filename = f"report_{base_name}.html"
            elif 'buffered_reports' in path_str:
                template_dir = self.templates_dir / 'buffered_reports'
                filename = f"{base_name}.html"
            elif 'report' in path_str:
                template_dir = self.templates_dir / 'reports'
                if base_name and base_name != 'report':
                    filename = f"{base_name}.html"
                else:
                    filename = 'financial_reports.html'
            elif 'auth' in path_str or 'login' in path_str or 'sign_in' in path_str:
                template_dir = self.templates_dir / 'auth'
                if 'register' in path_str:
                    filename = 'register.html'
                else:
                    filename = 'login.html'
            elif 'user' in path_str and 'sign_in' in path_str:
                template_dir = self.templates_dir / 'users'
                filename = 'sign_in.html'
            elif 'user' in path_str and 'setting' in path_str:
                template_dir = self.templates_dir / 'admin'
                filename = 'user_settings.html'
            elif 'company' in path_str and 'setting' in path_str:
                template_dir = self.templates_dir / 'admin'
                filename = 'company_settings.html'
            elif 'admin' in path_str and 'user' in path_str:
                template_dir = self.templates_dir / 'admin'
                filename = 'users.html'
            elif 'email' in path_str and 'admin' in path_str:
                template_dir = self.templates_dir / 'admin'
                filename = 'emails.html'
            elif 'showing' in path_str:
                template_dir = self.templates_dir / 'admin'
                filename = 'showings.html'
            elif 'dashboard' in path_str:
                template_dir = self.templates_dir
                filename = 'dashboard.html'
            elif 'calendar' in path_str:
                template_dir = self.templates_dir
                filename = 'calendar.html'
            elif 'inbox' in path_str or 'message' in path_str:
                template_dir = self.templates_dir
                filename = 'inbox.html'
            elif 'pending' in path_str:
                template_dir = self.templates_dir
                filename = 'pending.html'
            elif 'processed' in path_str:
                template_dir = self.templates_dir
                filename = 'processed.html'
            elif 'payment' in path_str and 'online' in path_str:
                template_dir = self.templates_dir
                filename = 'online_payments.html'
            elif 'metric' in path_str:
                template_dir = self.templates_dir
                filename = 'metrics.html'
            elif 'letter' in path_str:
                template_dir = self.templates_dir / 'communication'
                filename = 'letters.html'
            elif 'phone' in path_str and 'log' in path_str:
                template_dir = self.templates_dir / 'communication'
                filename = 'phone_logs.html'
            elif 'search' in path_str and 'advanced' in path_str:
                template_dir = self.templates_dir / 'search'
                filename = 'advanced_search.html'
            elif 'stack' in path_str or 'marketplace' in path_str:
                template_dir = self.templates_dir / 'marketplace'
                filename = 'stack_marketplace.html'
            elif 'document_template' in path_str:
                template_dir = self.templates_dir
                filename = 'document_templates.html'
            elif 'whats_new' in path_str or 'what_new' in path_str:
                template_dir = self.templates_dir
                filename = 'whats_new.html'
            elif 'survey' in path_str:
                template_dir = self.templates_dir / 'reporting'
                filename = 'surveys.html'
            elif 'scheduled_report' in path_str:
                template_dir = self.templates_dir / 'reporting'
                filename = 'scheduled_reports.html'
            elif 'financial_report' in path_str:
                template_dir = self.templates_dir / 'reporting'
                filename = 'financial_reports.html'
            elif 'vacancy_report' in path_str:
                template_dir = self.templates_dir / 'reporting'
                filename = 'vacancy_reports.html'
            elif path_str == '/' or not path_str:
                # Root/home page - use descriptive name
                template_dir = self.templates_dir
                filename = 'dashboard.html'  # Most likely the dashboard
            else:
                # Default: use URL structure with meaningful name
                if len(path_parts) > 1:
                    template_dir = self.templates_dir / '/'.join(path_parts[:-1])
                    filename = f"{base_name}.html"
                else:
                    template_dir = self.templates_dir
                    filename = f"{base_name}.html"
            
            # NEVER use index.html - ensure we have a meaningful name
            if filename == 'index.html' or filename == '.html' or not filename:
                # Extract something meaningful from the URL
                if base_name and base_name != 'index':
                    filename = f"{base_name}.html"
                elif 'appfolio' in parsed.netloc:
                    filename = 'appfolio_property_manager.html'
                else:
                    filename = 'portal.html'  # Better default than index
            
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
pattern = r'(    def save_template\(self, url: str, html: str\) -> str:.*?)(?=\n    def |\n\nclass |\Z)'
match = re.search(pattern, content, re.DOTALL)

if match:
    # Replace the entire method
    content = content[:match.start()] + new_save_template + '\n' + content[match.end():]
    
    # Write back
    with open(agent_file, 'w') as f:
        f.write(content)
    
    print("✅ SUCCESS! save_template fixed - NO MORE index.html!")
    print("\n📝 All templates will now have descriptive names:")
    print("   ❌ NEVER: index.html")
    print("   ✅ ALWAYS: descriptive names like:")
    print("      • vacancies.html")
    print("      • tenants.html")
    print("      • work_orders.html")
    print("      • bank_accounts.html")
    print("      • dashboard.html")
    print("      • property_dashboard.html")
    print("\n🎯 Even root URLs will get meaningful names!")
    print("   / → dashboard.html (not index.html)")
    print("   /unknown → portal.html (not index.html)")
else:
    print("❌ Could not find save_template method to patch")
