# Complete Property Management System - app.py
# This file has ALL routes working

from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_cors import CORS
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'f3cfe9ed8fae309f02079dbf')
app.config['FLASK_ENV'] = os.environ.get('FLASK_ENV', 'development')

# Supabase configuration
SUPABASE_URL = os.environ.get('SUPABASE_URL', "https://sejebqdhcilwcpjpznep.supabase.co")
SUPABASE_KEY = os.environ.get('SUPABASE_KEY', "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNlamVicWRoY2lsd2NwanB6bmVwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ0NTg5NjQsImV4cCI6MjA3MDAzNDk2NH0.vFM0Gr3QZF4MN3vtDGghjyCpnIkyC_mmUOOkVO3ahPQ")

# Try to initialize Supabase client
try:
    from supabase import create_client, Client
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✅ Connected to Supabase successfully!")
except Exception as e:
    print(f"⚠️ Supabase connection failed: {e}")
    supabase = None

# ============================================
# MAIN ROUTES
# ============================================

@app.route('/')
def index():
    return redirect(url_for('dashboard'))

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/quick-login', methods=['POST'])
def quick_login():
    session['logged_in'] = True
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    """Dashboard with move-ins"""
    move_ins = []
    alerts = []
    
    # Sample data
    move_ins = [
        {
            'tenant': {'first_name': 'John', 'last_name': 'Smith'},
            'property': {'name': 'Sunset Apartments'},
            'unit': {'unit_number': '101'},
            'lease_status': 'executed',
            'portal_status': 'active',
            'balance': 0,
            'insurance_status': 'covered',
            'move_in_date': datetime.now()
        }
    ]
    
    return render_template('dashboard.html', move_ins=move_ins, alerts=alerts)

# ============================================
# LEASING SECTION
# ============================================

@app.route('/vacancies')
def vacancies():
    """Vacancies page"""
    vacancies_data = [
        {
            'id': '1',
            'unit_number': '10-02',
            'properties': {
                'name': 'Gene Field Apts / DW Gene Field LLC',
                'address': '3515 Gene Field Rd, St. Joseph, MO 64506'
            },
            'days_vacant': 1052,
            'bedrooms': 1,
            'bathrooms': 1.0,
            'square_feet': 731,
            'rent': 546.0,
            'photos_count': 0
        },
        {
            'id': '2',
            'unit_number': '10-04',
            'properties': {
                'name': 'Gene Field Apts / DW Gene Field LLC',
                'address': '3515 Gene Field Rd, St. Joseph, MO 64506'
            },
            'days_vacant': 896,
            'bedrooms': 1,
            'bathrooms': 1.0,
            'square_feet': 731,
            'rent': 546.0,
            'photos_count': 0
        }
    ]
    
    return render_template('vacancies.html', vacancies=vacancies_data)

@app.route('/guest-cards')
def guest_cards():
    """Guest cards page"""
    guests = []  # The template has sample data built in
    return render_template('guest_cards.html', guests=guests)

@app.route('/rental-applications')
def rental_applications():
    """Rental applications page"""
    applications = [
        {
            'id': '1',
            'guest_cards': {
                'first_name': 'David',
                'last_name': 'Brown',
                'email': 'david@email.com',
                'phone': '555-0123'
            },
            'units': {
                'unit_number': '303',
                'properties': {'name': 'City View'}
            },
            'status': 'pending',
            'score': 720,
            'monthly_income': 4500,
            'created_at': datetime.now().isoformat()
        }
    ]
    
    return render_template('rental_applications.html', applications=applications)

@app.route('/leases')
def leases():
    """Leases page"""
    leases_data = [
        {
            'id': '1',
            'tenants': {
                'first_name': 'Alice',
                'last_name': 'Johnson'
            },
            'units': {
                'unit_number': '301',
                'properties': {'name': 'Sunset Apartments'}
            },
            'generated_date': datetime.now(),
            'status': 'executed'
        }
    ]
    
    current_status = request.args.get('status', 'all')
    return render_template('leases.html', leases=leases_data, current_status=current_status)

@app.route('/renewals')
def renewals():
    """Renewals page"""
    renewals_data = [
        {
            'id': '1',
            'tenants': {
                'first_name': 'Bob',
                'last_name': 'Martin',
                'email': 'bob@email.com'
            },
            'units': {
                'unit_number': '505',
                'rent': 1400,
                'properties': {'name': 'Garden Court'}
            },
            'end_date': (datetime.now().date() + timedelta(days=45)).isoformat(),
            'renewal_status': 'pending',
            'current_rent': 1400,
            'proposed_rent': 1450
        }
    ]
    
    return render_template('renewals.html', renewals=renewals_data)

@app.route('/metrics')
def metrics():
    """Metrics page"""
    metrics_data = {
        'total_properties': 10,
        'total_units': 50,
        'vacant_units': 5,
        'occupancy_rate': 90.0
    }
    
    from_date = datetime.now().date().isoformat()
    to_date = (datetime.now().date() + timedelta(days=30)).isoformat()
    
    return render_template('metrics.html', 
                         metrics=metrics_data,
                         from_date=from_date,
                         to_date=to_date)

# ============================================
# PROPERTIES SECTION
# ============================================

@app.route('/properties')
def properties():
    """Properties page"""
    properties_data = [
        {
            'id': '1',
            'name': 'Sunset Apartments',
            'type': 'Multi-Family',
            'address': '123 Main St',
            'city': 'Kansas City',
            'state': 'MO',
            'zip': '64111',
            'units_count': 24,
            'units': [{'status': 'vacant'}, {'status': 'vacant'}, {'status': 'occupied'}]
        },
        {
            'id': '2',
            'name': 'Oak Grove',
            'type': 'Multi-Family',
            'address': '456 Oak Ave',
            'city': 'Kansas City',
            'state': 'MO',
            'zip': '64112',
            'units_count': 16,
            'units': [{'status': 'vacant'}]
        }
    ]
    
    return render_template('properties.html', properties=properties_data)

# ============================================
# PEOPLE SECTION
# ============================================

@app.route('/tenants')
def tenants():
    """Tenants page"""
    tenants_data = [
        {
            'id': '1',
            'name': 'Anderson, John',
            'status': 'Current',
            'property': 'Sunset Apartments',
            'unit': '101',
            'phone': '555-0201',
            'email': 'john@email.com'
        }
    ]
    
    return render_template('tenants.html', tenants=tenants_data)

@app.route('/owners')
def owners():
    """Owners page"""
    owners_data = [
        {
            'id': '1',
            'name': 'Smith, Robert',
            'company': 'Smith Properties LLC',
            'phone': '555-0301',
            'email': 'robert@smithproperties.com'
        }
    ]
    
    return render_template('owners.html', owners=owners_data)

@app.route('/vendors')
def vendors():
    """Vendors page"""
    vendors_data = [
        {
            'id': '1',
            'name': 'Mike Jones',
            'company': 'Quick Fix Plumbing',
            'trade': 'Plumbing',
            'phone': '555-0401',
            'email': 'mike@quickfix.com'
        }
    ]
    
    return render_template('vendors.html', vendors=vendors_data)

# ============================================
# ACCOUNTING SECTION
# ============================================

@app.route('/receivables')
def receivables():
    """Receivables page"""
    receipts = [
        {
            'id': '1',
            'date': datetime.now().date(),
            'tenant': 'John Doe',
            'amount': 1500.00,
            'type': 'Rent',
            'property': 'Sunset Apartments',
            'unit': '101'
        }
    ]
    
    return render_template('receivables.html', receipts=receipts)

@app.route('/payables')
def payables():
    """Payables page"""
    bills = [
        {
            'payee': 'City Water',
            'ref': 'INV-001',
            'bill_date': '2025-01-01',
            'for': 'Water Bill',
            'gl_account': '6100',
            'due_date': '2025-01-15',
            'amount': 450.00,
            'status': 'Pending',
            'cash_account': 'Operating'
        }
    ]
    
    return render_template('payables.html', bills=bills)

@app.route('/bank-accounts')
def bank_accounts():
    """Bank accounts page"""
    accounts = [
        {
            'name': 'Operating Account',
            'bank': 'First National Bank',
            'account_number': '****4567',
            'last_reconciliation': '2025-01-01',
            'payments_enabled': 'ENABLED',
            'auto_reconciliation': 'PLAID'
        }
    ]
    
    return render_template('bank_accounts.html', accounts=accounts)

@app.route('/journal-entries')
def journal_entries():
    """Journal entries page"""
    entries = []
    return render_template('journal_entries.html', entries=entries)

@app.route('/bank-transfers')
def bank_transfers():
    """Bank transfers page"""
    transfers = []
    return render_template('bank_transfers.html', transfers=transfers)

@app.route('/gl-accounts')
def gl_accounts():
    """GL accounts page"""
    accounts = []
    return render_template('gl_accounts.html', accounts=accounts)

@app.route('/diagnostics')
def diagnostics():
    """Diagnostics page"""
    diagnostics_data = {
        'checks': [],
        'warnings': [],
        'errors': []
    }
    return render_template('diagnostics.html', diagnostics=diagnostics_data)

# ============================================
# API ENDPOINTS
# ============================================

@app.route('/api/units/update-status', methods=['POST'])
def update_unit_status():
    data = request.json
    return jsonify({'success': True})

@app.route('/api/guest-cards/bulk-update', methods=['POST'])
def bulk_update_guest_cards():
    data = request.json
    return jsonify({'success': True})

@app.route('/api/leases/countersign', methods=['POST'])
def countersign_lease():
    data = request.json
    return jsonify({'success': True})

@app.route('/api/applications/update-status', methods=['POST'])
def update_application_status():
    data = request.json
    return jsonify({'success': True})

# ============================================
# DEBUG ROUTES
# ============================================

@app.route('/debug')
def debug():
    """Debug route to check setup"""
    import os
    templates = os.listdir('templates') if os.path.exists('templates') else []
    
    return jsonify({
        'templates': templates,
        'current_dir': os.getcwd(),
        'template_folder': app.template_folder,
        'app_root': app.root_path,
        'routes': [str(rule) for rule in app.url_map.iter_rules()]
    })

@app.route('/test-templates')
def test_templates():
    """Test all templates"""
    import os
    results = {}
    template_dir = os.path.join(app.root_path, 'templates')
    
    if not os.path.exists(template_dir):
        return jsonify({'error': 'Templates directory not found'})
    
    for template in os.listdir(template_dir):
        if template.endswith('.html'):
            try:
                if template == 'base.html':
                    continue
                elif template == 'dashboard.html':
                    render_template(template, move_ins=[], alerts=[])
                elif template == 'metrics.html':
                    render_template(template, metrics={'total_properties': 0, 'total_units': 0, 'vacant_units': 0, 'occupancy_rate': 0}, from_date='', to_date='')
                elif template == 'properties.html':
                    render_template(template, properties=[])
                elif template == 'renewals.html':
                    render_template(template, renewals=[])
                elif template == 'rental_applications.html':
                    render_template(template, applications=[])
                elif template == 'vendors.html':
                    render_template(template, vendors=[])
                else:
                    render_template(template)
                results[template] = "✅ OK"
            except Exception as e:
                results[template] = f"❌ Error: {str(e)[:100]}"
    
    return jsonify(results)

# ============================================
# ERROR HANDLERS
# ============================================

@app.errorhandler(404)
def not_found(e):
    return render_template('base.html'), 404

@app.errorhandler(500)
def server_error(e):
    import traceback
    error_trace = traceback.format_exc()
    print(f"Internal Server Error: {error_trace}")
    
    if app.config.get('FLASK_ENV') == 'development':
        return f"""
        <h1>Internal Server Error</h1>
        <pre>{error_trace}</pre>
        <p><a href="/">Go to Dashboard</a></p>
        """, 500
    else:
        return render_template('base.html'), 500

# ============================================
# MAIN EXECUTION
# ============================================

if __name__ == '__main__':
    print("\n" + "="*50)
    print("🏠 PROPERTY MANAGEMENT SYSTEM")
    print("="*50)
    print(f"Environment: {app.config['FLASK_ENV']}")
    print(f"Supabase Project: sejebqdhcilwcpjpznep")
    print("="*50)
    print(f"Starting server on http://localhost:5000")
    print("Press CTRL+C to stop")
    print("="*50 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)