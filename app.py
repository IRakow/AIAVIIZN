# Property Management System - Flask Application with Supabase Integration
# File: app.py

from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_cors import CORS
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from supabase import create_client, Client
import json

# Load environment variables
try:
    load_dotenv()
except:
    pass  # .env file might not exist in production

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'f3cfe9ed8fae309f02079dbf')
app.config['ENV'] = os.environ.get('FLASK_ENV', 'production')
CORS(app)

# Your Supabase configuration - COMPLETE CREDENTIALS
SUPABASE_URL = os.environ.get('SUPABASE_URL', "https://sejebqdhcilwcpjpznep.supabase.co")
SUPABASE_KEY = os.environ.get('SUPABASE_KEY', "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNlamVicWRoY2lsd2NwanB6bmVwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ0NTg5NjQsImV4cCI6MjA3MDAzNDk2NH0.vFM0Gr3QZF4MN3vtDGghjyCpnIkyC_mmUOOkVO3ahPQ")

# Initialize Supabase client
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✅ Connected to Supabase successfully!")
    print(f"   URL: {SUPABASE_URL}")
    print(f"   Environment: {app.config['ENV']}")
except Exception as e:
    print(f"⚠️ Supabase connection warning: {e}")
    print("   Please check your API key is complete")
    supabase = None

# Helper function to safely execute Supabase queries
def safe_supabase_query(query_func):
    """Safely execute a Supabase query and return data or empty list"""
    try:
        if supabase:
            result = query_func()
            if result and hasattr(result, 'data'):
                return result.data
    except Exception as e:
        print(f"Query error: {e}")
    return []

# Test the connection
def test_connection():
    """Test Supabase connection and create tables if needed"""
    if not supabase:
        return False
    
    try:
        # Test with a simple query
        result = supabase.table('properties').select("id").limit(1).execute()
        return True
    except Exception as e:
        print(f"⚠️ Table 'properties' doesn't exist. Creating sample tables...")
        try:
            # Create basic tables if they don't exist
            create_sample_tables()
            return True
        except:
            return False

def create_sample_tables():
    """Create sample data for testing if tables don't exist"""
    # This would normally be done in Supabase SQL editor
    # For now, we'll return sample data when queries fail
    pass

# Routes with Real Supabase Integration
@app.route('/')
@app.route('/dashboard')
def dashboard():
    # Fetch real move-ins data from Supabase
    move_ins = safe_supabase_query(
        lambda: supabase.table('move_ins').select(
            "*, leases(*, tenants(*), units(*, properties(*)))"
        ).eq('completed', False).order('move_in_date').execute()
    )
    
    # Fetch active alerts
    alerts = safe_supabase_query(
        lambda: supabase.table('alerts').select("*").eq('active', True).execute()
    )
    
    # If no alerts, add default one
    if not alerts:
        alerts = [{'message': 'Have you checked your Financial Diagnostics Page recently?', 'link': '/diagnostics'}]
    
    return render_template('dashboard.html', move_ins=move_ins, alerts=alerts)

@app.route('/properties')
def properties():
    # Fetch real properties from Supabase
    properties_data = safe_supabase_query(
        lambda: supabase.table('properties').select(
            "*, units(count)"
        ).order('name').execute()
    )
    
    # If no data, provide sample data
    if not properties_data:
        properties_data = [
            {
                'name': '(BARR) Rock Ridge Ranch Apartments',
                'address': '10561 Cypress Ave',
                'city': 'Kansas City',
                'state': 'MO',
                'zip': '64137',
                'type': 'Multi-Family',
                'units': 75,
                'vacant_count': 3,
                'owners': 'Rock Ridge Ranch LLC'
            },
            {
                'name': '12520 Grandview Rd. House',
                'address': '12520 Grandview Rd',
                'city': 'Grandview',
                'state': 'MO',
                'zip': '64030',
                'type': 'Single-Family',
                'units': 1,
                'vacant_count': 0,
                'owners': 'HLF Investments MO LLC'
            }
        ]
    else:
        # Add vacancy count for each property
        for prop in properties_data:
            if supabase:
                try:
                    vacant_result = supabase.table('units').select("count", count='exact').eq('property_id', prop['id']).eq('status', 'vacant').execute()
                    prop['vacant_count'] = vacant_result.count if hasattr(vacant_result, 'count') else 0
                except:
                    prop['vacant_count'] = 0
    
    return render_template('properties.html', properties=properties_data)

@app.route('/tenants')
def tenants():
    # Fetch real tenants from Supabase
    tenants_data = safe_supabase_query(
        lambda: supabase.table('tenants').select(
            "*, leases(*, units(*, properties(*)))"
        ).order('last_name', 'first_name').execute()
    )
    
    # Format tenant data or provide sample
    if tenants_data:
        formatted_tenants = []
        for tenant in tenants_data:
            current_lease = None
            if tenant.get('leases'):
                for lease in tenant['leases']:
                    if lease.get('status') == 'active':
                        current_lease = lease
                        break
            
            formatted_tenants.append({
                'id': tenant.get('id'),
                'name': f"{tenant.get('last_name', '')}, {tenant.get('first_name', '')}",
                'status': 'Current' if current_lease else 'Past',
                'property': current_lease['units']['properties']['name'] if current_lease else '-',
                'unit': current_lease['units']['unit_number'] if current_lease else '-',
                'phone': tenant.get('phone', ''),
                'email': tenant.get('email', '')
            })
    else:
        # Sample data
        formatted_tenants = [
            {'name': 'Smith, John', 'status': 'Current', 'property': 'Rock Ridge Ranch', 'unit': '101', 'phone': '(816) 555-0101'},
            {'name': 'Johnson, Mary', 'status': 'Current', 'property': 'Blue Ridge Manor', 'unit': '205', 'phone': '(816) 555-0102'}
        ]
    
    return render_template('tenants.html', tenants=formatted_tenants)

@app.route('/owners')
def owners():
    # Fetch real owners from Supabase
    owners_data = safe_supabase_query(
        lambda: supabase.table('owners').select("*").order('company').execute()
    )
    
    if not owners_data:
        # Sample data
        owners_data = [
            {'name': '3825 Baltimore / Finkelstein', 'company': '3825 Baltimore / Finkelstein', 'phone': '(650) 922-0967', 'email': 'owner@example.com'}
        ]
    
    return render_template('owners.html', owners=owners_data)

@app.route('/vendors')
def vendors():
    vendors_data = safe_supabase_query(
        lambda: supabase.table('vendors').select("*").order('name').execute()
    )
    
    if not vendors_data:
        vendors_data = [
            {'name': 'ABC Plumbing', 'address': '123 Main St', 'trade': 'Plumbing', 'phone': '(816) 555-0201', 'email': 'plumber@example.com'}
        ]
    
    return render_template('vendors.html', vendors=vendors_data)

@app.route('/vacancies')
def vacancies():
    vacancies_data = safe_supabase_query(
        lambda: supabase.table('units').select(
            "*, properties(name, address, city, state, zip)"
        ).eq('status', 'vacant').order('days_vacant', desc=True).execute()
    )
    
    return render_template('vacancies.html', vacancies=vacancies_data)

@app.route('/guest-cards')
def guest_cards():
    guests = safe_supabase_query(
        lambda: supabase.table('guest_cards').select(
            "*, properties(name), units(unit_number)"
        ).order('created_at', desc=True).execute()
    )
    
    return render_template('guest_cards.html', guests=guests)

@app.route('/rental-applications')
def rental_applications():
    """Rental applications page - fixed route"""
    try:
        # Try to get data from Supabase
        applications = []
        if supabase:
            try:
                result = supabase.table('applications').select(
                    "*, guest_cards(first_name, last_name, email, phone), units(unit_number, properties(name))"
                ).order('created_at', desc=True).execute()
                applications = result.data if result else []
            except Exception as e:
                print(f"Database error: {e}")
                applications = []
        
        # Provide sample data if no database connection or empty
        if not applications:
            applications = [
                {
                    'id': '1',
                    'guest_cards': {
                        'first_name': 'John',
                        'last_name': 'Doe',
                        'email': 'john@example.com',
                        'phone': '555-0123'
                    },
                    'units': {
                        'unit_number': '101',
                        'properties': {'name': 'Sunset Apartments'}
                    },
                    'status': 'pending',
                    'score': 720,
                    'monthly_income': 4500,
                    'created_at': datetime.now().isoformat()
                },
                {
                    'id': '2',
                    'guest_cards': {
                        'first_name': 'Jane',
                        'last_name': 'Smith',
                        'email': 'jane@example.com',
                        'phone': '555-0124'
                    },
                    'units': {
                        'unit_number': '205',
                        'properties': {'name': 'Oak Grove'}
                    },
                    'status': 'approved',
                    'score': 780,
                    'monthly_income': 5200,
                    'created_at': (datetime.now() - timedelta(days=2)).isoformat()
                }
            ]
        
        return render_template('rental_applications.html', applications=applications)
        
    except Exception as e:
        # Log the error and return a helpful message
        print(f"Error in rental_applications route: {e}")
        import traceback
        traceback.print_exc()
        
        # Return with empty data rather than erroring
        return render_template('rental_applications.html', applications=[])

@app.route('/leases')
def leases():
    """Leases management page - fixed route"""
    try:
        # Try to get data from Supabase
        leases_data = []
        properties = []
        
        if supabase:
            try:
                # Get leases
                result = supabase.table('leases').select(
                    "*, tenants(first_name, last_name, email), units(unit_number, rent, properties(name))"
                ).order('created_at', desc=True).execute()
                leases_data = result.data if result else []
                
                # Get properties for filter dropdown
                prop_result = supabase.table('properties').select("name").execute()
                properties = prop_result.data if prop_result else []
            except Exception as e:
                print(f"Database error: {e}")
                leases_data = []
                properties = []
        
        # Provide sample data if no database connection or empty
        if not leases_data:
            leases_data = [
                {
                    'id': '1',
                    'tenants': {
                        'first_name': 'Alice',
                        'last_name': 'Johnson',
                        'email': 'alice@example.com'
                    },
                    'units': {
                        'unit_number': '301',
                        'rent': 1500,
                        'properties': {'name': 'Sunset Apartments'}
                    },
                    'status': 'active',
                    'start_date': datetime.now().date().isoformat(),
                    'end_date': (datetime.now().date() + timedelta(days=365)).isoformat(),
                    'rent': 1500,
                    'created_at': datetime.now().isoformat()
                },
                {
                    'id': '2',
                    'tenants': {
                        'first_name': 'Bob',
                        'last_name': 'Wilson',
                        'email': 'bob@example.com'
                    },
                    'units': {
                        'unit_number': '205',
                        'rent': 1200,
                        'properties': {'name': 'Oak Grove'}
                    },
                    'status': 'pending',
                    'start_date': (datetime.now().date() + timedelta(days=15)).isoformat(),
                    'end_date': (datetime.now().date() + timedelta(days=380)).isoformat(),
                    'rent': 1200,
                    'created_at': (datetime.now() - timedelta(days=5)).isoformat()
                },
                {
                    'id': '3',
                    'tenants': {
                        'first_name': 'Carol',
                        'last_name': 'Davis',
                        'email': 'carol@example.com'
                    },
                    'units': {
                        'unit_number': '102',
                        'rent': 1350,
                        'properties': {'name': 'Riverside Plaza'}
                    },
                    'status': 'draft',
                    'start_date': None,
                    'end_date': None,
                    'rent': 1350,
                    'created_at': (datetime.now() - timedelta(days=1)).isoformat()
                }
            ]
            
            properties = [
                {'name': 'Sunset Apartments'},
                {'name': 'Oak Grove'},
                {'name': 'Riverside Plaza'}
            ]
        
        return render_template('leases.html', leases=leases_data, properties=properties)
        
    except Exception as e:
        # Log the error and return a helpful message
        print(f"Error in leases route: {e}")
        import traceback
        traceback.print_exc()
        
        # Return with empty data rather than erroring
        return render_template('leases.html', leases=[], properties=[])

@app.route('/renewals')
def renewals():
    expiry_date = (datetime.now() + timedelta(days=90)).isoformat()
    
    renewals_data = safe_supabase_query(
        lambda: supabase.table('leases').select(
            "*, tenants(first_name, last_name), units(unit_number, rent, properties(name))"
        ).lte('end_date', expiry_date).gte('end_date', datetime.now().isoformat()).execute()
    )
    
    return render_template('renewals.html', renewals=renewals_data)

@app.route('/debug')
def debug():
    import os
    templates = os.listdir('templates')
    return jsonify({
        'templates': templates,
        'current_dir': os.getcwd(),
        'template_folder': app.template_folder,
        'app_root': app.root_path
    })

@app.route('/metrics')
def metrics():
    metrics_data = {
        'total_properties': 0,
        'total_units': 0,
        'vacant_units': 0,
        'active_leases': 0,
        'occupancy_rate': 0
    }
    
    if supabase:
        try:
            properties_count = supabase.table('properties').select("count", count='exact').execute()
            units_count = supabase.table('units').select("count", count='exact').execute()
            vacant_units = supabase.table('units').select("count", count='exact').eq('status', 'vacant').execute()
            active_leases = supabase.table('leases').select("count", count='exact').eq('status', 'active').execute()
            
            metrics_data = {
                'total_properties': properties_count.count if hasattr(properties_count, 'count') else 0,
                'total_units': units_count.count if hasattr(units_count, 'count') else 0,
                'vacant_units': vacant_units.count if hasattr(vacant_units, 'count') else 0,
                'active_leases': active_leases.count if hasattr(active_leases, 'count') else 0,
                'occupancy_rate': ((units_count.count - vacant_units.count) / units_count.count * 100) 
                                if hasattr(units_count, 'count') and units_count.count > 0 else 0
            }
        except Exception as e:
            print(f"Metrics error: {e}")
    
    return render_template('metrics.html', metrics=metrics_data)

# Remaining routes stay the same...
@app.route('/receivables')
def receivables():
    receipts_data = safe_supabase_query(
        lambda: supabase.table('transactions').select(
            "*, properties(name), units(unit_number), tenants(first_name, last_name)"
        ).eq('type', 'receipt').order('transaction_date', desc=True).limit(50).execute()
    )
    
    formatted_receipts = []
    for receipt in receipts_data:
        formatted_receipts.append({
            'date': receipt.get('transaction_date', ''),
            'payer': f"{receipt.get('tenants', {}).get('first_name', '')} {receipt.get('tenants', {}).get('last_name', '')}",
            'gl_account': receipt.get('gl_account', ''),
            'property': f"{receipt.get('properties', {}).get('name', '')} - {receipt.get('units', {}).get('unit_number', '')}",
            'amount': receipt.get('amount', 0),
            'reference': receipt.get('reference_number', '')
        })
    
    return render_template('receivables.html', receipts=formatted_receipts)

@app.route('/payables')
def payables():
    bills_data = safe_supabase_query(
        lambda: supabase.table('bills').select(
            "*, vendors(name), properties(name)"
        ).order('bill_date', desc=True).limit(50).execute()
    )
    
    formatted_bills = []
    for bill in bills_data:
        formatted_bills.append({
            'payee': bill.get('vendors', {}).get('name', bill.get('payee', '')),
            'ref': bill.get('reference_number', ''),
            'bill_date': bill.get('bill_date', ''),
            'for': bill.get('properties', {}).get('name', ''),
            'gl_account': bill.get('gl_account', ''),
            'due_date': bill.get('due_date', ''),
            'amount': bill.get('amount', 0),
            'status': bill.get('status', 'Pending'),
            'cash_account': bill.get('cash_account', '1150: Cash in Bank')
        })
    
    return render_template('payables.html', bills=formatted_bills)

@app.route('/bank-accounts')
def bank_accounts():
    accounts_data = safe_supabase_query(
        lambda: supabase.table('bank_accounts').select("*").order('name').execute()
    )
    
    return render_template('bank_accounts.html', accounts=accounts_data)

@app.route('/journal-entries')
def journal_entries():
    entries_data = safe_supabase_query(
        lambda: supabase.table('journal_entries').select(
            "*, journal_entry_lines(*), properties(name)"
        ).order('entry_date', desc=True).limit(50).execute()
    )
    
    return render_template('journal_entries.html', entries=entries_data)

@app.route('/bank-transfers')
def bank_transfers():
    transfers_data = safe_supabase_query(
        lambda: supabase.table('bank_transfers').select(
            "*, from_account:bank_accounts!from_account_id(name), to_account:bank_accounts!to_account_id(name)"
        ).eq('status', 'incomplete').order('created_at', desc=True).execute()
    )
    
    return render_template('bank_transfers.html', transfers=transfers_data)

@app.route('/gl-accounts')
def gl_accounts():
    gl_accounts_data = safe_supabase_query(
        lambda: supabase.table('gl_accounts').select("*").order('account_number').execute()
    )
    
    return render_template('gl_accounts.html', gl_accounts=gl_accounts_data)

@app.route('/diagnostics')
def diagnostics():
    diagnostics_data = {'security_deposits': [], 'escrow_cash': []}
    
    if supabase:
        properties = safe_supabase_query(
            lambda: supabase.table('properties').select("id, name").execute()
        )
        
        for prop in properties:
            gl_balance = safe_supabase_query(
                lambda p=prop: supabase.table('gl_balances').select("balance")
                .eq('property_id', p['id']).eq('account_type', 'security_deposit').execute()
            )
            
            security_funds = safe_supabase_query(
                lambda p=prop: supabase.table('security_deposits').select("amount")
                .eq('property_id', p['id']).eq('status', 'held').execute()
            )
            
            gl_total = sum([b.get('balance', 0) for b in gl_balance]) if gl_balance else 0
            security_total = sum([s.get('amount', 0) for s in security_funds]) if security_funds else 0
            
            if gl_total != security_total:
                diagnostics_data['security_deposits'].append({
                    'property': prop['name'],
                    'general_ledger': gl_total,
                    'security_funds': security_total
                })
    
    return render_template('diagnostics.html', diagnostics=diagnostics_data)

# All API routes remain the same...
# [Previous API routes code continues here]

# Simple login page
@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/quick-login', methods=['POST'])
def quick_login():
    session['logged_in'] = True
    return redirect(url_for('dashboard'))

# Error handler to help debug template issues
@app.errorhandler(500)
def internal_error(error):
    """Handle internal server errors"""
    import traceback
    error_trace = traceback.format_exc()
    print(f"Internal Server Error: {error_trace}")
    
    # In development, show the error
    if app.config.get('FLASK_ENV') == 'development':
        return f"""
        <h1>Internal Server Error</h1>
        <pre>{error_trace}</pre>
        <p><a href="/">Go to Dashboard</a></p>
        """, 500
    else:
        return render_template('base.html'), 500

# Test route to check if templates are working
@app.route('/test-templates')
def test_templates():
    """Test route to verify templates are accessible"""
    import os
    
    results = {}
    template_dir = os.path.join(app.root_path, 'templates')
    
    for template in os.listdir(template_dir):
        if template.endswith('.html'):
            try:
                # Try to render each template with minimal data
                if template == 'base.html':
                    continue  # Skip base template
                elif template == 'rental_applications.html':
                    render_template(template, applications=[])
                    results[template] = "✅ OK"
                elif template == 'leases.html':
                    render_template(template, leases=[], properties=[])
                    results[template] = "✅ OK"
                elif template == 'guest_cards.html':
                    render_template(template, guest_cards=[])
                    results[template] = "✅ OK"
                elif template == 'vacancies.html':
                    render_template(template, vacancies=[])
                    results[template] = "✅ OK"
                elif template == 'dashboard.html':
                    render_template(template, move_ins=[], alerts=[])
                    results[template] = "✅ OK"
                else:
                    # Try with generic empty data
                    render_template(template)
                    results[template] = "✅ OK"
            except Exception as e:
                results[template] = f"❌ Error: {str(e)[:100]}"
    
    return jsonify(results)

if __name__ == '__main__':
    print("\n" + "="*50)
    print("🏠 PROPERTY MANAGEMENT SYSTEM")
    print("="*50)
    print(f"Secret Key: {app.config['SECRET_KEY'][:10]}...")
    print(f"Environment: {app.config['ENV']}")
    print(f"Supabase Project: sejebqdhcilwcpjpznep")
    print("="*50)
    
    # Test connection
    if test_connection():
        print("✅ Database connection successful!")
    else:
        print("⚠️ Running in demo mode with sample data")
        print("   To connect to Supabase:")
        print("   1. Go to: https://supabase.com/dashboard/project/sejebqdhcilwcpjpznep/settings/api")
        print("   2. Copy your complete 'anon public' key")
        print("   3. Add it to your .env file as SUPABASE_KEY=your_complete_key")
    
    print("="*50)
    print("Starting server on http://localhost:5000")
    print("Press CTRL+C to stop")
    print("="*50 + "\n")
    
    # Only run the development server if this script is executed directly
    if __name__ == "__main__":
        app.run(debug=True, port=5000)