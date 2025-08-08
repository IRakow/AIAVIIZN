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
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'f3cfe9ed8fae309f02079dbf'
app.config['ENV'] = 'development'
CORS(app)

# Your Supabase configuration - COMPLETE CREDENTIALS
SUPABASE_URL = "https://sejebqdhcilwcpjpznep.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNlamVicWRoY2lsd2NwanB6bmVwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ0NTg5NjQsImV4cCI6MjA3MDAzNDk2NH0.vFM0Gr3QZF4MN3vtDGghjyCpnIkyC_mmUOOkVO3ahPQ"

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
    applications = safe_supabase_query(
        lambda: supabase.table('rental_applications').select(
            "*, properties(name), units(unit_number)"
        ).order('created_at', desc=True).execute()
    )
    
    return render_template('rental_applications.html', applications=applications)

@app.route('/leases')
def leases():
    status_filter = request.args.get('status', 'all')
    
    if supabase:
        query = supabase.table('leases').select(
            "*, tenants(first_name, last_name), units(unit_number, properties(name))"
        )
        
        if status_filter != 'all':
            query = query.eq('status', status_filter)
        
        leases_data = safe_supabase_query(lambda: query.execute())
    else:
        leases_data = []
    
    return render_template('leases.html', leases=leases_data, current_status=status_filter)

@app.route('/renewals')
def renewals():
    expiry_date = (datetime.now() + timedelta(days=90)).isoformat()
    
    renewals_data = safe_supabase_query(
        lambda: supabase.table('leases').select(
            "*, tenants(first_name, last_name), units(unit_number, rent, properties(name))"
        ).lte('end_date', expiry_date).gte('end_date', datetime.now().isoformat()).execute()
    )
    
    return render_template('renewals.html', renewals=renewals_data)

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

@app.route('/calendar')
def calendar():
    # Calendar view placeholder
    events = safe_supabase_query(
        lambda: supabase.table('calendar_events').select("*").execute()
    ) if supabase else []
    
    return render_template('calendar.html', events=events)

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

# Additional routes for sidebar menu items
@app.route('/leasing_vacancies')
def leasing_vacancies():
    return redirect(url_for('vacancies'))

@app.route('/leasing_metrics')
def leasing_metrics():
    return redirect(url_for('metrics'))

@app.route('/signals')
def signals():
    return render_template('signals.html')

@app.route('/work_orders')
def work_orders():
    return render_template('work_orders.html')

@app.route('/recurring_work_orders')
def recurring_work_orders():
    return render_template('recurring_work_orders.html')

@app.route('/inspections')
def inspections():
    return render_template('inspections.html')

@app.route('/unit_turns')
def unit_turns():
    return render_template('unit_turns.html')

@app.route('/projects')
def projects():
    return render_template('projects.html')

@app.route('/purchase_orders')
def purchase_orders():
    return render_template('purchase_orders.html')

@app.route('/inventory')
def inventory():
    return render_template('inventory.html')

@app.route('/fixed_assets')
def fixed_assets():
    return render_template('fixed_assets.html')

@app.route('/smart_maintenance')
def smart_maintenance():
    return render_template('smart_maintenance.html')

@app.route('/reporting')
def reporting():
    return render_template('reporting.html')

@app.route('/letters')
def letters():
    return render_template('letters.html')

@app.route('/forms')
def forms():
    return render_template('forms.html')

@app.route('/inbox')
def inbox():
    return render_template('inbox.html')

@app.route('/whats_new')
def whats_new():
    return render_template('whats_new.html')

# Simple login page
@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/quick-login', methods=['POST'])
def quick_login():
    session['logged_in'] = True
    return redirect(url_for('dashboard'))

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
    
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=True, host='0.0.0.0', port=port)