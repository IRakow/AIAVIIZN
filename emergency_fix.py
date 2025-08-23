#!/usr/bin/env python3
"""
EMERGENCY FIX: Install all missing dependencies and fix failing components
This script will fix all the failing tests
"""

import os
import sys
import subprocess
import json

def fix_dependencies():
    """Install all missing dependencies"""
    print("🔧 FIXING: Installing missing dependencies...")
    
    # Create virtual environment if it doesn't exist
    if not os.path.exists('venv'):
        print("📦 Creating virtual environment...")
        subprocess.run([sys.executable, '-m', 'venv', 'venv'], check=True)
    
    # Determine activation script
    if os.name == 'nt':  # Windows
        activate_script = 'venv\\Scripts\\activate'
        pip_path = 'venv\\Scripts\\pip'
        python_path = 'venv\\Scripts\\python'
    else:  # Unix/Linux/MacOS
        activate_script = 'venv/bin/activate'
        pip_path = 'venv/bin/pip'
        python_path = 'venv/bin/python'
    
    # Install packages using the virtual environment pip
    print("📥 Installing packages...")
    
    packages = [
        'pip>=24.0',
        'playwright>=1.41.0',
        'openai>=1.8.0', 
        'anthropic>=0.12.0',
        'google-generativeai>=0.4.0',
        'supabase>=2.3.0',
        'beautifulsoup4>=4.12.2',
        'requests>=2.32.0',
        'python-dotenv>=1.0.1',
        'lxml>=5.1.0',
        'aiohttp>=3.9.3'
    ]
    
    # Upgrade pip first
    subprocess.run([python_path, '-m', 'pip', 'install', '--upgrade', 'pip'], check=True)
    
    # Install each package
    for package in packages:
        print(f"Installing {package}...")
        try:
            subprocess.run([pip_path, 'install', package], check=True)
            print(f"✅ {package}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {package}: {e}")
            return False
    
    # Install Playwright browsers
    print("🌐 Installing Playwright browsers...")
    try:
        # Use the virtual environment's playwright
        subprocess.run([python_path, '-m', 'playwright', 'install', 'chromium'], check=True)
        subprocess.run([python_path, '-m', 'playwright', 'install-deps'], check=True, capture_output=True)
        print("✅ Playwright browsers installed")
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Playwright browser install had issues: {e}")
        # Try alternative method
        try:
            subprocess.run(['playwright', 'install', 'chromium'], check=True)
            print("✅ Playwright browsers installed (fallback method)")
        except:
            print("❌ Playwright browser installation failed")
            return False
    
    return True

def fix_env_loading():
    """Fix environment loading in Python scripts"""
    print("🔧 FIXING: Environment variable loading...")
    
    scripts_to_fix = ['terminal_agent.py', 'math_validator.py', 'link_tracker.py']
    
    env_import = """
# PRODUCTION FIX: Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # Fallback: load .env manually
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
"""
    
    for script in scripts_to_fix:
        if os.path.exists(script):
            with open(script, 'r') as f:
                content = f.read()
            
            # Only add if not already present
            if 'load_dotenv()' not in content:
                # Find where to insert (after imports)
                lines = content.split('\n')
                insert_pos = 0
                
                # Find the end of imports
                for i, line in enumerate(lines):
                    if (line.startswith('import ') or line.startswith('from ')) and 'dotenv' not in line:
                        insert_pos = i + 1
                
                # Insert the fix
                lines.insert(insert_pos, env_import)
                
                with open(script, 'w') as f:
                    f.write('\n'.join(lines))
                
                print(f"✅ Fixed {script}")
    
    return True

def test_imports():
    """Test if we can import required packages"""
    print("🧪 TESTING: Package imports...")
    
    # Use virtual environment python
    python_path = 'venv/bin/python' if os.name != 'nt' else 'venv\\Scripts\\python'
    
    test_script = '''
import sys
success = True

packages = [
    "playwright", "openai", "anthropic", 
    "google.generativeai", "supabase", 
    "bs4", "requests", "dotenv"
]

for pkg in packages:
    try:
        __import__(pkg.replace("-", "_"))
        print(f"✅ {pkg}")
    except ImportError as e:
        print(f"❌ {pkg}: {e}")
        success = False

sys.exit(0 if success else 1)
'''
    
    with open('test_imports.py', 'w') as f:
        f.write(test_script)
    
    try:
        result = subprocess.run([python_path, 'test_imports.py'], capture_output=True, text=True)
        print(result.stdout)
        if result.returncode == 0:
            print("✅ All packages can be imported")
            return True
        else:
            print("❌ Some packages failed to import")
            return False
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False
    finally:
        if os.path.exists('test_imports.py'):
            os.remove('test_imports.py')

def create_test_script():
    """Create a simple test script to verify everything works"""
    print("📝 Creating verification test...")
    
    test_content = '''#!/usr/bin/env python3
"""
Simple test to verify the system is working
"""
import os
import sys

# Load environment
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value

def test_env():
    """Test environment variables"""
    required = ['SUPABASE_URL', 'SUPABASE_SERVICE_KEY', 'OPENAI_API_KEY', 'ANTHROPIC_API_KEY', 'GEMINI_API_KEY', 'WOLFRAM_APP_ID']
    missing = [var for var in required if not os.getenv(var)]
    
    if missing:
        print(f"❌ Missing env vars: {missing}")
        return False
    
    print("✅ Environment variables OK")
    return True

def test_database():
    """Test database connection"""
    try:
        from supabase import create_client
        client = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_KEY'))
        result = client.table('appfolio_pages').select('id').limit(1).execute()
        print("✅ Database connection OK")
        return True
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def test_playwright():
    """Test Playwright"""
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto("https://httpbin.org/json")
            browser.close()
        print("✅ Playwright OK")
        return True
    except Exception as e:
        print(f"❌ Playwright error: {e}")
        return False

def test_openai():
    """Test OpenAI"""
    try:
        import openai
        client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": "Say 'OK'"}],
            max_tokens=5
        )
        print("✅ OpenAI OK")
        return True
    except Exception as e:
        print(f"❌ OpenAI error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Quick System Test")
    print("=" * 30)
    
    tests = [test_env, test_database, test_playwright, test_openai]
    results = []
    
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"❌ Test failed: {e}")
            results.append(False)
    
    if all(results):
        print("\\n🎉 ALL TESTS PASSED!")
        print("🚀 System is ready!")
    else:
        print("\\n❌ Some tests failed")
        print("🔧 Check the errors above")
'''
    
    with open('quick_test.py', 'w') as f:
        f.write(test_content)
    
    os.chmod('quick_test.py', 0o755)
    print("✅ Created quick_test.py")

def main():
    """Main fix function"""
    print("🚨 EMERGENCY FIX - AIVIIZN Production Issues")
    print("=" * 50)
    
    if not os.path.exists('.env'):
        print("❌ No .env file found. Please create it with your API keys.")
        return False
    
    try:
        # Step 1: Fix dependencies
        if not fix_dependencies():
            print("❌ Failed to fix dependencies")
            return False
        
        # Step 2: Fix environment loading
        fix_env_loading()
        
        # Step 3: Test imports
        if not test_imports():
            print("❌ Import test failed")
            return False
        
        # Step 4: Create test script
        create_test_script()
        
        print("\n🎉 EMERGENCY FIXES APPLIED!")
        print("=" * 30)
        print("✅ Dependencies installed")
        print("✅ Environment loading fixed") 
        print("✅ Test script created")
        print("\n🧪 Run quick test:")
        print("   ./venv/bin/python quick_test.py")
        print("\n🚀 If test passes, run:")
        print("   ./quick_start.sh")
        
        return True
        
    except Exception as e:
        print(f"❌ Emergency fix failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
