# Property Management System - Flask Application
# File: app.py

from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_cors import CORS
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from supabase import create_client, Client
import secrets

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(16))
CORS(app)

# Your Supabase configuration
SUPABASE_URL = "https://sejebqdhcilwcpjpznep.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNlamVicWRoY2lsd2NwanB6bmVwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ0NTg5NjQsImV4cCI6MjA3MDAzNDk2NH0.vFM0Gr3QZF4MN3vtDGghjyCpnIkyC_mmUOOkVO3ahPQ"

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Test connection on startup
try:
    test = supabase.table('properties').select("count", count='exact').execute()
    print(f"✅ Connected to Supabase successfully!")
except Exception as e:
    print(f"⚠️ Supabase connection error: {e}")
    print("Make sure to run the SQL schema in your Supabase dashboard first!")

# Routes - No authentication required
@app.route('/')
@app.route('/dashboard')
def dashboard():
    # Fetch move-ins data
    move_ins = supabase.table('move_ins').select("*").execute()
    alerts = supabase.table('alerts').select("*").eq('active', True).execute()
    
    return render_template('dashboard.html', 
                         move_ins=move_ins.data if move_ins else [],
                         alerts=alerts.data if alerts else [])

@app.route('/vacancies')
def vacancies():
    # Fetch vacancies with property details
    vacancies_data = supabase.table('units').select(
        "*, properties(name, address, city, state, zip)"
    ).eq('status', 'vacant').execute()
    
    return render_template('vacancies.html', 
                         vacancies=vacancies_data.data if vacancies_data else [])

@app.route('/guest-cards')
def guest_cards():
    # Fetch guest cards (leads)
    guests = supabase.table('guest_cards').select(
        "*, properties(name), units(unit_number)"
    ).order('created_at', desc=True).execute()
    
    return render_template('guest_cards.html', 
                         guests=guests.data if guests else [])

@app.route('/leases')
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
def renewals():
    # Get leases expiring in next 90 days
    expiry_date = (datetime.now() + timedelta(days=90)).isoformat()
    
    renewals_data = supabase.table('leases').select(
        "*, tenants(first_name, last_name), units(unit_number, rent, properties(name))"
    ).lte('end_date', expiry_date).gte('end_date', datetime.now().isoformat()).execute()
    
    return render_template('renewals.html', 
                         renewals=renewals_data.data if renewals_data else [])

@app.route('/rental-applications')
def rental_applications():
    applications = supabase.table('rental_applications').select(
        "*, properties(name), units(unit_number)"
    ).order('created_at', desc=True).execute()
    
    return render_template('rental_applications.html', 
                         applications=applications.data if applications else [])

@app.route('/metrics')
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
def properties():
    properties_data = supabase.table('properties').select(
        "*, units(count)"
    ).execute()
    
    return render_template('properties.html', 
                         properties=properties_data.data if properties_data else [])

# API Routes - No authentication required for now
@app.route('/api/units/update-status', methods=['POST'])
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

@app.route('/api/guest-cards/bulk-update', methods=['POST'])
def bulk_update_guest_cards():
    data = request.json
    ids = data.get('ids', [])
    status = data.get('status')
    
    results = []
    for guest_id in ids:
        result = supabase.table('guest_cards').update({
            'status': status,
            'updated_at': datetime.now().isoformat()
        }).eq('id', guest_id).execute()
        results.append(result.data)
    
    return jsonify({'success': True, 'data': results})

@app.route('/api/leases/countersign', methods=['POST'])
def countersign_lease():
    lease_id = request.json.get('lease_id')
    
    result = supabase.table('leases').update({
        'status': 'executed',
        'countersigned_date': datetime.now().isoformat()
    }).eq('id', lease_id).execute()
    
    return jsonify({'success': True, 'data': result.data})

@app.route('/api/applications/update-status', methods=['POST'])
def update_application_status():
    data = request.json
    app_id = data.get('application_id')
    status = data.get('status')
    
    result = supabase.table('rental_applications').update({
        'status': status,
        'updated_at': datetime.now().isoformat()
    }).eq('id', app_id).execute()
    
    return jsonify({'success': True, 'data': result.data})

@app.route('/api/applications/create-lease', methods=['POST'])
def create_lease_from_application():
    app_id = request.json.get('application_id')
    
    # Get application details
    app_data = supabase.table('rental_applications').select("*").eq('id', app_id).execute()
    
    if app_data.data:
        app = app_data.data[0]
        # Create lease logic here
        # This is a placeholder - you'd need to create the actual lease
        
    return jsonify({'success': True, 'message': 'Lease creation initiated'})

@app.route('/api/alerts/dismiss', methods=['POST'])
def dismiss_alert():
    data = request.json
    alert_id = data.get('alert_id')
    permanent = data.get('permanent', False)
    
    if permanent:
        result = supabase.table('alerts').update({
            'active': False
        }).eq('id', alert_id).execute()
    else:
        # Just hide for 7 days (you could add a dismissed_until field)
        result = supabase.table('alerts').update({
            'active': False
        }).eq('id', alert_id).execute()
    
    return jsonify({'success': True})

@app.route('/api/units/post', methods=['POST'])
def post_unit():
    unit_id = request.json.get('unit_id')
    
    # Here you would implement logic to post to listing sites
    # This is a placeholder
    
    return jsonify({'success': True, 'message': 'Unit posted to listing sites'})

# Simple login page (for future implementation)
@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/quick-login', methods=['POST'])
def quick_login():
    # Simple one-button login - you can implement this later
    # For now, just redirect to dashboard
    session['logged_in'] = True
    return redirect(url_for('dashboard'))

# Search functionality
@app.route('/search')
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
    # Get port from environment variable for Cloud Run
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=False, host='0.0.0.0', port=port)