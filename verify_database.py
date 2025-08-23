#!/usr/bin/env python3
"""
Verify database setup for AIVIIZN SaaS
Run this after executing the SQL setup script
"""

import os
from supabase import create_client
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

def verify_database():
    """Check if all tables were created correctly"""
    
    print("🔍 VERIFYING DATABASE SETUP")
    print("=" * 50)
    
    # Connect to Supabase
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ Missing environment variables!")
        print("   Required: SUPABASE_URL, SUPABASE_SERVICE_KEY")
        return False
    
    try:
        supabase = create_client(supabase_url, supabase_key)
        print("✅ Connected to Supabase")
    except Exception as e:
        print(f"❌ Failed to connect: {e}")
        return False
    
    # Tables to check
    tables = [
        'companies',
        'field_mappings',
        'captured_pages',
        'company_calculations',
        'company_templates',
        'captured_entities',
        'field_patterns'
    ]
    
    all_good = True
    
    for table in tables:
        try:
            # Try to query the table
            result = supabase.table(table).select('id').limit(1).execute()
            print(f"✅ Table '{table}' exists")
            
            # Check if it has any data
            if result.data:
                print(f"   → Contains {len(result.data)} record(s)")
            else:
                print(f"   → Empty (ready for data)")
                
        except Exception as e:
            print(f"❌ Table '{table}' not found or error: {str(e)[:50]}")
            all_good = False
    
    print("\n" + "=" * 50)
    
    if all_good:
        print("🎉 DATABASE SETUP SUCCESSFUL!")
        print("\nNext steps:")
        print("1. Run: python aiviizn_real_agent_saas.py")
        print("2. Create or select a company")
        print("3. Start capturing pages with field mapping!")
        
        # Try to create a test company
        print("\n🧪 Creating test company...")
        try:
            test_company = {
                'name': 'Test Property Management',
                'domain': 'test.example.com',
                'base_url': 'https://test.example.com',
                'subscription_tier': 'trial',
                'settings': {
                    'auto_detect_fields': True,
                    'test_company': True
                }
            }
            
            result = supabase.table('companies').insert(test_company).execute()
            if result.data:
                company = result.data[0]
                print(f"✅ Test company created: {company['name']}")
                print(f"   ID: {company['id']}")
                
                # Clean up test company
                supabase.table('companies').delete().eq('id', company['id']).execute()
                print("✅ Test company removed (database is working)")
            
        except Exception as e:
            print(f"⚠️ Could not create test company: {e}")
            print("   This might be normal if RLS is enabled")
    
    else:
        print("❌ DATABASE SETUP INCOMPLETE!")
        print("\nPlease:")
        print("1. Go to Supabase SQL Editor")
        print("2. Copy and run the contents of: database_setup.sql")
        print("3. Run this script again to verify")
    
    # Check for old tables
    print("\n📦 Checking for old tables to migrate...")
    old_tables = ['pages', 'calculations', 'api_responses']
    has_old_data = False
    
    for table in old_tables:
        try:
            result = supabase.table(table).select('id').limit(1).execute()
            if result.data:
                print(f"⚠️ Found old table '{table}' with data")
                has_old_data = True
        except:
            pass  # Table doesn't exist, which is fine
    
    if has_old_data:
        print("\n📝 You have old data that can be migrated!")
        print("   Run the migration script: database_migration.sql")
    
    return all_good

if __name__ == "__main__":
    success = verify_database()
    exit(0 if success else 1)
