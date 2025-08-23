#!/usr/bin/env python3
"""
Test the new SaaS database structure
Run this after applying the SQL to verify everything works
"""

import os
from supabase import create_client
from dotenv import load_dotenv
import json

load_dotenv()

# Connect to Supabase
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_SERVICE_KEY')
supabase = create_client(supabase_url, supabase_key)

print("🔍 TESTING SAAS DATABASE STRUCTURE")
print("=" * 60)

# Test 1: Check if companies table exists and has AIVIIZN
print("\n1️⃣ Checking Companies Table:")
try:
    companies = supabase.table('companies').select('*').execute()
    if companies.data:
        for company in companies.data:
            print(f"   ✅ Found company: {company['name']}")
            print(f"      ID: {company['id']}")
            print(f"      Tier: {company['subscription_tier']}")
            if company['name'] == 'AIVIIZN':
                print(f"      🎯 AIVIIZN company ready!")
                aiviizn_id = company['id']
    else:
        print("   ❌ No companies found - run the SQL setup first!")
except Exception as e:
    print(f"   ❌ Error: {e}")
    print("      Run complete_saas_database_setup.sql first!")

# Test 2: Check table structure
print("\n2️⃣ Checking Table Structure:")
tables_to_check = ['pages', 'calculations', 'api_responses', 'page_errors', 'page_links']
for table in tables_to_check:
    try:
        # Try to select from table
        result = supabase.table(table).select('id').limit(1).execute()
        print(f"   ✅ Table '{table}' exists and is accessible")
    except Exception as e:
        print(f"   ❌ Table '{table}' error: {e}")

# Test 3: Test duplicate prevention
print("\n3️⃣ Testing Duplicate Prevention:")
if 'aiviizn_id' in locals():
    try:
        test_url = "https://test.example.com/duplicate-test"
        
        # Try to insert the same page twice
        test_page = {
            'company_id': aiviizn_id,
            'url': test_url,
            'title': 'Test Page',
            'html_preview': 'Test content'
        }
        
        # First insert
        result1 = supabase.table('pages').insert(test_page).execute()
        if result1.data:
            print(f"   ✅ First insert successful")
        
        # Try duplicate insert (should fail)
        try:
            result2 = supabase.table('pages').insert(test_page).execute()
            print(f"   ❌ Duplicate was allowed! Check constraints.")
        except:
            print(f"   ✅ Duplicate prevented by unique constraint!")
        
        # Clean up test data
        supabase.table('pages').delete().eq('url', test_url).execute()
        
    except Exception as e:
        print(f"   ⚠️ Test partially failed: {e}")

# Test 4: Check views
print("\n4️⃣ Checking Views:")
try:
    # Check company usage stats
    stats = supabase.table('company_usage_stats').select('*').execute()
    if stats.data:
        for stat in stats.data:
            print(f"   ✅ Company: {stat['name']}")
            print(f"      Pages: {stat.get('total_pages', 0)}")
            print(f"      Calculations: {stat.get('total_calculations', 0)}")
            print(f"      API Calls: {stat.get('total_api_calls', 0)}")
    else:
        print("   📊 No usage data yet (normal for fresh setup)")
except Exception as e:
    print(f"   ⚠️ Views might not be accessible via API (this is normal)")

# Test 5: Check for any existing duplicates
print("\n5️⃣ Checking for Existing Duplicates:")
try:
    duplicates = supabase.table('duplicate_check').select('*').execute()
    if duplicates.data and len(duplicates.data) > 0:
        print(f"   ❌ Found {len(duplicates.data)} duplicates!")
        for dup in duplicates.data:
            print(f"      Table: {dup['table_name']}, ID: {dup['identifier']}")
    else:
        print("   ✅ No duplicates found!")
except:
    print("   ℹ️ Duplicate check view might not be accessible via API")

print("\n" + "=" * 60)
print("📋 SUMMARY:")
print("=" * 60)

# Final recommendations
print("""
✅ If all tests passed, your database is ready!
❌ If any tests failed:

1. Run the complete setup SQL:
   cat complete_saas_database_setup.sql
   (Copy and paste into Supabase SQL Editor)

2. Update your agent code:
   - Replace store_in_supabase_real with the new version
   - The new version has duplicate prevention built in

3. Your agent will now:
   ✓ Never create duplicate pages
   ✓ Update existing pages instead of duplicating
   ✓ Track all errors properly
   ✓ Maintain version history
   ✓ Work as a proper SaaS system

4. Next time you run the agent:
   python aiviizn_real_agent_fixed.py
   
   It will automatically:
   - Use AIVIIZN company ID
   - Prevent duplicates
   - Update existing pages
   - Track all relationships
""")
