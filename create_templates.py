# create_templates.py
"""
This script creates all the necessary template files for AVIIZN
Run this to generate all template files in the correct structure
"""

import os

# Define the base template content (simplified for all pages to extend)
BASE_TEMPLATE = """{% extends "base.html" %}

{% block title %}{{ title }} - AVIIZN{% endblock %}

{% block content %}
<div class="content-header">
    <h2>{{ title }}</h2>
</div>

<div class="content-body">
    <div class="search-container">
        <p>Click here to search</p>
    </div>
    
    <div class="data-table">
        <table class="table">
            <thead>
                <tr>
                    <th>Loading...</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>{{ title }} data will be displayed here</td>
                </tr>
            </tbody>
        </table>
    </div>
</div>
{% endblock %}

{% block contextsidebar %}
<h5><i class="fas fa-th"></i> {{ title }}</h5>
<div class="menu-item starred-item">Tasks</div>
<div class="menu-item">New {{ title }}</div>
<div class="menu-item">View All</div>
<div class="menu-item">Reports</div>
{% endblock %}
"""

# Define all templates that need to be created
templates = {
    # Main pages
    'dashboard.html': BASE_TEMPLATE.replace('{{ title }}', 'Dashboard'),
    'inbox.html': BASE_TEMPLATE.replace('{{ title }}', 'Inbox'),
    'calendar.html': BASE_TEMPLATE.replace('{{ title }}', 'Calendar'),
    'online_payments.html': BASE_TEMPLATE.replace('{{ title }}', 'Online Payments'),
    'whats_new.html': BASE_TEMPLATE.replace('{{ title }}', "What's New"),
    
    # People section
    'people/tenants.html': BASE_TEMPLATE.replace('{{ title }}', 'Tenants'),
    'people/owners.html': BASE_TEMPLATE.replace('{{ title }}', 'Owners'),
    
    # Properties section
    'properties/properties.html': BASE_TEMPLATE.replace('{{ title }}', 'Properties'),
    
    # Leasing section
    'leasing/vacancies.html': BASE_TEMPLATE.replace('{{ title }}', 'Vacancies'),
    'leasing/guest_cards.html': BASE_TEMPLATE.replace('{{ title }}', 'Guest Cards'),
    'leasing/rental_applications.html': BASE_TEMPLATE.replace('{{ title }}', 'Rental Applications'),
    'leasing/leases.html': BASE_TEMPLATE.replace('{{ title }}', 'Leases'),
    'leasing/renewals.html': BASE_TEMPLATE.replace('{{ title }}', 'Renewals'),
    'leasing/metrics.html': BASE_TEMPLATE.replace('{{ title }}', 'Leasing Metrics'),
    'leasing/signals.html': BASE_TEMPLATE.replace('{{ title }}', 'Signals'),
    
    # Maintenance section
    'maintenance/vendors.html': BASE_TEMPLATE.replace('{{ title }}', 'Vendors'),
    'maintenance/work_orders.html': BASE_TEMPLATE.replace('{{ title }}', 'Work Orders'),
    'maintenance/recurring_work_orders.html': BASE_TEMPLATE.replace('{{ title }}', 'Recurring Work Orders'),
    'maintenance/inspections.html': BASE_TEMPLATE.replace('{{ title }}', 'Inspections'),
    'maintenance/unit_turns.html': BASE_TEMPLATE.replace('{{ title }}', 'Unit Turns'),
    'maintenance/projects.html': BASE_TEMPLATE.replace('{{ title }}', 'Projects'),
    'maintenance/purchase_orders.html': BASE_TEMPLATE.replace('{{ title }}', 'Purchase Orders'),
    'maintenance/inventory.html': BASE_TEMPLATE.replace('{{ title }}', 'Inventory'),
    'maintenance/fixed_assets.html': BASE_TEMPLATE.replace('{{ title }}', 'Fixed Assets'),
    'maintenance/smart_maintenance.html': BASE_TEMPLATE.replace('{{ title }}', 'Smart Maintenance'),
    
    # Accounting section
    'accounting/receivables.html': BASE_TEMPLATE.replace('{{ title }}', 'Receivables'),
    'accounting/payables.html': BASE_TEMPLATE.replace('{{ title }}', 'Payables'),
    'accounting/bank_accounts.html': BASE_TEMPLATE.replace('{{ title }}', 'Bank Accounts'),
    'accounting/journal_entries.html': BASE_TEMPLATE.replace('{{ title }}', 'Journal Entries'),
    'accounting/bank_transfers.html': BASE_TEMPLATE.replace('{{ title }}', 'Bank Transfers'),
    'accounting/gl_accounts.html': BASE_TEMPLATE.replace('{{ title }}', 'GL Accounts'),
    'accounting/diagnostics.html': BASE_TEMPLATE.replace('{{ title }}', 'Financial Diagnostics'),
    'accounting/receipts.html': BASE_TEMPLATE.replace('{{ title }}', 'Receipts'),
    
    # Reporting section
    'reporting/reports.html': BASE_TEMPLATE.replace('{{ title }}', 'Reports'),
    'reporting/scheduled_reports.html': BASE_TEMPLATE.replace('{{ title }}', 'Scheduled Reports'),
    'reporting/metrics.html': BASE_TEMPLATE.replace('{{ title }}', 'Metrics'),
    'reporting/surveys.html': BASE_TEMPLATE.replace('{{ title }}', 'Surveys'),
    
    # Communication section
    'communication/letters.html': BASE_TEMPLATE.replace('{{ title }}', 'Letter Templates'),
    'communication/forms.html': BASE_TEMPLATE.replace('{{ title }}', 'Forms'),
}

def create_templates():
    """Create all template files in the correct directory structure"""
    
    base_dir = 'templates'
    
    # Create base directory if it doesn't exist
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
    
    # Create each template file
    for template_path, content in templates.items():
        full_path = os.path.join(base_dir, template_path)
        
        # Create directory if it doesn't exist
        directory = os.path.dirname(full_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        
        # Write the template file
        with open(full_path, 'w') as f:
            f.write(content)
        
        print(f"Created: {full_path}")
    
    print(f"\n✅ Created {len(templates)} template files")
    print("\nDirectory structure:")
    print("templates/")
    print("├── auth/")
    print("│   └── login.html")
    print("├── base.html")
    print("├── dashboard.html")
    print("├── inbox.html")
    print("├── calendar.html")
    print("├── online_payments.html")
    print("├── whats_new.html")
    print("├── people/")
    print("│   ├── tenants.html")
    print("│   └── owners.html")
    print("├── properties/")
    print("│   └── properties.html")
    print("├── leasing/")
    print("│   ├── vacancies.html")
    print("│   ├── guest_cards.html")
    print("│   ├── rental_applications.html")
    print("│   ├── leases.html")
    print("│   ├── renewals.html")
    print("│   ├── metrics.html")
    print("│   └── signals.html")
    print("├── maintenance/")
    print("│   ├── vendors.html")
    print("│   ├── work_orders.html")
    print("│   ├── recurring_work_orders.html")
    print("│   ├── inspections.html")
    print("│   ├── unit_turns.html")
    print("│   ├── projects.html")
    print("│   ├── purchase_orders.html")
    print("│   ├── inventory.html")
    print("│   ├── fixed_assets.html")
    print("│   └── smart_maintenance.html")
    print("├── accounting/")
    print("│   ├── receivables.html")
    print("│   ├── payables.html")
    print("│   ├── bank_accounts.html")
    print("│   ├── journal_entries.html")
    print("│   ├── bank_transfers.html")
    print("│   ├── gl_accounts.html")
    print("│   ├── diagnostics.html")
    print("│   └── receipts.html")
    print("├── reporting/")
    print("│   ├── reports.html")
    print("│   ├── scheduled_reports.html")
    print("│   ├── metrics.html")
    print("│   └── surveys.html")
    print("└── communication/")
    print("    ├── letters.html")
    print("    └── forms.html")

if __name__ == "__main__":
    create_templates()