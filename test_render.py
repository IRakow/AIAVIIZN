from flask import Flask, render_template, request
from werkzeug.test import EnvironBuilder
from werkzeug.wrappers import Request

app = Flask(__name__)
app.config['SECRET_KEY'] = 'test'
app.config['SERVER_NAME'] = 'localhost:5000'

# Define the routes so url_for works
@app.route('/')
@app.route('/dashboard')
def dashboard():
    pass

@app.route('/vacancies')
def vacancies():
    pass

@app.route('/guest-cards')
def guest_cards():
    pass

@app.route('/rental-applications')
def rental_applications():
    pass

@app.route('/leases')
def leases():
    pass

@app.route('/renewals')
def renewals():
    pass

@app.route('/metrics')
def metrics():
    pass

with app.app_context():
    with app.test_request_context('/dashboard'):
        # Mock data for template
        move_ins = []
        alerts = [{'message': 'Test alert', 'link': '/test'}]
        
        # Render the template
        html = render_template('dashboard.html', move_ins=move_ins, alerts=alerts)
        
        # Check for new sidebar elements
        if 'menu-section' in html:
            print("✅ New sidebar with menu-section found!")
        else:
            print("❌ New sidebar NOT found")
        
        if 'sidebar' in html and 'class="sidebar"' in html:
            print("✅ Sidebar element with class found")
        else:
            print("❌ No sidebar with class found")
            
        # Check for specific new elements
        if 'menu-section-header' in html:
            print("✅ menu-section-header found")
        else:
            print("❌ menu-section-header NOT found")
            
        if 'Leasing' in html:
            print("✅ Leasing section found")
        else:
            print("❌ Leasing section NOT found")
            
        # Save to file for inspection
        with open('rendered_dashboard.html', 'w') as f:
            f.write(html)
        print("\n📄 Full rendered HTML saved to rendered_dashboard.html")
        
        # Check structure
        print("\nChecking HTML structure...")
        lines = html.split('\n')
        for i, line in enumerate(lines[:30]):
            if 'sidebar' in line.lower() or 'menu' in line.lower():
                print(f"Line {i}: {line.strip()[:100]}")