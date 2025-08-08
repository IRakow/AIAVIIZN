# Complete app.py with all necessary imports and setup
# Place this at the top of your app.py file

from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from flask_session import Session
from supabase import create_client, Client
from functools import wraps
from datetime import datetime, timedelta
import os
import redis
import secrets
import json
import traceback

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(32))
app.config['DEBUG'] = os.environ.get('FLASK_ENV') == 'development'

# Session configuration (optional - can use simple sessions instead of Redis)
app.config['SESSION_TYPE'] = 'filesystem'  # Use filesystem instead of Redis for simplicity
app.config['SESSION_PERMANENT'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

Session(app)

# Supabase configuration
SUPABASE_URL = os.environ.get('SUPABASE_URL', 'https://sejebqdhcilwcpjpznep.supabase.co')
SUPABASE_ANON_KEY = os.environ.get('SUPABASE_ANON_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNlamVicWRoY2lsd2NwanB6bmVwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ0NTg5NjQsImV4cCI6MjA3MDAzNDk2NH0.vFM0Gr3QZF4MN3vtDGghjyCpnIkyC_mmUOOkVO3ahPQ')

# Initialize Supabase client
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    print("✅ Supabase connected successfully")
except Exception as e:
    print(f"⚠️ Supabase connection failed: {e}")
    supabase = None

# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

# Helper function to get current user
def get_current_user():
    if 'user_id' in session:
        return {
            'id': session.get('user_id'),
            'email': session.get('user_email', 'user@example.com'),
            'role': session.get('user_role', 'viewer'),
            'company_id': session.get('company_id', 'default-company-id')
        }
    return None

# For development/testing - auto-login a test user
@app.before_request
def auto_login_for_development():
    """Auto-login for development - remove in production"""
    if app.config['DEBUG'] and 'user_id' not in session:
        session['user_id'] = 'test-user-id'
        session['user_email'] = 'test@aiviizn.com'
        session['user_role'] = 'admin'
        session['company_id'] = 'test-company-id'

# ============================================
# MAIN ROUTES
# ============================================

# Updated dashboard route for app.py
# Replace the existing dashboard route with this one

@app.route('/')
@app.route('/dashboard')
@login_required
def dashboard():
    user = get_current_user()
    
    # Initialize metrics dictionary with all required fields
    metrics = {
        'total_properties': 0,
        'total_units': 0,
        'occupied_units': 0,
        'total_tenants': 0,
        'monthly_income': 0,
        'monthly_expenses': 0,
        'delinquencies': 0,
        'work_orders': 0,
        'move_ins': [],
        'move_outs': [],
        'lease_expirations': [],
        'occupancy_rate': 0,
        'vacant_units': 0,
        'maintenance_requests': 0,
        'online_payments_percentage': 90,  # Default values
        'units_paid_online_percentage': 92
    }
    
    try:
        # Only try to fetch from Supabase if we have a valid connection
        if supabase:
            try:
                # Fetch properties
                properties_response = supabase.table('properties').select('*').eq('company_id', user['company_id']).execute()
                if properties_response and hasattr(properties_response, 'data'):
                    metrics['total_properties'] = len(properties_response.data)
                
                # Fetch units
                units_response = supabase.table('units').select('*').eq('company_id', user['company_id']).execute()
                if units_response and hasattr(units_response, 'data'):
                    units_data = units_response.data
                    metrics['total_units'] = len(units_data)
                    metrics['occupied_units'] = len([u for u in units_data if u.get('status') == 'occupied'])
                    metrics['vacant_units'] = len([u for u in units_data if u.get('status') == 'vacant'])
                
                # Fetch tenants
                tenants_response = supabase.table('tenants').select('*').eq('company_id', user['company_id']).execute()
                if tenants_response and hasattr(tenants_response, 'data'):
                    metrics['total_tenants'] = len([t for t in tenants_response.data if t.get('status') == 'active'])
                
                # Calculate financial metrics
                current_month = datetime.now().month
                current_year = datetime.now().year
                
                # Try to fetch transactions
                try:
                    transactions_response = supabase.table('transactions').select('*').eq('company_id', user['company_id']).execute()
                    if transactions_response and hasattr(transactions_response, 'data'):
                        for trans in transactions_response.data:
                            if trans.get('date'):
                                trans_date = datetime.fromisoformat(trans['date'])
                                if trans_date.month == current_month and trans_date.year == current_year:
                                    if trans.get('type') == 'income':
                                        metrics['monthly_income'] += float(trans.get('amount', 0))
                                    else:
                                        metrics['monthly_expenses'] += float(trans.get('amount', 0))
                except Exception as e:
                    print(f"Error fetching transactions: {e}")
                
                # Fetch recent move-ins
                try:
                    move_ins_response = supabase.table('move_ins').select('*').eq('company_id', user['company_id']).limit(10).execute()
                    if move_ins_response and hasattr(move_ins_response, 'data'):
                        # Format move-ins data for template
                        for move_in in move_ins_response.data:
                            metrics['move_ins'].append({
                                'tenant_name': move_in.get('tenant_name', 'Unknown'),
                                'property_name': move_in.get('property_name', 'Unknown'),
                                'unit_number': move_in.get('unit_number', 'Unknown'),
                                'move_in_date': move_in.get('move_in_date', ''),
                                'balance_due': float(move_in.get('balance_due', 0)),
                                'insurance_verified': move_in.get('insurance_verified', False)
                            })
                except Exception as e:
                    print(f"Error fetching move-ins: {e}")
                
                # Calculate occupancy rate
                if metrics['total_units'] > 0:
                    metrics['occupancy_rate'] = round((metrics['occupied_units'] / metrics['total_units']) * 100, 2)
                
            except Exception as e:
                print(f"Supabase query error: {e}")
                # Continue with default metrics if Supabase fails
                
    except Exception as e:
        print(f"Dashboard data error: {e}")
        # Use default metrics if there's an error
    
    # Provide some default/mock data if database is empty
    if not metrics['move_ins']:
        # Add sample data for development
        metrics['move_ins'] = [
            {
                'tenant_name': 'Sample Tenant',
                'property_name': 'Sample Property',
                'unit_number': '101',
                'move_in_date': datetime.now().strftime('%m/%d/%Y'),
                'balance_due': 1500.00,
                'insurance_verified': True
            }
        ]
    
    # Add sample move-outs if empty
    if not metrics['move_outs']:
        metrics['move_outs'] = []
    
    # Add sample lease expirations
    metrics['lease_expirations'] = [
        {'count': 41, 'period': 'This Month'},
        {'count': 74, 'period': 'Next Month'}
    ]
    
    # Add delinquency data
    metrics['delinquencies'] = {
        'current': 185,
        'thirty_days': 31,
        'sixty_plus_days': 110
    }
    
    # Add work order stats
    metrics['work_order_stats'] = {
        'new': 220,
        'assigned': 122,
        'scheduled': 5,
        'waiting': 15,
        'completed_unbilled': 21,
        'ready_to_bill': 0,
        'completed_today': 1066
    }
    
    # Add guest cards and rental applications
    metrics['guest_cards'] = 371
    metrics['rental_applications'] = 64
    metrics['online_leases'] = {
        'out_for_signing': 9,
        'ready_to_countersign': 2,
        'fully_executed': 37
    }
    
    # Add current statistics
    metrics['units_posted_online'] = 36
    metrics['average_turnover_time'] = 66
    
    # If monthly_income is 0, provide some default values
    if metrics['monthly_income'] == 0:
        metrics['monthly_income'] = 842569.29
        metrics['monthly_expenses'] = 231078.74
    
    return render_template('dashboard/dashboard.html', 
                         metrics=metrics, 
                         user=user)

# Debug version of login route to see what's happening
# Replace your login route in app.py with this one

import json
from flask import Flask, render_template, request, redirect, url_for, session, flash
from supabase import create_client, Client
import os

# Supabase configuration - YOUR KEYS
SUPABASE_URL = 'https://sejebqdhcilwcpjpznep.supabase.co'
SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNlamVicWRoY2lsd2NwanB6bmVwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ0NTg5NjQsImV4cCI6MjA3MDAzNDk2NH0.vFM0Gr3QZF4MN3vtDGghjyCpnIkyC_mmUOOkVO3ahPQ'

# Initialize Supabase client with proper error handling
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    print("✅ Supabase client created successfully")
    print(f"   URL: {SUPABASE_URL}")
    print(f"   Key: {SUPABASE_ANON_KEY[:20]}...")
except Exception as e:
    print(f"❌ Failed to create Supabase client: {e}")
    supabase = None

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        print("\n" + "="*50)
        print(f"🔐 LOGIN ATTEMPT")
        print(f"   Email: {email}")
        print(f"   Password length: {len(password) if password else 0}")
        print("="*50)
        
        if not supabase:
            print("❌ Supabase client is None!")
            flash('Database connection error. Please try again.', 'danger')
            return render_template('auth/login.html')
        
        try:
            # Attempt Supabase authentication
            print("📡 Calling Supabase auth.sign_in_with_password...")
            
            auth_response = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            print(f"📦 Response received: {auth_response}")
            
            if auth_response and auth_response.user:
                # Authentication successful!
                user = auth_response.user
                session_data = auth_response.session
                
                print(f"✅ Authentication successful!")
                print(f"   User ID: {user.id}")
                print(f"   User Email: {user.email}")
                print(f"   Email Confirmed: {user.email_confirmed_at}")
                
                # Set session variables
                session['user_id'] = user.id
                session['user_email'] = user.email
                session['user_role'] = user.role if hasattr(user, 'role') else 'user'
                session['company_id'] = 'default-company'  # You can fetch this from a users table
                
                if session_data:
                    session['access_token'] = session_data.access_token
                    session['refresh_token'] = session_data.refresh_token
                    print(f"   Session tokens stored")
                
                flash('Successfully logged in!', 'success')
                
                # Redirect to dashboard or next page
                next_page = request.args.get('next')
                return redirect(next_page or url_for('dashboard'))
                
            else:
                print("❌ No user in response - authentication failed")
                flash('Invalid email or password', 'danger')
                
        except Exception as e:
            error_str = str(e)
            print(f"❌ Authentication error: {error_str}")
            print(f"   Error type: {type(e).__name__}")
            
            # Parse the error message for specific issues
            if 'Invalid login credentials' in error_str:
                flash('Invalid email or password. Please check your credentials.', 'danger')
            elif 'Email not confirmed' in error_str:
                flash('Please confirm your email address before logging in. Check your inbox for the confirmation link.', 'warning')
            elif 'User not found' in error_str:
                flash('No account found with this email address.', 'danger')
            else:
                # Show the actual error in development
                flash(f'Login error: {error_str}', 'danger')
                
    return render_template('auth/login.html')

# Test route to verify Supabase connection
@app.route('/test-supabase')
def test_supabase():
    """Test route to verify Supabase is working"""
    results = {
        'client_exists': supabase is not None,
        'url': SUPABASE_URL,
        'key_preview': SUPABASE_ANON_KEY[:20] + '...' if SUPABASE_ANON_KEY else None
    }
    
    if supabase:
        try:
            # Try to fetch from a table to test connection
            response = supabase.table('users').select('*').limit(1).execute()
            results['table_query'] = 'Success'
            results['data'] = response.data if response else None
        except Exception as e:
            results['table_query'] = f'Failed: {str(e)}'
    
    return f"<pre>{json.dumps(results, indent=2)}</pre>"

# Alternative login method using direct API call
@app.route('/login-direct', methods=['GET', 'POST'])
def login_direct():
    """Direct API login for testing"""
    if request.method == 'POST':
        import requests
        
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Direct API call to Supabase
        url = f"{SUPABASE_URL}/auth/v1/token?grant_type=password"
        headers = {
            "apikey": SUPABASE_ANON_KEY,
            "Content-Type": "application/json"
        }
        data = {
            "email": email,
            "password": password
        }
        
        print(f"🔧 Direct API call to: {url}")
        
        try:
            response = requests.post(url, json=data, headers=headers)
            print(f"📡 Response status: {response.status_code}")
            print(f"📦 Response body: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                
                # Set session
                session['user_id'] = result.get('user', {}).get('id')
                session['user_email'] = result.get('user', {}).get('email')
                session['access_token'] = result.get('access_token')
                session['user_role'] = 'user'
                session['company_id'] = 'default-company'
                
                flash('Login successful!', 'success')
                return redirect(url_for('dashboard'))
            else:
                error = response.json().get('error_description', 'Login failed')
                flash(f'Error: {error}', 'danger')
                
        except Exception as e:
            flash(f'Connection error: {str(e)}', 'danger')
            
    return render_template('auth/login.html')

@app.route('/quick-login', methods=['POST'])
def quick_login():
    session['logged_in'] = True
    return redirect(url_for('dashboard'))

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
    try:
        # Fetch security deposit funds mismatch data
        security_deposit_mismatches = []
        if supabase:
            # Query for properties with security deposit mismatches
            deposit_response = supabase.table('properties').select(
                'id, name, address',
                'gl_accounts!inner(account_type, balance)',
                'security_deposits(amount)'
            ).eq('gl_accounts.account_type', 'security_deposit').execute()
            
            for prop in deposit_response.data:
                gl_balance = sum([acc['balance'] for acc in prop.get('gl_accounts', [])])
                deposit_balance = sum([dep['amount'] for dep in prop.get('security_deposits', [])])
                
                if abs(gl_balance - deposit_balance) > 0.01:  # Significant difference
                    security_deposit_mismatches.append({
                        'property_name': prop['name'],
                        'gl_balance': gl_balance,
                        'deposit_balance': deposit_balance
                    })
        
        # Fetch escrow cash account balance mismatch data
        escrow_mismatches = []
        if supabase:
            # Query for escrow account mismatches
            escrow_response = supabase.table('properties').select(
                'id, name, address',
                'gl_accounts!inner(account_type, balance)',
                'bank_accounts(account_type, balance)'
            ).eq('gl_accounts.account_type', 'escrow').execute()
            
            for prop in escrow_response.data:
                escrow_gl_balance = sum([acc['balance'] for acc in prop.get('gl_accounts', []) if acc['account_type'] == 'escrow'])
                deposit_gl_balance = sum([acc['balance'] for acc in prop.get('gl_accounts', []) if acc['account_type'] == 'security_deposit'])
                all_gl_balance = sum([acc['balance'] for acc in prop.get('gl_accounts', [])])
                
                escrow_mismatches.append({
                    'property_name': prop['name'],
                    'escrow_gl_balance': escrow_gl_balance,
                    'deposit_gl_balance': deposit_gl_balance,
                    'all_gl_balance': all_gl_balance
                })
        
        # Define diagnostic sections
        diagnostic_sections = [
            {
                'id': 'security_deposit_mismatch',
                'title': 'Security Deposit Funds Mismatch',
                'expanded': True,
                'data': security_deposit_mismatches
            },
            {
                'id': 'escrow_mismatch',
                'title': 'Escrow Cash Account Balance Mismatch',
                'expanded': True,
                'data': escrow_mismatches
            },
            {
                'id': 'security_clearing',
                'title': 'Non-Zero Security Clearing Account Balances',
                'expanded': False,
                'data': []
            },
            {
                'id': 'negative_fees',
                'title': 'Negative Balance on Additional Fee GL Accounts',
                'expanded': False,
                'data': []
            },
            {
                'id': 'positive_fees',
                'title': 'Positive Balance on Additional Fee GL Accounts',
                'expanded': False,
                'data': []
            },
            {
                'id': 'unused_prepayments',
                'title': 'Tenants and Homeowners With Unused Prepayments / Open Charges / Open Credits',
                'expanded': False,
                'data': []
            },
            {
                'id': 'prepayment_mismatch',
                'title': 'Prepayment Balance Mismatch',
                'expanded': False,
                'data': []
            },
            {
                'id': 'reconciliation_lapses',
                'title': 'Bank Account Reconciliation Lapses Over 60 Days',
                'expanded': False,
                'data': []
            },
            {
                'id': 'past_tenant_prepayments',
                'title': 'Unused Prepayments for Past Tenants',
                'expanded': False,
                'data': []
            },
            {
                'id': 'non_prepay_accounts',
                'title': 'Unused Prepayments Associated with a Non-Prepay GL Account',
                'expanded': False,
                'data': []
            }
        ]
        
    except Exception as e:
        print(f"Error fetching diagnostics data: {e}")
        security_deposit_mismatches = []
        escrow_mismatches = []
        diagnostic_sections = []
    
    # Fetch diagnostic data from Supabase
    return render_template('diagnostics.html', 
                         security_deposit_mismatches=security_deposit_mismatches,
                         escrow_mismatches=escrow_mismatches,
                         diagnostic_sections=diagnostic_sections)

# ============================================
# MAINTENANCE SECTION
# ============================================

@app.route('/work-orders')
def work_orders():
    """Work orders page"""
    work_orders_data = [
        {
            'id': '1',
            'property': 'Sunset Apartments',
            'unit': '101',
            'tenant': 'John Smith',
            'issue': 'Leaky faucet',
            'priority': 'Medium',
            'status': 'Open',
            'created_date': datetime.now().date().isoformat()
        }
    ]
    return render_template('work_orders.html', work_orders=work_orders_data)

@app.route('/recurring-work-orders')
def recurring_work_orders():
    """Recurring work orders page"""
    recurring_orders = [
        {
            'id': '1',
            'description': 'HVAC Filter Change',
            'frequency': 'Monthly',
            'properties': 'All Properties',
            'next_due': (datetime.now().date() + timedelta(days=15)).isoformat()
        }
    ]
    return render_template('recurring_work_orders.html', recurring_orders=recurring_orders)

@app.route('/inspections')
def inspections():
    """Inspections page"""
    inspections_data = [
        {
            'id': '1',
            'property': 'Sunset Apartments',
            'unit': '101',
            'type': 'Move-out',
            'scheduled_date': (datetime.now().date() + timedelta(days=7)).isoformat(),
            'inspector': 'Jane Doe',
            'status': 'Scheduled'
        }
    ]
    return render_template('inspections.html', inspections=inspections_data)

# ============================================
# MARKETING SECTION
# ============================================

@app.route('/listings')
def listings():
    """Listings page"""
    listings_data = [
        {
            'id': '1',
            'property': 'Sunset Apartments',
            'unit': '101',
            'rent': 1500,
            'available_date': datetime.now().date().isoformat(),
            'listed_on': ['Zillow', 'Apartments.com'],
            'status': 'Active'
        }
    ]
    return render_template('listings.html', listings=listings_data)

@app.route('/showings')
def showings():
    """Showings page"""
    showings_data = [
        {
            'id': '1',
            'property': 'Sunset Apartments',
            'unit': '101',
            'prospect': 'Jane Smith',
            'date': (datetime.now().date() + timedelta(days=2)).isoformat(),
            'time': '2:00 PM',
            'agent': 'Mike Johnson',
            'status': 'Scheduled'
        }
    ]
    return render_template('showings.html', showings=showings_data)

# ============================================
# COMMUNICATIONS SECTION
# ============================================

@app.route('/emails')
def emails():
    """Emails page"""
    emails_data = [
        {
            'id': '1',
            'to': 'tenant@example.com',
            'subject': 'Rent Reminder',
            'date': datetime.now().date().isoformat(),
            'status': 'Sent'
        }
    ]
    return render_template('emails.html', emails=emails_data)

@app.route('/letters')
def letters():
    """Letters page"""
    letters_data = [
        {
            'id': '1',
            'recipient': 'John Smith',
            'type': 'Late Notice',
            'property': 'Sunset Apartments',
            'unit': '101',
            'date': datetime.now().date().isoformat(),
            'status': 'Printed'
        }
    ]
    return render_template('letters.html', letters=letters_data)

@app.route('/phone-logs')
def phone_logs():
    """Phone logs page"""
    phone_logs_data = [
        {
            'id': '1',
            'contact': 'John Smith',
            'phone': '555-0123',
            'type': 'Incoming',
            'duration': '5 min',
            'notes': 'Maintenance request',
            'date': datetime.now().isoformat()
        }
    ]
    return render_template('phone_logs.html', phone_logs=phone_logs_data)

# ============================================
# REPORTS SECTION
# ============================================

@app.route('/rent-roll')
def rent_roll():
    """Rent roll report page"""
    rent_roll_data = [
        {
            'property': 'Sunset Apartments',
            'unit': '101',
            'tenant': 'John Smith',
            'rent': 1500,
            'balance': 0,
            'next_due': (datetime.now().date() + timedelta(days=30)).isoformat()
        }
    ]
    return render_template('rent_roll.html', rent_roll=rent_roll_data)

@app.route('/financial-reports')
def financial_reports():
    """Financial reports page"""
    return render_template('financial_reports.html')

@app.route('/vacancy-reports')
def vacancy_reports():
    """Vacancy reports page"""
    vacancy_data = {
        'total_units': 100,
        'vacant_units': 10,
        'vacancy_rate': 10.0,
        'avg_days_vacant': 30
    }
    return render_template('vacancy_reports.html', vacancy_data=vacancy_data)

# ============================================
# ADMINISTRATION SECTION
# ============================================

@app.route('/company-settings')
def company_settings():
    """Company settings page"""
    settings = {
        'company_name': 'Celtic Property Management',
        'address': '123 Main St',
        'phone': '555-0100',
        'email': 'info@celticpm.com'
    }
    return render_template('company_settings.html', settings=settings)

@app.route('/users')
def users():
    """Users management page"""
    users_data = [
        {
            'id': '1',
            'name': 'Admin User',
            'email': 'admin@celticpm.com',
            'role': 'Administrator',
            'status': 'Active'
        }
    ]
    return render_template('users.html', users=users_data)

@app.route('/document-templates')
def document_templates():
    """Document templates page"""
    templates = [
        {
            'id': '1',
            'name': 'Standard Lease Agreement',
            'type': 'Lease',
            'last_modified': datetime.now().date().isoformat()
        }
    ]
    return render_template('document_templates.html', templates=templates)

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

# Also update the error handlers to be more informative
@app.errorhandler(500)
def internal_error(error):
    import traceback
    error_text = traceback.format_exc()
    print(f"500 Error: {error_text}")
    return render_template('errors/500.html', error=error_text), 500

@app.errorhandler(404)
def not_found(error):
    return render_template('errors/404.html'), 404

# ============================================
# MAIN EXECUTION
# ============================================

if __name__ == '__main__':
    print("\n" + "="*50)
    print("🏠 PROPERTY MANAGEMENT SYSTEM")
    print("="*50)
    print(f"Environment: {app.config.get('FLASK_ENV', 'development')}")
    print(f"Supabase Project: sejebqdhcilwcpjpznep")
    print("="*50)
    print(f"Starting server on http://localhost:8080")
    print("Press CTRL+C to stop")
    print("="*50 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=8080)