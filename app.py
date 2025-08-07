# Property Management System - Flask Application
# File: app.py

from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_cors import CORS
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from supabase import create_client, Client
import random

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'f3cfe9ed8fae309f02079dbf'
app.config['ENV'] = 'development'
CORS(app)

# Your Supabase configuration - SAVED CREDENTIALS
SUPABASE_URL = "https://sejebqdhcilwcpjpznep.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNlamVicWRoY2lsd2NwanB6bmVwIiwicm9sZSI6ImFub24iLCJpYXQiO"

# Initialize Supabase client
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✅ Connected to Supabase successfully!")
except Exception as e:
    print(f"⚠️ Supabase connection warning: {e}")
    supabase = None

# Sample data generators for demonstration
def get_sample_properties():
    return [
        {
            'name': '(BARR) Rock Ridge Ranch Apartments',
            'address': '10561 Cypress Ave',
            'city': 'Kansas City',
            'state': 'MO',
            'zip': '64137',
            'type': 'Multi-Family',
            'units': 75,
            'vacant': True,
            'owners': 'Rock Ridge Ranch / Rock Ridge Ranch LLC'
        },
        {
            'name': '12520 Grandview Rd. House',
            'address': '12520 Grandview Rd',
            'city': 'Grandview',
            'state': 'MO',
            'zip': '64030',
            'type': 'Single-Family',
            'units': 1,
            'vacant': False,
            'owners': 'HLF Investments MO LLC / Keith S...'
        },
        {
            'name': '340 Belmont House / Stanion',
            'address': '340 N Belmont Blvd',
            'city': 'Kansas City',
            'state': 'MO',
            'zip': '34123',
            'type': 'Single-Family',
            'units': 1,
            'vacant': False,
            'owners': 'Judson Stanion'
        },
        {
            'name': '3815 Shawnee House / Stanion',
            'address': '3815 Shawnee Dr.',
            'city': 'Kansas City',
            'state': 'KS',
            'zip': '66106',
            'type': 'Single-Family',
            'units': 1,
            'vacant': False,
            'owners': 'Judson Stanion'
        },
        {
            'name': '3825 Baltimore',
            'address': '3825 Baltimore',
            'city': 'Kansas City',
            'state': 'MO',
            'zip': '64111',
            'type': 'Multi-Family',
            'units': 7,
            'vacant': True,
            'owners': '3825 Baltimore / Finkelstein'
        },
        {
            'name': '4012 W. 75th Street / TLAR LLC',
            'address': '4012 W. 75th Street',
            'city': 'Prairie Village',
            'state': 'KS',
            'zip': '66208',
            'type': 'Single-Family',
            'units': 1,
            'vacant': False,
            'owners': 'Greg Sweat'
        },
        {
            'name': '40th Street Apartments',
            'address': '1109-1111 W. 40th St.',
            'city': 'Kansas City',
            'state': 'MO',
            'zip': '64111',
            'type': 'Multi-Family',
            'units': 6,
            'vacant': True,
            'owners': 'David Montgomery / 40th st property'
        }
    ]

def get_sample_tenants():
    return [
        {
            'name': 'Arita, Elias',
            'status': 'Current',
            'property': '527 Oakley House / Stanion - 527 N Oakley',
            'unit': '',
            'phone': '(816) 883-9832'
        },
        {
            'name': 'Artigus, Milagros',
            'status': 'Current',
            'property': 'Brentwood Park / Brentwood Park Ventures LLC - 3601-3619 Blue Ridge Blvd.',
            'unit': '3615 #08',
            'phone': '(816) 984-3234'
        },
        {
            'name': 'Barnes, Keisha',
            'status': 'Past',
            'property': 'Blue Ridge Manor - 3813 Duck Road',
            'unit': '3811 11',
            'phone': '(816) 988-1279'
        },
        {
            'name': 'Bell, Mariel',
            'status': 'Past',
            'property': '(BARR) Rock Ridge Ranch Apartments - 10561 Cypress Ave',
            'unit': '41A-R',
            'phone': ''
        },
        {
            'name': 'Burns, Kathy',
            'status': 'Current',
            'property': '(BARR) Rock Ridge Ranch Apartments - 10561 Cypress Ave',
            'unit': '39A',
            'phone': ''
        },
        {
            'name': 'Byers-Boyd, Angela',
            'status': 'Current',
            'property': '(BARR) Rock Ridge Ranch Apartments - 10561 Cypress Ave',
            'unit': '23B',
            'phone': '(816) 359-0719'
        }
    ]

def get_sample_owners():
    return [
        {
            'name': '3825 Baltimore / Finkelstein',
            'company': '3825 Baltimore / Finkelstein',
            'phone': '(650) 922-0967',
            'email': 'dfinkelstein@dgflaw.com'
        },
        {
            'name': 'AC Equity, LLC',
            'company': 'AC Equity, LLC',
            'phone': '(816) 492-0644',
            'email': 'mitch.d.case@gmail.com'
        },
        {
            'name': 'Antioch HS, LLC',
            'company': 'Antioch HS, LLC',
            'phone': '(714) 486-4200',
            'email': 'jjokechoi@gmail.com'
        },
        {
            'name': 'Best Beach LLC',
            'company': 'Best Beach LLC',
            'phone': '',
            'email': 'john619@outlook.com'
        },
        {
            'name': 'Blue Ridge KC LLC',
            'company': 'Blue Ridge KC LLC',
            'phone': '(816) 517-1138',
            'email': 'jbrandmeyer@fambran.com'
        }
    ]

def get_sample_vendors():
    return [
        {
            'name': '1-800 Water Damage Of Kansas City',
            'address': '2581 SW Highway 169 Trimble',
            'phone': '(816) 7850-5023',
            'email': 'dave.johnson@1800waterdamage.com',
            'trade': ''
        },
        {
            'name': '1245 Consulting',
            'address': '3423 Limestone Sky Court House',
            'phone': '(713) 927-0992',
            'email': '',
            'trade': ''
        },
        {
            'name': '12520 Grandview Rd. House / HLF Investments MO LLC',
            'address': '',
            'phone': '',
            'email': '',
            'trade': ''
        },
        {
            'name': '3G Holdings LLC',
            'address': '11002 W 143rd Terr. Overland Park, KS',
            'phone': '(913) 980-9902',
            'email': 'tladish@celticproperties.net',
            'trade': ''
        },
        {
            'name': '40th St Property Escrow',
            'address': '',
            'phone': '',
            'email': '',
            'trade': ''
        },
        {
            'name': '435 Roofing, Inc',
            'address': '9265 Flint St Overland Park KS 66214',
            'phone': '(913) 444-0725',
            'email': 'info@435roofing.com',
            'trade': ''
        },
        {
            'name': '5M Restoration LLC',
            'address': '2773 Vernon Rd Prescott KS 66767',
            'phone': '',
            'email': '',
            'trade': ''
        },
        {
            'name': '7 - 11',
            'address': '',
            'phone': '',
            'email': '',
            'trade': ''
        },
        {
            'name': '84 Lumber',
            'address': '',
            'phone': '',
            'email': '',
            'trade': ''
        },
        {
            'name': 'A&M Heating And Cooling Inc',
            'address': '513 South 4th St. St Joseph MO 64501',
            'phone': '(816) 279-5215',
            'email': 'amhcooling@gmail.com',
            'trade': 'Plumbing'
        }
    ]

def get_sample_receipts():
    return [
        {
            'date': '08/07/2025',
            'payer': 'Reiman Ventura Sarmiento (Paid online)',
            'gl_account': '2300: Prepaid Rent',
            'property': '(BARR) Rock Ridge Ranch Apartments - 59A',
            'amount': 607.74,
            'reference': '3A2B-CFA0'
        },
        {
            'date': '08/07/2025',
            'payer': 'Avianne E. Jones (Paid online)',
            'gl_account': '4100: Rent Charge, 4310: RUBS Utility Charge',
            'property': 'Charlotte Park Apartments - 805 #2W',
            'amount': 1000.00,
            'reference': 'C025-CB60'
        },
        {
            'date': '08/07/2025',
            'payer': 'Desiree M. Brown (Paid online)',
            'gl_account': '2300: Prepaid Rent',
            'property': 'Walnut Ridge Apts - 6116-F',
            'amount': 688.39,
            'reference': '6543-A7C0'
        },
        {
            'date': '08/07/2025',
            'payer': 'William S. Hopkins (Paid online)',
            'gl_account': '4310: RUBS Utility Charge, 5999: Liability to Landlord Insurance, 4100: Rent Charge, 5680: Late Fee',
            'property': '3825 Baltimore - 3827 #04',
            'amount': 948.50,
            'reference': 'F257-7770'
        },
        {
            'date': '08/07/2025',
            'payer': 'Marcel L. Goodwin (Paid online)',
            'gl_account': '2300: Prepaid Rent',
            'property': '(BARR) Rock Ridge Ranch Apartments - 69A-R',
            'amount': 23.18,
            'reference': '1717-E0B0'
        }
    ]

def get_sample_bills():
    return [
        {
            'payee': 'Fair & Square Roof Repair, LLC',
            'ref': '800',
            'bill_date': '08/07/2025',
            'for': 'Longmeadow Apartments',
            'gl_account': '3108: capital expense Roofing',
            'due_date': '08/07/2025',
            'amount': 1179.81,
            'status': 'Paid',
            'cash_account': '1150: Cash in Bank'
        },
        {
            'payee': 'Fair & Square Roof Repair, LLC',
            'ref': '795',
            'bill_date': '08/07/2025',
            'for': 'Indian Creek Townhomes',
            'gl_account': '6780: Roof Repairs/Supplies',
            'due_date': '08/07/2025',
            'amount': 300.09,
            'status': 'Paid',
            'cash_account': '1150: Cash in Bank'
        },
        {
            'payee': 'Metro Appliances',
            'ref': '909457',
            'bill_date': '08/06/2025',
            'for': 'Brentwood Park / Brentwood Park Ventures LLC - 3619 #03',
            'gl_account': '3107: capital expense Appliance',
            'due_date': '08/06/2025',
            'amount': 651.27,
            'status': 'Paid',
            'cash_account': '1150: Cash in Bank'
        },
        {
            'payee': 'Walgreens',
            'ref': '--',
            'bill_date': '08/06/2025',
            'for': 'Brentwood Park / Brentwood Park Ventures LLC',
            'gl_account': '7420: Office Supplies',
            'due_date': '08/06/2025',
            'amount': 13.03,
            'status': 'Paid',
            'cash_account': '1150: Cash in Bank'
        }
    ]

def get_sample_bank_accounts():
    return [
        {
            'name': '3825 Baltimore / Finkelstein',
            'bank': 'US Bank',
            'account_number': '*******2041',
            'last_reconciliation': '07/31/2025',
            'payments_enabled': 'ENABLED',
            'auto_reconciliation': 'PLAID'
        },
        {
            'name': '40th St Escrow',
            'bank': 'US Bank',
            'account_number': '*******7206',
            'last_reconciliation': '11/30/2021',
            'payments_enabled': 'NOT ENABLED',
            'auto_reconciliation': 'PLAID'
        },
        {
            'name': '40th st property',
            'bank': 'US Bank',
            'account_number': '*******3228',
            'last_reconciliation': '06/30/2025',
            'payments_enabled': 'ENABLED',
            'auto_reconciliation': 'PLAID'
        },
        {
            'name': 'AC Equity, LLC / Highland',
            'bank': 'US Bank',
            'account_number': '*******6234',
            'last_reconciliation': '07/31/2025',
            'payments_enabled': 'ENABLED',
            'auto_reconciliation': 'PLAID'
        },
        {
            'name': 'Aspen Village Apts/EM2 Investments, LLC',
            'bank': 'Bank of America',
            'account_number': '*******0610',
            'last_reconciliation': '06/30/2025',
            'payments_enabled': 'ENABLED',
            'auto_reconciliation': 'NOT ENABLED'
        }
    ]

def get_sample_journal_entries():
    return [
        {
            'entry_date': '08/05/2025',
            'reference': '7018',
            'property': 'Homestead Villas Housing / Homestead Villas Investment Housing',
            'remarks': 'August 2025 - Transfer to Operating Account',
            'accounts': [
                {'account': '1150 - Cash in Bank', 'debit': 1500.00, 'credit': 0},
                {'account': '1160 - Escrow Cash', 'debit': 0, 'credit': 1500.00}
            ]
        },
        {
            'entry_date': '08/01/2025',
            'reference': '7013',
            'property': 'Indian Creek Townhomes - 11622 Bluejacket St.',
            'remarks': 'August 2025 - Mortgage Payment',
            'accounts': [
                {'account': '1150 - Cash in Bank', 'debit': 8409.56, 'credit': 0},
                {'account': '9110 - Mortgage Principal', 'debit': 8409.56, 'credit': 0}
            ]
        },
        {
            'entry_date': '08/01/2025',
            'reference': '7014',
            'property': 'Homestead Villas Housing / Homestead Villas Investment Housing',
            'remarks': 'August 2025 - Monthly Interest',
            'accounts': [
                {'account': '1160 - Escrow Cash', 'debit': 116.42, 'credit': 0},
                {'account': '8100 - Interest on Bank Accounts', 'debit': 0, 'credit': 116.42}
            ]
        }
    ]

# Routes
@app.route('/')
@app.route('/dashboard')
def dashboard():
    move_ins = []
    alerts = [{'message': 'Have you checked your Financial Diagnostics Page recently?', 'link': '/diagnostics'}]
    
    return render_template('dashboard.html', 
                         move_ins=move_ins,
                         alerts=alerts)

@app.route('/properties')
def properties():
    properties_data = get_sample_properties()
    return render_template('properties.html', properties=properties_data)

@app.route('/tenants')
def tenants():
    tenants_data = get_sample_tenants()
    return render_template('tenants.html', tenants=tenants_data)

@app.route('/owners')
def owners():
    owners_data = get_sample_owners()
    return render_template('owners.html', owners=owners_data)

@app.route('/vendors')
def vendors():
    vendors_data = get_sample_vendors()
    return render_template('vendors.html', vendors=vendors_data)

@app.route('/receivables')
def receivables():
    receipts_data = get_sample_receipts()
    return render_template('receivables.html', receipts=receipts_data)

@app.route('/payables')
def payables():
    bills_data = get_sample_bills()
    return render_template('payables.html', bills=bills_data)

@app.route('/bank-accounts')
def bank_accounts():
    accounts_data = get_sample_bank_accounts()
    return render_template('bank_accounts.html', accounts=accounts_data)

@app.route('/journal-entries')
def journal_entries():
    entries_data = get_sample_journal_entries()
    return render_template('journal_entries.html', entries=entries_data)

@app.route('/bank-transfers')
def bank_transfers():
    transfers_data = [
        {
            'from_account': 'Goodman Townhomes / Goodman Holding LLC / Jeff Lamott',
            'from_cash': '1150: Cash in Bank',
            'transfers_count': 5,
            'to_account': 'Goodman Townhomes/Goodman CoreFirst',
            'to_cash': '1150: Cash in Bank',
            'to_transfers_count': 5,
            'status': 'INCOMPLETE',
            'amount': 3295.76,
            'created': '06/01/2024'
        },
        {
            'from_account': 'Martway Townhomes / Martway Holdings / Jeff Lamott',
            'from_cash': '1150: Cash in Bank',
            'transfers_count': 2,
            'to_account': 'Martway Townhomes/Martway CoreFirst',
            'to_cash': '1150: Cash in Bank',
            'to_transfers_count': 2,
            'status': 'INCOMPLETE',
            'amount': 2893.05,
            'created': '06/01/2024'
        }
    ]
    return render_template('bank_transfers.html', transfers=transfers_data)

@app.route('/gl-accounts')
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
        {'account': '2300: Prepaid Rent', 'type': 'Liability'}
    ]
    return render_template('gl_accounts.html', gl_accounts=gl_accounts_data)

@app.route('/diagnostics')
def diagnostics():
    diagnostics_data = {
        'security_deposits': [
            {'property': '(BARR) Rock Ridge Ranch Apartments', 'general_ledger': 34692.00, 'security_funds': 35073.00},
            {'property': '3739 Wyandotte Apartments', 'general_ledger': 0.00, 'security_funds': 4250.00},
            {'property': '4504 Terrace / Cottone Properties LLC', 'general_ledger': 0.00, 'security_funds': 600.00},
            {'property': 'BAR Wyandotte / BAR Wyandotte LLC', 'general_ledger': 0.00, 'security_funds': 12000.00},
            {'property': 'Bella Condo', 'general_ledger': 600.00, 'security_funds': 0.00},
            {'property': 'Brushwood Apts / Brush Creek Holdings LLC', 'general_ledger': 10686.50, 'security_funds': 9733.00},
            {'property': 'Highland / Highland Ventures', 'general_ledger': 0.00, 'security_funds': 5097.00},
            {'property': 'Kaanapali Apartments / BAR Development LLC', 'general_ledger': 0.00, 'security_funds': 7300.00},
            {'property': 'La Casa / KC Virginia LLC', 'general_ledger': 0.00, 'security_funds': 4300.00},
            {'property': 'Lincrest Apts / Linwood Holdings LLC', 'general_ledger': 15993.75, 'security_funds': 9600.00},
            {'property': 'Shadow Creek Apartments', 'general_ledger': 10516.00, 'security_funds': 10366.00}
        ],
        'escrow_cash': [
            {'property': '(BARR) Rock Ridge Ranch Apartments', 'gl_balance': 246927.56, 'deposit_accounts': 0.00, 'escrow_offset': 0.00}
        ]
    }
    return render_template('diagnostics.html', diagnostics=diagnostics_data)

@app.route('/vacancies')
def vacancies():
    vacancies_data = []
    return render_template('vacancies.html', vacancies=vacancies_data)

@app.route('/guest-cards')
def guest_cards():
    guests = []
    return render_template('guest_cards.html', guests=guests)

@app.route('/rental-applications')
def rental_applications():
    applications = []
    return render_template('rental_applications.html', applications=applications)

@app.route('/leases')
def leases():
    leases_data = []
    return render_template('leases.html', leases=leases_data, current_status='all')

@app.route('/renewals')
def renewals():
    renewals_data = []
    return render_template('renewals.html', renewals=renewals_data)

@app.route('/metrics')
def metrics():
    metrics_data = {
        'total_properties': 15,
        'total_units': 127,
        'vacant_units': 8,
        'active_leases': 119,
        'occupancy_rate': 93.7
    }
    return render_template('metrics.html', metrics=metrics_data)

# API Routes
@app.route('/api/properties/search', methods=['POST'])
def search_properties():
    query = request.json.get('query', '')
    # Implement search logic
    return jsonify({'success': True, 'results': []})

@app.route('/api/tenants/search', methods=['POST'])
def search_tenants():
    query = request.json.get('query', '')
    # Implement search logic
    return jsonify({'success': True, 'results': []})

@app.route('/api/bills/approve', methods=['POST'])
def approve_bill():
    bill_id = request.json.get('bill_id')
    # Implement approval logic
    return jsonify({'success': True, 'message': 'Bill approved'})

@app.route('/api/transfers/complete', methods=['POST'])
def complete_transfer():
    transfer_id = request.json.get('transfer_id')
    # Implement transfer completion logic
    return jsonify({'success': True, 'message': 'Transfer completed'})

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
    print("Starting server on http://localhost:5000")
    print("Press CTRL+C to stop")
    print("="*50 + "\n")
    
    app.run(debug=True, port=5000)