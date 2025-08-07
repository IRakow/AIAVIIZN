from supabase import create_client

SUPABASE_URL = "https://sejebqdhcilwcpjpznep.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNlamVicWRoY2lsd2NwanB6bmVwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ0NTg5NjQsImV4cCI6MjA3MDAzNDk2NH0.vFM0Gr3QZF4MN3vtDGghjyCpnIkyC_mmUOOkVO3ahPQ"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Test query
try:
    result = supabase.table('properties').select("*").execute()
    print("✅ Connection successful!")
    print(f"Found {len(result.data)} properties")
except Exception as e:
    print(f"❌ Error: {e}")