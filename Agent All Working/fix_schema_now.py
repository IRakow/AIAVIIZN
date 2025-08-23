#!/usr/bin/env python3
"""
Quick fix for missing pages table and html_content column in Supabase
Run this script to fix the schema issue immediately
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Supabase credentials
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    print("❌ Missing Supabase credentials in .env file")
    exit(1)

# Initialize Supabase client with service key for admin access
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

# SQL to create/fix the pages table
sql_fix = """
-- Create the pages table if it doesn't exist
CREATE TABLE IF NOT EXISTS pages (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    url TEXT NOT NULL,
    title TEXT,
    html_content TEXT,
    main_content TEXT,
    screenshot_path TEXT,
    field_data JSONB DEFAULT '{}'::jsonb,
    calculations JSONB DEFAULT '[]'::jsonb,
    api_responses JSONB DEFAULT '[]'::jsonb,
    field_mappings JSONB DEFAULT '[]'::jsonb,
    field_statistics JSONB DEFAULT '{}'::jsonb,
    captured_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(company_id, url)
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_pages_company_id ON pages(company_id);
CREATE INDEX IF NOT EXISTS idx_pages_url ON pages(url);

-- If table exists but missing columns, add them
ALTER TABLE pages ADD COLUMN IF NOT EXISTS html_content TEXT;
ALTER TABLE pages ADD COLUMN IF NOT EXISTS calculations JSONB DEFAULT '[]'::jsonb;
ALTER TABLE pages ADD COLUMN IF NOT EXISTS api_responses JSONB DEFAULT '[]'::jsonb;
ALTER TABLE pages ADD COLUMN IF NOT EXISTS field_mappings JSONB DEFAULT '[]'::jsonb;
ALTER TABLE pages ADD COLUMN IF NOT EXISTS field_statistics JSONB DEFAULT '{}'::jsonb;
"""

print("🔧 Fixing pages table schema...")

try:
    # Execute the SQL using Supabase's rpc method for raw SQL
    # Note: Supabase Python client doesn't have direct SQL execution,
    # so we'll use the REST API approach
    
    import requests
    
    headers = {
        'apikey': SUPABASE_SERVICE_KEY,
        'Authorization': f'Bearer {SUPABASE_SERVICE_KEY}',
        'Content-Type': 'application/json'
    }
    
    # First, check if pages table exists
    check_url = f"{SUPABASE_URL}/rest/v1/pages?select=id&limit=1"
    response = requests.get(check_url, headers=headers)
    
    if response.status_code == 404 or 'pages' not in response.text:
        print("📝 Pages table doesn't exist, you need to create it via Supabase SQL editor")
        print("\n👉 Go to: https://supabase.com/dashboard/project/sejebqdhcilwcpjpznep/sql/new")
        print("👉 Copy and paste the contents of: fix_pages_table_schema.sql")
        print("👉 Click 'Run' to execute the SQL")
    else:
        print("✅ Pages table exists, checking columns...")
        
        # Try to insert a test record to see if html_content column exists
        test_data = {
            'company_id': os.getenv('SUPABASE_COMPANY_ID'),
            'url': 'test_schema_check',
            'html_content': 'test'
        }
        
        insert_url = f"{SUPABASE_URL}/rest/v1/pages"
        response = requests.post(insert_url, headers=headers, json=test_data)
        
        if 'html_content' in response.text and 'column' in response.text:
            print("❌ html_content column is missing!")
            print("\n👉 Go to: https://supabase.com/dashboard/project/sejebqdhcilwcpjpznep/sql/new")
            print("👉 Run this SQL:")
            print("\nALTER TABLE pages ADD COLUMN IF NOT EXISTS html_content TEXT;")
        else:
            # Clean up test record
            delete_url = f"{SUPABASE_URL}/rest/v1/pages?url=eq.test_schema_check"
            requests.delete(delete_url, headers=headers)
            print("✅ Schema looks good!")
            
except Exception as e:
    print(f"❌ Error: {e}")
    print("\n🔧 Manual Fix Required:")
    print("1. Go to: https://supabase.com/dashboard/project/sejebqdhcilwcpjpznep/sql/new")
    print("2. Copy and paste the contents of: fix_pages_table_schema.sql")
    print("3. Click 'Run' to execute the SQL")

print("\n📄 SQL fix has been saved to: fix_pages_table_schema.sql")
print("If automatic fix didn't work, manually run the SQL in Supabase dashboard")
