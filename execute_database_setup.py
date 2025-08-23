#!/usr/bin/env python3
"""
Execute the complete database setup for AIVIIZN Multi-Tenant SaaS
This will DELETE all existing tables and create the new structure
"""

import os
import sys
import time
import json
from supabase import create_client
from dotenv import load_dotenv
import subprocess

load_dotenv()

def execute_database_setup():
    """Execute the complete database setup via Supabase"""
    
    print("🚀 EXECUTING AIVIIZN DATABASE SETUP")
    print("=" * 60)
    print("⚠️  WARNING: This will DELETE all existing data!")
    print("=" * 60)
    
    # Connect to Supabase
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ Missing environment variables!")
        return False
    
    print(f"✅ Connecting to: {supabase_url}")
    
    try:
        # Since Supabase Python client doesn't support raw SQL, we need to use the REST API
        import requests
        
        # Extract project ref from URL
        import re
        match = re.match(r'https://([^.]+)\.supabase\.co', supabase_url)
        if not match:
            print("❌ Invalid Supabase URL format")
            return False
        
        project_ref = match.group(1)
        
        # Read the SQL file
        sql_file = "/Users/ianrakow/Desktop/AIVIIZN/complete_database_setup.sql"
        with open(sql_file, 'r') as f:
            sql_content = f.read()
        
        print(f"📝 Loaded SQL file: {len(sql_content)} characters")
        
        # Use Supabase REST API to execute SQL
        headers = {
            'apikey': supabase_key,
            'Authorization': f'Bearer {supabase_key}',
            'Content-Type': 'application/json',
            'Prefer': 'return=minimal'
        }
        
        # Split SQL into individual statements (Supabase REST API limitation)
        sql_statements = []
        current_statement = []
        
        for line in sql_content.split('\n'):
            # Skip comments and empty lines
            if line.strip().startswith('--') or not line.strip():
                continue
            
            current_statement.append(line)
            
            # Check if statement is complete
            if ';' in line:
                statement = '\n'.join(current_statement).strip()
                if statement and not statement.startswith('--'):
                    sql_statements.append(statement)
                current_statement = []
        
        print(f"📋 Found {len(sql_statements)} SQL statements to execute")
        
        # Since we can't execute raw SQL via Python client, let's create tables using Supabase API
        supabase = create_client(supabase_url, supabase_key)
        
        print("\n🗑️  Checking for existing tables...")
        
        # Tables to check and potentially delete
        old_tables = [
            'pages',
            'calculations', 
            'api_responses',
            'captured_entities',
            'captured_pages',
            'company_calculations',
            'company_templates',
            'field_mappings',
            'field_patterns',
            'companies'
        ]
        
        for table in old_tables:
            try:
                # Try to access the table
                result = supabase.table(table).select('id').limit(1).execute()
                print(f"  ⚠️  Table '{table}' exists - needs to be dropped")
            except:
                print(f"  ✓ Table '{table}' doesn't exist")
        
        print("\n" + "=" * 60)
        print("📝 MANUAL SQL EXECUTION REQUIRED")
        print("=" * 60)
        
        print("\nThe Supabase Python client cannot execute DDL statements.")
        print("I've prepared everything for you. Please follow these steps:\n")
        
        print("1. I'll open your Supabase SQL Editor")
        print("2. Copy the SQL from: complete_database_setup.sql")
        print("3. Paste and run it")
        print("4. Come back here and press ENTER\n")
        
        # Try to open Supabase SQL editor
        dashboard_url = f"https://supabase.com/dashboard/project/{project_ref}/sql/new"
        
        print(f"🌐 Opening: {dashboard_url}")
        
        # Try different methods to open URL
        try:
            # Method 1: webbrowser
            import webbrowser
            webbrowser.open(dashboard_url)
        except:
            try:
                # Method 2: macOS open command
                subprocess.run(['open', dashboard_url])
            except:
                print("⚠️  Please open manually: " + dashboard_url)
        
        print("\n" + "=" * 60)
        print("📋 SQL FILE LOCATION:")
        print("=" * 60)
        print(f"\n{sql_file}\n")
        
        print("Steps:")
        print("1. Copy ALL content from the file above")
        print("2. Paste into Supabase SQL Editor")
        print("3. Click 'Run'")
        print("4. Wait for success message")
        
        input("\n✅ Press ENTER after running the SQL in Supabase... ")
        
        # Verify the setup worked
        print("\n🔍 Verifying database setup...")
        
        new_tables = [
            'companies',
            'field_mappings',
            'captured_pages',
            'captured_entities',
            'company_calculations',
            'company_templates',
            'field_patterns'
        ]
        
        all_good = True
        for table in new_tables:
            try:
                result = supabase.table(table).select('id').limit(1).execute()
                print(f"  ✅ Table '{table}' created successfully")
            except Exception as e:
                print(f"  ❌ Table '{table}' not found - SQL may not have run")
                all_good = False
        
        if all_good:
            print("\n" + "=" * 60)
            print("🎉 DATABASE SETUP COMPLETE!")
            print("=" * 60)
            
            # Create a demo company
            print("\n📝 Creating demo company...")
            
            try:
                demo_company = {
                    'name': 'Demo Property Management',
                    'domain': 'demo.appfolio.com',
                    'base_url': 'https://demo.appfolio.com',
                    'subscription_tier': 'trial',
                    'settings': {
                        'auto_detect_fields': True,
                        'capture_api_responses': True,
                        'require_field_verification': False
                    }
                }
                
                result = supabase.table('companies').insert(demo_company).execute()
                
                if result.data:
                    company = result.data[0]
                    print(f"✅ Demo company created!")
                    print(f"   Name: {company['name']}")
                    print(f"   ID: {company['id']}")
                    
                    # Check field patterns
                    patterns = supabase.table('field_patterns').select('*').limit(5).execute()
                    if patterns.data:
                        print(f"\n✅ Field patterns loaded: {len(patterns.data)} patterns")
                    
                    print("\n🚀 READY TO GO!")
                    print("\nYou can now run:")
                    print("  python3 aiviizn_real_agent_saas.py")
                    
            except Exception as e:
                print(f"⚠️  Could not create demo company: {e}")
                print("   But the database structure is ready!")
        
        else:
            print("\n❌ Some tables are missing!")
            print("Please make sure you ran the complete SQL in Supabase")
            print(f"SQL file: {sql_file}")
        
        return all_good
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("AIVIIZN DATABASE EXECUTOR")
    print("=" * 60)
    
    confirm = input("\n⚠️  This will DELETE all data. Type 'YES' to continue: ")
    
    if confirm == 'YES':
        success = execute_database_setup()
        
        if success:
            print("\n✅ Setup complete! Run: python3 aiviizn_real_agent_saas.py")
        else:
            print("\n⚠️  Setup incomplete. Please check the instructions above.")
    else:
        print("❌ Cancelled")
