#!/usr/bin/env python3
"""
AIVIIZN Setup Assistant
Guides you through setting up the multi-tenant database
"""

import os
import webbrowser
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def main():
    print("\n" + "=" * 70)
    print("🚀 AIVIIZN MULTI-TENANT SETUP ASSISTANT")
    print("=" * 70)
    
    print("\nThis will guide you through setting up your multi-tenant database.")
    print("This process will DELETE all existing data and create a new structure.")
    
    # Check environment
    print("\n📋 STEP 1: Checking Environment")
    print("-" * 40)
    
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_KEY')
    supabase_anon = os.getenv('SUPABASE_KEY')
    anthropic_key = os.getenv('ANTHROPIC_API_KEY')
    openai_key = os.getenv('OPENAI_API_KEY')
    
    env_ok = True
    
    if supabase_url:
        print(f"  ✅ SUPABASE_URL: {supabase_url[:30]}...")
    else:
        print("  ❌ SUPABASE_URL: Missing")
        env_ok = False
    
    if supabase_key:
        print(f"  ✅ SUPABASE_SERVICE_KEY: {supabase_key[:20]}...")
    else:
        print("  ❌ SUPABASE_SERVICE_KEY: Missing")
        env_ok = False
    
    if supabase_anon:
        print(f"  ✅ SUPABASE_KEY: {supabase_anon[:20]}...")
    else:
        print("  ❌ SUPABASE_KEY: Missing")
        env_ok = False
    
    if anthropic_key:
        print(f"  ✅ ANTHROPIC_API_KEY: {anthropic_key[:20]}...")
    else:
        print("  ⚠️  ANTHROPIC_API_KEY: Missing (optional but recommended)")
    
    if openai_key:
        print(f"  ✅ OPENAI_API_KEY: {openai_key[:20]}...")
    else:
        print("  ⚠️  OPENAI_API_KEY: Missing (optional for enhanced field detection)")
    
    if not env_ok:
        print("\n❌ Please set up your .env file first!")
        print("   Copy .env.example to .env and fill in your keys")
        return
    
    # SQL file info
    print("\n📋 STEP 2: Database Setup")
    print("-" * 40)
    
    sql_file = "/Users/ianrakow/Desktop/AIVIIZN/complete_database_setup.sql"
    
    if os.path.exists(sql_file):
        print(f"  ✅ SQL file ready: {sql_file}")
        
        # Get file size
        size = os.path.getsize(sql_file)
        print(f"     Size: {size:,} bytes")
        print(f"     Created: {datetime.fromtimestamp(os.path.getctime(sql_file)).strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        print(f"  ❌ SQL file not found: {sql_file}")
        return
    
    print("\n" + "=" * 70)
    print("📝 INSTRUCTIONS")
    print("=" * 70)
    
    print("\n1. OPEN SUPABASE SQL EDITOR:")
    print("   • Go to your Supabase dashboard")
    print("   • Click on 'SQL Editor' in the left sidebar")
    print("   • Click 'New query' button")
    
    print("\n2. COPY THE SQL:")
    print(f"   • Open the file: {sql_file}")
    print("   • Select ALL the content (Cmd+A)")
    print("   • Copy it (Cmd+C)")
    
    print("\n3. RUN THE SQL:")
    print("   • Paste into Supabase SQL Editor (Cmd+V)")
    print("   • Click 'Run' button")
    print("   • Wait for success message")
    
    print("\n4. VERIFY:")
    print("   • Run: python3 test_complete_system.py")
    print("   • This will verify everything is working")
    
    print("\n" + "=" * 70)
    print("🎯 WHAT THIS CREATES")
    print("=" * 70)
    
    print("\n• Multi-tenant architecture with complete data isolation")
    print("• Intelligent field mapping system that learns")
    print("• Entity storage (tenants, units, properties, payments)")
    print("• Company-specific templates and calculations")
    print("• Machine learning patterns for better field detection")
    
    print("\n" + "=" * 70)
    print("⚠️  WARNING")
    print("=" * 70)
    
    print("\nThis will DELETE all existing tables including:")
    print("  • pages")
    print("  • calculations")
    print("  • api_responses")
    print("\nAnd create new multi-tenant tables.")
    
    # Open browser option
    print("\n" + "=" * 70)
    choice = input("\nOpen Supabase dashboard in browser? (y/n): ").lower()
    
    if choice == 'y' and supabase_url:
        # Extract project ref from URL
        # Format: https://xxxxx.supabase.co
        import re
        match = re.match(r'https://([^.]+)\.supabase\.co', supabase_url)
        if match:
            project_ref = match.group(1)
            dashboard_url = f"https://supabase.com/dashboard/project/{project_ref}/sql/new"
            print(f"\n🌐 Opening: {dashboard_url}")
            webbrowser.open(dashboard_url)
        else:
            print("\n⚠️  Could not determine dashboard URL")
            print("   Please open Supabase manually")
    
    print("\n" + "=" * 70)
    print("📚 NEXT STEPS")
    print("=" * 70)
    
    print("\n1. Run the SQL in Supabase")
    print("2. Run: python3 test_complete_system.py")
    print("3. Run: python3 aiviizn_real_agent_saas.py")
    print("4. Create your first company")
    print("5. Start capturing with intelligent field mapping!")
    
    print("\n✨ Good luck with your multi-tenant SaaS platform!")
    print("=" * 70)

if __name__ == "__main__":
    main()
