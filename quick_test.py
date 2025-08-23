#!/usr/bin/env python3
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
        print("\n🎉 ALL TESTS PASSED!")
        print("🚀 System is ready!")
    else:
        print("\n❌ Some tests failed")
        print("🔧 Check the errors above")
