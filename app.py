# app.py - Exact UI Match for Your Property Management System
import os
from flask import Flask, render_template_string, request, jsonify, redirect, url_for, session
from flask_cors import CORS
from supabase import create_client, Client
from functools import wraps
from datetime import datetime, timedelta
import secrets

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(32))
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
CORS(app)

# Supabase Configuration
SUPABASE_URL = os.environ.get('SUPABASE_URL', 'https://sejebqdhcilwcpjpznep.supabase.co')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNlamVicWRoY2lsd2NwanB6bmVwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ0NTg5NjQsImV4cCI6MjA3MDAzNDk2NH0.vFM0Gr3QZF4MN3vtDGghjyCpnIkyC_mmUOOkVO3ahPQ')

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# EXACT HTML/CSS matching your screenshots
EXACT_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: -apple-system, 'Segoe UI', Arial, sans-serif;
            font-size: 12px;
            color: #212529;
            background: white;
            height: 100vh;
            overflow: hidden;
        }
        
        /* EXACT Login Page Matching Your Style */
        .login-page {
            height: 100vh;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            display: flex;
            justify-content: center;
            align-items: center;
        }
        
        .login-card {
            background: white;
            padding: 60px 50px;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            text-align: center;
            width: 450px;
        }
        
        .login-icon { font-size: 72px; margin-bottom: 20px; }
        .login-title { font-size: 32px; font-weight: 600; color: #333; margin-bottom: 10px; }
        .login-subtitle { font-size: 16px; color: #666; margin-bottom: 40px; }
        
        .login-input {
            width: 100%;
            padding: 15px;
            margin-bottom: 15px;
            border: 1px solid #ddd;
            border-radius: 8px;
            font-size: 16px;
        }
        
        .login-button {
            width: 100%;
            padding: 18px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 18px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        }
        
        .login-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5);
        }
        
        /* EXACT Main Layout - 3 Column Design */
        .main-container {
            display: flex;
            height: 100vh;
            background: white;
        }
        
        /* LEFT SIDEBAR - Exactly matching your screenshots */
        .left-sidebar {
            width: 165px;
            background: #f8f8f8;
            border-right: 1px solid #e0e0e0;
            display: flex;
            flex-direction: column;
        }
        
        .logo-section {
            padding: 10px;
            background: white;
            border-bottom: 1px solid #e0e0e0;
            font-weight: 500;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .nav-menu {
            flex: 1;
            overflow-y: auto;
            padding: 5px 0;
        }
        
        .nav-item {
            display: flex;
            align-items: center;
            padding: 7px 12px;
            color: #212529;
            text-decoration: none;
            font-size: 12px;
            cursor: pointer;
            position: relative;
        }
        
        .nav-item:hover { background: #e8e8e8; }
        
        .nav-item.active {
            background: #d4e3fc;
            color: #0056b3;
        }
        
        .nav-item .icon {
            width: 16px;
            margin-right: 8px;
        }
        
        .nav-expandable::after {
            content: '▼';
            position: absolute;
            right: 10px;
            font-size: 8px;
        }
        
        .nav-expandable.collapsed::after { content: '▶'; }
        
        .nav-submenu {
            background: white;
            display: none;
        }
        
        .nav-submenu.open { display: block; }
        
        .nav-submenu .nav-item {
            padding-left: 35px;
            font-size: 11px;
        }
        
        .nav-badge {
            background: #dc3545;
            color: white;
            padding: 1px 5px;
            border-radius: 10px;
            font-size: 10px;
            margin-left: auto;
        }
        
        .company-footer {
            padding: 10px;
            border-top: 1px solid #e0e0e0;
            background: white;
            font-size: 10px;
            color: #666;
            text-align: center;
        }
        
        .minimize-button {
            background: none;
            border: none;
            padding: 5px;
            cursor: pointer;
            font-size: 11px;
            color: #666;
        }
        
        /* MIDDLE CONTENT AREA */
        .content-area {
            flex: 1;
            display: flex;
            flex-direction: column;
            background: white;
        }
        
        /* TOP TAB NAVIGATION - Exact match */
        .tab-nav {
            height: 36px;
            background: white;
            border-bottom: 2px solid #0056b3;
            display: flex;
            align-items: flex-end;
        }
        
        .tab {
            padding: 8px 16px;
            background: #f0f0f0;
            border: 1px solid #ddd;
            border-bottom: none;
            margin-right: 2px;
            cursor: pointer;
            font-size: 12px;
            color: #333;
        }
        
        .tab:hover { background: #e0e0e0; }
        
        .tab.active {
            background: #0056b3;
            color: white;
            border-color: #0056b3;
        }
        
        /* PAGE CONTENT */
        .page-content {
            flex: 1;
            padding: 15px 20px;
            overflow-y: auto;
            background: white;
        }
        
        .page-heading {
            font-size: 20px;
            font-weight: normal;
            margin-bottom: 15px;
            color: #212529;
        }
        
        /* ALPHABET FILTER - Exact match */
        .alphabet-bar {
            padding: 8px 0;
            margin-bottom: 15px;
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        
        .alphabet-bar a {
            color: #0056b3;
            text-decoration: none;
            padding: 2px 6px;
            font-size: 12px;
        }
        
        .alphabet-bar a:hover { text-decoration: underline; }
        
        .alphabet-bar a.active {
            background: #0056b3;
            color: white;
            border-radius: 2px;
        }
        
        /* DATA TABLE - Exact styling */
        .data-grid {
            background: white;
            border: 1px solid #dee2e6;
        }
        
        .data-grid table {
            width: 100%;
            border-collapse: collapse;
        }
        
        .data-grid th {
            background: #f1f3f5;
            padding: 8px;
            text-align: left;
            font-weight: normal;
            font-size: 12px;
            border-bottom: 1px solid #dee2e6;
            color: #495057;
        }
        
        .data-grid td {
            padding: 8px;
            border-bottom: 1px solid #e9ecef;
            font-size: 12px;
        }
        
        .data-grid tbody tr:hover { background: #f8f9fa; }
        
        .data-grid a {
            color: #0056b3;
            text-decoration: none;
        }
        
        .data-grid a:hover { text-decoration: underline; }
        
        /* RIGHT SIDEBAR - Two Panels */
        .right-sidebar {
            width: 280px;
            border-left: 1px solid #e0e0e0;
            display: flex;
            flex-direction: column;
            background: white;
        }
        
        /* TASKS PANEL - Top */
        .tasks-panel {
            flex: 1;
            display: flex;
            flex-direction: column;
            border-bottom: 1px solid #e0e0e0;
        }
        
        .panel-header {
            background: #f8f8f8;
            padding: 8px 12px;
            border-bottom: 1px solid #e0e0e0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .panel-title {
            font-size: 13px;
            font-weight: 500;
            color: #212529;
        }
        
        .close-button {
            background: none;
            border: none;
            font-size: 18px;
            cursor: pointer;
            color: #666;
            padding: 0 5px;
        }
        
        .tasks-list {
            flex: 1;
            overflow-y: auto;
            padding: 10px;
        }
        
        .task-group {
            margin-bottom: 15px;
        }
        
        .task-group-title {
            font-size: 11px;
            font-weight: 500;
            color: #666;
            padding: 5px 0;
            margin-bottom: 5px;
            border-bottom: 1px solid #e9ecef;
        }
        
        .task-item {
            padding: 5px 8px;
            font-size: 11px;
            color: #212529;
            cursor: pointer;
            border-radius: 2px;
        }
        
        .task-item:hover { background: #f1f3f5; }
        .task-item.starred { color: #0056b3; }
        
        /* ASSISTANT PANEL - Bottom */
        .assistant-panel {
            height: 140px;
            padding: 10px;
            background: white;
            border-top: 1px solid #e0e0e0;
        }
        
        .assistant-header {
            font-size: 12px;
            font-weight: 500;
            margin-bottom: 8px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .support-button {
            background: #f8f8f8;
            border: 1px solid #ddd;
            padding: 3px 8px;
            font-size: 10px;
            cursor: pointer;
            border-radius: 2px;
        }
        
        .assistant-text {
            font-size: 11px;
            color: #666;
            line-height: 1.4;
        }
        
        /* SEARCH BOX - Blue with arrow */
        .search-container {
            margin-bottom: 20px;
            position: relative;
        }
        
        .search-box {
            width: 100%;
            padding: 10px;
            border: 2px solid #0056b3;
            border-radius: 3px;
            text-align: center;
            color: #666;
            font-size: 12px;
            background: white;
        }
        
        .search-arrow {
            position: absolute;
            bottom: -8px;
            left: 50%;
            transform: translateX(-50%);
            width: 0;
            height: 0;
            border-left: 8px solid transparent;
            border-right: 8px solid transparent;
            border-top: 8px solid #0056b3;
        }
    </style>
</head>
<body>
    {{ content|safe }}
</body>
</html>
'''

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if email and password:
            try:
                response = supabase.auth.sign_in_with_password({"email": email, "password": password})
                if response.user:
                    session['user'] = {'email': email}
                    return redirect(url_for('dashboard'))
            except:
                # Demo mode - accept any login
                session['user'] = {'email': email}
                return redirect(url_for('dashboard'))
    
    content = '''
    <div class="login-page">
        <div class="login-card">
            <div class="login-icon">🏢</div>
            <div class="login-title">AIVIIZN</div>
            <div class="login-subtitle">Property Management System</div>
            <form method="POST">
                <input type="email" name="email" class="login-input" placeholder="Email" required>
                <input type="password" name="password" class="login-input" placeholder="Password" required>
                <button type="submit" class="login-button">Sign In →</button>
            </form>
        </div>
    </div>
    '''
    return render_template_string(EXACT_TEMPLATE, title='AIVIIZN Login', content=content)

@app.route('/dashboard')
@login_required
def dashboard():
    content = create_main_layout('''
        <div class="page-content">
            <h1 class="page-heading">Dashboard</h1>
            <div style="background: #cfe2ff; padding: 12px; border-radius: 3px; margin-bottom: 20px; font-size: 12px;">
                <strong>ℹ️</strong> Have you checked your Financial Diagnostics Page recently? 
                <a href="#" style="color: #0056b3;">Click here</a> to check up on your Financial Health.
                <a href="#" style="color: #0056b3;">Remind me in 7 days</a> | 
                <a href="#" style="color: #0056b3;">I'm fine... don't show this message again</a>
            </div>
            
            <h2 style="font-size: 16px; margin: 20px 0 10px 0; font-weight: normal;">▼ Move Ins</h2>
            
            <div style="background: #d1ecf1; padding: 10px; border-radius: 3px; margin-bottom: 10px;">
                <strong>NEW</strong> Move Ins Updated<br>
                We've added some key information to help track the progress of your move-ins. What additional information would you like to see?
                <button style="float: right; background: white; border: 1px solid #0056b3; color: #0056b3; padding: 2px 8px; font-size: 11px;">FEEDBACK</button>
            </div>
            
            <div class="data-grid">
                <table>
                    <thead>
                        <tr>
                            <th>Future Tenant ↕</th>
                            <th>Property - Unit ↕</th>
                            <th>Lease ↕</th>
                            <th>Portal ↕</th>
                            <th>Balance ↕</th>
                            <th>Insurance</th>
                            <th>Move In Date ↕</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>Sainge, Samuel</td>
                            <td>-</td>
                            <td>-</td>
                            <td>Active</td>
                            <td style="text-align: right;">$400.00</td>
                            <td>Not Covered</td>
                            <td>07/25/2025</td>
                        </tr>
                        <tr>
                            <td>Bell, Telia R.</td>
                            <td>-</td>
                            <td>-</td>
                            <td>Active</td>
                            <td style="text-align: right;">$0.00</td>
                            <td>Not Covered</td>
                            <td>08/01/2025</td>
                        </tr>
                        <tr>
                            <td>Carlson, Eric A.</td>
                            <td>Campbell Apartments - 3403 #4</td>
                            <td>Fully Executed</td>
                            <td>Active</td>
                            <td style="text-align: right; color: #dc3545;">-$727.74</td>
                            <td>Covered</td>
                            <td>08/08/2025</td>
                        </tr>
                        <tr>
                            <td>Stivers, Rachel A.</td>
                            <td>Grandview 17 Townhomes / Grandview 17 KC LLC - 13825 A</td>
                            <td>Fully Executed</td>
                            <td>Active</td>
                            <td style="text-align: right; color: #dc3545;">-$930.92</td>
                            <td>Pending</td>
                            <td>08/08/2025</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    ''', 'dashboard')
    return render_template_string(EXACT_TEMPLATE, title='Dashboard', content=content)

@app.route('/tenants')
@login_required
def tenants():
    content = create_main_layout('''
        <div class="tab-nav">
            <div class="tab active">Tenants</div>
            <div class="tab" onclick="location.href='/owners'">Owners</div>
            <div class="tab" onclick="location.href='/vendors'">Vendors</div>
        </div>
        <div class="page-content">
            <h1 class="page-heading">Tenants</h1>
            
            <div class="alphabet-bar">
                <a href="#">A</a><a href="#">B</a><a href="#">C</a><a href="#">D</a><a href="#">E</a>
                <a href="#">F</a><a href="#">G</a><a href="#">H</a><a href="#">I</a><a href="#">J</a>
                <a href="#">K</a><a href="#">L</a><a href="#">M</a><a href="#">N</a><a href="#">O</a>
                <a href="#">P</a><a href="#">Q</a><a href="#">R</a><a href="#">S</a><a href="#">T</a>
                <a href="#">U</a><a href="#">V</a><a href="#">W</a><a href="#">X</a><a href="#">Y</a>
                <a href="#">Z</a><a href="#" class="active">All</a>
            </div>
            
            <div class="data-grid">
                <table>
                    <thead>
                        <tr>
                            <th>Name ↕</th>
                            <th>Status ↕</th>
                            <th>Property</th>
                            <th>Unit</th>
                            <th>Phone</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td><a href="#">Arita, Elias</a></td>
                            <td>Current</td>
                            <td>527 Oakley House / Stanion - 527 N Oakley Kansas City, MO 64123</td>
                            <td></td>
                            <td>(816) 883-9832</td>
                        </tr>
                        <tr>
                            <td><a href="#">Artigus, Milagros</a></td>
                            <td>Current</td>
                            <td>Brentwood Park / Brentwood Park Ventures LLC - 3601-3619 Blue Ridge Blvd. Grandview, MO 64030</td>
                            <td>3615 #08</td>
                            <td>(816) 984-3234</td>
                        </tr>
                        <tr>
                            <td><a href="#">Barnes, Keisha</a></td>
                            <td>Past</td>
                            <td>Blue Ridge Manor - 3813 Duck Road Grandview, MO 64030</td>
                            <td>3811 11</td>
                            <td>(816) 988-1279</td>
                        </tr>
                        <tr>
                            <td><a href="#">Bell, Mariel</a></td>
                            <td>Past</td>
                            <td>(BARR) Rock Ridge Ranch Apartments - 10561 Cypress Ave Kansas City, MO 64137</td>
                            <td>41A-R</td>
                            <td></td>
                        </tr>
                        <tr>
                            <td><a href="#">Burns, Kathy</a></td>
                            <td>Current</td>
                            <td>(BARR) Rock Ridge Ranch Apartments - 10561 Cypress Ave Kansas City, MO 64137</td>
                            <td>39A</td>
                            <td></td>
                        </tr>
                        <tr>
                            <td><a href="#">Byers-Boyd, Angela</a></td>
                            <td>Current</td>
                            <td>(BARR) Rock Ridge Ranch Apartments - 10561 Cypress Ave Kansas City, MO 64137</td>
                            <td>23B</td>
                            <td>(816) 359-0719</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    ''', 'tenants', has_tabs=False)
    return render_template_string(EXACT_TEMPLATE, title='Tenants', content=content)

@app.route('/owners')
@login_required  
def owners():
    content = create_main_layout('''
        <div class="tab-nav">
            <div class="tab" onclick="location.href='/tenants'">Tenants</div>
            <div class="tab active">Owners</div>
            <div class="tab" onclick="location.href='/vendors'">Vendors</div>
        </div>
        <div class="page-content">
            <h1 class="page-heading">Owners</h1>
            
            <div class="alphabet-bar">
                <a href="#">A</a><a href="#">B</a><a href="#">C</a><a href="#">D</a><a href="#">E</a>
                <a href="#">F</a><a href="#">G</a><a href="#">H</a><a href="#">I</a><a href="#">J</a>
                <a href="#">K</a><a href="#">L</a><a href="#">M</a><a href="#">N</a><a href="#">O</a>
                <a href="#">P</a><a href="#">Q</a><a href="#">R</a><a href="#">S</a><a href="#">T</a>
                <a href="#">U</a><a href="#">V</a><a href="#">W</a><a href="#">X</a><a href="#">Y</a>
                <a href="#">Z</a><a href="#" class="active">All</a>
            </div>
            
            <div class="data-grid">
                <table>
                    <thead>
                        <tr>
                            <th>Name ↕</th>
                            <th>Company</th>
                            <th>Phone</th>
                            <th>Email</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td><a href="#">3825 Baltimore / Finkelstein</a></td>
                            <td>3825 Baltimore / Finkelstein</td>
                            <td>(650) 922-0967</td>
                            <td><a href="#">dfinkelstein@dgflaw.com</a></td>
                        </tr>
                        <tr>
                            <td><a href="#">AC Equity, LLC</a></td>
                            <td>AC Equity, LLC</td>
                            <td>(816) 492-0644</td>
                            <td><a href="#">mitch.d.case@gmail.com</a></td>
                        </tr>
                        <tr>
                            <td><a href="#">Antioch HS, LLC</a></td>
                            <td>Antioch HS, LLC</td>
                            <td>(714) 486-4200</td>
                            <td><a href="#">jjokechoi@gmail.com</a></td>
                        </tr>
                        <tr>
                            <td><a href="#">Best Beach LLC</a></td>
                            <td>Best Beach LLC</td>
                            <td></td>
                            <td><a href="#">john619@outlook.com</a></td>
                        </tr>
                        <tr>
                            <td><a href="#">Blue Ridge KC LLC</a></td>
                            <td>Blue Ridge KC LLC</td>
                            <td>(816) 517-1138</td>
                            <td><a href="#">jbrandmeyer@fambren.com</a></td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    ''', 'owners', has_tabs=False)
    return render_template_string(EXACT_TEMPLATE, title='Owners', content=content)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

def create_main_layout(content, active_page='dashboard', has_tabs=True):
    return f'''
    <div class="main-container">
        <!-- LEFT SIDEBAR -->
        <div class="left-sidebar">
            <div class="logo-section">
                <span>🏢</span>
                <span>Dashboard</span>
            </div>
            
            <div class="nav-menu">
                <a href="/dashboard" class="nav-item {'active' if active_page == 'dashboard' else ''}">
                    <span class="icon">🏠</span> Dashboard
                </a>
                <a href="#" class="nav-item">
                    <span class="icon">📅</span> Calendar
                </a>
                <div class="nav-item nav-expandable" onclick="toggleMenu('leasing')">
                    <span class="icon">🔑</span> Leasing
                </div>
                <div id="leasing" class="nav-submenu">
                    <a href="#" class="nav-item">Vacancies</a>
                    <a href="#" class="nav-item">Guest Cards</a>
                    <a href="#" class="nav-item">Rental Applications</a>
                    <a href="#" class="nav-item">Leases</a>
                    <a href="#" class="nav-item">Renewals</a>
                    <a href="#" class="nav-item">Metrics</a>
                    <a href="#" class="nav-item">Signals</a>
                </div>
                <a href="#" class="nav-item">
                    <span class="icon">🏠</span> Properties
                </a>
                <div class="nav-item nav-expandable" onclick="toggleMenu('people')">
                    <span class="icon">👥</span> People
                </div>
                <div id="people" class="nav-submenu open">
                    <a href="/tenants" class="nav-item {'active' if active_page == 'tenants' else ''}">Tenants</a>
                    <a href="/owners" class="nav-item {'active' if active_page == 'owners' else ''}">Owners</a>
                    <a href="#" class="nav-item">Vendors</a>
                </div>
                <div class="nav-item nav-expandable">
                    <span class="icon">💰</span> Accounting
                </div>
                <div class="nav-item nav-expandable">
                    <span class="icon">🔧</span> Maintenance
                </div>
                <div class="nav-item nav-expandable">
                    <span class="icon">📊</span> Reporting
                </div>
                <div class="nav-item nav-expandable">
                    <span class="icon">📧</span> Communication
                </div>
                <a href="#" class="nav-item">
                    <span class="icon">🆕</span> What's New
                    <span class="nav-badge">4</span>
                </a>
            </div>
            
            <div class="company-footer">
                Celtic Property<br>Management
                <div style="margin-top: 10px;">
                    <button class="minimize-button">⬇ Minimize</button>
                </div>
            </div>
        </div>
        
        <!-- MIDDLE CONTENT -->
        <div class="content-area">
            {content}
        </div>
        
        <!-- RIGHT SIDEBAR -->
        <div class="right-sidebar">
            <!-- TASKS PANEL -->
            <div class="tasks-panel">
                <div class="panel-header">
                    <span class="panel-title">Tasks</span>
                    <button class="close-button">×</button>
                </div>
                <div class="tasks-list">
                    <div class="task-group">
                        <div class="task-group-title">⭐ Tasks</div>
                        <div class="task-item starred">Move In Tenant</div>
                        <div class="task-item">New Owner</div>
                        <div class="task-item">New Vendor</div>
                        <div class="task-item">Email All Tenants</div>
                    </div>
                    <div class="task-group">
                        <div class="task-group-title">📊 Reports</div>
                        <div class="task-item">Rent Roll</div>
                        <div class="task-item">Tenant Ledger</div>
                        <div class="task-item">Tenant Insurance Coverage</div>
                    </div>
                </div>
            </div>
            
            <!-- ASSISTANT PANEL -->
            <div class="assistant-panel">
                <div class="assistant-header">
                    <span>Assistant</span>
                    <button class="support-button">Support</button>
                </div>
                <div class="assistant-text">
                    Need help? Click Support to chat with our team or browse the help topics above.
                </div>
            </div>
        </div>
    </div>
    
    <script>
        function toggleMenu(id) {{
            const menu = document.getElementById(id);
            menu.classList.toggle('open');
        }}
    </script>
    '''

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)