#!/usr/bin/env python3
"""
AIVIIZN Database Status Checker
Quick script to check your current Supabase database status
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv

def check_database_status():
    """Check current Supabase database status"""
    
    # Load environment variables
    load_dotenv()
    
    # Get Supabase credentials
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ Missing Supabase credentials in .env file")
        print("📝 Create .env file with:")
        print("   SUPABASE_URL=your-project-url")
        print("   SUPABASE_KEY=your-anon-key")
        return
    
    try:
        # Connect to Supabase
        supabase: Client = create_client(supabase_url, supabase_key)
        print("✅ Connected to Supabase successfully")
        
        # Check for common property management tables
        tables_to_check = [
            'properties', 'tenants', 'units', 'leases', 
            'maintenance_requests', 'financial_transactions', 
            'payments', 'vendors', 'documents'
        ]
        
        existing_tables = []
        table_data = {}
        
        for table in tables_to_check:
            try:
                # Try to query the table (just count rows)
                result = supabase.table(table).select("*", count="exact").limit(1).execute()
                row_count = result.count if hasattr(result, 'count') else 0
                existing_tables.append(table)
                table_data[table] = row_count
                print(f"✅ Table '{table}' exists - {row_count} rows")
            except Exception:
                print(f"❌ Table '{table}' does not exist")
        
        # Summary and recommendations
        print("\n" + "="*50)
        print("📊 DATABASE STATUS SUMMARY")
        print("="*50)
        
        if not existing_tables:
            print("🆕 EMPTY DATABASE - No property management tables found")
            print("📝 RECOMMENDATION: Use database/clean_install.sql for fresh setup")
            
        elif len(existing_tables) < 5:
            print("🔧 PARTIAL SETUP - Some tables exist but incomplete")
            print(f"📊 Found {len(existing_tables)} tables: {', '.join(existing_tables)}")
            print("📝 RECOMMENDATION: Use database/schema.sql to add missing tables")
            
        else:
            total_rows = sum(table_data.values())
            print("🏢 ACTIVE DATABASE - Property management system detected")
            print(f"📊 Found {len(existing_tables)} tables with {total_rows} total rows")
            
            if total_rows > 0:
                print("⚠️  DATA DETECTED - Contains actual property data")
                print("📝 RECOMMENDATION: Use database/schema.sql (safe migration)")
                print("🔒 BACKUP FIRST if data is important")
            else:
                print("📝 RECOMMENDATION: Either option works:")
                print("   - database/schema.sql (safe, preserves structure)")
                print("   - database/clean_install.sql (fresh, optimized)")
        
        print("\n📁 NEXT STEPS:")
        print("1. Run the build script: python build_real_system.py")
        print("2. Follow the database setup instructions in README.md")
        
    except Exception as e:
        print(f"❌ Failed to connect to Supabase: {e}")
        print("📝 Check your .env credentials and network connection")

if __name__ == "__main__":
    print("🔍 AIVIIZN Database Status Checker")
    print("="*40)
    check_database_status()
