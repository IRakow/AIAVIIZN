#!/usr/bin/env python3
"""
Check for duplicate pages in Supabase
Run this to see if you have duplicate issues
"""

import os
from supabase import create_client
from dotenv import load_dotenv
from collections import Counter

load_dotenv()

# Connect to Supabase
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_SERVICE_KEY')
supabase = create_client(supabase_url, supabase_key)

print("🔍 CHECKING FOR DUPLICATES IN SUPABASE")
print("=" * 50)

# Check pages table
try:
    pages = supabase.table('pages').select('company_id, url').execute()
    
    if pages.data:
        # Count duplicates
        url_counts = Counter([(p['company_id'], p['url']) for p in pages.data])
        duplicates = {k: v for k, v in url_counts.items() if v > 1}
        
        print(f"\n📊 Pages Table:")
        print(f"   Total records: {len(pages.data)}")
        print(f"   Unique URLs: {len(url_counts)}")
        
        if duplicates:
            print(f"\n❌ FOUND {len(duplicates)} DUPLICATE URLS:")
            for (company_id, url), count in duplicates.items():
                print(f"   • {url}")
                print(f"     Company: {company_id}")
                print(f"     Duplicates: {count} copies")
        else:
            print("   ✅ No duplicates found!")
    else:
        print("   📭 No pages in database yet")
        
except Exception as e:
    print(f"   ❌ Error checking pages: {e}")

# Check calculations table
try:
    calcs = supabase.table('calculations').select('company_id, page_url, name').execute()
    
    if calcs.data:
        calc_counts = Counter([(c['company_id'], c['page_url'], c['name']) for c in calcs.data])
        calc_duplicates = {k: v for k, v in calc_counts.items() if v > 1}
        
        print(f"\n📊 Calculations Table:")
        print(f"   Total records: {len(calcs.data)}")
        print(f"   Unique calculations: {len(calc_counts)}")
        
        if calc_duplicates:
            print(f"\n❌ FOUND {len(calc_duplicates)} DUPLICATE CALCULATIONS:")
            for (company_id, page_url, name), count in calc_duplicates.items():
                print(f"   • {name} on {page_url}")
                print(f"     Duplicates: {count} copies")
        else:
            print("   ✅ No duplicates found!")
    else:
        print("   📭 No calculations in database yet")
        
except Exception as e:
    print(f"   ❌ Error checking calculations: {e}")

print("\n" + "=" * 50)
print("💡 TO FIX DUPLICATES:")
print("1. Run: python check_duplicates.py")
print("2. If duplicates found, run the SQL:")
print("   cat add_duplicate_prevention.sql")
print("3. Update your agent with duplicate prevention code")
