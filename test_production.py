#!/usr/bin/env python3
"""
PRODUCTION VERIFICATION: Test all systems before live deployment
"""

import os
import sys
import asyncio
import json
from datetime import datetime

def test_environment():
    """Test environment setup"""
    print("🔍 Testing environment...")
    
    # Load environment
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ dotenv loaded")
    except ImportError:
        print("❌ python-dotenv not installed")
        return False
    
    # Check required variables
    required = [
        'SUPABASE_URL', 'SUPABASE_SERVICE_KEY',
        'OPENAI_API_KEY', 'ANTHROPIC_API_KEY', 
        'GEMINI_API_KEY', 'WOLFRAM_APP_ID'
    ]
    
    missing = []
    for var in required:
        if not os.getenv(var):
            missing.append(var)
    
    if missing:
        print(f"❌ Missing environment variables: {missing}")
        return False
    
    print("✅ All environment variables present")
    return True

def test_dependencies():
    """Test all required dependencies"""
    print("📦 Testing dependencies...")
    
    deps = {
        'playwright': 'playwright',
        'openai': 'openai', 
        'anthropic': 'anthropic',
        'google.generativeai': 'google-generativeai',
        'supabase': 'supabase',
        'bs4': 'beautifulsoup4',
        'requests': 'requests'
    }
    
    missing = []
    for import_name, package_name in deps.items():
        try:
            __import__(import_name)
            print(f"✅ {package_name}")
        except ImportError:
            missing.append(package_name)
            print(f"❌ {package_name}")
    
    if missing:
        print(f"❌ Missing packages: {missing}")
        return False
    
    return True

def test_database():
    """Test database connection"""
    print("🗄️ Testing database...")
    
    try:
        from supabase import create_client
        
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_SERVICE_KEY')
        
        client = create_client(url, key)
        
        # Test each table
        tables = [
            'appfolio_pages',
            'calculation_formulas', 
            'multi_ai_validations',
            'generated_components'
        ]
        
        for table in tables:
            try:
                result = client.table(table).select('id').limit(1).execute()
                print(f"✅ {table} accessible")
            except Exception as e:
                print(f"❌ {table} error: {e}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

async def test_ai_services():
    """Test AI service connections"""
    print("🤖 Testing AI services...")
    
    # Test OpenAI
    try:
        import openai
        client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": "Test: respond with 'OpenAI working'"}],
            max_tokens=10
        )
        if "working" in response.choices[0].message.content.lower():
            print("✅ OpenAI GPT-4o")
        else:
            print("⚠️ OpenAI responded but unexpected content")
    except Exception as e:
        print(f"❌ OpenAI: {e}")
        return False
    
    # Test Claude
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=10,
            messages=[{"role": "user", "content": "Test: respond with 'Claude working'"}]
        )
        if "working" in response.content[0].text.lower():
            print("✅ Claude 3.5 Sonnet")
        else:
            print("⚠️ Claude responded but unexpected content")
    except Exception as e:
        print(f"❌ Claude: {e}")
        return False
    
    # Test Gemini
    try:
        import google.generativeai as genai
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content("Test: respond with 'Gemini working'")
        if "working" in response.text.lower():
            print("✅ Gemini Pro")
        else:
            print("⚠️ Gemini responded but unexpected content")
    except Exception as e:
        print(f"❌ Gemini: {e}")
        return False
    
    # Test Wolfram Alpha
    try:
        import requests
        app_id = os.getenv('WOLFRAM_APP_ID')
        url = "http://api.wolframalpha.com/v2/query"
        params = {
            'input': '2+2',
            'appid': app_id,
            'format': 'plaintext',
            'output': 'JSON'
        }
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('queryresult', {}).get('success'):
                print("✅ Wolfram Alpha")
            else:
                print("⚠️ Wolfram Alpha responded but query failed")
        else:
            print(f"❌ Wolfram Alpha HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Wolfram Alpha: {e}")
        return False
    
    return True

def test_playwright():
    """Test Playwright browser"""
    print("🌐 Testing Playwright...")
    
    try:
        from playwright.sync_api import sync_playwright
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto("https://www.google.com")
            title = page.title()
            browser.close()
            
            if "google" in title.lower():
                print("✅ Playwright browser working")
                return True
            else:
                print("⚠️ Playwright browser issue")
                return False
                
    except Exception as e:
        print(f"❌ Playwright: {e}")
        return False

def test_file_permissions():
    """Test script permissions"""
    print("🔐 Testing file permissions...")
    
    scripts = [
        'terminal_agent.py',
        'link_tracker.py',
        'math_validator.py',
        'quick_start.sh',
        'monitor_progress.sh'
    ]
    
    for script in scripts:
        if os.path.exists(script):
            if os.access(script, os.X_OK):
                print(f"✅ {script} executable")
            else:
                print(f"❌ {script} not executable")
                return False
        else:
            print(f"❌ {script} missing")
            return False
    
    return True

async def run_full_test():
    """Run comprehensive production test"""
    print("🔥 AIVIIZN PRODUCTION VERIFICATION")
    print("=" * 45)
    
    tests = [
        ("Environment", test_environment),
        ("Dependencies", test_dependencies), 
        ("Database", test_database),
        ("AI Services", test_ai_services),
        ("Playwright", test_playwright),
        ("File Permissions", test_file_permissions)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}:")
        print("-" * 20)
        
        if asyncio.iscoroutinefunction(test_func):
            result = await test_func()
        else:
            result = test_func()
        
        results[test_name] = result
    
    # Summary
    print("\n" + "=" * 45)
    print("🎯 PRODUCTION VERIFICATION SUMMARY")
    print("=" * 45)
    
    all_passed = True
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<15} {status}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 45)
    if all_passed:
        print("🎉 ALL TESTS PASSED - PRODUCTION READY!")
        print("🚀 System is ready for live deployment")
        print("\n▶️  Start with: ./quick_start.sh")
        return True
    else:
        print("❌ TESTS FAILED - NOT PRODUCTION READY")
        print("🔧 Fix the failing tests before deployment")
        return False

def main():
    """Main test runner"""
    if not os.path.exists('.env'):
        print("❌ Run from AIVIIZN directory (where .env is)")
        sys.exit(1)
    
    try:
        result = asyncio.run(run_full_test())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted")
        sys.exit(1)

if __name__ == "__main__":
    main()
