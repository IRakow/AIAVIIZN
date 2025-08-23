#!/usr/bin/env python3
"""
AIVIIZN Flask Application - Auto-generated from replicated pages
Serves all captured pages with proper interlinking
"""

from flask import Flask, render_template, jsonify, request, redirect, url_for, session, flash
from functools import wraps
from datetime import datetime, timedelta
import os
import json
from pathlib import Path

app = Flask(__name__)
app.secret_key = 'aiviizn-secret-key-2025-change-in-production'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

# Template and static paths
app.template_folder = 'templates'
app.static_folder = 'static'

# Load page metadata
PAGE_METADATA = {}
data_dir = Path('data')
if (data_dir / 'processed_pages.json').exists():
    with open(data_dir / 'processed_pages.json', 'r') as f:
        processed_pages = json.load(f)
        for page_url in processed_pages:
            # Generate route name from URL
            route_name = page_url.replace('https://celticprop.appfolio.com', '').strip('/').replace('/', '_') or 'index'
            PAGE_METADATA[route_name] = {{
                'url': page_url,
                'title': route_name.replace('_', ' ').title()
            }}

# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Base routes
@app.route('/')
def index():
    """Main landing page"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Demo login
        if email == "admin@aiviizn.com" and password == "demo123":
            session.permanent = True
            session['user_id'] = 'demo-user-id'
            session['email'] = email
            flash('Welcome to AIVIIZN!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials. Use admin@aiviizn.com / demo123', 'danger')
    
    return render_template('auth/login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard"""
    return render_template('dashboard.html', pages=PAGE_METADATA)

@app.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


@app.route('/search/advanced_search')
@login_required
def search_advanced_search():
    """Auto-generated route for https://celticprop.appfolio.com/search/advanced_search"""
    # Load any field mappings for this page
    field_mappings = {}
    
    # Load AI field mappings if available
    if (data_dir / 'ai_field_mappings.json').exists():
        with open(data_dir / 'ai_field_mappings.json', 'r') as f:
            all_mappings = json.load(f)
            # Filter mappings for this page
            page_mappings = {k: v for k, v in all_mappings.items() if 'https://celticprop.appfolio.com/search/advanced_search' in k}
            field_mappings.update(page_mappings)
    
    return render_template('search/advanced_search.html', 
                         field_mappings=field_mappings,
                         current_page='search/advanced_search')


@app.route('/v_plus_services_marketplace')
@login_required
def v_plus_services_marketplace():
    """Auto-generated route for https://celticprop.appfolio.com/v_plus_services_marketplace"""
    # Load any field mappings for this page
    field_mappings = {}
    
    # Load AI field mappings if available
    if (data_dir / 'ai_field_mappings.json').exists():
        with open(data_dir / 'ai_field_mappings.json', 'r') as f:
            all_mappings = json.load(f)
            # Filter mappings for this page
            page_mappings = {k: v for k, v in all_mappings.items() if 'https://celticprop.appfolio.com/v_plus_services_marketplace' in k}
            field_mappings.update(page_mappings)
    
    return render_template('v_plus_services_marketplace.html', 
                         field_mappings=field_mappings,
                         current_page='v_plus_services_marketplace')


@app.route('/vacancies')
@login_required
def vacancies():
    """Auto-generated route for https://celticprop.appfolio.com/vacancies"""
    # Load any field mappings for this page
    field_mappings = {}
    
    # Load AI field mappings if available
    if (data_dir / 'ai_field_mappings.json').exists():
        with open(data_dir / 'ai_field_mappings.json', 'r') as f:
            all_mappings = json.load(f)
            # Filter mappings for this page
            page_mappings = {k: v for k, v in all_mappings.items() if 'https://celticprop.appfolio.com/vacancies' in k}
            field_mappings.update(page_mappings)
    
    return render_template('vacancies.html', 
                         field_mappings=field_mappings,
                         current_page='vacancies')


@app.route('/stack')
@login_required
def stack():
    """Auto-generated route for https://celticprop.appfolio.com/stack"""
    # Load any field mappings for this page
    field_mappings = {}
    
    # Load AI field mappings if available
    if (data_dir / 'ai_field_mappings.json').exists():
        with open(data_dir / 'ai_field_mappings.json', 'r') as f:
            all_mappings = json.load(f)
            # Filter mappings for this page
            page_mappings = {k: v for k, v in all_mappings.items() if 'https://celticprop.appfolio.com/stack' in k}
            field_mappings.update(page_mappings)
    
    return render_template('stack.html', 
                         field_mappings=field_mappings,
                         current_page='stack')


@app.route('/index')
@login_required
def index():
    """Auto-generated route for https://celticprop.appfolio.com/"""
    # Load any field mappings for this page
    field_mappings = {}
    
    # Load AI field mappings if available
    if (data_dir / 'ai_field_mappings.json').exists():
        with open(data_dir / 'ai_field_mappings.json', 'r') as f:
            all_mappings = json.load(f)
            # Filter mappings for this page
            page_mappings = {k: v for k, v in all_mappings.items() if 'https://celticprop.appfolio.com/' in k}
            field_mappings.update(page_mappings)
    
    return render_template('index.html', 
                         field_mappings=field_mappings,
                         current_page='index')


# API Routes
@app.route('/api/fields/<page_id>')
@login_required
def api_get_fields(page_id):
    """Get field mappings for a specific page"""
    if (data_dir / 'identified_fields.json').exists():
        with open(data_dir / 'identified_fields.json', 'r') as f:
            fields = json.load(f)
            page_fields = [f for f in fields.values() if page_id in f.get('page_url', '')]
            return jsonify(page_fields)
    return jsonify([])

@app.route('/api/calculations/<page_id>')
@login_required
def api_get_calculations(page_id):
    """Get calculations for a specific page"""
    # Would load from database in production
    return jsonify([])

@app.route('/api/ai-mappings')
@login_required
def api_get_ai_mappings():
    """Get all AI field mappings"""
    if (data_dir / 'ai_field_mappings.json').exists():
        with open(data_dir / 'ai_field_mappings.json', 'r') as f:
            return jsonify(json.load(f))
    return jsonify({})

if __name__ == '__main__':
    app.run(debug=True, port=8080)
