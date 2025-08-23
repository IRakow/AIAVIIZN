#!/usr/bin/env python3
"""Fix Supabase pages table by adding missing columns"""

import os
from supabase import create_client
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Connect to Supabase
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_SERVICE_KEY')
supabase = create_client(supabase_url, supabase_key)

# Add missing columns
sql = """
ALTER TABLE pages 
ADD COLUMN IF NOT EXISTS calculations JSONB DEFAULT '[]'::jsonb,
ADD COLUMN IF NOT EXISTS api_responses JSONB DEFAULT '[]'::jsonb,
ADD COLUMN IF NOT EXISTS field_mappings JSONB DEFAULT '[]'::jsonb,
ADD COLUMN IF NOT EXISTS field_statistics JSONB DEFAULT '{}'::jsonb;
"""

try:
    # Execute the SQL
    result = supabase.rpc('exec_sql', {'query': sql}).execute()
    print("✅ Successfully added missing columns to pages table")
except Exception as e:
    # If direct SQL doesn't work, try a different approach
    print(f"Direct SQL failed: {e}")
    print("\nPlease run this SQL in your Supabase SQL editor:")
    print(sql)
    print("\n📋 Go to: https://supabase.com/dashboard/project/sejebqdhcilwcpjpznep/sql/new")

print("\nAlternatively, you can check if the columns exist by querying:")
try:
    # Try to query with the new columns to verify
    test = supabase.table('pages').select('id, calculations, api_responses, field_mappings, field_statistics').limit(1).execute()
    print("✅ Columns verified - they exist!")
except Exception as e:
    print(f"❌ Columns still missing: {e}")
    print("\nYou need to add them manually in Supabase SQL editor")
