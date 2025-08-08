import os
import json
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_cors import CORS
from flask_session import Session
from functools import wraps
from datetime import datetime, timedelta
import redis
from supabase import create_client, Client
import logging
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# App Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here-change-in-production')
app.config['SESSION_TYPE'] = 'filesystem'  # Use filesystem instead of redis for now
app.config['SESSION_PERMANENT'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

# Initialize Flask-Session
Session(app)

# Supabase Configuration - YOUR ACTUAL KEYS
SUPABASE_URL = 'https://sejebqdhcilwcpjpznep.supabase.co'
SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNlamVicWRoY2lsd2NwanB6bmVwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ0NTg5NjQsImV4cCI6MjA3MDAzNDk2NH0.vFM0Gr3QZF4MN3vtDGghjyCpnIkyC_mmUOOkVO3ahPQ'

# Initialize Supabase client
try:
    supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    logger.info("✅ Supabase client initialized successfully")
except Exception as e:
    logger.error(f"❌ Failed to initialize Supabase client: {e}")
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

# Routes
@app.route('/')
def index():
    """Root route - redirect to login or dashboard"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Main login route with Supabase authentication"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        logger.info(f"🔐 Login attempt for email: {email}")
        
        if not email or not password:
            flash('Please enter both email and password.', 'danger')
            return render_template('auth/login.html')
        
        if not supabase:
            flash('Database connection error. Please try again later.', 'danger')
            return render_template('auth/login.html')
        
        try:
            # Attempt Supabase authentication
            auth_response = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if auth_response and auth_response.user:
                user = auth_response.user
                session_data = auth_response.session
                
                # Store user information in session
                session['user_id'] = user.id
                session['user_email'] = user.email
                session['user_role'] = getattr(user, 'role', 'user')
                session['company_id'] = 'default-company'
                
                if session_data:
                    session['access_token'] = session_data.access_token
                    session['refresh_token'] = session_data.refresh_token
                
                logger.info(f"✅ Login successful for user: {user.email}")
                flash('Successfully logged in!', 'success')
                
                next_page = request.args.get('next')
                return redirect(next_page or url_for('dashboard'))
            else:
                flash('Invalid email or password.', 'danger')
                
        except Exception as e:
            error_msg = str(e)
            logger.error(f"❌ Login error: {error_msg}")
            
            if 'Invalid login credentials' in error_msg:
                flash('Invalid email or password. Please check your credentials.', 'danger')
            elif 'Email not confirmed' in error_msg:
                flash('Please confirm your email address before logging in.', 'warning')
            elif 'email_logins_disabled' in error_msg:
                flash('Email login is currently disabled. Please contact support.', 'danger')
            else:
                flash('Login error. Please try again.', 'danger')
    
    return render_template('auth/login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """User registration route"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        if not email or not password:
            flash('Please enter both email and password.', 'danger')
            return render_template('auth/signup.html')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/signup.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return render_template('auth/signup.html')
        
        if not supabase:
            flash('Database connection error. Please try again later.', 'danger')
            return render_template('auth/signup.html')
        
        try:
            # Create user in Supabase
            auth_response = supabase.auth.sign_up({
                "email": email,
                "password": password
            })
            
            if auth_response and auth_response.user:
                flash('Account created successfully! Please check your email to confirm your account.', 'success')
                return redirect(url_for('login'))
            else:
                flash('Failed to create account. Please try again.', 'danger')
                
        except Exception as e:
            error_msg = str(e)
            logger.error(f"❌ Signup error: {error_msg}")
            
            if 'User already registered' in error_msg:
                flash('An account with this email already exists.', 'danger')
            else:
                flash('Registration error. Please try again.', 'danger')
    
    return render_template('auth/signup.html')

@app.route('/logout')
def logout():
    """Logout route"""
    try:
        if supabase and 'access_token' in session:
            supabase.auth.sign_out()
    except:
        pass
    
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    """Protected dashboard route"""
    # Get user information from session
    user = {
        'id': session.get('user_id'),
        'email': session.get('user_email'),
        'role': session.get('user_role', 'user'),
        'company_id': session.get('company_id')
    }
    
    # Dashboard metrics
    metrics = {
        'move_ins': [],
        'move_outs': [],
        'vacant_units': 115,
        'occupied_units': 1099,
        'total_units': 1214,
        'occupancy_rate': 90.53,
        'maintenance_orders': {
            'new': 220,
            'assigned': 122,
            'waiting': 15,
            'completed': 1066
        },
        'tenant_insurance_coverage': 91.93,
        'delinquencies': {
            'total': 185,
            '0_30_days': 185,
            '31_60_days': 31,
            '61_plus_days': 110
        }
    }
    
    return render_template('dashboard/dashboard.html', user=user, metrics=metrics)

@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    """Password reset request route"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        
        if not email:
            flash('Please enter your email address.', 'danger')
            return render_template('auth/reset_password.html')
        
        if not supabase:
            flash('Database connection error. Please try again later.', 'danger')
            return render_template('auth/reset_password.html')
        
        try:
            # Request password reset
            supabase.auth.reset_password_email(email)
            flash('Password reset email sent! Please check your inbox.', 'success')
            return redirect(url_for('login'))
            
        except Exception as e:
            logger.error(f"❌ Password reset error: {e}")
            flash('Error sending reset email. Please try again.', 'danger')
    
    return render_template('auth/reset_password.html')

# API Routes for testing
@app.route('/api/test-supabase')
def test_supabase():
    """Test Supabase connection"""
    result = {
        'client_exists': supabase is not None,
        'url': SUPABASE_URL,
        'key_preview': SUPABASE_ANON_KEY[:20] + '...' if SUPABASE_ANON_KEY else None,
        'timestamp': datetime.now().isoformat()
    }
    
    if supabase:
        try:
            # Test authentication endpoint
            test_response = supabase.auth.get_session()
            result['auth_test'] = 'Success'
        except Exception as e:
            result['auth_test'] = f'Failed: {str(e)}'
    
    return jsonify(result)

@app.route('/api/create-test-user', methods=['POST'])
def create_test_user():
    """Create a test user for development"""
    if not supabase:
        return jsonify({'error': 'Supabase client not initialized'}), 500
    
    try:
        # Create test user
        auth_response = supabase.auth.sign_up({
            "email": "test@example.com",
            "password": "Test123456"
        })
        
        if auth_response and auth_response.user:
            return jsonify({
                'success': True,
                'message': 'Test user created successfully',
                'user_id': auth_response.user.id,
                'email': auth_response.user.email
            })
        else:
            return jsonify({'error': 'Failed to create test user'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Quick login for development/demo
@app.route('/quick-login', methods=['GET', 'POST'])
def quick_login():
    """Quick login for demo purposes"""
    # Set demo session
    session['user_id'] = 'demo-user-id'
    session['user_email'] = 'demo@aiviizn.com'
    session['user_role'] = 'admin'
    session['company_id'] = 'demo-company'
    
    flash('Logged in with demo account', 'info')
    return redirect(url_for('dashboard'))

# Error handlers
@app.errorhandler(404)
def not_found(e):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('errors/500.html'), 500

# Health check
@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'supabase_connected': supabase is not None,
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    logger.info(f"🚀 Starting AIVIIZN Property Management System on port {port}")
    app.run(debug=False, host='0.0.0.0', port=port)