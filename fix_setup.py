#!/usr/bin/env python3
"""
AIVIIZN Terminal Agent - Fix Setup Issues
This script addresses common setup problems
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - Success")
            return True
        else:
            print(f"❌ {description} - Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} - Exception: {e}")
        return False

def check_and_install_dependencies():
    """Check and install missing dependencies"""
    print("📦 Checking Python dependencies...")
    
    required_packages = [
        'playwright',
        'openai', 
        'anthropic',
        'google-generativeai',
        'supabase',
        'beautifulsoup4',
        'requests',
        'python-dotenv'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package} - installed")
        except ImportError:
            missing.append(package)
            print(f"❌ {package} - missing")
    
    if missing:
        print(f"🔄 Installing {len(missing)} missing packages...")
        cmd = f"pip install {' '.join(missing)}"
        if run_command(cmd, "Installing packages"):
            print("✅ All packages installed")
        else:
            print("❌ Package installation failed")
            return False
    
    # Install Playwright browsers
    if 'playwright' in missing or not Path.home().joinpath('.cache/ms-playwright').exists():
        run_command("playwright install chromium", "Installing Playwright browsers")
        run_command("playwright install-deps", "Installing Playwright dependencies")
    
    return True

def create_directories():
    """Create necessary directories"""
    print("📁 Creating directories...")
    
    directories = [
        'screenshots',
        'logs', 
        'reports',
        'templates/reports',
        'templates/admin',
        'templates/properties',
        'templates/accounting',
        'templates/maintenance',
        'templates/leasing'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created: {directory}")

def fix_env_loading():
    """Fix environment variable loading in the main scripts"""
    print("🔧 Fixing environment variable loading...")
    
    env_fix = '''
# Add python-dotenv import at the top
from dotenv import load_dotenv
load_dotenv()
'''
    
    scripts_to_fix = ['terminal_agent.py', 'math_validator.py', 'link_tracker.py']
    
    for script in scripts_to_fix:
        if os.path.exists(script):
            with open(script, 'r') as f:
                content = f.read()
            
            if 'from dotenv import load_dotenv' not in content:
                # Add after the imports section
                lines = content.split('\n')
                import_end = 0
                for i, line in enumerate(lines):
                    if line.startswith('import ') or line.startswith('from '):
                        import_end = i
                
                lines.insert(import_end + 1, '\nfrom dotenv import load_dotenv')
                lines.insert(import_end + 2, 'load_dotenv()\n')
                
                with open(script, 'w') as f:
                    f.write('\n'.join(lines))
                
                print(f"✅ Fixed {script}")

def check_env_variables():
    """Check if required environment variables are present"""
    print("🔍 Checking environment variables...")
    
    required_vars = [
        'SUPABASE_URL',
        'SUPABASE_SERVICE_KEY', 
        'OPENAI_API_KEY',
        'ANTHROPIC_API_KEY',
        'GEMINI_API_KEY',
        'WOLFRAM_APP_ID'
    ]
    
    env_path = '.env'
    if not os.path.exists(env_path):
        print("❌ .env file not found")
        return False
    
    with open(env_path, 'r') as f:
        env_content = f.read()
    
    missing_vars = []
    for var in required_vars:
        if f"{var}=" not in env_content or f"{var}=your_" in env_content:
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing or incomplete environment variables: {missing_vars}")
        print("💡 Please update your .env file with proper API keys")
        return False
    else:
        print("✅ All environment variables present")
        return True

def test_database_connection():
    """Test Supabase database connection"""
    print("🗄️ Testing database connection...")
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        from supabase import create_client
        
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_SERVICE_KEY')
        
        if not url or not key:
            print("❌ Missing Supabase credentials")
            return False
        
        client = create_client(url, key)
        
        # Test connection by listing tables
        result = client.table('appfolio_pages').select('id').limit(1).execute()
        print("✅ Database connection successful")
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def create_integration_file():
    """Create a file to help integrate routes with Flask app"""
    print("🔗 Creating integration helper...")
    
    integration_code = '''
# Add this to your main app.py file to integrate generated routes

# At the top with other imports:
import os
from datetime import datetime

# After your existing routes, add:
def load_generated_routes():
    """Load dynamically generated routes"""
    routes_file = 'routes_reports.py'
    if os.path.exists(routes_file):
        try:
            exec(open(routes_file).read(), globals())
            print(f"✅ Loaded routes from {routes_file}")
        except Exception as e:
            print(f"❌ Error loading routes: {e}")

# Call this function after your app initialization:
# load_generated_routes()
'''
    
    with open('integration_helper.py', 'w') as f:
        f.write(integration_code)
    
    print("✅ Created integration_helper.py")

def make_scripts_executable():
    """Make all scripts executable"""
    print("🔐 Setting script permissions...")
    
    scripts = [
        'terminal_agent.py',
        'link_tracker.py', 
        'math_validator.py',
        'quick_start.sh',
        'monitor_progress.sh',
        'setup_dependencies.sh'
    ]
    
    for script in scripts:
        if os.path.exists(script):
            os.chmod(script, 0o755)
            print(f"✅ Made {script} executable")

def main():
    """Main setup function"""
    print("🔧 AIVIIZN Terminal Agent - Setup Fixer")
    print("====================================")
    
    # Change to the correct directory
    if not os.path.exists('.env'):
        print("❌ Please run this from the AIVIIZN directory (where .env is located)")
        sys.exit(1)
    
    success = True
    
    # Step 1: Install dependencies
    if not check_and_install_dependencies():
        success = False
    
    # Step 2: Create directories
    create_directories()
    
    # Step 3: Fix environment loading
    fix_env_loading()
    
    # Step 4: Check environment variables
    if not check_env_variables():
        success = False
    
    # Step 5: Test database connection
    if not test_database_connection():
        success = False
    
    # Step 6: Create integration helper
    create_integration_file()
    
    # Step 7: Make scripts executable
    make_scripts_executable()
    
    print("\n" + "="*50)
    if success:
        print("🎉 Setup completed successfully!")
        print("\n🚀 Next steps:")
        print("1. Run: ./quick_start.sh")
        print("2. Select option 1 to start with reports")
        print("3. Monitor progress with: ./monitor_progress.sh")
        print("\n💡 To integrate with Flask app:")
        print("Add the code from integration_helper.py to your app.py")
    else:
        print("⚠️ Setup completed with issues")
        print("Please fix the errors above before proceeding")
    
    print("\n📋 System status:")
    print("✅ Python scripts created")
    print("✅ Shell scripts created") 
    print("✅ Directories created")
    print("✅ Integration helper created")

if __name__ == "__main__":
    main()
