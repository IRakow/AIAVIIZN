# app.py
import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from functools import wraps
from datetime import datetime, timedelta
import secrets
from supabase import create_client, Client
import random
from decimal import Decimal
from calendar_api import calendar_api

app = Flask(__name__, static_folder='static', static_url_path='/static')
# Use a fixed secret key so sessions persist across deployments
# In production, this should be an environment variable
app.secret_key = 'aiviizn-secret-key-2025-keep-this-private-and-change-in-production'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

# Register the calendar API blueprint
app.register_blueprint(calendar_api)

# Supabase Configuration
SUPABASE_URL = "https://sejebqdhcilwcpjpznep.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNlamVicWRoY2lsd2NwanB6bmVwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ0NTg5NjQsImV4cCI6MjA3MDAzNDk2NH0.vFM0Gr3QZF4MN3vtDGghjyCpnIkyC_mmUOOkVO3ahPQ"

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:

            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/favicon.ico')
def favicon():
    return app.send_static_file('favicon.ico')

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        try:
            response = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if response.user:
                session.permanent = True  # Make session last for PERMANENT_SESSION_LIFETIME
                session['user_id'] = response.user.id
                session['email'] = response.user.email
                session['company'] = 'Your Company Name'
                
                flash('Welcome back!', 'success')
                return redirect(url_for('dashboard'))
                
        except Exception as e:
            # For testing - allow demo login
            if email == "admin@aiviizn.com" and password == "demo123":
                session.permanent = True  # Make session last for PERMANENT_SESSION_LIFETIME
                session['user_id'] = 'demo-user-id'
                session['email'] = email
                session['company'] = 'Test Company'
                flash('Welcome to AIVIIZN!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid email or password.', 'danger')
    
    return render_template('auth/login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # For now, just redirect to login
        # In production, you'd handle registration here
        flash('Registration feature coming soon! Please use demo login.', 'info')
        return redirect(url_for('login'))
    
    return render_template('auth/register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Dashboard data - exactly as you had it
    stats = {
        'move_ins': {
            'updated': 10,
            'finished': 25
        },
        'delinquencies': {
            '0_30': 185,
            '31_60': 31,
            '61_plus': 110
        },
        'maintenance': {
            'work_orders': {
                'new': 220,
                'assigned': 122,
                'completed': 1066
            }
        },
        'insurance': {
            'renters': 501,
            'liability': 825,
            'total_coverage': '91.93%'
        },
        'online_payments': {
            'percentage': 90,
            'units_paid': 92
        },
        'notifications': {
            'activities': 24,
            'bills': 0,
            'purchase_orders': 0
        },
        'leasing': {
            'guest_cards': 371,
            'applications': 64,
            'out_for_signing': 9,
            'ready_to_countersign': 2,
            'executed': 37,
            'expiring_this_month': 41,
            'expiring_next_month': 74,
            'posted_online': 36,
            'average_turnover': 66
        },
        'financials': {
            'total_income': 842569.29,
            'total_expense': 231078.74,
            'market_rent': 1109081.00
        }
    }
    
    recent_moveins = [
        {'tenant': 'Sainge, Samuel', 'unit': '-', 'property': '-', 'lease': 'Active', 'balance': 400.00, 'insurance': 'Not Covered', 'move_date': '07/25/2025'},
        {'tenant': 'Bell, Telia R.', 'unit': '-', 'property': '-', 'lease': 'Active', 'balance': 0.00, 'insurance': 'Not Covered', 'move_date': '08/01/2025'},
        {'tenant': 'Carlson, Eric A.', 'unit': 'Campbell Apartments - 3403 #4', 'property': 'Campbell Apartments - 3403 #4', 'lease': 'Fully Executed', 'balance': -727.74, 'insurance': 'Covered', 'move_date': '08/08/2025'},
    ]
    
    return render_template('dashboard.html', stats=stats, recent_moveins=recent_moveins)

@app.route('/inbox')
@login_required
def inbox():
    return render_template('inbox.html')

@app.route('/tenants')
@login_required
def tenants():
    tenants_data = [
        {'name': 'Arita, Elias', 'status': 'Current', 'property': '527 Oakley House / Stanion - 527 N Oakley Kansas City, MO 64123', 'unit': '', 'phone': '(816) 883-9832'},
        {'name': 'Artigus, Milagros', 'status': 'Current', 'property': 'Brentwood Park / Brentwood Park Ventures LLC - 3601-3619 Blue Ridge Blvd. Grandview, MO 64030', 'unit': '3615 #08', 'phone': '(816) 984-3234'},
        {'name': 'Barnes, Keisha', 'status': 'Past', 'property': 'Blue Ridge Manor - 3813 Duck Road Grandview, MO 64030', 'unit': '3811 11', 'phone': '(816) 988-1279'},
        {'name': 'Bell, Mariel', 'status': 'Past', 'property': '(BARR) Rock Ridge Ranch Apartments - 10561 Cypress Ave Kansas City, MO 64137', 'unit': '41A-R', 'phone': ''},
        {'name': 'Burns, Kathy', 'status': 'Current', 'property': '(BARR) Rock Ridge Ranch Apartments - 10561 Cypress Ave Kansas City, MO 64137', 'unit': '39A', 'phone': ''},
        {'name': 'Byers-Boyd, Angela', 'status': 'Current', 'property': '(BARR) Rock Ridge Ranch Apartments - 10561 Cypress Ave Kansas City, MO 64137', 'unit': '23B', 'phone': '(816) 359-0719'},
        {'name': 'Clark, Destiny', 'status': 'Past', 'property': '(BARR) Rock Ridge Ranch Apartments - 10561 Cypress Ave Kansas City, MO 64137', 'unit': '41B', 'phone': ''},
        {'name': 'Clark, Hakai', 'status': 'Past', 'property': '(BARR) Rock Ridge Ranch Apartments - 10561 Cypress Ave Kansas City, MO 64137', 'unit': '41B', 'phone': ''},
        {'name': 'Cunningham, Domeruis', 'status': 'Past', 'property': '(BARR) Rock Ridge Ranch Apartments - 10561 Cypress Ave Kansas City, MO 64137', 'unit': '11B', 'phone': '(816) 491-1644'},
        {'name': 'Donley, Armani', 'status': 'Past', 'property': '(BARR) Rock Ridge Ranch Apartments - 10561 Cypress Ave Kansas City, MO 64137', 'unit': '41A-R', 'phone': ''},
        {'name': 'Enamorado, Raul', 'status': 'Current', 'property': '(BARR) Rock Ridge Ranch Apartments - 10561 Cypress Ave Kansas City, MO 64137', 'unit': '21A-R', 'phone': '(816) 406-4866'},
        {'name': 'Flanagan, Savion', 'status': 'Past', 'property': '(BARR) Rock Ridge Ranch Apartments - 10561 Cypress Ave Kansas City, MO 64137', 'unit': '41B', 'phone': '(816) 888-0774'},
        {'name': 'Gagne, Alexander', 'status': 'Current', 'property': '(BARR) Rock Ridge Ranch Apartments - 10561 Cypress Ave Kansas City, MO 64137', 'unit': '43B', 'phone': '(816) 666-0338'},
        {'name': 'Gonzalez Roa, Mario', 'status': 'Current', 'property': 'Lodge Apartments - 600 SE 291 Hwy Lees Summit, MO 64063', 'unit': '106', 'phone': '(816) 394-1782'},
    ]
    
    return render_template('people/tenants.html', tenants=tenants_data)

@app.route('/owners')
@login_required
def owners():
    owners_data = [
        {'name': '3825 Baltimore / Finkelstein', 'company': '3825 Baltimore / Finkelstein', 'phone': '(650) 922-0967', 'email': 'dfinkelstein@dgflaw.com'},
        {'name': 'AC Equity, LLC', 'company': 'AC Equity, LLC', 'phone': '(816) 492-0644', 'email': 'mitch.d.case@gmail.com'},
        {'name': 'Antioch HS, LLC', 'company': 'Antioch HS, LLC', 'phone': '(714) 486-4200', 'email': 'jjokechoi@gmail.com'},
        {'name': 'Best Beach LLC', 'company': 'Best Beach LLC', 'phone': '', 'email': 'john619@outlook.com'},
        {'name': 'Blue Ridge KC LLC', 'company': 'Blue Ridge KC LLC', 'phone': '(816) 517-1138', 'email': 'jbrandmeyer@fambran.com'},
        {'name': 'Booth Apartments LLC', 'company': 'Booth Apartments LLC', 'phone': '', 'email': 'michael.sullivan@berkadia.com'},
        {'name': 'Brancato, Marion', 'company': 'JoMar Apartments LLc / Marion Brancato', 'phone': '', 'email': 'rubyttara@me.com'},
        {'name': 'Brentwood Park Ventures LLC', 'company': 'Brentwood Park Ventures LLC', 'phone': '', 'email': 'mjvaranka@gmail.com'},
        {'name': 'Cory Finley / Charlotte Park Apartments, LLC', 'company': 'Cory Finley / Charlotte Park Apartments, LLC', 'phone': '(816) 550-5877', 'email': 'coryfinley@gmail.com'},
        {'name': 'D&T LLC', 'company': 'D&T LLC', 'phone': '(503) 260-5477', 'email': 'mrt51@icloud.com'},
        {'name': 'David Montgomery / 40th st property', 'company': 'David Montgomery / 40th st property', 'phone': '(785) 546-2606', 'email': 'davidcoemontgomery@gmail.com'},
        {'name': 'DW Gene Field LLC', 'company': 'DW Gene Field LLC', 'phone': '', 'email': 'rldeutsch@gmail.com'},
        {'name': 'DW Investments LLC', 'company': 'DW Investments LLC', 'phone': '(785) 249-0379', 'email': 'rldeutsch@gmail.com'},
    ]
    
    return render_template('people/owners.html', owners=owners_data)

@app.route('/vendors')
@login_required
def vendors():
    vendors_data = [
        {'name': '1-800 Water Damage Of Kansas City', 'address': '2581 SW Highway 169 Trimble MO 64492', 'trades': '', 'phone': '(816) 7850-5023', 'email': 'dave.johnson@1800waterdamage.com'},
        {'name': '1245 Consulting', 'address': '3423 Limestone Sky Court Houston TX 77059', 'trades': '', 'phone': '(713) 927-0992', 'email': ''},
        {'name': '12520 Grandview Rd. House / 12520 Grandview', 'address': '11002 W 143rd Terr. Overland Park, Kansas 66221', 'trades': '', 'phone': '(913) 980-9902', 'email': 'tladish@celticproperties.net'},
        {'name': '40th St Property Escrow', 'address': '', 'trades': '', 'phone': '', 'email': ''},
        {'name': '435 Roofing, Inc', 'address': '9265 Flint St Overland Park KS 66214', 'trades': '', 'phone': '(913) 444-0725', 'email': 'info@435roofing.com'},
        {'name': '5M Restoration LLC', 'address': '2773 Vernon Rd Prescott KS 66767', 'trades': '', 'phone': '', 'email': ''},
        {'name': '7 - 11', 'address': '', 'trades': '', 'phone': '', 'email': ''},
        {'name': '84 Lumber', 'address': '', 'trades': '', 'phone': '', 'email': ''},
        {'name': 'A&M Heating And Cooling Inc', 'address': '513 South 4th St. St Joseph MO 64501', 'trades': '', 'phone': '(816) 279-5215', 'email': 'amhcooling@gmail.com'},
        {'name': 'A-1 Sewer & Septic Services Inc.', 'address': '1891 Merriam Ln, Kansas City KS 66106', 'trades': 'Plumbing', 'phone': '(913) 631-5201', 'email': ''},
        {'name': 'A.D. Heating And Air Services LLC', 'address': '7204 Lydia Ave Kansas City MO 64138', 'trades': '', 'phone': '(816) 456-5254', 'email': ''},
        {'name': 'AAA Disposal Service', 'address': 'P.O. Box 109 Oak Grove MO 64075', 'trades': '', 'phone': '(816) 650-3180', 'email': 'aaadisposal@gmail.com'},
    ]
    
    return render_template('maintenance/vendors.html', vendors=vendors_data)

@app.route('/properties')
@login_required
def properties():
    properties_data = [
        {'name': '(BARR) Rock Ridge Ranch Apartments', 'address': '10561 Cypress Ave Kansas City, MO 64137', 'type': 'Multi-Family', 
         'units_count': 75, 'units': [{'status': 'vacant'} for _ in range(5)] + [{'status': 'occupied'} for _ in range(70)], 'owners': 'Rock Ridge Ranch / Rock Ridge Ranch'},
        {'name': '12520 Grandview Rd. House', 'address': '12520 Grandview Rd Grandview, MO 64030', 'type': 'Single-Family', 
         'units_count': 1, 'units': [{'status': 'occupied'}], 'owners': 'HLF Investments MO LLC / Keith S...'},
        {'name': '340 Belmont House / Stanion', 'address': '340 N Belmont Blvd Kansas City, MO 34123', 'type': 'Single-Family', 
         'units_count': 1, 'units': [{'status': 'occupied'}], 'owners': 'Judson Stanion'},
        {'name': '3815 Shawnee House / Stanion', 'address': '3815 Shawnee Dr. Kansas City, KS 66106', 'type': 'Single-Family', 
         'units_count': 1, 'units': [{'status': 'occupied'}], 'owners': 'Judson Stanion'},
        {'name': '3825 Baltimore', 'address': '3825 Baltimore Kansas City, MO 64111', 'type': 'Multi-Family', 
         'units_count': 7, 'units': [{'status': 'vacant'} for _ in range(2)] + [{'status': 'occupied'} for _ in range(5)], 'owners': '3825 Baltimore / Finkelstein'},
        {'name': '4012 W. 75th Street / TLAR LLC', 'address': '4012 W. 75th Street Prairie Village, KS 66208', 'type': 'Single-Family', 
         'units_count': 1, 'units': [{'status': 'occupied'}], 'owners': 'Greg Sweat'},
        {'name': '40th Street Apartments', 'address': '1109-1111 W. 40th St. Kansas City, MO 64111', 'type': 'Multi-Family', 
         'units_count': 6, 'units': [{'status': 'vacant'} for _ in range(1)] + [{'status': 'occupied'} for _ in range(5)], 'owners': 'David Montgomery / 40th st property'},
        {'name': '4111 Booth House', 'address': '4111 Booth Kansas City, KS 66103', 'type': 'Single-Family', 
         'units_count': 1, 'units': [{'status': 'occupied'}], 'owners': 'KC KINGS LLC'},
        {'name': '4451 Francis / Francis House', 'address': '4451 Francis St. Kansas City, KS 66103', 'type': 'Single-Family', 
         'units_count': 1, 'units': [{'status': 'occupied'}], 'owners': 'Gregg Sullivan / 4451 Francis House'},
        {'name': '527 Oakley House / Stanion', 'address': '527 N Oakley Kansas City, MO 64123', 'type': 'Single-Family', 
         'units_count': 1, 'units': [{'status': 'occupied'}], 'owners': 'Judson Stanion'},
    ]
    
    return render_template('properties/properties.html', properties=properties_data)

# Leasing Routes
@app.route('/leasing/vacancies')
@login_required
def vacancies():
    vacancies_data = [
        {
            'properties': {
                'name': 'Gene Field Apts',
                'address': '3515 Gene Field Rd',
                'city': 'St. Joseph',
                'state': 'MO',
                'zip': '64506'
            },
            'unit_number': '10-02',
            'bedrooms': 1,
            'bathrooms': 1,
            'sqft': 731,
            'rent': 546,
            'available': 'Now',
            'days_vacant': 1062,
            'website': False,
            'internet': False,
            'premium': False
        },
        {
            'properties': {
                'name': 'Gene Field Apts',
                'address': '3515 Gene Field Rd',
                'city': 'St. Joseph',
                'state': 'MO',
                'zip': '64506'
            },
            'unit_number': '10-04',
            'bedrooms': 1,
            'bathrooms': 1,
            'sqft': 731,
            'rent': 546,
            'available': 'Now',
            'days_vacant': 896,
            'website': False,
            'internet': False,
            'premium': False
        },
        {
            'properties': {
                'name': 'Gene Field Apts',
                'address': '3515 Gene Field Rd',
                'city': 'St. Joseph',
                'state': 'MO',
                'zip': '64506'
            },
            'unit_number': '10-05',
            'bedrooms': 1,
            'bathrooms': 1,
            'sqft': 731,
            'rent': 546,
            'available': 'Now',
            'days_vacant': 804,
            'website': False,
            'internet': False,
            'premium': False
        },
        {
            'properties': {
                'name': 'Gene Field Apts',
                'address': '3515 Gene Field Rd',
                'city': 'St. Joseph',
                'state': 'MO',
                'zip': '64506'
            },
            'unit_number': '10-01',
            'bedrooms': 1,
            'bathrooms': 1,
            'sqft': 731,
            'rent': 573,
            'available': 'Now',
            'days_vacant': 753,
            'website': False,
            'internet': False,
            'premium': False
        }
    ]
    
    return render_template('leasing/vacancies.html', vacancies=vacancies_data)

@app.route('/leasing/guest-cards')
@login_required
def guest_cards():
    guest_cards_data = [
        {'name': 'Phillips, Stevie', 'property': '(BARR) Rock Ridge Ranch Apartments\nWalnut Ridge Apts', 'activity_date': '08/07/2025', 'email_sent': 'Auto-Response Email Sent\n08/07/2025', 'source': 'EveryApartment'},
        {'name': 'Cutroni, Doreen', 'property': 'Indian Creek Townhomes - 11622 Bluejacket St.', 'activity_date': '08/07/2025', 'email_sent': 'Auto-Response Email Sent\n08/07/2025', 'source': 'Rent.'},
        {'name': 'Pool, Josephine', 'property': 'Summit Apartments', 'activity_date': '08/07/2025', 'email_sent': 'Pre-qualification Form Submitted\n08/07/2025', 'source': 'Zillow Rental Network'},
        {'name': 'Raja, Rajput', 'property': 'Lodge Apartments', 'activity_date': '08/07/2025', 'email_sent': 'Auto-Response Email Sent\n08/07/2025', 'source': 'Apartments.com'},
        {'name': 'Hall, Isaiah', 'property': 'Barton Crossing / W&W Properties LLC - 6117 #1B', 'activity_date': '08/07/2025', 'email_sent': 'Showing\n08/11/2025', 'source': 'Facebook Marketplace'},
        {'name': 'Thomas, Mary', 'property': 'Longmeadow Apartments - #15C', 'activity_date': '08/07/2025', 'email_sent': 'Showing\n08/11/2025', 'source': 'call'},
    ]
    
    return render_template('leasing/guest_cards.html', guest_cards=guest_cards_data)

@app.route('/leasing/rental-applications')
@login_required
def rental_applications():
    applications_data = [
        {
            'property': '(BARR) Rock Ridge Ranch Apartments - 59A',
            'address': '10559 Cypress Ave\n59A\nKansas City, MO 64137',
            'rent': 785,
            'vacant': 'Not Vacant',
            'applicants': [
                {'name': 'Reiman Ventura Sarmiento', 'move_in': '08/17/2025', 'status': 'Converting', 'history': 'None Requested', 'received': '08/01/2025 12:39 AM'}
            ]
        },
        {
            'property': '(BARR) Rock Ridge Ranch Apartments - 69A-R',
            'address': '10569 Cypress Ave\n69A\nKansas City, MO 64137',
            'rent': 1175,
            'vacant': 'Not Vacant',
            'applicants': [
                {'name': 'Samuel Sainge', 'move_in': '07/25/2025', 'status': 'Converting', 'history': 'None Requested', 'received': '07/14/2025 04:48 PM'},
                {'name': 'RickSonder Sainge', 'move_in': '07/25/2025', 'status': 'Converting', 'history': 'None Requested', 'received': '07/14/2025 05:49 PM'},
                {'name': 'Balnette Destine', 'move_in': '07/25/2025', 'status': 'Converting', 'history': 'None Requested', 'received': '07/14/2025 06:44 PM'},
                {'name': 'Marcel L. Goodwin', 'move_in': '08/04/2025', 'status': 'Converting', 'history': 'None Requested', 'received': '07/23/2025 11:21 PM'},
                {'name': 'Kenia V. Robles Hidalgo', 'move_in': '08/01/2025', 'status': 'Decision Pending', 'history': 'None Requested', 'received': '07/26/2025 12:22 PM'}
            ]
        }
    ]
    
    return render_template('leasing/rental_applications.html', applications=applications_data)

@app.route('/leasing/leases')
@login_required
def leases():
    leases_data = [
        {'tenants': 'Chris Minear', 'unit': 'Gene Field Apts / DW Gene Field LLC / Ryan Deutsch - 01-02', 'generation_date': '03/12/2025 10:06 AM', 'status': 'Ready to Countersign'},
        {'tenants': 'Kianna I. Evans', 'unit': 'Castle Row Apartments - #5B', 'generation_date': '08/01/2025 04:48 PM', 'status': 'Ready to Countersign'},
    ]
    
    return render_template('leasing/leases.html', leases=leases_data)

@app.route('/leasing/renewals')
@login_required
def renewals():
    renewals_data = [
        {'units': {'properties': {'name': '(BARR) Rock Ridge Ranch Apartments'}, 'unit_number': '...', 'rent': 695.00}, 'tenants': 'Eugene Boyd\nAngela Byers-Boyd', 'expiration': '--', 'proposed_rent': None, 'status': 'Out For Signing'},
        {'units': {'properties': {'name': '3825 Baltimore'}, 'unit_number': '3825 #03', 'rent': 900.00}, 'tenants': 'Sarita M. Vangundy', 'expiration': '--', 'proposed_rent': None, 'status': 'Out For Signing'},
        {'units': {'properties': {'name': 'Blue Ridge Manor'}, 'unit_number': '3809.5', 'rent': 950.00}, 'tenants': 'Yoilbeth Z. Madrid\nBenito V. Ronquillo', 'expiration': '--', 'proposed_rent': None, 'status': 'Eligible'},
        {'units': {'properties': {'name': 'Lodge Apartments'}, 'unit_number': '102', 'rent': 950.00}, 'tenants': 'Joe Edwards', 'expiration': '--', 'proposed_rent': 950.00, 'status': 'Eligible'},
        {'units': {'properties': {'name': 'Longmeadow Apartments'}, 'unit_number': '#21C', 'rent': 785.00}, 'tenants': 'Tara L. Boenig', 'expiration': '--', 'proposed_rent': 785.00, 'status': 'MTM 07/16/2025'},
        {'units': {'properties': {'name': 'West Plaza'}, 'unit_number': '1709', 'rent': 800.00}, 'tenants': 'CPM 1709 Property Management', 'expiration': '--', 'proposed_rent': None, 'status': 'Eligible'},
    ]
    
    return render_template('leasing/renewals.html', renewals=renewals_data)

@app.route('/leasing/metrics')
@login_required
def leasing_metrics():
    metrics_data = {
        'occupancy_rate': 90.53,
        'units_vacant': 115,
        'demand': {
            'guest_cards': 93,
            'applications': 11,
            'conversion_rate': 11.83
        },
        'occupancy': {
            'current': 90.53,
            'units_vacant': 115
        },
        'pricing': {
            'projected_occupancy': [],
            'projected_vacancy': [],
            'price_per_sqft': []
        },
        'box_score': {
            'properties': []
        }
    }
    
    return render_template('leasing/metrics.html', metrics=metrics_data)

@app.route('/leasing/signals')
@login_required
def signals():
    return render_template('leasing/signals.html')

# Lease Documents Routes
@app.route('/leasing/lease_documents')
@login_required
def lease_documents():
    return render_template('leasing/lease_documents.html')

@app.route('/leasing/lease_documents/out_for_signing')
@login_required
def lease_documents_out_for_signing():
    return render_template('leasing/lease_documents_out_for_signing.html')

@app.route('/leasing/lease_documents/printed')
@login_required
def lease_documents_printed():
    return render_template('leasing/lease_documents_printed.html')

# Maintenance Routes
@app.route('/maintenance/work-orders')
@login_required
def work_orders():
    work_orders_data = [
        {'id': '113231-1', 'status': 'NEW INTERNAL', 'property': 'West Plaza', 'address': '1705/1707 Yarn Social, LLC', 'description': 'Water leaking down wall from hvac . She will be in here space at 9am', 'vendor': 'Vendor/Assignee --', 'created': 'Aug 7, 2025'},
        {'id': '113230-1', 'status': 'NEW RESIDENT', 'property': 'Longmeadow Apartments', 'address': '#19A Larry Davis', 'description': 'I have water leaking from my AC unit, and it is causing mold in closet. this needs to be addressed ...', 'vendor': 'Vendor/Assignee --', 'created': 'Aug 7, 2025'},
        {'id': '113229-1', 'status': 'NEW RESIDENT', 'property': 'Norclay Apartments', 'address': '4655-1 Amy L. Lutgen', 'description': 'Kitchen faucet leaking under the sink when water turned on', 'vendor': 'Vendor/Assignee --', 'created': 'Aug 7, 2025'},
        {'id': '113228-1', 'status': 'NEW UNIT TURN', 'property': 'Brentwood Park / Brentwood Park ...', 'address': '3617 #01 Vacant', 'description': 'Inspection Areas: Living Room - Paint Make Ready for paint Bedroom 1 - Paint Make ready for ...', 'vendor': 'Vendor/Assignee --', 'created': 'Aug 7, 2025'},
        {'id': '113227-1', 'status': 'NEW UNIT TURN', 'property': 'Brentwood Park / Brentwood Park ...', 'address': '3605 #04 Vacant', 'description': 'Inspection Areas: Kitchen - Refrigerator Check fridge damage and missing shelves Kitchen - ...', 'vendor': 'Vendor/Assignee --', 'created': 'Aug 7, 2025'},
        {'id': '113226-1', 'status': 'NEW RESIDENT', 'property': 'Randall Court Ventures', 'address': '6724-9 Kayeson O. Slayden', 'description': 'The toilet moves when you sit on it. It\'s always down this since I\'ve lived here but someone told me it ...', 'vendor': 'Vendor/Assignee --', 'created': 'Aug 7, 2025'},
        {'id': '113225-1', 'status': 'NEW RESIDENT', 'property': 'Randall Court Ventures', 'address': '6724-9 Kayeson O. Slayden', 'description': 'Kitchen light out', 'vendor': 'Vendor/Assignee --', 'created': 'Aug 7, 2025'},
    ]
    
    return render_template('maintenance/work_orders.html', work_orders=work_orders_data)

@app.route('/maintenance/recurring-work-orders')
@login_required
def recurring_work_orders():
    recurring_data = [
        {'vendor': '--', 'property': '(BARR) Rock Ridge Ranch Apartments', 'repeats': 'Monthly', 'description': 'Walk EVERY SINGLE UNIT for a housekeeping inspection- che...'},
        {'vendor': '--', 'property': '(BARR) Rock Ridge Ranch Apartments', 'repeats': 'Monthly', 'description': 'Snake out House Drains in each Building to ensure no back...'},
        {'vendor': '--', 'property': '(BARR) Rock Ridge Ranch Apartments', 'repeats': 'Monthly', 'description': 'Replace all furnace filters in each unit and check smoke ...'},
        {'vendor': '--', 'property': '(BARR) Rock Ridge Ranch Apartments', 'repeats': 'Monthly', 'description': 'Common Areas/Interior/Exterior Walk Through ANNUALLY 1ST ...'},
        {'vendor': '--', 'property': '(BARR) Rock Ridge Ranch Apartments', 'repeats': 'Bi-weekly', 'description': 'Clean Laundry Rooms'},
        {'vendor': 'AIVIIZN', 'property': '3825 Baltimore', 'repeats': 'Bi-weekly', 'description': 'Route Clean'},
        {'vendor': 'AIVIIZN', 'property': '40th Street Apartments', 'repeats': 'Bi-weekly', 'description': 'Route Clean'},
        {'vendor': 'Daryl Grovenburg', 'property': 'Aspen Village Apartments', 'repeats': 'Never (Must Post Manually)', 'description': 'Pool maintenance on a daily basis. 45 minutes daily ...'},
        {'vendor': '--', 'property': 'Barton Crossing / W&W Properties LLC', 'repeats': 'Never (Must Post Manually)', 'description': 'Clean grounds. pick up any trash, empty any common area t...'},
        {'vendor': '--', 'property': 'Blue Ridge Manor', 'repeats': 'Never (Must Post Manually)', 'description': 'Make ready checklist template: *Keypad code needs chan...'},
    ]
    
    return render_template('maintenance/recurring_work_orders.html', recurring=recurring_data)

@app.route('/maintenance/inspections')
@login_required
def inspections():
    inspections_data = [
        {'date': '08/07/25', 'name': 'Brentwood Park', 'unit': 'Brentwood Park / Brentwood Park Ventures LLC - 3617 #01', 'type': 'Inspection', 'flags': 23},
        {'date': '08/07/25', 'name': 'Brentwood Park', 'unit': 'Brentwood Park / Brentwood Park Ventures LLC - 3605 #04', 'type': 'Inspection', 'flags': 20},
        {'date': '08/04/25', 'name': 'Make Ready Inspection - 3825 Baltimore #5', 'unit': '3825 Baltimore - 3825 #05', 'type': 'Inspection', 'flags': 13},
        {'date': '08/04/25', 'name': 'Make Ready Inspection - 3827 Baltimore #2', 'unit': '3825 Baltimore - 3827 #02', 'type': 'Inspection', 'flags': 10},
        {'date': '08/04/25', 'name': 'Make Ready Inspection - Pearl 4303 #4', 'unit': 'Pearl St. Apts / GBA1947 LLC - 4303-4', 'type': 'Inspection', 'flags': 20},
        {'date': '08/04/25', 'name': 'Make Ready Inspection - RRR 61A', 'unit': '(BARR) Rock Ridge Ranch Apartments - 61A', 'type': 'Inspection', 'flags': 31},
        {'date': '08/04/25', 'name': 'Westport 4034#5', 'unit': 'Westport Plaza Apts', 'type': 'Inspection', 'flags': 13},
        {'date': '08/01/25', 'name': '303U MOVE OUT INSPECTION 1/1', 'unit': 'Villas of Mur-Len / TSI Villas of Mur-Len - 303 P', 'type': 'Inspection', 'flags': 23},
        {'date': '07/30/25', 'name': 'Walnut Ridge 6122 D', 'unit': 'Walnut Ridge Apts', 'type': 'Inspection', 'flags': 14},
        {'date': '07/25/25', 'name': 'Walnut 6120 B', 'unit': 'Walnut Ridge Apts', 'type': 'Inspection', 'flags': 17},
    ]
    
    return render_template('maintenance/inspections.html', inspections=inspections_data)

@app.route('/maintenance/unit-turns')
@login_required
def unit_turns():
    unit_turns_data = [
        {
            'property': 'Flats at Walnut / Flats at Walnut LLC - 4231 C - DOWN',
            'move_out': '5/31/2021',
            'move_in': '--',
            'target_date': '6/10/2021 (4 years ago)',
            'status': 'In Progress',
            'maintenance': '--',
            'paint': '--',
            'appliances': '--',
            'floors': '--',
            'other': '--',
            'housekeeping': '--',
            'keys': '--'
        },
        {
            'property': 'Flats at Walnut / Flats at Walnut LLC - 4239 D - DOWN',
            'move_out': '5/31/2021',
            'move_in': '--',
            'target_date': '6/10/2021 (4 years ago)',
            'status': 'In Progress',
            'maintenance': '--',
            'paint': '--',
            'appliances': '--',
            'floors': '--',
            'other': '--',
            'housekeeping': '--',
            'keys': '--'
        },
        {
            'property': 'Flats at Walnut / Flats at Walnut LLC - 4231 B - DOWN',
            'move_out': '5/31/2021',
            'move_in': '--',
            'target_date': '6/10/2021 (4 years ago)',
            'status': 'In Progress',
            'maintenance': '--',
            'paint': '--',
            'appliances': '--',
            'floors': '--',
            'other': '--',
            'housekeeping': '--',
            'keys': '--'
        },
        {
            'property': 'Flats at Walnut / Flats at Walnut LLC - 4231 F - DOWN',
            'move_out': '5/31/2021',
            'move_in': '--',
            'target_date': '6/10/2021 (4 years ago)',
            'status': 'In Progress',
            'maintenance': '--',
            'paint': '--',
            'appliances': '--',
            'floors': '--',
            'other': '--',
            'housekeeping': '--',
            'keys': '--'
        }
    ]
    
    return render_template('maintenance/unit_turns.html', unit_turns=unit_turns_data)

@app.route('/maintenance/projects')
@login_required
def projects():
    return render_template('maintenance/projects.html')

@app.route('/maintenance/purchase-orders')
@login_required
def purchase_orders():
    return render_template('maintenance/purchase_orders.html')

@app.route('/maintenance/inventory')
@login_required
def inventory():
    return render_template('maintenance/inventory.html')

@app.route('/maintenance/fixed-assets')
@login_required
def fixed_assets():
    fixed_assets_data = [
        {'property': 'Brentwood Park / Brentwood Park Ventures LLC - 3605 #06', 'asset_id': '292', 'type': 'Hot Water Heater', 'status': 'Installed', 'placed': '12/31/2024', 'warranty': '01/31/2026'},
        {'property': 'Brentwood Park / Brentwood Park Ventures LLC - 3607 #09', 'asset_id': '293', 'type': 'Hot Water Heater', 'status': 'Installed', 'placed': '12/31/2024', 'warranty': '12/31/2025'},
        {'property': 'Gene Field Apts / DW Gene Field LLC / Ryan Deutsch - 08-05', 'asset_id': '108', 'type': 'Flooring', 'status': 'Installed', 'placed': '12/31/2021', 'warranty': ''},
        {'property': 'Brentwood Park / Brentwood Park Ventures LLC - 3619 #09', 'asset_id': '291', 'type': 'Refrigerator', 'status': 'Installed', 'placed': '12/23/2024', 'warranty': '12/23/2025'},
        {'property': 'Gene Field Apts / DW Gene Field LLC / Ryan Deutsch - 09-06 Market', 'asset_id': '109', 'type': 'Flooring', 'status': 'Installed', 'placed': '12/21/2021', 'warranty': ''},
        {'property': 'Brentwood Park / Brentwood Park Ventures LLC - 3615 #04', 'asset_id': '209', 'type': 'Oven', 'status': 'Installed', 'placed': '12/14/2022', 'warranty': ''},
        {'property': 'Lodge Apartments - 201', 'asset_id': '288', 'type': 'Oven', 'status': 'Installed', 'placed': '12/12/2024', 'warranty': ''},
        {'property': 'Brentwood Park / Brentwood Park Ventures LLC - 3615 #03', 'asset_id': '290', 'type': 'Oven', 'status': 'Installed', 'placed': '12/10/2024', 'warranty': '12/10/2025'},
        {'property': 'Brentwood Park / Brentwood Park Ventures LLC - 3619 #09', 'asset_id': '289', 'type': 'Oven', 'status': '', 'placed': '12/09/2024', 'warranty': '12/09/2025'},
        {'property': 'Kaanapali Apartments / FinFreedom LLC', 'asset_id': '50', 'type': 'Flooring', 'status': 'Installed', 'placed': '12/01/2019', 'warranty': ''},
    ]
    
    return render_template('maintenance/fixed_assets.html', fixed_assets=fixed_assets_data)

@app.route('/maintenance/smart-maintenance')
@login_required
def smart_maintenance():
    return render_template('maintenance/smart_maintenance.html')

# Accounting Routes
@app.route('/accounting/receivables')
@login_required
def receivables():
    return render_template('accounting/receivables.html')

@app.route('/accounting/payables')
@login_required
def payables():
    payables_data = [
        {'payee': 'Fair & Square Roof Repair, LLC', 'ref': '800', 'bill_date': '08/07/2025', 'for': 'Longmeadow Apartments', 'account': '3108: capital expense Roofing', 'due_date': '08/07/2025', 'amount': 1179.81, 'status': 'Paid', 'cash_account': '1150: Cash in Bank'},
        {'payee': 'Fair & Square Roof Repair, LLC', 'ref': '795', 'bill_date': '08/07/2025', 'for': 'Indian Creek Townhomes', 'account': '6780: Roof Repairs/ Supplies', 'due_date': '08/07/2025', 'amount': 300.00, 'status': 'Paid', 'cash_account': '1150: Cash in Bank'},
        {'payee': 'Metro Appliances', 'ref': '909457', 'bill_date': '08/06/2025', 'for': 'Brentwood Park / Brentwood Park Ventures LLC - 3619 #03', 'account': '3107: capital expense Appliance', 'due_date': '08/06/2025', 'amount': 651.27, 'status': 'Paid', 'cash_account': '1150: Cash in Bank'},
        {'payee': 'Walgreens', 'ref': '--', 'bill_date': '08/06/2025', 'for': 'Brentwood Park / Brentwood Park Ventures LLC', 'account': '7420: Office Supplies', 'due_date': '08/06/2025', 'amount': 13.03, 'status': 'Paid', 'cash_account': '1150: Cash in Bank'},
        {'payee': 'Fair & Square Roof Repair, LLC', 'ref': '799', 'bill_date': '08/06/2025', 'for': 'Brentwood Park / Brentwood Park Ventures LLC', 'account': '7443: Vendor Maintenance', 'due_date': '08/06/2025', 'amount': 300.00, 'status': 'Paid', 'cash_account': '1150: Cash in Bank'},
        {'payee': 'Lowes Home Improvement', 'ref': '97004 0825', 'bill_date': '08/05/2025', 'for': 'Villas of Mur-Len / TSI Villas of Mur-Len - 306 P', 'account': '7440: Maintenance Materials', 'due_date': '08/05/2025', 'amount': 43.77, 'status': 'Paid', 'cash_account': '1150: Cash in Bank'},
        {'payee': 'Lowes Home Improvement', 'ref': '97668 0825', 'bill_date': '08/05/2025', 'for': 'Villas of Mur-Len / TSI Villas of Mur-Len - 516 C', 'account': '7440: Maintenance Materials', 'due_date': '08/05/2025', 'amount': 43.77, 'status': 'Paid', 'cash_account': '1150: Cash in Bank'},
        {'payee': 'True Value Hardware', 'ref': '113130.1 0825', 'bill_date': '08/05/2025', 'for': 'Villas of Mur-Len / TSI Villas of Mur-Len - 127 P', 'account': '7440: Maintenance Materials', 'due_date': '08/05/2025', 'amount': 10.50, 'status': 'Paid', 'cash_account': '1150: Cash in Bank'},
    ]
    
    return render_template('accounting/payables.html', payables=payables_data)

@app.route('/accounting/bank-accounts')
@login_required
def bank_accounts():
    bank_accounts_data = [
        {'name': '3825 Baltimore / Finkelstein', 'bank': 'US Bank', 'account_number': '********2041', 'last_reconciliation': '07/31/2025', 'payments_enabled': 'ENABLED', 'auto_reconciliation': 'PLAID'},
        {'name': '40th St Escrow', 'bank': 'US Bank', 'account_number': '********2206', 'last_reconciliation': '11/30/2021', 'payments_enabled': 'NOT ENABLED', 'auto_reconciliation': 'PLAID'},
        {'name': '40th st property', 'bank': 'US Bank', 'account_number': '********3228', 'last_reconciliation': '06/30/2025', 'payments_enabled': 'ENABLED', 'auto_reconciliation': 'PLAID'},
        {'name': 'AC Equity, LLC / Highland', 'bank': 'US Bank', 'account_number': '********2234', 'last_reconciliation': '07/31/2025', 'payments_enabled': 'ENABLED', 'auto_reconciliation': 'PLAID'},
        {'name': 'Aspen Village Apts/EM2 Investments, LLC', 'bank': 'Bank of America', 'account_number': '********0610', 'last_reconciliation': '06/30/2025', 'payments_enabled': 'ENABLED', 'auto_reconciliation': 'NOT ENABLED'},
        {'name': 'Barton Crossing/Flint', 'bank': 'Arvest', 'account_number': '****1304', 'last_reconciliation': '06/30/2025', 'payments_enabled': 'ENABLED', 'auto_reconciliation': 'PLAID'},
        {'name': 'Blue Ridge Manor', 'bank': 'US Bank', 'account_number': '********1556', 'last_reconciliation': '07/31/2025', 'payments_enabled': 'ENABLED', 'auto_reconciliation': 'PLAID'},
        {'name': 'Booth Apartments / Michael Sullivan', 'bank': 'US Bank', 'account_number': '********6994', 'last_reconciliation': '07/31/2025', 'payments_enabled': 'ENABLED', 'auto_reconciliation': 'PLAID'},
        {'name': 'Booth Apts / FBB', 'bank': 'First Business Bank', 'account_number': '****3934', 'last_reconciliation': '08/01/2020', 'payments_enabled': 'NOT ENABLED', 'auto_reconciliation': 'NOT ENABLED'},
        {'name': 'Brentwood park / escrow', 'bank': 'US Bank', 'account_number': '********6928', 'last_reconciliation': '04/30/2020', 'payments_enabled': 'NOT ENABLED', 'auto_reconciliation': 'PLAID'},
    ]
    
    return render_template('accounting/bank_accounts.html', bank_accounts=bank_accounts_data)

@app.route('/accounting/journal-entries')
@login_required
def journal_entries():
    journal_entries_data = [
        {'date': '08/05/2025', 'reference': '7018', 'property': 'Homestead Villas ...', 'remarks': 'August 2025 - Tra...', 'account': '1150 - Cash in Bank', 'debit': 1500.00, 'credit': 0},
        {'date': '08/01/2025', 'reference': '7013', 'property': 'Indian Creek Town...', 'remarks': 'August 2025 - Mor...', 'account': '1150 - Cash in Bank', 'debit': 8409.56, 'credit': 0},
        {'date': '08/01/2025', 'reference': '7014', 'property': 'Homestead Villas ...', 'remarks': 'August 2025 - Mon...', 'account': '1160 - Escrow Cash', 'debit': 0, 'credit': 116.42},
        {'date': '08/01/2025', 'reference': '7010', 'property': 'Eaton Apartments ...', 'remarks': 'August 2025', 'account': '1150 - Cash in Bank', 'debit': 4518.75, 'credit': 0},
        {'date': '08/01/2025', 'reference': '7011', 'property': 'Randall Court Ven...', 'remarks': 'August 2025 - tra...', 'account': '1150 - Cash in Bank', 'debit': 2333.00, 'credit': 0},
        {'date': '08/01/2025', 'reference': '7012', 'property': 'Randall Court Ven...', 'remarks': 'August 2025 - tra...', 'account': '1503 - Construction Reserve', 'debit': 0, 'credit': 1100.00},
        {'date': '08/01/2025', 'reference': '7003', 'property': 'Homestead Villas ...', 'remarks': 'August 2025 - Tra...', 'account': '1150 - Cash in Bank', 'debit': 1500.00, 'credit': 0},
    ]
    
    return render_template('accounting/journal_entries.html', journal_entries=journal_entries_data)

@app.route('/accounting/bank-transfers')
@login_required
def bank_transfers():
    transfers_data = [
        {'from_account': 'Charlotte Park Apartments LLC*\nCharlotte Park Apartments', 'to_account': 'Charlotte Park Apartments LLC\nCharlotte Park Apartments', 'created': '03/25/2022', 'amount': 4460.63, 'status': 'INCOMPLETE'},
        {'from_account': 'Goodman Townhomes / Goodman Holding LLC / Jeff Lamott\nGoodman Townhomes', 'to_account': 'Goodman Townhomes/Goodman CoreFirst\nGoodman Townhomes', 'created': '06/01/2024', 'amount': 110.38, 'status': 'INCOMPLETE'},
        {'from_account': 'Goodman Townhomes / Goodman Holding LLC / Jeff Lamott\nGoodman Townhomes', 'to_account': 'Goodman Townhomes/Goodman CoreFirst\nGoodman Townhomes', 'created': '06/01/2024', 'amount': 35.48, 'status': 'INCOMPLETE'},
        {'from_account': 'Goodman Townhomes / Goodman Holding LLC / Jeff Lamott\nGoodman Townhomes', 'to_account': 'Goodman Townhomes/Goodman CoreFirst\nGoodman Townhomes', 'created': '06/01/2024', 'amount': 55.97, 'status': 'INCOMPLETE'},
        {'from_account': 'Goodman Townhomes / Goodman Holding LLC / Jeff Lamott\nGoodman Townhomes', 'to_account': 'Goodman Townhomes/Goodman CoreFirst\nGoodman Townhomes', 'created': '06/01/2024', 'amount': 2446.13, 'status': 'INCOMPLETE'},
        {'from_account': 'Goodman Townhomes / Goodman Holding LLC / Jeff Lamott\nGoodman Townhomes', 'to_account': 'Goodman Townhomes/Goodman CoreFirst\nGoodman Townhomes', 'created': '06/01/2024', 'amount': 647.80, 'status': 'INCOMPLETE'},
        {'from_account': 'Martway Townhomes / Martway Holdings / Jeff Lamott\nMartway Townhomes', 'to_account': 'Martway Townhomes/Martway CoreFirst\nMartway Townhomes', 'created': '06/01/2024', 'amount': 446.92, 'status': 'INCOMPLETE'},
        {'from_account': 'Martway Townhomes / Martway Holdings / Jeff Lamott\nMartway Townhomes', 'to_account': 'Martway Townhomes/Martway CoreFirst\nMartway Townhomes', 'created': '06/01/2024', 'amount': 2446.13, 'status': 'INCOMPLETE'},
    ]
    
    return render_template('accounting/bank_transfers.html', transfers=transfers_data)

@app.route('/accounting/gl-accounts')
@login_required
def gl_accounts():
    gl_accounts_data = [
        {'account': 'Aquisition Fees', 'type': 'Expense'},
        {'account': 'Security Deposit', 'type': 'Liability'},
        {'account': '1150: Cash in Bank', 'type': 'Cash'},
        {'account': '1151: Cash Account 2', 'type': 'Cash'},
        {'account': '1152: Capital GL Account', 'type': 'Cash'},
        {'account': '1155: Construction Reserve', 'type': 'Cash'},
        {'account': '1160: Escrow Cash', 'type': 'Cash'},
        {'account': '1165: Other Escrow', 'type': 'Cash'},
        {'account': '1170: Shadow Creek Payroll Reserve', 'type': 'Cash'},
        {'account': '1300: Accounts Receivable', 'type': 'Asset'},
        {'account': '1500: Tax/Insurance Escrow', 'type': 'Asset'},
        {'account': '1503: Construction Reserve', 'type': 'Asset'},
        {'account': '1504: Management Deposit', 'type': 'Asset'},
        {'account': '1610: Land', 'type': 'Asset'},
        {'account': '1700: Buildings', 'type': 'Asset'},
        {'account': '1705: Deposit - Loan Underwriting', 'type': 'Asset'},
        {'account': '1780: Depreciation', 'type': 'Asset'},
        {'account': '1781: Amortization', 'type': 'Asset'},
        {'account': '2103: Unclaimed Security Deposits', 'type': 'Liability'},
        {'account': '2120: Security Deposits Clearing', 'type': 'Liability'},
        {'account': '2300: Prepaid Rent', 'type': 'Liability'},
    ]
    
    return render_template('accounting/gl_accounts.html', gl_accounts=gl_accounts_data)

@app.route('/accounting/diagnostics')
@login_required
def diagnostics():
    diagnostics_data = {
        'security_deposit_mismatch': [
            {'property': '(BARR) Rock Ridge Ranch Apartments', 'ledger_balance': 34692.00, 'funds_balance': 35073.00},
            {'property': '3739 Wyandotte Apartments', 'ledger_balance': 0.00, 'funds_balance': 4250.00},
            {'property': '4504 Terrace / Cottone Properties LLC', 'ledger_balance': 0.00, 'funds_balance': 600.00},
            {'property': 'BAR Wyandotte / BAR Wyandotte LLC', 'ledger_balance': 0.00, 'funds_balance': 12000.00},
            {'property': 'Bella Condo', 'ledger_balance': 600.00, 'funds_balance': 0.00},
            {'property': 'Brushwood Apts / Brush Creek Holdings LLC', 'ledger_balance': 10686.50, 'funds_balance': 9733.00},
            {'property': 'Highland / Highland Ventures', 'ledger_balance': 0.00, 'funds_balance': 5097.00},
            {'property': 'Kaanapali Apartments / BAR Development LLC', 'ledger_balance': 0.00, 'funds_balance': 7300.00},
            {'property': 'La Casa / KC Virginia LLC', 'ledger_balance': 0.00, 'funds_balance': 4300.00},
            {'property': 'Lincrest Apts / Linwood Holdings LLC', 'ledger_balance': 15983.75, 'funds_balance': 9600.00},
            {'property': 'Shadow Creek Apartments', 'ledger_balance': 10516.00, 'funds_balance': 10366.00}
        ],
        'escrow_cash_mismatch': []
    }
    
    return render_template('accounting/diagnostics.html', diagnostics=diagnostics_data)

@app.route('/accounting/receipts')
@login_required
def receipts():
    receipts_data = [
        {'date': '08/07/2025', 'payer': 'Sandra L. Phelps (Paid online)', 'account': '4100: Rent Charge, 4310: RUBS Utility Charge', 'property': 'Summit Apartments - 905 #03', 'amount': 100.00, 'reference': '5305-EEB0'},
        {'date': '08/07/2025', 'payer': 'Derek Bauswell-Curtiss (Paid online)', 'account': '4310: RUBS Utility Charge, 4100: Rent Charge', 'property': 'Walnut Ridge Apts - 6126 E', 'amount': 1140.00, 'reference': 'F476-7F30'},
        {'date': '08/07/2025', 'payer': 'Sarah A. Dement (Paid online)', 'account': '4100: Rent Charge, 4310: RUBS Utility Charge, 5999: Liability to Landlord Insurance, 5680: Late Fee', 'property': 'Windscape Apartments - 9119', 'amount': 1028.50, 'reference': 'C5C3-B650'},
        {'date': '08/07/2025', 'payer': 'DeWayne Williams (Paid online)', 'account': '4100: Rent Charge', 'property': 'Homestead Villas 4-Plex - 4872 Terr', 'amount': 290.00, 'reference': '600F-6CC0'},
        {'date': '08/07/2025', 'payer': 'Angelo F. Della Croce (Paid online)', 'account': '4100: Rent Charge', 'property': 'Brentwood Park / Brentwood Park Ventures LLC - 3607 #02', 'amount': 88.50, 'reference': 'ABCD-1234'}
    ]

    return render_template('accounting/receipts.html', receipts=receipts_data)

# Calendar route
@app.route('/calendar')
@login_required
def calendar():
    return render_template('calendar.html')

# People routes with URL patterns your templates expect
@app.route('/people/tenants')
@login_required
def people_tenants():
    return tenants()  # Calls your existing tenants function

@app.route('/people/owners')
@login_required
def people_owners():
    return owners()  # Calls your existing owners function

@app.route('/people/vendors')
@login_required
def people_vendors():
    return vendors()  # Calls your existing vendors function

# What's New route
@app.route('/whats-new')
@login_required
def whats_new():
    return render_template('whats_new.html')

# Online Payments route
@app.route('/online-payments')
@login_required
def online_payments():
    return render_template('online_payments.html')

# Reporting routes
@app.route('/reporting/reports')
@login_required
def reports():
    return render_template('reporting/reports.html')

@app.route('/reporting/scheduled-reports')
@login_required
def scheduled_reports():
    return render_template('reporting/scheduled_reports.html')

@app.route('/reporting/metrics')
@login_required
def reporting_metrics():
    return render_template('reporting/metrics.html')

@app.route('/reporting/surveys')
@login_required
def surveys():
    return render_template('reporting/surveys.html')

@app.route('/reporting/financial-reports')
@login_required
def financial_reports():
    return render_template('reporting/financial_reports.html')

@app.route('/reporting/rent-roll')
@login_required
def rent_roll():
    return render_template('reporting/rent_roll.html')

@app.route('/reporting/vacancy-reports')
@login_required
def vacancy_reports():
    return render_template('reporting/vacancy_reports.html')

# Communication routes
@app.route('/communication/letters')
@login_required
def letters():
    return render_template('communication/letters.html')

@app.route('/communication/forms')
@login_required
def forms():
    return render_template('communication/forms.html')

@app.route('/communication/phone-logs')
@login_required
def phone_logs():
    return render_template('communication/phone_logs.html')

# API endpoint for lazy loading dashboard sections
@app.route('/api/dashboard/sections', methods=['POST'])
@login_required
def get_dashboard_sections():
    """Return dashboard sections for lazy loading"""
    requested_sections = request.json.get('sections', [])
    sections_data = []
    
    # Generate HTML for each section (simplified version)
    # In production, this would fetch real data from database
    section_templates = {
        'moveOuts': generate_move_outs_section(),
        'onlinePayments': generate_online_payments_section(),
        'notifications': generate_notifications_section(),
        'leasingActivity': generate_leasing_activity_section(),
        'keyMetrics': generate_key_metrics_section(),
        'portfolio': generate_portfolio_section(),
        'delinquencies': generate_delinquencies_section(),
        'maintenance': generate_maintenance_section(),
        'insurance': generate_insurance_section()
    }
    
    for section in requested_sections:
        if section in section_templates:
            sections_data.append({
                'id': section,
                'html': section_templates[section]
            })
    
    return jsonify({'sections': sections_data})

# Helper functions for generating section HTML
def generate_move_outs_section():
    return '''<div class="section-header" onclick="toggleSection('moveOutsContent')">
        <span class="section-arrow collapsed">▼</span>
        <h6 class="section-title">Move Outs</h6>
    </div>
    <div id="moveOutsContent" class="section-content collapsed">
        <div class="text-muted">Loading move outs data...</div>
    </div>'''

def generate_online_payments_section():
    return '''<div class="section-header" onclick="toggleSection('onlinePaymentsContent')">
        <span class="section-arrow collapsed">▼</span>
        <h6 class="section-title">Online Payments</h6>
    </div>
    <div id="onlinePaymentsContent" class="section-content collapsed">
        <div class="text-muted">Loading payments data...</div>
    </div>'''

def generate_notifications_section():
    return '''<div class="section-header" onclick="toggleSection('notificationsContent')">
        <span class="section-arrow collapsed">▼</span>
        <h6 class="section-title">Notifications</h6>
    </div>
    <div id="notificationsContent" class="section-content collapsed">
        <div class="text-muted">Loading notifications...</div>
    </div>'''

def generate_leasing_activity_section():
    return '''<div class="section-header" onclick="toggleSection('leasingActivityContent')">
        <span class="section-arrow collapsed">▼</span>
        <h6 class="section-title">Leasing Activity (Last 30 Days)</h6>
    </div>
    <div id="leasingActivityContent" class="section-content collapsed">
        <div class="text-muted">Loading leasing data...</div>
    </div>'''

def generate_key_metrics_section():
    return '''<div class="section-header" onclick="toggleSection('keyMetricsContent')">
        <span class="section-arrow collapsed">▼</span>
        <h6 class="section-title">Key Performance Metrics</h6>
    </div>
    <div id="keyMetricsContent" class="section-content collapsed">
        <canvas data-chart-type="line" data-chart-data='{}' width="400" height="100"></canvas>
    </div>'''

def generate_portfolio_section():
    return '''<div class="section-header" onclick="toggleSection('portfolioContent')">
        <span class="section-arrow collapsed">▼</span>
        <h6 class="section-title">Portfolio Summary</h6>
    </div>
    <div id="portfolioContent" class="section-content collapsed">
        <div class="text-muted">Loading portfolio data...</div>
    </div>'''

def generate_delinquencies_section():
    return '''<div class="section-header" onclick="toggleSection('delinquenciesContent')">
        <span class="section-arrow collapsed">▼</span>
        <h6 class="section-title">Delinquencies</h6>
    </div>
    <div id="delinquenciesContent" class="section-content collapsed">
        <div class="text-muted">Loading delinquencies data...</div>
    </div>'''

def generate_maintenance_section():
    return '''<div class="section-header" onclick="toggleSection('maintenanceContent')">
        <span class="section-arrow collapsed">▼</span>
        <h6 class="section-title">Maintenance</h6>
    </div>
    <div id="maintenanceContent" class="section-content collapsed">
        <div class="text-muted">Loading maintenance data...</div>
    </div>'''

def generate_insurance_section():
    return '''<div class="section-header" onclick="toggleSection('insuranceContent')">
        <span class="section-arrow collapsed">▼</span>
        <h6 class="section-title">Insurance Coverage</h6>
    </div>
    <div id="insuranceContent" class="section-content collapsed">
        <div class="text-muted">Loading insurance data...</div>
    </div>'''

# Admin routes for your additional files
@app.route('/admin/users')
@login_required
def users():
    return render_template('admin/users.html')

@app.route('/admin/showings')
@login_required
def showings():
    return render_template('admin/showings.html')

@app.route('/admin/emails')
@login_required
def emails():
    return render_template('admin/emails.html')

@app.route('/admin/company-settings')
@login_required
def company_settings():
    return render_template('admin/company_settings.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)