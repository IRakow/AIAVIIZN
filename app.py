# Property Management System - Flask Application
# File: app.py

from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_cors import CORS
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from supabase import create_client, Client
from functools import wraps
import secrets

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(16))
CORS(app)

# Supabase configuration
SUPABASE_URL = os.environ.get("SUPABASE_URL", "your-supabase-url")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "your-supabase-anon-key")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
@app.route('/dashboard')
@login_required
def dashboard():
    # Fetch move-ins data
    move_ins = supabase.table('move_ins').select("*").execute()
    alerts = supabase.table('alerts').select("*").eq('active', True).execute()
    
    return render_template('dashboard.html', 
                         move_ins=move_ins.data if move_ins else [],
                         alerts=alerts.data if alerts else [])

@app.route('/vacancies')
@login_required
def vacancies():
    # Fetch vacancies with property details
    vacancies_data = supabase.table('units').select(
        "*, properties(name, address, city, state, zip)"
    ).eq('status', 'vacant').execute()
    
    return render_template('vacancies.html', 
                         vacancies=vacancies_data.data if vacancies_data else [])

@app.route('/guest-cards')
@login_required
def guest_cards():
    # Fetch guest cards (leads)
    guests = supabase.table('guest_cards').select(
        "*, properties(name), units(unit_number)"
    ).order('created_at', desc=True).execute()
    
    return render_template('guest_cards.html', 
                         guests=guests.data if guests else [])

@app.route('/leases')
@login_required
def leases():
    status_filter = request.args.get('status', 'all')
    
    query = supabase.table('leases').select(
        "*, tenants(first_name, last_name), units(unit_number, properties(name))"
    )
    
    if status_filter != 'all':
        query = query.eq('status', status_filter)
    
    leases_data = query.execute()
    
    return render_template('leases.html', 
                         leases=leases_data.data if leases_data else [],
                         current_status=status_filter)

@app.route('/renewals')
@login_required
def renewals():
    # Get leases expiring in next 90 days
    expiry_date = (datetime.now() + timedelta(days=90)).isoformat()
    
    renewals_data = supabase.table('leases').select(
        "*, tenants(first_name, last_name), units(unit_number, rent, properties(name))"
    ).lte('end_date', expiry_date).gte('end_date', datetime.now().isoformat()).execute()
    
    return render_template('renewals.html', 
                         renewals=renewals_data.data if renewals_data else [])

@app.route('/rental-applications')
@login_required
def rental_applications():
    applications = supabase.table('rental_applications').select(
        "*, properties(name), units(unit_number)"
    ).order('created_at', desc=True).execute()
    
    return render_template('rental_applications.html', 
                         applications=applications.data if applications else [])

@app.route('/metrics')
@login_required
def metrics():
    # Aggregate metrics data
    properties_count = supabase.table('properties').select("count", count='exact').execute()
    units_count = supabase.table('units').select("count", count='exact').execute()
    vacant_units = supabase.table('units').select("count", count='exact').eq('status', 'vacant').execute()
    active_leases = supabase.table('leases').select("count", count='exact').eq('status', 'active').execute()
    
    metrics_data = {
        'total_properties': properties_count.count if properties_count else 0,
        'total_units': units_count.count if units_count else 0,
        'vacant_units': vacant_units.count if vacant_units else 0,
        'active_leases': active_leases.count if active_leases else 0,
        'occupancy_rate': ((units_count.count - vacant_units.count) / units_count.count * 100) if units_count and units_count.count > 0 else 0
    }
    
    return render_template('metrics.html', metrics=metrics_data)

@app.route('/properties')
@login_required
def properties():
    properties_data = supabase.table('properties').select(
        "*, units(count)"
    ).execute()
    
    return render_template('properties.html', 
                         properties=properties_data.data if properties_data else [])

# API Routes
@app.route('/api/units/update-status', methods=['POST'])
@login_required
def update_unit_status():
    data = request.json
    unit_id = data.get('unit_id')
    status = data.get('status')
    
    result = supabase.table('units').update({
        'status': status,
        'updated_at': datetime.now().isoformat()
    }).eq('id', unit_id).execute()
    
    return jsonify({'success': True, 'data': result.data})

@app.route('/api/guest-cards/create', methods=['POST'])
@login_required
def create_guest_card():
    data = request.json
    
    guest_card = {
        'name': data.get('name'),
        'email': data.get('email'),
        'phone': data.get('phone'),
        'property_id': data.get('property_id'),
        'unit_id': data.get('unit_id'),
        'source': data.get('source'),
        'status': 'active',
        'created_at': datetime.now().isoformat()
    }
    
    result = supabase.table('guest_cards').insert(guest_card).execute()
    
    return jsonify({'success': True, 'data': result.data})

@app.route('/api/leases/countersign', methods=['POST'])
@login_required
def countersign_lease():
    lease_id = request.json.get('lease_id')
    
    result = supabase.table('leases').update({
        'status': 'executed',
        'countersigned_date': datetime.now().isoformat()
    }).eq('id', lease_id).execute()
    
    return jsonify({'success': True, 'data': result.data})

@app.route('/api/applications/update-status', methods=['POST'])
@login_required
def update_application_status():
    data = request.json
    app_id = data.get('application_id')
    status = data.get('status')
    
    result = supabase.table('rental_applications').update({
        'status': status,
        'updated_at': datetime.now().isoformat()
    }).eq('id', app_id).execute()
    
    return jsonify({'success': True, 'data': result.data})

# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Authenticate with Supabase
        try:
            user = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            session['user_id'] = user.user.id
            session['user_email'] = user.user.email
            return redirect(url_for('dashboard'))
        except Exception as e:
            return render_template('login.html', error="Invalid credentials")
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# Search functionality
@app.route('/search')
@login_required
def search():
    query = request.args.get('q', '')
    search_type = request.args.get('type', 'all')
    
    results = {
        'properties': [],
        'tenants': [],
        'units': []
    }
    
    if search_type in ['all', 'properties']:
        properties = supabase.table('properties').select("*").ilike('name', f'%{query}%').execute()
        results['properties'] = properties.data if properties else []
    
    if search_type in ['all', 'tenants']:
        tenants = supabase.table('tenants').select("*").or_(
            f"first_name.ilike.%{query}%,last_name.ilike.%{query}%"
        ).execute()
        results['tenants'] = tenants.data if tenants else []
    
    if search_type in ['all', 'units']:
        units = supabase.table('units').select("*, properties(name)").ilike('unit_number', f'%{query}%').execute()
        results['units'] = units.data if units else []
    
    return render_template('search_results.html', results=results, query=query)

if __name__ == '__main__':
    app.run(debug=True, port=5000)