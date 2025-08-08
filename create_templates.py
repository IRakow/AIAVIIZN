#!/usr/bin/env python3
"""
Create ALL missing template files for the Property Management System
"""

import os

templates = {
    'work_orders.html': '''{% extends "base.html" %}
{% block title %}Work Orders{% endblock %}
{% block content %}
<h2>Work Orders</h2>
<div class="data-table">
    <table>
        <thead>
            <tr>
                <th>Property</th>
                <th>Unit</th>
                <th>Tenant</th>
                <th>Issue</th>
                <th>Priority</th>
                <th>Status</th>
                <th>Date</th>
            </tr>
        </thead>
        <tbody>
            {% for order in work_orders %}
            <tr>
                <td>{{ order.property }}</td>
                <td>{{ order.unit }}</td>
                <td>{{ order.tenant }}</td>
                <td>{{ order.issue }}</td>
                <td>{{ order.priority }}</td>
                <td>{{ order.status }}</td>
                <td>{{ order.created_date }}</td>
            </tr>
            {% else %}
            <tr><td colspan="7" style="text-align: center;">No work orders found</td></tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% endblock %}''',

    'recurring_work_orders.html': '''{% extends "base.html" %}
{% block title %}Recurring Work Orders{% endblock %}
{% block content %}
<h2>Recurring Work Orders</h2>
<div class="data-table">
    <table>
        <thead>
            <tr>
                <th>Description</th>
                <th>Frequency</th>
                <th>Properties</th>
                <th>Next Due</th>
            </tr>
        </thead>
        <tbody>
            {% for order in recurring_orders %}
            <tr>
                <td>{{ order.description }}</td>
                <td>{{ order.frequency }}</td>
                <td>{{ order.properties }}</td>
                <td>{{ order.next_due }}</td>
            </tr>
            {% else %}
            <tr><td colspan="4" style="text-align: center;">No recurring work orders found</td></tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% endblock %}''',

    'inspections.html': '''{% extends "base.html" %}
{% block title %}Inspections{% endblock %}
{% block content %}
<h2>Inspections</h2>
<div class="data-table">
    <table>
        <thead>
            <tr>
                <th>Property</th>
                <th>Unit</th>
                <th>Type</th>
                <th>Scheduled Date</th>
                <th>Inspector</th>
                <th>Status</th>
            </tr>
        </thead>
        <tbody>
            {% for inspection in inspections %}
            <tr>
                <td>{{ inspection.property }}</td>
                <td>{{ inspection.unit }}</td>
                <td>{{ inspection.type }}</td>
                <td>{{ inspection.scheduled_date }}</td>
                <td>{{ inspection.inspector }}</td>
                <td>{{ inspection.status }}</td>
            </tr>
            {% else %}
            <tr><td colspan="6" style="text-align: center;">No inspections scheduled</td></tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% endblock %}''',

    'listings.html': '''{% extends "base.html" %}
{% block title %}Listings{% endblock %}
{% block content %}
<h2>Property Listings</h2>
<div class="data-table">
    <table>
        <thead>
            <tr>
                <th>Property</th>
                <th>Unit</th>
                <th>Rent</th>
                <th>Available Date</th>
                <th>Listed On</th>
                <th>Status</th>
            </tr>
        </thead>
        <tbody>
            {% for listing in listings %}
            <tr>
                <td>{{ listing.property }}</td>
                <td>{{ listing.unit }}</td>
                <td>${{ listing.rent }}</td>
                <td>{{ listing.available_date }}</td>
                <td>{{ listing.listed_on|join(', ') }}</td>
                <td>{{ listing.status }}</td>
            </tr>
            {% else %}
            <tr><td colspan="6" style="text-align: center;">No active listings</td></tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% endblock %}''',

    'showings.html': '''{% extends "base.html" %}
{% block title %}Showings{% endblock %}
{% block content %}
<h2>Property Showings</h2>
<div class="data-table">
    <table>
        <thead>
            <tr>
                <th>Property</th>
                <th>Unit</th>
                <th>Prospect</th>
                <th>Date</th>
                <th>Time</th>
                <th>Agent</th>
                <th>Status</th>
            </tr>
        </thead>
        <tbody>
            {% for showing in showings %}
            <tr>
                <td>{{ showing.property }}</td>
                <td>{{ showing.unit }}</td>
                <td>{{ showing.prospect }}</td>
                <td>{{ showing.date }}</td>
                <td>{{ showing.time }}</td>
                <td>{{ showing.agent }}</td>
                <td>{{ showing.status }}</td>
            </tr>
            {% else %}
            <tr><td colspan="7" style="text-align: center;">No showings scheduled</td></tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% endblock %}''',

    'emails.html': '''{% extends "base.html" %}
{% block title %}Emails{% endblock %}
{% block content %}
<h2>Email Communications</h2>
<div class="data-table">
    <table>
        <thead>
            <tr>
                <th>To</th>
                <th>Subject</th>
                <th>Date</th>
                <th>Status</th>
            </tr>
        </thead>
        <tbody>
            {% for email in emails %}
            <tr>
                <td>{{ email.to }}</td>
                <td>{{ email.subject }}</td>
                <td>{{ email.date }}</td>
                <td>{{ email.status }}</td>
            </tr>
            {% else %}
            <tr><td colspan="4" style="text-align: center;">No emails found</td></tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% endblock %}''',

    'letters.html': '''{% extends "base.html" %}
{% block title %}Letters{% endblock %}
{% block content %}
<h2>Letters</h2>
<div class="data-table">
    <table>
        <thead>
            <tr>
                <th>Recipient</th>
                <th>Type</th>
                <th>Property</th>
                <th>Unit</th>
                <th>Date</th>
                <th>Status</th>
            </tr>
        </thead>
        <tbody>
            {% for letter in letters %}
            <tr>
                <td>{{ letter.recipient }}</td>
                <td>{{ letter.type }}</td>
                <td>{{ letter.property }}</td>
                <td>{{ letter.unit }}</td>
                <td>{{ letter.date }}</td>
                <td>{{ letter.status }}</td>
            </tr>
            {% else %}
            <tr><td colspan="6" style="text-align: center;">No letters found</td></tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% endblock %}''',

    'phone_logs.html': '''{% extends "base.html" %}
{% block title %}Phone Logs{% endblock %}
{% block content %}
<h2>Phone Logs</h2>
<div class="data-table">
    <table>
        <thead>
            <tr>
                <th>Contact</th>
                <th>Phone</th>
                <th>Type</th>
                <th>Duration</th>
                <th>Notes</th>
                <th>Date</th>
            </tr>
        </thead>
        <tbody>
            {% for log in phone_logs %}
            <tr>
                <td>{{ log.contact }}</td>
                <td>{{ log.phone }}</td>
                <td>{{ log.type }}</td>
                <td>{{ log.duration }}</td>
                <td>{{ log.notes }}</td>
                <td>{{ log.date }}</td>
            </tr>
            {% else %}
            <tr><td colspan="6" style="text-align: center;">No phone logs found</td></tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% endblock %}''',

    'rent_roll.html': '''{% extends "base.html" %}
{% block title %}Rent Roll{% endblock %}
{% block content %}
<h2>Rent Roll Report</h2>
<div class="data-table">
    <table>
        <thead>
            <tr>
                <th>Property</th>
                <th>Unit</th>
                <th>Tenant</th>
                <th>Rent</th>
                <th>Balance</th>
                <th>Next Due</th>
            </tr>
        </thead>
        <tbody>
            {% for item in rent_roll %}
            <tr>
                <td>{{ item.property }}</td>
                <td>{{ item.unit }}</td>
                <td>{{ item.tenant }}</td>
                <td>${{ item.rent }}</td>
                <td>${{ item.balance }}</td>
                <td>{{ item.next_due }}</td>
            </tr>
            {% else %}
            <tr><td colspan="6" style="text-align: center;">No data available</td></tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% endblock %}''',

    'financial_reports.html': '''{% extends "base.html" %}
{% block title %}Financial Reports{% endblock %}
{% block content %}
<h2>Financial Reports</h2>
<div style="padding: 40px; text-align: center;">
    <h3>Available Reports</h3>
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-top: 20px;">
        <button class="btn-primary" style="padding: 20px;">Income Statement</button>
        <button class="btn-primary" style="padding: 20px;">Balance Sheet</button>
        <button class="btn-primary" style="padding: 20px;">Cash Flow</button>
        <button class="btn-primary" style="padding: 20px;">P&L Report</button>
    </div>
</div>
{% endblock %}''',

    'vacancy_reports.html': '''{% extends "base.html" %}
{% block title %}Vacancy Reports{% endblock %}
{% block content %}
<h2>Vacancy Reports</h2>
<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0;">
    <div style="background: white; padding: 20px; border-radius: 8px; text-align: center;">
        <h3>Total Units</h3>
        <p style="font-size: 32px; font-weight: bold;">{{ vacancy_data.total_units }}</p>
    </div>
    <div style="background: white; padding: 20px; border-radius: 8px; text-align: center;">
        <h3>Vacant Units</h3>
        <p style="font-size: 32px; font-weight: bold; color: #dc3545;">{{ vacancy_data.vacant_units }}</p>
    </div>
    <div style="background: white; padding: 20px; border-radius: 8px; text-align: center;">
        <h3>Vacancy Rate</h3>
        <p style="font-size: 32px; font-weight: bold;">{{ vacancy_data.vacancy_rate }}%</p>
    </div>
    <div style="background: white; padding: 20px; border-radius: 8px; text-align: center;">
        <h3>Avg Days Vacant</h3>
        <p style="font-size: 32px; font-weight: bold;">{{ vacancy_data.avg_days_vacant }}</p>
    </div>
</div>
{% endblock %}''',

    'company_settings.html': '''{% extends "base.html" %}
{% block title %}Company Settings{% endblock %}
{% block content %}
<h2>Company Settings</h2>
<div style="background: white; padding: 20px; border-radius: 8px;">
    <form>
        <div style="margin-bottom: 15px;">
            <label>Company Name:</label><br>
            <input type="text" value="{{ settings.company_name }}" style="width: 100%; padding: 8px;">
        </div>
        <div style="margin-bottom: 15px;">
            <label>Address:</label><br>
            <input type="text" value="{{ settings.address }}" style="width: 100%; padding: 8px;">
        </div>
        <div style="margin-bottom: 15px;">
            <label>Phone:</label><br>
            <input type="text" value="{{ settings.phone }}" style="width: 100%; padding: 8px;">
        </div>
        <div style="margin-bottom: 15px;">
            <label>Email:</label><br>
            <input type="email" value="{{ settings.email }}" style="width: 100%; padding: 8px;">
        </div>
        <button type="submit" class="btn-primary">Save Settings</button>
    </form>
</div>
{% endblock %}''',

    'users.html': '''{% extends "base.html" %}
{% block title %}Users{% endblock %}
{% block content %}
<h2>User Management</h2>
<div class="data-table">
    <table>
        <thead>
            <tr>
                <th>Name</th>
                <th>Email</th>
                <th>Role</th>
                <th>Status</th>
                <th>Actions</th>
            </tr>
        </thead>
        <tbody>
            {% for user in users %}
            <tr>
                <td>{{ user.name }}</td>
                <td>{{ user.email }}</td>
                <td>{{ user.role }}</td>
                <td>{{ user.status }}</td>
                <td>
                    <button class="btn-sm btn-primary">Edit</button>
                    <button class="btn-sm btn-danger">Delete</button>
                </td>
            </tr>
            {% else %}
            <tr><td colspan="5" style="text-align: center;">No users found</td></tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% endblock %}''',

    'document_templates.html': '''{% extends "base.html" %}
{% block title %}Document Templates{% endblock %}
{% block content %}
<h2>Document Templates</h2>
<div class="data-table">
    <table>
        <thead>
            <tr>
                <th>Name</th>
                <th>Type</th>
                <th>Last Modified</th>
                <th>Actions</th>
            </tr>
        </thead>
        <tbody>
            {% for template in templates %}
            <tr>
                <td>{{ template.name }}</td>
                <td>{{ template.type }}</td>
                <td>{{ template.last_modified }}</td>
                <td>
                    <button class="btn-sm btn-primary">Edit</button>
                    <button class="btn-sm btn-info">Preview</button>
                    <button class="btn-sm btn-danger">Delete</button>
                </td>
            </tr>
            {% else %}
            <tr><td colspan="4" style="text-align: center;">No templates found</td></tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% endblock %}'''
}

def create_all_templates():
    """Create all missing template files"""
    os.makedirs('templates', exist_ok=True)
    
    created = []
    skipped = []
    
    for filename, content in templates.items():
        filepath = os.path.join('templates', filename)
        if not os.path.exists(filepath):
            with open(filepath, 'w') as f:
                f.write(content)
            created.append(filename)
            print(f"✅ Created {filename}")
        else:
            skipped.append(filename)
            print(f"ℹ️ {filename} already exists")
    
    print(f"\n✅ Created {len(created)} new templates")
    print(f"ℹ️ Skipped {len(skipped)} existing templates")
    print("\n🎉 All templates are ready!")

if __name__ == '__main__':
    create_all_templates()